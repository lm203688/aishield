"""
eco/badge.py — 安全徽章 + 认证API

功能:
  - BadgeService:
      generate_badge_svg(tool_name, score, badge_level): 生成SVG徽章
      generate_badge_markdown(tool_name, score, badge_level): 生成Markdown徽章
      支持Gold/Silver/Bronze/None四级
  - CertificationService:
      certify_tool(source_url, scan_report): 认证工具
      生成认证ID: cert-aishield-xxxxx
      持久化到 data/certifications.json
      持续认证机制: 有效期管理、过期检查、续期、即将过期提醒

API路由:
  GET  /api/v1/badge/{tool_name}?score=X&level=gold  — 返回SVG
  POST /api/v1/certify                                — 提交认证
  GET  /api/v1/certify/{cert_id}                      — 查询认证
  POST /api/v1/certify/renew      — 续期认证
  GET  /api/v1/certify/expiring?days=7 — 即将过期的认证
  POST /api/v1/certify/check-expiry — 检查并更新过期状态
"""

import json
import os
import uuid
import threading
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse, parse_qs

# ── 路径配置 ──
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_BASE_DIR, "api", "data")
CERTIFICATIONS_FILE = os.path.join(_DATA_DIR, "certifications.json")

TZ = timezone(timedelta(hours=8))
_lock = threading.Lock()


# ══════════════════════════════════════════════
#  工具函数
# ══════════════════════════════════════════════

