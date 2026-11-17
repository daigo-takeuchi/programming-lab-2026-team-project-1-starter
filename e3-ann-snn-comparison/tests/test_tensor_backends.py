# E3：tensor_backends.py のテスト（NumPy・PyTorch・JAX 版が基準実装と一致するか）
#
# NumPy がない環境ではすべてスキップする（既存の Core Research は標準ライブラリだけで動く）。
# PyTorch・JAX はインストールされている場合だけテストする。

import importlib.util
import unittest

HAS_NUMPY = importlib.util.find_spec("numpy") is not None
HAS_TORCH = importlib.util.find_spec("torch") is not None
HAS_JAX = importlib.util.find_spec("jax") is not None

from ann import dense_forward
from benchmark import make_ann
from spike_lut import SpikeLUT, lut_forward, make_random_tables

if HAS_NUMPY:
    import numpy as np
    import tensor_backends as tb

ANCHORS = [(0, 1), (1, 2), (2, 3)]
ROWS = [[0.1, 0.2], [0.3, 0.1], [0.0, 0.4], [0.5, 0.2],
        [0.2, 0.3], [0.4, 0.4], [0.1, 0.5], [0.6, 0.1]]


@unittest.skipUnless(HAS_NUMPY, "NumPy が必要です")
class TestNumpyBackend(unittest.TestCase):
    def setUp(self):
        self.n, self.nt, self.nc, self.m = 8, 5, 4, 6
        self.tables = make_random_tables(self.n, self.nt, self.nc, self.m, seed=1)
        self.anchors, self.rows = tb.tables_to_arrays(self.tables, dtype=np.float64)
        # 同時発火（等しい値）も含めるため、0.1 刻みに丸めた入力を使う
        self.X = np.round(tb.make_batch(64, self.n, seed=2, dtype=np.float64), 1)

    def test_bit_weights_msb_first(self):
        self.assertEqual(tb.bit_weights(3).tolist(), [4, 2, 1])

    def test_single_lut_example(self):
        anchors, rows = tb.tables_to_arrays([SpikeLUT(4, ANCHORS, ROWS)])
        X = np.array([[0.3, 0.1, 0.4, 0.2], [0.1, 0.2, 0.3, 0.4], [0.4, 0.3, 0.2, 0.1]], dtype=np.float32)
        self.assertEqual(tb.numpy_lut_indices(X, anchors)[:, 0].tolist(), [5, 0, 7])
        np.testing.assert_allclose(tb.numpy_lut_forward(X, anchors, rows)[0], [0.4, 0.4], rtol=1e-6)

    def test_lut_matches_reference(self):
        idx = tb.numpy_lut_indices(self.X, self.anchors)
        Y = tb.numpy_lut_forward(self.X, self.anchors, self.rows)
        for i, x in enumerate(self.X.tolist()):
            ref = lut_forward(x, self.tables)
            self.assertEqual(idx[i].tolist(), ref["indices"])
            np.testing.assert_allclose(Y[i], ref["output"], rtol=1e-12)

    def test_ann_matches_reference(self):
        W, b = make_ann(self.n, self.m, seed=3)
        Y = tb.numpy_ann_forward(self.X, np.array(W), np.array(b))
        for i, x in enumerate(self.X.tolist()):
            np.testing.assert_allclose(Y[i], dense_forward(x, W, b), rtol=1e-12, atol=1e-12)

    def test_tables_must_share_shape(self):
        t1 = make_random_tables(4, 1, 2, 3, seed=0)
        t2 = make_random_tables(4, 1, 3, 3, seed=0)
        with self.assertRaises(ValueError):
            tb.tables_to_arrays(t1 + t2)

    def test_time_call(self):
        r = tb.time_call(lambda: sum(range(10)), warmup=1, repeats=5)
        self.assertEqual(len(r["times"]), 5)
        self.assertGreaterEqual(r["median"], 0)


@unittest.skipUnless(HAS_NUMPY and HAS_TORCH, "PyTorch が必要です")
class TestTorchBackend(unittest.TestCase):
    def test_matches_numpy(self):
        import torch
        tables = make_random_tables(8, 4, 3, 5, seed=4)
        anchors, rows = tb.tables_to_arrays(tables)
        X = tb.make_batch(32, 8, seed=5)
        W, b = tb.make_ann_arrays(8, 5, seed=6)
        weights = torch.as_tensor(tb.bit_weights(3), dtype=torch.long)
        Yl = tb.torch_lut_forward(torch.as_tensor(X), torch.as_tensor(anchors).long(),
                                  torch.as_tensor(rows), weights)
        Ya = tb.torch_ann_forward(torch.as_tensor(X), torch.as_tensor(W), torch.as_tensor(b))
        np.testing.assert_allclose(Yl.numpy(), tb.numpy_lut_forward(X, anchors, rows), rtol=1e-5, atol=1e-6)
        np.testing.assert_allclose(Ya.numpy(), tb.numpy_ann_forward(X, W, b), rtol=1e-5, atol=1e-6)


@unittest.skipUnless(HAS_NUMPY and HAS_JAX, "JAX が必要です")
class TestJaxBackend(unittest.TestCase):
    def test_matches_numpy(self):
        import jax
        ann_f, lut_f = tb.jax_functions()
        tables = make_random_tables(8, 4, 3, 5, seed=4)
        anchors, rows = tb.tables_to_arrays(tables)
        X = tb.make_batch(32, 8, seed=5)
        W, b = tb.make_ann_arrays(8, 5, seed=6)
        Yl = jax.jit(lut_f)(X, anchors, rows).block_until_ready()
        Ya = jax.jit(ann_f)(X, W, b).block_until_ready()
        np.testing.assert_allclose(np.asarray(Yl), tb.numpy_lut_forward(X, anchors, rows), rtol=1e-5, atol=1e-6)
        np.testing.assert_allclose(np.asarray(Ya), tb.numpy_ann_forward(X, W, b), rtol=1e-5, atol=1e-6)


if __name__ == "__main__":
    unittest.main()
