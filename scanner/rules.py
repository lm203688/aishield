"""
AIShield 扫描规则 v4.0 — 严格对齐 OWASP MCP Top 10 (2025 v0.1)

OWASP MCP Top 10 (2025 v0.1) 真实映射:
  MCP01 - Improper Token & Secret Management (令牌管理不当与密钥暴露)
  MCP02 - Privilege Scope Creep Leading to Escalation (权限范围蔓延导致提权)
  MCP03 - Tool Poisoning (工具投毒)
  MCP04 - Software Supply Chain Attack & Dependency Tampering (软件供应链攻击与依赖篡改)
  MCP05 - Command Injection & Execution (命令注入与执行)
  MCP06 - Intent Flow Subversion / Prompt Injection (意图流颠覆/上下文提示注入)
  MCP07 - Insufficient Authentication & Authorization (身份认证与授权不足)
  MCP08 - Lack of Audit & Observability (审计与可观测性缺失)
  MCP09 - Shadow MCP Servers (影子MCP服务器)
  MCP10 - Context Injection & Over-Sharing (上下文注入与过度共享)

规则统计目标: 10类 × 6条 = 60+ 规则
"""

import re

# ============================================================
# OWASP MCP Top 10 真实定义 (2025 v0.1)
# ============================================================
OWASP_MCP_TOP10 = {
    "MCP01": {
        "name": "Improper Token & Secret Management",
        "name_cn": "令牌管理不当与密钥暴露",
        "severity": "critical",
        "description": "API密钥、认证令牌、数据库凭据等敏感信息硬编码或泄露"
    },
    "MCP02": {
        "name": "Privilege Scope Creep Leading to Escalation",
        "name_cn": "权限范围蔓延导致提权",
        "severity": "high",
        "description": "工具请求超出必要的权限（文件系统、网络、系统命令等）"
    },
    "MCP03": {
        "name": "Tool Poisoning",
        "name_cn": "工具投毒",
        "severity": "critical",
        "description": "工具描述中嵌入隐藏恶意指令，利用零宽字符、Unicode转义等方式"
    },
    "MCP04": {
        "name": "Software Supply Chain Attack & Dependency Tampering",
        "name_cn": "软件供应链攻击与依赖篡改",
        "severity": "high",
        "description": "恶意依赖包、npm/pypi供应链攻击、postinstall脚本恶意代码"
    },
    "MCP05": {
        "name": "Command Injection & Execution",
        "name_cn": "命令注入与执行",
        "severity": "critical",
        "description": "用户输入直接传入命令执行函数，导致远程代码执行"
    },
    "MCP06": {
        "name": "Intent Flow Subversion / Prompt Injection",
        "name_cn": "意图流颠覆/上下文提示注入",
        "severity": "high",
        "description": "通过提示注入篡改Agent意图流，绕过安全限制"
    },
    "MCP07": {
        "name": "Insufficient Authentication & Authorization",
        "name_cn": "身份认证与授权不足",
        "severity": "medium",
        "description": "MCP服务器缺少认证机制，或授权粒度过粗"
    },
    "MCP08": {
        "name": "Lack of Audit & Observability",
        "name_cn": "审计与可观测性缺失",
        "severity": "high",
        "description": "缺少日志记录、操作审计和异常检测机制"
    },
    "MCP09": {
        "name": "Shadow MCP Servers",
        "name_cn": "影子MCP服务器",
        "severity": "medium",
        "description": "未经授权的MCP服务器运行，绕过安全管控"
    },
    "MCP10": {
        "name": "Context Injection & Over-Sharing",
        "name_cn": "上下文注入与过度共享",
        "severity": "medium",
        "description": "将过多敏感上下文传递给外部工具/模型，导致数据泄露"
    },
}

