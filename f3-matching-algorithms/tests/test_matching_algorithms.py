# F3：matching_algorithms.py のテスト

import itertools
import random
import unittest

import evaluation as ev
import matching_algorithms as ma
import participants as pt
import preferences as pr


def sample():
    g = pt.load_participants()
    s = pr.score_table(g)
    r = pr.build_rankings(g, s)
    return r, [p["id"] for p in g["A"]], [p["id"] for p in g["B"]]


def random_market(n, seed, density=0.7):
    """ランダムな希望順位（受け入れ可能性もランダム）"""
    rng = random.Random(seed)
    a_ids = [f"A{i}" for i in range(n)]
    b_ids = [f"B{i}" for i in range(n)]
    r = {}
    for x, others in [(a, b_ids) for a in a_ids] + [(b, a_ids) for b in b_ids]:
        lst = [o for o in others if rng.random() < density]
        rng.shuffle(lst)
        r[x] = lst
    return r, a_ids, b_ids


class TestBasicConstraints(unittest.TestCase):
    def test_all_algorithms_valid(self):
        r, a_ids, b_ids = sample()
        for name in ma.ALGORITHMS:
            for seed in range(5):
                m = ma.run(name, r, a_ids, b_ids, seed=seed)
                ma.validate_matching(m, r)                                   # 1 人 1 ペア・相互承諾
                self.assertEqual(len(set(m.values())), len(m))
                self.assertTrue(all(pr.mutually_acceptable(r, a, b) for a, b in m.items()))
                self.assertNotIn("A5", m)                                    # 受け入れ可能な相手がいない人は未マッチング

    def test_random_seed_reproducible(self):
        r, a_ids, b_ids = sample()
        self.assertEqual(ma.random_matching(r, a_ids, b_ids, 3), ma.random_matching(r, a_ids, b_ids, 3))
        results = {tuple(sorted(ma.random_matching(r, a_ids, b_ids, s).items())) for s in range(20)}
        self.assertGreater(len(results), 1)                                  # シードで結果が変わる

    def test_random_is_maximal(self):
        r, a_ids, b_ids = random_market(8, 1)
        m = ma.random_matching(r, a_ids, b_ids, 0)
        used_b = set(m.values())
        for a, b in ma.acceptable_pairs(r, a_ids, b_ids):
            self.assertTrue(a in m or b in used_b)                           # これ以上組を足せない


class TestGreedy(unittest.TestCase):
    def test_sample_greedy(self):
        r, a_ids, b_ids = sample()
        self.assertEqual(ma.greedy_matching(r, a_ids, b_ids), {"A1": "B1", "A2": "B2", "A3": "B3", "A4": "B4"})

    def test_order_matters(self):
        r, a_ids, b_ids = sample()
        m = ma.greedy_matching(r, a_ids, b_ids, order=["A3", "A1", "A2", "A4", "A5"])
        self.assertEqual(m["A3"], "B2")                                      # A3 が先なら B2 をとる
        with self.assertRaises(ValueError):
            ma.greedy_matching(r, a_ids, b_ids, order=["A1"])

    def test_greedy_order_seed(self):
        self.assertEqual(ma.greedy_order(["A2", "A1"]), ["A1", "A2"])
        self.assertEqual(ma.greedy_order(list("abcdef"), 5), ma.greedy_order(list("abcdef"), 5))


class TestGaleShapley(unittest.TestCase):
    def test_sample_gs(self):
        r, a_ids, b_ids = sample()
        m, steps = ma.gale_shapley(r, a_ids, b_ids, record=True)
        self.assertEqual(m, {"A1": "B1", "A2": "B3", "A3": "B2", "A4": "B4"})
        self.assertEqual([s["action"] for s in steps], ["accept", "accept", "replace", "accept", "accept"])
        self.assertEqual(steps[2]["rejected"], "A2")
        self.assertNotEqual(m, ma.greedy_matching(r, a_ids, b_ids))          # Greedy と結果が異なるケース

    def test_stable_on_random_markets(self):
        for seed in range(30):
            r, a_ids, b_ids = random_market(7, seed)
            m = ma.gale_shapley(r, a_ids, b_ids)
            ma.validate_matching(m, r)
            self.assertEqual(ev.blocking_pairs(m, r, a_ids, b_ids), [], seed)

    def test_each_proposes_at_most_once(self):
        r, a_ids, b_ids = random_market(7, 3, density=0.9)
        _m, steps = ma.gale_shapley(r, a_ids, b_ids, record=True)
        proposals = [(s["proposer"], s["receiver"]) for s in steps]
        self.assertEqual(len(proposals), len(set(proposals)))
        self.assertLessEqual(len(proposals), sum(len(r[a]) for a in a_ids))

    def test_proposer_optimal_among_stable(self):
        # 小さな市場で、すべての安定マッチングの中で提案側（A）にとって最良であることを全探索で確かめる
        r, a_ids, b_ids = random_market(4, 11, density=1.0)
        gs = ma.gale_shapley(r, a_ids, b_ids)
        idx = pr.rank_index(r)
        for perm in itertools.permutations(b_ids):
            m = dict(zip(a_ids, perm))
            if ev.is_stable(m, r, a_ids, b_ids):
                for a in a_ids:
                    self.assertLessEqual(idx[a][gs[a]], idx[a][m[a]])

    def test_empty_lists(self):
        r = {"A1": [], "A2": ["B1"], "B1": ["A2"], "B2": []}
        for name in ma.ALGORITHMS:
            self.assertEqual(ma.run(name, r, ["A1", "A2"], ["B1", "B2"]), {"A2": "B1"})
        self.assertEqual(ma.gale_shapley({"A1": [], "B1": []}, ["A1"], ["B1"]), {})

    def test_one_sided_acceptance_not_matched(self):
        r = {"A1": ["B1"], "B1": []}                                        # B1 は A1 を受け入れない
        for name in ma.ALGORITHMS:
            self.assertEqual(ma.run(name, r, ["A1"], ["B1"]), {})

    def test_b_proposing(self):
        r, a_ids, b_ids = sample()
        m = ma.swap_sides(r, a_ids, b_ids)
        ma.validate_matching(m, r)
        self.assertTrue(ev.is_stable(m, r, a_ids, b_ids))


if __name__ == "__main__":
    unittest.main()
