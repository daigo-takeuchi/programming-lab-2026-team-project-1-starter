import random
import unittest

from tests import _helpers  # noqa: F401
import state_transitions as st
import simulation as sim


class TestStateTransitions(unittest.TestCase):
    def setUp(self):
        self.p = sim.load_parameters()
        self.tp = self.p["transition"]

    def test_rows_sum_to_one(self):
        for o in st.OUTCOMES:
            st.validate_matrix(self.tp["base"][o])
            for trust in (0.0, 0.5, 1.0):
                for dialogue in (False, True):
                    for extra in (-1.0, 0.0, 1.0):
                        mat = st.transition_matrix("C" if o != "mutual_noncooperation" else "N",
                                                   "C" if o == "mutual_cooperation" else "N",
                                                   trust, dialogue, True, self.tp, extra)
                        self.assertTrue(st.validate_matrix(mat))

    def test_invalid_probabilities(self):
        good = self.tp["base"]["mixed"]
        bad1 = [row[:] for row in good]
        bad1[0][0] += 0.1
        bad2 = [row[:] for row in good]
        bad2[1] = [1.2, -0.2, 0.0, 0.0]
        for bad in (bad1, bad2, good[:3]):
            with self.assertRaises(ValueError):
                st.validate_matrix(bad)
        with self.assertRaises(ValueError):
            sim.with_changes(self.p, **{"transition.external_shock_probability": 1.5})

    def test_reproducible(self):
        def run(seed):
            rng = random.Random(seed)
            s, out = "Neutral", []
            for _ in range(50):
                s, _shock = st.next_state(s, "C", "N", 0.5, False, False, self.tp, rng)
                out.append(s)
            return out
        self.assertEqual(run(3), run(3))
        self.assertNotEqual(run(3), run(4))

    def test_dialogue_effect_zero(self):
        no_effect = dict(self.tp, dialogue_effect=0.0)
        a = st.transition_matrix("C", "N", 0.5, True, False, no_effect)
        b = st.transition_matrix("C", "N", 0.5, False, False, no_effect)
        self.assertEqual(a, b)
        control = dict(self.tp, dialogue_affects_transitions=False)
        self.assertEqual(st.transition_matrix("C", "N", 0.5, True, False, control),
                         st.transition_matrix("C", "N", 0.5, False, False, control))
        with_effect = st.transition_matrix("C", "N", 0.5, True, False, self.tp)
        self.assertGreater(with_effect[2][1], b[2][1])                # 対話あり：緊張 → 中立 が増える

    def test_direction(self):
        cc = st.stationary_distribution(st.transition_matrix("C", "C", 0.5, False, False, self.tp))
        nn = st.stationary_distribution(st.transition_matrix("N", "N", 0.5, False, False, self.tp))
        self.assertGreater(cc[0], nn[0])                              # 相互協調 → 協調状態が多い
        self.assertGreater(nn[2] + nn[3], cc[2] + cc[3])              # 相互非協調 → 緊張・紛争状態が多い
        self.assertAlmostEqual(sum(cc), 1.0)

    def test_shift_and_sample(self):
        self.assertEqual(st.shift_row([0.0, 1.0, 0.0, 0.0], 0.5), [0.5, 0.5, 0.0, 0.0])
        self.assertEqual(st.shift_row([0.0, 1.0, 0.0, 0.0], -0.5), [0.0, 0.5, 0.5, 0.0])
        self.assertEqual(st.sample([0.2, 0.3, 0.5, 0.0], 0.1), 0)
        self.assertEqual(st.sample([0.2, 0.3, 0.5, 0.0], 0.45), 1)
        self.assertEqual(st.sample([0.2, 0.3, 0.5, 0.0], 0.99), 2)

    def test_external_shock(self):
        always = dict(self.tp, external_shock_probability=1.0)
        rng = random.Random(0)
        s, shock = st.next_state("Conflict", "N", "N", 0.0, False, False, always, rng)
        self.assertTrue(shock)
        self.assertEqual(s, "Conflict")                               # それ以上悪くならない
        self.assertAlmostEqual(st.update_tension(0.0, "Conflict", 0.3), 0.3)


if __name__ == "__main__":
    unittest.main()
