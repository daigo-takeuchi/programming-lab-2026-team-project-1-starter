# C4：Merkle Tree のテスト
#
# Merkle Proof の生成・検証（generate_proof、verify_proof）は学生の課題なので、
# 未実装の間はテストをスキップする。実装すると自動的にテストが実行される。

import hashlib
import unittest

import merkle_tree as mt


def sha(b):
    return hashlib.sha256(b).digest()


class TestMerkleTree(unittest.TestCase):

    def test_leaf_hash(self):
        """1. 葉ハッシュ = SHA-256(0x00 + データ)"""
        self.assertEqual(mt.leaf_hash("A"), sha(b"\x00A"))
        self.assertEqual(mt.leaf_hash(b"A"), mt.leaf_hash("A"))
        self.assertEqual(mt.leaf_hash("日本語"), sha(b"\x00" + "日本語".encode("utf-8")))
        # RFC 6962 の空の葉のハッシュ値と一致する
        self.assertEqual(mt.leaf_hash(b"").hex(),
                         "6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d")

    def test_parent_hash(self):
        """2. 親ハッシュ = SHA-256(0x01 + 左 + 右)、左右の順序で値が変わる"""
        a, b = mt.leaf_hash("A"), mt.leaf_hash("B")
        self.assertEqual(mt.parent_hash(a, b), sha(b"\x01" + a + b))
        self.assertNotEqual(mt.parent_hash(a, b), mt.parent_hash(b, a))
        # 葉と内部ノードは接頭辞で区別される
        self.assertNotEqual(mt.parent_hash(a, b), mt.leaf_hash(a + b))

    def test_root_n2(self):
        """3. 2件のデータの Merkle Root"""
        expected = sha(b"\x01" + sha(b"\x00A") + sha(b"\x00B"))
        self.assertEqual(mt.merkle_root(["A", "B"]), expected)

    def test_root_n4(self):
        """4. 4件のデータの Merkle Root"""
        h = [sha(b"\x00" + d) for d in (b"A", b"B", b"C", b"D")]
        expected = sha(b"\x01" + sha(b"\x01" + h[0] + h[1]) + sha(b"\x01" + h[2] + h[3]))
        self.assertEqual(mt.merkle_root(["A", "B", "C", "D"]), expected)
        tree = mt.build_tree(["A", "B", "C", "D"])
        self.assertEqual([len(level) for level in tree], [4, 2, 1])
        self.assertEqual(mt.tree_height(tree), 2)

    def test_root_n8(self):
        """5. 8件のデータの Merkle Root（4件ずつの木の Root を組み合わせたものと一致）"""
        data = [f"Tx {i}" for i in range(8)]
        left, right = mt.merkle_root(data[:4]), mt.merkle_root(data[4:])
        self.assertEqual(mt.merkle_root(data), mt.parent_hash(left, right))
        self.assertEqual([len(level) for level in mt.build_tree(data)], [8, 4, 2, 1])

    def test_deterministic(self):
        """6. 同じデータから同じ Root"""
        data = ["Tx A", "Tx B", "Tx C", "Tx D"]
        self.assertEqual(mt.merkle_root(data), mt.merkle_root(list(data)))
        self.assertEqual(mt.merkle_root(["X"]), mt.leaf_hash("X"))     # N = 1 なら葉がそのまま Root

    def test_root_changes(self):
        """7. どのデータを変えても、順序を変えても Root が変化する"""
        data = [f"Tx {i}" for i in range(8)]
        root = mt.merkle_root(data)
        for i in range(8):
            changed = list(data)
            changed[i] = changed[i] + "!"
            self.assertNotEqual(mt.merkle_root(changed), root)
        swapped = list(data)
        swapped[0], swapped[1] = swapped[1], swapped[0]
        self.assertNotEqual(mt.merkle_root(swapped), root)

    def test_invalid_input(self):
        """8. 不正な入力は例外になる（黙って受け入れない）"""
        for bad in [[], ["A", "B", "C"], ["A"] * 6]:          # 0件・2のべき乗でない件数
            with self.assertRaises(ValueError):
                mt.build_tree(bad)
        with self.assertRaises(TypeError):
            mt.build_tree(("A", "B"))                           # リストでない
        with self.assertRaises(TypeError):
            mt.build_tree(["A", 1])                             # str / bytes でないデータ
        with self.assertRaises(ValueError):
            mt.parent_hash(b"short", mt.leaf_hash("A"))         # 32 バイトでない


class TestMerkleProof(unittest.TestCase):
    """学生が実装したら実行されるテスト（未実装の間はスキップ）"""

    DATA = [f"Tx {i}" for i in range(8)]

    def setUp(self):
        self.tree = mt.build_tree(self.DATA)
        self.root = self.tree[-1][0]
        try:
            mt.generate_proof(self.tree, 0)
        except NotImplementedError:
            self.skipTest("generate_proof は未実装")

    def run_verify(self, data, proof, root):
        try:
            return mt.verify_proof(data, proof, root)
        except NotImplementedError:
            self.skipTest("verify_proof は未実装")

    def test_valid_proofs(self):
        """すべての位置のデータについて、正しい Proof が受理される"""
        for i, data in enumerate(self.DATA):
            proof = mt.generate_proof(self.tree, i)        # Proof の形はチームで設計してよい
            self.assertTrue(self.run_verify(data, proof, self.root))

    def test_tampered_data_rejected(self):
        """改ざんしたデータや、別の位置の Proof は拒否される"""
        proof = mt.generate_proof(self.tree, 2)
        self.assertFalse(self.run_verify("Tx 2 (changed)", proof, self.root))
        self.assertFalse(self.run_verify("Tx 3", proof, self.root))


if __name__ == "__main__":
    unittest.main()
