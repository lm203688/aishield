# 部署隔离硬验证报告

- **日期**：2026-09-03
- **方法**：Cloudflare API 实地查询（Zones / DNS Records / Page Rules），非 DNS 猜测
- **凭据**：用户提供的 CF API Token（T1，全账户可读）
- **结论**：**aishield 与 healthlens / swarmlabs / oraclemind 已完全分开部署，不存在互相影响**

---

## 一、隔离矩阵（权威证据：DNS Records API）

| 域名 | 出口机制 | 目标标识 | 与 aishield 共享？ |
|---|---|---|---|
| `aishield.tools` | Cloudflare Named Tunnel | `0c39bcfb-0c96-4858-9025-d54131e062ec.cfargotunnel.com` | —（自身） |
| `www.aishield.tools` | 同上 | `0c39bcfb-…cfargotunnel.com` | 同一隧道（aishield 自有） |
| `swarm.aishield.tools` | 同上 | `0c39bcfb-…cfargotunnel.com` | 同一隧道（aishield 自有） |
| `healthlens.cc` | Cloudflare Pages | `healthlens-a3w.pages.dev` | ❌ 不共享 |
| `www.healthlens.cc` | Cloudflare Pages | `healthlens-a3w.pages.dev` | ❌ 不共享 |
| `api.healthlens.cc` | Cloudflare Named Tunnel | `772e48b6-fec9-4295-9816-92f6479e823d.cfargotunnel.com` | ❌ **不同隧道 ID** |
| `swarmlabs.tools` | Cloudflare Pages | `swarmlabs-dnh.pages.dev` | ❌ 不共享 |
| `oraclemind.cc` | Vercel | A `76.76.21.21` | ❌ 不共享 |

**判定**：5 个站点分属 5 套独立出口（2 条互不相同的 Named Tunnel + 2 个 Pages 项目 + 1 个 Vercel）。
aishield 隧道 `0c39bcfb` 是**专属**的，healthlens 的 API 走 `772e48b6`（另一条），前端走 Pages。
**不存在「一个通道共用」的问题，任何一方的部署都不会抹掉另一方的路由。**

## 二、实时健康复核

| URL | HTTP | 说明 |
|---|---|---|
| `https://aishield.tools/` | 200 | 正常 |
| `https://aishield.tools/api/v1/health` | 200 | `rules_count=228` |
| `https://www.aishield.tools/` | **404** | 见问题 ② |
| `https://swarm.aishield.tools/` | **404** | 见问题 ② |
| `https://healthlens.cc/` | 200 | 正常 |
| `https://api.healthlens.cc/` | 200 | 正常 |

---

## 三、发现的三处残留问题（均未修改，待确认）

### ① `aishield.tools.healthlens.cc` — 跨项目耦合死记录

- 位于 **healthlens.cc** zone 内，CNAME 指向 **aishield 的隧道** `0c39bcfb`。
- 这是历史上 `cert.pem` 默认 zone 是 healthlens.cc 时误建的记录（`diagnostics/deploy-result.md` 第 85 行有同样痕迹），**至今未清理**。
- 当前状态：`HTTP 000`（不可达），因为该 hostname 未注册在 aishield 隧道的 Public Hostname 里，CF 直接拒绝。
- **风险**：目前无害（死记录），但属跨项目耦合残留，将来任何一方调整时容易被误判/误路由。
- **建议**：删除该 CNAME 记录。

### ② `www` / `swarm` 子域 404 — 隧道未注册 Public Hostname

- 两条 CNAME 均正确指向 aishield 隧道，但隧道的 Public Hostname 只注册了 apex（`aishield.tools`）。
- 结果：CF 在 hostname 校验阶段就返回 404（`Server: cloudflare`，非 aishield 服务返回）。

### ③ Page Rule 对未注册 hostname 不生效（关键机制认知）

- `www.aishield.tools/* → 301 → https://aishield.tools` 这条 Page Rule **存在且 status=active，priority=1**（最高优先级）。
- 但实测请求 `www.aishield.tools` 返回 **404 且无 `Location` 头** —— 跳转**没有执行**。
- **结论**：Cloudflare 对「指向隧道但未注册为 Public Hostname」的 hostname，在 Page Rule 执行之前就已 404。
  **因此修复顺序必须是：先注册 Public Hostname，跳转规则才可能生效。** 只改 Page Rule 无效。

### 附：nginx 配置层面仍有混合（历史遗留）

| 文件 | `server_name` 内容 | 隔离？ |
|---|---|---|
| `nginx/nginx.conf`（L27、L61） | `aishield.tools www.aishield.tools healthlens.cc www.healthlens.cc _` | ❌ 混写 |
| `fix-nginx.sh`（L155） | 同上 | ❌ 混写 |
| `setup-nginx.sh`（L56） | `aishield.tools www.aishield.tools _` | ✅ |
| `nginx-aishield.conf`（L14） | `aishield.tools www.aishield.tools _` | ✅ |

