# E3：ann.py のテスト

import unittest

from ann import ann_operation_counts, dense_forward, relu, weighted_sum


class TestANN(unittest.TestCase):
    def test_weighted_sum(self):
        x = [1.0, 2.0, 3.0]
        W = [[1.0, 0.0, -1.0], [0.5, 0.5, 0.5]]
        b = [0.0, 0.0]
        self.assertEqual(weighted_sum(x, W, b), [-2.0, 3.0])   # 1-3、0.5+1+1.5

    def test_bias(self):
        x = [1.0, 2.0]
        W = [[0.0, 0.0], [1.0, 1.0]]
        self.assertEqual(weighted_sum(x, W, [0.25, -1.0]), [0.25, 2.0])

    def test_relu(self):
        self.assertEqual(relu(2.5), 2.5)
        self.assertEqual(relu(-0.1), 0.0)
        self.assertEqual(relu(0.0), 0.0)
        x = [1.0, 2.0, 3.0]
        W = [[1.0, 0.0, -1.0], [0.5, 0.5, 0.5]]
        self.assertEqual(dense_forward(x, W, [0.0, 0.0]), [0.0, 3.0])

    def test_sample_values(self):
        y = dense_forward([0.2, 0.5, 0.8], [[0.5, -0.2, 0.1], [-0.3, 0.8, -0.6]], [0.1, 0.05])
        self.assertAlmostEqual(y[0], 0.18)
        self.assertEqual(y[1], 0.0)   # -0.09 → ReLU で 0

    def test_shape_mismatch(self):
        W = [[1.0, 2.0], [3.0, 4.0]]
        with self.assertRaises(ValueError):
            dense_forward([1.0, 2.0, 3.0], W, [0.0, 0.0])   # 入力次元が違う
        with self.assertRaises(ValueError):
            dense_forward([1.0, 2.0], W, [0.0])             # バイアスの長さが違う
        with self.assertRaises(ValueError):
            dense_forward([1.0, 2.0], [[1.0, 2.0], [3.0]], [0.0, 0.0])   # 行の長さが不ぞろい
        with self.assertRaises(ValueError):
            dense_forward([1.0], [], [])

    def test_operation_counts(self):
        ops = ann_operation_counts(3, 2)
        self.assertEqual(ops["multiplications"], 6)
        self.assertEqual(ops["additions"], 6)
        self.assertEqual(ops["parameters"], 8)


if __name__ == "__main__":
    unittest.main()
