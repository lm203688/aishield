import base64, json, os, subprocess, sys, tempfile

REPO = "lm203688/aishield"
BRANCH = "main"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAT_FILE = os.path.join(ROOT, ".workbuddy", "schedule-revert-pat.txt")
TOKEN = open(PAT_FILE, encoding="utf-8").read().strip()

FILES = sys.argv[2:]
MESSAGE = sys.argv[1]
if not FILES:
    raise SystemExit("usage: _push_batch.py <msg> <file>...")


def req(method, url, payload=None):
    body_path = tempfile.mktemp(suffix=".out")
    cmd = ["curl", "-sS", "--ssl-no-revoke", "--tlsv1.3", "-X", method,
           "-H", f"Authorization: Bearer {TOKEN}", "-H", "Accept: application/vnd.github+json",
           "-H", "User-Agent: aishield-ops", "-o", body_path, "-w", "%{http_code}"]
    pf = None
    if payload is not None:
        pf = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(payload, pf); pf.close()
        cmd += ["-H", "Content-Type: application/json", "-d", f"@{pf.name}"]
    cmd.append(url)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        status = int((p.stdout or "0").strip() or 0)
        body = open(body_path, encoding="utf-8", errors="replace").read()
    finally:
        if pf and os.path.exists(pf.name):
            os.unlink(pf.name)
        if os.path.exists(body_path):
            os.unlink(body_path)
    try:
        return status, json.loads(body or "{}")
    except Exception:
        return status, {"message": body[:300]}


s, who = req("GET", "https://api.github.com/user")
assert s == 200 and who.get("login") == "lm203688", f"auth failed: {who}"

s, ref = req("GET", f"https://api.github.com/repos/{REPO}/git/refs/heads/{BRANCH}")
base_sha = ref["object"]["sha"]
s, base_commit = req("GET", f"https://api.github.com/repos/{REPO}/git/commits/{base_sha}")
base_tree = base_commit["tree"]["sha"]
print(f"[base] {base_sha[:8]} tree {base_tree[:8]}")

blobs = []
deletes = []
for rel in FILES:
    # 前缀 '!' 表示删除该文件，其余视为新增/修改。
    if rel.startswith("!"):
        rel = rel[1:]
        rel = os.path.relpath(os.path.abspath(rel), ROOT).replace(os.sep, "/")
        s, cur = req("GET", f"https://api.github.com/repos/{REPO}/contents/{rel}?ref={BRANCH}")
        if s != 200:
            print(f"  skip (not on remote): {rel}")
            continue
        deletes.append(rel)
        print(f"  delete: {rel}")
        continue
    rel = os.path.relpath(os.path.abspath(rel), ROOT).replace(os.sep, "/")
    with open(os.path.join(ROOT, rel), "rb") as fh:
        content = base64.b64encode(fh.read()).decode("ascii")
    s, cur = req("GET", f"https://api.github.com/repos/{REPO}/contents/{rel}?ref={BRANCH}")
    cur_b64 = cur.get("content", "").replace("\n", "") if s == 200 else None
    if cur_b64 == content:
        print(f"  unchanged: {rel}")
        continue
    s, blob = req("POST", f"https://api.github.com/repos/{REPO}/git/blobs",
                  {"content": content, "encoding": "base64"})
    assert s in (200, 201), f"blob failed {rel}: {s} {blob}"
    blobs.append((rel, blob["sha"]))
    print(f"  blob: {rel}")

if not blobs and not deletes:
    print("Nothing changed. Aborting.")
    raise SystemExit(0)

# 有删除时不能再用 base_tree（未被列出的路径会被保留），
# 必须把整棵树展开后重建，把要删的路径排除在外。
if deletes:
    s, bt = req("GET", f"https://api.github.com/repos/{REPO}/git/trees/{base_tree}?recursive=1")
    assert s == 200, f"tree fetch failed: {s}"
    assert not bt.get("truncated"), "base tree too large for recursive listing"
    keep = [e for e in bt["tree"]
            if e["type"] == "blob" and e["path"] not in set(deletes)]
    for rel, sha in blobs:
        keep = [e for e in keep if e["path"] != rel]
        keep.append({"path": rel, "mode": "100644", "type": "blob", "sha": sha})
    s, tree = req("POST", f"https://api.github.com/repos/{REPO}/git/trees", {"tree": keep})
else:
    entries = [{"path": r, "mode": "100644", "type": "blob", "sha": h} for r, h in blobs]
    s, tree = req("POST", f"https://api.github.com/repos/{REPO}/git/trees",
                  {"base_tree": base_tree, "tree": entries})
assert s == 201, f"tree failed: {s} {tree}"
s, commit = req("POST", f"https://api.github.com/repos/{REPO}/git/commits",
                {"message": MESSAGE, "tree": tree["sha"], "parents": [base_sha]})
assert s == 201, f"commit failed: {s} {commit}"
s, upd = req("PATCH", f"https://api.github.com/repos/{REPO}/git/refs/heads/{BRANCH}",
             {"sha": commit["sha"], "force": False})
assert s in (200, 201), f"ref update failed: {s} {upd}"
print(f"\n[done] {commit['sha'][:8]} pushed {len(blobs)} file(s), deleted {len(deletes)}.")
