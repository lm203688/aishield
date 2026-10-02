# 每日安全守夜 automation-1786840209961 执行记忆

## 最近执行
- 2026-10-02 08:30 (CST)：① PASS / ② PASS / ③ PASS，**常规日（三项全绿，无关键异常）**。
  - ① 对外自检：self_scan --json `blocking_unsuppressed=0`、`stale_allowlist_entries=[]`、`ok=true`、no_execute/no_network=true；11 源 56 发现/28 抑制（阻断级全自指误报，逐源空），无漏报、允许清单无失效、无需新增条目；v4.10.0 / 235 规则。
  - ② 线上存活：health.json healthy=True/score=4/4/updated 2026-10-01T22:47Z（≈9.7h，FRESH）；aishield.tools 200/28822B；/api/v1/health 200/v4.10.0/235 规则/commit 509594ec/deployed_at 2026-09-30T02:39Z（≈2.25d，源存活）；main HEAD cc62fd4e（部署漂移，日级信息性非升级）。
  - ③ 测试：1696/0/0/26 全绿（ALL TESTS PASSED；核心契约成立）。后台流式曾显 test_dual_form_integration ERROR 行，同沙箱复跑权威汇总 0 failed/0 errors，确认是捕获截断假象非回归。
  - 常规日：仅写 digest（append 到 2026-10-02.md，Tech Radar 段之后），无跨项目升级、无即时高亮。产出 guard-2026-10-02.md。
- 2026-10-01 08:30 (CST)：① PASS / ② PASS / ③ PASS，**常规日（三项全绿，无关键异常）**。
  - ① 对外自检：self_scan --json `blocking_unsuppressed=0`、`stale_allowlist_entries=[]`、`ok=true`、no_execute/no_network=true；11 源 56 发现/28 抑制（阻断级全自指误报，逐源空），无漏报、允许清单无失效、无需新增条目；v4.10.0 / 235 规则。
  - ② 线上存活：health.json healthy=True/score=4/4/updated 2026-09-30T22:24Z（≈2.1h，FRESH）；aishield.tools 200/28822B；/api/v1/health 200/v4.10.0/235 规则/commit 509594ec/deployed_at 2026-09-30T02:39Z（≈22h，FRESH）；部署漂移 deployed 509594ec vs main HEAD 9c5e973a（日级信息性，非升级）。
  - ③ 测试：1579→**1696**/0/26 全绿（ALL TESTS PASSED；核心契约成立）。
  - 常规日：仅写 digest（append 到 2026-10-01.md，Tech Radar 段之后），无跨项目升级、无即时高亮。产出 guard-2026-10-01.md；commit `0cc7883c` 单提交推送并 Contents API 复验（两文件 HTTP 200、main HEAD=0cc7883c）通过。
- 2026-09-30 08:30 (CST)：① PASS(修复后) / ② PASS / ③ PASS(修复后)，**捕获并就地修复 2 项真实异常（非常规日）**。
  - ① 对外自检：捕获时 `blocking_unsuppressed=1`（index.ts `ai_slop_evasion`/jailbreak_roleplay, high）；研判为扫描器检测词表自指误报（与已登记 dangerous_pattern 同源），新增 allowlist 条目 `(mcp-server/src, index.ts, ai_slop_evasion)`，复扫 `0`、`stale=[]`、`ok=True`、no_execute/no_network=true。
  - ② 线上存活：health.json healthy=True/score=4/4/updated 2026-09-29T22:25Z（FRESH）；aishield.tools 200/v4.8.3/235 规则；commit 53bc038b 落后于 main HEAD a9572080（部署漂移，信息性非升级）。
  - ③ 测试：捕获时 1578/1/0/26，`test_all_tools_documented` 失败（index.ts 新增 `aishield_laya_gate`+`aishield_laya_shadow_stats` 未入 README）；补两行文档后复跑 **1579/0/26 全绿**。
  - 关键异常 2 项均即时高亮 + 跨项目升级 🔴（OPEN_ISSUES「🟠 跨项目升级」追加 2 条，标注同轮已修复/复验）。产出 guard-2026-09-30.md + 本地 digest（append 到 2026-09-30.md，Tech Radar 段之后）；commit `a04874af` 单提交推送并 Contents API 复验（main HEAD 一致、allowlist+README blob HTTP 200）通过。

