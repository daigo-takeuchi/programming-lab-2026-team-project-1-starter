# F3：preferences.py のテスト

import unittest

import participants as pt
import preferences as pr

W = {"interest": 0.25, "lifestyle": 0.25, "values": 0.25, "age": 0.25}


def person(pid, group, age=30, interests=(), lifestyle=None, values=None, age_range=(25, 35), min_score=0.0, cands=None):
    return {"id": pid, "group": group, "age": age, "interests": list(interests),
            "lifestyle": lifestyle or {"x": 0.5}, "values": values or {"y": 0.5},
            "preferences": {"weights": dict(W), "age_range": list(age_range), "min_score": min_score},
            "acceptable_candidates": cands}


class TestComponents(unittest.TestCase):
    def test_interest_jaccard(self):
        p, q = person("A1", "A", interests=["a", "b"]), person("B1", "B", interests=["b", "c"])
        self.assertAlmostEqual(pr.interest_similarity(p, q), 1 / 3)
        self.assertEqual(pr.interest_similarity(person("A1", "A"), person("B1", "B")), 0.0)

    def test_profile_similarity(self):
        p = person("A1", "A", lifestyle={"m": 0.2, "s": 1.0})
        q = person("B1", "B", lifestyle={"m": 0.6, "s": 1.0})
        self.assertAlmostEqual(pr.lifestyle_similarity(p, q), (0.6 + 1.0) / 2)

    def test_age(self):
        p = person("A1", "A", age_range=(25, 30))
        self.assertEqual(pr.age_compatibility(p, person("B1", "B", age=28)), 1.0)
        self.assertAlmostEqual(pr.age_compatibility(p, person("B1", "B", age=35)), 0.5)
        self.assertEqual(pr.age_compatibility(p, person("B1", "B", age=50)), 0.0)

    def test_score_formula_and_range(self):
        p = person("A1", "A", interests=["a"], lifestyle={"m": 0.0}, values={"v": 1.0}, age_range=(30, 30))
        q = person("B1", "B", age=30, interests=["a"], lifestyle={"m": 1.0}, values={"v": 1.0})
        # interest 1, lifestyle 0, values 1, age 1 → 0.75
        self.assertAlmostEqual(pr.compatibility_score(p, q), 0.75)
        g = pt.load_participants()
        for v in pr.score_table(g).values():
            self.assertTrue(0 <= v <= 1)

    def test_weights_must_sum_to_one(self):
        p, q = person("A1", "A"), person("B1", "B")
        with self.assertRaises(ValueError):
            pr.compatibility_score(p, q, {"interest": 0.5, "lifestyle": 0.5, "values": 0.5, "age": 0.0})


class TestRankings(unittest.TestCase):
    def setUp(self):
        self.g = pt.load_participants()
        self.s = pr.score_table(self.g)
        self.r = pr.build_rankings(self.g, self.s)

    def test_sorted_by_score(self):
        for pid, lst in self.r.items():
            vals = [self.s[(pid, q)] for q in lst]
            self.assertEqual(vals, sorted(vals, reverse=True))
        pr.validate_rankings(self.r, self.g)                  # 存在・相手のグループ・重複なし

    def test_threshold(self):
        self.assertEqual(self.r["A5"], [])                     # A5 は min_score が厳しく、受け入れ可能な相手がいない
        for pid, lst in self.r.items():
            p = pt.by_id(self.g)[pid]
            self.assertTrue(all(self.s[(pid, q)] >= p["preferences"]["min_score"] for q in lst))

    def test_tie_broken_by_id(self):
        g = {"A": [person("A1", "A")], "B": [person("B2", "B"), person("B1", "B")]}   # 同じプロフィール → 同点
        s = pr.score_table(g)
        self.assertEqual(pr.build_rankings(g, s)["A1"], ["B1", "B2"])

    def test_acceptable_candidates_filter(self):
        g = {"A": [person("A1", "A", cands=["B2"])], "B": [person("B1", "B"), person("B2", "B")]}
        self.assertEqual(pr.build_rankings(g, pr.score_table(g))["A1"], ["B2"])

    def test_mutual_acceptance(self):
        self.assertTrue(pr.mutually_acceptable(self.r, "A1", "B1"))
        self.assertFalse(pr.mutually_acceptable(self.r, "A5", "B5"))   # B5 は A5 を受け入れるが、A5 は受け入れない
        self.assertIn("A5", self.r["B5"])

    def test_rank_index_and_compat(self):
        idx = pr.rank_index(self.r)
        self.assertEqual(idx["A1"]["B1"], 0)
        self.assertAlmostEqual(pr.pair_compatibility("A1", "B1", self.s), (self.s[("A1", "B1")] + self.s[("B1", "A1")]) / 2)


if __name__ == "__main__":
    unittest.main()
