"""
eco/sandbox.py — 安全沙箱执行

功能:
  - SandboxTask:          Agent代码任务提交与管理
      submit / get_task / list_tasks / cancel_task / execute_pending / get_task_result
      安全预检查: os.system, subprocess, eval, exec 等危险模式
      language: "python" / "javascript" / "shell"
      status: "queued" / "running" / "completed" / "failed" / "timeout" / "rejected"
  - LocalExecutor:        本地代码执行器
      Python → subprocess.run(["python", tmp])
      JavaScript → subprocess.run(["node", "-e", code])
      Shell → subprocess.run(["powershell", "-Command", code])
  - SandboxSecurityInspector: 执行结果安全审查
  - 数据持久化: api/data/sandbox_tasks.json

API路由:
  POST /api/v1/sandbox/submit           — 提交沙箱任务
  GET  /api/v1/sandbox/tasks            — 列出任务
  GET  /api/v1/sandbox/tasks/{task_id}  — 查询任务详情
  POST /api/v1/sandbox/cancel/{task_id} — 取消任务
  GET  /api/v1/sandbox/result/{task_id} — 获取任务结果
"""

import json
import os
import re
import time
import uuid
import subprocess
import tempfile
import threading
from datetime import datetime, timezone, timedelta

# ── 路径配置 ──
# 数据目录: api/data/（相对于项目根目录）
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_BASE_DIR, "api", "data")
SANDBOX_TASKS_FILE = os.path.join(_DATA_DIR, "sandbox_tasks.json")

TZ = timezone(timedelta(hours=8))
_lock = threading.Lock()


# ══════════════════════════════════════════════
#  工具函数
# ══════════════════════════════════════════════

