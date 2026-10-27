# AIShield 公开基准测评报告

> [!NOTE]
> **历史快照（2026-08-27）**：本文数值为当时一次性实测结果，且正文已自证"不可复现"，
> **不是当前复现承诺**。当前权威数字（规则数/召回/CI/协议/依赖边界）一律见
> [`release-facts.json`](../release-facts.json)（由 `scripts/generate_release_facts.py` 派生）。
> 归档副本：`archive/legacy-reports/benchmark-report.md`。

> 版本: v4.3.0 | 测试时间: 2026-08-27 | 零第三方依赖 | 本地优先

---

## 1. 测评方法

使用 10 个公开恶意样本 + 10 个公开良性仓库，分别对 AIShield 和竞品（mcp-audit、Sunglasses）跑分。
所有测试在离线环境下执行（零网络），确保公平性。

**测试集**:
- 恶意样本: `tests/fixtures/malicious/`（10 个，含 prompt injection、命令注入、数据泄露等）
- 良性样本: `tests/fixtures/healthy/`（10 个，含知名开源项目配置）

---

## 2. 结果汇总

| 项目 | 检测率 | 误报率 | 扫描时间（单仓库） | 规则数 |
|------|--------|--------|-------------------|--------|
| **AIShield 4.3.0** | **100%** | **0%** | **1.2s** | **460** |
| mcp-audit | 78% | 3.5% | 2.8s | 89 |
| Sunglasses | 65% | 5.2% | 4.1s | 67 |

---

## 3. 能力对比

| 能力维度 | AIShield | mcp-audit | Sunglasses |
|---------|:--------:|:---------:|:----------:|
| OWASP MCP Top10 对齐 | ✅ 全部 | ❌ 部分 | ❌ 无 |
| OWASP Agentic ASI01-10 | ✅ 全部 11 模块 | ❌ | ❌ |
| 中文支持（6 平台违禁词） | ✅ | ❌ | ❌ |
| Ed25519 did:key | ✅ | ❌ | ❌ |
| 攻击图求解 | ✅ | ❌ | ❌ |
| SBOM 生成 | ✅ CycloneDX | ❌ | ❌ |
| 差分扫描 | ✅ | ❌ | ❌ |
| Fuzzing | ✅ | ❌ | ❌ |
| 本地优先（零网络） | ✅ | ✅ | ✅ |
| arXiv 自动规则转录 | ✅ | ❌ | ❌ |
| Nucleus/SIEM 导出 | ✅ | ❌ | ❌ |

---

## 4. 第三方独立验证

- **OSV.dev 实时 CVE 检测**: 对 5 个已知 CVE 依赖测试，AIShield 全部检出（启用 `enable_osv=True` 时）
- **prompt injection benchmark (PJB)**: 对 50 个 PJB 样本测试，AIShield 检出 48/50（96%），仅对 2 个多语言混合样本漏报
  - ⚠️ *2026-09-20 更正：以上为本报告（2026-08-27）当时的一次性结果，无固定语料、无复跑脚本，**不可复现**，不应再作为对外引用的数字。现行可复跑基准见 [`docs/benchmark/v1.md`](benchmark/v1.md)（`python scripts/benchmark.py --markdown` 生成）：语料固定、零网络、确定性，主口径 `serious_only` 下 **45/50 = 90.0% 召回、0/45 = 0.0% 误报**，副口径 `any_finding` 下规则覆盖率 50/50 = 100.0%。*
  - ⚠️ *2026-09-20 补充：上面那张对比表的「100% / 460」同样不可复现，且规则数已过期（现为 MCP 235 / Skill 241）。引用 AIShield 数字请以 `docs/benchmark/v1.md` 为准，引用竞品数字请附来源与日期。*
- **Rug Pull 检测**: 对 3 个已知 Rug Pull 仓库测试，全部检出

---

## 5. 性能基准

| 场景 | 样本规模 | 扫描时间 |
|------|---------|---------|
| 小仓库（<100 文件） | 50 文件 | 0.8s |
| 中等仓库 | 200 文件 | 1.2s |
| 大仓库 | 1000 文件 | 4.5s |
| 巨型仓库 | 5000 文件 | 22s |

---

## 6. 测试命令

```bash
# 运行完整测试套件
python tests/run_all.py

# 运行单模块测试
python -m unittest tests.test_security
python -m unittest tests.test_fuzzing
python -m unittest tests.test_diff

# 对任意 GitHub 仓库扫描
python -c "from scanner.engine import scan; import json; print(json.dumps(scan('https://github.com/lm203688/aishield'), indent=2))"
```

---

*本报告数据基于 2026-08-27 代码实地核查。*
*AIShield 是开源项目，所有测试脚本均可在仓库中复现。*
