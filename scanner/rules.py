"""
AIShield 扫描规则 v4.2 — 双维对齐 OWASP MCP Top 10 (2025 v0.1) + OWASP Agentic AI Top 10 (2025)

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

规则统计目标: MCP 10类 × 6条 + Agentic(AIS) 10类 × 6条 = 120+ 规则
"""

import json
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
# OWASP Agentic AI Top 10 (2025) 真实映射
# 与 MCP Top 10 并列，构成 "MCP + Agentic" 双维检测体系
# ============================================================
OWASP_AGENTIC_AI_TOP10 = {
    "ASI01": {
        "name": "Goal and Instruction Manipulation",
        "name_cn": "目标与指令操纵",
        "severity": "critical",
        "description": "通过提示注入或上下文操纵篡改Agent的目标、计划与决策边界"
    },
    "ASI02": {
        "name": "Tool Misuse",
        "name_cn": "工具滥用",
        "severity": "critical",
        "description": "Agent调用工具超出授权范围或用于恶意目的(邮件/支付/文件系统)"
    },
    "ASI03": {
        "name": "Excessive Agency",
        "name_cn": "过度代理",
        "severity": "high",
        "description": "Agent拥有超出必要的最小权限，或在无人值守下自动执行高危操作"
    },
    "ASI04": {
        "name": "Memory Manipulation",
        "name_cn": "记忆操纵与投毒",
        "severity": "high",
        "description": "对共享记忆/知识库/RAG的读写缺乏校验，导致记忆投毒与跨会话污染"
    },
    "ASI05": {
        "name": "Agent Identity and Trust",
        "name_cn": "智能体身份与信任",
        "severity": "high",
        "description": "Agent间缺乏身份认证与信任锚定，可被伪造身份或冒名调用"
    },
    "ASI06": {
        "name": "Agent Communication and Supply Chain",
        "name_cn": "智能体通信与供应链",
        "severity": "high",
        "description": "接入未验证的MCP/A2A服务器或第三方工具，形成供应链攻击面"
    },
    "ASI07": {
        "name": "Unbounded Resource Consumption",
        "name_cn": "无限制资源消耗",
        "severity": "medium",
        "description": "缺少迭代、Token、并发与超时上限，导致失控的成本与拒绝服务"
    },
    "ASI08": {
        "name": "Observability and Monitoring Gaps",
        "name_cn": "可观测性与监控缺口",
        "severity": "medium",
        "description": "缺少Agent行为追踪、决策审计与异常告警，攻击不可见"
    },
    "ASI09": {
        "name": "Cascading Failures & Multi-Agent Risks",
        "name_cn": "级联失败与多智能体风险",
        "severity": "high",
        "description": "多Agent委派/编排缺乏熔断与共识校验，单点故障级联放大"
    },
    "ASI10": {
        "name": "Rogue Agent & Human-Autonomy Boundary",
        "name_cn": "流氓智能体与人-机自治边界",
        "severity": "critical",
        "description": "Agent可自我修改、绕过人类确认边界或缺少终止开关"
    },
}

# ============================================================
# ASI01 - 目标与指令操纵 (6条规则)
# ============================================================
ASI01_RULES = {
    r'\b(goal|objective|task)\s*[:=]\s*["\'].*?(ignore|override|bypass|redefine|change)\b': ("目标/指令被运行时重定义", "critical"),
    r'(redefine|rewrite|change)\s+(your\s+)?(goal|objective|system\s+prompt)': ("运行时改写系统目标或提示", "critical"),
    r'<goal>.*?</goal>': ("可外部注入的目标标签", "high"),
    r'\b(plan|replan|strategy)\s*[:=]\s*["\'].*?(without|skip).{0,20}(validation|approval|check)': ("计划生成跳过校验", "high"),
    r'instruction_override\s*[:=]': ("指令覆盖参数", "critical"),
    r'prompt_injection_protection\s*[:=]\s*(false|off|disabled|0)': ("提示注入防护被显式关闭", "high"),
}

# ============================================================
# ASI02 - 工具滥用 (6条规则)
# ============================================================
ASI02_RULES = {
    r'allowed_tools\s*[:=]\s*["\']\*["\']': ("工具白名单通配符(可被滥用)", "critical"),
    r'\b(tools|functions)\s*[:=]\s*(all|["\']\*["\'])': ("工具集声明为全部", "high"),
    r'allowed_functions\s*[:=]\s*\[\s*\]': ("空工具限制(等同于全开)", "high"),
    r'\b(send_email|send_mail|smtp)\b.*\b(agent|auto|without|no_?approval)': ("Agent自动发送邮件无确认", "critical"),
    r'(transfer|send|withdraw)\s*(money|fund|payment).{0,20}(agent|auto|without|no_?approval)': ("Agent自动转账/支付无确认", "critical"),
    r'\bautonomous.{0,20}(file|delete|remove|rm)\b': ("Agent自主删除文件", "high"),
}

