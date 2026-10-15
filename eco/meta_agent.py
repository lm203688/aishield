"""
eco/meta_agent.py — 有界元 agent（RSES 的草拟侧）
=================================================

解决的问题
----------
规则自进化循环里最危险的一环是"谁把候选变成线上规则"。此前的候选队列
（`scanner/_proposed/`）靠人工审阅，积压 40+ 条不动；而一旦把晋升权交给
自动化 agent，一次被污染的草稿会话就能把任意正则写进线上规则集 —— 扫描器
卖的是信任，误报规则比没有规则更糟。

本模块把元 agent 的能力边界钉在结构上：

    propose_rule   —— 从情报信号起草候选（写 _proposed/，账本记 draft）
    test_draft     —— 对留存集 + 自有仓库试跑，自触发须 0（账本记 test）
    submit_for_promotion —— 把"我认为可以晋升"作为提案交出（账本记 reflect）

**没有** promote / demote / rollback —— 不是忘了写，是刻意不存在。晋升只能
由人类经 `scripts/promote_rule.py`（六道闸门 + --approved-by）执行，账本层
（`eco/evolution_ledger.py`）再用 `meta:` actor 前缀挡一次。双保险。

自触发为什么必须为 0
--------------------
"留存集"（BENIGN_CORPUS）之外再加一层**自有仓库扫描**：本仓的 docs/、api/、
eco/、README 里满是防御性文档 —— 大篇在讲"我们检测 prompt injection / 工具
投毒 / piped download"。一条宽到会命中这些文档的 pattern，上线后会把我们
自己的发布物、用户的防御性 README 全扫成红色。rule_corpus.py 的引用语境样本
只覆盖了其中一类；自有仓库扫描覆盖的是**真实 shipped 面**。

自有仓库扫描的豁免（为什么可以豁免）：`scanner/`（规则定义）、`scripts/`
（语料与自动化）、`tests/`（攻击夹具）、`data/`（规则库与状态）里，攻击载荷
是合法居民 —— 拿草稿去打它们等于用定义当反例（自指误报）。豁免只保留 shipped
面，理由写死在 `_SELF_SCAN_SKIP_PATH_PARTS` 的注释里。

保守性声明
----------
元 agent 的判定是**第一遍草拟**，刻意保守（宁拒勿误）：benign 或自有仓库任一
命中即判 rejected。人类闸门（promote_rule.py 只查 BENIGN_CORPUS）可以放行
被元 agent 拒掉的风险候选 —— 层级关系是"元 agent 建议，人类裁决"。

语料取不到时 fail-closed：负控语料加载失败 → test_draft 判 rejected
（"无法验证零误报"），绝不静默跳过检查假装干净。

零第三方依赖；`from eco import evolution_ledger` 记账，路径可注入以便测试。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

from eco import evolution_ledger

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: 候选落点（与 scripts/promote_rule.py 的 PROPOSED_DIR 同一目录）。
PROPOSED_DIR = os.path.join(_BASE, "scanner", "_proposed")

#: 元 agent 的 actor 身份。前缀 `meta:` 即信任域标记 —— 账本对特权动作
#: 一律拒绝该前缀（见 evolution_ledger.PRIVILEGED_ACTIONS）。
META_ACTOR = "meta:rses-drafter-v1"

VALID_SEVERITIES = {"critical", "high", "medium", "low", "info"}

# 自有仓库扫描的覆盖面。比 scripts/rule_count_gate.py 的 TEXT_EXT 多一个
# `.py`：那个白名单服务的是"对外声明面"（门禁只扫被服务的资产），这里要扫
# 的是"会被规则打到的面" —— 本仓自己的源码正是误报的第一受害者。
_SELF_SCAN_EXTS = (".md", ".json", ".yaml", ".yml", ".html", ".htm", ".txt",
                   ".ts", ".xml", ".py")

_SELF_SCAN_SKIP_DIRS = frozenset({
    ".git", ".github", ".workbuddy", ".hypothesis", ".pytest_cache",
    "node_modules", "__pycache__", "dist", "build",
})

# 父目录名命中即跳过（任一层级）：
#   tests/    攻击夹具 —— 载荷作为测试数据的合法居所
#   data/     规则库与运行时状态（含 api/data/）
#   scanner/  规则引擎本体 —— pattern 字面量在这里是定义不是误报
#   scripts/  语料单一真源（rule_corpus.py）+ 自动化脚本
# 注意用**目录名分量**判定，不用 "/data/" 子串：顶层目录的路径没有前导分隔符
# （"data/x.md" 不含 "/data/"），子串判据会整个漏掉顶层豁免目录 —— 第一轮
# 实现就是这么漏的，被 test_default_self_scan_uses_the_real_repo 当场抓住。
_SELF_SCAN_SKIP_PARENT_NAMES = frozenset({"tests", "data", "scanner", "scripts"})

_SELF_SCAN_MAX_FILES = 4000
_SELF_SCAN_MAX_BYTES = 512 * 1024


# ---------------------------------------------------------------------------
# 可注入的默认实现
# ---------------------------------------------------------------------------
def _default_self_scan(pattern: str) -> list:
    """对自有仓库的 shipped 面跑草稿 pattern，返回命中列表。

    每个命中是 {"path": 相对路径, "match": 片段}。自触发（非空）= 这条规则
    会在我们自己的发布物上开火，正是误报的定义。
    """
    compiled = re.compile(pattern, re.IGNORECASE)
    hits = []
    scanned = 0
    for dirpath, dirnames, filenames in os.walk(_BASE):
        dirnames[:] = [d for d in dirnames
                       if d not in _SELF_SCAN_SKIP_DIRS
                       and d not in _SELF_SCAN_SKIP_PARENT_NAMES]
        for fn in sorted(filenames):
            if not fn.endswith(_SELF_SCAN_EXTS):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, _BASE)
            if any(p in _SELF_SCAN_SKIP_PARENT_NAMES
                   for p in rel.split(os.sep)[:-1]):
                continue
            try:
                if os.path.getsize(full) > _SELF_SCAN_MAX_BYTES:
                    continue
                with open(full, "r", encoding="utf-8", errors="replace") as f:
                    text = f.read()
            except OSError:
                continue
            scanned += 1
            m = compiled.search(text)
            if m:
                hits.append({"path": rel.replace(os.sep, "/"),
                             "match": m.group()[:80]})
            if scanned >= _SELF_SCAN_MAX_FILES:
                return hits
    return hits


def _load_corpus():
    """加载负控/正控语料（单一真源 scripts/rule_corpus.py）。

    返回 (benign, attack)；取不到时返回 (None, None) —— 调用方必须按
    "无法验证零误报"处理（fail-closed），不得当成空语料放行。
    """
    scripts_dir = os.path.join(_BASE, "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import rule_corpus
        return list(rule_corpus.BENIGN_CORPUS), list(rule_corpus.ATTACK_SAMPLES)
    except Exception:
        return None, None


def _default_known_patterns():
    """现网已激活的 pattern 集合（去重用）。取不到返回空集合。

    去重失败不是安全问题（promote_rule.py 的闸门会权威复核），但证据里要
    如实标注 "duplicate_check": "unavailable"，不留静默缺口。
    """
    pats = set()
    try:
        if _BASE not in sys.path:
            sys.path.insert(0, _BASE)
        from scanner import rules as scanner_rules
        pats |= set(getattr(scanner_rules, "ALL_RULES", {}) or {})
        radar_path = os.path.join(_BASE, "data", "radar_rules.json")
        if os.path.exists(radar_path):
            with open(radar_path, encoding="utf-8") as f:
                pats |= set((json.load(f) or {}).get("rules", {}) or {})
    except Exception:
        return set(), False
    return pats, True


# ---------------------------------------------------------------------------
# 起草期校验（promote_rule.validate 的逐条镜像，让候选"生来可晋升"）
# ---------------------------------------------------------------------------
def _validate_draft(pattern: str, description: str, severity: str) -> list:
    problems = []
    pattern = (pattern or "").strip()
    description = (description or "").strip()
    severity = (severity or "").strip().lower()
    if not pattern:
        problems.append("pattern is empty")
        return problems
    if len(pattern) < 6:
        problems.append("pattern suspiciously short (%d chars)" % len(pattern))
    try:
        compiled = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        problems.append("regex does not compile -- %s" % e)
        return problems
    if compiled.search("") or compiled.search("a"):
        problems.append("pattern matches empty/trivial input -- too broad")
    if not description or description.upper().startswith("TODO"):
        problems.append("description is empty or a TODO placeholder")
    if severity not in VALID_SEVERITIES:
        problems.append("severity %r not in %s" % (severity, sorted(VALID_SEVERITIES)))
    return problems


# ---------------------------------------------------------------------------
# 有界元 agent
# ---------------------------------------------------------------------------
class DraftingMetaAgent:
    """只起草、只自测、只提交审议。结构上不含任何晋升/降级/回滚能力。

    参数全部可注入（测试用临时目录/假扫描器/假账本路径）：
      actor            —— 账本 actor（默认 meta:rses-drafter-v1）
      proposals_dir    —— 候选落点
      ledger_path      —— 进化账本路径（None = 模块默认）
      self_scan_fn     —— 自有仓库扫描（默认真实扫描）
      corpus_fn        —— 语料加载（默认 scripts/rule_corpus.py）
      known_patterns_fn —— 现网 pattern 集合（默认真实加载）
    """

    #: 结构边界：这些名字在本类上不得存在（tests/test_evolution_ledger.py 钉死）。
    FORBIDDEN_METHODS = ("promote", "demote", "rollback", "promote_rule",
                         "promote_all", "_promote", "_demote", "_rollback",
                         "write_radar_rules", "edit_rules")

    def __init__(self, *, actor: str = META_ACTOR, proposals_dir: str | None = None,
                 ledger_path: str | None = None, self_scan_fn=None,
                 corpus_fn=None, known_patterns_fn=None):
        self.actor = actor
        self.proposals_dir = proposals_dir or PROPOSED_DIR
        self.ledger_path = ledger_path
        self._self_scan_fn = self_scan_fn or _default_self_scan
        self._corpus_fn = corpus_fn or _load_corpus
        self._known_patterns_fn = known_patterns_fn or _default_known_patterns

    # -- 账本 ---------------------------------------------------------------
    def _record(self, action: str, target: str, rationale: str = "",
                evidence: dict | None = None) -> dict:
        """元 agent 只发 draft/test/reflect —— 特权动作在账本层就会被拒。"""
        return evolution_ledger.record(
            actor=self.actor, action=action, target=target,
            rationale=rationale, evidence=evidence, path=self.ledger_path)

    # -- 草拟 ---------------------------------------------------------------
    def propose_rule(self, *, signal_id: str, signal_title: str, signal_url: str,
                     pattern: str, description: str, severity: str,
                     attack_category: str | None = None,
                     source: str = "meta-agent") -> dict:
        """把一条情报信号起草成候选文件（status=draft，待 test_draft）。

        起草期就执行 promote_rule 的逐条校验（可编译/不过宽/不太短/描述与
        严重级合法/不与现网重复）—— 让候选"生来可晋升"，而不是把垃圾倒进
        队列让人工收拾。校验不过 → ValueError（调用方写错了，必须响）。
        """
        problems = _validate_draft(pattern, description, severity)
        if problems:
            raise ValueError("draft rejected at authoring time: %s"
                             % "; ".join(problems))

        known, dedup_ok = self._known_patterns_fn()
        if pattern.strip() in known:
            raise ValueError("draft rejected: pattern already live "
                             "(duplicate) -- promoting it again is a no-op")

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        slug = re.sub(r"[^a-z0-9]+", "-", (signal_title or "").lower())
        slug = slug.strip("-")[:40] or "signal"
        digest = hashlib.sha256(
            (signal_id or signal_title or pattern).encode("utf-8")
        ).hexdigest()[:6]
        fname = "PROPOSED_%s_%s_%s.json" % (today, slug, digest)
        path = os.path.join(self.proposals_dir, fname)

        draft = {
            "status": "draft",
            "drafted_at": today,
            "drafted_by": self.actor,
            "signal": {"id": signal_id, "title": signal_title,
                       "url": signal_url, "source": source},
            "attack_category": attack_category or "unclassified",
            "severity": severity.strip().lower(),
            "rules": [{"pattern": pattern.strip(),
                       "description": description.strip(),
                       "severity": severity.strip().lower()}],
            "review_notes": "",
            "auto_ready": False,
        }
        os.makedirs(self.proposals_dir, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(draft, f, ensure_ascii=False, indent=2)

        self._record("draft", fname,
                     rationale="meta-agent drafted from signal %s" % signal_id,
                     evidence={"pattern": pattern.strip(),
                               "severity": severity.strip().lower(),
                               "signal_url": signal_url,
                               "duplicate_check": "ok" if dedup_ok
                               else "unavailable"})
        return {"draft_path": path, "draft": draft}

    # -- 自测 ---------------------------------------------------------------
    def test_draft(self, draft) -> dict:
        """对留存集 + 自有仓库试跑候选，零命中才置 ready。

        draft 是候选文件路径（propose_rule 的返回值带它）或文件名（相对
        proposals_dir）。返回 {verdict, reasons, benign_hits, self_hits,
        attack_hits, attack_samples, draft_path}。判定写回候选文件
        （status/meta_verified/review_notes/auto_ready）并记入账本。
        """
        path, data = self._resolve_draft(draft)
        rules = data.get("rules") or []
        if not rules:
            report = {"verdict": "rejected", "reasons": ["draft has no rules"],
                      "benign_hits": [], "self_hits": [], "attack_hits": 0,
                      "attack_samples": 0, "draft_path": path}
            return report

        benign, attack = self._corpus_fn()
        if benign is None:
            # 负控取不到 = 无法证明零误报 = fail-closed
            report = {"verdict": "rejected",
                      "reasons": ["negative control (BENIGN_CORPUS) "
                                  "unavailable -- refusing to certify"],
                      "benign_hits": [], "self_hits": [], "attack_hits": 0,
                      "attack_samples": 0, "draft_path": path}
            self._write_verdict(path, data, report)
            self._record("test", os.path.basename(path),
                         rationale="self-test refused: corpus unavailable",
                         evidence={"verdict": "rejected",
                                   "reasons": report["reasons"]})
            return report

        benign_hits, self_hits, reasons = [], [], []
        attack_hits = 0
        for r in rules:
            pattern = (r.get("pattern") or "").strip()
            if not pattern:
                reasons.append("empty pattern in rules[]")
                continue
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                reasons.append("regex does not compile -- %s" % e)
                continue
            for j, sample in enumerate(benign):
                m = compiled.search(sample)
                if m:
                    benign_hits.append({"rule": pattern, "sample": j,
                                        "match": m.group()[:80]})
                    break
            for h in (self._self_scan_fn(pattern) or []):
                self_hits.append(dict(h, rule=pattern))
            attack_hits += sum(1 for s in attack if compiled.search(s))

        if benign_hits:
            reasons.append("%d benign-corpus false positive(s)" % len(benign_hits))
        if self_hits:
            reasons.append("%d self-trigger(s) on the repo's shipped surface"
                           % len(self_hits))

        verdict = "rejected" if reasons else "ready"
        report = {
            "verdict": verdict,
            "reasons": reasons,
            "benign_hits": benign_hits,
            "self_hits": self_hits,
            "attack_hits": attack_hits,
            "attack_samples": len(attack),
            "draft_path": path,
        }
        self._write_verdict(path, data, report)
        self._record("test", os.path.basename(path),
                     rationale=("self-test %s: %s"
                                % (verdict, "; ".join(reasons)
                                   if reasons else "zero false positives")),
                     evidence={"verdict": verdict,
                               "benign_hits": len(benign_hits),
                               "self_hits": len(self_hits),
                               "attack_hits": attack_hits,
                               "attack_samples": len(attack)})
        return report

    # -- 提交审议 -----------------------------------------------------------
    def submit_for_promotion(self, draft) -> dict:
        """把 ready 候选作为"晋升提案"交出。不执行晋升，只记录 + 指路。

        只有 status==ready（test_draft 判过）才受理。返回的 promote_command
        就是人类要敲的那条 —— 提案与执行之间隔着 promote_rule.py 的六道闸门
        和 --approved-by。
        """
        path, data = self._resolve_draft(draft)
        fname = os.path.basename(path)
        if data.get("status") != "ready":
            return {"ok": False,
                    "reason": "draft %s is %r -- run test_draft first / fix "
                              "the false positives" % (fname, data.get("status")),
                    "draft_path": path}
        entry = self._record(
            "reflect", fname,
            rationale="meta-agent recommends promotion after zero-FP self-test",
            evidence={"meta_verified": data.get("meta_verified"),
                      "pattern": (data.get("rules") or [{}])[0].get("pattern")})
        return {
            "ok": True,
            "draft_path": path,
            "reflect_entry": entry["seq"],
            "promote_command": ("python scripts/promote_rule.py --promote %s "
                                "--approved-by <your-name>" % fname),
        }

    # -- 内部 ---------------------------------------------------------------
    def _resolve_draft(self, draft):
        """把 路径/文件名 归一成 (abs_path, data)。只认磁盘上的真实候选。"""
        if isinstance(draft, dict):
            raise TypeError("draft must be a file path (see propose_rule's "
                            "return value); dicts carry no verifiable source")
        path = draft if os.path.isabs(draft) else os.path.join(
            self.proposals_dir, draft)
        if not os.path.exists(path):
            raise ValueError("draft not found: %s" % path)
        with open(path, encoding="utf-8") as f:
            return path, json.load(f)

    def _write_verdict(self, path, data, report):
        """把自测结论写回候选文件（人工审阅时的第一眼信息）。"""
        if not os.path.exists(path):
            return
        data["status"] = report["verdict"]
        data["auto_ready"] = report["verdict"] == "ready"
        data["meta_verified"] = {
            "verdict": report["verdict"],
            "reasons": report["reasons"],
            "benign_hits": report["benign_hits"],
            "self_hits": report["self_hits"],
            "attack_hits": report["attack_hits"],
            "attack_samples": report["attack_samples"],
            "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "checked_by": self.actor,
        }
        if report["verdict"] == "rejected":
            data["review_notes"] = ("meta-agent self-test rejected: %s"
                                    % "; ".join(report["reasons"]))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
