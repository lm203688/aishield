#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则数一致性门禁
================

问题
----
版本漂移已有 `sync_version.py` 兜住，但**规则数漂移从未被门禁约束**。
实测同一个仓库里同时存在六个互不相同的规则数：

    api/static/index.html                 238 条规则
    api/static/agent.html                 238 条规则（12 处）
    api/static/mcp-security-guide.html    238 条安全规则
    api/static/pricing.html               238 条规则
    api/static/.well-known/agent-card.json 227 条 MCP / 233 条 Skill
    api/static/.well-known/mcp/server-card.json  235 MCP / +244 skill
    mcp-server/README.md                  201 rules
    registry/{SKILL.md,dify_*.yaml}       133 条规则
    smithery.yaml                         244 skill rules

而权威值是动态算出来的：`scanner.rules.get_rule_breakdown()` 给出 MCP
208 静态 + 8 情报 + 19 雷达 = 235，`get_rule_count('skill')` 给出 241。
这些散文式声明里没有一个引用权威源，全是手写数字，于是每次规则晋升都会
漏改若干个，外部用户看到"238 条规则"而实际只有 235 条 —— 一个安全扫描器
自己谎报能力数量，是最伤信任的失真方式。

与 `sync_version.py` 的区别
--------------------------
版本号是**单一字符串**，锚点固定，直接正则替换即可。规则数不是：它散布在
中文/英文散文里，语境决定它该等于哪个值（MCP 235 还是 Skill 241），而且
同一个数字（如 233）在 CSS `rgba(233,69,96)` 里只是颜色分量。所以这里必须
**先锚定语境，再校验数字**，不能用裸数字正则全局替换。

用法
----
    python scripts/rule_count_gate.py            # 报告现状
    python scripts/rule_count_gate.py --check    # CI 门禁，不一致 exit 1
    python scripts/rule_count_gate.py --sync     # 把声明位对齐权威值
    python scripts/rule_count_gate.py --json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, Iterator, List, Tuple

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)


# ── 权威源 ───────────────────────────────────────────────────────────
def authority() -> Dict[str, str]:
    """规则数的唯一真相。全部数字都从这个函数来，不写死。"""
    from scanner.rules import get_rule_breakdown, get_rule_count
    b = get_rule_breakdown()
    return {
        "mcp": str(b["total"]),
        "skill": str(get_rule_count("skill")),
        "static": str(b["static"]),
        "generated": str(b["generated"]),
        "radar": str(b["radar"]),
    }