VPS 上实际加载的是哪一份无法从本地确认（SSH key 已失效）。若仍在用 `nginx/nginx.conf`，虽不影响当前（隧道直连 `localhost:8450`，可能旁路 nginx），但属待清理的耦合点。

---

## 四、附带的旧问题解答：「pages build and deployment / build Failed in 17 seconds」

- 这是 **Cloudflare Pages 的构建失败**，与 aishield 无关（aishield 走隧道，从无 Pages）。
- 该账户下有两个 Pages 项目：`healthlens-a3w`（healthlens.cc）与 `swarmlabs-dnh`（swarmlabs.tools），失败来自其中之一。
- 本次 token 对 **Pages API 返回 403**，拿不到具体 Build log。
- **需要你操作**：CF 控制台 → 对应 Pages 项目 → Deployments → 打开失败那条 → 展开 **Build log**，把红色报错发我。

---

## 六、清理执行记录（2026-09-03 已执行）

| # | 动作 | 对象 | 结果 |
|---|---|---|---|
| 1 | **删除 DNS 死记录** | `aishield.tools.healthlens.cc`（healthlens zone → aishield 隧道） | ✅ 已删除并复验，zone 内仅剩 api/根/www 三条 |
| 2 | **删除无引用子域** | `swarm.aishield.tools` | ✅ 已删除并复验，全仓无任何代码/配置引用 |
| 3 | **解耦 nginx 配置** | `nginx/nginx.conf`（L27、L61）、`fix-nginx.sh`（主配置 L155、FALLBACK 兜底 L205）移除 `healthlens.cc www.healthlens.cc`；FALLBACK 由 `server_name _;`（全兜）收紧为 `server_name aishield.tools www.aishield.tools;` | ✅ 主配置=`server_name aishield.tools www.aishield.tools _;`；FALLBACK=`server_name aishield.tools www.aishield.tools;`；`setup-nginx.sh` 经 grep 确认无 healthlens 残留；两脚本 `bash -n` 通过 |
| 4 | `www.aishield.tools` | 保留 | ⛔ 无法由我修复，见下 |

**执行后健康复核（无连带影响）**

| URL | HTTP |
|---|---|
| `https://aishield.tools/` | 200 |
| `https://aishield.tools/api/v1/health` | 200（`rules_count=228`，commit `93fcd10c5a07`，`deployed_at=2026-09-01T05:00:07Z`） |
| `https://healthlens.cc/` | 200 |
| `https://api.healthlens.cc/` | 200 |

### 为什么 `www.aishield.tools` 没被处理

- 修复它需要在隧道上注册 **Public Hostname**，而：
  - CF API `cfd_tunnel/{id}/configurations` → **401 Not authorized**（当前 token 无 Tunnel:Edit）
  - VPS SSH 已失效，无法执行 `cloudflared tunnel route` 或改 `config.yml` 的 ingress
- 删除它只会让 www 从「404」变成「不解析」，**没有任何改善**，反而丢失已有的 Page Rule 配置 → 因此**保留原样**。
- 好消息：Page Rule `www.aishield.tools/* → 301 → https://aishield.tools` 已 active 且优先级最高，**一旦注册 Public Hostname 就会立即生效**。

**需要你手动做（约 30 秒）**：Cloudflare 控制台 → Zero Trust → Networks → Tunnels → 选中 `0c39bcfb-...` → Public Hostname → Add：

| Subdomain | Domain | Type | URL |
|---|---|---|---|
| `www` | `aishield.tools` | HTTP | `localhost:8450` |

（若不想让 www 生效，也可直接删掉那条 CNAME 和对应的 Page Rule，两者结果等价。）

### 附：环境坑记录

`grep -c $'\r' <file>` 在 Git Bash 下会**误报**（`$'\r'` 未正确传入，退化为空模式 → 命中所有行）。
判断行尾必须按字节统计：`b.count(b'\r\n')` 或用 `cat -A` 看是否有 `^M`。本次 4 个 nginx 文件实测 `total_CR=0`，均为纯 LF，无需转换。

---

## 五、Token 权限边界（下次别撞墙）

| API | T1 结果 |
|---|---|
| `GET /accounts` | ✅ 200，可见全部 3 个账户 |
| `GET /zones` | ✅ 200，5 个 zone |
| `GET /zones/{id}/dns_records` | ✅ 200 |
| `GET /zones/{id}/pagerules` | ✅ 200 |
| `GET /accounts/{id}/cfd_tunnel` | ⚠️ 200 但 `result: []`（无 Tunnel:Read 权限） |
| `GET /accounts/{id}/pages/projects` | ❌ 403 |
| `GET /zones/{id}/rulesets` | ❌ 403 |

**技巧**：`cfd_tunnel` 枚举不到时，从 **DNS 记录的 content 反查隧道 UUID** 同样能定性，且更贴近真实路由。
