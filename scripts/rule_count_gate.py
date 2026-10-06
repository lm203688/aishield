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
        # re.I 不是风格问题：2026-10-05 实测 `docs/.well-known/agent-card.json`
        # 写的是 `against 235 MCP / 241 skill rule categories`（小写 skill）。
        # 上面这条要求大写 `Skill`，于是**整个 pair 不匹配**，只剩单值的
        # `241 skill rule categories` 被抓住 —— 235 一侧无任何模式覆盖。
        # 后果不是"漏报一条"，而是 **sync 会写出半对的文件**：把 241 改成 291、
        # 把 235 原样留下，得到 `235 MCP / 291 skill`，而门禁因为 235 不匹配
        # 任何模式、一路绿灯。假阳性 + 静默篡改 + 假绿再次连环。
        (re.compile(r"(?<!\d)(\d+)\s*MCP\s*/\s*(\d+)\s*Skill", re.I), "pair"),
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
        # `235 / 241 条 (OWASP 双维对齐)` —— 括号里是口径说明、后面没有"规则"
        # 二字。缺这条盲区是实测出来的：README.md 就长期停在这一形态上，
        # 门禁一路绿灯，是 tests/test_mcp_contract 把它掀出来的。
        (re.compile(r"(?<!\d)(\d+)\s*/\s*(\d+)\s*条\s*[（(]"), "pair"),
        # `253 类规则`：JSON/散文里拿"类"当量词时同样是在声明规则总数。
        (re.compile(r"(?<!\d)(\d+)\s*类\s*规则"), "mcp"),
        # `235+ 规则扫描`：带加号的写法。action.yml 的描述就一直是这个形态
        # （"235+ 规则扫描"），缺这条时它连同 action.yml 一起在门禁外待着。
        (re.compile(r"(?<!\d)(\d+)\s*\+\s*(?:条)?(?:安全|检测)?规则"), "mcp"),
        (re.compile(r"(?<!\d)(\d+)\s*\+\s*(?:security\s+)?rules\b", re.I),
         "mcp"),
        # 结构化声明：`"total": 253` / `"skill_categories": 280`。
        # agent-discovery.json 的 rules 块是机器读的契约字段，散文模式看不见它，
        # 而它恰恰是 /api/v1/health 会被外部比对的那一份。
        # agent.json / agent-discovery.json 的 rules 块把构成也拆开写了：
        # 只校 total 是不够的 —— total 已经是 256、static 还停在 226 时，
        # 这份文件对外报出的构成自相矛盾（256 = 226+8+19 根本不成立）。
        (re.compile(r'"total"\s*:\s*(\d+)'), "mcp"),
        (re.compile(r'"skill_?categori[a-z]*"\s*:\s*(\d+)', re.I), "skill"),
        (re.compile(r'"static"\s*:\s*(\d+)'), "static"),
        (re.compile(r'"radar"\s*:\s*(\d+)'), "radar"),
        (re.compile(r'"generated"\s*:\s*(\d+)'), "generated"),
        # 散文里的构成写法："静态 208 + 情报 8 + 雷达 19"。
        # AGENTS.md / CLAUDE.md 的这条等式是给 AI agent 读的项目手册，
        # 它自己写着"勿引用过期规则计数"，而它自己的 208 已经过期 ——
        # 只校验 JSON 的 "static" 看不见散文里的"静态 N"。
        (re.compile(r"(?:静态|static)\s*(\d+)"), "static"),
        # 英文
        (re.compile(r"(?<!\d)(\d+)\s*MCP\s*(?:security\s+)?rules", re.I), "mcp"),
        (re.compile(r"(?<!\d)\+?(\d+)\s*skill\s*rules", re.I), "skill"),
        # `235 MCP rule categories / 241 skill rule categories`。
        # 上一两条要求名词是 `rules`，这里写的是 `rule categories` —— 一个复数
        # 变形就把它推出门禁。直出位置是 .well-known/agent.json 的 description
        # 字段：机器读的 agent 名片，却长期停在线上 235/241 而 rules 块已是
        # 264/291，同一份文件自相矛盾。
        (re.compile(r"(?<!\d)(\d+)\s*MCP\s*rule\s*categor(?:y|ies)", re.I), "mcp"),
        (re.compile(r"(?<!\d)(\d+)\s*(?:skill|SKILL)\s*rule\s*categor(?:y|ies)",
                    re.I), "skill"),
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
# 必须含 .ts：MCP server 的工具描述里写着"N 条规则"，而工具描述是**每一次
# 调用都展示给用户**的东西（比 README 更直白）。它此前因为不是 TEXT_EXT 里
# 的后缀而完全逃过门禁，是 tests/test_finding_anchor 抓到的。
#
# 必须含 .xml（2026-10-05 补）：api/static/feeds.xml 是对外发布的 Atom 订阅源，
# 第 28 行写着"基于 AIShield 227 条安全规则扫描"，227 停在两代之前。它被漏掉
# 的原因不是模式不全，而**仅仅因为 .xml 不在这个元组里** —— 声明面门禁的运行时
# 探针（scripts/declaration_surface_gate.py）扫响应文本时才掀出来。
# 教训：静态门禁的"文件清单"本身就是一处盲区来源，扩展名白名单必须与
# "对外真会服务的资产"对齐。
TEXT_EXT = (".md", ".json", ".yaml", ".yml", ".html", ".htm", ".txt", ".ts", ".xml")

