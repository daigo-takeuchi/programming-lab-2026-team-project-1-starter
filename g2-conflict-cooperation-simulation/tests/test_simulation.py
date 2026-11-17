import unittest

from tests import _helpers  # noqa: F401
import agents as ag
import game_theory as gt
import simulation as sim
import network_model as nm
import evaluation as ev


class TestSimulation(unittest.TestCase):
    def setUp(self):
        self.cs = ag.load_countries()
        self.p = sim.load_parameters()
        self.m = gt.load_payoff_matrix()
        self.edges = nm.make_network("ring", [c["id"] for c in self.cs])

    def test_horizons(self):
        for years in sim.HORIZONS:
            out = sim.simulate(self.cs, self.edges, self.p, self.m, years=years)
            self.assertEqual(len(out["records"]), years + 1)
            self.assertEqual(out["records"][-1]["year"], years)

    def test_record_consistency(self):
        out = sim.simulate(self.cs, self.edges, self.p, self.m, years=10)
        for r in out["records"][1:]:
            self.assertEqual(set(r["actions"]), set(self.edges))
            self.assertEqual(set(r["states"]), set(self.edges))
            self.assertAlmostEqual(r["cooperation_state_rate"] + r["tension_rate"] + r["conflict_rate"]
                                   + sum(s == "Neutral" for s in r["states"].values()) / len(self.edges), 1.0)
            for e, (a, b) in r["actions"].items():
                self.assertEqual(r["payoffs"][e], gt.payoffs(self.m, a, b))
            self.assertTrue(all(0 <= t <= 1 for t in r["trust"].values()))
        total = sum(sum(p) for r in out["records"][1:] for p in r["payoffs"].values())
        self.assertAlmostEqual(total, sum(out["payoff"].values()))                    # 累積利得と一致

    def test_reproducible(self):
        a = sim.simulate(self.cs, self.edges, self.p, self.m, years=20, seed=5, run=3)
        b = sim.simulate(self.cs, self.edges, self.p, self.m, years=20, seed=5, run=3)
        self.assertEqual(a, b)
        m1 = sim.monte_carlo(self.cs, self.edges, self.p, self.m, runs=10, years=10, seed=1)
        m2 = sim.monte_carlo(self.cs, self.edges, self.p, self.m, runs=10, years=10, seed=1)
        self.assertEqual(m1["summary"], m2["summary"])
        m3 = sim.monte_carlo(self.cs, self.edges, self.p, self.m, runs=10, years=10, seed=2)
        self.assertNotEqual(m1["summary"], m3["summary"])

    def test_monte_carlo(self):
        mc = sim.monte_carlo(self.cs, self.edges, self.p, self.m, runs=20, years=10)
        self.assertEqual(len(mc["runs"]), 20)
        self.assertEqual(len(mc["yearly"]), 10)
        s = mc["summary"]
        self.assertTrue(0 <= s["cooperation_rate"] <= 1)
        self.assertGreaterEqual(s["cooperation_rate_sd"], 0)
        avg = sum(r["cooperation_rate"] for r in mc["runs"]) / 20
        self.assertAlmostEqual(s["cooperation_rate"], avg)
        with self.assertRaises(ValueError):
            sim.monte_carlo(self.cs, self.edges, self.p, self.m, runs=0)

    def test_pair_and_policies(self):
        out = sim.simulate_pair(self.cs[0], self.cs[1], self.p, self.m, years=5)
        self.assertEqual(out["edges"], [("A", "B")])
        all_coop = ag.with_strategy(self.cs, "always_cooperate")
        p0 = sim.with_changes(self.p, action_noise=0.0)
        r = sim.simulate(all_coop, self.edges, p0, self.m, years=5)
        self.assertEqual(ev.cooperation_rate(r["records"]), 1.0)
        sup = sim.simulate(self.cs, self.edges, self.p, self.m, years=1, supported=[("A", "B")], policy="trust_building")
        base = sim.simulate(self.cs, self.edges, self.p, self.m, years=1)
        self.assertGreater(sup["records"][0]["trust"][("A", "B")], base["records"][0]["trust"][("A", "B")])
        with self.assertRaises(ValueError):
            sim.simulate(self.cs, self.edges, self.p, self.m, years=1, supported=[("A", "B")], policy="unknown")

    def test_common_random_numbers(self):
        # 政策は乱数の使い方を変えない → 行動の乱数は同じで、支援なしと支援ありで 1 年目の行動は同じ
        a = sim.simulate(self.cs, self.edges, self.p, self.m, years=1)
        b = sim.simulate(self.cs, self.edges, self.p, self.m, years=1, supported=[("A", "B")], policy="dialogue")
        self.assertEqual(a["records"][1]["actions"], b["records"][1]["actions"])

    def test_spillover(self):
        nb = sim.edge_neighbors(self.edges)
        self.assertEqual(len(nb[("A", "B")]), 2)                                       # リング：両隣
        states = {e: "Cooperation" for e in self.edges}
        self.assertEqual(sim.neighbor_spillover(states, nb[("A", "B")]), 1.0)
        states = {e: "Conflict" for e in self.edges}
        self.assertEqual(sim.neighbor_spillover(states, nb[("A", "B")]), -1.0)
        self.assertEqual(sim.neighbor_spillover(states, []), 0.0)

    def test_with_changes(self):
        p = sim.with_changes(self.p, **{"transition.dialogue_effect": 0.0, "action_noise": 0.1})
        self.assertEqual(p["transition"]["dialogue_effect"], 0.0)
        self.assertEqual(self.p["transition"]["dialogue_effect"], 0.15)
        with self.assertRaises(KeyError):
            sim.with_changes(self.p, **{"transition.unknown": 1})


if __name__ == "__main__":
    unittest.main()
