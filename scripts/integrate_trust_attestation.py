#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""integrate_trust_attestation.py —— 把 Trust Attestation 接进 agent 开发框架。

解决的问题
──────────
"我们做了持续鉴证" 和 "用 CrewAI/AutoGen/LangGraph 的人能用上持续鉴证" 是两件事。
后者缺的不是概念，是**三个具体动作**：知道自己的项目该挂哪里、拿到一份合规凭证、
以及在 CI 里自动续期。本工具就做这三件事，零依赖、离线可跑（`attest` 除外）。

三个子命令
──────────
    detect       扫一个项目目录：识别用了哪些 agent 框架、有哪些客户端配置面
    attest       把一次扫描结果换成**平台签发的**合规 attestation（调线上 API）
    emit-action  打印可粘贴的 GitHub Actions 作业片段（含校验步骤，防"凭证过期无人知"）

设计上的两条克制
────────────────
1. **评分不在本地重造。** `attest` 调 `POST /api/v1/attestations/from-scan`，
   用平台自己的评分语义。本地另算一套分数，只会产出第二份"看起来权威"的口径。
2. **不给第三方做背书。** 生成的凭证只声明"在本次规则集下未发现已知模式"，
   不声明"该工具无风险"（与 README 的 Runner Provenance 边界一致）。

用法
────
    python scripts/integrate_trust_attestation.py detect  .
    python scripts/integrate_trust_attestation.py attest  scan-result.json --out aishield-attestation.json
    python scripts/integrate_trust_attestation.py emit-action --frameworks crewai,langgraph
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, List

DEFAULT_BASE = os.environ.get("AISHIELD_BASE", "https://aishield.tools")

# 框架指纹：依赖名 / import 名 / 项目里出现的标志性文件。
# 只做"发现了什么"的陈述，不猜测没证据的东西。
FRAMEWORKS: Dict[str, Dict[str, Any]] = {
    "crewai": {"deps": ("crewai",), "imports": ("from crewai", "import crewai"),
               "files": ("crew.yaml", "crew.json", "agents.yaml")},
    "autogen": {"deps": ("autogen", "pyautogen", "ag2"), "imports": ("import autogen", "from autogen"),
                "files": ("OAI_CONFIG_LIST", "autogen_oai_config.json")},
    "langgraph": {"deps": ("langgraph",), "imports": ("from langgraph", "import langgraph"),
                  "files": ("langgraph.json",)},
    "langchain": {"deps": ("langchain",), "imports": ("from langchain", "import langchain"),
                  "files": ("langchain.yaml",)},
    "openai-agents": {"deps": ("openai-agents", "agents"), "imports": ("from agents import",),
                      "files": ("agents.json",)},
    "mcp": {"deps": ("mcp", "@modelcontextprotocol/sdk", "fastmcp"),
            "imports": ("from mcp", "import mcp", "from fastmcp"),
            "files": ("mcp.json", ".mcp.json", "server.json")},
}

DEP_FILES = ("requirements.txt", "requirements-dev.txt", "pyproject.toml", "Pipfile",
             "setup.py", "setup.cfg", "poetry.lock", "uv.lock")
JS_DEP_FILES = ("package.json",)

# 客户端配置面（MCP 客户端各自约定的路径）。判定"该挂哪里"用。
CLIENT_CONFIG_GLOBS = (
    ".mcp.json", "mcp.json", "server.json",
    ".cursor/mcp.json", ".vscode/mcp.json",
    "claude_desktop_config.json", ".claude/settings.json",
)

_SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv",
              ".mypy_cache", ".pytest_cache", ".next", "target"}


def _iter_files(root: str, exts: tuple, max_files: int = 4000) -> List[str]:
    """有界遍历（大仓库不失控）。"""
    out: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS and not d.startswith(".egg")]
        for fn in filenames:
            if fn.endswith(exts):
                out.append(os.path.join(dirpath, fn))
                if len(out) >= max_files:
                    return out
    return out


def _read(path: str, limit: int = 200_000) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(limit)
    except OSError:
        return ""


