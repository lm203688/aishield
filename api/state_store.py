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

# 进程内锁：按目录分发的写锁，同目录写串行、不同目录并行。
_dir_locks: dict[str, threading.Lock] = {}
_global_lock = threading.Lock()


def _lock_for(directory: str) -> threading.Lock:
    with _global_lock:
        lock = _dir_locks.get(directory)
        if lock is None:
            lock = threading.Lock()
            _dir_locks[directory] = lock
        return lock


# 跨进程锁：threading.Lock 只在单进程内有效。Railway / Render 常见多 worker
# 部署，两个进程同时写同一个 JSON 时，后写的 os.replace 会静默覆盖先写的
# —— 丢更新，且不报任何错。用一个旁路 .lock 文件承载 advisory 锁
# （POSIX fcntl / Windows msvcrt），跨进程互斥；崩溃进程持锁会自动由内核释放，
# 不会留死锁。文件锁是「软互斥」：只有本模块的写者遵守它，故它是对原子写
# 的补强而非替代，两把锁都要留。
class _FileLock:
    """跨进程 advisory 互斥锁（标准库实现，零第三方依赖）。

    用法：`with file_lock(dir) as fh: ...`。POSIX 下用 fcntl.flock 独占阻塞锁；
    Windows 下用 msvcrt.locking 锁 1 字节（必须持 open 句柄，故锁句柄由调用方
    在 with 块内自行管理，本类只负责加/解锁与超时退避）。
    """

    def __init__(self, directory: str, *, timeout: float = 30.0, poll: float = 0.05):
        self.path = os.path.join(directory, ".state_write.lock")
        self.timeout = timeout
        self.poll = poll
        self._fh = None

    def acquire(self) -> bool:
        deadline = time.monotonic() + self.timeout
        while True:
            fh = open(self.path, "a+b")
            try:
                fh.seek(0)
                fh.write(b"\0")
            except OSError:
                fh.close()
                fh = None
            if fh is not None and _try_lock(fh):
                # 锁已持有：句柄必须保持打开直到 release()（flock 绑在
                # open file description 上，提前 close 等于提前解锁）。
                self._fh = fh
                return True
            if fh is not None:
                try:
                    fh.close()
                except OSError:
                    pass
            if time.monotonic() >= deadline:
                return False
            time.sleep(self.poll)

    def release(self) -> None:
        fh = self._fh
        self._fh = None
        if fh is None:
            return
        try:
            _unlock(fh)
        except OSError:
            pass
        try:
            fh.close()
        except OSError:
            pass

    def __enter__(self):
        if not self.acquire():
            raise TimeoutError(
                f"state write lock timed out after {self.timeout}s: {self.path}")
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()
        return False


def _try_lock(fh) -> bool:
    """尽力加锁；不支持平台返回 True（退化为仅进程内互斥）。"""
    try:
        import fcntl  # POSIX
    except ImportError:
        try:
            import msvcrt  # Windows
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            return True
        except (ImportError, OSError):
            return True
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError:
        return False


def _unlock(fh) -> None:
    try:
        import fcntl
        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        return
    except ImportError:
        pass
    try:
        import msvcrt
        fh.seek(0)
        msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
    except (ImportError, OSError):
        pass


def file_lock(directory: str) -> _FileLock:
    """取得跨进程写锁（同一目录下所有 state 文件共用一把）。"""
    return _FileLock(directory)


def save_json(path: str, data, *, fsync: bool = True, tmp_suffix: str = ".tmp",
              cross_process: bool = True) -> None:
    """原子写 JSON：临时文件 → fsync → os.replace。

    中途崩溃最多留下一个 .tmp 文件，活文件始终完整。
    cross_process=True 时在进程内锁之外再加一把跨进程文件锁，覆盖多 worker
    部署（见模块内 `_FileLock` 的说明）。
    """
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    tmp = f"{path}{tmp_suffix}"
    with _lock_for(directory):
        if cross_process:
            with file_lock(directory):
                _write_atomic(path, tmp, data, fsync)
        else:
            _write_atomic(path, tmp, data, fsync)


def _write_atomic(path: str, tmp: str, data, fsync: bool) -> None:
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
