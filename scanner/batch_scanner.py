"""
AIShield 批量扫描引擎 — 爬取MCP目录 → 批量扫描 → 入库

支持:
  - 爬取Smithery/Glama/PulseMCP/Smithery API的MCP Server列表
  - 批量安全扫描（可配置并发和延迟）
  - 增量扫描（跳过最近7天内扫描过的工具）
  - 并发控制（ThreadPoolExecutor, max_workers=3）
  - 进度回调
  - 结果持久化到JSON文件
  - 生成安全报告
"""

import json
import os
import re
import time
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib import request as urllib_request
from urllib.parse import quote
from urllib.error import URLError
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scanner.engine import scan

TZ = timezone(timedelta(hours=8))
USER_AGENT = "AIShield-BatchScanner/4.1"
SCANNER_VERSION = "4.1"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)
BATCH_DB = os.path.join(DATA_DIR, "batch_scans.json")

# ── 线程安全的进度输出锁 ──
_progress_lock = threading.Lock()


def urlopen_json(url, timeout=15):
    """安全地获取JSON"""
    try:
        req = urllib_request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        with urllib_request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  [WARN] Failed to fetch {url}: {e}")
        return None


# ── MCP目录爬取 ──

def fetch_smithery_servers(limit=100):
    """从Smithery Registry爬取MCP Server列表"""
    print(f"[*] Fetching Smithery Registry servers (limit={limit})...")
    servers = []

    # Smithery Registry search API
    url = f"https://registry.smithery.ai/servers?limit={limit}"
    data = urlopen_json(url)

    if data and isinstance(data, list):
        for item in data[:limit]:
            repo = item.get("repository", {})
            github = repo.get("url", "")
            if not github and repo.get("owner") and repo.get("name"):
                github = f"https://github.com/{repo['owner']}/{repo['name']}"
            if github and "github.com" in github:
                servers.append({
                    "url": github,
                    "name": item.get("identifier", repo.get("name", "")),
                    "source": "smithery",
                    "description": item.get("description", "")[:200],
                })

    print(f"  Found {len(servers)} servers from Smithery Registry")
    return servers


def fetch_smithery_api_servers(limit=100):
    """从Smithery API (smithery.ai/api/servers) 获取热门工具列表
    如果API不可用则回退到GitHub搜索替代
    """
    print(f"[*] Fetching Smithery API servers (limit={limit})...")
    servers = []

    # 尝试Smithery API
    url = f"https://smithery.ai/api/servers?limit={limit}"
    data = urlopen_json(url, timeout=10)

    if data and isinstance(data, list):
        for item in data[:limit]:
            repo = item.get("repository", {})
            github = repo.get("url", "")
            if not github and repo.get("owner") and repo.get("name"):
                github = f"https://github.com/{repo['owner']}/{repo['name']}"
            if not github and item.get("githubUrl"):
                github = item.get("githubUrl")
            if not github and item.get("sourceUrl"):
                github = item.get("sourceUrl")
            if github and "github.com" in github:
                servers.append({
                    "url": github,
                    "name": item.get("identifier", item.get("name", repo.get("name", ""))),
                    "source": "smithery-api",
                    "description": (item.get("description", "") or "")[:200],
                    "stars": item.get("stars", item.get("starCount", 0)),
                })
        print(f"  Found {len(servers)} servers from Smithery API")
        return servers

    # 如果Smithery API不可用，回退到GitHub搜索
    print(f"  [FALLBACK] Smithery API unavailable, falling back to GitHub search...")
    fallback_servers = fetch_github_mcp_servers(limit, query_prefix="smithery+mcp")
    for s in fallback_servers:
        s["source"] = "smithery-api-github-fallback"
    return fallback_servers


def fetch_glama_servers(limit=100):
    """从Glama爬取MCP Server列表"""
    print(f"[*] Fetching Glama servers (limit={limit})...")
    servers = []

    # Glama MCP directory API
    url = f"https://glama.ai/api/mcp/v1/servers?limit={limit}&sort=popular"
    data = urlopen_json(url)

    if data:
        items = data.get("servers", data if isinstance(data, list) else [])
        for item in items[:limit]:
            github = item.get("githubUrl", item.get("sourceUrl", item.get("url", "")))
            if github and "github.com" in github:
                servers.append({
                    "url": github,
                    "name": item.get("name", item.get("identifier", "")),
                    "source": "glama",
                    "description": (item.get("description", "") or "")[:200],
                })

    print(f"  Found {len(servers)} servers from Glama")
    return servers


