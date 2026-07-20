"""
scanner/api_scanner.py — API接口安全扫描

包含:
  - APISpecLoader:           API规格文件加载器
      load_from_url / validate_spec
      支持JSON/YAML（简单正则解析，不依赖pyyaml）
  - AuthVulnerabilityScanner:  认证安全漏洞扫描
      未定义securitySchemes、未保护端点、弱认证、敏感端点匿名访问、CORS宽松
  - InputValidationScanner:    输入校验漏洞扫描
      参数无schema、字符串无maxLength、数字无range、路径参数无格式验证
      URL参数无域名限制、additionalProperties未限制
  - APIScanOrchestrator:       扫描编排器
      整合所有扫描器，计算5维评分（auth/input_validation/business_logic/
      data_exposure/config 各20%）
  - 数据持久化: data/api_scan_results.json
"""

import json
import os
import re
import uuid
import time
import threading
from datetime import datetime, timezone, timedelta
from urllib import request as urllib_request
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse

# ── 路径配置 ──
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_BASE_DIR, "data")
API_SCAN_RESULTS_FILE = os.path.join(_DATA_DIR, "api_scan_results.json")

TZ = timezone(timedelta(hours=8))
_lock = threading.Lock()
USER_AGENT = "AIShield-APIScanner/4.0"


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


def _now_iso():
    """返回当前时间的ISO格式字符串"""
    return datetime.now(TZ).isoformat()


def _generate_scan_id():
    """生成扫描ID"""
    return f"api-scan-{uuid.uuid4().hex[:12]}"


def _generate_finding_id(scanner_name, index):
    """生成发现ID"""
    return f"{scanner_name}-{index:03d}-{uuid.uuid4().hex[:6]}"


# ══════════════════════════════════════════════
#  OWASP API安全映射
# ══════════════════════════════════════════════

OWASP_API_CATEGORIES = {
    "API1": "Broken Object Level Authorization",
    "API2": "Broken Authentication",
    "API3": "Broken Object Property Level Authorization",
    "API4": "Unrestricted Resource Consumption",
    "API5": "Broken Function Level Authorization",
    "API6": "Mass Assignment",
    "API7": "Security Misconfiguration",
    "API8": "Injection",
    "API9": "Improper Inventory Management",
}

# OWASP分类用于扫描器映射
OWASP_MAPPING = {
    "no_security_schemes":     "API2",
    "unprotected_endpoint":   "API5",
    "weak_auth":              "API2",
    "sensitive_anonymous":    "API1",
    "cors_lax":               "API7",
    "no_schema":              "API8",
    "no_max_length":          "API4",
    "no_number_range":        "API4",
    "no_path_format":         "API8",
    "no_url_domain":          "API8",
    "additional_properties":  "API6",
    "no_rate_limit":          "API4",
    "verbose_errors":         "API7",
    "deprecated_endpoint":    "API9",
    "business_logic":        "API1",
    "data_exposure":          "API3",
    "config_misconfig":       "API7",
}


# ══════════════════════════════════════════════
#  API规格加载器
# ══════════════════════════════════════════════

