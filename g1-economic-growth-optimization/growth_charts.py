# G1：Notebook 用のグラフ（matplotlib）
#
# 計算はすべて既存の .py（economic_model・simulation・allocation_strategies・optimization・evaluation）で行い、
# ここでは「描くだけ」にする。matplotlib は関数の中で import するので、matplotlib がない環境でも
# このモジュールの import はでき、Core（starter.py・unittest）は標準ライブラリだけで動く。
#
# ■ グラフの約束
#   ・分野の色は固定（教育 青、研究開発 オレンジ、インフラ 緑、医療 黄）。重点配分シナリオもその分野の色、均等配分は濃い灰色
#   ・アルゴリズムの色は固定（全探索 濃い灰色、Greedy ピンク、局所探索 紫）
#   ・順序のある条件（パラメータの大小・評価期間）は青の濃淡
#   ・図の文字は英語（Google Colab には日本語フォントがないことが多い）
#   ・すべて架空モデルの計算結果（タイトルに model と書く）

import economic_model as em

SECTOR_COLORS = {"education": "#2a78d6", "rd": "#eb6834", "infrastructure": "#1baf7a", "healthcare": "#eda100"}
SCENARIO_COLORS = {"equal": "#3d3c39", "education": "#2a78d6", "rd": "#eb6834", "infrastructure": "#1baf7a",
                   "healthcare": "#eda100"}
ALGO_COLORS = {"exhaustive": "#3d3c39", "greedy": "#e87ba4", "local_search": "#6250d6"}
ALGO_LABELS = {"exhaustive": "Exhaustive", "greedy": "Greedy", "local_search": "Local search"}
STATE_LABELS = {"human_capital": "Human capital", "technology": "Technology", "infrastructure": "Infrastructure",
                "health": "Health", "gdp": "GDP", "living_standard": "Living standard",
                "gdp_per_capita": "GDP per capita"}
RAMP = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281", "#0d366b"]
TEXT = "#52514e"
NEUTRAL = "#8a8985"


def ramp(n):
    if n <= 1:
        return [RAMP[2]]
    return [RAMP[round(i * (len(RAMP) - 1) / (n - 1))] for i in range(n)]


def setup_style(font_scale=1.0):
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.figsize": (10, 5.2), "figure.dpi": 100, "savefig.dpi": 150, "savefig.bbox": "tight",
        "font.size": 12 * font_scale, "axes.titlesize": 14 * font_scale, "axes.labelsize": 12 * font_scale,
        "legend.fontsize": 10.5 * font_scale, "axes.grid": True, "grid.alpha": 0.3,
        "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 2.2,
        "axes.edgecolor": TEXT, "axes.labelcolor": TEXT, "xtick.color": TEXT, "ytick.color": TEXT,
    })


def save(fig, path):
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(p)
    return str(p)


def _end_labels(ax, x, items, min_gap_frac=0.05):
    """線の右端に名前を書く（重ならないよう上下にずらす）。items = [(y, text, color)]"""
    lo, hi = ax.get_ylim()
    gap = (hi - lo) * min_gap_frac
    items = sorted(items, key=lambda it: it[0])
    placed = []
    for y, _t, _c in items:
        placed.append(max(y, placed[-1] + gap) if placed else y)
    top = hi - gap * 0.6                                   # 上にはみ出すなら、上から下へ詰め直す
    if placed and placed[-1] > top:
        placed[-1] = top
        for i in range(len(placed) - 2, -1, -1):
            placed[i] = min(placed[i], placed[i + 1] - gap)
    for (y, text, color), yl in zip(items, placed):
        ax.annotate(text, (x, y), xytext=(x, yl), textcoords="data", va="center", fontsize="small", color=TEXT,
                    fontweight="bold", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=color, lw=1.2))


def _year_axis(ax):
    from matplotlib.ticker import MaxNLocator
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, steps=[1, 5, 10]))


