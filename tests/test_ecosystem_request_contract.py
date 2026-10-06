#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生态请求体声明表的契约测试。

它守的不是"接口能跑"，而是**这份声明表没有撒谎**：

  1. 声明的 path+verb 必须真的在 ``api/openapi_runtime_paths.json`` 里
     （不许多出一条 phantom 路由）；
  2. 声明的每个字段名必须能在 ``source`` 指向的 handler 文件里以
     ``"字段名"`` 字面量找到（不许有编出来的字段 —— 这是本表存在的全部理由）；
  3. required 必须是 properties 的子集；
  4. ``get_openapi_spec()`` 输出里这些操作确实带上了 requestBody；
  5. 数量不许悄悄缩水（>= 20 条）。

第 2 条是这套测试的核心：只要有人凭想象往表里塞一个字段名，它立刻红。

用 unittest 而不是 pytest：本仓测试套件的第三方依赖只有 cryptography + pyyaml
（``.github/actions/prepare-tests`` 那行 pip install 是被 E12 门禁读取的声明），
引 pytest 会被 validate_workflows 的 E12 当场拦下 —— 干净 runner 上会变 ImportError。
"""
from __future__ import annotations

import json
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from api.ecosystem_request_bodies import ECO_REQUEST_BODIES  # noqa: E402
from api.openapi_spec import get_openapi_spec  # noqa: E402

_MANIFEST = os.path.join(REPO, "api", "openapi_runtime_paths.json")


def _runtime_routes() -> dict:
    with open(_MANIFEST, encoding="utf-8") as f:
        man = json.load(f)
    out: dict = {}
    for route in man.get("routes", []):
        out.setdefault(route["path"], set()).update(
            o["verb"] for o in route.get("operations", [])
        )
    return out


class TestDeclarationTableShape(unittest.TestCase):
    def test_at_least_twenty_entries(self):
        self.assertGreaterEqual(
            len(ECO_REQUEST_BODIES), 20,
            f"声明表只有 {len(ECO_REQUEST_BODIES)} 条，验收要求 agent 最需要的 20 条",
        )

    def test_required_subset_of_properties(self):
        for (path, verb), spec in ECO_REQUEST_BODIES.items():
            props = set(spec["properties"])
            req = set(spec.get("required") or [])
            self.assertTrue(
                req <= props,
                f"{verb.upper()} {path}: required 不是 properties 子集",
            )

    def test_verb_is_post(self):
        for (path, verb) in ECO_REQUEST_BODIES:
            self.assertEqual(verb, "post", f"{path} 声明了非 POST 动词 {verb}")

    def test_source_file_exists(self):
        for (path, _verb), spec in ECO_REQUEST_BODIES.items():
            self.assertTrue(
                os.path.exists(os.path.join(REPO, spec["source"])),
                f"{path} 的 source {spec['source']} 不存在",
            )


class TestNoPhantomRoutes(unittest.TestCase):
    def test_every_declared_route_exists_at_runtime(self):
        routes = _runtime_routes()
        for (path, verb), spec in ECO_REQUEST_BODIES.items():
            self.assertIn(
                path, routes,
                f"{path} 不在 api/openapi_runtime_paths.json —— 这是 phantom 路由。"
                f"（source={spec['source']}）",
            )
            self.assertIn(
                verb, routes[path],
                f"{verb.upper()} {path} 未被运行时探针命中（该 path 实际只有 "
                f"{sorted(routes[path])}）",
            )


class TestNoFabricatedFields(unittest.TestCase):
    def test_every_field_name_appears_in_source(self):
        """字段名必须在该 handler 源码里以 "字段名" 字面量出现。"""
        missing = []
        for (path, _verb), spec in ECO_REQUEST_BODIES.items():
            with open(os.path.join(REPO, spec["source"]), encoding="utf-8") as f:
                src = f.read()
            for field in spec["properties"]:
                if f'"{field}"' not in src and f"'{field}'" not in src:
                    missing.append(f"{path} :: {field} (source={spec['source']})")
        self.assertEqual(
            missing, [],
            "以下字段在源码里找不到字面量，属于凭空声明：\n  " + "\n  ".join(missing),
        )


class TestSpecInjection(unittest.TestCase):
    def test_spec_carries_request_body_for_every_entry(self):
        spec = get_openapi_spec()
        paths = spec["paths"]
        for (path, verb) in ECO_REQUEST_BODIES:
            op = paths.get(path, {}).get(verb)
            self.assertIsNotNone(op, f"契约里没有 {verb.upper()} {path}")
            self.assertTrue(
                op.get("requestBody"), f"{verb.upper()} {path} 注入后仍无 requestBody"
            )

    def test_declared_fields_survive_into_spec(self):
        spec = get_openapi_spec()
        components = (spec.get("components") or {}).get("schemas") or {}
        for (path, verb), entry in ECO_REQUEST_BODIES.items():
            rb = spec["paths"][path][verb]["requestBody"]
            bsch = rb["content"]["application/json"]["schema"]
            # curated 层常用 $ref 指向 components.schemas，这里解开再比。
            ref = bsch.get("$ref")
            if ref:
                bsch = components.get(ref.split("/")[-1]) or {}
            got = set(bsch.get("properties") or {})
            self.assertLessEqual(
                set(entry["properties"]), got,
                f"{verb.upper()} {path} 契约里的字段少于声明表："
                f"缺 {sorted(set(entry['properties']) - got)}",
            )

    def test_injection_counter_matches(self):
        spec = get_openapi_spec()
        injected = spec.get("x-aishield-request-bodies-injected")
        self.assertIsInstance(injected, int)
        self.assertGreater(injected, 0, "注入计数器缺失")


class TestIndexReflectsDeclarations(unittest.TestCase):
    """索引生成器应该看到这些 requestBody —— 否则门禁是在自欺。"""

    def test_agent_api_index_generator_sees_bodies(self):
        if os.path.join(REPO, "scripts") not in sys.path:
            sys.path.insert(0, os.path.join(REPO, "scripts"))
        import gen_agent_api_index as g  # noqa: PLC0415

        data = g.collect()
        self.assertGreater(data["with_body"], 0)
        self.assertLess(data["total"] - data["with_body"], data["total"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
