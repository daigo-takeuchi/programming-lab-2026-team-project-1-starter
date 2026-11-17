# E2：NumPy のベクトル演算と、Python の for ループの比較
#
# cpu_basics.py と「同じ数学的計算」を NumPy で書き、結果の一致と実行時間を比べる。
#
#   Task A：y = a * b + c                    （要素ごとの演算をまとめて実行）
#   Task B：np.sum(a)                        （総和）
#   Task C：A @ B（np.matmul）               （行列積。内部で最適化された BLAS ライブラリを使う）
#   Task D：np.where(x > 0, x * x, 0)        （条件分岐を「両方計算して選ぶ」形に書き換える）
#
# ■ なぜ NumPy は速いことが多いのか
#   ・ループが C 言語の中で回る（Python のインタプリタが 1 要素ごとに命令を解釈しない）
#   ・データが連続したメモリに同じ型で並ぶ（list は要素ごとに別々の Python オブジェクト）
#   ・SIMD 命令・BLAS など、CPU の並列機能を使える
# ■ NumPy が必ず速いとは限らない
#   ・要素数が少ないと、NumPy の関数呼び出しや配列の準備の固定コストの方が大きい
#   ・list → 配列の変換にも時間がかかる（この教材では「データ生成」として計算時間と分けて測る）
#   ・np.where は両方の分岐（x * x と 0）を全要素について計算するので、余分な計算をしている
#   ・逐次的な依存関係のある処理（前の結果を使って次を計算する）はベクトル化しにくい
#   ・ベクトル化しても、アルゴリズムの計算量のオーダー（O(n) など）は変わらない

import numpy as np

import cpu_basics
from benchmark_utils import measure

# Python の for ループの安全上限（これより大きい問題では Python ループを実行しない）
PYTHON_MAX_N = {"elementwise": 1_000_000, "total": 1_000_000, "conditional": 1_000_000, "matmul": 200}
# NumPy の安全上限（メモリ不足を避ける）
NUMPY_MAX_N = {"elementwise": 50_000_000, "total": 50_000_000, "conditional": 50_000_000, "matmul": 4096}

TASKS = ["elementwise", "total", "matmul", "conditional"]


# ------------------------------------------------------------
# NumPy 版
# ------------------------------------------------------------
def np_elementwise(a, b, c):
    return a * b + c


def np_total(a):
    return np.sum(a)


def np_matmul(A, B):
    return A @ B


def np_conditional_square(x):
    return np.where(x > 0, x * x, 0).astype(x.dtype, copy=False)


# ------------------------------------------------------------
# データの準備（list と配列の両方を、同じ値で作る）
# ------------------------------------------------------------
def make_inputs(task, n, seed=0, dtype=np.float64):
    """task 用の入力を list 版と NumPy 版の両方で作る

    返り値：(python_args, numpy_args)。NumPy 版は list から変換するので、値は同じ（dtype による丸めを除く）。
    """
    if task in ("elementwise",):
        lists = [cpu_basics.make_vector(n, seed + k) for k in range(3)]
    elif task in ("total", "conditional"):
        lists = [cpu_basics.make_vector(n, seed)]
    elif task == "matmul":
        lists = [cpu_basics.make_matrix(n, n, seed), cpu_basics.make_matrix(n, n, seed + 1)]
    else:
        raise ValueError(f"不明な task：{task}")
    arrays = [np.asarray(v, dtype=dtype) for v in lists]
    return lists, arrays


PY_FUNCS = {"elementwise": cpu_basics.elementwise, "total": cpu_basics.total,
            "matmul": cpu_basics.matmul, "conditional": cpu_basics.conditional_square}
NP_FUNCS = {"elementwise": np_elementwise, "total": np_total,
            "matmul": np_matmul, "conditional": np_conditional_square}


def tolerance(dtype):
    """dtype に応じた許容誤差（float32 は有効数字が約 7 桁なので緩める）"""
    return (1e-4, 1e-5) if np.dtype(dtype) == np.float32 else (1e-9, 1e-12)


def results_match(py_result, np_result, dtype=np.float64, scale=1):
    """Python と NumPy の結果が、丸め誤差の範囲で一致するか（np.allclose）

    総和や行列積は足し合わせる順序が違うため、誤差が要素数 scale に比例して大きくなり得る。
    """
    rtol, atol = tolerance(dtype)
    return bool(np.allclose(np.asarray(py_result, dtype=np.float64), np.asarray(np_result, dtype=np.float64),
                            rtol=rtol, atol=atol * max(1, scale)))


def compare(task, n, repeats=5, warmup=1, seed=0, dtype=np.float64):
    """1 つの task・サイズ n で、Python ループと NumPy を比べた結果の辞書を返す

    安全上限を超える場合、その実装は実行せず None を記録する（推測で値を埋めない）。
    """
    import time
    t0 = time.perf_counter()
    py_args, np_args = make_inputs(task, n, seed, dtype)
    t_data = time.perf_counter() - t0

    row = {"task": task, "n": n, "dtype": np.dtype(dtype).name, "repeats": repeats, "seed": seed,
           "data_gen_s": t_data, "python_s": None, "numpy_s": None, "speedup": None, "match": None}
    if n > NUMPY_MAX_N[task]:
        row["note"] = "NumPy の安全上限を超えたので実行しない"
        return row
    np_res = NP_FUNCS[task](*np_args)
    row["numpy_s"] = measure(lambda: NP_FUNCS[task](*np_args), repeats, warmup)["median"]

    if n <= PYTHON_MAX_N[task]:
        py_res = PY_FUNCS[task](*py_args)
        py_repeats = repeats if (task != "matmul" or n <= 100) else max(1, repeats // 2)
        row["python_s"] = measure(lambda: PY_FUNCS[task](*py_args), py_repeats, min(warmup, 1))["median"]
        row["speedup"] = row["python_s"] / row["numpy_s"] if row["numpy_s"] > 0 else None
        row["match"] = results_match(py_res, np_res, dtype, scale=n)
    else:
        row["note"] = "Python ループの安全上限を超えたので実行しない"
    return row


def run_comparison(sizes=None, matmul_sizes=None, repeats=5, dtype=np.float64):
    """全 task をいくつかのサイズで比べる（結果の辞書のリスト）"""
    sizes = sizes or [100, 1_000, 10_000, 100_000]
    matmul_sizes = matmul_sizes or [10, 50, 100]
    rows = []
    for task in TASKS:
        for n in (matmul_sizes if task == "matmul" else sizes):
            rows.append(compare(task, n, repeats=repeats, dtype=dtype))
    return rows


if __name__ == "__main__":
    from benchmark_utils import format_table
    rows = run_comparison()
    print(format_table(rows, [("task", "task"), ("n", "n"), ("dtype", "dtype"), ("data_gen_s", "data gen"),
                              ("python_s", "Python"), ("numpy_s", "NumPy"), ("speedup", "speedup"),
                              ("match", "match")]))
    print("\nspeedup = Python の時間 / NumPy の時間（中央値）。matmul の n は n×n 行列。")
    print("※ 時間は環境・実行ごとに変わります。データ生成（list・配列の作成）の時間は計算時間に含めていません。")

# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：dtype を np.float32・np.int64 に変えて、時間と誤差を比べる（int では make_inputs を工夫する）。
# TODO 2：n = 1, 10 のような小さいサイズで、NumPy が Python より遅くなる条件を探す。
# TODO 3：list → NumPy 配列の変換時間（np.asarray）を含めた場合の speedup を計算する。
# TODO 4：Task D を np.maximum(x, 0) ** 2 などの別の書き方にして比べる。
