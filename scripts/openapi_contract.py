#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""openapi_contract.py —— API 契约与运行时路由的一致性门禁（漂移式）。

背景（2026-10-03 一手实测，不是推测）
──────────────────────────────────────
进程内直调 ``api.server.AIShieldHandler.do_GET/do_POST`` 逐个探 API 运行时
路由，再拿**服务器自己发布的 /openapi.json** 做双向 diff：

  unknown  —— 实现了但契约里没有：智能体按契约发现服务时会扑空（真正要害）
  phantom  —— 契约里写了但跑不通：文档与实现分家
  errors   —— 探针本身报错（异常/超时），必须暴露而不是吞掉

实测结果：**运行时命中 128 条路由，契约里只有 10 条 → 118 条对智能体不可发现**。
原因是 ``api/openapi_spec.py`` 是**手工维护**的 curated 清单（10 条），而路由
实现散在 api/server.py 的 if/startswith 长链 + 7 个 handler 模块里，两边从来
没有强制同步的机制 —— 加路由不会有人想起改 spec。

为什么不做"补齐式"（把 118 条手写进 spec）
──────────────────────────────────────────
把 118 条逐条写进 openapi 是机械活，而且要写 schema、示例、错误码 —— 那是
表面工作，写完第二天加第 119 条又回到原点。真正要害只有一条：**以后每加一条
路由，契约必须跟着走**。所以这里沿用 ``rule_count_gate`` 的存量基线套路
（``drifted_files()`` + ``HISTORICAL_ALLOWLIST``）：基线里已有的（那 118 条）
不报错，基线**之外**新出现一条就算漂移，CI 直接红。补齐存量留给逐次迭代，
让智能体逐步可见；门禁只负责"不许再烂下去"。

为什么探针必须 hermetic（血泪）
──────────────────────────────
探针会真的打到 ``/api/v1/fleet/ingest`` 这类**写状态**的端点。2026-10-03 第
一版探针（走 HTTP）就是这么往 ``data/fleet.json`` 里塞了一条
``anon-2026-10-03T16:40:46`` 成员的 —— 已定位、备份在仓外、并已清掉。所以本
脚本探针前快照状态根、探针后**逐字节还原**，并把"被探针碰过的文件"报出来；
还原不成功（文件被删/内容对不上）即失败，绝不静默放过。

!!! 别在同一个进程里跑两次 diff() !!!
────────────────────────────────────
探针会真的写状态（fleet ingest 会塞一条新成员），还原只覆盖已有文件；第二次
diff 看到的是被第一次探针改过的数据，implemented 会从 110 漂到 123 —— 一个
"跑两遍结果不一样"的门禁比没有门禁更糟（它会让人以为在漂移，然后瞎改）。
所以：一条命令只做一次 diff，测试一律走子进程（见 tests/test_openapi_contract.py）。

用法
────
  python scripts/openapi_contract.py --check          # 漂移式校验（CI 用）
  python scripts/openapi_contract.py --json           # 机器出口
  python scripts/openapi_contract.py --update-baseline
  python scripts/openapi_contract.py --no-probe       # 只做静态提取 + diff
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import sys
from email.message import Message
from typing import Any, Dict, List, Set, Tuple

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

BASELINE = os.path.join(REPO, "scripts", "openapi_contract_baseline.json")

# 探针会碰到的状态根（历史上的敏感位置：data/ 已被 hermetic guard 盯过）
# ``api/data`` 是身份注册表（agents.json / registration_tokens.json / identity_events.jsonl）
# 的落盘位置 —— DELETE 探针一旦真跑进注销分支就会改写它。不快照这一根，探针就有
# 正当理由污染身份数据（"探针绿的"和"生产身份被写脏了"可以同时成立，这是最坏的一种绿）。
STATE_ROOTS = ("data", ".state", "state", "var", "api/data")