- 2026-09-29 08:30 (CST)：① PASS / ② PASS / ③ PASS，**常规日（三项全绿，无关键异常）**。对外自检 blocking_unsuppressed=0、stale_allowlist_entries=[]、ok=true、no_execute/no_network=true；11 源 54 发现/27 抑制（阻断级全自指误报，逐源空），无漏报、允许清单无失效、无需新增条目。线上 health.json healthy=true/score=4/4/consecutive_failures=0/updated 2026-09-28T23:23:26Z（≈7min，FRESH）；aishield.tools 200 / 28818B / v4.8.3 / 235 规则（static 208+gen 8+radar 19）；/api/v1/health commit 53bc038b / deployed_at 2026-09-28T09:48:01Z（≈14h，FRESH）；main HEAD c51c626e（`[skip ci]` 自愈状态结算，日级漂移，信息性非升级）。本地测试 1579/0/0/23 全绿（ALL TESTS PASSED；核心契约成立）。产出 guard-2026-09-29.md + 本地 digest；commit 59c0864b 单提交推送并 Contents API 复验（main HEAD=59c0864b、两 blob HTTP 200）通过。
- 2026-09-28 08:30 (CST)：① PASS / ② PASS / ③ PASS，**常规日（三项全绿，无关键异常）**。对外自检 blocking_unsuppressed=0、stale_allowlist_entries=[]、ok=true、no_execute/no_network=true；11 源 54 发现/27 抑制（阻断级全自指误报，逐源空），无漏报、允许清单无失效、无需新增条目。线上 health.json healthy=true/score=4/4/consecutive_failures=0/checked_at 2026-09-27T21:28:05Z（age≈3h，FRESH）；aishield.tools 200 / 28818B / v4.8.3 / 235 规则（static 208+gen 8+radar 19）；/api/v1/health commit de89017f / deployed_at 2026-09-27T09:20:00Z（≈15h，FRESH）；main HEAD 60336fe4（日级漂移，Spine 11:17 CST 追平，信息性非升级）。本地测试 1579/0/0/23 全绿（ALL TESTS PASSED；核心契约成立）。产出 guard-2026-09-28.md + 本地 digest；待推送。
- 2026-09-26 08:36 (CST)：① PASS / ② PASS / ③ PASS，**常规日（三项全绿，无关键异常）**。对外自检 blocking_unsuppressed=0、stale_allowlist_entries=[]、ok=true、no_execute/no_network=true；11 源 54 发现/27 抑制（阻断级全自指误报，逐源空），无漏报、允许清单无失效、无需新增条目。线上 health.json healthy=True/score=4/4/consecutive_failures=0/updated 2026-09-25T21:41:29Z（age≈2h55m，FRESH）；aishield.tools 200 / 28818B / v4.3.0 / 235 规则（static 208+gen 8+radar 19）；/api/v1/health commit e746884a / deployed_at 2026-09-23T01:56:42Z（约 3 天旧、落后 main HEAD 81bb923b — Spine 11:17 CST 部署前漂移，信息性非升级）；main HEAD 81bb923b（"chore(radar): publish 2026-09-26 tech radar"）。本地测试 1579/0/0/23 全绿（ALL TESTS PASSED；`recall 0.9000<1.5000` 为故意门禁探针非真实失败，Failed=0 不升级）。产出 guard-2026-09-26.md + 本地 digest；commit f7061ea5 单提交推送并 Contents API 复验（main HEAD=f7061ea5、两 blob HTTP 200）通过。
- 2026-09-23 08:30 (CST)：① PASS / ② PASS / ③ PASS，**常规日（三项全绿，无关键异常）**。对外自检 blocking_unsuppressed=0、stale_allowlist_entries=[]、ok=true、no_execute/no_network=true；11 源 52 发现/25 抑制（阻断级全自指误报，逐源空），无漏报、允许清单无失效、无需新增条目。线上 health.json healthy=True/score=4/4/consecutive_failures=0/updated 2026-09-22T21:29:46Z（age≈3h，FRESH）；aishield.tools 200 / 28818B / v4.3.0 / 235 规则（static 208+gen 8+radar 19）；/api/v1/health commit b7d9c18b / deployed_at 2026-09-21T08:58:48Z（日级漂移，非异常）；main HEAD 3ccf3f52 领先 → Spine 11:17 CST 追平。本地测试 1283/0/0/26 全绿（ALL TESTS PASSED；较昨日 +39；`recall 0.9000<1.5000` 为故意门禁探针非真实失败，Failed=0 不升级）。产出 guard-2026-09-23.md + 本地 digest；commit 16a5cba1 单提交推送并 Contents API 复验（main HEAD=16a5cba1、两 blob HTTP 200）通过。
- 2026-09-22 08:30 (CST)：① PASS / ② PASS / ③ PASS，**常规日（三项全绿，无关键异常）**。对外自检 blocking_unsuppressed=0、stale_allowlist_entries=[]、ok=true、no_execute/no_network=true；12 源 49 发现/22 抑制（阻断级全自指误报，逐源空），无漏报、允许清单无失效、无需新增条目。线上 health.json healthy=True/score=4/4/consecutive_failures=None/updated 2026-09-21T22:04:12Z（age≈2.46h，FRESH）；aishield.tools 200 / 28818B / v4.3.0 / 235 规则（static 208+generated 8+radar 19）；/api/v1/health commit b7d9c18b / deployed_at 2026-09-21T08:58:48Z（≈23.5h，FRESH）；main HEAD 691e5a09 领先 → 日级漂移（Spine 11:17 CST 追平，非异常）。本地测试 1244/0/0/26 全绿（ALL TESTS PASSED；`recall 0.9000<1.5000` 为故意门禁探针非真实失败，Failed=0 不升级）。产出 guard-2026-09-22.md + 本地 digest；commit 8bdd0a50 单提交推送并 Contents API 复验（main HEAD=8bdd0a5034d0、两 blob HTTP 200：report b352ed48 / digest 827a75a6）通过。
- 2026-09-21 08:30 (CST)：① PASS / ② PASS / ③ PASS，**常规日（三项全绿，无关键异常）**。对外自检 blocking_unsuppressed=0、stale_allowlist_entries=[]、ok=true、no_execute/no_network=true；12 源 45 发现/21 抑制（阻断级全自指误报，逐源空），无漏报、允许清单无失效、无需新增条目。线上 health.json healthy=true/score=4/4/consecutive_failures=0/updated 2026-09-20T20:56:04Z（age≈3.60h，FRESH）；aishield.tools 200 / 28821B / v4.3.0 / 235 规则；/api/v1/health commit eed3df14 / deployed_at 2026-09-20T08:38:30Z（≈15.9h，FRESH）；main HEAD cf9c147 领先 → 日级漂移（Spine 11:17 CST 追平，非异常）。本地测试 1244/0/0/26 全绿（ALL TESTS PASSED；较 09-20 基准 +45 用例，日志 `recall 0.9000<1.5000` 为故意门禁探针非真实失败，Failed=0 不升级）。产出 guard-2026-09-21.md + 本地 digest；commit b5b6026e 单提交推送并 Contents API 复验（main HEAD=b5b6026e、两 blob HTTP 200）通过。
- 2026-09-20 08:30 (CST)：① PASS / ② PASS / ③ PASS，**常规日（三项全绿，无关键异常）**。对外自检 blocking_unsuppressed=0、stale_allowlist_entries=[]、ok=true、no_execute/no_network=true；12 源 45 发现/21 抑制（阻断级全自指误报，逐源空）。线上 health.json healthy=true/score=4/4/consecutive_failures=0/updated 2026-09-19T20:50:59Z（aishield.tools 200 / 28821B / v4.3.0 / 235 规则 / commit c133bbed / deployed_at 2026-09-19T14:03:08Z ≈9.5h，FRESH）→ 昨日 502 失活未复发。本地测试 1199/0/0/26 全绿（ALL TESTS PASSED；基准 recall 96.0% / fp 0.0%，漏 2/50 属信息性、Failed=0 不升级）。产出 guard-2026-09-20.md + 本地 digest；commit b137c647 单提交推送并 Contents API 复验（main HEAD 一致、两 blob HTTP 200）通过。
- 2026-09-19 08:30 (CST)：① PASS / ② PASS / ③ PASS，**常规日（三项全绿，线上已恢复）**。对外自检 blocking_unsuppressed=0、stale_allowlist_entries=[]、ok=true、no_execute/no_network=true；11 源 45 发现/21 抑制（阻断级全自指误报）。线上 health.json healthy=true/score=4/4/consecutive_failures=0/updated 2026-09-18T21:01:04Z（aishield.tools 200 / 238 规则）→ 昨日 502 失活已恢复，09-18 🔴 升级事项转已恢复、不重复升级。部署 commit 83d6318b 落后 main HEAD 24a3d311 1 提交（日级漂移，非异常）。本地测试 1108/0/26 全绿。产出 guard-2026-09-19.md + 本地 digest；commit 08d58ebb 单提交推送并 Contents API 复验（main HEAD 一致、两 blob HTTP 200）通过。
- 2026-09-18 08:30 (CST)：① PASS / ② 🔴 FAIL / ③ PASS，**关键异常日（线上站失活，已即时高亮 + 跨项目升级 🔴）**。
  - 对外发布物自检：self_scan --json `blocking_unsuppressed=0`、`stale_allowlist_entries=[]`、`ok=true`、no_execute/no_network=true；44 发现 / 20 抑制（全自指误报，11 源 blocking 均空），无未登记阻断、无漏报、允许清单无失效。
  - 线上存活：**aishield.tools 首页 + /api/v1/health 三次探测均 502**（502 非 404 → 源不可达，非 DNS/路由层）；远端 health.json `updated=2026-09-17T21:31:30Z`、`current.healthy=False / level=degraded / score=0/4 / consecutive_failures=3 / last_healthy_at=2026-09-17T05:01:19Z` → Spine 自 09-17 11:53Z 起连续 3 次失败，outage 跨 09-17 与 09-18 两自然日（连续 2 日失活）。根因：VPS :8450 / cloudflared 隧道中断（源无响应）。需用户登录 VPS 排查。
  - 本地测试 `tests/run_all.py` **1015/0/0/26 全绿**（较 09-17 的 1028/0/0/44 收敛，0 失败，核心契约成立）。
  - 处置：报告 `eco/reports/guard-2026-09-18.md` + 本地 digest `2026-09-18.md`；commit `5d4eb2e2` 单提交推送并 Contents API 复验（main HEAD 一致、blob 5118B 存在）通过；OPEN_ISSUES 「🟠 跨项目升级」节追加 🔴 条目（同日同来源无重复）；临时探针文件已清理。
