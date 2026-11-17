# C3：教科書的な RSA（鍵生成・暗号化・復号）
#
# ⚠️ これは数学的な原理を理解するための「教科書的な RSA」であり、実用的な暗号通信には使えない。
#    - 小さな素数しか扱わないので、n はすぐに素因数分解でき、秘密鍵が求められてしまう
#    - パディング（RSA-OAEP など）がないので、同じメッセージは常に同じ暗号文になる
#    - 実際の暗号には、信頼できる暗号ライブラリを使うこと

from modular_power import modular_power_squaring
from number_theory import is_coprime, is_prime, mod_inverse


def totient(p, q):
    """φ(n) = (p − 1)(q − 1)（p, q は異なる素数）"""
    return (p - 1) * (q - 1)


def generate_keys(p, q, e):
    """素数 p, q と公開指数 e から、公開鍵 (n, e) と秘密鍵 (n, d) を作る

    戻り値：(public_key, private_key)
    不正な入力には ValueError を送出する。
    """
    if not is_prime(p):
        raise ValueError(f"p = {p} は素数ではありません")
    if not is_prime(q):
        raise ValueError(f"q = {q} は素数ではありません")
    if p == q:
        raise ValueError("p と q は異なる素数である必要があります")

    n = p * q
    phi = totient(p, q)

    if not 1 < e < phi:
        raise ValueError(f"e は 1 < e < φ(n) = {phi} を満たす必要があります（e = {e}）")
    if not is_coprime(e, phi):
        raise ValueError(f"e = {e} と φ(n) = {phi} は互いに素ではありません（逆元 d が存在しない）")

    d = mod_inverse(e, phi)        # e × d ≡ 1 (mod φ(n))
    return (n, e), (n, d)


def _check_message(value, n, name):
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} は整数である必要があります（{value!r}）")
    if not 0 <= value < n:
        raise ValueError(f"{name} は 0 以上 n = {n} 未満である必要があります（{value}）")


def encrypt(message, public_key, power=modular_power_squaring):
    """暗号化：c = m^e mod n

    power には剰余べき乗の関数を渡せる（例：modular_power_naive、pow）。
    """
    n, e = public_key
    _check_message(message, n, "message")
    return power(message, e, n)


def decrypt(ciphertext, private_key, power=modular_power_squaring):
    """復号：m = c^d mod n"""
    n, d = private_key
    _check_message(ciphertext, n, "ciphertext")
    return power(ciphertext, d, n)