def fetch_pulsemcp_servers(limit=100):
    """从PulseMCP爬取MCP Server列表"""
    print(f"[*] Fetching PulseMCP servers (limit={limit})...")
    servers = []

    url = f"https://pulsemcp.com/api/servers?limit={limit}"
    data = urlopen_json(url)

    if data and isinstance(data, list):
        for item in data[:limit]:
            github = item.get("repository", item.get("github", item.get("url", "")))
            if github and "github.com" in github:
                servers.append({
                    "url": github,
                    "name": item.get("name", item.get("identifier", "")),
                    "source": "pulsemcp",
                    "description": (item.get("description", "") or "")[:200],
                })

    print(f"  Found {len(servers)} servers from PulseMCP")
    return servers


def fetch_github_mcp_servers(limit=50, query_prefix=None):
    """从GitHub搜索MCP Server仓库"""
    prefix = query_prefix or "mcp-server"
    print(f"[*] Searching GitHub for MCP servers (limit={limit}, prefix={prefix})...")
    servers = []

    # GitHub search API (no auth needed for basic search)
    queries = [
        f"{prefix}+language:typescript+stars:>10",
        f"{prefix}+language:python+stars:>10",
        "modelcontextprotocol+stars:>5",
    ]

    seen = set()
    for q in queries:
        url = f"https://api.github.com/search/repositories?q={q}&per_page=20&sort=stars"
        data = urlopen_json(url)
        if data and "items" in data:
            for item in data["items"][:20]:
                full_name = item["full_name"]
                if full_name not in seen:
                    seen.add(full_name)
                    servers.append({
                        "url": item["html_url"],
                        "name": full_name,
                        "source": "github-search",
                        "description": (item.get("description", "") or "")[:200],
                        "stars": item.get("stargazers_count", 0),
                    })
        time.sleep(2)  # GitHub rate limit

    print(f"  Found {len(servers)} servers from GitHub search")
    return servers[:limit]


# ── 增量扫描 ──

def get_recently_scanned_urls(days=7):
    """从batch_scans.json中获取最近N天内已扫描的工具URL集合"""
    if not os.path.exists(BATCH_DB):
        return set()

    try:
        with open(BATCH_DB, "r", encoding="utf-8") as f:
            db = json.load(f)
    except Exception:
        return set()

    cutoff = datetime.now(TZ) - timedelta(days=days)
    cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")
    recent_urls = set()

    for scan_batch in db.get("scans", []):
        scanned_at = scan_batch.get("scanned_at", "")
        if scanned_at >= cutoff_str:
            for r in scan_batch.get("results", []):
                url = r.get("source_url", "")
                if url:
                    recent_urls.add(url)

    return recent_urls


def filter_already_scanned(servers, days=7):
    """过滤掉最近N天内已扫描过的工具，返回(待扫描, 已跳过)"""
    recent_urls = get_recently_scanned_urls(days)
    to_scan = []
    skipped = []

    for s in servers:
        if s["url"] in recent_urls:
            skipped.append(s)
        else:
            to_scan.append(s)

    return to_scan, skipped


# ── 单工具扫描（供并发使用） ──

def _scan_single_tool(server, index, total, delay, progress_callback=None):
    """扫描单个工具（线程安全，含进度输出）"""
    url = server["url"]
    name = server["name"]
    source = server["source"]

    with _progress_lock:
        print(f"  [{index}/{total}] Scanning {name} ({source})...")

    try:
        result = scan(url, "mcp", name)
        result["source"] = source
        result["directory_description"] = server.get("description", "")
        if "stars" in server:
            result["stars"] = server["stars"]

        score = result["overall_score"]
        badge = result["badge_level"]
        findings = result["total_findings"]
        owasp = result["owasp_coverage"]["covered_count"]

        with _progress_lock:
            print(f"    -> Score:{score} Badge:{badge} Findings:{findings} OWASP:{owasp}/10")

        # 进度回调
        if progress_callback:
            try:
                progress_callback(index, total, server, {
                    "status": "success",
                    "score": score,
                    "badge": badge,
                })
            except Exception:
                pass

        return {"status": "success", "result": result}

    except Exception as e:
        with _progress_lock:
            print(f"    -> ERROR: {e}")

        if progress_callback:
            try:
                progress_callback(index, total, server, {
                    "status": "error",
                    "error": str(e),
                })
            except Exception:
                pass

        return {"status": "error", "error_info": {"url": url, "name": name, "error": str(e)}}


# ── 批量扫描（并发版） ──

