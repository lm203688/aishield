#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公开声明面注册表 —— 「哪个文件服务哪个公开 URL」的唯一事实源。

问题
----
2026-10-05 实测线上 ``https://aishield.tools/.well-known/agent-card.json``
返回 ``235 MCP / 241 skill rule categories``，而权威值是 **264 / 291**。
同一时刻 ``python scripts/rule_count_gate.py --check`` 报「✅ 全部一致，无漂移」。

两边说的都是真话，错的是**验证面与服务面脱节**：

    server.py:483  Trust API 分支   path == "/.well-known/agent-card.json"
                   → 提前 return，读 docs/.well-known/agent-card.json   ← 真正在服务
    server.py:768  静态资产分支     path == "/.well-known/agent-card.json"
                   → 永远执行不到（先命中者胜）                        ← 死代码
    rule_count_gate 覆盖的恰好是后者（api/static/ 前缀命中），
                    前者（docs/ 前缀）被 `_is_declared_surface` 当作
                    "历史快照"整体豁免                                 ← 放行

于是"文件里的数字"全对，"服务出去的数字"全错。此后任何"一致性检查通过"
都不再构成证据 —— 这就是这一类缺陷的完整形状。

设计
----
本模块只做一件事：把「URL → 服务文件」从**隐式 if 顺序**变成**显式数据**。

    SERVED   每个公开 URL 由哪个文件/哪个计算函数服务
    SHADOWS  声明路径下存在、但不被任何路由服务的同名孪生文件

两者都由 ``scripts/declaration_surface_gate.py`` 用**运行时探针 + AST** 反向
校验（不是"声明了就算数"）：探针直调 handler 取真实响应，AST 断言同一 URL
在分派链里只声明一次，孪生审计断言每个同名副本身份明确。

刻意不引入运行时耦合：``server.py`` / ``trust_api.py`` 保持原样，本表是
**被验证的声明**而非**控制流的一部分**。声明若与实现不符，门禁红 —— 而不是
悄悄按声明执行、掩盖实现。这样表错了会响，实现改了也会响。

用法
----
    from api.declaration_surface import SERVED, SHADOWS, twin_of, abs_path
