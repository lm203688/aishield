from pathlib import Path
from math import sqrt
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).resolve().parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

NAVY = "#14213D"
BLUE = "#2563EB"
TEAL = "#0F9D8A"
AMBER = "#D97706"
RED = "#C2413B"
LIGHT = "#F4F7FB"
MID = "#D8E1EE"
TEXT = "#263449"
MUTED = "#64748B"


def wilson(k, n, z=1.959963984540054):
    p = k / n
    d = 1 + z * z / n
    center = (p + z * z / (2 * n)) / d
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return center - half, center + half

print("Wilson 95% CI overall:", wilson(559, 593))
print("Wilson 95% upper FPR 0/517:", wilson(0, 517)[1])
print("Wilson 95% CI primary 66/66:", wilson(66, 66))
print("IPI recall:", 142 / 176)

# Figure 1: measured benchmark slices
labels = ["主范围 GHSA（66/66）", "配置面（12/12）", "总体（559/593）",
          "指令面（547/581）", "次范围 InjecAgent（493/527）", "间接提示注入家族（142/176）"]
values = [100.0, 100.0, 94.27, 94.15, 93.55, 80.68]
colors = [TEAL, TEAL, BLUE, BLUE, BLUE, AMBER]
fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=160)
fig.patch.set_facecolor("white")
ax.set_facecolor(LIGHT)
y = list(range(len(labels)))
bars = ax.barh(y, values, color=colors, height=0.58)
ax.set_yticks(y, labels=labels, fontsize=11, color=TEXT)
ax.invert_yaxis()
ax.set_xlim(0, 108)
ax.set_xticks([0, 20, 40, 60, 80, 100])
ax.set_xlabel("检出召回率（%）", fontsize=11, color=TEXT)
ax.set_title("AIShield 外部语料实测：总体表现与集中漏检点", loc="left",
             fontsize=18, fontweight="bold", color=NAVY, pad=22)
ax.text(0, 1.02, "检测门槛：至少 1 条 high/critical；小样本分组不代表总体上限",
        transform=ax.transAxes, fontsize=10, color=MUTED)
for bar, value in zip(bars, values):
    ax.text(value + 1.2, bar.get_y() + bar.get_height()/2, f"{value:.2f}%",
            va="center", fontsize=11, fontweight="bold", color=TEXT)
ax.grid(axis="x", color=MID, linewidth=0.8)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis="both", length=0, colors=MUTED)
fig.text(0.075, 0.02, "负样本观察到 0/517 误报；这是样本内结果，不等于真实误报率为 0。",
         fontsize=10, color=MUTED)
plt.tight_layout(rect=(0.04, 0.06, 0.98, 0.95))
fig.savefig(OUT / "aishield-benchmark-2026-10-27.png", bbox_inches="tight")
plt.close(fig)

# Figure 2: proposed trust architecture
fig, ax = plt.subplots(figsize=(15, 8.6), dpi=160)
fig.patch.set_facecolor("white")
ax.set_xlim(0, 15)
ax.set_ylim(0, 8.6)
ax.axis("off")
ax.text(0.5, 8.12, "目标架构：离线可验证的 Agent 供应链与行动信任层",
        fontsize=20, fontweight="bold", color=NAVY)
ax.text(0.5, 7.69, "静态扫描与运行时控制共用安全图、策略模型和证据语义；PEP 必须不可绕过",
        fontsize=11, color=MUTED)


def box(x, y, w, h, title, body, color=BLUE, fill="white"):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.025,rounding_size=0.12",
                       linewidth=1.5, edgecolor=color, facecolor=fill)
    ax.add_patch(p)
    ax.text(x + 0.18, y + h - 0.34, title, fontsize=12, fontweight="bold", color=color)
    ax.text(x + 0.18, y + h - 0.73, body, fontsize=9.6, color=TEXT, va="top", linespacing=1.45)
    return p


def arrow(x1, y1, x2, y2, color=MUTED, style="-|>"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=14, linewidth=1.5, color=color,
                                 connectionstyle="arc3,rad=0"))

box(0.5, 5.55, 2.45, 1.45, "资产与发现", "MCP / Skill / Prompt\nA2A / 依赖 / 配置", BLUE, "#EFF6FF")
box(3.45, 5.55, 2.45, 1.45, "静态与动态检测", "no-spawn 静态扫描\n沙箱符合性与红队", TEAL, "#ECFDF5")
box(6.4, 5.55, 2.45, 1.45, "统一安全图", "Artifact—Identity\nCapability—Data—Action", NAVY, "#F1F5F9")
box(9.35, 5.55, 2.45, 1.45, "策略决策 PDP", "确定性规则 / ACS\n风险、上下文、撤销", AMBER, "#FFFBEB")
box(12.3, 5.55, 2.2, 1.45, "执行前 PEP", "allow / deny\nescalate / degrade", RED, "#FEF2F2")
for x1, x2 in [(2.95, 3.45), (5.9, 6.4), (8.85, 9.35), (11.8, 12.3)]:
    arrow(x1, 6.28, x2, 6.28)

box(0.5, 2.82, 2.45, 1.5, "六类核心对象 ①②", "Artifact：资产与版本\nIdentity：主体与凭证", BLUE)
box(3.45, 2.82, 2.45, 1.5, "六类核心对象 ③④", "Intent：人类授权边界\nPolicy：可判定约束", TEAL)
box(6.4, 2.82, 2.45, 1.5, "六类核心对象 ⑤⑥", "Action：一次具体调用\nEvidence：可验证据", NAVY)
box(9.35, 2.82, 5.15, 1.5, "互操作与证据出口",
    "OpenTelemetry GenAI spans · SARIF · SBOM / SLSA · 签名 Attestation\n默认脱敏；原始内容本地保留；跨组织只交换可验证证明", AMBER, "#FFFBEB")
arrow(7.62, 5.55, 7.62, 4.32)
arrow(10.57, 5.55, 10.57, 4.32)

box(0.5, 0.48, 4.25, 1.35, "隐私与安全边界", "源码与凭证不出机；扫描不执行被测配置\n在线探测只进入显式批准的隔离环境", TEAL, "#ECFDF5")
box(5.25, 0.48, 4.25, 1.35, "关键运行时不变量", "委托权限单调收敛；过期与撤销 fail-closed\n每次放行都能回到主体、意图、策略与证据", RED, "#FEF2F2")
box(10, 0.48, 4.5, 1.35, "差异化而非重造企业套件", "离线开发者和 CI 是入口； federated 控制面后置\n以可复现评估和可移植证明建立信任", BLUE, "#EFF6FF")
arrow(13.4, 5.55, 13.4, 4.32)
arrow(12.3, 5.0, 4.75, 1.83, TEAL)
ax.text(7.45, 2.37, "反馈：漂移、撤销、基准与策略更新", fontsize=10, color=TEAL, ha="center")

plt.tight_layout()
fig.savefig(OUT / "aishield-target-architecture-2026-10-27.png", bbox_inches="tight")
plt.close(fig)
