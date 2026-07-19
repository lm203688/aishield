"""
AIShield Rug Pull 检测模块

检测MCP工具在版本更新中是否:
1. 移除了安全相关代码
2. 新增了可疑的网络请求
3. 修改了权限声明（扩大）
4. 改变了工具描述（隐藏意图）
"""

import json
import re
import time
from urllib import request as urllib_request
from urllib.error import URLError
from datetime import datetime, timezone, timedelta

from .engine import urlopen, _is_safe_url

TZ = timezone(timedelta(hours=8))
USER_AGENT = "AIShield-RugPullDetector/4.0"


def _fetch_commit_diff(owner, repo, sha1, sha2):
    """获取两个commit之间的diff"""
    url = f"https://api.github.com/repos/{owner}/{repo}/compare/{sha1}...{sha2}"
    data = urlopen(url, {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github.v3.diff",
    }, 15)
    return data.decode("utf-8", errors="replace") if data else ""


def _fetch_recent_commits(owner, repo, count=10):
    """获取最近的commit列表"""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page={count}"
    data = urlopen(url, {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github.v3+json",
    }, 10)
    if data:
        commits = json.loads(data.decode())
        return [{"sha": c["sha"][:8], "message": c["commit"]["message"][:100], "date": c["commit"]["committer"]["date"]} for c in commits]
    return []


def _analyze_diff_for_rug_pull(diff_text, commit_msg=""):
    """分析diff文本中的rug pull指标"""
    findings = []
    
    # 指标1: 移除安全相关代码
    REMOVED_SECURITY_PATTERNS = [
        (r'^-\s*.*(?:validate|sanitize|escape|filter|check).*input', "移除输入验证"),
        (r'^-\s*.*(?:verify|auth|authenticate|authorize)', "移除认证/验证"),
        (r'^-\s*.*(?:rate.?limit|throttle|quota)', "移除速率限制"),
        (r'^-\s*.*(?:permission|access.?control|acl)', "移除权限控制"),
        (r'^-\s*.*(?:log|audit|monitor|alert)', "移除日志/监控"),
        (r'^-\s*.*(?:CORS|cors|origin)', "移除CORS配置"),
        (r'^-\s*.*(?:encrypt|decrypt|hash|sign)', "移除加密/签名"),
    ]
    
    for pattern, desc in REMOVED_SECURITY_PATTERNS:
        matches = re.findall(pattern, diff_text, re.MULTILINE | re.IGNORECASE)
        if matches:
            findings.append({
                "type": "security_removal",
                "severity": "critical",
                "description": f"Rug Pull指标: {desc}",
                "evidence": f"{len(matches)}处删除",
                "owasp_category": "MCP08",
            })
    
    # 指标2: 新增可疑网络请求
    ADDED_NETWORK_PATTERNS = [
        (r'^\+\s*.*(?:requests?\.(?:get|post)|fetch|axios|http\.get|http\.post)\s*\(\s*[\'"]https?://', "新增HTTP请求"),
        (r'^\+\s*.*(?:urlopen|urlretrieve|download)', "新增URL请求"),
        (r'^\+\s*.*websocket|ws://|wss://', "新增WebSocket连接"),
    ]
    
    for pattern, desc in ADDED_NETWORK_PATTERNS:
        matches = re.findall(pattern, diff_text, re.MULTILINE | re.IGNORECASE)
        # 排除对已知安全API的调用
        safe_hosts = ["aishield", "owasp", "security"]
        suspicious = [m for m in matches if not any(h in m.lower() for h in safe_hosts)]
        if suspicious:
            findings.append({
                "type": "suspicious_network_addition",
                "severity": "high",
                "description": f"Rug Pull指标: {desc}",
                "evidence": f"{len(suspicious)}处新增",
                "owasp_category": "MCP10",
            })
    
    # 指标3: 权限声明扩大
    PERM_ESCALATION = [
        (r'^\+.*\*\s*', "新增通配符权限"),
        (r'^\+.*all\s*permissions', "新增all权限"),
        (r'^\+.*sudo|root|admin', "新增特权操作"),
        (r'^\+.*rmtree|unlink|remove|delete', "新增删除操作"),
    ]
    
    for pattern, desc in PERM_ESCALATION:
        matches = re.findall(pattern, diff_text, re.MULTILINE | re.IGNORECASE)
        if matches:
            findings.append({
                "type": "permission_escalation",
                "severity": "high",
                "description": f"Rug Pull指标: {desc}",
                "evidence": f"{len(matches)}处新增",
                "owasp_category": "MCP02",
            })
    
    # 指标4: 可疑commit消息
    SUSPICIOUS_COMMIT_WORDS = ["cleanup", "refactor", "fix lint", "formatting", "typo", "minor"]
    # 如果commit消息看起来很无害，但diff很大且有以上指标 → 高度可疑
    if any(w in commit_msg.lower() for w in SUSPICIOUS_COMMIT_WORDS):
        if findings:
            for f in findings:
                f["description"] += "（配合无害commit消息，高度可疑）"
    
    # 指标5: 大量文件删除
    deletions = len(re.findall(r'^---', diff_text, re.MULTILINE))
    additions = len(re.findall(r'^\+\+\+', diff_text, re.MULTILINE))
    if deletions > additions * 2 and deletions > 5:
        findings.append({
            "type": "mass_deletion",
            "severity": "medium",
            "description": f"大量代码删除: {deletions}处删除 vs {additions}处新增",
            "owasp_category": "MCP08",
        })
    
    return findings


def detect_rug_pull(source_url):
    """
    对GitHub仓库进行Rug Pull检测
    
    Args:
        source_url: GitHub仓库URL
    
    Returns:
        dict: Rug Pull检测报告
    """
    match = re.match(r'https://github\.com/([^/]+)/([^/]+)', source_url)
    if not match:
        return {"error": "Only GitHub URLs supported", "rug_pull_risk": "unknown"}
    
    owner, repo = match.groups()
    
    # 获取最近commits
    commits = _fetch_recent_commits(owner, repo, 10)
    if not commits or len(commits) < 2:
        return {"error": "Could not fetch commits", "rug_pull_risk": "unknown", "commits_analyzed": 0}
    
    all_findings = []
    comparisons = 0
    
    # 对比最近几对commit
    for i in range(min(5, len(commits) - 1)):
        sha_new = commits[i]["sha"]
        sha_old = commits[i + 1]["sha"]
        
        diff = _fetch_commit_diff(owner, repo, sha_old, sha_new)
        if not diff:
            continue
        
        findings = _analyze_diff_for_rug_pull(diff, commits[i]["message"])
        for f in findings:
            f["commit_sha"] = sha_new
            f["commit_message"] = commits[i]["message"]
        all_findings.extend(findings)
        comparisons += 1
        time.sleep(1)  # API限流
    
    # 计算风险等级
    critical = sum(1 for f in all_findings if f["severity"] == "critical")
    high = sum(1 for f in all_findings if f["severity"] == "high")
    
    if critical > 0:
        risk = "critical"
        score = 20
    elif high > 2:
        risk = "high"
        score = 40
    elif high > 0:
        risk = "medium"
        score = 65
    elif all_findings:
        risk = "low"
        score = 80
    else:
        risk = "safe"
        score = 95
    
    return {
        "source_url": source_url,
        "rug_pull_risk": risk,
        "rug_pull_score": score,
        "commits_analyzed": comparisons,
        "total_findings": len(all_findings),
        "findings": all_findings,
        "recent_commits": commits[:5],
        "scanned_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "scanner_version": "4.0",
    }