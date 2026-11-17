# E2：教科書の探索・ソートアルゴリズムと、計算量・実測時間の関係
#
# 教科書（柴田望洋『新・明解 Pythonで学ぶアルゴリズムとデータ構造 第2版』）のコードを textbook/ から直接 import する。
#   線形探索  textbook/ssearch_while.py  seq_search       O(n)
#   二分探索  textbook/bsearch.py        bin_search       O(log n)  ※ソート済みのデータが前提
#   バブルソート textbook/bubble_sort1.py  bubble_sort    O(n^2)（この版は最良の場合も O(n^2)）
#   挿入ソート   textbook/insertion_sort.py insertion_sort O(n^2)（ソート済みの入力では O(n)）
#   マージソート textbook/merge_sort.py   merge_sort      O(n log n)
#   Python 組み込みの sorted()（Timsort）               O(n log n)（ソート済みに近い入力では O(n) に近い）
#   NumPy の np.sort()（既定はクイックソート系）          O(n log n)
#
# ■ 注意
#   探索・ソートは「前の比較の結果で次に何をするかが決まる」逐次的なアルゴリズムで、
#   行列積のように GPU・TPU で単純に並列化できる計算ではない。この教材では GPU・TPU へは移植しない。

import math
import random

import numpy as np

from textbook.bsearch import bin_search
from textbook.bubble_sort1 import bubble_sort
from textbook.insertion_sort import insertion_sort
from textbook.merge_sort import merge_sort
from textbook.ssearch_while import seq_search

from benchmark_utils import measure

# O(n^2) のソートの安全上限（Python で n = 5,000 のバブルソートは数秒〜十数秒かかる）
QUADRATIC_MAX_N = 3_000
MERGE_SORT_MAX_N = 200_000


# ------------------------------------------------------------
# 探索
# ------------------------------------------------------------
linear_search = seq_search   # 教科書の関数をそのまま使う（-1 は「見つからない」）


def binary_search(a, key):
    """教科書の bin_search で二分探索する（見つからなければ -1）

    【前提条件】a は昇順にソートされていること（この関数は確認しない。確認すると O(n) かかるため）。
    教科書の bin_search は空のシーケンスで a[-1] を参照して IndexError になるので、空の場合だけ先に -1 を返す。
    同じ値が複数あるとき、返す添字は「そのうちのどれか 1 つ」（最初のものとは限らない）。
    """
    if len(a) == 0:
        return -1
    return bin_search(a, key)


def is_sorted(a):
    """昇順に並んでいるか（O(n)）"""
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


# ------------------------------------------------------------
# ソート（教科書の関数は「その場で」並べ替えて None を返す。ここでは新しいリストを返す形にそろえる）
# ------------------------------------------------------------
def _sorted_copy(sort_func):
    def run(a):
        b = list(a)
        sort_func(b)
        return b
    run.__name__ = sort_func.__name__
    return run


SORTS = {
    "bubble_sort": _sorted_copy(bubble_sort),
    "insertion_sort": _sorted_copy(insertion_sort),
    "merge_sort": _sorted_copy(merge_sort),
    "sorted": sorted,
    "np.sort": np.sort,
}
COMPLEXITY = {"bubble_sort": "n^2", "insertion_sort": "n^2", "merge_sort": "n log n",
              "sorted": "n log n", "np.sort": "n log n", "linear_search": "n", "binary_search": "log n"}


def complexity_value(name, n):
    """理論計算量の式 f(n) の値（定数倍は無視）"""
    expr = COMPLEXITY[name]
    n = max(n, 2)
    return {"n": n, "log n": math.log2(n), "n log n": n * math.log2(n), "n^2": n * n}[expr]


# ------------------------------------------------------------
# 入力データ
# ------------------------------------------------------------
def make_data(n, order="random", seed=0):
    """長さ n の整数リスト

    order : "random"（ランダム）、"sorted"（昇順）、"reversed"（降順）、"few_unique"（重複が多い）
    """
    rng = random.Random(seed)
    if order == "few_unique":
        return [rng.randrange(10) for _ in range(n)]
    data = [rng.randrange(10 * n + 1) for _ in range(n)]
    if order == "sorted":
        data.sort()
    elif order == "reversed":
        data.sort(reverse=True)
    elif order != "random":
        raise ValueError(f"不明な order：{order}")
    return data


