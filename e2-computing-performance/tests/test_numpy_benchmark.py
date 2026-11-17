# E2：numpy_benchmark.py のテスト（NumPy が必要）

import unittest

import numpy as np

import cpu_basics as cb
import numpy_benchmark as nb


class TestSameResults(unittest.TestCase):
    """Python ループと NumPy の結果が、丸め誤差の範囲で一致する"""

    def check(self, task, n, dtype=np.float64):
        py_args, np_args = nb.make_inputs(task, n, seed=1, dtype=dtype)
        py_res = nb.PY_FUNCS[task](*py_args)
        np_res = nb.NP_FUNCS[task](*np_args)
        self.assertTrue(nb.results_match(py_res, np_res, dtype, scale=n), f"{task} n={n} {dtype}")
        return py_res, np_res

    def test_elementwise(self):
        py_res, np_res = self.check("elementwise", 1000)
        self.assertEqual(np_res.shape, (1000,))

    def test_total(self):
        py_res, np_res = self.check("total", 10_000)
        self.assertEqual(np.ndim(np_res), 0)

    def test_matmul(self):
        py_res, np_res = self.check("matmul", 20)
        self.assertEqual(np_res.shape, (20, 20))

    def test_conditional(self):
        py_res, np_res = self.check("conditional", 1000)
        self.assertEqual(np_res.shape, (1000,))
        self.assertTrue((np_res >= 0).all())

    def test_float32(self):
        for task, n in [("elementwise", 1000), ("total", 1000), ("matmul", 16), ("conditional", 1000)]:
            py_res, np_res = self.check(task, n, np.float32)
            self.assertEqual(np.asarray(np_res).dtype, np.float32)

    def test_int64(self):
        a = np.array([1, 2, 3], dtype=np.int64)
        self.assertEqual(nb.np_elementwise(a, a, a).tolist(), cb.elementwise([1, 2, 3], [1, 2, 3], [1, 2, 3]))
        self.assertEqual(nb.np_conditional_square(np.array([-1, 2], dtype=np.int64)).dtype, np.int64)


class TestMatmulValues(unittest.TestCase):
    def test_known(self):
        A = np.array([[1, 2], [3, 4]], dtype=np.float64)
        B = np.array([[5, 6], [7, 8]], dtype=np.float64)
        np.testing.assert_array_equal(nb.np_matmul(A, B), [[19, 22], [43, 50]])

    def test_rectangular_shape(self):
        self.assertEqual(nb.np_matmul(np.ones((2, 3)), np.ones((3, 5))).shape, (2, 5))


class TestRoundingError(unittest.TestCase):
    def test_sum_order_changes_result_slightly(self):
        # 足す順序が違うと、浮動小数点の結果はわずかに変わることがある → 完全一致ではなく allclose で比べる
        x = [0.1] * 10
        self.assertNotEqual(cb.total(x), 1.0)
        self.assertTrue(np.isclose(cb.total(x), 1.0))

    def test_tolerance_depends_on_dtype(self):
        self.assertGreater(nb.tolerance(np.float32)[0], nb.tolerance(np.float64)[0])

    def test_detects_mismatch(self):
        self.assertFalse(nb.results_match([1.0, 2.0], np.array([1.0, 2.1])))


class TestCompare(unittest.TestCase):
    def test_row(self):
        r = nb.compare("elementwise", 100, repeats=2)
        self.assertTrue(r["match"])
        self.assertGreater(r["python_s"], 0)
        self.assertAlmostEqual(r["speedup"], r["python_s"] / r["numpy_s"])
        self.assertEqual(r["dtype"], "float64")

    def test_safety_limit_skips_python(self):
        n = nb.PYTHON_MAX_N["matmul"] + 1
        old = nb.NUMPY_MAX_N["matmul"]
        r = nb.compare("matmul", n, repeats=1)
        self.assertIsNone(r["python_s"])
        self.assertIsNone(r["speedup"])
        self.assertEqual(nb.NUMPY_MAX_N["matmul"], old)

    def test_unknown_task(self):
        with self.assertRaises(ValueError):
            nb.make_inputs("unknown", 10)


if __name__ == "__main__":
    unittest.main()
