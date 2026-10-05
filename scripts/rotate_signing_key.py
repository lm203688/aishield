#!/usr/bin/env python
"""scripts/rotate_signing_key.py — 生产签名密钥迁移 / 轮换运维脚本（#369）

═══════════════════════════════════════════════════════════════════
  为什么必须有这个脚本：L1/L3 在生产是「死能力」，而本地测试全绿
═══════════════════════════════════════════════════════════════════
  2026-10-05 线上核线发现：``/.well-known/jwks.json`` 与
  ``/api/v1/identity/jwks`` 都返回 ``keys=[] ready=false``。原因不是端点挂了，
  而是生产 ``api/data/agent_card_key.json`` 里的 alg 是 **hmac-sha256（对称）**，
  private_key 与 public_key 是同一个值。

  于是线上状态是：

    * JWKS 发不出任何公钥 —— 「别家能不能验我」这一层在生产等于不存在；
    * 凭证签发直接 503（``issue_credential`` 对非 Ed25519 拒绝签，宁可不发也
      不发一枚只能自证的凭证 —— 这个设计是对的，但它让死能力保持沉默）；
    * 意图授权（L3）同样签不出可验证的 mandate。

  而 ``tests/`` 里 1865 个用例、契约 148 条路由全是绿的 —— 因为它们验证的是
  **代码**，不是**生产**。这就是继「handler 写了但入口没接」之后的第二层假绿：
  代码完成 ≠ 能力可用。

  所以这个脚本的定位不是「再包一层 rotate()」，而是把迁移做成一条**可验证的
  生产动作**：先备、再迁、迁完立刻自检、任何一环不过就**自动回滚**。

═══════════════════════════════════════════════════════════════════
  用法
═══════════════════════════════════════════════════════════════════
    python scripts/rotate_signing_key.py                # 只看状态 + dry-run 计划（默认，不写盘）
    python scripts/rotate_signing_key.py --yes          # 真迁移到 Ed25519（旧密钥进 deprecated）
    python scripts/rotate_signing_key.py --yes --force  # 强制轮换（已是 Ed25519 时也换，定期轮换用）
    python scripts/rotate_signing_key.py --key-file X   # 指定密钥环（默认 api/data/signing_keys.json）

  退出码：0 成功 / 1 参数或前置错误 / 2 无需迁移（幂等正常） /
  3 迁移后自检失败并已回滚 / 4 迁移过程中异常。

  铁律（与项目其余门禁一致）：退出码显式返回，**不吞异常、不用 || true**。
"""
from __future__ import annotations

import argparse
import base64
import datetime as _dt
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eco import crypto_sign as _cs                       # noqa: E402
from eco import verifiable_identity as vi                # noqa: E402

DEFAULT_KEY_FILE = vi.KEY_FILE
BACKUP_DIR_SUFFIX = "key-backups"

EXIT_OK = 0
EXIT_ARGS = 1
EXIT_NOTHING_TO_DO = 2
EXIT_ROLLBACK = 3
EXIT_CRASH = 4


# ── 工具 ─────────────────────────────────────────────────────────────
def _stamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def _backup_path(key_file: str) -> str:
    d = os.path.join(os.path.dirname(os.path.abspath(key_file)), BACKUP_DIR_SUFFIX)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"{os.path.basename(key_file)}.{_stamp()}")


def _backup(key_file: str) -> str | None:
    """把当前密钥环备份一份（不覆盖历史备份）。没有文件就返回 None。"""
    if not os.path.exists(key_file):
        return None
    dst = _backup_path(key_file)
    shutil.copy2(key_file, dst)
    return dst


def _restore(key_file: str, bak: str | None, existed_before: bool) -> str:
    """回滚。返回一句**如实**描述发生了什么的说明，绝不谎报成功。

    坑：迁移前文件不存在时没有备份可回滚 —— 但此时脚本已经把新文件写出来了，
    只打印「无备份」却把半吊子文件留在盘上，等于自己制造一次假绿。所以这条
    路径必须真的把盘上状态清回「迁移前不存在」。
    """
    if bak and os.path.exists(bak):
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        shutil.copy2(bak, key_file)
        return f"已回滚到备份：{bak}"
    if not existed_before and os.path.exists(key_file):
        try:
            os.remove(key_file)
            return f"已删除迁移新建的密钥环文件（恢复迁移前的不存在状态）：{key_file}"
        except Exception as e:                          # noqa: BLE001
            # 有些环境（含本地 WorkBuddy 安全删除守卫）会拦 os.remove，
            # 拦了就必须明说，不能当成已回滚。
            return f"无法删除新建文件（{type(e).__name__}: {e}），请人工删除：{key_file}"
    return "无备份且迁移前文件即已存在，请人工检查"