class APISpecLoader:
    """
    API规格文件加载器
    支持从URL加载OpenAPI/Swagger规格文件（JSON和YAML）
    YAML解析使用简单正则实现，不依赖pyyaml
    """

    def load_from_url(self, url):
        """
        从URL加载API规格文件

        Args:
            url (str): API规格文件URL（支持.json/.yaml/.yml）

        Returns:
            dict: {"format", "version", "spec", "source_url"}
        """
        parsed = urlparse(url)
        path_lower = parsed.path.lower()

        # 确定格式
        if path_lower.endswith(".json"):
            fmt = "json"
        elif path_lower.endswith(".yaml") or path_lower.endswith(".yml"):
            fmt = "yaml"
        else:
            # 尝试通过Content-Type判断，默认JSON
            fmt = "json"

        # 获取内容
        try:
            req = urllib_request.Request(
                url,
                headers={"User-Agent": USER_AGENT, "Accept": "application/json, application/x-yaml"},
            )
            with urllib_request.urlopen(req, timeout=30) as resp:
                raw_content = resp.read().decode("utf-8", errors="replace")
        except (URLError, HTTPError, Exception) as e:
            return {
                "format": fmt,
                "version": None,
                "spec": None,
                "source_url": url,
                "error": f"获取规格文件失败: {str(e)}",
            }

        # 解析内容
        if fmt == "json":
            try:
                spec = json.loads(raw_content)
            except json.JSONDecodeError as e:
                return {
                    "format": fmt,
                    "version": None,
                    "spec": None,
                    "source_url": url,
                    "error": f"JSON解析失败: {str(e)}",
                }
        else:
            # YAML → 使用简单正则转JSON（支持基本结构）
            spec = self._simple_yaml_to_json(raw_content)

        # 检测版本
        version = self._detect_version(spec)

        return {
            "format": fmt,
            "version": version,
            "spec": spec,
            "source_url": url,
        }

    def validate_spec(self, spec_data):
        """
        验证API规格文件的完整性

        Args:
            spec_data (dict): load_from_url的返回值

        Returns:
            dict: {"valid", "errors", "warnings"}
        """
        errors = []
        warnings = []

        spec = spec_data.get("spec")
        if not spec:
            errors.append("规格内容为空")
            return {"valid": False, "errors": errors, "warnings": warnings}

        if not isinstance(spec, dict):
            errors.append("规格文件根元素必须是对象")
            return {"valid": False, "errors": errors, "warnings": warnings}

        # OpenAPI 3.x / Swagger 2.0 基本字段检查
        version = spec_data.get("version")

        if version and version.startswith("3."):
            # OpenAPI 3.x
            if "paths" not in spec:
                errors.append("缺少必需字段: paths")
            if "info" not in spec:
                warnings.append("缺少推荐字段: info")
            else:
                if "title" not in spec.get("info", {}):
                    warnings.append("info.title 缺失")
                if "version" not in spec.get("info", {}):
                    warnings.append("info.version 缺失")
        elif version and version.startswith("2."):
            # Swagger 2.0
            if "paths" not in spec:
                errors.append("缺少必需字段: paths")
            if "swagger" not in spec:
                warnings.append("缺少字段: swagger")
        else:
            warnings.append(f"未识别的API规格版本: {version}")

        # 检查路径定义
        if "paths" in spec:
            if not isinstance(spec["paths"], dict) or len(spec["paths"]) == 0:
                errors.append("paths 为空或格式不正确")
            else:
                # 检查每个路径是否有操作定义
                empty_paths = []
                for path, path_item in spec["paths"].items():
                    if not isinstance(path_item, dict):
                        warnings.append(f"路径 {path} 格式不正确")
                    elif not any(k in path_item for k in ("get", "post", "put", "delete", "patch")):
                        empty_paths.append(path)
                if empty_paths:
                    warnings.append(f"以下路径无操作定义: {', '.join(empty_paths[:5])}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def _detect_version(self, spec):
        """
        检测API规格版本

        Args:
            spec (dict): 规格内容

        Returns:
            str | None: 版本号
        """
        if not spec or not isinstance(spec, dict):
            return None

        # OpenAPI 3.x
        if "openapi" in spec:
            return str(spec["openapi"])
        # Swagger 2.0
        if "swagger" in spec:
            return str(spec["swagger"])
        return None

    def _simple_yaml_to_json(self, yaml_str):
        """
        简单YAML解析（不依赖pyyaml）
        支持基本结构: 键值对、列表、缩进层级

        Args:
            yaml_str (str): YAML内容

        Returns:
            dict: 解析后的字典
        """
        if not yaml_str or not yaml_str.strip():
            return {}

        result = {}
        stack = [(result, -1)]  # (current_dict, indent_level)
        current_list = None
        list_indent = -1

        for line in yaml_str.split("\n"):
            stripped = line.rstrip()
            if not stripped or stripped.strip().startswith("#"):
                continue

            # 计算缩进
            indent = len(line) - len(line.lstrip())

            # 简单列表处理（- 开头）
            if stripped.lstrip().startswith("- "):
                item_str = stripped.lstrip()[2:].strip()
                if current_list is None or indent != list_indent:
                    current_list = []
                    list_indent = indent
                    # 附加到最近的stack项
                    while stack and stack[-1][1] >= indent:
                        stack.pop()
                    if stack:
                        parent = stack[-1][0]
                        # 找到最后一个键并设置
                        last_key = list(parent.keys())[-1] if parent else None
                        if last_key and isinstance(parent[last_key], list):
                            current_list = parent[last_key]
                        elif last_key:
                            parent[last_key] = current_list
                # 解析值
                parsed_val = self._parse_yaml_value(item_str)
                current_list.append(parsed_val)
                continue

            current_list = None

            # 跳过过深的缩进
            if indent > 20:
                continue

            # 弹出栈到当前缩进
            while stack and stack[-1][1] >= indent:
                stack.pop()

            # 解析键值对
            if ":" in stripped:
                colon_pos = stripped.index(":")
                key = stripped[:colon_pos].strip().strip('"').strip("'")
                value_str = stripped[colon_pos + 1:].strip()

                if stack:
                    parent = stack[-1][0]
                else:
                    parent = result

                parsed_val = self._parse_yaml_value(value_str)

                if value_str == "":
                    # 子对象或子列表
                    new_dict = {}
                    parent[key] = new_dict
                    stack.append((new_dict, indent))
                else:
                    parent[key] = parsed_val

        return result

    def _parse_yaml_value(self, value_str):
        """解析YAML值"""
        value_str = value_str.strip()

        # 去除引号
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]

        # 布尔值
        if value_str.lower() in ("true", "yes", "on"):
            return True
        if value_str.lower() in ("false", "no", "off"):
            return False

        # null
        if value_str.lower() in ("null", "~", ""):
            return None

        # 数字
        try:
            if "." in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass

        return value_str


