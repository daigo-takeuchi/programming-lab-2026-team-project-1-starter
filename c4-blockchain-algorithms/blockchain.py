# C4：簡易ブロックチェーン（ハッシュチェーン）
#
# ■ ブロック
#   {"index": 1, "data": "Transaction A", "previous_hash": "...", "hash": "..."} の辞書。
#   hash は index・data・previous_hash から SHA-256 で計算する（16進数の文字列）。
#
# ■ ハッシュの計算方法（シリアライズ）
#   3つの値を、キーの順序を固定した JSON 文字列にしてから UTF-8 のバイト列に変換し、
#   hashlib.sha256 でハッシュ値を求める。
#   単純な文字列連結（例：str(1) + "23" と str(12) + "3" はどちらも "123"）のような
#   曖昧さがなく、同じ入力からは必ず同じハッシュ値が得られる。
#
# ⚠️ これは教材用の簡易ハッシュチェーンであり、実用のブロックチェーンではない。
#    攻撃者が改ざんしたブロック以降のハッシュをすべて計算し直すと、
#    このチェーンの内部の整合性チェックだけでは改ざんを検出できない（README 4章）。

import copy
import hashlib
import json

GENESIS_DATA = "Genesis Block"
GENESIS_PREVIOUS_HASH = "0" * 64        # Genesis Block には前のブロックがない


def compute_hash(index, data, previous_hash):
    """ブロックのハッシュ値（SHA-256 の16進数文字列）を計算する"""
    content = {"index": index, "data": data, "previous_hash": previous_hash}
    serialized = json.dumps(content, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def make_block(index, data, previous_hash):
    """ブロックを作る（hash は自動で計算する）"""
    return {
        "index": index,
        "data": data,
        "previous_hash": previous_hash,
        "hash": compute_hash(index, data, previous_hash),
    }


def create_genesis_block():
    """最初のブロック（Genesis Block）を作る"""
    return make_block(0, GENESIS_DATA, GENESIS_PREVIOUS_HASH)


def add_block(chain, data):
    """チェーンの末尾に新しいブロックを追加し、そのブロックを返す"""
    last = chain[-1]
    block = make_block(last["index"] + 1, data, last["hash"])
    chain.append(block)
    return block


def create_chain(data_list):
    """Genesis Block と、data_list の各データを持つブロックからなるチェーンを作る"""
    chain = [create_genesis_block()]
    for data in data_list:
        add_block(chain, data)
    return chain


def find_problems(chain):
    """チェーンの不整合を調べ、(ブロックの位置, 内容) のリストを返す（問題がなければ空）

    確認すること：
      1. 各ブロックに保存された hash が、再計算した値と一致する
      2. previous_hash が、直前のブロックの hash と一致する
      3. index が 0, 1, 2, ... と連続している
      4. Genesis Block が定義済みの形式（index 0、previous_hash が 0 × 64）に従う
    """
    if len(chain) == 0:
        return [(None, "チェーンが空です")]

    problems = []
    genesis = chain[0]
    if genesis["index"] != 0 or genesis["previous_hash"] != GENESIS_PREVIOUS_HASH:
        problems.append((0, "Genesis Block の形式が正しくありません"))

    for i, block in enumerate(chain):
        if block["index"] != i:
            problems.append((i, f"index が連続していません（{block['index']}）"))
        if block["hash"] != compute_hash(block["index"], block["data"], block["previous_hash"]):
            problems.append((i, "保存された hash が再計算した値と一致しません"))
        if i > 0 and block["previous_hash"] != chain[i - 1]["hash"]:
            problems.append((i, "previous_hash が直前のブロックの hash と一致しません"))
    return problems


def is_valid_chain(chain):
    """チェーンに不整合がなければ True"""
    return len(find_problems(chain)) == 0


def tamper_data(chain, index, new_data):
    """改ざん実験用：チェーンのコピーを作り、index 番目のブロックの data だけを書き換えて返す

    hash は計算し直さない。元のチェーンは変更しない。
    """
    tampered = copy.deepcopy(chain)
    tampered[index]["data"] = new_data
    return tampered


# ------------------------------------------------------------
# 学生が取り組む課題（Advanced C・E）
# ------------------------------------------------------------
# TODO：改ざんしたブロックから最後まで、hash と previous_hash を計算し直す関数を作り、
#       find_problems() で改ざんを検出できなくなることを確かめる。
#       計算し直したハッシュの回数（改ざん位置以降のブロック数）も数える。
# TODO：信頼できる外部の値（例：最後のブロックの正しい hash を別に保存しておく）と比べて、
#       上の改ざんを検出する方法を考える。
