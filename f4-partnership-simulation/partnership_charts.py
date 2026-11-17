# F4：Notebook 用のグラフ（matplotlib）
#
# 計算はすべて既存の .py（partners・household_model・decision_strategies・relationship_dynamics・evaluation）で行い、
# ここでは「描くだけ」にする。matplotlib は関数の中で import するので、matplotlib がない環境でも
# このモジュールの import はでき、Core（starter.py・unittest）は標準ライブラリだけで動く。
#
# ■ グラフの約束
#   ・戦略の色は固定（Fixed 青、Greedy オレンジ、Fairness-aware 緑、Adaptive 黄）
#   ・Partner A は紫、Partner B はピンク（性別とは関係のない、区別のための色）。関係全体は濃い灰色
#   ・順序のある条件（パラメータの大小など）は青の濃淡
#   ・図の文字は英語（Google Colab には日本語フォントがないことが多い）
#   ・関係の時間変化・継続率のグラフはすべて「教育用の架空モデル」の結果（タイトルに model と書く）

STRATEGY_COLORS = {"fixed": "#2a78d6", "greedy": "#eb6834", "fairness": "#1baf7a", "adaptive": "#eda100"}
STRATEGY_LABELS = {"fixed": "Fixed", "greedy": "Greedy", "fairness": "Fairness-aware", "adaptive": "Adaptive"}
PARTNER_COLORS = {"A": "#6250d6", "B": "#e87ba4"}
RELATION_COLOR = "#3d3c39"
RAMP = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281", "#0d366b"]
NEUTRAL = "#8a8985"
TEXT = "#52514e"
ALERT = "#d03b3b"
EVENT_COLOR = "#d03b3b"


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
    for (y, text, color), yl in zip(items, placed):
        ax.annotate(text, (x, y), xytext=(x, yl), textcoords="data", va="center", fontsize="small", color=TEXT,
                    fontweight="bold", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=color, lw=1.2))


def _year_axis(ax):
    from matplotlib.ticker import MaxNLocator
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, steps=[1, 5, 10]))


def _event_lines(ax, event_years, label=True):
    _year_axis(ax)
    for i, y in enumerate(event_years):
        ax.axvline(y, color=EVENT_COLOR, lw=1.2, ls=":", zorder=0)
        if label:
            ax.annotate("event", (y, 1), xycoords=("data", "axes fraction"), xytext=(3, -2),
                        textcoords="offset points", va="top", fontsize="small", color=EVENT_COLOR)


def _bar_labels(ax, bars, fmt="{:.2f}", offsets=None):
    for i, b in enumerate(bars):
        h = b.get_height()
        dy = 0 if offsets is None else offsets[i]
        ax.annotate(fmt.format(h), (b.get_x() + b.get_width() / 2, h + dy), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize="small", color=TEXT)


def _grouped(ax, groups, series, values, colors, errors=None, fmt="{:.2f}", width=0.8, label_bars=True):
    """groups（x 軸）× series（棒）の棒グラフ。values[s][g]、errors[s][g]（なければ None）"""
    n = len(series)
    w = width / n
    for i, s in enumerate(series):
        xs = [g + (i - (n - 1) / 2) * w for g in range(len(groups))]
        vals = [values[s][j] for j in range(len(groups))]
        err = None if errors is None else [errors[s][j] or 0 for j in range(len(groups))]
        bars = ax.bar(xs, vals, w * 0.92, color=colors[s], label=s, yerr=err, capsize=3 if err else 0,
                      error_kw={"ecolor": TEXT, "lw": 1}, edgecolor="white", linewidth=1)
        if label_bars:
            _bar_labels(ax, bars, fmt, err)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups)