- 2026-09-17 08:30 (CST)：三项 PASS，**常规日**（仅写 digest，无关键异常、无跨项目升级）。
  - 对外发布物自检：self_scan --json `blocking_unsuppressed=0`、`stale_allowlist_entries=[]`、`ok=true`、no_execute/no_network=true；44 发现 / 20 抑制（全自指误报，11 源 blocking 均空：mcp-server/src 6/5 / guardrail-harness 12/9 / github-marketplace 4/3 / action_entrypoint 3/3 等），无未登记阻断、无漏报、允许清单无失效条目。
  - 线上存活：远端 health.json updated 2026-09-16T21:26:55Z（age≈3.1h，FRESH，current 4/4）；aishield.tools 200 / 28509B；/api/v1/health 4.3.0 / 238 规则；线上 commit `f65e4986` deployed_at 2026-09-16T08:39:15Z（≈16h，FRESH）；main HEAD `f794ee7b` 日级漂移（Spine 11:17 CST 追平，非异常）。
  - 本地测试 `tests/run_all.py` **1028/0/0/44 全绿**（与 09-16 基准一致），核心契约（良性零误报 + 恶意仍拦）成立。
  - 产出 `eco/reports/guard-2026-09-17.md` + digest 追加；commit `2123e527` 单提交推送并 Contents API 复验（main HEAD 一致、两 blob 均存在）通过。
  - 工具链备注：本机沙箱下 curl `-o` 会丢弃写出文件且 body 显 0B（GitHub API 同日 0B 已证伪"站点空响应"），改用 shell 重定向后抓取正常；属抓取特性，不影响存活判定。