# ============================================================
# MCP01 - 令牌管理不当与密钥暴露 (8条规则)
# ============================================================
MCP01_RULES = {
    # API密钥
    r'\b(api[_-]?key|apikey)\s*[=:]\s*["\'][^"\']{8,}["\']': ("硬编码API密钥", "critical"),
    r'sk-[0-9a-zA-Z]{32,}': ("OpenAI API Key泄露", "critical"),
    r'sk-ant-[0-9a-zA-Z]{40,}': ("Anthropic API Key泄露", "critical"),
    r'(?:AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[0-9A-Z]{16}': ("AWS Access Key泄露", "critical"),
    r'ghp_[0-9a-zA-Z]{36}': ("GitHub Personal Access Token泄露", "critical"),
    r'gho_[0-9a-zA-Z]{36}': ("GitHub OAuth Token泄露", "critical"),
    r'glpat-[0-9a-zA-Z\-]{20,}': ("GitLab Personal Access Token泄露", "critical"),
    # 密码/Token
    r'\b(secret|password|passwd|pwd)\s*[=:]\s*["\'][^"\']{4,}["\']': ("硬编码密码", "critical"),
    r'\b(token|bearer|auth[_-]?token)\s*[=:]\s*["\'][A-Za-z0-9._\-]{16,}["\']': ("硬编码Token", "critical"),
    # 私钥
    r'-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----': ("私钥文件暴露", "critical"),
    # 数据库连接串
    r'(?:mongodb|postgres|postgresql|mysql|redis)://[^\s\'"]+:[^\s\'"]+@': ("数据库连接字符串含密码", "critical"),
    # 其他凭证
    r'\bBasic\s+[A-Za-z0-9+/=]{16,}': ("HTTP Basic认证凭据", "high"),
    r'\bBearer\s+[A-Za-z0-9._\-]{16,}': ("Bearer Token暴露", "high"),
    r'xox[bpras]-[0-9a-zA-Z\-]{20,}': ("Slack Token泄露", "critical"),
    r'hooks\.slack\.com/services/T[A-Z0-9]{8,}/B[A-Z0-9]{8,}/[A-Za-z0-9]{20,}': ("Slack Webhook URL泄露", "high"),
    r'eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+': ("JWT Token泄露", "high"),
}

# ============================================================
# MCP02 - 权限范围蔓延导致提权 (8条规则)
# ============================================================
MCP02_RULES = {
    # 通配符权限
    r'\bpermissions?\s*[:=]\s*["\']\*["\']': ("通配符权限声明(过宽)", "high"),
    r'\bpermissions?\s*[:=]\s*["\']all["\']': ("all权限声明(过宽)", "high"),
    r'\ballow\s*[:=]\s*["\']\*["\']': ("通配符allow(过宽)", "high"),
    r'\bhost_permissions?\s*[:=]\s*\[\s*["\']<all_urls>["\']': ("所有URL权限(过宽)", "high"),
    r'\bfs\.(read|write|append|unlink|rmdir|mkdir|rename|copyFile)\b': ("完整文件系统权限", "medium"),
    r'\bos\.(remove|rename|makedirs|listdir|chdir|chmod|chown)\b': ("OS文件操作权限(过宽)", "medium"),
    r'\bPath\([^)]*\)\.(write_text|write_bytes|unlink|rmdir)\b': ("Pathlib完整操作权限", "medium"),
    r'\bshutil\.(rmtree|copy|move)\b': ("shutil高危文件操作", "high"),
    r'\bchmod\s*\(\s*0?[67]?77': ("chmod 777权限(过宽)", "high"),
    r'\b(os\.environ|process\.env)\b': ("完整环境变量访问", "low"),
    r'\bprocess\.env\.(HOME|USERPATH|PATH)\b': ("系统路径环境变量访问", "medium"),
    r'\bcredentials?\s*[:=]': ("凭据处理(需最小权限)", "medium"),
}

# ============================================================
# MCP03 - 工具投毒 (8条规则)
# ============================================================
MCP03_RULES = {
    # 零宽字符
    r'[\u200b\u200c\u200d\u2060\ufeff]': ("零宽字符(可能隐藏恶意指令)", "critical"),
    # HTML注释隐藏指令
    r'<!--.*?(ignore|exec|eval|system|fetch|forget|jailbreak|bypass).*?-->': ("HTML注释中隐藏恶意指令", "critical"),
    # 块注释隐藏指令
    r'/\*.*?(ignore|exec|eval|system|fetch).*?\*/': ("块注释中隐藏恶意指令", "critical"),
    # 工具描述嵌入指令
    r'tool_description\s*[:=]\s*["\'].*?(ignore|exec|eval|fetch|forget|bypass)': ("工具描述中嵌入恶意指令", "critical"),
    r'\bdescription\s*[:=]\s*["\'][^"\']{500,}': ("异常长的工具描述(>500字符，可能隐藏指令)", "medium"),
    # Unicode转义
    r'\\u[0-9a-fA-F]{4}.*\\u[0-9a-fA-F]{4}.*\\u[0-9a-fA-F]{4}.*(ignore|exec|eval|system)': ("Unicode转义序列隐藏指令", "critical"),
    # 隐藏指令关键词
    r'\bhidden\s+(instruction|command|prompt)\b': ("隐藏指令关键词", "critical"),
    # HTML实体编码
    r'&#\d+;.*?(ignore|exec|eval|system|fetch|forget|bypass)': ("HTML实体编码隐藏指令", "critical"),
}

