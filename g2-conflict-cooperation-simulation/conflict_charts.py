# G2：Notebook 用のグラフ（matplotlib）
#
# 計算はすべて既存の .py で行い、ここでは「描くだけ」にする。matplotlib は関数の中で import するので、
# matplotlib がない環境でもこのモジュールの import はでき、Core（starter.py・unittest）は標準ライブラリだけで動く。
# ネットワーク図も matplotlib だけで描く（NetworkX は不要。使ってもよい）。
#
# ■ グラフの約束
#   ・戦略の色は固定（Always Cooperate 青、Always Non-cooperate オレンジ、Tit-for-Tat 緑、Conditional 紫）
#   ・関係状態の色は固定（Cooperation 青、Neutral 灰色、Tension 黄、Conflict 赤）。状態名も図の中に書く
#   ・アルゴリズムの色は固定（全探索 濃い灰色、Greedy ピンク、DFS 青、BFS 緑）
#   ・図の文字は英語（Google Colab には日本語フォントがないことが多い）
#   ・すべて教育用の架空モデルの結果（タイトルに model と書く）。実行時間だけは実測値（measured）

import math

STRATEGY_COLORS = {"always_cooperate": "#2a78d6", "always_noncooperate": "#eb6834", "tit_for_tat": "#1baf7a",
                   "conditional": "#6250d6"}
STATE_COLORS = {"Cooperation": "#2a78d6", "Neutral": "#b8b7b3", "Tension": "#eda100", "Conflict": "#d03b3b"}
ALGO_COLORS = {"exhaustive": "#3d3c39", "greedy": "#e87ba4", "dfs": "#2a78d6", "bfs": "#1baf7a"}
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


def _bars(ax, labels, values, colors, fmt="{:.2f}", errors=None):
    bars = ax.bar(range(len(values)), values, 0.62, color=colors, edgecolor="white",
                  yerr=errors, capsize=4 if errors else 0, error_kw={"ecolor": TEXT, "lw": 1})
    for i, (b, v) in enumerate(zip(bars, values)):
        top = v + (errors[i] if errors else 0)
        ax.annotate(fmt.format(v), (b.get_x() + b.get_width() / 2, top), xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize="small", color=TEXT)
    ax.set_xticks(range(len(values)))
    ax.set_xticklabels(labels)
    ax.grid(axis="x", visible=False)


def plot_bar(labels, values, title, ylabel, colors=None, fmt="{:.2f}", errors=None, ylim=None):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(max(7, 1.7 * len(labels) + 2), 4.8))
    _bars(ax, labels, values, colors or ramp(len(values)), fmt, errors)
    ax.set_ylim(*(ylim or (0, max(v + (e or 0) for v, e in zip(values, errors or [0] * len(values))) * 1.18 or 1)))
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    fig.tight_layout()
    return fig


def plot_grouped(groups, series, values, title, ylabel, colors=None, fmt="{:.2f}", errors=None, ylim=(0, 1.1)):
    """groups（x 軸）× series（棒）。values[series] = [groups の順]。errors も同じ形（なければ None）"""
    import matplotlib.pyplot as plt
    n = len(series)
    fig, ax = plt.subplots(figsize=(max(8, (0.45 * n + 0.8) * len(groups) + 2), 5.2))
    w = 0.8 / n
    shades = ramp(n)
    for i, s in enumerate(series):
        xs = [g + (i - (n - 1) / 2) * w for g in range(len(groups))]
        err = errors[s] if errors else None
        bars = ax.bar(xs, values[s], w * 0.92, color=(colors or {}).get(s, shades[i]), label=s, edgecolor="white",
                      yerr=err, capsize=3 if err else 0, error_kw={"ecolor": TEXT, "lw": 1})
        if n * len(groups) <= 16:
            for j, (b, v) in enumerate(zip(bars, values[s])):
                ax.annotate(fmt.format(v), (b.get_x() + b.get_width() / 2, v + (err[j] if err else 0)), xytext=(0, 3),
                            textcoords="offset points", ha="center", va="bottom", fontsize="x-small", color=TEXT)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups)
    ax.set_ylim(*ylim)
    ax.set_ylabel(ylabel)
    ax.set_title(title, pad=26 if n <= 4 else 40)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.08 if n <= 4 else 1.14), ncol=min(n, 4), frameon=False,
              fontsize="small")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return fig


