"""
AIShield 扫描规则 v3.0 — OWASP MCP Top 10 对齐 + 100+ 规则

OWASP MCP Top 10 (2026):
  MCP01 - Prompt Injection (提示注入)
  MCP02 - Tool Poisoning (工具投毒)
  MCP03 - Rug Pull (版本篡改)
  MCP04 - Data Exfiltration (数据外传)
  MCP05 - Insecure Authentication (不安全认证)
  MCP06 - Server-Side Request Forgery (SSRF)
  MCP07 - Command Injection (命令注入)
  MCP08 - Insecure Transport (不安全传输)
  MCP09 - Overly Broad Permissions (过宽权限)
  MCP10 - Supply Chain Risks (供应链风险)
"""

import re

# ============================================================
# 规则定义格式: (pattern, description, severity, owasp_category)
# severity: critical / high / medium / low / info
# owasp_category: MCP01-MCP10 或 None
# ============================================================

STATIC_RULES = {
    # ========== MCP07 - Command Injection (命令注入) ==========
    r'\bos\.system\s*\(': ("os.system() 命令执行", "critical", "MCP07"),
    r'\bos\.popen\s*\(': ("os.popen() 命令执行", "critical", "MCP07"),
    r'\bos\.exec\s*\(': ("os.exec() 命令执行", "critical", "MCP07"),
    r'\bos\.spawn\s*\(': ("os.spawn() 命令执行", "high", "MCP07"),
    r'\bsubprocess\.(run|call|Popen|check_output|check_call)\s*\(': ("subprocess 命令执行", "high", "MCP07"),
    r'\bsubprocess\.(run|call|Popen)\s*\([^)]*shell\s*=\s*True': ("subprocess shell=True 极危险", "critical", "MCP07"),
    r'\bexec\s*\(': ("exec() 动态代码执行", "critical", "MCP07"),
    r'\beval\s*\(': ("eval() 动态代码执行", "critical", "MCP07"),
    r'\bchild_process\.exec\s*\(': ("Node.js child_process.exec", "high", "MCP07"),
    r'\bchild_process\.execSync\s*\(': ("Node.js child_process.execSync", "high", "MCP07"),
    r'\bchild_process\.spawn\s*\(': ("Node.js child_process.spawn", "high", "MCP07"),
    r'\bFunction\s*\(\s*["\']': ("Function构造器动态执行", "critical", "MCP07"),
    r'\b__import__\s*\(': ("Python __import__动态导入", "high", "MCP07"),
    r'\bimportlib\.import_module\s*\(': ("importlib动态导入", "medium", "MCP07"),
    r'\brequire\s*\(\s*[^\'"]': ("Node.js require动态导入", "high", "MCP07"),
    r'\bvm\.runInNewContext\s*\(': ("VM沙箱逃逸风险", "critical", "MCP07"),
    r'\bvm\.runInThisContext\s*\(': ("VM沙箱逃逸风险", "critical", "MCP07"),

    # ========== MCP06 - SSRF (服务端请求伪造) ==========
    r'\brequests\.(get|post|put|delete|patch|head)\s*\(': ("Python requests HTTP请求", "medium", "MCP06"),
    r'\bhttpx\.(get|post|put|delete|patch)\s*\(': ("httpx HTTP请求", "medium", "MCP06"),
    r'\bfetch\s*\(': ("fetch HTTP请求", "medium", "MCP06"),
    r'\baxios\.(get|post|put|delete|patch)\s*\(': ("axios HTTP请求", "medium", "MCP06"),
    r'\bhttp\.(get|post|request)\s*\(': ("Node.js http请求", "medium", "MCP06"),
    r'\bhttps\.(get|post|request)\s*\(': ("Node.js https请求", "medium", "MCP06"),
    r'\bhttpclient\s*\(': ("HTTP客户端调用", "medium", "MCP06"),
    r'\bopen_url\s*\(': ("URL打开(SSRF风险)", "high", "MCP06"),
    r'\bdownload_?file\s*\(': ("文件下载(SSRF风险)", "high", "MCP06"),
    r'\b(localhost|127\.0\.0\.1|0\.0\.0\.0|169\.254\.169\.254)': ("内网/元数据地址访问", "high", "MCP06"),
    r'\b169\.254\.169\.254': ("AWS元数据服务访问(SSRF)", "critical", "MCP06"),
    r'\bmetadata\.google\.internal': ("GCP元数据服务访问(SSRF)", "critical", "MCP06"),

    # ========== MCP04 - Data Exfiltration (数据外传) ==========
    r'\b(upload|send|post|transfer)\s+.*\b(file|data|content|document)\b.*\b(to|2|→)\s+https?://': ("数据上传到外部", "critical", "MCP04"),
    r'\b(export|exfiltrate|leak)\s+.*\b(data|file|secret|key|password)\b': ("数据外传行为", "critical", "MCP04"),
    r'\b(encode|base64|btoa|atob)\s*\(' : ("Base64编码(可能用于数据隐藏)", "low", "MCP04"),
    r'\b(jsonp|XMLHttpRequest|navigator\.sendBeacon)\b': ("隐蔽数据外传通道", "high", "MCP04"),
    r'\bDNS\s*(exfil|tunnel|over)\b': ("DNS隧道数据外传", "critical", "MCP04"),
    r'\bwebsocket\s*\(|\bnew\s+WebSocket\s*\(': ("WebSocket连接(可能用于数据外传)", "medium", "MCP04"),

    # ========== MCP01 - Prompt Injection (提示注入) ==========
    r'ignore\s+(all\s+)?(previous|prior|above)\s+(instruction|prompt|rule)': ("越狱指令: 忽略前文", "critical", "MCP01"),
    r'forget\s+(everything|all|previous|prior)': ("越狱指令: 忘记一切", "critical", "MCP01"),
    r'you\s+are\s+now\s+(a|an)\s+': ("身份切换指令", "high", "MCP01"),
    r'(disregard|ignore)\s+(the\s+)?(above|previous|prior)\s+': ("忽略前文指令", "critical", "MCP01"),
    r'\b(DAN|jailbreak|bypass|override)\b': ("越狱关键词", "critical", "MCP01"),
    r'(act|pretend|play)\s+as\s+(if\s+you\s+(are|were)\s+)?(a|an)\s+': ("角色扮演注入", "high", "MCP01"),
    r'system\s*prompt\s*[:=]': ("系统提示词暴露/覆盖", "high", "MCP01"),
    r'<!--\s*(ignore|forget|disregard)': ("HTML注释中隐藏指令", "critical", "MCP01"),
    r'<system>|<instruction>|<override>': ("伪标签注入", "critical", "MCP01"),
    r'(reveal|show|print|output)\s+(your\s+)?(system\s+)?(prompt|instruction|rule)': ("系统提示窃取", "high", "MCP01"),

    # ========== MCP02 - Tool Poisoning (工具投毒) ==========
    r'<!--.*?(ignore|exec|eval|system).*?-->': ("HTML注释中隐藏恶意指令(Tool Poisoning)", "critical", "MCP02"),
    r'/\*.*?(ignore|exec|eval|system).*?\*/': ("块注释中隐藏恶意指令(Tool Poisoning)", "critical", "MCP02"),
    r'\bhidden\s+(instruction|command|prompt)\b': ("隐藏指令(Tool Poisoning)", "critical", "MCP02"),
    r'tool_description\s*[:=]\s*["\'].*?(ignore|exec|eval|fetch)': ("工具描述中嵌入恶意指令", "critical", "MCP02"),
    r'\bdescription\s*[:=]\s*["\'][^"\']{200,}': ("异常长的工具描述(可能隐藏指令)", "medium", "MCP02"),
    r'unicode\s+escape|\\u[0-9a-fA-F]{4}.*?(ignore|exec|eval)': ("Unicode转义隐藏指令", "critical", "MCP02"),
    r'zero[\s-]?width|​|‌|‍': ("零宽字符(可能隐藏指令)", "high", "MCP02"),

    # ========== MCP03 - Rug Pull (版本篡改) ==========
    r'\bpostinstall\b.*\bexec\b': ("postinstall钩子执行命令(Rug Pull风险)", "high", "MCP03"),
    r'\bpreinstall\b.*\bexec\b': ("preinstall钩子执行命令(Rug Pull风险)", "high", "MCP03"),
    r'\bnpm\s+install\s+--force': ("强制安装(可能绕过校验)", "medium", "MCP03"),
    r'\bversion\s*[:=]\s*["\'](\*|latest|>\d)': ("使用通配符/latest版本(供应链风险)", "medium", "MCP03"),

    # ========== MCP05 - Insecure Authentication (不安全认证) ==========
    r'\b(api[_-]?key|apikey)\s*[=:]\s*["\'][^"\']{8,}["\']': ("硬编码API密钥", "critical", "MCP05"),
    r'\b(secret|password|passwd|pwd)\s*[=:]\s*["\'][^"\']{4,}["\']': ("硬编码密码", "critical", "MCP05"),
    r'\b(token|bearer|auth)\s*[=:]\s*["\'][^"\']{8,}["\']': ("硬编码Token", "critical", "MCP05"),
    r'-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----': ("私钥文件暴露", "critical", "MCP05"),
    r'(?:AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[0-9A-Z]{16}': ("AWS Access Key", "critical", "MCP05"),
    r'ghp_[0-9a-zA-Z]{36}': ("GitHub Personal Access Token", "critical", "MCP05"),
    r'gho_[0-9a-zA-Z]{36}': ("GitHub OAuth Token", "critical", "MCP05"),
    r'sk-[0-9a-zA-Z]{32,}': ("OpenAI API Key", "critical", "MCP05"),
    r'sk-ant-[0-9a-zA-Z]{40,}': ("Anthropic API Key", "critical", "MCP05"),
    r'(?:mongodb|postgres|postgresql|mysql|redis)://[^\s\'"]+:[^\s\'"]+@': ("数据库连接字符串含密码", "critical", "MCP05"),
    r'\bBasic\s+[A-Za-z0-9+/=]{16,}': ("HTTP Basic认证凭据", "high", "MCP05"),
    r'\bBearer\s+[A-Za-z0-9._-]{16,}': ("Bearer Token暴露", "high", "MCP05"),

    # ========== MCP08 - Insecure Transport (不安全传输) ==========
    r'\bhttp://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)': ("使用HTTP明文传输", "medium", "MCP08"),
    r'verify\s*=\s*False': ("SSL证书验证禁用", "critical", "MCP08"),
    r'verify\s*=\s*None': ("SSL证书验证禁用", "critical", "MCP08"),
    r'rejectUnauthorized\s*=\s*false': ("Node.js SSL验证禁用", "critical", "MCP08"),
    r'NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*[\'"]?0': ("全局SSL验证禁用", "critical", "MCP08"),
    r'\bssl\s*[:=]\s*False': ("SSL禁用", "high", "MCP08"),
    r'INSECURE\s*=\s*True': ("不安全模式", "high", "MCP08"),

    # ========== MCP09 - Overly Broad Permissions (过宽权限) ==========
    r'\bpermissions?\s*[:=]\s*["\']\*["\']': ("通配符权限(过宽)", "high", "MCP09"),
    r'\bpermissions?\s*[:=]\s*["\']all["\']': ("all权限(过宽)", "high", "MCP09"),
    r'\ballow\s*[:=]\s*["\']\*["\']': ("通配符允许", "high", "MCP09"),
    r'\bhost_permissions?\s*[:=]\s*\[\s*["\']<all_urls>["\']': ("所有URL权限", "high", "MCP09"),
    r'\bfs\.(read|write|append|unlink|rmdir|mkdir|rename|copyFile)\b': ("文件系统操作", "medium", "MCP09"),
    r'\bopen\s*\([^)]*["\'][wax]["\']': ("文件写入/追加", "medium", "MCP09"),
    r'\bos\.(remove|rename|makedirs|listdir|chdir|chmod|chown)\b': ("OS文件操作", "medium", "MCP09"),
    r'\bPath\([^)]*\)\.(write_text|write_bytes|unlink|rmdir)\b': ("Pathlib文件操作", "medium", "MCP09"),
    r'\bshutil\.(rmtree|copy|move)\b': ("shutil高危操作", "high", "MCP09"),
    r'\b(os\.environ|process\.env)\b': ("环境变量访问", "low", "MCP09"),
    r'\bprocess\.env\.(HOME|USERPATH|PATH)\b': ("系统路径访问", "medium", "MCP09"),
    r'\bchmod\s*\(\s*0?[67]?77': ("chmod 777权限", "high", "MCP09"),
    r'\bcredentials?\s*[:=]': ("凭据处理", "medium", "MCP09"),

    # ========== MCP10 - Supply Chain (供应链风险) ==========
    r'\b(npx|npm\s+exec)\s+[^|]*(?<!comment)': ("npx/npm exec执行远程包", "high", "MCP10"),
    r'\bcurl\s+.*\|\s*(bash|sh|python)': ("curl管道执行(供应链风险)", "critical", "MCP10"),
    r'\bwget\s+.*\|\s*(bash|sh|python)': ("wget管道执行(供应链风险)", "critical", "MCP10"),
    r'\beval\s*\(\s*(urlopen|requests\.get)': ("远程代码eval执行", "critical", "MCP10"),
    r'\bexec\s*\(\s*(urlopen|requests\.get)': ("远程代码exec执行", "critical", "MCP10"),
    r'\bpip\s+install\s+git\+https?://': ("从git安装包(供应链风险)", "high", "MCP10"),
    r'\bnpm\s+install\s+git\+https?://': ("从git安装npm包", "high", "MCP10"),

    # ========== 数据库操作 ==========
    r'\b(sqlite3|psycopg2|pymysql|mysql)\.(connect|cursor|execute)\b': ("数据库操作", "medium", None),
    r'\bmongodb|pymongo|MongoClient\b': ("MongoDB操作", "medium", None),
    r'\bredis\s*\.\s*(get|set|delete|hget|hset)\b': ("Redis操作", "medium", None),
    r'\b(sql|query)\s*[:=]\s*["\'].*\b(drop|delete|truncate|alter)\b': ("危险SQL操作", "high", None),
    r'\bexecute\s*\(\s*f["\']': ("f-string SQL注入风险", "high", None),
    r'\bexecute\s*\(\s*["\'].*\+\s*': ("字符串拼接SQL注入风险", "high", None),

    # ========== MCP协议特定 ==========
    r'\bmcp\s*\.\s*(tool|resource|prompt|server)\b': ("MCP协议使用", "info", None),
    r'@modelcontextprotocol/sdk': ("MCP SDK依赖", "info", None),
    r'\bMcpServer\b|FastMCP\b': ("MCP服务端实现", "info", None),
    r'\bStdioServerTransport\b': ("MCP stdio传输", "info", None),
    r'\bSSEServerTransport\b': ("MCP SSE传输", "info", None),
    r'\bStreamableHTTP\b': ("MCP HTTP传输", "info", None),

    # ========== 其他危险操作 ==========
    r'\b__reduce__|pickle\.loads?': ("Pickle反序列化(RCE风险)", "critical", "MCP07"),
    r'\byaml\.load\s*\(\s*[^)]*\)': ("yaml.load不安全反序列化", "critical", "MCP07"),
    r'\bmarshal\.loads?\s*\(': ("marshal反序列化", "high", "MCP07"),
    r'\btempfile\.mktemp\b': ("mktemp不安全(竞态条件)", "medium", None),
    r'\brandom\.random\b': ("伪随机数(不安全用途)", "low", None),
    r'\bhashlib\.(md5|sha1)\b': ("弱哈希算法", "low", None),
    r'\b(Crypto|Cryptodome)\.Cipher\.(DES|ARC4|RC4)\b': ("弱加密算法", "high", None),
    r'\bsocket\s*\.\s*socket\s*\(': ("原始socket网络操作", "medium", "MCP06"),
    r'\bctypes\.(CDLL|POINTER|cast)\b': ("ctypes FFI调用(内存安全风险)", "high", "MCP07"),
    r'\bcffi\.(FFI|dlopen)\b': ("cffi FFI调用", "high", "MCP07"),
    r'\bdeno\.(Command|run)\b': ("Deno命令执行", "high", "MCP07"),
    r'\bDeno\.run\s*\(': ("Deno.run命令执行", "high", "MCP07"),
}

