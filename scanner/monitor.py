"""
AIShield 持续监控模块 — scanner/monitor.py

功能：
  - check_version_change(source_url): 获取GitHub仓库最新commit date和version，与上次扫描对比
  - get_monitored_tools(): 获取当前监控列表
  - add_monitor(source_url): 添加工具到监控列表
  - remove_monitor(source_url): 从监控列表中移除工具
  - check_all_monitored(): 检查所有监控中的工具是否有变更

数据存储: data/monitored_tools.json
"""

import json
import os
import re
import threading
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

# ── 数据存储路径 ──
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
MONITOR_FILE = os.path.join(DATA_DIR, "monitored_tools.json")

# ── 线程安全锁 ──
_lock = threading.Lock()

# ── 时区设置（北京时间）──
TZ = timezone(timedelta(hours=8))


def _load_monitor_data():
    """加载监控数据"""
    if os.path.exists(MONITOR_FILE):
        try:
            with open(MONITOR_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"tools": {}, "version": "1.0"}


def _save_monitor_data(data):
    """保存监控数据（线程安全）"""
    with _lock:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(MONITOR_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def _normalize_url(source_url):
    """标准化URL：去除尾部斜杠，转小写"""
    return source_url.strip().rstrip("/").lower()


def _extract_repo_info(source_url):
    """从GitHub URL中提取owner和repo"""
    parsed = urlparse(source_url)
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) >= 2:
        owner, repo = path_parts[0], path_parts[1]
        repo = re.sub(r"\.git$", "", repo)  # 去除.git后缀
        return owner, repo
    return None, None


def get_monitored_tools():
    """
    获取当前监控中的工具列表

    返回:
        list: 监控中的工具列表，每个元素包含：
            - source_url: GitHub仓库地址
            - name: 工具名称
            - last_version: 上次扫描时的版本
            - last_commit: 上次扫描时的最新commit date
            - added_at: 添加监控的时间
            - last_checked: 上次检查的时间
    """
    data = _load_monitor_data()
    tools = []
    for url, info in data.get("tools", {}).items():
        tools.append({
            "source_url": url,
            "name": info.get("name", ""),
            "last_version": info.get("last_version", ""),
            "last_commit": info.get("last_commit", ""),
            "added_at": info.get("added_at", ""),
            "last_checked": info.get("last_checked", ""),
        })
    return tools


def add_monitor(source_url, name=None):
    """
    添加工具到监控列表

    参数:
        source_url (str): GitHub仓库地址
        name (str, optional): 工具自定义名称

    返回:
        dict: 添加结果
    """
    if not source_url:
        return {"success": False, "error": "source_url is required"}

    normalized = _normalize_url(source_url)
    data = _load_monitor_data()

    # 如果已存在，更新名称
    if normalized in data.get("tools", {}):
        data["tools"][normalized]["name"] = name or data["tools"][normalized].get("name", "")
        _save_monitor_data(data)
        return {"success": True, "message": "工具已在监控列表中，已更新名称", "source_url": normalized}

    # 尝试从URL推断名称
    owner, repo = _extract_repo_info(source_url)
    tool_name = name or repo or "unknown"

    data.setdefault("tools", {})[normalized] = {
        "name": tool_name,
        "last_version": "",
        "last_commit": "",
        "added_at": datetime.now(TZ).isoformat(),
        "last_checked": "",
    }

    _save_monitor_data(data)
    return {"success": True, "message": f"已添加 {tool_name} 到监控列表", "source_url": normalized, "name": tool_name}


def remove_monitor(source_url):
    """
    从监控列表中移除工具

    参数:
        source_url (str): GitHub仓库地址

    返回:
        dict: 移除结果
    """
    if not source_url:
        return {"success": False, "error": "source_url is required"}

    normalized = _normalize_url(source_url)
    data = _load_monitor_data()

    if normalized not in data.get("tools", {}):
        return {"success": False, "error": "工具不在监控列表中", "source_url": normalized}

    removed_name = data["tools"][normalized].get("name", "")
    del data["tools"][normalized]
    _save_monitor_data(data)
    return {"success": True, "message": f"已从监控列表移除 {removed_name}", "source_url": normalized}


