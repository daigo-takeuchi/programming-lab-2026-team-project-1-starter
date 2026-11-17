# E3：lif_snn.py のテスト

import math
import unittest

from lif_snn import first_spike_latency, firing_rate, latency_encode, simulate_lif


class TestLIF(unittest.TestCase):
    def test_membrane_update(self):
        # V[1] = 0 + 1/10 * (-(0 - 0) + 1 * 0.5) = 0.05
        r = simulate_lif([0.5, 0.5], dt=1.0, tau=10.0)
        self.assertAlmostEqual(r["v"][0], 0.05)
        self.assertAlmostEqual(r["v"][1], 0.05 + 0.1 * (-0.05 + 0.5))
        self.assertEqual(r["currents"], [0.5, 0.5])
        self.assertEqual(r["times"], [1.0, 2.0])

    def test_leak_without_input(self):
        r = simulate_lif([0.0] * 3, v_rest=0.0)
        self.assertEqual(r["v"], [0.0, 0.0, 0.0])
        self.assertEqual(r["spike_count"], 0)

    def test_spike_when_threshold_reached(self):
        r = simulate_lif([2.0] * 20, dt=1.0, tau=10.0, v_th=1.0)
        self.assertTrue(any(r["spikes"]))
        self.assertGreater(r["spike_count"], 0)

    def test_no_spike_below_threshold(self):
        # R*I = 0.9 < v_th なので、V は 0.9 に近づくだけで発火しない
        r = simulate_lif([0.9] * 200)
        self.assertEqual(r["spike_count"], 0)

    def test_reset_after_spike(self):
        r = simulate_lif([2.0] * 20, v_reset=0.0)
        for v, spiked in zip(r["v"], r["spikes"]):
            if spiked:
                self.assertEqual(v, 0.0)
            self.assertLess(v, 1.0)

    def test_spike_times(self):
        # 一定入力 I = 2：V[k] = 2(1 - 0.9^k) が 1 以上になる最初の k は 0.9^k <= 0.5 → k = 7
        k = math.ceil(math.log(0.5) / math.log(0.9))
        r = simulate_lif([2.0] * 20, dt=1.0, tau=10.0, v_th=1.0)
        self.assertEqual(k, 7)
        self.assertEqual(r["spike_times"], [7.0, 14.0])
        self.assertEqual(r["spike_count"], 2)
        self.assertEqual([t for t, s in zip(r["times"], r["spikes"]) if s], r["spike_times"])
        self.assertAlmostEqual(firing_rate(r), 2 / 20)

    def test_stronger_input_fires_earlier(self):
        latencies = latency_encode([1.2, 1.5, 2.0, 3.0])
        self.assertEqual(latencies, sorted(latencies, reverse=True))
        self.assertIsNone(first_spike_latency(0.5))

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            simulate_lif([1.0], tau=0)
        with self.assertRaises(ValueError):
            simulate_lif([1.0], v_th=0.0, v_reset=0.0)


if __name__ == "__main__":
    unittest.main()
