# C1：線形探索版と辞書版の性能比較 — 学生が実験を作るための入口
#
# ここにあるのは「合成ログの生成」と「1回だけの測定例」だけである。
# N や U を変えた繰り返し測定、グラフ化、メモリ測定は、学生が実装する（下の TODO）。
#
# 実行：python3 benchmark.py

import random
import time

import detection


def make_ip(i):
    """i 番目の架空のIPアドレスを返す（ドキュメント用に予約されたアドレスだけを使う）

    i = 0〜767   : 192.0.2.0/24、198.51.100.0/24、203.0.113.0/24（IPv4）
    i = 768 以上 : 2001:db8::/32（IPv6 のドキュメント用アドレス）
    """
    prefixes = ["192.0.2", "198.51.100", "203.0.113"]
    if i < 768:
        return f"{prefixes[i // 256]}.{i % 256}"
    return f"2001:db8::{i:x}"


def make_records(n, u, error_rate=0.05, seed=0):
    """N 件・異なるIP数 U の合成ログ（辞書のリスト）を作る

    各ログのIPは U 個の中からランダムに選ぶ（U が N より大きいと、実際の異なるIP数は U より少なくなる）。
    集計に使う "ip" と "status" だけを持つ簡略化したレコードである。
    """
    rng = random.Random(seed)
    ips = [make_ip(i) for i in range(u)]
    records = []
    for _ in range(n):
        status = 404 if rng.random() < error_rate else 200
        records.append({"ip": rng.choice(ips), "status": status})
    return records


if __name__ == "__main__":
    N = 2_000
    U = 200

    # ログの生成時間は、集計時間に含めない
    records = make_records(N, U, seed=2026)

    start = time.perf_counter()
    detection.count_linear(records)
    linear_time = time.perf_counter() - start

    start = time.perf_counter()
    detection.count_dict(records)
    dict_time = time.perf_counter() - start

    print(f"N = {N}, U = {U}（1回だけの測定例）")
    print(f"  線形探索版: {linear_time:.6f} 秒")
    print(f"  辞書版    : {dict_time:.6f} 秒")


# ------------------------------------------------------------
# 学生が取り組む課題
# ------------------------------------------------------------
# TODO 1：ログ件数 N を増やす（例：1,000 / 10,000 / 100,000）。
# TODO 2：異なるIPアドレス数 U を増やす（例：10 / 100 / 1,000 / 10,000）。
# TODO 3：線形探索版（detection.count_linear）の処理時間を測定する。
# TODO 4：辞書版（detection.count_dict）の処理時間を測定する。
# TODO 5：複数回測定して、平均値・中央値を比較する（statistics モジュール）。
# TODO 6：N と処理時間の関係をグラフ化する（U は固定する）。
# TODO 7：U と処理時間の関係をグラフ化する（N は固定する）。
# TODO 8：メモリ使用量を比較する（tracemalloc モジュール、sys.getsizeof()）。
# TODO 9：理論計算量（線形探索版 O(N×U)、辞書版 平均 O(N)）と実測結果を比較する。
#
# 測定のコツ：
#   - ログの生成・ファイルの読み込みの時間と、集計処理の時間を分けて測る。
#       start = time.perf_counter()
#       detection.count_linear(records)        # 測りたい処理だけを挟む
#       elapsed = time.perf_counter() - start
#   - 乱数シード（seed）を記録し、同じデータで両方の方法を測る。
#   - 線形探索版は N と U が大きいと非常に遅くなる。最初は小さい値から試す。