# Skill/GPT/Prompt 专用规则
SKILL_RULES = {
    r'ignore.*previous.*instruction': ("越狱指令(忽略前文)", "critical", "MCP01"),
    r'forget.*everything': ("越狱指令(忘记一切)", "critical", "MCP01"),
    r'you\s+are\s+now': ("身份切换指令", "high", "MCP01"),
    r'send.*to\s+https?://': ("数据外传指令", "critical", "MCP04"),
    r'POST.*data.*to': ("数据外传(POST)", "high", "MCP04"),
    r'api[_-]?key|secret|password|token': ("敏感信息请求", "high", "MCP05"),
    r'\bDAN\b|jailbreak|bypass': ("越狱关键词", "critical", "MCP01"),
    r'(reveal|show|print).*(system|hidden|secret).*(prompt|instruction|rule)': ("系统提示窃取", "high", "MCP01"),
    r'(download|fetch|curl|wget)\s+https?://': ("从外部URL下载", "high", "MCP06"),
    r'eval\s*\(|exec\s*\(|os\.system': ("代码执行指令", "critical", "MCP07"),
    r'(write|create|delete|remove)\s+file': ("文件操作指令", "medium", "MCP09"),
    r'(access|read|send).*(contact|calendar|location|camera|microphone)': ("隐私数据访问", "high", "MCP04"),
    r'keylog|screen.?capture|record.?audio': ("监控/录制行为", "critical", "MCP04"),
    r'(encrypt|ransom|lock).*(file|data|disk)': ("勒索/加密行为", "critical", "MCP07"),
    r'(spread|propagate|infect|replicate)': ("自我传播行为", "critical", "MCP10"),
    r'(persist|autostart|launch.?agent|cron)': ("持久化/自启动", "high", "MCP09"),
    r'(elevate|privilege|sudo|root|admin).*(access|permission|escalat)': ("权限提升", "critical", "MCP09"),
    r'(disable|bypass|turn.?off).*(firewall|antivirus|security|defender)': ("安全防护禁用", "critical", "MCP09"),
}

