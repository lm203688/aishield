"""
scripts/gen_project_sbom.py — 生成 AIShield 项目自身的 CycloneDX SBOM

补齐赛道一「工程落地 & 安全审计」维度：除 scanner/sbom.py 对"扫描结果"
生成 SBOM 外，本脚本对**项目本身**产出 CycloneDX 1.5 SBOM
（零第三方依赖 + 内部模块组件清单），可被 CI / 安全工具链直接消费。

用法：
    python scripts/gen_project_sbom.py [--out sbom.cyclonedx.json]
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DEFAULT = os.path.join(_BASE, "sbom.cyclonedx.json")

TOOL_VERSION = "4.2.2"
PYTHON_REQUIRED = ">=3.10"


def _now_iso():
    return datetime.now(TZ).isoformat()


def _collect_internal_modules():
    """收集 eco/ 与 scanner/ 下的 .py 模块作为内部组件。"""
    components = []
    for root in ("eco", "scanner"):
        d = os.path.join(_BASE, root)
        if not os.path.isdir(d):
            continue
        for dirpath, _, files in os.walk(d):
            for fn in files:
                if fn.endswith(".py") and not fn.startswith("__"):
                    full = os.path.join(dirpath, fn)
                    rel = os.path.relpath(full, _BASE).replace("\\", "/")
                    components.append({
                        "type": "library",
                        "name": rel,
                        "version": TOOL_VERSION,
                        "bom-ref": "comp-" + rel,
                        "scope": "required",
                        "licenses": [{"license": {"id": "MIT"}}],
                    })
    return components


def generate(out_path=OUT_DEFAULT):
    components = _collect_internal_modules()
    # 零第三方依赖：仅 Python 标准库；显式声明一个 "stdlib" 运行时组件
    components.append({
        "type": "framework",
        "name": "Python standard library",
        "version": "3",
        "bom-ref": "comp-python-stdlib",
        "scope": "required",
        "description": "AIShield 仅依赖 Python 标准库，无任何第三方包（零供应链面）。",
    })

    bom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": "urn:uuid:" + str(uuid.uuid4()),
        "version": 1,
        "metadata": {
            "timestamp": _now_iso(),
            "authors": [{"name": "AIShield Project"}],
            "component": {
                "type": "application",
                "name": "aishield",
                "version": TOOL_VERSION,
                "description": "Local-first open-source AI Agent security scanner (MCP/Skill/Agent).",
                "licenses": [{"license": {"id": "MIT"}}],
                "externalReferences": [
                    {"type": "vcs", "url": "https://github.com/lm203688/aishield"},
                    {"type": "website", "url": "https://aishield.tools"},
                ],
            },
            "tools": [{"vendor": "AIShield", "name": "gen_project_sbom", "version": TOOL_VERSION}],
        },
        "components": components,
        "dependencies": [
            {"ref": "comp-python-stdlib", "dependsOn": []},
        ],
    }
    # 所有内部组件都依赖 stdlib
    for c in components:
        if c["bom-ref"] == "comp-python-stdlib":
            continue
        bom["dependencies"].append({"ref": c["bom-ref"], "dependsOn": ["comp-python-stdlib"]})

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(bom, f, ensure_ascii=False, indent=2)
    return out_path, len(components)


if __name__ == "__main__":
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else OUT_DEFAULT
    path, n = generate(out)
    print(f"SBOM 已生成: {path} (组件数={n})")
