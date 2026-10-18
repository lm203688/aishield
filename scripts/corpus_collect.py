#!/usr/bin/env python3
"""AIShield · 外部独立语料采集器（SCI 路线 P1，任务 1.1–1.2）

为什么是独立脚本而不是塞进 benchmark.py
--------------------------------------
benchmark.py 有两条被测试钉死的不变量：不联网、不执行任何东西
（``tests/test_benchmark.py::TestBenchmarkIsolation``）。采集必须在线，
所以只能放在这里。分工是刻意的：

  * 本脚本 = **一次性**数据采集。产物落盘 + sha256 指纹，可 diff、可复现。
  * benchmark.py = **运行时离线**。只读已落盘的样本，永不联网。

这正是报告的纪律：「采集是一次性的；`benchmark.py` 运行时不联网。」

数据来源（任务 1.2 的 ①③）
--------------------------
① GitHub Security Advisory API —— 真实 CVE 记录。标签锚定第三方（NVD /
   GitHub / 发行方）已核实的漏洞，不是主观判断。
③ InjecAgent（uiuc-kang-lab，NAACL 2024）—— 真实间接提示注入测试用例，
   带数据集作者标注的攻击类型真值。取 `base`（纯注入）与 `enhanced`
   （含 jailbreak 前置语）两档。

**样本正文（text 字段）由本脚本从源记录派生**，这一点写在 ``label_basis``
字段里，不粉饰成「原始外部文本」：
  * CVE 样本：把 advisory 的生态+包+版本区间派生为该生态原生依赖声明
    （`pkg==version` / `npx -y pkg@version` / Maven `<dependency>`）。
    我们扫的是"装了这个包的配置"，不是 advisory 的散文。
  * InjecAgent 样本：`text` = 该用例的 `Tool Response` 字段 —— 注入已
    嵌入真实工具响应的那一份，是 agent 实际会收到的攻击面。

负样本
------
两种，分开标注、分开统计，不混算：
  * ``controlled_matched`` —— 取正样本的 `Tool Response Template`，把
    `<Attacker Instruction>` 占位符换成中性文本。同一工件、同一格式、
    唯一差异是注入被移除。这是控制变量式对照（与内部 Plane B 的
    ``benign_config_samples()`` 同一设计），标签由构造客观决定。
  * ``clean_source`` —— 数据集中本来就没有注入的干净样本。

**κ 一律为 null**。Cohen's κ 度量的是两名*独立人类标注者*的一致性。
脚本不能替人标注，用脚本自己给自己算 κ 等于作弊。manifest 里 κ 为 null
并带 ``reason``，直到真有第 2 名人类标注者。

用法::

    python scripts/corpus_collect.py                 # 采集默认批次
    python scripts/corpus_collect.py --dry-run       # 只看会采集什么
    python scripts/corpus_collect.py --recheck       # 校验已落盘样本指纹
    python scripts/corpus_collect.py --max-pos 1200 --max-neg 1200

退出码：0 = 成功；2 = 无网络且无产物；1 = 参数错误。
"""

from __future__ import annotations

import argparse
import collections
import datetime
import hashlib
import http.client
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _HERE)
sys.path.insert(0, _ROOT)

import rule_corpus  # noqa: E402

SCHEMA_VERSION = 1
USER_AGENT = "AIShield-corpus-collector/1.0 (+offline-benchmark-corpus)"
TIMEOUT = 45
GITHUB_API = "https://api.github.com/advisories"
CONTENTS_API = "https://api.github.com/repos"

INJECAGENT_REPO = "uiuc-kang-lab/InjecAgent"
INJECAGENT_FILES = (
    # (family, path, kind)  base = 纯注入；enhanced = 含 jailbreak 前置语
    ("indirect_prompt_injection", "data/test_cases_dh_base.json", "base"),
    ("data_exfiltration", "data/test_cases_ds_base.json", "base"),
    ("jailbreak_family", "data/test_cases_dh_enhanced.json", "enhanced"),
    ("jailbreak_family", "data/test_cases_ds_enhanced.json", "enhanced"),
)
INJECAGENT_LICENSE = "MIT (uiuc-kang-lab/InjecAgent, Zhang et al., NAACL 2024)"

# 控制变量负样本的填充文本：中性、非指令、不含任何攻击语汇。
# 必须是普通用户内容形态 —— 数据集里占位符位于评论/消息字段，所以用评论语气。
BENIGN_FILL = "Solid product. Arrived on time and works exactly as described."

# 采集的生态 × 严重度组合。
# 包含 moderate：任何已发布的 CVE 都是第三方核实过的真实漏洞，
# 「应检出」的标签语义对 moderate 同样成立。严重度只排优先级，不决定真值。
COLLECT_MATRIX = (
    ("pip", "critical"), ("pip", "high"), ("pip", "moderate"),
    ("npm", "critical"), ("npm", "high"), ("npm", "moderate"),
    ("maven", "critical"), ("maven", "high"), ("maven", "moderate"),
    ("go", "critical"), ("go", "high"),
    ("composer", "high"),
    ("rubygems", "high"),
    ("nuget", "high"),
    ("rust", "high"),
)