# ------------------------------------------------------------
# Notebook 01：家事と経済的負担
# ------------------------------------------------------------
def plot_hours_bars(rows, title="Weekly housework hours by rule"):
    """rows = [{"name", "A", "B", "limit_A", "limit_B"}]。家事時間（棒）と、家事に使える時間の上限（横線）"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(max(8, 1.7 * len(rows) + 2), 5))
    names = [r["name"] for r in rows]
    vals = {"Partner A": [r["A"] for r in rows], "Partner B": [r["B"] for r in rows]}
    cols = {"Partner A": PARTNER_COLORS["A"], "Partner B": PARTNER_COLORS["B"]}
    _grouped(ax, names, list(vals), vals, cols, fmt="{:.1f}")
    for j, r in enumerate(rows):
        for i, pid in enumerate(("A", "B")):
            x = j + (i - 0.5) * 0.4
            over = r[pid] > r["limit_" + pid] + 1e-9
            ax.hlines(r["limit_" + pid], x - 0.2, x + 0.2, color=ALERT if over else TEXT, lw=2, ls="--")
    ax.plot([], [], color=TEXT, ls="--", lw=2, label="available hours (limit)")
    ax.set_ylabel("hours / week")
    ax.set_title(title)
    ax.legend(loc="upper left", ncol=3, frameon=False)
    ax.set_ylim(0, max(max(r["A"], r["B"], r["limit_A"], r["limit_B"]) for r in rows) * 1.3)
    fig.tight_layout()
    return fig


def plot_money_bars(rows, title="Annual household expenses paid by each partner (10k yen)"):
    """rows = [{"name", "A", "B", "income_A", "income_B"}]"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(max(8, 1.7 * len(rows) + 2), 5))
    names = [r["name"] for r in rows]
    vals = {"Partner A": [r["A"] for r in rows], "Partner B": [r["B"] for r in rows]}
    cols = {"Partner A": PARTNER_COLORS["A"], "Partner B": PARTNER_COLORS["B"]}
    _grouped(ax, names, list(vals), vals, cols, fmt="{:.0f}")
    ax.set_ylabel("10k yen / year")
    ax.set_title(title)
    ax.legend(loc="upper left", ncol=2, frameon=False)
    ax.set_ylim(0, max(max(r["A"], r["B"]) for r in rows) * 1.3)
    fig.tight_layout()
    return fig


def plot_share_comparison(rows, title="Partner A's shares: income vs housework vs expenses"):
    """rows = [{"name", "income", "work", "housework", "financial"}]（すべて Partner A の割合 0〜1）"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(max(8, 1.9 * len(rows) + 2), 5))
    keys = [("income", "share of income", RAMP[1]), ("work", "share of paid work hours", RAMP[4]),
            ("housework", "share of housework", PARTNER_COLORS["A"]),
            ("financial", "share of expenses", "#1baf7a")]
    vals = {k: [r[k] for r in rows] for k, _l, _c in keys}
    _grouped(ax, [r["name"] for r in rows], [k for k, _l, _c in keys], vals, {k: c for k, _l, c in keys},
             fmt="{:.0%}")
    handles, _ = ax.get_legend_handles_labels()
    ax.legend(handles, [l for _k, l, _c in keys], loc="upper center", ncol=4, frameon=False, fontsize="small",
              bbox_to_anchor=(0.5, 1.0))
    ax.axhline(0.5, color=NEUTRAL, lw=1, ls=":")
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Partner A's share (B = 1 - share)")
    ax.set_title(title, pad=24)
    fig.tight_layout()
    return fig


# ------------------------------------------------------------
# Notebook 02：満足度と公平性
# ------------------------------------------------------------
def plot_share_sweep(xs, ua, ub, xlabel, title, marks=None):
    """分担率を動かしたときの U_A・U_B・平均・最低。marks = {名前: x}（縦線で示す）"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    mean = [(a + b) / 2 for a, b in zip(ua, ub)]
    low = [min(a, b) for a, b in zip(ua, ub)]
    ax.plot(xs, ua, color=PARTNER_COLORS["A"], label="Partner A", marker="o", ms=5)
    ax.plot(xs, ub, color=PARTNER_COLORS["B"], label="Partner B", marker="o", ms=5)
    ax.plot(xs, mean, color=RELATION_COLOR, label="mean", lw=2.4)
    ax.plot(xs, low, color=RELATION_COLOR, label="minimum", ls="--", lw=1.8)
    for i, (name, x) in enumerate((marks or {}).items()):
        ax.axvline(x, color=NEUTRAL, lw=1, ls=":")
        ax.annotate(name, (x, 1.0), xycoords=("data", "axes fraction"), xytext=(3, -4 - 16 * (i % 3)),
                    textcoords="offset points", va="top", fontsize="small", color=TEXT,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))
    ax.set_xlabel(xlabel)
    ax.set_ylabel("satisfaction (utility, 0-1)")
    ax.set_title(title)
    ax.set_xlim(min(xs), max(xs) + (max(xs) - min(xs)) * 0.12)
    _end_labels(ax, max(xs) + (max(xs) - min(xs)) * 0.02,
                [(ua[-1], "A", PARTNER_COLORS["A"]), (ub[-1], "B", PARTNER_COLORS["B"]),
                 (mean[-1], "mean", RELATION_COLOR), (low[-1], "min", RELATION_COLOR)])
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=4, frameon=False, fontsize="small")
    fig.tight_layout()
    return fig


