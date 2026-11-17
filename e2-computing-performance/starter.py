# E2：CPU・GPU・TPU による計算性能とアルゴリズムの関係 ―― 一連のデモ（CPU のみ、数十秒以内）
#
# 1. Python の for ループ（Task A〜D）と結果の確認
# 2. NumPy のベクトル演算と、Python ループとの結果の一致・実行時間・高速化率
# 3. 線形探索と二分探索
# 4. ソート（O(n^2) と O(n log n)）
# 5. PyTorch（インストールされていれば CPU、GPU があれば GPU も）の行列積
# 6. 学生向け TODO
#
# GPU・TPU の本格的な比較は notebooks/02・03 を Google Colab で実行する。

import platform

import numpy as np

import cpu_basics
from algorithm_benchmark import binary_search, linear_search, search_experiment, sort_experiment, complexity_table
from benchmark_utils import format_table, measure
from numpy_benchmark import compare

SEED = 0

print("E2: CPU / GPU / TPU と計算性能・アルゴリズム")
print(f"Python {platform.python_version()} / NumPy {np.__version__} / {platform.platform()}")
print("（時間は環境・実行ごとに変わります。中央値を表示しています）")
print()

# ------------------------------------------------------------
print("=== 1. Python の for ループ（cpu_basics.py）===")
a, b, c = [1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [0.5, 0.5, 0.5]
print(f"Task A elementwise a*b+c : {cpu_basics.elementwise(a, b, c)}")
print(f"Task B total([1..10])    : {cpu_basics.total(list(range(1, 11)))}")
print(f"Task C matmul            : {cpu_basics.matmul([[1, 2], [3, 4]], [[5, 6], [7, 8]])}")
print(f"Task D conditional       : {cpu_basics.conditional_square([-2.0, -0.5, 0.0, 1.5, 3.0])}")
print()

# ------------------------------------------------------------
print("=== 2. Python ループ vs NumPy（numpy_benchmark.py、float64、seed = 0）===")
rows = []
for task, sizes in [("elementwise", [100, 10_000, 100_000]), ("total", [100, 10_000, 100_000]),
                    ("conditional", [100, 10_000, 100_000]), ("matmul", [10, 50, 100])]:
    for n in sizes:
        rows.append(compare(task, n, repeats=5, seed=SEED))
print(format_table(rows, [("task", "task"), ("n", "n"), ("python_s", "Python"), ("numpy_s", "NumPy"),
                          ("speedup", "speedup"), ("match", "match")]))
assert all(r["match"] for r in rows), "Python と NumPy の結果が一致しません"
print("speedup = Python の時間 / NumPy の時間。matmul の n は n×n 行列。すべて np.allclose で結果が一致。")
print()

# ------------------------------------------------------------
print("=== 3. 線形探索 O(n) と二分探索 O(log n)（教科書のコード、1 回の探索あたり）===")
data = [7, 3, 9, 1, 5]
print(f"linear_search({data}, 9) = {linear_search(data, 9)}")
print(f"binary_search({sorted(data)}, 9) = {binary_search(sorted(data), 9)}   ← 二分探索はソート済みが前提")
rows = [search_experiment(n, queries=50, repeats=3) for n in [100, 1_000, 10_000]]
print(format_table(rows, [("n", "n"), ("linear_search_s", "linear"), ("binary_search_s", "binary"),
                          ("binary_with_sort_s", "sort+binary")]))
print()

# ------------------------------------------------------------
print("=== 4. ソート（ランダムな整数）===")
rows = []
for n in [100, 1_000]:
    rows += sort_experiment(n, repeats=3)
print(format_table(rows, [("algorithm", "algorithm"), ("complexity", "O()"), ("n", "n"), ("time_s", "time")]))
print("時間 / f(n)（理論どおりなら n によらずほぼ一定）:")
print(format_table(complexity_table(rows), [("algorithm", "algorithm"), ("n", "n"), ("time_per_f", "time / f(n)")]))
print()

# ------------------------------------------------------------
print("=== 5. PyTorch の行列積（インストールされている場合のみ）===")
try:
    import torch
except ImportError:
    torch = None
    print("PyTorch がインストールされていないので、スキップします（Colab には標準で入っています）。")
if torch is not None:
    n = 256
    A = np.random.default_rng(SEED).standard_normal((n, n)).astype(np.float32)
    B = np.random.default_rng(SEED + 1).standard_normal((n, n)).astype(np.float32)
    ref = A @ B
    devices = ["cpu"] + (["cuda"] if torch.cuda.is_available() else [])
    for dev in devices:
        tA, tB = torch.as_tensor(A, device=dev), torch.as_tensor(B, device=dev)
        sync = (lambda _r: torch.cuda.synchronize()) if dev == "cuda" else None
        t = measure(lambda: tA @ tB, repeats=10, warmup=3, sync=sync)
        ok = np.allclose((tA @ tB).cpu().numpy(), ref, rtol=1e-3, atol=1e-3)
        print(f"torch {dev:4}: {n}x{n} matmul median {t['median'] * 1e3:.3f} ms  (matches NumPy: {ok})")
    if not torch.cuda.is_available():
        print("GPU（CUDA）は使えないので、GPU の測定はしていません。")
print()

# ------------------------------------------------------------
print("Student Research TODOs:")
for todo in [
    "1. notebooks/01 で、データサイズ・dtype を変えて Python と NumPy の speedup を比べる",
    "2. notebooks/02 を Colab の GPU ランタイムで実行し、GPU が有利になる行列サイズを探す",
    "3. notebooks/04 で、入力の並び（ソート済み・逆順）による最良・最悪の場合を調べる",
    "4. 理論計算量（O(n), O(log n), O(n^2), O(n log n)）と実測時間の関係を表・グラフにまとめる",
    "5. （Advanced）notebooks/03 を TPU ランタイムで実行し、同じ JAX 関数で CPU と TPU を比べる",
]:
    print(f"  {todo}")
