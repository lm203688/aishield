"""
eco/credentials.py — 统一凭证装载器（密钥绝不进仓库）

AIShield 是安全产品，仓库为 public。任何真实密钥（支付 AppSecret、PAT、API Key）
一律通过下列渠道注入，**代码里只有键名，没有值**：

装载优先级（先命中先用）：
  1. 环境变量                       —— 生产/CI 首选
  2. $AISHIELD_SECRETS_FILE 指向的 JSON
  3. <repo>/.secrets.json           —— 本地开发（已 gitignore）
  4. ~/.aishield/secrets.json       —— 跨项目共用（在仓库之外）

安全约定：
  - 任何对外输出（日志、API 响应、异常）都必须用 mask() 脱敏；
  - describe() 只回报"是否已配置 + 掩码指纹"，永不回传明文；
  - 文件缓存带 mtime 失效，改完密钥无需重启。
"""
from __future__ import annotations

import hashlib
import json
import os
import threading

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: 按优先级排列的本地私密文件候选路径
SECRET_FILE_CANDIDATES = [
    os.environ.get("AISHIELD_SECRETS_FILE", ""),
    os.path.join(_BASE, ".secrets.json"),
    os.path.join(os.path.expanduser("~"), ".aishield", "secrets.json"),
]

_lock = threading.Lock()
_cache = {"path": None, "mtime": 0.0, "data": {}}


def _load_secret_file():
    """读取第一个存在的私密文件；按 mtime 缓存，改动自动生效。"""
    for path in SECRET_FILE_CANDIDATES:
        if not path or not os.path.exists(path):
            continue
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            continue
        with _lock:
            if _cache["path"] == path and _cache["mtime"] == mtime:
                return _cache["data"]
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    data = {}
            except Exception:
                data = {}
            _cache.update({"path": path, "mtime": mtime, "data": data})
            return data
    return {}


def get(name, default=""):
    """取一个凭证。环境变量优先，其次本地私密文件。

    私密文件同时支持扁平键（"HUPIJIAO_APPID"）与分组键
    （{"hupijiao": {"appid": ...}}），后者用小写下划线命名。
    """
    val = os.environ.get(name)
    if val:
        return val

    data = _load_secret_file()
    if name in data and data[name]:
        return data[name]

    # 分组回退： HUPIJIAO_APP_SECRET -> data["hupijiao"]["app_secret"]
    lowered = name.lower()
    for group, payload in data.items():
        if not isinstance(payload, dict):
            continue
        prefix = group.lower() + "_"
        if lowered.startswith(prefix):
            key = lowered[len(prefix):]
            if payload.get(key):
                return payload[key]
    return default


def get_many(*names):
    """批量取值，返回 dict。"""
    return {n: get(n) for n in names}


def is_configured(*names):
    """所有给定键都非空才算已配置。"""
    return all(bool(get(n)) for n in names)


def mask(value, keep=4):
    """脱敏：保留首尾各 keep 位，中间打码。空值返回空串。"""
    if not value:
        return ""
    s = str(value)
    if len(s) <= keep * 2:
        return "*" * len(s)
    return f"{s[:keep]}{'*' * (len(s) - keep * 2)}{s[-keep:]}"


def fingerprint(value):
    """密钥指纹（sha256 前 8 位），用于确认"换没换密钥"而不泄露内容。"""
    if not value:
        return ""
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:8]


def describe(*names):
    """回报配置状态，**永不含明文**。可安全放进 API 响应与日志。"""
    out = {}
    for n in names:
        v = get(n)
        out[n] = {
            "configured": bool(v),
            "masked": mask(v),
            "fingerprint": fingerprint(v),
            "source": "env" if os.environ.get(n) else ("file" if v else "missing"),
        }
    return out


def active_secret_file():
    """返回当前生效的私密文件路径（用于排障），不含内容。"""
    for path in SECRET_FILE_CANDIDATES:
        if path and os.path.exists(path):
            return path
    return None


if __name__ == "__main__":
    print("secrets file:", active_secret_file() or "(none)")
    print(json.dumps(
        describe("HUPIJIAO_APPID", "HUPIJIAO_APP_SECRET", "X402_PAY_TO"),
        ensure_ascii=False, indent=2))
