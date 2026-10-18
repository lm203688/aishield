"""核对《AIShield 项目查缺报告_2026-10-17.md》14 项任务的真实完成状态。

每项都直接读文件系统/AST 验证，不依赖报告自述或 git log 措辞。
输出 [DONE]/[PART]/[TODO] + 证据。
"""
import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
results = []


def rec(pid, status, title, evidence):
    results.append((pid, status, title, evidence))


def read(p, default=None):
    try:
        return (ROOT / p).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return default


def exists(p):
    return (ROOT / p).exists()


def grep_paths(pat, globs=("**/*.py", "**/*.md", "**/*.yml", "**/*.yaml", "**/*.json", "**/*.txt"), limit=40):
    out = []
    rx = re.compile(pat)
    for g in globs:
        for f in ROOT.glob(g):
            if ".git" in f.parts or ".workbuddy" in f.parts:
                continue
            try:
                t = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for i, line in enumerate(t.splitlines(), 1):
                if rx.search(line):
                    out.append((str(f.relative_to(ROOT)), i, line.strip()[:110]))
                    if len(out) >= limit:
                        return out
    return out


def crlf_files():
    n = 0
    examples = []
    for f in ROOT.rglob("*"):
        if not f.is_file():
            continue
        if any(skip in f.parts for skip in (".git", ".workbuddy", "node_modules", ".hypothesis")):
            continue
        if f.suffix.lower() in (".png", ".jpg", ".gif", ".zip", ".gz", ".pdf", ".woff", ".ttf"):
            continue
        try:
            b = f.read_bytes()
        except Exception:
            continue
        if b"\r\n" in b:
            n += 1
            if len(examples) < 8:
                examples.append(str(f.relative_to(ROOT)))
    return n, examples


# ============ P0 ============
# 1. CRLF 全量归一化 + .gitattributes 行尾宪法
n_crlf, crlf_ex = crlf_files()
ga = read(".gitattributes", "")
ga_ok = ("eol=lf" in ga and "text=auto" in ga)
rec("P0-1", "DONE" if (n_crlf == 0 and ga_ok) else ("PART" if ga_ok else "TODO"),
    "CRLF 归一化 + .gitattributes 行尾宪法",
    f"含 CRLF 文件 {n_crlf} 个；.gitattributes 行尾策略={'有' if ga_ok else '缺失'}；例: {crlf_ex}")

# 2. AGENTS.md 自身事实错误（npm 版本 + sync_readme_counts）
ag = read("AGENTS.md", "")
bad_ver = "4.8.3" in ag
bad_script = "sync_readme_counts" in ag
ag_ver_ok = "4.11.0" in ag
# 检查 rule_count_gate.py 是否真存在
rcc_exists = exists("scripts/rule_count_gate.py")
rec("P0-2", "DONE" if (not bad_ver and not bad_script and ag_ver_ok and rcc_exists) else "TODO",
    "AGENTS.md 版本号 + 脚本引用纠正",
    f"含 4.8.3={'有' if bad_ver else '无'}; 含 4.11.0={'有' if ag_ver_ok else '无'}; "
    f"引用 sync_readme_counts={'有' if bad_script else '无'}; rule_count_gate.py 存在={'是' if rcc_exists else '否'}")

# 3. hypothesis 声明 + e2e/quick_test 移出 pytest 收集
pt = read("pyproject.toml", "")
setup = read("setup.py", "")
prep = read(".github/actions/prepare-tests/action.yml", "")
qt_exists = exists("tests/quick_test.py")
e2e_exists = exists("tests/e2e_test.py")
hyp_declared = "hypothesis" in pt or "hypothesis" in setup or "hypothesis" in prep
rec("P0-3", "DONE" if (hyp_declared and not qt_exists and not e2e_exists) else "PART",
    "hypothesis 声明 + e2e/quick_test 移出收集",
    f"hypothesis 声明位置={'有' if hyp_declared else '无'}; "
    f"quick_test.py 存在={'是' if qt_exists else '否'}; e2e_test.py 存在={'是' if e2e_exists else '否'}")