"""
from __future__ import annotations

import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 两个互相竞争的"声明面根"。
# 历史上同一路径在两边各躺一份文件，谁生效取决于 server.py 里 if 的先后顺序，
# 没有人能从文件布局推断出来。孪生审计就建立在这两个根上。
ROOT_STATIC = "api/static"
ROOT_DOCS = "docs"
DECL_ROOTS = (ROOT_STATIC, ROOT_DOCS)


class Surface:
    """一个公开 URL 的服务事实。"""

    __slots__ = ("url", "rel", "content_type", "producer", "kind", "note",
                 "version_path")

    def __init__(self, url, rel, content_type, producer, kind="static-file",
                 note="", version_path=None):
        self.url = url
        self.rel = rel                  # 仓库相对路径；computed 型为 "" 或仅作标识
        self.content_type = content_type
        self.producer = producer        # 真正处理该 URL 的模块
        self.kind = kind                # static-file | json-doc | computed
        self.note = note
        # 版本字段在响应 JSON 里的路径。None = 该资产本来就不带版本，
        # 不该被"缺版本"的告警打扰（jwks/manifest/geo-faqs 属于此类）。
        # 声明清楚比让门禁去猜"这个文件应该有版本吗"可靠得多。
        self.version_path = tuple(version_path) if version_path else None

    def __repr__(self):  # pragma: no cover - 调试用
        return f"<Surface {self.url} -> {self.rel or self.kind}>"


class Shadow:
    """声明路径下存在、但不被任何路由服务的孪生文件。

    它们不是"垃圾"——`docs/llms.txt` 是被测试钉死的字节镜像，删了反而破坏
    不变量。但它们的**身份必须显式**：是镜像、是被取代的旧副本、还是纯粹的
    残留。身份不明的孪生文件正是 235/241 漂移的温床，因此默认视为违规。
    """

    __slots__ = ("rel", "url", "role", "reason")

    def __init__(self, rel, url, role, reason):
        self.rel = rel
        self.url = url
        self.role = role        # mirror | superseded | leftover
        self.reason = reason

    def __repr__(self):  # pragma: no cover - 调试用
        return f"<Shadow {self.rel} ({self.role})>"


# ── 被服务的公开声明面 ────────────────────────────────────────────────
# rel 一律写成仓库相对路径，方便门禁直接 open()。producer 写真正处理该 URL
# 的模块（不是"碰巧也提到它"的模块），供 AST 交叉校验。
SERVED = {
    # A2A Agent Card。由 Trust API 分支处理（server.py 的 do_GET 把它并入
    # /api/v1/trust 前缀族），读 docs 那份 —— 线上实测确认（见模块 docstring）。
    "/.well-known/agent-card.json": Surface(
        "/.well-known/agent-card.json",
        "docs/.well-known/agent-card.json",
        "application/json; charset=utf-8",
        "api/trust_api.py",
        kind="json-doc",
        note="A2A 发现入口；agent 据此判断本服务有哪些技能、覆盖多少条规则。",
        version_path=("version",),
    ),
    # MCP Server Card：走 server.py 的静态分支（api/static 那份）。
    "/.well-known/mcp/server-card.json": Surface(
        "/.well-known/mcp/server-card.json",
        "api/static/.well-known/mcp/server-card.json",
        "application/json; charset=utf-8",
        "api/server.py",
        version_path=("serverInfo", "version"),
    ),
    # RFC 9116 安全联络。规范路径是 /.well-known/security.txt，/security.txt 是
    # 历史兼容写法；robots.txt 两条都 Allow，所以两条都必须真的能服务。
    # 2026-10-05 之前只实现了后者 —— 声明面门禁的运行时探针实测规范路径 404。
    "/.well-known/security.txt": Surface(
        "/.well-known/security.txt",
        "api/static/.well-known/security.txt",
        "text/plain; charset=utf-8",
        "api/server.py",
        note="RFC 9116 规范路径。",
    ),
    "/security.txt": Surface(
        "/security.txt",
        "api/static/.well-known/security.txt",
        "text/plain; charset=utf-8",
        "api/server.py",
        note="RFC 9116 历史兼容路径，与规范路径同一份文件。",
    ),
    "/.well-known/agent.json": Surface(
        "/.well-known/agent.json",
        "api/static/.well-known/agent.json",
        "application/json; charset=utf-8",
        "api/server.py",
    ),
    "/.well-known/ai-plugin.json": Surface(
        "/.well-known/ai-plugin.json",
        "api/static/.well-known/ai-plugin.json",
        "application/json; charset=utf-8",
        "api/server.py",
    ),
    "/llms.txt": Surface(
        "/llms.txt", "api/static/llms.txt", "text/plain; charset=utf-8",
        "api/server.py",
        note="与 docs/llms.txt 必须字节一致（tests/test_compliance.py 钉死）。",
    ),
    "/llms-full.txt": Surface(
        "/llms-full.txt", "api/static/llms-full.txt", "text/plain; charset=utf-8",
        "api/server.py",
    ),
    "/geo-faqs.json": Surface(
        "/geo-faqs.json", "api/static/geo-faqs.json",
        "application/json; charset=utf-8", "api/server.py",
    ),
    "/agent-discovery.json": Surface(
        "/agent-discovery.json", "api/static/agent-discovery.json",
        "application/json; charset=utf-8", "api/server.py",
    ),
    "/robots.txt": Surface(
        "/robots.txt", "api/static/robots.txt", "text/plain; charset=utf-8",
        "api/server.py",
    ),
    "/sitemap.xml": Surface(
        "/sitemap.xml", "api/static/sitemap.xml",
        "application/xml; charset=utf-8", "api/server.py",
    ),
    "/feeds.xml": Surface(
        "/feeds.xml", "api/static/feeds.xml",
        "application/atom+xml; charset=utf-8", "api/server.py",
    ),
    "/manifest.json": Surface(
        "/manifest.json", "api/static/manifest.json",
        "application/manifest+json; charset=utf-8", "api/server.py",
    ),
    # 计算型：没有落盘文件，响应由代码生成。它们同样是对外声明面，
    # 因此也在册（孪生审计对它们天然无话可说）。
    "/.well-known/jwks.json": Surface(
        "/.well-known/jwks.json", "", "application/json; charset=utf-8",
        "api/server.py", kind="computed",
        note="RFC 7517 公钥发现，由 eco.verifiable_identity.jwks() 生成。",
    ),
}


# ── 孪生副本台账 ──────────────────────────────────────────────────────
# 键 = 仓库相对路径。门禁会把"两根下同相对路径都存在"的情况全部列出来，
# 凡不在此表里的即报红 —— 这是"死副本复生"的机械拦截。
SHADOWS = {
    "api/static/.well-known/agent-card.json": Shadow(
        "api/static/.well-known/agent-card.json",
        "/.well-known/agent-card.json",
        role="superseded",
        reason=(
            "形态是 MCP 工具目录（23 个 skill 带 input/output_schema），"
            "不是 A2A Agent Card（A2A 的 AgentSkill 用 tags/examples）。"
            "该 URL 现由 docs 那份服务，这份仅供测试夹具与规则数声明位使用；"
            "曾在 server.py:768 由一个不可达分支引用，已删除。"
        ),
    ),
    "docs/.well-known/mcp/server-card.json": Shadow(
        "docs/.well-known/mcp/server-card.json",
        "/.well-known/mcp/server-card.json",
        role="leftover",
        reason=(
            "该 URL 由 api/static 那份服务（线上实测逐字段相等）。此副本规模小得多"
            "（2900 vs 6163 字节），无消费者。"
        ),
    ),
    "docs/robots.txt": Shadow(
        "docs/robots.txt", "/robots.txt", role="leftover",
        reason="该 URL 由 api/static/robots.txt 服务；GitHub Pages 已 301 回 aishield.tools，docs 侧不外服。",
    ),
    "docs/llms.txt": Shadow(
        "docs/llms.txt", "/llms.txt", role="mirror",
        reason="与 api/static/llms.txt 必须字节一致；tests/test_compliance.py 直接断言。",
    ),
    "docs/llms-full.txt": Shadow(
        "docs/llms-full.txt", "/llms-full.txt", role="mirror",
        reason="api/static 那份的服务副本；两份在规则数门禁里同列（历史发布日志，豁免改写）。",
    ),
}


def abs_path(rel: str) -> str:
    """仓库相对路径 → 绝对路径。"""
    return os.path.join(REPO_ROOT, rel.replace("/", os.sep))


def other_root(rel: str) -> str:
    """把路径换到另一个声明面根下（api/static <-> docs）。

    非声明面根下的路径返回空串 —— 调用方据此跳过，不要瞎猜。
    """
    rel = rel.replace(os.sep, "/")
    if rel.startswith(ROOT_STATIC + "/"):
        return ROOT_DOCS + rel[len(ROOT_STATIC):]
    if rel.startswith(ROOT_DOCS + "/"):
        return ROOT_STATIC + rel[len(ROOT_DOCS):]
    return ""


def twin_of(rel: str) -> str:
    """孪生文件路径（另一根下的同相对路径）。"""
    return other_root(rel)


def iter_twins():
    """产出所有"两根下都存在"的孪生对：(served_rel 或 '', twin_rel, url)。

    - 服务副本在 A 根、孪生在 B 根 → (served_rel, twin_rel, url)
    - 服务副本本身就是 B 根（如 agent-card）、孪生在 A 根 → 同上
    - 未在册的孪生 → served_rel 为空串（调用方判违规）
    """
    rel_to_url = {}
    for s in SERVED.values():
        if s.rel:
            rel_to_url[s.rel.replace(os.sep, "/")] = s.url

    seen = set()
    for rel, url in sorted(rel_to_url.items()):
        tw = twin_of(rel)
        if not tw or not os.path.exists(abs_path(tw)):
            continue
        key = tuple(sorted((rel, tw)))
        if key in seen:
            continue
        seen.add(key)
        served = rel if os.path.exists(abs_path(rel)) else ""
        yield served, tw, url


def served_by(rel: str):
    """反查：这个文件是不是某个 URL 的服务副本？返回 Surface 或 None。"""
    rel = rel.replace(os.sep, "/")
    for s in SERVED.values():
        if s.rel and s.rel.replace(os.sep, "/") == rel:
            return s
    return None


if __name__ == "__main__":  # pragma: no cover - 人工速查
    print(f"服务面 {len(SERVED)} 个 / 孪生台账 {len(SHADOWS)} 条")
    for url, s in sorted(SERVED.items()):
        mark = "计算型" if s.kind == "computed" else (
            "存在" if os.path.exists(abs_path(s.rel)) else "缺文件")
        print(f"  {url:42s} -> {s.rel or '(computed)':52s} [{mark}]")
    print("\n孪生审计：")
    for served_rel, twin_rel, url in iter_twins():
        tag = SHADOWS.get(twin_rel.replace(os.sep, "/"))
        verdict = f"已登记({tag.role})" if tag else "!! 未登记"
        print(f"  {url:42s} {twin_rel:52s} {verdict}")