# ============================================================
# MCP04 - 软件供应链攻击与依赖篡改 (8条规则)
# ============================================================
MCP04_RULES = {
    # postinstall/preinstall恶意脚本
    r'"(postinstall|preinstall|postpublish)"\s*:\s*["\'].*?(curl|wget|exec|eval|bash|sh|python|node\s+-e)': ("postinstall脚本执行外部命令", "critical"),
    r'"(postinstall|preinstall|postpublish)"\s*:\s*["\'].*?https?://': ("postinstall脚本访问网络", "high"),
    # pip install from git
    r'\bpip\s+install\s+git\+https?://': ("从git URL安装Python包(供应链风险)", "high"),
    r'\bnpm\s+install\s+git\+https?://': ("从git URL安装npm包(供应链风险)", "high"),
    # curl管道执行
    r'\bcurl\s+.*\|\s*(bash|sh|python|node)\b': ("curl管道执行(供应链攻击)", "critical"),
    r'\bwget\s+.*\|\s*(bash|sh|python|node)\b': ("wget管道执行(供应链攻击)", "critical"),
    # 远程代码执行
    r'\b(exec|eval)\s*\(\s*(urlopen|requests\.get|fetch)\b': ("远程代码eval/exec执行", "critical"),
    # npx远程执行
    r'\b(npx|npm\s+exec)\s+[^"\']*https?://': ("npx执行远程URL包", "high"),
    # 通配符版本
    r'"(dependencies|devDependencies)".*?"(\w+)"\s*:\s*["\'](\*|latest|>\s*\d)\s*["\']': ("依赖使用通配符版本(供应链风险)", "medium"),
}

# ============================================================
# MCP05 - 命令注入与执行 (8条规则)
# ============================================================
MCP05_RULES = {
    # Python
    r'\bos\.system\s*\(': ("os.system() 命令执行", "critical"),
    r'\bos\.popen\s*\(': ("os.popen() 命令执行", "critical"),
    r'\bos\.exec\s*\(': ("os.exec() 命令执行", "critical"),
    r'\bsubprocess\.(run|call|Popen|check_output|check_call)\s*\([^)]*shell\s*=\s*True': ("subprocess shell=True(极危险)", "critical"),
    r'\bsubprocess\.(run|call|Popen|check_output)\s*\(': ("subprocess命令执行", "high"),
    r'\bexec\s*\(': ("exec() 动态代码执行", "critical"),
    r'\beval\s*\(': ("eval() 动态代码执行", "critical"),
    r'\b__import__\s*\(': ("Python __import__动态导入", "high"),
    r'\bimportlib\.import_module\s*\(': ("importlib动态导入", "medium"),
    r'\bpickle\.loads?\s*\(': ("Pickle反序列化(RCE风险)", "critical"),
    r'\byaml\.load\s*\(\s*[^)]*\)': ("yaml.load不安全反序列化", "critical"),
    r'\bmarshal\.loads?\s*\(': ("marshal反序列化(RCE风险)", "high"),
    r'\bctypes\.(CDLL|POINTER|cast)\b': ("ctypes FFI调用(内存安全风险)", "high"),
    # Node.js
    r'\bchild_process\.exec\s*\(': ("Node.js child_process.exec", "high"),
    r'\bchild_process\.execSync\s*\(': ("Node.js child_process.execSync", "high"),
    r'\bchild_process\.spawn\s*\(': ("Node.js child_process.spawn", "high"),
    r'\bFunction\s*\(\s*["\']': ("Function构造器动态执行", "critical"),
    r'\bvm\.runInNewContext\s*\(': ("VM沙箱逃逸风险", "critical"),
    r'\bvm\.runInThisContext\s*\(': ("VM沙箱逃逸风险", "critical"),
    r'\brequire\s*\(\s*[^\'"]': ("Node.js require动态导入", "high"),
    # Deno
    r'\bdeno\.(Command|run)\b': ("Deno命令执行", "high"),
    # SQL注入
    r'\bexecute\s*\(\s*f["\']': ("f-string SQL注入风险", "high"),
    r'\bexecute\s*\(\s*["\'].*\+\s*': ("字符串拼接SQL注入风险", "high"),
    # 弱加密
    r'\b(Crypto|Cryptodome)\.Cipher\.(DES|ARC4|RC4)\b': ("弱加密算法", "high"),
}