def _preflight() -> list[str]:
    """迁移前置检查：没有 Ed25519 后端就别动手，别留下半吊子状态。"""
    fails: list[str] = []
    if not getattr(_cs, "_HAVE_CRYPTO", False):
        fails.append(
            f"本解释器的签名后端是 {_cs.backend()}（缺 cryptography）—— 迁过去拿到的"
            "还是对称密钥，JWKS 依旧发不出公钥。这正是线上 ready=false 的成因之一，"
            "不先补后端、只跑迁移，只会得到一个「迁移显示成功、第三方依然验不过」"
            "的半吊子状态。先在**跑服务的那个解释器**里执行 pip install cryptography，"
            "再回来跑本脚本。"
        )
    return fails


def _print_status(ring, key_file: str) -> None:
    a = ring.active()
    print("─ 当前状态 ───────────────────────────────")
    # 后端必须印在最前面：历史上「迁移/轮换都成功了，JWKS 还是 ready=false」的真正
    # 原因是这台机器没装 cryptography，crypto_sign 默默退回 hmac-sha256。不把后端
    # 打出来，排查的人只会看到「没跑迁移」这个错误结论。
    print(f"  签名后端     : {_cs.backend()}")
    print(f"  cryptography : {bool(getattr(_cs, '_HAVE_CRYPTO', False))}")
    print(f"  密钥环文件   : {key_file}")
    print(f"  legacy 源    : {ring.data.get('_legacy_source') or '(无)'}")
    print(f"  active.alg   : {(a or {}).get('alg') or '(无密钥)'}")
    print(f"  active.kid   : {vi._kid(str((a or {}).get('public_key') or '')) or '(无)'}")
    print(f"  Ed25519 ready: {ring.is_ed25519_ready()}")
    print(f"  deprecated   : {len(ring.deprecated())} 把（仅验旧签，不进 JWKS）")
    print(f"  除销凭证     : {len(ring.data.get('revoked_credentials') or [])} 枚")
    jw = ring.jwks()
    print(f"  JWKS 可发布  : {jw.get('ready')}   keys={len(jw.get('keys') or [])}")
    if not jw.get("ready"):
        # 诊断文案必须在打印里也可见 —— 否则运维只看到 ready=false 还得去翻代码
        print(f"  诊断         : {(jw.get('reason') or '(无诊断)')[:160]}")
    print()