def plot_partner_bars(rows, title="Satisfaction of each partner"):
    """rows = [{"name", "A", "B"}]。2 人の満足度を並べ、平均（◆）も示す"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(max(8, 1.7 * len(rows) + 2), 5))
    vals = {"Partner A": [r["A"] for r in rows], "Partner B": [r["B"] for r in rows]}
    cols = {"Partner A": PARTNER_COLORS["A"], "Partner B": PARTNER_COLORS["B"]}
    _grouped(ax, [r["name"] for r in rows], list(vals), vals, cols)
    ax.scatter(range(len(rows)), [(r["A"] + r["B"]) / 2 for r in rows], marker="D", s=50, color=RELATION_COLOR,
               zorder=5, label="mean", edgecolor="white")
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("satisfaction (0-1)")
    ax.set_title(title)
    ax.legend(loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout()
    return fig


def plot_heatmap(xs, ys, values, title, value_label, marks=None, cmap_name="seq"):
    """values[i][j] = 値(x = xs[j], y = ys[i])。marks = {名前: (x, y)}（印をつける）"""
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("seq", ["#f4f7fc", "#86b6ef", "#2a78d6", "#104281"])
    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    flat = [v for row in values for v in row if v is not None]
    lo, hi = min(flat), max(flat)
    im = ax.imshow([[float("nan") if v is None else v for v in row] for row in values], origin="lower",
                   cmap=cmap, vmin=lo, vmax=hi, aspect="auto",
                   extent=(min(xs) - 0.05, max(xs) + 0.05, min(ys) - 0.05, max(ys) + 0.05))
    cb = fig.colorbar(im, ax=ax)
    cb.set_label(value_label)
    markers = ["o", "s", "^", "D", "v", "P"]
    for i, (name, (x, y)) in enumerate((marks or {}).items()):
        ax.scatter([x], [y], marker=markers[i % len(markers)], s=110, facecolor="white", edgecolor="black",
                   lw=1.8, zorder=5, label=name)
    if marks:
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=min(3, len(marks)), frameon=False,
                  fontsize="small")
    ax.grid(False)
    ax.set_xlabel("x = Partner A's housework share")
    ax.set_ylabel("y = Partner A's expense share")
    ax.set_title(title)
    fig.tight_layout()
    return fig


# ------------------------------------------------------------
# Notebook 03・05：戦略の比較
# ------------------------------------------------------------
def plot_strategy_metrics(results, metrics, title, ylim=(0, 1.15), fmt="{:.2f}", sd=False):
    """metrics = [(キー, 表示名)]。x 軸 = 指標、棒 = 戦略。sd=True なら キー_sd を誤差棒にする"""
    import matplotlib.pyplot as plt
    strategies = list(results)
    fig, ax = plt.subplots(figsize=(max(8, 2.3 * len(metrics) + 2), 5))
    vals = {STRATEGY_LABELS[s]: [results[s][k] for k, _n in metrics] for s in strategies}
    errs = ({STRATEGY_LABELS[s]: [results[s].get(k + "_sd") for k, _n in metrics] for s in strategies}
            if sd else None)
    cols = {STRATEGY_LABELS[s]: STRATEGY_COLORS[s] for s in strategies}
    _grouped(ax, [n for _k, n in metrics], list(vals), vals, cols, errs, fmt)
    ax.set_ylim(*ylim)
    ax.set_title(title, pad=24)
    ax.legend(loc="upper center", ncol=len(strategies), frameon=False, bbox_to_anchor=(0.5, 1.07),
              fontsize="small")
    fig.tight_layout()
    return fig


def plot_strategy_paths(trajectories, key, ylabel, title, event_years=()):
    """trajectories = {戦略: records}。年ごとの分担率（または任意の値）の推移"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    widths = {s: 6.0 - 1.4 * i for i, s in enumerate(STRATEGY_COLORS)}   # 重なっても見えるよう、後の線ほど細く
    items = []
    last = 0
    for s, recs in trajectories.items():
        rs = recs[1:]
        ys = [r[key] for r in rs]
        ax.step([r["year"] for r in rs], ys, where="mid", color=STRATEGY_COLORS[s], label=STRATEGY_LABELS[s],
                lw=widths.get(s, 2.2), solid_capstyle="butt")
        items.append((ys[-1], STRATEGY_LABELS[s], STRATEGY_COLORS[s]))
        last = max(last, rs[-1]["year"])
    _event_lines(ax, event_years)
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlim(0.5, last + 4)
    _end_labels(ax, last + 0.6, items, 0.06)
    ax.set_xlabel("year")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc="lower left", ncol=4, frameon=False, fontsize="small")
    fig.tight_layout()
    return fig