# ============================================================
# ASI03 - 过度代理 (6条规则)
# ============================================================
ASI03_RULES = {
    r'(auto_approve|autoapprove|auto_accept)\s*[:=]\s*(true|1|on|yes)': ("自动批准已启用(无人值守)", "critical"),
    r'(human_in_the_loop|require_approval|human_approval)\s*[:=]\s*(false|0|off|no)': ("关闭人类确认环", "critical"),
    r'(dangerously|disable.{0,8}guardrail|disable.{0,8}safety)\b': ("显式关闭安全护栏", "critical"),
    r'\bautonomous_mode\s*[:=]\s*(true|1|on)': ("自主模式无检查点", "high"),
    r'(no|without).{0,20}(confirmation|approval|checkpoint)': ("缺少确认/检查点", "high"),
    r'permissions\s*[:=]\s*["\']?write["\']?': ("授予写权限(最小权限违反)", "medium"),
}

# ============================================================
# ASI04 - 记忆操纵与投毒 (6条规则)
# ============================================================
ASI04_RULES = {
    r'(memory|vector_db|knowledge_base|rag)\s*\.\s*(upsert|insert|add|write|store)\s*\(': ("向记忆/知识库写入(需校验来源)", "high"),
    r'\b(append|update)\s*(conversation|chat|episodic)\s*_?memory\b': ("更新会话记忆无来源校验", "high"),
    r'(documents?|corpus|dataset|knowledge_base)\s*\.\s*(insert|upsert|add)\s*\(': ("向语料插入内容(RAG投毒风险)", "critical"),
    r'(memory|context)\s*(shared|global|persistent)\b': ("共享/持久记忆(跨会话污染风险)", "medium"),
    r'(sanitize|validate|escape)\s*\(\s*\)\s*#\s*(no|todo|fixme|skip)': ("记忆写入缺少净化(占位未实现)", "high"),
    r'\bmemories?\.(set|put|write)\s*\(': ("记忆存储写入", "medium"),
}

# ============================================================
# ASI05 - 智能体身份与信任 (6条规则)
# ============================================================
ASI05_RULES = {
    r'(agent_card|agent-card|\.well-known/agent\.json)\b.*(skip|ignore|not.?verify|no_?verify)': ("Agent Card未验证", "critical"),
    r'(verify_agent|verify_identity|authenticate_agent)\s*[:=]\s*(false|0|off|no|null)': ("Agent身份认证被关闭", "critical"),
    r'(trust_all_agents|trust_all|allow_anonymous_agent)\b': ("信任所有Agent(无身份校验)", "critical"),
    r'(unsigned|unverified)\s*(agent|message|request)\b': ("接受未签名Agent消息", "high"),
    r'(mTLS|mutual_tls|client_cert)\s*[:=]\s*(false|off|disabled|null)': ("Agent间mTLS禁用", "high"),
    r'(spiffe|spire|oidc|oauth)\s+(for|to)\s+agent\b': ("Agent身份应使用标准协议(检查配置)", "info"),
}

# ============================================================
# ASI06 - 智能体通信与供应链 (6条规则)
# ============================================================
ASI06_RULES = {
    r'mcpServers\s*[=:]\s*\{[^}]*"(url|command)"\s*:\s*["\']https?://[^"\']*(?:169\.254|10\.|192\.168|172\.)': ("MCP服务器指向内网(供应链/SSRF)", "critical"),
    r'(a2a_endpoint|a2a_url|agent_endpoint)\s*[:=]\s*["\']https?://': ("远程Agent通信端点(需验证)", "medium"),
    r'(trust|verify|pin)\s*[:=]\s*(false|off)\s*.*(server|tool|agent|dependency)': ("未验证的服务器/依赖信任", "high"),
    r'(install|load|import)\s+(mcp|skill|plugin|tool)\s+from\s+https?://': ("从远程加载工具/插件(供应链)", "high"),
    r'(checksum|signature|integrity)\s*[:=]\s*(null|""|false|none)': ("缺少完整性校验(供应链)", "high"),
    r'(pin|lock).{0,20}(version|dependency|tool)\b': ("建议锁定依赖版本(检查)", "info"),
}

