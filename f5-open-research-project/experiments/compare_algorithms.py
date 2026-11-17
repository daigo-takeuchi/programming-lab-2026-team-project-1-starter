# F5：入力サイズを変えて、Algorithm A と Algorithm B を「同じ課題・同じ入力」で比較する
#
#   python3 -m experiments.compare_algorithms
#   python3 -m experiments.compare_algorithms --sizes 100 1000 10000 --repeat 7 --queries 200
#   python3 -m experiments.compare_algorithms --hit-ratio 0.0 --csv results.csv   # 見つからない値だけ（最悪ケース）
#
# ■ 比較の手順（入力サイズ N ごと）
#   1. 入力データを作る              … データ生成時間（gen_s）
#   2. 前処理（例：ソート）          … 前処理時間（prep_s）。前処理がないアルゴリズムは 0
#   3. アルゴリズムを実行する        … 実行時間（run_s）。repeat 回測定した中央値
#   4. 結果を検証する                … 検証時間（verify_s）。正しくなければ、その行は correct=False
#   5. アルゴリズム同士の結果を比べる … consistent（同じ答えか）
#
# ■ 「課題（task）」の形
#   比較の手順は課題によらない。研究テーマを変えたら、make_search_task と同じ形の辞書を作って
#   run_comparison に渡す（README「研究テーマを変更する方法」）。
#     task = {"name", "description", "make_input": f(n, seed) -> 入力,
#             "algorithms": [{"key", "label", "prepare": f(入力) -> 前処理の結果 または None,
#                             "run": f(前処理の結果, 入力) -> 結果, "count": f(前処理の結果, 入力) -> 数 または None,
#                             "mutates": 入力を変更するなら True}],
#             "verify": f(入力, 前処理の結果, 結果) -> bool,
#             "answer": f(入力, 前処理の結果, 結果) -> アルゴリズム間で比べられる形の答え}

import argparse
import csv
import random
import sys
from pathlib import Path

if __package__ in (None, ""):                       # python3 experiments/compare_algorithms.py でも動くように
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from algorithms import algorithm_a as alg_a
from algorithms import algorithm_b as alg_b
from experiments.benchmark import measure, timed

DEFAULT_SIZES = (100, 1_000, 10_000)


# ------------------------------------------------------------
# 初期デモの課題：探索（線形探索 vs 二分探索）
# ------------------------------------------------------------
def make_search_input(n, seed=0, queries=100, hit_ratio=0.5, order="random"):
    """探索の入力：N 個の整数データと、探す値（queries 個）

    hit_ratio：探す値のうち、データに含まれる値の割合（0 なら全部見つからない = 線形探索の最悪ケース）
    order    ："random"（並びはランダム）、"sorted"（昇順）、"reversed"（降順）
    """
    if n < 0 or queries < 0 or not 0 <= hit_ratio <= 1:
        raise ValueError("n・queries は 0 以上、hit_ratio は 0〜1 にしてください")
    rng = random.Random(seed)
    data = rng.sample(range(10 * max(n, 1)), n)        # 重複のない整数（値の範囲は 0〜10N）
    if order == "sorted":
        data.sort()
    elif order == "reversed":
        data.sort(reverse=True)
    elif order != "random":
        raise ValueError(f"order は random・sorted・reversed のどれかにしてください（{order!r}）")
    present = set(data)
    keys = []
    for _ in range(queries):
        if data and rng.random() < hit_ratio:
            keys.append(rng.choice(data))              # データに含まれる値
        else:
            k = rng.randrange(-10 * max(n, 1), 0)      # 必ず含まれない値（負の数）
            keys.append(k)
    assert all((k in present) or k < 0 for k in keys)
    return {"data": data, "queries": keys, "n": n, "seed": seed, "hit_ratio": hit_ratio, "order": order}


def _run_linear(_prepared, inp):
    return [alg_a.linear_search(inp["data"], k) for k in inp["queries"]]


