"""路由可达性门禁：代码里写下的每条 /api/v1/... 都必须被服务端真的接住。

═════════════════════════════════════════════════════════════════
  这条测试为什么存在（2026-10-05 真踩）
═════════════════════════════════════════════════════
L3 意图授权加完端点后，单测全绿、``openapi_contract --check`` 也报 OK
（实现 129 / 契约 129 / 清单 129），但线上 ``POST /api/v1/intent/mandates``
**一直是 404**。

根因不在 ecosystem_api 的 if 链（那条链上写得好好的），而在 ``api/server.py``
的入口白名单：生态类请求要先过 ``path.startswith(...)`` 那一串前缀才被转给
ecosystem_api，白名单里没有 ``/api/v1/intent``，请求直接掉进全局兜底返 404。

``openapi_contract`` 抓不到它，因为它的口径是「探针探得到命中的路由」——
404 的路由对探针来说等于不存在，双向 diff 的两边都看不见，**门禁保持绿灯**。
这就是典型的假绿：单元测的是 handler 函数（绕过了入口白名单），探针测的是
「已经能通的东西」，两边都没测到「声明了但根本到不了」。

所以这里补一层：静态抽取代码里**可执行**的路由字面量，逐条核对
``api/server.py`` 有没有能接住它的分支。纯 AST + 正则，不跑探针（探针要几分钟，
不适合进套件），因此这条门禁跑得比任何单测都快。

═════════════════════════════════════════════════════════════════
  为什么要用 AST 而不是正则扫字面量
═════════════════════════════════════════════════════
正则会把**文档字符串里举例子**的路径也当成路由（比如 trust_api 的 docstring 里
写的 ``POST /api/v1/attestations`` 从没实现过），于是门禁一上来就报 15 条假阳性，
真问题反而被淹掉。AST 版只收真在代码里出现的字符串常量，并显式跳过 docstring。

!!! 加新路由的标准动作 !!!
────────────────────────
1. handler 里写 ``if path == "/api/v1/xxx"``；
2. **在 server.py 的 do_GET / do_POST 前缀白名单里补上新前缀**（本文件会替你盯）；
3. 跑 ``python scripts/gen_openapi_spec.py`` 让契约跟上。
"""
from __future__ import annotations

import ast
import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_DIR = os.path.join(REPO, "api")
SERVER = os.path.join(API_DIR, "server.py")



def _strip_docstring(body: list) -> list:
    """去掉函数/模块首个字符串常量（docstring）后的节点列表。"""
    if (body and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)):
        return body[1:]
    return body


def code_route_literals(root: str = API_DIR) -> set:
    """api/ 下**可执行代码**里出现过的 /api/v1/... 字面量（不含 docstring）。"""
    out: set = set()
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            if not name.endswith(".py"):
                continue
            path = os.path.join(dirpath, name)
            try:
                with open(path, encoding="utf-8") as f:
                    tree = ast.parse(f.read())
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue
            stack = [tree]
            while stack:
                node = stack.pop()
                if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                                     ast.ClassDef)):
                    for child in _strip_docstring(getattr(node, "body", [])):
                        stack.append(child)
                    continue
                # 剩下的 ast.Expr 已经不是 docstring（docstring 在上一步被剥掉）。
                # 注意这里只能取值、不能把节点自己再压栈 —— 压回去会和自己成环，
                # 遍历当场死循环（2026-10-05 的真实挂死就是这个）。
                if isinstance(node, ast.Expr):
                    val = node.value
                    if isinstance(val, ast.Constant) and isinstance(val.value, str) \
                            and val.value.startswith("/api/v1/"):
                        out.add(val.value)
                    continue
                if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                        and node.value.startswith("/api/v1/")):
                    out.add(node.value)
                    continue
                for child in ast.iter_child_nodes(node):
                    stack.append(child)
    return out


