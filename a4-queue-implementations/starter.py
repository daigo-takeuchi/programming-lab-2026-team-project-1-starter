# A4：キューの実装方式と処理性能の比較 — starter code
#
# 教科書の2つのキュークラスを、同じ操作列で動かして比較する。
#   FixedQueue : Pythonのリストをリングバッファとして使うキュー
#   Queue      : collections.deque を使うキュー
#
# 注意：満杯のときの動作は2つのクラスで異なる。
#   FixedQueue.enque は例外 FixedQueue.Full を送出する。
#   Queue.enque は例外を出さず、先頭の（いちばん古い）データを捨ててしまう。
# そこで、enque の前に必ず is_full() で確認するルールに統一する。

from textbook.fixed_queue import FixedQueue
from textbook.queue import Queue

queues = [
    ("Array (Ring Buffer)", FixedQueue(3)),
    ("Deque", Queue(3)),
]

for name, queue in queues:
    print(name)

    # 1〜4：10, 20, 30 を追加し、40 を試みる（容量3なので40は拒否される）
    for value in [10, 20, 30, 40]:
        if queue.is_full():
            print("Full: cannot enqueue", value)
        else:
            queue.enque(value)

    # 5：1つ取り出す（最初に入れた10が出てくる＝FIFO）
    if not queue.is_empty():
        print("Dequeued:", queue.deque())

    # 6：空きができたので40を追加する
    #    リングバッファ版では、rear が配列の末尾から先頭（添字0）へ戻って格納される
    value = 40
    if queue.is_full():
        print("Full: cannot enqueue", value)
    else:
        queue.enque(value)
        print("Enqueued:", value)

    # 7：空になるまで取り出す
    while not queue.is_empty():
        print("Dequeued:", queue.deque())

    print()


# ------------------------------------------------------------
# 学生が取り組む追加課題（ここから先は各チームで実装する）
# ------------------------------------------------------------
# TODO 1：容量を 1、3、10 などに変更し、動作を比較する。
#         （満杯判定・空判定の境界で、両実装が同じ結果になるか？）
#
# TODO 2：enqueue と dequeue の回数を増やし、処理時間を測定する。
#         （ヒント：time.perf_counter() や timeit モジュール）
#
# TODO 3：データ数 N（例：1,000 / 10,000 / 100,000 ...）と実行時間の関係を調べる。
#         （表やグラフにまとめる）
#
# TODO 4：メモリ使用量を比較する。
#         （ヒント：tracemalloc モジュール、sys.getsizeof()）
#
# TODO 5：リングバッファの front / rear の変化を観察する。
#         （ヒント：FixedQueue の front, rear, no 属性を操作のたびに表示してみる）
#
# TODO 6：配列版と deque 版の違いを、Big-O（理論）と実測結果の両面から考察する。