# ── 声明位语境模式 ───────────────────────────────────────────────────
# 顺序敏感：先匹配最具体的（双值 pair、带类型标注），再匹配单值，最后兜底。
#
# 为什么不用裸数字正则：`238` 在 `rgba(238, 69, 96)` 里是颜色分量，
# 在 CVE 号、日期、端口里都可能出现。必须先锚定"条规则 / rules"这类
# 语境词，才能确定这个数字的语义身份。
def _patterns() -> List[Tuple[re.Pattern, str]]:
    # 所有以捕获组开头的模式都显式带 `(?<!\d)` 前缀。这不是风格问题，
    # 而是正确性问题：正则引擎在某处匹配失败后会退回**下一个字符位置**
    # 重试，若没有"前一个字符不能是数字"的约束，它就会从数字的中间起跳。
    #
    # 实测事故："OWASP MCP Top 10检测规则" 配 `(?<!Top )(?<!Top)(?<!条)`
    # 时，引擎在 "1" 处被 Top 后顾拦下，退回 "0" 处再试 —— 此时前面是
    # "1" 而非 "Top "，后顾通过，于是捕获 got="0"，sync 把 "10" 改写成
    # "1235"。门禁随后读到 "Top 1235" 又不匹配任何模式，一路绿灯通过。
    # 假阳性、错误替换、假绿三者连环，没有任何一步报警。
    p: List[Tuple[re.Pattern, str]] = [
        # 双值。三种写法都要覆盖：
        #   "227 条 MCP / 233 条 Skill"   "235 MCP / 241 Skill"
        #   "235/241 条规则"（README mermaid 里的紧凑写法）
        (re.compile(r"(?<!\d)(\d+)\s*条\s*MCP\s*/\s*(\d+)\s*条\s*Skill"), "pair"),
        (re.compile(r"(?<!\d)(\d+)\s*MCP\s*/\s*(\d+)\s*Skill"), "pair"),
        (re.compile(r"(?<!\d)(\d+)\s*/\s*(\d+)\s*条\s*(?:安全)?(?:检测)?规则"), "pair"),
        # 英文双值。缺这条会踩一次真实的"同步写坏数据"事故：llms.txt 写的是
        # `the OWASP MCP + ASI01-10 dual taxonomy with 253 / 280 rules.`，
        # 第二个数是 Skill 口径，但只有中文的 `/N条规则` 是 pair，英文那边
        # 落到兜底单值模式上被判成 MCP 声明 —— 于是 sync 把 280 改写成 253，
        # 一份对外文档的规则总数被静默篡改。
        (re.compile(r"(?<!\d)(\d+)\s*/\s*(\d+)\s*(?:security\s+)?rules\b", re.I), "pair"),
        # 中文单值
        (re.compile(r"(?<!\d)(\d+)\s*条\s*MCP\s*(?:安全)?规则"), "mcp"),
        (re.compile(r"(?<!\d)(\d+)\s*条\s*Skill\s*(?:安全)?规则"), "skill"),
        (re.compile(r"(?<!\d)(\d+)\s*条\s*OWASP\s+MCP\s+Top\s*10\s*(?:安全)?规则"), "mcp"),
        (re.compile(r"(?<!\d)(\d+)\s*条\s*(?:安全)?(?:检测)?规则"), "mcp"),
        # 不带量词的兜底："241安全规则" 这种写法同样是在声明规则总数。
        # Top 后顾用于排除 "OWASP MCP Top 10检测规则" —— 那里的 10 是
        # 风险类别数，不是规则数。
        (re.compile(r"(?<!\d)(?<!Top )(?<!Top)(\d+)\s*(?:安全|检测)\s*规则"), "mcp"),
        # 英文
        (re.compile(r"(?<!\d)(\d+)\s*MCP\s*(?:security\s+)?rules", re.I), "mcp"),
        (re.compile(r"(?<!\d)\+?(\d+)\s*skill\s*rules", re.I), "skill"),
        # "**Total: 235 rules** (MCP type) / **241 rules** (Skill type)"：
        # 数字与类型标注之间隔着 markdown 加粗符，靠 `(MCP` / `(Skill` 锚定。
        (re.compile(r"(?<!\d)(\d+)\s*rules?\s*\*{0,2}\s*\(Skill", re.I), "skill"),
        (re.compile(r"(?<!\d)(\d+)\s*rules?\s*\*{0,2}\s*\(MCP", re.I), "mcp"),
        (re.compile(r"(?<!\d)(\d+)\s*(?:security\s+)?rules\b", re.I), "mcp"),
        (re.compile(r"(?<!\d)(\d+)-rule\s+base", re.I), "mcp"),
        # 捕获组在末尾，前面已锚定 `[:=]\s*`，不可能落在数字上，无需后顾。
        (re.compile(r"rules?_count\s*[:=]\s*(\d+)"), "mcp"),
    ]
    return p


# ── 分解值语境 ───────────────────────────────────────────────────────
# 行内含这些标记时，数字是分类小计（OWASP MCP01–10 小计 113、ASI01–10 小计
# 62、静态基线 208……），不是"总计"声明。把它们当总计校验会产生一批假阳性
# —— mcp-server/README.md 的规则明细表和 mcp-security-guide.html 的 OWASP
# 速查表整个都是分解结构。
# 分解值语境。分两组，因为"整行豁免"和"这个数是不是小计"是两件事。
#
# 为什么必须分两组 —— 这是本门禁踩过的最隐蔽一个坑：
# 早期实现是「行内出现 mcp- / asi0 / subtotal 任一标记就整行豁免」。
# smithery.yaml 的描述行同时含 `OWASP MCP Top 10 + Agentic ASI01-10 aligned`
# （话题提及）和 `238 MCP / 244 skill rules`（真正的声明位），整行豁免把它
# 一起放走了 —— 门禁报 0 漂移，声明面却漂着。这和扫描器自己那条铁律是同一个
# 病：话题提及必须与祈使式执行区分，用行级关键词做豁免等于分不清这两者。
#
# 因此：
#   ROW_MARKERS   —— 只会出现在分解语境的词，命中即整行豁免（安全）
#   CELL_MARKERS  —— 分类编号，只豁免**紧邻它的那个数字**（或整行是表格时）
ROW_MARKERS = ("subtotal", "小计", "static baseline", "静态基线", "promoted")
CELL_MARKERS = ("mcp0", "mcp-", "asi0", "asi-")
# 分类编号与数字之间的最大距离。表格单元格里两者隔得近；
# 隔太远说明那个编号只是行文里提到的标准名，不是这个数的所属分类。
CELL_WINDOW = 14