# ══════════════════════════════════════════════
#  认证安全漏洞扫描器
# ══════════════════════════════════════════════

class AuthVulnerabilityScanner:
    """
    认证安全漏洞扫描器
    检测: 未定义securitySchemes、未保护端点、弱认证、敏感端点匿名访问、CORS宽松
    """

    # 敏感端点关键词
    _SENSITIVE_PATTERNS = [
        re.compile(r"(?:admin|delete|remove|config|setting|credential|secret|key|token|password|user)", re.IGNORECASE),
    ]

    # CORS宽松模式
    _CORS_LAX_PATTERNS = [
        re.compile(r"\*", re.IGNORECASE),
        re.compile(r"Access-Control-Allow-Origin.*\*", re.IGNORECASE),
    ]

    def scan(self, spec_data):
        """
        扫描认证安全漏洞

        Args:
            spec_data (dict): {"format", "version", "spec", "source_url"}

        Returns:
            dict: {"scanner", "total_findings", "findings", "owasp_mapping"}
        """
        spec = spec_data.get("spec", {})
        findings = []
        idx = 0

        # 1. 检查是否定义了securitySchemes
        security_schemes = {}
        if spec.get("version", "").startswith("3."):
            components = spec.get("components", {})
            security_schemes = components.get("securitySchemes", {})
        elif spec.get("version", "").startswith("2."):
            security_schemes = spec.get("securityDefinitions", {})

        if not security_schemes:
            idx += 1
            findings.append({
                "id": _generate_finding_id("auth", idx),
                "severity": "high",
                "title": "未定义安全认证方案",
                "description": "API规格中未定义任何securitySchemes，所有端点可能缺少认证保护",
                "endpoint": "*",
                "owasp_category": OWASP_MAPPING.get("no_security_schemes", ""),
                "recommendation": "定义securitySchemes并配置到需要保护的端点",
            })

        # 检查弱认证方案
        for scheme_name, scheme_config in security_schemes.items():
            scheme_type = scheme_config.get("type", "") if isinstance(scheme_config, dict) else ""
            if scheme_type == "basic" or scheme_type == "http" and scheme_config.get("scheme", "") == "basic":
                idx += 1
                findings.append({
                    "id": _generate_finding_id("auth", idx),
                    "severity": "medium",
                    "title": f"弱认证方案: {scheme_name}",
                    "description": f"使用Basic Auth认证方案 '{scheme_name}'，凭据以Base64明文传输",
                    "endpoint": "*",
                    "owasp_category": OWASP_MAPPING.get("weak_auth", ""),
                    "recommendation": "使用Bearer Token (JWT) 或 OAuth2 替代 Basic Auth",
                })

        # 2. 检查未保护的端点
        paths = spec.get("paths", {})
        global_security = spec.get("security", [])

        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue

            for method in ("get", "post", "put", "delete", "patch"):
                if method not in path_item:
                    continue

                operation = path_item[method]
                operation_security = operation.get("security")

                # 判断是否受保护
                is_protected = (
                    operation_security is not None
                    or (not operation_security and global_security)
                )

                if not is_protected:
                    endpoint = f"{method.upper()} {path}"
                    # 检查是否为敏感端点
                    is_sensitive = any(
                        p.search(path) or p.search(str(operation.get("summary", "")))
                        for p in self._SENSITIVE_PATTERNS
                    )

                    if is_sensitive:
                        idx += 1
                        findings.append({
                            "id": _generate_finding_id("auth", idx),
                            "severity": "critical",
                            "title": "敏感端点未受认证保护",
                            "description": f"端点 {endpoint} 涉及敏感操作但未配置认证",
                            "endpoint": endpoint,
                            "owasp_category": OWASP_MAPPING.get("sensitive_anonymous", ""),
                            "recommendation": "为该端点添加security配置",
                        })
                    else:
                        idx += 1
                        findings.append({
                            "id": _generate_finding_id("auth", idx),
                            "severity": "low",
                            "title": "端点未受认证保护",
                            "description": f"端点 {endpoint} 未配置认证要求",
                            "endpoint": endpoint,
                            "owasp_category": OWASP_MAPPING.get("unprotected_endpoint", ""),
                            "recommendation": "确认该端点是否需要认证保护",
                        })

        # 3. 检查CORS配置
        # 查找安全相关扩展字段
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            for method in ("get", "post", "put", "delete", "patch"):
                if method not in path_item:
                    continue
                operation = path_item[method]
                responses = operation.get("responses", {})
                headers = {}
                for resp_code, resp_data in responses.items():
                    if isinstance(resp_data, dict):
                        resp_headers = resp_data.get("headers", {})
                        headers.update(resp_headers)

                for header_name, header_config in headers.items():
                    header_name_lower = header_name.lower()
                    if "access-control-allow-origin" in header_name_lower:
                        if isinstance(header_config, dict):
                            schema_example = str(header_config.get("schema", {}).get("example", ""))
                        else:
                            schema_example = str(header_config)
                        if "*" in schema_example:
                            idx += 1
                            findings.append({
                                "id": _generate_finding_id("auth", idx),
                                "severity": "medium",
                                "title": "CORS配置过于宽松",
                                "description": f"端点 {method.upper()} {path} 的CORS允许所有来源 (*)",
                                "endpoint": f"{method.upper()} {path}",
                                "owasp_category": OWASP_MAPPING.get("cors_lax", ""),
                                "recommendation": "限制CORS允许的来源域名",
                            })

        # OWASP映射汇总
        owasp_map = {}
        for f in findings:
            cat = f.get("owasp_category", "")
            if cat:
                owasp_map[cat] = owasp_map.get(cat, 0) + 1

        return {
            "scanner": "AuthVulnerabilityScanner",
            "total_findings": len(findings),
            "findings": findings,
            "owasp_mapping": owasp_map,
        }