# ------------------------------------------------------------
# Notebook 04：関係状態の時間変化
# ------------------------------------------------------------
def plot_satisfaction_timeseries(records, title, event_years=(), observed_years=None):
    """1 組の満足度（A・B・関係全体）の推移。解消した年は × で示す。observed_years：横軸を観測期間全体にする"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    years = [r["year"] for r in records]
    for key, label, color, ls in (("satisfaction_A", "Partner A", PARTNER_COLORS["A"], "-"),
                                  ("satisfaction_B", "Partner B", PARTNER_COLORS["B"], "-"),
                                  ("relationship_satisfaction", "relationship", RELATION_COLOR, "--")):
        ax.plot(years, [r[key] for r in records], color=color, ls=ls, label=label, marker="o", ms=4)
    end = records[-1]
    if not end["continuing"]:
        ax.scatter([end["year"]], [end["relationship_satisfaction"]], marker="X", s=140, color=ALERT, zorder=6,
                   label=f"dissolved (year {end['year']})")
    _event_lines(ax, event_years)
    if observed_years:
        ax.set_xlim(-0.5, observed_years + 0.5)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("year")
    ax.set_ylabel("satisfaction (0-1)")
    ax.set_title(title)
    ax.legend(loc="lower left", ncol=4, frameon=False, fontsize="small")
    fig.tight_layout()
    return fig


def plot_yearly(series, key, ylabel, title, event_years=(), ylim=None, colors=None, labels=None):
    """series = {名前: records}。records の key を年ごとに描く。色は colors、なければ戦略の色か青の濃淡"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    names = list(series)
    shades = ramp(len(names))
    items = []
    last = 0
    for i, name in enumerate(names):
        rs = [r for r in series[name] if r.get(key) is not None]
        color = (colors or {}).get(name) or STRATEGY_COLORS.get(name) or shades[i]
        label = (labels or {}).get(name) or STRATEGY_LABELS.get(name) or str(name)
        ys = [r[key] for r in rs]
        ax.plot([r["year"] for r in rs], ys, color=color, label=label, marker="o", ms=3.5)
        items.append((ys[-1], label, color))
        last = max(last, rs[-1]["year"])
    _event_lines(ax, event_years)
    if ylim:
        ax.set_ylim(*ylim)
    ax.set_xlim(0, last + 4.5)
    _end_labels(ax, last + 0.5, items, 0.06)
    ax.set_xlabel("year")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc="best", frameon=False, fontsize="small")
    fig.tight_layout()
    return fig


def plot_survival(curves, title, theory=None, colors=None, labels=None, checkpoints=(5, 10, 20)):
    """curves = {名前: [継続率(0 年), ..., 継続率(T 年)]}。theory = {名前: 理論値のリスト}（点線）"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    names = list(curves)
    shades = ramp(len(names))
    items = []
    T = 0
    for i, name in enumerate(names):
        ys = curves[name]
        T = max(T, len(ys) - 1)
        color = (colors or {}).get(name) or STRATEGY_COLORS.get(name) or shades[i]
        label = (labels or {}).get(name) or STRATEGY_LABELS.get(name) or str(name)
        ax.step(range(len(ys)), ys, where="post", color=color, label=label)
        if theory and name in theory:
            ax.plot(range(len(theory[name])), theory[name], color=color, ls=":", lw=1.5)
        items.append((ys[-1], f"{label} {ys[-1]:.0%}", color))
    if theory:
        ax.plot([], [], color=NEUTRAL, ls=":", lw=1.5, label="theory  Π(1 - p)")
    for t in checkpoints:
        if t <= T:
            ax.axvline(t, color=NEUTRAL, lw=0.8, ls="--", zorder=0)
    ax.set_ylim(0, 1.05)
    ax.set_xlim(0, T + 5.5)
    _end_labels(ax, T + 0.4, items, 0.06)
    _year_axis(ax)
    ax.set_xlabel("years since start")
    ax.set_ylabel("continuation rate")
    ax.set_title(title)
    ax.legend(loc="lower left", frameon=False, fontsize="small")
    fig.tight_layout()
    return fig


def plot_duration_hist(outcomes, years, title):
    """解消した年の分布（棒）と、観測期間の終わりまで継続した（打ち切り）件数（別の色の棒）"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    counts = [0] * (years + 1)
    for o in outcomes:
        if o["dissolved"]:
            counts[o["dissolution_year"]] += 1
    censored = sum(1 for o in outcomes if not o["dissolved"])
    ax.bar(range(1, years + 1), counts[1:], color=RAMP[2], edgecolor="white", label="dissolved in year t")
    ax.bar([years + 2], [censored], color=NEUTRAL, edgecolor="white",
           label=f"continued to year {years} (censored)")
    ax.set_xticks(list(range(0, years + 1, 5)) + [years + 2])
    ax.set_xticklabels([str(t) for t in range(0, years + 1, 5)] + ["cens."])
    ax.set_xlabel("year of dissolution")
    ax.set_ylabel("count")
    ax.set_title(title)
    ax.legend(loc="upper center", frameon=False, fontsize="small")
    fig.tight_layout()
    return fig