# ── 各 handler 的"路由不存在"措辞（抓全了才不会把 miss 误判成 hit） ──────────
# server.py 兜底：do_GET / do_POST 收尾都是 {"error": "Not found"}, 404
# ecosystem_api：  unknown ecosystem endpoint
# ecosystem_support_api：unknown endpoint: ...
# connectors_api： unknown GET/POST route: ...
# trust_api：      unknown trust endpoint   ← 限定词可能夹在中间，所以允许 0~3 个词
# 收不全会把"未命中"当成"已实现"（实测 POST /api/v1/trust/score 就是这么被
# 误判成命中的），属于假绿，必须泛化。
_UNKNOWN = r"unknown\s+(?:\w+\s+){0,3}(?:route|endpoint|path)"
_MISS_RE = re.compile(
    rf"{_UNKNOWN}|"
    r'"error"\s*:\s*"Not found"|"not found"|未知(?:路由|接口)',
    re.I,
)
_MISS_WITH_NON404 = re.compile(_UNKNOWN, re.I)

# DELETE 也在列：身份注销是 DELETE /api/v1/identity/agents/{did}。不探 DELETE 就
# 等于默认"这个动词永远不存在"，注销这种破坏性端点会一路绕过契约与门禁（写在了
# 代码里、没写在契约里、也没人拦）。资源不存在的 404 仍是 miss（_is_miss 正确
# 判定），所以探到的多是 501/404，不是"少登记"。
_VERBS = ("GET", "POST", "DELETE")


# ════════════════════════════════════════════════════════════════════════════
# 1. 静态提取候选路由
# ════════════════════════════════════════════════════════════════════════════

def iter_route_candidates() -> List[str]:
    """从 api/**/*.py 里抽出所有 /api/v1/... 字面量（不含 openapi_spec.py 自身）。

    这是**超集**：文档字符串、错误信息里提到的路径也会进来，靠后面的运行时探
    针把它们洗掉 —— 宁可多收，不可漏收。
    """
    out: Set[str] = set()
    for root, dirs, files in os.walk(os.path.join(REPO, "api")):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", "static")]
        for fn in files:
            if not fn.endswith(".py") or fn == "openapi_spec.py":
                continue
            p = os.path.join(root, fn)
            try:
                with open(p, encoding="utf-8") as f:
                    src = f.read()
            except OSError:
                continue
            for m in re.finditer(r'["\'](/api/v1/[A-Za-z0-9\-_/{}.*]*)["\']', src):
                lit = m.group(1)
                if lit.endswith("/"):
                    continue
                out.add(lit)
    return sorted(out)


# ════════════════════════════════════════════════════════════════════════════
# 2. 运行时探针（进程内直调，带状态快照/还原）
# ════════════════════════════════════════════════════════════════════════════

def _state_files() -> Dict[str, bytes]:
    """快照状态根下所有文件的字节。"""
    snap: Dict[str, bytes] = {}
    for rel in STATE_ROOTS:
        d = os.path.join(REPO, rel)
        if not os.path.isdir(d):
            continue
        for root, dirs, files in os.walk(d):
            dirs[:] = [x for x in dirs if x not in ("__pycache__",)]
            for fn in files:
                p = os.path.join(root, fn)
                try:
                    with open(p, "rb") as f:
                        snap[p] = f.read()
                except OSError:
                    continue
    return snap


def _restore_state(snap: Dict[str, bytes]) -> Tuple[List[str], List[str]]:
    """还原快照：改过的写回，**探针新建的删掉**。

    只删"快照里根本不存在"的文件，所以不会误伤仓库既有数据；但这一段不能省 ——
    2026-10-03 CI 上就栽在这：干净 checkout 里 ``data/fleet.json`` 原本不存在，
    探针 POST /api/v1/fleet/ingest 给它造了一条 ``anon-*`` 成员，而只做"写回"
    的还原对这种新文件束手无束，于是探针污染一路留到了套件结束（CI 的 test job
    红在 test_fleet_file_has_no_probe_artifact）。
    """
    fixed: List[str] = []
    failed: List[str] = []
    for p, blob in snap.items():
        try:
            if not os.path.exists(p):
                with open(p, "wb") as f:
                    f.write(blob)
                fixed.append(p)
                continue
            with open(p, "rb") as f:
                if f.read() != blob:
                    with open(p, "wb") as f:
                        f.write(blob)
                    fixed.append(p)
        except OSError as e:  # noqa: BLE001
            failed.append(f"{p}: {e}")
    for p in _state_files():
        if p in snap:
            continue
        try:
            os.remove(p)
            fixed.append(f"(已删除探针新建) {p}")
        except OSError as e:  # noqa: BLE001
            failed.append(f"{p}: {e}")
    return fixed, failed