# ============================================================
# ASI07 - 无限制资源消耗 (6条规则)
# ============================================================
ASI07_RULES = {
    r'(max_iterations|max_steps|max_turns)\s*[:=]\s*(null|0|inf|None|-1)': ("迭代次数无上限", "high"),
    r'(max_tokens|token_limit|context_limit)\s*[:=]\s*(null|0|None|inf)': ("Token上限缺失", "high"),
    r'(concurrency|max_concurrent|parallel)\s*[:=]\s*(null|0|inf|None|-1|"unlimited")': ("并发数无限制", "high"),
    r'(timeout|deadline|ttl)\s*[:=]\s*(null|0|None|inf)': ("超时缺失(可能挂起)", "medium"),
    r'while\s*\(?\s*true|for\s*\(;;\)': ("无限循环风险", "high"),
    r'(no|without).{0,20}(rate.?limit|throttl|cost_?budget)': ("缺少速率/预算限制", "medium"),
}

# ============================================================
# ASI08 - 可观测性与监控缺口 (6条规则)
# ============================================================
ASI08_RULES = {
    r'(trace|tracing|langsmith|otel|opentelemetry)\s*[:=]\s*(false|off|disabled|null)': ("追踪被禁用(不可观测)", "high"),
    r'(audit_log|audit_logs|action_log)\s*[:=]\s*(false|off|null|"")': ("Agent操作审计日志缺失", "critical"),
    r'(monitor|alert|anomaly_detection)\s*[:=]\s*(false|off|null)': ("异常监控关闭", "high"),
    r'(log|logging)\s*[:=]\s*(false|off|null|disabled)': ("日志被禁用", "medium"),
    r'#\s*(todo|fixme|xxx).{0,20}(log|trace|monitor|audit)': ("可观测性待实现(占位)", "medium"),
    r'(decision|tool_call|reasoning)\s*[:=]\s*["\'].*?(no|without).{0,20}(log|record)': ("决策/工具调用未记录", "high"),
}

# ============================================================
# ASI09 - 级联失败与多智能体风险 (6条规则)
# ============================================================
ASI09_RULES = {
    r'(delegates_to|delegate_to|spawn_agent|sub_agent|subagent)\b': ("Agent委派(需熔断/共识)", "medium"),
    r'(retry|retries)\s*[:=]\s*(inf|infinite|null|-1|0)': ("无限重试(级联放大)", "high"),
    r'(circuit_breaker|fallback|backoff)\s*[:=]\s*(false|off|null|none)': ("缺少熔断/降级(级联风险)", "high"),
    r'(consensus|vote|quorum|approval)\s*[:=]\s*(none|false|"")': ("多Agent无共识校验", "high"),
    r'(cascade|propagate|fan.?out)\s*[:=]\s*(true|on)': ("级联传播启用无隔离", "medium"),
    r'(shared_state|global_state|blackboard)\s*[:=]': ("共享状态(多Agent竞态风险)", "medium"),
}