# ------------------------------------------------------------
# ゲーム理論
# ------------------------------------------------------------
def plot_payoff_matrix(m, title="Payoff matrix (row player, column player) - fictional"):
    """2×2 の利得行列。色 = 行の国家の利得、各セルに (行, 列) の利得を書く"""
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("pay", ["#f4f7fc", "#86b6ef", "#2a78d6", "#104281"])
    acts = ["C", "N"]
    names = {"C": "Cooperate", "N": "Non-cooperate"}
    vals = [[m[a][b] for b in acts] for a in acts]
    lo, hi = min(min(r) for r in vals), max(max(r) for r in vals)
    fig, ax = plt.subplots(figsize=(6.5, 5))
    im = ax.imshow(vals, cmap=cmap, vmin=lo, vmax=hi)
    for i, a in enumerate(acts):
        for j, b in enumerate(acts):
            v = m[a][b]
            ax.text(j, i, f"({m[a][b]}, {m[b][a]})", ha="center", va="center", fontsize="large", fontweight="bold",
                    color="white" if (v - lo) / ((hi - lo) or 1) > 0.55 else TEXT)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([names[a] for a in acts])
    ax.set_yticks([0, 1])
    ax.set_yticklabels([names[a] for a in acts])
    ax.set_xlabel("Country B (column)")
    ax.set_ylabel("Country A (row)")
    ax.grid(False)
    cb = fig.colorbar(im, ax=ax)
    cb.set_label("payoff of Country A")
    ax.set_title(title, fontsize="medium")
    fig.tight_layout()
    return fig


# ------------------------------------------------------------
# 状態遷移
# ------------------------------------------------------------
def plot_transition_matrix(matrix, states, title):
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("p", ["#ffffff", "#86b6ef", "#2a78d6", "#104281"])
    fig, ax = plt.subplots(figsize=(6.8, 5.4))
    im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=1)
    for i, row in enumerate(matrix):
        for j, p in enumerate(row):
            ax.text(j, i, f"{p:.2f}", ha="center", va="center", fontsize="small",
                    color="white" if p > 0.55 else TEXT, fontweight="bold")
    ax.set_xticks(range(len(states)))
    ax.set_xticklabels(states)
    ax.set_yticks(range(len(states)))
    ax.set_yticklabels(states)
    ax.set_xlabel("next state")
    ax.set_ylabel("current state")
    ax.grid(False)
    fig.colorbar(im, ax=ax, label="probability")
    ax.set_title(title, fontsize="medium")
    fig.tight_layout()
    return fig


def plot_transition_diagram(matrix, states, title, min_prob=0.05):
    """状態遷移図：4 つの状態を横に並べ、確率 min_prob 以上の遷移を矢印で示す（太さ = 確率）"""
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, Circle
    fig, ax = plt.subplots(figsize=(11, 4.6))
    xs = [i * 3.0 for i in range(len(states))]
    r = 0.62
    for i, s in enumerate(states):
        ax.add_patch(Circle((xs[i], 0), r, fc=STATE_COLORS[s], ec="white", lw=2, zorder=3))
        p = matrix[i][i]
        ax.text(xs[i], 0, f"{s}\nstay {p:.2f}", ha="center", va="center", color="white" if s != "Neutral" else TEXT,
                fontweight="bold", fontsize="x-small", zorder=4)
    for i in range(len(states)):
        for j in range(len(states)):
            p = matrix[i][j]
            if i == j or p < min_prob:
                continue
            up = j > i                                   # 悪化（右へ）は上、改善（左へ）は下にカーブ
            rad = -0.35 if up else -0.35
            arrow = FancyArrowPatch((xs[i], 0), (xs[j], 0), connectionstyle=f"arc3,rad={rad}",
                                    arrowstyle="-|>", mutation_scale=14, lw=0.6 + 6 * p,
                                    color=STATE_COLORS["Conflict"] if up else STATE_COLORS["Cooperation"],
                                    alpha=0.75, shrinkA=r * 30, shrinkB=r * 30, zorder=2)
            ax.add_patch(arrow)
            mid = (xs[i] + xs[j]) / 2
            h = abs(xs[j] - xs[i]) * 0.18 * (1 if up else -1)
            ax.text(mid, h, f"{p:.2f}", ha="center", va="center", fontsize="x-small", color=TEXT,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.9))
    ax.set_xlim(-1.2, xs[-1] + 1.2)
    ax.set_ylim(-2.2, 2.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title + "\n(red arrows: worsening, blue arrows: improvement; width = probability)", fontsize="medium")
    fig.tight_layout()
    return fig


