# C4：計算量の理論値のテスト

import unittest

import complexity
import merkle_tree


class TestComplexity(unittest.TestCase):

    def test_height(self):
        """1・2・3. N = 2, 4, 8 の木の高さ（実際に作った木の高さとも一致する）"""
        for n, height in [(1, 0), (2, 1), (4, 2), (8, 3), (1024, 10)]:
            self.assertEqual(complexity.tree_height(n), height)
        for n in [2, 4, 8]:
            tree = merkle_tree.build_tree([str(i) for i in range(n)])
            self.assertEqual(merkle_tree.tree_height(tree), complexity.tree_height(n))

    def test_node_counts(self):
        """4. 完全二分木のノード数：葉 N、内部 N − 1、合計 2N − 1（実際の木とも一致する）"""
        for n in [1, 2, 4, 8, 16]:
            self.assertEqual(complexity.leaf_count(n), n)
            self.assertEqual(complexity.internal_node_count(n), n - 1)
            self.assertEqual(complexity.total_node_count(n), 2 * n - 1)
            tree = merkle_tree.build_tree([str(i) for i in range(n)])
            self.assertEqual(sum(len(level) for level in tree), complexity.total_node_count(n))

    def test_proof_length(self):
        """5. Proof に必要な兄弟ハッシュ数 = log2(N)、検証のハッシュ演算 = 1 + log2(N)"""
        self.assertEqual(complexity.proof_length(8), 3)
        self.assertEqual(complexity.proof_length(2 ** 20), 20)
        self.assertEqual(complexity.proof_size_bytes(8), 96)
        self.assertEqual(complexity.hashes_proof_verification(8), 4)
        self.assertEqual(complexity.hashes_full_rebuild(8), 15)
        self.assertEqual(complexity.hashes_leaf_update(8), 4)

    def test_chain(self):
        """ハッシュチェーンの検証・再計算の回数"""
        self.assertEqual(complexity.hashes_chain_validation(5), 5)
        self.assertEqual(complexity.hashes_chain_recompute(5, 0), 5)
        self.assertEqual(complexity.hashes_chain_recompute(5, 4), 1)
        with self.assertRaises(ValueError):
            complexity.hashes_chain_recompute(5, 5)

    def test_invalid_n(self):
        """6. 不正な N は ValueError"""
        for bad in [0, -4, 3, 6, 12, 2.0, "8", None, True]:
            with self.subTest(n=bad):
                with self.assertRaises(ValueError):
                    complexity.tree_height(bad)
        with self.assertRaises(ValueError):
            complexity.hashes_chain_validation(0)


if __name__ == "__main__":
    unittest.main()