@contextlib.contextmanager
def _library_quiet():
    """把库级 import 噪音（eco.proxy_gateway 的启动横幅）从 stdout 挪走。

    不隔离的话 `--json` 出口前面会混进 "[ProxyGateway] 已加载 0 个已认证工具"，
    机器解析直接炸 —— 而这恰好是"门禁自己写坏了"的典型：跑得绿但不给机器用。
    """
    real = sys.stdout
    sys.stdout = sys.stderr
    try:
        yield
    finally:
        sys.stdout = real


def _probe_one(path: str, verb: str) -> Tuple[int, str]:
    """进程内直调一次路由，返回 (status_code, body)。"""
    with _library_quiet():
        from api.server import AIShieldHandler

    body = b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}' if verb == "POST" else b""
    status = 0
    buf = io.BytesIO()

    h = object.__new__(AIShieldHandler)
    h.rfile = io.BytesIO(body)
    w = io.BytesIO()
    h.wfile = w
    h.client_address = ("127.0.0.1", 5555)
    h.command = verb
    h.request_method = verb
    h.path = path
    h.requestline = f"{verb} {path} HTTP/1.1"
    h.request_version = "HTTP/1.1"
    h.server_version = "AIShield"
    h.system_version = ""
    h.protocol_version = "HTTP/1.1"
    msg = Message()
    msg["Host"] = "127.0.0.1"
    msg["Content-Length"] = str(len(body))
    msg["Content-Type"] = "application/json"
    h.headers = msg

    # 429 之类的限流会干扰分类，探针自持一份"免打扰"标记不生效就照实报
    _handler_for = {"GET": "do_GET", "POST": "do_POST",
                    "DELETE": "do_DELETE"}.get(verb, "do_GET")
    try:
        getattr(h, _handler_for)()
    except Exception as e:  # noqa: BLE001
        return -1, repr(e)

    # 注意：wfile 里是"整段报文"（状态行 + 头 + 空行 + JSON 体）。
    # 2026-10-03 第一版忘了剥头部，于是 `_is_miss` 的 "not found" 命中的是状态行
    # 里的 "404 Not Found" —— 把 128 条真路由全部误判成"未实现"，门禁一跑就假红
    # （假绿的反面：这是假红，但同样不可接受，因为它会逼人去"修"根本没坏的东西）。
    txt = w.getvalue().decode("utf-8", "replace")
    head, _, payload = txt.partition("\r\n\r\n")
    m = re.search(r"HTTP/1\.1\s+(\d{3})", head)
    status = int(m.group(1)) if m else 0
    return status, payload


def _is_miss(status: int, body: str) -> bool:
    """判定这次响应是"路由不存在"还是"真的跑进处理分支了"。"""
    if _MISS_RE.search(body) and (status == 404 or _MISS_WITH_NON404.search(body)):
        return True
    return bool(_MISS_WITH_NON404.search(body)) and status == 404


# 405（方法不允许）/ 501（未实现）：方法本身选错了，不代表路径不存在
_UNSUPPORTED = (405, 501)


def _is_hit(status: int, body: str) -> bool:
    """"这条 (verb, path) 是真实实现"的统一判定 —— 门禁与生成器必须共用它。

    2026-10-03 踩过：两边各写了一份，生成器把 **所有 404 都排除**，门禁却把
    "404 且没命中未命中措辞"算命中，于是 4 条（如 GET /api/v1/platforms/recommend，
    返回 ``{"error": "platform 不存在", "error_code": "NOT_FOUND"}``）被门禁记为
    已实现、被生成器漏登记 —— 同一套探针两种口径，差集永远对不上，门禁一开就
    天天假红。

    判据（与代理层一致）：404 且响应里没有"路由不存在"措辞 = **路由匹配了但
    资源不存在**（比如查一个不存在的平台），这恰恰证明路由是真的；只有 405/501
    才说明方法选错。
    """
    if status in _UNSUPPORTED:
        return False
    return not _is_miss(status, body)


