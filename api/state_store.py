"""
api/state_store.py — 运行时状态持久化（H1 / S3 状态地基）

背景（2026-10-16 地基加固，H1/S3）:
  server.py 原 _save_json 直接 open(path,'w') 覆盖写活文件，**无原子性**：
  进程在写一半被 kill -9（或磁盘满），文件就损坏成半截 JSON，下次启动
  _load_json 抛异常 → 整服务起不来。且 35 个运行时 JSON 进 git，污染仓库、
  还可能把一份过期运行时快照当成种子下发到生产。

  本模块提供：
  1. 原子写：先写同目录临时文件 → fsync → os.replace（POSIX 原子重命名），
     中途崩溃最多留下一个 .tmp，活文件始终完整。
  2. 目录锁：同一目录的写串行，避免并发写互相撕咬（健康检查并发调用写同一文件）。
  3. 损坏自愈：_load_json 遇到坏 JSON 时备份坏文件（.corrupt-<ts>）、
     返回 default，不让一次损坏把服务卡死。
  4. 可选的 schema_version 校验：写入可带版本戳，读出版本不符视为不兼容、
     返回 default（向后不兼容的旧格式不被静默加载）。

设计约束：零第三方依赖（只用标准库），可被 api.server 直接 import，
不引入循环依赖。
"""

from __future__ import annotations

import json
import os
import threading
import time

# 按目录分发的写锁：同一目录的写串行，不同目录可并行。
_dir_locks: dict[str, threading.Lock] = {}
_global_lock = threading.Lock()


def _lock_for(directory: str) -> threading.Lock:
    with _global_lock:
        lock = _dir_locks.get(directory)
        if lock is None:
            lock = threading.Lock()
            _dir_locks[directory] = lock
        return lock


def save_json(path: str, data, *, fsync: bool = True, tmp_suffix: str = ".tmp") -> None:
    """原子写 JSON：临时文件 → fsync → os.replace。

    中途崩溃最多留下一个 .tmp 文件，活文件始终完整。
    """
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    tmp = f"{path}{tmp_suffix}"
    with _lock_for(directory):
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
            if fsync:
                fh.flush()
                os.fsync(fh.fileno())
        os.replace(tmp, path)


def load_json(path: str, default=None, *, schema_version=None,
              schema_key: str = "schema_version"):
    """读取 JSON；损坏则备份坏文件并自愈返回 default。

    schema_version 非 None 时，读出顶层 schema_version 与之一致才返回，
    否则视为不兼容旧格式、返回 default（不静默加载坏/旧数据）。
    """
    if default is None:
        default = {}
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (ValueError, OSError):
        # 损坏自愈：备份后返回 default，绝不让一次坏文件卡死服务。
        _backup_corrupt(path)
        return default
    if schema_version is not None:
        if data.get(schema_key) != schema_version:
            return default
    return data


def _backup_corrupt(path: str) -> None:
    """把损坏文件改名备份，避免 os.replace 覆盖丢失现场（仅供排查）。"""
    try:
        if not os.path.exists(path):
            return
        ts = time.strftime("%Y%m%d-%H%M%S")
        dst = f"{path}.corrupt-{ts}"
        # 同秒多次损坏时直接覆盖旧备份，不堆积。
        os.replace(path, dst)
    except OSError:
        pass
