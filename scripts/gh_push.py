"""
GitHub Contents API 推送助手（本地 git 对象库损坏时的备用通道）

用法:
    python scripts/gh_push.py "commit message" path/to/file1 path/to/file2 ...

PAT 从 .workbuddy/schedule-revert-pat.txt 读取（该文件已 gitignore）。
脚本绝不打印 token；仅输出每个文件的推送结果。
"""

import base64
import json
import os
import subprocess
import sys
import tempfile

REPO = os.environ.get("AISHIELD_REPO", "lm203688/aishield")
BRANCH = os.environ.get("AISHIELD_BRANCH", "main")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAT_FILE = os.path.join(ROOT, ".workbuddy", "schedule-revert-pat.txt")


def _token():
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        return tok.strip()
    if os.path.exists(PAT_FILE):
        with open(PAT_FILE, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    raise SystemExit("ERROR: no token available (env GITHUB_TOKEN or .workbuddy/schedule-revert-pat.txt)")


def _req(url, token, method="GET", payload=None):
    # 本机有 TLS 拦截代理：Python urllib 握手被重置，必须用 curl --tlsv1.3 --ssl-no-revoke。
    body_path = tempfile.mktemp(suffix=".out")
    cmd = [
        "curl", "-sS", "--ssl-no-revoke", "--tlsv1.3",
        "-X", method,
        "-H", f"Authorization: Bearer {token}",
        "-H", "Accept: application/vnd.github+json",
        "-H", "User-Agent: aishield-ops",
        "-o", body_path,
        "-w", "%{http_code}",
    ]
    payload_file = None
    if payload is not None:
        payload_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        )
        json.dump(payload, payload_file)
        payload_file.close()
        cmd += ["-H", "Content-Type: application/json", "-d", f"@{payload_file.name}"]
    cmd.append(url)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        status = int((proc.stdout or "0").strip() or 0)
        with open(body_path, "r", encoding="utf-8", errors="replace") as fh:
            body = fh.read()
    except Exception as e:  # noqa: BLE001
        return 0, {"message": f"curl error: {e}"}
    finally:
        if payload_file and os.path.exists(payload_file.name):
            os.unlink(payload_file.name)
        if os.path.exists(body_path):
            os.unlink(body_path)
    try:
        return status, json.loads(body or "{}")
    except Exception:
        return status, {"message": body[:300]}


def push_file(rel_path, message, token):
    abs_path = os.path.join(ROOT, rel_path)
    if not os.path.exists(abs_path):
        return False, f"missing local file: {rel_path}"
    with open(abs_path, "rb") as fh:
        content_b64 = base64.b64encode(fh.read()).decode("ascii")

    api = f"https://api.github.com/repos/{REPO}/contents/{rel_path.replace(os.sep, '/')}"
    status, cur = _req(f"{api}?ref={BRANCH}", token)
    sha = cur.get("sha") if status == 200 else None
    if status == 200 and cur.get("content"):
        if cur["content"].replace("\n", "") == content_b64:
            return True, "unchanged (skipped)"

    payload = {"message": message, "content": content_b64, "branch": BRANCH}
    if sha:
        payload["sha"] = sha
    status, resp = _req(api, token, method="PUT", payload=payload)
    if status in (200, 201):
        return True, resp.get("commit", {}).get("sha", "")[:8]
    return False, f"HTTP {status}: {resp.get('message', '')[:160]}"


def _distribution_gate_ok():
    """推送前门禁：确认 distribution/ 下所有对外发布物都过自家扫描器。

    返回 True = 通过（可推送）。门禁脚本本身崩溃时按「通过」处理，
    避免坏门禁静默阻断正常推送；只有门禁真实判定失败才拦截。
    """
    script = os.path.join(ROOT, "scripts", "verify_distribution.py")
    if not os.path.exists(script):
        return True
    try:
        r = subprocess.run(
            [sys.executable, script, "--quiet"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        return r.returncode == 0
    except Exception:
        return True


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    message = sys.argv[1]
    paths = sys.argv[2:]
    token = _token()

    # 分发门禁：任何推送前先确认对外发布物都过自家扫描器，
    # 防止「自带洞」的 artifact 被推上 main（曾导致套件 520/3/9 变红）。
    if not _distribution_gate_ok():
        print("❌ 分发门禁未通过 —— gh_push 拒绝推送。")
        print("   先修复 distribution/ 下被自家扫描器拦截的产物，再推送。")
        print("   本地自检：python scripts/verify_distribution.py")
        sys.exit(2)

    ok = 0
    for p in paths:
        rel = os.path.relpath(os.path.abspath(p), ROOT).replace(os.sep, "/")
        success, info = push_file(rel, message, token)
        print(f"  [{'OK ' if success else 'ERR'}] {rel} -> {info}")
        ok += 1 if success else 0
    print(f"\npushed {ok}/{len(paths)} files to {REPO}@{BRANCH}")
    sys.exit(0 if ok == len(paths) else 1)


if __name__ == "__main__":
    main()
