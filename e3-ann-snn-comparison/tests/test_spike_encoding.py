# E3：spike_encoding.py のテスト

import unittest

from spike_encoding import (
    format_order, has_simultaneous_spikes, num_orders, quantize, spike_counts, spike_order,
)


class TestSpikeEncoding(unittest.TestCase):
    def test_spike_order(self):
        self.assertEqual(spike_order([0.3, 0.1, 0.4, 0.2]), [1, 3, 0, 2])
        self.assertEqual(format_order([1, 3, 0, 2]), "Neuron 1 → Neuron 3 → Neuron 0 → Neuron 2")

    def test_input_not_modified(self):
        lat = [0.3, 0.1, 0.4, 0.2]
        spike_order(lat)
        self.assertEqual(lat, [0.3, 0.1, 0.4, 0.2])

    def test_same_counts_different_order(self):
        a, b = [0.1, 0.2, 0.3, 0.4], [0.4, 0.3, 0.2, 0.1]
        self.assertEqual(spike_counts(a, 1.0), spike_counts(b, 1.0))
        self.assertNotEqual(spike_order(a), spike_order(b))

    def test_spike_counts_window(self):
        self.assertEqual(spike_counts([0.1, 1.5, 0.9], 1.0), [1, 0, 1])

    def test_factorial(self):
        expected = {3: 6, 4: 24, 5: 120, 6: 720, 10: 3628800}
        for n, value in expected.items():
            self.assertEqual(num_orders(n), value)

    def test_simultaneous_spikes(self):
        # 規則：発火時刻が等しいときは番号の小さい方が先
        lat = [0.2, 0.1, 0.2, 0.1]
        self.assertTrue(has_simultaneous_spikes(lat))
        self.assertEqual(spike_order(lat), [1, 3, 0, 2])
        self.assertFalse(has_simultaneous_spikes([0.1, 0.2]))

    def test_quantize(self):
        q = quantize([0.12, 0.14, 0.31], 0.1)
        self.assertEqual([round(v, 10) for v in q], [0.1, 0.1, 0.3])
        self.assertTrue(has_simultaneous_spikes(q))
        with self.assertRaises(ValueError):
            quantize([0.1], 0)


if __name__ == "__main__":
    unittest.main()
