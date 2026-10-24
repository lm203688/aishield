## AIShield Self-Scan

**Result**: FAIL | **Score**: 0/100 | **Risk**: critical

| 项 | 值 |
|----|----|
| 扫描源 | 13 |
| 全部发现 | 289 |
| 自指误报（已消噪） | 161 |
| 未登记阻断级 | 1 |
| 腐烂 allowlist 条目 | 0 |
| 免杀清单版本 | 2 |

### 未登记的阻断级发现（必须处理）

- **mcp-server** [critical] None — 依赖含已知漏洞（GHSA-6qxp-vccf-f47h）: @modelcontextprotocol/sdk（情报公告，建议升级至修复版本）

> 评分口径：各源扫描分文件数加权 = 33，扣 未登记阻断 x40、腐烂条目 x15 → 0/100。阈值 < 60 即失败。
> 免杀清单：`distribution/self_reference_allowlist.json` v2。
> 只读扫描：不执行被扫文件里的任何命令，不发起网络请求。
