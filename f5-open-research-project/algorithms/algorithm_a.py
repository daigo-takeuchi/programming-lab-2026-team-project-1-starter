# Algorithm A（初期デモ）：線形探索（Linear Search）
#
# ■ 解く問題（Algorithm B と共通）
#   入力：データ列 a（list または tuple）と、探す値 key
#   出力：a の中で key と等しい要素のうち「最初に現れる位置」（添字）。見つからなければ -1
#
# ■ 前提条件
#   なし。a はソートされていなくてよい（ここが二分探索との違い）。
#
# ■ 仕組み
#   先頭から 1 つずつ key と比べ、等しい要素が見つかった時点で終了する。
#   教科書 第3章「線形探索」（chap03/ssearch_while.py の seq_search）と同じ考え方。
#
# ■ 計算量（N = a の要素数）
#   最良 O(1)（先頭で見つかる）／平均 O(N)／最悪 O(N)（末尾にある、または存在しない）／追加の空間 O(1)
#
# TODO（研究テーマを変えたら）：このファイルを、チームが比較するアルゴリズム A に置き換える。

from collections.abc import Sequence

NAME = "Linear search"
PROBLEM = "データ列 a から key と等しい要素の最初の位置を求める（なければ -1）"
PRECONDITION = "なし（ソートされていなくてよい）"
COMPLEXITY = {"N": "データ列の要素数", "best": "O(1)", "average": "O(N)", "worst": "O(N)", "space": "O(1)",
              "preprocess": "なし"}


def _check_sequence(a):
    if isinstance(a, (str, bytes)) or not isinstance(a, Sequence):
        raise TypeError(f"データ列は list または tuple にしてください（{type(a).__name__}）")


def linear_search(a, key):
    """a の中で key と等しい最初の要素の添字。見つからなければ -1"""
    _check_sequence(a)
    i = 0
    n = len(a)
    while i < n:
        if a[i] == key:
            return i        # 探索成功
        i += 1
    return -1               # 探索失敗


def linear_search_count(a, key):
    """線形探索と同じ結果と、key との比較回数を返す：(添字, 比較回数)

    比較回数は実行環境によらない指標。実行時間の測定には linear_search を使う（数える処理の分だけ遅くなるため）。
    """
    _check_sequence(a)
    count = 0
    for i in range(len(a)):
        count += 1
        if a[i] == key:
            return i, count
    return -1, count


# TODO 1：番兵法（教科書 chap03/ssearch_sentinel.py）で書き直し、比較回数と実行時間を比べる。
# TODO 2：すべての出現位置を返す版を作る（計算量はどうなるか）。
