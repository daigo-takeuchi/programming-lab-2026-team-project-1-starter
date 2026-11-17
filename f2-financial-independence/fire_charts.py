# F2：Notebook 用のグラフ（matplotlib）
#
# 計算はすべて既存の .py（financial_model・fire_analysis・retirement_model・optimization）で行い、
# ここでは「描くだけ」にする。matplotlib は関数の中で import するので、matplotlib がない環境でも
# このモジュールの import はでき、Core（starter.py・unittest）は標準ライブラリだけで動く。
#
# ■ グラフの約束
#   ・1 枚のグラフで 1 つのメッセージ。軸に単位（万円・歳）を書く
#   ・シナリオごとの色は固定。条件を順に変える系列（貯蓄率 10%→50% など）は、青の濃淡（薄い→濃い）
#   ・FIRE 未達成は「値なし」として区別する（0 や 80 歳と混同しない）
#   ・図の文字は英語（Colab には日本語フォントがないことが多い）

SCENARIO_COLORS = {
    "standard": "#2a78d6",
    "high_savings": "#eb6834",
    "high_return": "#1baf7a",
    "high_income": "#eda100",
}
RAMP = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281", "#0d366b"]   # 順序のある系列用（薄い → 濃い）
NEUTRAL = "#8a8985"
TEXT = "#52514e"
TARGET = "#d03b3b"


def color_of(name):
    return SCENARIO_COLORS.get(name, NEUTRAL)


def ramp(n):
    """n 個の順序のある系列の色（薄い → 濃い）"""
    if n <= 1:
        return [RAMP[2]]
    return [RAMP[round(i * (len(RAMP) - 1) / (n - 1))] for i in range(n)]


def setup_style(font_scale=1.0):
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.figsize": (10, 5.2), "figure.dpi": 100, "savefig.dpi": 150, "savefig.bbox": "tight",
        "font.size": 12 * font_scale, "axes.titlesize": 15 * font_scale, "axes.labelsize": 13 * font_scale,
        "legend.fontsize": 11 * font_scale, "axes.grid": True, "grid.alpha": 0.3,
        "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 2.2,
        "axes.edgecolor": TEXT, "axes.labelcolor": TEXT, "xtick.color": TEXT, "ytick.color": TEXT,
    })


def _end_labels(ax, x, items, min_gap_frac=0.05):
    """線の右端に名前を書く（重ならないよう上下にずらす）。items = [(y, text, color)]"""
    lo, hi = ax.get_ylim()
    gap = (hi - lo) * min_gap_frac
    items = sorted(items, key=lambda it: it[0])
    placed = []
    for y, _t, _c in items:
        placed.append(max(y, placed[-1] + gap) if placed else y)
    for (y, text, color), yl in zip(items, placed):
        ax.annotate(text, (x, y), xytext=(x, yl), textcoords="data", va="center", fontsize="small",
                    color=TEXT, fontweight="bold", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=color, lw=1.2))


# ------------------------------------------------------------
# 資産の推移
# ------------------------------------------------------------
def plot_assets(series, title, target=None, fire_ages=None, ylabel="assets [10k JPY]", target_label=None):
    """series = [(label, ages, assets, color), ...]

    target    : FIRE 目標資産（水平線）。シナリオごとに違う場合は描かず、fire_ages の点だけ描く
    fire_ages : [age or None, ...]（series と同じ順）。達成した年齢に点を打つ
    """
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ends = []
    for i, (label, ages, assets, color) in enumerate(series):
        ax.plot(ages, assets, color=color, label=label)
        ends.append((assets[-1], label, color))
        if fire_ages and fire_ages[i] is not None:
            k = fire_ages[i] - ages[0]
            ax.plot([fire_ages[i]], [assets[k]], "o", ms=10, color=color, mec="white", mew=2, zorder=3)
    if target is not None:
        ax.axhline(target, color=TARGET, ls="--", lw=1.5)
        ax.annotate(target_label or f"FIRE target {target:,.0f}", (series[0][1][0], target), xytext=(4, 6),
                    textcoords="offset points", color=TARGET, fontweight="bold")
    xmax = max(s[1][-1] for s in series)
    xmin = min(s[1][0] for s in series)
    ax.set_xlim(xmin, xmax + (xmax - xmin) * 0.22)
    _end_labels(ax, xmax + (xmax - xmin) * 0.01, ends)
    ax.set_xlabel("age")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc="upper left")
    return fig