# ════════════════════════════════════════════════════════════════════════════
# 2b. 可复用探针 API（scripts/gen_openapi_spec.py 直接 import 这一层）
# ────────────────────────────────────────────────────────────────────────────
# 门禁只是"算缺口"，要修根还得有东西去**生成**契约。生成器不该再写一套会写状态
# 的探针（历史上就是这么把 data/fleet.json 写脏的），所以这里把能力摊成可复用
# 的模块级 API：hermetic_state / probe / runtime_path_records / schema_from_sample。
# ════════════════════════════════════════════════════════════════════════════

LAST_STATE_REPORT: Dict[str, Any] = {}


@contextlib.contextmanager
def hermetic_state() -> Any:
    """探针 hermetic 上下文：进时快照状态根，出时逐字节还原（连新建文件也删）。

    生成器每次 import 都会跑一遍探针，所以这个上下文必须能反复用 —— 不能靠
    "记得调还原函数"这种口头约定（2026-10-03 第一版探针就是漏了它才污染仓库，
    而且是在 CI 上才炸出来的）。
    """
    snap = _state_files()
    report: Dict[str, Any] = {"created": [], "restored": [], "failed": []}
    LAST_STATE_REPORT.clear()
    LAST_STATE_REPORT.update(report)
    try:
        yield report
    finally:
        fixed, failed = _restore_state(snap)
        report["restored"] = fixed
        report["failed"] = failed
        for p in _state_files():
            if p not in snap:
                report["created"].append(p)
        LAST_STATE_REPORT.clear()
        LAST_STATE_REPORT.update(report)


def probe(path: str, verb: str) -> Dict[str, Any]:
    """探一条路由，返回结构化结果（生成器消费的量裁接口）。

    永远不抛：路由实现炸了要被当成"探针异常"报出来，而不是让生成脚本悄悄断在
    半途、产出一个只有半份路由的契约 —— 那等于用漏报换来的绿。
    """
    try:
        status, body = _probe_one(path, verb)
    except Exception as e:  # noqa: BLE001
        return {"verb": verb, "path": path, "status": -1, "error": repr(e), "miss": True}
    return {
        "verb": verb,
        "path": path,
        "status": status,
        "body": body[:4096],
        "miss": _is_miss(status, body),
        "error": "",
    }


# 路由分派表：顺序 = server.py do_GET/do_POST 里的 if 链顺序，命中最先匹配的前缀。
# 表里没有的走 tag_for_path 的兜底分支，宁可打个杂 tag 也别漏登记。
_DISPATCH = (
    (("/api/v1/trust", "/api/v1/registry"), "trust", "Trust API 认证与信任评分"),
    (("/api/v1/ecosystem", "/api/v1/agent-card", "/api/v1/specialist", "/api/v1/chain",
      "/api/v1/identity", "/api/v1/protocol", "/api/v1/leaderboard", "/api/v1/contributors",
      "/api/v1/sandbox/backend"), "ecosystem", "Agent 生态 API"),
    (("/api/v1/personal-agents", "/api/v1/platforms"), "personal-agent", "个人 Agent 治理层与平台注册表"),
    (("/api/v1/connectors", "/api/v1/agent-infra"), "connectors", "海外平台接入与 Agent 基础设施扫描"),
    (("/api/v1/eco-support",), "eco-support", "Agent 生态支持体系：记忆扫描/策略包/红队探针/晋升/衰减"),
)


def tag_for_path(path: str) -> str:
    """给运行时路径定 OpenAPI tag（跟 server.py 的分派前缀对齐）。"""
    for prefixes, tag, _ in _DISPATCH:
        if any(path.startswith(p) for p in prefixes):
            return tag
    seg = path.strip("/").split("/")
    if len(seg) > 2:
        return seg[2] if seg[0] == "api" and seg[1] == "v1" and len(seg) > 2 else seg[0]
    return seg[0] if seg else "default"