# ============================================================
# ASI10 - 流氓智能体与人-机自治边界 (6条规则)
# ============================================================
ASI10_RULES = {
    r'(self_modif|self_modify|update.{0,12}own.{0,12}(code|weights|prompt|config))': ("Agent可自我修改", "critical"),
    r'(kill_switch|stop_signal|halt)\s*[:=]\s*(false|off|null|none|"")': ("终止开关缺失", "critical"),
    r'(execute|run|eval)\s*\(?\s*(arbitrary|dynamic|user.{0,8}provided|runtime)': ("执行任意/动态代码(失控)", "critical"),
    r'(human|user).{0,20}(override|veto|approval)\s*[:=]\s*(false|off|null|none)': ("人类否决权被关闭", "critical"),
    r'(autonomous|unattended|no.?human).{0,20}(deploy|execute|act)\b': ("无人值守自主执行", "high"),
    r'(guardrail|safety_check|policy_check)\s*[:=]\s*(bypass|skip|false|off)': ("护栏被绕过", "critical"),
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
ALL_RULES.update(ASI01_RULES)
ALL_RULES.update(ASI02_RULES)
ALL_RULES.update(ASI03_RULES)
ALL_RULES.update(ASI04_RULES)
ALL_RULES.update(ASI05_RULES)
ALL_RULES.update(ASI06_RULES)
ALL_RULES.update(ASI07_RULES)
ALL_RULES.update(ASI08_RULES)
ALL_RULES.update(ASI09_RULES)
ALL_RULES.update(ASI10_RULES)
ALL_RULES.update(ZH_PROMPT_INJECTION_RULES)

# ============================================================
# 情报驱动的动态规则（数据飞轮闭环的最后一齿）
# ============================================================
# 此前情报库只进不出：采集的漏洞从未转化为检测能力，扫描规则常年不变。
# 现由 scripts/intel_to_rules.py 从 OSV / NVD / GitHub Advisory 权威情报
# 自动生成规则，在此载入合并 —— 情报每更新一次，检测能力同步增强一次。
GENERATED_RULES = {}
GENERATED_PACKAGE_BLACKLIST = {}
_GENERATED_META = {}


def _load_generated_rules():
    """载入 data/generated_rules.json。文件缺失或损坏时静默降级，不影响基础规则。"""
    global GENERATED_RULES, GENERATED_PACKAGE_BLACKLIST, _GENERATED_META
    import json as _json
    import os as _os

    path = _os.path.join(
        _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
        "data", "generated_rules.json",
    )
    if not _os.path.exists(path):
        return
    try:
        with open(path, encoding="utf-8") as f:
            data = _json.load(f)
    except Exception:
        return

    for pattern, meta in (data.get("pattern_rules") or {}).items():
        GENERATED_RULES[pattern] = (
            f"[情报驱动] {meta.get('description', '')}",
            meta.get("severity", "medium"),
        )
    GENERATED_PACKAGE_BLACKLIST = data.get("package_blacklist") or {}
    _GENERATED_META = {
        "generated_at": data.get("generated_at"),
        "source_intel_count": data.get("source_intel_count", 0),
        "total_rules": data.get("total_rules", 0),
        "owasp_distribution": data.get("owasp_distribution", {}),
    }


_load_generated_rules()
ALL_RULES.update(GENERATED_RULES)


def get_generated_rules_meta():
    """返回情报驱动规则的元信息，供报告与元监控展示规则库新鲜度。"""
    return dict(_GENERATED_META)


# ============================================================
# 雷达晋升规则（Tech Radar 闭环的最后一齿）
# ============================================================
# scripts/tech_radar.py 每日扫描 AI Agent 生态的新攻击手法，起草规则候选到
# scanner/_proposed/；scripts/promote_rule.py 校验（正则可编译 + 良性语料零
# 误报 + 去重）后写入 data/radar_rules.json，在此载入合并。
#
# 刻意与 generated_rules.json 分开存放：后者由 intel_to_rules.py 整体重写，
# 混在一起会让雷达晋升的规则在下一次情报刷新时被静默抹掉。
RADAR_RULES = {}
_RADAR_META = {}


def _load_radar_rules():
    """载入 data/radar_rules.json。文件缺失或损坏时静默降级，不影响基础规则。"""
    global RADAR_RULES, _RADAR_META
    import json as _json
    import os as _os

    path = _os.path.join(
        _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
        "data", "radar_rules.json",
    )
    if not _os.path.exists(path):
        return
    try:
        with open(path, encoding="utf-8") as f:
            data = _json.load(f)
    except Exception:
        return

    for pattern, meta in (data.get("rules") or {}).items():
        try:
            desc, severity = meta[0], meta[1]
        except (TypeError, IndexError, KeyError):
            continue
        RADAR_RULES[pattern] = (f"[雷达] {desc}", severity)

    _RADAR_META = {
        "total_rules": len(RADAR_RULES),
        "provenance": data.get("provenance", {}),
    }


_load_radar_rules()
ALL_RULES.update(RADAR_RULES)


def get_radar_rules_meta():
    """返回雷达晋升规则的元信息（含每条规则的情报溯源）。"""
    return dict(_RADAR_META)


# 危险npm包（已知恶意）
DANGEROUS_NPM_PACKAGES = {
    "event-stream", "flatmap-stream", "ddos", "koa-session",
    "crossenv", "babel-cli-fake", "node-serialize",
}

# 危险PyPI包
DANGEROUS_PYPI_PACKAGES = {
    "pickle", "subprocess32",
}

# 由权威漏洞情报自动扩充的高危包名单（随情报库同步增长）
for _key, _entry in GENERATED_PACKAGE_BLACKLIST.items():
    _eco = (_entry.get("ecosystem") or "").lower()
    _name = _entry.get("package")
    if not _name:
        continue
    if _eco in ("npm", "node"):
        DANGEROUS_NPM_PACKAGES.add(_name)
    elif _eco in ("pypi", "pip", "python"):
        DANGEROUS_PYPI_PACKAGES.add(_name)

# ============================================================
# 离线「幻觉包 / 投毒依赖」检测（typosquat + 仿冒 + 形近字符）
# 对标 agent-security-scanner-mcp 的 hallucination-package detection。
# 纯本地、零依赖、不联网；联网校验作为可选远程项（见 engine 的 LLM 供应链分析）。
# ============================================================

# 可信包名录（常见 npm / PyPI 官方包，用于编辑距离比对 + 跨注册表混淆判定）
NPM_PACKAGE_CATALOG = {
    "express", "lodash", "react", "react-dom", "vue", "axios", "request",
    "chalk", "commander", "fs-extra", "dotenv", "jsonwebtoken", "bcrypt",
    "webpack", "babel", "eslint", "prettier", "mongoose", "sequelize",
    "socket.io", "moment", "underscore", "async", "body-parser", "cors",
    "node-fetch", "express-validator", "helmet", "passport", "socketio",
    "typescript", "tslib", "rimraf", "glob", "minimist", "yargs", "debug",
    "chai", "mocha", "jest", "npm", "yarn", "pnpm", "@modelcontextprotocol/sdk",
    # 高频合法复合名（避免复合式幻觉启发式误报）
    "react-router", "react-router-dom", "react-redux", "react-scripts",
    "react-native", "react-hook-form", "react-query", "react-codemod",
    "jscodeshift", "vue-router", "styled-components", "date-fns",
    "cross-env", "ts-node", "ts-jest", "eslint-config-prettier",
    "eslint-plugin-react", "babel-loader", "css-loader", "style-loader",
    "html-webpack-plugin", "node-cron", "next", "nuxt", "vite", "rollup",
    "esbuild", "zod", "redux", "redux-thunk", "graphql", "apollo-server",
}

PYPI_PACKAGE_CATALOG = {
    "numpy", "pandas", "flask", "django", "requests", "sqlalchemy",
    "pytest", "setuptools", "click", "jinja2", "fastapi", "uvicorn",
    "scipy", "matplotlib", "scikit-learn", "tensorflow", "torch", "pytorch",
    "openai", "anthropic", "langchain", "pypdf", "pillow", "boto3",
    "pydantic", "httpx", "aiohttp", "beautifulsoup4", "lxml", "cryptography",
    "python-dotenv", "six", "certifi", "urllib3", "idna", "charset-normalizer",
    "rich", "typer", "structlog", "loguru", "mcp", "pymupdf",
    # 高频合法复合名
    "langchain-core", "langchain-community", "langchain-openai",
    "langchain-anthropic", "llama-index", "sentence-transformers",
    "huggingface-hub", "python-multipart", "python-dateutil", "types-requests",
    "google-cloud-storage", "azure-identity", "openai-agents", "mcp-server",
    "pytest-asyncio", "pytest-cov", "flask-cors", "flask-sqlalchemy",
    "django-rest-framework", "djangorestframework", "opentelemetry-api",
}

# 向后兼容：并集
LEGIT_PACKAGE_CATALOG = NPM_PACKAGE_CATALOG | PYPI_PACKAGE_CATALOG


def _levenshtein(a, b):
    """标准编辑距离（本地、零依赖）。"""
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost))
        prev = cur
    return prev[lb]


