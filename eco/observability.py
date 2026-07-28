"""
eco/observability.py — 成本可观测性模块

功能:
  - CREDIT_COSTS:       各端点的积分消耗表（调用前预估 & 调用后记账）
  - TOKEN_ESTIMATES:    各端点的预估 Token 消耗（输入/输出）
  - CallRecord:         单次调用记录（track_call 写入 call_records.json）
  - ObservabilityService: 成本可观测性分析服务
      * cost_estimate          — 调用前预估积分总消耗、Token 总量、各端点明细
      * get_agent_efficiency   — 某 Agent 的效率指标（调用次数/积分/Token/Top3端点/效率评分）
      * get_system_metrics     — 系统级指标（调用分布/延迟分位/每小时趋势，适合图表渲染）
      * get_user_consumption   — 用户消耗明细（含异常检测、免费额度剩余）
      * get_cost_alerts        — 生成成本告警并持久化到 cost_alerts.json
  - 数据持久化: api/data/call_records.json、api/data/cost_alerts.json
  - 线程安全: threading.Lock
  - 零外部依赖，仅使用 Python 标准库

设计说明:
  - 所有时间戳统一使用 ISO8601（东八区）
  - call_records 自动清理 30 天前的数据
  - cost_alerts 保留最近 1000 条
  - 文件格式与 eco/a2a_gateway.py 保持一致（_lock / _load_json / _save_json / _now_iso 模式）

API路由:
  GET  /api/v1/observability/cost-estimate?endpoints=audit,prompt_check
  GET  /api/v1/observability/agent/{agent_id}/efficiency?days=7
  GET  /api/v1/observability/system?hours=24
  GET  /api/v1/observability/user/{account_id}/consumption?days=30
  GET  /api/v1/observability/alerts
  POST /api/v1/observability/track
"""

import json
import os
import math
import uuid
import threading
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict

# ── 路径配置 ──
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_BASE_DIR, "api", "data")
CALL_RECORDS_FILE = os.path.join(_DATA_DIR, "call_records.json")
COST_ALERTS_FILE = os.path.join(_DATA_DIR, "cost_alerts.json")

TZ = timezone(timedelta(hours=8))
_lock = threading.Lock()

# 数据保留策略
_RECORD_RETENTION_DAYS = 30      # 调用记录保留 30 天
_ALERT_MAX_COUNT = 1000          # 成本告警保留最近 1000 条

# 用户每日免费额度
FREE_DAILY_LIMIT = 50


# ══════════════════════════════════════════════
#  常量 — 积分消耗表 & Token 预估表
# ══════════════════════════════════════════════

# 各端点的积分消耗表（单位: 积分）
CREDIT_COSTS = {
    "audit": 1, "prompt_check": 1, "batch_audit": 5,
    "banned_words": 0.5, "rug_pull": 1, "handshake": 0.5,
    "guardrail": 1, "api_scan": 2, "skill_invoke": 1,
    "a2a_task": 0.5, "mcp_call": 0.5,
}

# 各端点的预估 Token 消耗（输入/输出）
TOKEN_ESTIMATES = {
    "audit":         {"input": 5000,  "output": 2000},
    "prompt_check":  {"input": 500,   "output": 200},
    "banned_words":  {"input": 800,   "output": 300},
    "rug_pull":      {"input": 3000,  "output": 1000},
    "handshake":     {"input": 2000,  "output": 800},
    "guardrail":     {"input": 5000,  "output": 2000},
    "api_scan":      {"input": 8000,  "output": 3000},
    "skill_invoke":  {"input": 1000,  "output": 500},
    "a2a_task":      {"input": 800,   "output": 400},
    "mcp_call":      {"input": 1000,  "output": 500},
}


# ══════════════════════════════════════════════
#  工具函数（与 eco/a2a_gateway.py 保持一致的风格）
# ══════════════════════════════════════════════