- 2026-09-16 08:30 (CST)：三项 PASS，**常规日**（仅写 digest，无关键异常、无跨项目升级）。
  - 对外发布物自检：self_scan --json `blocking_unsuppressed=0`、`stale_allowlist_entries=[]`、`ok=true`、no_execute/no_network=true；44 发现 / 20 抑制（全自指误报，逐源 blocking 均空：mcp-server/src 6/5 / guardrail-harness 12/9 / github-marketplace 4/3 / action_entrypoint 3/3 等），无未登记阻断、无漏报、允许清单无失效条目。
  - 线上存活：远端 health.json updated 2026-09-15T21:31:37Z（age≈2.97h，FRESH，current 4/4）；aishield.tools 200 / 28509B；/api/v1/health 4.3.0 / 238 规则；线上 commit `ff457dfc` deployed_at 2026-09-15T08:46:52Z（≈15.7h，FRESH）；main HEAD `67fa11e3` 领先（日级漂移，Spine 11:17 CST 追平，非异常）。
  - 本地测试 `tests/run_all.py` **1028/0/0/44 全绿**（较 09-15 的 748 +280，新增/参数化用例 + 网络依赖 skip 增多，失败数恒 0），核心契约（良性零误报 + 恶意仍拦）成立。
  - 产出 `eco/reports/guard-2026-09-16.md` + digest 追加；commit `4878b4ae` 单提交推送并 Contents API 复验（main HEAD 一致、两 blob 均存在）通过。
