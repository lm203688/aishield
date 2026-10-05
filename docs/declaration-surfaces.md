# 公开声明面：为什么"文件是对的"不等于"服务是对的"

> 2026-10-05 实测触发。本文记录一类缺陷的形状与它的机械拦截，供后续改动参考。

## 一、现象

同一时刻，两句话都是真话：

```bash
$ curl -s https://aishield.tools/.well-known/agent-card.json | grep -o 'against [0-9]* MCP / [0-9]* skill'
against 235 MCP / 241 skill rule categories      # 权威值是 264 / 291

$ python scripts/rule_count_gate.py --check
✅ 全部一致，无漂移                                # exit 0
```

一个以"自称能力数量必须真实"为卖点的安全扫描器，自己的 agent 名片上写着两代之前的
规则数，而所有一致性检查都是绿的。

## 二、根因：验证面与服务面脱节

```
api/server.py:483   Trust API 分支   path == "/.well-known/agent-card.json"
                    → 提前 return，读 docs/.well-known/agent-card.json   ← 真正在服务
api/server.py:768   静态资产分支     path == "/.well-known/agent-card.json"
                    → 永远执行不到（先命中者胜）                        ← 死代码
scripts/rule_count_gate.py
                    _is_declared_surface() 对 docs/ 一律返回 False
                    （理由是"docs/ 根级文档是带日期的历史快照"）
                    → 真服务的那个文件被整体豁免
```

于是：**门禁扫的是一份永不服务的副本，真正服务出去的字节没有任何检查。**

这不是"某个正则写漏了"。版本门禁（`sync_version.py`）与规则数门禁
（`rule_count_gate.py`）的**验证对象都是文件**。只要服务路径与文件路径之间存在
哪怕一层间接——两处 `if` 的先后顺序、两个根目录各躺一份、一个不可达分支——
"文件正确"就推不出"服务正确"。

## 三、修复

### 3.1 单一事实源：`api/declaration_surface.py`

把"哪个 URL 由哪个文件服务"从**隐式 if 顺序**变成**显式数据**：

- `SERVED`：每个公开 URL → 服务文件 / 内容类型 / 真正的处理模块 / 版本字段路径
- `SHADOWS`：声明路径下存在、但不被任何路由服务的同名孪生文件，逐条写明身份
  （`mirror` / `superseded` / `leftover`）

刻意**不引入运行时耦合**：`server.py` / `trust_api.py` 保持原样，注册表是
**被验证的声明**而非控制流的一部分。声明与实现不符时门禁红，而不是悄悄按声明执行、
掩盖实现。

### 3.2 消除死代码与同 URL 双声明

`server.py` 中那个不可达的 agent-card 静态分支已删除。现在该 URL 在 `do_GET` 里
**只有一处声明**，该不变量由门禁以 AST 断言钉死。

### 3.3 验证对象上移：`scripts/declaration_surface_gate.py`

七道检查，前四道在仓库里，后三道在**服务出去之后**：

| # | 检查 | 拦什么 |
|---|------|--------|
| 1 | 注册表完整性 | 在册 URL 没有服务文件 |
| 2 | 孪生副本身份 | 两根下同名并存却身份不明（235/241 的温床） |
| 3 | 分派唯一性（AST） | 同一 URL 在同一分派函数里声明两次 → 后面的分支不可达 |
| 4 | 门禁覆盖闭合 | 对外声明规则数的文件逃出 `rule_count_gate` 覆盖面 |
| 5 | 运行时规则数断言 | **响应体**里的规则数 ≠ 权威值 |
| 6 | 运行时版本断言 | 响应体版本 ≠ `api.server:API_VERSION` |
| 7 | 运行时可达性 | 在册声明面实际 404 |

第 5~7 条是本门禁存在的理由：它们直调 handler 取真实字节，与规则数门禁**共用同一套
模式与同一份权威值**（第 5 条用的就是 `rule_count_gate.scan_text`）。

退出码：`0` 通过 / `1` 检出问题 / `2` 门禁自身异常。`2` 必须与 `1` 分开——
门禁自己坏掉却报"通过"，是假绿的第一层。

## 四、同源缺陷清单（全部由这套检查实测抓出）

| 缺口 | 为什么此前看不见 |
|------|------------------|
| `/api/v1/governance/policy` 的 `allow`/`deny`/`default_deny` 全部不可调用 | `do_POST` 里同路径被分派两次，后者不可达。请求会落到"策略包绑定"分支，把 `deny` 当 pack 名，返回 `unknown policy pack: `——**降级成误导性错误的安全控制**。模块级测试全绿，因为 `tests/test_governance.py` 只测 `runtime_governance` 的函数，从不从路由发请求 |
| `smithery.yaml` 写着 `238 MCP / 291 skill rules` | pair 模式要求大写 `Skill`，正文是小写 → 整个 pair 不匹配，只剩单值的 `291 skill rules` 被抓。`--sync` 便把 291 改对、把 238 原样留下，产出**半对文件**，而 238 因为不匹配任何模式，门禁随后一路绿灯 |
| `api/static/feeds.xml` 写着"227 条安全规则扫描" | `.xml` 不在 `rule_count_gate.TEXT_EXT` 里 → 整份文件不进扫描。漏的原因不是模式不全，而是**文件清单**本身 |
| robots.txt `Allow: /.well-known/security.txt`，而该路径 404 | 路由只实现了历史兼容路径 `/security.txt`；RFC 9116 的规范路径从未实现。对外"允许"了却服务不了 |

## 五、维护约定

改了公开声明面（`.well-known/*`、`/llms*.txt`、`/geo-faqs.json`、`/robots.txt`、
`/feeds.xml` 等）之后：

```bash
python scripts/rule_count_gate.py --check          # 文件里的数字
python scripts/declaration_surface_gate.py --check # 服务出去的数字
```

新增/移动声明面文件时，先改 `api/declaration_surface.py` 的 `SERVED`；
若在两个根下并存，必须在 `SHADOWS` 里写明身份，否则门禁红。
新增路由后，`do_GET`/`do_POST` 里同一个 URL 只允许出现一次。