def _count_linear(_prepared, inp):
    return sum(alg_a.linear_search_count(inp["data"], k)[1] for k in inp["queries"])


def _run_binary(prepared, inp):
    return [alg_b.binary_search(prepared, k) for k in inp["queries"]]


def _count_binary(prepared, inp):
    return sum(alg_b.binary_search_count(prepared, k)[1] for k in inp["queries"])


def _searched_array(inp, prepared):
    """結果の添字が指す配列（前処理があれば前処理後の配列）"""
    return prepared if prepared is not None else inp["data"]


def verify_search(inp, prepared, result):
    """探索結果の検証：見つかった添字の要素が探す値と等しく、-1 なら本当に含まれない（Python の set と照合）"""
    arr = _searched_array(inp, prepared)
    present = set(inp["data"])
    if len(result) != len(inp["queries"]):
        return False
    for k, idx in zip(inp["queries"], result):
        if idx == -1:
            if k in present:
                return False
        elif not (0 <= idx < len(arr) and arr[idx] == k):
            return False
        elif any(arr[j] == k for j in range(idx)):   # 「最初の位置」になっているか
            return False
    return True


def search_answer(inp, prepared, result):
    """アルゴリズム間で比べる答え：各探索値が「見つかったか」（添字は配列が違うので比べない）"""
    return [idx != -1 for idx in result]


def make_search_task(queries=100, hit_ratio=0.5, order="random"):
    return {
        "name": "search",
        "description": f"N 個の整数から {queries} 個の値を探す（含まれる割合 {hit_ratio:.0%}、並び {order}）",
        "make_input": lambda n, seed: make_search_input(n, seed, queries, hit_ratio, order),
        "algorithms": [
            {"key": "A", "label": f"A: {alg_a.NAME}", "prepare": None, "run": _run_linear, "count": _count_linear,
             "mutates": False, "complexity": alg_a.COMPLEXITY},
            {"key": "B", "label": f"B: {alg_b.NAME}", "prepare": lambda inp: alg_b.prepare(inp["data"]),
             "run": _run_binary, "count": _count_binary, "mutates": False, "complexity": alg_b.COMPLEXITY},
        ],
        "verify": verify_search,
        "answer": search_answer,
    }


# ------------------------------------------------------------
# 汎用の比較
# ------------------------------------------------------------
def _copy_input(inp):
    return {k: (list(v) if isinstance(v, list) else v) for k, v in inp.items()}


def run_comparison(task, sizes=DEFAULT_SIZES, repeat=5, warmup=1, seed=0, number="auto", progress=None):
    """task を各入力サイズで実行し、行（辞書）のリストを返す

    ・同じサイズでは、すべてのアルゴリズムに同じ入力（同じシードで作ったもの）を使う。
    ・アルゴリズムが入力を変更する（mutates=True）なら、測定ごとに入力をコピーする。
      コピーの時間は run_s に含めない（setup として別に測る）。
    ・時間はすべて秒。run_s・prep_s は repeat 回の中央値。
    ・number="auto" なら、短い処理は 1 回の測定の中で何回も呼び出し、1 回あたりの時間に直す。
    """
    rows = []
    for n in sizes:
        inp, gen_s = timed(task["make_input"], n, seed)
        answers = {}
        for alg in task["algorithms"]:
            prepare = alg.get("prepare")
            if prepare is not None:
                pm = measure(prepare, setup=lambda: (_copy_input(inp),), repeat=repeat, warmup=warmup)
                prepared = prepare(_copy_input(inp))
                prep_s = pm["median"]
            else:
                prepared, prep_s = None, 0.0
            first = alg["run"](prepared, _copy_input(inp) if alg.get("mutates") else inp)
            correct, verify_s = timed(task["verify"], inp, prepared, first)
            if alg.get("mutates"):
                m = measure(alg["run"], repeat=repeat, warmup=warmup, setup=lambda: (prepared, _copy_input(inp)))
            else:
                m = measure(alg["run"], args=(prepared, inp), repeat=repeat, warmup=warmup, number=number)
            count = alg["count"](prepared, inp) if alg.get("count") else None
            answers[alg["key"]] = task["answer"](inp, prepared, first)
            rows.append({"task": task["name"], "n": n, "algorithm": alg["key"], "label": alg["label"],
                         "gen_s": gen_s, "prep_s": prep_s, "run_s": m["median"], "run_min_s": m["min"],
                         "run_max_s": m["max"], "total_s": prep_s + m["median"], "verify_s": verify_s,
                         "correct": bool(correct), "operations": count, "repeat": repeat, "number": m["number"],
                         "times": m["times"]})
            if progress:
                progress(rows[-1])
        base = answers[task["algorithms"][0]["key"]]
        for r in rows:
            if r["n"] == n:
                r["consistent"] = answers[r["algorithm"]] == base
    return rows