def _is_breakdown_row(line: str) -> bool:
    """整行豁免判定：行内出现分解专属词，或整行是分类明细表。"""
    low = line.lower()
    if any(m in low for m in ROW_MARKERS):
        return True
    # 表格行 + 分类编号：`| MCP-06 | Prompt 注入 | Critical | 22 条规则 |`
    # 这种行里标记与数字可能隔很远，无法用紧邻窗口判断，只能整行豁免。
    if "|" in line and any(m in low for m in CELL_MARKERS):
        return True
    return False


def _is_breakdown_context(line: str, start: int) -> bool:
    """单点豁免判定：这个数字紧邻分类编号，才认为是小计。"""
    seg = line[max(0, start - CELL_WINDOW): start].lower()
    return any(m in seg for m in CELL_MARKERS)


# ── 声明位范围 ───────────────────────────────────────────────────────
TEXT_EXT = (".md", ".json", ".yaml", ".yml", ".html", ".htm", ".txt")

EXCLUDE_DIR_PARTS = (
    ".git", ".workbuddy", "node_modules", "__pycache__", "tests",
    "scanner", "eco", "dist", "archive",
)
EXCLUDE_PATH_PARTS = ("docs/blog", "docs/intel", "docs/eco")
EXCLUDE_FILES = {
    # 历史发布日志：llms-full.txt 的 "Shipped in v4.2.0 … 214-rule base"
    # 记录的是那个版本当时的真实基线。把它改成当前数字等于伪造历史，
    # 对一个以真实性为卖点的扫描器来说是不可接受的失真。
    "api/static/llms-full.txt",
    "docs/llms-full.txt",
}


def _is_declared_surface(rel: str) -> bool:
    """判定一个文件是否属于"对外声明面"。

    刻意收窄范围：门禁的代价是每次晋升规则都要改一堆文件，所以只覆盖
    用户/Agent 真会读到的地方，而不是全仓库 grep。
    """
    if rel.startswith("api/static/"):
        return True
    if rel.startswith("mcp-server/") and "dist" not in rel:
        return True
    if rel.startswith("registry/"):
        return True
    if rel.startswith("docs/benchmark/"):
        return True
    if rel.startswith("docs/"):
        # docs/ 根级文档是带日期的历史分析快照（标题或正文标注了测量日期），
        # 其中的数字是"当时测到的值"。同步成当前数字等于把它改写成伪造历史，
        # 而时间准确性正是这类文档的价值所在。对外承诺数字只由 api/static、
        # mcp-server、registry 三处承载 —— 那才是用户和 Agent 真会读到的地方。
        return False
    root = os.path.basename(rel)
    if "/" not in rel:
        return root in ("README.md", "AGENTS.md", "CLAUDE.md", "smithery.yaml",
                        ".mcp.json", "SECURITY.md")
    return False


def collect_files() -> List[str]:
    """列出所有受门禁约束的声明位文件。"""
    out: List[str] = []
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = [
            d for d in dirnames
            if not any(bad in d for bad in EXCLUDE_DIR_PARTS)
        ]
        rel_dir = os.path.relpath(dirpath, REPO).replace(os.sep, "/")
        if any(rel_dir.startswith(bad) for bad in EXCLUDE_PATH_PARTS):
            continue
        for fn in filenames:
            if not fn.endswith(TEXT_EXT):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), REPO)
            rel = rel.replace(os.sep, "/")
            if rel in EXCLUDE_FILES:
                continue
            if not _is_declared_surface(rel):
                continue
            out.append(rel)
    return sorted(out)


