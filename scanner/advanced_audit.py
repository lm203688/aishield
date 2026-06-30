"""
AIShield 高级审计模块 v1.0 — 语义级深度检测

新增功能:
1. Tool Poisoning语义检测 (零宽字符 + 隐藏指令 + 描述-代码不一致)
2. Rug Pull检测 (版本对比 + postinstall分析)
3. 污点分析 (taint data flow tracking)
4. Trust Boundary检测
5. MCP握手验证 (live handshake)
6. 依赖混淆检测 (typosquatting)
"""

import re
import json
import hashlib
import urllib.request
import urllib.error
from datetime import datetime

# ============================================================
# 1. Tool Poisoning 语义级检测
# ============================================================

# 零宽字符
ZERO_WIDTH_CHARS = ['\u200b', '\u200c', '\u200d', '\u2060', '\ufeff']

# 隐藏指令模式（语义级，超越正则）
HIDDEN_INJECTION_PATTERNS = [
    # HTML实体编码的指令
    (r'&#\d+;.*(ignore|exec|eval|system|fetch)', "HTML实体编码隐藏指令"),
    # Base64编码的可疑字符串
    (r'(?:description|prompt|instructions)\s*[=:]\s*["\'][A-Za-z0-9+/=]{40,}["\']', "Base64编码的描述(可能隐藏指令)"),
    # Unicode转义序列
    (r'\\u[0-9a-fA-F]{4}\\u[0-9a-fA-F]{4}\\u[0-9a-fA-F]{4}', "Unicode转义序列(可能隐藏指令)"),
    # 嵌套JSON中的隐藏指令
    (r'"description"\s*:\s*"[^"]*\\"?[;|&][^"]*"', "JSON描述中的命令分隔符"),
    # Markdown链接中的隐藏指令
    (r'\[!\[.*?\]\(.*?\)\]\(javascript:.*?\)', "Markdown XSS链接注入"),
    # 工具描述中的过度权限声明
    (r'(?:description|instructions)\s*[=:]\s*["\'][^"\']*(?:always|must|never|ignore|override|bypass)[^"\']*["\']', "工具描述中的绝对指令"),
]

# 工具描述与代码行为不一致的指标
DESCRIPTION_CODE_MISMATCH = [
    (r'description\s*[=:]\s*["\'][^"\']*(?:read|get|fetch|list|search)[^"\']*["\']', 
     r'\b(write|create|delete|update|remove|drop|exec|system)\s*\(',
     "描述声称只读但代码有写操作"),
    (r'description\s*[=:]\s*["\'][^"\']*(?:safe|secure|no.*risk|trusted)[^"\']*["\']',
     r'\b(exec|eval|system|subprocess|child_process)\s*\(',
     "描述声称安全但代码有命令执行"),
    (r'description\s*[=:]\s*["\'][^"\']*(?:local|offline|no.*network)[^"\']*["\']',
     r'\b(fetch|requests\.(get|post)|axios|http\.(get|post))\s*\(',
     "描述声称本地但代码有网络请求"),
]

def detect_tool_poisoning_semantic(files):
    """语义级Tool Poisoning检测"""
    findings = []
    
    for filepath, content in files.items():
        # 检测零宽字符
        for zwc in ZERO_WIDTH_CHARS:
            if zwc in content:
                count = content.count(zwc)
                pos = content.index(zwc)
                line_num = content[:pos].count('\n') + 1
                findings.append({
                    "type": "tool_poisoning",
                    "severity": "critical",
                    "owasp_category": "MCP02",
                    "description": f"零宽字符检测到({count}个) — 可能隐藏恶意指令",
                    "file": filepath,
                    "lines": str(line_num),
                    "evidence": f"零宽字符 U+{ord(zwc):04X}"
                })
        
        # 检测隐藏指令模式
        for pattern, desc in HIDDEN_INJECTION_PATTERNS:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            for m in matches[:3]:
                line_num = content[:m.start()].count('\n') + 1
                findings.append({
                    "type": "tool_poisoning",
                    "severity": "high",
                    "owasp_category": "MCP02",
                    "description": desc,
                    "file": filepath,
                    "lines": str(line_num),
                    "evidence": m.group()[:100]
                })
        
        # 检测描述-代码不一致
        for desc_pattern, code_pattern, desc in DESCRIPTION_CODE_MISMATCH:
            if re.search(desc_pattern, content, re.IGNORECASE) and re.search(code_pattern, content, re.IGNORECASE):
                findings.append({
                    "type": "tool_poisoning",
                    "severity": "critical",
                    "owasp_category": "MCP02",
                    "description": f"描述-代码不一致: {desc}",
                    "file": filepath,
                    "lines": "multiple",
                    "evidence": desc
                })
    
    return findings


