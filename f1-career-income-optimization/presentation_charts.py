# F1：発表用のグラフ（Notebook から使う）
#
# 計算はすべて既存の .py（scenarios・income_analysis・optimization）で行い、ここでは「描くだけ」にする。
# matplotlib は関数の中で import するので、matplotlib がない環境でもこのモジュールの import はできる
# （starter.py・unittest の Core 部分は、これまでどおり標準ライブラリだけで動く）。
#
# ■ 発表用の約束
#   ・1 枚のグラフで 1 つのメッセージ。タイトルに「何の図か」、軸に単位（万円・歳）を書く
#   ・色はキャリアごとに固定（どのグラフでも同じキャリアは同じ色）。線の終わりに名前を直接書く
#   ・図の文字は英語（Google Colab には日本語フォントがないことが多い。日本語にする方法は notebooks/README.md）
#   ・2 つの量（例：生涯所得と NPV）を 1 つの縦軸に重ねない。単位や大きさが違うものは図を分ける

import career_model as cm
import income_analysis as ia
import scenarios as sc

# キャリアごとの固定色（data/sample_careers.json の順）。足りない場合は灰色
CAREER_COLORS = {
    "early_job": "#2a78d6",
    "vocational": "#eb6834",
    "university": "#1baf7a",
    "certificate": "#eda100",
    "job_change": "#e87ba4",
}
NEUTRAL = "#8a8985"
TEXT = "#52514e"
CRITERIA_COLORS = {"gross": "#2a78d6", "net": "#1baf7a", "npv": "#6250d6"}


def color_of(name):
    return CAREER_COLORS.get(name, NEUTRAL)


def setup_style(font_scale=1.0):
    """発表用の共通スタイル（文字を大きめ、グリッドは控えめ）"""
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.figsize": (10, 5.2), "figure.dpi": 100, "savefig.dpi": 150, "savefig.bbox": "tight",
        "font.size": 12 * font_scale, "axes.titlesize": 15 * font_scale, "axes.labelsize": 13 * font_scale,
        "legend.fontsize": 11 * font_scale, "axes.grid": True, "grid.alpha": 0.3,
        "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 2.2,
        "axes.edgecolor": TEXT, "axes.labelcolor": TEXT, "xtick.color": TEXT, "ytick.color": TEXT,
    })


def _label_line_ends(ax, x, items, min_gap_frac=0.055):
    """線の右端に名前を書く。items = [(y, text, color), ...]。ラベルが重ならないよう上下にずらす"""
    lo, hi = ax.get_ylim()
    gap = (hi - lo) * min_gap_frac
    items = sorted(items, key=lambda it: it[0])
    placed = []
    for y, _text, _color in items:                       # 下から順に、前のラベルと gap 以上離す
        placed.append(max(y, placed[-1] + gap) if placed else y)
    for (y, text, color), y_label in zip(items, placed):
        ax.annotate(text, (x, y), xytext=(x, y_label), textcoords="data", va="center",
                    fontsize="small", color=TEXT, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=color, lw=1.2))


# ------------------------------------------------------------
# 1. 年齢別所得
# ------------------------------------------------------------
def plot_income_by_age(careers, title="Annual income by age (fictional data)"):
    """各キャリアの年齢別年収（万円）の折れ線"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    xs = cm.ages()
    ends = []
    for s in careers:
        ys = sc.incomes(s)
        ax.plot(xs, ys, color=color_of(s["name"]), label=s.get("label", s["name"]))
        ends.append((ys[-1], s.get("label", s["name"]), color_of(s["name"])))
    _label_line_ends(ax, xs[-1] + 0.6, ends)
    ax.set_xlabel("age")
    ax.set_ylabel("annual income [10k JPY]")
    ax.set_title(title)
    ax.set_xlim(xs[0], xs[-1] + 9)
    ax.legend(loc="upper left")
    return fig


# ------------------------------------------------------------
# 2. 累積純収入（投資回収の様子）
# ------------------------------------------------------------
def plot_cumulative_net(careers, baseline=None, title="Cumulative net income by age"):
    """累積純収入（年収 − 費用の累積和）。baseline を渡すと、各キャリアの回収年齢に印をつける"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    xs = cm.ages()
    ends = []
    for s in careers:
        ys = ia.cumulative(sc.cashflows(s))
        ax.plot(xs, ys, color=color_of(s["name"]), label=s.get("label", s["name"]))
        ends.append((ys[-1], s.get("label", s["name"]), color_of(s["name"])))
        if baseline is not None and s is not baseline and s["name"] != baseline["name"]:
            p = ia.payback_age(s, baseline)
            if p["status"] == "recovered":
                y = ys[cm.index_of_age(p["payback_age"])]
                ax.plot([p["payback_age"]], [y], "o", ms=9, color=color_of(s["name"]), mec="white", mew=2, zorder=3)
    ax.axhline(0, color=TEXT, lw=0.8)
    _label_line_ends(ax, xs[-1] + 0.6, ends)
    ax.set_xlabel("age")
    ax.set_ylabel("cumulative net income [10k JPY]")
    if baseline is not None:
        title += f"  (dots: catches up with {baseline.get('label', baseline['name'])})"
    ax.set_title(title)
    ax.set_xlim(xs[0], xs[-1] + 9)
    ax.legend(loc="upper left")
    return fig