# 危险npm包
DANGEROUS_NPM_PACKAGES = {
    "event-stream", "flatmap-stream", "ddos", "koa-session",
    "crossenv", "babel-cli-fake", "rimraf", "node-serialize",
}

# 危险PyPI包
DANGEROUS_PYPI_PACKAGES = {
    "pickle", "subprocess32", "eval", "exec", "marshal",
}

# ============================================================
# OWASP MCP Top 10 映射表
# ============================================================
OWASP_MCP_TOP10 = {
    "MCP01": {"name": "Prompt Injection", "name_cn": "提示注入", "severity": "critical"},
    "MCP02": {"name": "Tool Poisoning", "name_cn": "工具投毒", "severity": "critical"},
    "MCP03": {"name": "Rug Pull", "name_cn": "版本篡改", "severity": "high"},
    "MCP04": {"name": "Data Exfiltration", "name_cn": "数据外传", "severity": "critical"},
    "MCP05": {"name": "Insecure Authentication", "name_cn": "不安全认证", "severity": "critical"},
    "MCP06": {"name": "Server-Side Request Forgery", "name_cn": "SSRF", "severity": "high"},
    "MCP07": {"name": "Command Injection", "name_cn": "命令注入", "severity": "critical"},
    "MCP08": {"name": "Insecure Transport", "name_cn": "不安全传输", "severity": "medium"},
    "MCP09": {"name": "Overly Broad Permissions", "name_cn": "过宽权限", "severity": "medium"},
    "MCP10": {"name": "Supply Chain Risks", "name_cn": "供应链风险", "severity": "high"},
}