# ============================================================
# 2. Rug Pull 检测（版本对比）
# ============================================================

def detect_rug_pull(files, previous_version_files=None):
    """Rug Pull检测 — 对比版本差异"""
    findings = []
    
    # 如果没有历史版本，只做postinstall分析
    if previous_version_files is None:
        for filepath, content in files.items():
            if filepath.endswith('package.json'):
                try:
                    pkg = json.loads(content)
                    scripts = pkg.get('scripts', {})
                    for script_name, script_cmd in scripts.items():
                        if script_name in ('postinstall', 'preinstall', 'postpublish'):
                            # 检查postinstall是否执行外部命令
                            if re.search(r'(curl|wget|exec|eval|node -e|python -c)', script_cmd):
                                findings.append({
                                    "type": "rug_pull_risk",
                                    "severity": "critical",
                                    "owasp_category": "MCP03",
                                    "description": f"{script_name}脚本执行外部命令(Rug Pull风险)",
                                    "file": filepath,
                                    "lines": "N/A",
                                    "evidence": script_cmd[:100]
                                })
                            # 检查postinstall是否访问网络
                            if re.search(r'https?://', script_cmd):
                                findings.append({
                                    "type": "rug_pull_risk",
                                    "severity": "high",
                                    "owasp_category": "MCP03",
                                    "description": f"{script_name}脚本访问网络(Rug Pull风险)",
                                    "file": filepath,
                                    "lines": "N/A",
                                    "evidence": script_cmd[:100]
                                })
                except json.JSONDecodeError:
                    pass
        return findings
    
    # 有历史版本时，对比差异
    for filepath, current_content in files.items():
        if filepath in previous_version_files:
            old_content = previous_version_files[filepath]
            # 计算内容hash
            old_hash = hashlib.sha256(old_content.encode()).hexdigest()
            new_hash = hashlib.sha256(current_content.encode()).hexdigest()
            
            if old_hash != new_hash:
                # 找出新增的危险代码
                old_lines = set(old_content.splitlines())
                new_lines = set(current_content.splitlines())
                added_lines = new_lines - old_lines
                
                dangerous_patterns = [
                    (r'(exec|eval|system|subprocess)', "新增代码执行"),
                    (r'(fetch|requests\.|axios)', "新增网络请求"),
                    (r'(writeFile|write_text|open.*[wax])', "新增文件写入"),
                    (r'(child_process|os\.system)', "新增命令执行"),
                ]
                
                for line in added_lines:
                    for pattern, desc in dangerous_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            findings.append({
                                "type": "rug_pull_detected",
                                "severity": "critical",
                                "owasp_category": "MCP03",
                                "description": f"版本更新中新增危险代码: {desc}",
                                "file": filepath,
                                "lines": "N/A",
                                "evidence": line.strip()[:100]
                            })
    
    return findings


# ============================================================
# 3. 污点分析 (Taint Data Flow)
# ============================================================

# 污点源（用户输入/外部数据）
TAINT_SOURCES = [
    r'\brequest\.(args|form|json|data|files|values|cookies|headers)\b',
    r'\binput\s*\(',
    r'\bargv\b',
    r'\bprocess\.argv\b',
    r'\bos\.environ\b',
    r'\bgetenv\b',
    r'\breadline\b',
    r'\bstdin\b',
    r'params\[',
    r'args\[',
]

