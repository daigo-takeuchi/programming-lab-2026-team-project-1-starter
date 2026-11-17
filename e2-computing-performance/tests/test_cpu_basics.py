# E2：cpu_basics.py と benchmark_utils.py のテスト（標準ライブラリのみ）

import unittest

import cpu_basics as cb
from benchmark_utils import format_seconds, format_table, measure


class TestElementwise(unittest.TestCase):
    def test_values(self):
        self.assertEqual(cb.elementwise([1, 2, 3], [4, 5, 6], [7, 8, 9]), [11, 18, 27])

    def test_empty(self):
        self.assertEqual(cb.elementwise([], [], []), [])

    def test_length_mismatch(self):
        with self.assertRaises(ValueError):
            cb.elementwise([1, 2], [1], [1, 2])


class TestTotal(unittest.TestCase):
    def test_values(self):
        self.assertEqual(cb.total(list(range(1, 101))), 5050)

    def test_empty_is_zero(self):
        self.assertEqual(cb.total([]), 0)

    def test_float(self):
        self.assertAlmostEqual(cb.total([0.1] * 10), 1.0, places=12)


class TestMatmul(unittest.TestCase):
    def test_square(self):
        self.assertEqual(cb.matmul([[1, 2], [3, 4]], [[5, 6], [7, 8]]), [[19, 22], [43, 50]])

    def test_rectangular(self):
        # (2×3) × (3×1) = (2×1)
        self.assertEqual(cb.matmul([[1, 0, 2], [0, 1, 0]], [[1], [2], [3]]), [[7], [2]])

    def test_identity(self):
        A = cb.make_matrix(4, 4, seed=1)
        eye = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]
        self.assertEqual(cb.matmul(A, eye), A)

    def test_shape_mismatch(self):
        with self.assertRaises(ValueError):
            cb.matmul([[1, 2]], [[1, 2]])        # (1×2) × (1×2) は計算できない

    def test_empty(self):
        with self.assertRaises(ValueError):
            cb.matmul([], [[1]])

    def test_ragged(self):
        with self.assertRaises(ValueError):
            cb.matmul([[1, 2]], [[1, 2], [3]])


class TestConditional(unittest.TestCase):
    def test_values(self):
        self.assertEqual(cb.conditional_square([-2.0, 0.0, 1.5, 3.0]), [0.0, 0.0, 2.25, 9.0])

    def test_empty(self):
        self.assertEqual(cb.conditional_square([]), [])


class TestDataAndCounts(unittest.TestCase):
    def test_seed_reproducible(self):
        self.assertEqual(cb.make_vector(5, seed=3), cb.make_vector(5, seed=3))
        self.assertNotEqual(cb.make_vector(5, seed=3), cb.make_vector(5, seed=4))

    def test_negative_size(self):
        with self.assertRaises(ValueError):
            cb.make_vector(-1)

    def test_operation_counts(self):
        self.assertEqual(cb.operation_counts("matmul", 10)["multiplications"], 1000)
        self.assertEqual(cb.operation_counts("total", 7)["additions"], 7)
        with self.assertRaises(ValueError):
            cb.operation_counts("unknown", 1)


class TestBenchmarkUtils(unittest.TestCase):
    def test_measure(self):
        r = measure(lambda: sum(range(100)), repeats=5, warmup=2)
        self.assertEqual(len(r["times"]), 5)
        self.assertLessEqual(r["min"], r["median"])
        self.assertGreaterEqual(r["stdev"], 0)

    def test_measure_setup_is_passed_and_excluded(self):
        seen = []
        r = measure(lambda x: seen.append(x), repeats=3, warmup=1, setup=lambda: "data")
        self.assertEqual(seen, ["data"] * 4)
        self.assertIsNotNone(r["setup_median"])

    def test_measure_sync_called(self):
        calls = []
        measure(lambda: 1, repeats=2, warmup=0, sync=calls.append)
        self.assertEqual(calls, [1, 1])

    def test_measure_invalid(self):
        with self.assertRaises(ValueError):
            measure(lambda: None, repeats=0)

    def test_format(self):
        self.assertEqual(format_seconds(0.0015), "1.5 ms")
        self.assertEqual(format_seconds(None), "-")
        table = format_table([{"n": 10, "time_s": 2e-6}], [("n", "n"), ("time_s", "time")])
        self.assertIn("2 µs", table)


if __name__ == "__main__":
    unittest.main()
