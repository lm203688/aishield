#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在部署目标机上采集「磁盘侧真相」，供部署验证门做线上/磁盘比对。

用法（由 deploy-server.yml 通过 stdin 喂给远端 python3）：

    ssh -p 22 user@host "cd /opt/aishield && python3 -" < scripts/deploy_state_probe.py

为什么是独立脚本而不是内联 heredoc：
    上一版把这个脚本内联在工作流的 YAML 块标量里，用嵌套 heredoc 传给 ssh。
    但 heredoc 的结束符必须顶格，而 YAML 块标量里的每一行都必须比 `run:`
    多缩进——两者不可调和。结果结束符带缩进、heredoc 永不结束、ssh 命令畸形，
    失败信息又被 `2>/dev/null || echo '{}'` 吞掉，磁盘侧状态恒为空，
    验证门的两条核心断言被静默跳过，门禁退化成又一个橡皮图章。
    写成独立文件经 stdin 传输，缩进问题从根上消失，且脚本可在本地单测。

设计原则：
    - 只依赖标准库（远端是系统 python3，没有装任何东西）
    - 任何一项采集失败都降级为 null，但**整体必须仍是可解析的 JSON**
    - 永远 exit 0：本脚本的失败信号由采集不到值来体现，
      让验证门明确报告「拿不到磁盘状态」而不是让 ssh 步骤本身炸掉
"""

import json
import os
import subprocess
import sys


def sh(cmd, timeout=15):
    """执行命令，失败返回空串（不抛异常）。"""
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True, timeout=timeout
        )
        return (r.stdout or b"").decode("utf-8", "replace").strip()
    except Exception:
        return ""


def git_head():
    """所在仓库的短 commit。"""
    c = sh("git rev-parse --short HEAD")
    return c or None


def rules_state():
    """从磁盘上的代码算出规则数明细。"""
    try:
        sys.path.insert(0, os.getcwd())
        from scanner.rules import get_rule_count, get_rule_breakdown  # noqa

        return get_rule_count("mcp"), get_rule_breakdown()
    except Exception as exc:
        return None, {"error": "%s: %s" % (type(exc).__name__, exc)}


def deploy_meta():
    return _load_json(".deploy_meta.json")


def _load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def main():
    # 探测解释器位置，便于诊断「远端到底在用哪个 python」。
    # 用 shutil.which 而不是 `command -v`：后者是 shell 内建，在没有完整
    # shell 环境的调用路径下会静默返回空，反而制造新的假信号。
    import shutil

    py = shutil.which("python3") or shutil.which("python") or None

    disk_rules, breakdown = rules_state()

    out = {
        "disk_commit": git_head(),
        "disk_rules_count": disk_rules,
        "disk_rules_breakdown": breakdown,
        # 部署脚本写的是完整 sha，这里一并保留，让验证门可自行决定比对方式
        "disk_commit_full": sh("git rev-parse HEAD") or None,
        "deploy_meta": deploy_meta(),
        "data_files": (
            sorted(os.listdir("data")) if os.path.isdir("data") else []
        ),
        "python": py,
        "cwd": os.getcwd(),
    }
    json.dump(out, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
