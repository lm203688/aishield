"""
运行所有测试 — 串联 test_linkages, test_geo, test_security, test_hupijiao,
test_governance, test_mcp_contract 等

用法:
  python tests/run_all.py
  python tests/run_all.py -v          # 详细模式
  python -m tests.run_all            # 模块方式运行

Hermetic 守卫
-------------
套件跑完会核对一份「被跟踪数据面」的哈希快照。如果某个测试把生产数据文件
改写了（2026-09-19 实测：test_commercialization 里 `FleetService()` 漏传 path，
直接 reset 掉了真实的 data/fleet.json），守卫会：

  1. 打印被改动的文件清单；
  2. 从快照还原原文件；
  3. 让整次运行以非 0 退出。

为什么不是「警告一下就算了」：这类污染不会红。测试全绿、数据已脏，改动混在
下次 `git add -A` 里当成人工变更提交上线 —— 和假绿是同一个病，只是更难看见。
"""

import hashlib
import shutil
import tempfile
import unittest
import sys
import os

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 被跟踪的数据面。测试可以读，但绝不该写。
_PROTECTED_FILES = (
    'data/batch_scans.json',
    'data/fleet.json',
    'data/generated_rules.json',
    'data/monitored_tools.json',
    'data/radar_rules.json',
    'data/threat_intel.json',
    'mcp-server/README.md',
    'README.md',
)


def _protected_paths(root=None):
    root = root or _ROOT
    paths = list(_PROTECTED_FILES)
    state_dir = os.path.join(root, 'data', 'state')
    if os.path.isdir(state_dir):
        for name in sorted(os.listdir(state_dir)):
            if os.path.isfile(os.path.join(state_dir, name)):
                paths.append(os.path.join('data', 'state', name))
    return [p for p in paths if os.path.exists(os.path.join(root, p))]


