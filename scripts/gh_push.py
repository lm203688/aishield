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
import sys
import urllib.error
import urllib.request

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
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "aishield-ops")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(body or "{}")
        except Exception:
            return e.code, {"message": body[:300]}


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


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    message = sys.argv[1]
    paths = sys.argv[2:]
    token = _token()

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