def server_dispatch_branches(path: str = SERVER) -> tuple:
    """server.py 里能接住请求的所有分支（AST 精确抽取，不靠正则）。

    三种形态都得认，缺一种就会把活路由误判成死路由：

      * ``path.startswith("/api/v1/x")`` —— 入口前缀白名单（本漏洞的根因）；
      * ``path == "/api/v1/x"`` —— do_GET/do_POST 尾部的兜底 if 链；
      * ``path in ("/api/v1/a", "/api/v1/b")`` —— 一对多比较（export/* 就是这么写的）。

    返回 (星前缀集合, 精确路径集合)。
    """
    prefixes: set = set()
    exact: set = set()
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    def is_path(node) -> bool:
        return isinstance(node, ast.Name) and node.id == "path"

    def const_str(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None

    for node in ast.walk(tree):
        # 形态一：path.startswith("/api/v1/x")
        # 不用 ast.StartsWith —— 那是 3.14 才有的 operator method，3.13 一跑就
        # AttributeError（本机 managed 解释器是 3.13），这里取跨版本写法。
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == "startswith" and node.args and is_path(node.func.value):
            val = const_str(node.args[0])
            if val is not None:
                prefixes.add(val)
            continue
        # 形态二/三：path == "..." / path in ("a", "b")
        if not isinstance(node, ast.Compare) or not is_path(node.left):
            continue
        for op, comp in zip(node.ops, node.comparators):
            val = const_str(comp)
            if isinstance(op, (ast.In, ast.NotIn)):
                # ``path in ("/api/v1/a", "/api/v1/b")``：comp 是元组，const_str
                # 返回 None —— 早先就是在这儿先 `continue` 了，把 export/* 四条
                # 真路由误判成死路由。所以元组必须先拆，**再**决定要不要 continue。
                if isinstance(comp, (ast.Tuple, ast.List, ast.Set)):
                    for elt in comp.elts:
                        sub_val = const_str(elt)
                        if sub_val is not None:
                            exact.add(sub_val)
                    continue
                if val is None:
                    continue
                if val.startswith("/api/v1/"):
                    exact.add(val)
                continue
            if val is None:
                continue
            if isinstance(op, ast.Eq):
                exact.add(val)
    return prefixes, exact


class TestRouteReachability(unittest.TestCase):
    """代码里声明的路由，必须有一条真能走通的分派分支。"""

    def setUp(self):
        self.prefixes, self.exact = server_dispatch_branches()
        self.literals = code_route_literals()

    def test_every_route_literal_has_a_dispatch_branch(self):
        # 带 "?" 的是拼 URL 的片段（"/api/v1/checkout/create?product_key="），
        # 真正的路由不会带 query —— 它们既不在前缀白名单里也不该在那儿。
        unreachable = sorted(
            p for p in self.literals
            if "?" not in p
            and p not in self.exact
            and not any(p.startswith(pre) for pre in self.prefixes))
        if unreachable:
            self.fail(
                "这些 /api/v1/... 字面量在 api/ 下的代码里存在，但 api/server.py 里\n"
                "没有任何分支能接住它们 —— 请求会掉进全局兜底返 404（单元测绕过了入口\n"
                "白名单，探针看不见 404，所以两个门禁都是绿的）。\n"
                f"   未接住 {len(unreachable)} 条：{unreachable}\n"
                "   修法：在 do_GET / do_POST 的 path.startswith(...) 白名单里补上对应前缀。")

    def test_l3_intent_prefix_is_in_dispatch_whitelist(self):
        """2026-10-05 的 regression：/api/v1/intent 漏在白名单外，直接 404。"""
        self.assertIn("/api/v1/intent", self.prefixes,
                      "L3 意图授权的入口前缀必须同时出现在 do_GET 与 do_POST 白名单里")

    def test_intent_routes_are_code_literals(self):
        """L3 三条路由必须在代码里（不是文档），且都在可达集合内。"""
        for p in ("/api/v1/intent/mandates", "/api/v1/intent/mandates/verify",
                  "/api/v1/intent/mandates/evaluate"):
            self.assertIn(p, self.literals)

    def test_collected_literals_look_like_routes(self):
        """AST 抽取必须保持精确：收上来的只能是「像路由」的字符串。

        曾经踩过：正则扫字面量会把 docstring 里举例子写的整段 API 清单也收进来
        （ ``POST /api/v1/attestations — Create Trust Attestation credential``
        这种），一上来就报 15 条假阳性，真问题被淹掉 —— 所以这里钉死
        「收上来的东西长什么样」，抽取一旦放宽（有人改成正则、或把 docstring
        的剥离去掉）立即红，而不是等若干天后淹掉别的告警。
        """
        for lit in sorted(self.literals):
            self.assertTrue(lit.startswith("/api/v1/"), f"不该收进文档文本：{lit!r}")
            self.assertNotIn("\n", lit, f"不该收进多行文本：{lit!r}")
            self.assertLess(len(lit), 80, f"不像路由字面量：{lit!r}")
            self.assertNotIn(" ", lit, f"路径里不该有空格：{lit!r}")

    def test_url_fragment_literals_are_not_gated(self):
        """带 ? 的字面量是拼 URL 用的片段（不是路由），不进可达性门禁。"""
        frags = [p for p in self.literals if "?" in p]
        self.assertTrue(frags, "应当至少有一条 ? 片段字面量，否则这条用例已经空转")
        for frag in frags:
            self.assertNotIn(frag, self.exact)


if __name__ == "__main__":
    unittest.main(verbosity=2)