- 2026-09-15 08:30 (CST)：三项 PASS，**常规日**（仅写 digest，无关键异常、无跨项目升级）。
  - 对外发布物自检：self_scan --json `blocking_unsuppressed=0`、`stale_allowlist_entries=[]`、`ok=true`、no_execute/no_network=true；44 发现 / 20 抑制（全自指误报，逐源 blocking 均空：mcp-server/src 5 / guardrail-harness 9 / github-marketplace 3 / action_entrypoint 3），无未登记阻断、无漏报、允许清单无失效条目。
  - 线上存活：远端 health.json updated 2026-09-14T21:55:01Z（age 2.64h，FRESH，healthy 4/4）；aishield.tools 200 / 28.5KB；/api/v1/health 4.3.0 / 236 规则；线上 commit `73c67266` deployed_at 2026-09-14T08:57:26Z（~15.5h，FRESH）；main HEAD `46bdbda5` 领先 16 提交（日级漂移，Spine 11:17 CST 追平，非异常）。
  - 本地测试 `tests/run_all.py` **748/0/0/12 全绿**（较 09-14 的 745 +3），核心契约（良性零误报 + 恶意仍拦）成立。
  - 产出 `eco/reports/guard-2026-09-15.md` + digest 追加；commit `23e201bf` 单提交推送并 Contents API 复验（main HEAD 一致、两 blob 均存在）通过。
- 2026-09-14 08:30 (CST)：三项 PASS，**常规日**（仅写 digest，无关键异常、无跨项目升级）。
  - 对外发布物自检：self_scan --json `blocking_unsuppressed=0`、`stale_allowlist_entries=[]`、`ok=true`、no_execute/no_network=true；44 发现 / 20 抑制（全部自指误报，分布同 09-13：mcp-server/src 5 / guardrail-harness 9 / github-marketplace 3 / action_entrypoint 3），无未登记阻断、无漏报、允许清单无失效条目。
  - 线上存活：远端 health.json updated 2026-09-13T20:57:35Z（~3.5h，FRESH，改走 GitHub Contents API 因 raw.githubusercontent 偶发 HTTP 000）；aishield.tools 200 / 28.5KB；/api/v1/health 4.3.0 / 236 规则；线上 commit `566d8dc` deployed_at 2026-09-13T08:23:42Z（~16h，FRESH）；main HEAD `7b98246` 日级漂移（Spine 11:17 CST 追平，非异常）。
  - 本地测试 `tests/run_all.py` **745/0/0/12 全绿**（较 09-13 的 733 +12），核心契约（良性零误报 + 恶意仍拦）成立。
  - 产出 `eco/reports/guard-2026-09-14.md` + digest 追加；commit `6ac39287` 单提交推送并 Contents API 复验（main HEAD 一致、两文件 blob 均存在）通过。
