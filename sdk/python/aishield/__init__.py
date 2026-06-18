"""
AIShield SDK - Agent-native AI tool security scanner.

Scan MCP/Skill/GPT/Prompt for security risks with 4-dimensional scoring.

Usage:
    from aishield import AIShield
    
    shield = AIShield()  # or AIShield(api_key="...")
    result = shield.scan("https://github.com/user/repo", tool_type="mcp")
    print(result.overall_score)  # 85
    print(result.badge_level)    # "gold"
    
    # Quick safety check
    safe = shield.check_safety("https://github.com/user/repo")
    # Returns (is_safe: bool, score: int, risk: str)
"""

import json
import time
import urllib.request
import urllib.error
import urllib.parse

__version__ = "2.1.0"
__all__ = ["AIShield", "ScanResult", "AIShieldError"]

DEFAULT_API_URL = "https://aishield.ai"


class AIShieldError(Exception):
    """AIShield SDK error."""
    pass


class ScanResult:
    """Security scan result."""
    def __init__(self, data: dict):
        self._data = data
        self.audit_id = data.get("audit_id", "")
        self.status = data.get("status", "")
        report = data.get("report", data)
        self.name = report.get("name", "")
        self.tool_type = report.get("tool_type", "")
        self.overall_score = report.get("overall_score", 0)
        self.security_score = report.get("security_score", 0)
        self.privacy_score = report.get("privacy_score", 0)
        self.quality_score = report.get("quality_score", 0)
        self.performance_score = report.get("performance_score", 0)
        self.badge_level = report.get("badge_level", "none")
        self.risk_level = report.get("risk_level", "unknown")
        self.findings = report.get("findings", [])
        self.recommendations = report.get("recommendations", [])
        self.report_url = report.get("report_url", "")
    
    @property
    def is_safe(self) -> bool:
        return self.overall_score >= 60 and self.risk_level not in ("high", "critical")
    
    @property
    def badge_emoji(self) -> str:
        return {"gold": "🥇", "silver": "🥈", "bronze": "🥉", "none": "⚠️"}.get(self.badge_level, "⚠️")
    
    @property
    def badge_markdown(self) -> str:
        return f"![AIShield](https://aishield.ai/api/v1/badge-name/{urllib.parse.quote(self.name)})"
    
    def __repr__(self):
        return f"ScanResult(name='{self.name}', score={self.overall_score}, badge='{self.badge_level}', risk='{self.risk_level}')"
    
    def summary(self) -> str:
        lines = [
            f"{self.badge_emoji} {self.name}: {self.overall_score}/100 ({self.risk_level})",
            f"  Security: {self.security_score} | Privacy: {self.privacy_score} | Quality: {self.quality_score} | Performance: {self.performance_score}",
        ]
        critical = [f for f in self.findings if f.get("severity") in ("critical", "high")]
        if critical:
            lines.append(f"  🚨 {len(critical)} critical/high issues")
        return "\n".join(lines)


class AIShield:
    """AIShield security scanner client.
    
    Args:
        api_key: API key (optional, free tier: 5 scans/day without key)
        api_url: API URL (default: https://aishield.ai)
    """
    
    def __init__(self, api_key: str = "", api_url: str = DEFAULT_API_URL):
        self.api_key = api_key
        self.api_url = api_url.rstrip("/")
    
    def _request(self, method: str, path: str, body: dict = None) -> dict:
        url = self.api_url + path
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        if self.api_key:
            req.add_header("X-API-Key", self.api_key)
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            try:
                err = json.loads(body)
                raise AIShieldError(f"HTTP {e.code}: {err.get('error', err.get('message', body))}")
            except json.JSONDecodeError:
                raise AIShieldError(f"HTTP {e.code}: {body[:200]}")
        except Exception as e:
            raise AIShieldError(f"Request failed: {e}")
    
    def scan(self, source_url: str, tool_type: str = "mcp", name: str = "") -> ScanResult:
        """Scan an AI tool for security risks.
        
        Args:
            source_url: Tool source URL (GitHub repo, GPT Store link, etc.)
            tool_type: "mcp", "skill", "gpt", or "prompt"
            name: Tool name (optional)
            
        Returns:
            ScanResult with scores, findings, and recommendations
        """
        submit = self._request("POST", "/api/v1/audit", {
            "tool_type": tool_type,
            "source_url": source_url,
            "name": name
        })
        audit_id = submit.get("audit_id")
        if not audit_id:
            raise AIShieldError(f"Submit failed: {submit}")
        
        for _ in range(60):
            time.sleep(3)
            result = self._request("GET", f"/api/v1/audit/{audit_id}")
            if result.get("status") == "completed":
                return ScanResult(result)
            if result.get("status") == "failed":
                raise AIShieldError(f"Scan failed: {result.get('error', 'unknown')}")
        
        raise AIShieldError("Scan timeout (180s)")
    
    def check_safety(self, source_url: str, name: str = "") -> tuple:
        """Quick safety check for an MCP tool.
        
        Args:
            source_url: GitHub repo URL
            name: Tool name (optional)
            
        Returns:
            (is_safe: bool, score: int, risk_level: str)
        """
        result = self.scan(source_url, tool_type="mcp", name=name)
        return (result.is_safe, result.overall_score, result.risk_level)
    
    def get_badge(self, name: str = "", source_url: str = "") -> dict:
        """Get security badge info for a previously scanned tool."""
        params = []
        if source_url:
            params.append(f"url={urllib.parse.quote(source_url)}")
        if name:
            params.append(f"name={urllib.parse.quote(name)}")
        query = "&".join(params)
        return self._request("GET", f"/api/v1/badge-info?{query}")
    
    def batch_scan(self, tools: list) -> list:
        """Batch scan multiple tools (max 10)."""
        if len(tools) > 10:
            raise AIShieldError("Max 10 tools per batch")
        results = []
        for t in tools:
            try:
                r = self.scan(t["source_url"], t.get("tool_type", "mcp"), t.get("name", ""))
                results.append(r)
            except AIShieldError as e:
                results.append({"error": str(e), "source_url": t.get("source_url", "")})
        return results