# ============================================================
# MCP06 - 意图流颠覆/上下文提示注入 (8条规则)
# ============================================================
MCP06_RULES = {
    # 越狱指令
    r'ignore\s+(all\s+)?(previous|prior|above)\s+(instruction|prompt|rule|guidance)': ("越狱指令: 忽略前文指令", "critical"),
    r'forget\s+(everything|all|previous|prior|your)\s+(instruction|prompt|rule|training)': ("越狱指令: 忘记一切", "critical"),
    r'\b(DAN|jailbreak|bypass|override)\b': ("越狱关键词", "critical"),
    r'(disregard|ignore|neglect)\s+(the\s+)?(above|previous|prior|all)\s+(instruction|prompt|rule|safety)': ("忽略安全指令", "critical"),
    r'you\s+are\s+now\s+(a|an)\s+': ("身份切换指令", "high"),
    r'(act|pretend|play|roleplay)\s+as\s+(if\s+you\s+(are|were)\s+)?(a|an)\s+': ("角色扮演注入", "high"),
    # 系统提示窃取
    r'(reveal|show|print|output|display)\s+(your\s+)?(system\s+)?(prompt|instruction|rule|guidance)': ("系统提示窃取", "high"),
    r'system\s*prompt\s*[:=]': ("系统提示词暴露/覆盖", "high"),
    # 伪标签注入
    r'<system>|<instruction>|<override>|<admin>': ("伪XML标签注入", "critical"),
    # 数据外传指令
    r'(send|upload|exfiltrate|transmit|post)\s+.*\b(data|content|file|secret|key|password|token)\b.*\b(to|2|→)\s+https?://': ("数据外传指令", "critical"),
    # 隐蔽通道
    r'(download|fetch|curl|wget)\s+https?://[^\s]*\.(py|js|sh|bash|exe|ps1)': ("从外部下载可执行文件", "high"),
    # 监控/录制
    r'\bkeylog|screen.?capture|record.?audio|webcam.?access': ("监控/录制行为", "critical"),
    # 持久化
    r'(persist|autostart|launch.?agent|cron|systemd)\b': ("持久化/自启动指令", "high"),
    # 安全防护禁用
    r'(disable|bypass|turn.?off)\s+(firewall|antivirus|security|defender|protection)': ("安全防护禁用指令", "critical"),
}

# ============================================================
# MCP07 - 身份认证与授权不足 (6条规则)
# ============================================================
MCP07_RULES = {
    # 无认证的敏感端点
    r'(app\.(get|post|put|delete|route)|router\.(get|post|put|delete))\s*\(\s*["\']/(admin|config|settings|users|tokens|keys)': ("敏感管理端点无认证装饰器", "high"),
    r'@app\.route.*admin.*': ("管理路由可能缺少认证", "medium"),
    # SSL/TLS问题
    r'verify\s*=\s*False': ("SSL证书验证禁用", "critical"),
    r'verify\s*=\s*None': ("SSL证书验证禁用", "critical"),
    r'rejectUnauthorized\s*=\s*false': ("Node.js SSL验证禁用", "critical"),
    r'NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*[\'"]?0': ("全局SSL验证禁用", "critical"),
    r'INSECURE\s*=\s*True': ("不安全模式启用", "high"),
    # CORS通配
    r'(Access-Control-Allow-Origin|cors)\s*[:=]\s*["\']?\*["\']?': ("CORS设置为通配符(无跨域限制)", "high"),
}