def batch_scan_servers(servers, delay=2, max_errors=10, max_workers=3, progress_callback=None):
    """批量扫描服务器列表（并发控制版）

    Args:
        servers: 待扫描的服务器列表
        delay: 扫描间隔（秒），用于限流
        max_errors: 最大连续错误数，超过则停止
        max_workers: 并发线程数（默认3，避免GitHub限流）
        progress_callback: 进度回调函数 callback(index, total, server, scan_result)
    """
    results = []
    errors = []
    error_count = 0
    stop_flag = threading.Event()

    total = len(servers)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交任务，每个任务带有延迟
        future_to_server = {}
        for i, server in enumerate(servers, 1):
            if stop_flag.is_set():
                break
            # 每个任务延迟 (i-1)*delay 秒后执行，避免同时发出请求
            futures = []
            def _delayed_scan(srv=server, idx=i):
                if idx > 1:
                    time.sleep(delay)
                return _scan_single_tool(srv, idx, total, delay, progress_callback)

            future = executor.submit(_delayed_scan)
            future_to_server[future] = server

        # 收集结果
        for future in as_completed(future_to_server):
            if stop_flag.is_set():
                break

            try:
                outcome = future.result()
            except Exception as e:
                server = future_to_server[future]
                errors.append({"url": server["url"], "name": server["name"], "error": str(e)})
                error_count += 1
                with _progress_lock:
                    print(f"    -> FATAL ERROR for {server.get('name', server['url'])}: {e}")
                if error_count >= max_errors:
                    print(f"  [STOP] {max_errors} consecutive errors, stopping.")
                    stop_flag.set()
                continue

            if outcome["status"] == "success":
                results.append(outcome["result"])
                error_count = 0  # 成功则重置连续错误计数
            else:
                errors.append(outcome["error_info"])
                error_count += 1
                if error_count >= max_errors:
                    print(f"  [STOP] {max_errors} consecutive errors, stopping.")
                    stop_flag.set()

    return results, errors


def save_results(results, errors, source="batch"):
    """保存批量扫描结果"""
    # 加载已有数据
    if os.path.exists(BATCH_DB):
        with open(BATCH_DB, "r", encoding="utf-8") as f:
            db = json.load(f)
    else:
        db = {"scans": [], "summary": {}}

    # 添加新结果
    batch_record = {
        "id": f"batch_{datetime.now(TZ).strftime('%Y%m%d_%H%M%S')}",
        "source": source,
        "scanner_version": SCANNER_VERSION,
        "scanned_at": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(results) + len(errors),
        "success": len(results),
        "errors": len(errors),
        "results": results,
        "error_details": errors,
    }
    db["scans"].append(batch_record)

    # 更新汇总（每个工具只保留最新扫描）
    tool_map = {}
    for scan_batch in db["scans"]:
        for r in scan_batch.get("results", []):
            key = r.get("source_url", "")
            tool_map[key] = r  # 后来的覆盖前面的

    db["tools"] = list(tool_map.values())
    db["summary"] = {
        "total_tools": len(db["tools"]),
        "last_scan": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "scanner_version": SCANNER_VERSION,
        "avg_score": sum(t.get("overall_score", 0) for t in db["tools"]) / max(len(db["tools"]), 1),
        "badge_distribution": {},
        "risk_distribution": {},
        "owasp_coverage_avg": 0,
    }

    # 统计
    for t in db["tools"]:
        badge = t.get("badge_level", "none")
        db["summary"]["badge_distribution"][badge] = db["summary"]["badge_distribution"].get(badge, 0) + 1
        risk = t.get("risk_level", "unknown")
        db["summary"]["risk_distribution"][risk] = db["summary"]["risk_distribution"].get(risk, 0) + 1

    owasp_totals = [t.get("owasp_coverage", {}).get("covered_count", 0) for t in db["tools"]]
    if owasp_totals:
        db["summary"]["owasp_coverage_avg"] = sum(owasp_totals) / len(owasp_totals)

    with open(BATCH_DB, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"\n[*] Saved {len(results)} results to {BATCH_DB}")
    print(f"    Total tools in DB: {db['summary']['total_tools']}")
    print(f"    Average score: {db['summary']['avg_score']:.1f}")
    print(f"    Scanner version: {SCANNER_VERSION}")

    return db["summary"]


