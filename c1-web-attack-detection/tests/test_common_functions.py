# C-1：Notebook 第3章の共通関数（教員提供コード）の単体テスト
#
# Notebook から共通関数のセルを取り出して実行し、学生が出会う場面（未実装・エラー・不一致・空データ）で
# 正しく区別して表示されるかを確かめる。Python 標準ライブラリだけで実行できる。

import contextlib
import csv
import io
import json
import random
import statistics
import time
import unittest
from pathlib import Path

NOTEBOOK = Path(__file__).resolve().parent.parent / "C1_cybersecurity_starter.ipynb"


def load_common_functions():
    cells = json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]
    namespace = {"Path": Path, "csv": csv, "random": random, "statistics": statistics, "time": time,
                 "HAS_MATPLOTLIB": False, "JAPANESE_FONT": None}
    for cell in cells:
        text = "".join(cell["source"])
        if cell["cell_type"] == "code" and ("def check(" in text or "def compare_speed(" in text):
            with contextlib.redirect_stdout(io.StringIO()):
                exec(text, namespace)
    return namespace


def run_quiet(func, *args):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        result = func(*args)
    return result, buffer.getvalue()


class TestCheck(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ns = load_common_functions()

    def check(self, func, args, expected):
        return run_quiet(self.ns["check"], "テスト", func, args, expected)

    def test_ok(self):
        result, out = self.check(lambda x: x + 1, (1,), 2)
        self.assertTrue(result)
        self.assertIn("[OK]", out)

    def test_not_implemented(self):
        def stub(x):
            raise NotImplementedError("学生実装課題")
        result, out = self.check(stub, (1,), 2)
        self.assertIsNone(result)
        self.assertIn("[未実装]", out)

    def test_error_is_not_reported_as_unimplemented(self):
        """実装の中のエラーは [未実装] ではなく [エラー] とし、場所を表示する"""
        def buggy(records):
            return records[0]["src_ip"]          # 空のリストで IndexError
        result, out = self.check(buggy, ([],), None)
        self.assertFalse(result)
        self.assertIn("[エラー]", out)
        self.assertNotIn("[未実装]", out)
        self.assertIn("IndexError", out)
        self.assertIn('records[0]["src_ip"]', out)

    def test_ng_explains_difference(self):
        _, out = self.check(lambda x: None, (1,), [1])
        self.assertIn("[NG]", out)
        self.assertIn("return を書き忘れていませんか", out)
        _, out = self.check(lambda x: [1, 3], (1,), [1, 2])
        self.assertIn("1 番目", out)
        _, out = self.check(lambda x: {"a": 1}, (1,), {"a": 1, "b": 2})
        self.assertIn("足りないキー", out)

    def test_ng_shows_large_input_briefly(self):
        _, out = self.check(lambda records: 0, (list(range(100)),), 1)
        self.assertIn("リスト（100 件）", out)


class TestEvaluationAndSpeed(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ns = load_common_functions()

    def test_evaluation_counts(self):
        r = self.ns["evaluate_detection"](["C", "D"], ["B", "C"], ["A", "B", "C", "D", "E"])
        self.assertEqual((r["TP"], r["FP"], r["FN"], r["TN"]), (1, 1, 1, 2))
        self.assertEqual(r["Precision"], 0.5)

    def test_evaluation_empty_does_not_divide_by_zero(self):
        r = self.ns["evaluate_detection"]([], [], [])
        self.assertIsNone(r["Precision"])
        self.assertIsNone(r["Recall"])
        self.assertIsNone(r["Accuracy"])

    def test_compare_speed_requires_same_result(self):
        rows, out = run_quiet(self.ns["compare_speed"], lambda x: [1], lambda x: [2], lambda n: (n,), [10])
        self.assertEqual(rows, [])
        self.assertIn("[NG]", out)

    def test_compare_speed_unimplemented(self):
        def stub(x):
            raise NotImplementedError
        rows, out = run_quiet(self.ns["compare_speed"], stub, stub, lambda n: (n,), [10])
        self.assertEqual(rows, [])
        self.assertIn("[未実装]", out)

    def test_compare_speed_measures_with_same_input(self):
        rows, out = run_quiet(self.ns["compare_speed"], sorted, sorted, lambda n: (list(range(n, 0, -1)),), [10, 100])
        self.assertEqual([r[0] for r in rows], [10, 100])
        self.assertIn("結果は一致しました", out)

    def test_plot_without_matplotlib_prints_text(self):
        _, out = run_quiet(self.ns["plot_bars"], ["a", "b"], [1, 3], "タイトル", "件数", ["b"])
        self.assertIn("タイトル", out)
        self.assertIn("←", out)


if __name__ == "__main__":
    unittest.main()
