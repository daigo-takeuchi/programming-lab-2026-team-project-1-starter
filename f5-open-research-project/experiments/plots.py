# F5：Notebook 用のグラフ（matplotlib）
#
# 計算・測定は algorithms/ と experiments/ で行い、ここでは「描くだけ」にする。
# matplotlib は関数の中で import するので、matplotlib がない環境でもこのモジュールの import はでき、
# Core（starter.py・experiments・unittest）は標準ライブラリだけで動く。
#
# ■ グラフの約束
#   ・アルゴリズムの色は、run_comparison の行に出てくる順に固定の色を割り当てる（A 青、B オレンジ、…）
#   ・「前処理を含む」線は同じ色の破線
#   ・図の文字は英語（Google Colab には日本語フォントがないことが多い）
#   ・実測値のグラフには「measured」、理論の形のグラフには「theory」とタイトルに書く

import math

COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6"]
TEXT = "#52514e"
NEUTRAL = "#8a8985"

THEORY = {
    "O(1)": lambda n: 1.0,
    "O(log N)": lambda n: math.log2(n) if n > 1 else 1.0,
    "O(N)": lambda n: float(n),
    "O(N log N)": lambda n: n * math.log2(n) if n > 1 else 1.0,
    "O(N^2)": lambda n: float(n) ** 2,
}


def setup_style(font_scale=1.0):
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.figsize": (9.5, 5.2), "figure.dpi": 100, "savefig.dpi": 150, "savefig.bbox": "tight",
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


def algorithm_colors(rows):
    """行に出てくるアルゴリズムの順に色を決める（{key: 色}）"""
    keys = []
    for r in rows:
        if r["algorithm"] not in keys:
            keys.append(r["algorithm"])
    return {k: COLORS[i % len(COLORS)] for i, k in enumerate(keys)}


def _series(rows, key, value):
    pts = sorted((r["n"], r[value]) for r in rows if r["algorithm"] == key)
    return [p[0] for p in pts], [p[1] for p in pts]


def _labels(rows):
    out = {}
    for r in rows:
        out.setdefault(r["algorithm"], r["label"])
    return out


def _end_label(ax, x, y, text, color):
    ax.annotate(text, (x, y), xytext=(6, 0), textcoords="offset points", va="center", fontsize="small",
                color=TEXT, fontweight="bold", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=color, lw=1.2))


def plot_time_vs_size(rows, title="Execution time vs input size (measured)", include_prep=True, log=True,
                      value="run_s"):
    """横軸 = 入力サイズ N、縦軸 = 実行時間（ms）。前処理があるアルゴリズムは「前処理 + 実行」も破線で描く"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    colors, labels = algorithm_colors(rows), _labels(rows)
    for k, c in colors.items():
        xs, ys = _series(rows, k, value)
        ys = [y * 1e3 for y in ys]
        ax.plot(xs, ys, marker="o", ms=7, color=c, label=labels[k])
        _end_label(ax, xs[-1], ys[-1], labels[k].split(":")[0], c)
        if include_prep and any(r["prep_s"] > 0 for r in rows if r["algorithm"] == k):
            xs2, ys2 = _series(rows, k, "total_s")
            ax.plot(xs2, [y * 1e3 for y in ys2], marker="s", ms=6, color=c, ls="--",
                    label=labels[k] + " (prep + run)")
    if log:
        ax.set_xscale("log")
        ax.set_yscale("log")
    ax.set_xlabel("input size N" + (" (log scale)" if log else ""))
    ax.set_ylabel("time [ms]" + (" (log scale)" if log else ""))
    ax.set_title(title)
    ax.legend(loc="upper left", frameon=False, fontsize="small")
    fig.tight_layout()
    return fig


def plot_bars_by_size(rows, title="Algorithm A vs B at each input size (measured)", value="run_s"):
    """入力サイズごとに、アルゴリズムの実行時間（中央値）を棒で並べる。誤差棒 = 最小〜最大"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    colors, labels = algorithm_colors(rows), _labels(rows)
    sizes = sorted({r["n"] for r in rows})
    w = 0.8 / len(colors)
    for i, (k, c) in enumerate(colors.items()):
        xs, vals, lo, hi = [], [], [], []
        for j, n in enumerate(sizes):
            r = next(r for r in rows if r["algorithm"] == k and r["n"] == n)
            xs.append(j + (i - (len(colors) - 1) / 2) * w)
            v = r[value] * 1e3
            vals.append(v)
            if value == "run_s":
                lo.append(v - r["run_min_s"] * 1e3)
                hi.append(r["run_max_s"] * 1e3 - v)
        bars = ax.bar(xs, vals, w * 0.92, color=c, label=labels[k], edgecolor="white",
                      yerr=[lo, hi] if lo else None, capsize=3, error_kw={"ecolor": TEXT, "lw": 1})
        tops = [v + (hi[j] if hi else 0) for j, v in enumerate(vals)]     # 誤差棒の上に数値を書く
        for b, v, top in zip(bars, vals, tops):
            ax.annotate(f"{v:.3g}", (b.get_x() + b.get_width() / 2, top), xytext=(0, 3),
                        textcoords="offset points", ha="center", va="bottom", fontsize="small", color=TEXT)
    ax.set_xticks(range(len(sizes)))
    ax.set_xticklabels([f"N = {n:,}" for n in sizes])
    ax.set_yscale("log")
    ax.set_ylabel("time [ms] (log scale)")
    ax.set_title(title, pad=22)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.06), ncol=len(colors), frameon=False, fontsize="small")
    fig.tight_layout()
    return fig