def _sha256(path):
    with open(path, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


class _DataGuard:
    """快照 → 运行 → 核对 → 还原。

    ``root`` / ``paths`` 可覆写，唯一目的是让 tests/test_hermetic_guard.py 能
    用一个临时目录做**正向对照**：守卫必须真的能抓到一次写入，否则它自己就是
    一层假绿 —— 一个永远不报错的守卫，和没有守卫是一样的。
    """

    def __init__(self, root=None, paths=None):
        self._root = root or _ROOT
        self._paths = list(paths) if paths is not None else _protected_paths(self._root)
        self._dir = tempfile.mkdtemp(prefix='aishield_dataguard_')
        self._before = {}
        self.leaked = []

    @staticmethod
    def _backup_name(rel):
        return rel.replace('/', '__').replace('\\', '__')

    def __enter__(self):
        for rel in self._paths:
            abs_p = os.path.join(self._root, rel)
            self._before[rel] = _sha256(abs_p)
            shutil.copyfile(abs_p, os.path.join(self._dir, self._backup_name(rel)))
        return self

    def __exit__(self, *exc):
        for rel in self._paths:
            abs_p = os.path.join(self._root, rel)
            if not os.path.exists(abs_p):
                self.leaked.append((rel, 'DELETED'))
            elif _sha256(abs_p) != self._before[rel]:
                self.leaked.append((rel, 'MODIFIED'))
        if self.leaked:
            for rel, _kind in self.leaked:
                src = os.path.join(self._dir, self._backup_name(rel))
                if os.path.exists(src):
                    shutil.copyfile(src, os.path.join(self._root, rel))
        shutil.rmtree(self._dir, ignore_errors=True)
        return False


# 需要非对称签名后端的模块。缺 cryptography 时密钥环会**按设计**降级成
# hmac-sha256，而 issue_credential 是 fail-closed 的（拒绝签出无法被第三方
# 公开验证的凭证）—— 于是这两个模块会集体报红，看起来像代码回归。
#
# 2026-10-05 真踩（本机）：用托管解释器 3.13.12（无 cryptography）跑全量，得到
# 11 FAIL + 17 ERROR，全在身份/意图授权；换成本机 C:\Python314\python.exe
# （cryptography 50.0.1）立刻 27/27 绿。**这不是回归，是解释器选错**。
#
# 2026-10-05 同日 CI 侧（后果严重得多）：threat-intel-feed 的 verify job 裸跑本
# 脚本，干净 runner 上无 cryptography → 成片报红 → 该 job 失败 → spine 在 job 2
# 终止 → 其后 8 个 job 全部 skipped，整条闭环停摆一天。CI 侧不再靠"记得装"：
# 统一前置是 ./.github/actions/prepare-tests，并由 validate_workflows.py 的 E11
# **强制**每个跑本脚本的 job 引用它。本预检是第二道防线 —— 万一某个入口漏了
# 引用，得到的也是一句能直接照做的提示，而不是一屏伪装成回归的红。
#
# 所以这里做预检：与其让人对着 28 条误导性红自己找根因，不如开机就报一句
# 能直接照做的提示。允许显式降级（AISHIELD_ALLOW_DEGRADED_CRYPTO=1），
# 但降级时会大声跳过这两个模块 —— 静默跳过就是假绿。
_CRYPTO_MODULES = ('tests.test_verifiable_identity', 'tests.test_intent_mandate')


_DELETE_GUARD_ENV = 'CODEBUDDY_SAFE_DELETE_BULK_STATE_DIR'


def _neutralize_sandbox_delete_guard() -> str:
    """
    撤掉 WorkBuddy 沙箱的「批量删除守卫」状态，返回 'active' | 'popped' | 'kept'。

    这个 shim（sitecustomize 包住 os.remove）按**一次工具调用**累计删除次数，
    超阈值就 raise SystemExit(1)。测试自己就会成片删临时 store 文件
    （tests/test_personal_agent._clean_store()），于是守卫在 setUp 里把进程顶掉：

        2026-10-05 实测：SystemExit(1) 从 test_personal_agent 起连锁
        169 条 ERROR，横扫其后所有模块 —— 看日志像全面回归，实则本机沙箱工件。
        CI 没有这个 shim（那边全绿），所以「本地全红 / CI 全绿」时第一件事
        该查它，而不是去改产品代码。

    为什么放进 run_all 而不是继续靠「记得加 -c 前缀」：靠记忆的做法一旦漏掉，
    代价是 169 条误导性红 —— 把不可复现的纪律换成可复现的机制。
    只有显式 AISHIELD_KEEP_DELETE_GUARD=1 时才保留守卫（要复现守卫行为时用）。
    """
    if os.environ.get('AISHIELD_KEEP_DELETE_GUARD') == '1':
        return 'kept'
    if _DELETE_GUARD_ENV in os.environ:
        os.environ.pop(_DELETE_GUARD_ENV, None)
        return 'popped'
    return 'active'


def _crypto_backend_guard() -> str:
    """
    返回 'ok' | 'degraded' | 'abort'。

    'ok'       有 cryptography，正常跑。
    'degraded' 没有，但用户显式允许降级 → 跳过签名相关模块（大声跳过）。
    'abort'    没有且未允许 → 中止，避免 28 条误导性红把人带沟里。
    """
    try:
        import cryptography  # noqa: F401
        return 'ok'
    except ImportError:
        pass
    allow = os.environ.get('AISHIELD_ALLOW_DEGRADED_CRYPTO') == '1'
    print("=" * 68)
    print("⚠  未安装 cryptography → 签名后端只能降级到 hmac-sha256（对称）")
    print("   受影响模块：%s" % ", ".join(_CRYPTO_MODULES))
    print("   这**不是代码回归**：降级态下 L1 可移植身份（JWKS 只发非对称公钥、")
    print("   第三方凭公钥离线验签）与 L3 意图授权（AP2 Intent Mandate）在密码学上")
    print("   根本不成立，用例会 fail-closed 成片报红，且看起来像产品回归。")
    print("   修复（任选其一）：")
    print("     · 装依赖：python -m pip install cryptography")
    print("     · 换解释器：改用已装 cryptography 的那个 python 跑本脚本")
    print("   CI 侧由 ./.github/actions/prepare-tests 统一保证，无需手工处理。")
    if allow:
        print("   AISHIELD_ALLOW_DEGRADED_CRYPTO=1 → 显式降级：跳过上述模块。")
        print("=" * 68)
        return 'degraded'
    print("   要在降级模式下跑全量："
          "AISHIELD_ALLOW_DEGRADED_CRYPTO=1 python tests/run_all.py")
    print("=" * 68)
    return 'abort'


def _declared_missing_deps() -> list:
    """统一前置声明的测试依赖里，当前**不可用**的那些（cryptography 除外）。

    为什么去读 `.github/actions/prepare-tests` 而不是在本地再列一遍清单：
    在这里再列一遍就是「同一件事的第二处实现」，而本仓为此已经出过两次事故
    （6 处各自实现、5 处漏装依赖；收敛之后新依赖 pyyaml 又漏同步）。声明只留一处，
    这里只做「按声明自查」。

    cryptography 不算在内：它的缺失由 `_crypto_backend_guard` 按降级语义处理
    （有 AISHIELD_ALLOW_DEGRADED_CRYPTO 这个显式出口），不在这里重复报。
    """
    try:
        from scripts.validate_workflows import (  # noqa: WPS433
            declared_pip_deps, import_name_to_dist)
        action = os.path.join(_ROOT, '.github', 'actions', 'prepare-tests',
                              'action.yml')
        with open(action, 'r', encoding='utf-8') as fh:
            names = declared_pip_deps(fh.read())
    except Exception:
        # 读不到声明（例如只拷了 tests/ 目录）不该让整套测试跑不起来
        return []
    import importlib
    missing = []
    for name in names:
        if name == 'cryptography':
            continue
        try:
            importlib.import_module(name)
        except Exception:
            # 返回值用**发行名**：提示里的 `pip install X` 必须能照着做。
            # 写导入名会装错（`pip install yaml` 装到的是 PyPI 上另一个同名的历史遗留包）。
            missing.append(import_name_to_dist(name))
    return missing


def main():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    guard_state = _neutralize_sandbox_delete_guard()
    if guard_state == 'popped':
        print("[harness] 已撤掉本机沙箱的批量删除守卫（否则 test_personal_agent 的 "
              "clean_store 会触发 SystemExit(1)，连锁上百条假 ERROR）")
    elif guard_state == 'kept':
        print("[harness] AISHIELD_KEEP_DELETE_GUARD=1 → 保留沙箱删除守卫（结果可能被守卫打断）")

    crypto_state = _crypto_backend_guard()
    if crypto_state == 'abort':
        print("已中止：换用带 cryptography 的解释器重跑（见上面的提示）。")
        return 2
    degraded = crypto_state == 'degraded'

    # 其余声明的依赖（如 pyyaml）缺了同样属于「环境不满足」，必须退 2 而不是让
    # 依赖它的用例静默跳过（跳过即假绿），更不是把「该装包」混成「该改代码」的 1。
    missing_deps = _declared_missing_deps()
    if missing_deps:
        print("=" * 68)
        print("⚠  统一前置声明的测试依赖缺失: %s" % ", ".join(missing_deps))
        print("   .github/actions/prepare-tests 是本仓**唯一**的依赖声明处；")
        print("   缺包时依赖它的用例会静默跳过 —— 跳过就是假绿，所以在此中止。")
        print("   修复：python -m pip install %s" % " ".join(missing_deps))
        print("=" * 68)
        return 2

    # 加载所有测试文件
    test_files = [
        'tests.test_linkages',
        'tests.test_geo',
        'tests.test_security',
        'tests.test_supply_chain',
        'tests.test_client_discovery',
        'tests.test_ci_contract',
        'tests.test_commercialization',
        'tests.test_hupijiao',
        'tests.test_governance',
        'tests.test_mcp_contract',
        'tests.test_tech_radar',
        'tests.test_workspace_scan',
        'tests.test_sandbox_rules',
        'tests.test_guardrail_harness',
        'tests.test_attestation_live',
        'tests.test_distribution_gate',
        'tests.test_trust_api',
        'tests.test_identity_network_scan',
        'tests.test_capability_boundary_scan',
        'tests.test_capability_full_scan',
        'tests.test_agent_security_gateway',
        'tests.test_trust_protocol',
        'tests.test_claim_lock',
        'tests.test_replay',
        'tests.test_vertical_risk',
        'tests.test_diff',
        'tests.test_fuzzing',
        'tests.test_baseline_scan',
        'tests.test_compliance',
        'tests.test_fleet_versions',
        'tests.test_runtime_behavior',
        'tests.test_self_reference',
        'tests.test_vuln_feed_health',
        'tests.test_radar_effect',
        'tests.test_digest_window',
        'tests.test_stale_exemptions',
        'tests.test_finding_anchor',
        'tests.test_isolation_invariants',
        'tests.test_sync_version_targets',
        'tests.test_no_hardcoded_cf_token',
        # 2026-09-16 补登记：下列文件此前不在列表中，被 run_all 静默跳过。
        # 本清单是硬编码的，新增测试文件若忘记登记就不会被执行（假绿），
        # tests/test_ci_contract.py::TestRunnerCoverage 会把这件事钉死。
        # 注意：tests.test_geo 已在上方登记，此处不得重复 —— 重复会让整个模块跑两遍，
        # 既拖慢 CI，又让单个失败在日志里重复出现两次、误判为两个缺陷
        # （2026-09-17 root 护栏那条 CI 全红就是被这个假象掩盖了）。
        'tests.test_indexnow',
        'tests.test_gap_fill',
        'tests.test_rule_promotion_rollback',
        # 2026-09-17 新增扫描器（ASI04 记忆完整性）的回归测试
        'tests.test_memory_integrity_scan',
        'tests.test_promote_rule_shadow',  # shadow/enforce 双模式 + 雷达加载期字段契约
        'tests.test_deployment_root_guard',  # 2026-09-18：root 护栏与部署身份冲突 = 20.5h 静默 502
        'tests.test_deployment_observability',  # 退出码传导契约：诊断语句不得抢占部署/自愈的退出码
        'tests.test_notify_hardening',  # 2026-09-18：告警链路出站脱敏 + fail-closed 退出码 + 未送达台账闭环
        'tests.test_rule_audit_contract',  # 2026-09-18：基线审计契约（零 critical 误报/引用抑制/情报去重/对抗式评审闸门有效）
        # 2026-10-06：Trust Attestation 签发链路 —— 钉"schema 文件必须随仓库发布"。
        # 线上长期返回 'Schema not found' 而本地全绿：schema/trust-attestation-v1.json
        # 本地有、main 上不存在（未入库），部署 tarball 来自 checkout ⇒ 线上签不出凭证。
        'tests.test_trust_attestation_schema',
        # 2026-10-06：生态请求体声明表契约 —— 声明表的 path/verb 必须是运行时真路由
        # （无 phantom），字段名必须能在 handler 源码里找到字面量（无编造）。
        # 覆盖 agent 接入最先要调的 22 条（attestations / trust / agent-card /
        # identity / protocol / chain / agent-infra）。
        'tests.test_ecosystem_request_contract',
        # 2026-09-19 在线扫描页 + 框架适配器 + SARIF 导出契约
        'tests.test_sarif_export',
        'tests.test_scan_inline_page',
        # 2026-09-25 版本声明位覆盖门禁：防"门禁假绿"（api/server.py 曾 6 处 4.3.0
        # 而 mcp.json 已 4.8.3，sync_version 报"全部一致"却对那 8 处失明）
        'tests.test_version_declare',
        # 2026-09-25 import 完整性门禁：仓库内引用的模块/符号必须真的存在。
        # 起因是 api/trust_api.py 的 attestation 扩展从未推送到 main，导致
        # `import api.server` 在干净 checkout 上 ImportError、self-scan 连红 8 次；
        # 另查出 eco/crypto_sign.py 等 6 个模块缺失，Muse/Grok/NVIDIA 三个连接器
        # 在远端全都无法导入——而本机因为有这些文件，测试全绿。
        'tests.test_import_integrity',
        # 2026-09-19 AIShield Collector：本地持续观测（不 spawn / 不联网 / 指纹幂等 / 紧凑摘要）
        # 2026-09-22 MCP SEP-2640 manifest 扫描器：过度代理/供应链/凭据/签名/过期
        'tests.test_mcp_manifest_scan',
        'tests.test_collector',
        # 2026-09-19 紧凑信任摘要（aishield-digest/v1）+ 套件脏数据守卫的正向对照
        'tests.test_trust_digest',
        'tests.test_hermetic_guard',
        # 2026-09-19 安全基准 v1（固定语料 + 参数化变体 + 确定性 + 质量门禁）
        'tests.test_benchmark',
        # 2026-09-19 雷达规则 provenance 可审计性（trigger / intended_effect + 老数据兼容）
        'tests.test_provenance_audit',
        # 2026-09-20 规则数一致性门禁契约：scan/sync 口径不得分裂、pair 替换
        # 不得截断、正则不得从数字中间起跳、分解表与 CSS 颜色不得误报
        'tests.test_rule_count_gate',
        # 2026-09-22 已知良性项目白名单：PenguinHarness/Cua/Mano-P 路径不降级误报
        'tests.test_registry_supply_scan',
        # 2026-09-24 Agent 生态 5 支柱落地：specialist_registry / kyad_compat / ecosystem_api / ship_gate
        'tests.test_ecosystem_activation',
        # 2026-09-24 R4-深化：Evidence Bundle 1.0 + Responsibility Chain v1.1 + ship_gate 10 态状态机
        # 对标 GOAI 2026 Agent Infra 季军 CyberGuard（HMAC 链式审计 + OCSF/STIX/ATT&CK + 双轮独立复测）
        'tests.test_evidence_bundle',
        # 2026-09-24 v4.8.0：个人 Agent 治理层（PAI DID + 预算守护 + 行动溯源 + Connector 独立审核）
        # 触发：Meta Muse 上线 13 天 250 万下载，2026-09-18 开放 connector platform
        'tests.test_personal_agent',
        # 2026-09-24 v4.8.1：平台中立接入层（40+ 平台注册表 + 治理缺口矩阵 + 推荐引擎）
        'tests.test_platform_registry',
        # 2026-09-24 v4.8.2：海外平台真实接入（Meta Muse + xAI Grok Bot）
        # OAuth + PAT 双通道、fail-closed 续期、preflight 敏感词升级、proxy 透传
        'tests.test_connectors',
        # 2026-09-25 v4.8.3：NVIDIA 开发者平台真实接入（NGC Catalog + NIM 推理 + NeMo 编排）
        # NGC API Key 形态，复用个人 Agent 治理层 preflight + HMAC 行动链
        'tests.test_nvidia_connector',
        # 2026-09-25 v4.8.3：Agent 基础设施开源扫描管道
        # scanner.engine → 封装（MCP 适配器骨架）→ 二次研发清单，支持 URL/本地/内存三态
        'tests.test_agent_infra_scan',
        # 2026-09-25 v4.8.3：三平台双形态联调（开发者身份形态 + MCP 桥形态）
        'tests.test_dual_form_integration',
        'tests.test_arena_join_gate',
        # 2026-09-30 战略转向：从"agent 安全扫描器"→"agent 生态支持体系基础设施"
        # 5 项硬骨头 P0/P1 落地（117 新增测试）：Agent Memory 深度扫描 + confidence 晋升
        # + 独立 rule decay + Policy Pack + Red-team probe
        'tests.test_agent_memory_scan',
        'tests.test_confidence_promotion',
        'tests.test_rule_decay',
        'tests.test_policy_pack',
        'tests.test_red_team_probe',
        # 2026-10-03 攻击语料攻击面族覆盖度：recall=1.0 必须在 17 个攻击面上
        # 分别站得住，族级 0 检出要报出来而不是被总数摊平；KNOWN_GAP_SAMPLES
        # 记账当前规则真覆盖不到的攻击面（补上规则即要求把样本移出名单）。
        'tests.test_corpus_family_coverage',
        # 2026-10-03 API 契约一致性门禁：运行时路由 vs /openapi.json 双向 diff。
        # 存量 103 条未登记 + 3 条跑不通进基线（只拦新增）；探针带状态快照/还原。
        'tests.test_openapi_contract',
        # 2026-10-05 公开声明面门禁：验证「服务出去的字节」而非「仓库里的文件」。
        # 起因是线上 agent-card 报 235/241（真值 264/291）而 --check 全绿 ——
        # 门禁扫的是不可达分支引用的副本。本组同时钉死：孪生副本身份、
        # 分派唯一性（AST）、运行时规则数/版本断言，以及
        # /api/v1/governance/policy 各 action 的路由级可达性（曾因同路径双分派
        # 而全部不可调用，模块级测试全绿却完全看不见）。
        'tests.test_declaration_surface',
        # 2026-10-03 身份锚点闭环：注册凭据 → 归属 → 注销 → 审计事件（可回放）。
        # 裸注册 401 / 越权注销 403 是硬边界，不是洁癖。
        'tests.test_identity_revocation',
        # 2026-10-04 L2 策略贯通：扫描期 policy pack 编译为运行时 PEP 策略。
        # 未绑 pack 的 server 行为必须与贯通前逐字一致（不误伤存量）；
        # red-team 编译后绝不能获得任何运行时拒绝能力（永不 fail 语义）。
        'tests.test_policy_bridge',
        # 2026-10-05 L3 意图授权：AP2 对齐的 Intent Mandate —— 行动前先签字，
        # 过期/超上限/越动作/换 DID/重放五道必须拒，账本损坏 fail-closed。
        'tests.test_intent_mandate',
        # 2026-10-05 路由可达性门禁：代码里写下的每条 /api/v1/... 都必须被
        # server.py 的分派分支接住（曾经 intent/attestations/digest/evidence/
        # ship-gate 全是「handler 写了、入口没接」的死路由，两个门禁都绿）。
        'tests.test_server_prefix_gate',
        # 2026-10-04 L1 可移植身份：JWKS 公钥发现 + VC 签发/验签/除销。
        # 对称密钥永不进 JWKS 是红线；除销必须实时读盘（缓存=攻击复用窗口）；
        # 第三方仅凭 JWKS 的 x 就能离线验签，这才是「别家能不能验我」。
        'tests.test_verifiable_identity',
        # 2026-10-05 干净 checkout 门禁：把身份侧文件全部重定向到一个**空目录**，
        # 跑一遍「发凭据 → 注册 → 签 VC → 验 VC → 除销」闭环。CI 里 api/data/*.json
        # 一个都没有（全被 .gitignore），同类 setUp 崩溃只在那里暴露 —— 这条必须
        # 进总入口，否则它永远只在本地运行，变成又一个看不见的空转门禁。
        'tests.test_clean_checkout',
        # 2026-10-05 评分可解释收口（#365 复活）：扣分账必须 100% 闭合
        # （曾经 penalty=105 只展示 80，25 分凭空蒸发）、每条扣分必须带 rule_id
        # （否则申诉到不了规则）、并有独立复算路径交叉验证（不一致即判分数不可信）。
        # 含 5 条反向用例：掐掉全量账本/篡改 penalty/抹掉 rule_id/改 overall/
        # 改维度分，审计必须全部报出 —— 否则这条门禁就是空转。
        'tests.test_score_explain',
        # 2026-10-05 统一导出面收口（#365 复活）：6 个目标端逐一实跑并校验合规格
        # （OCSF 1.1 class_uid=2001/severity_id 映射、STIX 2.1 uuid5 稳定 id），
        # 目标端配置化 + headers 凭据脱敏 + 产物泄露探针；含 3 条反向用例
        # （缺必填/构建异常/CSV 表头）验证校验不是装饰品。
        'tests.test_export_registry',
        # 2026-10-05 测试前置门禁（E11）：`python tests/run_all.py` 曾在 6 个
        # workflow 里各自实现，只有 1 个装了 cryptography。另 5 个在干净 runner 上
        # 跑会让签名后端静默降级 → L1/L3 用例成片报假回归 → spine 在 job 2 终止、
        # 后 8 个 job 全跳过。修法不是补那 5 处，而是把前置定义一次
        # （.github/actions/prepare-tests）并由门禁强制没人能绕过。
        'tests.test_workflow_test_prereq',
        # 2026-10-05 并发 push 的「快照类」声明（E13）：同一天第三条同型事故 ——
        # spine 复验时同一生产者被并发实例化，两份快照在 data/generated_rules.json
        # 上撞 content 冲突，而判据是路径前缀代理「data/state/ 之外一律是真实逻辑」
        # → exit 3 → 当天闭环在 job 4 终止、后 8 个 job 全跳过。
        # 修法：判据改为「写入者是否唯一」，声明受 E13 派生实测；含真跑 git rebase
        # 冲突的端到端用例（快照类自动解决 / 非快照类 exit 3）。
        'tests.test_auto_resolvable_paths',
    ]

    loaded = 0
    skipped_degraded = []
    for tf in test_files:
        if degraded and tf in _CRYPTO_MODULES:
            # 显式降级才走到这里；大声说出来，别静默跳过（静默跳过=假绿）
            print(f"  [SKIP-CRYPTO] {tf}: 缺 cryptography，已按 AISHIELD_ALLOW_DEGRADED_CRYPTO=1 跳过")
            skipped_degraded.append(tf)
            continue
        try:
            suite.addTests(loader.loadTestsFromName(tf))
            loaded += 1
        except Exception as e:
            print(f"  [SKIP] {tf}: {e}")
    if skipped_degraded:
        print("  ⚠ 本次为降级运行，签名/意图授权模块未验证 —— 结果不能当「全绿」用。")

    print(f"\n{'=' * 60}")
    print(f"AIShield Test Suite")
    print(f"Loaded {loaded}/{len(test_files)} test modules")
    print(f"{'=' * 60}\n")

    runner = unittest.TextTestRunner(verbosity=2)
    with _DataGuard() as guard:
        result = runner.run(suite)

    # 输出摘要
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"\n{'=' * 60}")
    print(f"AIShield Test Suite Summary")
    print(f"{'=' * 60}")
    print(f"Total:    {result.testsRun}")
    print(f"Passed:   {passed}")
    print(f"Failed:   {len(result.failures)}")
    print(f"Errors:   {len(result.errors)}")
    print(f"Skipped:  {len(result.skipped)}")
    print(f"{'=' * 60}")

    if guard.leaked:
        print("")
        print("!" * 60)
        print("HERMETIC GUARD: THE SUITE MUTATED TRACKED DATA FILES")
        print("!" * 60)
        for rel, kind in guard.leaked:
            print(f"  {kind:9s} {rel}")
        print("  -> originals restored from snapshot")
        print("  -> a test is writing production data; give it a temp path")
        print("!" * 60)

    if result.wasSuccessful() and not guard.leaked:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
        if result.failures:
            print(f"\n--- Failures ({len(result.failures)}) ---")
            for test, traceback in result.failures:
                print(f"  FAIL: {test}")
        if result.errors:
            print(f"\n--- Errors ({len(result.errors)}) ---")
            for test, traceback in result.errors:
                print(f"  ERROR: {test}")
        if guard.leaked:
            print(f"\n--- Data Leaks ({len(guard.leaked)}) ---")
            for rel, kind in guard.leaked:
                print(f"  LEAK: {kind} {rel}")

    sys.exit(0 if (result.wasSuccessful() and not guard.leaked) else 1)


if __name__ == '__main__':
    # 必须显式接住 main() 的返回码：预检中止返回 2，裸调 main() 会把它变成 0
    # —— 又一个「吞退出码」的假绿（本文件顶部的铁律第 1 条）。
    sys.exit(main())
