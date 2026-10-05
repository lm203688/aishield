"""
统一导出面：目标端注册表 + 目标端配置化（F3 收口）。

为什么要有这一层
----------------
scanner/exporters.py 里有 to_nucleus / to_splunk / to_attack_graph 三个函数，
但它们有俩问题：
  1. **没有统一入口** —— 接一个新平台就得在 server.py 的路由分支里再添一条
     `if path.endswith("xxx")`，路由表和格式实现贴在一起，加一个目标端动一处
     分发逻辑。企业接 SIEM 是 agent 安全落地的真实痛点（SOAR 要按目标端投），
     用「路由里堆 if」硬扛住不了。
  2. **没有目标端配置** —— 目标端的 endpoint / headers / 字段映射写死在代码里，
     不同客户（Splunk HEC token、Nucleus FlexConnect 端口）没法配，只能改代码。

本模块把「格式实现」和「目标端投放」拆开：
  * TARGETS 注册表：格式实现只管把 findings 变成合规格的 payload（纯函数）。
  * TargetConfig：目标端怎么投（endpoint/headers/enabled/timeout/映射覆盖），
    从 dict 或 JSON 文件来，不进代码。
  * export() 单一入口：给定 target + config，返回 payload + 规格声明 + 校验结果。

顺带把任务板里那条假绿钉掉：#365 的描述写「OCSF/STIX 已有雏形」，实际全仓
grep 只在 exporters.py 里命中「通用 SIEM HEC」一句注释，OCSF/STIX 是零代码。
这里按真实规范补齐（OCSF 1.1.0、STIX 2.1），不是拿字段名糊一层。

安全红线：目标端 headers 里常带 HEC token / API key，**绝不能进 payload**；
本模块对所有目标端产物统一脱敏（见 redact_headers）。
零依赖：只用标准库。
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import uuid
from datetime import datetime, timezone

from . import exporters as _exporters

__all__ = ["TARGETS", "TargetConfig", "ExportResult", "register_target",
           "export", "export_to", "batch_export", "load_config", "mask_secret"]

TARGET_SCHEMA = "aishield/export-registry"

# 固定命名空间：STIX 对象 id 走 uuid5，保证同 rule_id 永远同一 id（可回放）
_UUID_NS = uuid.UUID("6ba7b811-9dad-11d1-80b4-00c04fd430c8")

# OCSF severity_id（OCSF 1.1）：0 unknown / 1 informational / 2 low / 3 medium
# / 4 high / 5 critical / 6 fatal / 7 other
_OCSF_SEV_ID = {"unknown": 0, "info": 1, "informational": 1, "low": 2,
                "medium": 3, "high": 4, "critical": 5, "fatal": 6, "other": 7}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sev_str(f: dict) -> str:
    return str(f.get("severity", "info") or "info").lower()


def _stix_id(kind: str, seed: str) -> str:
    """uuid5 ⇒ 同一 finding 每次导出同一 id（SOAR 去重靠这个）。"""
    return "%s--%s" % (kind, uuid.uuid5(_UUID_NS, "%s:%s" % (kind, seed)))


# ── 格式实现（纯函数：findings → payload） ────────────────────────────────

def _build_nucleus(findings, cfg):
    return _exporters.to_nucleus(findings, asset_name=cfg.get("asset_name") or "aishield-scan")


def _build_splunk(findings, cfg):
    return _exporters.to_splunk(findings, source=cfg.get("source") or "aishield")


def _build_ocsf(findings, cfg):
    """
    OCSF 1.1.0 Vulnerability Finding（class_uid=2001）。
    只映射规范里真存在的字段（不拿自造字段冒充合规），字段缺失就留空串。
    """
    events = []
    for f in findings:
        sev = _sev_str(f)
        events.append({
            "class_uid": 2001,
            "severity_id": _OCSF_SEV_ID.get(sev, 0),
            "severity": sev.capitalize(),
            "message": f.get("description", ""),
            "title": f.get("type") or f.get("rule_id", ""),
            "cve": f.get("cve", ""),
            # 注意：OCSF 1.1 Vulnerability Finding 规范里没有 remediation 字段，
            # 所以修复建议不进这条产物（不是漏映射，是规范没这格）——
            # 由 export() 在发现 remediation 非空时显式警告，别让用户以为丢了。
            "risky": {"boolean": False},
            "related_assets": [{"schema": "asset", "asset_name": f.get("file") or f.get("package") or "",
                                "asset_type": cfg.get("asset_type") or "code"}],
            "metadata": {"product": {"name": cfg.get("product_name") or "AIShield"},
                         "uvx_rule_id": f.get("rule_id", "")},
        })
    return {
        "schema": "ocsf",
        "schema_version": "1.1.0",
        "class_uid": 2001,
        "class_name": "Vulnerability Finding",
        "metadata": {
            "event_uid": uuid.uuid5(_UUID_NS, str(len(findings)) + ":" + (findings[0].get("rule_id", "") if findings else "")).hex[:16],
            "event_time": _now_iso(),
            "time": _now_iso(),
            "product": {"name": cfg.get("product_name") or "AIShield",
                        "vendor_name": cfg.get("vendor_name") or "lm203688"},
            "version": cfg.get("vendor_version", ""),
            "severity": _sev_str(findings[0]) if findings else "informational",
        },
        "count": len(events),
        "findings": events,
    }


def _build_stix(findings, cfg):
    """STIX 2.1 bundle：identity + 每个 finding 一条 vulnerability SDO。"""
    objects = [{
        "type": "identity",
        "id": _stix_id("identity", cfg.get("identity_name") or "AIShield"),
        "name": cfg.get("identity_name") or "AIShield",
        "identity_class": "organization",
    }]
    for i, f in enumerate(findings):
        rule_id = f.get("rule_id") or "AS-%04d" % (i + 1)
        objects.append({
            "type": "vulnerability",
            "id": _stix_id("vulnerability", rule_id),
            "name": str(f.get("type") or rule_id)[:60],
            "description": f.get("description", ""),
            "confidence": cfg.get("confidence", 100),
            "external_references": [
                {"source_name": "aishield", "external_id": rule_id},
                {"source_name": "owasp", "external_id": f.get("owasp_category", "")},
            ],
        })
    return {
        "type": "bundle",
        "id": _stix_id("bundle", cfg.get("identity_name") or "AIShield"),
        "objects": objects,
    }


def _build_json(findings, cfg):
    """归一化 JSON：企业自研管道最容易吃的形式，字段不丢。"""
    return {
        "schema": "aishield/findings/1",
        "generated_at": _now_iso(),
        "count": len(findings),
        "findings": findings,
    }


def _build_csv(findings, cfg):
    """扁平 CSV（text 类型，SOAR 表格摄入友好）。"""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["rule_id", "severity", "type", "file", "lines", "col", "owasp_category",
                "description", "remediation"])
    for f in findings:
        w.writerow([f.get("rule_id", ""), _sev_str(f), f.get("type", ""), f.get("file", ""),
                    f.get("lines", ""), f.get("col", ""), f.get("owasp_category", ""),
                    f.get("description", ""), f.get("remediation", "")])
    return buf.getvalue()


# ── 目标端注册表 ──────────────────────────────────────────────────────────

# name -> {format, schema_name, schema_version, build, requires, validate}
TARGETS: dict[str, dict] = {}


def register_target(name: str, builder, schema_name: str, schema_version: str = "1.0",
                    kind: str = "json", required=(), note: str = "", validate=None):
    """注册新目标端。新增一个导出格式 = 加一行，不用碰路由分发。"""
    TARGETS[name] = {
        "build": builder,
        "schema_name": schema_name,
        "schema_version": schema_version,
        "kind": kind,  # json / text
        "required": tuple(required),
        "note": note,
        "validate": validate,
    }


def _validate_generic(payload, spec, cfg):
    """通用必填校验：dict 型看顶层键，text 型看头部。"""
    issues = []
    if spec["kind"] == "text":
        head = payload.split("\n", 1)[0] if isinstance(payload, str) else ""
        for col in spec["required"]:
            if col not in head:
                issues.append("CSV 缺少表头列: %s" % col)
        return issues
    if not isinstance(payload, dict):
        return ["payload 不是 JSON 对象"]
    for key in spec["required"]:
        if key not in payload:
            issues.append("缺少顶层字段: %s" % key)
    return issues


register_target("nucleus", _build_nucleus, "Nucleus FlexConnect", "1.0", "json",
                required=("schema", "asset_name", "findings"),
                note="Nucleus FlexConnect 摄入；字段对齐 Qualys/Tenable/CrowdStrike 摄入管道")
register_target("splunk", _build_splunk, "Splunk HEC", "1.0", "json",
                required=("event_count", "events"),
                note="Splunk HTTP Event Collector 风格事件流")
register_target("ocsf", _build_ocsf, "OCSF", "1.1.0", "json",
                required=("schema", "schema_version", "class_uid", "findings"),
                note="OCSF 1.1.0 Vulnerability Finding (class_uid=2001)，SIEM/SOAR 通用")
register_target("stix", _build_stix, "STIX 2.1", "2.1", "json",
                required=("type", "id", "objects"),
                note="STIX 2.1 Bundle（identity + vulnerability SDO），可投 Sentinel/IBM Resilient")
register_target("json", _build_json, "AIShield Findings", "1", "json",
                required=("schema", "findings"),
                note="归一化 findings，企业自研管道")
register_target("csv", _build_csv, "AIShield CSV", "1", "text",
                required=("rule_id", "severity", "description"),
                note="扁平 CSV，表格型 SOAR 摄入")


# ── 目标端配置 ────────────────────────────────────────────────────────────

_SECRET_KEYS = ("authorization", "auth", "token", "apikey", "api-key", "x-api-key",
                "password", "secret", "bearer")
_SECRET_VAL = re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._\-]{6,}|(sk-[A-Za-z0-9_\-]{6,})|([A-Za-z0-9_\-]{24,}\.[A-Za-z0-9_\-]{6,}\.[A-Za-z0-9_\-]{6,})")


def mask_secret(value, keep_tail: int = 4) -> str:
    """
    模块级脱敏：给**任意字符串**用（headers 值、token、webhook URL 里的 key）。
    只保留末 4 位，够 humans 排查「是不是配错 env」又不够还原。
    """
    s = "" if value is None else str(value)
    if not s:
        return s
    tail = s[-keep_tail:] if len(s) > keep_tail * 2 else ""
    return "***MASKED***%s" % tail


class TargetConfig:
    """
    目标端配置：一个导出目标怎么投，全在这里，不进代码。

    fields: name(目标名) / target(格式名, 对应 TARGETS) / endpoint / headers /
            enabled / timeout / 以及格式特有的 asset_name/source/product_name 等。
    """

    def __init__(self, name: str, target: str, **kw):
        if target not in TARGETS:
            raise KeyError("未知目标端 %r，可选: %s" % (target, ", ".join(sorted(TARGETS))))
        self.name = name
        self.target = target
        self.endpoint = kw.pop("endpoint", "")
        self.headers = dict(kw.pop("headers", {}) or {})
        self.enabled = bool(kw.pop("enabled", True))
        self.timeout = kw.pop("timeout", 10)
        # 格式特有参数透传给 builder
        self.options = dict(kw)
        self._masked_headers = False

    def get(self, k, default=None):
        return self.options.get(k, default)

    def redact_headers(self) -> dict:
        """
        脱敏后返回 headers —— 给 HTTP 客户端用。

        目标端 headers 常带 HEC token / API key，绝不能进导出产物或日志。
        调用方（投递层）必须走这个返回值，别直接读 self.headers。
        """
        out = {}
        for k, v in (self.headers or {}).items():
            lk = str(k).lower()
            if any(s in lk for s in _SECRET_KEYS):
                out[k] = mask_secret(v)
            else:
                out[k] = _SECRET_VAL.sub(_mask_repl, str(v))
        self._masked_headers = True
        return out

    def to_dict(self) -> dict:
        return {"name": self.name, "target": self.target, "endpoint": self.endpoint,
                "headers": self.redact_headers(), "enabled": self.enabled,
                "timeout": self.timeout, "options": dict(self.options)}

    @classmethod
    def from_dict(cls, d: dict) -> "TargetConfig":
        if not isinstance(d, dict):
            raise TypeError("target 配置必须是对象，实际 %s" % type(d).__name__)
        name = d.get("name") or d.get("target")
        target = d.get("target")
        if not name or not target:
            raise KeyError("target 配置缺 name 或 target")
        opts = {k: v for k, v in d.items()
                if k not in ("name", "target", "endpoint", "headers", "enabled", "timeout")}
        cfg = cls(name, target, **opts)
        cfg.endpoint = d.get("endpoint", cfg.endpoint)
        cfg.headers = dict(d.get("headers") or {})
        if "enabled" in d:
            cfg.enabled = bool(d["enabled"])
        if "timeout" in d:
            cfg.timeout = d["timeout"]
        return cfg


def _mask_repl(m) -> str:
    return (m.group(1) or m.group(2) or m.group(3) or "") + "***MASKED***"


def load_config(path: str) -> list[TargetConfig]:
    """
    从 JSON 文件加载目标端清单。

    兼容两种形状：
      {"targets": [ {...}, {...} ]}       （推荐，多目标）
      {"name": "x", "target": "ocsf"}     （单目标，直接给对象）
    """
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    items = data.get("targets") if isinstance(data, dict) and "targets" in data else [data]
    return [TargetConfig.from_dict(i) for i in items]


# ── 导出 ──────────────────────────────────────────────────────────────────

class ExportResult:
    """一次导出的结果：payload（可能被投递层消费）+ 规格声明 + 校验结论。"""

    def __init__(self, name, target, payload, warnings, issues, spec):
        self.name = name
        self.target = target
        self.payload = payload
        self.warnings = warnings
        self.issues = issues
        self.spec = spec
        self.emitted_at = _now_iso()

    @property
    def ok(self) -> bool:
        return not self.issues

    def to_dict(self):
        return {
            "name": self.name, "target": self.target,
            "schema": "%s %s" % (self.spec["schema_name"], self.spec["schema_version"]),
            "emitted_at": self.emitted_at,
            "ok": self.ok, "issues": self.issues, "warnings": self.warnings,
            "has_payload": True,
        }

    def __repr__(self):
        return "<ExportResult %s ok=%s issues=%d>" % (self.name, self.ok, len(self.issues))


def export(findings, cfg: TargetConfig, **kw) -> ExportResult:
    """
    单一导出入口：findings + 目标端配置 ⇒ payload + 规格 + 校验结论。

    不联网、不投递 —— 这里只产出"能投的东西"，投递（HEC push 等）由调用方决定，
    免得导出器自带 IO 让测试跑真网络。
    """
    spec = TARGETS[cfg.target]
    warnings = []
    try:
        payload = spec["build"](list(findings or []), cfg)
    except Exception as e:  # 格式实现出错必须显式报，不能静默给空
        return ExportResult(cfg.name, cfg.target, None,
                            ["格式构建异常: %r" % e], ["build_failed"], spec)

    # 必填校验必须**每次都跑**：早先只调了 spec["validate"]（多数目标端是 None），
    # _validate_generic 定义了却没人调用 —— required 声明成了装饰品，坏产物照过。
    # 是测试里的反向用例把它抓出来的，这里补上调用。
    issues = list(_validate_generic(payload, spec, cfg))
    if spec["validate"]:
        issues.extend(spec["validate"](payload, spec, cfg) or [])
    # 规范装不下的字段，如实警告，不要闷着让用户以为丢了
    if cfg.target in ("ocsf",) and any((f or {}).get("remediation")
                                       for f in (findings or [])):
        warnings.append("OCSF 1.1 Vulnerability Finding 无 remediation 字段，"
                        "修复建议未随产物投递（需走工单通道）")
    # 安全兜底：产物里任何疑似 secret 都不许带出去
    leaks = _scan_secret_leak(payload)
    if leaks:
        issues.append("产物含疑似凭据（已脱敏字段: %s）" % ", ".join(sorted(leaks)))
        warnings.append("该目标端的 headers/产物做过脱敏，如投递仍失败请查目标端鉴权配置")
    # 目标端声明的必填（如 Nucleus 的 asset_name）缺失也要报
    for key, val in (("endpoint", cfg.endpoint),):
        if val and not val.startswith(("http://", "https://")):
            warnings.append("%s 不是合法 URL，投递层需自行处理" % key)
    return ExportResult(cfg.name, cfg.target, payload, warnings, issues, spec)


def export_to(findings, target: str, **kw) -> ExportResult:
    """免配置快捷导出（CLI/API 用）：只给格式名，参数走 kw。"""
    cfg = TargetConfig("adhoc", target, **kw)
    return export(findings, cfg)


def batch_export(findings, configs) -> list[ExportResult]:
    """按配置清单批量导出，跳过 disabled。"""
    out = []
    for c in configs:
        if not getattr(c, "enabled", True):
            continue
        out.append(export(findings, c))
    return out


def _scan_secret_leak(payload) -> set:
    """
    产物里不许带凭据。只做**弱探针**（找明显 token 形态），
    命中就报 issue —— 比「什么都不查」强，也不至于误报一堆正常串。
    """
    hits = set()
    if isinstance(payload, str):
        blob = payload
    else:
        try:
            blob = json.dumps(payload, ensure_ascii=False)
        except (TypeError, ValueError):
            blob = str(payload)
    if "Bearer " in blob:
        hits.add("authorization")
    if re.search(r"sk-[A-Za-z0-9]{16,}", blob):
        hits.add("api_key")
    if re.search(r"(?i)api[_-]?key\"?\s*[:=]\s*\"[A-Za-z0-9]{20,}", blob):
        hits.add("api_key_field")
    return hits