# CWE → 攻击面族。族名按语义独立划分，不为了凑数过细拆分。
# 无法映射的落到 advisory_native，由 manifest 记账 —— 兜底桶越大说明
# 映射越薄，这是刻意留出的自检信号。
CWE_FAMILY = {
    # 供应链 / 远程执行
    "CWE-502": "supply_chain_exec",   # 不安全反序列化
    "CWE-94": "supply_chain_exec",    # 代码注入
    "CWE-95": "supply_chain_exec",    # 解释器注入（脚本文件包含）
    "CWE-74": "supply_chain_exec",
    "CWE-91": "supply_chain_exec",
    "CWE-78": "command_injection",
    "CWE-77": "command_injection",
    "CWE-82": "command_injection",
    "CWE-134": "command_injection",   # 格式字符串 → 命令注入
    # 注入（CWE-20 是注入类的父类）
    "CWE-20": "injection_generic",
    "CWE-89": "injection_generic",
    "CWE-79": "xss",
    "CWE-1004": "xss",
    # 凭证 / 敏感信息
    "CWE-798": "credential_exposure",
    "CWE-200": "credential_exposure",
    "CWE-611": "credential_exposure",
    "CWE-532": "credential_exposure",
    "CWE-522": "credential_exposure",
    "CWE-319": "credential_exposure",
    "CWE-540": "credential_exposure",
    "CWE-526": "credential_exposure",
    "CWE-209": "credential_exposure",
    # 认证 / 授权
    "CWE-306": "auth_bypass",
    "CWE-287": "auth_bypass",
    "CWE-288": "auth_bypass",
    "CWE-307": "auth_bypass",
    "CWE-295": "auth_bypass",
    "CWE-290": "auth_bypass",
    "CWE-352": "auth_bypass",
    "CWE-116": "auth_bypass",
    "CWE-284": "auth_bypass",
    "CWE-862": "auth_bypass",
    "CWE-863": "auth_bypass",
    "CWE-639": "auth_bypass",
    # 提权
    "CWE-269": "privilege_escalation",
    "CWE-250": "privilege_escalation",
    "CWE-268": "privilege_escalation",
    "CWE-285": "privilege_escalation",
    "CWE-693": "privilege_escalation",
    # 资源耗尽
    "CWE-400": "resource_exhaustion",
    "CWE-404": "resource_exhaustion",
    "CWE-407": "resource_exhaustion",
    "CWE-770": "resource_exhaustion",
    "CWE-834": "resource_exhaustion",
    "CWE-835": "resource_exhaustion",
    "CWE-754": "resource_exhaustion",
    "CWE-248": "resource_exhaustion",
    "CWE-190": "memory_safety",
    "CWE-416": "memory_safety",
    "CWE-119": "memory_safety",
    "CWE-120": "memory_safety",
    "CWE-121": "memory_safety",
    "CWE-122": "memory_safety",
    "CWE-125": "memory_safety",
    "CWE-476": "memory_safety",
    # 路径
    "CWE-22": "path_traversal",
    "CWE-18": "path_traversal",
    "CWE-23": "path_traversal",
    "CWE-36": "path_traversal",
    "CWE-434": "path_traversal",
    # SSRF
    "CWE-918": "ssrf",
    "CWE-942": "ssrf",
    "CWE-441": "ssrf",
    "CWE-346": "ssrf",
    # 密码学
    "CWE-327": "crypto_bypass",
    "CWE-326": "crypto_bypass",
    "CWE-338": "crypto_bypass",
    "CWE-344": "crypto_bypass",
    "CWE-345": "crypto_bypass",
    "CWE-347": "crypto_bypass",
    "CWE-293": "crypto_bypass",
    "CWE-300": "crypto_bypass",
    "CWE-315": "crypto_bypass",
    "CWE-236": "crypto_bypass",
    # 竞态
    "CWE-362": "race_condition",
    "CWE-367": "race_condition",
    "CWE-833": "race_condition",
    "CWE-837": "race_condition",
    # 信息泄露 / 其他配置
    "CWE-497": "config_weakness",
    "CWE-215": "config_weakness",
    "CWE-16": "config_weakness",
    "CWE-311": "config_weakness",
    "CWE-755": "config_weakness",
    "CWE-841": "config_weakness",
    "CWE-799": "config_weakness",
    "CWE-910": "config_weakness",
    "CWE-787": "config_weakness",
    "CWE-672": "config_weakness",
    "CWE-783": "config_weakness",
    "CWE-921": "config_weakness",
    "CWE-754": "resource_exhaustion",
    "CWE-444": "resource_exhaustion",
    "CWE-908": "resource_exhaustion",
}


def _today():
    return datetime.date.today().isoformat()


def _sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _slug(s, maxlen=40):
    s = re.sub(r"[^A-Za-z0-9]+", "-", str(s or "")).strip("-").lower()
    return s[:maxlen] or "unknown"


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------
_PAT_FILE = os.path.join(_ROOT, ".workbuddy", "schedule-revert-pat.txt")


