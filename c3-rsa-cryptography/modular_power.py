# C3：剰余べき乗（base ** exponent % modulus）の計算方法の比較
#
#   modular_power_naive    : 通常の反復乗算（base を exponent 回掛ける）  → 乗算 約 exponent 回
#   modular_power_squaring : 繰返し二乗法                                  → 乗算 約 2 × log2(exponent) 回
#   pow(base, exponent, modulus) : Python 標準（比較・検証用）
#
# どちらも、掛けるたびに modulus で割った余りを取る。
# base ** exponent を先に計算すると、途中の整数が巨大になってしまうため。

# 反復乗算で扱う指数の上限（これより大きいと時間がかかりすぎるので、安全のため止める）
MAX_NAIVE_EXPONENT = 10_000_000


def _check_arguments(base, exponent, modulus):
    """入力条件：base は整数、exponent は 0 以上の整数、modulus は正の整数"""
    for name, value in [("base", base), ("exponent", exponent), ("modulus", modulus)]:
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"{name} は整数である必要があります（{value!r}）")
    if exponent < 0:
        raise ValueError(f"exponent は 0 以上である必要があります（{exponent}）")
    if modulus <= 0:
        raise ValueError(f"modulus は正の整数である必要があります（{modulus}）")


def modular_power_naive(base, exponent, modulus):
    """通常の反復乗算による剰余べき乗

    result を 1 から始め、base を exponent 回掛ける。掛けるたびに modulus の余りを取る。
    （result を 1 % modulus から始めるのは、modulus = 1 のとき答えが 0 になるようにするため）
    """
    _check_arguments(base, exponent, modulus)
    if exponent > MAX_NAIVE_EXPONENT:
        raise ValueError(f"exponent が大きすぎます（上限 {MAX_NAIVE_EXPONENT:,}）")

    result = 1 % modulus
    for _ in range(exponent):
        result = (result * base) % modulus
    return result


def modular_power_squaring(base, exponent, modulus):
    """繰返し二乗法による剰余べき乗（反復版）

    指数を2進数で考え、下の桁から順に処理する。
      - 指数が奇数なら、現在の底を結果に掛ける
      - 底を二乗し、指数を半分にする（切り捨て）
      - 指数が 0 になるまで繰り返す

    例：3^13（13 = 2進数で 1101）= 3^8 × 3^4 × 3^1
    """
    _check_arguments(base, exponent, modulus)

    result = 1 % modulus
    base = base % modulus
    while exponent > 0:
        if exponent % 2 == 1:                   # 奇数：今の底を結果に掛ける
            result = (result * base) % modulus
        base = (base * base) % modulus          # 底を二乗する
        exponent = exponent // 2                # 指数を半分にする
    return result


# ------------------------------------------------------------
# 学生が取り組む課題
# ------------------------------------------------------------
# TODO（Core 7 / Advanced A）：各関数で、剰余乗算を何回行ったかを数える。
#   例：乗算の回数も一緒に返す版（modular_power_naive_count など）を自分たちで作る。
#   ここにある関数は結果だけを返す（テストや rsa.py が使うので、戻り値の形は変えないこと）。
# TODO（Advanced A）：再帰版の繰返し二乗法を書き、反復版と比べる。