def _load_json(path, default=None):
    """加载JSON文件"""
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
    """线程安全保存JSON文件"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def _now_iso():
    """返回当前时间ISO格式"""
    return datetime.now(TZ).isoformat()


def _parse_iso(iso_str):
    """解析ISO时间字符串为datetime对象，失败返回None"""
    if not iso_str:
        return None
    try:
        return datetime.fromisoformat(iso_str)
    except (ValueError, TypeError):
        return None


# ══════════════════════════════════════════════
#  徽章等级定义
# ══════════════════════════════════════════════

BADGE_LEVELS = {
    "gold": {
        "label": "Gold",
        "label_zh": "金牌",
        "color": "#F5A623",
        "bg_color": "#FFD700",
        "text_color": "#333333",
        "min_score": 90,
    },
    "silver": {
        "label": "Silver",
        "label_zh": "银牌",
        "color": "#A0A0A0",
        "bg_color": "#C0C0C0",
        "text_color": "#333333",
        "min_score": 70,
    },
    "bronze": {
        "label": "Bronze",
        "label_zh": "铜牌",
        "color": "#CD7F32",
        "bg_color": "#D2691E",
        "text_color": "#FFFFFF",
        "min_score": 50,
    },
    "none": {
        "label": "None",
        "label_zh": "未认证",
        "color": "#999999",
        "bg_color": "#E0E0E0",
        "text_color": "#666666",
        "min_score": 0,
    },
}


# ══════════════════════════════════════════════
#  徽章服务
# ══════════════════════════════════════════════

class BadgeService:
    """
    安全徽章生成服务
    支持SVG和Markdown格式
    """

    @staticmethod
    def _resolve_level(level, score):
        """
        解析徽章等级
        如果level已指定则使用，否则根据分数自动判定

        Args:
            level (str): 手动指定等级
            score (int):  安全分数

        Returns:
            str: 等级名称
        """
        if level and level.lower() in BADGE_LEVELS:
            return level.lower()
        # 根据分数自动判定
        if score >= 90:
            return "gold"
        elif score >= 70:
            return "silver"
        elif score >= 50:
            return "bronze"
        return "none"

    @classmethod
    def generate_badge_svg(cls, tool_name, score, badge_level=None):
        """
        生成SVG格式安全徽章

        Args:
            tool_name (str):    工具名称
            score (int):        安全分数 (0-100)
            badge_level (str):  手动指定等级 (gold/silver/bronze/none)

        Returns:
            str: SVG字符串
        """
        level = cls._resolve_level(badge_level, score)
        config = BADGE_LEVELS[level]

        # 计算尺寸（根据工具名称长度动态调整）
        name_width = max(60, len(tool_name) * 8 + 20)
        score_width = 50
        total_width = name_width + score_width
        height = 28

        # 构建SVG
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{height}" role="img" aria-label="AIShield Badge: {tool_name} - {config['label']}">
  <!-- AIShield安全徽章 -->
  <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{config['bg_color']}" stop-opacity="1"/>
    <stop offset="100%" stop-color="{config['color']}" stop-opacity="1"/>
  </linearGradient>
  <clipPath id="c">
    <rect width="{total_width}" height="{height}" rx="4" ry="4"/>
  </clipPath>
  <g clip-path="url(#c)">
    <rect width="{name_width}" height="{height}" fill="{config['color']}"/>
    <rect x="{name_width}" width="{score_width}" height="{height}" fill="{config['bg_color']}"/>
    <rect width="{total_width}" height="{height}" fill="url(#g)" opacity="0.1"/>
  </g>
  <g font-family="DejaVu Sans,Verdana,sans-serif" font-size="11">
    <text x="{name_width // 2}" y="18" text-anchor="middle" fill="{config['text_color']}" font-weight="bold">{tool_name}</text>
    <text x="{name_width + score_width // 2}" y="18" text-anchor="middle" fill="{config['text_color']}" font-weight="bold">{score}</text>
  </g>
  <!-- AIShield安全认证 {config['label_zh']} 徽章 -->
</svg>'''
        return svg

    @classmethod
    def generate_badge_markdown(cls, tool_name, score, badge_level=None):
        """
        生成Markdown格式安全徽章

        Args:
            tool_name (str):    工具名称
            score (int):        安全分数
            badge_level (str):  手动指定等级

        Returns:
            str: Markdown字符串
        """
        level = cls._resolve_level(badge_level, score)
        config = BADGE_LEVELS[level]

        # shields.io 格式
        left_color = config["color"].replace("#", "")
        right_color = config["bg_color"].replace("#", "")
        md = (
            f"![AIShield: {tool_name} - {config['label']}]"
            f"(https://img.shields.io/badge/{tool_name}-{config['label']}-"
            f"{left_color}?style=flat&logo=shield&logoColor=white&labelColor={right_color})"
        )
        return md


# ══════════════════════════════════════════════
#  认证服务
# ══════════════════════════════════════════════

class CertificationService:
    """
    工具认证服务
    对已扫描的工具进行安全认证
    支持持续认证机制: 有效期管理、过期检查、续期、即将过期提醒
    """

    def __init__(self):
        self._certs = {}

    def _load(self):
        """从磁盘加载认证数据"""
        data = _load_json(CERTIFICATIONS_FILE, {"certifications": {}})
        self._certs = data.get("certifications", {})

    def _save(self):
        """持久化到磁盘"""
        _save_json(CERTIFICATIONS_FILE, {"certifications": self._certs})

    def _generate_cert_id(self):
        """
        生成唯一认证ID
        格式: cert-aishield-xxxxx

        Returns:
            str: 认证ID
        """
        return f"cert-aishield-{uuid.uuid4().hex[:12]}"

    def certify_tool(self, source_url, scan_report=None):
        """
        认证工具

        Args:
            source_url (str):    工具源地址（GitHub等）
            scan_report (dict):   安全扫描报告（可选，如无则需已有报告）

        Returns:
            dict: 认证信息
        """
        self._load()

        cert_id = self._generate_cert_id()

        # 从扫描报告中提取关键指标
        score = 0
        badge_level = "none"
        risk_level = "unknown"

        if scan_report:
            score = scan_report.get("overall_score", 0)
            badge_level = scan_report.get("badge_level", "none")
            risk_level = scan_report.get("risk_level", "unknown")
            findings_count = scan_report.get("total_findings", 0)
        else:
            findings_count = 0

        # 认证状态: score >= 70 才能获得认证
        certified = score >= 70
        status = "certified" if certified else "rejected"

        # 认证有效期：Gold 90天，Silver 60天，Bronze 30天，其余30天
        _expiry_days_map = {"gold": 90, "silver": 60, "bronze": 30}
        expiry_days = _expiry_days_map.get(badge_level, 30)
        expires_at = ""
        if certified:
            expires_at = (datetime.now(TZ) + timedelta(days=expiry_days)).isoformat()

        cert_info = {
            "cert_id": cert_id,
            "source_url": source_url,
            "score": score,
            "badge_level": badge_level,
            "risk_level": risk_level,
            "findings_count": findings_count,
            "status": status,
            "certified_at": _now_iso(),
            "expires_at": expires_at,
        }

        self._certs[cert_id] = cert_info
        self._save()

        return cert_info

    def get_certification(self, cert_id):
        """
        查询认证信息

        Args:
            cert_id (str): 认证ID

        Returns:
            dict | None: 认证信息
        """
        self._load()
        return self._certs.get(cert_id)

    def list_certifications(self, status=None):
        """
        列出所有认证

        Args:
            status (str): 过滤状态 (certified/rejected/all)

        Returns:
            list: 认证信息列表
        """
        self._load()
        certs = list(self._certs.values())
        if status and status != "all":
            certs = [c for c in certs if c.get("status") == status]
        return certs

    def revoke_certification(self, cert_id, reason=""):
        """
        撤销认证

        Args:
            cert_id (str): 认证ID
            reason (str):  撤销原因

        Returns:
            bool: 是否成功。认证已过期时返回 False 并提示"认证已过期，无需撤销"。
        """
        self._load()
        if cert_id not in self._certs:
            return False

        # 如果认证已过期，无需撤销
        cert = self._certs[cert_id]
        if cert.get("status") == "expired":
            return False

        # 检查是否已自然过期但状态未更新
        expires_at_str = cert.get("expires_at", "")
        if expires_at_str:
            expires_at = _parse_iso(expires_at_str)
            if expires_at and datetime.now(TZ) > expires_at:
                # 自动更新状态为过期
                cert["status"] = "expired"
                self._save()
                return False

        self._certs[cert_id]["status"] = "revoked"
        self._certs[cert_id]["revoked_at"] = _now_iso()
        self._certs[cert_id]["revoke_reason"] = reason
        self._save()
        return True

    def check_certification_expiry(self):
        """
        检查所有认证是否过期，将过期的认证状态改为"expired"。

        Returns:
            dict: {"checked": int, "expired": int, "expired_ids": list}
        """
        self._load()
        now = datetime.now(TZ)
        checked = 0
        expired_count = 0
        expired_ids = []

        for cert_id, cert in self._certs.items():
            # 只检查有效认证（certified 状态且有 expires_at）
            if cert.get("status") != "certified":
                continue
            expires_at_str = cert.get("expires_at", "")
            if not expires_at_str:
                continue
            checked += 1
            expires_at = _parse_iso(expires_at_str)
            if expires_at and now > expires_at:
                cert["status"] = "expired"
                cert["expired_at"] = _now_iso()
                expired_count += 1
                expired_ids.append(cert_id)

        if expired_count > 0:
            self._save()

        return {
            "checked": checked,
            "expired": expired_count,
            "expired_ids": expired_ids,
        }

    def renew_certification(self, cert_id, new_scan_report):
        """
        续期认证，需要提供新的扫描报告。

        Args:
            cert_id (str):        认证ID
            new_scan_report (dict): 新的安全扫描报告

        Returns:
            dict | None: 更新后的认证信息，失败返回None
        """
        self._load()
        if cert_id not in self._certs:
            return None

        cert = self._certs[cert_id]

        # 已撤销的认证不允许续期
        if cert.get("status") == "revoked":
            return None

        # 从新扫描报告中提取关键指标
        score = new_scan_report.get("overall_score", 0)
        badge_level = new_scan_report.get("badge_level", "none")
        risk_level = new_scan_report.get("risk_level", "unknown")
        findings_count = new_scan_report.get("total_findings", 0)

        # 续期要求分数 >= 70
        if score < 70:
            return None

        # 计算新的有效期
        _expiry_days_map = {"gold": 90, "silver": 60, "bronze": 30}
        expiry_days = _expiry_days_map.get(badge_level, 30)
        expires_at = (datetime.now(TZ) + timedelta(days=expiry_days)).isoformat()

        # 更新认证信息
        cert["score"] = score
        cert["badge_level"] = badge_level
        cert["risk_level"] = risk_level
        cert["findings_count"] = findings_count
        cert["status"] = "certified"
        cert["renewed_at"] = _now_iso()
        cert["expires_at"] = expires_at

        self._save()
        return cert

    def get_expiring_certifications(self, days=7):
        """
        获取N天内即将过期的认证列表（用于提醒）。

        Args:
            days (int): 天数阈值，默认7天

        Returns:
            list: 即将过期的认证信息列表（含 remaining_days 字段）
        """
        self._load()
        now = datetime.now(TZ)
        deadline = now + timedelta(days=days)
        result = []

        for cert_id, cert in self._certs.items():
            # 只关注有效认证
            if cert.get("status") != "certified":
                continue
            expires_at_str = cert.get("expires_at", "")
            if not expires_at_str:
                continue
            expires_at = _parse_iso(expires_at_str)
            if expires_at and now <= expires_at <= deadline:
                remaining = (expires_at - now).days
                cert_copy = dict(cert)
                cert_copy["remaining_days"] = remaining
                result.append(cert_copy)

        # 按过期时间升序（最快过期的排前面）
        result.sort(key=lambda c: c.get("expires_at", ""))
        return result


# ══════════════════════════════════════════════
#  API路由处理函数
# ══════════════════════════════════════════════

def register_routes(handler):
    """
    将徽章和认证模块路由注册到HTTPServer的Handler上

    兼容 api/server.py 的 AIShieldHandler 模式。

    Args:
        handler: AIShieldHandler实例
    """
    original_do_get = handler.do_GET
    original_do_post = handler.do_POST

    def do_get_patched(self):
        """扩展GET路由"""
        if hasattr(self, "_parsed_path"):
            parsed = self._parsed_path
        else:
            from urllib.parse import urlparse
            parsed = urlparse(self.path)
        path = parsed.path

        # ── GET /api/v1/badge/{tool_name}?score=X&level=gold — 返回SVG ──
        if path.startswith("/api/v1/badge/"):
            tool_name = path[len("/api/v1/badge/"):]
            if not tool_name:
                self._send_json({"error": "tool_name is required"}, 400)
                return

            query = parse_qs(parsed.query)
            try:
                score = int(query.get("score", [0])[0])
            except (ValueError, IndexError):
                score = 0
            level = query.get("level", [None])[0]

            svg = BadgeService.generate_badge_svg(tool_name, score, level)
            body = svg.encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "public, max-age=3600")
            self.end_headers()
            self.wfile.write(body)
            return

        # ── GET /api/v1/certify/expiring?days=7 — 即将过期的认证 ──
        if path == "/api/v1/certify/expiring":
            query = parse_qs(parsed.query)
            try:
                days = int(query.get("days", ["7"])[0])
            except (ValueError, IndexError):
                days = 7
            try:
                cert_service = CertificationService()
                expiring = cert_service.get_expiring_certifications(days=days)
                self._send_json({
                    "success": True,
                    "total": len(expiring),
                    "days": days,
                    "certifications": expiring,
                })
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ── GET /api/v1/certify/{cert_id} — 查询认证 ──
        if path.startswith("/api/v1/certify/"):
            cert_id = path[len("/api/v1/certify/"):]
            cert_service = CertificationService()
            cert = cert_service.get_certification(cert_id)
            if cert:
                self._send_json({"success": True, "certification": cert})
            else:
                self._send_json({"error": "认证不存在", "cert_id": cert_id}, 404)
            return

        # 非本模块路由
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

        # ── POST /api/v1/certify — 提交认证 ──
        if path == "/api/v1/certify":
            source_url = data.get("source_url", "")
            if not source_url:
                self._send_json({"error": "source_url is required"}, 400)
                return

            scan_report = data.get("scan_report")
            try:
                cert_service = CertificationService()
                cert = cert_service.certify_tool(source_url, scan_report)
                self._send_json({"success": True, "certification": cert}, 201)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ── POST /api/v1/certify/renew — 续期认证 ──
        if path == "/api/v1/certify/renew":
            cert_id = data.get("cert_id", "")
            new_scan_report = data.get("new_scan_report")
            if not cert_id:
                self._send_json({"error": "cert_id is required"}, 400)
                return
            if not new_scan_report or not isinstance(new_scan_report, dict):
                self._send_json({"error": "new_scan_report is required"}, 400)
                return
            try:
                cert_service = CertificationService()
                result = cert_service.renew_certification(cert_id, new_scan_report)
                if result:
                    self._send_json({"success": True, "certification": result})
                else:
                    self._send_json({"error": "续期失败，认证不存在、已撤销或新扫描分数不足"}, 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ── POST /api/v1/certify/check-expiry — 检查并更新过期状态 ──
        if path == "/api/v1/certify/check-expiry":
            try:
                cert_service = CertificationService()
                result = cert_service.check_certification_expiry()
                self._send_json({"success": True, **result})
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
    print("=== SVG徽章生成测试 ===")
    for level, config in BADGE_LEVELS.items():
        svg = BadgeService.generate_badge_svg("MyTool", 85, level)
        print(f"  [{level}] 长度: {len(svg)}字符")
        # 显示前3行
        lines = svg.strip().split("\n")
        for line in lines[:3]:
            print(f"    {line}")
        print("    ...")

    print("\n=== Markdown徽章测试 ===")
    md = BadgeService.generate_badge_markdown("ExampleTool", 92)
    print(f"  {md}")

    print("\n=== 认证服务测试 ===")
    cert_service = CertificationService()

    # 认证一个工具
    cert = cert_service.certify_tool(
        "https://github.com/example/tool",
        scan_report={
            "overall_score": 85,
            "badge_level": "silver",
            "risk_level": "low",
            "total_findings": 3,
        },
    )
    print(f"  认证ID: {cert['cert_id']}")
    print(f"  状态: {cert['status']}")
    print(f"  分数: {cert['score']} ({cert['badge_level']})")
    print(f"  有效期至: {cert['expires_at']}")

    # 查询认证
    found = cert_service.get_certification(cert["cert_id"])
    print(f"  查询: {found['cert_id']} = {found['status']}")

    # 列出认证
    certs = cert_service.list_certifications()
    print(f"  总认证数: {len(certs)}")

    # 撤销认证
    cert_service.revoke_certification(cert["cert_id"], "安全漏洞修复")
    found = cert_service.get_certification(cert["cert_id"])
    print(f"  撤销后: {found['status']}")

    print("\n=== 持续认证机制测试 ===")

    # 认证一个Gold工具
    cert_gold = cert_service.certify_tool(
        "https://github.com/example/gold-tool",
        scan_report={
            "overall_score": 92,
            "badge_level": "gold",
            "risk_level": "safe",
            "total_findings": 0,
        },
    )
    print(f"  Gold认证有效期: {cert_gold['expires_at']}")

    # 认证一个Bronze工具
    cert_bronze = cert_service.certify_tool(
        "https://github.com/example/bronze-tool",
        scan_report={
            "overall_score": 55,
            "badge_level": "bronze",
            "risk_level": "medium",
            "total_findings": 5,
        },
    )
    print(f"  Bronze认证有效期: {cert_bronze['expires_at']}")

    # 获取即将过期的认证
    expiring = cert_service.get_expiring_certifications(days=90)
    print(f"  90天内即将过期: {len(expiring)}个")
    for c in expiring:
        print(f"    {c['cert_id']} ({c['badge_level']}) 剩余{c.get('remaining_days', '?')}天")

    # 续期认证
    renewed = cert_service.renew_certification(
        cert_gold["cert_id"],
        new_scan_report={
            "overall_score": 95,
            "badge_level": "gold",
            "risk_level": "safe",
            "total_findings": 0,
        },
    )
    if renewed:
        print(f"  续期成功: {renewed['cert_id']}, 新有效期: {renewed['expires_at']}")
    else:
        print("  续期失败")

    # 检查过期
    expiry_result = cert_service.check_certification_expiry()
    print(f"  过期检查: 检查{expiry_result['checked']}个, 过期{expiry_result['expired']}个")

    print("\n=== 全部测试通过 ===")