def check_version_change(source_url):
    """
    检查GitHub仓库是否有版本变更

    获取最新commit date和version，与上次扫描结果对比。

    参数:
        source_url (str): GitHub仓库地址

    返回:
        dict: 变更信息，格式：
            {
                "tool": "xxx",
                "source_url": "https://github.com/xxx/xxx",
                "previous_version": "1.0",
                "current_version": "1.1",
                "previous_commit": "2025-01-01T00:00:00",
                "last_commit": "2025-01-15T00:00:00",
                "has_changes": true,
                "checked_at": "2025-01-15T12:00:00+08:00"
            }
    """
    import urllib.request

    if not source_url:
        return {"error": "source_url is required"}

    normalized = _normalize_url(source_url)
    owner, repo = _extract_repo_info(source_url)
    if not owner or not repo:
        return {"error": f"无法从URL解析仓库信息: {source_url}"}

    # 获取仓库最新commit信息（GitHub API，无需认证的公开仓库）
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=1"
    current_commit = ""
    current_version = ""

    try:
        req = urllib.request.Request(api_url)
        req.add_header("User-Agent", "AIShield-Monitor/4.1")
        req.add_header("Accept", "application/vnd.github.v3+json")

        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                commits = json.loads(resp.read().decode("utf-8"))
                if commits:
                    current_commit = commits[0].get("commit", {}).get("committer", {}).get("date", "")
    except Exception as e:
        return {"error": f"获取commit信息失败: {str(e)}"}

    # 获取最新release版本号
    try:
        release_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        req2 = urllib.request.Request(release_url)
        req2.add_header("User-Agent", "AIShield-Monitor/4.1")
        req2.add_header("Accept", "application/vnd.github.v3+json")

        with urllib.request.urlopen(req2, timeout=10) as resp:
            if resp.status == 200:
                release = json.loads(resp.read().decode("utf-8"))
                current_version = release.get("tag_name", "") or release.get("name", "")
    except Exception:
        # 没有release也是正常的，使用commit date作为版本标识
        if not current_version:
            current_version = current_commit[:10] if current_commit else "unknown"

    # 从监控数据中获取上次的值
    data = _load_monitor_data()
    tool_info = data.get("tools", {}).get(normalized, {})
    previous_version = tool_info.get("last_version", "")
    previous_commit = tool_info.get("last_commit", "")
    tool_name = tool_info.get("name", repo)

    # 判断是否有变更
    has_changes = (current_version != previous_version) or (current_commit != previous_commit)

    # 更新监控数据
    if normalized in data.get("tools", {}):
        data["tools"][normalized]["last_version"] = current_version
        data["tools"][normalized]["last_commit"] = current_commit
        data["tools"][normalized]["last_checked"] = datetime.now(TZ).isoformat()
        _save_monitor_data(data)

    return {
        "tool": tool_name,
        "source_url": normalized,
        "previous_version": previous_version or "N/A",
        "current_version": current_version or "N/A",
        "previous_commit": previous_commit or "N/A",
        "last_commit": current_commit or "N/A",
        "has_changes": has_changes,
        "checked_at": datetime.now(TZ).isoformat(),
    }


def check_all_monitored():
    """
    检查所有监控中的工具是否有变更

    返回:
        list: 所有监控工具的变更结果列表
    """
    data = _load_monitor_data()
    results = []

    for source_url in list(data.get("tools", {}).keys()):
        result = check_version_change(source_url)
        # 只返回成功的检查结果
        if "error" not in result:
            results.append(result)
        else:
            results.append({
                "tool": data["tools"][source_url].get("name", source_url),
                "source_url": source_url,
                "error": result.get("error", "检查失败"),
                "has_changes": False,
            })

    return results