- 2026-09-13 08:30 (CST)：三项 PASS，**常规日**（仅写 digest，无关键异常、无跨项目升级）。
  - 对外发布物自检：self_scan --json `blocking_unsuppressed=0`、`stale_allowlist_entries=[]`、`ok=true`、no_execute/no_network=true；44 发现全为自指误报按 (source,file,type) 精确消噪（mcp-server/src 5 / guardrail-harness 9 / github-marketplace 3 / action_entrypoint 3），无未登记阻断、无漏报、允许清单无失效条目。
  - 线上存活：远端 health.json updated 2026-09-12T20:40:52Z（~3.8h，FRESH）；aishield.tools 200 / 28.5KB；/api/v1/health 4.3.0 / 236 规则；线上 commit `81eb016a` deployed_at 2026-09-12T07:59:45Z（~16.5h，FRESH）；main HEAD `a79713e62b53` 日级漂移（Spine 11:17 CST 未运行，非异常）。
  - 本地测试 `tests/run_all.py` **733/0/0/12 全绿**（较 09-12 的 699 +34），核心契约（良性零误报 + 恶意仍拦）成立。
  - 产出 `eco/reports/guard-2026-09-13.md` + digest 追加；commit `4bf927be7489` 单提交推送并 Contents API 复验（两文件 HTTP 200、main HEAD 一致）通过。
- 2026-09-12 08:30 (CST)：三项 PASS，**常规日**（仅写 digest，无关键异常、无跨项目升级）。
  - 对外发布物自检：self_scan --json `blocking_unsuppressed=0`、`stale_allowlist_entries=[]`、`ok=true`、no_execute/no_network=true；44 发现全为自指误报按 (source,file,type) 精确消噪（mcp-server/src 5 / guardrail-harness 9 / github-marketplace 3 / action_entrypoint 3 等），无未登记阻断、无漏报、允许清单无失效条目。
  - 线上存活：远端 health.json updated 2026-09-11T21:04:29Z（~11.5h，FRESH）；aishield.tools 200 / 28.5KB；/api/v1/health 4.3.0 / 236 规则；线上 commit `85c1f91c` deployed_at 2026-09-11T08:08:07Z（~16h，FRESH）；main HEAD `4f14a5f4` 日级漂移（Spine 11:17 CST 追平，非异常）。
  - 本地测试 `tests/run_all.py` **699/0/0/12 全绿**，核心契约（良性零误报 + 恶意仍拦）成立。
  - 产出 `eco/reports/guard-2026-09-12.md` + digest 追加；commit `dcc951f5` 单提交推送并 Contents API 复验（两文件 HTTP 200、main HEAD 一致）通过。
- 2026-09-11 08:30 (CST)：三项 PASS，**常规日**（仅写 digest，无关键异常、无跨项目升级）。
  - 对外发布物自检：self_scan --json `blocking_unsuppressed=0`、`stale_allowlist_entries=[]`、`ok=true`、no_execute/no_network=true；44 发现全为自指误报按 (source,file,type) 精确消噪（mcp-server/src 5 / guardrail-harness 9 / github-marketplace 3 / action_entrypoint 3 等），无未登记阻断、无漏报。
  - 线上存活：远端 health.json updated 2026-09-10T20:59:14Z（3.5h，FRESH）；aishield.tools 200 / 28.5KB；/api/v1/health 4.3.0 / 236 规则；线上 commit `2e12c70b` = Spine #16 部署目标，deployed_at 2026-09-10T08:11:32Z；main HEAD `1dd08fb1` 落后 64 提交（post-spine 正常漂移，今日 ~16:05 CST Spine 追平）。
  - 本地测试 `tests/run_all.py` **699/0/0/12 全绿**（较 09-09 的 621 +78），核心契约（良性零误报 + 恶意仍拦）成立。
  - CI/Spine 侧：Spine #16 success、CI/CD #1059 success、Meta-Monitor #608 success；近 24h 9 次 CI/CD 短暂失败（09-10 推送风暴期）已转绿，信息性非升级。
  - 产出 `eco/reports/guard-2026-09-11.md` + digest 追加；commit `ebadb904` 单提交推送并 Contents API 复验（两文件 sha 一致）通过。