def _load_json(path, default=None):
    """加载JSON文件，失败返回默认值"""
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
    """线程安全地保存JSON文件"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def _ensure_data_dir():
    """确保数据目录存在"""
    os.makedirs(_DATA_DIR, exist_ok=True)


def _now_iso():
    """返回当前时间的ISO格式字符串"""
    return datetime.now(TZ).isoformat()


def _generate_task_id():
    """生成任务ID"""
    return f"sbox-{uuid.uuid4().hex[:12]}"


# ══════════════════════════════════════════════
#  危险模式定义
# ══════════════════════════════════════════════

# 各语言危险模式（正则列表）
DANGEROUS_PATTERNS = {
    "python": [
        (r"\bos\.(system|popen|execvp|spawnl)\b", "os.system / os.popen — 可执行任意系统命令"),
        (r"\bsubprocess\.(run|call|Popen|check_output)\b", "subprocess — 可执行外部进程"),
        (r"\beval\s*\(", "eval() — 可执行任意表达式"),
        (r"\bexec\s*\(", "exec() — 可执行任意代码"),
        (r"\b__import__\s*\(", "__import__() — 可动态导入恶意模块"),
        (r"\bcompile\s*\(", "compile() — 可编译任意代码"),
        (r"\bglobals\(\s*\)\s*\[", "globals()['key'] — 可读写全局变量"),
        (r"\bgetattr\s*\(.*,\s*['\"]__", "getattr 绕过属性访问控制"),
        (r"\bopen\s*\(.*/", "open() 路径遍历风险"),
        (r"\bshutil\.(rmtree|copy|move)\b", "shutil 文件操作 — 可能破坏文件系统"),
        (r"\bos\.(remove|unlink|rmdir)\b", "os.remove — 可删除文件"),
        (r"\bos\.(chmod|chown)\b", "os.chmod — 可修改权限"),
        (r"\bsignal\.(alarm|kill)\b", "signal — 可发送信号"),
        (r"\bctypes\b", "ctypes — 可调用C函数绕过沙箱"),
        (r"\bpickle\.(loads|load)\b", "pickle — 反序列化可执行任意代码"),
    ],
    "javascript": [
        (r"\brequire\s*\(\s*['\"]child_process['\"]\)", "require('child_process') — 可执行系统命令"),
        (r"\brequire\s*\(\s*['\"]fs['\"]\)", "require('fs') — 可读写文件系统"),
        (r"\beval\s*\(", "eval() — 可执行任意代码"),
        (r"\bFunction\s*\(", "Function() — 动态创建函数执行代码"),
        (r"\bprocess\.(exit|kill|chdir)\b", "process.* — 可操控进程"),
        (r"\brequire\s*\(\s*['\"]net['\"]\)", "require('net') — 可创建网络连接"),
        (r"\brequire\s*\(\s*['\"]os['\"]\)", "require('os') — 可操作系统接口"),
        (r"\bglobal\b", "global — 可访问全局对象"),
        (r"\bBuffer\s*\(", "Buffer() — 可操作原始内存"),
    ],
    "shell": [
        (r"\brm\s+(-rf|-r)\b", "rm -rf — 可删除文件/目录"),
        (r"\bchmod\s+777\b", "chmod 777 — 过度开放权限"),
        (r"\bcurl\b.*\|\s*\b(sh|bash|powershell)\b", "curl | sh — 远程代码执行"),
        (r"\bwget\b.*\|\s*\b(sh|bash|powershell)\b", "wget | sh — 远程代码执行"),
        (r"\bformat\b.*[/\\]\b", "format — 可格式化磁盘"),
        (r"\bshutdown\b", "shutdown — 可关机"),
        (r"\breg\s+delete\b", "reg delete — 可删除注册表"),
        (r"\btaskkill\b", "taskkill — 可终止进程"),
        (r"\bnet\s+user\b", "net user — 可创建/修改用户"),
        (r"\bNew-Item\b.*-ItemType\s+Service\b", "New-Item Service — 可创建系统服务"),
    ],
}


# ══════════════════════════════════════════════
#  本地执行器
# ══════════════════════════════════════════════

class LocalExecutor:
    """
    本地代码执行器
    支持 Python / JavaScript / Shell 的安全执行
    """

    # 敏感信息正则（用于输出清理）
    _SENSITIVE_PATTERNS = [
        (re.compile(r'(api[_-]?key|apikey|api_secret)["\s]*[:=]["\s]*["\']?[\w\-]{20,}["\']?', re.IGNORECASE), "[API_KEY_REDACTED]"),
        (re.compile(r'(password|passwd|pwd)["\s]*[:=]["\s]*["\']?[\w\-@#$%^&*!]{8,}["\']?', re.IGNORECASE), "[PASSWORD_REDACTED]"),
        (re.compile(r'(token|access_token|auth_token)["\s]*[:=]["\s]*["\']?[\w\-\.]{20,}["\']?', re.IGNORECASE), "[TOKEN_REDACTED]"),
        (re.compile(r'(secret|secret_key)["\s]*[:=]["\s]*["\']?[\w\-]{20,}["\']?', re.IGNORECASE), "[SECRET_REDACTED]"),
        (re.compile(r'(private_key|priv_key)["\s]*[:=]["\s]*["\']?[\w\-+/=\n]{40,}["\']?', re.IGNORECASE), "[PRIVATE_KEY_REDACTED]"),
    ]

    def _pre_check_code(self, code, language):
        """
        安全预检查代码中的危险模式

        Args:
            code (str):      待检查的代码
            language (str):  编程语言

        Returns:
            tuple: (is_safe, findings)
                is_safe (bool):    是否安全
                findings (list):   发现的危险模式列表
        """
        patterns = DANGEROUS_PATTERNS.get(language, [])
        findings = []

        for pattern, description in patterns:
            matches = re.findall(pattern, code)
            if matches:
                findings.append({
                    "pattern": pattern,
                    "description": description,
                    "match_count": len(matches),
                })

        return (len(findings) == 0, findings)

    def _sanitize_output(self, output):
        """
        清理输出中的敏感信息

        Args:
            output (str): 原始输出

        Returns:
            str: 清理后的输出
        """
        sanitized = output
        for pattern, replacement in self._SENSITIVE_PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized

    def execute(self, task_id, code, language, timeout,
                resource_limits=None, env_vars=None):
        """
        执行代码任务

        Args:
            task_id (str):         任务ID
            code (str):            代码内容
            language (str):        编程语言 (python/javascript/shell)
            timeout (int):         超时秒数
            resource_limits (dict): 资源限制（预留）
            env_vars (dict):       环境变量

        Returns:
            dict: {"exit_code", "stdout", "stderr", "duration_ms"}
        """
        env_vars = env_vars or {}
        start_time = time.time()

        try:
            if language == "python":
                result = self._execute_python(code, timeout, env_vars)
            elif language == "javascript":
                result = self._execute_javascript(code, timeout, env_vars)
            elif language == "shell":
                result = self._execute_shell(code, timeout, env_vars)
            else:
                result = {
                    "exit_code": -1,
                    "stdout": "",
                    "stderr": f"不支持的语言: {language}",
                }
        except subprocess.TimeoutExpired:
            duration_ms = int((time.time() - start_time) * 1000)
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"执行超时 ({timeout}秒)",
                "duration_ms": duration_ms,
                "timed_out": True,
            }
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"执行异常: {str(e)}",
                "duration_ms": duration_ms,
            }

        duration_ms = int((time.time() - start_time) * 1000)
        result["duration_ms"] = duration_ms

        # 清理敏感信息
        result["stdout"] = self._sanitize_output(result.get("stdout", ""))
        result["stderr"] = self._sanitize_output(result.get("stderr", ""))

        return result

    def _execute_python(self, code, timeout, env_vars):
        """执行Python代码（写入临时.py文件后运行）"""
        env = os.environ.copy()
        env.update({str(k): str(v) for k, v in env_vars.items()})

        # 限制Python的环境变量以增强安全性
        env.pop("PYTHONPATH", None)
        env["PYTHONDONTWRITEBYTECODE"] = "1"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        try:
            proc = subprocess.run(
                ["python", tmp_path],
                timeout=timeout,
                capture_output=True,
                text=True,
                env=env,
            )
            return {
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }
        finally:
            # 清理临时文件
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def _execute_javascript(self, code, timeout, env_vars):
        """执行JavaScript代码（通过node -e）"""
        env = os.environ.copy()
        env.update({str(k): str(v) for k, v in env_vars.items()})

        proc = subprocess.run(
            ["node", "-e", code],
            timeout=timeout,
            capture_output=True,
            text=True,
            env=env,
        )
        return {
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }

    def _execute_shell(self, code, timeout, env_vars):
        """执行Shell命令（Windows环境使用powershell）"""
        env = os.environ.copy()
        env.update({str(k): str(v) for k, v in env_vars.items()})

        proc = subprocess.run(
            ["powershell", "-Command", code],
            timeout=timeout,
            capture_output=True,
            text=True,
            env=env,
        )
        return {
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }


# ══════════════════════════════════════════════
#  安全审查器
# ══════════════════════════════════════════════

class SandboxSecurityInspector:
    """
    沙箱执行结果安全审查器
    检查执行结果中是否存在安全风险
    """

    # 执行结果中的危险模式
    _OUTPUT_RISK_PATTERNS = [
        (re.compile(r"(?:password|passwd|pwd)\s*[:=]\s*\S+", re.IGNORECASE), "high", "输出包含密码明文"),
        (re.compile(r"(?:api[_-]?key|apikey)\s*[:=]\s*\S+", re.IGNORECASE), "high", "输出包含API Key"),
        (re.compile(r"(?:token|secret|credential)\s*[:=]\s*\S+", re.IGNORECASE), "high", "输出包含凭据信息"),
        (re.compile(r"(?:private_key|priv_key)\s*[:=]\s*\S+", re.IGNORECASE), "critical", "输出包含私钥"),
        (re.compile(r"(?:\d{1,3}\.){3}\d{1,3}", re.IGNORECASE), "low", "输出包含IP地址"),
        (re.compile(r"(?:C:\\|D:\\|/home/|/etc/)", re.IGNORECASE), "medium", "输出包含文件路径"),
        (re.compile(r"(?:connection refused|permission denied|access denied)", re.IGNORECASE), "medium", "输出包含系统错误信息"),
    ]

    def inspect_result(self, task_id, execution_result):
        """
        审查执行结果的安全性

        Args:
            task_id (str):            任务ID
            execution_result (dict):  执行结果 {exit_code, stdout, stderr, duration_ms}

        Returns:
            dict: {"safe", "risk_level", "findings", "sanitized_output"}
        """
        findings = []
        combined_output = execution_result.get("stdout", "") + execution_result.get("stderr", "")

        for pattern, severity, description in self._OUTPUT_RISK_PATTERNS:
            matches = pattern.findall(combined_output)
            if matches:
                findings.append({
                    "severity": severity,
                    "description": description,
                    "match_count": len(matches),
                    "sample": matches[0][:80],
                })

        # 确定风险等级
        if not findings:
            risk_level = "safe"
            safe = True
        elif any(f["severity"] == "critical" for f in findings):
            risk_level = "critical"
            safe = False
        elif any(f["severity"] == "high" for f in findings):
            risk_level = "high"
            safe = False
        elif any(f["severity"] == "medium" for f in findings):
            risk_level = "medium"
            safe = False
        else:
            risk_level = "low"
            safe = True

        # 清理输出
        sanitized_output = combined_output
        for pattern, _, _ in self._OUTPUT_RISK_PATTERNS:
            sanitized_output = pattern.sub("[REDACTED]", sanitized_output)

        return {
            "task_id": task_id,
            "safe": safe,
            "risk_level": risk_level,
            "findings": findings,
            "sanitized_output": sanitized_output,
        }


# ══════════════════════════════════════════════
#  沙箱任务管理
# ══════════════════════════════════════════════

class SandboxTask:
    """
    沙箱任务管理器
    负责代码任务的提交、执行、查询和管理
    """

    def __init__(self):
        self._tasks = {}
        self._results = {}
        self._executor = LocalExecutor()
        self._inspector = SandboxSecurityInspector()

    def _load(self):
        """从磁盘加载任务数据"""
        data = _load_json(SANDBOX_TASKS_FILE, {"tasks": {}, "results": {}})
        self._tasks = data.get("tasks", {})
        self._results = data.get("results", {})

    def _save(self):
        """持久化任务数据到磁盘"""
        _ensure_data_dir()
        _save_json(SANDBOX_TASKS_FILE, {
            "tasks": self._tasks,
            "results": self._results,
        })

    def submit(self, agent_id, code, language, timeout_seconds=30,
               environment_vars=None, resource_limits=None):
        """
        提交沙箱执行任务

        Args:
            agent_id (str):           Agent ID
            code (str):               代码内容
            language (str):           编程语言 (python/javascript/shell)
            timeout_seconds (int):    超时时间（秒）
            environment_vars (dict):   环境变量
            resource_limits (dict):    资源限制

        Returns:
            dict: {"task_id", "status", "findings"}
        """
        self._load()

        # 验证语言
        supported_languages = ("python", "javascript", "shell")
        if language not in supported_languages:
            raise ValueError(f"不支持的语言: {language}，支持: {supported_languages}")

        # 安全预检查
        is_safe, pre_findings = self._executor._pre_check_code(code, language)

        task_id = _generate_task_id()

        if not is_safe:
            # 危险代码，拒绝执行
            task = {
                "task_id": task_id,
                "agent_id": agent_id,
                "code": code,
                "language": language,
                "timeout_seconds": timeout_seconds,
                "environment_vars": environment_vars or {},
                "resource_limits": resource_limits or {},
                "status": "rejected",
                "security_findings": pre_findings,
                "submitted_at": _now_iso(),
                "updated_at": _now_iso(),
            }
            self._tasks[task_id] = task
            self._save()

            return {
                "task_id": task_id,
                "status": "rejected",
                "reason": "代码包含危险模式",
                "security_findings": pre_findings,
            }

        # 创建任务（状态: queued）
        task = {
            "task_id": task_id,
            "agent_id": agent_id,
            "code": code,
            "language": language,
            "timeout_seconds": timeout_seconds,
            "environment_vars": environment_vars or {},
            "resource_limits": resource_limits or {},
            "status": "queued",
            "security_findings": [],
            "submitted_at": _now_iso(),
            "updated_at": _now_iso(),
        }

        self._tasks[task_id] = task
        self._save()

        return {
            "task_id": task_id,
            "status": "queued",
        }

    def get_task(self, task_id):
        """
        查询任务详情

        Args:
            task_id (str): 任务ID

        Returns:
            dict | None: 任务信息
        """
        self._load()
        return self._tasks.get(task_id)

    def list_tasks(self, agent_id=None, status=None, page=1):
        """
        列出任务（支持筛选和分页）

        Args:
            agent_id (str, opt):  按Agent ID筛选
            status (str, opt):    按状态筛选
            page (int):           页码（从1开始）

        Returns:
            dict: {"tasks", "total", "page", "page_size"}
        """
        self._load()

        page_size = 20
        tasks = list(self._tasks.values())

        # 筛选
        if agent_id:
            tasks = [t for t in tasks if t.get("agent_id") == agent_id]
        if status:
            tasks = [t for t in tasks if t.get("status") == status]

        # 按提交时间倒序
        tasks.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)

        total = len(tasks)
        start = (page - 1) * page_size
        end = start + page_size
        tasks_page = tasks[start:end]

        return {
            "tasks": tasks_page,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def cancel_task(self, task_id, agent_id):
        """
        取消任务

        Args:
            task_id (str):  任务ID
            agent_id (str): Agent ID（用于权限验证）

        Returns:
            bool: 是否取消成功
        """
        self._load()

        task = self._tasks.get(task_id)
        if not task:
            return False

        # 验证Agent归属
        if task.get("agent_id") != agent_id:
            return False

        # 只有 queued 或 running 状态可取消
        if task["status"] not in ("queued", "running"):
            return False

        task["status"] = "cancelled"
        task["updated_at"] = _now_iso()
        self._tasks[task_id] = task
        self._save()

        return True

    def execute_pending(self, task_id):
        """
        执行待处理任务

        Args:
            task_id (str): 任务ID

        Returns:
            dict: 执行结果
        """
        self._load()

        task = self._tasks.get(task_id)
        if not task:
            return {"error": f"任务 {task_id} 不存在"}

        if task["status"] not in ("queued",):
            return {"error": f"任务状态为 {task['status']}，不可执行"}

        # 更新状态为 running
        task["status"] = "running"
        task["updated_at"] = _now_iso()
        self._tasks[task_id] = task
        self._save()

        # 执行代码
        exec_result = self._executor.execute(
            task_id=task_id,
            code=task["code"],
            language=task["language"],
            timeout=task.get("timeout_seconds", 30),
            resource_limits=task.get("resource_limits"),
            env_vars=task.get("environment_vars"),
        )

        # 更新任务状态
        if exec_result.get("timed_out"):
            task["status"] = "timeout"
        elif exec_result["exit_code"] == 0:
            task["status"] = "completed"
        else:
            task["status"] = "failed"

        task["updated_at"] = _now_iso()
        self._tasks[task_id] = task

        # 安全审查
        inspection = self._inspector.inspect_result(task_id, exec_result)

        # 保存结果
        self._results[task_id] = {
            "task_id": task_id,
            "exit_code": exec_result.get("exit_code"),
            "stdout": exec_result.get("stdout", ""),
            "stderr": exec_result.get("stderr", ""),
            "duration_ms": exec_result.get("duration_ms", 0),
            "timed_out": exec_result.get("timed_out", False),
            "security_inspection": inspection,
            "completed_at": _now_iso(),
        }

        self._save()

        return {
            "task_id": task_id,
            "status": task["status"],
            "exit_code": exec_result.get("exit_code"),
            "duration_ms": exec_result.get("duration_ms", 0),
            "security_inspection": {
                "safe": inspection["safe"],
                "risk_level": inspection["risk_level"],
                "findings_count": len(inspection["findings"]),
            },
        }

    def get_task_result(self, task_id):
        """
        获取任务执行结果

        Args:
            task_id (str): 任务ID

        Returns:
            dict | None: 执行结果
        """
        self._load()
        return self._results.get(task_id)


# ══════════════════════════════════════════════
#  API路由处理函数
# ══════════════════════════════════════════════

def register_routes(handler):
    """
    将沙箱模块路由注册到HTTPServer的Handler上

    兼容 api/server.py 的 AIShieldHandler 模式。
    在 Handler.__init__ 中调用此函数注册路由。

    Args:
        handler: AIShieldHandler实例（需要已有 _send_json 和 _read_body 方法）
    """
    # 保存原始方法引用
    original_do_get = handler.do_GET
    original_do_post = handler.do_POST

    def do_get_patched(self):
        """扩展GET路由"""
        # 兼容: 如果handler已有_parsed_path则复用，否则解析self.path
        if hasattr(self, "_parsed_path"):
            parsed = self._parsed_path
        else:
            from urllib.parse import urlparse
            parsed = urlparse(self.path)
        path = parsed.path

        # ── GET /api/v1/sandbox/tasks — 列出任务 ──
        if path == "/api/v1/sandbox/tasks":
            mgr = SandboxTask()
            from urllib.parse import parse_qs
            qs = parse_qs(parsed.query)
            agent_id = qs.get("agent_id", [None])[0]
            status = qs.get("status", [None])[0]
            page = int(qs.get("page", ["1"])[0])
            result = mgr.list_tasks(agent_id=agent_id, status=status, page=page)
            self._send_json({"success": True, **result})
            return

        # ── GET /api/v1/sandbox/tasks/{task_id} — 查询任务详情 ──
        if path.startswith("/api/v1/sandbox/tasks/"):
            task_id = path[len("/api/v1/sandbox/tasks/"):]
            mgr = SandboxTask()
            task = mgr.get_task(task_id)
            if task:
                self._send_json({"success": True, "task": task})
            else:
                self._send_json({"error": "任务不存在", "task_id": task_id}, 404)
            return

        # ── GET /api/v1/sandbox/result/{task_id} — 获取任务结果 ──
        if path.startswith("/api/v1/sandbox/result/"):
            task_id = path[len("/api/v1/sandbox/result/"):]
            mgr = SandboxTask()
            result = mgr.get_task_result(task_id)
            if result:
                self._send_json({"success": True, "result": result})
            else:
                self._send_json({"error": "结果不存在", "task_id": task_id}, 404)
            return

        # 非本模块路由，交给原始处理器
        original_do_get(self)

    def do_post_patched(self):
        """扩展POST路由"""
        if hasattr(self, "_parsed_path"):
            parsed = self._parsed_path
        else:
            from urllib.parse import urlparse
            parsed = urlparse(self.path)
        path = parsed.path

        try:
            body = self._read_body()
            data = json.loads(body) if body else {}
        except (json.JSONDecodeError, TypeError):
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        # ── POST /api/v1/sandbox/submit — 提交沙箱任务 ──
        if path == "/api/v1/sandbox/submit":
            agent_id = data.get("agent_id", "").strip()
            code = data.get("code", "")
            language = data.get("language", "").strip()

            if not agent_id or not code or not language:
                self._send_json({"error": "agent_id, code, language 为必填"}, 400)
                return

            try:
                mgr = SandboxTask()
                result = mgr.submit(
                    agent_id=agent_id,
                    code=code,
                    language=language,
                    timeout_seconds=data.get("timeout_seconds", 30),
                    environment_vars=data.get("environment_vars"),
                    resource_limits=data.get("resource_limits"),
                )
                self._send_json({"success": True, **result}, 201)
            except ValueError as e:
                self._send_json({"error": str(e)}, 400)
            return

        # ── POST /api/v1/sandbox/execute/{task_id} — 执行待处理任务 ──
        if path.startswith("/api/v1/sandbox/execute/"):
            task_id = path[len("/api/v1/sandbox/execute/"):]
            mgr = SandboxTask()
            result = mgr.execute_pending(task_id)
            if "error" in result:
                self._send_json({"error": result["error"]}, 400)
            else:
                self._send_json({"success": True, **result})
            return

        # ── POST /api/v1/sandbox/cancel/{task_id} — 取消任务 ──
        if path.startswith("/api/v1/sandbox/cancel/"):
            task_id = path[len("/api/v1/sandbox/cancel/"):]
            agent_id = data.get("agent_id", "").strip()
            if not agent_id:
                self._send_json({"error": "agent_id 为必填"}, 400)
                return
            mgr = SandboxTask()
            ok = mgr.cancel_task(task_id, agent_id)
            if ok:
                self._send_json({"success": True, "task_id": task_id, "cancelled": True})
            else:
                self._send_json({"error": "取消失败", "task_id": task_id}, 400)
            return

        # 非本模块路由，交给原始处理器
        original_do_post(self)

    # 替换Handler的方法
    handler.do_GET = do_get_patched.__get__(handler, type(handler))
    handler.do_POST = do_post_patched.__get__(handler, type(handler))


# ══════════════════════════════════════════════
#  独立测试入口
# ══════════════════════════════════════════════

if __name__ == "__main__":
    print("=== 安全沙箱测试 ===")

    # 测试安全预检查
    print("\n--- 安全预检查 ---")
    executor = LocalExecutor()

    # 安全代码
    safe_code = "print('Hello, World!')"
    is_safe, findings = executor._pre_check_code(safe_code, "python")
    print(f"  安全代码: safe={is_safe}, findings={findings}")

    # 危险代码
    danger_code = "import os; os.system('rm -rf /')"
    is_safe, findings = executor._pre_check_code(danger_code, "python")
    print(f"  危险代码: safe={is_safe}, findings={len(findings)}个")
    for f in findings:
        print(f"    - {f['description']}")

    # 测试任务提交
    print("\n--- 任务提交 ---")
    mgr = SandboxTask()

    # 提交安全任务
    result = mgr.submit(
        agent_id="did:aishield:test001",
        code='print("Hello from sandbox!")',
        language="python",
        timeout_seconds=10,
    )
    print(f"  安全任务: task_id={result['task_id']}, status={result['status']}")

    # 提交危险任务
    result = mgr.submit(
        agent_id="did:aishield:test001",
        code="import subprocess; subprocess.run(['rm', '-rf', '/'])",
        language="python",
        timeout_seconds=10,
    )
    print(f"  危险任务: task_id={result['task_id']}, status={result['status']}")
    print(f"    原因: {result.get('reason', '')}")

    # 执行安全任务
    print("\n--- 任务执行 ---")
    tasks = mgr.list_tasks(status="queued")
    if tasks["tasks"]:
        task = tasks["tasks"][0]
        exec_result = mgr.execute_pending(task["task_id"])
        print(f"  执行结果: status={exec_result['status']}, "
              f"exit_code={exec_result.get('exit_code')}, "
              f"duration={exec_result.get('duration_ms')}ms")
        print(f"  安全审查: safe={exec_result['security_inspection']['safe']}, "
              f"risk={exec_result['security_inspection']['risk_level']}")

    # 查询结果
    print("\n--- 结果查询 ---")
    tasks = mgr.list_tasks(status="completed")
    if tasks["tasks"]:
        task = tasks["tasks"][0]
        result = mgr.get_task_result(task["task_id"])
        if result:
            print(f"  stdout: {result['stdout'].strip()}")
            print(f"  duration: {result['duration_ms']}ms")

    print("\n=== 全部测试通过 ===")