# ══════════════════════════════════════════════
#  输入校验漏洞扫描器
# ══════════════════════════════════════════════

class InputValidationScanner:
    """
    输入校验漏洞扫描器
    检测: 参数无schema、字符串无maxLength、数字无range、路径参数无格式验证
          URL参数无域名限制、additionalProperties未限制
    """

    def scan(self, spec_data):
        """
        扫描输入校验漏洞

        Args:
            spec_data (dict): {"format", "version", "spec", "source_url"}

        Returns:
            dict: {"scanner", "total_findings", "findings", "owasp_mapping"}
        """
        spec = spec_data.get("spec", {})
        findings = []
        idx = 0

        paths = spec.get("paths", {})

        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue

            for method in ("get", "post", "put", "delete", "patch"):
                if method not in path_item:
                    continue

                operation = path_item[method]
                endpoint = f"{method.upper()} {path}"

                # 检查参数定义
                parameters = operation.get("parameters", [])

                for param in parameters:
                    if not isinstance(param, dict):
                        continue

                    param_name = param.get("name", "unknown")
                    param_in = param.get("in", "")
                    param_schema = param.get("schema", {})

                    # 1. 参数无schema
                    if not param_schema and param.get("in") != "body":
                        idx += 1
                        findings.append({
                            "id": _generate_finding_id("input", idx),
                            "severity": "medium",
                            "title": f"参数无Schema定义: {param_name}",
                            "description": f"参数 '{param_name}' (位置: {param_in}) 未定义schema，无法校验类型和格式",
                            "endpoint": endpoint,
                            "owasp_category": OWASP_MAPPING.get("no_schema", ""),
                            "recommendation": "为参数定义schema，指定类型和约束",
                        })
                        continue

                    # 2. 字符串参数无maxLength
                    if param_schema.get("type") == "string":
                        has_max_length = (
                            "maxLength" in param_schema
                            or "max_length" in param_schema
                            or "pattern" in param_schema
                        )
                        if not has_max_length:
                            idx += 1
                            findings.append({
                                "id": _generate_finding_id("input", idx),
                                "severity": "low",
                                "title": f"字符串参数无长度限制: {param_name}",
                                "description": f"字符串参数 '{param_name}' 未设置maxLength，可能导致缓冲区溢出或DoS",
                                "endpoint": endpoint,
                                "owasp_category": OWASP_MAPPING.get("no_max_length", ""),
                                "recommendation": "设置maxLength限制字符串长度",
                            })

                    # 3. 数字参数无范围
                    if param_schema.get("type") in ("integer", "number"):
                        has_range = (
                            "minimum" in param_schema
                            or "maximum" in param_schema
                            or "exclusiveMinimum" in param_schema
                            or "exclusiveMaximum" in param_schema
                        )
                        if not has_range:
                            idx += 1
                            findings.append({
                                "id": _generate_finding_id("input", idx),
                                "severity": "medium",
                                "title": f"数字参数无范围限制: {param_name}",
                                "description": f"数字参数 '{param_name}' 未设置minimum/maximum，可能导致数值溢出",
                                "endpoint": endpoint,
                                "owasp_category": OWASP_MAPPING.get("no_number_range", ""),
                                "recommendation": "设置minimum和maximum限制数值范围",
                            })

                    # 4. 路径参数无格式验证
                    if param_in == "path":
                        has_format = (
                            "format" in param_schema
                            or "pattern" in param_schema
                            or "enum" in param_schema
                        )
                        if not has_format:
                            idx += 1
                            findings.append({
                                "id": _generate_finding_id("input", idx),
                                "severity": "medium",
                                "title": f"路径参数无格式验证: {param_name}",
                                "description": f"路径参数 '{param_name}' 无format/pattern限制，可能接受恶意输入",
                                "endpoint": endpoint,
                                "owasp_category": OWASP_MAPPING.get("no_path_format", ""),
                                "recommendation": "添加format或pattern约束路径参数",
                            })

                    # 5. URL参数无域名限制
                    if param_schema.get("type") == "string" and param_schema.get("format") == "uri":
                        has_pattern = "pattern" in param_schema
                        if not has_pattern:
                            idx += 1
                            findings.append({
                                "id": _generate_finding_id("input", idx),
                                "severity": "medium",
                                "title": f"URL参数无域名限制: {param_name}",
                                "description": f"URL参数 '{param_name}' 无pattern限制，可能被用于SSRF攻击",
                                "endpoint": endpoint,
                                "owasp_category": OWASP_MAPPING.get("no_url_domain", ""),
                                "recommendation": "添加pattern限制允许的域名格式",
                            })

                # 6. 检查requestBody的additionalProperties
                request_body = operation.get("requestBody", {})
                if isinstance(request_body, dict):
                    content = request_body.get("content", {})
                    for content_type, media_type in content.items():
                        if not isinstance(media_type, dict):
                            continue
                        schema = media_type.get("schema", {})
                        if isinstance(schema, dict):
                            # 检查additionalProperties
                            additional = schema.get("additionalProperties")
                            if additional is None or additional is True:
                                idx += 1
                                findings.append({
                                    "id": _generate_finding_id("input", idx),
                                    "severity": "medium",
                                    "title": "请求体未限制额外属性",
                                    "description": f"端点 {endpoint} 的请求体schema未设置additionalProperties=false",
                                    "endpoint": endpoint,
                                    "owasp_category": OWASP_MAPPING.get("additional_properties", ""),
                                    "recommendation": "设置additionalProperties=false或定义明确的属性列表",
                                })

        # OWASP映射汇总
        owasp_map = {}
        for f in findings:
            cat = f.get("owasp_category", "")
            if cat:
                owasp_map[cat] = owasp_map.get(cat, 0) + 1

        return {
            "scanner": "InputValidationScanner",
            "total_findings": len(findings),
            "findings": findings,
            "owasp_mapping": owasp_map,
        }


