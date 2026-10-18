#!/usr/bin/env python3
"""benchmarks/baselines/runner.py — 公开基线对比的基线执行器（SCI 方案 P2 任务 2.2）

设计纪律（报告 §2.2 / §2.4 明确要求）
--------------------------------------
  1. **同一固定语料** —— 所有基线吃的是 ``benchmarks/corpus/external/`` 里的
     同一个样本集，不是各自挑软柿子。AIShield 自己也走同一条管道（见
     ``--include-self``），避免"自己给自己打分时用了一套、给别人用另一套"。
  2. **版本号 + 运行日期 + 命令** —— 每个结果文件必须带这三项留痕，否则结果
     不可复现。锁版本是刻意的：基线工具升级后分数会变，那是"换了个基线"，
     不是"我们的分数变了"，必须能区分开。
  3. **诚实** —— 基线跑不起来就记 ``status="not_run"`` + ``reason``，**绝不
     伪造数字**。一个跑不起来的基线在对比表里比一个被编造的高分更有价值：
     它诚实地标注了"这个对比条件不对等"，这正是报告 §2.4 要的东西。

为什么离线检查是硬要求
----------------------
本项目不变量是"不发起任何网络请求"。基线执行器在 ``check_availability`` 阶段
只做**本地探测**（binary 存不存在、镜像拉没拉、模块 import 不 import 得动），
不联网；真正联网的基线（如 Snyk agent-scan）被标记 ``offline=False``，由调用方
显式决定是否跳过，而不是悄悄去调。
"""

from __future__ import annotations

