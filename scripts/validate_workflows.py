#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIShield Workflow 静态校验器
============================
解决问题：self-heal-closed-loop.yml 中 `escalate.needs: verify` 指向的是
step id 而非 job id，GitHub Actions 解析期直接报错，整个 workflow 48 天
从未运行，而本地无任何机制能发现——因为没人校验过这 14 个 workflow。

本校验器在 CI 与本地都能跑，专抓以下"沉默杀手"：
  E1 YAML 语法错误
  E2 needs 指向不存在的 job（当初的致命伤）
  E3 job 依赖成环
  E4 引用了不存在的本地脚本文件
  E5 定时任务缺少 workflow_dispatch（无法手动补跑）
  E6 非法顶层键（run 块续行落到第 0 列，命令被静默截断）
  E8 表达式含 shell 变量插值 / 注释里写坏表达式（workflow 无法加载）
  E9 CRLF(\\r) 行尾（破坏 heredoc 定界符导致 bash 语法错）/ 命令替换内嵌 heredoc（脆弱写法）
  E10 并发 push 假绿吞错（`git push || echo`）/ `git add data/state/` 整目录提交
  W1 关键步骤使用 continue-on-error（测试形同虚设）
  W2 workflow 无任何触发器
  W3 cron 表达式字段数不合法

退出码：0=全部通过，1=存在错误(E)
用法：
    python scripts/validate_workflows.py
    python scripts/validate_workflows.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
WF_DIR = REPO_ROOT / ".github" / "workflows"

# ${{ ... }} 表达式提取（非贪婪，一行内可命中多个）
EXPRESSION_RE = re.compile(r"\$\{\{(.*?)\}\}")
# 表达式里的 shell 变量插值：$ 紧跟标识符。Actions 表达式不支持这个。
SHELL_VAR_IN_EXPR = re.compile(r"\$[A-Za-z_][A-Za-z0-9_.]*")

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


def _load(path: Path) -> tuple[Dict[str, Any] | None, str]:
    text = path.read_text(encoding="utf-8")
    if yaml is None:
        return None, "PyYAML 未安装，跳过深度解析"
    try:
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            return None, "顶层不是映射结构"
        return data, ""
    except Exception as e:
        return None, f"YAML 解析失败: {e}"


def _detect_cycle(deps: Dict[str, List[str]]) -> List[str]:
    """返回成环的 job 名列表（空表示无环）。"""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {k: WHITE for k in deps}
    cycle: List[str] = []

    def dfs(node: str, stack: List[str]) -> bool:
        color[node] = GRAY
        stack.append(node)
        for nxt in deps.get(node, []):
            if nxt not in color:
                continue
            if color[nxt] == GRAY:
                cycle.extend(stack[stack.index(nxt):] + [nxt])
                return True
            if color[nxt] == WHITE and dfs(nxt, stack):
                return True
        stack.pop()
        color[node] = BLACK
        return False

    for n in list(deps):
        if color[n] == WHITE and dfs(n, []):
            break
    return cycle