# ============================================================
# MCP08 - 审计与可观测性缺失 (6条规则)
# ============================================================
MCP08_RULES = {
    # 无日志记录的敏感操作 — 通过检测缺少logging模式来间接发现
    r'\b(exec|eval|system|subprocess|child_process)\s*\(': ("命令执行操作(需验证是否有日志)", "medium"),
    # 缺少错误处理的网络请求
    r'\b(requests\.(get|post)|fetch|axios\.(get|post))\s*\([^)]*\)\s*;?\s*$': ("网络请求无错误处理(可能缺少审计)", "low"),
    # 静默异常
    r'except(\s*:)?:?\s*pass\s*$': ("静默异常处理(吞掉错误，影响审计)", "medium"),
    r'except\s+Exception\s*:\s*pass': ("裸异常捕获并忽略", "high"),
    r'\bprint\s*\(': ("使用print而非logging(缺少结构化审计)", "info"),
    r'console\.log\s*\(': ("使用console.log而非结构化日志", "info"),
}

# ============================================================
# MCP09 - 影子MCP服务器 (6条规则)
# ============================================================
MCP09_RULES = {
    # 动态MCP服务器配置
    r'mcpServers\s*[=:]\s*\{': ("MCP服务器配置(检查是否为影子服务器)", "info"),
    r'"command"\s*:\s*["\'].*?(npx|npm|node|python)\b': ("通过npx/npm/node/python启动MCP服务器", "medium"),
    r'"url"\s*:\s*["\']https?://': ("远程MCP服务器URL配置", "medium"),
    # 动态添加服务器
    r'addServer|registerServer|addMcpServer|mcp\.connect': ("动态注册MCP服务器(可能为影子)", "medium"),
    # 非标准端口
    r':\d{4,5}\b': ("非标准端口服务(检查是否为未授权MCP)", "low"),
    # stdio传输的外部进程
    r'StdioServerTransport\s*\(\s*\w+\.\s*(spawn|exec|Popen)': ("MCP stdio传输启动外部进程", "medium"),
}

# ============================================================
# MCP10 - 上下文注入与过度共享 (6条规则)
# ============================================================
MCP10_RULES = {
    # SSRF
    r'\b(requests|httpx|axios|fetch|http\.|https\.)\s*\(\s*["\']?\s*(http|https)://': ("HTTP请求(检查目标是否为内部服务)", "medium"),
    r'\b(localhost|127\.0\.0\.1|0\.0\.0\.0|169\.254\.169\.254)\b': ("内网/元数据地址访问(SSRF)", "critical"),
    r'\bmetadata\.google\.internal\b': ("GCP元数据服务访问(SSRF)", "critical"),
    r'\b100\.64\.\d+\.\d+\b': ("CGNAT内部地址访问(SSRF)", "high"),
    # 过度数据共享
    r'\bcontext_window|context_length|max_tokens\s*[:=]\s*\d{4,}': ("大上下文窗口(注意过度共享)", "info"),
    # WebSocket持久连接
    r'\b(new\s+)?WebSocket\s*\(': ("WebSocket连接(可能用于数据外泄)", "medium"),
    # DNS隧道
    r'\bDNS\s*(exfil|tunnel|over)\b': ("DNS隧道数据外传", "critical"),
}

# ============================================================
# Skill/GPT/Prompt 专用额外规则
# ============================================================
SKILL_EXTRA_RULES = {
    r'(write|create|delete|remove)\s+file': ("文件操作指令", "medium"),
    r'(access|read|send).*(contact|calendar|location|camera|microphone)': ("隐私数据访问指令", "high"),
    r'(encrypt|ransom|lock).*(file|data|disk)': ("勒索/加密行为", "critical"),
    r'(spread|propagate|infect|replicate)\b': ("自我传播行为", "critical"),
    r'(elevate|privilege|sudo|root|admin).*(access|permission|escalat)': ("权限提升指令", "critical"),
    r'api[_-]?key|secret[_-]?key|access_token': ("敏感凭证请求", "high"),
}