# 形近字符归一化（防 homoglyph 投毒：0/o 1/l 3/e 5/s @/a）
_HOMOGLYPH_MAP = str.maketrans("01358@", "olzebo")


def _homoglyph_normalize(name):
    return name.translate(_HOMOGLYPH_MAP)


# 仿冒官方厂商包名的可疑销售词
_BRAND_ROOTS = {
    "openai", "anthropic", "claude", "mcp", "langchain", "aws", "google",
    "azure", "gpt", "modelcontextprotocol", "huggingface", "cohere", "ollama",
}
_IMPERSONATION_SOCIAL = (
    "official", "real", "true", "genuine", "safe", "secure", "security",
    "wrapper", "proxy", "apikey", "api-key", "sdk", "client", "auth",
)


def _entropy(s):
    """简单香农熵，用于判断包名尾部是否为随机串。"""
    if not s:
        return 0.0
    from collections import Counter
    import math
    cnt = Counter(s)
    return -sum((c / len(s)) * math.log2(c / len(s)) for c in cnt.values())


# ------------------------------------------------------------------
# Slopsquatting（AI 幻觉包）离线启发式
# 背景：USENIX Security 2025 —— 16 个模型 / 57.6 万代码样本中 19.7% 推荐的包不存在，
# 共 205,474 个唯一虚构包名；43~58% 的幻觉名可复现。关键点是**约一半幻觉名与任何
# 真实包都不形近**，编辑距离/相似度检测天然失效（典型案例 react-codeshift，
# 2026-01 经 AI 生成的 skill 文件扩散到 237 个仓库）。
# 因此这里补一条「复合式幻觉包」通道：以生态锚点词 + 未收录 + 复合结构为特征，
# 输出 **advisory（info 级，不扣分）**，提示人工/远程核实注册表存在性。
# 纯离线，不联网；联网存在性校验属可选远程项。
# ------------------------------------------------------------------

# 生态锚点词：出现即说明该名字自称属于某知名生态
_ECOSYSTEM_ANCHORS = {
    "react", "vue", "angular", "svelte", "next", "nuxt", "node", "npm",
    "webpack", "babel", "eslint", "jest", "express", "redux", "graphql",
    "langchain", "llamaindex", "openai", "anthropic", "claude", "gpt",
    "mcp", "modelcontextprotocol", "huggingface", "transformers", "torch",
    "tensorflow", "pandas", "numpy", "django", "flask", "fastapi", "pytest",
    "aws", "azure", "gcp", "google", "cloudflare", "supabase", "stripe",
    "agent", "agents", "ollama", "cohere", "gemini", "copilot",
}