# ── 统一解析 ─────────────────────────────────────────────────────────
def iter_declarations(lines: List[str], patterns: List[Tuple[re.Pattern, str]],
                      auth: Dict[str, str]) -> Iterator[Tuple[int, re.Match, str, Any, Any, bool]]:
    """统一的声明位解析器。

    产出 (lineno, match, kind, got, expected, ok)，已完成三件事：

    1. 去重 —— 同一段文字会被多条 pattern 命中（"238 条安全规则" 同时命中
       `条安全规则` 与 `条(?:安全)?(?:检测)?规则`），不去重会放大告警噪音。
    2. 排除分解表行 —— OWASP 分类小计（MCP-01 … MCP-10、Subtotal）不是
       总计声明，把它们当总计校验会产生一片假阳性。
    3. 排除被合法声明覆盖的子串 —— `235/241 条规则` 是合法的双值写法，
       但单值 pattern 会再去匹配它的尾部 `241 条规则` 并报成漂移；
       `**241 rules** (Skill type)` 被 skill 模式判为合法后，英文兜底模式
       还会匹配它的头部 `241 rules` 并判成 MCP 漂移 —— 同一个数字，
       两个 pattern 各说各话。

    **scan 与 sync 必须共用这一个函数。** 此前二者各写一套判定逻辑，结果
    是 scan 认定 `241 rules (Skill type)` 合法、sync 却按 MCP 口径把它改成
    了 235 —— 门禁说"对"、同步说"错"，属于最隐蔽的假绿：检查一路绿灯，
    数据已经写坏。
    """
    seen = set()
    covered: List[Tuple[int, int, int]] = []
    for lineno, line in enumerate(lines, 1):
        if _is_breakdown_row(line):
            continue
        for pat, kind in patterns:
            for m in pat.finditer(line):
                # 分类小计的单点豁免：只有这个数字紧邻分类编号才算小计。
                # 否则 smithery.yaml 那种「ASI01-10 aligned ... 244 skill rules」
                # 会被整行豁免放走。
                if _is_breakdown_context(line, m.start()):
                    continue
                key = (lineno, m.start(), m.end(), kind)
                if key in seen:
                    continue
                seen.add(key)
                # 重叠即视为已被覆盖（不是"完全包含"）。
                # pair 的 group(0) 到 "Skill" 为止，而单值模式 `(\d+)条Skill安全规则`
                # 会一路匹配到 "规则"，区间尾端越出 pair 区间 —— 用"完全包含"
                # 判断就会漏放这条重复噪音。同一行里两个区间重叠，只可能是
                # 同一个声明的不同 pattern 视角，不可能真是两个独立声明。
                if any(c[0] == lineno and not (c[2] <= m.start() or m.end() <= c[1])
                       for c in covered):
                    continue
                if kind == "pair":
                    got = (m.group(1), m.group(2))
                    expected = (auth["mcp"], auth["skill"])
                else:
                    got = m.group(1)
                    expected = auth[kind]
                ok = got == expected
                # pair 无论是否合法都要登记覆盖：它的两个数字是**同一个声明**
                # 的两半，报"pair 漂移"一条就够，再报内部单值只是噪音。
                # 单值则仅在合法时登记，合法声明才需要屏蔽自己的子串。
                if kind == "pair" or ok:
                    covered.append((lineno, m.start(), m.end()))
                yield lineno, m, kind, got, expected, ok


def scan(rel: str, auth: Dict[str, str],
         patterns: List[Tuple[re.Pattern, str]]) -> List[Dict[str, Any]]:
    """返回该文件的漂移条目。"""
    full = os.path.join(REPO, rel)
    if not os.path.isfile(full):
        return []
    try:
        with open(full, "r", encoding="utf-8-sig", errors="replace") as f:
            text = f.read()
    except OSError:
        return []

    findings: List[Dict[str, Any]] = []
    for lineno, m, kind, got, expected, ok in iter_declarations(
            text.splitlines(keepends=True), patterns, auth):
        if ok:
            continue
        if kind == "pair":
            findings.append({
                "file": rel, "line": lineno, "kind": "pair",
                "match": m.group(0),
                "got": {"mcp": got[0], "skill": got[1]},
                "expected": {"mcp": expected[0], "skill": expected[1]},
            })
        else:
            findings.append({
                "file": rel, "line": lineno, "kind": kind,
                "match": m.group(0), "got": got, "expected": expected,
            })
    return findings


