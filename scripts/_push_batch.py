import argparse
import base64, json, os, subprocess, sys, tempfile, time

REPO = "lm203688/aishield"
BRANCH = "main"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAT_FILE = os.path.join(ROOT, ".workbuddy", "schedule-revert-pat.txt")
TOKEN = open(PAT_FILE, encoding="utf-8").read().strip()

_SCRIPTS = os.path.join(ROOT, "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

# 本轮检出的规则数漂移声明位。由 _auto_declaration_files 填充，供 commit
# 循环里的"本地与远端一致但仍漂移"告警使用。
_DRIFTED = set()


def _auto_declaration_files(batch: list) -> list:
    """把规则数漂移的声明位并进本批推送（可用 --no-auto-decl 关闭）。

    为什么是机制而不是纪律：规则晋升后 ``rule_count_gate --sync`` 一次会改
    20+ 个声明位（README / agent.html / agent-card.json / smithery.yaml …），
    人工挑文件推送必然只带一部分，CI 的 "Workflow Integrity Gate" 就在剩下
    那些文件上红 —— 红的是"本地已改、远端未同步"的半推状态。2026-10-02 的
    实证是：本地 --sync 改了 20+ 文件，push 批次只带 8 个，CI 立刻报 8 处。

    漂移文件本身的 blob 循环会自己跳过"本地与远端一致"的条目，所以这里
    多带几个文件不会造出空提交。
    """
    if "--no-auto-decl" in sys.argv or os.environ.get("PUSH_NO_AUTO_DECL"):
        return []
    global _DRIFTED  # noqa: PLW0603
    try:
        import rule_count_gate as g
        _DRIFTED = set(g.drifted_files())
        drifted = _DRIFTED
    except Exception as exc:                      # noqa: BLE001
        # 拿不到门禁 ≠ 没漂移。降级放行而不是阻断：网关类故障不该挡住
        # 正常代码推送，CI 里该红的门禁仍会自己报。
        print(f"  ! 自动带漂移声明位失败（不阻断本次推送）：{exc}")
        return []
    have = set()
    for rel in batch:
        have.add(os.path.relpath(os.path.abspath(rel), ROOT).replace(os.sep, "/"))
    extras = [r for r in sorted(drifted - have)
              if os.path.isfile(os.path.join(ROOT, r))]
    for r in extras:
        print(f"  + auto drift decl: {r}")
    return extras


ap = argparse.ArgumentParser(description="多文件单提交推送（Contents API）")
ap.add_argument("message")
ap.add_argument("files", nargs="*")
ap.add_argument("--no-auto-decl", action="store_true",
                help="不自动带上规则数漂移的声明位")
ap.add_argument("--dry-run", action="store_true",
                help="算完 blob 就打印将提交的文件清单并退出，不写远端")
ARGS = ap.parse_args()

MESSAGE = ARGS.message
FILES = list(ARGS.files)
if not FILES:
    raise SystemExit("usage: _push_batch.py <msg> <file>...")
FILES += _auto_declaration_files(FILES)


def req(method, url, payload=None):
    """带明确诊断的重试。

    2026-10-05：本机沙箱会间歇性地让 curl **不写出** -o 的目标文件，原实现直接
    `open(body_path)` → 抛一个毫无信息的 FileNotFoundError（连 curl 的 returncode
    和 stderr 都丢了），看起来像脚本坏了而其实是传输抖动。现在把它变成
    "带 rc/stderr 的错误 + 重试 3 次"，失败时也说得清是什么失败。
    """
    pf = None
    if payload is not None:
        pf = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False,
                                         encoding="utf-8")
        json.dump(payload, pf)
        pf.close()

    last_err = ""
    try:
        for attempt in (1, 2, 3):
            body_path = tempfile.mktemp(suffix=".out")
            cmd = ["curl", "-sS", "--ssl-no-revoke", "--tlsv1.3", "-X", method,
                   "-H", f"Authorization: Bearer {TOKEN}",
                   "-H", "Accept: application/vnd.github+json",
                   "-H", "User-Agent: aishield-ops", "-o", body_path,
                   "-w", "%{http_code}"]
            if pf:
                cmd += ["-H", "Content-Type: application/json", "-d", f"@{pf.name}"]
            cmd.append(url)
            try:
                p = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
                if not os.path.exists(body_path):
                    raise RuntimeError(
                        f"curl 未写出响应体 rc={p.returncode} "
                        f"stderr={(p.stderr or '')[:200]!r}")
                with open(body_path, encoding="utf-8", errors="replace") as fh:
                    body = fh.read()
                status = int((p.stdout or "0").strip() or 0)
                try:
                    return status, json.loads(body or "{}")
                except Exception:
                    return status, {"message": body[:300]}
            except RuntimeError as e:
                last_err = str(e)
                if attempt < 3:
                    time.sleep(2 * attempt)
            finally:
                if os.path.exists(body_path):
                    try:
                        os.unlink(body_path)
                    except OSError:
                        pass
        raise SystemExit(
            f"push 失败：{method} {url} 连续 3 次未拿到响应体 —— {last_err}")
    finally:
        if pf and os.path.exists(pf.name):
            try:
                os.unlink(pf.name)
            except OSError:
                pass


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
        # 本地与远端一致时直接跳过是对的，但如果这个文件仍在漂移名单里，
        # 说明"没人改过它"——推送再多次也修不掉远端那个错数字。这种
        # 静默跳过最容易被误读成"已同步"，必须显式喊出来。
        if rel in _DRIFTED:
            print(f"  unchanged BUT STILL DRIFTED: {rel} "
                  f"（先跑 rule_count_gate.py --sync 再推）")
        else:
            print(f"  unchanged: {rel}")
        continue
    s, blob = req("POST", f"https://api.github.com/repos/{REPO}/git/blobs",
                  {"content": content, "encoding": "base64"})
    assert s in (200, 201), f"blob failed {rel}: {s} {blob}"
    blobs.append((rel, blob["sha"]))
    print(f"  blob: {rel}")

if ARGS.dry_run:
    print(f"[dry-run] 将提交 {len(blobs)} 个 blob（删除 {len(deletes)} 个）：")
    for rel, _sha in blobs:
        print(f"    M {rel}")
    raise SystemExit(0)

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
