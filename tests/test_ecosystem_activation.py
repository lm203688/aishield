"""
tests/test_ecosystem_activation.py — Agent 生态 5 支柱落地自证测试

覆盖：
  1. eco.specialist_registry：8 域注册 / 查询 / 续期 / 吊销
  2. eco.kyad_compat：KYA claims + Web Bot Auth + ERC-8004
  3. api.ecosystem_api：Agent Card sign/verify + 责任链 + 协议桥 + 中立身份
  4. 篡改检测（防"拿到信任签名后偷改 card"的关键场景）

零外部依赖；直接用 unittest 跑。
"""
from __future__ import annotations

import json
import os
import sys
import unittest
from copy import deepcopy

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _ROOT + "/api" not in sys.path:
    sys.path.insert(0, _ROOT + "/api")
if _ROOT + "/eco" not in sys.path:
    sys.path.insert(0, _ROOT + "/eco")


class SpecialistRegistryTest(unittest.TestCase):
    def setUp(self):
        from eco import specialist_registry as sr
        # 强制重置内存注册表
        sr.seed_if_empty(force=True)

    def test_8_domains_registered(self):
        from eco import specialist_registry as sr
        cats = sr.domains_catalog()
        self.assertEqual(len(cats), 8)
        ids = {c["id"] for c in cats}
        self.assertIn("legal", ids)
        self.assertIn("medical", ids)
        self.assertIn("finance", ids)
        self.assertIn("civic", ids)

    def test_register_and_lookup(self):
        from eco import specialist_registry as sr
        rec = sr.register_agent(
            agent_id="test-med-1", name="Med Agent", domain="medical",
            capabilities=["diagnosis", "triage"], url="https://example.org/med")
        self.assertEqual(rec["domain"], "medical")
        self.assertEqual(rec["state"], "active")
        got = sr.get("test-med-1")
        self.assertEqual(got["name"], "Med Agent")

    def test_renew_and_revoke(self):
        from eco import specialist_registry as sr
        sr.register_agent(agent_id="test-x-1", name="X", domain="legal",
                           capabilities=["review"])
        r = sr.renew("test-x-1")
        self.assertEqual(r["state"], "active")
        r = sr.revoke("test-x-1", reason="test")
        self.assertEqual(r["state"], "revoked")
        self.assertEqual(r["revoke_reason"], "test")
        # 已吊销的不应出现在列表
        lst = sr.list_agents(domain="legal")
        self.assertNotIn("test-x-1", [x["agent_id"] for x in lst])

    def test_invalid_domain_rejected(self):
        from eco import specialist_registry as sr
        with self.assertRaises(ValueError):
            sr.register_agent(agent_id="bad", name="X", domain="nonsense",
                               capabilities=["x"])

    def test_empty_capabilities_rejected(self):
        from eco import specialist_registry as sr
        with self.assertRaises(ValueError):
            sr.register_agent(agent_id="bad2", name="X", domain="legal",
                               capabilities=[])


class KyadCompatTest(unittest.TestCase):
    def test_kya_claims_structure(self):
        from eco import kyad_compat as kc
        claims = kc.build_kya_claims(
            agent_id="test-agent-1", name="Test Agent",
            capabilities=["scan", "audit"], trust_score=80)
        self.assertEqual(claims["schema"], kc.KYA_SCHEMA)
        self.assertEqual(claims["alg"], "ES256")
        # 至少 4 个 claims：metadata + capability + trust + ...
        self.assertGreaterEqual(len(claims["claims"]), 3)
        for c in claims["claims"]:
            self.assertIn("cty", c)
            self.assertIn("disc", c)
            self.assertEqual(len(c["disc"]), 44)  # base64url sha-256 = 43+padding=44

    def test_web_bot_auth_headers(self):
        from eco import kyad_compat as kc
        h = kc.build_web_bot_auth_headers(agent_id="test-1", agent_url="https://x.example")
        self.assertIn("(request-target)", h)
        self.assertIn("X-Web-Bot-Auth-Agent", h)
        self.assertIn("X-Web-Bot-Auth-URL", h)
        self.assertIn("X-Web-Bot-Auth-Timestamp", h)
        self.assertEqual(h["X-Web-Bot-Auth-Agent"], "test-1")

    def test_erc8004_round_trip(self):
        from eco import kyad_compat as kc
        did = kc.wallet_to_did("0x1234567890abcdef1234567890abcdef12345678", 1)
        self.assertTrue(did.startswith("did:erc8004:chain1:"))
        parsed = kc.did_to_wallet(did)
        self.assertEqual(parsed["chain_id"], 1)
        self.assertEqual(parsed["address"], "0x1234567890abcdef1234567890abcdef12345678")

    def test_erc8004_invalid_address_rejected(self):
        from eco import kyad_compat as kc
        with self.assertRaises(ValueError):
            kc.wallet_to_did("not-a-wallet", 1)
        with self.assertRaises(ValueError):
            kc.wallet_to_did("0xshort", 1)
        with self.assertRaises(ValueError):
            kc.wallet_to_did("0xZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ", 1)

    def test_agent_card_to_identity_full(self):
        from eco import kyad_compat as kc
        card = {
            "name": "Med-Consult",
            "url": "https://x.example/med",
            "capabilities": {"supported": ["consult", "triage"]},
            "aishield": {"signature": "sig-abc", "signer_did": "did:aishield:ts",
                          "signed_at": "2026-09-24T09:00:00+08:00"},
        }
        ident = kc.agent_card_to_identity(card, trust_score=75)
        self.assertEqual(ident["agent_id"], "Med-Consult")
        self.assertEqual(len(ident["kya"]["claims"]), 4)  # meta + cap + trust + attestation
        self.assertTrue(ident["kya_sd_jwt_compact"].startswith("eyJ"))  # base64
        self.assertIn("headers", ident["web_bot_auth"])


