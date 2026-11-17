# C3：RSA暗号の仕組みと計算量 — starter code
#
# 小さな素数で RSA の鍵を作り、整数のメッセージを暗号化・復号する。
# 剰余べき乗を「反復乗算」「繰返し二乗法」「Python 標準の pow」の3つで計算し、結果を比べる。
#
# ⚠️ 教材用の小さな数値によるデモであり、実用の暗号ではない。
#    秘密指数 d を表示しているのも、これが実用の秘密鍵ではないから。

import rsa
from modular_power import modular_power_naive, modular_power_squaring

p = 61
q = 53
e = 17
message = 65

print("=== C3：RSA暗号の仕組みと計算量 ===")
print("（教材用の小さな数値によるデモです。実用の暗号には使えません）")
print()

public_key, private_key = rsa.generate_keys(p, q, e)
n, d = private_key

print("p, q          :", p, q)
print("n = p × q     :", n)
print("φ(n)          :", rsa.totient(p, q))
print("公開指数 e    :", e)
print("秘密指数 d    :", d, f"（e × d mod φ(n) = {e * d % rsa.totient(p, q)}）")
print("公開鍵 (n, e) :", public_key)
print()

ciphertext = rsa.encrypt(message, public_key)
decrypted = rsa.decrypt(ciphertext, private_key)

print("元のメッセージ m :", message)
print("暗号文 c = m^e mod n :", ciphertext)
print("復号結果 c^d mod n   :", decrypted)
print("元のメッセージと一致:", decrypted == message)
print()

# 3つの方法で同じ計算をして、結果を比べる
for label, base, exponent in [("暗号化 m^e mod n", message, e), ("復号   c^d mod n", ciphertext, d)]:
    naive = modular_power_naive(base, exponent, n)
    squaring = modular_power_squaring(base, exponent, n)
    builtin = pow(base, exponent, n)
    print(f"{label}：反復乗算 = {naive}, 繰返し二乗法 = {squaring}, pow = {builtin}")
    print("  反復乗算と繰返し二乗法の一致:", naive == squaring)
    print("  Python 標準の pow との一致   :", squaring == builtin)


# ------------------------------------------------------------
# 学生が取り組む課題（ここから先は各チームで実装する）
# ------------------------------------------------------------
# TODO 1：別の小さな素数 p, q と e で鍵を作り、暗号化・復号を確かめる。
# TODO 2：rsa.encrypt(message, public_key, power=modular_power_naive) のように、
#         計算方法を変えても結果が同じになることを確かめる。
# TODO 3：benchmark.py を使って、指数を変えたときの処理時間と乗算回数を比べる。
# TODO 4：0, 1, n − 1 を暗号化すると何が起きるか調べ、教科書的な RSA の弱点を考える。
