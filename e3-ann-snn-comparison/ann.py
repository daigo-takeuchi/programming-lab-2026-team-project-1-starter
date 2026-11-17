# E3：簡易 ANN（全結合層1層）
#
#   y = ReLU(Wx + b)
#
#   x : 入力ベクトル（長さ n の list）
#   W : 重み行列（m 行 n 列。W[i][j] は 入力 j → 出力 i の重み）
#   b : バイアス（長さ m の list）
#   y : 出力ベクトル（長さ m の list。連続値の activation）
#
# NumPy を使わず、重み付き和を for ループで計算する。
# 出力 1 つにつき 乗算 n 回・加算 n 回（バイアスから始めて n 個の積を足す）なので、
# 全体の積和演算は m × n 回 = O(nm)。


def relu(v):
    """ReLU(v) = max(0, v)"""
    return v if v > 0 else 0.0


def check_shapes(x, W, b):
    """入力・重み・バイアスの次元が合っているか確認する（合わなければ ValueError）"""
    m = len(W)
    if m == 0:
        raise ValueError("重み行列 W が空です")
    if len(b) != m:
        raise ValueError(f"バイアスの長さ {len(b)} が出力次元 {m}（W の行数）と一致しません")
    n = len(x)
    for i, row in enumerate(W):
        if len(row) != n:
            raise ValueError(f"W の {i} 行目の長さ {len(row)} が入力次元 {n} と一致しません")


def weighted_sum(x, W, b):
    """活性化関数をかける前の値 Wx + b（長さ m の list）"""
    check_shapes(x, W, b)
    z = []
    for i in range(len(W)):
        acc = b[i]
        for j in range(len(x)):
            acc += W[i][j] * x[j]   # 乗算1回・加算1回
        z.append(acc)
    return z


def dense_forward(x, W, b, activation=relu):
    """全結合層の forward：y = activation(Wx + b)"""
    return [activation(v) for v in weighted_sum(x, W, b)]


def ann_operation_counts(n, m):
    """この実装の全結合層1層（入力 n、出力 m）の演算回数とパラメータ数"""
    return {
        "multiplications": n * m,
        "additions": n * m,
        "comparisons": m,               # ReLU の比較（v > 0）
        "parameters": n * m + m,        # W の n×m 個 + b の m 個
        "values_read": n * m + m,       # 1回の forward で読み出すパラメータの数（全部）
    }


# TODO（学生）：2層以上の ANN（隠れ層あり）を作り、演算回数の式を考える。
# TODO（学生）：ReLU 以外の活性化関数（シグモイドなど）と比べる。
