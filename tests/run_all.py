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


def main():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

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
        # 2026-10-03 身份锚点闭环：注册凭据 → 归属 → 注销 → 审计事件（可回放）。
        # 裸注册 401 / 越权注销 403 是硬边界，不是洁癖。
        'tests.test_identity_revocation',
    ]

    loaded = 0
    for tf in test_files:
        try:
            suite.addTests(loader.loadTestsFromName(tf))
            loaded += 1
        except Exception as e:
            print(f"  [SKIP] {tf}: {e}")

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
    main()
