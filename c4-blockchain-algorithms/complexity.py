# C4：計算量の理論値（ハッシュ演算の回数のモデル）
#
# N はデータ件数（葉の数）。Merkle Tree の関数は、N が 2 のべき乗の完全二分木を前提とする。
# ここで数えるのは「ハッシュ演算の回数」であり、1回のハッシュ計算にかかる時間
# （データのバイト長に比例する）は別に考える必要がある。

from merkle_tree import is_power_of_two


def _check_power_of_two(n):
    if not is_power_of_two(n):
        raise ValueError(f"N は 2 のべき乗の正の整数である必要があります（N = {n!r}）")


def _check_positive(n, name="N"):
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError(f"{name} は正の整数である必要があります（{name} = {n!r}）")


def tree_height(n):
    """完全二分木の高さ = log2(N)"""
    _check_power_of_two(n)
    return n.bit_length() - 1


def leaf_count(n):
    """葉ノード数 = N"""
    _check_power_of_two(n)
    return n


def internal_node_count(n):
    """内部ノード数 = N − 1"""
    _check_power_of_two(n)
    return n - 1


def total_node_count(n):
    """合計ノード数 = 2N − 1"""
    _check_power_of_two(n)
    return 2 * n - 1


def proof_length(n):
    """Merkle Proof に必要な兄弟ハッシュの数 = log2(N)"""
    return tree_height(n)


def proof_size_bytes(n, hash_size=32):
    """Merkle Proof の兄弟ハッシュの合計バイト数（左右の情報は含めない）"""
    return proof_length(n) * hash_size


def hashes_full_rebuild(n):
    """全件のデータから Root を作り直すときのハッシュ演算回数 = 葉 N 回 + 内部ノード N − 1 回"""
    return total_node_count(n)


def hashes_proof_verification(n):
    """Merkle Proof の検証に必要なハッシュ演算回数 = 対象データの葉 1 回 + log2(N) 回"""
    return 1 + proof_length(n)


def hashes_leaf_update(n):
    """既存の木で葉を1つ更新するときのハッシュ演算回数 = 葉 1 回 + Root までの log2(N) 回"""
    return 1 + tree_height(n)


def hashes_chain_validation(b):
    """B 個のブロックのチェーンを先頭から検証するときのハッシュ演算回数 = B 回"""
    _check_positive(b, "B")
    return b


def hashes_chain_recompute(b, position):
    """position 番目（0 から）のブロックを変更し、そこから最後までハッシュを計算し直す回数"""
    _check_positive(b, "B")
    if not isinstance(position, int) or not 0 <= position < b:
        raise ValueError(f"position は 0 以上 B 未満である必要があります（{position!r}）")
    return b - position
