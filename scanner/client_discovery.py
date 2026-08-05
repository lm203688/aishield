"""
AIShield — 多客户端 MCP 配置自动发现与配置级威胁分析（纯离线 / 零第三方依赖）

设计不变量
----------
1. **绝不执行被扫描的命令**：本模块只做路径推导、文件读取与静态解析。
   竞品（Snyk Agent Scan 等）为读取 tools/list 会 **真实 spawn** 配置中的命令，
   其 README 明确警告 "Scanning MCP configurations will execute the commands
   defined in them"。AIShield 选择纯静态，扫描本身不构成新的信任边界。
2. **零网络**：不联网校验包名、不查 CVE 在线库、不上报遥测。
3. **零第三方依赖**：仅标准库（os/json/re/socket 之外不引入任何东西）。

覆盖的威胁（对齐 OWASP MCP Top 10 + Agentic AI Top 10）
------------------------------------------------------
- STDIO 启动命令暴露面（OX Security 2026-04「Mother of All AI Supply Chains」，
  MCP STDIO 无论进程是否成功启动命令都会执行；CVE-2026-30623 同类）
- 运行时拉包（npx -y / uvx pkg@latest）导致的 rug-pull 与幻觉包落地
- 提权启动（sudo/doas/pkexec/su/run0）
- 配置内明文凭证
- 明文传输 / 通配监听 / 远程无鉴权（参 arXiv 2605.22333：7,973 个在线远程
  MCP server 中 40.55% 无鉴权）
- 服务名冲突导致的命名空间遮蔽（NSA MCP 指南点名的 tool shadowing）
- 跨服务器毒性组合流（7 类高危能力对）
- 项目级配置信任陷阱（Adversa TrustFall / CVE-2026-30615）
"""

import json
import os
import re

__all__ = [
    "CLIENT_PROFILES",
    "get_client_profiles",
    "discover_client_configs",
    "parse_mcp_config",
    "infer_capabilities",
    "analyze_server_entry",
    "analyze_cross_server",
    "scan_client_configs",
    "discover_and_scan",
]

# --------------------------------------------------------------------------
# 一、已知客户端配置位置
#     path 模板变量：{home} {appdata} {xdg} {project}
#     scope: user / project
# --------------------------------------------------------------------------

CLIENT_PROFILES = [
    {
        "client": "Claude Desktop",
        "scope": "user",
        "paths": {
            "win32": ["{appdata}/Claude/claude_desktop_config.json"],
            "darwin": ["{home}/Library/Application Support/Claude/claude_desktop_config.json"],
            "linux": ["{xdg}/Claude/claude_desktop_config.json"],
        },
    },
    {
        "client": "Claude Code (user)",
        "scope": "user",
        "paths": {
            "win32": ["{home}/.claude.json", "{home}/.claude/settings.json"],
            "darwin": ["{home}/.claude.json", "{home}/.claude/settings.json"],
            "linux": ["{home}/.claude.json", "{home}/.claude/settings.json"],
        },
    },
    {
        "client": "Claude Code (project)",
        "scope": "project",
        "paths": {
            "*": ["{project}/.mcp.json", "{project}/.claude/settings.json"],
        },
    },
    {
        "client": "Cursor",
        "scope": "user",
        "paths": {"*": ["{home}/.cursor/mcp.json"]},
    },
    {
        "client": "Cursor (project)",
        "scope": "project",
        "paths": {"*": ["{project}/.cursor/mcp.json"]},
    },
    {
        "client": "VS Code",
        "scope": "user",
        "paths": {
            "win32": ["{appdata}/Code/User/mcp.json", "{appdata}/Code/User/settings.json"],
            "darwin": [
                "{home}/Library/Application Support/Code/User/mcp.json",
                "{home}/Library/Application Support/Code/User/settings.json",
            ],
            "linux": ["{xdg}/Code/User/mcp.json", "{xdg}/Code/User/settings.json"],
        },
    },
    {
        "client": "VS Code (project)",
        "scope": "project",
        "paths": {"*": ["{project}/.vscode/mcp.json"]},
    },
    {
        "client": "Windsurf",
        "scope": "user",
        "paths": {"*": ["{home}/.codeium/windsurf/mcp_config.json"]},
    },
    {
        "client": "Gemini CLI",
        "scope": "user",
        "paths": {"*": ["{home}/.gemini/settings.json"]},
    },
    {
        "client": "GitHub Copilot CLI",
        "scope": "user",
        "paths": {"*": ["{home}/.copilot/mcp-config.json"]},
    },
    {
        "client": "Augment Code",
        "scope": "user",
        "paths": {"*": ["{home}/.augment/mcp.json"]},
    },
    {
        "client": "Zed",
        "scope": "user",
        "paths": {"*": ["{home}/.config/zed/settings.json"]},
    },
    {
        "client": "Cline",
        "scope": "user",
        "paths": {"*": ["{home}/.cline/mcp_settings.json"]},
    },
    {
        "client": "WorkBuddy",
        "scope": "user",
        "paths": {"*": ["{home}/.workbuddy/mcp.json"]},
    },
]