EXCLUDE_DIR_PARTS = (
    ".git", ".workbuddy", "node_modules", "__pycache__", "tests",
    "scanner", "eco", "dist", "archive",
)
EXCLUDE_PATH_PARTS = ("docs/blog", "docs/intel", "docs/eco")

# ── 豁免台账：路径 → **非空理由** ─────────────────────────────────────
# 为什么不是裸 set：豁免就是"把一个对外资产从门禁里拿出去"，是一种特权。
# 特权集合若能凭空变大，门禁就等于关掉了一半（假绿的第 2 层）。所以每一处
# 豁免都必须写明"为什么这里的数字不该被同步"，由
# scripts/declaration_surface_gate.py 的第 5 项检查强制非空；且豁免的文件
# 必须真实存在 —— 死豁免会掩盖将来同路径的新漏网，与"死台账"同理。
#
# 保持 dict 而非换类型是刻意的：消费方只做 `rel in EXCLUDE_FILES` 的键
# 成员判定，dict 的键判定与之兼容，改动不会波及其他模块（已核对全仓
# 四个消费点，均为成员判定）。
EXCLUDE_FILES: Dict[str, str] = {
    # 历史发布日志：llms-full.txt 的 "Shipped in v4.2.0 … 214-rule base"
    # 记录的是那个版本当时的真实基线。把它改成当前数字等于伪造历史，
    # 对一个以真实性为卖点的扫描器来说是不可接受的失真。
    "api/static/llms-full.txt": (
        "历史发布日志：'Shipped in v4.2.0 … 214-rule base' 是那一版当时的真实"
        "基线，同步成当前数字等于伪造历史。"),
    "docs/llms-full.txt": (
        "api/static/llms-full.txt 的 docs 侧镜像，同一份历史发布日志。"),
}


def exempt_reason(rel: str) -> str:
    """该路径的豁免理由；未豁免返回空串。"""
    return EXCLUDE_FILES.get(rel.replace(os.sep, "/"), "")


def exempt_table_errors():
    """豁免台账自身的问题，返回 ``[(severity, message), ...]``。

    刻意放在台账所在的模块：校验跟着台账走，消费方 import 即可，避免两处
    各自维护一份判断（那正是本仓库反复吃亏的"判据复写掉一半"）。
    """
    out = []
    for rel, reason in EXCLUDE_FILES.items():
        if not (reason or "").strip():
            out.append((
                "error",
                f"{rel} 在 EXCLUDE_FILES 里却没有写豁免理由 —— "
                f"豁免是特权，必须能自证为什么这里的数字不该被同步"))
        if not os.path.isfile(os.path.join(REPO, rel.replace("/", os.sep))):
            out.append((
                "warn",
                f"{rel} 在 EXCLUDE_FILES 里但文件已不存在（死豁免）—— "
                f"请删除，否则会掩盖将来同路径的新漏网"))
    return out


# docs/ 下的特例。docs/ 根级文档是带日期的历史快照，理应豁免；但 llms.txt
# 是机器读的实时产物（与 api/static/llms.txt 成对出现，二者必须字节一致），
# 把它当历史文档豁免，等于给"两份 llms.txt 已经吵起来了"留了门。
ALLOWED_DOCS = ("docs/llms.txt",)