def cmd_detect(args: argparse.Namespace) -> int:
    root = os.path.abspath(args.path)
    if not os.path.isdir(root):
        print(f"❌ 不是目录：{root}")
        return 2

    dep_blob = ""
    for fn in DEP_FILES + JS_DEP_FILES:
        p = os.path.join(root, fn)
        if os.path.exists(p):
            dep_blob += "\n" + _read(p)
    dep_low = dep_blob.lower()

    # 导入面：只在 .py / .ts / .js 里找，且限制文件数。
    # **必须行内锚定 import 语句**：曾经用整块文本子串匹配，结果本仓库
    # 文档/注释里提到 "CrewAI / LangGraph" 就把自己判成了那四个框架的用户
    # —— 检测器的假阳性会直接变成"照这个结论去接鉴证"的错误动作。
    src = _iter_files(root, (".py", ".ts", ".js", ".tsx", ".jsx"))
    import_lines: List[str] = []
    for p in src:
        for line in _read(p, 40_000).splitlines():
            stripped = line.strip()
            if stripped.startswith(("import ", "from ")) or "require(" in stripped:
                import_lines.append(stripped.lower())
    import_low = "\n".join(import_lines)

    # 配置面（按 glob 判定，而不是猜）
    configs: List[str] = []
    for rel in CLIENT_CONFIG_GLOBS:
        if os.path.exists(os.path.join(root, rel)):
            configs.append(rel)

    found: List[Dict[str, Any]] = []
    for name, fp in FRAMEWORKS.items():
        ev: List[str] = []
        for d in fp["deps"]:
            if re.search(r"(^|[\s\"'=/><=])" + re.escape(d.lower()) + r"($|[\s\"'<>=,;\]]|==|>=|@)", dep_low, re.M):
                ev.append(f"依赖 {d}")
        for imp in fp["imports"]:
            if imp.lower() in import_low:
                ev.append(f"import `{imp}`")
        for f in fp["files"]:
            if os.path.exists(os.path.join(root, f)):
                ev.append(f"文件 {f}")
        if ev:
            found.append({"framework": name, "evidence": ev})

    result = {
        "root": root,
        "frameworks": found,
        "client_configs": configs,
        "scanned_source_files": len(src),
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(f"扫描目录：{root}（{len(src)} 个源文件）")
    if not found:
        print("  未识别到已知 agent 框架 —— 这不代表没有，只代表没有命中上表指纹。")
    for f in found:
        print(f"  ✓ {f['framework']:14s} ← " + "、".join(f["evidence"]))
    if configs:
        print("客户端/服务配置面（值得纳入扫描目标）：")
        for c in configs:
            print(f"  · {c}")
    else:
        print("未发现常见 MCP 客户端配置文件；若你的 agent 通过其他路径加载工具，请显式指定扫描目标。")
    return 0


def cmd_attest(args: argparse.Namespace) -> int:
    """把一次扫描结果换成平台签发的 attestation。

    **评分不在本地重造** —— 调平台端点，用平台自己的口径。
    """
    try:
        with open(args.scan_result, encoding="utf-8") as f:
            scan_result = json.load(f)
    except OSError as e:
        print(f"❌ 读不到扫描结果：{e}")
        return 2
    except json.JSONDecodeError as e:
        print(f"❌ 扫描结果不是合法 JSON：{e}")
        return 2

    payload = {
        "scan_result": scan_result,
        "subject_url": args.subject_url or "",
        "subject_name": args.subject_name or "",
        "subject_type": args.subject_type,
    }

    # fail-closed：平台端点要求 scan_result 里带 summary.overall_score。
    # 少了它端点会按 0 分算 → 直接产出"critical"级凭证。宁可本地炸，
    # 也不要把一份没依据的差评凭证签出去（或反过来，签出假的合规）。
    summary = scan_result.get("summary") if isinstance(scan_result, dict) else None
    if not isinstance(summary, dict) or "overall_score" not in summary:
        print("❌ 扫描结果缺少 `summary.overall_score` —— 平台端点会按 0 分处理，"
              "从而签出 critical 级凭证。拒绝继续。")
        print("   期望形状："
              '{"source_url": str, "scan_id": str, '
              '"summary": {"overall_score": int, "findings_total": int, "severity_counts": {...}}, '
              '"findings": [...]}')
        return 2
    if not args.subject_url:
        print("❌ 缺少 --subject-url（平台端点必填）。")
        return 2

    url = args.base.rstrip("/") + "/api/v1/attestations/from-scan"
    req = urllib.request.Request(
        url, method="POST",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "aishield-integrate/1"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        detail = e.read()[:400].decode("utf-8", "ignore")
        print(f"❌ 平台返回 {e.code}：{detail}")
        print("   若为鉴权失败，请通过 POST /api/v1/agent/setup 获取 api_key 后带上 Bearer 头。")
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"❌ 调用失败：{type(e).__name__}: {e}")
        return 1

    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(body, f, ensure_ascii=False, indent=2)
        print(f"✅ 凭证已写入 {args.out}")
        print("   边界说明：本凭证只声明「在本次规则集下未发现已知模式」，不构成对第三方无风险的背书。")
    else:
        print(json.dumps(body, ensure_ascii=False, indent=2))
    return 0


_ACTION_TMPL = """  # ── AIShield Trust Attestation：扫描 + 签发 + 过期即红 ──
  aishield-attestation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: 扫描（本地、离线、非执行式）
        run: |
          # 换成你的真实扫描命令，产物必须是 JSON
          python scripts/scan_to_json.py > scan-result.json

      - name: 签发 Trust Attestation
        run: |
          python scripts/integrate_trust_attestation.py attest scan-result.json             --subject-url "$GITHUB_SERVER_URL/$GITHUB_REPOSITORY"             --subject-name "$GITHUB_REPOSITORY"             --out aishield-attestation.json

      - name: 凭证过期即红（防"签过一次就不再管"）
        run: |
          python - <<'PYEOF'
          import json, datetime, sys
          d = json.load(open("aishield-attestation.json", encoding="utf-8"))
          exp = d.get("expires_at") or (d.get("attestation") or {}).get("expires_at")
          if not exp:
              print("::warning::凭证未含 expires_at，无法判过期")
              sys.exit(0)
          t = datetime.datetime.fromisoformat(str(exp).replace("Z", "+00:00"))
          if t < datetime.datetime.now(datetime.timezone.utc):
              print("::error::Trust Attestation 已过期 —— 请重跑签发")
              sys.exit(1)
          print("凭证有效至 " + t.isoformat())
          PYEOF

      - uses: actions/upload-artifact@v4
        with:
          name: aishield-attestation
          path: aishield-attestation.json
"""


def cmd_emit_action(args: argparse.Namespace) -> int:
    fw = [x.strip() for x in (args.frameworks or "").split(",") if x.strip()]
    print(f"# 目标框架：{', '.join(fw) if fw else '（未指定；片段与框架无关）'}")
    print("# 把下面这段粘进 .github/workflows/ 下的任意 job 集合里：")
    print(_ACTION_TMPL)
    print("# 说明：")
    print("#  1) 扫描必须是「本地、离线、非执行式」—— 绝不 spawn 被扫配置里的命令。")
    print("#  2) 凭证的 expires_at 校验是必须的：没有它，过期凭证会长期冒充有效状态。")
    print("#  3) 本凭证只声明「在本次规则集下未发现已知模式」，不是对第三方无风险的背书。")
    return 0


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="把 Trust Attestation 接进 agent 开发框架（CrewAI / AutoGen / LangGraph / MCP …）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("detect", help="识别项目用了哪些 agent 框架与配置面")
    d.add_argument("path", nargs="?", default=".")
    d.add_argument("--json", action="store_true")
    d.set_defaults(func=cmd_detect)

    a = sub.add_parser("attest", help="用平台端点把扫描结果换成合规 attestation")
    a.add_argument("scan_result", help="扫描结果 JSON 路径")
    a.add_argument("--out", help="输出凭证路径")
    a.add_argument("--base", default=DEFAULT_BASE, help=f"平台基址（默认 {DEFAULT_BASE}）")
    a.add_argument("--subject-url", default="")
    a.add_argument("--subject-name", default="")
    a.add_argument("--subject-type", default="agent",
                   choices=("agent", "mcp_server", "skill", "prompt"))
    a.set_defaults(func=cmd_attest)

    e = sub.add_parser("emit-action", help="打印 GitHub Actions 集成片段")
    e.add_argument("--frameworks", default="", help="逗号分隔，仅用于标注")
    e.set_defaults(func=cmd_emit_action)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