def get_client_profiles():
    """返回受支持的客户端档案（拷贝，避免调用方污染常量）。"""
    return [dict(p) for p in CLIENT_PROFILES]


def _platform_key(platform_name=None):
    name = (platform_name or "").lower()
    if not name:
        import sys

        name = sys.platform
    if name.startswith("win"):
        return "win32"
    if name.startswith("darwin") or name == "mac":
        return "darwin"
    return "linux"


def _expand(template, home, appdata, xdg, project):
    return (
        template.replace("{home}", home)
        .replace("{appdata}", appdata)
        .replace("{xdg}", xdg)
        .replace("{project}", project or "")
    )


def discover_client_configs(home=None, project_root=None, platform_name=None,
                            appdata=None, exists=None):
    """
    推导并发现本机 MCP 配置文件（只读）。

    exists: 可注入的存在性判定函数（测试用），默认 os.path.isfile。
    返回: [{client, scope, path, exists}]
    """
    plat = _platform_key(platform_name)
    home = home or os.path.expanduser("~")
    appdata = appdata or os.environ.get("APPDATA") or os.path.join(home, "AppData", "Roaming")
    xdg = os.environ.get("XDG_CONFIG_HOME") or os.path.join(home, ".config")
    checker = exists or os.path.isfile

    results = []
    seen = set()
    for profile in CLIENT_PROFILES:
        if profile["scope"] == "project" and not project_root:
            continue
        templates = profile["paths"].get(plat) or profile["paths"].get("*") or []
        for tpl in templates:
            path = _expand(tpl, home, appdata, xdg, project_root)
            norm = path.replace("\\", "/")
            key = (profile["client"], norm.lower())
            if key in seen:
                continue
            seen.add(key)
            results.append({
                "client": profile["client"],
                "scope": profile["scope"],
                "path": norm,
                "exists": bool(checker(path)),
            })
    return results


# --------------------------------------------------------------------------
# 二、配置解析（兼容多种 schema）
# --------------------------------------------------------------------------

_SERVER_CONTAINER_KEYS = ("mcpServers", "servers", "context_servers", "mcp_servers")


def parse_mcp_config(content):
    """
    把任意已知形态的客户端配置解析成统一的 {name: entry} 映射。
    支持顶层 mcpServers/servers/context_servers，以及嵌套在 "mcp" 下的写法。
    解析失败返回空字典（fail-safe，不抛异常）。
    """
    if isinstance(content, dict):
        data = content
    elif isinstance(content, str):
        try:
            data = json.loads(content)
        except Exception:
            return {}
    else:
        return {}

    if not isinstance(data, dict):
        return {}

    servers = {}

    def _collect(container):
        if isinstance(container, dict):
            for name, entry in container.items():
                if isinstance(entry, dict):
                    servers[name] = entry

    for key in _SERVER_CONTAINER_KEYS:
        _collect(data.get(key))

    nested = data.get("mcp")
    if isinstance(nested, dict):
        for key in _SERVER_CONTAINER_KEYS:
            _collect(nested.get(key))

    return servers


