# F3：Notebook 用のグラフ（matplotlib）
#
# 計算はすべて既存の .py（participants・preferences・matching_algorithms・relationship_stability・evaluation）で行い、
# ここでは「描くだけ」にする。matplotlib は関数の中で import するので、matplotlib がない環境でも
# このモジュールの import はでき、Core（starter.py・unittest）は標準ライブラリだけで動く。
#
# ■ グラフの約束
#   ・アルゴリズムの色は固定（Random：オレンジ、Greedy：青、Gale-Shapley：緑）。凡例と、線の端の名前の両方で示す
#   ・順序のある条件（適合度・ストレスの大小）は青の濃淡（薄い → 濃い）
#   ・図の文字は英語（Google Colab には日本語フォントがないことが多い）
#   ・関係継続のグラフはすべて「教育用の架空モデル」の結果（タイトルに model と書く）

ALG_COLORS = {"random": "#eb6834", "greedy": "#2a78d6", "gale_shapley": "#1baf7a"}
ALG_LABELS = {"random": "Random", "greedy": "Greedy", "gale_shapley": "Gale-Shapley"}
RAMP = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281", "#0d366b"]
NEUTRAL = "#8a8985"
TEXT = "#52514e"
ALERT = "#d03b3b"
ACTION_COLORS = {"accept": "#1baf7a", "replace": "#eda100", "reject": "#d03b3b"}


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


