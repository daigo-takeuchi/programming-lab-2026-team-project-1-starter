# C4：ブロックチェーンの仕組みと計算量 — starter code
#
# Demo A：簡易ブロックチェーン（ハッシュチェーン）を作り、改ざんを検出する
# Demo B：Merkle Tree を作り、Merkle Root を計算する
#
# 扱うデータはすべて架空の文字列である。

import blockchain
import complexity
import merkle_tree

# ------------------------------------------------------------
# Demo A：簡易ブロックチェーン
# ------------------------------------------------------------
print("=== C4：ブロックチェーンの仕組みと計算量 ===")
print()
print("--- Demo A：簡易ブロックチェーン ---")

chain = blockchain.create_chain([
    "Alice -> Bob : 10",
    "Bob -> Carol : 4",
    "Carol -> Dave : 2",
    "Dave -> Alice : 1",
])

for block in chain:
    print(f"[{block['index']}] data = {block['data']!r}")
    print(f"    previous_hash = {block['previous_hash'][:16]}...")
    print(f"    hash          = {block['hash'][:16]}...")

print()
print("正常なチェーンの検証:", "OK" if blockchain.is_valid_chain(chain) else "NG")

# 元のチェーンは残したまま、コピーのブロック2のデータを書き換える
tampered = blockchain.tamper_data(chain, 2, "Bob -> Carol : 400")
print()
print("ブロック2のデータを 'Bob -> Carol : 400' に書き換えたコピーを検証:")
print("検証結果:", "OK" if blockchain.is_valid_chain(tampered) else "NG（不整合を検出）")
for index, message in blockchain.find_problems(tampered):
    print(f"  ブロック{index}: {message}")
print("元のチェーンは変更されていない:", blockchain.is_valid_chain(chain))

# ------------------------------------------------------------
# Demo B：Merkle Tree
# ------------------------------------------------------------
print()
print("--- Demo B：Merkle Tree ---")

data = ["Tx A", "Tx B", "Tx C", "Tx D"]
tree = merkle_tree.build_tree(data)

print("データ:", data)
print("葉ハッシュ:")
for d, h in zip(data, tree[0]):
    print(f"  {d!r:8} -> {merkle_tree.short_hex(h)}")
print("1つ上の階層:")
for i, h in enumerate(tree[1]):
    print(f"  H{2 * i}{2 * i + 1}      -> {merkle_tree.short_hex(h)}")
print("Merkle Root:", tree[-1][0].hex())
print("データ件数 N:", len(data), " 木の高さ:", merkle_tree.tree_height(tree))

changed = merkle_tree.merkle_root(["Tx A", "Tx B", "Tx C (changed)", "Tx D"])
print("データ C を変えたときの Root:", merkle_tree.short_hex(changed), "（元の Root と一致:", changed == tree[-1][0], "）")

print()
print("理論的なハッシュ計算回数（1件のデータが含まれることを確かめる場合）")
for n in [4, 8, 1024, 2 ** 20]:
    print(f"  N = {n:>9,}：全件から Root を再計算 {complexity.hashes_full_rebuild(n):>9,} 回 / "
          f"Merkle Proof の検証 {complexity.hashes_proof_verification(n):>2} 回"
          f"（兄弟ハッシュ {complexity.proof_length(n)} 個）")
print("（Merkle Proof の検証は、信頼できる Merkle Root が手元にあることが前提）")

print()
print("TODO：merkle_tree.generate_proof() と merkle_tree.verify_proof() を実装し、")
print("      Merkle Proof を実際に作って検証してみよう（README 6章・12章 Advanced A）。")


# ------------------------------------------------------------
# 学生が取り組む課題（ここから先は各チームで実装する）
# ------------------------------------------------------------
# TODO 1：Merkle Proof の生成・検証を実装する（merkle_tree.py）。
# TODO 2：改ざんするブロックの位置を変えて、find_problems() の結果を比べる。
# TODO 3：改ざん後にハッシュをすべて計算し直したチェーンを作り、検出できるか確かめる。
# TODO 4：benchmark.py を使って、N を変えたときの処理時間を測定する。