# ------------------------------------------------------------
# Notebook 05：統合比較・感度分析
# ------------------------------------------------------------
def plot_checkpoints(results, title, checkpoints=(5, 10, 20)):
    """戦略 × {5, 10, 20 年} の継続率（誤差棒 = シード間の標準偏差）"""
    metrics = [(f"continuation_{t}", f"{t}-year") for t in checkpoints]
    fig = plot_strategy_metrics(results, metrics, title, ylim=(0, 1.15), fmt="{:.0%}", sd=True)
    fig.axes[0].set_ylabel("continuation rate")
    return fig


def plot_condition_bars(rows, key, title, ylabel, series=None, fmt="{:.0%}", ylim=(0, 1.15)):
    """rows = [{"name": 条件, 戦略: {キー: 値, キー_sd: 値}}]。x 軸 = 条件、棒 = 戦略"""
    import matplotlib.pyplot as plt
    series = series or [s for s in STRATEGY_COLORS if s in rows[0]]
    fig, ax = plt.subplots(figsize=(max(9, 1.9 * len(rows) + 2), 5))
    vals = {STRATEGY_LABELS[s]: [r[s][key] for r in rows] for s in series}
    errs = {STRATEGY_LABELS[s]: [r[s].get(key + "_sd") for r in rows] for s in series}
    cols = {STRATEGY_LABELS[s]: STRATEGY_COLORS[s] for s in series}
    _grouped(ax, [r["name"] for r in rows], list(vals), vals, cols,
             errs if any(v is not None for e in errs.values() for v in e) else None, fmt,
             label_bars=len(rows) * len(series) <= 12)
    ax.set_ylim(*ylim)
    ax.set_ylabel(ylabel)
    ax.set_title(title, pad=24)
    ax.legend(loc="upper center", ncol=len(series), frameon=False, bbox_to_anchor=(0.5, 1.07), fontsize="small")
    fig.tight_layout()
    return fig


def plot_short_vs_long(results, title):
    """横軸 = 1 年目の平均満足度、縦軸 = 20 年継続率（RQ6）。点 = 戦略、誤差棒 = シード間の標準偏差

    横軸の値が同じ戦略（例：Fixed と Adaptive は 1 年目の分担が同じ）は、重ならないよう少しだけ左右にずらす。
    """
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    xs = [r["first_year_mean_utility"] for r in results.values()]
    ys = [r["continuation_20"] for r in results.values()]
    dx = (max(xs) - min(xs)) or 0.05
    dy = (max(ys) - min(ys)) or 0.05
    seen = {}
    for s, r in results.items():
        x0 = r["first_year_mean_utility"]
        k = seen.get(round(x0, 4), 0)
        seen[round(x0, 4)] = k + 1
        x = x0 + k * dx * 0.04
        ax.errorbar(x, r["continuation_20"], yerr=r.get("continuation_20_sd") or 0, fmt="o", ms=11,
                    color=STRATEGY_COLORS[s], ecolor=STRATEGY_COLORS[s], capsize=4, label=STRATEGY_LABELS[s],
                    markeredgecolor="white", markeredgewidth=1.5)
        ax.annotate(STRATEGY_LABELS[s], (x, r["continuation_20"]), xytext=(9, 0), textcoords="offset points",
                    va="center", fontsize="small", color=TEXT, fontweight="bold")
    ax.set_xlim(min(xs) - dx * 0.3, max(xs) + dx * 0.5)
    ax.set_ylim(max(0, min(ys) - dy * 1.5), min(1, max(ys) + dy * 1.5))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_xlabel("short term: mean satisfaction in year 1")
    ax.set_ylabel("long term: 20-year continuation (model)")
    ax.set_title(title)
    ax.legend(loc="lower right", frameon=False, fontsize="small")
    fig.tight_layout()
    return fig