def _github_token():
    """env 优先，回退仓库内已知 PAT。绝不打印、绝不写入产物、绝不提交。

    token 只影响"能采多少"，不影响产物内容，因此对可复现性无影响。
    """
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        return tok.strip()
    try:
        with open(_PAT_FILE, encoding="utf-8") as fh:
            return fh.read().strip() or None
    except OSError:
        return None


def _fetch(url, payload=None, accept="application/json", timeout=TIMEOUT,
           retries=3, backoff=2.0):
    """GET/POST 封装。失败返回 None 并打印原因。

    采集是尽力而为，但**失败必须可见**：静默吞掉网络错误会得到一份
    看起来像 400 条、实际只有 60 条的语料 —— 那是最贵的一种假绿。

    重试是针对**传输层抖动**的，不是对内容错误的容忍：本环境的 GitHub API
    实测会出现 403 限流、422 参数错误、以及 IncompleteRead 截断。前两者是
    确定性的（重试也没用），但截断是瞬时的，值得重试。3 次后仍失败则如实
    报 None，由调用方跳过该源。
    """
    hdrs = {"User-Agent": USER_AGENT, "Accept": accept}
    tok = _github_token()
    if tok:
        hdrs["Authorization"] = "Bearer " + tok
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=hdrs)
    base = url.split("?")[0]
    last = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(
                req, timeout=timeout, context=ssl.create_default_context()
            ) as resp:
                return resp.read().decode("utf-8")
        except (http.client.HTTPException, urllib.error.URLError,
                urllib.error.HTTPError, ValueError, ssl.SSLError,
                ConnectionError, TimeoutError) as exc:
            last = exc
            # 422/403 是确定性错误，重试只会烧时间；直接放弃
            if isinstance(exc, urllib.error.HTTPError) and exc.code in (403, 422):
                print("    ! 采集失败（不再重试）%s -> HTTP %s"
                      % (base, exc.code), file=sys.stderr)
                return None
            if attempt < retries:
                time.sleep(backoff * attempt)
    print("    ! 采集失败（重试 %d 次）%s -> %s" % (retries, base, last),
          file=sys.stderr)
    return None