def _served_docs_surfaces() -> Tuple[str, ...]:
    """docs/ 下**真正被服务的**声明面文件（从注册表现算，不硬编码）。

    为什么必须算出来而不能只靠 ALLOWED_DOCS 手写：2026-10-05 实测线上
    `https://aishield.tools/.well-known/agent-card.json` 返回 235/241，
    而 `--check` 报"无漂移"。根因就是这个函数当时**不存在** ——
    docs/ 被整体当作"带日期的历史快照"豁免，而该 URL 服务的恰是
    `docs/.well-known/agent-card.json`；门禁覆盖的 `api/static/` 那份
    反而被一段不可达代码引用、永不服务。门禁扫死副本、放行活副本，
    于是"检查全绿 + 线上全错"。

    刻意不加 try/except 兜底：注册表导入失败就必须炸，退化成空元组等于
    把上一次的假绿原样搬回来。假绿的第 2 层就是"吞异常/退化成空集合"。
    """
    from api.declaration_surface import ROOT_DOCS, SERVED
    return tuple(
        s.rel.replace(os.sep, "/")
        for s in SERVED.values()
        if s.rel and s.rel.replace(os.sep, "/").startswith(ROOT_DOCS + "/")
    )


SERVED_DOCS = _served_docs_surfaces()


def _published_content_sources() -> Tuple[str, ...]:
    """**被发布出去的**稿件源文件（从发布器自己的发现函数现算，不手抄清单）。

    为什么必须算出来：2026-10-06 定时 spine 连续失败，根因是
    `content/blog/case-filesystem-test-2026-07-25.md` 里写死 `133 条安全规则`
    —— 而 `scripts/publish_content.py:publish_feed()` 会把每篇稿件的
    ``summary`` **原样抄进** ``api/static/feeds.xml``（受约束声明面）。
    源不在门禁里、产物在门禁里，于是每天分发都把过期数字重新写回对外面，
    推送前预检再把它拦下 —— 闭环自己把自己摁死，且报警指向产物、不指向源。

    判据派生自 ``publish_content.CONTENT_DIRS``（发布器真正读的目录），
    而不是在门禁里另抄一份路径前缀：两处白名单一扩缩就会分叉，
    而那正是 feeds.xml 的根因形状。

    刻意不加 try/except：发布器缺失/导入失败就必须炸，退化成空元组
    等于把"源不受门禁"这件事悄悄搬回来。
    """
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    from publish_content import CONTENT_DIRS, INTERNAL_PREFIXES  # 唯一真相源
    out: List[str] = []
    for d in CONTENT_DIRS:
        try:
            rel_dir = os.path.relpath(str(d), REPO).replace(os.sep, "/")
        except ValueError:  # 跨盘符（Windows 下理论可能）
            continue
        if rel_dir.startswith(".."):
            continue
        for name in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if not name.endswith(".md"):
                continue
            if name.startswith(INTERNAL_PREFIXES):
                continue
            out.append(f"{rel_dir}/{name}")
    return tuple(out)


PUBLISHED_SOURCES = _published_content_sources()


def _is_declared_surface(rel: str) -> bool:
    """判定一个文件是否属于"对外声明面"。

    刻意收窄范围：门禁的代价是每次晋升规则都要改一堆文件，所以只覆盖
    用户/Agent 真会读到的地方，而不是全仓库 grep。
    """
    if rel in ALLOWED_DOCS:
        return True
    # 稿件源（content/blog、eco/content）：它们的内容会被发布器抄进
    # api/static/feeds.xml。产物受门禁而源不受，就是"门禁抓症状、放走病因"。
    if rel in PUBLISHED_SOURCES:
        return True
    # 被服务的 docs 声明面（当前是 docs/.well-known/agent-card.json）。
    # 它们和 api/static 下的副本**同样对外**，只因历史遗留的"两个根"而
    # 分居两处；门禁必须两边都覆盖，否则又回到"扫死副本、放行活副本"。
    if rel in SERVED_DOCS:
        return True
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
        # action.yml 是 GitHub Marketplace 的插件描述 —— 用户点进去第一眼
        # 看见的那句话，写的是"235+ 规则扫描"。此前它不在声明面里，
        # 于是这份对外描述停了两代规则数没人管。
        return root in ("README.md", "AGENTS.md", "CLAUDE.md", "smithery.yaml",
                        ".mcp.json", "SECURITY.md", "action.yml")
    return False