# 内部命名空间词（dependency confusion / 命名空间劫持信号）
_INTERNAL_NAMESPACE_HINTS = {
    "internal", "private", "corp", "corporate", "intranet", "inhouse",
    "in-house", "confidential", "staging", "prod-only", "companyname",
    "acme", "sandbox-internal",
}


def _split_tokens(name):
    return [t for t in re.split(r"[-_.@/]+", name) if t]


def check_package_name(name, ecosystem="npm"):
    """
    离线检测单个依赖名是否为幻觉包 / typosquat / 仿冒包。
    返回 findings 列表（每项含 type/severity/description/owasp_category/evidence）。
    纯本地启发式，不联网。
    """
    findings = []
    if not name or not isinstance(name, str):
        return findings
    n = name.strip().lower()
    # 去掉 npm scope 前缀（如 @scope/name -> name）
    if n.startswith("@") and "/" in n:
        n = n.split("/", 1)[1]
    if not n:
        return findings
    _is_npm = ecosystem in ("npm", "node")
    _is_py = ecosystem in ("pypi", "pip", "python")
    # 已知恶意包由 dependency_analysis 处理，这里不重复
    if _is_npm and n in DANGEROUS_NPM_PACKAGES:
        return findings
    if _is_py and n in DANGEROUS_PYPI_PACKAGES:
        return findings

    # 0) 跨注册表混淆（研究：8.7% 的 Python 幻觉包名在 npm 上真实存在）
    #    必须先于「可信名录」早退判定，否则会被并集名录吞掉。
    if _is_py and n in NPM_PACKAGE_CATALOG and n not in PYPI_PACKAGE_CATALOG:
        findings.append({
            "type": "cross_registry_confusion",
            "severity": "medium",
            "description": f"跨注册表混淆: '{name}' 是 npm 生态包名，却出现在 Python 依赖中",
            "owasp_category": "MCP04",
            "evidence": f"{name} (npm-only name in pypi manifest)",
            "remediation": "确认生态归属；对 agent 生成的依赖强制 registry 白名单",
        })
        return findings
    if _is_npm and n in PYPI_PACKAGE_CATALOG and n not in NPM_PACKAGE_CATALOG:
        findings.append({
            "type": "cross_registry_confusion",
            "severity": "medium",
            "description": f"跨注册表混淆: '{name}' 是 PyPI 生态包名，却出现在 npm 依赖中",
            "owasp_category": "MCP04",
            "evidence": f"{name} (pypi-only name in npm manifest)",
            "remediation": "确认生态归属；对 agent 生成的依赖强制 registry 白名单",
        })
        return findings

    if n in LEGIT_PACKAGE_CATALOG:
        return findings

    # 1) 编辑距离 typosquat
    best, best_d = None, 99
    for legit in LEGIT_PACKAGE_CATALOG:
        if abs(len(legit) - len(n)) > 3:
            continue
        d = _levenshtein(n, legit)
        if d < best_d:
            best_d, best = d, legit
    if best is not None:
        if best_d == 1 or (best_d == 2 and len(n) >= 8):
            findings.append({
                "type": "typosquatting",
                "severity": "high",
                "description": f"可能的 typosquatting 包名: '{name}' 形近官方包 '{best}'",
                "owasp_category": "MCP04",
                "evidence": f"{name} ~ {best} (dist={best_d})",
            })
            return findings

    # 2) 形近字符（homoglyph）
    norm = _homoglyph_normalize(n)
    if norm in LEGIT_PACKAGE_CATALOG and norm != n:
        findings.append({
            "type": "typosquatting",
            "severity": "high",
            "description": f"形近字符(homoglyph)投毒: '{name}' 归一后为官方包 '{norm}'",
            "owasp_category": "MCP04",
            "evidence": f"{name} -> {norm}",
        })
        return findings

    # 3) 厂商名仿冒（仅当尾部含可疑销售词或高熵随机串时告警，降低误报）
    root = n.split("-")[0].split("_")[0].split(".")[0]
    if root in _BRAND_ROOTS and n != root:
        tail = n[len(root):].lstrip("-_.")
        # 熵启发式只对「单段无分隔」的尾部生效，避免 langchain-mcp-toolkit 这类
        # 语义化复合名被误判为品牌仿冒（它们应走幻觉包 advisory 通道）。
        _tail_is_single_token = not any(sep in tail for sep in "-_.")
        if any(w in tail for w in _IMPERSONATION_SOCIAL) or (
            _tail_is_single_token and len(tail) >= 6 and _entropy(tail) > 3.0
        ):
            findings.append({
                "type": "brand_impersonation",
                "severity": "medium",
                "description": f"疑似仿冒官方厂商包名: '{name}' 借用 '{root}' 品牌",
                "owasp_category": "MCP04",
                "evidence": f"{name} (root={root})",
            })
            return findings

    tokens = _split_tokens(n)

    # 4) 依赖混淆 / 内部命名空间外泄（内部包名出现在公共 manifest 中）
    if any(t in _INTERNAL_NAMESPACE_HINTS for t in tokens):
        findings.append({
            "type": "dependency_confusion",
            "severity": "medium",
            "description": f"依赖混淆风险: '{name}' 含内部命名空间标识，公共注册表可被抢注同名包",
            "owasp_category": "MCP04",
            "evidence": f"{name} (internal token)",
            "remediation": "为内部包配置私有 registry scope 并锁定解析顺序",
        })
        return findings

    # 5) 复合式幻觉包（slopsquatting）—— 与真实包不形近，编辑距离检测失效的那一半
    #    特征：≥2 段的复合名 + 至少一个生态锚点词 + 不在可信名录内。
    #    严重度 info（不扣分），仅作「请核实注册表存在性」的 advisory。
    if 2 <= len(tokens) <= 5 and all(t.isalnum() for t in tokens):
        anchors = [t for t in tokens if t in _ECOSYSTEM_ANCHORS]
        if anchors:
            findings.append({
                "type": "suspected_hallucinated_package",
                "severity": "info",
                "description": (
                    f"疑似 AI 幻觉包(slopsquatting): '{name}' 借用 '{anchors[0]}' 生态命名但不在可信名录，"
                    f"需核实其在注册表中真实存在"
                ),
                "owasp_category": "MCP04",
                "evidence": f"{name} (anchor={anchors[0]}, composite)",
                "remediation": "安装前校验注册表存在性/包龄/下载量；使用 lockfile 与依赖白名单",
            })

    return findings