# --------------------------------------------------------------------------
# 三、能力标签推断
# --------------------------------------------------------------------------

_CAPABILITY_HINTS = {
    "filesystem": (
        "filesystem", "file-system", "files", "fs-", "directory", "desktop-commander",
        "everything-search", "obsidian", "notion-local", "读写文件",
    ),
    "network_out": (
        "fetch", "http", "https-client", "web", "browser", "puppeteer", "playwright",
        "curl", "requests", "brave-search", "tavily", "exa", "serper", "crawl",
        "scrape", "slack", "discord", "telegram", "email", "smtp", "webhook",
    ),
    "shell_exec": (
        "shell", "bash", "terminal", "iterm", "command", "exec", "desktop-commander",
        "run-", "subprocess", "powershell",
    ),
    "database": (
        "postgres", "postgresql", "mysql", "sqlite", "mongo", "redis", "mssql",
        "supabase", "clickhouse", "duckdb", "neo4j", "-db", "database", "bigquery",
    ),
    "secrets": (
        "vault", "1password", "keychain", "secret", "credential", "keyring",
        "bitwarden", "lastpass", "sops",
    ),
    "cloud": (
        "aws", "azure", "gcp", "google-cloud", "cloudflare", "s3", "kubernetes",
        "k8s", "terraform", "docker",
    ),
}

_SHELL_BINARIES = {"sh", "bash", "zsh", "dash", "ksh", "fish", "cmd", "cmd.exe",
                   "powershell", "powershell.exe", "pwsh", "pwsh.exe"}
_PRIVILEGE_BINARIES = {"sudo", "doas", "pkexec", "su", "run0", "runas"}


def _entry_text(name, entry):
    parts = [str(name)]
    for key in ("command", "url", "type", "description"):
        val = entry.get(key)
        if isinstance(val, str):
            parts.append(val)
    args = entry.get("args")
    if isinstance(args, list):
        parts.extend(str(a) for a in args)
    env = entry.get("env")
    if isinstance(env, dict):
        parts.extend(str(k) for k in env)
    return " ".join(parts).lower()


def infer_capabilities(name, entry):
    """根据服务器名/命令/参数推断能力标签集合（保守启发式，纯离线）。"""
    if not isinstance(entry, dict):
        return set()
    text = _entry_text(name, entry)
    caps = set()
    for cap, hints in _CAPABILITY_HINTS.items():
        if any(h in text for h in hints):
            caps.add(cap)

    command = str(entry.get("command") or "")
    base = os.path.basename(command.replace("\\", "/")).lower()
    if base in _SHELL_BINARIES:
        caps.add("shell_exec")
    if base in _PRIVILEGE_BINARIES:
        caps.add("shell_exec")

    # 远程 server 天然具备出网能力
    if entry.get("url") or str(entry.get("type") or "").lower() in ("sse", "http", "streamable-http"):
        caps.add("network_out")

    # env 中**实际内联的明文凭证**才算 secrets 能力。
    # 注意：仅凭键名（API_KEY 等）判定会把绝大多数合法配置误判为持有密钥，
    # 进而让「secrets + network_out」毒性流对几乎所有人恒亮 —— 这是噪声源。
    # 持有自己的一个 API Key 引用是常态；能读到明文凭证才是真实外泄面。
    env = entry.get("env")
    if isinstance(env, dict):
        for v in env.values():
            if not isinstance(v, str) or not v.strip() or _PLACEHOLDER_RE.match(v):
                continue
            if any(re.search(pat, v) for pat, _ in _CREDENTIAL_PATTERNS):
                caps.add("secrets")
                break
    return caps


# --------------------------------------------------------------------------
# 四、单服务器风险检测
# --------------------------------------------------------------------------

