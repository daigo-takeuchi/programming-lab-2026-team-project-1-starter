# F3：evaluation.py のテスト

import unittest

import evaluation as ev
import matching_algorithms as ma
import participants as pt
import preferences as pr
import relationship_stability as rs

R = {"A1": ["B1", "B2"], "A2": ["B1"], "A3": [],
     "B1": ["A2", "A1"], "B2": ["A1"], "B3": []}
A, B = ["A1", "A2", "A3"], ["B1", "B2", "B3"]


def rec(year, observed=20):
    return {"dissolution_year": year, "observed_years": observed, "dissolved": year is not None,
            "censored": year is None, "years_continued": observed if year is None else year - 1}


class TestMatchingMetrics(unittest.TestCase):
    def test_matching_rate(self):
        self.assertAlmostEqual(ev.matching_rate({"A1": "B2", "A2": "B1"}, 6), 4 / 6)
        self.assertEqual(ev.matching_rate({}, 6), 0)
        self.assertIsNone(ev.matching_rate({}, 0))
        with self.assertRaises(ValueError):
            ev.matching_rate({"A1": "B1", "A2": "B2"}, 3)             # 成立ペア数と全参加者数が整合しない

    def test_satisfaction(self):
        m = {"A1": "B2", "A2": "B1"}
        s = ev.satisfaction_by_participant(m, R)
        self.assertEqual(s["A1"], 0.5)          # 2 人中 2 番目 → 1 − 1/2
        self.assertEqual(s["A2"], 1.0)
        self.assertEqual(s["B1"], 1.0)
        self.assertEqual(s["B2"], 1.0)
        self.assertEqual(s["A3"], 0.0)          # 受け入れ可能な相手なし（未マッチング）
        self.assertEqual(s["B3"], 0.0)
        summ = ev.satisfaction_summary(m, R, A, B)
        self.assertAlmostEqual(summ["mean_all"], 3.5 / 6)
        self.assertAlmostEqual(summ["mean_matched"], 3.5 / 4)
        self.assertAlmostEqual(summ["unmatched_A"], 1 / 3)
        self.assertEqual(summ["min"], 0.0)
        self.assertEqual(summ["rank_distribution"], {2: 1, 1: 3, "unmatched": 2})

    def test_blocking_pairs(self):
        self.assertEqual(ev.blocking_pairs({"A1": "B2", "A2": "B1"}, R, A, B), [])
        # A1 は第 1 希望の B1 と組んでいるので (A1, B2) は blocking pair ではない。B1 は A1 より A2 を好み、A2 は未マッチング
        self.assertEqual(ev.blocking_pairs({"A1": "B1"}, R, A, B), [("A2", "B1")])
        # 未マッチングの人は、受け入れ可能な相手とのマッチングを未マッチングより好む
        self.assertEqual(ev.blocking_pairs({}, R, A, B), [("A1", "B1"), ("A1", "B2"), ("A2", "B1")])
        self.assertTrue(ev.is_stable({"A1": "B2", "A2": "B1"}, R, A, B))

    def test_greedy_blocking_on_sample(self):
        g = pt.load_participants()
        s = pr.score_table(g)
        r = pr.build_rankings(g, s)
        a_ids, b_ids = [p["id"] for p in g["A"]], [p["id"] for p in g["B"]]
        self.assertEqual(ev.blocking_pairs(ma.greedy_matching(r, a_ids, b_ids), r, a_ids, b_ids), [("A3", "B2")])
        self.assertEqual(ev.blocking_pairs(ma.gale_shapley(r, a_ids, b_ids), r, a_ids, b_ids), [])


class TestContinuationMetrics(unittest.TestCase):
    def test_continuation_rate(self):
        records = [rec(None), rec(3), rec(12), rec(None)]
        self.assertEqual(ev.continuation_rate(records, 5), 0.75)
        self.assertEqual(ev.continuation_rate(records, 10), 0.75)
        self.assertEqual(ev.continuation_rate(records, 20), 0.5)

    def test_no_pairs_is_undefined(self):
        self.assertIsNone(ev.continuation_rate([], 10))              # 0% とは断定しない
        self.assertEqual(ev.long_term_matching_rate([], 10, 10), 0)
        self.assertIsNone(ev.survival_curve([]))

    def test_outside_observation(self):
        with self.assertRaises(ValueError):
            ev.continuation_rate([rec(None, observed=5)], 10)

    def test_long_term_rate(self):
        records = [rec(None), rec(3), rec(12), rec(None)]
        self.assertAlmostEqual(ev.long_term_matching_rate(records, 10, 10), 2 * 3 / 10)
        self.assertLessEqual(ev.long_term_matching_rate(records, 10, 10), 2 * len(records) / 10)

    def test_durations(self):
        d = ev.duration_summary([rec(None), rec(3), rec(12)])
        self.assertEqual((d["pairs"], d["dissolved"], d["censored"]), (3, 2, 1))
        self.assertAlmostEqual(d["mean_years_dissolved"], (2 + 11) / 2)
        self.assertAlmostEqual(d["mean_observed_years"], (20 + 2 + 11) / 3)

    def test_survival_curve(self):
        curve = ev.survival_curve([rec(2, 3), rec(None, 3)])
        self.assertEqual(curve, [1.0, 1.0, 0.5, 0.5])


class TestIntegrated(unittest.TestCase):
    def test_compare_algorithms_consistency(self):
        g = pt.load_participants()
        s = pr.score_table(g)
        r = pr.build_rankings(g, s)
        res = ev.compare_algorithms(g, r, s, rs.load_parameters(), matching_seeds=range(3), replicates=20)
        for v in res.values():
            self.assertAlmostEqual(v["matching_rate"], 2 * v["pairs"] / pt.total_participants(g))
            self.assertLessEqual(v["long_term_10y"], v["matching_rate"])
            self.assertAlmostEqual(v["long_term_10y"], v["matching_rate"] * v["continuation_10y"], places=9)
            self.assertEqual(v["survival_curve"][0], 1.0)
        self.assertEqual(res["gale_shapley"]["blocking_pairs"], 0)
        self.assertEqual(res["random"]["matching_runs"], 3)


if __name__ == "__main__":
    unittest.main()
