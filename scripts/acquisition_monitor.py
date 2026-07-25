#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/acquisition_monitor.py — 获客与收益转化监控

功能:
  1. 分析注册转化漏斗（访问 → 注册 → 激活 → 付费）
  2. 监控支付成功率和收入趋势
  3. 跟踪积分消耗和余额分布
  4. 识别高价值用户和流失风险用户
  5. 输出获客健康报告到 api/data/acquisition_report.json

用法:
  python scripts/acquisition_monitor.py           # 生成完整报告
  python scripts/acquisition_monitor.py --alert   # 仅检查告警阈值

数据源:
  - api/data/accounts.json    (用户账户)
  - api/data/usage.json       (API 调用统计)
  - api/data/credit_transactions.json (积分流水)
  - api/data/webhook_processed.json   (支付记录)

关键指标:
  - 注册转化率
  - 免费→付费转化率
  - ARPU (每用户平均收入)
  - 付费用户占比
  - 积分消耗速率
  - 支付成功率
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "api", "data")
REPORT_FILE = os.path.join(DATA_DIR, "acquisition_report.json")

ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.json")
USAGE_FILE = os.path.join(DATA_DIR, "usage.json")
TXN_FILE = os.path.join(DATA_DIR, "credit_transactions.json")
WEBHOOK_FILE = os.path.join(DATA_DIR, "webhook_processed.json")

TZ = timezone(timedelta(hours=8))