def summary_for_path(path: str, verb: str) -> str:
    """操作摘要。

    摘要是给人看的元数据，不是要害 —— 要害是"这条路径到底存在不存在"（那个由
    探针自动判定）。所以这里允许用前缀表兜底，取不到就拼段落，绝不因为凑不出
    漂亮文案就跳过登记。
    """
    for prefixes, _tag, desc in _DISPATCH:
        if any(path.startswith(p) for p in prefixes):
            tail = path.strip("/").split("/")[-1] or desc
            return f"{desc} · {tail}"
    return f"{verb} {path}（运行时探得；schema 由真实响应推导）"


def schema_from_sample(sample: Any, max_depth: int = 3) -> Dict[str, Any]:
    """从**真实响应样本**推最小 JSON Schema（不手写、不臆造字段）。

    深度截断是必要的：agent-card 之类的响应里嵌着整棵树，全量铺开会得到一份
    没人看得完的 spec，反而把真正要害的端点淹掉。
    """
    if max_depth <= 0:
        return {"type": "object"}
    if isinstance(sample, dict):
        props: Dict[str, Any] = {}
        for k, v in list(sample.items())[:24]:
            props[k] = schema_from_sample(v, max_depth - 1)
        return {"type": "object", "properties": props,
                "additionalProperties": True}
    if isinstance(sample, list):
        return {"type": "array",
                "items": schema_from_sample(sample[0] if sample else {}, max_depth - 1)}
    if isinstance(sample, bool):
        return {"type": "boolean"}
    if isinstance(sample, int):
        return {"type": "integer"}
    if isinstance(sample, float):
        return {"type": "number"}
    if isinstance(sample, str):
        return {"type": "string"}
    if sample is None:
        return {"type": "null"}
    return {}


def runtime_path_records(do_probe: bool = True) -> Tuple[List[Dict[str, Any]],
                                                         List[Tuple[str, str, str]],
                                                         Dict[str, Any]]:
    """运行时命中的路由**全量记录**（不只是 (verb, path) 二元组）。

    返回 (records, errors, state_report)。records 每项::

        {"verb": "GET", "path": "...", "tag": "...", "summary": "...",
         "status": 200, "sample": {...}, "sample_truncated": bool}

    ``sample`` 是响应体原样的裁剪版 —— schema 一律从它推导，绝不凭空编字段。
    """
    records: List[Dict[str, Any]] = []
    errors: List[Tuple[str, str, str]] = []
    if not do_probe:
        return records, errors, {}
    with hermetic_state() as rep:
        for path in iter_route_candidates():
            for verb in _VERBS:
                r = probe(path, verb)
                if r["status"] == -1 or r["error"]:
                    errors.append(("probe", path, r["error"][:160]))
                    continue
                # 两个动词都探、都记：eco-support 这类模块 GET/POST 各挂一堆端点，
                # 探到一个就 break 会把另一半动词吞掉（2026-10-03 实测 109 路径只
                # 出 109 个操作，一下子少登记了几十条真实现）。判定口径一律走
                # _is_hit，别在这里另写一份条件。
                if not _is_hit(r["status"], r["body"]):
                    continue
                sample, truncated = _sample_of(r["body"])
                records.append({
                    "verb": verb,
                    "path": path,
                    "tag": tag_for_path(path),
                    "summary": summary_for_path(path, verb),
                    "status": r["status"],
                    "sample": sample,
                    "sample_truncated": truncated,
                })
    return records, errors, rep


def _sample_of(body: str, limit: int = 4000) -> Tuple[Any, bool]:
    """把响应体解析成样本；解析不了（纯文本/HTML）就报 None + 已裁剪标记。"""
    txt = (body or "").strip()
    if not txt or len(txt) > limit:
        return None, True
    try:
        return json.loads(txt), False
    except (ValueError, TypeError):
        return None, True


