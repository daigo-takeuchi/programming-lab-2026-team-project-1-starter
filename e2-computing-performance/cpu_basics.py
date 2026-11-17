# E2：Python の for ループによる基本計算（Python 標準ライブラリのみ）
#
# numpy_benchmark.py と「同じ数学的計算」を、list と for ループで書いたもの。
# 計算結果の正しさの基準（リファレンス）でもある。
#
#   Task A：要素ごとの演算   y[i] = a[i] * b[i] + c[i]          O(n)
#   Task B：総和             s = a[0] + a[1] + ... + a[n-1]      O(n)
#   Task C：行列積           C[i][j] = Σ_k A[i][k] * B[k][j]     O(n m p)（正方行列なら O(n^3)）
#   Task D：条件分岐         y[i] = x[i]^2 (x[i] > 0)、0 (それ以外)  O(n)

import random


# ------------------------------------------------------------
# データの生成（計算時間とは別に測る）
# ------------------------------------------------------------
def make_vector(n, seed=0, low=-1.0, high=1.0):
    """長さ n の乱数リスト（seed 固定）"""
    if n < 0:
        raise ValueError("n は 0 以上にしてください")
    rng = random.Random(seed)
    return [rng.uniform(low, high) for _ in range(n)]


def make_matrix(rows, cols, seed=0, low=-1.0, high=1.0):
    """rows 行 cols 列の乱数行列（リストのリスト、seed 固定）"""
    if rows < 0 or cols < 0:
        raise ValueError("行数・列数は 0 以上にしてください")
    rng = random.Random(seed)
    return [[rng.uniform(low, high) for _ in range(cols)] for _ in range(rows)]


# ------------------------------------------------------------
# Task A：要素ごとの演算
# ------------------------------------------------------------
def elementwise(a, b, c):
    """y[i] = a[i] * b[i] + c[i]（乗算 n 回・加算 n 回）"""
    if not (len(a) == len(b) == len(c)):
        raise ValueError(f"長さがそろっていません：{len(a)}, {len(b)}, {len(c)}")
    y = [0.0] * len(a)
    for i in range(len(a)):
        y[i] = a[i] * b[i] + c[i]
    return y


# ------------------------------------------------------------
# Task B：総和
# ------------------------------------------------------------
def total(a):
    """全要素の総和（加算 n 回）。空のリストの総和は 0"""
    s = 0.0
    for v in a:
        s += v
    return s


# ------------------------------------------------------------
# Task C：行列積
# ------------------------------------------------------------
def matmul(A, B):
    """C = AB を 3 重 for ループで計算する（A は n×m、B は m×p → C は n×p。乗算・加算 n m p 回）"""
    n = len(A)
    m = len(B)
    if n == 0 or m == 0:
        raise ValueError("空の行列は扱いません")
    if any(len(row) != m for row in A):
        raise ValueError(f"A の列数が B の行数 {m} と一致しません")
    p = len(B[0])
    if any(len(row) != p for row in B):
        raise ValueError("B の各行の長さがそろっていません")

    C = [[0.0] * p for _ in range(n)]
    for i in range(n):
        for j in range(p):
            s = 0.0
            for k in range(m):
                s += A[i][k] * B[k][j]
            C[i][j] = s
    return C


# ------------------------------------------------------------
# Task D：条件分岐
# ------------------------------------------------------------
def conditional_square(x):
    """x > 0 なら x * x、それ以外は 0 にする（要素ごとに if 文で分岐）"""
    y = [0.0] * len(x)
    for i, v in enumerate(x):
        if v > 0:
            y[i] = v * v
        else:
            y[i] = 0.0
    return y


# ------------------------------------------------------------
# 演算回数（理論値）
# ------------------------------------------------------------
def operation_counts(task, n, m=None, p=None):
    """各 Task の演算回数の理論値（この実装での数え方）"""
    if task == "elementwise":
        return {"multiplications": n, "additions": n, "comparisons": 0}
    if task == "total":
        return {"multiplications": 0, "additions": n, "comparisons": 0}
    if task == "matmul":
        m = n if m is None else m
        p = n if p is None else p
        return {"multiplications": n * m * p, "additions": n * m * p, "comparisons": 0}
    if task == "conditional":
        return {"multiplications": n, "additions": 0, "comparisons": n}   # 乗算は最大 n 回
    raise ValueError(f"不明な task：{task}")


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：総和を while 文で書き、for 文・組み込みの sum() と速さを比べる。
# TODO 2：行列積のループの順番（i-j-k、i-k-j など）を入れ替えて、速さが変わるか調べる（メモリアクセスの順序）。
# TODO 3：条件分岐の条件（x > 0 の割合）を変えて、実行時間が変わるか調べる。
# TODO 4：内包表記（[a*b + c for a, b, c in zip(...)]）で書き、for ループと比べる。