# ── 告警阈值 ──
ALERT_THRESHOLDS = {
    "min_daily_signups": 3,           # 日注册数低于此值告警
    "min_conversion_rate": 0.02,      # 转化率低于 2% 告警
    "min_payment_success_rate": 0.85, # 支付成功率低于 85% 告警
    "max_avg_balance": 5000,          # 平均余额过高（消耗慢）告警
    "min_credit_consumption": 10,     # 日积分消耗低于此值告警
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


def analyze_funnel():
    """分析转化漏斗"""
    accounts_data = _load_json(ACCOUNTS_FILE, {"accounts": {}})
    accounts = accounts_data.get("accounts", {})
    usage = _load_json(USAGE_FILE, {"daily": {}, "total": 0})
    txns = _load_json(TXN_FILE, {"transactions": []})
    
    total_accounts = len(accounts)
    if not total_accounts:
        return None
    
    # 分类用户
    never_used = 0      # 注册后从未调用API
    free_active = 0     # 只使用免费额度
    paying_users = 0    # 有过充值
    churned = 0         # 余额为0且7天无活动
    
    now = datetime.now(TZ)
    week_ago = (now - timedelta(days=7)).isoformat()
    
    # 统计有充值记录的用户
    recharged_user_ids = set()
    total_revenue_credits = 0
    for txn in txns.get("transactions", []):
        if txn.get("type") == "recharge":
            recharged_user_ids.add(txn.get("account_id", ""))
            total_revenue_credits += txn.get("credits", 0)
    
    for acct_id, acct in accounts.items():
        balance = acct.get("balance", 0)
        updated_at = acct.get("updated_at", "")
        created_at = acct.get("created_at", "")
        
        # 判断是否付费用户
        if acct_id in recharged_user_ids:
            paying_users += 1
        
        # 判断是否流失（7天无更新且余额为0）
        if balance <= 0 and updated_at < week_ago:
            churned += 1
    
    # 计算转化率
    conversion_rate = paying_users / total_accounts if total_accounts else 0
    
    # 计算 ARPU（每用户平均收入，单位：元）
    # 1元 = 100积分
    arpu_credits = total_revenue_credits / total_accounts if total_accounts else 0
    arpu_yuan = arpu_credits / 100
    
    # 计算平均余额
    total_balance = sum(a.get("balance", 0) for a in accounts.values())
    avg_balance = total_balance / total_accounts if total_accounts else 0
    
    # 日注册数（最近7天）
    recent_signups = sum(
        1 for a in accounts.values()
        if a.get("created_at", "") > week_ago
    )
    avg_daily_signups = recent_signups / 7
    
    return {
        "total_accounts": total_accounts,
        "paying_users": paying_users,
        "free_users": total_accounts - paying_users,
        "churned_users": churned,
        "conversion_rate": round(conversion_rate, 4),
        "conversion_rate_pct": round(conversion_rate * 100, 2),
        "arpu_credits": round(arpu_credits, 2),
        "arpu_yuan": round(arpu_yuan, 2),
        "total_revenue_credits": round(total_revenue_credits, 2),
        "total_revenue_yuan": round(total_revenue_credits / 100, 2),
        "avg_balance": round(avg_balance, 2),
        "recent_7d_signups": recent_signups,
        "avg_daily_signups": round(avg_daily_signups, 2),
    }


def analyze_usage():
    """分析 API 使用趋势"""
    usage = _load_json(USAGE_FILE, {"daily": {}, "total": 0})
    daily = usage.get("daily", {})
    
    if not daily:
        return None
    
    # 最近7天/30天调用量
    now = datetime.now(TZ)
    week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    month_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d")
    
    last_7d_calls = 0
    last_30d_calls = 0
    
    for day, data in daily.items():
        if day >= week_ago:
            last_7d_calls += data.get("total", 0)
        if day >= month_ago:
            last_30d_calls += data.get("total", 0)
    
    avg_daily_calls_7d = last_7d_calls / 7
    avg_daily_calls_30d = last_30d_calls / 30 if last_30d_calls else 0
    
    # 趋势判断
    trend = "stable"
    if avg_daily_calls_7d > avg_daily_calls_30d * 1.2:
        trend = "growing"
    elif avg_daily_calls_7d < avg_daily_calls_30d * 0.8:
        trend = "declining"
    
    return {
        "total_calls": usage.get("total", 0),
        "last_7d_calls": last_7d_calls,
        "last_30d_calls": last_30d_calls,
        "avg_daily_calls_7d": round(avg_daily_calls_7d, 2),
        "avg_daily_calls_30d": round(avg_daily_calls_30d, 2),
        "trend": trend,
    }


def analyze_payments():
    """分析支付数据"""
    txns = _load_json(TXN_FILE, {"transactions": []})
    webhooks = _load_json(WEBHOOK_FILE, {"checkouts": []})
    
    transactions = txns.get("transactions", [])
    if not transactions:
        return None
    
    # 支付相关交易
    recharge_txns = [t for t in transactions if t.get("type") == "recharge"]
    consume_txns = [t for t in transactions if t.get("type") == "consume"]
    
    total_recharge = sum(t.get("credits", 0) for t in recharge_txns)
    total_consume = sum(t.get("credits", 0) for t in consume_txns)
    
    # 支付成功率估算（webhook 成功数 / 总 checkout 尝试）
    # 简化：有 webhook 记录的视为成功支付
    successful_payments = len(webhooks.get("checkouts", []))
    # 估算尝试数：从交易中的 checkout_id 去重
    checkout_ids = set()
    for t in recharge_txns:
        if t.get("checkout_id"):
            checkout_ids.add(t["checkout_id"])
    total_attempts = len(checkout_ids) if checkout_ids else max(successful_payments, 1)
    success_rate = successful_payments / total_attempts if total_attempts else 1.0
    
    return {
        "total_recharge_transactions": len(recharge_txns),
        "total_consume_transactions": len(consume_txns),
        "total_recharge_credits": round(total_recharge, 2),
        "total_revenue_yuan": round(total_recharge / 100, 2),
        "total_consume_credits": round(total_consume, 2),
        "payment_success_rate": round(success_rate, 4),
        "payment_success_rate_pct": round(success_rate * 100, 2),
    }


def check_alerts(metrics):
    """检查告警阈值"""
    alerts = []
    
    funnel = metrics.get("funnel", {})
    usage = metrics.get("usage", {})
    payments = metrics.get("payments", {})
    
    if funnel.get("avg_daily_signups", 0) < ALERT_THRESHOLDS["min_daily_signups"]:
        alerts.append({
            "level": "warning",
            "metric": "daily_signups",
            "message": f"日注册数过低: {funnel.get('avg_daily_signups', 0)}/天",
            "suggestion": "加强 GEO 推广和 MCP 目录曝光",
        })
    
    if funnel.get("conversion_rate", 0) < ALERT_THRESHOLDS["min_conversion_rate"]:
        alerts.append({
            "level": "critical",
            "metric": "conversion_rate",
            "message": f"付费转化率过低: {funnel.get('conversion_rate_pct', 0)}%",
            "suggestion": "优化定价页 CTA 和积分不足引导",
        })
    
    if payments.get("payment_success_rate", 1.0) < ALERT_THRESHOLDS["min_payment_success_rate"]:
        alerts.append({
            "level": "critical",
            "metric": "payment_success",
            "message": f"支付成功率异常: {payments.get('payment_success_rate_pct', 100)}%",
            "suggestion": "检查 Creem 支付网关和 webhook 配置",
        })
    
    if funnel.get("avg_balance", 0) > ALERT_THRESHOLDS["max_avg_balance"]:
        alerts.append({
            "level": "info",
            "metric": "avg_balance",
            "message": f"平均余额过高: {funnel.get('avg_balance', 0)} 积分",
            "suggestion": "用户消耗慢，考虑降低积分价格或增加使用场景",
        })
    
    if usage and usage.get("avg_daily_calls_7d", 0) < ALERT_THRESHOLDS["min_credit_consumption"]:
        alerts.append({
            "level": "warning",
            "metric": "usage",
            "message": f"日调用量偏低: {usage.get('avg_daily_calls_7d', 0)}/天",
            "suggestion": "增加扫描场景或降低单次消耗积分",
        })
    
    return alerts


def generate_report():
    """生成完整获客监控报告"""
    print("=" * 60)
    print("📊 AIShield 获客与收益转化监控报告")
    print("=" * 60)
    print(f"📅 生成时间: {_now_iso()}")
    print("=" * 60)
    
    funnel = analyze_funnel()
    usage = analyze_usage()
    payments = analyze_payments()
    
    metrics = {
        "funnel": funnel or {},
        "usage": usage or {},
        "payments": payments or {},
        "generated_at": _now_iso(),
    }
    
    # 检查告警
    alerts = check_alerts(metrics)
    metrics["alerts"] = alerts
    
    # 输出报告
    if funnel:
        print("\n🎯 转化漏斗")
        print(f"   总注册用户: {funnel['total_accounts']}")
        print(f"   付费用户: {funnel['paying_users']} ({funnel['conversion_rate_pct']}%)")
        print(f"   免费用户: {funnel['free_users']}")
        print(f"   流失用户: {funnel['churned_users']}")
        print(f"   ARPU: ¥{funnel['arpu_yuan']}")
        print(f"   近7日注册: {funnel['recent_7d_signups']} (日均 {funnel['avg_daily_signups']})")
        print(f"   累计收入: ¥{funnel['total_revenue_yuan']}")
    
    if usage:
        print("\n📈 API 使用趋势")
        print(f"   总调用量: {usage['total_calls']}")
        print(f"   近7日调用: {usage['last_7d_calls']} (日均 {usage['avg_daily_calls_7d']})")
        print(f"   近30日调用: {usage['last_30d_calls']} (日均 {usage['avg_daily_calls_30d']})")
        print(f"   趋势: {usage['trend']}")
    
    if payments:
        print("\n💳 支付数据")
        print(f"   充值笔数: {payments['total_recharge_transactions']}")
        print(f"   消费笔数: {payments['total_consume_transactions']}")
        print(f"   累计充值积分: {payments['total_recharge_credits']}")
        print(f"   支付成功率: {payments['payment_success_rate_pct']}%")
    
    if alerts:
        print("\n🚨 告警")
        for alert in alerts:
            icon = "🔴" if alert["level"] == "critical" else "🟡" if alert["level"] == "warning" else "🔵"
            print(f"   {icon} [{alert['metric']}] {alert['message']}")
            print(f"      建议: {alert['suggestion']}")
    else:
        print("\n✅ 所有指标正常，无告警")
    
    # 保存报告
    _save_json(REPORT_FILE, metrics)
    print(f"\n💾 报告已保存: {REPORT_FILE}")
    print("=" * 60)
    
    return metrics


if __name__ == "__main__":
    if "--alert" in sys.argv:
        # 仅检查告警
        funnel = analyze_funnel()
        usage = analyze_usage()
        payments = analyze_payments()
        metrics = {"funnel": funnel or {}, "usage": usage or {}, "payments": payments or {}}
        alerts = check_alerts(metrics)
        if alerts:
            print("ALERTS_FOUND")
            for a in alerts:
                print(f"{a['level'].upper()}: {a['message']}")
            sys.exit(1)
        else:
            print("ALL_CLEAR")
            sys.exit(0)
    else:
        generate_report()