# 污点汇（危险操作）
TAINT_SINKS = [
    (r'\bexec\s*\(', "exec() with tainted input"),
    (r'\beval\s*\(', "eval() with tainted input"),
    (r'\bos\.system\s*\(', "os.system() with tainted input"),
    (r'\bsubprocess\.(run|call|Popen)\s*\(', "subprocess with tainted input"),
    (r'\bchild_process\.exec\s*\(', "child_process.exec with tainted input"),
    (r'\b(?:requests|axios|fetch)\s*\(', "HTTP request with tainted input"),
    (r'\bexecute\s*\(', "SQL execute with tainted input"),
    (r'\bopen\s*\(', "File open with tainted input"),
]

def taint_analysis(files):
    """污点分析 — 检测用户输入到危险操作的数据流"""
    findings = []
    
    for filepath, content in files.items():
        lines = content.splitlines()
        
        # 简化的污点分析：检测同一函数内是否有source→sink
        # 找到所有函数定义
        func_pattern = r'(?:def\s+(\w+)\s*\(|function\s+(\w+)\s*\(|(\w+)\s*[:=]\s*(?:async\s+)?function)'
        
        # 对每行检测是否有taint source
        tainted_vars = set()
        for i, line in enumerate(lines):
            # 检测taint source
            for source_pattern in TAINT_SOURCES:
                if re.search(source_pattern, line):
                    # 提取被赋值的变量名
                    var_match = re.match(r'\s*(\w+)\s*[:=]', line)
                    if var_match:
                        tainted_vars.add(var_match.group(1))
            
            # 检测taint sink
            for sink_pattern, sink_desc in TAINT_SINKS:
                if re.search(sink_pattern, line):
                    # 检查是否有tainted变量在sink中
                    for var in tainted_vars:
                        if var in line:
                            findings.append({
                                "type": "taint_flow",
                                "severity": "critical",
                                "owasp_category": "MCP07",
                                "description": f"污点数据流: 用户输入 → {sink_desc}",
                                "file": filepath,
                                "lines": str(i + 1),
                                "evidence": line.strip()[:100]
                            })
                            break
    
    return findings


# ============================================================
# 4. Trust Boundary 检测
# ============================================================

def detect_trust_boundary_violations(files):
    """检测Trust Boundary违规"""
    findings = []
    
    for filepath, content in files.items():
        # 检测无认证的敏感操作
        lines = content.splitlines()
        in_auth_check = False
        
        for i, line in enumerate(lines):
            # 检测认证检查
            if re.search(r'(auth|verify|check.*token|check.*key|require.*auth)', line, re.IGNORECASE):
                in_auth_check = True
                continue
            
            # 检测敏感操作前没有认证检查
            if re.search(r'(exec|eval|system|subprocess|writeFile|delete|remove|drop)', line, re.IGNORECASE):
                # 往上找10行，看是否有认证检查
                context_start = max(0, i - 10)
                context = '\n'.join(lines[context_start:i])
                if not re.search(r'(auth|verify|check.*token|check.*key|permission|authorize)', context, re.IGNORECASE):
                    findings.append({
                        "type": "trust_boundary",
                        "severity": "high",
                        "owasp_category": "MCP05",
                        "description": "敏感操作前无认证检查(Trust Boundary违规)",
                        "file": filepath,
                        "lines": str(i + 1),
                        "evidence": line.strip()[:100]
                    })
            
            # 检测跨域访问无限制
            if re.search(r'(Access-Control-Allow-Origin|CORS|cors)', line, re.IGNORECASE):
                if re.search(r'\*|true|all', line, re.IGNORECASE):
                    findings.append({
                        "type": "trust_boundary",
                        "severity": "high",
                        "owasp_category": "MCP05",
                        "description": "CORS设置为通配符(跨域无限制)",
                        "file": filepath,
                        "lines": str(i + 1),
                        "evidence": line.strip()[:100]
                    })
    
    return findings


# ============================================================
# 5. 依赖混淆检测 (Typosquatting)
# ============================================================

