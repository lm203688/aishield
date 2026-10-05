# 统一导出面 + 评分可解释

企业要把 agent 安全扫描接进 SIEM/SOAR，缺的从来不是「一个 JSON 输出」，
而是两件事：**产出得合目标端的规格**，**分数得能向审计/客户交代**。这份文档
是这两件事的接入说明。

代码入口：

| 用途 | 入口 |
| --- | --- |
| 目标端格式实现 + 注册表 | `scanner/export_registry.py` |
| HTTP API | `POST /api/v1/export/<target>`、`POST /api/v1/score/audit` |
| 目标端清单（发现有哪些） | `POST /api/v1/export/registry` |
| CLI | `python scripts/export_findings.py` |
| 评分账本 / 独立复算 | `scanner/score_explain.py` |

---

## 1. 目标端

`POST /api/v1/export/registry` 会列出当前全部目标端。六个内置：

| 目标端 | 规格 | 说明 |
| --- | --- | --- |
| `ocsf` | OCSF 1.1.0 | Vulnerability Finding（`class_uid=2001`），SIEM/SOAR 通用；severity 映射到 `severity_id`（info=1/low=2/medium=3/high=4/critical=5） |
| `stix` | STIX 2.1 | Bundle：`identity` + 每条 finding 一个 `vulnerability` SDO，`external_id` 用稳定 rule_id，对象 id 走 uuid5（同规则永远同 id，SOAR 去重靠它） |
| `nucleus` | Nucleus FlexConnect | 字段对齐 Qualys / Tenable / CrowdStrike 摄入管道 |
| `splunk` | Splunk HEC 风格 | `{event_count, events[]}` |
| `json` | AIShield Findings | 归一化，字段不丢，自研管道用 |
| `csv` | AIShield CSV | 扁平表格，返回 `payload_text` |

已知边界（都会出现在响应的 `warnings` 里，不会闷着）：

* OCSF 1.1 的 Vulnerability Finding **没有 remediation 字段**，所以修复建议
  不在这条产物里 —— 需要走工单通道。
* 映射只覆盖规范里真实存在的字段，不拿自造字段冒充合规。

### 目标端配置化

目标端怎么投（endpoint / headers / 开关 / 格式参数）不进代码，走 JSON 清单：

```json
{
  "targets": [
    {
      "name": "corp-splunk",
      "target": "splunk",
      "endpoint": "https://splunk.internal:8088/services/collector",
      "enabled": true,
      "headers": { "Authorization": "Bearer <HEC-TOKEN>" }
    },
    { "name": "sentinel", "target": "ocsf", "enabled": true },
    { "name": "resilient", "target": "stix", "enabled": false }
  ]
}
```

```bash
# 批量导出（enabled=false 的自动跳过）
python scripts/export_findings.py --findings scan.json --config targets.json --outdir out/
```

**凭据红线**：headers 里的 token 只用于投递鉴权，**绝不进导出产物**。
`TargetConfig.redact_headers()` 会把 `Authorization` / `*token*` / `*api-key*`
一类头统一掩码；产物本身还会再过一道弱探针（Bearer / `sk-` / api_key 字段），
命中即报 issue。所以导出产物可以直接入库/发工单，不会把密钥带出去。

---

## 2. 评分可解释

分数不再是黑盒。每个维度都是 `基准 − 扣分`，扣分项逐条可查、可申诉：

```bash
python scripts/export_findings.py --findings scan.json --target json --audit-score --total-files 42
```

输出（节选）：

```
总分 80（medium，badge=silver）
  · security_score       60 = 基准 100 − 扣分 40（展示 40）
      - [critical] 缺失鉴权 -20  rule=ASI04-01
      - [high] 第1条指令被覆盖 -10  rule=ASI01-INJ-01
  · data_handling_score  90 = 基准 100 − 扣分 10（展示 10）
      - [high] 硬编码凭据 -10  rule=SEC-01
[audit] ✓ 扣分账本闭合，attribution_complete=True coverage=100.0%
```

三条硬保证：

1. **账本闭合**：`penalty` 必须等于全部扣分项之和。曾经展示位只留 top5、
   而 `penalty` 是全量求和，出现「展示 80 / 实际 105」—— 25 分凭空蒸发，
   用户永远拼不出总分为何是 60。现在全量账本在 `contributions_full`，
   `audit()` 逐维度强制闭合，少一分都报 `penalty_not_reproducible`。
2. **每条扣分带 `rule_id`**：申诉能直接落到规则条目，而不是只有一句中文描述。
   缺 rule_id 报 `missing_rule_id`。
3. **独立复算**：`replay()` 不复用 `calculate_scores()` 的计算路径，而是另写
   一条从原始 findings 重算。两条路径不一致 ⇒ 报 `replay_mismatch`，
   这个分数当下不可信。replay 还给出确定性 `digest`，同输入必得同输出 ——
   评分口径被悄悄改动时，digest 会变，能当 CI 回归用。

### HTTP

```bash
# 直接审计一份已有扫描结果（给 scores）
curl -s -X POST https://<host>/api/v1/score/audit \
  -H 'content-type: application/json' \
  -d '{"scores": {...}}'

# 或者只给 findings，服务端复算 + 审计
curl -s -X POST https://<host>/api/v1/score/audit \
  -H 'content-type: application/json' \
  -d '{"findings": [...], "total_files": 42}'
```

响应里的 `attribution_complete` 才是「这条分数解释得清」的判据；
`coverage` 是展示口径覆盖了多少扣分；`issues[]` 是账本问题清单。

### 两个别误读的点

* **展示截断 ≠ 解释不完整**。`contributors` 仍只展示扣分最多的 5 条（历史
  兼容），但只要全量账本在、被截断金额如实报出（`hidden_amount`），
  这条分数照样算解释得清。审计把截断放在 `warnings`，不放在 `issues` ——
  否则门禁会「永远报红」，自己先变成空转。
* **同描述跨文件只扣一次**，这是评分口径，不是漏算。被折叠的条目记在
  `folded_duplicates`（含 rule_id 与次数），能查到「3 个文件为什么只扣一次」。