def _load_json(path, default=None):
    """加载 JSON 文件，失败时返回默认值"""
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
    """线程安全保存 JSON 文件"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def _now_iso():
    """返回当前时间 ISO 格式（东八区）"""
    return datetime.now(TZ).isoformat()


def _generate_record_id():
    """生成调用记录 ID"""
    return f"rec-{uuid.uuid4().hex[:16]}"


def _parse_iso(iso_str):
    """
    解析 ISO 时间字符串为 datetime 对象。

    Args:
        iso_str (str): ISO 格式时间字符串

    Returns:
        datetime | None: 解析失败返回 None
    """
    if not iso_str:
        return None
    try:
        return datetime.fromisoformat(iso_str)
    except Exception:
        return None


def _percentile(values, p):
    """
    计算分位数（P50/P95/P99 等）。

    Args:
        values (list): 数值列表
        p (float): 百分位（0-100）

    Returns:
        float: 分位数值；空列表返回 0
    """
    if not values:
        return 0
    sorted_vals = sorted(values)
    # 线性插值法
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return float(sorted_vals[f])
    return float(sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f))


def _safe_float(value, default=0.0):
    """安全转换为 float，失败返回默认值"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value, default=0):
    """安全转换为 int，失败返回默认值"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ══════════════════════════════════════════════
#  CallRecord — 单次调用记录
# ══════════════════════════════════════════════

class CallRecord:
    """
    单次 API 调用记录管理

    记录字段:
      - record_id:       记录唯一 ID
      - endpoint:        端点名称（如 audit / prompt_check）
      - account_id:      用户账户 ID
      - agent_id:        Agent ID（可选）
      - input_tokens:    输入 Token 数
      - output_tokens:   输出 Token 数
      - credits_charged: 实际扣减的积分
      - latency_ms:      调用延迟（毫秒，可选）
      - created_at:      创建时间 ISO

    持久化:
      - 写入 api/data/call_records.json
      - 自动清理超过 30 天的记录
    """

    def __init__(self):
        self._records = []
        # 单条记录内存缓存时使用，加载时清空
        self._loaded = False

    def _load(self):
        """从磁盘加载调用记录"""
        data = _load_json(CALL_RECORDS_FILE, {"records": []})
        self._records = data.get("records", [])
        self._loaded = True

    def _save(self):
        """持久化调用记录到磁盘"""
        _save_json(CALL_RECORDS_FILE, {"records": self._records})

    def _cleanup(self):
        """清理超过 30 天的记录"""
        cutoff = datetime.now(TZ) - timedelta(days=_RECORD_RETENTION_DAYS)
        kept = []
        for rec in self._records:
            created = _parse_iso(rec.get("created_at", ""))
            if created is None:
                # 无法解析时间的记录直接保留，避免误删
                kept.append(rec)
                continue
            # 统一时区再比较
            if created.tzinfo is None:
                created = created.replace(tzinfo=TZ)
            if created >= cutoff:
                kept.append(rec)
        self._records = kept

    def track_call(self, endpoint, account_id, agent_id=None,
                   input_tokens=None, output_tokens=None,
                   credits_charged=None, latency_ms=None, metadata=None):
        """
        记录一次 API 调用。

        - 若未传 input_tokens/output_tokens，使用 TOKEN_ESTIMATES 中的预估值
        - 若未传 credits_charged，使用 CREDIT_COSTS 中的预估值
        - 持久化到 api/data/call_records.json
        - 自动清理超过 30 天的记录

        Args:
            endpoint (str):        端点名称
            account_id (str):      用户账户 ID
            agent_id (str):        Agent ID（可选）
            input_tokens (int):    输入 Token 数（可选，缺省用预估值）
            output_tokens (int):   输出 Token 数（可选，缺省用预估值）
            credits_charged (float): 扣减的积分（可选，缺省用预估值）
            latency_ms (int):      调用延迟毫秒（可选）
            metadata (dict):       扩展元数据（可选）

        Returns:
            dict: 本次调用记录
        """
        self._load()

        # Token 缺省值：取预估值，未知端点取 0
        est = TOKEN_ESTIMATES.get(endpoint, {"input": 0, "output": 0})
        in_tok = input_tokens if input_tokens is not None else est.get("input", 0)
        out_tok = output_tokens if output_tokens is not None else est.get("output", 0)

        # 积分缺省值：取预估值，未知端点取 0
        if credits_charged is not None:
            credits = _safe_float(credits_charged)
        else:
            credits = _safe_float(CREDIT_COSTS.get(endpoint, 0))

        record = {
            "record_id": _generate_record_id(),
            "endpoint": endpoint,
            "account_id": account_id,
            "agent_id": agent_id,
            "input_tokens": _safe_int(in_tok),
            "output_tokens": _safe_int(out_tok),
            "credits_charged": round(credits, 4),
            "latency_ms": _safe_int(latency_ms) if latency_ms is not None else None,
            "metadata": metadata or {},
            "created_at": _now_iso(),
        }

        self._records.append(record)
        # 写入前先清理过期记录
        self._cleanup()
        self._save()
        return record

    def list_records(self, endpoint=None, account_id=None, agent_id=None,
                     since=None, until=None, limit=None):
        """
        查询调用记录（支持多维过滤）。

        Args:
            endpoint (str):    按端点过滤
            account_id (str):  按账户过滤
            agent_id (str):    按 Agent 过滤
            since (datetime):  起始时间（含）
            until (datetime):  结束时间（含）
            limit (int):       最多返回条数

        Returns:
            list: 调用记录列表（按时间倒序）
        """
        self._load()
        results = []
        for rec in self._records:
            if endpoint and rec.get("endpoint") != endpoint:
                continue
            if account_id and rec.get("account_id") != account_id:
                continue
            if agent_id and rec.get("agent_id") != agent_id:
                continue
            created = _parse_iso(rec.get("created_at", ""))
            if created is not None:
                if created.tzinfo is None:
                    created = created.replace(tzinfo=TZ)
                if since is not None and created < since:
                    continue
                if until is not None and created > until:
                    continue
            results.append(rec)
        # 按时间倒序
        results.sort(key=lambda r: r.get("created_at", ""), reverse=True)
        if limit is not None:
            results = results[:limit]
        return results


# ══════════════════════════════════════════════
#  ObservabilityService — 成本可观测性分析
# ══════════════════════════════════════════════

class ObservabilityService:
    """
    成本可观测性分析服务

    提供:
      - cost_estimate          — 调用前成本预估
      - get_agent_efficiency   — Agent 效率指标
      - get_system_metrics     — 系统级指标（含图表渲染数据）
      - get_user_consumption   — 用户消耗明细（含异常检测）
      - get_cost_alerts        — 成本告警生成
    """

    def __init__(self):
        self._record_mgr = CallRecord()

    # ───────────────────────────────────────
    #  调用前预估
    # ───────────────────────────────────────

    def cost_estimate(self, endpoints):
        """
        调用前预估：给定端点列表，返回预估积分总消耗、预估 Token 总量、各端点明细。

        Args:
            endpoints (list): 端点名称列表，如 ["audit", "prompt_check"]

        Returns:
            dict: {
                "total_credits":   预估总积分,
                "total_tokens":    预估总 Token（输入+输出）,
                "total_input":     预估总输入 Token,
                "total_output":    预估总输出 Token,
                "endpoints":       各端点明细列表,
                "unknown_endpoints": 未知端点列表（无法预估）,
            }
        """
        total_credits = 0.0
        total_input = 0
        total_output = 0
        details = []
        unknown = []

        for ep in endpoints:
            credit = CREDIT_COSTS.get(ep)
            est = TOKEN_ESTIMATES.get(ep)
            if credit is None or est is None:
                unknown.append(ep)
                details.append({
                    "endpoint": ep,
                    "credits": credit if credit is not None else 0,
                    "input_tokens": est.get("input", 0) if est else 0,
                    "output_tokens": est.get("output", 0) if est else 0,
                    "known": False,
                })
                continue
            total_credits += credit
            total_input += est.get("input", 0)
            total_output += est.get("output", 0)
            details.append({
                "endpoint": ep,
                "credits": credit,
                "input_tokens": est.get("input", 0),
                "output_tokens": est.get("output", 0),
                "known": True,
            })

        return {
            "total_credits": round(total_credits, 4),
            "total_tokens": total_input + total_output,
            "total_input": total_input,
            "total_output": total_output,
            "endpoints": details,
            "unknown_endpoints": unknown,
            "estimated_at": _now_iso(),
        }

    # ───────────────────────────────────────
    #  Agent 效率指标
    # ───────────────────────────────────────

    def get_agent_efficiency(self, agent_id, days=7):
        """
        某 Agent 的效率指标。

        返回:
          - 总调用次数
          - 总积分消耗
          - 日均调用
          - 平均每次 Token 消耗（输入+输出）
          - Top3 最常用端点
          - 效率评分（0-100，基于积分/Token 比）

        Args:
            agent_id (str): Agent ID
            days (int):     统计天数

        Returns:
            dict: Agent 效率指标
        """
        since = datetime.now(TZ) - timedelta(days=days)
        records = self._record_mgr.list_records(agent_id=agent_id, since=since)

        total_calls = len(records)
        total_credits = sum(_safe_float(r.get("credits_charged", 0)) for r in records)
        total_tokens = sum(
            _safe_int(r.get("input_tokens", 0)) + _safe_int(r.get("output_tokens", 0))
            for r in records
        )
        avg_tokens = (total_tokens / total_calls) if total_calls > 0 else 0
        daily_avg_calls = round(total_calls / days, 2) if days > 0 else 0

        # Top3 最常用端点
        ep_counter = Counter(r.get("endpoint", "unknown") for r in records)
        top3 = [{"endpoint": ep, "count": cnt} for ep, cnt in ep_counter.most_common(3)]

        # 效率评分（0-100）：基于积分/Token 比
        # 思路: 单位积分产出的 Token 越多越高效；同时避免 Token 为 0 的情况
        # efficiency_ratio = total_tokens / total_credits（每积分产出多少 Token）
        # 归一化到 0-100: 取 ratio 的对数尺度，再线性映射
        efficiency_score = self._compute_efficiency_score(total_credits, total_tokens)

        return {
            "agent_id": agent_id,
            "days": days,
            "total_calls": total_calls,
            "total_credits": round(total_credits, 4),
            "daily_avg_calls": daily_avg_calls,
            "total_tokens": total_tokens,
            "avg_tokens_per_call": round(avg_tokens, 2),
            "top3_endpoints": top3,
            "efficiency_score": efficiency_score,
            "computed_at": _now_iso(),
        }

    def _compute_efficiency_score(self, total_credits, total_tokens):
        """
        计算效率评分（0-100）。

        基于积分/Token 比: 单位积分产出的 Token 越多，效率越高。
        - 无消耗或无 Token: 评分 0
        - ratio = total_tokens / total_credits
        - 使用对数尺度归一化到 0-100（ratio=1000 对应约 50 分，ratio=10000 对应约 80 分）

        Args:
            total_credits (float): 总积分消耗
            total_tokens (int):    总 Token 消耗

        Returns:
            int: 效率评分（0-100）
        """
        if total_credits <= 0 or total_tokens <= 0:
            return 0
        ratio = total_tokens / total_credits
        # 对数尺度: ratio=1 → 0, ratio=10 → ~23, ratio=100 → ~46, ratio=1000 → ~69, ratio=10000 → ~92
        # 用 log10(ratio+1) * 23 映射，并截断到 0-100
        score = math.log10(ratio + 1) * 23.0
        score = max(0, min(100, score))
        return round(score)

    # ───────────────────────────────────────
    #  系统级指标
    # ───────────────────────────────────────

    def get_system_metrics(self, hours=24):
        """
        系统级指标（返回格式适合直接渲染图表）。

        返回:
          - 总调用次数
          - 总积分消耗
          - 各端点调用分布（饼图数据）
          - P50/P95/P99 延迟（如有记录）
          - 每小时调用趋势（折线图数据）

        Args:
            hours (int): 统计小时数

        Returns:
            dict: 系统指标
        """
        since = datetime.now(TZ) - timedelta(hours=hours)
        records = self._record_mgr.list_records(since=since)

        total_calls = len(records)
        total_credits = sum(_safe_float(r.get("credits_charged", 0)) for r in records)

        # 各端点调用分布（饼图数据）
        ep_counter = Counter(r.get("endpoint", "unknown") for r in records)
        endpoint_distribution = [
            {"name": ep, "value": cnt}
            for ep, cnt in ep_counter.most_common()
        ]

        # 延迟分位数（仅统计有 latency_ms 的记录）
        latencies = [
            _safe_int(r.get("latency_ms"))
            for r in records
            if r.get("latency_ms") is not None
        ]
        latency_stats = {
            "p50": round(_percentile(latencies, 50), 2),
            "p95": round(_percentile(latencies, 95), 2),
            "p99": round(_percentile(latencies, 99), 2),
            "sample_count": len(latencies),
        }

        # 每小时调用趋势（折线图数据）
        hourly_trend = self._build_hourly_trend(records, hours)

        return {
            "hours": hours,
            "total_calls": total_calls,
            "total_credits": round(total_credits, 4),
            "endpoint_distribution": endpoint_distribution,
            "latency": latency_stats,
            "hourly_trend": hourly_trend,
            "computed_at": _now_iso(),
        }

    def _build_hourly_trend(self, records, hours):
        """
        构建每小时调用趋势（折线图数据）。

        Args:
            records (list): 调用记录列表
            hours (int):    统计小时数

        Returns:
            list: [{hour: "YYYY-MM-DDTHH", count: N, credits: M}, ...]
        """
        now = datetime.now(TZ)
        # 初始化每个小时桶
        buckets = {}
        for i in range(hours):
            t = now - timedelta(hours=(hours - 1 - i))
            key = t.strftime("%Y-%m-%dT%H")
            buckets[key] = {"hour": key, "count": 0, "credits": 0.0}

        for rec in records:
            created = _parse_iso(rec.get("created_at", ""))
            if created is None:
                continue
            if created.tzinfo is None:
                created = created.replace(tzinfo=TZ)
            key = created.strftime("%Y-%m-%dT%H")
            if key in buckets:
                buckets[key]["count"] += 1
                buckets[key]["credits"] += _safe_float(rec.get("credits_charged", 0))

        # 按时间顺序输出
        result = []
        for i in range(hours):
            t = now - timedelta(hours=(hours - 1 - i))
            key = t.strftime("%Y-%m-%dT%H")
            bucket = buckets[key]
            result.append({
                "hour": key,
                "count": bucket["count"],
                "credits": round(bucket["credits"], 4),
            })
        return result

    # ───────────────────────────────────────
    #  用户消耗明细
    # ───────────────────────────────────────

    def get_user_consumption(self, account_id, days=30):
        """
        用户消耗明细（含异常检测、免费额度剩余）。

        返回:
          - 总消耗（积分）
          - 日均消耗
          - 消耗趋势（按天）
          - 端点使用分布
          - 免费额度剩余（50 次/天）
          - 异常检测: 某天消耗超过日均 3 倍标记为 abnormal

        Args:
            account_id (str): 用户账户 ID
            days (int):       统计天数

        Returns:
            dict: 用户消耗明细
        """
        since = datetime.now(TZ) - timedelta(days=days)
        records = self._record_mgr.list_records(account_id=account_id, since=since)

        total_credits = sum(_safe_float(r.get("credits_charged", 0)) for r in records)
        total_calls = len(records)
        daily_avg = round(total_credits / days, 4) if days > 0 else 0

        # 按天聚合消耗趋势
        daily_map = defaultdict(lambda: {"credits": 0.0, "calls": 0})
        for rec in records:
            created = _parse_iso(rec.get("created_at", ""))
            if created is None:
                continue
            day_key = created.strftime("%Y-%m-%d")
            daily_map[day_key]["credits"] += _safe_float(rec.get("credits_charged", 0))
            daily_map[day_key]["calls"] += 1

        # 构建完整趋势（补齐空缺天数）
        now = datetime.now(TZ)
        trend = []
        for i in range(days):
            t = now - timedelta(days=(days - 1 - i))
            day_key = t.strftime("%Y-%m-%d")
            item = daily_map.get(day_key, {"credits": 0.0, "calls": 0})
            # 异常检测: 某天消耗超过日均 3 倍
            is_abnormal = (
                daily_avg > 0
                and item["credits"] > 0
                and item["credits"] > daily_avg * 3
            )
            trend.append({
                "date": day_key,
                "credits": round(item["credits"], 4),
                "calls": item["calls"],
                "abnormal": is_abnormal,
            })

        # 端点使用分布
        ep_counter = Counter(r.get("endpoint", "unknown") for r in records)
        endpoint_usage = [
            {"endpoint": ep, "count": cnt,
             "credits": round(sum(
                 _safe_float(r.get("credits_charged", 0))
                 for r in records if r.get("endpoint") == ep
             ), 4)}
            for ep, cnt in ep_counter.most_common()
        ]

        # 免费额度剩余（基于今日调用次数）
        today_key = now.strftime("%Y-%m-%d")
        today_calls = daily_map.get(today_key, {"calls": 0})["calls"]
        free_remaining = max(0, FREE_DAILY_LIMIT - today_calls)

        return {
            "account_id": account_id,
            "days": days,
            "total_credits": round(total_credits, 4),
            "total_calls": total_calls,
            "daily_avg_credits": daily_avg,
            "trend": trend,
            "endpoint_usage": endpoint_usage,
            "free_quota": {
                "daily_limit": FREE_DAILY_LIMIT,
                "used_today": today_calls,
                "remaining": free_remaining,
            },
            "abnormal_days": [t for t in trend if t["abnormal"]],
            "computed_at": _now_iso(),
        }

    # ───────────────────────────────────────
    #  成本告警
    # ───────────────────────────────────────

    def get_cost_alerts(self):
        """
        生成成本告警并持久化到 cost_alerts.json（保留最近 1000 条）。

        告警规则:
          - 规则1（high）:   单用户 24h 消耗超过 500 积分
          - 规则2（medium）: 系统总消耗较前日增长超过 50%
          - 规则3（low）:    某端点调用量异常增长（超过 7 日均值 3 倍）

        Returns:
            list: 告警列表 [{level, rule, detail, agent_id/account_id, created_at}, ...]
        """
        now = datetime.now(TZ)
        alerts = []

        # ── 规则1: 单用户 24h 消耗超过 500 积分 ──
        since_24h = now - timedelta(hours=24)
        records_24h = self._record_mgr.list_records(since=since_24h)
        user_credits = defaultdict(float)
        for rec in records_24h:
            user_credits[rec.get("account_id", "unknown")] += _safe_float(
                rec.get("credits_charged", 0)
            )
        for account_id, credits in user_credits.items():
            if credits > 500:
                alerts.append({
                    "level": "high",
                    "rule": "rule1_user_24h_over_500",
                    "detail": f"用户 {account_id} 24 小时内消耗 {round(credits, 2)} 积分，超过 500 阈值",
                    "account_id": account_id,
                    "credits": round(credits, 4),
                    "created_at": _now_iso(),
                })

        # ── 规则2: 系统总消耗较前日增长超过 50% ──
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        today_records = self._record_mgr.list_records(
            since=today_start, until=now
        )
        yesterday_records = self._record_mgr.list_records(
            since=yesterday_start, until=today_start
        )
        today_total = sum(_safe_float(r.get("credits_charged", 0)) for r in today_records)
        yesterday_total = sum(_safe_float(r.get("credits_charged", 0)) for r in yesterday_records)
        if yesterday_total > 0:
            growth_rate = (today_total - yesterday_total) / yesterday_total
            if growth_rate > 0.5:
                alerts.append({
                    "level": "medium",
                    "rule": "rule2_system_daily_growth_over_50pct",
                    "detail": (
                        f"系统今日总消耗 {round(today_total, 2)} 积分，"
                        f"较昨日 {round(yesterday_total, 2)} 增长 {round(growth_rate * 100, 2)}%，"
                        f"超过 50% 阈值"
                    ),
                    "today_total": round(today_total, 4),
                    "yesterday_total": round(yesterday_total, 4),
                    "growth_rate": round(growth_rate, 4),
                    "created_at": _now_iso(),
                })

        # ── 规则3: 某端点调用量异常增长（超过 7 日均值 3 倍） ──
        since_7d = now - timedelta(days=7)
        since_1d = now - timedelta(days=1)
        records_7d = self._record_mgr.list_records(since=since_7d)
        records_1d = self._record_mgr.list_records(since=since_1d)

        # 7 日各端点调用次数
        ep_7d = Counter(r.get("endpoint", "unknown") for r in records_7d)
        # 1 日各端点调用次数
        ep_1d = Counter(r.get("endpoint", "unknown") for r in records_1d)

        for ep, count_1d in ep_1d.items():
            count_7d = ep_7d.get(ep, 0)
            # 7 日日均
            daily_avg_7d = count_7d / 7.0 if count_7d > 0 else 0
            if daily_avg_7d > 0 and count_1d > daily_avg_7d * 3:
                alerts.append({
                    "level": "low",
                    "rule": "rule3_endpoint_anomaly_growth",
                    "detail": (
                        f"端点 {ep} 近 24 小时调用 {count_1d} 次，"
                        f"超过 7 日日均 {round(daily_avg_7d, 2)} 次的 3 倍"
                    ),
                    "endpoint": ep,
                    "count_24h": count_1d,
                    "daily_avg_7d": round(daily_avg_7d, 2),
                    "created_at": _now_iso(),
                })

        # 持久化告警（保留最近 1000 条）
        self._persist_alerts(alerts)

        return alerts

    def _persist_alerts(self, new_alerts):
        """
        持久化告警到 cost_alerts.json，保留最近 1000 条。

        Args:
            new_alerts (list): 新生成的告警列表
        """
        if not new_alerts:
            return
        data = _load_json(COST_ALERTS_FILE, {"alerts": []})
        existing = data.get("alerts", [])
        existing.extend(new_alerts)
        # 按时间倒序保留最近 _ALERT_MAX_COUNT 条
        existing.sort(key=lambda a: a.get("created_at", ""), reverse=True)
        existing = existing[:_ALERT_MAX_COUNT]
        data["alerts"] = existing
        _save_json(COST_ALERTS_FILE, data)

    def list_alerts(self, level=None, limit=100):
        """
        查询已持久化的成本告警。

        Args:
            level (str): 按级别过滤（high/medium/low）
            limit (int): 最多返回条数

        Returns:
            list: 告警列表（按时间倒序）
        """
        data = _load_json(COST_ALERTS_FILE, {"alerts": []})
        alerts = data.get("alerts", [])
        if level:
            alerts = [a for a in alerts if a.get("level") == level]
        alerts.sort(key=lambda a: a.get("created_at", ""), reverse=True)
        return alerts[:limit]


# ══════════════════════════════════════════════
#  API路由处理函数
# ══════════════════════════════════════════════

def register_routes(handler):
    """
    将可观测性模块路由注册到 HTTPServer 的 Handler 上。

    兼容 api/server.py 的 AIShieldHandler 模式。
    与 eco/a2a_gateway.py 的 register_routes 风格保持一致。

    Args:
        handler: AIShieldHandler 实例
    """
    original_do_get = handler.do_GET
    original_do_post = handler.do_POST

    def do_get_patched(self):
        """扩展 GET 路由"""
        if hasattr(self, "_parsed_path"):
            parsed = self._parsed_path
        else:
            from urllib.parse import urlparse
            parsed = urlparse(self.path)
        path = parsed.path
        from urllib.parse import parse_qs
        query = parse_qs(parsed.query)

        svc = ObservabilityService()

        # ── GET /api/v1/observability/cost-estimate — 成本预估 ──
        if path == "/api/v1/observability/cost-estimate":
            endpoints_param = query.get("endpoints", [""])[0]
            if not endpoints_param.strip():
                self._send_json({"error": "endpoints 参数必填（逗号分隔）"}, 400)
                return
            endpoints = [e.strip() for e in endpoints_param.split(",") if e.strip()]
            try:
                result = svc.cost_estimate(endpoints)
                self._send_json({"success": True, **result})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ── GET /api/v1/observability/agent/{agent_id}/efficiency — Agent效率 ──
        prefix_eff = "/api/v1/observability/agent/"
        suffix_eff = "/efficiency"
        if path.startswith(prefix_eff) and path.endswith(suffix_eff):
            agent_id = path[len(prefix_eff):-len(suffix_eff)]
            if not agent_id:
                self._send_json({"error": "agent_id 必填"}, 400)
                return
            try:
                days = int(query.get("days", [7])[0])
            except (ValueError, IndexError):
                days = 7
            try:
                result = svc.get_agent_efficiency(agent_id, days=days)
                self._send_json({"success": True, **result})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ── GET /api/v1/observability/system — 系统指标 ──
        if path == "/api/v1/observability/system":
            try:
                hours = int(query.get("hours", [24])[0])
            except (ValueError, IndexError):
                hours = 24
            try:
                result = svc.get_system_metrics(hours=hours)
                self._send_json({"success": True, **result})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ── GET /api/v1/observability/user/{account_id}/consumption — 用户消耗 ──
        prefix_cons = "/api/v1/observability/user/"
        suffix_cons = "/consumption"
        if path.startswith(prefix_cons) and path.endswith(suffix_cons):
            account_id = path[len(prefix_cons):-len(suffix_cons)]
            if not account_id:
                self._send_json({"error": "account_id 必填"}, 400)
                return
            try:
                days = int(query.get("days", [30])[0])
            except (ValueError, IndexError):
                days = 30
            try:
                result = svc.get_user_consumption(account_id, days=days)
                self._send_json({"success": True, **result})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ── GET /api/v1/observability/alerts — 成本告警 ──
        if path == "/api/v1/observability/alerts":
            level = query.get("level", [None])[0]
            try:
                limit = int(query.get("limit", [100])[0])
            except (ValueError, IndexError):
                limit = 100
            try:
                # 同时触发新告警生成，再返回持久化的告警列表
                svc.get_cost_alerts()
                alerts = svc.list_alerts(level=level, limit=limit)
                self._send_json({
                    "success": True,
                    "total": len(alerts),
                    "alerts": alerts,
                })
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # 非本模块路由
        original_do_get(self)

    def do_post_patched(self):
        """扩展 POST 路由"""
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

        # ── POST /api/v1/observability/track — 手动记录调用 ──
        if path == "/api/v1/observability/track":
            endpoint = data.get("endpoint", "").strip()
            account_id = data.get("account_id", "").strip()
            if not endpoint or not account_id:
                self._send_json(
                    {"error": "endpoint 和 account_id 均为必填"}, 400
                )
                return
            try:
                record_mgr = CallRecord()
                record = record_mgr.track_call(
                    endpoint=endpoint,
                    account_id=account_id,
                    agent_id=data.get("agent_id"),
                    input_tokens=data.get("input_tokens"),
                    output_tokens=data.get("output_tokens"),
                    credits_charged=data.get("credits_charged"),
                    latency_ms=data.get("latency_ms"),
                    metadata=data.get("metadata"),
                )
                self._send_json({"success": True, "record": record}, 201)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # 非本模块路由
        original_do_post(self)

    handler.do_GET = do_get_patched.__get__(handler, type(handler))
    handler.do_POST = do_post_patched.__get__(handler, type(handler))


# ══════════════════════════════════════════════
#  独立测试入口
# ══════════════════════════════════════════════

if __name__ == "__main__":
    print("=== 成本可观测性模块 测试 ===")

    # ── 1. 成本预估 ──
    print("\n--- 1. 成本预估 ---")
    svc = ObservabilityService()
    estimate = svc.cost_estimate(["audit", "prompt_check", "unknown_ep"])
    print(f"  端点列表: audit, prompt_check, unknown_ep")
    print(f"  预估总积分: {estimate['total_credits']}")
    print(f"  预估总 Token: {estimate['total_tokens']}")
    print(f"  未知端点: {estimate['unknown_endpoints']}")

    # ── 2. 记录调用 ──
    print("\n--- 2. 记录调用 ---")
    record_mgr = CallRecord()
    # 记录多条测试数据
    rec1 = record_mgr.track_call(
        endpoint="audit",
        account_id="user-test-001",
        agent_id="agent-test-001",
        latency_ms=1200,
    )
    print(f"  记录1: {rec1['record_id']} endpoint={rec1['endpoint']} credits={rec1['credits_charged']}")
    rec2 = record_mgr.track_call(
        endpoint="prompt_check",
        account_id="user-test-001",
        agent_id="agent-test-001",
        latency_ms=300,
    )
    print(f"  记录2: {rec2['record_id']} endpoint={rec2['endpoint']} credits={rec2['credits_charged']}")
    rec3 = record_mgr.track_call(
        endpoint="audit",
        account_id="user-test-002",
        agent_id="agent-test-001",
        latency_ms=800,
    )
    print(f"  记录3: {rec3['record_id']} endpoint={rec3['endpoint']} credits={rec3['credits_charged']}")

    # ── 3. Agent 效率 ──
    print("\n--- 3. Agent 效率 ---")
    eff = svc.get_agent_efficiency("agent-test-001", days=7)
    print(f"  Agent: {eff['agent_id']}")
    print(f"  总调用次数: {eff['total_calls']}")
    print(f"  总积分消耗: {eff['total_credits']}")
    print(f"  日均调用: {eff['daily_avg_calls']}")
    print(f"  平均每次 Token: {eff['avg_tokens_per_call']}")
    print(f"  Top3 端点: {eff['top3_endpoints']}")
    print(f"  效率评分: {eff['efficiency_score']}/100")

    # ── 4. 系统指标 ──
    print("\n--- 4. 系统指标 ---")
    metrics = svc.get_system_metrics(hours=24)
    print(f"  总调用次数: {metrics['total_calls']}")
    print(f"  总积分消耗: {metrics['total_credits']}")
    print(f"  端点分布: {metrics['endpoint_distribution']}")
    print(f"  延迟 P50/P95/P99: {metrics['latency']['p50']}/{metrics['latency']['p95']}/{metrics['latency']['p99']}")
    print(f"  每小时趋势条数: {len(metrics['hourly_trend'])}")

    # ── 5. 用户消耗 ──
    print("\n--- 5. 用户消耗 ---")
    cons = svc.get_user_consumption("user-test-001", days=30)
    print(f"  账户: {cons['account_id']}")
    print(f"  总消耗: {cons['total_credits']}")
    print(f"  日均消耗: {cons['daily_avg_credits']}")
    print(f"  端点使用: {cons['endpoint_usage']}")
    print(f"  免费额度剩余: {cons['free_quota']['remaining']}/{cons['free_quota']['daily_limit']}")
    print(f"  异常天数: {len(cons['abnormal_days'])}")

    # ── 6. 成本告警 ──
    print("\n--- 6. 成本告警 ---")
    alerts = svc.get_cost_alerts()
    print(f"  本次生成告警数: {len(alerts)}")
    for a in alerts:
        print(f"    [{a['level']}] {a['rule']}: {a['detail'][:50]}...")
    persisted = svc.list_alerts()
    print(f"  持久化告警总数: {len(persisted)}")

    print("\n=== 全部测试通过 ===")
