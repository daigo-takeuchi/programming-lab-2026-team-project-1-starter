# C4：Merkle Tree（ハッシュ木）
#
# ■ ハッシュの計算規則（RFC 6962 と同じ接頭辞の付け方）
#   葉ノード  ：leaf_hash   = SHA-256( 0x00 + データのバイト列 )
#   内部ノード：parent_hash = SHA-256( 0x01 + 左の子のハッシュ + 右の子のハッシュ )
#   接頭辞 0x00 / 0x01 によって、葉と内部ノードのハッシュを区別する。
#   ハッシュ値は内部では bytes（32バイト）で扱い、表示するときに16進数文字列にする。
#
# ■ 木の表し方
#   build_tree() は「階層のリスト」を返す。
#     levels[0]  = 葉ハッシュのリスト（N 個）
#     levels[1]  = その親のリスト（N/2 個）
#     ...
#     levels[-1] = [Merkle Root]
#
#        levels[2]:            Root
#        levels[1]:      H01          H23
#        levels[0]:   H0    H1     H2    H3
#                     |     |      |     |
#        データ：      A     B      C     D
#
# ■ Core Research の対象
#   データ件数 N が 2 のべき乗（1, 2, 4, 8, ...）の場合だけを扱う。
#   それ以外の N は ValueError にする（Advanced D の課題）。

import hashlib

LEAF_PREFIX = b"\x00"
NODE_PREFIX = b"\x01"
HASH_SIZE = 32          # SHA-256 のハッシュ値は 32 バイト


def _to_bytes(data):
    """データを bytes にする（文字列は UTF-8 で変換）"""
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return data.encode("utf-8")
    raise TypeError(f"データは str または bytes である必要があります（{type(data).__name__}）")


def leaf_hash(data):
    """葉ノードのハッシュ値（bytes）"""
    return hashlib.sha256(LEAF_PREFIX + _to_bytes(data)).digest()


def parent_hash(left, right):
    """内部ノードのハッシュ値（bytes）：左右の子のハッシュ値をこの順に結合して計算する"""
    for h in (left, right):
        if not isinstance(h, bytes) or len(h) != HASH_SIZE:
            raise ValueError("子のハッシュ値は 32 バイトの bytes である必要があります")
    return hashlib.sha256(NODE_PREFIX + left + right).digest()


def is_power_of_two(n):
    """n が 2 のべき乗（1, 2, 4, 8, ...）か"""
    return isinstance(n, int) and not isinstance(n, bool) and n >= 1 and (n & (n - 1)) == 0


def build_tree(data_list):
    """データのリストから Merkle Tree を作り、階層のリスト levels を返す

    1. 各データの葉ハッシュを計算する（levels[0]）
    2. 隣り合う2つのハッシュから親のハッシュを計算して、1つ上の階層を作る
    3. 1つになるまで（Root まで）繰り返す
    """
    if not isinstance(data_list, list):
        raise TypeError("データはリストで渡してください")
    if not is_power_of_two(len(data_list)):
        raise ValueError(f"Core Research ではデータ件数が 2 のべき乗である必要があります（N = {len(data_list)}）")

    level = [leaf_hash(data) for data in data_list]
    levels = [level]
    while len(level) > 1:
        level = [parent_hash(level[i], level[i + 1]) for i in range(0, len(level), 2)]
        levels.append(level)
    return levels


def merkle_root(data_list):
    """データのリストから Merkle Root（bytes）を計算する"""
    return build_tree(data_list)[-1][0]


def tree_height(levels):
    """木の高さ（葉から Root までの階層の数）"""
    return len(levels) - 1


def short_hex(h, length=16):
    """表示用：ハッシュ値の16進数表記の先頭 length 文字"""
    return h.hex()[:length] + "..."


# ------------------------------------------------------------
# 学生が実装する関数（Core 6 / Advanced A・B）
# ------------------------------------------------------------

def generate_proof(tree, index):
    """TODO（Advanced A）：index 番目のデータの Merkle Proof を作る

    引数
        tree  : build_tree() が返した階層のリスト
        index : 証明したいデータの位置（0 から）

    考え方
        葉から Root まで1階層ずつ上がりながら、各階層で「兄弟ノードのハッシュ」を集める。
        - 自分が左の子（位置が偶数）なら、兄弟は右隣（位置 + 1）
        - 自分が右の子（位置が奇数）なら、兄弟は左隣（位置 − 1）
        - 1つ上の階層での自分の位置は、位置 // 2

    戻り値の形はチームで設計すること。
        兄弟ハッシュだけでなく、それが「左右どちら側にあるか」の情報も必要。
        例：[(兄弟のハッシュ, "left" または "right"), ...]（葉に近い順）
    """
    raise NotImplementedError("Merkle Proof の生成は学生の課題です")


def verify_proof(data, proof, root):
    """TODO（Advanced A）：data が、root を持つ Merkle Tree に含まれることを proof で検証する

    考え方
        1. data の葉ハッシュを計算する
        2. proof の兄弟ハッシュを順に使い、左右の順序に気をつけて parent_hash() で親を計算していく
        3. 最後に得られたハッシュが root と一致すれば True

    前提：root は信頼できる経路で手に入れたものであること。
          root そのものが偽物なら、この検証には意味がない。
    """
    raise NotImplementedError("Merkle Proof の検証は学生の課題です")


def update_leaf(tree, index, new_data):
    """TODO（Advanced B）：index 番目のデータを new_data に変えたときの木を、
    変更した葉から Root までの経路だけを計算し直して求める

    木全体を作り直す build_tree() と、ハッシュ計算回数・実行時間を比べる。
    """
    raise NotImplementedError("Merkle Tree の増分更新は学生の課題です")
