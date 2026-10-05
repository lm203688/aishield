#!/usr/bin/env python
"""
导出 findings 到指定目标端（F3 收口 CLI）+ 评分账本审计。

设计约束：
  * **不联网**。本脚本只负责「产出能投的东西」，投递留给调用方
    （curl 到 Splunk HEC 等），免得导出器自带 IO 让 CI 跑真网络。
  * 退出码严格：0 成功 / 1 参数错 / 2 目标端校验失败 / 3 其他异常。
    不用 `|| echo` 吞失败（项目铁律）。

用法：
  # 列可用目标端
  python scripts/export_findings.py --list

  # 单目标端免配置导出
  python scripts/export_findings.py --findings runs.json --target ocsf --out ocsf.json

  # 按目标端清单批量导出（配置里 enabled=false 的会跳过）
  python scripts/export_findings.py --findings runs.json --config targets.json --outdir out/

  # CSV 走文本（payload_text）
  python scripts/export_findings.py --findings runs.json --target csv --out findings.csv

  # 顺便审一遍评分账本：扣分能不能逐项翻出来、归因有没有 rule_id
  python scripts/export_findings.py --findings runs.json --target json --audit-score
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scanner.export_registry import TARGETS, TargetConfig, batch_export, export  # noqa: E402


def _load_findings(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if isinstance(data.get("findings"), list):
            return data["findings"]
        if isinstance(data.get("scan_result"), dict):
            return data["scan_result"].get("findings") or []
    raise SystemExit("[arg] 不支持的 findings 结构: %s" % path)


def _configs(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    items = data.get("targets") if isinstance(data, dict) and "targets" in data else [data]
    return [TargetConfig.from_dict(i) for i in items]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="AIShield 统一导出面 CLI")
    ap.add_argument("--list", action="store_true", help="列出可用目标端")
    ap.add_argument("--findings", help="findings JSON 文件（数组或 {findings:[...]}）")
    ap.add_argument("--target", help="目标端名（见 --list）")
    ap.add_argument("--config", help="目标端配置 JSON（含 targets 清单或单个目标）")
    ap.add_argument("--name", default="adhoc", help="单目标导出时的目标名")
    ap.add_argument("--out", help="输出文件（不给则打印）")
    ap.add_argument("--outdir", help="批量导出输出目录")
    ap.add_argument("--audit-score", action="store_true", help="对 findings 重算分数并审计扣分账本")
    ap.add_argument("--total-files", type=int, default=0, help="审计用的文件数（影响空扫描阻尼）")
    args = ap.parse_args(argv)

    if args.list:
        print("可用目标端（%d）:" % len(TARGETS))
        for n, s in sorted(TARGETS.items()):
            print("  %-10s %-22s %s" % (n, "%s %s" % (s["schema_name"], s["schema_version"]), s["note"]))
        return 0
    if not args.findings:
        print("[arg] 需要 --findings（或用 --list）")
        return 1
    if not args.target and not args.config:
        print("[arg] 需要 --target 或 --config")
        return 1

    findings = _load_findings(args.findings)
    print("[load] findings=%d" % len(findings))

    rc = 0

    if args.config:
        cfgs = _configs(args.config)
        print("[config] 加载 %d 个目标端: %s" % (len(cfgs), ", ".join(c.name for c in cfgs)))
        outdir = args.outdir or "."
        os.makedirs(outdir, exist_ok=True)
        results = batch_export(findings, cfgs)
        for r in results:
            if not r.ok:
                rc = 2
            dst = os.path.join(outdir, "%s.%s" % (r.name, "csv" if r.spec["kind"] == "text" else "json"))
            _write(dst, r.payload, r.spec["kind"])
            print("[export] %-14s -> %s  ok=%s issues=%s"
                  % (r.name, dst, r.ok, r.issues or "-"))
    else:
        cfg = TargetConfig(args.name, args.target)
        r = export(findings, cfg)
        rc = 0 if r.ok else 2
        if args.out:
            _write(args.out, r.payload, r.spec["kind"])
            print("[export] %s -> %s" % (r.name, args.out))
        else:
            if r.spec["kind"] == "text":
                sys.stdout.write(r.payload)
            else:
                print(json.dumps(r.payload, ensure_ascii=False, indent=2))
        print("[export] schema=%s %s ok=%s warnings=%s"
              % (r.spec["schema_name"], r.spec["schema_version"], r.ok, r.warnings or "-"))

    if args.audit_score:
        rc = _audit_score(findings, args.total_files) or rc
    return rc


def _write(dst: str, payload, kind: str) -> None:
    if kind == "text":
        with open(dst, "w", encoding="utf-8", newline="") as fh:
            fh.write(payload)
    else:
        with open(dst, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)


def _audit_score(findings, total_files: int) -> int:
    """独立复算 + 账本审计，返回退出码（2=账本对不上）。"""
    from scanner.score_explain import audit, replay, ledger_from_replay, attribution_text

    rp = replay(findings, total_files=total_files)
    print("[score] 独立复算 overall=%s risk=%s digest=%s"
          % (rp["overall_score"], rp["risk_level"], rp["digest"]))
    scores = ledger_from_replay(rp)
    aud = audit(scores, findings=findings, total_files=total_files)
    print(attribution_text(scores))
    if not aud["ok"]:
        print("[audit] ✗ 账本有问题:")
        for i in aud["issues"]:
            print("        - [%s] %s" % (i.get("code"), i.get("message")))
        return 2
    if aud["warnings"]:
        for w in aud["warnings"]:
            print("[audit] ! %s" % w["message"])
    print("[audit] ✓ 扣分账本闭合，attribution_complete=%s coverage=%.1f%%"
          % (aud["attribution_complete"], aud["coverage"] * 100))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - CLI 顶层兜底，退出码必须诚实
        print("[fatal] %r" % exc)
        sys.exit(3)
