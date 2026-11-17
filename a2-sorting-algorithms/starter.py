# A2：基本的なソートアルゴリズムの性能比較 — starter code
#
# 教科書の3つのソート関数に、同じデータを与えて結果を比較する。
#   bubble_sort    : バブルソート（単純交換ソート）
#   selection_sort : 選択ソート（単純選択ソート）
#   insertion_sort : 挿入ソート（単純挿入ソート）
#
# 注意：どの関数も、渡されたリストそのものを書き換えて昇順に並べる（in-place）。
#       戻り値は None なので、ソート後のリストを見て結果を確認する。
#       元の data を書き換えないように、毎回 data.copy() で作ったコピーを渡す。

from textbook.bubble_sort1 import bubble_sort
from textbook.selection_sort import selection_sort
from textbook.insertion_sort import insertion_sort

data = [8, 3, 5, 1, 9, 2, 7]

algorithms = [
    ("Bubble Sort", bubble_sort),
    ("Selection Sort", selection_sort),
    ("Insertion Sort", insertion_sort),
]

print("Original:", data)

all_correct = True
for name, sort_function in algorithms:
    values = data.copy()        # 元データのコピーを渡す
    sort_function(values)       # values が書き換えられる（戻り値は使わない）
    print(f"{name}: {values}")

    # sorted() は正解の確認だけに使う（比較対象のアルゴリズムではない）
    if values != sorted(data):
        all_correct = False

print()
print("All results match sorted(data):", all_correct)
print("Original data unchanged:", data == [8, 3, 5, 1, 9, 2, 7])


# ------------------------------------------------------------
# 学生が取り組む追加課題（ここから先は各チームで実装する）
# ------------------------------------------------------------
# TODO 1：データ数 N を 100、500、1,000、2,000 などに変更し、処理時間を比較する。
#         （O(n²) のアルゴリズムなので、最初は小さい N から試すこと）
#
# TODO 2：ランダム順、昇順、降順のデータを用いて比較する。
#         （ヒント：random.shuffle()、list(range(N))、list(range(N, 0, -1))）
#
# TODO 3：重複値を含むデータでも比較する。
#         （ヒント：random.randint() で狭い範囲の値を作る）
#
# TODO 4：time.perf_counter() を用いて実行時間を測定する。
#         （データ生成・コピー・表示の時間は含めない）
#
# TODO 5：複数回測定し、平均値や中央値を比較する。
#         （ヒント：statistics モジュール）
#
# TODO 6：N と実行時間の関係を表・グラフにまとめる。
#
# TODO 7：比較回数、交換回数、要素移動回数を調べる。
#         （教科書コードは編集せず、自分たちのファイルで数える仕組みを作る）
#
# TODO 8：最良・平均・最悪の場合の計算量を考察する。
#
# TODO 9：（発展）Python 標準の sorted() との性能差を調べる。
