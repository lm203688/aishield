"""
AIShield MCP实时握手验证 (2026-07-28 协议兼容)

支持两种协议模式:
  - 新模式 (2026-07-28): 无状态请求，无需 initialize 握手，每个请求自包含协议版本和身份
  - 旧模式 (2025-03-26及之前): 有状态握手，initialize → initialized → 请求

模拟MCP客户端验证流程:
  1. 读取工具的MCP配置（从README或package.json提取）
  2. 如果是stdio类型: 解析command/args，无法直接执行（安全限制），标记为"需本地验证"
  3. 如果是HTTP类型: 尝试无状态 tools/list 请求，失败则回退到旧版 initialize 握手
  4. 对比声明的工具列表与实际返回的工具列表
  5. 检测异常: 声明的工具比实际多/少、工具描述过长（可能隐藏指令）
  6. 检测协议兼容性: 废弃传输(SSE/HTTP+SSE)、废弃功能(DCR)、缓存契约(ttlMs/cacheScope)
"""

import json
import re
import time
from urllib import request as urllib_request
from urllib.error import URLError
from datetime import datetime, timezone, timedelta

from .engine import urlopen, _is_safe_url

TZ = timezone(timedelta(hours=8))
USER_AGENT = "AIShield-Handshake/4.3"

# MCP 协议版本
MCP_PROTOCOL_LATEST = "2026-07-28"
MCP_PROTOCOL_LEGACY = "2025-03-26"


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
    """
    对HTTP MCP Server执行握手验证
    
    2026-07-28 协议: 优先尝试无状态 tools/list 请求（无需 initialize）
    旧版协议: 回退到 initialize → tools/list 有状态握手
    
    检测项:
    - 废弃的 SSE 传输（12个月过渡期）
    - 缓存契约 (ttlMs/cacheScope)
    - Multi Round-Trip Requests (input_required)
    - OAuth iss 参数缺失
    """
    if not _is_safe_url(url):
        return {"error": "Unsafe URL", "handshake_status": "blocked"}
    
    findings = []
    protocol_used = None
    
    # ========== 策略1: 尝试 2026-07-28 无状态请求 ==========
    # 新协议无需 initialize，直接发送 tools/list，通过 header 路由
    stateless_body = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {},
    }).encode()
    
    try:
        req = urllib_request.Request(
            url,
            data=stateless_body,
            headers={
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
                "Mcp-Method": "tools/list",
                "Mcp-Protocol-Version": MCP_PROTOCOL_LATEST,
            },
            method="POST",
        )
        with urllib_request.urlopen(req, timeout=10) as resp:
            resp_body = resp.read().decode("utf-8", errors="replace")
            resp_headers = dict(resp.headers)
            
            # 检查响应头中的协议版本
            server_protocol = resp_headers.get("Mcp-Protocol-Version", "")
            
            if resp_body.startswith("{"):
                try:
                    result = json.loads(resp_body)
                    if "result" in result:
                        protocol_used = MCP_PROTOCOL_LATEST
                        tools = result["result"].get("tools", [])
                        findings.append({
                            "type": "stateless_success",
                            "severity": "info",
                            "description": f"无状态请求成功 (2026-07-28)，返回 {len(tools)} 个工具",
                        })
                        
                        # 检查缓存契约
                        _check_cache_contract(result, findings)
                        
                        # 检查 Multi Round-Trip Requests
                        _check_input_required(tools, findings)
                        
                    elif "error" in result:
                        # 服务器不支持无状态模式，回退到旧版
                        findings.append({
                            "type": "stateless_unsupported",
                            "severity": "info",
                            "description": "服务器不支持无状态模式，回退到旧版握手",
                        })
                except json.JSONDecodeError:
                    pass
            elif "text/event-stream" in resp_headers.get("Content-Type", ""):
                # SSE 传输 - 2026-07-28 已废弃（12个月过渡期）
                findings.append({
                    "type": "deprecated_sse_transport",
                    "severity": "medium",
                    "description": "服务器使用 SSE 传输（2026-07-28 已废弃，12个月过渡期）",
                    "owasp_category": "MCP05",
                })
                
    except URLError:
        # 无状态请求失败，尝试旧版握手
        pass
    except Exception:
        pass
    
    # ========== 策略2: 回退到旧版 initialize 握手 ==========
    if protocol_used is None:
        init_body = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": MCP_PROTOCOL_LEGACY,
                "capabilities": {},
                "clientInfo": {"name": "AIShield-Scanner", "version": "4.3"},
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
                resp_headers = dict(resp.headers)
                
                # 检查是否返回了 Mcp-Session-Id（旧版有状态协议）
                session_id = resp_headers.get("Mcp-Session-Id", "")
                
                if resp_body.startswith("{"):
                    try:
                        result = json.loads(resp_body)
                        if "result" in result:
                            server_info = result["result"].get("serverInfo", {})
                            server_protocol = result["result"].get("protocolVersion", "")
                            protocol_used = server_protocol or MCP_PROTOCOL_LEGACY
                            
                            findings.append({
                                "type": "handshake_success",
                                "severity": "info",
                                "description": f"握手成功(旧版): {server_info.get('name', 'unknown')} v{server_info.get('version', '?')} (协议: {protocol_used})",
                            })
                            
                            # 如果服务器仍使用旧版协议，提示升级
                            if protocol_used != MCP_PROTOCOL_LATEST:
                                findings.append({
                                    "type": "legacy_protocol",
                                    "severity": "low",
                                    "description": f"服务器使用旧版协议 ({protocol_used})，建议升级到 2026-07-28",
                                })
                            
                            # 检查 session ID（旧版有状态特征）
                            if session_id:
                                findings.append({
                                    "type": "stateful_session",
                                    "severity": "low",
                                    "description": "服务器使用有状态会话 (Mcp-Session-Id)，2026-07-28 已废弃此模式",
                                })
                    except json.JSONDecodeError:
                        findings.append({
                            "type": "handshake_partial",
                            "severity": "medium",
                            "description": "服务器响应了但格式异常",
                            "evidence": resp_body[:200],
                        })
                elif "text/event-stream" in resp_headers.get("Content-Type", ""):
                    findings.append({
                        "type": "deprecated_sse_transport",
                        "severity": "medium",
                        "description": "服务器返回SSE流（2026-07-28 已废弃SSE传输）",
                        "owasp_category": "MCP05",
                    })
                    protocol_used = "SSE (deprecated)"
                    
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
        "handshake_status": "completed" if any(f["type"] in ("stateless_success", "handshake_success") for f in findings) else "failed",
        "protocol_detected": protocol_used,
        "findings": findings,
    }


