# 分发提交手册（Registry / 技能市场 / 插件市场）

本文件解决一类**只在真人登录时才暴露**的问题：产物已经通过自检、源文件已入库，
但没人知道「下一个动作到底是在哪个页面上点哪一下」。

所以每条渠道都写清四件事：**入口 → 是否需要账号 → 精确步骤 → 可粘贴的载荷在哪**。
凡是需要手机号 / OTP / 图形验证码 / 实名的地方，都单独标 🔒 —— 那一步只能人来。

## 提交前必跑（30 秒）

```bash
python scripts/verify_distribution.py          # 退出码 0 才允许提交
```

它读 `distribution/published.json` 台账，逐条校验：源文件是否在仓库里留底
（`source_dir`）、评分是否 ≥ 台账 `policy.min_overall_score`、是否命中
`policy.block_severities`。**任何投放到外部渠道的产物都必须先在台账登记**
—— 否则这次发布就是一次没有留底的投放，下次想覆盖发布时找不到源。

提交完成后，回写台账两个字段：`published_version` 与 `published_at`。
`published_version` 与 `version` 不一致时，`verify_distribution.py` 会持续提示
版本漂移（这是设计，不是噪音：它在提醒你线上还是旧版）。

---

## A. 台账里在等的 5 条（4 条未发布）

来源：`distribution/published.json`

| 渠道 | 名称 | 线上版本 | 状态 |
| --- | --- | --- | --- |
| `agensi` | chinese-seo-compliance | 1.0.0 | ⚠️ 漂移（源已 1.1.0，等覆盖发布） |
| `claude-skills` | aishield-security-scan | 未发布 | 源就绪 |
| `gpt-store` | aishield-gpt | 未发布 | 源就绪 |
| `huggingface` | aishield-agent-security-benchmark | 未发布 | 源就绪 |
| `clawhub` | aishield | 未发布 | 源就绪（需较老的 GitHub 账号） |

### A1. `agensi` / chinese-seo-compliance —— 覆盖发布

- 入口：Agensi 创作者后台（用当时收到 `noreply@agensi.io` 投递通知的那个账号登录）。
- 需求：🔒 账号登录。
- 步骤：
  1. 后台找到已上架的 `chinese-seo-compliance`；
  2. 选「更新 / 覆盖发布」，不要新建条目（新建会留下两个同名条目，且旧条目无法回收）；
  3. 上传 `distribution/agensi/chinese-seo-compliance` 的打包产物；
  4. 版本号填 `1.1.0`；
  5. 发布后回来改台账：`published_version` → `"1.1.0"`，`published_at` → 当天日期。
- 收尾验证：

  ```bash
  python scripts/verify_distribution.py    # 退出码 0，且不再出现 agensi 漂移提示
  ```

### A2. `claude-skills` —— 首次提交技能

- 源：`distribution/claude-skill`
- 需求：🔒 登录 Claude 账号（同一个账号在会话里用过技能才方便自测）。
- 步骤：进入技能提交入口 → 上传源目录产物 → 填名称 `aishield-security-scan` → 提交审核。
- 审核期无法自查，通过后回写台账 `published_version`。

### A3. `gpt-store` —— GPT + Actions

- 源：`distribution/gpt-store`
- 需求：🔒 登录 ChatGPT（建 GPT 需 Plus/Pro 订阅）。
- 步骤：新建 GPT → 把 Actions 的 OpenAPI 指向线上契约
  （`https://aishield.tools/openapi.json`，**不要手抄一份 schema 贴进去**，
  手抄的那份会先过期）→ 隐私政策填 `https://aishield.tools/privacy`（若无此页先补）。

### A4. `huggingface` —— 数据集卡

- 源：`distribution/huggingface`
- 需求：🔒 登录 HuggingFace。
- 步骤：新建 dataset → 上传 → 填卡片元数据 → 提交。

### A5. `clawhub` —— 认领命名空间

- 源：`distribution/clawhub`
- 需求：🔒 `clawhub login`，且**需要较老的 GitHub 账号**（命名空间认领有账号年龄门槛）。
- 目的不是流量：是反制第三方 `clawhub/ai-shield-audit`（laurentaia）占用的混淆名。
  这类抢注一旦形成，用户在外部看到的"aishield 审计工具"就不是本仓的。

---

## B. MCP Registry / 目录站

| # | 渠道 | 入口 | 需要登录 | 载荷来源 |
| --- | --- | --- | --- | --- |
| B1 | GitHub MCP Registry（官方） | CLI：`npx @anthropic/mcp-registry publish --from ./mcp-server` | 🔒 GitHub | `mcp-server/server.json` |
| B2 | Glama（56K+ Servers） | https://glama.ai/mcp/servers/new | 🔒 站点账号 | `registry/glama.json` |
| B3 | Smithery | `npx @smithery/cli publish ./mcp-server` | 🔒 站点账号 | `mcp-server/smithery.yaml` |
| B4 | mcp.so | https://mcp.so/submit | 🔒 站点账号 | `registry/mcpso.yaml` |
| B5 | PulseMCP | 站点提交入口 | 🔒 站点账号 | `registry/pulsemcp.json` |
| B6 | npm | `cd mcp-server && npm publish` | 🔒 npm token | `mcp-server/package.json` |
| B7 | Docker MCP Registry | `docker build -t aishield/aishield-api:latest . && docker push aishield/aishield-api:latest` | 🔒 Docker Hub | `Dockerfile` |
| B8 | PyPI（Python SDK） | `pip install build && python -m build && twine upload dist/*` | 🔒 PyPI token | `setup.py` / `pyproject.toml` |

> 目录站普遍会**自动爬取** GitHub 仓库（Glama 就是其中之一）。所以 B2/B5 有时
> 不提交也会出现条目 —— 但那时条目内容不受你控制，字段往往缺一半。
> 主动提交是为了拿到**可编辑的条目**。

### 提交流程里最容易漏的一步

`mcp-server/server.json` 与 `registry/server.json` 是**两份** MCP Registry 清单，
各自带一个 `version` 字段。`scripts/sync_version.py` 把它们都纳入了声明位门禁
（漏了其中一份就会重现 2026-09-19 那次「registry 已升级、mcp-server 停在旧版」的
漂移）。**提交前先跑**：

```bash
python scripts/sync_version.py --check     # 版本声明位全一致才提交
```

---

## C. 自检清单（每次发布后照抄）

```bash
# 1. 台账 + 评分 + 留底
python scripts/verify_distribution.py

# 2. 版本声明位（含两份 registry 清单）
python scripts/sync_version.py --check

# 3. 规则数声明位（对外资产里不许出现过期数字）
python scripts/rule_count_gate.py --check

# 4. 线上契约确实带上了新字段（不是只有本地函数里对）
curl -sS https://aishield.tools/openapi.json | head -c 200
```

第 4 条的意义：本地 `get_openapi_spec()` 返回正确**不等于**线上服务出去的是正确的。
本仓真实发生过「本地文件全对、线上服务错版本」的缺陷（`api/declaration_surface.py`
的模块注释里记着完整形状），所以第 4 条不能省。

---

## D. 不要做的事

- ❌ 不要为同一个产物新建第二个条目来"更新"——旧条目回收不了，目录会重复。
- ❌ 不要把规则数、工具数写死进提交材料 —— 权威值只有 `GET /api/v1/health` 一处。
- ❌ 不要在台账里把 `published_version` 提前改成新版本号"免得门禁报错"。
  那个提示是唯一在告诉你"线上还是旧版"的信号，改了它就等于自己关掉告警。
