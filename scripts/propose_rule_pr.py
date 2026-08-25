"""
scripts/propose_rule_pr.py — 把 scanner/_proposed/ 的规则候选自动开成 draft PR

借鉴赛道一「开源吸纳 pipeline」思路：Tech Radar 自动起草的规则候选
（scanner/_proposed/PROPOSED_*.json），从这里一键变成 GitHub draft PR，
进入人类评审闭环，而不是躺在目录里无人问津。

安全：
  - 默认 --dry-run，只打印将要做什么，不开 PR。
  - 真实执行需 --execute，且只开 **draft** PR（不会自动合入）。
  - 每个候选独立分支 proposed/<id>，互不干扰。

用法：
    python scripts/propose_rule_pr.py                 # dry-run
    python scripts/propose_rule_pr.py --execute       # 真实开 draft PR
    python scripts/propose_rule_pr.py --id <file_id>  # 只处理某一个
"""
from __future__ import annotations

import base64
import glob
import json
import os
import subprocess
import sys

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "lm203688/aishield"
PROPOSED_DIR = os.path.join(_BASE, "scanner", "_proposed")
PAT_FILE = os.path.join(_BASE, ".workbuddy", "schedule-revert-pat.txt")
BRANCH = "main"


def _pat():
    p = os.path.join(_BASE, ".workbuddy", "schedule-revert-pat.txt")
    if not os.path.exists(p):
        return ""
    with open(p, "r", encoding="utf-8") as f:
        return f.read().strip()


def _api(method, url, data=None):
    cmd = ["curl", "-sS", "--ssl-no-revoke", "--tlsv1.3", "-X", method,
           "-H", f"Authorization: Bearer {_pat()}",
           "-H", "Accept: application/vnd.github+json",
           "-H", "Content-Type: application/json",
           f"https://api.github.com{url}"]
    if data is not None:
        cmd += ["-d", json.dumps(data, ensure_ascii=False)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(out.stdout or "{}")
    except Exception:
        return {"__raw__": out.stdout}


def _get_main_sha():
    r = _api("GET", f"/repos/{REPO}/git/ref/heads/{BRANCH}")
    return r.get("object", {}).get("sha")


def _create_branch(branch, sha):
    return _api("POST", f"/repos/{REPO}/git/refs",
                {"ref": f"refs/heads/{branch}", "sha": sha})


def _create_file_on_branch(branch, path, content, message):
    body = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "branch": branch,
    }
    return _api("PUT", f"/repos/{REPO}/contents/{path}", body)


def _open_pr(branch, title, body):
    return _api("POST", f"/repos/{REPO}/pulls",
                {"title": title, "head": branch, "base": BRANCH,
                 "body": body, "draft": True})


def _slug(s):
    return "".join(c if c.isalnum() else "-" for c in (s or "")).strip("-").lower()[:40]


def main():
    execute = "--execute" in sys.argv
    only_id = None
    if "--id" in sys.argv:
        only_id = sys.argv[sys.argv.index("--id") + 1]

    files = sorted(glob.glob(os.path.join(PROPOSED_DIR, "PROPOSED_*.json")))
    if only_id:
        files = [f for f in files if only_id in os.path.basename(f)]
    if not files:
        print("没有可处理的规则候选。")
        return

    sha = _get_main_sha() if execute else None
    print(f"[mode={'EXECUTE' if execute else 'DRY-RUN'}] 候选数={len(files)}")

    for fp in files:
        with open(fp, "r", encoding="utf-8") as f:
            cand = json.load(f)
        cid = cand.get("id") or os.path.basename(fp).replace("PROPOSED_", "").replace(".json", "")
        title = cand.get("title") or cand.get("name") or cid
        category = cand.get("category") or cand.get("owasp_category") or "uncategorized"
        rationale = cand.get("rationale") or cand.get("why") or ""
        source = cand.get("source_url") or cand.get("source") or ""

        branch = f"proposed/{_slug(cid) or cid[:30]}"
        md_path = f"scanner/_proposed/promoted/PROPOSED_{_slug(cid)}.md"
        md = (f"# 规则候选：{title}\n\n"
              f"- **ID**: {cid}\n- **类别**: {category}\n"
              f"- **来源**: {source}\n\n## 理由\n{rationale}\n\n"
              f"> 由 scripts/propose_rule_pr.py 自动起草为 draft PR，待人工评审。\n")

        if not execute:
            print(f"  [DRY] {branch}  → 将开 draft PR: {title}")
            continue

        # 真实执行
        b = _create_branch(branch, sha)
        if b.get("__raw__") is None and "message" in b and "exists" in str(b.get("message", "")).lower():
            print(f"  [SKIP] 分支已存在: {branch}")
            continue
        _create_file_on_branch(branch, md_path, md, f"chore(proposed): draft rule {cid}")
        pr = _open_pr(branch, f"[Rule Proposal] {title}", md)
        pr_url = pr.get("html_url") or pr.get("message")
        print(f"  [OK] PR: {pr_url}")

    print("完成。")


if __name__ == "__main__":
    main()