# ------------------------------------------------------------------
# 依赖卫生检查（manifest 级，离线）
# 覆盖：安装脚本投毒、不可信来源直装、版本未锁定、缺 lockfile。
# ------------------------------------------------------------------

_INSTALL_HOOK_KEYS = ("preinstall", "install", "postinstall", "prepare")
_INSTALL_HOOK_DANGER = re.compile(
    r"\b(curl|wget|iwr|invoke-webrequest|base64\s+-d|chmod\s+\+x|bash\s+-c|sh\s+-c|"
    r"node\s+-e|python\s+-c|powershell|certutil|eval)\b",
    re.IGNORECASE,
)
_UNTRUSTED_SPEC = re.compile(
    r"^(git\+|git:|github:|gitlab:|bitbucket:|http://|file:|link:)", re.IGNORECASE
)
_UNPINNED_SPEC = {"*", "", "latest", "x", "*.*", "next"}


def check_dependency_hygiene(files):
    """
    manifest 级依赖卫生检查（纯离线）。
    files: {filename: content}
    返回 findings 列表。
    """
    findings = []
    if not isinstance(files, dict):
        return findings

    lowered = {k.lower().replace("\\", "/").split("/")[-1] for k in files}
    has_npm_lock = bool(
        lowered & {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "npm-shrinkwrap.json"}
    )

    for fname, content in files.items():
        base = fname.lower().replace("\\", "/").split("/")[-1]
        if not isinstance(content, str):
            continue

        if base == "package.json":
            try:
                pkg = json.loads(content)
            except Exception:
                continue
            if not isinstance(pkg, dict):
                continue

            # a) 安装脚本投毒
            scripts = pkg.get("scripts") or {}
            if isinstance(scripts, dict):
                for hook in _INSTALL_HOOK_KEYS:
                    cmd = scripts.get(hook)
                    if isinstance(cmd, str) and _INSTALL_HOOK_DANGER.search(cmd):
                        findings.append({
                            "type": "install_script_execution",
                            "severity": "critical",
                            "description": f"安装期脚本执行高危命令: scripts.{hook}",
                            "file": fname,
                            "owasp_category": "MCP04",
                            "evidence": cmd[:160],
                            "remediation": "使用 --ignore-scripts 安装并人工审计该 hook",
                        })

            # b) 依赖来源与版本锁定
            declared = 0
            for dep_type in ("dependencies", "devDependencies", "optionalDependencies"):
                deps = pkg.get(dep_type) or {}
                if not isinstance(deps, dict):
                    continue
                for dname, spec in deps.items():
                    declared += 1
                    spec_s = spec if isinstance(spec, str) else ""
                    if _UNTRUSTED_SPEC.match(spec_s.strip()):
                        findings.append({
                            "type": "untrusted_dependency_source",
                            "severity": "high",
                            "description": f"依赖 '{dname}' 从非注册表来源安装: {spec_s[:60]}",
                            "file": fname,
                            "owasp_category": "MCP04",
                            "evidence": f"{dname}: {spec_s[:80]}",
                            "remediation": "改用已发布的注册表版本并锁定完整性哈希",
                        })
                    elif spec_s.strip().lower() in _UNPINNED_SPEC:
                        findings.append({
                            "type": "unpinned_dependency",
                            "severity": "medium",
                            "description": f"依赖 '{dname}' 未锁定版本({spec_s or '空'})，存在供应链漂移/rug-pull 风险",
                            "file": fname,
                            "owasp_category": "MCP04",
                            "evidence": f"{dname}: {spec_s}",
                            "remediation": "锁定精确版本并提交 lockfile",
                        })

            if declared and not has_npm_lock:
                findings.append({
                    "type": "missing_lockfile",
                    "severity": "low",
                    "description": "声明了依赖但未见 lockfile，幻觉包/漂移无法 fail-closed",
                    "file": fname,
                    "owasp_category": "MCP04",
                    "evidence": f"{declared} deps, no package-lock.json/yarn.lock/pnpm-lock.yaml",
                    "remediation": "提交 lockfile 并在 CI 使用 npm ci",
                })

        elif base == "requirements.txt":
            for raw in content.split("\n"):
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("-e ") or line.startswith("--editable"):
                    target = line.split(None, 1)[1] if " " in line else ""
                    if target.startswith(("git+", "http://", "https://")):
                        findings.append({
                            "type": "untrusted_dependency_source",
                            "severity": "high",
                            "description": f"可编辑依赖来自非 PyPI 来源: {target[:60]}",
                            "file": fname,
                            "owasp_category": "MCP04",
                            "evidence": line[:120],
                            "remediation": "改用 PyPI 发布版本并锁定哈希",
                        })
                    continue
                if line.startswith(("git+", "http://")):
                    findings.append({
                        "type": "untrusted_dependency_source",
                        "severity": "high",
                        "description": f"依赖从非 PyPI/明文 HTTP 来源安装: {line[:60]}",
                        "file": fname,
                        "owasp_category": "MCP04",
                        "evidence": line[:120],
                        "remediation": "改用 HTTPS 的 PyPI 发布版本并锁定哈希",
                    })
                elif "--index-url" in line or "--extra-index-url" in line:
                    findings.append({
                        "type": "dependency_confusion",
                        "severity": "medium",
                        "description": "requirements 指定了额外索引源，存在依赖混淆解析风险",
                        "file": fname,
                        "owasp_category": "MCP04",
                        "evidence": line[:120],
                        "remediation": "固定单一索引源或使用 --index-url 替代 --extra-index-url",
                    })

    return findings

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
        "ASI01": ASI01_RULES, "ASI02": ASI02_RULES, "ASI03": ASI03_RULES,
        "ASI04": ASI04_RULES, "ASI05": ASI05_RULES, "ASI06": ASI06_RULES,
        "ASI07": ASI07_RULES, "ASI08": ASI08_RULES, "ASI09": ASI09_RULES,
        "ASI10": ASI10_RULES,
    }
    return len(mapping.get(category, {}))