def plot_gap_vs_baseline(scenario, baseline, title=None):
    """scenario − baseline の累積純収入の差。0 を上回る年齢が投資回収年齢"""
    import matplotlib.pyplot as plt
    xs = cm.ages()
    a = ia.cumulative(sc.cashflows(scenario))
    b = ia.cumulative(sc.cashflows(baseline))
    gap = [x - y for x, y in zip(a, b)]
    p = ia.payback_age(scenario, baseline)
    fig, ax = plt.subplots(figsize=(10, 4.2))
    c = color_of(scenario["name"])
    ax.fill_between(xs, gap, 0, where=[g < 0 for g in gap], color=c, alpha=0.15, step=None)
    ax.plot(xs, gap, color=c)
    ax.axhline(0, color=TEXT, lw=1)
    if p["status"] == "recovered":
        ax.axvline(p["payback_age"], color=TEXT, ls="--", lw=1)
        ax.annotate(f"payback at {p['payback_age']}", (p["payback_age"], 0), xytext=(8, 12),
                    textcoords="offset points", color=TEXT, fontweight="bold")
    ax.set_xlabel("age")
    ax.set_ylabel("cumulative gap [10k JPY]")
    ax.set_title(title or f"{scenario.get('label')} minus {baseline.get('label', 'baseline')} (cumulative net income)")
    return fig


# ------------------------------------------------------------
# 3. キャリアの比較（棒グラフ）
# ------------------------------------------------------------
def plot_metric_bars(results, key, title, xlabel="[10k JPY]"):
    """1 つの評価指標でキャリアを横棒にする（大きい順に上から）。値を棒の端に書く"""
    import matplotlib.pyplot as plt
    import optimization as op
    ranked = op.rank(results, key)
    fig, ax = plt.subplots(figsize=(10, 0.7 * len(ranked) + 1.4))
    labels = [r["label"] for r in ranked][::-1]
    values = [r[key] for r in ranked][::-1]
    colors = [color_of(r["name"]) for r in ranked][::-1]
    bars = ax.barh(labels, values, color=colors, height=0.6)
    for bar, v in zip(bars, values):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f" {v:,.0f}", va="center", color=TEXT)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.set_xlim(0, max(values) * 1.15 if values else 1)
    ax.grid(axis="y", visible=False)
    return fig


# ------------------------------------------------------------
# 4. 転職年齢の全探索
# ------------------------------------------------------------
def plot_switch_age_search(rows, best, stay=None, title="Exhaustive search over job-change age"):
    """転職年齢ごとの生涯所得と NPV（単位は同じ万円だが大きさが違うので、2 つの図に分ける）"""
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    xs = [r["switch_age"] for r in rows]
    for ax, key, name in [(axes[0], "gross", "lifetime gross income"), (axes[1], "npv", "NPV")]:
        ys = [r[key] for r in rows]
        ax.plot(xs, ys, marker="o", ms=4, color=CRITERIA_COLORS[key])
        if best.get(key):
            bx, by = best[key]["switch_age"], best[key]["value"]
            ax.plot([bx], [by], "o", ms=12, color=CRITERIA_COLORS[key], mec="white", mew=2, zorder=3)
            ax.annotate(f"best: {bx}", (bx, by), xytext=(8, 8), textcoords="offset points",
                        color=TEXT, fontweight="bold")
        if stay is not None:
            ax.axhline(stay[key], color=NEUTRAL, ls="--", lw=1.2)
            ax.annotate("no job change", (xs[-1], stay[key]), xytext=(0, 6), textcoords="offset points",
                        ha="right", color=TEXT, fontsize="small")
        ax.set_xlabel("job-change age")
        ax.set_ylabel(f"{name} [10k JPY]")
        ax.set_title(name)
    fig.suptitle(title, fontsize="x-large")
    fig.tight_layout()
    return fig