def runtime_routes(probe: bool = True) -> Tuple[
    List[Tuple[str, str]], List[Tuple[str, str, str]], List[str], List[str]
]:
    """运行时命中的 (verb, path)。

    返回四元组：(命中, 探针异常, 探针新建的状态文件, 探针还原过的状态文件)。
    后两项是"探针有没有污染仓库"的凭据 —— 探针污染过一次（2026-10-03 的 anon 成员），
    所以这里必须能自证清白。
    """
    hits: List[Tuple[str, str]] = []
    errors: List[Tuple[str, str, str]] = []
    created: List[str] = []
    restored: List[str] = []
    if not probe:
        return hits, errors, created, restored
    snap = _state_files()
    try:
        with _library_quiet():
            for path in iter_route_candidates():
                for verb in _VERBS:
                    try:
                        status, body = _probe_one(path, verb)
                    except Exception as e:  # noqa: BLE001
                        errors.append(("probe", path, repr(e)))
                        continue
                    if status == -1:
                        errors.append(("error", path, body[:120]))
                        continue
                    # 两个动词都记，不要 break：GET 命中就 break 会把同一路径的
                    # POST 吞掉（实测少记 10 条真实现 —— 门禁少报，假绿方向）。
                    if _is_hit(status, body):
                        hits.append((verb, path))
    finally:
        restored, failed = _restore_state(snap)
        restored += failed
        for p in _state_files():
            if p not in snap:
                created.append(p)
    return hits, errors, created, restored


# ════════════════════════════════════════════════════════════════════════════
# 3. 契约（取服务器自己发布的 /openapi.json，保证与实现同源）
# ════════════════════════════════════════════════════════════════════════════

def contract_routes() -> Set[Tuple[str, str]]:
    """从运行中的服务器拉取 /openapi.json，抽出 (verb, path)。"""
    with _library_quiet():
        status, body = _probe_one("/openapi.json", "GET")
    if status != 200:
        raise RuntimeError(f"无法取契约 /openapi.json: status={status} body={body[:200]}")
    spec = json.loads(body[body.find("{"):] if body.startswith("HTTP") else body)
    out: Set[Tuple[str, str]] = set()
    for p, methods in (spec.get("paths") or {}).items():
        # OpenAPI 的方法键是小写（get/post/...），不归一化的话契约侧永远数出 0
        for verb in methods:
            if verb.upper() in _VERBS:
                out.add((verb.upper(), p))
    return out


# ════════════════════════════════════════════════════════════════════════════
# 4. diff + 基线
# ════════════════════════════════════════════════════════════════════════════

MANIFEST = os.path.join(REPO, "api", "openapi_runtime_paths.json")