# ── 同步 ─────────────────────────────────────────────────────────────
def sync_text(text: str, auth: Dict[str, str],
              patterns: List[Tuple[re.Pattern, str]]) -> Tuple[str, int]:
    """把声明位数字对齐权威值，返回 (新文本, 改动次数)。

    与 scan 共用 iter_declarations，保证"该改什么"和"改成什么"口径一致。
    按 span 从右往左替换，避免前面的替换让后面的偏移失效。
    """
    lines = text.splitlines(keepends=True)
    out: List[str] = []
    n = 0
    for lineno, line in enumerate(lines, 1):
        edits: List[Tuple[int, int, str]] = []
        for ln, m, kind, got, expected, ok in iter_declarations(
                lines, patterns, auth):
            if ok or ln != lineno:
                continue
            if kind == "pair":
                # 按两个捕获组的**相对偏移**拼接，保留中间与尾部文字。
                # 不能用 `len(got[1])` 从尾部倒切：group(0) 的结尾不一定是
                # 第二个数字（"227条MCP/233条Skill" 之后可能紧跟 "安全规则"），
                # 那样会把 "Skill" 截成 "Sk"，产出 "235条MCP/233条Sk241" 这种
                # 既错又被门禁漏检的乱码。
                base = m.start(0)
                s1, e1 = m.start(1) - base, m.end(1) - base
                s2, e2 = m.start(2) - base, m.end(2) - base
                frag = m.group(0)
                new = frag[:s1] + expected[0] + frag[e1:s2] + expected[1] + frag[e2:]
            else:
                new = m.group(0).replace(got, expected, 1)
            edits.append((m.start(), m.end(), new))
        for start, end, new in sorted(edits, reverse=True):
            line = line[:start] + new + line[end:]
            n += 1
        out.append(line)
    return "".join(out), n


def main() -> int:
    ap = argparse.ArgumentParser(description="规则数一致性门禁")
    ap.add_argument("--check", action="store_true", help="不一致则退出码 1（CI 门禁）")
    ap.add_argument("--sync", action="store_true", help="把声明位对齐权威值")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    auth = authority()
    pats = _patterns()
    files = collect_files()

    all_findings: List[Dict[str, Any]] = []
    for rel in files:
        all_findings.extend(scan(rel, auth, pats))

    if args.json:
        print(json.dumps({"authority": auth, "files_checked": len(files),
                          "drifts": all_findings},
                         ensure_ascii=False, indent=2))
        return 0

    print(f"规则数一致性检查（权威：MCP {auth['mcp']} = "
          f"{auth['static']} 静态 + {auth['generated']} 情报 + {auth['radar']} 雷达"
          f" · Skill {auth['skill']}）")
    print("=" * 64)
    print(f"受约束声明位：{len(files)} 个文件")
    if not all_findings:
        print("✅ 全部一致，无漂移")
        print("=" * 64)
        return 0
    for f in all_findings:
        if f["kind"] == "pair":
            got = f"{f['got']['mcp']}/{f['got']['skill']}"
            exp = f"{f['expected']['mcp']}/{f['expected']['skill']}"
        else:
            got, exp = f["got"], f["expected"]
        print(f"❌ {f['file']}:{f['line']}")
        print(f"     实测 {got}  → 应为 {exp}   〔{f['match']}〕")
    print("=" * 64)
    print(f"检出 {len(all_findings)} 处漂移，涉及 "
          f"{len({f['file'] for f in all_findings})} 个文件")

    if args.sync:
        changed_files = 0
        for rel in sorted({f["file"] for f in all_findings}):
            full = os.path.join(REPO, rel)
            # 按字节读写并显式保留 BOM：部分 .html 带 BOM，用 utf-8-sig 读
            # 再普通 utf-8 写会静默丢失，把无关编码差异混进 diff。
            with open(full, "rb") as fh:
                raw_b = fh.read()
            bom = b"\xef\xbb\xbf" if raw_b.startswith(b"\xef\xbb\xbf") else b""
            raw = raw_b.decode("utf-8-sig")
            new, n = sync_text(raw, auth, pats)
            if n and new != raw:
                with open(full, "wb") as fh:
                    fh.write(bom + new.encode("utf-8"))
                changed_files += 1
                print(f"   ✓ 修正 {n} 处: {rel}")
        print(f"同步完成，改动 {changed_files} 个文件")
        return 0

    print("修复：python scripts/rule_count_gate.py --sync")
    return 1 if args.check else 0


if __name__ == "__main__":
    sys.exit(main())