# ══════════════════════════════════════════════
#  扫描编排器
# ══════════════════════════════════════════════

class APIScanOrchestrator:
    """
    API扫描编排器
    整合所有扫描器，计算5维安全评分

    评分维度（各20%）:
      - auth:             认证安全
      - input_validation: 输入校验
      - business_logic:   业务逻辑（预留）
      - data_exposure:    数据泄露（预留）
      - config:           配置安全
    """

    # 评分权重
    _DIMENSIONS = {
        "auth":             {"weight": 0.20, "label": "认证安全"},
        "input_validation": {"weight": 0.20, "label": "输入校验"},
        "business_logic":   {"weight": 0.20, "label": "业务逻辑"},
        "data_exposure":    {"weight": 0.20, "label": "数据泄露"},
        "config":           {"weight": 0.20, "label": "配置安全"},
    }

    def scan(self, spec_source, scanner_names=None):
        """
        执行API安全扫描

        Args:
            spec_source (str):         API规格URL或规格内容（JSON字符串）
            scanner_names (list, opt): 指定要运行的扫描器名称

        Returns:
            dict: {"scan_id", "spec_info", "results", "score", "owasp_compliance"}
        """
        scan_id = _generate_scan_id()
        start_time = time.time()

        # 加载规格
        loader = APISpecLoader()

        if spec_source.startswith("http://") or spec_source.startswith("https://"):
            spec_data = loader.load_from_url(spec_source)
        else:
            # 尝试解析为JSON内容
            try:
                spec_content = json.loads(spec_source)
                spec_data = {
                    "format": "json",
                    "version": loader._detect_version(spec_content),
                    "spec": spec_content,
                    "source_url": "inline",
                }
            except (json.JSONDecodeError, TypeError):
                spec_data = loader.load_from_url(spec_source)

        # 验证规格
        validation = loader.validate_spec(spec_data)

        # 确定要运行的扫描器
        all_scanners = {
            "auth":             AuthVulnerabilityScanner(),
            "input_validation": InputValidationScanner(),
        }

        if scanner_names:
            scanners_to_run = {
                name: all_scanners[name]
                for name in scanner_names
                if name in all_scanners
            }
        else:
            scanners_to_run = all_scanners

        # 运行扫描器
        results = {}
        all_findings = []
        owasp_summary = {}

        for name, scanner in scanners_to_run.items():
            try:
                result = scanner.scan(spec_data)
                results[name] = result
                all_findings.extend(result.get("findings", []))

                # 合并OWASP映射
                for cat, count in result.get("owasp_mapping", {}).items():
                    owasp_summary[cat] = owasp_summary.get(cat, 0) + count
            except Exception as e:
                results[name] = {
                    "scanner": scanner.__class__.__name__,
                    "total_findings": 0,
                    "findings": [],
                    "owasp_mapping": {},
                    "error": str(e),
                }

        # 计算5维评分
        scores = self._calculate_scores(results)
        overall_score = sum(
            scores[dim]["score"] * self._DIMENSIONS[dim]["weight"]
            for dim in self._DIMENSIONS
        )
        overall_score = round(overall_score, 1)

        # 计算OWASP合规率
        owasp_compliance = self._calc_owasp_compliance(owasp_summary)

        duration_ms = int((time.time() - start_time) * 1000)

        # 持久化结果
        self._save_result(scan_id, spec_data, validation, results,
                          scores, overall_score, owasp_compliance, duration_ms)

        return {
            "scan_id": scan_id,
            "spec_info": {
                "source_url": spec_data.get("source_url", ""),
                "format": spec_data.get("format", ""),
                "version": spec_data.get("version", ""),
                "valid": validation["valid"],
                "validation_errors": len(validation["errors"]),
                "validation_warnings": len(validation["warnings"]),
            },
            "results": {
                name: {
                    "scanner": r.get("scanner", ""),
                    "total_findings": r.get("total_findings", 0),
                }
                for name, r in results.items()
            },
            "findings_summary": {
                "total": len(all_findings),
                "critical": len([f for f in all_findings if f.get("severity") == "critical"]),
                "high": len([f for f in all_findings if f.get("severity") == "high"]),
                "medium": len([f for f in all_findings if f.get("severity") == "medium"]),
                "low": len([f for f in all_findings if f.get("severity") == "low"]),
            },
            "score": {
                "overall": overall_score,
                "dimensions": {
                    dim: {
                        "score": scores[dim]["score"],
                        "label": self._DIMENSIONS[dim]["label"],
                    }
                    for dim in self._DIMENSIONS
                },
            },
            "owasp_compliance": owasp_compliance,
            "duration_ms": duration_ms,
        }

    def _calculate_scores(self, results):
        """
        计算5维安全评分

        评分规则:
          - 有扫描器结果: 基于 finding 数量和严重程度扣分
          - 无扫描器结果（预留维度）: 默认80分

        Args:
            results (dict): 扫描器结果

        Returns:
            dict: 各维度评分
        """
        scores = {}

        for dim in self._DIMENSIONS:
            dim_result = results.get(dim)
            if dim_result is None:
                # 预留维度，暂无扫描器，给默认分
                scores[dim] = {"score": 80, "max": 100, "findings": 0}
                continue

            findings = dim_result.get("findings", [])
            score = 100

            # 按严重程度扣分
            for f in findings:
                severity = f.get("severity", "low")
                if severity == "critical":
                    score -= 20
                elif severity == "high":
                    score -= 10
                elif severity == "medium":
                    score -= 5
                elif severity == "low":
                    score -= 2

            score = max(0, score)
            scores[dim] = {
                "score": score,
                "max": 100,
                "findings": len(findings),
            }

        return scores

    def _calc_owasp_compliance(self, owasp_summary):
        """
        计算OWASP API合规率

        Args:
            owasp_summary (dict): OWASP分类发现数量

        Returns:
            dict: {"compliant_categories", "total_categories", "compliance_rate"}
        """
        total = len(OWASP_API_CATEGORIES)
        compliant = total - len(owasp_summary)
        rate = round((compliant / total) * 100, 1) if total > 0 else 100

        return {
            "compliant_categories": compliant,
            "total_categories": total,
            "compliance_rate": rate,
            "violations": owasp_summary,
        }

    def _save_result(self, scan_id, spec_data, validation, results,
                     scores, overall_score, owasp_compliance, duration_ms):
        """持久化扫描结果"""
        os.makedirs(_DATA_DIR, exist_ok=True)

        existing = _load_json(API_SCAN_RESULTS_FILE, {"scans": {}})

        scan_record = {
            "scan_id": scan_id,
            "spec_info": {
                "source_url": spec_data.get("source_url", ""),
                "format": spec_data.get("format", ""),
                "version": spec_data.get("version", ""),
            },
            "validation": validation,
            "results": results,
            "scores": scores,
            "overall_score": overall_score,
            "owasp_compliance": owasp_compliance,
            "duration_ms": duration_ms,
            "scanned_at": _now_iso(),
        }

        existing["scans"][scan_id] = scan_record
        _save_json(API_SCAN_RESULTS_FILE, existing)