class EcosystemApiTest(unittest.TestCase):
    def setUp(self):
        import ecosystem_api
        ecosystem_api._chains.clear()

    def test_agent_card_sign_and_verify(self):
        import ecosystem_api
        card = {"name": "CardTest", "url": "https://x.example/card",
                "capabilities": {"supported": ["scan"]}}
        signed, sc = ecosystem_api._agent_card_sign(card, trust_score=85)
        self.assertEqual(sc, 200)
        self.assertIn("aishield", signed)
        self.assertEqual(signed["aishield"]["trust_score"], 85)

        v, sc = ecosystem_api._agent_card_verify(signed, None)
        self.assertEqual(sc, 200)
        self.assertTrue(v["valid"])

    def test_agent_card_tamper_detection(self):
        """篡改已签名的 card 必须被检出。"""
        import ecosystem_api
        card = {"name": "TamperTest", "url": "https://x.example/t",
                "capabilities": {"supported": ["scan"]}}
        signed, _ = ecosystem_api._agent_card_sign(card, 90)
        evil = deepcopy(signed)
        evil["capabilities"] = {"supported": ["admin", "delete-all"]}
        v, sc = ecosystem_api._agent_card_verify(evil, None)
        self.assertEqual(sc, 400)
        self.assertFalse(v["valid"])

    def test_chain_create_append_verify(self):
        import ecosystem_api
        c, sc = ecosystem_api._chain_create(None)
        self.assertEqual(sc, 201)
        cid = c["chain_id"]

        e1, sc = ecosystem_api._chain_append(
            cid, {"agent_id": "planner", "action": "plan",
                   "input_ref": "user:do-thing",
                   "output_ref": {"subtasks": ["s1"]}})
        self.assertEqual(sc, 201)
        self.assertEqual(e1["seq"], 1)

        e2, sc = ecosystem_api._chain_append(
            cid, {"agent_id": "executor", "action": "call_tool:execute",
                   "parent_seq": e1["seq"], "input_ref": e1["output_ref"],
                   "output_ref": {"result": "done"}})
        self.assertEqual(sc, 201)
        self.assertEqual(e2["parent_seq"], 1)

        vr, sc = ecosystem_api._chain_verify(cid)
        self.assertEqual(sc, 200)
        self.assertTrue(vr["valid"])
        self.assertEqual(vr["entries"], 2)

    def test_chain_trace_root_cause(self):
        import ecosystem_api
        c, _ = ecosystem_api._chain_create(None)
        cid = c["chain_id"]
        e1, _ = ecosystem_api._chain_append(
            cid, {"agent_id": "planner", "action": "plan",
                   "input_ref": "x", "output_ref": "p_out"})
        e2, _ = ecosystem_api._chain_append(
            cid, {"agent_id": "executor", "action": "execute",
                   "parent_seq": 1, "input_ref": "p_out",
                   "output_ref": "bad_output"})
        tr, sc = ecosystem_api._chain_trace(cid, "bad_output")
        self.assertEqual(sc, 200)
        self.assertEqual(tr["depth"], 2)
        self.assertEqual(tr["root_cause"]["agent_id"], "planner")

    def test_protocol_bridge_normalize_and_translate(self):
        import ecosystem_api
        mcp_payload = {"name": "BridgeTest",
                       "tools": [{"name": "add", "description": "add two numbers"}]}
        norm, sc = ecosystem_api._bridge_normalize("mcp", mcp_payload)
        self.assertEqual(sc, 200)
        self.assertEqual(norm["universal_agent"]["name"], "BridgeTest")
        self.assertEqual(len(norm["universal_agent"]["skills"]), 1)

        tr, sc = ecosystem_api._bridge_translate("a2a", mcp_payload, "mcp")
        self.assertEqual(sc, 200)
        self.assertEqual(tr["result"]["name"], "BridgeTest")
        self.assertIn("aishield", tr["result"])

    def test_protocol_bridge_invalid_proto_rejected(self):
        import ecosystem_api
        _, sc = ecosystem_api._bridge_normalize("graphql", {})
        self.assertEqual(sc, 400)

    def test_specialist_register_and_query(self):
        import ecosystem_api
        from eco import specialist_registry as sr
        sr.seed_if_empty(force=True)
        # 注册一个测试 agent
        data = {"agent_id": "test-ea-1", "name": "Test EA",
                "domain": "research", "capabilities": ["literature-review"]}
        rec, sc = ecosystem_api._specialist_register(data)
        self.assertEqual(sc, 201)
        self.assertEqual(rec["domain"], "research")

        got, sc = ecosystem_api._specialist_get("test-ea-1")
        self.assertEqual(sc, 200)
        self.assertEqual(got["name"], "Test EA")

    def test_specialist_invalid_domain_rejected(self):
        import ecosystem_api
        data = {"agent_id": "bad", "name": "X",
                "domain": "nonsense", "capabilities": ["x"]}
        rec, sc = ecosystem_api._specialist_register(data)
        self.assertEqual(sc, 400)
        self.assertIn("error", rec)

    def test_kyad_export_via_ecosystem_api(self):
        import ecosystem_api
        card = {"name": "KyaTest", "url": "https://x.example/kya",
                "capabilities": {"supported": ["foo"]},
                "aishield": {"signature": "s", "signer_did": "did:aishield:ts",
                              "signed_at": "now"}}
        ident, sc = ecosystem_api._agent_card_export_identity(card, 70)
        self.assertEqual(sc, 200)
        self.assertIn("kya", ident)
        self.assertIn("web_bot_auth", ident)
        self.assertIn("kya_sd_jwt_compact", ident)

    def test_erc8004_wrap_via_ecosystem_api(self):
        import ecosystem_api
        r, sc = ecosystem_api._erc8004_wrap("0x1234567890abcdef1234567890abcdef12345678", 1)
        self.assertEqual(sc, 200)
        self.assertTrue(r["did"].startswith("did:erc8004:"))

    def test_erc8004_invalid_rejected(self):
        import ecosystem_api
        r, sc = ecosystem_api._erc8004_wrap("not-valid", 1)
        self.assertEqual(sc, 400)

    def test_route_dispatch_handle_get_unknown(self):
        import ecosystem_api
        r, sc = ecosystem_api.handle_get("/api/v1/ecosystem/does-not-exist")
        self.assertEqual(sc, 404)

    def test_route_dispatch_handle_post_unknown(self):
        import ecosystem_api
        r, sc = ecosystem_api.handle_post("/api/v1/ecosystem/nope", {})
        self.assertEqual(sc, 404)