# ------------------------------------------------------------
# 時系列
# ------------------------------------------------------------
def plot_series(runs, key, title, ylabel=None, colors=None, labels=None, end_labels=True):
    """runs = {名前: records}。records の key を年ごとに描く"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    names = list(runs)
    shades = ramp(len(names))
    items = []
    last = 0
    for i, name in enumerate(names):
        recs = runs[name]
        color = (colors or {}).get(name) or SCENARIO_COLORS.get(name) or shades[i]
        label = (labels or {}).get(name) or str(name)
        xs = [r["year"] for r in recs]
        ys = [r[key] for r in recs]
        ax.plot(xs, ys, color=color, label=label)
        items.append((ys[-1], label, color))
        last = max(last, xs[-1])
    _year_axis(ax)
    ax.set_xlabel("year")
    ax.set_ylabel(ylabel or STATE_LABELS.get(key, key))
    ax.set_title(title)
    if end_labels:
        ax.set_xlim(0, last * 1.28 + 1)
        _end_labels(ax, last + 0.4, items)
    ax.legend(loc="upper left", frameon=False, fontsize="small")
    fig.tight_layout()
    return fig


def plot_state_panels(records, title="State variables over time (model)", keys=None):
    """1 つの記録の状態変数を小さなグラフに並べる（GDP・人的資本・技術・インフラ・健康・生活水準）"""
    import matplotlib.pyplot as plt
    keys = keys or ["gdp", "human_capital", "technology", "infrastructure", "health", "living_standard"]
    colors = {"gdp": "#3d3c39", "human_capital": SECTOR_COLORS["education"], "technology": SECTOR_COLORS["rd"],
              "infrastructure": SECTOR_COLORS["infrastructure"], "health": SECTOR_COLORS["healthcare"],
              "living_standard": "#6250d6", "gdp_per_capita": "#3d3c39"}
    cols = 3
    rows = (len(keys) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(12, 3.4 * rows), squeeze=False)
    for i, key in enumerate(keys):
        ax = axes[i // cols][i % cols]
        ax.plot([r["year"] for r in records], [r[key] for r in records], color=colors.get(key, RAMP[2]))
        ax.set_title(STATE_LABELS.get(key, key), fontsize="medium")
        _year_axis(ax)
    for j in range(len(keys), rows * cols):
        axes[j // cols][j % cols].axis("off")
    fig.suptitle(title)
    fig.tight_layout()
    return fig


# ------------------------------------------------------------
# 配分
# ------------------------------------------------------------
def plot_allocation_bars(items, title="Investment allocation", horizontal=False):
    """items = [(名前, 配分率)]。分野ごとの積み上げ棒グラフ（各棒の合計 = 100%）"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(max(7, 1.6 * len(items) + 3), 5))
    names = [n for n, _ in items]
    bottoms = [0.0] * len(items)
    for sec in em.SECTORS:
        vals = [sh[sec] for _n, sh in items]
        bars = ax.bar(range(len(items)), vals, 0.62, bottom=bottoms, color=SECTOR_COLORS[sec],
                      label=em.SECTOR_LABELS[sec], edgecolor="white", linewidth=2)
        for b, v, bot in zip(bars, vals, bottoms):
            if v >= 0.08:
                ax.text(b.get_x() + b.get_width() / 2, bot + v / 2, f"{v:.0%}", ha="center", va="center",
                        color="white", fontweight="bold", fontsize="small")
        bottoms = [b + v for b, v in zip(bottoms, vals)]
    ax.set_xticks(range(len(items)))
    ax.set_xticklabels(names)
    ax.set_ylim(0, 1.0)
    ax.yaxis.set_major_formatter(__import__("matplotlib.ticker", fromlist=["PercentFormatter"]).PercentFormatter(1.0))
    ax.set_ylabel("share of annual budget")
    ax.set_title(title, pad=26)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.08), ncol=4, frameon=False, fontsize="small")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return fig


