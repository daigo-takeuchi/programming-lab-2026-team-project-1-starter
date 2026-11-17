import itertools
import unittest

from tests import _helpers  # noqa: F401
import agents as ag
import game_theory as gt
import simulation as sim
import network_model as nm
import cooperation_policies as cp
import evaluation as ev


class TestCooperationPolicies(unittest.TestCase):
    def setUp(self):
        self.cs = ag.load_countries()
        self.p = sim.load_parameters()
        self.m = gt.load_payoff_matrix()
        self.edges = nm.make_network("ring", [c["id"] for c in self.cs])
        self.ev = cp.PolicyEvaluator(self.cs, self.edges, self.p, self.m, runs=5, years=10)

    def test_budget(self):
        for bad in (-1, 6, 1.5):
            with self.assertRaises(ValueError):
                cp.exhaustive(self.ev, self.edges, bad)
        r = cp.greedy(self.ev, self.edges, 2)
        self.assertEqual(len(r["selected"]), 2)
        with self.assertRaises(ValueError):
            self.ev([("A", "Z")])

    def test_combinations(self):
        items = list("abcde")
        for k in range(0, 6):
            self.assertEqual(cp.combinations(items, k), list(itertools.combinations(items, k)))
        self.assertEqual(cp.combinations(items, 6), [])

    def test_exhaustive(self):
        r = cp.exhaustive(self.ev, self.edges, 2)
        best = max(self.ev(c) for c in itertools.combinations(self.edges, 2))
        self.assertAlmostEqual(r["objective"], best)
        self.assertEqual(len(r["all"]), 10)

    def test_greedy_and_upper_bound(self):
        for k in (1, 2, 3):
            ex = cp.exhaustive(self.ev, self.edges, k)
            gr = cp.greedy(self.ev, self.edges, k)
            self.assertGreaterEqual(ex["objective"] + 1e-12, gr["objective"])     # 全探索 ≥ Greedy
            self.assertIn(gr["selected"], [tuple(sorted(c)) for c, _v in ex["all"]])   # 同じ探索空間

    def test_same_space_and_counts(self):
        r = cp.compare(self.cs, self.edges, self.p, self.m, 2, runs=5, years=10)
        self.assertEqual(r["exhaustive"]["evaluations"], 10)                      # C(5, 2)
        self.assertEqual(r["greedy"]["evaluations"], 5 + 4)
        self.assertGreaterEqual(r["greedy"]["gap"], -1e-12)
        self.assertEqual(r["exhaustive"]["gap"], 0)
        self.assertGreater(r["exhaustive"]["runtime_s"], 0)

    def test_deterministic(self):
        a = self.ev((("A", "B"),))
        b = self.ev((("A", "B"),))
        self.assertEqual(a, b)
        self.assertEqual(self.ev((("A", "B"), ("B", "C"))), self.ev((("B", "C"), ("A", "B"))))   # 順序によらない

    def test_objectives_and_improvement(self):
        s = {"tension_rate": 0.2, "conflict_rate": 0.1, "cooperation_rate": 0.6}
        self.assertAlmostEqual(cp.objective_from_summary(s, "stability"), 0.7)
        self.assertAlmostEqual(cp.objective_from_summary(s, "low_conflict"), 0.9)
        with self.assertRaises(ValueError):
            cp.objective_from_summary(s, "power")
        imp = ev.policy_improvement({"cooperation_rate": 0.5, "tension_rate": 0.3, "conflict_rate": 0.2, "stability": 0.5},
                                    {"cooperation_rate": 0.6, "tension_rate": 0.2, "conflict_rate": 0.1, "stability": 0.7})
        self.assertAlmostEqual(imp["stability"], 0.2)
        with self.assertRaises(ValueError):
            cp.PolicyEvaluator(self.cs, self.edges, self.p, self.m, policy="sanctions")


if __name__ == "__main__":
    unittest.main()