# 4. E9 扩到 .github/actions + 孤儿 action 检测
vw = read("scripts/validate_workflows.py", "")
e9_actions = ".github/actions" in vw or "actions/" in vw
rec("P0-4", "DONE" if e9_actions else "TODO",
    "E9 门禁覆盖 .github/actions",
    f"validate_workflows.py 提及 .github/actions={'有' if e9_actions else '无'}")

# ============ P1 ============
# 5. 规则数单一出口（删手写 264/235/291）
hard_coded = grep_paths(r"\b(264|235|291)\b", globs=("api/**/*.py", "api/**/*.json", "mcp-server/**/README.md", "README*.md"), limit=60)
# 排除 rule_count_gate.py 与测试
hot = [(p, i, l) for p, i, l in hard_coded if "rule_count_gate" not in p and not p.startswith("tests/")]
rec("P1-5", "DONE" if not hot else "PART",
    "规则数单一出口（消灭手写 264/235/291）",
    f"手写数字残留 {len(hot)} 处: " + "; ".join(f"{p}:{i}" for p, i, _ in hot[:12]))

# 6. 声明面门禁盲区（docs/ 前缀豁免 + server 启动自检）
ds = read("api/declaration_surface.py", "")
srv = read("api/server.py", "")
gate_no_exempt = "_is_declared_surface" in ds and "豁免" in ds
startup_assert = "声明" in srv and ("sys.exit" in srv or "assert" in srv)
rec("P1-6", "TODO" if not (gate_no_exempt and startup_assert) else "PART",
    "声明面门禁盲区关闭 + 启动自检",
    f"declaration_surface 有豁免注释={'有' if gate_no_exempt else '无'}; "
    f"server 启动自检断言={'有' if startup_assert else '无'}")

# 7. 依赖钉版
render = read("render.yaml", "")
swallow = "; true" in render or "2>/dev/null" in render
install_req_empty = "install_requires=[]" in setup or "install_requires = []" in setup
cryptography_pinned = re.search(r'cryptography==\d', prep + setup + pt)
swallow_type = "有" if swallow else "无"
rec("P1-7", "DONE" if (cryptography_pinned and not swallow) else "PART",
    "依赖钉版 + 删除 render.yaml 吞错",
    f"cryptography 钉版={'有' if cryptography_pinned else '无'}; "
    f"render.yaml 吞错={swallow_type}; "
    f"setup.py install_requires 空列表={'是' if install_req_empty else '否'}")

# ============ P2 ============
# 8. published.json 真台账
pub = read("distribution/published.json")
pub_ok = False
pub_ev = ""
if pub:
    try:
        d = json.loads(pub)
        entries = d.get("entries", [])
        live = [e for e in entries if e.get("status") in ("live", "staging") and e.get("url")]
        pub_ok = bool(entries) and all(e.get("url") for e in entries)
        pub_ev = f"updated={d.get('updated')}; entries={len(entries)}; 有url+status={len(live)}"
    except Exception as e:
        pub_ev = f"解析失败 {e}"
else:
    pub_ev = "文件不存在"
rec("P2-8", "DONE" if pub_ok else "TODO", "published.json 真台账", pub_ev)

# 9. 根 llms.txt + 根 .well-known/agent.json
llms_root = ROOT / "llms.txt"
llms_size = llms_root.stat().st_size if llms_root.exists() else 0
wk_root = (ROOT / ".well-known" / "agent.json").exists()
rec("P2-9", "DONE" if (llms_size > 100 and wk_root) else "PART",
    "根 llms.txt + 根 .well-known/agent.json",
    f"根 llms.txt 大小={llms_size}B; 根 .well-known/agent.json={'有' if wk_root else '无'}")

# 10. 英文文档 3 篇 + 文档链接门禁
en_dir = ROOT / "docs" / "en"
en_count = len(list(en_dir.glob("*.md"))) if en_dir.exists() else 0
link_gate = exists("scripts/check_doc_links.py")
rec("P2-10", "DONE" if (en_count >= 3 and link_gate) else "PART",
    "英文文档 3 篇 + check_doc_links.py",
    f"docs/en 篇数={en_count}; check_doc_links.py={'有' if link_gate else '无'}")