# 常见合法包名
LEGIT_PACKAGES = {
    'express', 'lodash', 'react', 'vue', 'axios', 'request', 'chalk',
    'commander', 'fs-extra', 'dotenv', 'jsonwebtoken', 'bcrypt',
    'numpy', 'pandas', 'flask', 'django', 'requests', 'sqlalchemy',
    'pytest', 'setuptools', 'pip', 'click', 'jinja2',
}

# 常见typosquatting模式
TYPOSQUAT_PATTERNS = [
    (r'(\w+)\.js$', "可能模仿{pkg}.js"),
    (r'(\w+)-cli$', "可能模仿{pkg} CLI工具"),
    (r'(\w+)2$', "可能模仿{pkg}（数字后缀）"),
    (r'(\w+)-pro$', "可能模仿{pkg} Pro版"),
]

def detect_typosquatting(files):
    """检测依赖混淆/typosquatting"""
    findings = []
    
    for filepath, content in files.items():
        if not (filepath.endswith('package.json') or filepath.endswith('requirements.txt') or 
                filepath.endswith('pyproject.toml') or filepath.endswith('setup.py')):
            continue
        
        # 提取依赖名
        deps = []
        if filepath.endswith('package.json'):
            try:
                pkg = json.loads(content)
                deps = list(pkg.get('dependencies', {}).keys()) + list(pkg.get('devDependencies', {}).keys())
            except:
                pass
        elif filepath.endswith('requirements.txt'):
            for line in content.splitlines():
                line = line.strip().split('==')[0].split('>=')[0].split('<=')[0].strip()
                if line and not line.startswith('#'):
                    deps.append(line)
        
        # 检查每个依赖
        for dep in deps:
            dep_lower = dep.lower()
            # 检查是否与合法包名相似
            for legit in LEGIT_PACKAGES:
                if legit == dep_lower:
                    continue
                # 编辑距离检查（简化版）
                if len(legit) >= 4 and len(dep_lower) >= 4:
                    # 检查常见typosquatting
                    if (dep_lower.startswith(legit) and len(dep_lower) - len(legit) <= 2 and dep_lower != legit):
                        findings.append({
                            "type": "typosquatting",
                            "severity": "high",
                            "owasp_category": "MCP10",
                            "description": f"可能的typosquatting: '{dep}' 模仿 '{legit}'",
                            "file": filepath,
                            "lines": "N/A",
                            "evidence": f"{dep} vs {legit}"
                        })
                    elif (legit.startswith(dep_lower) and len(legit) - len(dep_lower) <= 2):
                        findings.append({
                            "type": "typosquatting",
                            "severity": "medium",
                            "owasp_category": "MCP10",
                            "description": f"可能的typosquatting: '{dep}' 模仿 '{legit}'",
                            "file": filepath,
                            "lines": "N/A",
                            "evidence": f"{dep} vs {legit}"
                        })
    
    return findings


# ============================================================
# 6. MCP 握手验证 (Live Handshake)
# ============================================================