def check_file(path: Path) -> Dict[str, Any]:
    res: Dict[str, Any] = {"file": path.name, "errors": [], "warnings": [], "jobs": []}
    data, err = _load(path)
    if err and data is None:
        res["errors"].append(f"E1 {err}")
        return res
    if data is None:
        return res

    text = path.read_text(encoding="utf-8")

    # E9a CRLF 行尾检查（致命但本地极难发现）
    #
    # 背景：本仓库 workflow 多经 Windows 环境推送，历史上是 CRLF 行尾。CRLF 对 bash
    # 是隐形炸弹——heredoc 定界符行变成 'PYCI\r'，bash 比对永远不等，于是报
    # "unterminated here-document" 继而 "syntax error near ')'"，整个 workflow 静默失败。
    # threat-intel-feed 因此连续 3 次失败（2026-08-28~31）。读原始字节，含 \r 即报错，
    # 杜绝该类回归（涉及变量插值时 GitHub 不会在本地给出任何提示）。
    raw = path.read_bytes()
    if b"\r" in raw:
        res["errors"].append(
            "E9 文件含 CRLF(\\r) 行尾 —— 会破坏 heredoc 定界符导致 bash 语法错，须统一转为 LF"
        )

    # E9b 命令替换内嵌 heredoc（脆弱写法）：$( ... <<'EOF' ... )
    #   该写法在 CRLF / 定界符带尾随空白 / 结束符缩进时彻底崩，且极难调试。
    #   建议把脚本落盘成文件再调用，而非塞进 $( ) 里。warning 级别，不阻断推送。
    HEREDOC_IN_SUBST = re.compile(r"\$\(\s*[^)]*<<")

    def _walk_runs(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "run" and isinstance(v, str):
                    # 逐行跳过注释，避免说明性注释里的字面量（如解释某 bug 时的示例代码）误报
                    for line in v.splitlines():
                        if line.strip().startswith("#"):
                            continue
                        if HEREDOC_IN_SUBST.search(line):
                            yield v
                            break
                else:
                    yield from _walk_runs(v)
        elif isinstance(node, list):
            for i in node:
                yield from _walk_runs(i)

    for _ in _walk_runs(data.get("jobs", {})):
        res["warnings"].append(
            "E9 检测到命令替换内嵌 heredoc ($( ... <<'EOF' ...))，"
            "该写法在 CRLF/定界符带尾随空白时会致 bash 语法错，建议改为调用落盘脚本"
        )
        break

    # E10 并发 push 假绿吞错 / 整目录状态提交（2026-09-05 审计 spine 三次失败）
    #
    # 背景：closed-loop-spine 每日主干里多个 workflow 先后 push 同一个 main。
    #   (a) `git push ... || echo "push skipped"` —— job 永远绿灯，但产物永久丢失。
    #       feature-closed-loop 因此连挂 09-01 / 09-02 两天，迭代汇报被 skip；
    #       规则晋升产物靠人工补 13 条才入库（数据飞轮"只进不出"同型根因）。
    #   (b) `git add data/state/` —— 把别的 workflow 刚 push 的状态文件一并提交，
    #       rebase 时产生内容冲突（重试无法解决），必须精确到本 workflow 自己的域文件。
    # 统一要求走 scripts/git_push_safe.sh（带重试，耗尽才真 exit 1 触发 alert job）。
    PUSHSWALLOW = re.compile(
        r"git\s+push\s+.*\|\|\s*(?:echo\b|true\b|\d\s*$)"
    )
    PULL_NO_RETRY = re.compile(r"git\s+pull\s+--rebase\b[^\n]*\|\|\s*true")
    # 目录引用 = 同一行存在 `git add`，且 `data/state/` 之后紧跟空白或行尾。
    # 反例（不报）：`git add ROADMAP.md data/state/feature.json` —— 精确文件，合法。
    # 反例（不报）：`python -c "...p='data/state/published.json'..."` —— 行内无 git add，
    #              纯字符串引用。上一版正则漏了 `git add` 前缀，导致这类行被误报。
    ADD_STATE_DIR = re.compile(r"git\s+add\b[^\n]*\bdata/state/(?=\s|$)")

    def _run_lines(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "run" and isinstance(v, str):
                    for line in v.splitlines():
                        if line.strip().startswith("#"):
                            continue
                        yield line
                else:
                    yield from _run_lines(v)
        elif isinstance(node, list):
            for i in node:
                yield from _run_lines(i)

    for line in _run_lines(data.get("jobs", {})):
        s = line.strip()
        if "git_push_safe" in s:
            continue
        if PUSHSWALLOW.search(s):
            res["errors"].append(
                f"E10 `git push` 的失败被 `|| echo`/`|| true` 吞成假绿（{s[:70]}）"
                "—— 并发冲突时产物永久丢失；改用 `bash scripts/git_push_safe.sh`"
            )
        elif PULL_NO_RETRY.search(s):
            res["errors"].append(
                f"E10 `git pull --rebase ... || true` 吞掉 rebase 失败且无重试（{s[:70]}）；"
                "改用 `bash scripts/git_push_safe.sh`"
            )
        if ADD_STATE_DIR.search(s):
            res["errors"].append(
                f"E10 `git add data/state/` 提交整个状态目录（{s[:70]}）"
                "—— 会把其他 workflow 刚 push 的文件一并提交并引发 rebase 内容冲突；"
                "请只 add 本 workflow 自己拥有的 data/state/<domain>.json"
            )

    # E6 顶层键污染检查

    # 场景：run 块里的多行字符串未缩进，续行落到第 0 列后被 YAML 当成新的顶层键。
    # 这类错误语法上合法、GitHub 不报错，但 run 命令已被截断 —— 比语法错更隐蔽。
    ALLOWED_TOP = {
        "name", "on", "jobs", "permissions", "env", "defaults",
        "concurrency", "run-name", True,  # PyYAML 把 on: 解析成布尔 True
    }
    for key in data.keys():
        if key not in ALLOWED_TOP:
            res["errors"].append(
                f"E6 非法顶层键 '{key}' —— 多半是 run 块内多行字符串未缩进导致命令被截断"
            )

    # E8 表达式合法性检查（抓「workflow 无法加载」这类沉默杀手）
    #
    # 背景：GitHub Actions 的表达式在 workflow 加载时就静态求值，而且
    # **连 YAML 注释里的 ${{ }} 也照样求值**。所以任何写在注释里的坏表达式，
    # 都会让整个 workflow 无法加载——而 PyYAML 与 E1 的语法检查都完全正常，
    # 这个错只在 GitHub 侧出现，本地门禁永远发现不了。
    #
    # 三种已实测的致命写法：
    #   1) 表达式里嵌 shell 变量：needs.$job.result
    #      -> (Line 247, Col 14) Unexpected symbol: '$job'
    #   2) 注释里写下坏表达式的字面量当作文档说明
    #      -> 同一个解析错误被「注释」重新引入（已实测复现）
    #   3) 注释里打一个空的表达式标记占位（本来说明「注释也会被求值」时
    #      顺手打的例子）-> An expression was expected（已实测复现）
    #
    # 命中后的表现极具误导：run 名退化为 .github/workflows/ci.yml、
    # 零 job、秒红，看起来像「CI 全红」，实际是「CI 从来没跑过」。
    # 曾连续 17 次全因此失败，而门禁脚本本地全绿，极难发现。
    #
    # 这里只做可疑模式的静态拦截，不是完整表达式解析器——
    # 宁可多报也不放过，人工 5 秒即可确认。
    for lineno, line in enumerate(text.splitlines(), start=1):
        for expr in EXPRESSION_RE.findall(line):
            body = expr.strip()
            if not body:
                # 空表达式标记：GitHub 报 "An expression was expected"。
                # 极易在注释里踩到——写「表达式标记」来解释这个规则时，
                # 顺手打个占位空标记，就会让整个 workflow 无法加载。
                res["errors"].append(
                    f"E8 第 {lineno} 行存在空表达式标记 —— GitHub 报 "
                    f"'An expression was expected'，整个 workflow 无法加载。"
                    f"注释里要举例就用文字描述，不要打标记的字面量。"
                )
                continue
            if SHELL_VAR_IN_EXPR.search(body):
                res["errors"].append(
                    f"E8 第 {lineno} 行表达式含 shell 变量插值: ${{{{ {body} }}}}"
                    f" —— Actions 表达式不支持，整个 workflow 将无法加载"
                )

    # 触发器检查（PyYAML 会把 on: 解析成 True 键，需两边都看）
    on = data.get("on", data.get(True))
    if not on:
        res["warnings"].append("W2 未定义任何触发器，此 workflow 永不执行")

    # 记录本文件的 workflow 名与 workflow_run 引用，供跨文件检查（E7）使用
    res["name"] = data.get("name")
    res["workflow_run_refs"] = []
    if isinstance(on, dict):
        wr = on.get("workflow_run") or {}
        refs = wr.get("workflows") if isinstance(wr, dict) else None
        if isinstance(refs, str):
            refs = [refs]
        res["workflow_run_refs"] = [str(x) for x in (refs or [])]

    has_dispatch = False
    res["crons"] = []
    if isinstance(on, dict):
        has_dispatch = "workflow_dispatch" in on
        sched = on.get("schedule")
        if sched:
            if not has_dispatch:
                res["errors"].append("E5 存在 schedule 但缺少 workflow_dispatch，故障时无法手动补跑")
            if isinstance(sched, list):
                for s in sched:
                    cron = (s or {}).get("cron", "")
                    if cron:
                        res["crons"].append(str(cron))
                    if cron and len(str(cron).split()) != 5:
                        res["errors"].append(f"W3 cron 表达式字段数非 5: '{cron}'")
    elif isinstance(on, list):
        has_dispatch = "workflow_dispatch" in on

    # Job 依赖检查 —— 当初的致命伤就在这里
    jobs = data.get("jobs") or {}
    if not isinstance(jobs, dict) or not jobs:
        res["errors"].append("E1 未定义任何 job")
        return res

    job_names = set(jobs.keys())
    res["jobs"] = sorted(job_names)
    dep_map: Dict[str, List[str]] = {}

    for jname, jbody in jobs.items():
        if not isinstance(jbody, dict):
            continue
        needs = jbody.get("needs")
        deps: List[str] = []
        if isinstance(needs, str):
            deps = [needs]
        elif isinstance(needs, list):
            deps = [str(n) for n in needs]
        dep_map[jname] = deps

        for d in deps:
            if d not in job_names:
                # 判断是不是误把 step id 当 job（历史事故的确切形态）
                step_ids = set()
                for jb in jobs.values():
                    if isinstance(jb, dict):
                        for st in jb.get("steps") or []:
                            if isinstance(st, dict) and st.get("id"):
                                step_ids.add(st["id"])
                hint = "（该名称是某个 step 的 id，不是 job）" if d in step_ids else ""
                res["errors"].append(
                    f"E2 job '{jname}' 的 needs 指向不存在的 job '{d}'{hint}"
                )

        # needs.<job>.outputs 引用校验
        for m in re.finditer(r"needs\.([A-Za-z0-9_-]+)\.", json.dumps(jbody, ensure_ascii=False)):
            ref = m.group(1)
            if ref not in job_names:
                res["errors"].append(f"E2 job '{jname}' 引用了不存在的 needs.{ref}")
            elif ref not in deps:
                res["warnings"].append(
                    f"W4 job '{jname}' 引用 needs.{ref} 但未在 needs 中声明依赖"
                )

    cycle = _detect_cycle(dep_map)
    if cycle:
        res["errors"].append(f"E3 job 依赖成环: {' -> '.join(cycle)}")

    # 引用的本地脚本是否存在
    for m in re.finditer(r"python\s+(scripts/[\w./-]+\.py|tests/[\w./-]+\.py)", text):
        rel = m.group(1)
        if not (REPO_ROOT / rel).exists():
            res["errors"].append(f"E4 引用了不存在的脚本: {rel}")
    for m in re.finditer(r"bash\s+(scripts/[\w./-]+\.sh)", text):
        rel = m.group(1)
        if not (REPO_ROOT / rel).exists():
            res["warnings"].append(f"W5 引用了本仓库不存在的 shell 脚本: {rel}（可能在服务器侧）")

    # 测试步骤被 continue-on-error 架空
    for jname, jbody in jobs.items():
        if not isinstance(jbody, dict):
            continue
        for st in jbody.get("steps") or []:
            if not isinstance(st, dict):
                continue
            name = (st.get("name") or "").lower()
            run = st.get("run") or ""
            # 只认"真的在跑测试套件"的步骤。诊断/探活步骤名里也常带 test，
            # 但它们本就该 continue-on-error（属可观测性，不是门禁），不应误报。
            TEST_CMDS = ("run_all.py", "quick_test.py", "pytest",
                         "npm test", "npm run test", "py_compile",
                         "validate_workflows.py")
            is_test = any(c in run for c in TEST_CMDS)
            if is_test and st.get("continue-on-error") is True:
                res["warnings"].append(
                    f"W1 job '{jname}' 步骤 '{st.get('name') or run[:30]}' "
                    f"跑了测试却设 continue-on-error，测试无法阻断发布"
                )
    return res


def cross_check(results: List[Dict[str, Any]]) -> None:
    """跨文件检查 E7：workflow_run 引用了不存在的 workflow 名。

    GitHub 对写错的 workflow 名**不会报任何错**，该触发器只是永不生效。
    这与当初 self-heal 静默死亡 48 天是同一类故障：
    配置看起来完全正常，实际从未生效，且没有任何信号告诉你。
    """
    known = {r["name"] for r in results if r.get("name")}
    for r in results:
        for ref in r.get("workflow_run_refs", []):
            if ref not in known:
                near = [n for n in known if n and (
                    ref.lower() in n.lower() or n.lower() in ref.lower())]
                hint = f"，最接近的是 '{near[0]}'" if near else ""
                r["errors"].append(
                    f"E7 workflow_run 引用了不存在的 workflow 名 '{ref}'"
                    f" —— 该触发器永不生效{hint}"
                )

    # W4/W5 调度拥塞检查
    #
    # GitHub 官方明确说明：schedule 事件在高负载时段会被延迟，甚至直接丢弃，
    # 而「每小时的开始」正是高负载时段。整点排任务 = 主动把自己排进最可能
    # 被丢弃的时间格。多个 workflow 共用同一表达式则会进一步加剧竞争。
    slots: Dict[str, List[str]] = {}
    for r in results:
        for cron in r.get("crons", []):
            slots.setdefault(cron, []).append(r["file"])

    for cron, files in slots.items():
        parts = str(cron).split()
        if len(parts) == 5 and parts[0] == "0":
            for f in files:
                for r in results:
                    if r["file"] == f:
                        r["warnings"].append(
                            f"W4 cron '{cron}' 排在整点，GitHub 高负载时段易被延迟或丢弃"
                            f" —— 建议错开到非整点分钟"
                        )
        if len(files) > 1:
            for f in files:
                for r in results:
                    if r["file"] == f:
                        others = [x for x in files if x != f]
                        r["warnings"].append(
                            f"W5 cron '{cron}' 与 {', '.join(others)} 完全撞车，互相争抢配额"
                        )


def main() -> int:
    ap = argparse.ArgumentParser(description="AIShield Workflow 校验器")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not WF_DIR.exists():
        print("未找到 .github/workflows 目录")
        return 0

    files = sorted(list(WF_DIR.glob("*.yml")) + list(WF_DIR.glob("*.yaml")))
    results = [check_file(f) for f in files]
    cross_check(results)
    n_err = sum(len(r["errors"]) for r in results)
    n_warn = sum(len(r["warnings"]) for r in results)

    if args.json:
        print(json.dumps(
            {"total": len(files), "errors": n_err, "warnings": n_warn, "results": results},
            ensure_ascii=False, indent=2))
    else:
        print(f"校验 {len(files)} 个 workflow 文件\n" + "=" * 62)
        for r in results:
            if r["errors"] or r["warnings"]:
                icon = "❌" if r["errors"] else "⚠️ "
                print(f"\n{icon} {r['file']}  (jobs: {', '.join(r['jobs']) or '-'})")
                for e in r["errors"]:
                    print(f"     ERROR  {e}")
                for w in r["warnings"]:
                    print(f"     WARN   {w}")
            else:
                print(f"✅ {r['file']}")
        print("\n" + "=" * 62)
        print(f"结果：{n_err} 个错误，{n_warn} 个警告")
        if n_err == 0:
            print("所有 workflow 依赖链合法，可被 GitHub Actions 正常解析。")
    return 1 if n_err else 0


if __name__ == "__main__":
    raise SystemExit(main())
