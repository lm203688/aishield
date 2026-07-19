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
    SKIP_EXTENSIONS, SKIP_NAMES, analyze as rules_analyze,
)

try:
    from .llm_analyzer import analyze_tool_poisoning as llm_poisoning, analyze_supply_chain_risk as llm_supply_chain
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

TZ = timezone(timedelta(hours=8))
USER_AGENT = "AIShield/4.0"


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
                            findings.append({"type": "dangerous_dependency", "package": name, "severity": "critical", "description": f"已知恶意npm包: {name}", "owasp_category": "MCP04"})
            except Exception:
                pass
        elif fname == "requirements.txt":
            for line in content.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = re.split('[=<>!]+', line, 1)
                    name = parts[0].strip()
                    ver = parts[1].strip() if len(parts) > 1 else "latest"
                    dependencies.append({"name": name, "version": ver, "source": "pypi"})
                    if name in DANGEROUS_PYPI_PACKAGES:
                        findings.append({"type": "dangerous_dependency", "package": name, "severity": "critical", "description": f"已知恶意PyPI包: {name}", "owasp_category": "MCP04"})
        elif fname == "pyproject.toml":
            for line in content.split('\n'):
                m = re.match(r'^\s*([a-zA-Z0-9_-]+)\s*[=<>!]', line)
                if m:
                    dependencies.append({"name": m.group(1), "version": "unknown", "source": "pypi"})

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

    # 依赖typosquatting检测
    LEGIT_PACKAGES = {
        'express', 'lodash', 'react', 'vue', 'axios', 'request', 'chalk',
        'commander', 'fs-extra', 'dotenv', 'jsonwebtoken', 'bcrypt',
        'numpy', 'pandas', 'flask', 'django', 'requests', 'sqlalchemy',
        'pytest', 'setuptools', 'click', 'jinja2', 'fastapi', 'uvicorn',
    }

    for filepath, content in files.items():
        if filepath not in ("package.json", "requirements.txt", "pyproject.toml"):
            continue
        deps = []
        if filepath == "package.json":
            try:
                pkg = json.loads(content)
                deps = list(pkg.get('dependencies', {}).keys()) + list(pkg.get('devDependencies', {}).keys())
            except Exception:
                pass
        elif filepath == "requirements.txt":
            for line in content.splitlines():
                line = line.strip().split('==')[0].split('>=')[0].split('<=')[0].strip()
                if line and not line.startswith('#'):
                    deps.append(line)

        for dep in deps:
            dep_lower = dep.lower()
            for legit in LEGIT_PACKAGES:
                if legit == dep_lower:
                    continue
                if len(legit) >= 4 and len(dep_lower) >= 4:
                    if dep_lower.startswith(legit) and 0 < len(dep_lower) - len(legit) <= 2:
                        findings.append({
                            "type": "typosquatting",
                            "severity": "high",
                            "description": f"可能的typosquatting: '{dep}' 模仿 '{legit}'",
                            "file": filepath,
                            "lines": "N/A",
                            "evidence": f"{dep} vs {legit}",
                            "owasp_category": "MCP04",
                        })

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


def calculate_scores(static, dependency, secrets, poisoning, taint, total_files):
    """5维评分"""
    # 收集所有findings
    all_findings = []
    for f in static.get("findings", []): all_findings.append(f)
    for f in dependency.get("findings", []): all_findings.append(f)
    for f in secrets.get("findings", []): all_findings.append(f)
    for f in poisoning: all_findings.append(f)
    for f in taint: all_findings.append(f)

    # 去重
    seen = set()
    unique = []
    for f in all_findings:
        key = f"{f.get('type', '')}:{f.get('description', '')}:{f.get('file', '')}"
        if key not in seen:
            seen.add(key)
            unique.append(f)

    # 安全分 (40%)
    security = 100
    seen_descs = set()
    for f in unique:
        desc_key = f.get("description", "")
        if desc_key in seen_descs:
            continue
        seen_descs.add(desc_key)
        deductions = {"critical": 20, "high": 10, "medium": 4, "low": 1, "info": 0}
        security -= deductions.get(f.get("severity", "info"), 0)
    if total_files == 0:
        security = min(security, 65)
    security = max(0, min(100, security))

    # 权限分 (20%)
    permissions = 100
    for f in unique:
        cat = f.get("owasp_category", "")
        if cat == "MCP02":
            permissions -= {"critical": 25, "high": 15, "medium": 8, "low": 2}.get(f.get("severity", "info"), 0)
    permissions = max(0, min(100, permissions))

    # 数据处理分 (20%)
    data_handling = 100
    for f in unique:
        cat = f.get("owasp_category", "")
        if cat in ("MCP01", "MCP04", "MCP10"):
            data_handling -= {"critical": 20, "high": 10, "medium": 5, "low": 2}.get(f.get("severity", "info"), 0)
    if total_files == 0:
        data_handling = min(data_handling, 70)
    data_handling = max(0, min(100, data_handling))

    # 供应链分 (10%)
    supply_chain = 100
    for f in unique:
        cat = f.get("owasp_category", "")
        if cat == "MCP04":
            supply_chain -= {"critical": 30, "high": 15, "medium": 5}.get(f.get("severity", "info"), 0)
    supply_chain = max(0, min(100, supply_chain))

    # 可靠性分 (10%)
    reliability = 100
    for f in unique:
        cat = f.get("owasp_category", "")
        if cat in ("MCP07", "MCP08"):
            reliability -= {"critical": 15, "high": 8, "medium": 3}.get(f.get("severity", "info"), 0)
    if total_files == 0:
        reliability -= 30
    reliability = max(0, min(100, reliability))

    overall = int(security * 0.40 + permissions * 0.20 + data_handling * 0.20 + supply_chain * 0.10 + reliability * 0.10)

    if security < 40:
        risk_level = "critical"
    elif security < 60:
        risk_level = "high"
    elif security < 80:
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

    return {
        "security_score": security,
        "permissions_score": permissions,
        "data_handling_score": data_handling,
        "supply_chain_score": supply_chain,
        "reliability_score": reliability,
        "overall_score": overall,
        "risk_level": risk_level,
        "badge_level": badge,
        "owasp_coverage": static.get("owasp_coverage", {}),
        "rules_count": static.get("patterns_checked", 0),
    }


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