# ── 迁移后自检：过不了就回滚 ──────────────────────────────────────────
def _selfcheck(ring) -> list[str]:
    """迁移后必须全过的四道检查。返回失败清单（空 = 全过）。"""
    fails: list[str] = []

    active = ring.active()
    if not active:
        return ["密钥环里没有 active 密钥"]

    # 1) JWKS 可发布，且恰好一模公钥
    try:
        jw = ring.jwks()
    except Exception as e:                       # noqa: BLE001 —— 红线守卫会抛，必须转成失败项
        return [f"jwks() 抛异常：{e}"]
    keys = jw.get("keys") or []
    if not jw.get("ready"):
        fails.append(f"JWKS 仍不可发布：{jw.get('reason') or '(无诊断)'}")
    if len(keys) != 1:
        fails.append(f"JWKS 公钥数量应为 1，实际 {len(keys)}")
    x = (keys[0].get("x") if keys else "") or ""
    if not x:
        fails.append("JWKS 公钥 x 为空")

    # 2) 红线：JWKS 里绝不能出现私钥（对称迁移时 public==private，最容易漏）
    priv = str(active.get("private_key") or "")
    if priv:
        blob = json.dumps(jw, ensure_ascii=False)
        if priv in blob:
            fails.append("红线：JWKS 输出里含私钥原文")
    # kty/alg/crv 必须是对的（第三方拿错 crv 验不出来）
    if keys:
        for k in ("kty", "crv", "alg"):
            if not keys[0].get(k):
                fails.append(f"JWKS 公钥缺字段 {k}")

    # 3) 真签一枚、只凭 JWKS 的 x 离线验通 —— 这是「别家能不能验我」的物理证明
    try:
        cred = ring.issue_credential("urn:rotate:selfcheck", ttl=60)
        token = str(cred.get("token") or "")
        if not x:
            fails.append("无法离线验签：JWKS 没有可用的 x")
        else:
            head, sep, sig = token.partition(".")
            if not (sep and head and sig):
                fails.append("自测凭证 token 结构非法")
            else:
                payload = vi._b64u_dec(head)
                sig_raw = vi._b64u_dec(sig)
                ok = _cs.verify(payload, base64.b64encode(sig_raw).decode("ascii"),
                                x, _cs.ALG_ED25519)
                if not ok:
                    fails.append("离线验签失败：凭 JWKS 公钥验不出自测凭证（第三方会验不过）")
    except Exception as e:                       # noqa: BLE001
        fails.append(f"自测凭证签发失败：{e}")

    # 4) 双窗口：旧密钥必须还在 deprecated（否则历史凭证一夜之间全部验不过）
    if not ring.deprecated():
        fails.append("旧密钥未进入 deprecated（双窗口丢失，历史凭证将验不过）")
    if ring.deprecated() and not ring.is_ed25519_ready():
        fails.append("迁移后 active 仍不是 Ed25519")

    return fails


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="签名密钥迁移 / 轮换（生产安全）")
    ap.add_argument("--key-file", default=DEFAULT_KEY_FILE,
                    help=f"密钥环文件（默认 {DEFAULT_KEY_FILE}）")
    ap.add_argument("--yes", action="store_true",
                    help="确认执行（默认 dry-run，不写盘）")
    ap.add_argument("--force", action="store_true",
                    help="已是 Ed25519 也强制轮换（定期轮换用；不加则幂等跳过）")
    ap.add_argument("--no-backup", action="store_true",
                    help="跳过备份（不推荐；默认迁移前会备份一份）")
    args = ap.parse_args(argv)

    key_file = os.path.abspath(args.key_file)

    # 注意：__init__ 里不能把默认值写成常量，否则测试改了模块常量就重定向不到；
    # 这里同理 —— 显式把用户给的 --key-file 传下去，别依赖模块级常量。
    ring = vi.SigningKeyRing(path=key_file)
    ring.load()

    _print_status(ring, key_file)

    # ── 0) 前置检查：先于任何写盘动作 ──
    pre = _preflight()
    if pre:
        print("[preflight 失败]（未做任何改动）")
        for f in pre:
            print(f"   - {f}")
        return EXIT_ARGS

    already = ring.is_ed25519_ready()
    if already and not args.force:
        print("已是 Ed25519，且未给 --force —— 无需迁移（幂等，不做无谓轮换）。")
        return EXIT_NOTHING_TO_DO
    if already and args.force:
        print("已是 Ed25519，按 --force 执行定期轮换（旧 active 进 deprecated，历史凭证仍可验）。")

    if not args.yes:
        print("[dry-run] 上面是当前状态；加 --yes 才真正迁移/轮换并落盘。")
        return EXIT_OK

    # ── 1) 备份（记住迁移前文件是否存在，回滚要还原到那个状态）──
    existed_before = os.path.exists(key_file)
    bak = None
    if not args.no_backup:
        bak = _backup(key_file)
        print(f"[backup] {'备份于 ' + bak if bak else '无现有密钥文件，无需备份'}")
        if not bak:
            print("         （首次迁移：没有旧文件可备份，迁移后请自行留存新密钥）")

    # ── 2) 迁移 ──
    # 重新 load 一次，避免备份/状态打印期间文件被别处改过
    ring2 = vi.SigningKeyRing(path=key_file)
    ring2.load()
    try:
        res = ring2.rotate(force=args.force, persist=True)
    except Exception as e:                       # noqa: BLE001
        print(f"[迁移失败] 异常：{e}")
        return EXIT_CRASH
    print(f"[migrate] migrated={res.get('migrated')} kid={res.get('kid')} "
          f"alg={res.get('alg')} old_alg={res.get('old_alg')} "
          f"kept_deprecated={res.get('kept_deprecated')}")

    # ── 3) 自检，不过就回滚 ──
    ring3 = vi.SigningKeyRing(path=key_file)
    ring3.load()
    fails = _selfcheck(ring3)
    if fails:
        print("[自检失败] 以下检查未通过：")
        for f in fails:
            print(f"   - {f}")
        print(f"[rollback] {_restore(key_file, bak, existed_before)}")
        print("[rollback] 未通过自检的迁移绝不能留在生产上 —— 宁可没有 Ed25519，"
              "也不能有一个「迁移显示成功、第三方其实验不过」的半吊子状态。")
        return EXIT_ROLLBACK

    print("[selfcheck] JWKS 可发布 / 无私钥外泄 / 仅凭 x 离线验签通过 / 双窗口保留 —— 全过")
    print()
    print("迁移完成。验证生产是否真活：")
    print("  curl -s https://aishield.tools/api/v1/identity/jwks | head -c 300")
    print("  python scripts/prove_identity_chain.py")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