# ------------------------------------------------------------
# Experiment A：線形探索と二分探索
# ------------------------------------------------------------
def search_experiment(n, queries=100, repeats=5, seed=0):
    """線形探索と二分探索を比べる（見つかるキーと見つからないキーを半分ずつ）

    binary_search_s            : ソート済みのデータに対する探索時間だけ
    binary_with_sort_s         : 探索の前に sorted() でソートする時間を含めた場合（データが毎回変わる状況）
    sort_once_then_binary_s    : 1 回だけソートして、queries 回探索する場合の合計
    """
    rng = random.Random(seed)
    data = make_data(n, "random", seed)
    sorted_data = sorted(data)
    present = [rng.choice(data) for _ in range(queries // 2)] if n > 0 else []
    absent = [-1 - k for k in range(queries - len(present))]   # データは 0 以上なので必ず見つからない
    keys = present + absent

    # 正しさの確認
    for k in keys:
        i, j = linear_search(data, k), binary_search(sorted_data, k)
        assert (i == -1) == (j == -1)
        assert i == -1 or (data[i] == k and sorted_data[j] == k)

    lin = measure(lambda: [linear_search(data, k) for k in keys], repeats, 1)["median"]
    bina = measure(lambda: [binary_search(sorted_data, k) for k in keys], repeats, 1)["median"]
    sort_t = measure(lambda: sorted(data), repeats, 1)["median"]
    return {
        "n": n, "queries": queries, "repeats": repeats, "seed": seed,
        "linear_search_s": lin / queries,
        "binary_search_s": bina / queries,
        "binary_with_sort_s": (bina / queries) + sort_t,
        "sort_once_then_binary_s": sort_t + bina,
        "linear_total_s": lin,
    }


# ------------------------------------------------------------
# Experiment B：ソート
# ------------------------------------------------------------
def sort_experiment(n, order="random", names=None, repeats=3, seed=0):
    """ソートアルゴリズムの時間を比べる（安全上限を超えるものは実行せず None）"""
    names = names or list(SORTS)
    data = make_data(n, order, seed)
    expected = sorted(data)
    rows = []
    for name in names:
        row = {"algorithm": name, "complexity": COMPLEXITY[name], "n": n, "order": order,
               "repeats": repeats, "seed": seed, "time_s": None}
        if name in ("bubble_sort", "insertion_sort") and n > QUADRATIC_MAX_N:
            row["note"] = f"n > {QUADRATIC_MAX_N}（O(n^2) の安全上限）なので実行しない"
        elif name == "merge_sort" and n > MERGE_SORT_MAX_N:
            row["note"] = f"n > {MERGE_SORT_MAX_N} なので実行しない"
        else:
            func = SORTS[name]
            if name == "np.sort":
                arr = np.asarray(data)   # list → 配列の変換は計算時間に含めない
                assert np.sort(arr).tolist() == expected
                row["time_s"] = measure(lambda: np.sort(arr), repeats, 1)["median"]
            else:
                assert list(func(data)) == expected
                # 入力は書き換えない（_sorted_copy がコピーを作る）。コピーの O(n) は O(n^2) に比べ小さい
                row["time_s"] = measure(lambda: func(data), repeats, 1)["median"]
        rows.append(row)
    return rows


# ------------------------------------------------------------
# Experiment C：データサイズと計算量
# ------------------------------------------------------------
def complexity_table(rows, name_key="algorithm", time_key="time_s"):
    """時間 / f(n) を計算する。理論どおりなら、n を変えてもほぼ一定になるはず"""
    out = []
    for r in rows:
        if r.get(time_key) is None:
            continue
        name = r[name_key]
        f = complexity_value(name, r["n"])
        out.append({**r, "f(n)": f, "time_per_f": r[time_key] / f})
    return out


if __name__ == "__main__":
    from benchmark_utils import format_table
    print("=== Experiment A：線形探索 O(n) と二分探索 O(log n)（1 回の探索あたり）===")
    rows = [search_experiment(n) for n in [100, 1_000, 10_000, 100_000]]
    print(format_table(rows, [("n", "n"), ("linear_search_s", "linear"), ("binary_search_s", "binary"),
                              ("binary_with_sort_s", "sort+binary")]))
    print()
    print("=== Experiment B：ソート（ランダムな入力）===")
    rows = []
    for n in [100, 1_000, 3_000]:
        rows += sort_experiment(n)
    print(format_table(rows, [("algorithm", "algorithm"), ("complexity", "O()"), ("n", "n"), ("time_s", "time")]))
    print()
    print("=== Experiment C：時間 / f(n)（理論どおりなら n によらずほぼ一定）===")
    print(format_table(complexity_table(rows), [("algorithm", "algorithm"), ("n", "n"), ("time_per_f", "time / f(n)")]))

# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：入力の並び（"sorted"・"reversed"・"few_unique"）を変えて、最良・平均・最悪の場合を比べる。
# TODO 2：探索するキーの位置（先頭・末尾・存在しない）で、線形探索の時間がどう変わるか調べる。
# TODO 3：教科書の selection_sort・quick_sort・heap_sort なども比べる（textbook/ にコピーする場合は SHA-256 を確認）。
# TODO 4：「1 回ソートして何回も探索する」場合、何回以上探索するなら二分探索の方が得か計算する。
# TODO 5：bisect モジュール（Python 標準の二分探索）や np.searchsorted と比べる。