def plot_state_timeline(records, title, edges=None):
    """エッジ（行）× 年（列）の関係状態を色で示す"""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    import state_transitions as st
    edges = edges or list(records[0]["states"])
    years = [r["year"] for r in records[1:]]
    fig, ax = plt.subplots(figsize=(11, 0.55 * len(edges) + 1.8))
    for i, e in enumerate(edges):
        for r in records[1:]:
            ax.barh(i, 1, left=r["year"] - 0.5, height=0.8, color=STATE_COLORS[r["states"][e]], edgecolor="white",
                    linewidth=0.5)
    ax.set_yticks(range(len(edges)))
    ax.set_yticklabels([f"{u}-{v}" for u, v in edges])
    ax.invert_yaxis()
    ax.set_xlim(0.5, years[-1] + 0.5)
    ax.set_xlabel("year")
    ax.grid(False)
    ax.legend(handles=[Patch(color=STATE_COLORS[s], label=s) for s in st.STATES], loc="center left",
              bbox_to_anchor=(1.01, 0.5), frameon=False, fontsize="small")
    ax.set_title(title)
    fig.tight_layout()
    return fig


def plot_lines(xs, series, title, ylabel, xlabel="year", colors=None, ylim=(0, 1.05), styles=None):
    """series = {名前: [y...]}"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    shades = ramp(len(series))
    for i, (name, ys) in enumerate(series.items()):
        ax.plot(xs, ys, color=(colors or {}).get(name, shades[i]), label=name,
                ls=(styles or {}).get(name, "-"))
    if ylim:
        ax.set_ylim(*ylim)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc="best", frameon=False, fontsize="small")
    fig.tight_layout()
    return fig


# ------------------------------------------------------------
# モンテカルロ
# ------------------------------------------------------------
def plot_hist(values, title, xlabel, color=None, bins=20):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.hist(values, bins=bins, color=color or RAMP[2], edgecolor="white")
    mean = sum(values) / len(values)
    ax.axvline(mean, color=TEXT, lw=1.5, ls="--")
    ax.annotate(f"mean {mean:.3f}", (mean, 1), xycoords=("data", "axes fraction"), xytext=(4, -4),
                textcoords="offset points", va="top", fontsize="small", color=TEXT)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("number of runs")
    ax.set_title(title)
    fig.tight_layout()
    return fig


def plot_running_mean(values, title, ylabel):
    """試行回数を増やしたときの推定値（それまでの平均）の変化"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    means, s = [], 0.0
    for i, v in enumerate(values, 1):
        s += v
        means.append(s / i)
    ax.plot(range(1, len(values) + 1), means, color=RAMP[3])
    ax.axhline(means[-1], color=NEUTRAL, lw=1, ls=":")
    ax.set_xscale("log")
    ax.set_xlabel("number of runs (log scale)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    fig.tight_layout()
    return fig


# ------------------------------------------------------------
# ネットワーク
# ------------------------------------------------------------
def circle_layout(nodes):
    n = len(nodes)
    return {v: (math.cos(math.pi / 2 - 2 * math.pi * i / max(n, 1)), math.sin(math.pi / 2 - 2 * math.pi * i / max(n, 1)))
            for i, v in enumerate(nodes)}


def draw_network(ax, nodes, edges, title, states=None, highlight=(), pos=None, labels=True):
    """国家（ノード）と関係（エッジ）を描く。states があればエッジを状態の色に、highlight のエッジは太い枠"""
    pos = pos or circle_layout(nodes)
    for e in edges:
        (x1, y1), (x2, y2) = pos[e[0]], pos[e[1]]
        color = STATE_COLORS[states[e]] if states else NEUTRAL
        if e in highlight:
            ax.plot([x1, x2], [y1, y2], color="black", lw=9, solid_capstyle="round", zorder=1)
        ax.plot([x1, x2], [y1, y2], color=color, lw=4.5, solid_capstyle="round", zorder=2)
    for v in nodes:
        x, y = pos[v]
        ax.scatter([x], [y], s=900 if len(nodes) <= 12 else 160, color="white", edgecolor="#3d3c39", lw=2, zorder=3)
        if labels:
            ax.text(x, y, v, ha="center", va="center", fontweight="bold", color="#3d3c39", zorder=4,
                    fontsize="medium" if len(nodes) <= 12 else "x-small")
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.35, 1.35)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize="medium")