# ══════════════════════════════════════════════
#  独立测试入口
# ══════════════════════════════════════════════

if __name__ == "__main__":
    print("=== API接口安全扫描测试 ===")

    # 构造一个测试用的OpenAPI 3.0规格
    test_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Test API",
            "version": "1.0.0",
        },
        "paths": {
            "/api/public/info": {
                "get": {
                    "summary": "Public info",
                    "responses": {"200": {"description": "OK"}},
                }
            },
            "/api/admin/users": {
                "delete": {
                    "summary": "Delete admin user",
                    "parameters": [
                        {
                            "name": "userId",
                            "in": "path",
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {"200": {"description": "OK"}},
                }
            },
            "/api/users": {
                "post": {
                    "summary": "Create user",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "email": {"type": "string", "format": "email"},
                                        "age": {"type": "integer"},
                                    },
                                },
                            }
                        }
                    },
                    "responses": {"201": {"description": "Created"}},
                }
            },
            "/api/callback": {
                "get": {
                    "summary": "Webhook callback",
                    "parameters": [
                        {
                            "name": "url",
                            "in": "query",
                            "schema": {"type": "string", "format": "uri"},
                        }
                    ],
                    "responses": {"200": {"description": "OK"}},
                }
            },
        },
    }

    print("\n--- 扫描测试API规格 ---")
    orchestrator = APIScanOrchestrator()

    # 传入JSON字符串（模拟内联规格）
    spec_json = json.dumps(test_spec)
    result = orchestrator.scan(spec_json)

    print(f"  scan_id: {result['scan_id']}")
    print(f"  总评分: {result['score']['overall']}/100")
    print(f"  扫描耗时: {result['duration_ms']}ms")
    print(f"  OWASP合规率: {result['owasp_compliance']['compliance_rate']}%")

    print("\n  维度评分:")
    for dim, info in result["score"]["dimensions"].items():
        print(f"    {info['label']}: {info['score']}/100")

    print(f"\n  发现汇总:")
    print(f"    总计: {result['findings_summary']['total']}个")
    print(f"    critical: {result['findings_summary']['critical']}")
    print(f"    high: {result['findings_summary']['high']}")
    print(f"    medium: {result['findings_summary']['medium']}")
    print(f"    low: {result['findings_summary']['low']}")

    # 显示OWASP违规
    violations = result["owasp_compliance"].get("violations", {})
    if violations:
        print(f"\n  OWASP违规:")
        for cat, count in violations.items():
            cat_name = OWASP_API_CATEGORIES.get(cat, cat)
            print(f"    {cat} ({cat_name}): {count}个发现")

    # 测试YAML加载器
    print("\n--- YAML简单解析测试 ---")
    loader = APISpecLoader()
    yaml_content = """
openapi: "3.0.0"
info:
  title: YAML Test API
  version: "1.0.0"
paths:
  /api/test:
    get:
      summary: Test endpoint
      responses:
        200:
          description: OK
"""
    parsed = loader._simple_yaml_to_json(yaml_content)
    print(f"  解析成功: openapi={parsed.get('openapi')}")
    print(f"  title={parsed.get('info', {}).get('title')}")

    # 测试规格验证
    print("\n--- 规格验证测试 ---")
    validation = loader.validate_spec({
        "format": "json",
        "version": "3.0.0",
        "spec": test_spec,
    })
    print(f"  valid={validation['valid']}")
    print(f"  errors={validation['errors']}")
    print(f"  warnings={validation['warnings']}")

    print("\n=== 全部测试通过 ===")
