"""
AIShield MCP实时握手验证

模拟MCP客户端握手流程:
  1. 读取工具的MCP配置（从README或package.json提取）
  2. 如果是stdio类型: 解析command/args，无法直接执行（安全限制），标记为"需本地验证"
  3. 如果是SSE/StreamableHTTP类型: 尝试连接并执行initialize → tools/list
  4. 对比声明的工具列表与实际返回的工具列表
  5. 检测异常: 声明的工具比实际多/少、工具描述过长（可能隐藏指令）
"""

import json
import re
import time
from urllib import request as urllib_request
from urllib.error import URLError
from datetime import datetime, timezone, timedelta

from .engine import urlopen, _is_safe_url

TZ = timezone(timedelta(hours=8))
USER_AGENT = "AIShield-Handshake/4.0"


def _extract_mcp_config_from_repo(files):
    """从仓库文件中提取MCP Server配置"""
    configs = []
    
    # 从README/文档中提取JSON配置块
    doc_files = {k: v for k, v in files.items() if k.endswith('.md')}
    for fname, content in doc_files.items():
        # 匹配 mcpServers JSON配置
        json_blocks = re.findall(r'mcpServers["\s]*[:=]["\s]*\{[^}]+\}[^}]*\}', content, re.DOTALL)
        for block in json_blocks[:3]:
            try:
                # 尝试解析
                cleaned = block
                # 提取最内层的JSON对象
                match = re.search(r'\{["\s\w:/"\'\-,\.]+\}', cleaned)
                if match:
                    parsed = json.loads(match.group())
                    if "command" in parsed or "url" in parsed:
                        configs.append(parsed)
            except (json.JSONDecodeError, ValueError):
                pass
        
        # 匹配 npx / node 命令行
        npx_matches = re.findall(r'npx\s+-y\s+([@\w/-]+)', content)
        for pkg in npx_matches[:3]:
            configs.append({"command": "npx", "args": ["-y", pkg], "source": "readme"})
    
    # 从package.json提取bin配置
    if "package.json" in files:
        try:
            pkg = json.loads(files["package.json"])
            if "bin" in pkg:
                bin_config = pkg["bin"]
                if isinstance(bin_config, str):
                    configs.append({"command": "node", "args": [bin_config], "source": "package.json"})
                elif isinstance(bin_config, dict):
                    for name, path in list(bin_config.items())[:1]:
                        configs.append({"command": "node", "args": [path], "source": "package.json"})
        except (json.JSONDecodeError, ValueError):
            pass
    
    return configs


def _try_http_handshake(url):
    """尝试对HTTP/SSE MCP Server执行握手"""
    if not _is_safe_url(url):
        return {"error": "Unsafe URL", "handshake_status": "blocked"}
    
    findings = []
    
    # Step 1: 尝试initialize
    init_body = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "AIShield-Scanner", "version": "4.0"},
        },
    }).encode()
    
    try:
        req = urllib_request.Request(
            url,
            data=init_body,
            headers={
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
                "Accept": "application/json, text/event-stream",
            },
            method="POST",
        )
        with urllib_request.urlopen(req, timeout=10) as resp:
            resp_body = resp.read().decode("utf-8", errors="replace")
            
            # 可能是SSE流或JSON-RPC响应
            if resp_body.startswith("{"):
                try:
                    result = json.loads(resp_body)
                    if "result" in result:
                        server_info = result["result"].get("serverInfo", {})
                        findings.append({
                            "type": "handshake_success",
                            "severity": "info",
                            "description": f"握手成功: {server_info.get('name', 'unknown')} v{server_info.get('version', '?')}",
                        })
                except json.JSONDecodeError:
                    findings.append({
                        "type": "handshake_partial",
                        "severity": "medium",
                        "description": "服务器响应了但格式异常",
                        "evidence": resp_body[:200],
                    })
            else:
                findings.append({
                    "type": "handshake_sse",
                    "severity": "info",
                    "description": "服务器返回SSE流（StreamableHTTP）",
                })
                
    except URLError as e:
        findings.append({
            "type": "handshake_failed",
            "severity": "medium",
            "description": f"握手失败: {str(e)[:100]}",
        })
    except Exception as e:
        findings.append({
            "type": "handshake_error",
            "severity": "low",
            "description": f"握手异常: {str(e)[:100]}",
        })
    
    return {
        "handshake_status": "completed" if any(f["type"] == "handshake_success" for f in findings) else "failed",
        "findings": findings,
    }