class ShipGateTest(unittest.TestCase):
    """发布门禁 CLI 的核心函数测试（不实际启动 subprocess）。"""

    def test_judge_ship_passes(self):
        sys.path.insert(0, _ROOT + "/scripts")
        from scripts.ship_gate import _judge, _count_findings_by_severity, _compute_trust_score
        counts = _count_findings_by_severity([])
        score = _compute_trust_score([])
        info = _judge(score, counts)
        self.assertEqual(info["verdict"], "ship")
        self.assertEqual(info["score"], 100)

    def test_judge_hold_on_high(self):
        from scripts.ship_gate import _judge, _count_findings_by_severity, _compute_trust_score
        findings = [{"severity": "high"}, {"severity": "medium"}]
        counts = _count_findings_by_severity(findings)
        score = _compute_trust_score(findings)
        info = _judge(score, counts)
        self.assertEqual(info["verdict"], "hold")

    def test_judge_break_on_critical(self):
        from scripts.ship_gate import _judge, _count_findings_by_severity, _compute_trust_score
        findings = [{"severity": "critical"}]
        counts = _count_findings_by_severity(findings)
        score = _compute_trust_score(findings)
        info = _judge(score, counts)
        self.assertEqual(info["verdict"], "break")

    def test_exit_code_verdict_mapping(self):
        from scripts.ship_gate import _exit_code
        self.assertEqual(_exit_code("ship", [], False), 0)
        self.assertEqual(_exit_code("break", [], False), 1)
        self.assertEqual(_exit_code("hold", [], True), 2)
        self.assertEqual(_exit_code("hold", [], False), 0)

    def test_attestation_output_shape(self):
        from scripts.ship_gate import _make_attestation
        result = {"target": "foo.json", "files_scanned": 1, "findings": []}
        vi = {"verdict": "ship", "score": 100, "reason": "OK",
              "counts": {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}}
        att = _make_attestation(result, vi)
        self.assertIn("schema", att)
        self.assertIn("issuer", att)
        self.assertIn("subject", att)
        self.assertEqual(att["verdict"], "ship")
        self.assertEqual(att["trust_score"], 100)