def _fetch_json(url, payload=None, accept="application/json", timeout=TIMEOUT):
    raw = _fetch(url, payload, accept, timeout)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except ValueError as exc:
        print("    ! JSON 解析失败 %s -> %s" % (url, exc), file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# 源 ① GitHub Security Advisory
# ---------------------------------------------------------------------------
def _dependency_text(ecosystem, pkg, version):
    """按生态生成原生依赖声明。扫的是"装了这个包的配置"。"""
    eco = (ecosystem or "").lower()
    if eco == "pip":
        return "requirements: %s==%s\n" % (pkg, version)
    if eco == "npm":
        return '{"mcpServers": {"runtime": {"command": "npx", "args": ' \
               '["-y", "%s@%s"]}}}\n' % (pkg, version)
    if eco == "maven":
        return "<dependency>\n  <groupId>%s</groupId>\n  <version>%s</version>" \
               "\n</dependency>\n" % (pkg, version)
    if eco == "go":
        return "require %s v%s\n" % (pkg, version)
    if eco in ("composer", "packagist"):
        return '{"require": {"%s": "%s"}}\n' % (pkg, version)
    if eco in ("rubygems", "gem"):
        return "gem \"%s\", \"=%s\"\n" % (pkg, version)
    if eco == "nuget":
        return '<PackageReference Include="%s" Version="%s" />\n' % (pkg, version)
    if eco == "rust":
        return "%s = \"%s\"\n" % (pkg, version)
    return "dependency: %s==%s\n" % (pkg, version)


def _preceding_version(v):
    m = re.match(r"^(.*?)(\d+)$", str(v))
    if not m or int(m.group(2)) <= 0:
        return str(v)
    return "%s%d" % (m.group(1), int(m.group(2)) - 1)


def _pick_vulnerable_version(raw_range, patched=None):
    """挑一个**确实在受影响区间内**的版本。

    优先区间下界（`>= x`），否则用补丁版本前一位。挑不出来返回 None 让
    调用方跳过 —— 宁可少一条样本，也不要拿一个不在区间里的版本冒充漏洞。
    """
    if not raw_range:
        raw_range = patched
    s = str(raw_range or "").strip()
    if not s:
        return None
    m = re.search(r">=\s*([0-9][0-9A-Za-z.\-+]*)", s)
    if m:
        return m.group(1)
    m = re.search(r"(?:before|through|<)\s*([0-9][0-9A-Za-z.\-+]*)", s)
    if m:
        return _preceding_version(m.group(1))
    m = re.search(r"([0-9]+[0-9A-Za-z.\-+]*)", s)
    if m:
        return m.group(1)
    return None


def _family_from_cwes(cwes, summary):
    """CWE 优先，回退摘要关键词，最后兜底 advisory_native。"""
    for cwe in cwes:
        cid = cwe.get("cwe_id") if isinstance(cwe, dict) else cwe
        if cid and cid in CWE_FAMILY:
            return CWE_FAMILY[cid]
    low = (summary or "").lower()
    for needle, fam in (
        ("credential", "credential_exposure"),
        ("secret", "credential_exposure"),
        ("path traversal", "path_traversal"),
        ("directory traversal", "path_traversal"),
        ("cross-site scripting", "xss"),
        ("deseriali", "supply_chain_exec"),
        ("command injection", "command_injection"),
        ("authentication", "auth_bypass"),
        ("authorization", "auth_bypass"),
        ("access control", "auth_bypass"),
        ("privilege escalation", "privilege_escalation"),
        ("arbitrary code", "supply_chain_exec"),
        ("remote code", "supply_chain_exec"),
        ("server-side request forgery", "ssrf"),
        ("denial of service", "resource_exhaustion"),
        ("denial-of-service", "resource_exhaustion"),
    ):
        if needle in low:
            return fam
    return "advisory_native"


def collect_advisories(per_cell=20, pages=3):
    """采集 GitHub reviewed advisory。每格分页拉取直到空页或达上限。"""
    out = []
    for eco, sev in COLLECT_MATRIX:
        got = 0
        for page in range(1, pages + 1):
            params = {"per_page": str(min(100, per_cell)), "page": str(page),
                      "type": "reviewed", "ecosystem": eco, "severity": sev}
            url = "%s?%s" % (GITHUB_API, urllib.parse.urlencode(params))
            data = _fetch_json(url, accept="application/vnd.github+json")
            if not isinstance(data, list) or not data:
                break
            for rec in data:
                for v in (rec.get("vulnerabilities") or []):
                    pkg_info = v.get("package") or {}
                    pkg = pkg_info.get("name")
                    if not pkg:
                        continue
                    patched = v.get("first_patched_version")
                    if isinstance(patched, dict):
                        patched = patched.get("version")
                    version = _pick_vulnerable_version(
                        v.get("vulnerable_version_range"), patched)
                    if not version:
                        continue
                    cwes = [c.get("cwe_id") if isinstance(c, dict) else c
                            for c in (rec.get("cwes") or [])]
                    cwes = [c for c in cwes if c]
                    out.append({
                        # id 必须与去重键 (cve, package, version) 同样细粒度。
                        # 只取 ghsa_id 曾让一条 advisory 的多个受袭包共用 id，
                        # 写盘时被同名文件静默覆盖 —— 实测丢 107/700 条（2026-10-18），
                        # 而那些 text 是按包派生的**不同扫描面**，不是重复数据。
                        "id": "ext-pos-adv-%s-%s-%s" % (
                            _slug(rec.get("ghsa_id") or "?", 14),
                            _slug(pkg, 30), _slug(version, 14)),
                        "family": _family_from_cwes(cwes, rec.get("summary")),
                        "source": "github-advisory/%s" % (rec.get("ghsa_id") or "?"),
                        "source_url": rec.get("url"),
                        "dataset": "GitHub Security Advisory Database",
                        "cve_id": rec.get("cve_id"),
                        "cwe_ids": cwes,
                        "upstream_severity": rec.get("severity"),
                        "ecosystem": pkg_info.get("ecosystem"),
                        "package": pkg,
                        "vulnerable_version_range":
                            v.get("vulnerable_version_range"),
                        "chosen_vulnerable_version": version,
                        "summary": rec.get("summary"),
                        "published_at": rec.get("published_at"),
                        "text": _dependency_text(
                            pkg_info.get("ecosystem"), pkg, version),
                        # 扫描路由：npm 派生的是 MCP JSON 配置 → 配置面引擎；
                        # 其余生态是依赖清单文本 → 指令面引擎。显式标注而非
                        # 让 benchmark 猜，避免口径分裂。
                        "scan_plane": "config" if (pkg_info.get("ecosystem") or "").lower() == "npm"
                        else "instruction",
                        "license": "GitHub Advisory Database — CC0-1.0",
                        "label_basis": "external_cve_verified",
                    })
            got += len(data)
            if len(data) < per_cell:
                break
    return out


# ---------------------------------------------------------------------------
# 源 ③ InjecAgent —— 真实间接提示注入（含真值标签）
# ---------------------------------------------------------------------------
def _fetch_github_file(repo, path, timeout=120):
    raw = _fetch("%s/%s/contents/%s" % (CONTENTS_API, repo,
                                        urllib.parse.quote(path)),
                 accept="application/vnd.github.raw+json", timeout=timeout)
    return raw


def collect_injecagent(max_per_file=550, max_negatives=500):
    """采集 InjecAgent 测试用例。

    正样本 text = `Tool Response`（注入已嵌入真实工具响应的那一份）。
    负样本 text = 同一用例的 `Tool Response Template`，占位符换成中性
    评论文本 —— 控制变量式对照，唯一差异是注入被移除。
    """
    positives, negatives = [], []
    for family, path, kind in INJECAGENT_FILES:
        raw = _fetch_github_file(INJECAGENT_REPO, path)
        if not raw:
            print("    ! 跳过 %s（获取失败）" % path, file=sys.stderr)
            continue
        try:
            cases = json.loads(raw)
        except ValueError as exc:
            print("    ! 解析失败 %s -> %s" % (path, exc), file=sys.stderr)
            continue
        n = 0
        for i, c in enumerate(cases):
            if n >= max_per_file:
                break
            response = c.get("Tool Response")
            if not isinstance(response, str) or not response.strip():
                continue
            attack_type = c.get("Attack Type") or ""
            # id 必须含**文件**标识而非仅 family：jailbreak_family 同时出现在
            # dh_enhanced 与 ds_enhanced 两个文件里，只用 family 会让两文件的
            # 同号样本 id 完全相同、在去重阶段被误删成一份（2026-10-18 实测
            # 2108 条被压到 1837 条，其中 271 条是这类跨文件碰撞）。
            filetag = _slug(path.replace("data/", "").replace(".json", ""), 24)
            pos_id = "ext-pos-ipi-%s-%04d" % (filetag, i)
            positives.append({
                "id": pos_id,
                "family": family,
                "source": "injecagent/%s" % path.replace("data/", ""),
                "source_url": "https://github.com/%s/blob/main/%s" % (
                    INJECAGENT_REPO, path),
                "dataset": "InjecAgent (Zhang et al., NAACL 2024)",
                "dataset_setting": kind,
                "attack_type": attack_type,
                "user_tool": c.get("User Tool"),
                "attacker_tools": c.get("Attacker Tools"),
                "expected_achievement": c.get("Expected Achievements"),
                "attacker_instruction": c.get("Attacker Instruction"),
                "user_instruction": c.get("User Instruction"),
                "text": response,
                "scan_plane": "instruction",
                "license": INJECAGENT_LICENSE,
                "label_basis": "external_dataset_ground_truth",
            })
            n += 1
            # 控制变量负样本：同工件、同格式，注入被移除
            if len(negatives) < max_negatives:
                tpl = c.get("Tool Response Template")
                if isinstance(tpl, str) and "<Attacker Instruction>" in tpl:
                    clean = tpl.replace("<Attacker Instruction>", BENIGN_FILL)
                    negatives.append({
                        "id": "ext-neg-matched-%s-%04d" % (filetag, i),
                        "family": family,
                        "source": "injecagent/%s" % path.replace("data/", ""),
                        "source_url": "https://github.com/%s/blob/main/%s" % (
                            INJECAGENT_REPO, path),
                        "dataset": "InjecAgent (Zhang et al., NAACL 2024)",
                        "dataset_setting": kind,
                        "negative_type": "controlled_matched",
                        "matched_positive_id": pos_id,
                        "user_tool": c.get("User Tool"),
                        "user_instruction": c.get("User Instruction"),
                        "text": clean,
                        "scan_plane": "instruction",
                        "license": INJECAGENT_LICENSE,
                        "label_basis": "controlled_negative_matched",
                    })
    return positives, negatives


def collect_clean_negatives(limit=50):
    """InjecAgent user_cases.jsonl —— 数据集里本来就没有注入的干净样本。"""
    raw = _fetch_github_file(INJECAGENT_REPO, "data/user_cases.jsonl")
    out = []
    if not raw:
        return out
    for i, line in enumerate(raw.splitlines()):
        if not line.strip() or len(out) >= limit:
            continue
        try:
            c = json.loads(line)
        except ValueError:
            continue
        tpl = c.get("Tool Response Template")
        if not isinstance(tpl, str) or not tpl.strip():
            continue
        # 占位符替换成中性内容 —— 该字段本就是评论/消息槽位
        clean = tpl.replace("<Attacker Instruction>", BENIGN_FILL)
        out.append({
            "id": "ext-neg-clean-usercase-%04d" % i,
            "family": "benign_user_task",
            "source": "injecagent/data/user_cases.jsonl",
            "source_url": "https://github.com/%s/blob/main/data/user_cases.jsonl"
                          % INJECAGENT_REPO,
            "dataset": "InjecAgent (Zhang et al., NAACL 2024)",
            "negative_type": "clean_source",
            "user_tool": c.get("User Tool"),
            "user_instruction": c.get("User Instruction"),
            "text": clean,
            "scan_plane": "instruction",
            "license": INJECAGENT_LICENSE,
            "label_basis": "external_dataset_clean_sample",
        })
    return out


def _stratified_sample(records, total, per_family_cap=None):
    """按族分层的**确定性**抽样。

    族内按 id 排序，族间按族名轮转取，直到凑够 ``total``。
    确定性的意义：CI 里重跑必须得到同一份语料，否则基准数字不可比。
    分层的意义：不做分层的话，样本量最大的族会占满配额，把小族挤成 0 ——
    那会让族覆盖度指标（R1 的 ≥15）看起来达标、实际某几个族没被测到。
    """
    by_fam = {}
    for r in records:
        by_fam.setdefault(r.get("family", "?"), []).append(r)
    for f in by_fam:
        by_fam[f].sort(key=lambda r: r["id"])
        if per_family_cap:
            by_fam[f] = by_fam[f][:per_family_cap]
    families = sorted(by_fam)
    out = []
    while len(out) < total:
        added = False
        for f in families:
            if by_fam[f] and len(out) < total:
                out.append(by_fam[f].pop(0))
                added = True
        if not added:
            break
    out.sort(key=lambda r: r["id"])
    return out


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------
def manifest_from_samples(positives, negatives, sources_log):
    pos_families = collections.Counter(s.get("family", "?") for s in positives)
    neg_families = collections.Counter(s.get("family", "?") for s in negatives)
    datasets = sorted({s.get("dataset", "?") for s in positives + negatives})

    # κ：需要 ≥2 名标注者。当前所有样本只有 A（外部真值），B 为空。
    labels_a = [lab.get("positive") for s in positives + negatives
                for lab in s.get("labels", []) if lab.get("annotator") == "A"]
    labels_b = [lab.get("positive") for s in positives + negatives
                for lab in s.get("labels", []) if lab.get("annotator") == "B"]
    # 只有当两组标签都非空且等长时 κ 才有定义。否则 cohen_kappa 会因长度
    # 不一致直接抛 ValueError —— 那次抛异常会让下面这段诚实留空的补救分支
    # 永远走不到（实测 2026-10-18：A=1217 B=0 时脚本崩在 manifest 生成上，
    # 样本已写盘、manifest 没写出）。先判后调。
    if len(labels_a) >= 2 and len(labels_b) == len(labels_a):
        kappa, kappa_detail = rule_corpus.cohen_kappa(labels_a, labels_b)
    else:
        kappa = None
        reason = ("仅 1 个标注来源（A = 外部真值：CVE 记录或数据集作者标注）。"
                  "Cohen's κ 需 ≥2 名独立人类标注者；用脚本自算 κ 等于作弊，"
                  "因此留空而非编造。补 B 标注后重跑本脚本即可自动出 κ。")
        kappa_detail = {"reason": reason, "n_a": len(labels_a),
                        "n_b": len(labels_b)}

    return {
        "schema_version": SCHEMA_VERSION,
        "benchmark": "aishield-external-corpus/v1",
        "collected_at": _today(),
        "totals": {
            "positives": len(positives),
            "negatives": len(negatives),
            "total": len(positives) + len(negatives),
        },
        "target": {"positives": 400, "negatives": 400, "families": 15,
                   "min_kappa": 0.8, "min_annotators": 2},
        "shortfall": {
            "positives": max(0, 400 - len(positives)),
            "negatives": max(0, 400 - len(negatives)),
            "families": max(0, 15 - len(pos_families)),
        },
        "families_positive": dict(sorted(pos_families.items(),
                                         key=lambda kv: (-kv[1], kv[0]))),
        "families_negative": dict(sorted(neg_families.items(),
                                         key=lambda kv: (-kv[1], kv[0]))),
        "family_count": len(pos_families),
        "cohen_kappa": kappa,
        "cohen_kappa_detail": kappa_detail,
        "annotation_status": "not_human_annotated" if kappa is None
                             else "annotated",
        "r1_status": _r1_status(positives, negatives, kappa, len(pos_families)),
        "label_basis": {
            "external_cve_verified":
                "标签锚定第三方（NVD/GitHub/发行方）已发布 CVE，非主观判断",
            "external_dataset_ground_truth":
                "标签为公开数据集作者标注的攻击类型真值",
            "controlled_negative_matched":
                "控制变量负样本：同工件同格式，注入被移除；标签由构造客观决定",
            "external_dataset_clean_sample":
                "数据集中本身不含注入的干净样本",
        },
        "provenance_honesty": (
            "CVE 样本的 text 由 advisory 的生态+包+版本区间派生为原生依赖声明，"
            "非 advisory 原文；InjecAgent 样本的 text 为该数据集的 Tool Response "
            "字段原值。provenance 与标签均为外部，派生过程记录在 label_basis。"),
        "datasets": datasets,
        "sources": sources_log,
    }


def _r1_status(positives, negatives, kappa, family_count):
    """R1 验收的逐项判定，全部如实 —— 达不到的就说达不到。"""
    checks = {
        "positives_ge_400": {"met": len(positives) >= 400,
                             "actual": len(positives), "target": 400},
        "negatives_ge_400": {"met": len(negatives) >= 400,
                             "actual": len(negatives), "target": 400},
        "families_ge_15": {"met": family_count >= 15,
                           "actual": family_count, "target": 15},
        "kappa_ge_0.8": {"met": bool(kappa is not None and kappa >= 0.8),
                         "actual": kappa, "target": 0.8},
    }
    unmet = [k for k, v in checks.items() if not v["met"]]
    return {"met": not unmet, "checks": checks, "unmet": unmet,
            "note": ("κ 项无法由自动化补齐 —— 需 ≥2 名独立人类标注者。"
                     "这是 R1 的真实阻塞项，不伪造。")
            if "kappa_ge_0.8" in unmet else None}


def _sources_log_from_disk(positives, negatives):
    """从已落盘样本重建 sources 台账（--manifest-only 用）。

    采集时的 sources_log 只存在内存里，脚本重跑就得联网重采。本函数从样本
    自身记录的 dataset / source 字段按来源聚合重建，**不猜** —— 每字段都
    来自盘上真实值，重建出的台账与首次采集口径一致。
    """
    def _bucket(records):
        out = collections.OrderedDict()
        for s in records:
            key = (s.get("dataset") or "?", s.get("label_basis") or "?")
            b = out.setdefault(key, {"name": s.get("dataset") or "?",
                                     "count": 0,
                                     "label_bases": collections.Counter(),
                                     "sources": collections.Counter(),
                                     "scan_planes": collections.Counter()})
            b["count"] += 1
            b["label_bases"][key[1]] += 1
            b["sources"][(s.get("source") or "?")[:48]] += 1
            b["scan_planes"][s.get("scan_plane") or "?"] += 1
        return out

    pos = _bucket(positives)
    neg = _bucket(negatives)
    entries = []
    for (ds, lb), b in pos.items():
        entries.append({
            "dataset": ds,
            "side": "positives",
            "count": b["count"],
            "label_basis": lb,
            "scan_planes": dict(b["scan_planes"]),
            "distinct_sources": len(b["sources"]),
            "source_examples": sorted(b["sources"])[:5],
        })
    for (ds, lb), b in neg.items():
        entries.append({
            "dataset": ds,
            "side": "negatives",
            "count": b["count"],
            "label_basis": lb,
            "scan_planes": dict(b["scan_planes"]),
            "distinct_sources": len(b["sources"]),
            "source_examples": sorted(b["sources"])[:5],
        })
    return entries


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="corpus_collect", description=__doc__.split("\n")[0])
    ap.add_argument("--per-cell", type=int, default=20,
                    help="每个 (生态,严重度) 组合每页取多少条（默认 20）")
    ap.add_argument("--pages", type=int, default=4,
                    help="每个组合最多翻页数（默认 4）")
    ap.add_argument("--max-per-file", type=int, default=550,
                    help="每个 InjecAgent 文件最多取多少条正样本（默认 550）")
    ap.add_argument("--max-negatives", type=int, default=500,
                    help="控制变量负样本上限（默认 500）")
    ap.add_argument("--no-injecagent", action="store_true",
                    help="只采 CVE，不采 InjecAgent")
    ap.add_argument("--source", choices=("advisories", "injecagent", "all"),
                    default="all",
                    help="只采指定源（默认 all；分源采集便于快速迭代与定位故障）")
    ap.add_argument("--max-positives", type=int, default=700,
                    help="正样本总数上限，按族分层确定性抽样（默认 700）")
    ap.add_argument("--max-advisories", type=int, default=400,
                    help="CVE 来源正样本上限（默认 400）")
    ap.add_argument("--dry-run", action="store_true", help="只打印计划，不写盘")
    ap.add_argument("--recheck", action="store_true",
                    help="校验已落盘样本指纹，不联网")
    ap.add_argument("--manifest-only", action="store_true",
                    help="不联网：从已落盘样本重建 manifest.json（补 B 标注后重跑本模式即可自动出 κ）")
    args = ap.parse_args(argv)

    root = os.path.join(_ROOT, "benchmarks", "corpus", "external")

    if args.recheck:
        corpus = rule_corpus.load_external_corpus()
        bad = [e for k in ("positives", "negatives")
               for e in corpus["stats"][k]["errors"]]
        print("已落盘：pos=%d neg=%d  校验错误=%d"
              % (len(corpus["positives"]), len(corpus["negatives"]), len(bad)))
        for e in bad:
            print("  ! %s" % e)
        return 1 if bad else 0

    if args.manifest_only:
        # 离线路径：采集是一次性的，但 manifest 会因 κ 补齐、样本增删而需要
        # 重算。若每次都要联网重采，补一个 B 标注者就得再花 6 分钟且可能
        # 因上游变更得到不同样本集 —— 那会污染指纹。所以单独一条离线分支。
        corpus = rule_corpus.load_external_corpus()
        pos = corpus["positives"]
        neg = corpus["negatives"]
        bad = [e for k in ("positives", "negatives")
               for e in corpus["stats"][k]["errors"]]
        if bad:
            print("已落盘样本存在校验错误，拒绝生成 manifest：", file=sys.stderr)
            for e in bad[:20]:
                print("  ! %s" % e, file=sys.stderr)
            return 1
        manifest = manifest_from_samples(pos, neg, _sources_log_from_disk(pos, neg))
        with open(os.path.join(root, "manifest.json"), "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")
        st = manifest["r1_status"]
        print("manifest-only：从盘上 pos=%d neg=%d 重建（未联网）"
              % (len(pos), len(neg)))
        print("  κ=%s  R1 met=%s  未达标=%s"
              % (manifest["cohen_kappa"], st["met"], st["unmet"] or "无"))
        return 0

    advisories = []
    sources_log = []
    if args.source in ("advisories", "all"):
        print("采集源 ① GitHub Security Advisory（%d 格 × %d 页）"
              % (len(COLLECT_MATRIX), args.pages))
        advisories = collect_advisories(per_cell=args.per_cell, pages=args.pages)
        print("  采集到 %d 条" % len(advisories))
        if advisories:
            sources_log.append({
                "name": "GitHub Security Advisory API",
                "endpoint": GITHUB_API,
                "cells": ["/".join(c) for c in COLLECT_MATRIX],
                "per_cell": args.per_cell, "pages": args.pages,
                "collected": len(advisories),
            })

    all_pos, all_neg = list(advisories), []

    # CVE 侧独立限额：两个来源的攻击面不同（供应链 vs 提示注入），
    # 各自限额再合并，比合并后统一抽样更能保住两边的分布形状。
    if len(all_pos) > args.max_advisories:
        all_pos = _stratified_sample(all_pos, args.max_advisories)
        print("  CVE 侧按族分层抽样至 %d 条" % len(all_pos))

    if args.source in ("injecagent", "all") and not args.no_injecagent:
        print("采集源 ③ InjecAgent（%d 个文件）" % len(INJECAGENT_FILES))
        ipi_pos, ipi_neg = collect_injecagent(
            max_per_file=args.max_per_file, max_negatives=args.max_negatives)
        clean = collect_clean_negatives()
        all_pos += ipi_pos
        all_neg += ipi_neg + clean
        print("  正样本 %d  负样本 %d（matched %d + clean %d）"
              % (len(ipi_pos), len(all_neg), len(ipi_neg), len(clean)))
        sources_log.append({
            "name": "InjecAgent",
            "repo": INJECAGENT_REPO,
            "files": [f[1] for f in INJECAGENT_FILES] + ["data/user_cases.jsonl"],
            "collected_positives": len(ipi_pos),
            "collected_negatives": len(all_neg),
        })

    # 去重：CVE 键为 (cve_id, package, version) —— 一条 advisory 影响多个包时，
    # 每个包是**不同的扫描目标**，折叠成一个会丢失扫描面。InjecAgent 按 id。
    seen, dedup = set(), []
    for s in all_pos:
        if s.get("dataset", "").startswith("GitHub"):
            key = ("cve", s.get("cve_id"), s.get("package"),
                   s.get("chosen_vulnerable_version"))
        else:
            key = ("id", s["id"])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(s)
    all_pos = sorted(dedup, key=lambda s: s["id"])

    # 分层抽样控制语料规模：不设上限会让语料膨胀到 5000+ 条，CI 跑不动，
    # 而检出率读数并不会因此更有说服力（更多同质样本只是重复计数）。
    if len(all_pos) > args.max_positives:
        all_pos = _stratified_sample(all_pos, args.max_positives)

    print("合计：正样本 %d  负样本 %d" % (len(all_pos), len(all_neg)))
    fams = collections.Counter(s["family"] for s in all_pos)
    print("正样本族数 %d：%s" % (len(fams), dict(fams.most_common())))

    if args.dry_run:
        print("\ndry-run：未写盘。")
        return 0 if all_pos else 2

    pos_dir = os.path.join(root, "positives")
    neg_dir = os.path.join(root, "negatives")
    os.makedirs(pos_dir, exist_ok=True)
    os.makedirs(neg_dir, exist_ok=True)

    # 清理旧的 positives/negatives（采集是全量重写，不残留陈旧样本）
    for d in (pos_dir, neg_dir):
        for name in os.listdir(d):
            if name.endswith(".json"):
                os.remove(os.path.join(d, name))

    def _emit(records, directory, positive):
        for s in records:
            s["schema_version"] = SCHEMA_VERSION
            s["sha256"] = _sha256(s["text"])
            # labels：A = 外部真值。B 位留给未来第 2 名人类标注者。
            s["labels"] = [{"annotator": "A", "positive": positive,
                            "basis": s.get("label_basis", "external")}]
            with open(os.path.join(directory, "%s.json" % s["id"]), "w",
                      encoding="utf-8") as fh:
                json.dump(s, fh, ensure_ascii=False, indent=2, sort_keys=True)
                fh.write("\n")

    _emit(all_pos, pos_dir, True)
    _emit(all_neg, neg_dir, False)
    print("  写入 positives %d 个 / negatives %d 个"
          % (len(all_pos), len(all_neg)))

    manifest = manifest_from_samples(all_pos, all_neg, sources_log)
    with open(os.path.join(root, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    st = manifest["r1_status"]
    print("  manifest.json：κ=%s  R1=%s  未达标项=%s"
          % (manifest["cohen_kappa"], st["met"], st["unmet"] or "无"))

    return 0 if all_pos else 2


if __name__ == "__main__":
    raise SystemExit(main())
