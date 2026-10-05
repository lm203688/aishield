#!/usr/bin/env python
"""scripts/prove_identity_chain.py — L1/L3 线上「能力死活」核线（#369）

═══════════════════════════════════════════════════════════════════
  它证明什么：不是「代码有」，而是「别家在生产上能不能验到我」
═══════════════════════════════════════════════════════════════════
  ``run_all.py`` 的 1865 个用例全绿、契约 148 条路由全绿 —— 但线上 JWKS
  一度返回 ``keys=[] ready=false``：L1 签不出可验证凭证、L3 签不出可验证
  mandate。**测试验证代码，这条脚本验证生产。**

  两条所以在项目里都不可省：
    * 单测绕过 HTTP 入口直接调 handler（所以「handler 写了、入口没接」的死
      路由它照绿）；
    * 契约门禁把 404 当成「路由不存在」跳过（所以入口漏接它也照绿）。

  这条核线走的每一步都是**一个真实 agent 会走的路**，且验签只用拉到的 JWKS
  —— 不碰服务端任何私钥。这一步是全部意义所在：只有 JWKS 还能验通，才叫
  「可移植身份 / 意图授权」，否则只是自证清白。

═══════════════════════════════════════════════════════════════════
  链路
═══════════════════════════════════════════════════════════════════
  1. GET  /api/v1/identity/jwks                  → 取公钥（第三方唯一凭据）
  2. POST /api/v1/identity/registration-token     → 领注册凭据（绑定 owner）
  3. POST /api/v1/identity/register               → 建一个临时 DID
  4. POST /api/v1/identity/credentials/issue      → 签发身份凭证（VC）
  5. 【离线】只凭 1 的 x 验 4 的 VC                  ← 硬实力所在
  6. POST /api/v1/intent/mandates                 → 签一张意图授权
  7. POST /api/v1/intent/mandates/verify          → 服务端验
  8. 【离线】只凭 1 的 x 验 6 的 mandate              ← 同上
  9. POST /api/v1/intent/mandates/evaluate        → 合法请求放行
 10. POST /api/v1/intent/mandates/evaluate        → 同一张券重放必须拒
 11. POST /api/v1/intent/mandates/evaluate        → 超额度必须拒
 12. DELETE /api/v1/identity/agents/{did}         → 自注销，**绝不留孤儿**

═══════════════════════════════════════════════════════════════════
  用法
═══════════════════════════════════════════════════════════════════
    python scripts/prove_identity_chain.py
    python scripts/prove_identity_chain.py --base http://127.0.0.1:8450
    python scripts/prove_identity_chain.py --skip-tls-verify   # TLS 拦截代理环境

  退出码：0 全过 / 1 断言失败 / 2 L1 死能力（JWKS 不可发布，先跑 rotate）/ 3 HTTP 失败 / 4 崩溃。

  铁律：不吞异常、不用 || true、不 mock；每个失败都打印真实 status + body 片段。
  核线会写生产状态（注册一条记录），因此**必须自注销** —— 第 12 步失败也照样非零退出。
"""
from __future__ import annotations

import argparse
import base64
import datetime as _dt
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eco import crypto_sign as _cs                       # noqa: E402
from eco import verifiable_identity as _vi               # noqa: E402

DEFAULT_BASE = "https://aishield.tools"
UA = "aishield-prove-identity-chain/1.0"

EXIT_OK = 0
EXIT_ASSERT = 1
EXIT_L1_DEAD = 2
EXIT_HTTP = 3
EXIT_CRASH = 4


class ProbeHttpError(Exception):
    def __init__(self, status: int, body: str, action: str):
        super().__init__(f"{action} 返回 HTTP {status}：{body[:300]}")
        self.status = status
        self.body = body
        self.action = action