def declared_surface_changed(paths) -> List[str]:
    """从一批改动路径里筛出"对外声明面"的那些。

    供 ``scripts/git_push_safe.sh`` 在**推送前**调用：本仓 16 个推送点全部经过
    那个脚本，所以"自动提交改写了对外资产却没有验证"只需要在那里堵一次。

    判据必须**派生**（``_is_declared_surface`` + ``EXCLUDE_FILES``），不在这里
    手抄路径前缀 —— 两处白名单一扩缩就会分叉，而那正是 feeds.xml 的根因形状。
    豁免文件不算宣言面：它们本就是"数字不该被同步"的历史资产。
    """
    out: List[str] = []
    for p in paths:
        rel = (p or "").strip().replace(os.sep, "/")
        while rel.startswith("./"):
            rel = rel[2:]
        if not rel or rel in EXCLUDE_FILES:
            continue
        if _is_declared_surface(rel):
            out.append(rel)
    return out


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


def scan_text(label: str, text: str, auth: Dict[str, str],
              patterns: List[Tuple[re.Pattern, str]]) -> List[Dict[str, Any]]:
    """扫描**任意文本**的规则数漂移条目。

    与 `scan()` 分开是为了让"服务出去的字节"也能被同一套模式校验：
    声明面门禁（scripts/declaration_surface_gate.py）拿运行时响应当输入，
    不需要先把响应写成临时文件再扫。两处共用同一套模式与同一份权威值，
    避免"文件里用一套口径、线上用另一套"的老问题重演。
    """
    lines = text.splitlines(keepends=True)
    findings: List[Dict[str, Any]] = []
    for lineno, m, kind, got, expected, ok in iter_declarations(
            lines, patterns, auth):
        if ok:
            continue
        if kind == "pair":
            findings.append({
                "file": label, "line": lineno, "kind": "pair",
                "match": m.group(0),
                "got": {"mcp": got[0], "skill": got[1]},
                "expected": {"mcp": expected[0], "skill": expected[1]},
            })
        else:
            findings.append({
                "file": label, "line": lineno, "kind": kind,
                "match": m.group(0), "got": got, "expected": expected,
            })

    # 逐类小计单独查一遍：它们所在的行已被 breakdown 豁免，永远走不到
    # iter_declarations。用引擎真值直接比对，不再依赖散文模式。
    cats = category_counts()
    for lineno, line in enumerate(lines, 1):
        for m in _CATEGORY_ROW.finditer(line):
            key = m.group(1) + m.group(2)
            if key not in cats:
                continue
            if m.group(3) != str(cats[key]):
                findings.append({
                    "file": label, "line": lineno, "kind": "category",
                    "match": m.group(0), "got": m.group(3),
                    "expected": str(cats[key]), "category": key,
                })
    return findings


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
    return scan_text(rel, text, auth, patterns)


# ── 逐类小计 ─────────────────────────────────────────────────────────
# 表格行 `| MCP03 | 工具投毒 | Critical | 11 |` 上的分类编号与数字。
# 这类行被 `_is_breakdown_row` 整行豁免（它们不是"总计"声明，豁免是对的），
# 但豁免的同时把它们**完全**丢出了视线，于是 README 里的逐类分布可以漂
# （实测 MCP03 写着 10、引擎 11）而门禁零反应。逐类累计同样是对外承诺：
# 选型的人看的是"你这一类覆盖了多少"，不是只看个总数。
_CATEGORY_ROW = re.compile(r"\|\s*\*{0,2}(MCP|ASI)(\d{2})\*{0,2}\s*\|"
                           r"\s*\*{0,2}(\d+)\*{0,2}\s*\|")


def category_counts() -> Dict[str, int]:
    """逐类规则数真值，直接问引擎要，不在门禁里写死。"""
    from scanner import rules as R
    out: Dict[str, int] = {}
    for prefix in ("MCP", "ASI"):
        for i in range(1, 11):
            key = f"{prefix}{i:02d}"
            if hasattr(R, key + "_RULES"):
                out[key] = len(getattr(R, key + "_RULES"))
    return out