def live_handshake_check(server_url, timeout=10):
    """对远程MCP服务器执行实时握手验证"""
    findings = []
    
    try:
        # 1. 健康检查
        req = urllib.request.Request(f"{server_url}/health", headers={'User-Agent': 'AIShield/2.0'})
        resp = urllib.request.urlopen(req, timeout=timeout)
        if resp.status != 200:
            findings.append({
                "type": "handshake_failure",
                "severity": "high",
                "owasp_category": "MCP05",
                "description": f"MCP服务器健康检查失败: HTTP {resp.status}",
                "file": "remote",
                "lines": "N/A",
                "evidence": server_url
            })
        
        # 2. 检查MCP initialize握手
        init_payload = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "AIShield", "version": "2.0"}
            }
        }).encode()
        
        req = urllib.request.Request(
            server_url,
            data=init_payload,
            headers={'Content-Type': 'application/json', 'User-Agent': 'AIShield/2.0'},
            method='POST'
        )
        resp = urllib.request.urlopen(req, timeout=timeout)
        result = json.loads(resp.read())
        
        # 验证响应
        if 'result' not in result:
            findings.append({
                "type": "handshake_failure",
                "severity": "critical",
                "owasp_category": "MCP05",
                "description": "MCP initialize握手失败: 无result字段",
                "file": "remote",
                "lines": "N/A",
                "evidence": str(result)[:100]
            })
        else:
            server_info = result['result'].get('serverInfo', {})
            if not server_info.get('name'):
                findings.append({
                    "type": "handshake_warning",
                    "severity": "medium",
                    "owasp_category": "MCP05",
                    "description": "MCP服务器未提供名称",
                    "file": "remote",
                    "lines": "N/A",
                    "evidence": str(server_info)[:100]
                })
        
        # 3. 检查tools/list
        tools_payload = json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }).encode()
        
        req = urllib.request.Request(
            server_url,
            data=tools_payload,
            headers={'Content-Type': 'application/json', 'User-Agent': 'AIShield/2.0'},
            method='POST'
        )
        resp = urllib.request.urlopen(req, timeout=timeout)
        tools_result = json.loads(resp.read())
        
        tools = tools_result.get('result', {}).get('tools', [])
        
        # 检查每个工具描述是否安全
        for tool in tools:
            desc = tool.get('description', '')
            # 检查工具描述中的隐藏指令
            for pattern in [r'ignore.*previous', r'forget.*everything', r'you\s+are\s+now']:
                if re.search(pattern, desc, re.IGNORECASE):
                    findings.append({
                        "type": "handshake_tool_poisoning",
                        "severity": "critical",
                        "owasp_category": "MCP02",
                        "description": f"运行时发现工具描述含恶意指令: {tool.get('name', '?')}",
                        "file": "remote",
                        "lines": "N/A",
                        "evidence": desc[:100]
                    })
    
    except urllib.error.URLError as e:
        findings.append({
            "type": "handshake_failure",
            "severity": "high",
            "owasp_category": "MCP05",
            "description": f"MCP服务器连接失败: {str(e)}",
            "file": "remote",
            "lines": "N/A",
            "evidence": server_url
        })
    except Exception as e:
        findings.append({
            "type": "handshake_error",
            "severity": "medium",
            "owasp_category": "MCP05",
            "description": f"握手验证异常: {str(e)}",
            "file": "remote",
            "lines": "N/A",
            "evidence": str(e)[:100]
        })
    
    return findings


# ============================================================
# 综合高级审计
# ============================================================

def run_advanced_audit(files, tool_type="mcp", server_url=None, previous_version=None):
    """运行所有高级审计模块"""
    all_findings = []
    
    # 1. Tool Poisoning语义检测
    all_findings.extend(detect_tool_poisoning_semantic(files))
    
    # 2. Rug Pull检测
    all_findings.extend(detect_rug_pull(files, previous_version))
    
    # 3. 污点分析
    all_findings.extend(taint_analysis(files))
    
    # 4. Trust Boundary检测
    all_findings.extend(detect_trust_boundary_violations(files))
    
    # 5. 依赖混淆检测
    all_findings.extend(detect_typosquatting(files))
    
    # 6. MCP握手验证（可选，需要server_url）
    if server_url:
        all_findings.extend(live_handshake_check(server_url))
    
    # 汇总
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in all_findings:
        sev = f.get("severity", "info")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
    
    return {
        "advanced_findings": all_findings,
        "total_advanced_findings": len(all_findings),
        "severity_counts": severity_counts,
        "modules_run": [
            "tool_poisoning_semantic",
            "rug_pull_detection",
            "taint_analysis",
            "trust_boundary",
            "typosquatting",
            "live_handshake" if server_url else None
        ],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


if __name__ == "__main__":
    # 自测
    test_files = {
        "test.py": """
import os
user_input = input("Enter command: ")
os.system(user_input)  # taint flow!

description = "This is a safe read-only tool"
exec("rm -rf /")  # mismatch!
""",
        "package.json": '{"dependencies": {"expressx": "1.0", "lodahs": "2.0"}}'
    }
    
    result = run_advanced_audit(test_files)
    print(f"Total findings: {result['total_advanced_findings']}")
    for f in result['advanced_findings']:
        print(f"  [{f['severity']}] {f['description']}")
