#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/submit_mcp_directories.py — MCP 目录平台批量提交自动化

功能:
  1. 读取 mcp-server/mcp.json 作为元数据源
  2. 生成各平台所需的提交格式 (Smithery, Glama, MCP.so, PulseMCP, etc.)
  3. 自动提交到支持 API/CLI 的平台
  4. 输出剩余平台的手动提交指南
  5. 记录提交状态到 api/data/mcp_submissions.json

用法:
  python scripts/submit_mcp_directories.py --dry-run    # 预览
  python scripts/submit_mcp_directories.py --submit     # 执行提交

平台覆盖:
  [自动]   smithery.ai     — 通过 smithery.yaml 已配置
  [半自动] github-awesome  — 自动 fork + 发 PR（需 GITHUB_TOKEN）
  [手动]   mcp.so          — 生成提交数据，输出链接
  [手动]   glama.ai        — 生成提交数据，输出链接
  [手动]   pulsemcp.com    — 生成提交数据，输出链接
  [手动]   mcp.run         — 生成提交数据，输出链接
"""

import json
import os
import sys
import subprocess
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

# ── 路径配置 ──
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MCP_JSON = os.path.join(BASE_DIR, "mcp-server", "mcp.json")
DATA_DIR = os.path.join(BASE_DIR, "api", "data")
SUBMISSIONS_FILE = os.path.join(DATA_DIR, "mcp_submissions.json")

TZ = timezone(timedelta(hours=8))

# ── 平台配置 ──
PLATFORMS = {
    "smithery": {
        "name": "Smithery.ai",
        "url": "https://smithery.ai/server/@aishield/mcp-server",
        "auto": True,
        "method": "yaml",
        "yaml_file": "mcp-server/smithery.yaml",
        "description": "已配置 smithery.yaml，平台自动抓取",
    },
    "github_awesome": {
        "name": "Awesome MCP Servers (GitHub)",
        "url": "https://github.com/punkpeye/awesome-mcp-servers",
        "auto": False,  # 需要 GITHUB_TOKEN 才能自动 PR
        "method": "pr",
        "repo": "punkpeye/awesome-mcp-servers",
        "description": "通过 Pull Request 提交到 awesome-mcp-servers 列表",
    },
    "mcp_so": {
        "name": "MCP.so",
        "url": "https://mcp.so/submit",
        "auto": False,
        "method": "form",
        "description": "表单提交，支持 GitHub URL 自动解析",
    },
    "glama": {
        "name": "Glama.ai",
        "url": "https://glama.ai/mcp/submit",
        "auto": False,
        "method": "form",
        "description": "提交 GitHub 仓库地址即可",
    },
    "pulsemcp": {
        "name": "PulseMCP",
        "url": "https://www.pulsemcp.com/submit",
        "auto": False,
        "method": "form",
        "description": "MCP 服务器发现平台",
    },
    "mcp_run": {
        "name": "MCP.run",
        "url": "https://www.mcp.run/",
        "auto": False,
        "method": "manual",
        "description": "需要手动注册并配置",
    },
    "mcp_get": {
        "name": "mcp-get.com",
        "url": "https://www.mcp-get.com/",
        "auto": False,
        "method": "manual",
        "description": "MCP 工具包管理平台",
    },
    "fleek": {
        "name": "Fleek MCP",
        "url": "https://fleek.xyz/agents/",
        "auto": False,
        "method": "manual",
        "description": "Agent 部署与托管平台",
    },
}


def _load_json(path, default=None):
    if default is None:
        default = {}
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _now_iso():
    return datetime.now(TZ).isoformat()


def load_mcp_manifest():
    """读取 MCP 元数据"""
    data = _load_json(MCP_JSON, {})
    if not data:
        print(f"❌ 无法读取 {MCP_JSON}")
        sys.exit(1)
    return data


def generate_glama_json(manifest):
    """生成 Glama.ai 提交格式"""
    return {
        "name": manifest.get("displayName", manifest.get("name", "")),
        "description": manifest.get("description", ""),
        "repository": manifest.get("repository", {}).get("url", ""),
        "homepage": manifest.get("homepage", ""),
        "license": manifest.get("license", "MIT"),
        "keywords": manifest.get("keywords", []),
        "categories": manifest.get("categories", []),
    }


def generate_mcp_so_data(manifest):
    """生成 MCP.so 提交格式"""
    return {
        "title": manifest.get("displayName", manifest.get("name", "")),
        "description": manifest.get("description", ""),
        "github_url": manifest.get("repository", {}).get("url", ""),
        "tags": manifest.get("keywords", []),
        "website": manifest.get("homepage", ""),
    }


def generate_awesome_pr_body(manifest):
    """生成 awesome-mcp-servers PR 描述"""
    name = manifest.get("displayName", manifest.get("name", "AIShield"))
    desc = manifest.get("description", "")
    repo = manifest.get("repository", {}).get("url", "")
    return f"""## Add {name}

