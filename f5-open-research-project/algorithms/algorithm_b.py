# Algorithm B（初期デモ）：二分探索（Binary Search）
#
# ■ 解く問題（Algorithm A と共通）
#   入力：ソート済み（昇順）のデータ列 a と、探す値 key
#   出力：a の中で key と等しい要素のうち「最初に現れる位置」（添字）。見つからなければ -1
#
# ■ 前提条件
#   a が昇順にソートされていること。ソートされていない入力では、正しい結果になる保証がない。
#   → ソートは「前処理」。前処理の時間（prepare）を含める比較と、含めない比較を区別する。
#
# ■ 仕組み
#   探索範囲 [lo, hi) の中央の要素と key を比べ、範囲を半分に絞り込む。
#   教科書 第3章「2 分探索」（chap03/bsearch.py の bin_search）の考え方を、
#   「同じ値が複数あるときは最初の位置を返す」ように変えたもの（下限探索、lower bound）。
#   教科書の版は、見つかった時点で終了する（最良 O(1)）が、同じ値が複数あるとどの位置を返すかは決まらない。
#   この版は常に範囲が 1 つになるまで絞り込むので、最良でも O(log N)。
#
# ■ 計算量（N = a の要素数）
#   最良 O(log N)／平均 O(log N)／最悪 O(log N)／追加の空間 O(1)
#   前処理（ソート）：O(N log N)。データが変わらず、何回も探索するなら、ソートは 1 回でよい。
#
# TODO（研究テーマを変えたら）：このファイルを、チームが比較するアルゴリズム B に置き換える。

from collections.abc import Sequence

NAME = "Binary search"
PROBLEM = "ソート済みデータ列 a から key と等しい要素の最初の位置を求める（なければ -1）"
PRECONDITION = "a が昇順にソートされていること"
COMPLEXITY = {"N": "データ列の要素数", "best": "O(log N)", "average": "O(log N)", "worst": "O(log N)",
              "space": "O(1)", "preprocess": "ソート O(N log N)"}


def _check_sequence(a):
    if isinstance(a, (str, bytes)) or not isinstance(a, Sequence):
        raise TypeError(f"データ列は list または tuple にしてください（{type(a).__name__}）")


def is_sorted(a):
    """a が昇順か（O(N)）"""
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


def prepare(a):
    """前処理：昇順にソートした新しいリストを返す（元の a は変えない）

    ソートは比較対象ではない前処理なので、Python の sorted()（O(N log N)）を使う。
    TODO：教科書のソート（chap06）を使う版に変え、前処理の時間がどう変わるか調べる。
    """
    _check_sequence(a)
    return sorted(a)


def binary_search(a, key, check_sorted=False):
    """ソート済みの a の中で key と等しい最初の要素の添字。見つからなければ -1

    check_sorted=True なら、最初にソート済みかを確かめる（O(N) かかるので、時間の測定では False にする）。
    """
    _check_sequence(a)
    if check_sorted and not is_sorted(a):
        raise ValueError("二分探索の入力はソート済み（昇順）にしてください")
    lo, hi = 0, len(a)          # 探索範囲は a[lo] 〜 a[hi - 1]
    while lo < hi:
        mid = (lo + hi) // 2    # 中央の添字
        if a[mid] < key:
            lo = mid + 1        # 後半に絞り込む
        else:
            hi = mid            # 前半（mid を含む）に絞り込む
    if lo < len(a) and a[lo] == key:
        return lo               # 探索成功（最初の位置）
    return -1                   # 探索失敗


def binary_search_count(a, key):
    """二分探索と同じ結果と、key との比較回数を返す：(添字, 比較回数)"""
    _check_sequence(a)
    count = 0
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        count += 1
        if a[mid] < key:
            lo = mid + 1
        else:
            hi = mid
    if lo < len(a):
        count += 1
        if a[lo] == key:
            return lo, count
    return -1, count


# TODO 1：教科書の bin_search（見つかったら終了する版）と比較回数を比べる。
# TODO 2：再帰で書いた二分探索を作り、ループ版と比べる（README「10. 再帰アルゴリズム」）。