- 2026-09-09 08:30 (CST)：三项 PASS + CI 全绿，**常规日**（仅写 digest，无关键异常、无跨项目升级）。
  - 对外发布物自检：台账门禁 `verify_distribution.py` **5/5 通过**（评分 94–97，0 阻断）；台账外补扫（npm 源 / DSH / guardrail / github-marketplace / listings / 已上架 skill 等 10 目录）命中 **13 条 critical/high**，逐条与 09-07 基线（14）一致、全部为扫描器自指误报（index.ts 检测字样 / proxy_example.py 演示载荷 / action_entrypoint.py 只读 preflight），artifact 安全、未静默跳过、已留证；建议加演示标记消噪（非阻塞）。
  - 线上存活：aishield.tools 200 / 28.5KB；/api/v1/health 4.3.0 / 236 规则；线上 commit `b524162e` deployed_at 09-08T08:12:16Z（约 16h，<24h）；远端 health.json updated 09-08T21:16:20Z（约 3h，<24h）；main HEAD `6c89b8bb` 日级漂移正常。
  - 本地测试 `tests/run_all.py` **621/0/0/12 全绿**（+11 vs 09-08 的 610），核心契约（良性零误报 + 恶意仍拦）成立。
  - CI 侧挂起项闭环：**Spine #14（09-08 08:01Z）success**，已追平部署到 `b524162e`（与线上 commit 一致），昨日 #13 失败断言 5 验证通过；CI/CD #1039 / Meta-Monitor #593 均 success。
  - 产出 `eco/reports/guard-2026-09-09.md` + digest 追加；commit `c66c2783` 单提交推送并 Contents API 复验（sha256 一致）通过。
- 2026-09-08 08:34 (CST)：本地三项 PASS，**CI 侧 1 处异常已即时高亮**（非阻塞）。
  - 对外发布物自检：5/5 通过（评分 94–97，0 阻断，no_execute/no_network=true）。
  - 线上存活：aishield.tools 200 / 28.5KB；/api/v1/health 4.3.0 / 236 规则；
    线上 commit `a8201ff7` deployed_at 09-07T14:24:39Z；远端 health.json updated 09-07T21:36:48Z（<24h）。
  - 本地测试 610/0/0/12 全绿（+18 于 09-07 的 592）。
  - ⚠️ **AIShield Closed-Loop Spine #13 failure**（run 34099499303，09-07 16:14 CST）：
    Post-Deploy Verification Gate 断言 5 命中「磁盘=08a75eba ≠ 触发 run sha=08a986d5」，
    根因 VPS git fetch 失败 + tarball 兜底失效；门禁判红正确（非假绿）；
    09-07 22:20 CST 独立 Deploy #1017 追平线上到 a8201ff7；Meta-Monitor #589 拉分至 67/degraded。
    明日 11:17 CST Spine 若复红需排查代码同步通道根因。
  - 产出 `eco/reports/guard-2026-09-08.md` + digest 追加；commit `9a217e37` 单提交推送并 Contents API 复验通过。
- 2026-09-07 08:30 (CST)：三项全部 PASS，常规日（仅写 digest，无关键异常）。
  - 对外发布物自检：台账门禁 `verify_distribution.py` **5/5 通过**（评分 94–97，0 阻断）；**补扫台账外目录**（DSH 骨架 / guardrail-harness / github-marketplace / listings / npm 包源 mcp-server/src）命中 **14 条 critical/high**，逐条人工分诊**全部为扫描器自指误报**（proxy_example.py 演示被拦载荷、index.ts 工具描述含「越狱/零宽/exfil」检测字样、action_entrypoint.py 仅用 subprocess clone 待扫目标跑只读 preflight），artifact 安全、未静默跳过、已逐条留证。建议后续为 scanner 加演示标记/允许清单消噪（非阻塞待用户处置）。
  - 线上存活：aishield.tools 200（28.5KB）；/api/v1/health 4.3.0 / 228 规则；远端 health.json `updated` 2026-09-06T20:32:28Z（<24h）；线上 commit `08a75eba` 落后 main `a6c1eb63` 13 提交（祖先，日级漂移，今日 11:17 CST spine 追平）；CI/CD `34036775273`、Deploy `34022696367`、Self-Heal `34058304888` 全 success。
  - 本地测试 `tests/run_all.py` 592/0/0/12 全绿，核心契约（良性零误报 + 恶意仍拦）成立；CI 最近一次 CI/CD 同步 success。
  - 产出 `eco/reports/guard-2026-09-07.md` + digest；commit `80e1d94d` 单提交推送（_push_batch.py）并 Contents API 复验通过。
- 2026-09-06 09:32 (CST)：三项全部 PASS，常规日（仅写 digest，无关键异常）。
  - 对外发布物自检：5/5 通过，评分 94–97，0 阻断项；不变量 no_execute/no_network=true；agensi 线上 1.0.0≠源 1.1.0（信息性待覆盖）。
  - 线上存活：health.json updated 2026-09-05T20:29:54Z（<24h）；aishield.tools 200；v4.3.0 / 228 规则；CI/CD#1029 success；Spine#11 success；线上 commit 4c18b94b 落后 main d238c65d 14 提交（日级正常漂移，今日 11:17 CST spine 将追平）。
  - 本地测试 592/0/0/12 绿，核心契约（良性零误报 + 恶意仍拦）成立。
  - 产出 `eco/reports/guard-2026-09-06.md` + digest；commit `79096815` 推送并 Contents API 复验通过。