def plot_grouped_bars(groups, series, values, title, ylabel, colors=None, fmt="{:.2f}", ylim=None, logy=False,
                      label_bars=None):
    """groups（x 軸）× series（棒）。values[series][group の位置]。棒が多いときは数値を書かない"""
    import matplotlib.pyplot as plt
    label_bars = len(series) <= 3 if label_bars is None else label_bars
    fig, ax = plt.subplots(figsize=(max(8, (0.5 * len(series) + 0.8) * len(groups) + 2), 5.4))
    n = len(series)
    w = 0.8 / n
    shades = ramp(n)
    for i, s in enumerate(series):
        xs = [g + (i - (n - 1) / 2) * w for g in range(len(groups))]
        color = (colors or {}).get(s) or shades[i]
        bars = ax.bar(xs, values[s], w * 0.92, color=color, label=s, edgecolor="white")
        for b, v in zip(bars, values[s] if label_bars else []):
            ax.annotate(fmt.format(v), (b.get_x() + b.get_width() / 2, b.get_height()), xytext=(0, 3),
                        textcoords="offset points", ha="center", va="bottom", fontsize="small", color=TEXT)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups)
    if logy:
        ax.set_yscale("log")
    if ylim:
        ax.set_ylim(*ylim)
    ax.set_ylabel(ylabel)
    ncol = n if n <= 3 else (n + 1) // 2
    ax.set_title(title, pad=24 if n <= 3 else 40)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.07 if n <= 3 else 1.13), ncol=ncol, frameon=False,
              fontsize="small")
    fig.tight_layout()
    return fig


# ------------------------------------------------------------
# 最適化アルゴリズム
# ------------------------------------------------------------
def plot_algorithm_metric(results, key, title, ylabel, fmt="{:.3g}", logy=False, ylim=None):
    """results = optimization.compare_algorithms の結果。1 つの指標をアルゴリズムごとに棒で示す"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    keys = list(results)
    vals = [results[k][key] for k in keys]
    bars = ax.bar(range(len(keys)), vals, 0.6, color=[ALGO_COLORS.get(k, RAMP[2]) for k in keys], edgecolor="white")
    for b, v in zip(bars, vals):
        ax.annotate(fmt.format(v), (b.get_x() + b.get_width() / 2, b.get_height()), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize="small", color=TEXT)
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels([ALGO_LABELS.get(k, k) for k in keys])
    if logy:
        ax.set_yscale("log")
    if ylim:
        ax.set_ylim(*ylim)
    elif not logy:
        ax.set_ylim(0, max(vals) * 1.15 if max(vals) > 0 else 1)   # 棒グラフは 0 から始める
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return fig


def plot_search_path(result, title):
    """Greedy 法・局所探索の途中経過（ステップごとの目的関数の値）"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    vals = [v for _u, v in result["path"]]
    key = "greedy" if result["algorithm"] == "Greedy" else "local_search"
    ax.plot(range(len(vals)), vals, marker="o", color=ALGO_COLORS[key])
    for i, (u, v) in enumerate(result["path"]):
        if i in (0, len(vals) - 1):
            ax.annotate(str(u), (i, v), xytext=(4, -12 if i else 6), textcoords="offset points",
                        fontsize="x-small", color=TEXT)
    _year_axis(ax)                                       # 整数の目盛り
    ax.set_xlabel("step" if key == "greedy" else "iteration")
    ax.set_ylabel("objective")
    ax.set_title(title)
    fig.tight_layout()
    return fig


