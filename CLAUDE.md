# CLAUDE.md

Agent 原生项目手册见 **[AGENTS.md](./AGENTS.md)** —— 架构、核心不变量、贡献约定（含范围纪律）都在那里。

## 硬不变量（违背即 bug，先读再动）

1. **扫描器绝不 spawn 被扫配置里的命令** —— 被扫内容只当字符串读取、做正则/语义匹配。
   自证：`python scripts/prove_isolation.py`
2. **代码与配置绝不上传云端** —— 本地优先、零依赖、可离线。
3. **勿引用过期规则计数**（227/215/133/228）。真值看 `/api/v1/health` 的 `rules_breakdown`；
   当前 256 = 静态 229 + 情报 8 + 雷达 19。
4. **本地绿 ≠ CI 绿**；多文件推送走 `scripts/_push_batch.py`，推完 API 复验。

## 一键启动

```
git clone https://github.com/lm203688/aishield.git && cd aishield
python -m venv .venv && source .venv/bin/activate && pip install pytest
python tests/run_all.py
python scripts/prove_isolation.py
```