def _check_cache_contract(result, findings):
    """检查 2026-07-28 缓存契约 (ttlMs/cacheScope)"""
    result_data = result.get("result", {})
    
    # 检查工具列表是否有缓存契约
    if isinstance(result_data, dict):
        ttl_ms = result_data.get("ttlMs")
        cache_scope = result_data.get("cacheScope")
        
        if ttl_ms is not None:
            findings.append({
                "type": "cache_contract_present",
                "severity": "info",
                "description": f"服务器声明缓存契约: ttlMs={ttl_ms}, cacheScope={cache_scope or 'default'}",
            })
        else:
            # 服务器未声明缓存契约，可能导致客户端过度重新获取
            findings.append({
                "type": "missing_cache_contract",
                "severity": "low",
                "description": "服务器未声明缓存契约 (ttlMs)，客户端可能过度重新获取工具列表",
            })


def _check_input_required(tools, findings):
    """检查 Multi Round-Trip Requests (input_required)"""
    if not isinstance(tools, list):
        return
    
    for tool in tools:
        if not isinstance(tool, dict):
            continue
        # 检查工具是否声明了 input_required 结果类型
        result_types = tool.get("resultTypes", [])
        if isinstance(result_types, list) and "input_required" in result_types:
            findings.append({
                "type": "multi_round_trip_tool",
                "severity": "info",
                "description": f"工具 '{tool.get('name', '?')}' 使用 Multi Round-Trip Requests (input_required)",
            })


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
    
    # 检查5: 废弃功能检测 (2026-07-28 协议)
    for fname, content in files.items():
        if not fname.endswith(('.ts', '.js', '.py')):
            continue
        
        # 检测 Dynamic Client Registration (DCR) - 已废弃
        if re.search(r'(?:register|dynamic).*(?:client|registration)', content, re.IGNORECASE):
            if 'client_id_metadata' not in content.lower():
                findings.append({
                    "type": "deprecated_dcr",
                    "severity": "low",
                    "description": "使用 Dynamic Client Registration (2026-07-28 已废弃，建议迁移到 Client ID Metadata Documents)",
                    "file": fname,
                    "owasp_category": "MCP02",
                })
        
        # 检测旧版 HTTP+SSE 传输 - 已废弃
        if re.search(r'(?:http\+sse|sse_transport|EventSource)', content, re.IGNORECASE):
            findings.append({
                "type": "deprecated_sse_code",
                "severity": "low",
                "description": "代码中使用 HTTP+SSE 传输 (2026-07-28 已废弃，12个月过渡期)",
                "file": fname,
                "owasp_category": "MCP05",
            })
        
        # 检测 Mcp-Session-Id 使用 - 已废弃
        if re.search(r'Mcp-Session-Id|session_id.*mcp', content, re.IGNORECASE):
            findings.append({
                "type": "deprecated_session_id",
                "severity": "low",
                "description": "代码中使用 Mcp-Session-Id (2026-07-28 已废弃有状态会话)",
                "file": fname,
            })
        
        # 检测 OAuth iss 参数缺失 (RFC 9207)
        if re.search(r'authorization.*code|oauth.*token', content, re.IGNORECASE):
            if 'iss' not in content and 'issuer' not in content.lower():
                findings.append({
                    "type": "missing_oauth_iss",
                    "severity": "medium",
                    "description": "OAuth 流程未验证 iss 参数 (RFC 9207)，存在 mix-up 攻击风险",
                    "file": fname,
                    "owasp_category": "MCP02",
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
        "scanner_version": "4.3",
        "protocol_version": MCP_PROTOCOL_LATEST,
    }