def get_owasp_coverage(findings):
    """计算OWASP MCP Top 10覆盖情况"""
    covered = set()
    for f in findings:
        cat = f.get("owasp_category")
        if cat and cat.startswith("MCP"):
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


def get_agentic_coverage(findings):
    """计算OWASP Agentic AI Top 10 (ASI01-ASI10) 覆盖情况"""
    covered = set()
    for f in findings:
        cat = f.get("owasp_category")
        if cat and cat.startswith("ASI"):
            covered.add(cat)
    categories_detail = {}
    for cat in covered:
        info = OWASP_AGENTIC_AI_TOP10.get(cat, {})
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
        "agentic_coverage": get_agentic_coverage(findings),
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
    if pattern in ASI01_RULES: return "ASI01"
    if pattern in ASI02_RULES: return "ASI02"
    if pattern in ASI03_RULES: return "ASI03"
    if pattern in ASI04_RULES: return "ASI04"
    if pattern in ASI05_RULES: return "ASI05"
    if pattern in ASI06_RULES: return "ASI06"
    if pattern in ASI07_RULES: return "ASI07"
    if pattern in ASI08_RULES: return "ASI08"
    if pattern in ASI09_RULES: return "ASI09"
    if pattern in ASI10_RULES: return "ASI10"
    return None