# AIShield GitHub Action（独立仓库源码）

把 AIShield 安全扫描接入任意 CI 工作流，作为 **merge 门禁**：PR 里引入的 MCP
server / AI skill / prompt 一旦触碰 `fail_on` 风险阈值，CI 直接失败，并产出
**SARIF**（可上报 GitHub Security tab）与 JSON 报告。

> 核心不变量：扫描器**绝不执行被扫配置里的任何命令**、**绝不联网抓取被扫内容**
> （`enable_osv=false` 时完全离线）。本地优先，代码不出 runner。

## ⚠️ 发布硬性约束（重要）

GitHub Marketplace 的 **Action 仓库不得包含任何 `.github/workflows` 文件**。
主仓库 `lm203688/aishield` 有 18 个 workflow，因此本 Action **必须发布到独立仓库**
`lm203688/aishield-action`，且**该仓库保持无 workflow**。

## 发布步骤（一次性，需你登录）

1. 在 GitHub 新建仓库 **`lm203688/aishield-action`**（Public，无 workflow 文件）。
2. 把本目录（`distribution/github-marketplace/`）内容推到该仓库：
   - `action.yml`
   - `action_entrypoint.py`
   - `Dockerfile`
   - 本 `README.md`
3. 在仓库 **Releases** 打一个 tag（如 `v4.2.2`）→ 发布 Release。
4. 发布页勾选 **Publish to GitHub Marketplace** → 接受 Marketplace 开发者协议。
5. 等待 GitHub 审核通过（数工作日）。

## 用法（消费者侧）

```yaml
# .github/workflows/security.yml
name: AIShield Scan
on: [pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: lm203688/aishield-action@v4.2.2
        with:
          tool_type: mcp        # mcp / skill / gpt / prompt
          fail_on: high         # safe / medium / high / critical
          enable_osv: "false"   # true 时联网查 OSV.dev 实时 CVE
      - name: Upload SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: aishield.sarif
```

## 自包含说明

`action_entrypoint.py` 在独立仓库运行时，若找不到 `scanner/` 包，会**惰性克隆
AIShield 自身仓库**（是我们自己的源码，不是被扫目标）以加载扫描引擎——因此本
Action 仓库无需打包整套扫描器，保持轻量。
