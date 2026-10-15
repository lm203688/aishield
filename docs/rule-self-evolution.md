# AIShield 规则自进化（RSES）v0.1

> 状态：机制已落地并有测试钉死（2026-10-15）。本文件描述的是**已实现的契约**，
> 不是路线图。任何"将来会做"的部分都明确标了【未实现】。

规则集是扫描器的资产，也是它最大的攻击面：一条被污染的规则要么漏报
（安全失效），要么误报（信誉失效）。RSES 把"情报 → 草稿 → 自测 → 晋升 →
回滚"这条链上的每个决定变成**可验的记账事实**。

## 1. 拓扑

```
情报信号（tech_radar / arXiv / CVE）
   │
   ▼
┌─────────────────────────────┐
│ 有界元 agent                 │  eco/meta_agent.py
│   propose_rule    → draft   │  actor: meta:rses-drafter-v1
│   test_draft      → test    │  结构上无 promote/demote/rollback
│   submit_for_promotion → reflect │
└──────────────┬──────────────┘
               │ 候选文件（scanner/_proposed/PROPOSED_*.json）
               ▼
        （人类审阅 —— 唯一裁决点）
               │
               ▼
┌─────────────────────────────┐
│ 晋升闸门                     │  scripts/promote_rule.py
│  六道闸门 + --approved-by    │  actor: human:<approver>
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ 进化账本（哈希链）            │  eco/evolution_ledger.py
│  data/state/evolution_ledger │  promote/demote/rollback 必带 approved_by
│  .jsonl（merge=union 提交）   │  meta:* actor 无权特权动作
└─────────────────────────────┘
               ▲
               │ 回滚（promote_rule --rollback / 测试红灯安全阀 / rule_decay --retire）
               └─────────────────────────────────────────────
```

## 2. 三条硬不变量（测试钉死）

| # | 不变量 | 机制 | 测试 |
|---|--------|------|------|
| 1 | 账本不可被静默篡改 | 每条记录含 `prev_hash` + 自身 `hash`（除 hash 外全字段规范化 JSON 的 sha256） | `TestHashChain`：改字段/删行/调序/插坏行全部在第一个断点报出 |
| 2 | 特权动作必须带批准人 | `promote`/`demote`/`rollback` 缺 `approved_by` → `ValueError` | `TestPrivilegedActions` |
| 3 | 元 agent 永不晋升 | 结构上无晋升方法 + 账本层拒 `meta:` actor（双保险） | `TestMetaAgentBounding::test_structurally_has_no_promotion_capability` |

**自触发须为 0**（元 agent 的准入门槛）：草稿 pattern 在 BENIGN_CORPUS
（`scripts/rule_corpus.py`，单一真源）或自有仓库 shipped 面上任一命中即判
`rejected`。豁免目录（`tests/` `data/` `scanner/` `scripts/`）里攻击载荷是
合法居民——拿定义当反例是自指误报。负控语料取不到时 fail-closed，绝不静默
跳过检查。

## 3. 账本条目格式

```json
{"seq": 7, "ts": "2026-10-15T16:28:09Z", "actor": "human:alice",
 "action": "promote", "target": "PROPOSED_xxx.json",
 "rationale": "signal: <title> (<url>)",
 "evidence": {"patterns": ["..."], "attack_category": "...",
              "signal_url": "...", "snapshot": "radar_rules.2026...Z.json",
              "radar_rule_count": 21},
 "approved_by": "alice",
 "prev_hash": "<上一条 hash>", "hash": "<本条 hash>"}
```

动作词汇：`draft` / `test` / `reflect`（草拟侧，元 agent 可发）；
`promote` / `demote` / `rollback`（特权侧，必须带批准人，元 agent 禁入）。

actor 前缀即信任域：`meta:*` 只许起草；`human:*` / `ci:*` 可带批准人改规则集
（`ci:` 用于测试红灯安全阀等自动化身份——诚实记账：没有人类批准过它）。

## 4. 日常操作

```bash
# 元 agent 全流程（草拟 → 自测 → 提交审议）
python -c "
from eco.meta_agent import DraftingMetaAgent
a = DraftingMetaAgent()
out = a.propose_rule(signal_id='S1', signal_title='...', signal_url='...',
                     pattern=r'...', description='...', severity='high')
print(a.test_draft(out['draft_path']))
print(a.submit_for_promotion(out['draft_path']))
"

# 人类晋升（第七道闸门：批准人）
python scripts/promote_rule.py --promote PROPOSED_xxx.json --approved-by <你的名字>
# 或一次性导出：export AISHIELD_APPROVER=<名字>

# 回滚 / 退役（同为特权动作）
python scripts/promote_rule.py --rollback --approved-by <名字>
python scripts/rule_decay.py --retire --approved-by <名字>

# 账本
python eco/evolution_ledger.py --verify      # 校验整条链（CI 可挂）
python eco/evolution_ledger.py --summary
python eco/evolution_ledger.py --list
python scripts/promote_rule.py --evolution-ledger
```

CI 侧：`rule-promoter` workflow 每日用 `github.actor` 作为批准人跑
`--promote-all`；测试红灯时安全阀回滚并记 `ci:rule-promoter` 账。
账本随晋升提交进 git（`.gitattributes` 配 `merge=union`，追加型日志的语义
正确合并驱动；单写者 = 只有该 workflow 记账）。

## 5. 与既有机制的关系（不重复造）

- **promote_rule.py 六道闸门**：权威放行判据（schema/正则/宽度/重复/良性语料
  + shadow 三档）。元 agent 的自测是**第一遍保守草拟**，刻意更严（加自有仓库
  扫描）；人类闸门可以放行被元 agent 拒掉的风险候选——层级是"建议 vs 裁决"。
- **confidence_promotion.py**：候选的 evidence 累积（raw→seed→draft→rule）。
  RSES 不替代它；晋升时其结论自然成为账本 evidence 的一部分【未实现：
  自动把 confidence 快照写进 promote 的 evidence】。
- **promotion_ledger.jsonl**：信息性事件流水（写失败不阻断晋升，既有契约）。
  进化账本是问责脊柱（加载/写入失败会 raise）——两个账本分工不同，见
  `eco/evolution_ledger.py` docstring。

## 6. 诚实边界

- 哈希链证明的是"入链后未被静默改写"，不证明"该记的都记了"——后者靠
  promote_rule/rule_decay/安全阀三处接线 + 测试钉死（`TestPromoteRuleLedgerWiring`、
  `TestRuleDecayRetireWiring`）。
- 元 agent 的默认后端是规则式草拟参数（调用方给 pattern），**没有**自动从
  情报文本推导正则的能力【未实现】；LLM 后端与 NSE 语义探针同型，须过
  "候选无结论字段"契约后才可接入。
- 账本提交进 git 依赖 `merge=union`；若将来出现第二个提交者，先补单写者
  证明再改 `.github/auto-resolvable-paths.txt` 的说明。
