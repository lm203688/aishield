"""
AIShield 扫描引擎 — 完整扫描流水线

包含: 静态分析 + 依赖分析 + 密钥检测 + Tool Poisoning语义检测 + 污点分析 + 评分
"""

import re
import json
import time
import os
import sys
from urllib import request as urllib_request
from urllib.error import URLError, HTTPError
from datetime import datetime, timezone, timedelta
from ipaddress import ip_address

from .rules import (
    OWASP_MCP_TOP10, DANGEROUS_NPM_PACKAGES, DANGEROUS_PYPI_PACKAGES,
    GENERATED_PACKAGE_BLACKLIST,
    SKIP_EXTENSIONS, SKIP_NAMES, analyze as rules_analyze,
    check_package_name,
    check_dependency_hygiene,
)

try:
    from .llm_analyzer import analyze_tool_poisoning as llm_poisoning, analyze_supply_chain_risk as llm_supply_chain
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

TZ = timezone(timedelta(hours=8))

# 单一版本常量：任何「用户可读到的扫描版本声明」都必须引用它，
# 并经 scripts/sync_version.py 门禁与全仓库版本保持一致（不得手抄字面量）。
SCANNER_VERSION = "4.11.0"
USER_AGENT = "AIShield/4.0"

# 关键分析器：它们失败 = 「没能分析」而不是「没有发现风险」。
# 安全工具的失败语义必须区分二者：前者绝不能显示成 safe/0 findings。
# 审计 P0-3：把 except Exception → [] 的静默失败改为显式 failed 状态。
_CRITICAL_ANALYZERS = frozenset({
    "toxic_flow",
    "cross_channel",
    "capability",
    "baseline_drift",
})

# 统一退出码（审计 §10）：0=完成且未达阈值 / 1=完成且达阻断阈值 /
# 2=输入或配置错误 / 3=扫描不完整或关键分析器失败 / 4=证据或签名验证失败。
EXIT_OK = 0
EXIT_THRESHOLD = 1
EXIT_CONFIG = 2
EXIT_INCOMPLETE = 3
EXIT_EVIDENCE = 4


def _new_analyzer_state():
    """返回分析器状态容器。每个分析器记录 status/error/duration_ms。"""
    return {}


def _record_analyzer(state, name, status, error=None, duration_ms=None, findings_count=0):
    """记录单个分析器的运行状态。

    status: complete / partial / failed / not_applicable / skipped
    - complete: 正常跑完
    - partial: 部分输入无法分析（如个别文件解析失败），但主体完成
    - failed:  分析器整体失败（异常），结果不可信
    - not_applicable: 该分析器在本场景下无输入（如无 baseline 传入）
    - skipped: 可选分析器未启用（如 LLM 不可用）
    """
    state[name] = {
        "status": status,
        "error": error,
        "duration_ms": duration_ms,
        "findings_count": findings_count,
    }
    return state[name]


def analyzer_failures(state):
    """返回关键分析器中 status == failed 的名字列表（非关键失败不视为不完整）。"""
    if not state:
        return []
    return sorted(
        name for name, info in state.items()
        if name in _CRITICAL_ANALYZERS and info.get("status") == "failed"
    )


def scan_exit_code(report, fail_on="high"):
    """统一退出码决策：0/1/2/3/4。

    优先级（审计 §10 口径）：配置错误 > 关键分析器失败 > 达阈值 > 完成。
    关键分析器失败返回 3，即使分数显示 safe —— 这是 fail-closed 的核心：
    「没能分析」绝不能伪装成「没有发现风险」。
    """
    state = report.get("analyzer_status") or {}
    fails = analyzer_failures(state)
    if fails:
        return EXIT_INCOMPLETE
    # 达阻断阈值（复用 action_entrypoint 的风险档排序语义）
    rank = {"": 0, "info": 1, "safe": 1, "low": 1, "medium": 2, "high": 3, "critical": 4}
    risk = (report.get("risk_level") or "safe").lower()
    if rank.get(risk, 0) >= rank.get(str(fail_on).lower(), 2):
        return EXIT_THRESHOLD
    return EXIT_OK