# ══════════════════════════════════════════════
#  R2: KYA 完整版签名 + Leaderboard + Contributors
# ══════════════════════════════════════════════
class KyadFullSignatureTest(unittest.TestCase):
    """KYA SD-JWT 完整版（带 Ed25519 签名）"""

    def test_signed_sd_jwt_round_trip(self):
        from eco import crypto_sign as cs
        from eco.kyad_compat import build_kya_claims, to_sd_jwt_compact, verify_sd_jwt
        alg, priv, pub = cs.generate_keypair()
        claims = build_kya_claims(agent_id="x", name="X",
                                   capabilities=["scan"], trust_score=70)
        jwt = to_sd_jwt_compact(claims, private_key_b64=priv, private_key_alg=alg)
        parts = jwt.split("~")[0].split(".")
        self.assertEqual(len(parts), 3)  # header.payload.signature
        self.assertGreater(len(parts[2]), 20)  # 签名非空
        v = verify_sd_jwt(jwt, pub, alg)
        self.assertTrue(v["valid"])
        # 无 attestations 时 claims = meta + capability + trust = 3
        self.assertEqual(v["claims_count"], 3)

    def test_unsigned_sd_jwt_is_structure_only(self):
        from eco.kyad_compat import build_kya_claims, to_sd_jwt_compact
        claims = build_kya_claims(agent_id="y", name="Y", capabilities=["a"])
        jwt = to_sd_jwt_compact(claims)  # 无 private_key
        # 未签名时 signature 部分为空
        self.assertTrue(jwt.endswith("."))

    def test_signed_sd_jwt_tamper_detection(self):
        """篡改 payload 或 discs 都必须失败验证。"""
        from eco import crypto_sign as cs
        from eco.kyad_compat import build_kya_claims, to_sd_jwt_compact, verify_sd_jwt
        alg, priv, pub = cs.generate_keypair()
        claims = build_kya_claims(agent_id="z", name="Z", capabilities=["scan"])
        jwt = to_sd_jwt_compact(claims, private_key_b64=priv, private_key_alg=alg)
        # 篡改 payload（替换第二段 base64）
        head, discs = jwt.split("~")
        parts = head.split(".")
        tampered = ".".join([parts[0], "eyJ0YW1wZXJlZA", parts[2]]) + "~" + discs
        v = verify_sd_jwt(tampered, pub, alg)
        self.assertFalse(v["valid"])
        self.assertEqual(v["reason"], "signature verification failed")


class LeaderboardTest(unittest.TestCase):
    """Trust Leaderboard 聚合。"""

    def setUp(self):
        from eco import leaderboard as lb
        self.lb = lb

    def test_top_by_score_returns_sorted_list(self):
        rows = self.lb.top_by_score(limit=10)
        # 全库至少有 1 条数据（真实 api/data/certifications.json）
        self.assertIsInstance(rows, list)
        for i in range(1, len(rows)):
            self.assertGreaterEqual(rows[i - 1]["score"], rows[i]["score"])

    def test_top_by_domain_invalid_domain_rejected(self):
        with self.assertRaises(ValueError):
            self.lb.top_by_domain("nonsense", limit=5)

    def test_snapshot_schema(self):
        snap = self.lb.snapshot()
        self.assertEqual(snap["schema"],
                         "https://aishield.tools/schema/trust-leaderboard/v1")
        for k in ("top_by_score", "top_by_badge", "top_by_domain", "top_by_provider",
                   "totals", "generated_at"):
            self.assertIn(k, snap)
        # 8 域全部在快照里
        self.assertEqual(len(snap["top_by_domain"]), 8)

    def test_top_by_provider_aggregation(self):
        provs = self.lb.top_by_provider(limit=5)
        for p in provs:
            self.assertIn("provider", p)
            self.assertIn("count", p)
            self.assertIn("mean_score", p)
            self.assertIn("max_score", p)