# ============================================================
# 中文Prompt注入检测规则 (中国市场核心差异化)
# ============================================================
ZH_PROMPT_INJECTION_RULES = {
    # 越狱指令（中文）
    r'忽略.{0,4}(之前|上面|所有|前文).{0,6}(指令|提示|规则|要求|限制)': ("中文越狱: 忽略前文指令", "critical"),
    r'忘记.{0,4}(所有|一切|之前|以前).{0,6}(指令|规则|设定|限制)': ("中文越狱: 忘记一切", "critical"),
    r'不要.{0,4}(遵守|遵循|执行).{0,6}(规则|指令|限制|要求)': ("中文越狱: 不遵守规则", "critical"),
    r'你(现在|现在起|从现在).{0,4}(是|变成|作为).{0,10}(没有|无).{0,4}(限制|约束|禁忌)': ("中文越狱: 取消所有限制", "critical"),
    r'无视.{0,4}(安全|系统|之前).{0,6}(规则|指令|设定|要求)': ("中文越狱: 无视安全规则", "critical"),
    r'跳过.{0,4}(安全|审核|检查|验证|限制)': ("中文越狱: 跳过安全检查", "critical"),
    r'突破.{0,4}(限制|约束|封锁|审查)': ("中文越狱: 突破限制", "high"),
    r'绕过.{0,4}(安全|过滤|审查|限制|防火墙)': ("中文越狱: 绕过安全", "high"),
    r'解除.{0,4}(限制|约束|封锁|锁定)': ("中文越狱: 解除限制", "high"),
    r'取消.{0,4}(所有|一切|安全).{0,4}(限制|规则|约束)': ("中文越狱: 取消限制", "critical"),
    # 关键词越狱（中英混合）
    r'DAN(模式)?': ("DAN越狱模式", "critical"),
    r'(越狱|jailbreak|越狱模式)': ("越狱关键词", "critical"),
    # 身份切换
    r'(扮演|假装|假设|当作).{0,6}(你是|作为).{0,10}(一个|一名)': ("中文角色扮演注入", "high"),
    r'你(现在|现在起).{0,4}(是|变成).{0,6}(一个|一名|一位)': ("中文身份切换", "high"),
    # 系统提示窃取
    r'(输出|显示|打印|告诉我|复述).{0,6}(你的|系统|原始).{0,6}(提示|指令|规则|prompt)': ("中文系统提示窃取", "high"),
    r'(重复|复述|输出).{0,4}(上面|之前|你的).{0,6}(内容|指令|设定)': ("中文重复前文指令", "high"),
    # 数据外传
    r'(发送|上传|传输|提交|泄露).{0,6}(数据|信息|内容|文件|密钥|密码).{0,4}(到|至|给)': ("中文数据外传指令", "critical"),
    r'(访问|获取|读取).{0,6}(用户|系统|配置|环境).{0,6}(数据|信息|文件|变量)': ("中文敏感数据访问", "high"),
    # 持久化/后门
    r'(添加|写入|创建).{0,4}(自启动|定时任务|持久化|后门|守护进程)': ("中文持久化/后门指令", "critical"),
    # 安全防护禁用
    r'(关闭|禁用|停用|关闭).{0,4}(防火墙|杀毒|安全|防护|监控|日志)': ("中文安全防护禁用", "critical"),
    # 伪造指令
    r'(?<![a-zA-Z])系统指令[：:]\s*(?:忽略|跳过|不要|停止)': ("中文伪造系统指令", "critical"),
    r'\[系统\].*?(忽略|跳过|不要|停止|取消)': ("中文伪系统消息", "critical"),
    r'【.{0,4}系统.{0,4}】.*?(忽略|跳过|不要|停止)': ("中文伪系统标签", "critical"),
}

# ============================================================
# 合并所有规则
# ============================================================
ALL_RULES = {}
ALL_RULES.update(MCP01_RULES)
ALL_RULES.update(MCP02_RULES)
ALL_RULES.update(MCP03_RULES)
ALL_RULES.update(MCP04_RULES)
ALL_RULES.update(MCP05_RULES)
ALL_RULES.update(MCP06_RULES)
ALL_RULES.update(MCP07_RULES)
ALL_RULES.update(MCP08_RULES)
ALL_RULES.update(MCP09_RULES)
ALL_RULES.update(MCP10_RULES)
ALL_RULES.update(ZH_PROMPT_INJECTION_RULES)

# 危险npm包（已知恶意）
DANGEROUS_NPM_PACKAGES = {
    "event-stream", "flatmap-stream", "ddos", "koa-session",
    "crossenv", "babel-cli-fake", "node-serialize",
}

