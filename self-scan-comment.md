## AIShield Self-Scan

**Result**: PASS | **Score**: 88/100 | **Risk**: low

| 项 | 值 |
|----|----|
| 扫描源 | 11 |
| 全部发现 | 56 |
| 自指误报（已消噪） | 28 |
| 未登记阻断级 | 0 |
| 腐烂 allowlist 条目 | 0 |
| 免杀清单版本 | 1 |

> 评分口径：各源扫描分文件数加权 = 88，扣 未登记阻断 x40、腐烂条目 x15 → 88/100。阈值 < 60 即失败。
> 免杀清单：`distribution/self_reference_allowlist.json` v1。
> 只读扫描：不执行被扫文件里的任何命令，不发起网络请求。
