#!/bin/bash
# git_push_safe.sh — 带重试的 rebase+push，用于 GitHub Actions 并发写主分支场景。
#
# 用法:
#   scripts/git_push_safe.sh [attempts] [sleep_seconds] [branch]
#   默认: 5 次重试 / 每次间隔 8 秒 / main 分支
#
# 为什么存在:
#   closed-loop-spine 每日主干里多个 workflow 会先后 push 同一个 main 分支
#   （威胁情报入库、规则晋升、反馈采纳、部署回写、分发状态…）。并发下 git 报
#   "cannot lock ref refs/heads/main: is at X but expected Y"——这是正常的非快进
#   竞争，rebase 一次即可解决。但过去各处用裸 `git push || echo "push skipped"`
#   兜住失败，导致 job 永远绿灯而产物永远进不了仓库：
#     - feature-closed-loop 因此连挂 2 天（09-01 / 09-02），迭代汇报被 skip；
#     - 规则晋升产物靠人工补 13 条才入库（数据飞轮"只进不出"的同型根因）。
#   本脚本把这条保护收敛成单一事实来源，重试耗尽则真 exit 1，让 alert job 生效。
#
# 退出码:
#   0 = push 成功
#   1 = 重试耗尽仍失败（真失败，上游 job 应转 failure）
#   2 = 本地没有待 push 的提交（调用方已自行判断，此处不重复判断）
#   3 = rebase 出现内容冲突（重试无法解决，需人工处理）
#
# 注意: 行尾必须保持 LF。workflow 内嵌 heredoc 与本脚本配合时，CRLF 会让定界符
# 永不匹配（见 scripts/validate_workflows.py E9）。

set -u

ATTEMPTS="${1:-5}"
SLEEP_SECONDS="${2:-8}"
BRANCH="${3:-main}"
REMOTE="origin"

git config user.name  "aishield-bot" 2>/dev/null || true
git config user.email "bot@aishield.local" 2>/dev/null || true

for i in $(seq 1 "$ATTEMPTS"); do
  # rebase 阶段：只处理"非快进"（pull 会自行 rebase 成功）；若出现内容冲突，
  # 重试不会让冲突消失，立即中止并清理 rebase 状态，避免污染后续 run。
  if ! git pull --rebase --autostash "$REMOTE" "$BRANCH" >/tmp/gps_rebase.log 2>&1; then
    if git rebase --abort 2>/dev/null; then
      echo "::error::rebase 出现内容冲突，无法通过重试解决"
      sed -n '1,20p' /tmp/gps_rebase.log
      exit 3
    fi
  fi

  if git push "$REMOTE" "$BRANCH" >/tmp/gps_push.log 2>&1; then
    echo "git_push_safe: push ok (attempt $i/$ATTEMPTS)"
    exit 0
  fi

  echo "git_push_safe: push 失败，重试 $i/$ATTEMPTS"
  sed -n '1,6p' /tmp/gps_push.log
  # 竞争型失败需要等对方 run 结束才可能推进；随机抖动避免多个 run 同时重试。
  sleep $((SLEEP_SECONDS + RANDOM % 5))
done

echo "::error::git_push_safe: 重试 $ATTEMPTS 次仍失败，判定为真失败"
sed -n '1,10p' /tmp/gps_push.log
exit 1
