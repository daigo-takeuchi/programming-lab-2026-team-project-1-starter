import random
import unittest

from tests import _helpers  # noqa: F401
import agents as ag
import game_theory as gt
import simulation as sim


class TestGameTheory(unittest.TestCase):
    def setUp(self):
        self.m = gt.load_payoff_matrix()
        self.p = sim.with_changes(sim.load_parameters(), action_noise=0.0)

    def test_payoff_matrix(self):
        self.assertEqual(gt.payoffs(self.m, "C", "C"), (3, 3))
        self.assertEqual(gt.payoffs(self.m, "C", "N"), (0, 5))
        self.assertEqual(gt.payoffs(self.m, "N", "C"), (5, 0))
        self.assertEqual(gt.payoffs(self.m, "N", "N"), (1, 1))
        self.assertTrue(gt.is_prisoners_dilemma(self.m))
        self.assertEqual(gt.nash_equilibria(self.m), [("N", "N")])
        stag = {"C": {"C": 4, "N": 0}, "N": {"C": 3, "N": 2}}            # 協調にも均衡があるゲーム
        self.assertEqual(gt.nash_equilibria(stag), [("C", "C"), ("N", "N")])
        with self.assertRaises(ValueError):
            gt.validate_payoff_matrix({"C": {"C": 1}})
        with self.assertRaises(ValueError):
            gt.payoffs(self.m, "X", "C")

    def test_strategy_actions(self):
        rng = random.Random(0)
        me = ag.make_country("A")
        self.assertEqual(gt.choose_action("always_cooperate", me, [], ["N"], 0.0, rng, self.p), "C")
        self.assertEqual(gt.choose_action("always_noncooperate", me, [], ["C"], 1.0, rng, self.p), "N")
        self.assertEqual(gt.choose_action("tit_for_tat", me, ["C"], ["N"], 1.0, rng, self.p), "N")
        self.assertEqual(gt.choose_action("tit_for_tat", me, ["N"], ["C"], 0.0, rng, self.p), "C")
        with self.assertRaises(ValueError):
            gt.choose_action("random", me, [], [], 0.5, rng, self.p)

    def test_tit_for_tat_first_move(self):
        me = ag.make_country("A")
        self.assertEqual(gt.choose_action("tit_for_tat", me, [], [], 0.0, random.Random(1), self.p), "C")

    def test_conditional(self):
        me = ag.make_country("A", 0.5, 0.5, 0.5)
        c = self.p["conditional"]
        hi = gt.conditional_probability(me, 1.0, ["C"] * 5, c)
        lo = gt.conditional_probability(me, 0.0, ["N"] * 5, c)
        self.assertGreater(hi, lo)
        self.assertLessEqual(hi, c["max_probability"])                  # 信頼度が高くても必ず協調するとは限らない
        self.assertLess(c["max_probability"], 1.0)
        self.assertGreaterEqual(lo, c["min_probability"])

    def test_repeated_game(self):
        a = ag.make_country("A", strategy="always_cooperate")
        b = ag.make_country("B", strategy="always_noncooperate")
        g = gt.play_repeated(a, b, 10, self.m, self.p)
        self.assertEqual(g["cumulative"], (0, 50))
        self.assertEqual(g["cooperation_rate"], 0.5)
        self.assertEqual(g["mutual_cooperation_rate"], 0.0)
        t1 = ag.make_country("A", strategy="tit_for_tat")
        g2 = gt.play_repeated(t1, b, 5, self.m, self.p)
        self.assertEqual([x for x, _ in g2["actions"]], ["C", "N", "N", "N", "N"])
        self.assertEqual(g2["cumulative"], (0 + 1 * 4, 5 + 1 * 4))
        g3 = gt.play_repeated(t1, ag.make_country("B", strategy="tit_for_tat"), 8, self.m, self.p)
        self.assertEqual(g3["average_payoff"], 3.0)

    def test_noise_and_reproducibility(self):
        p = sim.with_changes(self.p, action_noise=0.2)
        a = ag.make_country("A", strategy="always_cooperate")
        g1 = gt.play_repeated(a, a, 200, self.m, p, seed=4)
        g2 = gt.play_repeated(a, a, 200, self.m, p, seed=4)
        self.assertEqual(g1, g2)
        self.assertLess(g1["cooperation_rate"], 1.0)                    # 誤りで非協調になることがある

    def test_ranking(self):
        ranked = gt.rank({"x": 1.0, "y": 3.0, "z": 3.0})
        self.assertEqual([n for n, _ in ranked], ["y", "z", "x"])


if __name__ == "__main__":
    unittest.main()