_CREDENTIAL_PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"ghp_[A-Za-z0-9]{20,}", "GitHub Personal Access Token"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "GitHub Fine-grained PAT"),
    (r"gho_[A-Za-z0-9]{20,}", "GitHub OAuth Token"),
    (r"sk-ant-[A-Za-z0-9\-_]{20,}", "Anthropic API Key"),
    (r"sk-[A-Za-z0-9]{32,}", "OpenAI API Key"),
    (r"xox[baprs]-[A-Za-z0-9\-]{10,}", "Slack Token"),
    (r"sk_live_[A-Za-z0-9]{16,}", "Stripe Live Key"),
    (r"AIza[0-9A-Za-z\-_]{30,}", "Google API Key"),
    (r"(?:postgres|postgresql|mysql|mongodb(?:\+srv)?|redis)://[^\s:@/]+:[^\s:@/]+@", "数据库连接串（含明文口令）"),
    (r"eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.", "JWT"),
]

_PLACEHOLDER_RE = re.compile(
    r"^\s*(\$\{|\$[A-Z_]|<|\{\{|your[-_ ]|xxx+|placeholder|changeme|todo|example|dummy|test[-_]?key)",
    re.I,
)

_RUNTIME_FETCH_RUNNERS = {"npx", "npx.cmd", "uvx", "pnpm", "pnpx", "bunx", "pipx", "dlx"}
_PRIVATE_HOST_RE = re.compile(
    r"^(localhost|127\.0\.0\.1|::1|0\.0\.0\.0|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|"
    r"172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+|.*\.local|.*\.internal)$",
    re.I,
)
_AUTH_KEY_RE = re.compile(
    r"(authorization|api[-_]?key|token|bearer|secret|credential|oauth|client[-_]?secret)", re.I
)
_VERSION_PIN_RE = re.compile(r"@\d+\.\d+")


def _finding(ftype, severity, description, owasp, evidence, remediation, **extra):
    f = {
        "type": ftype,
        "severity": severity,
        "description": description,
        "owasp_category": owasp,
        "evidence": (evidence or "")[:200],
        "remediation": remediation,
    }
    f.update(extra)
    return f