class Probe:
    def __init__(self, base: str, skip_tls: bool = False):
        self.base = base.rstrip("/")
        self.ctx = ssl.create_default_context()
        if skip_tls:
            # 只在运维本机的 TLS 拦截代理下用；默认路径保持证书全校验。
            self.ctx.check_hostname = False
            self.ctx.verify_mode = ssl.CERT_NONE

    def call(self, method: str, path: str, body: dict | None = None) -> dict:
        url = self.base + path
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(url, data=data, method=method, headers={
            "Content-Type": "application/json", "User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=30, context=self.ctx) as r:
                raw = r.read().decode("utf-8", "replace")
                try:
                    return json.loads(raw) if raw else {}
                except json.JSONDecodeError:
                    return {"_raw": raw}
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")
            raise ProbeHttpError(e.code, raw, f"{method} {path}") from None
        except urllib.error.URLError as e:
            raise ProbeHttpError(0, f"连接失败：{e.reason}", f"{method} {path}") from None


# ── 第三方验签：手里只有 JWKS，没有服务端任何私钥 ──────────────────────
def _x_for_kid(jwks_doc: dict, kid: str) -> str | None:
    for k in jwks_doc.get("keys") or []:
        if k.get("kid") == kid:
            return k.get("x") or None
    return None


def third_party_verify(jwks_doc: dict, token: str) -> tuple[bool, str]:
    """只凭 JWKS 验一枚紧凑串行 token（payload.sig）。

    返回 (ok, 说明)。这一步刻意**不 import 服务端密钥环** —— 只要 import 了
    服务端模块，验出来的就是「自己验自己」，等于没验。
    """
    head, sep, sig = token.partition(".")
    if not sep or not head or not sig:
        return False, "token 结构非法（应为 payload.sig）"
    try:
        payload = _vi._b64u_dec(head)
        sig_raw = _vi._b64u_dec(sig)
    except Exception as e:                              # noqa: BLE001
        return False, f"token 段不是合法 base64url：{e}"

    try:
        outer = json.loads(payload.decode("utf-8"))
    except Exception:                                   # noqa: BLE001
        return False, "payload 不是 JSON"

    kid = str(outer.get("kid") or "")
    x = _x_for_kid(jwks_doc, kid)
    if not x:
        return False, f"JWKS 里没有 kid={kid} 的公钥（第三方无从验证）"
    if str(outer.get("alg") or "").upper() != _cs.ALG_ED25519.upper():
        return False, f"token alg={outer.get('alg')} 不是 Ed25519"

    try:
        b64sig = base64.b64encode(sig_raw).decode("ascii")
        ok = _cs.verify(payload, b64sig, x, _cs.ALG_ED25519)
    except Exception as e:                              # noqa: BLE001
        return False, f"验签异常：{e}"
    if not ok:
        return False, "签名校验失败（凭 JWKS 验不出，等于别人验不了）"
    exp = outer.get("exp")
    if isinstance(exp, (int, float)) and exp < _dt.datetime.now().timestamp():
        return False, "token 已过期"
    return True, f"kid={kid} 验签通过（subject={outer.get('sub')}）"


# ── 断言小工具：失败直接抛，退出码 1 ───────────────────────────────────
class AssertFail(Exception):
    pass


def _need(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertFail(msg)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="L1/L3 线上能力核线")
    ap.add_argument("--base", default=DEFAULT_BASE, help=f"站点根地址（默认 {DEFAULT_BASE}）")
    ap.add_argument("--skip-tls-verify", action="store_true",
                    help="关闭证书校验（仅 TLS 拦截代理环境，默认关闭）")
    ap.add_argument("--owner", default=None,
                    help="归属标识（默认自动生成临时 ops-probe-<时间戳>）")
    args = ap.parse_args(argv)

    owner = args.owner or f"ops-probe-{_dt.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    probe = Probe(args.base, args.skip_tls_verify)

    steps: list[tuple[str, bool, str]] = []
    did: str | None = None

    def step(name: str, ok: bool, detail: str = "") -> None:
        steps.append((name, ok, detail))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}{(' — ' + detail) if detail else ''}")

    try:
        # ── 1) JWKS 必须可发布 ──
        print("─ 1. 公钥发现（JWKS）───────────────────")
        jw = probe.call("GET", "/api/v1/identity/jwks")
        keys = jw.get("keys") or []
        if not keys:
            print("  [FAIL] L1 在生产是死能力：JWKS 没有可发布公钥。")
            print(f"         诊断：{str(jw.get('reason') or '(无诊断)')[:200]}")
            print("         先执行：python scripts/rotate_signing_key.py --yes")
            return EXIT_L1_DEAD
        x0 = keys[0].get("x") or ""
        step("JWKS 可发布", True, f"keys={len(keys)} kty={keys[0].get('kty')} "
                                  f"crv={keys[0].get('crv')} alg={keys[0].get('alg')}")
        _need(bool(x0), "JWKS 公钥 x 为空")
        # 红线复核：JWKS 里绝不能含私钥
        blob = json.dumps(jw, ensure_ascii=False)
        _need("private_key" not in blob, "JWKS 里出现 private_key 字段（红线）")

        # ── 2/3) 领凭据 → 注册临时 DID ──
        print("─ 2. 身份注册（临时 DID，结束自注销）───")
        tok = probe.call("POST", "/api/v1/identity/registration-token", {"owner": owner})
        rt = str(tok.get("token") or "")
        _need(bool(rt), f"领注册凭据失败：{tok}")
        reg = probe.call("POST", "/api/v1/identity/register", {
            "name": "chain-probe", "owner": owner, "registration_token": rt})
        # 早取 did：清理逻辑靠它兜底。断言在 did 之后失败时，如果 did 还没拿到，
        # finally 就删不掉这条记录 —— 核线本身就会在生产注册表留下一堆孤儿。
        did = str(reg.get("did") or (reg.get("agent") or {}).get("did") or "")
        _need(bool(did), f"注册失败：{reg}")
        step("注册临时 DID", True, did)

        # ── 4) 签发 VC ──
        print("─ 3. 可验证凭证（VC）───────────────────")
        it = str(reg.get("identity_token")
                 or (reg.get("agent") or {}).get("identity_token") or "")
        _need(bool(it), "register 未返回 identity_token（签发链路断在第 3 环）")
        cred = probe.call("POST", "/api/v1/identity/credentials/issue",
                          {"did": did, "owner": owner, "identity_token": it})
        ct = str(cred.get("token") or "")
        _need(bool(ct), f"签发凭证失败：{cred}")
        step("签发身份凭证", True, f"credential_id={cred.get('credential_id')} kid={cred.get('kid')}")

        # ── 5) 离线第三方验 VC ──
        print("─ 4. 离线第三方验 VC（只用 JWKS）───────")
        ok, why = third_party_verify(jw, ct)
        step("第三方凭 JWKS 验 VC", ok, why)

        # ── 6) 签 mandate ──
        print("─ 5. 意图授权（Intent Mandate / AP2）───")
        constraints = {"allowed_actions": ["transfer"],
                       "allowed_resources": ["account:probe"],
                       "max_amount": 100, "currency": "USD"}
        man = probe.call("POST", "/api/v1/intent/mandates", {
            "agent_did": did, "owner": owner, "action": "transfer",
            "constraints": constraints, "ttl": 600})
        mt = str(man.get("token") or "")
        _need(bool(mt), f"签 mandate 失败：{man}")
        step("签发意图券", True, f"mandate_id={man.get('mandate_id')}")

        # ── 7) 服务端验 ──
        vr = probe.call("POST", "/api/v1/intent/mandates/verify", {"token": mt})
        step("服务端验 mandate", bool(vr.get("valid")), str(vr.get("code") or ""))

        # ── 8) 离线第三方验 mandate ──
        ok, why = third_party_verify(jw, mt)
        step("第三方凭 JWKS 验 mandate", ok, why)

        # ── 9) 合法请求放行 ──
        print("─ 6. 五道闸门求值 ──────────────────────")
        good = {"action": "transfer", "amount": 10, "currency": "USD",
                "resource": "account:probe"}
        ev = probe.call("POST", "/api/v1/intent/mandates/evaluate", {"token": mt, "request": good})
        step("合法请求放行", bool(ev.get("valid")), str(ev.get("code") or ev.get("reason") or ""))

        # ── 10) 重放必须拒 ──
        try:
            probe.call("POST", "/api/v1/intent/mandates/evaluate", {"token": mt, "request": good})
            step("重放必须拒", False, "同一张券第二次 evaluate 竟然放行了")
        except ProbeHttpError as e:
            _need(e.status == 403, f"重放应 403，实际 {e.status}：{e}")
            _need("code" in e.body.lower() or "replay" in e.body.lower()
                  or "replayed" in e.body.lower(),
                  f"重放拒绝对象不是 replay：{e.body[:200]}")
            step("重放必须拒", True, f"HTTP {e.status} code=replayed")

        # ── 11) 超额度必须拒 ──
        man2 = probe.call("POST", "/api/v1/intent/mandates", {
            "agent_did": did, "owner": owner, "action": "transfer",
            "constraints": {"max_amount": 1, "currency": "USD"}, "ttl": 600})
        mt2 = str(man2.get("token") or "")
        _need(bool(mt2), f"第二张券签发失败：{man2}")
        try:
            probe.call("POST", "/api/v1/intent/mandates/evaluate",
                       {"token": mt2,
                        "request": {"action": "transfer", "amount": 999,
                                    "currency": "USD"}})
            step("超额度必须拒", False, "amount=999 > max_amount=1 竟然放行了")
        except ProbeHttpError as e:
            _need(e.status == 403, f"超限应 403，实际 {e.status}：{e}")
            step("超额度必须拒", True, f"HTTP {e.status}")

        step("全部闸门通过", all(s[1] for s in steps))

    except ProbeHttpError as e:
        print(f"  [FAIL] {e}")
        return EXIT_HTTP
    except AssertFail as e:
        print(f"  [FAIL] 断言失败：{e}")
        return EXIT_ASSERT
    except Exception as e:                              # noqa: BLE001
        print(f"  [FAIL] 崩溃：{type(e).__name__}: {e}")
        return EXIT_CRASH
    finally:
        # ── 12) 自注销，绝不留孤儿 ──
        if did:
            print("─ 7. 自注销（不留孤儿）───────────────")
            try:
                probe.call("DELETE", f"/api/v1/identity/agents/{did}?owner={owner}")
                step("自注销", True, did)
            except ProbeHttpError as e:
                print(f"  [FAIL] 自注销失败：{e} —— 生产注册表残留一条孤儿记录 "
                      f"（name=chain-probe, owner={owner}），请人工清理")
            except Exception as e:                       # noqa: BLE001
                print(f"  [FAIL] 自注销异常：{type(e).__name__}: {e}")

    total = len(steps)
    passed = sum(1 for s in steps if s[1])
    print()
    print(f"核线结果：{passed}/{total} 通过")
    if passed != total:
        print("未全过（上方 FAIL 项即为缺口）")
        return EXIT_ASSERT
    print("L1 可移植身份 + L3 意图授权：线上真闭环（第三方仅凭 JWKS 即可验）。")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
