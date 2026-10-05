#!/bin/bash
# git_push_safe.sh — 带重试的 rebase+push，用于 GitHub Actions 并发写主分支场景。
#
# 用法:
#   scripts/git_push_safe.sh [attempts] [sleep_seconds] [branch]
#   默认: 5 次重试 / 每次间隔 8 秒 / main 分支
#
# 为什么存在:
#   closed-loop-spine 主干里多个子工作流会先后 push 同一个 main 分支，而且:
#     - 同一 run 内：链 2/3/4 推送规则/情报会触发 ci.yml(on: push)，它的
#       "Write CI State to Bus" 与链 5(verify, via workflow_call)的同一个 job
#       并发写 data/state/ci.json；
#     - 跨 run：手动 dispatch 与每日 cron 若重叠，两个 spine 同时写 main。
#   并发下 git 会报内容冲突(CONFLICT content)或非快进。过去各处用裸
#   `git push || echo "push skipped"` 兜失败，导致 job 永远绿灯而产物进不了仓库。
#
# 本脚本把"状态总线回写"做成 single source of truth，并且:
#   * **快照类**文件（单一生产者 + 整体重写 → 最后写入者胜）并发冲突时，自动保留
#     【被重放的本地快照】(--theirs, 已本地实测确认语义)，继续 rebase，不再以
#     退出码 3 把 job 变成失败。每次 run 都会重算自己的快照，因此丢掉对方那一份
#     是安全的(下一轮即覆盖)。
#   * 其余文件（源码/手写规则/种子数据等）若冲突，说明两处都在改真实逻辑，不能
#     静默覆盖 —— 中止 rebase 并退出码 3，交由人工处理 + alert job 生效。
#
# 【2026-10-05 修正】哪一类是"快照类"不再由**路径前缀**决定（原为 `data/state/`）：
#   前缀只是"这类文件长什么样"的代理。一次合法重叠就让 data/generated_rules.json
#   的 content 冲突被判成"真实逻辑冲突"→ exit 3 → 当天闭环在 job 4 终止、其后
#   8 个 job 全 skipped。现改为读 .github/auto-resolvable-paths.txt（声明），
#   而声明的可信性由 scripts/validate_workflows.py 的 E13 **实测**把关：
#   写入者必须存在且唯一（唯一生产者 = last-writer-wins 成立的前提）。
#   声明文件不存在时退回内置前缀 data/state/*，与本修正之前的行为一致。
#
# 退出码:
#   0 = push 成功
#   1 = 重试耗尽仍失败(真失败，上游 job 应转 failure)
#   2 = 本地没有待 push 的提交(调用方已自行判断)
#   3 = 非状态文件出现内容冲突，需人工处理
#
# 注意: 行尾必须保持 LF。workflow 内嵌 heredoc 与本脚本配合时，CRLF 会让定界符
# 永不匹配(见 scripts/validate_workflows.py E9)。

set -u

ATTEMPTS="${1:-5}"
SLEEP_SECONDS="${2:-8}"
BRANCH="${3:-main}"
REMOTE="origin"

# 无交互 rebase 时，--continue 不应拉起编辑器(否则 CI 卡死)。
export GIT_EDITOR=true
export GIT_SEQUENCE_EDITOR=true

git config user.name  "aishield-bot" 2>/dev/null || true
git config user.email "bot@aishield.local" 2>/dev/null || true

# 快照类路径声明（见文件头）。可用环境变量覆盖，便于测试注入。
AUTO_PATHS_FILE="${AISHIELD_AUTO_PATHS_FILE:-.github/auto-resolvable-paths.txt}"

# 声明只在开始时解析**一次**，且全程用 bash 内建做字符串处理。
# 为什么较真：初版写成「每个冲突文件 × 每一行都 $(printf | tr -d) 去空白」，
# 每行都 spawn 一个子进程 —— 本机实测把一次冲突推送从 ~12s 拖到 58s
# （30 行 × 子进程创建 ≈ 45s 纯开销）。声明文件会长大，这个开销只会更差。
AUTO_PATTERNS=()
_load_auto_patterns() {
  local line pat
  [ -f "$AUTO_PATHS_FILE" ] || return 0
  while IFS= read -r line || [ -n "$line" ]; do
    pat="${line%%#*}"          # 去行内注释（纯 bash，无子进程）
    pat="${pat//[[:space:]]/}"  # 去所有空白（纯 bash 参数展开，无子进程）
    [ -n "$pat" ] && AUTO_PATTERNS+=("$pat")
  done < "$AUTO_PATHS_FILE"
}

# is_snapshot <path> —— 该文件是否属于"单一生产者快照"的一类。
# 退出 0 = 是（冲突可自动解决）；1 = 否（真冲突，交人工）。
is_snapshot() {
  local f="$1" pat
  if [ "${#AUTO_PATTERNS[@]}" -gt 0 ]; then
    for pat in "${AUTO_PATTERNS[@]}"; do
      # RHS 不加引号 = bash 内建 glob 匹配（无需把 glob 转成正则）
      # shellcheck disable=SC2254
      case "$f" in $pat) return 0 ;; esac
    done
    return 1
  fi
  # 声明缺失（老 checkout / 复用本脚本的其他仓库）→ 退回旧行为
  case "$f" in data/state/*) return 0 ;; esac
  return 1
}

_load_auto_patterns

for i in $(seq 1 "$ATTEMPTS"); do
  # rebase 阶段：把本 run 的提交重放到最新 origin/$BRANCH 之上。
  if ! git pull --rebase --autostash "$REMOTE" "$BRANCH" >/tmp/gps_rebase.log 2>&1; then
    # pull 失败 —— 大概率是 rebase 内容冲突。先列出未合并(冲突)文件。
    conflicted=$(git diff --name-only --diff-filter=U 2>/dev/null || true)
    if [ -n "$conflicted" ]; then
      # 按 is_snapshot 分区（路径无空格，故用空格分隔便于单行输出告警）。
      state_files=""
      other_files=""
      while IFS= read -r f; do
        [ -n "$f" ] || continue
        if is_snapshot "$f"; then state_files="$state_files $f"
        else other_files="$other_files $f"; fi
      done <<< "$conflicted"

      # 真冲突：不能静默覆盖，中止并交人工。
      if [ -n "$other_files" ]; then
        git rebase --abort 2>/dev/null
        echo "::error::非快照文件冲突，需人工处理:$other_files"
        sed -n '1,20p' /tmp/gps_rebase.log
        exit 3
      fi

      # 仅快照文件冲突：保留【被重放的本地快照】(--theirs, 已实测)后继续 rebase。
      for f in $state_files; do
        git checkout --theirs -- "$f"
        git add "$f"
      done
      if git rebase --continue >/tmp/gps_rebase.log 2>&1; then
        echo "git_push_safe: 快照文件冲突已自动解决 (尝试 $i/$ATTEMPTS):$state_files"
      else
        # 极端情况：rebase 后又有新冲突 → 中止重试。
        git rebase --abort 2>/dev/null
        echo "::warning::rebase 自动解决后仍失败，重试 $i/$ATTEMPTS"
        sed -n '1,10p' /tmp/gps_rebase.log
        sleep $((SLEEP_SECONDS + RANDOM % 5))
        continue
      fi
    else
      # pull 失败但无冲突(网络/其他非快进) → 中止重试。
      git rebase --abort 2>/dev/null
      echo "::warning::pull 失败(无冲突)，重试 $i/$ATTEMPTS"
      sed -n '1,10p' /tmp/gps_rebase.log
      sleep $((SLEEP_SECONDS + RANDOM % 5))
      continue
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
