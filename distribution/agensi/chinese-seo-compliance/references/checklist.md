# 中文站点 SEO / GEO 合规检查清单

逐项核对，每项只填「通过 / 缺失 / 不适用」+ 证据来源，不写推测。

## A. 搜索引擎收录（12 项）

| # | 检查项 | 判定标准 |
|---|--------|----------|
| A1 | robots.txt 可访问 | HTTP 200，非 HTML 错误页 |
| A2 | 未封 Baiduspider | 无 `User-agent: Baiduspider` + `Disallow: /` |
| A3 | 未封 Sogou / 神马 / 360 | 同上，逐个 UA 核对 |
| A4 | sitemap 已在 robots 声明 | robots 内含 `Sitemap:` 行 |
| A5 | sitemap 可访问且格式合法 | XML 解析通过，URL 数 > 0 |
| A6 | sitemap lastmod 真实 | 与页面实际更新时间一致，非全站同一时间戳 |
| A7 | title 长度合理 | ≤ 30 个汉字，核心词在前段 |
| A8 | description 长度合理 | ≤ 78 个汉字，非 title 复制 |
| A9 | 无大批量重复 title | 抽样 20 页，重复率 < 10% |
| A10 | canonical 正确 | 自指或指向主版本，无带参分散 |
| A11 | 移动端适配 | 存在 viewport 且渲染无横向滚动 |
| A12 | HTTPS 证书有效 | 未过期、链完整、无混合内容 |

## B. 中国大陆法规（7 项）

| # | 检查项 | 判定标准 |
|---|--------|----------|
| B1 | ICP 备案号展示 | 页脚可见，文本与备案信息一致 |
| B2 | 备案号链接工信部 | 指向 `beian.miit.gov.cn` |
| B3 | 公安联网备案 | 如适用，页脚展示且可点击核验 |
| B4 | 隐私政策 | 独立页面可访问，说明个人信息收集范围 |
| B5 | 用户协议 | 独立页面可访问 |
| B6 | Cookie / 埋点告知 | 首次访问有明确告知 |
| B7 | 行业资质 | 医疗 / 金融 / 教育等特殊行业展示对应资质 |

## C. AI 可见性 GEO（10 项）

| # | 检查项 | 判定标准 |
|---|--------|----------|
| C1 | `/llms.txt` 存在 | HTTP 200，Markdown 结构清晰 |
| C2 | llms.txt 说明站点定位 | 首段一句话讲清做什么 |
| C3 | llms.txt 列关键入口 | 主要栏目 / API / 数据集链接 |
| C4 | `/.well-known/agent-card.json` 存在 | HTTP 200，JSON 合法 |
| C5 | agent-card 声明能力 | 有 name / description / endpoints |
| C6 | AI 爬虫策略与意图一致 | GPTBot / ClaudeBot / PerplexityBot / Google-Extended 的允许或封禁是有意为之 |
| C7 | JSON-LD 结构化数据 | 至少有 Organization 或 Article |
| C8 | 结构化数据与页面一致 | 字段值能在可见内容中找到对应 |
| C9 | 正文服务端渲染 | 禁用 JS 后正文仍可读 |
| C10 | 事实密度 | 关键页含可引用的具体数字 / 日期 / 定义 |

## 优先级排序原则

出结论时按下列顺序排优先动作，不要平铺：

1. **阻断级**：robots 误封、站点不可访问、备案缺失导致的合规风险
2. **结构级**：sitemap 缺失、canonical 错乱、正文纯前端渲染
3. **增量级**：llms.txt、agent-card、结构化数据、事实密度

## 常见误判

- robots.txt 返回 HTML 404 页会被部分工具当成"存在"，要看状态码不要看内容长度
- `Disallow:` 后面为空表示允许全部，不是禁止
- 带参 URL 的 canonical 指回主版本是正确做法，不要报为错误
- 站点主动封禁 AI 爬虫可能是有意的商业选择，报"与意图不一致"前先问用户