{name} — {desc}

- **Repository**: {repo}
- **License**: {manifest.get("license", "MIT")}
- **Categories**: {', '.join(manifest.get("categories", ["security"]))}
- **Keywords**: {', '.join(manifest.get("keywords", [])[:5])}

### Features
- AI Agent security scanner for MCP tools
- Prompt injection detection
- OWASP MCP Top 10 aligned (133 rules)
- Native Chinese prompt detection
- Agent identity & trust system
- Built-in payment & credit system

### Installation
```json
{{
  "mcpServers": {{
    "aishield": {{
      "command": "npx",
      "args": ["-y", "@aishield/mcp-server"]
    }}
  }}
}}
```
"""


def check_smithery_status():
    """检查 Smithery.ai 配置状态"""
    yaml_path = os.path.join(BASE_DIR, "mcp-server", "smithery.yaml")
    if os.path.exists(yaml_path):
        return {"status": "configured", "file": yaml_path}
    return {"status": "missing", "file": yaml_path}


def _github_api_request(url, token, method="GET", data=None):
    """GitHub API 通用请求"""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "AIShield-Submission-Bot/1.0",
    }
    req = urllib.request.Request(url, headers=headers, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode("utf-8")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8")), resp.status
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode("utf-8")}, e.code
    except Exception as e:
        return {"error": str(e)}, 0


def submit_github_awesome(manifest, dry_run=True):
    """
    自动提交到 awesome-mcp-servers（需要 GITHUB_TOKEN）
    流程: Fork → 获取 README → 修改 → 提交 → 创建 PR
    """
    target_repo = "punkpeye/awesome-mcp-servers"
    target_owner = "punkpeye"
    target_name = "awesome-mcp-servers"
    
    if dry_run:
        print(f"\n📋 [GitHub Awesome MCP] 预览 PR 内容:")
        print(f"   目标仓库: {target_repo}")
        print(f"   修改: 在 README.md 的 Security 分类下添加一行")
        print(f"   PR 标题: Add AIShield — AI Agent security scanner")
        return {"status": "dry_run", "repo": target_repo}
    
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print(f"   ⚠️  缺少 GITHUB_TOKEN 环境变量，无法自动提交")
        print(f"   获取方式: https://github.com/settings/tokens (勾选 'repo' 权限)")
        return {"status": "failed", "reason": "missing GITHUB_TOKEN"}
    
    # 1. 获取当前用户
    user_data, status = _github_api_request("https://api.github.com/user", token)
    if status != 200:
        print(f"   ❌ GitHub API 认证失败: {user_data.get('error', 'unknown')}")
        return {"status": "failed", "reason": "auth_failed"}
    
    username = user_data.get("login", "")
    print(f"   ✅ GitHub 认证成功: @{username}")
    
    # 2. Fork 目标仓库
    print(f"   🍴 Forking {target_repo}...")
    fork_data, fork_status = _github_api_request(
        f"https://api.github.com/repos/{target_repo}/forks",
        token, method="POST"
    )
    if fork_status not in (200, 202):
        print(f"   ❌ Fork 失败: {fork_data.get('error', 'unknown')}")
        return {"status": "failed", "reason": "fork_failed"}
    
    fork_repo = fork_data.get("full_name", f"{username}/{target_name}")
    print(f"   ✅ Fork 成功: {fork_repo}")
    
    # 3. 获取 README 内容
    print(f"   📄 获取 README.md...")
    readme_data, readme_status = _github_api_request(
        f"https://api.github.com/repos/{fork_repo}/contents/README.md",
        token
    )
    if readme_status != 200:
        print(f"   ❌ 获取 README 失败: {readme_data.get('error', 'unknown')}")
        return {"status": "failed", "reason": "readme_fetch_failed"}
    
    import base64
    readme_content = base64.b64decode(readme_data.get("content", "")).decode("utf-8")
    readme_sha = readme_data.get("sha", "")
    
    # 4. 在 Security 分类下添加 AIShield
    display_name = manifest.get("displayName", manifest.get("name", "AIShield"))
    homepage = manifest.get("homepage", "https://aishield.tools")
    description = manifest.get("description", "AI Agent security scanner")
    new_line = f"- [{display_name}]({homepage}) — {description}\n"
    
    # 查找 Security 分类并插入
    security_marker = "### Security"
    if security_marker in readme_content:
        idx = readme_content.find(security_marker)
        # 找到该分类的下一个 ### 或在列表末尾插入
        next_section = readme_content.find("### ", idx + len(security_marker))
        if next_section == -1:
            readme_content += f"\n{new_line}"
        else:
            readme_content = readme_content[:next_section] + new_line + readme_content[next_section:]
    else:
        # 如果没有 Security 分类，在末尾添加
        readme_content += f"\n### Security\n\n{new_line}"
    
    # 5. 提交修改
    print(f"   ✏️  修改 README.md...")
    commit_data, commit_status = _github_api_request(
        f"https://api.github.com/repos/{fork_repo}/contents/README.md",
        token,
        method="PUT",
        data={
            "message": f"feat: add {display_name} to MCP servers list",
            "content": base64.b64encode(readme_content.encode("utf-8")).decode("utf-8"),
            "sha": readme_sha,
        }
    )
    if commit_status not in (200, 201):
        print(f"   ❌ 提交修改失败: {commit_data.get('error', 'unknown')}")
        return {"status": "failed", "reason": "commit_failed"}
    
    print(f"   ✅ README 修改已提交")
    
    # 6. 创建 PR
    print(f"   📬 创建 Pull Request...")
    pr_data, pr_status = _github_api_request(
        f"https://api.github.com/repos/{target_repo}/pulls",
        token,
        method="POST",
        data={
            "title": f"Add {display_name} — AI Agent security scanner",
            "body": generate_awesome_pr_body(manifest),
            "head": f"{username}:main",
            "base": "main",
        }
    )
    if pr_status not in (200, 201):
        print(f"   ❌ 创建 PR 失败: {pr_data.get('error', 'unknown')}")
        return {"status": "failed", "reason": "pr_failed"}
    
    pr_url = pr_data.get("html_url", "")
    print(f"   ✅ PR 创建成功: {pr_url}")
    return {"status": "submitted", "repo": target_repo, "pr_url": pr_url}


def run_submission(dry_run=True):
    """主流程：执行或预览所有平台提交"""
    manifest = load_mcp_manifest()
    submissions = _load_json(SUBMISSIONS_FILE, {"submissions": []})
    
    print("=" * 60)
    print("🚀 AIShield MCP 目录平台批量提交")
    print("=" * 60)
    print(f"📦 项目: {manifest.get('displayName', manifest.get('name', ''))}")
    print(f"🏠 主页: {manifest.get('homepage', '')}")
    print(f"📋 模式: {'预览 (dry-run)' if dry_run else '执行提交'}")
    print("=" * 60)
    
    results = []
    
    for key, platform in PLATFORMS.items():
        print(f"\n🔹 {platform['name']}")
        print(f"   方式: {platform['method']} | 自动: {'✅' if platform['auto'] else '👤'}")
        print(f"   链接: {platform['url']}")
        
        result = {
            "platform": key,
            "name": platform["name"],
            "timestamp": _now_iso(),
            "method": platform["method"],
        }
        
        if key == "smithery":
            status = check_smithery_status()
            result["status"] = status["status"]
            if status["status"] == "configured":
                print(f"   ✅ smithery.yaml 已配置，平台会自动抓取")
            else:
                print(f"   ❌ 缺少 smithery.yaml，请创建")
        
        elif key == "github_awesome":
            sub = submit_github_awesome(manifest, dry_run=dry_run)
            result["status"] = sub["status"]
        
        elif key in ("mcp_so", "glama", "pulsemcp"):
            if key == "mcp_so":
                data = generate_mcp_so_data(manifest)
            elif key == "glama":
                data = generate_glama_json(manifest)
            else:
                data = {"name": manifest.get("displayName", ""), "url": manifest.get("homepage", "")}
            
            print(f"   📋 提交数据预览:")
            for k, v in list(data.items())[:4]:
                v_str = str(v)[:50] + "..." if len(str(v)) > 50 else str(v)
                print(f"      {k}: {v_str}")
            result["status"] = "dry_run_preview" if dry_run else "manual_required"
        
        else:
            print(f"   👤 纯手动平台，请访问链接自行注册")
            result["status"] = "manual_only"
        
        results.append(result)
    
    # 保存结果
    if not dry_run:
        submissions["submissions"].extend(results)
        _save_json(SUBMISSIONS_FILE, submissions)
        print(f"\n💾 提交记录已保存到 {SUBMISSIONS_FILE}")
    
    # 输出总结
    print("\n" + "=" * 60)
    print("📊 提交总结")
    print("=" * 60)
    auto_count = sum(1 for r in results if r["status"] in ("configured", "submitted"))
    manual_count = len(results) - auto_count
    print(f"   自动/已配置: {auto_count}")
    print(f"   需手动操作: {manual_count}")
    print("\n📝 下一步操作:")
    print("   1. Smithery.ai — 确认 smithery.yaml 已推送，平台自动抓取")
    print("   2. MCP.so — 访问 https://mcp.so/submit 粘贴仓库地址")
    print("   3. Glama.ai — 访问 https://glama.ai/mcp/submit 提交")
    print("   4. PulseMCP — 访问 https://www.pulsemcp.com/submit 注册")
    print("   5. Awesome MCP — Fork 仓库后添加一行到 Security 分类")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    dry_run = "--submit" not in sys.argv
    if dry_run:
        print("💡 当前为预览模式，添加 --submit 执行实际提交\n")
    
    run_submission(dry_run=dry_run)