def plot_networks(networks, title=None, states=None, highlight=None, ncols=None):
    """networks = [(名前, ノード, エッジ)]。小さなネットワーク図を並べる"""
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    k = len(networks)
    ncols = ncols or min(k, 4)
    nrows = (k + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.6 * ncols, 3.8 * nrows), squeeze=False)
    for i, (name, nodes, edges) in enumerate(networks):
        st_i = states[i] if isinstance(states, list) else states
        hl = highlight[i] if isinstance(highlight, list) else (highlight or ())
        draw_network(axes[i // ncols][i % ncols], nodes, edges, name, st_i, hl)
    for j in range(k, nrows * ncols):
        axes[j // ncols][j % ncols].axis("off")
    if states is not None:
        handles = [Line2D([], [], color=c, lw=4, label=s) for s, c in STATE_COLORS.items()]
        if highlight:
            handles.append(Line2D([], [], color="black", lw=7, label="supported"))
        fig.legend(handles=handles, loc="lower center", ncol=len(handles), frameon=False, fontsize="small")
    if title:
        fig.suptitle(title)
    fig.tight_layout(rect=(0, 0.07 if states is not None else 0, 1, 1))
    return fig


def plot_search_orders(adj, start, dfs_result, bfs_result, pos=None):
    """DFS と BFS の訪問順を並べて示す（ノードの中の数字 = 訪問した順番）"""
    import matplotlib.pyplot as plt
    nodes = sorted(adj)
    edges = sorted({tuple(sorted((u, v))) for u in adj for v in adj[u]})
    pos = pos or circle_layout(nodes)
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    for ax, res, name, key in ((axes[0], dfs_result, "DFS (stack)", "dfs"), (axes[1], bfs_result, "BFS (queue)", "bfs")):
        draw_network(ax, nodes, edges, f"{name} from {start}", labels=False, pos=pos)
        for i, v in enumerate(res["order"], 1):
            x, y = pos[v]
            ax.text(x, y, f"{v}\n{i}", ha="center", va="center", fontsize="small", fontweight="bold",
                    color=ALGO_COLORS[key], zorder=5)
        parent = res["parent"]
        for v, p in parent.items():
            if p is not None:
                (x1, y1), (x2, y2) = pos[p], pos[v]
                ax.plot([x1, x2], [y1, y2], color=ALGO_COLORS[key], lw=2.5, zorder=2.5)
    fig.suptitle("Visit order (number) and search tree (colored edges)")
    fig.tight_layout()
    return fig


def plot_loglog(xs, series, title, ylabel, colors=None):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    for name, ys in series.items():
        ax.plot(xs, ys, marker="o", color=(colors or {}).get(name), label=name)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("number of nodes V (log scale)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc="upper left", frameon=False, fontsize="small")
    fig.tight_layout()
    return fig