def plot_contributions_vs_gains(labels, contributions, gains, title):
    """拠出した貯蓄と投資収益の積み上げ棒（複利の効果）"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    x = range(len(labels))
    ax.bar(x, contributions, color=NEUTRAL, label="contributions (savings)", edgecolor="white", lw=2)
    ax.bar(x, gains, bottom=contributions, color="#2a78d6", label="investment gains (compound)", edgecolor="white", lw=2)
    for i, (c, g) in enumerate(zip(contributions, gains)):
        ax.text(i, c + g, f"{c + g:,.0f}", ha="center", va="bottom", color=TEXT)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("assets [10k JPY]")
    ax.set_title(title)
    ax.legend(loc="upper left")
    ax.grid(axis="x", visible=False)
    return fig


# ------------------------------------------------------------
# FIRE 達成年齢と条件
# ------------------------------------------------------------
def plot_fire_age(xs, ages, xlabel, title, end_age=80, xfmt="{:.0%}", ax=None):
    """条件（横軸）ごとの FIRE 達成年齢。未達成は上の帯に灰色の × で示す（年齢の値とは混同しない）"""
    import matplotlib.pyplot as plt
    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 4.6))
    else:
        fig = ax.figure
    reached = [(x, a) for x, a in zip(xs, ages) if a is not None]
    missing = [x for x, a in zip(xs, ages) if a is None]
    if reached:
        rx, ry = zip(*reached)
        ax.plot(rx, ry, marker="o", ms=9, color="#2a78d6", mec="white", mew=2)
        for x, a in reached:
            ax.annotate(str(a), (x, a), xytext=(0, 9), textcoords="offset points", ha="center", color=TEXT)
    band = end_age + 4
    ax.axhspan(end_age + 1, end_age + 7, color=NEUTRAL, alpha=0.12, lw=0)
    if missing:
        ax.plot(missing, [band] * len(missing), "x", ms=11, mew=2.5, color=NEUTRAL)
    ax.set_ylim(min([a for a in ages if a is not None] or [end_age]) - 6, end_age + 7)
    # 縦軸の目盛り：年齢の目盛り（end_age まで）＋ 灰色の帯に「未達成」の目盛り（年齢の値ではない）
    ticks = [t for t in ax.get_yticks() if ax.get_ylim()[0] <= t <= end_age]
    ax.set_yticks(ticks + [band])
    ax.set_yticklabels([f"{t:g}" for t in ticks] + [f"not reached\nby {end_age}"])
    ax.set_xticks(list(xs))
    ax.set_xticklabels([xfmt.format(x) for x in xs])
    ax.set_xlabel(xlabel)
    ax.set_ylabel("FIRE age")
    ax.set_title(title)
    return fig


def plot_heatmap(matrix, rates, returns, title="FIRE age by savings rate and return", end_age=80):
    """貯蓄率（行）× 収益率（列）の FIRE 達成年齢。未達成のセルは斜線の灰色で「N/A」と書く"""
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import Rectangle
    values = [a for row in matrix for a in row if a is not None]
    lo, hi = (min(values), max(values)) if values else (0, 1)
    cmap = LinearSegmentedColormap.from_list("fire", ["#104281", "#2a78d6", "#86b6ef", "#e6eefb"])   # 早い = 濃い
    fig, ax = plt.subplots(figsize=(1.5 * len(returns) + 3, 1.0 * len(rates) + 2))
    for i, row in enumerate(matrix):
        for j, a in enumerate(row):
            if a is None:
                ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fc="#f0efec", ec="white", lw=2, hatch="///"))
                ax.text(j, i, "N/A", ha="center", va="center", color=TEXT, fontweight="bold")
            else:
                t = 0.5 if hi == lo else (a - lo) / (hi - lo)
                ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fc=cmap(t), ec="white", lw=2))
                ax.text(j, i, str(a), ha="center", va="center", fontweight="bold",
                        color="white" if t < 0.55 else TEXT)
    ax.set_xlim(-0.5, len(returns) - 0.5)
    ax.set_ylim(len(rates) - 0.5, -0.5)
    ax.set_xticks(range(len(returns)))
    ax.set_xticklabels([f"{r:.0%}" for r in returns])
    ax.set_yticks(range(len(rates)))
    ax.set_yticklabels([f"{r:.0%}" for r in rates])
    ax.set_xlabel("annual return")
    ax.set_ylabel("savings rate")
    ax.set_title(f"{title}\n(darker = earlier, N/A = not reached by {end_age})")
    ax.grid(False)
    return fig


# ------------------------------------------------------------
# リタイア後の取り崩し
# ------------------------------------------------------------
def plot_withdrawal(series, title, end_age=100):
    """series = [(label, rows, color), ...]（rows は retirement_model.simulate_withdrawal の結果）

    資産が 0 になった年齢に × を打つ。
    """
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ends = []
    for label, rows, color in series:
        ages = [r["age"] for r in rows] + [rows[-1]["age"] + 1]
        assets = [r["start_assets"] for r in rows] + [rows[-1]["end_assets"]]
        ax.plot(ages, assets, color=color, label=label)
        ends.append((assets[-1], label, color))
        dep = next((r["age"] for r in rows if r["depleted"]), None)
        if dep is not None:
            ax.plot([dep + 1], [0], "X", ms=12, color=color, mec="white", mew=1.5, zorder=3)
    ax.axhline(0, color=TEXT, lw=1)
    xmin = min(s[1][0]["age"] for s in series)
    ax.set_xlim(xmin, end_age + (end_age - xmin) * 0.25)
    _end_labels(ax, end_age + (end_age - xmin) * 0.01, ends)
    ax.set_xlabel("age")
    ax.set_ylabel("assets [10k JPY]")
    ax.set_title(title + "  (X: assets run out)")
    ax.legend(loc="upper left")
    return fig


# ------------------------------------------------------------
# 感度分析
# ------------------------------------------------------------
def plot_tornado(rows, reference, title, xlabel="FIRE age"):
    """rows = [{"label": ..., "low": 値, "high": 値}]（値が None なら「未達成」と書く）。影響の大きい順に上から"""
    import matplotlib.pyplot as plt
    def span(r):
        lo, hi = r["low"], r["high"]
        return abs((hi if hi is not None else reference) - (lo if lo is not None else reference))
    rows = sorted(rows, key=span)
    fig, ax = plt.subplots(figsize=(10, 0.8 * len(rows) + 1.6))
    for i, r in enumerate(rows):
        for key, color in [("low", "#2a78d6"), ("high", "#eb6834")]:
            v = r[key]
            if v is None:
                ax.text(reference, i + (0.18 if key == "high" else -0.18), f"  {key}: not reached", va="center",
                        color=TEXT, fontsize="small")
                continue
            ax.barh(i + (0.18 if key == "high" else -0.18), v - reference, left=reference, color=color, height=0.34)
            ax.text(v, i + (0.18 if key == "high" else -0.18), f" {v:g} ", va="center",
                    ha="left" if v >= reference else "right", color=TEXT, fontsize="small")
    ax.axvline(reference, color=TEXT, lw=1.2)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r["label"] for r in rows])
    ax.set_xlabel(xlabel)
    ax.set_title(f"{title} (base: {reference:g})")
    ax.grid(axis="y", visible=False)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color="#2a78d6", label="assumption lowered"),
                       Patch(color="#eb6834", label="assumption raised")], loc="lower right", fontsize="small")
    return fig


def save(fig, path):
    import os
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.savefig(path)
    return path