# ------------------------------------------------------------
# 5. 割引率と順位・NPV
# ------------------------------------------------------------
def plot_npv_vs_rate(careers, rates, title="NPV vs discount rate"):
    """割引率を横軸に、各キャリアの NPV"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    xs = [r * 100 for r in rates]
    ends = []
    for s in careers:
        ys = [ia.scenario_npv(s, r) for r in rates]
        ax.plot(xs, ys, color=color_of(s["name"]), label=s.get("label", s["name"]))
        ends.append((ys[-1], s.get("label", s["name"]), color_of(s["name"])))
    _label_line_ends(ax, xs[-1] + (xs[-1] - xs[0]) * 0.02, ends)
    ax.set_xlabel("discount rate [%]")
    ax.set_ylabel("NPV at age 18 [10k JPY]")
    ax.set_title(title)
    ax.set_xlim(xs[0], xs[-1] + (xs[-1] - xs[0]) * 0.28)
    ax.legend(loc="upper right")
    return fig


def plot_rank_by_rate(careers, rates, title="Ranking by NPV changes with the discount rate"):
    """割引率ごとの NPV の順位（1 位が上）。線が交差したところで順位が入れ替わる"""
    import matplotlib.pyplot as plt
    import optimization as op
    fig, ax = plt.subplots()
    positions = {s["name"]: [] for s in careers}
    for r in rates:
        ranked = op.rank([ia.evaluate(s, r) for s in careers], "npv")
        for pos, res in enumerate(ranked, start=1):
            positions[res["name"]].append(pos)
    xs = [r * 100 for r in rates]
    ends = []
    for s in careers:
        ys = positions[s["name"]]
        ax.plot(xs, ys, marker="o", ms=9, color=color_of(s["name"]), mec="white", mew=2)
        ends.append((ys[-1], s.get("label", s["name"]), color_of(s["name"])))
    ax.invert_yaxis()
    _label_line_ends(ax, xs[-1] + 0.12, ends, min_gap_frac=0.0)
    ax.set_yticks(range(1, len(careers) + 1))
    ax.set_xticks(xs)
    ax.set_xlabel("discount rate [%]")
    ax.set_ylabel("rank by NPV (1 = best)")
    ax.set_title(title)
    ax.set_xlim(xs[0] - 0.2, xs[-1] + (xs[-1] - xs[0]) * 0.35)
    return fig


# ------------------------------------------------------------
# 6. 感度分析（トルネード図）
# ------------------------------------------------------------
def plot_tornado(rows, reference, title="Sensitivity analysis", xlabel="result [10k JPY]"):
    """rows = [{"label": 変えた仮定, "low": 下げたときの結果, "high": 上げたときの結果}, ...]

    影響の大きい仮定から上に並べる。中央の縦線が基準の結果。
    """
    import matplotlib.pyplot as plt
    rows = sorted(rows, key=lambda r: abs(r["high"] - r["low"]))
    fig, ax = plt.subplots(figsize=(10, 0.75 * len(rows) + 1.6))
    for i, r in enumerate(rows):
        lo, hi = r["low"], r["high"]
        ax.barh(i, lo - reference, left=reference, color="#2a78d6", height=0.55)
        ax.barh(i, hi - reference, left=reference, color="#eb6834", height=0.55)
        ax.text(min(lo, hi), i, f"{min(lo, hi):,.0f} ", ha="right", va="center", color=TEXT, fontsize="small")
        ax.text(max(lo, hi), i, f" {max(lo, hi):,.0f}", ha="left", va="center", color=TEXT, fontsize="small")
    ax.axvline(reference, color=TEXT, lw=1.2)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r["label"] for r in rows])
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.grid(axis="y", visible=False)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color="#2a78d6", label="assumption lowered"),
                       Patch(color="#eb6834", label="assumption raised")], loc="lower right")
    lo_all = min(min(r["low"], r["high"]) for r in rows)
    hi_all = max(max(r["low"], r["high"]) for r in rows)
    pad = (hi_all - lo_all) * 0.2 or 1
    ax.set_xlim(lo_all - pad, hi_all + pad)
    return fig


def save(fig, path):
    """発表資料（スライド）に貼るために PNG で保存する（フォルダがなければ作る）"""
    import os
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.savefig(path)
    return path
