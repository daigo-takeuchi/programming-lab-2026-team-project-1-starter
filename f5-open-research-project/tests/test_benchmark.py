# 実行時間の測定（experiments/benchmark.py）と比較（experiments/compare_algorithms.py）のテスト
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments import benchmark as bm  # noqa: E402
from experiments import compare_algorithms as ca  # noqa: E402


def work(n=200):
    return sum(range(n))


class TestBenchmark(unittest.TestCase):
    def test_measure_works(self):
        m = bm.measure(work, args=(100,), repeat=3, warmup=1)
        for k in ("times", "median", "min", "max", "mean", "repeat", "number"):
            self.assertIn(k, m)
        self.assertLessEqual(m["min"], m["median"])
        self.assertLessEqual(m["median"], m["max"])

    def test_repeat_count(self):
        for r in (1, 4, 7):
            self.assertEqual(len(bm.measure(work, repeat=r, warmup=0)["times"]), r)
        calls = []
        bm.measure(lambda: calls.append(1), repeat=3, warmup=2, number=5)
        self.assertEqual(len(calls), 2 + 3 * 5)                # 慣らし 2 回 + 測定 3 回 × 5 呼び出し

    def test_non_negative(self):
        m = bm.measure(work, repeat=5, number="auto")
        self.assertTrue(all(t >= 0 for t in m["times"]))
        self.assertGreaterEqual(m["number"], 1)
        _r, t = bm.timed(work, 10)
        self.assertGreaterEqual(t, 0)

    def test_median(self):
        self.assertEqual(bm.median([3, 1, 2]), 2)
        self.assertEqual(bm.median([4, 1, 3, 2]), 2.5)
        self.assertEqual(bm.median([5]), 5)
        self.assertEqual(bm.median([0.3, 0.1, 100.0]), 0.3)     # 外れ値の影響を受けにくい
        with self.assertRaises(ValueError):
            bm.median([])

    def test_invalid_repeat(self):
        for bad in (0, -1, 1.5, "3", True, None):
            with self.assertRaises(ValueError):
                bm.measure(work, repeat=bad)
        with self.assertRaises(ValueError):
            bm.measure(work, warmup=-1)
        with self.assertRaises(ValueError):
            bm.measure(work, number=0)

    def test_setup_copies_input(self):
        data = [3, 1, 2]
        seen = []

        def sort_in_place(a):
            seen.append(list(a))
            a.sort()
        m = bm.measure(sort_in_place, setup=lambda: (list(data),), repeat=3, warmup=1)
        self.assertEqual(data, [3, 1, 2])                       # 元の入力は変わらない
        self.assertTrue(all(s == [3, 1, 2] for s in seen))      # 毎回、同じ（ソート前の）入力
        self.assertIsNotNone(m["setup_median"])
        with self.assertRaises(ValueError):
            bm.measure(sort_in_place, setup=lambda: (list(data),), number=2)

    def test_benchmark_verifies_first(self):
        m = bm.benchmark(work, args=(10,), verify=lambda r: r == 45, repeat=2)
        self.assertEqual(m["result"], 45)
        self.assertTrue(m["verified"])
        with self.assertRaises(AssertionError):
            bm.benchmark(work, args=(10,), verify=lambda r: r == 0, repeat=2)

    def test_summarize(self):
        self.assertIn("median", bm.summarize(bm.measure(work, repeat=2), "us"))


class TestCompareAlgorithms(unittest.TestCase):
    def test_input_generation(self):
        a = ca.make_search_input(50, seed=3, queries=20, hit_ratio=1.0)
        b = ca.make_search_input(50, seed=3, queries=20, hit_ratio=1.0)
        self.assertEqual(a, b)                                  # 同じシードなら同じ入力
        self.assertEqual(len(set(a["data"])), 50)               # 重複なし
        self.assertTrue(all(k in a["data"] for k in a["queries"]))
        miss = ca.make_search_input(50, seed=3, queries=20, hit_ratio=0.0)
        self.assertTrue(all(k not in miss["data"] for k in miss["queries"]))
        self.assertEqual(ca.make_search_input(0, queries=5)["data"], [])
        self.assertEqual(ca.make_search_input(10, order="sorted")["data"],
                         sorted(ca.make_search_input(10, order="sorted")["data"]))
        with self.assertRaises(ValueError):
            ca.make_search_input(10, hit_ratio=2)
        with self.assertRaises(ValueError):
            ca.make_search_input(10, order="zigzag")

    def test_verify_detects_wrong_result(self):
        inp = ca.make_search_input(30, seed=1, queries=10)
        right = [-1 if k not in inp["data"] else inp["data"].index(k) for k in inp["queries"]]
        self.assertTrue(ca.verify_search(inp, None, right))
        wrong = [-1] * len(right)
        self.assertEqual(ca.verify_search(inp, None, wrong), all(r == -1 for r in right))
        self.assertFalse(ca.verify_search(inp, None, right[:-1]))

    def test_run_comparison(self):
        task = ca.make_search_task(queries=20)
        rows = ca.run_comparison(task, sizes=(0, 10, 200), repeat=2, warmup=0)
        self.assertEqual(len(rows), 6)
        for r in rows:
            self.assertTrue(r["correct"])
            self.assertTrue(r["consistent"])
            self.assertGreaterEqual(r["run_s"], 0)
            self.assertAlmostEqual(r["total_s"], r["prep_s"] + r["run_s"])
            self.assertEqual(len(r["times"]), 2)
        a = [r for r in rows if r["algorithm"] == "A"]
        self.assertTrue(all(r["prep_s"] == 0 for r in a))       # 線形探索に前処理はない
        self.assertIn("Binary search", ca.format_table(rows))

    def test_wrong_algorithm_is_marked(self):
        task = ca.make_search_task(queries=10, hit_ratio=1.0)
        task["algorithms"].append({"key": "X", "label": "X: always -1", "prepare": None,
                                   "run": lambda _p, inp: [-1] * len(inp["queries"]), "count": None})
        rows = ca.run_comparison(task, sizes=(20,), repeat=1, warmup=0)
        x = next(r for r in rows if r["algorithm"] == "X")
        self.assertFalse(x["correct"])
        self.assertFalse(x["consistent"])

    def test_mutating_algorithm_gets_fresh_input(self):
        task = ca.make_search_task(queries=5, hit_ratio=1.0)

        def destructive(_p, inp):
            res = [inp["data"].index(k) for k in inp["queries"]]
            inp["data"].clear()                                 # 入力を壊す
            return res
        task["algorithms"].append({"key": "M", "label": "M: destructive", "prepare": None, "run": destructive,
                                   "count": None, "mutates": True})
        rows = ca.run_comparison(task, sizes=(30,), repeat=3, warmup=1)
        self.assertTrue(all(r["correct"] for r in rows))        # 他のアルゴリズムの入力は壊れていない

    def test_csv_and_cli(self):
        rows = ca.run_comparison(ca.make_search_task(queries=5), sizes=(10,), repeat=1, warmup=0)
        with tempfile.TemporaryDirectory() as d:
            p = ca.save_csv(rows, Path(d) / "r.csv")
            text = Path(p).read_text(encoding="utf-8")
            self.assertIn("run_s", text.splitlines()[0])
            self.assertEqual(len(text.splitlines()), 3)
        self.assertIn("python", ca.environment())


if __name__ == "__main__":
    unittest.main()
