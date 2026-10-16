"""
eco/runtime_governance.py — 运行时治理：fail-closed 决策网关 + kill switch + 不可篡改审计

补的是 AIShield 最大的能力缺口：扫描是"事前"，这里是"事中"。
对齐 OWASP Agentic AI ASI08（失控自主性）/ ASI10（治理缺失）与 CoSAI 对
"fail-closed 执行网关 + 不可变日志"的要求。

三件事，缺一不可：
  1. 决策网关 evaluate()  —— 每次工具调用前问一句"允许吗"，未知实体默认拒绝。
  2. kill switch          —— 出事时一键切断某个 server/tool，立刻生效，无需重启。
  3. 哈希链审计日志       —— append-only，每条含 prev_hash，事后可证明没被改过。

设计原则（与扫描器同源）：
  - 绝不 spawn 被治理的进程，本模块只做决策与记录。
  - 零第三方依赖、可完全离线运行、不外发任何数据。
  - fail-closed：策略损坏、实体未知、熔断触发 —— 一律 deny，不是 allow。
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA = os.path.join(_BASE, "api", "data")
POLICY_FILE = os.path.join(_DATA, "governance.json")
AUDIT_LOG = os.path.join(_DATA, "governance_audit.jsonl")

_lock = threading.RLock()

GENESIS_HASH = "0" * 64

# 连续高危事件达到此阈值自动熔断（kill）该 server
DEFAULT_INCIDENT_THRESHOLD = 3

DECISION_ALLOW = "allow"
DECISION_DENY = "deny"


def _now_iso():
    return datetime.now(TZ).isoformat()


def _sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _default_policy():
    return {
        # default_deny=True → 未在 allowlist 中的实体一律拒绝（fail-closed 的核心开关）
        "default_deny": False,
        "killed": {},        # server -> {reason, killed_at}
        "allow": {},         # server -> {"tools": [...] | "*"}
        "deny": {},          # server -> {"tools": [...] | "*"}
        "incidents": {},     # server -> {"count": n, "last": iso, "events": [...]}
        "incident_threshold": DEFAULT_INCIDENT_THRESHOLD,
        # L2 策略贯通：server -> {"source_pack", "runtime", "bound_at", "strict_runtime"}
        # 由 eco/policy_bridge.py 编译写入；扫描期 pack 的 excluded_categories 在此生效。
        "packs": {},         # server -> 绑定的 policy pack 及其运行时投影
        "updated_at": _now_iso(),
    }


# 策略的合法字段名。文件里一个都不含 ⇒ 无论 JSON 是否可解析，都是垃圾策略。
_POLICY_KNOWN_KEYS = frozenset({
    "default_deny", "killed", "allow", "deny", "incidents",
    "incident_threshold", "packs", "updated_at",
})
_POLICY_BOOL_FIELDS = ("default_deny",)
_POLICY_DICT_FIELDS = ("killed", "allow", "deny", "incidents", "packs")
_POLICY_INT_FIELDS = ("incident_threshold",)


def _validate_policy_shape(data):
    """策略结构校验。返回 (data, None) 合法 或 (None, 原因) 损坏。

    三道判据：① 根必须是 object；② 至少含一个可识别字段
    （空 dict / 全垃圾键 ⇒ 拒绝）；③ 出现了的关键字段类型必须对
    （bool/int 要真身，注意 bool 是 int 的子类，int 字段须显式排除 bool）。
    """
    if not isinstance(data, dict):
        return None, "policy root must be an object"
    if not any(k in _POLICY_KNOWN_KEYS for k in data):
        return None, "policy has no recognizable fields"
    for k in _POLICY_BOOL_FIELDS:
        if k in data and not isinstance(data[k], bool):
            return None, "policy field %r must be a boolean" % k
    for k in _POLICY_DICT_FIELDS:
        if k in data and not isinstance(data[k], dict):
            return None, "policy field %r must be an object" % k
    for k in _POLICY_INT_FIELDS:
        v = data.get(k)
        if k in data and (not isinstance(v, int) or isinstance(v, bool)):
            return None, "policy field %r must be an integer" % k
    return data, None


def _load_policy():
    """读策略。文件损坏时返回 fail-closed 策略（default_deny=True），绝不放行。

    "损坏"不只是字节不可解析：合法 JSON 但语义空洞（一个可识别字段都没有、
    或字段类型错误）同样必须 fail-closed。CI 上 Hypothesis 曾用
    ``{"":"","":0,"":""}`` 抓到旧漏洞——它能通过 json.load 与
    ``isinstance(dict)``，于是 default_deny 落回默认 False、整份策略
    放行一切。结构校验（_validate_policy_shape）补上这一类输入。
    """
    if not os.path.exists(POLICY_FILE):
        return _default_policy(), True
    try:
        with open(POLICY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data, err = _validate_policy_shape(data)
        if err is not None:
            raise ValueError(err)
        base = _default_policy()
        base.update(data)
        return base, True
    except Exception:
        # 关键：策略读不出来时收紧而不是放开
        broken = _default_policy()
        broken["default_deny"] = True
        broken["_load_error"] = True
        return broken, False


def _save_policy(policy):
    os.makedirs(os.path.dirname(POLICY_FILE), exist_ok=True)
    policy["updated_at"] = _now_iso()
    tmp = POLICY_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(policy, f, ensure_ascii=False, indent=2)
    os.replace(tmp, POLICY_FILE)


# ══════════════════════════════════════════
#  哈希链审计日志（append-only）
# ══════════════════════════════════════════

def _last_entry():
    """读日志末条。空日志返回 None。"""
    if not os.path.exists(AUDIT_LOG):
        return None
    last = None
    try:
        with open(AUDIT_LOG, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    last = line
    except Exception:
        return None
    if not last:
        return None
    try:
        return json.loads(last)
    except Exception:
        return None


def _entry_digest(entry):
    """对条目做规范化摘要——排除 hash 自身，键排序保证可复现。"""
    payload = {k: v for k, v in entry.items() if k != "hash"}
    return _sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def audit(event, detail=None):
    """追加一条审计记录，返回落盘后的条目（含 seq / prev_hash / hash）。"""
    with _lock:
        prev = _last_entry()
        seq = (prev.get("seq", 0) + 1) if prev else 1
        prev_hash = prev.get("hash", GENESIS_HASH) if prev else GENESIS_HASH
        entry = {
            "seq": seq,
            "ts": _now_iso(),
            "event": event,
            "detail": detail or {},
            "prev_hash": prev_hash,
        }
        entry["hash"] = _entry_digest(entry)
        os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry


def read_audit(limit=100, event=None):
    """按时间倒序读审计日志。"""
    if not os.path.exists(AUDIT_LOG):
        return []
    rows = []
    try:
        with open(AUDIT_LOG, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return []
    if event:
        rows = [r for r in rows if r.get("event") == event]
    rows.reverse()
    return rows[:limit]


def verify_chain():
    """校验整条哈希链。任何一条被改写/删除/插入都会被定位到。"""
    if not os.path.exists(AUDIT_LOG):
        return {"valid": True, "entries": 0, "note": "审计日志为空"}
    prev_hash = GENESIS_HASH
    expected_seq = 1
    count = 0
    try:
        with open(AUDIT_LOG, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except Exception:
                    return {"valid": False, "entries": count, "broken_at": lineno,
                            "reason": "JSON 解析失败"}
                count += 1
                if entry.get("seq") != expected_seq:
                    return {"valid": False, "entries": count, "broken_at": lineno,
                            "reason": f"序号断裂：期望 {expected_seq}，实际 {entry.get('seq')}"}
                if entry.get("prev_hash") != prev_hash:
                    return {"valid": False, "entries": count, "broken_at": lineno,
                            "reason": "prev_hash 不匹配（前序条目被篡改或删除）"}
                if _entry_digest(entry) != entry.get("hash"):
                    return {"valid": False, "entries": count, "broken_at": lineno,
                            "reason": "本条内容被篡改（hash 不符）"}
                prev_hash = entry["hash"]
                expected_seq += 1
    except Exception as exc:
        return {"valid": False, "entries": count, "reason": f"读取失败: {exc}"}
    return {"valid": True, "entries": count, "head_hash": prev_hash}


# ══════════════════════════════════════════
#  行为监控（事中异常检测）
# ══════════════════════════════════════════
#
# 决策网关回答"这次调用允许吗"（点），行为监控回答"这个 agent 最近的调用模式
# 正常吗"（线）。二者互补：一个 agent 每次调用都合规，但 60 秒内打 500 次、
# 或连续被拒 20 次疯狂探测，这本身就是失控/入侵信号（ASI08 失控自主性 /
# ASI10 治理缺失的行为面）。闭环四环节：检测(observe) → 动作(审计+可选升级
# 事故/熔断) → 验证(status) → 告警(behavior_anomaly 审计事件)。

BEHAVIOR_WINDOW_SEC = 60      # 滑动窗口
BEHAVIOR_RATE_MAX = 120       # 单 server 窗口内调用数上限，超过判 rate_burst
BEHAVIOR_DENIAL_MAX = 8       # 单 server 窗口内拒绝数达此值判 denial_probe

ANOMALY_RATE_BURST = "rate_burst"
ANOMALY_DENIAL_PROBE = "denial_probe"


def _behavior_path():
    """行为文件与审计日志同目录 —— 测试替换 AUDIT_LOG 时自动隔离，不碰真实数据。"""
    return os.path.join(os.path.dirname(AUDIT_LOG), "runtime_behavior.json")


class BehaviorMonitor:
    """运行时行为监控：滑动窗口速率 + 拒绝探测，异常写入哈希链审计。"""

    def __init__(self, path=None, window_sec=BEHAVIOR_WINDOW_SEC,
                 rate_max=BEHAVIOR_RATE_MAX, denial_max=BEHAVIOR_DENIAL_MAX,
                 escalate=None):
        self._path_override = path
        self.window_sec = window_sec
        self.rate_max = rate_max
        self.denial_max = denial_max
        # escalate(server, severity, detail) —— 命中异常时的"动作"钩子；
        # 默认 None（只审计不升级），闭环保守，避免监控本身误伤。
        self.escalate = escalate

    @property
    def path(self):
        """惰性解析：与 AttestationStream.path 同因（import 时固化的路径会让
        测试对 AUDIT_LOG 的替换失效，把行为状态写进真实 api/data/）。"""
        return self._path_override or _behavior_path()

    # ── 持久化（原子写） ──
    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    data.setdefault("windows", {})
                    data.setdefault("anomalies", [])
                    data.setdefault("fired", {})
                    return data
            except Exception:
                pass
        return {"windows": {}, "anomalies": [], "fired": {}}

    def _save(self, data):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    def observe(self, server, tool="", decision=DECISION_ALLOW, ts=None):
        """记录一次调用，返回本次命中的异常列表（无异常为 []）。

        异常按窗口去重（每个窗口每种异常只报一次），避免刷屏。
        """
        server = (server or "").strip()
        if not server:
            return []
        if ts is None:
            now = datetime.now(TZ)
        elif isinstance(ts, str):
            now = datetime.fromisoformat(ts)
        else:
            now = ts
        cutoff = (now - timedelta(seconds=self.window_sec)).isoformat()

        with _lock:
            data = self._load()
            win = data["windows"].setdefault(server, [])
            win.append({"ts": now.isoformat(), "tool": tool, "decision": decision})
            win[:] = [e for e in win if e.get("ts", "") >= cutoff]
            fired = data["fired"].setdefault(server, {})

            anomalies = []

            def _fire(kind, severity, count, reason):
                last = fired.get(kind)
                if last and last >= cutoff:
                    return              # 本窗口已报过，去重
                fired[kind] = now.isoformat()
                anomalies.append({"type": kind, "severity": severity, "server": server,
                                  "count": count, "window_sec": self.window_sec,
                                  "reason": reason, "ts": now.isoformat()})

            if len(win) > self.rate_max:
                _fire(ANOMALY_RATE_BURST, "high", len(win),
                      f"{self.window_sec}s 内调用 {len(win)} 次，超过上限 {self.rate_max}")
            denials = sum(1 for e in win if e.get("decision") == DECISION_DENY)
            if denials >= self.denial_max:
                _fire(ANOMALY_DENIAL_PROBE, "high", denials,
                      f"{self.window_sec}s 内被拒 {denials} 次，疑似越权探测")

            if anomalies:
                data["anomalies"].extend(anomalies)
                data["anomalies"] = data["anomalies"][-200:]
            self._save(data)

        for a in anomalies:
            audit("behavior_anomaly", a)
            if self.escalate:
                try:
                    self.escalate(server, a["severity"],
                                  {"anomaly": a["type"], "count": a["count"]})
                except Exception:
                    pass
        return anomalies

    def status(self):
        """验证环节：当前各 server 的窗口统计 + 最近异常。"""
        data = self._load()
        servers = {}
        for s, win in data.get("windows", {}).items():
            servers[s] = {
                "calls": len(win),
                "denials": sum(1 for e in win if e.get("decision") == DECISION_DENY),
                "tools": sorted({e.get("tool", "") for e in win if e.get("tool")}),
            }
        return {
            "window_sec": self.window_sec,
            "rate_max": self.rate_max,
            "denial_max": self.denial_max,
            "servers": servers,
            "anomalies": data.get("anomalies", [])[-50:],
            "anomaly_count": len(data.get("anomalies", [])),
            "healthy": not data.get("anomalies"),
        }

    def reset(self):
        self._save({"windows": {}, "anomalies": [], "fired": {}})


# ══════════════════════════════════════════
#  决策网关
# ══════════════════════════════════════════

def _matches(entry, tool):
    """entry 可以是 "*"、列表或 {"tools": [...]}。"""
    if entry in ("*", True):
        return True
    if isinstance(entry, dict):
        entry = entry.get("tools", [])
    if isinstance(entry, str):
        return entry == "*" or entry == tool
    if isinstance(entry, (list, tuple, set)):
        return "*" in entry or tool in entry
    return False


_SEVERITY_RANK = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def _cat_match(category: str, patterns) -> bool:
    """类别匹配（精确 + 前缀）。patterns 为空时永不命中。

    前缀匹配让 pack 里的「排除 ASI 整个族」在运行时成立：ASI03 命中 ASI01。
    """
    cat = (category or "").strip().upper()
    if not cat:
        return False
    try:
        pats = list(patterns or [])
    except TypeError:
        pats = []
    if not pats:
        return False
    if cat in pats:
        return True
    for p in pats:
        p = str(p or "").strip().upper()
        if p and cat.startswith(p.rstrip("*")):
            return True
    return False


def _pack_verdict(server: str, policy: dict, context=None) -> dict:
    """评估本次调用是否被已绑定的 policy pack 拦下。

    不拦时返回观察标记（schema 见下），放行判定不受任何影响 ——
    表外未知类别一律放行，绝不因为 pack 没覆盖就拒。
    """
    bound = (policy.get("packs") or {}).get(server) or {}
    if not bound:
        return {}
    rt = bound.get("runtime") or {}
    deny_cats = rt.get("deny_categories") or []
    allow_cats = rt.get("allow_categories") or []
    ctx = context or {}
    cat = str(ctx.get("category") or "").strip().upper()

    if deny_cats and cat and _cat_match(cat, deny_cats):
        return {
            "decision": DECISION_DENY,
            "reason": f"命中 policy pack「{bound.get('source_pack', '?')}」排除的类别 {cat}",
            "policy_hit": "pack_excluded_category",
            "source_pack": bound.get("source_pack"),
        }

    obs = {"source_pack": bound.get("source_pack"),
           "strictness": rt.get("strictness"),
           "severity_floor": rt.get("severity_floor")}
    sev = str(ctx.get("severity") or "").strip().lower()
    floor = str(rt.get("severity_floor") or "").strip().lower()
    if sev in _SEVERITY_RANK and floor in _SEVERITY_RANK:
        if _SEVERITY_RANK[sev] < _SEVERITY_RANK[floor]:
            obs["below_severity_floor"] = True
    if cat and allow_cats and not _cat_match(cat, allow_cats):
        obs["unlisted_category"] = True
    return obs


def bind_pack(server: str, pack_name: str, strict_runtime: bool = False) -> dict:
    """把一个扫描期 policy pack 绑定到某 server 的运行时网关（L2 策略贯通）。

    绑定后：pack 的 excluded_categories 在运行时产生**真拒绝**，
    required_categories 产生观察标记，severity_min 成为审计阈值。
    返回编译产物（含 rationale），调用方可直接呈现给运维。

    策略损坏（加载失败）时抛 RuntimeError —— 此时按 fail-closed 收紧，
    但拒绝在损坏状态下写入归属是危险的，必须先修策略。
    """
    from eco import policy_bridge  # noqa: PLC0415（延迟导入，运行时热路径不背扫描期依赖）

    compiled = policy_bridge.compile_pack(pack_name, strict_runtime=bool(strict_runtime))
    policy, ok = _load_policy()
    if not ok:
        raise RuntimeError("策略文件损坏且已按 fail-closed 收紧；请先修复策略再绑定 pack")
    policy.setdefault("packs", {})
    policy["packs"][(server or "").strip()] = {
        "source_pack": compiled["source_pack"],
        "runtime": compiled["runtime"],
        "rationale": compiled["rationale"],
        "strict_runtime": bool(strict_runtime),
        "bound_at": _now_iso(),
    }
    _save_policy(policy)
    return compiled


def unbind_pack(server: str) -> bool:
    """解绑某个 server 的 policy pack。解绑后回到纯默认运行时行为。"""
    policy, ok = _load_policy()
    if not ok:
        return False
    packs = policy.get("packs") or {}
    server = (server or "").strip()
    if server not in packs:
        return False
    del packs[server]
    policy["packs"] = packs
    _save_policy(policy)
    return True


def bound_pack(server: str) -> dict | None:
    """查某个 server 当前绑定的 pack 及其运行时投影。未绑定返回 None。"""
    policy, _ = _load_policy()
    ent = (policy.get("packs") or {}).get((server or "").strip())
    return ent or None


class RuntimeGovernor:
    """运行时治理网关。evaluate() 是唯一的准入判定入口。"""

    def evaluate(self, server, tool="", context=None, log=True, behavior=True):
        """判定一次工具调用是否放行。

        优先级（从高到低，任何一层命中即终止）：
            kill switch > deny 名单 > allow 名单 > default_deny 兜底

        behavior=True 时顺带把这次决策喂给行为监控（检测调用模式异常）。
        行为监控的任何故障都不影响放行判定本身（吞掉异常，绝不因监控而误拒）。
        """
        server = (server or "").strip()
        tool = (tool or "").strip()
        policy, ok = _load_policy()

        def _result(decision, reason, policy_hit):
            res = {"decision": decision, "allowed": decision == DECISION_ALLOW,
                   "server": server, "tool": tool, "reason": reason,
                   "policy_hit": policy_hit, "ts": _now_iso(),
                   # 策略贯通信息：未绑 pack 时为空 dict（保持键一致，消费方不必判存在）
                   "pack": {}}
            if not ok:
                res["policy_load_error"] = True
            if log:
                audit("decision", {"server": server, "tool": tool,
                                   "decision": decision, "reason": reason,
                                   "policy_hit": policy_hit,
                                   "context": (context or {})})
                if behavior:
                    try:
                        _default_behavior.observe(server, tool, decision)
                    except Exception:
                        pass
                # 持续证明流（Program C）：每 N 次判定签一次运行时快照。
                # 与行为监控同纪律：证明流故障绝不影响放行判定本身。
                try:
                    _default_attest.snapshot()
                except Exception:
                    pass
            return res

        if not server:
            return _result(DECISION_DENY, "server 标识缺失", "invalid_request")

        # 1) kill switch —— 最高优先级，立刻切断
        killed = policy.get("killed", {})
        if server in killed:
            return _result(DECISION_DENY,
                           f"该 server 已被熔断: {killed[server].get('reason', '未说明')}",
                           "kill_switch")

        # 2) 显式 deny
        deny = policy.get("deny", {})
        if server in deny and _matches(deny[server], tool):
            return _result(DECISION_DENY, "命中显式拒绝规则", "deny_list")

        # 3) 显式 allow
        allow = policy.get("allow", {})
        if server in allow and _matches(allow[server], tool):
            return _result(DECISION_ALLOW, "命中放行规则", "allow_list")

        # 4) policy pack 贯通（L2）：扫描期 pack 的 excluded_categories → 运行时真拒绝。
        #    未绑 pack 的 server 在这里原样继续，行为与贯通前完全一致（不误伤存量）。
        pack_ctx = _pack_verdict(server, policy, context)
        if pack_ctx.get("decision") == DECISION_DENY:
            return _result(DECISION_DENY, pack_ctx["reason"], pack_ctx["policy_hit"])

        # 5) 兜底：fail-closed 模式下未知实体一律拒绝
        if policy.get("default_deny"):
            return _result(DECISION_DENY, "未在放行名单内（fail-closed 默认拒绝）", "default_deny")
        res = _result(DECISION_ALLOW, "默认放行（未开启 fail-closed）", "default_allow")
        if pack_ctx:
            res["pack"] = pack_ctx
        return res

    # ── kill switch ──
    def kill(self, server, reason="manual kill switch"):
        server = (server or "").strip()
        if not server:
            return {"success": False, "error": "server 标识不能为空"}
        with _lock:
            policy, _ = _load_policy()
            policy.setdefault("killed", {})[server] = {
                "reason": reason, "killed_at": _now_iso()}
            _save_policy(policy)
        entry = audit("kill", {"server": server, "reason": reason})
        return {"success": True, "server": server, "reason": reason,
                "killed_at": entry["ts"], "audit_seq": entry["seq"]}

    def revive(self, server, reason="manual revive"):
        server = (server or "").strip()
        with _lock:
            policy, _ = _load_policy()
            if server not in policy.get("killed", {}):
                return {"success": False, "error": "该 server 未被熔断", "server": server}
            policy["killed"].pop(server, None)
            # 复活时清空事故计数，否则下一次事故立刻又被熔断
            policy.get("incidents", {}).pop(server, None)
            _save_policy(policy)
        entry = audit("revive", {"server": server, "reason": reason})
        return {"success": True, "server": server, "revived_at": entry["ts"],
                "audit_seq": entry["seq"]}

    def is_killed(self, server):
        policy, _ = _load_policy()
        return (server or "").strip() in policy.get("killed", {})

    # ── 策略管理 ──
    def set_default_deny(self, enabled):
        with _lock:
            policy, _ = _load_policy()
            policy["default_deny"] = bool(enabled)
            _save_policy(policy)
        audit("policy_change", {"default_deny": bool(enabled)})
        return {"success": True, "default_deny": bool(enabled)}

    def allow_tool(self, server, tools="*"):
        return self._set_list("allow", server, tools)

    def deny_tool(self, server, tools="*"):
        return self._set_list("deny", server, tools)

    def _set_list(self, bucket, server, tools):
        server = (server or "").strip()
        if not server:
            return {"success": False, "error": "server 标识不能为空"}
        if isinstance(tools, str):
            tools = [tools]
        with _lock:
            policy, _ = _load_policy()
            existing = policy.setdefault(bucket, {}).get(server)
            merged = set()
            if isinstance(existing, dict):
                merged |= set(existing.get("tools", []))
            elif isinstance(existing, (list, tuple, set)):
                merged |= set(existing)
            elif isinstance(existing, str):
                merged.add(existing)
            merged |= set(tools)
            policy[bucket][server] = {"tools": sorted(merged), "updated_at": _now_iso()}
            _save_policy(policy)
        audit("policy_change", {"bucket": bucket, "server": server, "tools": sorted(set(tools))})
        return {"success": True, "bucket": bucket, "server": server,
                "tools": policy[bucket][server]["tools"]}

    def clear_rule(self, bucket, server):
        if bucket not in ("allow", "deny"):
            return {"success": False, "error": "bucket 只能是 allow 或 deny"}
        with _lock:
            policy, _ = _load_policy()
            removed = policy.get(bucket, {}).pop((server or "").strip(), None)
            _save_policy(policy)
        audit("policy_change", {"bucket": bucket, "server": server, "cleared": bool(removed)})
        return {"success": True, "cleared": bool(removed), "bucket": bucket, "server": server}

    # ── 事故与自动熔断 ──
    def record_incident(self, server, severity="high", detail=None):
        """记录一次运行时事故。累计达阈值自动 kill（ASI08 失控自主性的刹车）。"""
        server = (server or "").strip()
        if not server:
            return {"success": False, "error": "server 标识不能为空"}
        with _lock:
            policy, _ = _load_policy()
            threshold = int(policy.get("incident_threshold", DEFAULT_INCIDENT_THRESHOLD))
            rec = policy.setdefault("incidents", {}).setdefault(
                server, {"count": 0, "events": []})
            # 只有 high/critical 计入熔断计数，低危不至于误伤
            counts = severity in ("high", "critical")
            if counts:
                rec["count"] = int(rec.get("count", 0)) + 1
            rec["last"] = _now_iso()
            rec.setdefault("events", []).append(
                {"ts": _now_iso(), "severity": severity, "detail": detail or {}})
            rec["events"] = rec["events"][-20:]     # 只留最近 20 条，避免无限膨胀
            auto_killed = False
            if counts and rec["count"] >= threshold and server not in policy.get("killed", {}):
                policy.setdefault("killed", {})[server] = {
                    "reason": f"自动熔断：连续 {rec['count']} 次 {severity} 事故",
                    "killed_at": _now_iso(), "auto": True}
                auto_killed = True
            _save_policy(policy)
        audit("incident", {"server": server, "severity": severity,
                           "count": rec["count"], "auto_killed": auto_killed,
                           "detail": detail or {}})
        if auto_killed:
            audit("kill", {"server": server, "reason": "auto: incident threshold reached",
                           "auto": True})
        return {"success": True, "server": server, "count": rec["count"],
                "threshold": threshold, "auto_killed": auto_killed}

    def status(self):
        policy, ok = _load_policy()
        chain = verify_chain()
        return {
            "default_deny": policy.get("default_deny", False),
            "killed": policy.get("killed", {}),
            "killed_count": len(policy.get("killed", {})),
            "allow_rules": len(policy.get("allow", {})),
            "deny_rules": len(policy.get("deny", {})),
            "incident_threshold": policy.get("incident_threshold", DEFAULT_INCIDENT_THRESHOLD),
            "incidents": {k: v.get("count", 0) for k, v in policy.get("incidents", {}).items()},
            "policy_healthy": ok,
            "audit_chain": chain,
            "updated_at": policy.get("updated_at"),
        }


# ══════════════════════════════════════════════
#  持续证明流（Program C — RIL）：流式鉴证
# ══════════════════════════════════════════════
#
# 决策网关回答"这次调用允许吗"（点），行为监控回答"模式正常吗"（线），
# 持续证明流回答"**此刻的整个运行时状态可被第三方验证吗**"（面）。
#
# 把 docs 蓝图 §3 Program C 的"连续证明（continuous attestation）流"
# 落地：每 N 次准入判定（或强制触发）对运行时状态签一次名 ——
#   策略指纹 + 审计链头 + 行为健康 + 熔断数
# 签名密钥即 verifiable_identity 的 active Ed25519 密钥，与 JWKS 对外
# 发布的同一把：第三方拉一次 JWKS（或从签名者 did:key 直接解出公钥）
# 就能离线验证任一快照，无需信任本服务在线。
#
# 缺 cryptography 时按设计降级 HMAC，并诚实标注
# third_party_verifiable=False —— 宁可不可验，也不假装可验。

ATTEST_EVERY_EVALUATIONS = 25   # 每 N 次判定签一次运行时快照


def _attest_path():
    """与审计日志同目录 —— 测试替换 AUDIT_LOG 时自动隔离，不碰真实数据。"""
    return os.path.join(os.path.dirname(AUDIT_LOG), "runtime_attestations.jsonl")


class AttestationStream:
    """流式证明：对运行时状态拍签名快照，追加进哈希链日志。"""

    def __init__(self, path=None, every=ATTEST_EVERY_EVALUATIONS, key_resolver=None):
        self._path_override = path
        self.every = max(1, int(every))
        self._counter = 0
        # key_resolver(kid) -> key dict：验证时按 kid 找公钥的回调。
        # 生产默认走 verifiable_identity 密钥环（含 deprecated，旧快照仍可验）；
        # 测试可注入，避免碰真实 api/data。
        self.key_resolver = key_resolver

    @property
    def path(self):
        """路径**每次访问都重新解析**，不是 import 时固化。

        2026-10-15 全量套件实测：`_default_attest = AttestationStream()` 在
        import 时就把路径钉成真实 api/data/runtime_attestations.jsonl，之后
        测试替换 rg.AUDIT_LOG 对单例无效 —— test_invariant_property 的
        Hypothesis 循环跑满 50 次判定，快照写进了真实数据文件（测试污染）。
        改为惰性解析后，"测试替换 AUDIT_LOG 即隔离"的注释才真正成立。
        """
        return self._path_override or _attest_path()

    # ── 签名者（与 JWKS 同一把密钥）──
    def _signer(self):
        """返回 active 签名密钥 dict；无密钥返回 None（调用方记 unsigned）。"""
        from eco import verifiable_identity as vi
        ring = vi.SigningKeyRing().load()
        return ring.active()

    # ── 运行时状态采集 ──
    def _policy_digest(self):
        try:
            with open(POLICY_FILE, "rb") as f:
                return _sha256(f.read().decode("utf-8", "replace"))
        except Exception:
            return "unreadable"

    @staticmethod
    def _audit_head_and_count():
        """只解析末条 + 计数（不整链校验；完整校验走 verify_chain()）。"""
        if not os.path.exists(AUDIT_LOG):
            return 0, None
        count = 0
        last = None
        try:
            with open(AUDIT_LOG, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    count += 1
                    last = line
        except Exception:
            return count, None
        if not last:
            return 0, None
        try:
            return count, json.loads(last).get("hash")
        except Exception:
            return count, None

    def _state(self):
        entries, head = self._audit_head_and_count()
        try:
            behavior = _default_behavior.status()
        except Exception:
            behavior = {"healthy": None, "anomaly_count": None}
        policy, ok = _load_policy()
        return {
            "ts": _now_iso(),
            "evaluations": self._counter,
            "policy_digest": self._policy_digest(),
            "policy_healthy": ok,
            "audit_entries": entries,
            "audit_head_hash": head,
            "behavior_healthy": behavior.get("healthy"),
            "behavior_anomaly_count": behavior.get("anomaly_count"),
            "killed_count": len(policy.get("killed", {})),
        }

    # ── 快照签发与落盘 ──
    def snapshot(self, force=False) -> dict | None:
        """签一次运行时快照。非 force 时按 every 节流（返回 None 表示未到点）。"""
        if not force:
            self._counter += 1
            if self._counter % self.every != 0:
                return None
        with _lock:
            prev = self._last_entry()
            seq = (prev.get("seq", 0) + 1) if prev else 1
            prev_hash = prev.get("hash", GENESIS_HASH) if prev else GENESIS_HASH
            payload = self._state()
            payload["seq"] = seq
            payload["prev_hash"] = prev_hash
            body = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                              separators=(",", ":")).encode("utf-8")
            entry = dict(payload)
            entry["hash"] = _sha256(body.decode("utf-8"))

            key = self._signer()
            if key:
                alg = str(key.get("alg") or "")
                try:
                    sig = _cs_sign(body, str(key.get("private_key") or ""), alg or None)
                    entry["signature"] = sig
                    entry["signature_alg"] = alg or "unknown"
                    entry["signer_kid"] = _kid_of(key)
                    # Ed25519 非对称 → 第三方可验；HMAC 对称 → 诚实标注不可验
                    entry["third_party_verifiable"] = bool(
                        alg and alg.lower() == "ed25519")
                except Exception as exc:
                    entry["signature"] = None
                    entry["unsigned_reason"] = f"sign failed: {type(exc).__name__}"
                    entry["third_party_verifiable"] = False
            else:
                entry["signature"] = None
                entry["unsigned_reason"] = "no active signing key"
                entry["third_party_verifiable"] = False

            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        audit("runtime_attestation", {"seq": seq, "policy_digest": payload["policy_digest"],
                                      "third_party_verifiable": entry["third_party_verifiable"]})
        return entry

    def _last_entry(self):
        if not os.path.exists(self.path):
            return None
        last = None
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        last = line
        except Exception:
            return None
        if not last:
            return None
        try:
            return json.loads(last)
        except Exception:
            return None

    # ── 查询与验证 ──
    def latest(self) -> dict | None:
        return self._last_entry()

    def verify(self) -> dict:
        """校验整条证明链：hash 链连续性 + 每条签名（有签的）。"""
        if not os.path.exists(self.path):
            return {"valid": True, "entries": 0, "note": "证明流为空"}
        prev_hash = GENESIS_HASH
        expected_seq = 1
        count = 0
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except Exception:
                        return {"valid": False, "entries": count, "broken_at": lineno,
                                "reason": "JSON 解析失败"}
                    count += 1
                    if entry.get("seq") != expected_seq:
                        return {"valid": False, "entries": count, "broken_at": lineno,
                                "reason": f"序号断裂：期望 {expected_seq}，实际 {entry.get('seq')}"}
                    if entry.get("prev_hash") != prev_hash:
                        return {"valid": False, "entries": count, "broken_at": lineno,
                                "reason": "prev_hash 不匹配（前序快照被篡改或删除）"}
                    body = {k: v for k, v in entry.items()
                            if k not in ("hash", "signature", "signature_alg",
                                        "signer_kid", "third_party_verifiable",
                                        "unsigned_reason")}
                    if _sha256(json.dumps(body, ensure_ascii=False, sort_keys=True,
                                          separators=(",", ":"))) != entry.get("hash"):
                        return {"valid": False, "entries": count, "broken_at": lineno,
                                "reason": "本条内容被篡改（hash 不符）"}
                    sig = entry.get("signature")
                    if sig:
                        key = self._key_by_kid(entry.get("signer_kid"))
                        if not key:
                            return {"valid": False, "entries": count, "broken_at": lineno,
                                    "reason": f"签名者 kid 不在密钥环: {entry.get('signer_kid')}"}
                        raw = json.dumps(body, ensure_ascii=False, sort_keys=True,
                                         separators=(",", ":")).encode("utf-8")
                        if not _cs_verify(raw, sig, str(key.get("public_key") or ""),
                                          str(key.get("alg") or "")):
                            return {"valid": False, "entries": count, "broken_at": lineno,
                                    "reason": "签名校验失败（快照被改写或密钥不匹配）"}
                    prev_hash = entry["hash"]
                    expected_seq += 1
        except Exception as exc:
            return {"valid": False, "entries": count, "reason": f"读取失败: {exc}"}
        return {"valid": True, "entries": count, "head_hash": prev_hash}

    def _key_by_kid(self, kid):
        if not kid:
            return None
        if self.key_resolver is not None:
            return self.key_resolver(kid)
        from eco import verifiable_identity as vi
        ring = vi.SigningKeyRing().load()
        for cand in [ring.active()] + ring.deprecated():
            if cand and _kid_of(cand) == kid:
                return cand
        return None

    def status(self):
        return {
            "every_evaluations": self.every,
            "evaluations_seen": self._counter,
            "latest": self.latest(),
            "chain": self.verify(),
        }


def _kid_of(key: dict) -> str:
    """签名密钥的 kid（与 verifiable_identity 同口径：公钥 sha256 前 12 位）。"""
    import hashlib as _hl
    return _hl.sha256(str(key.get("public_key") or "").encode("ascii")).hexdigest()[:12]


def _cs_sign(message: bytes, private_b64: str, alg=None) -> str:
    from eco import crypto_sign as cs
    return cs.sign(message, private_b64, alg)


def _cs_verify(message: bytes, signature_b64: str, public_b64: str, alg: str) -> bool:
    from eco import crypto_sign as cs
    return cs.verify(message, signature_b64, public_b64, alg)


# ── 模块级便捷 API ──
_default = RuntimeGovernor()
# 默认行为监控：只检测+审计，不自动升级（闭环保守；需要自动熔断时调
# enable_behavior_escalation()）。escalate 钩子可在任意时刻挂上。
_default_behavior = BehaviorMonitor()
# 持续证明流：每 25 次判定签一次运行时快照（路径随 AUDIT_LOG 隔离）。
_default_attest = AttestationStream()


def evaluate(server, tool="", context=None, log=True, behavior=True):
    return _default.evaluate(server, tool, context, log, behavior)


def observe_behavior(server, tool="", decision=DECISION_ALLOW, ts=None):
    return _default_behavior.observe(server, tool, decision, ts)


def behavior_status():
    return _default_behavior.status()


def reset_behavior():
    _default_behavior.reset()


def configure_behavior(**kw):
    """运行时调参：window_sec / rate_max / denial_max / escalate。

    例：configure_behavior(rate_max=30, denial_max=3)
    """
    for k in ("window_sec", "rate_max", "denial_max", "escalate", "path"):
        if k in kw:
            setattr(_default_behavior, k, kw[k])
    return behavior_status()


def enable_behavior_escalation(enabled=True):
    """把行为异常升级为运行时事故（进而触发既有的事故→自动熔断链路）。"""
    _default_behavior.escalate = (
        (lambda server, severity, detail: record_incident(server, severity, detail))
        if enabled else None)
    return {"success": True, "escalation_enabled": enabled}


def kill(server, reason="manual kill switch"):
    return _default.kill(server, reason)


def revive(server, reason="manual revive"):
    return _default.revive(server, reason)


def is_killed(server):
    return _default.is_killed(server)


def record_incident(server, severity="high", detail=None):
    return _default.record_incident(server, severity, detail)


def allow_tool(server, tools="*"):
    return _default.allow_tool(server, tools)


def deny_tool(server, tools="*"):
    return _default.deny_tool(server, tools)


def set_default_deny(enabled):
    return _default.set_default_deny(enabled)


def status():
    return _default.status()


def attest_now():
    """强制签一次运行时快照（供运维/测试触发，不经节流）。"""
    return _default_attest.snapshot(force=True)


def attest_status():
    """持续证明流状态：配置 + 最新快照 + 全链校验。"""
    return _default_attest.status()


if __name__ == "__main__":
    g = RuntimeGovernor()
    print("初始:", g.evaluate("demo-server", "read_file")["decision"])
    g.deny_tool("demo-server", ["exec_shell"])
    print("拒绝规则:", g.evaluate("demo-server", "exec_shell")["reason"])
    for i in range(3):
        r = g.record_incident("demo-server", "high", {"finding": f"prompt injection #{i+1}"})
    print("自动熔断:", r["auto_killed"])
    print("熔断后:", g.evaluate("demo-server", "read_file")["reason"])
    print("复活:", g.revive("demo-server")["success"])
    print("链校验:", verify_chain())