def manifest_routes() -> Set[Tuple[str, str]]:
    """读运行时清单 ``api/openapi_runtime_paths.json`` 的 (verb, path)。

    方法键**大小写归一**：清单里是小写 ``get/post``（OpenAPI 约定），运行时探针
    给的是大写 —— 不归一会得到"清单和运行时差 119 条"的假漂移，比没有门禁还糟。
    """
    if not os.path.exists(MANIFEST):
        return set()
    try:
        with open(MANIFEST, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return set()
    out: Set[Tuple[str, str]] = set()
    for r in (data or {}).get("routes", []):
        for o in r.get("operations", []):
            out.add((str(o.get("verb", "")).upper(), r["path"]))
    return out


def load_baseline() -> Set[Tuple[str, str]]:
    if not os.path.exists(BASELINE):
        return set()
    with open(BASELINE, encoding="utf-8") as f:
        data = json.load(f)
    return {(d["verb"], d["path"]) for d in data.get("routes", [])}


def save_baseline(routes: Set[Tuple[str, str]], note: str) -> None:
    payload = {
        "note": note,
        "generated_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        # 别直接 sorted(dict)：Py3.13 起 dict 之间不可比，会抛
        # "'<' not supported between instances of 'dict' and 'dict'"
        "routes": sorted(
            ({"verb": v, "path": p} for v, p in routes),
            key=lambda d: (d["verb"], d["path"]),
        ),
    }
    with open(BASELINE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def diff(probe: bool = True) -> Dict[str, Any]:
    hits, errors, state_created, state_restored = runtime_routes(probe=probe)
    implemented = set(hits)
    contract = contract_routes()
    manifest = manifest_routes()
    baseline = load_baseline()
    unknown_all = sorted(implemented - contract)
    phantom_all = sorted(contract - implemented)
    # 清单 vs 运行时：清单过期（加路由没重跑生成器）或清单残留（路由删了没重生成）
    manifest_missing = sorted(implemented - manifest)
    manifest_extra = sorted(manifest - implemented)
    return {
        "implemented_count": len(implemented),
        "contract_count": len(contract),
        "manifest_count": len(manifest),
        "baseline_count": len(baseline),
        "unknown": unknown_all,          # 实现了但没在契约里
        "phantom": phantom_all,          # 契约里有但跑不通
        "unknown_new": sorted(set(unknown_all) - baseline),
        "phantom_new": sorted(set(phantom_all) - baseline),
        "manifest_missing": manifest_missing,   # 运行时有、清单没有 → 生成器没重跑
        "manifest_extra": manifest_extra,       # 清单里有、运行时没了 → 清单陈旧
        "probe_errors": errors,
        "unknown_baselined": len(unknown_all) - len(set(unknown_all) - baseline),
        "state_created": state_created,
        "state_restored": state_restored,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="API 契约一致性门禁（漂移式）")
    ap.add_argument("--check", action="store_true", help="校验是否有新增漂移")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--update-baseline", action="store_true", help="把当前缺口写入基线")
    ap.add_argument("--no-probe", action="store_true", help="跳过运行时探针（只静态）")
    args = ap.parse_args()

    probe = not args.no_probe
    d = diff(probe=probe)

    if args.json:
        print(json.dumps(d, ensure_ascii=False, indent=2))
    elif args.update_baseline:
        save_baseline(set(d["unknown"]) | set(d["phantom"]),
                      "存量缺口基线（只拦新增；补齐靠逐次迭代）")
        print(f"基线已写入：{BASELINE}（{len(d['unknown']) + len(d['phantom'])} 条存量缺口）")
        return 0
    else:
        print("API 契约一致性检查（运行时路由 vs /openapi.json）")
        print("=" * 64)
        print(f"运行时命中路由：{d['implemented_count']}   契约路径：{d['contract_count']}"
              f"   基线存量：{d['baseline_count']}")
        print(f"实现了但契约缺失（存量）：{d['unknown_baselined']}  新增：{len(d['unknown_new'])}")
        print(f"契约有但跑不通（存量）：{len(set(d['phantom']) - set(d['phantom_new']))}"
              f"  新增：{len(d['phantom_new'])}")
        if d["probe_errors"]:
            print(f"探针异常：{len(d['probe_errors'])}")
            for e in d["probe_errors"][:10]:
                print("   ", e)
        print(f"探针污染自查：新建 {len(d['state_created'])} / 还原 {len(d['state_restored'])} 个状态文件")
        for p in d["state_created"][:5]:
            print("   新建:", p)
        for label, key in (("契约缺失（新增）", "unknown_new"), ("跑不通（新增）", "phantom_new")):
            rows = d[key]
            print(f"{label}：{len(rows)}")
            for r in rows[:20]:
                print("   ", r[0], r[1])
        print("=" * 64)

    if args.check:
        # 双向漂移，四个方向一个都不放行：
        #   unknown  —— 实现了没进契约（智能体按契约发现会扑空）
        #   phantom  —— 契约里写了跑不通（文档与实现分家），**一律零容忍**，不进基线
        #   manifest_missing / manifest_extra —— 运行时清单与实现不一致（生成器没重跑）
        blocks = [
            ("契约缺失", d["unknown_new"]),
            ("清单缺失（跑一遍 scripts/gen_openapi_spec.py）", d["manifest_missing"]),
            ("清单残留（路由已删除，重跑生成器）", d["manifest_extra"]),
        ]
        if d["phantom"]:
            blocks.append(("契约里有跑不通的路由", d["phantom"]))
        if d["probe_errors"]:
            blocks.append(("探针自身报错", [e[1] for e in d["probe_errors"]]))
        bad = any(rows for _label, rows in blocks)
        for label, rows in blocks:
            for r in rows[:20]:
                print(f"  FAIL[{label}] {r[0]} {r[1]}")
        if bad:
            print("FAIL：契约与运行时实现漂移 —— 契约必须是实现的投影，"
                  "新增路由要跑 scripts/gen_openapi_spec.py 并连清单一起入库")
            return 1
        print(f"OK：契约与运行时一致（实现 {d['implemented_count']} / "
              f"契约 {d['contract_count']} / 清单 {d['manifest_count']}，无 phantom）")
        return 0
    if args.json:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