# ------------------------------------------------------------
# GDP と生活水準
# ------------------------------------------------------------
def plot_tradeoff_scatter(points, highlights=None, title="GDP vs living standard for every allocation (model)",
                          xlabel="final GDP", ylabel="final living standard", color_by=None):
    """points = [(x, y, 配分率)]。全候補を点で描き、highlights = {名前: (x, y)} に印をつける

    color_by = 分野名なら、その分野の配分率で点の濃さを変える。
    """
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 6))
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    if color_by:
        from matplotlib.colors import LinearSegmentedColormap
        cmap = LinearSegmentedColormap.from_list("share", ["#e9eef6", SECTOR_COLORS[color_by], "#0d366b"])
        sc = ax.scatter(xs, ys, c=[p[2][color_by] for p in points], cmap=cmap, s=26, vmin=0, vmax=1,
                        edgecolor="none")
        cb = fig.colorbar(sc, ax=ax)
        cb.set_label(f"{em.SECTOR_LABELS[color_by]} share")
    else:
        ax.scatter(xs, ys, s=22, color=NEUTRAL, alpha=0.6, edgecolor="none", label="all allocations")
    markers = ["*", "D", "s", "^", "P", "X"]
    for i, (name, (x, y)) in enumerate((highlights or {}).items()):
        ax.scatter([x], [y], marker=markers[i % len(markers)], s=230 if markers[i % 6] == "*" else 110,
                   color="white", edgecolor="black", linewidth=1.8, zorder=5, label=name)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc="lower left", frameon=True, framealpha=0.9, fontsize="small")
    fig.tight_layout()
    return fig


# ------------------------------------------------------------
# 感度分析
# ------------------------------------------------------------
def plot_share_lines(xs, shares_list, xlabel, title):
    """パラメータ xs を変えたときの最適配分（分野ごとの線）"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    items = []
    for sec in em.SECTORS:
        ys = [sh[sec] for sh in shares_list]
        ax.plot(xs, ys, marker="o", color=SECTOR_COLORS[sec], label=em.SECTOR_LABELS[sec])
        items.append((ys[-1], em.SECTOR_LABELS[sec], SECTOR_COLORS[sec]))
    ax.set_ylim(-0.03, 1.0)
    ax.yaxis.set_major_formatter(__import__("matplotlib.ticker", fromlist=["PercentFormatter"]).PercentFormatter(1.0))
    span = max(xs) - min(xs) or 1
    ax.set_xlim(min(xs) - span * 0.03, max(xs) + span * 0.25)
    _end_labels(ax, max(xs) + span * 0.03, items)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("optimal share (exhaustive search)")
    ax.set_title(title)
    ax.legend(loc="upper left", frameon=False, fontsize="small", ncol=4)
    fig.tight_layout()
    return fig


def plot_heatmap(xs, ys, values, xlabel, ylabel, title, value_label, fmt="{:.0%}"):
    """values[i][j] = 値(x = xs[j], y = ys[i])。各セルに値を書く"""
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("seq", ["#f4f7fc", "#86b6ef", "#2a78d6", "#104281"])
    fig, ax = plt.subplots(figsize=(8.5, 6))
    flat = [v for row in values for v in row]
    lo, hi = min(flat), max(flat)
    im = ax.imshow(values, origin="lower", cmap=cmap, vmin=lo, vmax=hi if hi > lo else lo + 1e-9, aspect="auto")
    for i, row in enumerate(values):
        for j, v in enumerate(row):
            frac = (v - lo) / (hi - lo) if hi > lo else 0
            ax.text(j, i, fmt.format(v), ha="center", va="center", fontsize="small",
                    color="white" if frac > 0.55 else TEXT, fontweight="bold")
    ax.set_xticks(range(len(xs)))
    ax.set_xticklabels([f"{x:g}" for x in xs])
    ax.set_yticks(range(len(ys)))
    ax.set_yticklabels([f"{y:g}" for y in ys])
    ax.grid(False)
    cb = fig.colorbar(im, ax=ax)
    cb.set_label(value_label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    fig.tight_layout()
    return fig


def plot_xy(xs, series, xlabel, ylabel, title, colors=None):
    """series = {名前: [y...]}。パラメータ xs に対する値（例：予算規模と GDP）"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    shades = ramp(len(series))
    for i, (name, ys) in enumerate(series.items()):
        ax.plot(xs, ys, marker="o", color=(colors or {}).get(name) or SCENARIO_COLORS.get(name) or shades[i],
                label=name)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc="upper left", frameon=False, fontsize="small")
    fig.tight_layout()
    return fig