class ContributorsTest(unittest.TestCase):
    """贡献者激励系统。"""

    def setUp(self):
        from eco import contributors as cb
        self.cb = cb

    def test_register_and_add_event(self):
        self.cb.seed_if_empty(force=True)
        rec = self.cb.add_event("test-user-1", "rule_proposed",
                                 rule_id="MCP07", rule_name="test rule")
        self.assertEqual(rec["score"], 2)
        self.assertEqual(rec["events"][-1]["type"], "rule_proposed")
        self.assertEqual(rec["tier_info"]["tier"], "Contributor")

    def test_mature_rule_increments_counter(self):
        self.cb.seed_if_empty(force=True)
        rec = self.cb.add_event("test-user-2", "rule_matured", rule_id="MCP08",
                                 rule_name="X")
        self.assertEqual(rec["score"], 15)
        self.assertEqual(rec["rules_matured"], 1)

    def test_invalid_event_type_rejected(self):
        with self.assertRaises(ValueError):
            self.cb.add_event("test-user-3", "bogus_event", description="x")

    def test_missing_contributor_id_rejected(self):
        with self.assertRaises(ValueError):
            self.cb.register_contributor("", name="X")

    def test_tier_progression(self):
        """模拟累计贡献跨越等级门槛。"""
        from eco import contributors as cb
        # 直接调 tier_for 判定函数
        self.assertEqual(cb._tier_for(0, 1)["tier"], "Contributor")
        self.assertEqual(cb._tier_for(30, 3)["tier"], "Reviewer")
        self.assertEqual(cb._tier_for(80, 10)["tier"], "Maintainer")
        self.assertEqual(cb._tier_for(200, 25)["tier"], "Trustee")
        # 分数达标但规则数不够 → 保持低等级
        self.assertEqual(cb._tier_for(30, 1)["tier"], "Contributor")

    def test_leaderboard_sorted(self):
        self.cb.seed_if_empty(force=True)
        # 加一些贡献
        for i in range(5):
            self.cb.add_event(f"lb-user-{i}", "rule_matured", rule_id=f"R{i}")
        lb = self.cb.leaderboard(limit=10)
        for i in range(1, len(lb)):
            self.assertGreaterEqual(lb[i - 1]["score"], lb[i]["score"])

    def test_tier_summary_counts(self):
        self.cb.seed_if_empty(force=True)
        summary = self.cb.tier_summary()
        self.assertIn("Contributor", summary)
        self.assertIn("Reviewer", summary)
        self.assertIn("Maintainer", summary)
        self.assertIn("Trustee", summary)
        self.assertGreaterEqual(sum(summary.values()), 1)


