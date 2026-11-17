# C4：簡易ブロックチェーンのテスト

import copy
import unittest

import blockchain

DATA = ["Alice -> Bob : 10", "Bob -> Carol : 4", "Carol -> Dave : 2"]


class TestBlockchain(unittest.TestCase):

    def setUp(self):
        self.chain = blockchain.create_chain(DATA)

    def test_genesis_block(self):
        """1. Genesis Block を正しく生成できる"""
        genesis = blockchain.create_genesis_block()
        self.assertEqual(genesis["index"], 0)
        self.assertEqual(genesis["data"], blockchain.GENESIS_DATA)
        self.assertEqual(genesis["previous_hash"], "0" * 64)
        self.assertEqual(len(genesis["hash"]), 64)
        self.assertTrue(blockchain.is_valid_chain([genesis]))

    def test_add_block(self):
        """2. ブロックを追加できる"""
        chain = [blockchain.create_genesis_block()]
        block = blockchain.add_block(chain, "Tx X")
        self.assertEqual(len(chain), 2)
        self.assertIs(chain[-1], block)
        self.assertEqual(block["index"], 1)
        self.assertEqual(block["data"], "Tx X")
        self.assertEqual(len(self.chain), 4)

    def test_previous_hash_links(self):
        """3. previous_hash が直前のブロックの hash と一致する"""
        for i in range(1, len(self.chain)):
            self.assertEqual(self.chain[i]["previous_hash"], self.chain[i - 1]["hash"])

    def test_valid_chain(self):
        """4. 正常なチェーンを検証できる"""
        self.assertTrue(blockchain.is_valid_chain(self.chain))
        self.assertEqual(blockchain.find_problems(self.chain), [])

    def test_detect_data_tampering(self):
        """5. データの改ざんを検出できる（改ざんしたブロックの hash 不一致）"""
        tampered = blockchain.tamper_data(self.chain, 2, "Bob -> Carol : 400")
        self.assertFalse(blockchain.is_valid_chain(tampered))
        positions = [i for i, _ in blockchain.find_problems(tampered)]
        self.assertEqual(positions, [2])

    def test_detect_data_tampering_with_rehash(self):
        """改ざんしたブロックの hash だけを計算し直すと、次のブロックとのつながりで検出される"""
        tampered = blockchain.tamper_data(self.chain, 1, "Alice -> Bob : 1000")
        block = tampered[1]
        block["hash"] = blockchain.compute_hash(block["index"], block["data"], block["previous_hash"])
        positions = [i for i, _ in blockchain.find_problems(tampered)]
        self.assertEqual(positions, [2])

    def test_detect_previous_hash_tampering(self):
        """6. previous_hash の改ざんを検出できる"""
        tampered = copy.deepcopy(self.chain)
        tampered[2]["previous_hash"] = "f" * 64
        self.assertFalse(blockchain.is_valid_chain(tampered))
        messages = [m for _, m in blockchain.find_problems(tampered)]
        self.assertTrue(any("previous_hash" in m for m in messages))

    def test_detect_index_mismatch(self):
        """7. index の不整合を検出できる（ブロックの入れ替え・欠落）"""
        swapped = copy.deepcopy(self.chain)
        swapped[1], swapped[2] = swapped[2], swapped[1]
        self.assertFalse(blockchain.is_valid_chain(swapped))
        missing = copy.deepcopy(self.chain)
        del missing[1]
        self.assertFalse(blockchain.is_valid_chain(missing))
        renumbered = copy.deepcopy(self.chain)
        renumbered[3]["index"] = 7
        self.assertTrue(any("index" in m for _, m in blockchain.find_problems(renumbered)))

    def test_bad_genesis_and_empty_chain(self):
        """Genesis Block の形式違いと、空のチェーンを検出する"""
        bad = copy.deepcopy(self.chain)
        bad[0] = blockchain.make_block(0, "Genesis Block", "1" * 64)
        self.assertFalse(blockchain.is_valid_chain(bad))
        self.assertFalse(blockchain.is_valid_chain([]))

    def test_deterministic_hash(self):
        """8. 同じ入力から同じハッシュ値を生成できる（入力が少しでも違えば別の値）"""
        h1 = blockchain.compute_hash(1, "Tx", "0" * 64)
        h2 = blockchain.compute_hash(1, "Tx", "0" * 64)
        self.assertEqual(h1, h2)
        self.assertNotEqual(h1, blockchain.compute_hash(1, "Tx ", "0" * 64))
        self.assertNotEqual(h1, blockchain.compute_hash(2, "Tx", "0" * 64))
        self.assertEqual(blockchain.create_chain(DATA), blockchain.create_chain(DATA))
        # 単純な文字列連結では区別できない組合せも、別のハッシュ値になる
        self.assertNotEqual(blockchain.compute_hash(1, "23", "x"), blockchain.compute_hash(12, "3", "x"))

    def test_original_unchanged(self):
        """9. 元のチェーンを変更せずに改ざん実験できる"""
        backup = copy.deepcopy(self.chain)
        blockchain.tamper_data(self.chain, 1, "changed")
        self.assertEqual(self.chain, backup)
        self.assertTrue(blockchain.is_valid_chain(self.chain))


if __name__ == "__main__":
    unittest.main()