import datetime
import json
import os
import shutil
import subprocess
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
for _p in (_ROOT, _HERE, os.path.join(_ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

RESULTS_DIR = os.path.join(_HERE, "results")

# 归一化输出 schema（报告 §2.2 明确给定）
# {"sample_id": ..., "detected": true/false, "severity": "high"/...}
SCHEMA_VERSION = 1


# ---------------------------------------------------------------------------
# 基线适配器协议
# ---------------------------------------------------------------------------
# 每个基线声明三件事：
#   offline   —— 是否可在无网络下运行。False 的工具在离线环境必须诚实跳过。
#   check     —— 探测本环境能否跑（只看本地状态，不联网）。
#   invoke    —— 对单个样本扫描，返回归一化后的 dict。
#
# 不把这三个字段做成抽象基类，是因为报告要求的对比表是"工具+版本+命令"的
# 平面记录，过度面向对象反而让结果文件里的 provenance 更难读。
class Baseline:
    def __init__(self, name: str, version: str, offline: bool,
                 command: str, check: Callable[[], Tuple[bool, str]],
                 invoke: Callable[[Dict[str, Any]], Dict[str, Any]],
                 rule_count: Optional[int] = None,
                 source: str = "") -> None:
        self.name = name
        self.version = version
        self.offline = offline
        self.command = command
        self.check = check
        self.invoke = invoke
        self.rule_count = rule_count
        self.source = source

    def describe(self) -> Dict[str, Any]:
        """结果文件里的工具身份留痕。"""
        return {
            "name": self.name,
            "version": self.version,
            "offline": self.offline,
            "command": self.command,
            "rule_count": self.rule_count,
            "source": self.source,
        }


# ---------------------------------------------------------------------------
# AIShield 自身 —— 走同一管道，不自享双标
# ---------------------------------------------------------------------------
# 为什么不直接从 benchmark.py 抄数字：benchmark.py 的 Plane E 用的是
# serious_only 口径，但它的 detected 计数是"每样本任一 critical/high finding"。
# 对比表要的是**逐样本 0/1 结果序列**（bootstrap CI 需要它），所以要在这里
# 重扫一遍，保持与 Plane E **完全相同**的路由与阈值，只是输出粒度更细。
def _self_scan(sample: Dict[str, Any]) -> Dict[str, Any]:
    """对单个样本跑 AIShield 引擎。

    路径用样本 id 派生而非枚举下标：id 是语料内的稳定主键，下标会随采集
    排序漂移。基准要求"同一段代码跑两次必须得到同一个数"，路径漂移会让
    规则的路径敏感匹配（skills/ vs docs/）在不同运行间不一致。
    与 scripts/benchmark.py 的 Plane E 同口径（serious_only / 同路由）。
    """
    from scanner.rules import analyze
    from scanner.client_discovery import scan_client_configs

    sid = sample.get("id", "unknown")
    text = sample.get("text", "")
    plane = sample.get("scan_plane", "instruction")
    if plane == "config":
        findings = scan_client_configs(
            {"/bench/%s.json" % sid: text}).get("findings", [])
    else:
        findings = analyze(
            {"skills/%s.md" % sid: text}, "mcp").get("findings", [])
    serious = [f for f in findings
               if f.get("severity") in ("critical", "high")]
    return _normalize(sid, serious)


def _normalize(sample_id: str, serious: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not serious:
        return {"sample_id": sample_id, "detected": False, "severity": None}
    order = ("critical", "high", "medium", "low", "info")
    sev = min((f.get("severity", "info") for f in serious),
              key=lambda s: order.index(s) if s in order else 99)
    return {"sample_id": sample_id, "detected": True, "severity": sev}


def _docker_available() -> Tuple[bool, str]:
    exe = shutil.which("docker")
    if not exe:
        return False, "docker 二进制不在 PATH"
    try:
        out = subprocess.run(["docker", "info"], capture_output=True,
                             timeout=10)
        if out.returncode != 0:
            return False, "docker daemon 未运行"
    except Exception as exc:  # noqa: BLE001 - 探测期必须吞，探测失败=不可用
        return False, "docker 探测失败：%s" % type(exc).__name__
    return True, "docker 可用"


def _img_pulled(image: str) -> Tuple[bool, str]:
    try:
        out = subprocess.run(["docker", "image", "inspect", image],
                             capture_output=True, timeout=15)
        if out.returncode == 0:
            return True, "镜像已拉取：%s" % image
        return False, "镜像未拉取：%s（运行期不联网，请手工 docker pull）" % image
    except Exception as exc:  # noqa: BLE001
        return False, "镜像探测失败：%s" % type(exc).__name__


# ---------------------------------------------------------------------------
# 外部基线注册表
# ---------------------------------------------------------------------------
# 版本锁（2026-10-18 记录，运行期不联网）
#   · Invariant mcp-scan   v0.9.x  npm: @invariant-ai/mcp-scan
#   · agent-security-scanner-mcp  v0.4.x  pip: agent-security-scanner-mcp
#   · mcp-audit            v1.2.x  docker: ghcr.io/mcp-audit/mcp-audit
#   · Snyk agent-scan      v1.x    需联网 + Snyk API token
#
# 注意：这些版本号是**对比基线的锁定声明**，不是本仓库依赖。本仓库零依赖，
# 基线装不上就诚实标 not_run —— 见 check_availability。
def _reg_invariant() -> Baseline:
    def _check() -> Tuple[bool, str]:
        return _img_pulled("ghcr.io/invariant-ai/mcp-scan:v0.9")

    def _invoke(sample: Dict[str, Any]) -> Dict[str, Any]:
        # 真实实现：docker run + 解析其 JSON 输出为 detected/severity。
        # 本函数只有在 _check() 返回 True 时才会被调用。
        raise RuntimeError("基线调用未被实装：%s（镜像在位但适配器未完成）"
                           % sample.get("id"))

    return Baseline(
        name="Invariant mcp-scan", version="v0.9", offline=True,
        command="docker run --rm -v $PWD:/in /in/samples mcp-scan --json",
        check=_check, invoke=_invoke, rule_count=150,
        source="https://github.com/invariant-ai/mcp-scan")


def _reg_agent_security_scanner() -> Baseline:
    def _check() -> Tuple[bool, str]:
        import importlib.util
        spec = importlib.util.find_spec("agent_security_scanner")
        if spec is None:
            return False, "模块未安装：pip install agent-security-scanner-mcp"
        return True, "模块已安装"

    def _invoke(sample: Dict[str, Any]) -> Dict[str, Any]:
        raise RuntimeError("基线调用未被实装：%s" % sample.get("id"))

    return Baseline(
        name="agent-security-scanner-mcp", version="v0.4", offline=True,
        command="agent-security-scanner scan --output json <sample>",
        check=_check, invoke=_invoke, rule_count=120,
        source="https://github.com/agent-security-scanner/mcp")


def _reg_mcp_audit() -> Baseline:
    def _check() -> Tuple[bool, str]:
        return _img_pulled("ghcr.io/mcp-audit/mcp-audit:v1.2")

    def _invoke(sample: Dict[str, Any]) -> Dict[str, Any]:
        raise RuntimeError("基线调用未被实装：%s" % sample.get("id"))

    return Baseline(
        name="mcp-audit", version="v1.2", offline=True,
        command="docker run --rm -i mcp-audit < sample.json",
        check=_check, invoke=_invoke, rule_count=98,
        source="https://github.com/mcp-audit/mcp-audit")


def _reg_snyk_agent_scan() -> Baseline:
    def _check() -> Tuple[bool, str]:
        exe = shutil.which("snyk")
        if not exe:
            return False, "snyk CLI 未安装"
        tok = os.environ.get("SNYK_TOKEN")
        if not tok:
            return False, "缺 SNYK_TOKEN（该基线必须联网调用 Snyk 云）"
        return True, "CLI 与 token 齐备（仍需联网）"

    def _invoke(sample: Dict[str, Any]) -> Dict[str, Any]:
        raise RuntimeError("基线调用未被实装：%s" % sample.get("id"))

    return Baseline(
        name="Snyk agent-scan", version="v1.x", offline=False,
        command="snyk agent-scan --json <sample>",
        check=_check, invoke=_invoke, rule_count=None,
        source="https://docs.snyk.io/agent-scan")


def registry() -> List[Baseline]:
    """全部已登记基线。顺序稳定，保证对比表行序可复现。"""
    return [_reg_invariant(), _reg_agent_security_scanner(),
            _reg_mcp_audit(), _reg_snyk_agent_scan()]


SELF = Baseline(
    name="AIShield", version="self", offline=True,
    command="python scripts/benchmark.py --corpus external",
    check=lambda: (True, "仓库内引擎，恒可用"),
    invoke=_self_scan,
    source="本项目（scripts/benchmark.py Plane E 同口径）")


# ---------------------------------------------------------------------------
# 执行与落盘
# ---------------------------------------------------------------------------
def check_availability(baselines: List[Baseline]) -> List[Dict[str, Any]]:
    """逐个探测基线可用性，返回可落盘的留痕列表。不联网。"""
    out = []
    for b in baselines:
        try:
            ok, reason = b.check()
        except Exception as exc:  # noqa: BLE001 - 探测期异常=不可用，不能崩
            ok, reason = False, "探测异常：%s" % type(exc).__name__
        rec = b.describe()
        rec["available"] = bool(ok)
        rec["reason"] = reason
        out.append(rec)
    return out


def run_baseline(b: Baseline, corpus: Dict[str, Any],
                 include_negative: bool = True) -> Dict[str, Any]:
    """跑单个基线，产出归一化结果。

    失败语义分层（不吞失败）：
      · 工具不可用          -> status="not_run"，results 为空
      · 调用异常            -> status="failed"，reason 记首个异常
      · 成功                -> status="ok"，results 为逐样本 dict
    """
    ok, reason = b.check()
    header = {
        "schema_version": SCHEMA_VERSION,
        "baseline": b.describe(),
        "run_at": datetime.datetime.now(datetime.timezone.utc)
                  .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "corpus": "benchmarks/corpus/external/",
    }
    if not ok:
        header.update({"status": "not_run", "reason": reason, "results": {}})
        return header

    results: Dict[str, Dict[str, Any]] = {}
    try:
        for i, s in enumerate(corpus.get("positives", ())):
            results[s.get("id", "pos-%d" % i)] = b.invoke(s)
        if include_negative:
            for i, s in enumerate(corpus.get("negatives", ())):
                sid = s.get("id", "neg-%d" % i)
                # 负样本也归一化为"是否被报为 serious"——误报即 detected=True
                results[sid] = b.invoke(s)
        header.update({"status": "ok", "results": results,
                       "n_positives": len(corpus.get("positives", ())),
                       "n_negatives": len(corpus.get("negatives", ()))})
    except Exception as exc:  # noqa: BLE001 - 记录首个异常，不静默
        header.update({"status": "failed",
                       "reason": "%s: %s" % (type(exc).__name__, exc),
                       "partial_results": results})
    return header


def save_result(b: Baseline, payload: Dict[str, Any]) -> str:
    """落盘到 benchmarks/baselines/results/<safe_name>.json。"""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    safe = (b.name.replace("/", "_").replace(" ", "_")
                .replace(".", "_").lower())
    path = os.path.join(RESULTS_DIR, "%s.json" % safe)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    return path


def load_result(name: str) -> Optional[Dict[str, Any]]:
    """按工具名读回结果文件；不存在返回 None（调用方决定是否报错）。"""
    safe = (name.replace("/", "_").replace(" ", "_")
                .replace(".", "_").lower())
    path = os.path.join(RESULTS_DIR, "%s.json" % safe)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        prog="baselines-runner",
        description="探测基线可用性 / 执行基线（SCI 方案 P2 任务 2.2）")
    ap.add_argument("--check", action="store_true",
                    help="只探测可用性，不执行")
    ap.add_argument("--include-self", action="store_true",
                    help="同时把 AIShield 自身跑一遍（同一管道，不自享双标）")
    ap.add_argument("--json", action="store_true", help="输出 JSON 而非表格")
    ap.add_argument("--out", default=None, help="写入文件")
    args = ap.parse_args(argv)

    import rule_corpus
    corpus = rule_corpus.load_external_corpus()

    targets = registry()
    if args.include_self:
        targets = [SELF] + targets

    avail = check_availability(targets)
    if args.check:
        lines = ["基线可用性探测（不联网）："]
        for a in avail:
            mark = "可用" if a["available"] else "不可用"
            lines.append("  [%s] %-28s %-8s %s"
                         % (mark, a["name"], a["version"], a["reason"]))
        text = "\n".join(lines)
        if args.json:
            text = json.dumps({"availability": avail}, ensure_ascii=False,
                              indent=2, sort_keys=True)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(text + "\n")
            print("wrote %s" % args.out)
        else:
            print(text)
        return 0

    payloads = []
    for b in targets:
        payload = run_baseline(b, corpus)
        path = save_result(b, payload)
        payloads.append(payload)
        print("%-28s -> %-8s (%s)" % (b.name, payload["status"], path))

    if args.json:
        text = json.dumps(payloads, ensure_ascii=False, indent=2, sort_keys=True)
    else:
        text = "\n".join("%s: %s" % (p["baseline"]["name"], p["status"])
                         for p in payloads)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print("wrote %s" % args.out)
    else:
        print(text)

    # 退出码语义：all ok=0；有 failed=1；全 not_run=2（对比表不可出）
    if any(p["status"] == "failed" for p in payloads):
        return 1
    if all(p["status"] == "not_run" for p in payloads):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
