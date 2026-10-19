#!/usr/bin/env python3
"""plot_fig1.py — GC-CHE 版 Fig 1 三联图（仿 CHE/analysis/ 手稿原版式）。

数据：同目录的 harvest_ladder.csv / harvest_ledger.csv。
版式：(a) EG_Ox 纯电化学台阶；(b) OER（*OOH 解离作废，*O 直接到 O₂，y 轴分段）；(c) HER。
0.0V = CHE 线性外推（Ω 未在 0V 计算，残差 0.03–0.1 eV 量级，见 harvest.py ladder 自检）。
热化学支路（*CH2OHCOO+*H → *CH2OHCOOH，+0.25/+0.16 eV）与动力学标注（barrier/RDS）
均不入图；前者数值在 harvest_ladder.csv，后者待恒电势势垒重算。
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

ROOT = Path(__file__).resolve().parent
LADDER = ROOT / "harvest_ladder.csv"
LEDGER = ROOT / "harvest_ledger.csv"

C04, C09, C00 = "#2E75B6", "#C00000", "#595959"  # 0.4V 蓝 / 0.9V 红 / 0V 灰
POT = [("0.0 V vs RHE", C00, "-", 2.2),
       ("0.4 V vs RHE", C04, "-", 2.4),
       ("0.9 V vs RHE", C09, "-", 2.4)]

# ---- 读数 ----
ladder = {}
with LADDER.open() as f:
    for r in csv.DictReader(f):
        ladder[(r["section"], r["step"], r["U"])] = float(r["dG_eV"])
        ladder[(r["section"], r["step"], "n_e")] = int(r["n_e"])
led = {}
with LEDGER.open() as f:
    for r in csv.DictReader(f):
        led[(r["species"], r["U"])] = float(r["G_phi"])


def g04(sec, sp):
    return ladder[(sec, sp, "0.4V")]


def series(sec, sp):
    """三个电位的 ΔG：0.4/0.9 实测，0V = dG(0.4) − n_e·0.4 外推。"""
    ne = ladder[(sec, sp, "n_e")]
    return {"0.0V": g04(sec, sp) - ne * 0.4,
            "0.4V": g04(sec, sp),
            "0.9V": ladder[(sec, sp, "0.9V")]}


# pos6 态 *CH2OHCOO+*H（C2H4O3，nH=4, nW=1，与 *CH2OHCOOH 同参考系累计）
def pair_cum(u_name):
    u = float(u_name.rstrip("V"))
    return (led[("_ch2ohcoo+_h", u_name)] - led[("slab", u_name)]
            - led[("HOCH2CH2OH", "neutral")] - led[("H2O", "neutral")]
            + 2.0 * led[("H2", "neutral")] - 4 * u)


PAIR = {"0.4V": pair_cum("0.4V"), "0.9V": pair_cum("0.9V")}
PAIR["0.0V"] = PAIR["0.4V"] + 4 * 0.4  # nH=4 外推


def rung(ax, x, y, color, ls, lw, w=0.36):
    ax.plot([x - w, x + w], [y, y], color=color, ls=ls, lw=lw,
            solid_capstyle="butt", zorder=3)


def conn(ax, x0, y0, x1, y1, color, w=0.36):
    ax.plot([x0 + w, x1 - w], [y0, y1], color=color, ls="--", lw=0.8,
            alpha=0.45, zorder=1)


def val(ax, x, y, s, color, dy=0.10, fs=8):
    return ax.text(x, y + dy, f"{s:.2f}", ha="center", va="bottom", fontsize=fs,
                   color=color, fontweight="bold", zorder=4)


PURPLE = "#7030A0"


def darrow(ax, x0, y0, x1, y1, lw=1.0, ms=10):
    """紫色有向虚线箭头（shrink=0，端到端）。"""
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=2,
                arrowprops=dict(arrowstyle="-|>", color=PURPLE, lw=lw, ls="--",
                                shrinkA=0, shrinkB=0, mutation_scale=ms))


def panel_axes(ax, ylab):
    ax.set_xlabel("Reaction Coordinates", fontsize=13)
    if ylab:
        ax.set_ylabel("Free Energy (eV)", fontsize=13)
    ax.set_xticks([])
    for sp in ax.spines.values():
        sp.set_linewidth(1.3)


def letter(ax, s):
    ax.text(-0.06, 1.03, s, transform=ax.transAxes, fontsize=12,
            fontweight="bold", va="bottom", ha="left")


R_EDGE = 0.04  # 边距比 r = (rung边缘到边框距离)/(x轴总长)，三个子图共用此值


def xlim_edge(n, w, r=R_EDGE):
    """末态 x=n、rung 半宽 w 时，使 左距/L = 右距/L = r 的 xlim。"""
    e = r * (n + 2 * w) / (1 - 2 * r)
    return (-(w + e), n + w + e)


def main():
    eg = [("start", "*+HOCH$_2$CH$_2$OH"),
          ("ch2oh_choh", "*CH$_2$OHCHOH"),
          ("ch2oh_coh", "*CH$_2$OHCOH"),
          ("ch2oh_co", "*CH$_2$OHCO"),
          ("_ch2ohcooh", "*CH$_2$OHCOOH"),
          ("ch2ohco_o_", "*CH$_2$OHCOO"),
          ("pair", "*CH$_2$OHCOO+*H"),
          ("acid2", "*CH$_2$OHCOOH")]
    eg_y = {"start": {"0.0V": 0.0, "0.4V": 0.0, "0.9V": 0.0}, "pair": PAIR}
    for sp in ("ch2oh_choh", "ch2oh_coh", "ch2oh_co", "_ch2ohcooh", "ch2ohco_o_"):
        eg_y[sp] = series("EG_Ox", sp)
    eg_y["acid2"] = dict(eg_y["_ch2ohcooh"])  # pos7 = 同一态，数值与 pos4 一致

    oer = [("start", "*+H$_2$O"),
           ("_OH", "*OH\n+(H$^+$+e$^-$)"),
           ("_O", "*O\n+2(H$^+$+e$^-$)"),
           ("O2", "O$_2$\n+4(H$^+$+e$^-$)")]
    oer_y = {"start": {"0.0V": 0.0, "0.4V": 0.0, "0.9V": 0.0},
             "_OH": series("OER", "_OH"), "_O": series("OER", "_O"),
             "O2": series("OER", "O2")}

    her_y = {"start": {"0.0V": 0.0, "0.4V": 0.0, "0.9V": 0.0}, "_H": series("HER", "_H")}

    fig = plt.figure(figsize=(12.6, 5.4))
    gs = fig.add_gridspec(2, 2, width_ratios=[2.35, 1.0], height_ratios=[1.5, 0.8],
                          wspace=0.16, hspace=0.42, left=0.07, right=0.985, top=0.93, bottom=0.10)
    axa = fig.add_subplot(gs[:, 0])
    gs_b = gs[0, 1].subgridspec(2, 1, height_ratios=[1.0, 1.6], hspace=0.08)
    axb_top = fig.add_subplot(gs_b[0])
    axb = fig.add_subplot(gs_b[1], sharex=axb_top)
    axc = fig.add_subplot(gs[1, 1])

    # ---- (a) EG_Ox ----
    axa.set_ylim(-4.9, 1.35)
    axa.set_xlim(*xlim_edge(7, 0.36))
    # RDS 色块（复刻原版小巧思）：浅红=氧化过程(0.9V) RDS 区 pos3-4；浅蓝=还原过程(0.4V) RDS 区 pos5-7
    axa.add_patch(plt.Rectangle((2.62, -4.9), 1.88, 6.25, fc="#F6D2D2", ec="#808080", lw=0.8, zorder=0))
    axa.add_patch(plt.Rectangle((4.5, -4.9), xlim_edge(7, 0.36)[1] - 4.5, 6.25, fc="#D2E2F3", ec="#808080", lw=0.8, zorder=0))
    axa.text(3.56, -4.78, "RDS under\noxidation process", ha="center", va="bottom",
             fontsize=8, color="#C00000", fontweight="bold", zorder=2)
    axa.text(6.1, -4.78, "RDS under\nreduction process", ha="center", va="bottom",
             fontsize=8, color="#2E75B6", fontweight="bold", zorder=2)
    labels_a, labels_b, labels_c = [], [], []
    vals_a, vals_b, vals_b_top, vals_c = [], [], [], []  # (Text, y_rung)，供 R_VAL 统一摆放
    for (label, color, ls, lw) in POT:
        uname = label.split(" ")[0] + "V"
        prev = None
        for i, (sp, _) in enumerate(eg):
            y = eg_y[sp][uname]
            rung(axa, i, y, color, ls, lw)
            if prev is not None:
                conn(axa, i - 1, prev, i, y, color)
            prev = y
            if uname == "0.0V":
                labels_a.append(axa.text(i, 1.02, eg[i][1], ha="center", va="bottom",
                                         fontsize=7.5, fontweight="bold", zorder=4))
            if not (sp == "start"):
                vals_a.append((val(axa, i, y, y, color, dy=0.10, fs=11), y))
            elif uname == "0.0V":
                vals_a.append((val(axa, 0, 0.0, 0.0, "#000000", dy=0.10, fs=11), 0.0))
    handles = [plt.Line2D([0], [0], color=c, ls=ls, lw=lw) for _, c, ls, lw in POT]
    rung(axa, 0, 0.0, C00, "-", 2.2)  # state[0] 灰色覆盖蓝/红
    # ---- 电位切换路径（紫色有向虚线）----
    y09 = [eg_y[sp]["0.9V"] for sp, _ in eg]
    y04 = [eg_y[sp]["0.4V"] for sp, _ in eg]
    off = -0.12  # 沿路径下方一点点
    dx = 0.08    # 紫色 rung 相对参考 rung 的系统性左移（右缘小 δ；非段首态左缘也小 δ）

    def purple_rung(i, y, first, s, align_right=False):
        xl = i - 0.36 + (0 if first else s * dx)
        xr = i + 0.36 + (0 if align_right else s * dx)
        axa.plot([xl, xr], [y + off] * 2, color=PURPLE, ls="--", lw=1.0, zorder=2)

    # state0→5 沿 0.9V（s=-1 左移；state5 右缘与 0.9V rung 对齐）
    for a in range(5):
        purple_rung(a, y09[a], first=(a == 0), s=-1)
        darrow(axa, a + 0.36 - dx, y09[a] + off, a + 1 - 0.36 - dx, y09[a + 1] + off)
    purple_rung(5, y09[5], first=False, s=-1, align_right=True)
    # state5：0.9V → 0.4V 切换箭头（起点在 "-4.33" 标签上方，终点 0.4V 紫线中心下方一点，严格垂直）
    xc = ((5 - 0.36) + (5 + 0.36 + dx)) / 2
    darrow(axa, xc, y09[5] + 0.45, xc, y04[5] + off - 0.05)
    axa.text(xc + 0.15, (y09[5] + y04[5]) / 2, "Potential Switching",
             ha="left", va="center", fontsize=9, color=PURPLE, fontweight="bold", zorder=4)
    # state5→7 沿 0.4V（s=+1 右移，规则反转；state7 右缘与 0.4V rung 对齐）
    for a in range(5, 7):
        purple_rung(a, y04[a], first=(a == 5), s=1)
        darrow(axa, a + 0.36 + dx, y04[a] + off, a + 1 - 0.36 + dx, y04[a + 1] + off)
    purple_rung(7, y04[7], first=False, s=1, align_right=True)
    axa.legend(handles, [l for l, *_ in POT], loc="lower left", fontsize=14, frameon=False)
    panel_axes(axa, True)
    letter(axa, "(a)")

    # ---- (b) OER（*OOH 解离作废；*O 直接到 O₂；y 轴在 1.65–2.75 eV 断开）----
    y_break_lo, y_break_hi = 1.65, 2.75
    axb.set_ylim(-1.05, y_break_lo)
    axb_top.set_ylim(y_break_hi, 6.10)
    axb.set_yticks([-1, 0, 1])
    axb_top.set_yticks([3, 4, 5])
    axb.set_xlim(*xlim_edge(3, 0.30))
    okeys = [k for k, _ in oer]
    for (label, color, ls, lw) in POT:
        uname = label.split(" ")[0] + "V"
        prev = None
        for i, k in enumerate(okeys):
            y = oer_y[k][uname]
            for ax in (axb, axb_top):
                rung(ax, i, y, color, ls, lw, w=0.30)
                if prev is not None:
                    conn(ax, i - 1, prev, i, y, color, w=0.30)
            prev = y
            if k != "start":
                target = axb_top if y > y_break_lo else axb
                if y > 4.5:
                    # 4.92 eV 标签放在 rung 下方，避开 O₂ 物种标签
                    t = val(target, i, y, y, color, dy=-0.37, fs=10)
                    t.set_va("top")
                else:
                    t = val(target, i, y, y, color, dy=0.12, fs=10)
                    (vals_b_top if target is axb_top else vals_b).append((t, y))
    vals_b.append((val(axb, 0, 0.0, 0.0, "#000000", dy=0.12, fs=10), 0.0))
    rung(axb, 0, 0.0, C00, "-", 2.2, w=0.30)  # state[0] 灰色覆盖蓝/红
    for i, (k, lab) in enumerate(oer):
        labels_b.append(axb_top.text(i, 5.90, lab, ha="center", va="top",
                                     fontsize=7.0, fontweight="bold", linespacing=1.15))
    # 断轴：隐藏相邻边框，画折断线
    axb.spines["top"].set_visible(False)
    axb_top.spines["bottom"].set_visible(False)
    axb.tick_params(axis="x", bottom=False, labelbottom=False)
    axb_top.tick_params(axis="x", bottom=False, labelbottom=False)
    d = 0.015
    for ax, y0 in ((axb, 1.0), (axb_top, 0.0)):
        ax.plot((-d, +d), (y0 - d, y0 + d), transform=ax.transAxes,
                color="k", clip_on=False, lw=1.3)
        ax.plot((1 - d, 1 + d), (y0 - d, y0 + d), transform=ax.transAxes,
                color="k", clip_on=False, lw=1.3)
    panel_axes(axb, False)
    for sp in axb_top.spines.values():
        sp.set_linewidth(1.3)
    axb_top.set_xticks([])
    p_lo, p_hi = axb.get_position(), axb_top.get_position()
    fig.text(p_lo.x0 - 0.032, (p_lo.y0 + p_hi.y1) / 2, "Free Energy (eV)",
             rotation=90, va="center", ha="center", fontsize=13)
    letter(axb_top, "(b)")
    # ---- (c) HER ----
    axc.set_ylim(-0.72, 0.95)
    axc.set_xlim(*xlim_edge(1, 0.18))
    for (label, color, ls, lw) in POT:
        uname = label.split(" ")[0] + "V"
        conn(axc, 0, 0.0, 1, her_y["_H"][uname], color, w=0.18)
        rung(axc, 0, 0.0, color, ls, lw, w=0.18)
        rung(axc, 1, her_y["_H"][uname], color, ls, lw, w=0.18)
        vals_c.append((val(axc, 1, her_y["_H"][uname], her_y["_H"][uname], color, dy=0.05, fs=11),
                       her_y["_H"][uname]))
    vals_c.append((val(axc, 0, 0.0, 0.0, "#000000", dy=0.05, fs=11), 0.0))
    rung(axc, 0, 0.0, C00, "-", 2.2, w=0.18)  # state[0] 灰色覆盖蓝/红
    labels_c.append(axc.text(0, 0.68, "*+(H$^+$+e$^-$)", ha="center", fontsize=8, fontweight="bold"))
    labels_c.append(axc.text(1, 0.68, "*H", ha="center", fontsize=8, fontweight="bold"))
    panel_axes(axc, True)
    axc.yaxis.set_label_coords(-0.115, 0.5)  # 与 (b) 的 ylabel 对齐同一 x
    axc.yaxis.set_major_locator(MultipleLocator(0.5))  # 分度值 0.5
    letter(axc, "(c)")

    # 三个子图“顶部留白比”统一（以 (a) 为基准）：(ymax − 物种标签上沿)/(ymax − ymin) = r
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()

    def top_y(ax, texts):
        inv = ax.transData.inverted()
        return max(inv.transform((0, t.get_window_extent(rend).y1))[1] for t in texts)

    ya0, ya1 = axa.get_ylim()
    r_head = (ya1 - top_y(axa, labels_a)) / (ya1 - ya0)
    for ax, labels in ((axb_top, labels_b), (axc, labels_c)):
        ymin, _ = ax.get_ylim()
        t = top_y(ax, labels)
        ax.set_ylim(ymin, (t - r_head * ymin) / (1 - r_head))
    print(f"顶部留白比 r = {r_head:.4f}（以 (a) 为基准，三子图统一）")

    # 三个子图“底部留白比”统一（以 (a) 为基准）：(最低 rung − ymin)/(ymax − ymin) = r
    low = {axa: min(min(d.values()) for d in eg_y.values()),
           axb: min(min(d.values()) for d in oer_y.values()),
           axc: min(min(d.values()) for d in her_y.values())}
    ya0, ya1 = axa.get_ylim()
    r_low = (low[axa] - ya0) / (ya1 - ya0)
    for ax in (axb, axc):
        ymin, ymax = ax.get_ylim()
        ax.set_ylim((low[ax] - r_low * ymax) / (1 - r_low), ymax)
    print(f"底部留白比 r = {r_low:.4f}（以 (a) 为基准，三子图统一）")

    # 数值标签高度比统一（可调参量）：y_标签 = y_rung + R_VAL × 轴长；初值 = (a) state0 现状 0.10/6.25
    R_VAL = 0.008
    for ax, vals in ((axa, vals_a), (axc, vals_c)):
        ymin, ymax = ax.get_ylim()
        for t, yr in vals:
            t.set_y(yr + R_VAL * (ymax - ymin))
    R_VAL_B = 0.045  # 断轴后 (b) 两段各自按轴长取同一视觉偏移
    for ax, vals in ((axb, vals_b), (axb_top, vals_b_top)):
        ymin, ymax = ax.get_ylim()
        for t, yr in vals:
            t.set_y(yr + R_VAL_B * (ymax - ymin))
    print(f"数值标签高度比 R_VAL = {R_VAL:.4f}（(a)/(c)），R_VAL_B = {R_VAL_B:.4f}（(b)）")

    out_png = ROOT / "fig1_gc.png"
    out_pdf = ROOT / "fig1_gc.pdf"
    fig.savefig(out_png, dpi=300)
    fig.savefig(out_pdf)
    print(f"→ {out_png}\n→ {out_pdf}")

    print("\n=== 入图数值（0V 为外推）===")
    for sp, lab in eg:
        if sp != "start":
            s = eg_y[sp]
            print(f"{lab:28s} {s['0.0V']:+.2f} {s['0.4V']:+.2f} {s['0.9V']:+.2f}")
    for k, lab in oer[1:]:
        s = oer_y[k]
        lab = lab.replace("\n", " ")
        print(f"{lab:28s} {s['0.0V']:+.2f} {s['0.4V']:+.2f} {s['0.9V']:+.2f}")
    print(f"{'*H':28s} {her_y['_H']['0.0V']:+.2f} {her_y['_H']['0.4V']:+.2f} {her_y['_H']['0.9V']:+.2f}")


if __name__ == "__main__":
    main()