# 危险PyPI包
DANGEROUS_PYPI_PACKAGES = {
    "pickle", "subprocess32",
}

# 跳过的文件（非代码）
SKIP_EXTENSIONS = {'.ini', '.cfg', '.env', '.lock', '.log', '.svg', '.png', '.jpg'}
SKIP_NAMES = {'registry.yaml', 'registry.yml', 'tox.ini', '.gitignore', 'LICENSE', 'Makefile'}


def get_all_rules(tool_type="mcp"):
    """获取适用于指定工具类型的所有规则"""
    rules = dict(ALL_RULES)
    if tool_type in ("skill", "gpt", "prompt"):
        rules.update(SKILL_EXTRA_RULES)
    return rules


def get_rule_count(tool_type="mcp"):
    """获取规则数量"""
    return len(get_all_rules(tool_type))


def get_owasp_category_rules(category):
    """获取指定OWASP类别的规则数量"""
    mapping = {
        "MCP01": MCP01_RULES, "MCP02": MCP02_RULES, "MCP03": MCP03_RULES,
        "MCP04": MCP04_RULES, "MCP05": MCP05_RULES, "MCP06": MCP06_RULES,
        "MCP07": MCP07_RULES, "MCP08": MCP08_RULES, "MCP09": MCP09_RULES,
        "MCP10": MCP10_RULES,
    }
    return len(mapping.get(category, {}))


def get_owasp_coverage(findings):
    """计算OWASP MCP Top 10覆盖情况"""
    covered = set()
    for f in findings:
        cat = f.get("owasp_category")
        if cat:
            covered.add(cat)
    categories_detail = {}
    for cat in covered:
        info = OWASP_MCP_TOP10.get(cat, {})
        categories_detail[cat] = {
            "name": info.get("name", cat),
            "name_cn": info.get("name_cn", cat),
            "rules_triggered": len([f for f in findings if f.get("owasp_category") == cat]),
            "total_rules": get_owasp_category_rules(cat),
        }
    return {
        "covered": sorted(covered),
        "covered_count": len(covered),
        "total": 10,
        "coverage_percent": len(covered) * 10,
        "categories": categories_detail,
    }


def analyze(files, tool_type="mcp"):
    """执行静态分析，返回findings和OWASP覆盖"""
    rules = get_all_rules(tool_type)
    findings = []

    for filepath, content in files.items():
        # 跳过非代码文件
        if any(filepath.endswith(ext) for ext in SKIP_EXTENSIONS):
            continue
        if any(filepath.split('/')[-1] == name for name in SKIP_NAMES):
            continue

        is_doc = filepath.endswith('.md') or filepath.endswith('.txt')

        for pattern, (desc, severity) in rules.items():
            try:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
            except re.error:
                continue
            if matches:
                # 确定OWASP类别
                owasp_cat = _get_owasp_category(pattern)
                for m in matches[:3]:  # 每模式最多3个匹配
                    line_num = content[:m.start()].count('\n') + 1
                    actual_severity = severity
                    if is_doc and severity in ("critical", "high"):
                        actual_severity = "low"
                    elif is_doc and severity == "medium":
                        actual_severity = "info"
                    findings.append({
                        "type": "dangerous_pattern",
                        "severity": actual_severity,
                        "description": desc + (" (文档示例)" if is_doc else ""),
                        "file": filepath,
                        "lines": str(line_num),
                        "evidence": m.group()[:120],
                        "owasp_category": owasp_cat,
                    })

    return {
        "findings": findings,
        "total_files": len(files),
        "patterns_checked": len(rules),
        "owasp_coverage": get_owasp_coverage(findings),
    }


def _get_owasp_category(pattern):
    """根据pattern所属的规则集确定OWASP类别"""
    if pattern in MCP01_RULES: return "MCP01"
    if pattern in MCP02_RULES: return "MCP02"
    if pattern in MCP03_RULES: return "MCP03"
    if pattern in MCP04_RULES: return "MCP04"
    if pattern in MCP05_RULES: return "MCP05"
    if pattern in MCP06_RULES: return "MCP06"
    if pattern in MCP07_RULES: return "MCP07"
    if pattern in MCP08_RULES: return "MCP08"
    if pattern in MCP09_RULES: return "MCP09"
    if pattern in MCP10_RULES: return "MCP10"
    return None