# ============ P3 ============
# 11. neuro_symbolic_probe NotImplementedError
nsp = read("scanner/neuro_symbolic_probe.py", "")
n_nie = nsp.count("NotImplementedError")
rec("P3-11", "DONE" if n_nie == 0 else "TODO",
    "neuro_symbolic_probe 去空壳",
    f"NotImplementedError 出现 {n_nie} 次")

# 12. arxiv_to_rule / tech_radar 占位清零
def placeholder_count(p):
    t = read(p, "")
    if not t:
        return -1
    return len(re.findall(r"(?i)\b(TODO|FIXME|占位|stub|placeholder|mock|pass\s*$|NotImplemented)\b", t))
ax = placeholder_count("scripts/arxiv_to_rule.py")
tr = placeholder_count("scripts/tech_radar.py")
rec("P3-12", "DONE" if (ax == 0 and tr == 0) else "TODO",
    "arxiv_to_rule / tech_radar 占位清零",
    f"arxiv_to_rule 占位={ax}; tech_radar 占位={tr}")

# 13. 运行时状态出 git + 原子写 + 文件锁
gi = read(".gitignore", "")
state_ignored = "data/state" in gi or "api/data" in gi
tracked_state = subprocess.run(
    ["git", "ls-files", "data/state/", "api/data/"], capture_output=True, text=True).stdout.split()
tracked_state = [x for x in tracked_state if x.strip()]
atomic = []
for f in ("api/utils.py", "scanner/utils.py"):
    t = read(f, "")
    if "os.replace" in t or "atomic" in t.lower():
        atomic.append(f)
flock = subprocess.run(
    ["git", "grep", "-l", "fcntl\\|msvcrt\\|filelock"], capture_output=True, text=True).stdout.split()
flock = [x for x in flock if x.strip()]
rec("P3-13", "DONE" if (state_ignored and not tracked_state and atomic) else "PART",
    "运行时状态出 git + 原子写 + 文件锁",
    f".gitignore 含 data/state|api/data={'有' if state_ignored else '无'}; "
    f"git 跟踪的 state 文件 {len(tracked_state)} 个; 原子写={atomic or '无'}; "
    f"文件锁={flock[:3] or '无'}")

# 14. 文档收口（WIP 文档 + 根报告 md 归档）
wip = 0
wip_ex = []
for f in (ROOT / "docs").rglob("*.md"):
    t = f.read_text(encoding="utf-8", errors="replace")
    if re.search(r"(?i)\b(WIP|草稿|待写|TBD|占位|待补充)\b", t):
        wip += 1
        if len(wip_ex) < 6:
            wip_ex.append(str(f.relative_to(ROOT)))
root_reports = [p for p in ROOT.glob("*.md") if "报告" in p.name or "report" in p.name.lower()]
rec("P3-14", "TODO" if (wip > 0 or root_reports) else "DONE",
    "文档收口（WIP 收口 + 根报告归档）",
    f"docs/ 含 WIP 标记 {wip} 篇 (例: {wip_ex}); 根目录报告类 md {len(root_reports)} 个 "
    f"({', '.join(p.name for p in root_reports[:6])})")

# ============ 输出 ============
order = {"DONE": 0, "PART": 1, "TODO": 2}
print("=" * 92)
print("AIShield 查缺报告 14 项任务 · 真实完成状态核对")
print("=" * 92)
for pid, st, title, ev in sorted(results, key=lambda r: (order[r[1]], r[0])):
    print(f"[{st:4}] {pid:6} {title}")
    print(f"       {ev}")
print("-" * 92)
from collections import Counter
c = Counter(r[1] for r in results)
print(f"合计：DONE {c['DONE']} / PART {c['PART']} / TODO {c['TODO']}  （共 {len(results)} 项）")