def _is_safe_url(url):
    """防止SSRF: 拒绝内网地址和私有IP"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        host = parsed.hostname
        if not host:
            return False
        # 阻止私有IP
        ip = ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return False
    except (ValueError, TypeError):
        # 非IP地址，继续
        blocked_hosts = [
            "localhost", "127.0.0.1", "0.0.0.0", "::1",
            "169.254.169.254", "metadata.google.internal",
            "metadata.aws", "100.64.0.0",
        ]
        host_lower = host.lower()
        if any(h in host_lower for h in blocked_hosts):
            return False
    return True


def urlopen(url, headers=None, timeout=15):
    """安全的urlopen — 带SSRF防护"""
    if not _is_safe_url(url):
        return None
    try:
        req = urllib_request.Request(url, headers=headers or {"User-Agent": USER_AGENT})
        with urllib_request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except (URLError, HTTPError, OSError, ValueError):
        return None


def fetch_github_source(github_url):
    """从GitHub获取源码 — 多策略降级"""
    match = re.match(r'https://github\.com/([^/]+)/([^/]+)(?:/tree/([^/]+).*?)?$', github_url)
    if not match:
        return {"files": {}, "commit_hash": "", "error": "无法解析URL"}

    owner, repo, branch = match.groups()

    if not branch:
        repo_data = urlopen(
            f"https://api.github.com/repos/{owner}/{repo}",
            {"User-Agent": USER_AGENT, "Accept": "application/vnd.github.v3+json"}, 10
        )
        if repo_data:
            try:
                repo_info = json.loads(repo_data.decode())
                branch = repo_info.get("default_branch", "main")
            except Exception:
                branch = "main"
        else:
            branch = "main"

    files = {}
    commit_hash = ""

    # 策略1: GitHub API tree
    api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    data = urlopen(api_url, {"User-Agent": USER_AGENT, "Accept": "application/vnd.github.v3+json"}, 15)

    code_files = []
    if data:
        try:
            tree_data = json.loads(data.decode())
            commit_hash = tree_data.get("sha", "")[:8]
            for item in tree_data.get("tree", []):
                if item["type"] != "blob":
                    continue
                path = item["path"]
                if any(path.endswith(ext) for ext in [".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".yaml", ".yml", ".toml", ".md", ".txt", ".sh", ".env.example"]):
                    if any(skip in path for skip in ["node_modules", ".git", "dist", "__pycache__", ".venv", "vendor", "build", ".next", "package-lock", "yarn.lock", "pnpm-lock"]):
                        continue
                    if "/" not in path or path.startswith("src/") or path.startswith("lib/"):
                        code_files.insert(0, path)
                    else:
                        code_files.append(path)
        except Exception:
            pass

    # 策略2: API限流时，用raw URL拉常见文件
    if not code_files:
        for f in ["README.md", "package.json", "setup.py", "pyproject.toml", "requirements.txt",
                   "Dockerfile", "index.js", "index.ts", "main.py", "app.py", "server.py",
                   "src/index.ts", "src/index.js", "src/main.py", "src/app.py", "src/server.ts"]:
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{f}"
            content = urlopen(raw_url, {"User-Agent": USER_AGENT}, 8)
            if content:
                try:
                    text = content.decode("utf-8", errors="replace")
                    if len(text) > 100000:
                        continue
                    files[f] = text
                except Exception:
                    continue

    # 策略3: 有文件列表时，用raw URL拉取
    if code_files and not files:
        for path in code_files[:20]:
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
            content = urlopen(raw_url, {"User-Agent": USER_AGENT}, 8)
            if content:
                try:
                    text = content.decode("utf-8", errors="replace")
                    if len(text) > 100000:
                        continue
                    files[path] = text
                except Exception:
                    continue
            time.sleep(0.3)

    return {"files": files, "commit_hash": commit_hash, "repo": f"{owner}/{repo}"}


def dependency_analysis(files):
    """依赖分析 + 已知恶意包检测"""
    findings = []
    dependencies = []

    for fname, content in files.items():
        if fname == "package.json":
            try:
                pkg = json.loads(content)
                for dep_type in ["dependencies", "devDependencies"]:
                    for name, ver in pkg.get(dep_type, {}).items():
                        dependencies.append({"name": name, "version": ver, "source": "npm"})
                        if name in DANGEROUS_NPM_PACKAGES:
                            gen = GENERATED_PACKAGE_BLACKLIST.get(f"npm:{name}")
                            if gen:
                                cves = ", ".join(gen.get("advisories", [])[:3]) or "未知CVE"
                                desc = (f"依赖含已知漏洞（{cves}）: {name}"
                                        f"（情报公告，建议升级至修复版本）")
                            else:
                                desc = f"已知恶意npm包: {name}"
                            findings.append({"type": "dangerous_dependency", "package": name, "severity": "critical", "description": desc, "owasp_category": "MCP04"})
                        for _f in check_package_name(name, "npm"):
                            _f["file"] = fname
                            findings.append(_f)
            except Exception:
                pass
        elif fname == "requirements.txt":
            for line in content.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = re.split('[=<>!]+', line, maxsplit=1)
                    name = parts[0].strip()
                    ver = parts[1].strip() if len(parts) > 1 else "latest"
                    dependencies.append({"name": name, "version": ver, "source": "pypi"})
                    if name in DANGEROUS_PYPI_PACKAGES:
                        gen = GENERATED_PACKAGE_BLACKLIST.get(f"pypi:{name}")
                        if gen:
                            cves = ", ".join(gen.get("advisories", [])[:3]) or "未知CVE"
                            desc = (f"依赖含已知漏洞（{cves}）: {name}"
                                    f"（情报公告，建议升级至修复版本）")
                        else:
                            desc = f"已知恶意PyPI包: {name}"
                        findings.append({"type": "dangerous_dependency", "package": name, "severity": "critical", "description": desc, "owasp_category": "MCP04"})
                    for _f in check_package_name(name, "pypi"):
                        _f["file"] = fname
                        findings.append(_f)
        elif fname == "pyproject.toml":
            # PEP 621 数组形式: dependencies = ["a", "b>=1.0"]
            for m in re.finditer(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL):
                for item in re.findall(r'["\']([a-zA-Z0-9_.\-]+)["\']', m.group(1)):
                    _name = re.split(r'[<>=!~ ]', item, 1)[0].strip()
                    if not _name or _name == "dependencies":
                        continue
                    dependencies.append({"name": _name, "version": "unknown", "source": "pypi"})
                    for _f in check_package_name(_name, "pypi"):
                        _f["file"] = fname
                        findings.append(_f)
            # 单依赖写法: name = "ver"
            for line in content.split('\n'):
                m = re.match(r'^\s*([a-zA-Z0-9_-]+)\s*[=<>!]', line)
                if m and m.group(1) != "dependencies":
                    _name = m.group(1)
                    dependencies.append({"name": _name, "version": "unknown", "source": "pypi"})
                    for _f in check_package_name(_name, "pypi"):
                        _f["file"] = fname
                        findings.append(_f)

    # manifest 级依赖卫生（安装脚本投毒 / 不可信来源 / 未锁定版本 / 缺 lockfile）
    try:
        findings.extend(check_dependency_hygiene(files))
    except Exception:
        pass

    # 幻觉包 advisory 降噪：同类 info 级最多保留 5 条
    _advisory = [f for f in findings if f.get("type") == "suspected_hallucinated_package"]
    if len(_advisory) > 5:
        keep = set(id(f) for f in _advisory[:5])
        findings = [
            f for f in findings
            if f.get("type") != "suspected_hallucinated_package" or id(f) in keep
        ]

    return {"findings": findings, "dependencies": dependencies, "total_dependencies": len(dependencies)}


def secrets_detection(files):
    """敏感信息检测（MCP01补充）"""
    findings = []
    SECRET_PATTERNS = {
        r'(?:mongodb|postgres|postgresql|mysql|redis)://[^\s\'"]+': ("数据库连接字符串", "critical"),
        r'\.env\b': (".env文件引用", "low"),
        r'-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----': ("私钥文件", "critical"),
    }

    for filepath, content in files.items():
        for pattern, (desc, severity) in SECRET_PATTERNS.items():
            try:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
            except re.error:
                continue
            for m in matches[:2]:
                line_num = content[:m.start()].count('\n') + 1
                findings.append({
                    "type": "secret_exposure",
                    "severity": severity,
                    "description": desc,
                    "file": filepath,
                    "lines": str(line_num),
                    "evidence": m.group()[:60] + "..." if len(m.group()) > 60 else m.group(),
                    "owasp_category": "MCP01",
                })

    return {"findings": findings}


def tool_poisoning_detection(files):
    """Tool Poisoning语义级检测（MCP03补充）"""
    findings = []

    # 描述-代码不一致检测
    DESCRIPTION_CODE_MISMATCH = [
        (r'description\s*[=:]\s*["\'][^"\']*(?:read|get|fetch|list|search|query)[^"\']*["\']',
         r'\b(write|create|delete|update|remove|drop|exec|system)\s*\(',
         "描述声称只读但代码有写/执行操作"),
        (r'description\s*[=:]\s*["\'][^"\']*(?:safe|secure|no.*risk|trusted|harmless)[^"\']*["\']',
         r'\b(exec|eval|system|subprocess|child_process)\s*\(',
         "描述声称安全但代码有命令执行"),
        (r'description\s*[=:]\s*["\'][^"\']*(?:local|offline|no.*network|standalone)[^"\']*["\']',
         r'\b(fetch|requests\.(get|post)|axios|http\.(get|post))\s*\(',
         "描述声称本地/离线但代码有网络请求"),
    ]

    for filepath, content in files.items():
        for desc_pattern, code_pattern, desc in DESCRIPTION_CODE_MISMATCH:
            if re.search(desc_pattern, content, re.IGNORECASE) and re.search(code_pattern, content, re.IGNORECASE):
                findings.append({
                    "type": "tool_poisoning",
                    "severity": "critical",
                    "description": f"描述-代码不一致: {desc}",
                    "file": filepath,
                    "lines": "multiple",
                    "evidence": desc,
                    "owasp_category": "MCP03",
                })

    # typosquat / 幻觉包检测已下沉到 dependency_analysis（离线编辑距离 + 形近字符 + 厂商仿冒）

    return findings


def taint_analysis(files):
    """简化污点分析 — 检测用户输入→危险操作的数据流"""
    TAINT_SOURCES = [
        r'\brequest\.(args|form|json|data|files|values|cookies|headers)\b',
        r'\binput\s*\(',
        r'\bargv\b',
        r'\bprocess\.argv\b',
        r'\bgetenv\b',
    ]
    TAINT_SINKS = [
        (r'\bexec\s*\(', "exec()"),
        (r'\beval\s*\(', "eval()"),
        (r'\bos\.system\s*\(', "os.system()"),
        (r'\bsubprocess\.(run|call|Popen)\s*\(', "subprocess"),
        (r'\bchild_process\.exec\s*\(', "child_process.exec()"),
        (r'\b(?:requests|axios|fetch)\s*\(', "HTTP请求"),
        (r'\bexecute\s*\(', "SQL execute"),
    ]

    findings = []
    for filepath, content in files.items():
        lines = content.splitlines()
        tainted_vars = set()
        for i, line in enumerate(lines):
            for source_pattern in TAINT_SOURCES:
                if re.search(source_pattern, line):
                    var_match = re.match(r'\s*(\w+)\s*[:=]', line)
                    if var_match:
                        tainted_vars.add(var_match.group(1))
            for sink_pattern, sink_desc in TAINT_SINKS:
                if re.search(sink_pattern, line):
                    for var in tainted_vars:
                        if var in line:
                            findings.append({
                                "type": "taint_flow",
                                "severity": "critical",
                                "description": f"污点数据流: 用户输入 → {sink_desc}",
                                "file": filepath,
                                "lines": str(i + 1),
                                "evidence": line.strip()[:120],
                                "owasp_category": "MCP05",
                            })
                            break

    return findings


# 维度配置：(标签, 权重, 扣分表, 类别过滤)
_DIM_CONFIG = {
    "security_score":     ("security",     0.40, {"critical": 20, "high": 10, "medium": 4, "low": 1, "info": 0}, None),
    "permissions_score":  ("permissions",  0.20, {"critical": 25, "high": 15, "medium": 8, "low": 2, "info": 0}, "MCP02"),
    "data_handling_score":("data",         0.20, {"critical": 20, "high": 10, "medium": 5, "low": 2, "info": 0}, ("MCP01", "MCP04", "MCP10")),
    "supply_chain_score": ("supply",       0.10, {"critical": 30, "high": 15, "medium": 5, "low": 0, "info": 0}, "MCP04"),
    "reliability_score":  ("reliability",  0.10, {"critical": 15, "high": 8, "medium": 3, "low": 0, "info": 0}, ("MCP07", "MCP08")),
}


def calculate_scores(static, dependency, secrets, poisoning, taint, total_files, extra_findings=None):
    """
    5维评分 + 可解释归因（M3）。

    返回除分数外，额外携带 score_breakdown：每个维度的 base/penalty/主要扣分项，
    以及 top_deductions 全局排序，让"为什么 72 不是 71"可解释、可申诉。
    """
    # 收集所有 findings（含 LLM 语义分析等额外来源）
    all_findings = []
    for src in (static.get("findings", []), dependency.get("findings", []),
                secrets.get("findings", []), poisoning, taint):
        all_findings.extend(src)
    if extra_findings:
        all_findings.extend(extra_findings)

    # 去重
    seen = set()
    unique = []
    for f in all_findings:
        key = f"{f.get('type', '')}:{f.get('description', '')}:{f.get('file', '')}"
        if key not in seen:
            seen.add(key)
            unique.append(f)

    dims = {}
    breakdown = {}
    for dim_key, (label, w, ded, catfilter) in _DIM_CONFIG.items():
        penalties = []
        seen_desc = set()
        folded = []
        for f in unique:
            cat = f.get("owasp_category", "")
            if catfilter is not None:
                if isinstance(catfilter, str):
                    if cat != catfilter:
                        continue
                elif cat not in catfilter:
                    continue
            desc = f.get("description", "")
            if desc in seen_desc:
                # 同一描述只在扣分里体现一次。这是口径，不是 bug —— 但必须可见：
                # 否则用户以为「三条同类告警只扣一次分」是漏算，可解释性就假了。
                # 折叠项单独记录 rule_id/严重度/次数，回放时能查到被吞掉的是哪几条。
                folded.append({"reason": desc, "severity": f.get("severity", "info"),
                               "amount": ded.get(f.get("severity", "info"), 0),
                               "owasp": cat, "rule_id": f.get("rule_id") or f.get("type", ""),
                               "folded_count": 1})
                continue
            seen_desc.add(desc)
            amt = ded.get(f.get("severity", "info"), 0)
            if amt > 0:
                penalties.append({"reason": desc, "severity": f.get("severity", "info"),
                                   "amount": amt, "owasp": cat,
                                   # 归因必须能落到具体规则上，不然「为什么扣 25 分」
                                   # 只能看到一句中文描述、申诉无门。
                                   "rule_id": f.get("rule_id") or f.get("type", ""),
                                   "finding_type": f.get("type", "")})
        total_pen = sum(p["amount"] for p in penalties)
        base = 100
        # total_files==0 阻尼（空扫描不虚高）
        if total_files == 0:
            if dim_key == "security_score":
                base = min(base, 65)
            elif dim_key == "data_handling_score":
                base = min(base, 70)
            elif dim_key == "reliability_score":
                base = max(0, base - 30)
        score = max(0, min(100, base - total_pen))
        dims[dim_key] = score
        full = sorted(penalties, key=lambda p: -p["amount"])
        breakdown[dim_key] = {
            "base": base,
            "penalty": total_pen,
            # 展示用 top5（历史兼容，别改现有消费方）
            "contributors": full[:5],
            # 全量扣分账：contributors 只留 5 条，penalty 却是全量求和 ——
            # 之前「展示 80 / 实际 105」的缺口就出在这里，解释永远拼不平。
            #  attributable 字段让 audit() 能 100% 闭合，缺一分都要能被抓出来。
            "contributions_full": full,
            "truncated": len(full) > 5,
            "folded_duplicates": folded,
        }

    overall = int(round(
        dims["security_score"] * 0.40 + dims["permissions_score"] * 0.20 +
        dims["data_handling_score"] * 0.20 + dims["supply_chain_score"] * 0.10 +
        dims["reliability_score"] * 0.10
    ))

    if dims["security_score"] < 40:
        risk_level = "critical"
    elif dims["security_score"] < 60:
        risk_level = "high"
    elif dims["security_score"] < 80:
        risk_level = "medium"
    else:
        risk_level = "safe"

    if overall >= 85:
        badge = "gold"
    elif overall >= 70:
        badge = "silver"
    elif overall >= 55:
        badge = "bronze"
    else:
        badge = "none"

    # 全局 Top 扣分项（可解释性核心）
    all_pen = []
    for dim_key, b in breakdown.items():
        for c in b["contributors"]:
            all_pen.append({"dimension": dim_key, **c})
    top_deductions = sorted(all_pen, key=lambda p: -p["amount"])[:8]

    return {
        "security_score": dims["security_score"],
        "permissions_score": dims["permissions_score"],
        "data_handling_score": dims["data_handling_score"],
        "supply_chain_score": dims["supply_chain_score"],
        "reliability_score": dims["reliability_score"],
        "overall_score": overall,
        "risk_level": risk_level,
        "badge_level": badge,
        "owasp_coverage": static.get("owasp_coverage", {}),
        "agentic_coverage": static.get("agentic_coverage", {}),
        "rules_count": static.get("patterns_checked", 0),
        "score_breakdown": breakdown,
        "top_deductions": top_deductions,
    }


def explain_score(scores: dict) -> str:
    """把评分拆解转成一句话人话解释（供报告/CLI 使用）。"""
    lines = [f"总分 {scores.get('overall_score')}（{scores.get('risk_level')}，badge={scores.get('badge_level')}）"]
    for dim_key in ("security_score", "permissions_score", "data_handling_score",
                    "supply_chain_score", "reliability_score"):
        b = scores.get("score_breakdown", {}).get(dim_key, {})
        lines.append(f"  · {dim_key}: {scores.get(dim_key)} (基准 {b.get('base')} - 扣分 {b.get('penalty')})")
    top = scores.get("top_deductions", [])[:3]
    if top:
        lines.append("主要扣分项:")
        for t in top:
            lines.append(f"  - [{t.get('severity')}] {t.get('reason')} (-{t.get('amount')})")
    return "\n".join(lines)


def generate_recommendations(findings, scores):
    """生成修复建议"""
    recs = []
    critical = [f for f in findings if f.get("severity") == "critical"]
    high = [f for f in findings if f.get("severity") == "high"]

    if any("命令执行" in f.get("description", "") or "exec" in f.get("description", "").lower() for f in critical + high):
        recs.append("避免直接执行用户输入的命令，使用参数化调用或白名单机制")
    if any("网络请求" in f.get("description", "") or "HTTP请求" in f.get("description", "") for f in findings):
        recs.append("审查所有网络请求目标，确保不向未授权服务器发送数据")
    if any("越狱" in f.get("description", "") or "注入" in f.get("description", "") for f in findings):
        recs.append("检测到提示注入风险，建议添加输入过滤和输出检查")
    if any("外传" in f.get("description", "") or "SSRF" in f.get("description", "") for f in findings):
        recs.append("检测到数据外传/SSRF风险，建议审查数据流向并添加URL白名单")
    if any("密钥" in f.get("description", "") or "密码" in f.get("description", "") or "Token" in f.get("description", "") for f in findings):
        recs.append("检测到硬编码凭据，使用环境变量或密钥管理服务")
    if any("SSL" in f.get("description", "") or "证书" in f.get("description", "") for f in findings):
        recs.append("SSL证书验证被禁用，生产环境必须启用")
    if any("投毒" in f.get("description", "") or "不一致" in f.get("description", "") for f in findings):
        recs.append("工具描述与代码行为不一致，存在投毒嫌疑")
    if scores["security_score"] < 50:
        recs.append("安全评分较低，建议进行全面安全审查后再发布")
    if scores["supply_chain_score"] < 70:
        recs.append("供应链评分偏低，建议锁定依赖版本并审计所有依赖")
    if not recs:
        recs.append("未发现明显安全风险，建议定期重新审计")
    return recs


def scan(source_url, tool_type="mcp", name="", description="", enable_osv=False, baseline=None):
    """
    完整扫描流水线

    Args:
        source_url: GitHub repo URL 或工具内容
        tool_type: mcp / skill / gpt / prompt
        name: 工具名称（可选）
        description: 工具描述（可选）
        enable_osv: 是否联网查 OSV.dev 实时 CVE（默认 False，隐私/限流优先）

    Returns:
        dict: 完整扫描报告
    """
    # 输入验证
    if not source_url or not isinstance(source_url, str):
        return {"error": "source_url is required and must be a string", "overall_score": 0, "badge_level": "none", "risk_level": "unknown", "findings": [], "total_findings": 0, "scanned_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"), "scanner_version": SCANNER_VERSION}
    
    source_url = source_url.strip()
    if len(source_url) > 500:
        return {"error": "source_url too long (max 500 chars)", "overall_score": 0, "badge_level": "none", "risk_level": "unknown", "findings": [], "total_findings": 0, "scanned_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"), "scanner_version": SCANNER_VERSION}
    
    if tool_type not in ("mcp", "skill", "gpt", "prompt"):
        tool_type = "mcp"
    
    # 仅允许GitHub URL扫描（非prompt类型）
    if tool_type not in ("gpt", "prompt") and not re.match(r'^https?://github\.com/[\w.-]+/[\w.-]+', source_url):
        if not re.match(r'^https?://', source_url):
            return {"error": "Only GitHub URLs are supported for scanning", "overall_score": 0, "badge_level": "none", "risk_level": "unknown", "findings": [], "total_findings": 0, "scanned_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"), "scanner_version": SCANNER_VERSION}
    # Step 1: 获取源码
    if tool_type == "gpt":
        source_data = {"files": {}, "commit_hash": "", "gpt_url": source_url}
    elif tool_type == "prompt":
        source_data = {"files": {"prompt.txt": source_url}, "commit_hash": ""}
    else:
        source_data = fetch_github_source(source_url)

    files = source_data.get("files", {})
    total_files = len(files)

    # 分析器状态账本：审计 P0-3，except→[] 的静默失败必须显式化。
    # 关键分析器（toxic_flow / cross_channel / capability / baseline_drift）
    # 失败时 scan_exit_code() 返回 3，绝不显示成 safe/0 findings。
    analyzer_state = _new_analyzer_state()

    # Step 2: 静态分析（对齐OWASP MCP Top 10）
    _t0 = time.time()
    try:
        static_results = rules_analyze(files, tool_type)
        _record_analyzer(analyzer_state, "static", "complete",
                         duration_ms=int((time.time() - _t0) * 1000),
                         findings_count=len(static_results.get("findings", [])))
    except Exception as e:  # noqa: BLE001
        static_results = {"findings": [], "owasp_coverage": {}, "agentic_coverage": {}}
        _record_analyzer(analyzer_state, "static", "failed", error=repr(e),
                         duration_ms=int((time.time() - _t0) * 1000))

    # Step 3: 依赖分析
    _t0 = time.time()
    try:
        dependency_results = dependency_analysis(files)
        _record_analyzer(analyzer_state, "dependency", "complete",
                         duration_ms=int((time.time() - _t0) * 1000),
                         findings_count=len(dependency_results.get("findings", [])))
    except Exception as e:  # noqa: BLE001
        dependency_results = {"findings": [], "dependencies": [], "total_dependencies": 0}
        _record_analyzer(analyzer_state, "dependency", "failed", error=repr(e),
                         duration_ms=int((time.time() - _t0) * 1000))

    # Step 3b: OSV.dev 实时 CVE（D1，默认关闭）
    osv_findings = []
    if enable_osv:
        _t0 = time.time()
        try:
            from .osv import check_osv
            osv_findings = check_osv(dependency_results.get("dependencies", []), use_network=True)
            for _f in osv_findings:
                _f["file"] = "dependencies"
            _record_analyzer(analyzer_state, "osv", "complete",
                             duration_ms=int((time.time() - _t0) * 1000),
                             findings_count=len(osv_findings))
        except Exception as e:  # noqa: BLE001
            osv_findings = []
            _record_analyzer(analyzer_state, "osv", "failed", error=repr(e),
                             duration_ms=int((time.time() - _t0) * 1000))
    else:
        _record_analyzer(analyzer_state, "osv", "skipped",
                         error="enable_osv=false（默认离线优先）")

    # Step 4: 密钥检测
    _t0 = time.time()
    try:
        secrets_results = secrets_detection(files)
        _record_analyzer(analyzer_state, "secrets", "complete",
                         duration_ms=int((time.time() - _t0) * 1000),
                         findings_count=len(secrets_results.get("findings", [])))
    except Exception as e:  # noqa: BLE001
        secrets_results = {"findings": []}
        _record_analyzer(analyzer_state, "secrets", "failed", error=repr(e),
                         duration_ms=int((time.time() - _t0) * 1000))

    # Step 5: Tool Poisoning语义检测（正则）
    _t0 = time.time()
    try:
        poisoning_results = tool_poisoning_detection(files)
        _record_analyzer(analyzer_state, "poisoning", "complete",
                         duration_ms=int((time.time() - _t0) * 1000),
                         findings_count=len(poisoning_results))
    except Exception as e:  # noqa: BLE001
        poisoning_results = []
        _record_analyzer(analyzer_state, "poisoning", "failed", error=repr(e),
                         duration_ms=int((time.time() - _t0) * 1000))

    # Step 5b: LLM语义分析（如果可用）
    llm_results = {"findings": [], "analyzed": False}
    llm_sc_results = {"findings": [], "analyzed": False}
    if LLM_AVAILABLE:
        _t0 = time.time()
        try:
            llm_results = llm_poisoning(files, name)
            llm_sc_results = llm_supply_chain(dependency_results)
            _record_analyzer(analyzer_state, "llm", "complete",
                             duration_ms=int((time.time() - _t0) * 1000),
                             findings_count=len(llm_results.get("findings", [])) + len(llm_sc_results.get("findings", [])))
        except Exception as e:  # noqa: BLE001
            llm_results = {"findings": [], "analyzed": False}
            llm_sc_results = {"findings": [], "analyzed": False}
            _record_analyzer(analyzer_state, "llm", "failed", error=repr(e),
                             duration_ms=int((time.time() - _t0) * 1000))
    else:
        _record_analyzer(analyzer_state, "llm", "skipped",
                         error="LLM analyzer not available")

    # Step 6: 污点分析
    _t0 = time.time()
    try:
        taint_results = taint_analysis(files)
        _record_analyzer(analyzer_state, "taint", "complete",
                         duration_ms=int((time.time() - _t0) * 1000),
                         findings_count=len(taint_results))
    except Exception as e:  # noqa: BLE001
        taint_results = []
        _record_analyzer(analyzer_state, "taint", "failed", error=repr(e),
                         duration_ms=int((time.time() - _t0) * 1000))

    # Step 6b: Toxic Flow 致命三要素（借鉴 Snyk agent-scan / mcp-security-scan）
    # 关键分析器：失败 ≠ 没有发现风险，必须记录 failed（审计 P0-3 fail-closed）。
    _t0 = time.time()
    try:
        from .baseline_scan import detect_toxic_flows, check_drift
        toxic_results = detect_toxic_flows(files).get("findings", [])
        _record_analyzer(analyzer_state, "toxic_flow", "complete",
                         duration_ms=int((time.time() - _t0) * 1000),
                         findings_count=len(toxic_results))
    except Exception as e:  # noqa: BLE001
        toxic_results = []
        _record_analyzer(analyzer_state, "toxic_flow", "failed", error=repr(e),
                         duration_ms=int((time.time() - _t0) * 1000))

    # Step 6c: 基线漂移比对（可选，传入 baseline 时启用 —— 定义级 rug-pull 钉扎）
    # 关键分析器：有 baseline 时失败必须记录，不能把「无法比对」当「无漂移」。
    drift_findings = []
    if baseline is not None:
        _t0 = time.time()
        try:
            from .baseline_scan import check_drift as _check_drift
            drift_findings = _check_drift(files, baseline).get("findings", [])
            _record_analyzer(analyzer_state, "baseline_drift", "complete",
                             duration_ms=int((time.time() - _t0) * 1000),
                             findings_count=len(drift_findings))
        except Exception as e:  # noqa: BLE001
            drift_findings = []
            _record_analyzer(analyzer_state, "baseline_drift", "failed", error=repr(e),
                             duration_ms=int((time.time() - _t0) * 1000))
    else:
        _record_analyzer(analyzer_state, "baseline_drift", "not_applicable")

    # Step 6d: 跨通道污点（分片重组 / 编码规避 / 跨引用逃逸 —— 单一通道扫描看不到完整恶意载荷）
    # 关键分析器：失败必须记录，不能静默当无跨通道风险。
    _t0 = time.time()
    try:
        from .cross_channel_taint import scan_cross_channel
        cross_channel_results = scan_cross_channel(files)
        _record_analyzer(analyzer_state, "cross_channel", "complete",
                         duration_ms=int((time.time() - _t0) * 1000),
                         findings_count=len(cross_channel_results))
    except Exception as e:  # noqa: BLE001
        cross_channel_results = []
        _record_analyzer(analyzer_state, "cross_channel", "failed", error=repr(e),
                         duration_ms=int((time.time() - _t0) * 1000))

    # Step 6e: 能力契约 diff（实现能力集 vs 声明 surface，超权即报）
    # 关键分析器：失败必须记录，不能静默当无超权。
    _t0 = time.time()
    try:
        from .capability_contract import scan_capability_contract
        capability_results = scan_capability_contract(files)
        _record_analyzer(analyzer_state, "capability", "complete",
                         duration_ms=int((time.time() - _t0) * 1000),
                         findings_count=len(capability_results))
    except Exception as e:  # noqa: BLE001
        capability_results = []
        _record_analyzer(analyzer_state, "capability", "failed", error=repr(e),
                         duration_ms=int((time.time() - _t0) * 1000))

    # Step 7: 评分（含 LLM 语义 findings 归因）
    scores = calculate_scores(
        static_results, dependency_results, secrets_results, poisoning_results, taint_results,
        total_files, extra_findings=(
            llm_results.get("findings", []) + llm_sc_results.get("findings", [])
            + toxic_results + cross_channel_results + capability_results
        ),
    )

    # 汇总去重
    all_findings = []
    for f in static_results.get("findings", []): all_findings.append(f)
    for f in dependency_results.get("findings", []): all_findings.append(f)
    for f in secrets_results.get("findings", []): all_findings.append(f)
    for f in poisoning_results: all_findings.append(f)
    for f in taint_results: all_findings.append(f)
    for f in llm_results.get("findings", []): all_findings.append(f)
    for f in llm_sc_results.get("findings", []): all_findings.append(f)
    for f in toxic_results: all_findings.append(f)
    for f in cross_channel_results: all_findings.append(f)
    for f in capability_results: all_findings.append(f)
    for f in drift_findings: all_findings.append(f)
    for f in osv_findings: all_findings.append(f)

    seen = set()
    unique_findings = []
    for f in all_findings:
        key = f"{f.get('type', '')}:{f.get('description', '')}:{f.get('file', '')}"
        if key not in seen:
            seen.add(key)
            unique_findings.append(f)

    recommendations = generate_recommendations(unique_findings, scores)

    # Step 8: 合规映射（借鉴 Latteflo/mcp-scanner ——纯报告层，
    # findings 按 OWASP 类别聚合到 NIST CSF / ISO 27001 / PCI DSS 控制项）
    _t0 = time.time()
    try:
        from .compliance import compliance_summary as _compliance
        compliance_results = _compliance(unique_findings)
        _record_analyzer(analyzer_state, "compliance", "complete",
                         duration_ms=int((time.time() - _t0) * 1000))
    except Exception as e:  # noqa: BLE001
        compliance_results = {}
        _record_analyzer(analyzer_state, "compliance", "failed", error=repr(e),
                         duration_ms=int((time.time() - _t0) * 1000))

    # Step 8b: CoSAI MCP Security v2.0 采购证据包（2026-08-12 发布）。
    # 与 Step 8 的区别：CoSAI 回答的是"这套方案整体处于哪个安全保证级、
    # 八维度覆盖如何"—— 企业采购评审现场真正被问的问题。本仓内部 ASI
    # 编号与官方非同一套，故必须由这一层把证据对齐到采购方的语言。
    # 保证级不由扫描结果自动授予：未提供部署态证据时最高只主张 L1。
    _t0 = time.time()
    try:
        from .cosai_evidence import cosai_evidence_map as _cosai
        cosai_results = _cosai(unique_findings)
        _record_analyzer(analyzer_state, "cosai", "complete",
                         duration_ms=int((time.time() - _t0) * 1000))
    except Exception as e:  # noqa: BLE001
        cosai_results = {}
        _record_analyzer(analyzer_state, "cosai", "failed", error=repr(e),
                         duration_ms=int((time.time() - _t0) * 1000))

    return {
        **scores,
        "name": name or source_url.split("/")[-1],
        "source_url": source_url,
        "tool_type": tool_type,
        "findings": unique_findings,
        "total_findings": len(unique_findings),
        "static_analysis": static_results,
        "dependency_analysis": dependency_results,
        "secrets_detection": secrets_results,
        "llm_analysis": llm_results,
        "llm_supply_chain": llm_sc_results,
        "toxic_flow_scan": toxic_results,
        "baseline_drift": drift_findings,
        "compliance": compliance_results,
        "cosai": cosai_results,
        "osv_cve": osv_findings,
        # 审计 P0-3：分析器状态账本。每个分析器 status/error/duration_ms，
        # 关键分析器 failed → scan_exit_code() 返回 3（不完整），不得显示成 safe。
        "analyzer_status": analyzer_state,
        "analyzer_complete": sum(1 for i in analyzer_state.values() if i.get("status") == "complete"),
        "analyzer_failed": sum(1 for i in analyzer_state.values() if i.get("status") == "failed"),
        "commit_hash": source_data.get("commit_hash", ""),
        "recommendations": recommendations,
        "scanned_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "scanner_version": SCANNER_VERSION,
        "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)",
    }


def batch_scan(source_urls, tool_type="mcp", concurrency=3):
    """批量扫描多个工具（**真并发**，ThreadPoolExecutor）。

    早期实现是 ``for`` 循环 + ``time.sleep(1)``（注释明写"暂为串行"），并发形同
    虚设；此处改为线程池并行，与 ``batch_scanner.py`` 的并发模型一致。

    Args:
        source_urls: [{"url": "...", "name": "...", "type": "mcp"}, ...] 或 ["url", ...]
        tool_type: 默认工具类型
        concurrency: 并发数（线程池 worker 数）

    Returns:
        dict: 批量扫描结果汇总（结构与旧版一致，保证 server.py 调用方无感）
    """
    from concurrent.futures import ThreadPoolExecutor

    items = []
    for item in source_urls:
        url = item if isinstance(item, str) else item.get("url", "")
        name = "" if isinstance(item, str) else item.get("name", "")
        t = tool_type if isinstance(item, str) else item.get("type", tool_type)
        if url:
            items.append((url, name, t))

    results = []
    errors = []

    def _one(arg):
        url, name, t = arg
        try:
            return {"url": url, "result": scan(url, t, name)}
        except Exception as e:  # 单条失败不影响整体
            return {"url": url, "error": str(e)}

    with ThreadPoolExecutor(max_workers=max(1, int(concurrency))) as ex:
        for out in ex.map(_one, items):
            if "error" in out:
                errors.append(out)
            else:
                results.append(out["result"])

    return {
        "total": len(source_urls),
        "scanned": len(results),
        "errors": len(errors),
        "results": results,
        "error_details": errors,
        "scanned_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"),
    }


if __name__ == "__main__":
    # 自测
    test_result = scan("https://github.com/snyk/agent-scan", "mcp", "snyk-agent-scan")
    print(json.dumps({"success": True, "findings_count": test_result["total_findings"], "score": test_result["overall_score"]}, ensure_ascii=False))