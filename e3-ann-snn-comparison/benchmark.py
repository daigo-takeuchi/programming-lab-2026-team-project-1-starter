# E3：ANN と LUT の演算量・処理時間・メモリの比較 ―― 実験の入口
#
# ここにあるのは「1つの設定で、ANN と LUT の forward を複数回測って中央値を出す例」と、
# 「LUT の行を index で直接読む方法と、線形探索で探す方法の比較例」だけ。
# 設定を変えた実験・表やグラフへのまとめは学生が行う（下の TODO）。
#
# ■ 注意
#   ・Python の for ループで書いた ANN と、Python のリストで書いた LUT の処理時間は、
#     実装方法（NumPy を使うか、など）に強く依存する。
#     この測定だけから「SNN の方がハードウェア上で速い・省電力だ」とは結論できない。
#   ・ANN と LUT は計算の意味が違う。出力次元が同じでも、同じ性能のモデルとはいえない。
#   ・処理時間は毎回ぶれるので、複数回測って中央値（median）を使う。
#   ・tracemalloc で測れるのは Python オブジェクトのメモリ（list・float の管理領域を含む）であり、
#     値の数 × 4 バイト（float32）のような理論値とは一致しない。

import random
import statistics
import time
import tracemalloc

from textbook.ssearch_while import seq_search

from ann import ann_operation_counts, dense_forward
from spike_lut import bits_to_index, compare_pairs, lut_forward, lut_operation_counts, make_random_tables


def median_time(func, repeats=200):
    """func() を repeats 回実行し、1回あたりの時間（秒）の中央値を返す"""
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        func()
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def make_ann(n, m, seed):
    rng = random.Random(seed)
    W = [[rng.uniform(-1, 1) for _ in range(n)] for _ in range(m)]
    b = [rng.uniform(-1, 1) for _ in range(m)]
    return W, b


def traced_memory(build):
    """build() で作ったオブジェクトが使う Python のメモリ（バイト、tracemalloc の測定値）"""
    tracemalloc.start()
    obj = build()
    current, _peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del obj
    return current


def compare_ann_and_lut(n, nt, nc, seed=0, repeats=200):
    """入力 n・出力 m = n の ANN と、nt 個・各 nc 比較・出力 m = n の LUT を比べる"""
    m = n
    rng = random.Random(seed)
    x = [rng.random() for _ in range(n)]
    W, b = make_ann(n, m, seed)
    tables = make_random_tables(n, nt, nc, m, seed=seed)

    ann_ops = ann_operation_counts(n, m)
    lut_ops = lut_operation_counts(nt, nc, m)
    ann_time = median_time(lambda: dense_forward(x, W, b), repeats)
    lut_time = median_time(lambda: lut_forward(x, tables), repeats)
    ann_mem = traced_memory(lambda: make_ann(n, m, seed))
    lut_mem = traced_memory(lambda: make_random_tables(n, nt, nc, m, seed=seed))

    print(f"ANN: n = {n}, m = {m}     LUT: nt = {nt}, nc = {nc}, m = {m}（seed = {seed}、各 {repeats} 回測定の中央値）")
    print(f"{'':26}{'ANN':>14}{'LUT':>14}")
    rows = [
        ("multiplications", ann_ops["multiplications"], lut_ops["multiplications"]),
        ("additions", ann_ops["additions"], lut_ops["additions"]),
        ("comparisons", ann_ops["comparisons"], lut_ops["comparisons"]),
        ("LUT row accesses", 0, lut_ops["lut_accesses"]),
        ("parameters (stored)", ann_ops["parameters"], lut_ops["parameters"]),
        ("values read / forward", ann_ops["values_read"], lut_ops["values_read"]),
        ("Python memory [bytes]", ann_mem, lut_mem),
    ]
    for label, a, l in rows:
        print(f"{label:26}{a:>14,}{l:>14,}")
    print(f"{'forward time [µs]':26}{ann_time * 1e6:>14.2f}{lut_time * 1e6:>14.2f}")


def compare_direct_index_and_linear_search(nc, seed=0, repeats=200):
    """LUT の行を「index で直接読む」方法と、「ビット列のキーを線形探索で探す」方法の比較

    線形探索には教科書 第3章の seq_search を使う。行数 2^nc に比例して遅くなる。
    """
    rng = random.Random(seed)
    n = 8
    anchors = [tuple(rng.sample(range(n), 2)) for _ in range(nc)]
    rows = [[float(j)] for j in range(2 ** nc)]
    keys = [tuple((j >> (nc - 1 - r)) & 1 for r in range(nc)) for j in range(2 ** nc)]   # 行 j のビット列
    x = [rng.random() for _ in range(n)]

    def direct():
        return rows[bits_to_index(compare_pairs(x, anchors))]

    def linear():
        return rows[seq_search(keys, tuple(compare_pairs(x, anchors)))]

    assert direct() == linear()
    t_direct = median_time(direct, repeats)
    t_linear = median_time(linear, repeats)
    print(f"nc = {nc:2d}（{2 ** nc:5d} 行）: index で直接読む {t_direct * 1e6:8.2f} µs   "
          f"線形探索で探す {t_linear * 1e6:8.2f} µs")


if __name__ == "__main__":
    print("=== ANN と LUT の比較（1つの設定の例）===")
    compare_ann_and_lut(n=32, nt=8, nc=6)
    print()
    print("=== LUT の行の読み出し：index で直接 vs 線形探索 ===")
    for nc in [4, 8, 12]:
        compare_direct_index_and_linear_search(nc)
    print()
    print("※ 処理時間は Python の実装での測定値です。ハードウェア上の速度や消費電力を示すものではありません。")

# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：入力次元 n を変更する（8, 16, 32, 64, …）。
# TODO 2：ANN の出力次元 m を変更する（compare_ann_and_lut は m = n。m を別に指定できるようにする）。
# TODO 3：LUT 数 nt を変更する。
# TODO 4：anchor pair 数 nc を変更する（保存容量 nt × 2^nc × m の増え方に注意）。
# TODO 5：ANN の forward 計算時間を測定する（repeats を変え、中央値と四分位範囲を記録する）。
# TODO 6：LUT の forward 計算時間を測定する。
# TODO 7：乗算回数を比較する。
# TODO 8：比較回数を比較する。
# TODO 9：LUT 参照回数を比較する。
# TODO 10：パラメータ数を比較する（保存している値の数と、1回の forward で読み出す値の数を分けて考える）。
# TODO 11：メモリ使用量を比較する（tracemalloc の測定値と、値の数から計算した理論値）。
# TODO 12：結果を表・グラフにまとめる（横軸 n や nc、縦軸 時間・演算回数・容量）。