def generate_report():
    """生成安全报告"""
    if not os.path.exists(BATCH_DB):
        print("No scan data found. Run a batch scan first.")
        return

    with open(BATCH_DB, "r", encoding="utf-8") as f:
        db = json.load(f)

    tools = db.get("tools", [])
    if not tools:
        print("No tools in database.")
        return

    # 按分数排序
    tools.sort(key=lambda t: t.get("overall_score", 0))

    lines = [
        f"# AIShield MCP安全扫描报告",
        f"",
        f"生成时间: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')}",
        f"扫描引擎版本: {SCANNER_VERSION}",
        f"扫描工具总数: {len(tools)}",
        f"平均安全评分: {sum(t.get('overall_score',0) for t in tools)/len(tools):.1f}/100",
        f"",
        f"## 评分分布",
        f"",
        f"| 等级 | 数量 |",
        f"|------|------|",
    ]

    badges = db.get("summary", {}).get("badge_distribution", {})
    for badge in ["gold", "silver", "bronze", "none"]:
        count = badges.get(badge, 0)
        if count > 0:
            lines.append(f"| {badge} | {count} |")

    lines.extend([
        f"",
        f"## OWASP MCP Top 10 覆盖率",
        f"",
    ])

    # OWASP覆盖统计
    owasp_hit = {f"MCP0{i}": 0 for i in range(1, 11)}
    for t in tools:
        for cat in t.get("owasp_coverage", {}).get("covered", []):
            if cat in owasp_hit:
                owasp_hit[cat] += 1

    for cat in sorted(owasp_hit.keys()):
        info_map = {
            "MCP01": "令牌管理不当", "MCP02": "权限范围蔓延", "MCP03": "工具投毒",
            "MCP04": "供应链攻击", "MCP05": "命令注入", "MCP06": "提示注入",
            "MCP07": "认证不足", "MCP08": "审计缺失", "MCP09": "影子服务器", "MCP10": "上下文共享",
        }
        pct = owasp_hit[cat] / len(tools) * 100 if tools else 0
        lines.append(f"- **{cat}** {info_map.get(cat, '')}: {owasp_hit[cat]}/{len(tools)} ({pct:.0f}%)")

    lines.extend([
        f"",
        f"## 高风险工具 (score < 60)",
        f"",
    ])

    dangerous = [t for t in tools if t.get("overall_score", 0) < 60]
    for t in dangerous[:20]:
        name = t.get("name", t.get("source_url", "unknown"))
        score = t.get("overall_score", 0)
        findings = t.get("total_findings", 0)
        lines.append(f"- **{name}** — {score}/100, {findings} issues")

    lines.extend([
        f"",
        f"## 最安全工具 (score >= 85)",
        f"",
    ])

    safe = [t for t in tools if t.get("overall_score", 0) >= 85]
    for t in safe[:20]:
        name = t.get("name", t.get("source_url", "unknown"))
        score = t.get("overall_score", 0)
        lines.append(f"- **{name}** — {score}/100")

    report_path = os.path.join(DATA_DIR, "security_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[*] Report saved to {report_path}")
    return report_path


def _default_progress_callback(index, total, server, scan_result):
    """默认进度回调 — 输出进度百分比"""
    pct = index / total * 100
    status = scan_result.get("status", "unknown")
    name = server.get("name", server.get("url", "unknown"))
    if status == "success":
        score = scan_result.get("score", "?")
        badge = scan_result.get("badge", "?")
        print(f"  [PROGRESS] {pct:.0f}% ({index}/{total}) {name} -> Score:{score} Badge:{badge}")
    else:
        print(f"  [PROGRESS] {pct:.0f}% ({index}/{total}) {name} -> ERROR")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AIShield Batch Scanner v4.1")
    parser.add_argument("--source", default="github",
                        choices=["smithery", "smithery-api", "glama", "pulsemcp", "github", "all"])
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--delay", type=int, default=3)
    parser.add_argument("--workers", type=int, default=3,
                        help="并发线程数（默认3，避免GitHub限流）")
    parser.add_argument("--incremental", action="store_true",
                        help="启用增量扫描，跳过最近7天内已扫描的工具")
    parser.add_argument("--skip-days", type=int, default=7,
                        help="增量扫描跳过天数（默认7天）")
    parser.add_argument("--report", action="store_true", help="Generate report from existing data")
    args = parser.parse_args()

    if args.report:
        generate_report()
    else:
        servers = []
        if args.source in ("smithery", "all"):
            servers.extend(fetch_smithery_servers(args.limit))
        if args.source in ("smithery-api", "all"):
            servers.extend(fetch_smithery_api_servers(args.limit))
        if args.source in ("glama", "all"):
            servers.extend(fetch_glama_servers(args.limit))
        if args.source in ("pulsemcp", "all"):
            servers.extend(fetch_pulsemcp_servers(args.limit))
        if args.source in ("github", "all"):
            servers.extend(fetch_github_mcp_servers(args.limit))

        # 去重
        seen = set()
        unique = []
        for s in servers:
            if s["url"] not in seen:
                seen.add(s["url"])
                unique.append(s)

        # 增量扫描过滤
        if args.incremental:
            to_scan, skipped = filter_already_scanned(unique, days=args.skip_days)
            print(f"\n[*] 增量扫描: {len(to_scan)} 待扫描, {len(skipped)} 已跳过（最近{args.skip_days}天内已扫描）")
            for s in skipped:
                print(f"    [SKIP] {s.get('name', s['url'])}")
            unique = to_scan

        print(f"\n[*] Total {len(unique)} unique servers to scan (workers={args.workers})")
        if len(unique) == 0:
            print("[*] 没有需要扫描的工具")
        else:
            results, errors = batch_scan_servers(
                unique,
                delay=args.delay,
                max_workers=args.workers,
                progress_callback=_default_progress_callback,
            )
            summary = save_results(results, errors, args.source)
            generate_report()