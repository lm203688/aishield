#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公开声明面门禁 —— 校验「服务出去的字节」，而不是「仓库里的文件」。

问题
----
2026-10-05 实测：

    curl https://aishield.tools/.well-known/agent-card.json
    → "against 235 MCP / 241 skill rule categories"   （真值 264 / 291）

    python scripts/rule_count_gate.py --check
    → ✅ 全部一致，无漂移

两句都是真话。真服务的文件（docs/.well-known/agent-card.json）掉在规则数门禁
之外；门禁扫的 api/static 副本由一个**不可达分支**引用、永不服务。于是
"文件里的数字"全对，"服务出去的数字"全错，而没有任何一处报警。

为什么原有门禁都拦不住
----------------------
版本门禁（sync_version.py）与规则数门禁（rule_count_gate.py）的**验证对象
都是文件**。只要服务路径与文件路径之间存在哪怕一层间接（两处 if 顺序、
两个根目录各躺一份、一个不可达分支），"文件正确"就推不出"服务正确"。
这不是某个模式写漏了，而是**验证层选错了对象**。

本门禁把验证对象上移到**运行时响应**：

  1. 注册表完整性     每个在册 URL 的服务文件存在
  2. 孪生身份审计     两根下的同名文件必须显式登记身份（拦死副本复生）
  3. 分派唯一性(AST)  同一 URL 在**同一个分派函数**里不得声明两次
                      （拦"同 URL 双 if、靠先后顺序隐式决定谁生效"）。
                      扫描范围**从 api/ 派生**（凡定义 do_*/handle_* 的模块），
                      不是手工文件清单 —— 清单会漏掉新增的 api/xxx_api.py
  4. 门禁覆盖闭合     被服务的声明面文件必须落在规则数/版本门禁的覆盖范围内
                      —— 判据**派生自** `rule_count_gate.collect_files()`，
                      不再手抄它的条件（旧实现只抄了路径白名单，漏掉后缀
                      白名单，`.xml` 因此两代无人发现）
  5. 豁免台账自证     每处门禁豁免必须写明理由且文件真实存在
                      （豁免=特权；能悄悄变大的豁免表 = 门禁关掉一半）
  6. 运行时内容断言   直调 handler 取真实响应 → 规则数/版本必须等于权威值
                      （**这一条才是根治**：服务面错了就红，不管代码怎么重构）

判据与出口
----------
退出码：0 = 通过；1 = 检出问题；2 = 门禁自身异常（探针起不来、注册表读不到）。
2 必须与 1 区分：门禁自己坏掉却报"通过"，是假绿的第 1 层。

用法
----
    python scripts/declaration_surface_gate.py            # 报告
    python scripts/declaration_surface_gate.py --check    # CI 门禁
    python scripts/declaration_surface_gate.py --json     # 机器出口
    python scripts/declaration_surface_gate.py --no-probe # 只做静态部分（离线）
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "scripts"))

# 分派函数白名单：只有这些函数里的 URL 字面量参与"唯一性"判定。
# 收窄是刻意的 —— 助手函数里重复出现同一个 URL（比如拼日志）不算缺陷，
# 把那些也判红会逼人加豁免，豁免多了门禁就成摆设。
_DISPATCH_FUNCS = (
    "do_GET", "do_POST", "do_DELETE", "do_HEAD", "do_PUT", "do_PATCH",
    "handle_get", "handle_post", "handle_delete",
)

# 参与分派唯一性扫描的模块 —— **从 api/ 派生，不是手工清单**。
# 手工清单的代价（2026-10-06 点明，见 AGENTS.md 不变量 8）：覆盖面只要靠人
# 维护，新增一个 `api/xxx_api.py` 就会掉在外面，而"掉在外面"没有任何信号。
# 判据改为：凡在 api/ 下、且定义了任一 _DISPATCH_FUNCS 的模块，一律纳入。
# 实测（2026-10-06）派生结果与原手工清单**完全一致**（6/6，零缺失零多余），
# 因此这是一次零行为变化的净改进。
_DISPATCH_SCAN_ROOT = "api"


