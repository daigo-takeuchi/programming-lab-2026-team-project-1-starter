# C3：剰余べき乗の性能比較 — 学生が実験を作るための入口
#
# ここにあるのは「1つの条件で1回だけ測る例」だけである。
# 指数や modulus を変えた繰り返し測定、乗算回数の計測、グラフ化は、学生が実装する（下の TODO）。
#
# 実行：python3 benchmark.py

import time

from modular_power import MAX_NAIVE_EXPONENT, modular_power_naive, modular_power_squaring

if __name__ == "__main__":
    base = 65
    exponent = 100_000
    modulus = 3233

    results = {}
    times = {}
    for name, power in [("反復乗算", modular_power_naive),
                        ("繰返し二乗法", modular_power_squaring),
                        ("pow（標準）", pow)]:
        start = time.perf_counter()
        results[name] = power(base, exponent, modulus)
        times[name] = time.perf_counter() - start

    print(f"base = {base}, exponent = {exponent:,}（{exponent.bit_length()} ビット）, "
          f"modulus = {modulus}（{modulus.bit_length()} ビット）")
    print("1回だけの測定例：")
    for name in results:
        print(f"  {name:<10}: 結果 = {results[name]}, 時間 = {times[name]:.6f} 秒")
    print("結果がすべて一致:", len(set(results.values())) == 1)
    print(f"（反復乗算の指数の上限：{MAX_NAIVE_EXPONENT:,}）")


# ------------------------------------------------------------
# 学生が取り組む課題
# ------------------------------------------------------------
# TODO 1：指数 e を変更する（例：10, 100, 1,000, 10,000, 100,000, 1,000,000）。
# TODO 2：通常の反復乗算の時間を測定する。
# TODO 3：繰返し二乗法の時間を測定する。
# TODO 4：Python 標準の pow の時間を測定する。
# TODO 5：各アルゴリズムの剰余乗算の回数を計測する（回数を数える版の関数を自分たちで作る）。
# TODO 6：複数回測定して、平均・中央値を比較する（statistics モジュール）。
# TODO 7：指数 e と処理時間の関係をグラフ化する。
# TODO 8：指数のビット長（exponent.bit_length()）と処理時間の関係を考察する。
# TODO 9：modulus のビット長を変えて比較する（大きな素数どうしの積など）。
# TODO 10：理論計算量（反復乗算 O(e)、繰返し二乗法 O(log e)）と実測結果を比較する。
#
# 注意：
#   - すべての方法で、同じ base・exponent・modulus を使い、結果が一致することを確認する。
#   - 反復乗算は指数の「数値」に比例して遅くなる。指数を大きくしすぎない
#     （MAX_NAIVE_EXPONENT を超えると ValueError になる）。
#   - 指数の「数値」（例：1,000,000）と「ビット長」（例：20 ビット）を区別する。
#   - 実行時間の比較と、演算回数の比較を区別する。
#   - Python 標準の pow は C 言語で実装・最適化されている。Python で書いた関数との
#     時間差には、アルゴリズムの違いだけでなく実装言語の違いも含まれる。
#   - 測りたい処理だけを time.perf_counter() で挟む：
#       start = time.perf_counter()
#       modular_power_squaring(base, exponent, modulus)
#       elapsed = time.perf_counter() - start