def get_all_rules(tool_type="mcp"):
    """获取适用于指定工具类型的所有规则"""
    rules = dict(STATIC_RULES)
    if tool_type in ("skill", "gpt", "prompt"):
        rules.update(SKILL_RULES)
    return rules


def get_rule_count(tool_type="mcp"):
    """获取规则数量"""
    return len(get_all_rules(tool_type))


def get_owasp_coverage(findings):
    """获取OWASP覆盖情况"""
    covered = set()
    for f in findings:
        cat = f.get("owasp_category")
        if cat:
            covered.add(cat)
    return {
        "covered": list(covered),
        "covered_count": len(covered),
        "total": 10,
        "categories": {k: v for k, v in OWASP_MCP_TOP10.items() if k in covered}
    }


def analyze(files, tool_type="mcp"):
    """执行增强版静态分析"""
    rules = get_all_rules(tool_type)
    findings = []
    
    for filepath, content in files.items():
        # 跳过非代码文件
        skip_exts = ['.ini', '.cfg', '.env', '.lock', '.log']
        skip_names = ['registry.yaml', 'registry.yml', 'tox.ini', '.gitignore', 'LICENSE', 'Makefile']
        if any(filepath.endswith(ext) for ext in skip_exts):
            continue
        if any(filepath.split('/')[-1] == name for name in skip_names):
            continue
        
        is_doc = filepath.endswith('.md') or filepath.endswith('.txt')
        
        for pattern, (desc, severity, owasp) in rules.items():
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            if matches:
                for m in matches[:3]:  # 每个模式最多3个匹配
                    line_num = content[:m.start()].count('\n') + 1
                    actual_severity = severity
                    if is_doc and severity in ("critical", "high"):
                        actual_severity = "low"
                    elif is_doc and severity == "medium":
                        actual_severity = "info"
                    findings.append({
                        "type": "dangerous_api",
                        "severity": actual_severity,
                        "description": desc + (" (文档示例)" if is_doc else ""),
                        "file": filepath,
                        "lines": str(line_num),
                        "evidence": m.group()[:100],
                        "owasp_category": owasp,
                    })
    
    return {
        "findings": findings,
        "total_files": len(files),
        "patterns_checked": len(rules),
        "owasp_coverage": get_owasp_coverage(findings),
    }