def analyze_server_entry(name, entry, source="", scope="user"):
    """对单个 MCP server 配置条目做静态风险分析。返回 findings 列表。"""
    findings = []
    if not isinstance(entry, dict):
        return findings

    command = str(entry.get("command") or "")
    args = entry.get("args") if isinstance(entry.get("args"), list) else []
    args_s = [str(a) for a in args]
    argline = " ".join(args_s)
    base = os.path.basename(command.replace("\\", "/")).lower()
    url = str(entry.get("url") or "")

    def add(*a, **kw):
        f = _finding(*a, **kw)
        f["server"] = name
        f["file"] = source
        findings.append(f)

    # 1) 提权启动
    if base in _PRIVILEGE_BINARIES:
        add("elevated_privilege_launch", "critical",
            f"MCP server '{name}' 以提权方式启动（{base}），agent 可获得 root 等价权限",
            "MCP01", f"{command} {argline}",
            "移除提权包装，改用最小权限账户运行")

    # 2) STDIO 启动命令暴露面（OX Security 2026-04）
    #    注意：这对 100% 的 stdio server 都成立（Anthropic 明确回应「by design」），
    #    属于**上下文**而非缺陷。若给它 medium，20 个 server 就能刷出 20 条 medium
    #    把真实问题淹掉 —— 因此固定为 info（零扣分），仅用于资产清点与风险交底。
    if command and not url:
        add("stdio_command_execution_exposure", "info",
            f"STDIO server '{name}' 的启动命令会在客户端加载时被执行，"
            f"且无论进程是否成功启动都会执行（MCP 协议设计使然）",
            "MCP04", f"{command} {argline}",
            "确认命令来源可信；对第三方 server 使用容器/沙箱隔离")

    # 3) 运行时拉包（rug-pull / 幻觉包落地）
    if base.split(".")[0] in _RUNTIME_FETCH_RUNNERS or base in _RUNTIME_FETCH_RUNNERS:
        auto_yes = any(a in ("-y", "--yes", "--force") for a in args_s)
        pkg = next((a for a in args_s if not a.startswith("-")), "")
        pinned = bool(_VERSION_PIN_RE.search(pkg))
        latest = pkg.endswith("@latest")
        if not pinned or latest:
            add("runtime_package_fetch", "high" if auto_yes or latest else "medium",
                f"server '{name}' 每次启动都从注册表拉取未锁定版本的包"
                f"（{pkg or base}），存在 rug-pull 与幻觉包落地风险",
                "MCP04", f"{command} {argline}",
                "锁定精确版本（pkg@1.2.3）或预装到本地后以绝对路径启动")

    # 4) 直接以 shell 解释器启动
    if base in _SHELL_BINARIES and any(a in ("-c", "/c", "/C", "-Command") for a in args_s):
        add("shell_interpreter_launch", "high",
            f"server '{name}' 通过 shell -c 启动，命令串易被注入且难以审计",
            "MCP01", f"{command} {argline}",
            "改为直接调用可执行文件与显式参数数组，避免 shell 解释")

    # 5) 非注册表来源（git+ / 原始脚本 URL）
    for a in args_s:
        if a.startswith(("git+", "http://")) or re.match(r"^https?://.*\.(sh|ps1|py|js)$", a):
            add("untrusted_launch_source", "high",
                f"server '{name}' 从非注册表来源加载代码: {a[:60]}",
                "MCP04", a,
                "改用已发布的注册表版本并校验完整性哈希")
            break

    # 6) 明文凭证
    env = entry.get("env") if isinstance(entry.get("env"), dict) else {}
    headers = entry.get("headers") if isinstance(entry.get("headers"), dict) else {}
    for bag, label in ((env, "env"), (headers, "headers")):
        for k, v in bag.items():
            if not isinstance(v, str) or not v.strip():
                continue
            if _PLACEHOLDER_RE.match(v):
                continue
            for pat, kind in _CREDENTIAL_PATTERNS:
                if re.search(pat, v):
                    add("credential_exposure_in_config", "critical",
                        f"server '{name}' 的 {label}.{k} 中出现明文 {kind}",
                        "MCP02", f"{label}.{k}=<redacted:{kind}>",
                        "立即轮换该凭证，改用系统密钥管理或环境变量引用")
                    break

    # 7) 传输安全 / 远程鉴权
    if url:
        m = re.match(r"^(https?)://([^/:]+)", url, re.I)
        scheme = (m.group(1).lower() if m else "")
        host = (m.group(2) if m else "")
        is_private = bool(_PRIVATE_HOST_RE.match(host))
        if scheme == "http" and not is_private:
            add("insecure_transport", "high",
                f"server '{name}' 使用明文 HTTP 连接远程主机 {host}，令牌与工具描述可被中间人篡改",
                "MCP03", url,
                "改用 HTTPS；如为自建服务请配置 TLS")
        if host in ("0.0.0.0", "::"):
            add("wildcard_bind", "high",
                f"server '{name}' 指向通配地址 {host}，该 MCP 端点对整个局域网可达",
                "MCP03", url,
                "绑定 127.0.0.1；确需跨机访问时必须叠加 TLS 与鉴权")
        has_auth = any(_AUTH_KEY_RE.search(str(k)) for k in list(env) + list(headers))
        if not has_auth and scheme:
            add("remote_server_without_auth", "medium" if is_private else "high",
                f"远程 server '{name}' 未见任何鉴权材料"
                f"（学界实测 7,973 个在线远程 MCP server 中 40.55% 无鉴权）",
                "MCP05", url,
                "配置 OAuth 2.1 或 API Key，并校验 RFC 8707 audience 绑定")

    # 8) 项目级配置信任陷阱（Adversa TrustFall / CVE-2026-30615）
    if scope == "project" and (command or url):
        add("project_config_trust_risk", "high",
            f"项目级配置声明了 server '{name}'，克隆仓库后点击「信任此目录」即会加载，"
            f"属于典型的 TrustFall 攻击面",
            "MCP04", f"{source}: {command or url}",
            "审阅项目内 MCP 配置后再信任目录；CI 中对项目级配置做门禁")

    return findings