# ------------------------------------------------------------
# 希望スコア
# ------------------------------------------------------------
def plot_score_heatmap(a_ids, b_ids, values, rankings, title, value_label="score"):
    """行 = Group A、列 = Group B のヒートマップ。values[(a, b)] の値を色と数字で示す

    枠の太いセル = 相互承諾可能。斜線 = どちらかが受け入れない（成立し得ない組）。
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import Rectangle
    import preferences as pr
    cmap = LinearSegmentedColormap.from_list("score", ["#f4f7fc", "#86b6ef", "#2a78d6", "#104281"])
    fig, ax = plt.subplots(figsize=(1.3 * len(b_ids) + 3, 1.0 * len(a_ids) + 2))
    for i, a in enumerate(a_ids):
        for j, b in enumerate(b_ids):
            v = values[(a, b)]
            ok = pr.mutually_acceptable(rankings, a, b)
            ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fc=cmap(v), ec="white", lw=2))
            if not ok:
                ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fc="none", ec=NEUTRAL, lw=0, hatch="///"))
            else:
                ax.add_patch(Rectangle((j - 0.46, i - 0.46), 0.92, 0.92, fc="none", ec="black", lw=2))
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontweight="bold",
                    color="white" if v > 0.62 else TEXT)
    ax.set_xlim(-0.5, len(b_ids) - 0.5)
    ax.set_ylim(len(a_ids) - 0.5, -0.5)
    ax.set_xticks(range(len(b_ids)))
    ax.set_xticklabels(b_ids)
    ax.set_yticks(range(len(a_ids)))
    ax.set_yticklabels(a_ids)
    ax.set_xlabel("Group B")
    ax.set_ylabel("Group A")
    ax.set_title(f"{title}\n(bold frame = mutually acceptable, hatched = not acceptable; {value_label})")
    ax.grid(False)
    return fig


# ------------------------------------------------------------
# マッチングの図（二部グラフ）
# ------------------------------------------------------------
def draw_bipartite(ax, a_ids, b_ids, matching, title="", blocking=(), proposal=None, compat=None):
    """左に Group A、右に Group B。成立（仮）ペアを実線、blocking pair を赤の破線、提案を矢印で描く"""
    ya = {a: -i for i, a in enumerate(a_ids)}
    yb = {b: -i for i, b in enumerate(b_ids)}
    for a, b in matching.items():
        ax.plot([0, 1], [ya[a], yb[b]], color=ALG_COLORS["gale_shapley"], lw=3, zorder=1)
        if compat is not None:   # 線が交差しても重ならないよう、A 側の端の近く（線の 25% の位置）に書く
            ax.text(0.25, ya[a] + (yb[b] - ya[a]) * 0.25 + 0.14, f"{compat(a, b):.2f}", ha="center",
                    fontsize="small", color=TEXT, bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none"))
    for a, b in blocking:
        ax.plot([0, 1], [ya[a], yb[b]], color=ALERT, lw=2, ls="--", zorder=1)
    if proposal is not None:
        a, b, action = proposal
        ax.annotate("", xy=(0.93, yb[b]), xytext=(0.07, ya[a]),
                    arrowprops=dict(arrowstyle="->", color=ACTION_COLORS[action], lw=2.2, ls=":"), zorder=2)
    for x, ys in [(0, ya), (1, yb)]:
        for name, y in ys.items():
            ax.scatter([x], [y], s=650, color="white", edgecolor=TEXT, lw=1.5, zorder=3)
            ax.text(x, y, name, ha="center", va="center", fontsize="small", fontweight="bold", color=TEXT, zorder=4)
    ax.set_xlim(-0.35, 1.35)
    ax.set_ylim(-max(len(a_ids), len(b_ids)) + 0.4, 0.7)
    ax.set_axis_off()
    ax.set_title(title, fontsize="medium")


def plot_matching(a_ids, b_ids, matching, title, blocking=(), compat=None):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(4.2, 4.6))
    draw_bipartite(ax, a_ids, b_ids, matching, title, blocking, compat=compat)
    return fig


def plot_gs_steps(steps, a_ids, b_ids, cols=3):
    """Gale-Shapley の各ステップ：提案（矢印。緑 = 受け入れ、黄 = 入れ替え、赤 = 拒否）と、その後の仮マッチング"""
    import matplotlib.pyplot as plt
    rows = (len(steps) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(4.2 * cols, 4.4 * rows), squeeze=False)
    for k, ax in enumerate(axes.flat):
        if k >= len(steps):
            ax.set_axis_off()
            continue
        s = steps[k]
        note = f" ({s['rejected']} rejected)" if s["rejected"] else ""
        draw_bipartite(ax, a_ids, b_ids, s["tentative"],
                       f"step {s['step']}: {s['proposer']} -> {s['receiver']}  {s['action']}{note}",
                       proposal=(s["proposer"], s["receiver"], s["action"]))
    fig.suptitle("Gale-Shapley: proposals (arrow) and tentative matches (line)", fontsize="x-large")
    fig.tight_layout()
    return fig


# ------------------------------------------------------------
# アルゴリズムの比較
# ------------------------------------------------------------
def plot_metric_bars(summaries, key, title, ylabel, fmt="{:.0%}", err_key=None, ax=None, ylim=None):
    """アルゴリズムごとの指標の棒グラフ。err_key があれば誤差棒（シード間の標準偏差など）"""
    import matplotlib.pyplot as plt
    if ax is None:
        fig, ax = plt.subplots(figsize=(6.5, 4.2))
    else:
        fig = ax.figure
    names = list(summaries)
    vals = [summaries[n][key] if summaries[n][key] is not None else 0 for n in names]
    errs = [summaries[n].get(err_key) or 0 for n in names] if err_key else None
    bars = ax.bar([ALG_LABELS[n] for n in names], vals, color=[ALG_COLORS[n] for n in names], width=0.6,
                  yerr=errs, capsize=6, ecolor=TEXT)
    for i, (b, n, v) in enumerate(zip(bars, names, vals)):
        txt = "n/a" if summaries[n][key] is None else fmt.format(v)
        top = v + (errs[i] if errs else 0)                     # 誤差棒の上に書く
        ax.text(b.get_x() + b.get_width() * 0.5, top, txt, ha="center", va="bottom", color=TEXT, fontweight="bold")
    if ylim:
        ax.set_ylim(*ylim)
    else:
        ax.set_ylim(0, max([v + (errs[i] if errs else 0) for i, v in enumerate(vals)] + [1e-9]) * 1.2)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(axis="x", visible=False)
    return fig


def plot_trials(values, title, ylabel, fmt="{:.2f}"):
    """values = {アルゴリズム名: [試行ごとの値]}。点（少し横にずらす）と平均（横線）で、試行間のばらつきを示す"""
    import random
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4.4))
    jitter = random.Random(0)
    for i, (name, vals) in enumerate(values.items()):
        xs = [i + jitter.uniform(-0.18, 0.18) for _ in vals]
        ax.scatter(xs, vals, s=40, color=ALG_COLORS.get(name, NEUTRAL), alpha=0.7, edgecolor="white", lw=0.8)
        m = sum(vals) / len(vals)
        ax.plot([i - 0.3, i + 0.3], [m, m], color=TEXT, lw=2.5)
        ax.text(i + 0.33, m, f"mean {fmt.format(m)}", va="center", fontsize="small", color=TEXT)
    ax.set_xticks(range(len(values)))
    ax.set_xticklabels([ALG_LABELS.get(n, n) for n in values])
    ax.set_xlim(-0.6, len(values) - 0.1)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(axis="x", visible=False)
    return fig


# ------------------------------------------------------------
# 関係継続（教育用の架空モデル）
# ------------------------------------------------------------
def plot_survival(curves, title, colors=None, theory=None, checkpoints=(5, 10, 20)):
    """curves = {ラベル: [0 年後, 1 年後, ... の継続率]}。theory = {ラベル: [理論値]}（破線）"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ends = []
    for k, (label, ys) in enumerate(curves.items()):
        color = (colors or {}).get(label, ramp(len(curves))[k])
        ax.plot(range(len(ys)), ys, color=color, label=label)
        ends.append((ys[-1], label, color))
        if theory and label in theory:
            ax.plot(range(len(theory[label])), theory[label], color=color, ls="--", lw=1.3)
    years = max(len(ys) for ys in curves.values()) - 1
    for t in checkpoints:
        if t <= years:
            ax.axvline(t, color=NEUTRAL, lw=0.8, ls=":")
    ax.set_ylim(0, 1.05)
    ax.set_xlim(0, years * 1.28)
    _end_labels(ax, years + years * 0.01, ends)
    ax.set_xlabel("years after matching")
    ax.set_ylabel("continuation rate")
    ax.set_title(title + ("  (dashed = theory (1-p)^t)" if theory else ""))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _p: f"{v:.0%}"))
    ax.legend(loc="lower left")
    return fig


