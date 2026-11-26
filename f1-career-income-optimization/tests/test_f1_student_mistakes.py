# F-1：学生が起こしやすい誤りを、Notebook の動作確認が見つけられるかのテスト（教員用）
#
# 誤りの実装例は solutions/student_mistakes.py（Git 管理外。ほぼ完成した解答を含むため公開しない）。
# 参照実装（solutions/reference_solutions.py）の代わりに誤りを 1 つずつ差し込み、
# 第0〜3章＋担当テーマの章の動作確認が [NG] または [エラー] を出すことを確かめる。
# Notebook のコードセルを、このプロセスの中で順に実行する（カーネルを起動しないので速い）。
#
# 実行（f1-career-income-optimization ディレクトリで）:
#   <python> -m unittest tests.test_f1_student_mistakes -v

import contextlib
import io
import json
import os
import re
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
NOTEBOOK = PROJECT_DIR / "F1_life_planning_starter.ipynb"
SOLUTIONS = PROJECT_DIR / "solutions" / "reference_solutions.py"
MISTAKES = PROJECT_DIR / "solutions" / "student_mistakes.py"


def load_module(path):
    ns = {}
    exec(path.read_text(encoding="utf-8"), ns)
    return ns


def notebook_cells():
    cells = json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]
    result, chapter = [], None
    for cell in cells:
        text = "".join(cell["source"])
        m = re.match(r"# 第(\d+)章", text) if cell["cell_type"] == "markdown" else None
        if m:
            chapter = int(m.group(1))
        result.append((cell["cell_type"], text, chapter))
    return result


def run_theme(chapter, overrides=None):
    """第0〜3章と第 chapter 章のコードセルを実行し、[NG]・[エラー] の行を返す（第3章のわざと出す例は除く）"""
    overrides = overrides or {}
    ref = load_module(SOLUTIONS)
    ns = {"__name__": "__main__"}
    bad = []
    old_cwd = os.getcwd()
    os.environ.setdefault("MPLBACKEND", "Agg")
    os.chdir(PROJECT_DIR)
    try:
        for kind, text, ch in notebook_cells():
            if kind != "code" or ch is None or not (ch <= 3 or ch == chapter):
                continue
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(io.StringIO()):
                exec(compile(text, "<cell>", "exec"), ns)
                if "【学生実装課題" in text:
                    for name in re.findall(r"^def (\w+)\(", text, re.M):
                        exec(overrides.get(name, ref["SOLUTIONS"][name]), ns)
                if "【練習：" in text:
                    for key, body in ref["PRACTICE"].items():
                        if key in text:
                            exec(body, ns)
            if "わざと" in text:
                continue
            bad += [line for line in buffer.getvalue().splitlines() if line.startswith(("[NG]", "[エラー]"))]
    finally:
        os.chdir(old_cwd)
        try:
            import matplotlib.pyplot as plt
            plt.close("all")
        except ImportError:
            pass
    return bad


@unittest.skipUnless(SOLUTIONS.exists() and MISTAKES.exists(), "教員用の参照実装・誤りの例がない（solutions/）")
class TestStudentMistakes(unittest.TestCase):

    def test_reference_has_no_ng(self):
        """参照実装では、どのテーマでも [NG]・[エラー] が出ない（比較の基準）"""
        for chapter in (4, 5, 6, 7):
            with self.subTest(chapter=chapter):
                self.assertEqual(run_theme(chapter), [])

    def test_each_mistake_is_detected(self):
        """誤りの実装を 1 つ差し込むと、動作確認のどこかで [NG] または [エラー] になる"""
        for m in load_module(MISTAKES)["MISTAKES"]:
            with self.subTest(m["label"]):
                bad = run_theme(m["chapter"], {m["function"]: m["source"]})
                self.assertTrue(bad, f"見つけられない誤り: {m['label']}")

    def test_unsorted_input_breaks_binary_search(self):
        """ソート済みという前提を満たさない入力では、二分探索の件数が線形探索と合わない（第6章の教員提供の例）"""
        import csv
        ns = {}
        exec(load_module(SOLUTIONS)["SOLUTIONS"]["count_affordable"], ns)
        with open(PROJECT_DIR / "data" / "f1c" / "housing_options_tiny.csv", encoding="utf-8") as f:
            prices = [int(r["purchase_price"]) for r in csv.DictReader(f)]
        linear = sum(1 for p in prices if p <= 3000)
        self.assertNotEqual(ns["count_affordable"](prices, 3000), linear)
        self.assertEqual(ns["count_affordable"](sorted(prices), 3000), linear)
        text = "\n".join(t for kind, t, ch in notebook_cells() if ch == 6 and kind == "code")
        self.assertIn("ソートしていないリストに二分探索", text)


if __name__ == "__main__":
    unittest.main()