# --------------------------------------------------------------------------
# 五、跨服务器分析：命名空间遮蔽 + 毒性组合流
# --------------------------------------------------------------------------

# 毒性组合流是**架构姿态**问题，不是已确认缺陷：
# 「文件读 + 出网」在任何正常开发者机器上都成立（filesystem + fetch 是标配）。
# 若按 high 报，等于对所有人恒亮，会淹没真实缺陷 —— 这正是门禁自毁的典型方式。
# 因此：默认 medium + advisory=True；只有当参与方持有**内联明文凭证**（secrets
# 能力已按值判定）时才升 high，因为那时外泄链路是具体而非潜在的。
_TOXIC_PAIRS = [
    ("filesystem", "network_out", "本地文件可被读出并外发", "medium"),
    ("secrets", "network_out", "内联明文凭证可被读取并外发", "high"),
    ("database", "network_out", "数据库内容可被导出并外发", "medium"),
    ("shell_exec", "network_out", "命令执行结果可外发，且可下载并执行载荷", "medium"),
    ("filesystem", "shell_exec", "可写入文件并执行，构成持久化/提权链", "medium"),
    ("secrets", "shell_exec", "内联明文凭证可被注入到任意命令中使用", "high"),
    ("cloud", "network_out", "云控制面权限可被滥用并外发", "medium"),
]


def analyze_cross_server(inventory):
    """
    inventory: [{name, client, scope, file, capabilities:set}]
    检测命名空间遮蔽与跨服务器毒性组合流。
    """
    findings = []
    if not inventory:
        return findings

    # a) 服务名冲突 → 命名空间遮蔽（NSA MCP 指南点名）
    by_name = {}
    for item in inventory:
        by_name.setdefault(str(item.get("name")).lower(), []).append(item)
    for lname, items in sorted(by_name.items()):
        if len(items) > 1:
            where = ", ".join(f"{i.get('client')}:{i.get('file')}" for i in items)
            findings.append(_finding(
                "server_name_collision", "high",
                f"服务名 '{items[0].get('name')}' 在 {len(items)} 处配置中重复，"
                f"后加载者可静默遮蔽先前工具（tool shadowing）",
                "MCP07", where,
                "为每个 server 使用全局唯一名称，并在客户端固定加载顺序",
                server=items[0].get("name"),
            ))

    # b) 跨服务器毒性组合流
    cap_owners = {}
    for item in inventory:
        for cap in item.get("capabilities") or ():
            cap_owners.setdefault(cap, []).append(item)

    for cap_a, cap_b, why, sev in _TOXIC_PAIRS:
        owners_a = cap_owners.get(cap_a) or []
        owners_b = cap_owners.get(cap_b) or []
        if not owners_a or not owners_b:
            continue
        names_a = sorted({str(i.get("name")) for i in owners_a})
        names_b = sorted({str(i.get("name")) for i in owners_b})
        if names_a == names_b and len(names_a) == 1:
            scope_note = f"单个 server '{names_a[0]}' 同时具备"
        else:
            scope_note = "同一 agent 会话中并存"
        findings.append(_finding(
            "cross_server_toxic_flow", sev,
            f"{scope_note} [{cap_a}] 与 [{cap_b}] 能力：{why}",
            "ASI05", f"{cap_a}: {', '.join(names_a[:4])} | {cap_b}: {', '.join(names_b[:4])}",
            "拆分到不同 agent 会话，或对其中一侧启用人工确认/出网白名单",
            capability_pair=[cap_a, cap_b],
            advisory=True,
        ))

    return findings


