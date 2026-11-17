# C3：RSA の数学的基礎（最大公約数・素数判定・モジュラ逆元）
#
# 最大公約数には、教科書 第5章の gcd()（ユークリッドの互除法・再帰版）をそのまま使う。

from textbook.gcd import gcd


def is_coprime(a, b):
    """a と b が互いに素（最大公約数が1）か

    教科書の gcd() は、引数に負の数があると負の値を返すことがある（例：gcd(4, -6) は -2）。
    そのため、絶対値で 1 かどうかを調べる。
    """
    return abs(gcd(a, b)) == 1


def is_prime(n):
    """n が素数か（試し割り法：2 から √n までの整数で割ってみる）

    負の数・0・1 は素数ではない。小さな整数を対象とした、単純で遅い方法である。
    """
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def mod_inverse(a, m):
    """a × x ≡ 1 (mod m) を満たす x（0 ≤ x < m）を返す（モジュラ逆元）

    逆元が存在するのは、a と m が互いに素（gcd(a, m) = 1）のときだけ。
    存在しない場合は ValueError を送出する。

    Core Research では Python 標準の pow(a, -1, m) を使う。
    拡張ユークリッド互除法による計算は Advanced B の課題（extended_gcd の TODO）。
    """
    if m < 2:
        raise ValueError(f"法 m は 2 以上である必要があります（m = {m}）")
    if not is_coprime(a, m):
        raise ValueError(f"{a} と {m} は互いに素でないため、逆元は存在しません")
    return pow(a, -1, m)


def extended_gcd(a, b):
    """TODO（Advanced B）：拡張ユークリッド互除法

    a × x + b × y = gcd(a, b) を満たす (gcd(a, b), x, y) を返す関数を実装する。
    これを使うと、mod_inverse() を pow(a, -1, m) を使わずに計算できる。
    ヒント：教科書の gcd() と同じく、再帰で書くと短く書ける。
    """
    raise NotImplementedError("拡張ユークリッド互除法は Advanced B の課題です")