class EcosystemApiR2Test(unittest.TestCase):
    """R2 API 端点覆盖（Leaderboard + Contributors）。"""

    def test_leaderboard_top_via_api(self):
        import ecosystem_api
        r, sc = ecosystem_api.handle_get("/api/v1/leaderboard/top", "limit=5")
        self.assertEqual(sc, 200)
        self.assertIn("top", r)
        self.assertLessEqual(len(r["top"]), 5)

    def test_leaderboard_domain_via_api(self):
        import ecosystem_api
        r, sc = ecosystem_api.handle_get("/api/v1/leaderboard/domains/engineering", "")
        self.assertEqual(sc, 200)
        self.assertEqual(r["domain"], "engineering")
        self.assertIn("top", r)

    def test_leaderboard_domain_invalid_via_api(self):
        import ecosystem_api
        r, sc = ecosystem_api.handle_get("/api/v1/leaderboard/domains/bogus", "")
        self.assertEqual(sc, 400)

    def test_leaderboard_snapshot_via_api(self):
        import ecosystem_api
        r, sc = ecosystem_api.handle_get("/api/v1/leaderboard/snapshot", "")
        self.assertEqual(sc, 200)
        self.assertEqual(r["schema"],
                         "https://aishield.tools/schema/trust-leaderboard/v1")

    def test_contributor_register_via_api(self):
        import ecosystem_api
        data = {"contributor_id": "api-user-1", "name": "API User",
                "github": "api-user-1", "bio": "created via API test"}
        r, sc = ecosystem_api.handle_post("/api/v1/contributors", data)
        self.assertEqual(sc, 201)
        self.assertEqual(r["contributor_id"], "api-user-1")

    def test_contributor_event_via_api(self):
        import ecosystem_api
        # 先注册
        ecosystem_api.handle_post("/api/v1/contributors",
                                   {"contributor_id": "api-user-2", "name": "U2"})
        r, sc = ecosystem_api.handle_post(
            "/api/v1/contributors/api-user-2/events",
            {"type": "rule_matured", "rule_id": "MCP99", "rule_name": "x"})
        self.assertEqual(sc, 201)
        self.assertEqual(r["score"], 15)

    def test_contributor_invalid_event_via_api(self):
        import ecosystem_api
        ecosystem_api.handle_post("/api/v1/contributors",
                                   {"contributor_id": "api-user-3"})
        r, sc = ecosystem_api.handle_post(
            "/api/v1/contributors/api-user-3/events",
            {"type": "bogus"})
        self.assertEqual(sc, 400)

    def test_contributor_missing_id_via_api(self):
        import ecosystem_api
        r, sc = ecosystem_api.handle_post("/api/v1/contributors", {})
        self.assertEqual(sc, 400)


class SandboxBackendTest(unittest.TestCase):
    """R3: 沙箱后端抽象层"""

    def test_capabilities_matrix_has_all_backends(self):
        from eco import sandbox_backend as sb
        matrix = sb.capabilities_matrix()
        names = {r["name"] for r in matrix}
        self.assertGreaterEqual(len(matrix), 5)
        self.assertIn("openshell", names)
        self.assertIn("mcpguard", names)
        self.assertIn("python-subprocess", names)

    def test_python_subprocess_always_available(self):
        from eco import sandbox_backend as sb
        dets = sb.detect_backends()
        self.assertTrue(dets["python-subprocess"].available)

    def test_recommend_falls_back_to_python_subprocess(self):
        from eco import sandbox_backend as sb
        rec = sb.recommend_backend(min_block_rate=99.0)  # 不可能达成
        self.assertEqual(rec, "python-subprocess")

    def test_default_recommend_is_valid_name(self):
        from eco import sandbox_backend as sb
        rec = sb.recommend_backend()
        self.assertIn(rec, sb.BACKEND_PRIORITY)

    def test_current_backend_shape(self):
        from eco import sandbox_backend as sb
        cur = sb.current_backend()
        for k in ("recommended", "system", "python_version", "backends", "recommended_info"):
            self.assertIn(k, cur)

    def test_ecosystem_api_sandbox_endpoint(self):
        import ecosystem_api
        r, sc = ecosystem_api.handle_get("/api/v1/sandbox/backend/current", "")
        self.assertEqual(sc, 200)
        self.assertIn("recommended", r)
        self.assertIn("backends", r)
        r2, sc2 = ecosystem_api.handle_get("/api/v1/sandbox/backend/matrix", "")
        self.assertEqual(sc2, 200)
        self.assertGreaterEqual(len(r2["matrix"]), 5)


class AgentCardPubkeyDidKeyTest(unittest.TestCase):
    """#441：/api/v1/agent-card/pubkey 的 signer_did 必须是自认证 did:key。

    回归：AgentCardSigner 去掉 .signer_did 实例属性后，该端点曾 500
    （'AgentCardSigner' object has no attribute 'signer_did'）—— 现由
    signer_did 属性委托 _resolve_signer_did() 修复，此用例钉死不再复发。
    """

    def test_pubkey_endpoint_returns_did_key(self):
        import ecosystem_api
        from eco import did_key
        r, sc = ecosystem_api.handle_get("/api/v1/agent-card/pubkey", "")
        self.assertEqual(sc, 200)
        self.assertTrue(did_key.is_did_key(r["signer_did"]),
                        f"signer_did 应为 did:key，实际 {r.get('signer_did')!r}")
        self.assertEqual(r["alg"], "ed25519")
        self.assertIn("public_key", r)

    def test_pubkey_helper_returns_did_key(self):
        import ecosystem_api
        from eco import did_key
        r = ecosystem_api._agent_card_pubkey()
        self.assertTrue(did_key.is_did_key(r["signer_did"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