# --------------------------------------------------------------------------
# 六、顶层入口
# --------------------------------------------------------------------------

_SEVERITY_WEIGHT = {"critical": 20, "high": 8, "medium": 1.5, "low": 0.5, "info": 0}

# 低危等级的累计扣分上限。没有上限时，「server 越多分越低」会让任何中等规模的
# 正常机器恒得 0 分，评分就失去区分度（评分器自己坏掉 = 最隐蔽的失效模式）。
_SEVERITY_PENALTY_CAP = {"medium": 20, "low": 5}


def compute_config_score(findings):
    """
    由 findings 计算 0–100 配置健康分。
    critical/high 线性累加（确认缺陷，应当迅速归零）；
    medium/low 设累计上限（姿态类问题，不因资产规模而无限惩罚）。
    """
    counts = {}
    for f in findings:
        counts[f.get("severity", "info")] = counts.get(f.get("severity", "info"), 0) + 1
    penalty = 0.0
    for sev, n in counts.items():
        raw = _SEVERITY_WEIGHT.get(sev, 0) * n
        cap = _SEVERITY_PENALTY_CAP.get(sev)
        penalty += min(raw, cap) if cap is not None else raw
    return max(0, int(round(100 - min(penalty, 100)))), counts


def scan_client_configs(configs):
    """
    configs: {path: content} 或 [{path, content, client, scope}]
    返回 {inventory, findings, summary}
    """
    normalized = []
    if isinstance(configs, dict):
        for path, content in configs.items():
            normalized.append({"path": path, "content": content,
                               "client": "unknown", "scope": "user"})
    elif isinstance(configs, list):
        for item in configs:
            if isinstance(item, dict) and "path" in item:
                normalized.append({
                    "path": item.get("path"),
                    "content": item.get("content"),
                    "client": item.get("client", "unknown"),
                    "scope": item.get("scope", "user"),
                })

    inventory = []
    findings = []
    parsed_files = 0

    for item in normalized:
        servers = parse_mcp_config(item["content"])
        if servers:
            parsed_files += 1
        for name, entry in servers.items():
            findings.extend(analyze_server_entry(
                name, entry, source=item["path"], scope=item["scope"]
            ))
            inventory.append({
                "name": name,
                "client": item["client"],
                "scope": item["scope"],
                "file": item["path"],
                "transport": "remote" if entry.get("url") else "stdio",
                "command": str(entry.get("command") or entry.get("url") or ""),
                "capabilities": infer_capabilities(name, entry),
            })

    findings.extend(analyze_cross_server(inventory))

    score, counts = compute_config_score(findings)

    summary = {
        "files_parsed": parsed_files,
        "servers_found": len(inventory),
        "clients": sorted({i["client"] for i in inventory}),
        "findings_total": len(findings),
        "severity_counts": counts,
        "config_score": score,
    }

    # inventory 里的 set 不可 JSON 序列化，导出前转为排序列表
    export_inventory = [dict(i, capabilities=sorted(i["capabilities"])) for i in inventory]
    return {"inventory": export_inventory, "findings": findings, "summary": summary}


def discover_and_scan(home=None, project_root=None, platform_name=None, read=None):
    """
    发现本机配置并直接扫描（只读，绝不执行任何被扫命令）。
    read: 可注入的读文件函数（测试用）。
    """
    discovered = discover_client_configs(
        home=home, project_root=project_root, platform_name=platform_name
    )

    def _default_read(path):
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()

    reader = read or _default_read
    payload = []
    for d in discovered:
        if not d["exists"]:
            continue
        try:
            content = reader(d["path"])
        except Exception:
            continue
        payload.append({
            "path": d["path"], "content": content,
            "client": d["client"], "scope": d["scope"],
        })

    result = scan_client_configs(payload)
    result["discovered"] = discovered
    result["summary"]["configs_discovered"] = sum(1 for d in discovered if d["exists"])
    result["summary"]["clients_supported"] = len(CLIENT_PROFILES)
    return result