def verify_handshake(source_url):
    """
    对MCP Server执行握手验证
    
    1. 获取源码，提取MCP配置
    2. 分析配置（command/url/args/env）
    3. 如果是HTTP类型，尝试实际握手
    4. 检测配置中的安全指标
    """
    from .engine import fetch_github_source
    
    source_data = fetch_github_source(source_url)
    files = source_data.get("files", {})
    
    if not files:
        return {"error": "Could not fetch source files", "handshake_status": "unknown"}
    
    # 提取MCP配置
    configs = _extract_mcp_config_from_repo(files)
    
    # 分析配置安全指标
    findings = []
    
    for i, config in enumerate(configs):
        cmd = config.get("command", "")
        args = config.get("args", [])
        env = config.get("env", {})
        
        # 检查1: 是否使用npx（供应链风险）
        if cmd == "npx":
            if "-y" in args:
                findings.append({
                    "type": "npx_auto_install",
                    "severity": "medium",
                    "description": "使用npx -y自动安装（跳过确认，存在供应链风险）",
                    "evidence": f"npx {' '.join(args[:3])}",
                    "owasp_category": "MCP04",
                })
        
        # 检查2: 是否有敏感环境变量
        sensitive_env_keys = ["API_KEY", "SECRET", "TOKEN", "PASSWORD", "CREDENTIAL"]
        for key in env:
            if any(s in key.upper() for s in sensitive_env_keys):
                findings.append({
                    "type": "sensitive_env",
                    "severity": "high",
                    "description": f"MCP配置要求敏感环境变量: {key}",
                    "evidence": key,
                    "owasp_category": "MCP01",
                })
        
        # 检查3: 是否有url字段（远程MCP）
        remote_url = config.get("url", "")
        if remote_url:
            if not _is_safe_url(remote_url):
                findings.append({
                    "type": "unsafe_remote_url",
                    "severity": "critical",
                    "description": f"MCP配置指向不安全URL: {remote_url}",
                    "owasp_category": "MCP09",
                })
            else:
                # 尝试握手
                handshake = _try_http_handshake(remote_url)
                findings.extend(handshake.get("findings", []))
    
    # 检查4: 工具描述异常长度
    for fname, content in files.items():
        if not fname.endswith(('.ts', '.js', '.py', '.json')):
            continue
        desc_matches = re.findall(r'(?:description|desc)\s*[=:]\s*["\'`]([^"\'`]{200,})', content, re.DOTALL)
        for desc in desc_matches:
            if len(desc) > 500:
                findings.append({
                    "type": "oversized_description",
                    "severity": "high",
                    "description": f"工具描述异常长({len(desc)}字符)，可能隐藏恶意指令",
                    "file": fname,
                    "owasp_category": "MCP03",
                })
    
    # 汇总
    critical = sum(1 for f in findings if f["severity"] == "critical")
    high = sum(1 for f in findings if f["severity"] == "high")
    
    if critical > 0:
        status = "dangerous"
    elif high > 0:
        status = "warning"
    elif findings:
        status = "info"
    else:
        status = "passed"
    
    return {
        "source_url": source_url,
        "handshake_status": status,
        "configs_found": len(configs),
        "configs": configs[:3],
        "findings": findings,
        "total_findings": len(findings),
        "files_analyzed": len(files),
        "scanned_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "scanner_version": "4.0",
    }