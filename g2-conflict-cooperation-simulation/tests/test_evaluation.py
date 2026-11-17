import unittest

from tests import _helpers  # noqa: F401
import evaluation as ev


def rec(year, actions, states):
    return {"year": year, "actions": actions, "states": states, "trust": {}, "mean_trust": 0.5}


class TestEvaluation(unittest.TestCase):
    def setUp(self):
        e1, e2 = ("A", "B"), ("B", "C")
        self.records = [rec(0, {}, {e1: "Neutral", e2: "Neutral"}),
                        rec(1, {e1: ("C", "C"), e2: ("C", "N")}, {e1: "Cooperation", e2: "Tension"}),
                        rec(2, {e1: ("C", "C"), e2: ("N", "N")}, {e1: "Cooperation", e2: "Conflict"}),
                        rec(3, {e1: ("N", "C"), e2: ("N", "N")}, {e1: "Neutral", e2: "Tension"})]

    def test_rates(self):
        self.assertAlmostEqual(ev.cooperation_rate(self.records), 6 / 12)
        self.assertAlmostEqual(ev.mutual_cooperation_rate(self.records), 2 / 6)
        self.assertAlmostEqual(ev.tension_rate(self.records), (0.5 + 0 + 0.5) / 3)
        self.assertAlmostEqual(ev.conflict_rate(self.records), (0 + 0.5 + 0) / 3)
        self.assertIsNone(ev.cooperation_rate(self.records[:1]))

    def test_durations(self):
        self.assertEqual(ev.run_lengths(list("CCNCCC"), "C"), [2, 3])
        self.assertEqual(ev.run_lengths([], "C"), [])
        self.assertEqual(ev.state_durations(self.records, "Cooperation"), [2])
        self.assertEqual(ev.mean_duration(self.records, "Tension"), 1.0)
        self.assertIsNone(ev.mean_duration(self.records, "Missing"))

    def test_payoff_and_summary(self):
        self.assertAlmostEqual(ev.average_payoff({"payoff": {"A": 30, "B": 10}, "years": 10}), 2.0)
        self.assertIsNone(ev.average_payoff({"payoff": {}, "years": 10}))
        s = ev.summarize_run({"records": self.records, "payoff": {"A": 1, "B": 1, "C": 1}, "years": 3})
        self.assertAlmostEqual(s["stability"], 1 - s["tension_rate"] - s["conflict_rate"])
        self.assertTrue(s["ever_conflict"])

    def test_connectivity_and_time(self):
        met = ev.network_connectivity(["A", "B", "C"], [("A", "B"), ("B", "C")],
                                      {("A", "B"): "Cooperation", ("B", "C"): "Tension"})
        self.assertEqual(met["cooperation_edge_ratio"], 0.5)
        r, t = ev.measure_time(sum, [1, 2])
        self.assertEqual(r, 3)
        self.assertGreaterEqual(t, 0)


if __name__ == "__main__":
    unittest.main()