- 2026-09-04 08:30 (CST)：本地三项 PASS，**发现并修复关键异常（已即时高亮）**。
  - 对外发布物自检：5/5 通过，评分 94–97，0 阻断项。
  - 线上存活：远端 health.json updated 2026-09-03T21:08:55Z；aishield.tools 200；/api/v1/health v4.3.0 / 228 规则。**但线上 commit 停在 93fcd10c、deployed_at 2026-09-01，落后 main 3 天。**
  - 本地测试 592/0/12 绿，**但 CI 上一直红**：`test_life_science_papers_excluded` 失败，根因 `scripts/capability_gap.py` 本地 8-11 写的 12 条生命科学排除词从未推 main → spine `Verify Scanner Integrity` 失败 → 部署等 7 个下游 job 全 skipped。
  - 处置：commit `5df8c5f8` 推修复+报告并复验；CI run 33822550293 转全绿（9/9）。产出 `eco/reports/guard-2026-09-04.md`、digest `2026-09-04.md`。
  - **明日必做**：复验线上 commit/deployed_at 是否被 11:17 CST 的 spine 追平；若否，排查 deploy job 本身。
- 2026-09-03 08:30 (CST)：三项全部 PASS，无关键异常（常规日）。5/5 发布物通过；health.json 2026-09-02T21:08:59Z；测试 592/0/12；报告 commit db254257。
- 2026-09-02 08:30 (CST)：三项全部 PASS，常规日。5/5；health.json 2026-09-01T21:08:57Z；测试 590/0/12；commit c2b6094b。
- 2026-09-01 08:30 (CST)：三项全部 PASS，常规日。5/5；health.json 2026-08-31T21:31:35Z；测试 590/0/12；commit 68a497f5。

## 运行要点（可复用）
- 工具链：`python3 scripts/verify_distribution.py --json` → distribution gate；`curl --ssl-no-revoke --tlsv1.3` → 线上探测；`python3 tests/run_all.py` → 测试。
- **【2026-09-04 新增，重要】本地测试绿 ≠ CI 绿。守夜必须额外读 GitHub Actions：**
  `GET /repos/lm203688/aishield/actions/runs?per_page=20`，检查最近一次 `AIShield CI/CD` 与 `AIShield Closed-Loop Spine` 的 conclusion；failure 则拉 `/actions/runs/<id>/jobs` 找失败 step，再用 PAT 拉 `/actions/jobs/<job_id>/logs` 看断言文本。
  本机无 git 仓（推送走 Contents API），本地文件可能**领先**远端（改了没推）→ 本地假绿。定位法：算本地 git blob sha（`sha1('blob %d\0'%len + bytes)`）与 `GET /contents/<path>?ref=main` 的 sha 比对；全量扫描用 `GET /git/trees/<HEAD>?recursive=1`。
- **部署新鲜度断言**：`/api/v1/health` 的 `commit` 必须等于 main HEAD，`deployed_at` 应在近 24h。不等 = 部署链路被阻或进程陈旧（进程活着但代码旧，HTTP 200 掩盖之）。`.deploy_meta.json` 不在仓库（远端 404，部署时生成），别去 Contents API 找。
- 远程 health.json 必须走 GitHub Contents API（ref=main）读 `updated`，本地副本陈旧不可作判断。
- aishield.tools 用 `GET -o <工作区文件>` 探测（勿用 `-o /dev/null` 或 `-I`）。
- 推送：单文件 `scripts/gh_push.py "<msg>" <file>`；**多文件必用 `scripts/_push_batch.py`（单 commit，避免每文件触发一轮 workflow 风暴）**；推完 Contents API 复验 blob sha。
- spine cron = `17 3 * * *` UTC（11:17 CST），失败即当日整链终止，不会静默带坏产物继续。
- 常规日只写 digest 不发聊天；关键异常（测试转红/产物带洞/线上失活/**CI 或 spine 红灯**）须即时高亮。