def drifted_files() -> List[str]:
    """当前存在规则数漂移的声明位文件（仓库相对路径，已排序）。

    这是给**推送链路**用的出口：规则晋升后本地 ``--sync`` 会改掉几十个声明位
    （2026-10-02 实测一次 20+ 个文件），而人工挑文件推送只会带其中几个，
    CI 的 "Workflow Integrity Gate" 立刻在没推的那些文件上红 —— 红的是
    "本地已改、远端未同步"，不是"代码有问题"。人肉挑文件这件事本身不可靠，
    所以由 `_push_batch.py` 调用本函数，把漂移文件并进同一批提交。

    与 ``main()`` 的区别：main 是给人看的报告 + 给 CI 的退出码，本函数只
    要"哪些文件漂了"这一个事实，供机器消费。两者共用 authority / scan，
    不存在"门禁报干净但推送带上了别的东西"的口径分裂。
    """
    auth = authority()
    pats = _patterns()
    bad: set = set()
    for rel in collect_files():
        if scan(rel, auth, pats):
            bad.add(rel)
    return sorted(bad)


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
    cats = category_counts()
    for lineno, line in enumerate(lines, 1):
        edits: List[Tuple[int, int, str]] = []
        # 逐类小计：这些行被 breakdown 规则整行豁免，prose 模式根本不会
        # 产生 edit，所以必须单独补。少了这一段，新增的分类漂移就是
        # "--check 永远红" —— 门禁第一次报真问题时就卡死自己。
        for m in _CATEGORY_ROW.finditer(line):
            key = m.group(1) + m.group(2)
            want = str(cats.get(key, ""))
            if not want or m.group(3) == want:
                continue
            edits.append((m.start(), m.end(),
                          line[:m.start(3)] + want + line[m.end(3):],
                          -1))                      # priority -1：最具体
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
            # priorities：position in _patterns() —— 越靠前越具体。
            # pair > 类型标注((MCP / (Skill) > 裸单值兜底。
            edits.append((m.start(), m.end(), new, _priority_of(m, patterns)))
        # 同一行里**重叠**的 edit 必须先定性再替换，不能直接按位置倒序打。
        # 2026-10-02 实证：`**253 rules** (MCP type) / **253 rules** (Skill type)`
        # 这一行上，`rules\b` 兜底模式与 `(Skill` 标注模式同时覆盖第二处的
        # "253 rules"，两条 edit 落进同一段文本：先按 (Skill) 写成
        # "283 rules** (Skill"，紧接的兜底 edit 又把它整体替换成 "283 rules"
        # —— 加粗符与类型括号被抹掉、长度变化还会让后续落点错位。
        # 结果：第一次 --sync 只改了 MCP 那一半，Skill 那半留着旧值，
        # 必须再跑一遍才对（对外文档上就是「一半新一半旧」）。
        for start, end, new in sorted(_resolve_overlaps(edits), reverse=True):
            line = line[:start] + new + line[end:]
            n += 1
        out.append(line)
    return "".join(out), n


def _priority_of(m, patterns) -> int:
    """这条 match 来自 patterns 表里的第几条 —— 越靠前越具体。"""
    for i, (p, _kind) in enumerate(patterns):
        if m.re is p:
            return i
    return len(patterns)


def _resolve_overlaps(edits):
    """重叠 edit 定胜负：具体模式胜出，被覆盖的丢弃。

    edits 形如 (start, end, new, priority)。priority 小者优先；同优先级时
    长匹配（覆盖字符多）优先，否则会留下半截改写。
    """
    kept = []
    spans = []  # [(start, end), ...] 已被具体 edit 占用的区间
    for start, end, new, prio in sorted(
            edits, key=lambda t: (t[3], t[0], -(t[1] - t[0]))):
        if any(start < ke and end > ks for ks, ke in spans):
            continue
        spans.append((start, end))
        kept.append((start, end, new))
    return kept


def main() -> int:
    ap = argparse.ArgumentParser(description="规则数一致性门禁")
    ap.add_argument("--check", action="store_true", help="不一致则退出码 1（CI 门禁）")
    ap.add_argument("--sync", action="store_true", help="把声明位对齐权威值")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--declared-surface", action="store_true",
                    help="从 stdin 读改动路径，打印其中属于对外声明面的那些"
                         "（供 git_push_safe.sh 推送前预检）")
    args = ap.parse_args()

    if args.declared_surface:
        # 刻意早退：这是被 shell 高频调用的窄出口，不该顺带走一遍全仓扫描。
        for rel in declared_surface_changed(sys.stdin.read().splitlines()):
            print(rel)
        return 0

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
