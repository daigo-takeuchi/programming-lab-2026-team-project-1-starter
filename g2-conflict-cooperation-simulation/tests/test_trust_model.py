import unittest

from tests import _helpers  # noqa: F401
import trust_model as tm
import simulation as sim


class TestTrustModel(unittest.TestCase):
    def setUp(self):
        self.c = sim.load_parameters()["trust"]

    def test_update(self):
        self.assertAlmostEqual(tm.update_trust(0.5, "C", "C", self.c), 0.5 + self.c["mutual_cooperation"])

    def test_clip(self):
        self.assertEqual(tm.update_trust(1.0, "C", "C", self.c, True, True), 1.0)
        self.assertEqual(tm.update_trust(0.0, "N", "N", self.c), 0.0)
        t = 0.5
        for _ in range(100):
            t = tm.update_trust(t, "N", "C", self.c)
            self.assertTrue(0 <= t <= 1)

    def test_mutual_cooperation(self):
        self.assertGreater(tm.update_trust(0.5, "C", "C", self.c), 0.5)

    def test_noncooperation(self):
        self.assertLess(tm.update_trust(0.5, "N", "N", self.c), 0.5)
        one_sided = tm.update_trust(0.5, "C", "N", self.c)
        self.assertLess(one_sided, 0.5)
        self.assertEqual(one_sided, tm.update_trust(0.5, "N", "C", self.c))      # ペアで 1 つの値（対称）

    def test_dialogue_and_agreement(self):
        base = tm.update_trust(0.5, "C", "N", self.c)
        self.assertAlmostEqual(tm.update_trust(0.5, "C", "N", self.c, dialogue=True), base + self.c["dialogue"])
        self.assertAlmostEqual(tm.update_trust(0.5, "C", "N", self.c, agreement=True), base + self.c["agreement"])


if __name__ == "__main__":
    unittest.main()