def plot_duration_hist(records, years, title):
    """関係解消までに継続した年数の分布（解消したペア）と、観測終了まで継続したペア（打ち切り）を分けて示す"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 4.4))
    dissolved = [r["dissolution_year"] for r in records if r["dissolved"]]
    censored = sum(1 for r in records if r["censored"])
    counts = [dissolved.count(t) for t in range(1, years + 1)]
    ax.bar(range(1, years + 1), counts, color="#2a78d6", width=0.8, label="dissolved in year t")
    ax.bar([years + 2], [censored], color=NEUTRAL, width=1.6, hatch="//", edgecolor="white",
           label=f"still together at {years} (censored)")
    ax.set_xticks(list(range(1, years + 1, max(1, years // 10))) + [years + 2])
    ax.set_xticklabels([str(t) for t in range(1, years + 1, max(1, years // 10))] + [f">{years}"])
    ax.set_xlabel("year of dissolution")
    ax.set_ylabel("number of pairs (all replicates)")
    ax.set_title(title)
    ax.legend()
    ax.grid(axis="x", visible=False)
    return fig


def plot_grouped(summaries, keys, title, ylabel="rate"):
    """keys = [(指標のキー, 表示名)]。アルゴリズムごとに、複数の指標を並べた棒グラフ（例：成立率と 10 年長期成立率）"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 4.6))
    names = list(summaries)
    width = 0.8 / len(keys)
    shades = ramp(len(keys)) if len(keys) > 1 else [RAMP[2]]
    for k, (key, label) in enumerate(keys):
        vals = [summaries[n][key] or 0 for n in names]
        xs = [i + (k - (len(keys) - 1) / 2) * width for i in range(len(names))]
        bars = ax.bar(xs, vals, width * 0.92, color=shades[k], label=label)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.0%}", ha="center", va="bottom", fontsize="small", color=TEXT)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels([ALG_LABELS[n] for n in names])
    ax.set_ylim(0, 1.3)                                        # 凡例の場所を上に空ける
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_ylabel(ylabel)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _p: f"{v:.0%}"))
    ax.set_title(title)
    ax.legend(loc="upper center", ncol=min(4, len(keys)), fontsize="small")
    ax.grid(axis="x", visible=False)
    return fig


def plot_sensitivity(xs, series, xlabel, title, ylabel="10-year continuation rate"):
    """series = {アルゴリズム名: [xs ごとの値]}"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ends = []
    for name, ys in series.items():
        ax.plot(xs, ys, marker="o", ms=7, color=ALG_COLORS[name], label=ALG_LABELS[name], mec="white", mew=1.5)
        ends.append((ys[-1], ALG_LABELS[name], ALG_COLORS[name]))
    span = xs[-1] - xs[0]
    ax.set_xlim(xs[0] - span * 0.03, xs[-1] + span * 0.3)
    _end_labels(ax, xs[-1] + span * 0.02, ends)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _p: f"{v:.0%}"))
    ax.set_title(title)
    ax.legend(loc="best")
    return fig


def plot_compat_distribution(values, title):
    """values = {アルゴリズム名: [成立ペアの初期適合度]}。点の分布と平均"""
    return plot_trials(values, title, "initial compatibility of matched pairs")


def save(fig, path):
    import os
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.savefig(path)
    return path