def scan(source_url, tool_type="mcp", name="", description=""):
    """
    完整扫描流水线
    
    Args:
        source_url: GitHub repo URL 或工具内容
        tool_type: mcp / skill / gpt / prompt
        name: 工具名称（可选）
        description: 工具描述（可选）
    
    Returns:
        dict: 完整扫描报告
    """
    # 输入验证
    if not source_url or not isinstance(source_url, str):
        return {"error": "source_url is required and must be a string", "overall_score": 0, "badge_level": "none", "risk_level": "critical", "findings": [], "total_findings": 0, "scanned_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"), "scanner_version": "4.0"}
    
    source_url = source_url.strip()
    if len(source_url) > 500:
        return {"error": "source_url too long (max 500 chars)", "overall_score": 0, "badge_level": "none", "risk_level": "critical", "findings": [], "total_findings": 0, "scanned_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"), "scanner_version": "4.0"}
    
    if tool_type not in ("mcp", "skill", "gpt", "prompt"):
        tool_type = "mcp"
    
    # 仅允许GitHub URL扫描（非prompt类型）
    if tool_type not in ("gpt", "prompt") and not re.match(r'^https?://github\.com/[\w.-]+/[\w.-]+', source_url):
        if not re.match(r'^https?://', source_url):
            return {"error": "Only GitHub URLs are supported for scanning", "overall_score": 0, "badge_level": "none", "risk_level": "critical", "findings": [], "total_findings": 0, "scanned_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"), "scanner_version": "4.0"}
    # Step 1: 获取源码
    if tool_type == "gpt":
        source_data = {"files": {}, "commit_hash": "", "gpt_url": source_url}
    elif tool_type == "prompt":
        source_data = {"files": {"prompt.txt": source_url}, "commit_hash": ""}
    else:
        source_data = fetch_github_source(source_url)

    files = source_data.get("files", {})
    total_files = len(files)

    # Step 2: 静态分析（对齐OWASP MCP Top 10）
    static_results = rules_analyze(files, tool_type)

    # Step 3: 依赖分析
    dependency_results = dependency_analysis(files)

    # Step 4: 密钥检测
    secrets_results = secrets_detection(files)

    # Step 5: Tool Poisoning语义检测（正则）
    poisoning_results = tool_poisoning_detection(files)

    # Step 5b: LLM语义分析（如果可用）
    llm_results = {"findings": [], "analyzed": False}
    llm_sc_results = {"findings": [], "analyzed": False}
    if LLM_AVAILABLE:
        llm_results = llm_poisoning(files, name)
        llm_sc_results = llm_supply_chain(dependency_results)

    # Step 6: 污点分析
    taint_results = taint_analysis(files)

    # Step 7: 评分
    scores = calculate_scores(static_results, dependency_results, secrets_results, poisoning_results, taint_results, total_files)

    # 汇总去重
    all_findings = []
    for f in static_results.get("findings", []): all_findings.append(f)
    for f in dependency_results.get("findings", []): all_findings.append(f)
    for f in secrets_results.get("findings", []): all_findings.append(f)
    for f in poisoning_results: all_findings.append(f)
    for f in taint_results: all_findings.append(f)
    for f in llm_results.get("findings", []): all_findings.append(f)
    for f in llm_sc_results.get("findings", []): all_findings.append(f)

    seen = set()
    unique_findings = []
    for f in all_findings:
        key = f"{f.get('type', '')}:{f.get('description', '')}:{f.get('file', '')}"
        if key not in seen:
            seen.add(key)
            unique_findings.append(f)

    recommendations = generate_recommendations(unique_findings, scores)

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
        "commit_hash": source_data.get("commit_hash", ""),
        "recommendations": recommendations,
        "scanned_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "scanner_version": "4.0",
        "owasp_standard": "OWASP MCP Top 10 (2025 v0.1)",
    }


def batch_scan(source_urls, tool_type="mcp", concurrency=3):
    """
    批量扫描多个工具
    
    Args:
        source_urls: [{"url": "...", "name": "...", "type": "mcp"}, ...]
        tool_type: 默认工具类型
        concurrency: 并发数（暂为串行，后续支持async）
    
    Returns:
        dict: 批量扫描结果汇总
    """
    results = []
    errors = []
    for item in source_urls:
        url = item if isinstance(item, str) else item.get("url", "")
        name = "" if isinstance(item, str) else item.get("name", "")
        t = tool_type if isinstance(item, str) else item.get("type", tool_type)
        try:
            result = scan(url, t, name)
            results.append(result)
            time.sleep(1)  # 避免GitHub API限流
        except Exception as e:
            errors.append({"url": url, "error": str(e)})
            time.sleep(1)

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