def plot_theory(sizes, complexities, title="Growth of theoretical complexity (theory, normalized)"):
    """理論計算量の形を比べる。complexities = {名前: "O(N)" など}。最小の N で 1 になるよう正規化"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    xs = list(sizes)
    for i, (name, order) in enumerate(complexities.items()):
        f = THEORY[order]
        ys = [f(n) / f(xs[0]) for n in xs]
        ax.plot(xs, ys, marker="o", ms=5, color=COLORS[i % len(COLORS)], label=f"{name}: {order}")
        _end_label(ax, xs[-1], ys[-1], order, COLORS[i % len(COLORS)])
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("input size N (log scale)")
    ax.set_ylabel(f"relative cost (N = {xs[0]:,} → 1)")
    ax.set_title(title)
    ax.legend(loc="upper left", frameon=False, fontsize="small")
    fig.tight_layout()
    return fig


def plot_measured_vs_theory(rows, complexities, title="Measured growth vs theory (both normalized)"):
    """実測時間の増え方と、理論計算量の増え方を、最小の N で 1 にそろえて比べる"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    colors, labels = algorithm_colors(rows), _labels(rows)
    for k, c in colors.items():
        xs, ys = _series(rows, k, "run_s")
        ax.plot(xs, [y / ys[0] for y in ys], marker="o", ms=7, color=c, label=f"{labels[k]} (measured)")
        if k in complexities:
            f = THEORY[complexities[k]]
            ax.plot(xs, [f(n) / f(xs[0]) for n in xs], color=c, ls=":", lw=1.8,
                    label=f"{complexities[k]} (theory)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("input size N (log scale)")
    ax.set_ylabel("relative to smallest N")
    ax.set_title(title)
    ax.legend(loc="upper left", frameon=False, fontsize="small")
    fig.tight_layout()
    return fig


def plot_operations(rows, title="Number of comparisons vs input size (counted)"):
    """比較回数など、実行環境によらない指標（rows の operations）"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    colors, labels = algorithm_colors(rows), _labels(rows)
    for k, c in colors.items():
        xs, ys = _series(rows, k, "operations")
        if any(y is None for y in ys):
            continue
        ax.plot(xs, ys, marker="o", ms=7, color=c, label=labels[k])
        _end_label(ax, xs[-1], ys[-1], f"{ys[-1]:,}", c)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("input size N (log scale)")
    ax.set_ylabel("comparisons (log scale)")
    ax.set_title(title)
    ax.legend(loc="upper left", frameon=False, fontsize="small")
    fig.tight_layout()
    return fig


def plot_repeats(rows, n, title=None):
    """ある N での反復測定のばらつき（各測定値を点で、中央値を横線で）"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    colors, labels = algorithm_colors(rows), _labels(rows)
    for i, (k, c) in enumerate(colors.items()):
        r = next(r for r in rows if r["algorithm"] == k and r["n"] == n)
        ts = [t * 1e3 for t in r["times"]]
        ax.scatter([i + (j - (len(ts) - 1) / 2) * 0.04 for j in range(len(ts))], ts, color=c, s=40,
                   edgecolor="white", zorder=3)
        ax.hlines(r["run_s"] * 1e3, i - 0.25, i + 0.25, color=TEXT, lw=2, zorder=4)
        ax.annotate(f"median {r['run_s'] * 1e3:.3g} ms", (i + 0.27, r["run_s"] * 1e3), va="center",
                    fontsize="small", color=TEXT)
    ax.set_xticks(range(len(colors)))
    ax.set_xticklabels([labels[k] for k in colors])
    ax.set_xlim(-0.6, len(colors) - 0.1)
    ax.set_yscale("log")
    ax.set_ylabel("time [ms] (log scale)")
    ax.set_title(title or f"Repeated measurements at N = {n:,} (measured)")
    fig.tight_layout()
    return fig
