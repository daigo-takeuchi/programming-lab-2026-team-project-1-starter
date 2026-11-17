import unittest

from tests import _helpers  # noqa: F401
import economic_model as em
import allocation_strategies as al
from simulation import validate_allocation


class TestAllocationStrategies(unittest.TestCase):
    def test_equal(self):
        a = al.equal_allocation()
        self.assertTrue(all(abs(v - 0.25) < 1e-12 for v in a.values()))
        self.assertTrue(validate_allocation(a))

    def test_priority(self):
        a = al.priority_allocation("rd", 0.55)
        self.assertAlmostEqual(a["rd"], 0.55)
        self.assertAlmostEqual(a["education"], 0.15)
        self.assertTrue(validate_allocation(a))
        with self.assertRaises(ValueError):
            al.priority_allocation("military")
        with self.assertRaises(ValueError):
            al.priority_allocation("rd", 1.5)

    def test_random(self):
        for seed in range(50):
            a = al.random_allocation(seed)
            self.assertTrue(validate_allocation(a))
            g = al.random_allocation(seed, step=0.1)
            self.assertTrue(validate_allocation(g))
            self.assertTrue(all(abs(v * 10 - round(v * 10)) < 1e-9 for v in g.values()))   # 10% 刻み
        self.assertEqual(al.random_allocation(7), al.random_allocation(7))                  # 同じシード → 同じ配分
        self.assertNotEqual(al.random_allocation(7), al.random_allocation(8))

    def test_sum_is_one(self):
        for sc in al.load_scenarios():
            self.assertAlmostEqual(sum(sc["shares"].values()), 1.0)
        self.assertEqual(sum(al.units_from_shares(al.equal_allocation(), 10)), 10)
        self.assertEqual(al.units_from_shares(al.equal_allocation(), 10), (3, 3, 2, 2))     # 最大剰余法・決定的
        self.assertEqual(al.units_from_shares(al.equal_allocation(), 20), (5, 5, 5, 5))

    def test_invalid_allocation(self):
        bad = [{"education": 0.6, "rd": 0.6, "infrastructure": 0.0, "healthcare": -0.2},
               {"education": 0.5, "rd": 0.5, "infrastructure": 0.5, "healthcare": 0.5},
               {"education": 1.0, "rd": 0.0, "infrastructure": 0.0},
               {"education": "a", "rd": 0.0, "infrastructure": 0.0, "healthcare": 1.0}]
        for b in bad:
            with self.assertRaises(ValueError):
                validate_allocation(b)
        self.assertTrue(validate_allocation({"education": 0.1, "rd": 0.2, "infrastructure": 0.3, "healthcare": 0.4}))
        with self.assertRaises(ValueError):
            al.units_count(0.3)
        with self.assertRaises(ValueError):
            al.shares_from_units((1, 2, 3), 10)

    def test_units(self):
        self.assertEqual(al.units_count(0.1), 10)
        self.assertEqual(al.units_count(0.05), 20)
        self.assertEqual(al.shares_from_units((10, 0, 0, 0), 10)["education"], 1.0)

    def test_optimized_strategies(self):
        p = em.load_economy()
        for f in (al.greedy_allocation, al.exhaustive_allocation, al.local_search_allocation):
            a = f(p, "final_gdp", 0.25, years=5)
            self.assertTrue(validate_allocation(a))


if __name__ == "__main__":
    unittest.main()