TABLE_COLUMNS = [("n", "N", "{}"), ("label", "Algorithm", "{}"), ("correct", "Correct", "{}"),
                 ("consistent", "Same answer", "{}"), ("prep_s", "Prep (ms)", "{:.3f}"),
                 ("run_s", "Run median (ms)", "{:.3f}"), ("total_s", "Prep+Run (ms)", "{:.3f}"),
                 ("operations", "Comparisons", "{}")]


def format_table(rows, columns=TABLE_COLUMNS):
    """文字の表。時間の列（_s）はミリ秒で表示する"""
    def cell(r, key, fmt):
        v = r.get(key)
        if v is None:
            return "-"
        if key.endswith("_s"):
            v = v * 1e3
        return fmt.format(v)
    cells = [[cell(r, k, f) for k, _h, f in columns] for r in rows]
    heads = [h for _k, h, _f in columns]
    widths = [max([len(h)] + [len(c[i]) for c in cells]) for i, h in enumerate(heads)]
    out = ["  ".join(h.rjust(w) if i != 1 else h.ljust(w) for i, (h, w) in enumerate(zip(heads, widths)))]
    for c in cells:
        out.append("  ".join(v.rjust(w) if i != 1 else v.ljust(w) for i, (v, w) in enumerate(zip(c, widths))))
    return "\n".join(out)


def save_csv(rows, path):
    """結果を CSV に保存する（times 列は除く）。保存した CSV は実測値なので、実行環境とあわせて記録する"""
    keys = [k for k in rows[0] if k != "times"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in keys})
    return str(path)


def environment():
    """実行環境（実験記録に書く）"""
    import platform
    return {"python": platform.python_version(), "implementation": platform.python_implementation(),
            "system": platform.system(), "machine": platform.machine(), "processor": platform.processor() or "-"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="F5：Algorithm A と B を入力サイズごとに比較する")
    ap.add_argument("--sizes", type=int, nargs="+", default=list(DEFAULT_SIZES))
    ap.add_argument("--repeat", type=int, default=5)
    ap.add_argument("--warmup", type=int, default=1)
    ap.add_argument("--queries", type=int, default=100)
    ap.add_argument("--hit-ratio", type=float, default=0.5)
    ap.add_argument("--order", default="random", choices=["random", "sorted", "reversed"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--csv", default=None, help="結果を CSV に保存するパス（任意）")
    a = ap.parse_args(argv)
    task = make_search_task(a.queries, a.hit_ratio, a.order)
    print("課題:", task["description"])
    print("実行環境:", environment())
    print(f"測定: repeat={a.repeat}（中央値）, warmup={a.warmup}, seed={a.seed}。Run は探索 {a.queries} 回分の時間\n")
    rows = run_comparison(task, a.sizes, a.repeat, a.warmup, a.seed)
    print(format_table(rows))
    if not all(r["correct"] and r["consistent"] for r in rows):
        print("\n⚠️ 正しくない結果があります。性能を比べる前に原因を調べてください。")
    if a.csv:
        print("\nCSV:", save_csv(rows, a.csv))


if __name__ == "__main__":
    main()