def _dispatch_modules(root=None):
    """派生参与分派唯一性扫描的模块（仓库相对 POSIX 路径，已排序）。

    ``root`` 默认 ``REPO/api``；测试传临时目录即可验证"新模块会被自动纳入"，
    不必往真实 api/ 里写文件。

    返回空集合是**异常**而非"没问题"：分母为零意味着这项检查会在全绿里
    空转（假绿的一层）。调用方 check_dispatch_uniqueness 据此报错。
    """
    api_root = root or os.path.join(REPO, _DISPATCH_SCAN_ROOT)
    out = []
    for dirpath, dirnames, filenames in os.walk(api_root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in sorted(filenames):
            if not fn.endswith(".py"):
                continue
            full = os.path.join(dirpath, fn)
            try:
                with open(full, encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=fn)
            except (OSError, SyntaxError):
                continue
            names = {n.name for n in ast.walk(tree)
                     if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            if names & set(_DISPATCH_FUNCS):
                try:
                    label = os.path.relpath(full, REPO).replace(os.sep, "/")
                except ValueError:            # 跨盘符（Windows 上可能）
                    label = full.replace(os.sep, "/")
                out.append(label)
    return tuple(sorted(out))


class Finding:
    __slots__ = ("check", "target", "detail", "severity")

    def __init__(self, check, target, detail, severity="error"):
        self.check = check
        self.target = target
        self.detail = detail
        self.severity = severity

    def as_dict(self):
        return {"check": self.check, "target": self.target,
                "detail": self.detail, "severity": self.severity}


def _rule_gate():
    """门禁使用的规则数门禁模块对象。

    抽成函数是刻意的：本仓库里 ``scripts.rule_count_gate``（测试按包名导入）
    与 ``rule_count_gate``（门禁按模块名导入，因为它既要能当脚本跑、又要能被
    import）**是两个不同的模块实例**。测试若改了错的那一个，被改的状态对
    门禁不可见，断言的"绿"就是假的 —— 这正是假绿的一层，且极难自查。
    统一从这里取，测试注入与生产运行才面对同一个对象。
    """
    import rule_count_gate as rcg
    return rcg


# ════════════════════════════════════════════════════════════════════════
# 1. 注册表完整性
# ════════════════════════════════════════════════════════════════════════
def check_registry_files():
    from api.declaration_surface import SERVED, abs_path
    out = []
    for url, s in sorted(SERVED.items()):
        if s.kind == "computed":
            continue
        if not s.rel:
            out.append(Finding("registry_files", url,
                               "kind!=computed 却没有服务文件路径"))
            continue
        if not os.path.isfile(abs_path(s.rel)):
            out.append(Finding("registry_files", url,
                               f"服务文件不存在: {s.rel}"))
    return out


# ════════════════════════════════════════════════════════════════════════
# 2. 孪生身份审计
# ════════════════════════════════════════════════════════════════════════
def check_twin_identity():
    """两根下同相对路径并存 → 孪生文件必须在台账里写明身份。

    这条是 235/241 漂移的**机械拦截**：当时 docs/ 与 api/static/ 各躺一份
    .well-known/agent-card.json，谁生效无人知晓，两份各漂各的。
    只要"同名并存且身份不明"一律判红，这类问题就不可能再悄悄长大。
    """
    from api.declaration_surface import SHADOWS, iter_twins, served_by, abs_path
    out = []
    for served_rel, twin_rel, url in iter_twins():
        twin_rel = twin_rel.replace(os.sep, "/")
        if twin_rel in SHADOWS:
            continue
        # 两根下都存在、但没有任何一份在册 → 连"谁被服务"都定义不出来
        if not served_rel:
            out.append(Finding(
                "twin_identity", url,
                f"{twin_rel} 与同名文件并存，但两份都不在 SERVED 注册表里 —— "
                f"该 URL 的服务者未定义"))
            continue
        out.append(Finding(
            "twin_identity", url,
            f"孪生文件 {twin_rel}（与在册的服务副本 {served_rel} 同相对路径）"
            f"未在 SHADOWS 台账登记身份。"
            f"身份不明的孪生副本正是声明面漂移的温床：要么登记为 "
            f"mirror/superseded/leftover，要么删掉。"))

    # 台账里的条目也要真实存在，否则台账会烂成愿望清单
    for rel, sh in sorted(SHADOWS.items()):
        if not os.path.exists(abs_path(rel)):
            out.append(Finding(
                "twin_identity", sh.url,
                f"SHADOWS 登记的 {rel} 已不存在，请从台账移除（死台账会掩盖新孪生）",
                severity="warn"))
        elif served_by(rel):
            out.append(Finding(
                "twin_identity", sh.url,
                f"{rel} 既在 SERVED 又登记为 SHADOWS，身份自相矛盾"))
    return out


# ════════════════════════════════════════════════════════════════════════
# 3. 分派唯一性（AST）
# ════════════════════════════════════════════════════════════════════════
def _url_literals_in_compare(node: ast.AST):
    """收集某个函数体里**参与比较**的 URL 字符串字面量。

    只按函数形参名收集是错的 —— 这条踩过：真实分派函数写成
    ``def do_GET(self): path = parsed.path; if path == "...":``，
    `path` 是局部变量而非形参，于是按形参过滤后一个都收不到，
    **整个检查静默空转**（门禁自己假绿，比不做检查更危险，因为它会让人
    以为这一类缺陷已经受控）。是 tests/test_declaration_surface.py 的
    合成反向用例把它掀出来的。

    同时**只取 Compare 的直接操作数**，不递归进操作数内部。这两条都是实测
    逼出来的：

      * 递归进 BinOp 会把 ``path == "/" + key + ".txt"`` 里的 ``"/"`` 当成
        "URL / 被比较两次"，与 ``if path == "/":``（首页）撞在一起误报；
      * 递归进 JoinedStr 会把 f-string 的常量片段当独立 URL：
        ``path == f"/api/v1/connectors/{p}/self-check"`` 与
        ``.../state`` 的公共前缀 ``/api/v1/connectors/`` 被算成重复声明 ——
        那是两个不同端点，完全合法。

    代价：f-string 拼接出来的路径不参与唯一性判定。可接受 —— 这种写法的
    "字面量"本就是片段而非 URL，拿它判重必然误报；而真正会制造不可达分支的
    是 ``==`` 精确路径比较，那部分完整覆盖。
    """
    found = []
    for n in ast.walk(node):
        if not isinstance(n, ast.Compare):
            continue
        for o in [n.left] + list(n.comparators):
            if isinstance(o, ast.Constant) and isinstance(o.value, str) \
                    and o.value.startswith("/"):
                found.append(o.value)
    return found


def dispatch_duplicates(src: str, label: str):
    """AST 扫描一段源码：同一分派函数里重复比较同一 URL → findings。

    抽成纯函数（输入源码字符串）是为了让测试能喂**合成代码**做反向验证 ——
    否则"门禁不是空转"就只能靠改真实文件来证明，那种验证在 CI 里做不了。
    """
    out = []
    try:
        tree = ast.parse(src, filename=label)
    except SyntaxError as e:
        return [Finding("dispatch_unique", label, f"AST 解析失败: {e}")]
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if fn.name not in _DISPATCH_FUNCS:
            continue
        seen = {}
        for u in _url_literals_in_compare(fn):
            seen[u] = seen.get(u, 0) + 1
        for u, cnt in sorted(seen.items()):
            if cnt > 1:
                out.append(Finding(
                    "dispatch_unique", f"{label}:{fn.name}",
                    f"URL {u} 在同一个分派函数里被比较 {cnt} 次 —— "
                    f"先命中者胜，后面的分支不可达。"
                    f"声明面必须**只有一个**处理点，"
                    f"否则门禁可能覆盖到死分支。"))
    return out


def check_dispatch_uniqueness():
    """同一 URL 在同一分派函数里只能被比较一次。

    这正是 2026-10-05 缺陷的形状：do_GET 里既在 Trust 分支比较了
    /.well-known/agent-card.json 并 return，又在后面静态分支比较了同一个
    URL —— 后者永远不可达，且门禁覆盖的恰好是后者的文件。
    """
    out = []
    modules = _dispatch_modules()
    if not modules:
        # 分母为零 ≠ 没问题：这一项会变成永远绿的装饰。
        out.append(Finding(
            "dispatch_unique", f"{_DISPATCH_SCAN_ROOT}/",
            "派生出的分派模块集合为空 —— 本项检查会在全绿里空转。"
            "先确认 api/ 可读、且 _DISPATCH_FUNCS 未被改坏。"))
        return out
    for rel in modules:
        full = os.path.join(REPO, rel)
        if not os.path.isfile(full):
            continue
        try:
            with open(full, encoding="utf-8") as f:
                src = f.read()
        except OSError as e:
            out.append(Finding("dispatch_unique", rel, f"读取失败: {e}"))
            continue
        out += dispatch_duplicates(src, rel)
    return out


# ════════════════════════════════════════════════════════════════════════
# 4. 门禁覆盖闭合
# ════════════════════════════════════════════════════════════════════════
def coverage_findings(entries, collected, exempt, patterns):
    """纯函数：在册服务面里，哪些**声明了数字却掉在门禁覆盖面外**。

    判据必须是**派生的** —— ``collected`` 只能来自
    ``rule_count_gate.collect_files()`` 本身，不能在这里复写它的条件。

    为什么把这条单拎出来：覆盖面由**两处手工白名单**合成（``TEXT_EXT`` 后缀
    表 ∧ ``_is_declared_surface`` 路径表）。旧实现只复写了后一半，于是
    ``.xml`` 不在元组里这件事整整两代无人发现 —— `api/static/feeds.xml`
    一直被别人扫、被服务、却从不被门禁扫，最终是运行时探针掀出来的。
    只要还有人"手抄一半条件"，这类漏网就会以别的扩展名/目录重演。
    因此这里改为：**问权威函数要集合，只对它做集合运算。**

    参数
    ----
    entries   ``[(url, rel, text), ...]`` 在册的非计算型服务面
    collected 规则数门禁真正会扫的文件集合
    exempt    豁免台账（路径 → 理由）
    patterns  规则数声明模式（来自 ``rule_count_gate._patterns()``）
    """
    out = []
    rcg = _rule_gate()
    for url, rel, text in entries:
        if rel in collected or rel in exempt:
            continue
        if not any(p.search(text) for p, _ in patterns):
            # 不承载声明数字的资产（robots.txt / manifest.json …）本来就
            # 不需要被规则数门禁覆盖，强行纳入只会把门禁噪音化。
            continue
        why = []
        if not rel.endswith(tuple(rcg.TEXT_EXT)):
            why.append(f"后缀不在 TEXT_EXT {tuple(rcg.TEXT_EXT)}")
        if not rcg._is_declared_surface(rel):
            why.append("路径不在 _is_declared_surface 白名单")
        out.append(Finding(
            "gate_coverage", url,
            f"{rel} 对外服务且声明了规则数，却不在 rule_count_gate 的覆盖面内"
            f"（{'; '.join(why) or 'collect_files() 未收录，原因需查'}）"
            f"—— 服务面漏出验证面：该 URL 的数字将来漂移时没有任何门禁会报警。"))
    return out


def check_gate_coverage():
    """被服务的声明面文件必须落在规则数门禁的覆盖范围内。

    "服务面 ⊆ 验证面"是这套体系的最低要求：服务出去的东西没人管，
    等于对外承诺失去了任何一致性保证。
    """
    rcg = _rule_gate()
    from api.declaration_surface import SERVED, abs_path
    out = []
    entries = []
    for url, s in sorted(SERVED.items()):
        if s.kind == "computed" or not s.rel:
            continue
        rel = s.rel.replace(os.sep, "/")
        try:
            with open(abs_path(rel), encoding="utf-8-sig", errors="replace") as f:
                text = f.read()
        except OSError as e:
            out.append(Finding("gate_coverage", url, f"读取失败: {e}"))
            continue
        entries.append((url, rel, text))

    # 唯一判据来源：门禁自己的收集函数。刻意不在这里重算 ext/surface 条件。
    out += coverage_findings(entries, set(rcg.collect_files()),
                             dict(rcg.EXCLUDE_FILES), rcg._patterns())
    return out


# ════════════════════════════════════════════════════════════════════════
# 5. 豁免台账自证
# ════════════════════════════════════════════════════════════════════════
def check_exempt_ledger():
    """EXCLUDE_FILES 的每一处豁免都必须写明理由，且文件真实存在。

    豁免 = 把某个对外资产从门禁里拿出去。若豁免表能悄悄变大，门禁就等于
    被关掉一半 —— 这是假绿的第 2 层（"退化成空集合"的孪生形态）。
    因此豁免必须自证，死豁免必须清掉（死豁免会掩盖同路径的新漏网）。
    """
    rcg = _rule_gate()
    out = []
    for severity, msg in rcg.exempt_table_errors():
        out.append(Finding("exempt_ledger", "rule_count_gate.EXCLUDE_FILES",
                           msg, severity=severity))
    return out


# ════════════════════════════════════════════════════════════════════════
# 5. 运行时内容断言
# ════════════════════════════════════════════════════════════════════════
def _api_version() -> str:
    """取唯一版本事实源。

    必须在 _library_quiet 里 import：api.server 的依赖链会打一行
    "[ProxyGateway] 已加载 N 个已认证工具" 到 stdout。`--json` 出口混进这行
    就等于交付了一个不是 JSON 的 JSON，机器解析直接炸 —— 门禁自己写坏、
    跑得绿但不给机器用，是比报错更糟的一种失败。openapi_contract.py 已经
    为此维护了 _library_quiet，这里复用它而不是另写一份。
    """
    import openapi_contract as oc
    with oc._library_quiet():
        from api.server import API_VERSION
    return API_VERSION


def runtime_rules_findings(url: str, rel: str, body: str, auth, patterns,
                           excluded_files=()):
    """对一段**响应体**做规则数断言。抽成纯函数以便测试喂合成响应。

    历史发布日志例外：llms-full.txt 里的 "214-rule base" 记录的是那个版本
    当时的真实基线，改掉等于伪造历史。规则数门禁用 EXCLUDE_FILES 表达这条
    豁免，这里必须沿用同一份名单，否则"运行时口径比文件口径更严"会制造一批
    改不掉的假红 —— 而改不掉的假红，最终会被人用豁免抹掉，等于没有门禁。
    """
    rcg = _rule_gate()
    rel = (rel or "").replace(os.sep, "/")
    if rel and rel in excluded_files:
        return []
    out = []
    for h in rcg.scan_text(f"GET {url}", body, auth, patterns):
        if h["kind"] == "pair":
            detail = (f"响应体声明 {h['got']['mcp']}/{h['got']['skill']} 规则，"
                      f"权威值 {h['expected']['mcp']}/{h['expected']['skill']}"
                      f"（{h['match']!r}）")
        else:
            detail = (f"响应体声明 {h['got']}，权威值 {h['expected']}"
                      f"（{h['match']!r}）")
        out.append(Finding("runtime_rules", url, detail))
    return out


def version_finding(url: str, body: str, version_path, version):
    """对一段响应体做版本断言，返回 Finding 或 None。

    只在资产**显式声明了版本路径**时才检查。让门禁去猜"这个文件该不该有
    版本号"会产生一整片无法处理的告警（jwks/manifest/geo-faqs 本来就不带
    版本），告警一多就没人看，等于没有门禁。
    """
    try:
        doc = json.loads(body)
    except ValueError as e:
        return Finding("runtime", url, f"响应不是合法 JSON: {e}")
    node = doc
    for key in version_path:
        node = node.get(key) if isinstance(node, dict) else None
    if not isinstance(node, str) or not node:
        return Finding("runtime_version", url,
                       f"响应缺少 {'/'.join(version_path)} —— "
                       f"agent 无法判断该声明属于哪个版本")
    if node != version:
        return Finding("runtime_version", url,
                       f"响应 {'/'.join(version_path)}={node}，API_VERSION={version}")
    return None


def check_runtime(do_probe: bool = True):
    """对每个在册 URL 发一次真实请求，校验**响应体**。

    这是本门禁存在的理由：前四条都在"仓库里"，只有这条在"服务出去之后"。
    """
    from api.declaration_surface import SERVED
    rcg = _rule_gate()
    import openapi_contract as oc

    out = []
    if not do_probe:
        return out

    auth = rcg.authority()
    patterns = rcg._patterns()
    try:
        version = _api_version()
    except Exception as e:  # noqa: BLE001
        out.append(Finding("runtime", "api.server", f"取 API_VERSION 失败: {e}"))
        return out

    with oc.hermetic_state():
        for url, s in sorted(SERVED.items()):
            status, body = oc._probe_one(url, "GET")
            if status != 200:
                out.append(Finding(
                    "runtime", url,
                    f"探针返回 {status}（期望 200）—— 在册声明面实际不可服务"))
                continue

            # 响应体里的规则数必须等于权威值。这里扫的是**响应文本**，
            # 与规则数门禁共用同一套模式与同一份权威值 —— 刻意不让两边
            # 各写一份口径，那正是"生成器与门禁两种口径、差集永远对不上"
            # （见 openapi_contract._is_hit 的注释）的翻版。
            out += runtime_rules_findings(
                url, s.rel, body, auth, patterns,
                excluded_files=rcg.EXCLUDE_FILES)

            if s.version_path:
                f = version_finding(url, body, s.version_path, version)
                if f:
                    out.append(f)
    return out


# ════════════════════════════════════════════════════════════════════════
def run_checks(do_probe: bool = True):
    findings = []
    findings += check_registry_files()
    findings += check_twin_identity()
    findings += check_dispatch_uniqueness()
    findings += check_gate_coverage()
    findings += check_exempt_ledger()
    findings += check_runtime(do_probe=do_probe)
    return findings


_CHECK_ORDER = ("registry_files", "twin_identity", "dispatch_unique",
                "gate_coverage", "exempt_ledger",
                "runtime_rules", "runtime_version", "runtime")

_CHECK_TITLES = {
    "registry_files": "1. 注册表完整性",
    "twin_identity": "2. 孪生副本身份",
    "dispatch_unique": "3. 分派唯一性（AST）",
    "gate_coverage": "4. 门禁覆盖闭合（派生）",
    "exempt_ledger": "5. 豁免台账自证",
    "runtime_rules": "6. 运行时规则数断言",
    "runtime_version": "7. 运行时版本断言",
    "runtime": "8. 运行时可达性",
}


def main() -> int:
    ap = argparse.ArgumentParser(description="公开声明面门禁")
    ap.add_argument("--check", action="store_true", help="CI 模式：有 error 即 exit 1")
    ap.add_argument("--json", action="store_true", help="机器出口")
    ap.add_argument("--no-probe", action="store_true", help="跳过运行时探针")
    args = ap.parse_args()

    try:
        findings = run_checks(do_probe=not args.no_probe)
    except Exception as e:  # noqa: BLE001
        # 门禁自身坏掉必须 exit 2，绝不能退化成"没找到问题"
        payload = {"ok": False, "gate_error": f"{type(e).__name__}: {e}"}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"❌ 门禁自身异常：{type(e).__name__}: {e}", file=sys.stderr)
        return 2

    errors = [f for f in findings if f.severity == "error"]
    warns = [f for f in findings if f.severity == "warn"]

    if args.json:
        print(json.dumps({
            "ok": not errors,
            "error_count": len(errors),
            "warning_count": len(warns),
            "findings": [f.as_dict() for f in findings],
        }, ensure_ascii=False, indent=2))
        return 1 if (errors and args.check) else 0

    from api.declaration_surface import SERVED, SHADOWS
    print("公开声明面门禁（验证「服务出去的字节」，不只是仓库里的文件）")
    print("=" * 64)
    print(f"在册服务面 {len(SERVED)} 个 · 孪生台账 {len(SHADOWS)} 条 · "
          f"探针 {'跳过' if args.no_probe else '已启用'}")

    by_check = {}
    for f in findings:
        by_check.setdefault(f.check, []).append(f)

    for ck in _CHECK_ORDER:
        items = by_check.get(ck)
        title = _CHECK_TITLES.get(ck, ck)
        if not items:
            print(f"✅ {title}")
            continue
        mark = "❌" if any(i.severity == "error" for i in items) else "⚠️"
        print(f"{mark} {title}（{len(items)} 条）")
        for i in items:
            print(f"     [{i.target}] {i.detail}")

    print("=" * 64)
    if errors:
        print(f"检出 {len(errors)} 处问题（warning {len(warns)}）"
              f" —— 服务面与验证面已经脱节，先修服务面。")
        return 1 if args.check else 0
    print("✅ 声明面自洽：服务出去的内容与权威值一致，且不存在身份不明的孪生副本")
    return 0


if __name__ == "__main__":
    sys.exit(main())
