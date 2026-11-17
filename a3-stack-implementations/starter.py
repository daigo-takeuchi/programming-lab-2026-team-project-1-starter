# A3：スタックの実装方式と処理性能の比較 — starter code
#
# 教科書の2つのスタッククラスを、同じ操作列で動かして比較する。
#   FixedStack : Pythonのリストを固定長の配列として使うスタック
#   Stack      : collections.deque を使うスタック
#
# 注意：満杯のときの動作は2つのクラスで異なる。
#   FixedStack.push は例外 FixedStack.Full を送出する。
#   Stack.push は例外を出さず、いちばん古い（底の）データを捨ててしまう。
# そこで、push の前に必ず is_full() で確認するルールに統一する。

from textbook.fixed_stack import FixedStack
from textbook.stack import Stack

stacks = [
    ("Array", FixedStack(3)),
    ("Deque", Stack(3)),
]

values = [10, 20, 30, 40]   # 容量3なので、40は追加できないはず

for name, stack in stacks:
    print(name)

    # push：満杯なら追加しない
    for value in values:
        if stack.is_full():
            print("Full: cannot push", value)
        else:
            stack.push(value)

    # pop：空になるまで取り出す（後に入れたものから出てくる＝LIFO）
    while not stack.is_empty():
        print(stack.pop())

    print()


# ------------------------------------------------------------
# 学生が取り組む追加課題（ここから先は各チームで実装する）
# ------------------------------------------------------------
# TODO 1：容量を 1、3、10 などに変更し、動作を比較する。
#         （満杯判定・空判定の境界で、両実装が同じ結果になるか？）
#
# TODO 2：push と pop の回数を増やし、処理時間を測定する。
#         （ヒント：time.perf_counter() や timeit モジュール）
#
# TODO 3：データ数 N（例：1,000 / 10,000 / 100,000 ...）と実行時間の関係を調べる。
#         （表やグラフにまとめる）
#
# TODO 4：メモリ使用量を比較する。
#         （ヒント：tracemalloc モジュール、sys.getsizeof()）
#
# TODO 5：配列版と deque 版の違いを、Big-O（理論）と実測結果の両面から考察する。
