# E3：spike_lut.py のテスト

import unittest

from spike_lut import (
    SpikeLUT, bits_to_index, compare_pairs, index_to_bits, lut_forward,
    lut_operation_counts, make_random_tables, select_row,
)

ANCHORS = [(0, 1), (1, 2), (2, 3)]
ROWS = [[0.1, 0.2], [0.3, 0.1], [0.0, 0.4], [0.5, 0.2],
        [0.2, 0.3], [0.4, 0.4], [0.1, 0.5], [0.6, 0.1]]


class TestComparisonAndIndex(unittest.TestCase):
    def test_pairwise_comparison(self):
        lat = [0.3, 0.1, 0.4, 0.2]
        self.assertEqual(compare_pairs(lat, ANCHORS), [1, 0, 1])
        self.assertEqual(compare_pairs(lat, [(1, 0)]), [0])

    def test_tie_is_zero(self):
        self.assertEqual(compare_pairs([0.2, 0.2], [(0, 1), (1, 0)]), [0, 0])

    def test_bits(self):
        self.assertEqual(compare_pairs([0.1, 0.2, 0.3, 0.4], ANCHORS), [0, 0, 0])
        self.assertEqual(compare_pairs([0.4, 0.3, 0.2, 0.1], ANCHORS), [1, 1, 1])

    def test_binary_index(self):
        self.assertEqual(bits_to_index([0, 1, 1]), 3)   # 1つ目の比較が最上位ビット
        self.assertEqual(bits_to_index([1, 0, 0]), 4)
        self.assertEqual(bits_to_index([0, 0, 0]), 0)
        self.assertEqual(bits_to_index([1, 1, 1]), 7)
        for i in range(16):
            self.assertEqual(bits_to_index(index_to_bits(i, 4)), i)
        with self.assertRaises(ValueError):
            bits_to_index([0, 2])


class TestLUT(unittest.TestCase):
    def setUp(self):
        self.table = SpikeLUT(4, ANCHORS, ROWS)

    def test_select_row(self):
        self.assertEqual(select_row(ROWS, 3), [0.5, 0.2])
        r = lut_forward([0.3, 0.1, 0.4, 0.2], [self.table])
        self.assertEqual(r["bits"], [[1, 0, 1]])
        self.assertEqual(r["indices"], [5])
        self.assertEqual(r["output"], [0.4, 0.4])

    def test_invalid_index(self):
        for bad in [-1, 8, 100, 1.0, True, "3"]:
            with self.assertRaises(IndexError):
                select_row(ROWS, bad)

    def test_sum_of_multiple_luts(self):
        t2 = SpikeLUT(4, [(3, 0)], [[1.0, 0.0], [0.0, 1.0]])
        t3 = SpikeLUT(4, [(2, 1), (0, 3)], [[0.0, 0.0], [0.0, 0.0], [10.0, 20.0], [30.0, 40.0]])
        lat = [0.3, 0.1, 0.4, 0.2]
        r = lut_forward(lat, [self.table, t2, t3])
        # LUT0: index 5 → [0.4, 0.4]、LUT1: x3>x0 は偽 → index 0 → [1, 0]、LUT2: bits [1, 1] → index 3 → [30, 40]
        self.assertEqual(r["indices"], [5, 0, 3])
        self.assertEqual(r["output"], [0.4 + 1.0 + 30.0, 0.4 + 0.0 + 40.0])

    def test_input_dimension_mismatch(self):
        with self.assertRaises(ValueError):
            lut_forward([0.1, 0.2, 0.3], [self.table])
        with self.assertRaises(ValueError):
            lut_forward([0.1, 0.2, 0.3, 0.4, 0.5], [self.table])

    def test_invalid_tables(self):
        with self.assertRaises(ValueError):
            SpikeLUT(4, [(0, 4)], [[0.0], [0.0]])        # 範囲外の anchor
        with self.assertRaises(ValueError):
            SpikeLUT(4, [(1, 1)], [[0.0], [0.0]])        # 同じニューロンの組
        with self.assertRaises(ValueError):
            SpikeLUT(4, ANCHORS, ROWS[:7])               # 行数が 2^nc でない
        with self.assertRaises(ValueError):
            SpikeLUT(4, [(0, 1)], [[0.0], [0.0, 1.0]])   # 行の長さが不ぞろい
        other = SpikeLUT(4, [(0, 1)], [[0.0], [1.0]])
        with self.assertRaises(ValueError):
            lut_forward([0.1, 0.2, 0.3, 0.4], [self.table, other])   # 出力次元が違う

    def test_reproducible(self):
        lat = [0.25, 0.05, 0.4, 0.3, 0.1]
        t1 = make_random_tables(5, 4, 3, 5, seed=7)
        t2 = make_random_tables(5, 4, 3, 5, seed=7)
        self.assertEqual(lut_forward(lat, t1), lut_forward(lat, t2))
        self.assertEqual(lut_forward(lat, t1), lut_forward(lat, t1))
        for t in t1:
            self.assertEqual(len(t.rows), 8)
            for a, b in t.anchors:
                self.assertNotEqual(a, b)

    def test_operation_counts(self):
        ops = lut_operation_counts(3, 3, 4)
        self.assertEqual(ops["comparisons"], 9)
        self.assertEqual(ops["lut_accesses"], 3)
        self.assertEqual(ops["multiplications"], 0)
        self.assertEqual(ops["parameters"], 3 * 8 * 4)
        self.assertEqual(ops["values_read"], 12)


if __name__ == "__main__":
    unittest.main()
