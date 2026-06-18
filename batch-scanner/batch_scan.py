#!/usr/bin/env python3
"""
AIShield Batch Scanner
扫描Smithery/MCP Registry上的热门MCP工具，建立安全数据库。

用法:
  python3 batch_scan.py --source smithery --limit 100
  python3 batch_scan.py --source registry --limit 50
  python3 batch_scan.py --source custom --file urls.txt
  python3 batch_scan.py --source smithery --limit 100 --api-key YOUR_KEY
"""

import json
import time
import sys
import os
import argparse
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime

# Add parent to path for local scan
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scanner.scan_cli import scan as local_scan

API_URL = os.environ.get("AISHIELD_API_URL", "https://aishield.ai")
API_KEY = os.environ.get("AISHIELD_API_KEY", "")
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def urlopen(url, headers=None, timeout=15):
    """Safe urlopen."""
    try:
        req = urllib.request.Request(url, headers=headers or {"User-Agent": "AIShield-BatchScanner/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception:
        return None


def fetch_smithery_tools(limit=100):
    """Fetch popular MCP tools from Smithery."""
    print(f"📡 Fetching top {limit} tools from Smithery...")
    tools = []
    
    # Smithery has an API or we scrape the registry page
    # Try their API first
    for page in range(1, (limit // 20) + 2):
        url = f"https://smithery.ai/api/servers?page={page}&pageSize=20&sort=stars"
        data = urlopen(url, timeout=10)
        if not data:
            # Fallback: try the registry page
            url2 = f"https://smithery.ai/registry?page={page}"
            data = urlopen(url2, timeout=10)
            if not data:
                break
        
        try:
            j = json.loads(data)
            servers = j.get("servers", j.get("data", []))
            for s in servers:
                github = s.get("githubUrl") or s.get("sourceUrl") or s.get("repository", {}).get("url", "")
                name = s.get("qualifiedName") or s.get("name", "")
                if github and "github.com" in github:
                    tools.append({"name": name, "source_url": github, "tool_type": "mcp"})
                    if len(tools) >= limit:
                        return tools
        except Exception as e:
            print(f"  ⚠️ Parse error page {page}: {e}")
            break
        
        time.sleep(1)
    
    return tools[:limit]


def fetch_registry_tools(limit=50):
    """Fetch tools from official MCP Registry."""
    print(f"📡 Fetching {limit} tools from MCP Registry...")
    tools = []
    
    url = "https://registry.modelcontextprotocol.io/v0/servers"
    data = urlopen(url, timeout=15)
    if not data:
        print("  ❌ Failed to fetch from MCP Registry")
        return tools
    
    try:
        j = json.loads(data)
        servers = j.get("servers", [])
        for s in servers[:limit]:
            repo = s.get("repository", {})
            github = repo.get("url", "") if isinstance(repo, dict) else str(repo)
            name = s.get("name", "")
            if github and "github.com" in github:
                tools.append({"name": name, "source_url": github, "tool_type": "mcp"})
    except Exception as e:
        print(f"  ❌ Parse error: {e}")
    
    return tools


def fetch_github_popular_mcp(limit=100):
    """Fetch popular MCP servers from GitHub search."""
    print(f"📡 Searching GitHub for top MCP servers...")
    tools = []
    
    queries = [
        "mcp-server model context protocol",
        "modelcontextprotocol stars:>100",
        "mcp server claude",
    ]
    
    for q in queries:
        url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(q)}&sort=stars&order=desc&per_page=30"
        data = urlopen(url, {"User-Agent": "AIShield", "Accept": "application/vnd.github.v3+json"}, timeout=10)
        if not data:
            continue
        try:
            j = json.loads(data)
            for r in j.get("items", []):
                html_url = r.get("html_url", "")
                name = r.get("name", "")
                stars = r.get("stargazers_count", 0)
                if html_url and stars >= 10:
                    tools.append({
                        "name": name,
                        "source_url": html_url,
                        "tool_type": "mcp",
                        "stars": stars,
                    })
                    if len(tools) >= limit:
                        return tools
        except:
            pass
        time.sleep(3)  # Avoid GitHub API rate limit
    
    return tools[:limit]


def scan_via_api(tool, api_key=""):
    """Scan tool via AIShield SaaS API."""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
    
    # Submit
    body = json.dumps({
        "tool_type": tool.get("tool_type", "mcp"),
        "source_url": tool["source_url"],
        "name": tool.get("name", ""),
    }).encode()
    
    req = urllib.request.Request(f"{API_URL}/api/v1/audit", data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            submit = json.loads(resp.read())
    except Exception as e:
        return {"error": str(e), "source_url": tool["source_url"]}
    
    audit_id = submit.get("audit_id")
    if not audit_id:
        return {"error": "no audit_id", "submit_response": submit}
    
    # Poll
    for _ in range(60):
        time.sleep(3)
        try:
            req2 = urllib.request.Request(f"{API_URL}/api/v1/audit/{audit_id}", headers=headers)
            with urllib.request.urlopen(req2, timeout=10) as resp:
                result = json.loads(resp.read())
            if result.get("status") == "completed":
                report = result.get("report", {})
                return {
                    "audit_id": audit_id,
                    "name": tool.get("name", ""),
                    "source_url": tool["source_url"],
                    "overall_score": report.get("overall_score", 0),
                    "security_score": report.get("security_score", 0),
                    "privacy_score": report.get("privacy_score", 0),
                    "quality_score": report.get("quality_score", 0),
                    "risk_level": report.get("risk_level", "unknown"),
                    "badge_level": report.get("badge_level", "none"),
                    "findings_count": len(report.get("findings", [])),
                }
            if result.get("status") == "failed":
                return {"error": "scan failed", "audit_id": audit_id}
        except:
            pass
    
    return {"error": "timeout", "audit_id": audit_id}


def scan_local(tool):
    """Scan tool locally (no API)."""
    try:
        result = scan(
            tool_type=tool.get("tool_type", "mcp"),
            source_url=tool["source_url"],
            name=tool.get("name", ""),
        )
        return {
            "name": tool.get("name", ""),
            "source_url": tool["source_url"],
            "overall_score": result.get("scores", {}).get("overall", 0),
            "security_score": result.get("scores", {}).get("security", 0),
            "privacy_score": result.get("scores", {}).get("privacy", 0),
            "quality_score": result.get("scores", {}).get("quality", 0),
            "risk_level": result.get("risk_level", "unknown"),
            "badge_level": result.get("badge_level", "none"),
            "findings_count": len(result.get("findings", [])),
        }
    except Exception as e:
        return {"error": str(e), "source_url": tool["source_url"]}


def save_results(results, source):
    """Save scan results to data directory."""
    os.makedirs(DATA_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(DATA_DIR, f"batch_scan_{source}_{date_str}.json")
    
    with open(filename, "w") as f:
        json.dump({
            "scan_date": date_str,
            "source": source,
            "total": len(results),
            "results": results,
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {filename}")
    
    # Also update the master tools database
    master_file = os.path.join(DATA_DIR, "tools_database.json")
    master = []
    if os.path.exists(master_file):
        try:
            with open(master_file) as f:
                master = json.load(f)
        except:
            master = []
    
    # Merge by source_url
    existing_urls = {t.get("source_url") for t in master}
    for r in results:
        if "error" not in r and r.get("source_url") not in existing_urls:
            master.append(r)
            existing_urls.add(r["source_url"])
    
    with open(master_file, "w") as f:
        json.dump(master, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Master database: {len(master)} tools total")


def print_summary(results):
    """Print scan summary."""
    total = len(results)
    success = [r for r in results if "error" not in r]
    errors = [r for r in results if "error" in r]
    
    if not success:
        print("\n❌ All scans failed!")
        return
    
    scores = [r["overall_score"] for r in success]
    avg_score = sum(scores) / len(scores)
    
    badges = {}
    for r in success:
        b = r.get("badge_level", "none")
        badges[b] = badges.get(b, 0) + 1
    
    risks = {}
    for r in success:
        rk = r.get("risk_level", "unknown")
        risks[rk] = risks.get(rk, 0) + 1
    
    print(f"\n{'='*50}")
    print(f"  📊 Batch Scan Summary")
    print(f"{'='*50}")
    print(f"  Total: {total} | Success: {len(success)} | Failed: {len(errors)}")
    print(f"  Average Score: {avg_score:.1f}/100")
    print(f"\n  Badges:")
    for b in ["gold", "silver", "bronze", "none"]:
        if b in badges:
            icon = {"gold": "🥇", "silver": "🥈", "bronze": "🥉", "none": "⚠️"}[b]
            print(f"    {icon} {b}: {badges[b]}")
    print(f"\n  Risk Levels:")
    for rk in ["safe", "medium", "high", "critical"]:
        if rk in risks:
            icon = {"safe": "✅", "medium": "🟡", "high": "🟠", "critical": "🔴"}[rk]
            print(f"    {icon} {rk}: {risks[rk]}")
    
    # Top 5 safest and riskiest
    sorted_results = sorted(success, key=lambda x: x.get("overall_score", 0), reverse=True)
    print(f"\n  🏆 Top 5 Safest:")
    for r in sorted_results[:5]:
        print(f"    {r['overall_score']:>3}/100 | {r.get('name', r.get('source_url','').split('/')[-1])}")
    
    print(f"\n  ⚠️ Top 5 Riskiest:")
    for r in sorted_results[-5:]:
        print(f"    {r['overall_score']:>3}/100 | {r.get('name', r.get('source_url','').split('/')[-1])}")
    print(f"{'='*50}")


def main():
    parser = argparse.ArgumentParser(description="AIShield Batch Scanner")
    parser.add_argument("--source", choices=["smithery", "registry", "github", "custom"], default="github",
                        help="Source to fetch tools from")
    parser.add_argument("--limit", type=int, default=50, help="Max tools to scan")
    parser.add_argument("--file", help="Custom URL list file (one URL per line)")
    parser.add_argument("--api-key", default="", help="AIShield API key")
    parser.add_argument("--local", action="store_true", help="Scan locally (no API)")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between scans (seconds)")
    args = parser.parse_args()
    
    api_key = args.api_key or API_KEY
    
    # Fetch tools
    if args.source == "smithery":
        tools = fetch_smithery_tools(args.limit)
    elif args.source == "registry":
        tools = fetch_registry_tools(args.limit)
    elif args.source == "github":
        tools = fetch_github_popular_mcp(args.limit)
    elif args.source == "custom":
        if not args.file:
            print("❌ --file required for custom source")
            sys.exit(1)
        with open(args.file) as f:
            urls = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        tools = [{"source_url": u, "tool_type": "mcp", "name": u.split("/")[-1]} for u in urls]
    else:
        tools = []
    
    if not tools:
        print("❌ No tools found to scan")
        sys.exit(1)
    
    print(f"📋 Found {len(tools)} tools to scan")
    
    # Scan
    results = []
    for i, tool in enumerate(tools, 1):
        name = tool.get("name", tool["source_url"].split("/")[-1])
        print(f"\n[{i}/{len(tools)}] Scanning {name}...")
        print(f"  URL: {tool['source_url']}")
        
        if args.local:
            result = scan_local(tool)
        else:
            result = scan_via_api(tool, api_key)
        
        if "error" in result:
            print(f"  ❌ Error: {result['error']}")
        else:
            print(f"  ✅ Score: {result.get('overall_score', 0)}/100 | Risk: {result.get('risk_level', '?')} | Badge: {result.get('badge_level', '?')}")
        
        results.append(result)
        time.sleep(args.delay)
    
    # Summary
    print_summary(results)
    save_results(results, args.source)


if __name__ == "__main__":
    main()
