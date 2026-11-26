# F-1：統合 Notebook の構造・再生成・実行のテスト
#
# 構造のテストは標準ライブラリだけで実行できる。
# 再生成のテストには nbformat、実行のテストには nbformat・nbclient・ipykernel が必要（なければスキップ）。
#
# 実行（f1-career-income-optimization ディレクトリで）:
#   <python> -m unittest tests.test_f1_notebook -v

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
NOTEBOOK = PROJECT_DIR / "F1_life_planning_starter.ipynb"
BUILD = PROJECT_DIR / "scripts" / "build_notebook.py"

THEMES = {4: "F-1A", 5: "F-1B", 6: "F-1C", 7: "F-1D"}
THEME_DATA = {4: "f1a", 5: "f1b", 6: "f1c", 7: "f1d"}
SECTION_TITLES = [
    "社会的背景と解決すべき問題", "技術的背景と基本原理", "本演習の学習目標", "使用するデータセット",
    "STEP 1：データの読み込みと確認", "STEP 2：基本的な計算処理", "STEP 3：基本シミュレーションの完成",
    "STEP 4：探索アルゴリズムによる比較と改良", "STEP 5：公開統計データの利用と発展課題",
    "結果の考察とチーム独自の機能開発",
]
HAS_NBFORMAT = importlib.util.find_spec("nbformat") is not None
CAN_EXECUTE = all(importlib.util.find_spec(m) for m in ("nbformat", "nbclient", "ipykernel"))


def load_nb(path=NOTEBOOK):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def source(cell):
    return "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]


def chapter_of_cells(cells):
    chapter, result = None, []
    for cell in cells:
        m = re.match(r"# 第(\d+)章", source(cell)) if cell["cell_type"] == "markdown" else None
        if m:
            chapter = int(m.group(1))
        result.append(chapter)
    return result


class TestStructure(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.nb = load_nb()
        cls.cells = cls.nb["cells"]
        cls.chapters = chapter_of_cells(cls.cells)

    def test_valid_notebook(self):
        self.assertEqual(self.nb["nbformat"], 4)
        if HAS_NBFORMAT:
            import nbformat
            nbformat.validate(nbformat.reads(json.dumps(self.nb), as_version=4))

    def test_ten_chapters(self):
        self.assertEqual(sorted(set(c for c in self.chapters if c is not None)), list(range(10)))

    def test_theme_sections(self):
        for n, code in THEMES.items():
            text = "\n".join(source(c) for c, ch in zip(self.cells, self.chapters) if ch == n)
            self.assertIn(code, text)
            for i, title in enumerate(SECTION_TITLES, start=1):
                self.assertIn(f"## {n}.{i} {title}", text, f"第{n}章に {n}.{i} がない")
            for item in ("このテーマで解決する問題", "入力データ", "プログラム内部で行う計算", "出力結果",
                         "完成イメージ", "この章の進め方", "想定作業時間"):
                self.assertIn(item, text)

    def test_task_counts(self):
        """各テーマ Level 1 が 4 課題、Level 2 が 3 課題（合計 28）。テーマ章以外に課題はない"""
        for n in THEMES:
            for level, count in (("Level 1", 4), ("Level 2", 3)):
                stubs = [c for c, ch in zip(self.cells, self.chapters)
                         if ch == n and c["cell_type"] == "code" and f"【学生実装課題：{level}】" in source(c)]
                self.assertEqual(len(stubs), count, f"第{n}章の {level} 課題の数")
        all_stubs = [c for c in self.cells if c["cell_type"] == "code" and "【学生実装課題" in source(c)]
        self.assertEqual(len(all_stubs), 28)

    def test_function_names_unique(self):
        names = []
        for c in self.cells:
            if c["cell_type"] == "code" and "【学生実装課題" in source(c):
                names += re.findall(r"^def (\w+)\(", source(c), re.M)
        self.assertEqual(len(names), 28)
        self.assertEqual(len(names), len(set(names)), "学生実装課題の関数名が重複")

    def test_no_reference_solution_in_notebook(self):
        """教員用参照実装（solutions/、Git 管理外）の本体の行が、Notebook のコードセルに含まれていない
        （ヒントの Markdown には for 文の書き出しなどの「文法の例」を意図的に書いているので対象外）"""
        ref = PROJECT_DIR / "solutions" / "reference_solutions.py"
        if not ref.exists():
            self.skipTest("参照実装がない")
        ns = {}
        exec(ref.read_text(encoding="utf-8"), ns)
        text = "\n".join(source(c) for c in self.cells if c["cell_type"] == "code")
        for name, body in ns["SOLUTIONS"].items():
            for line in body.strip().splitlines()[1:]:
                line = line.strip()
                if len(line) >= 30 and not line.startswith(("#", '"""')):
                    self.assertNotIn(line, text, f"{name} の参照実装の行が Notebook にある: {line}")

    def test_tiny_checks_present(self):
        """各テーマに Tiny Dataset の期待値つき動作確認（Level 1・2）がある"""
        for n in THEMES:
            tiny = [c for c, ch in zip(self.cells, self.chapters)
                    if ch == n and c["cell_type"] == "code" and "【動作確認】Tiny Dataset" in source(c)]
            self.assertEqual(len(tiny), 2, f"第{n}章の Tiny の動作確認")
            for c in tiny:
                self.assertIn("check(", source(c))

    def test_student_stubs_are_unimplemented(self):
        for c in self.cells:
            if c["cell_type"] == "code" and "【学生実装課題" in source(c):
                body = source(c)
                self.assertIn('raise NotImplementedError("学生実装課題")', body)
                self.assertIn("TODO", body)
                # ひな形には return 文を書かない（完成解答の混入防止）
                self.assertNotRegex(body, r"^\s+return ", "学生実装課題のセルに return がある")

    def test_every_task_has_hints_and_check(self):
        for i, c in enumerate(self.cells):
            if c["cell_type"] == "code" and "【学生実装課題" in source(c):
                hint = source(self.cells[i + 1])
                for k in ("ヒント1", "ヒント2", "ヒント3"):
                    self.assertIn(k, hint)
                self.assertIn("【動作確認】", source(self.cells[i + 2]))
                self.assertIn("check(", source(self.cells[i + 3]))

    def test_no_absolute_paths(self):
        for c in self.cells:
            self.assertNotRegex(source(c), r"/home/|C:\\\\|/mnt/")

    def test_theme_chapters_do_not_reference_other_themes(self):
        """テーマ章は、他のテーマのデータフォルダ・Mini Dataset の変数を使わない"""
        theme_vars = {4: ["career_options", "tiny_careers", "salary_small"],
                      5: ["work_options", "household", "tiny_households", "CARE_SPLITS", "BASIC_HOURS"],
                      6: ["housing_options", "tiny_housing", "prices_small"],
                      7: ["family", "transfer_options", "tiny_members", "assets_small"]}
        for n in THEMES:
            code_text = "\n".join(source(c) for c, ch in zip(self.cells, self.chapters)
                                  if ch == n and c["cell_type"] == "code")
            for other in THEMES:
                if other == n:
                    continue
                self.assertNotIn(f'"{THEME_DATA[other]}"', code_text, f"第{n}章が {THEME_DATA[other]} を参照")
                for var in theme_vars[other]:
                    self.assertNotRegex(code_text, rf"\b{var}\b", f"第{n}章が {var} を参照")

    def test_f1b_level1_practice(self):
        """F-1B に Level 1 の統合演習（新しい関数を作らない練習）があり、ヒントと期待値つきの確認がある"""
        idx = [i for i, (c, ch) in enumerate(zip(self.cells, self.chapters))
               if ch == 5 and c["cell_type"] == "code" and "【練習：Level 1】" in source(c)]
        self.assertEqual(len(idx), 1)
        body = source(self.cells[idx[0]])
        self.assertNotRegex(body, r"^def ", "練習で新しい関数を作らせない")
        self.assertIn("TODO", body)
        for k in ("ヒント1", "ヒント2", "ヒント3"):
            self.assertIn(k, source(self.cells[idx[0] + 1]))
        self.assertIn("check(", source(self.cells[idx[0] + 3]))

    def test_b6_four_stages(self):
        text = "\n".join(source(c) for c, ch in zip(self.cells, self.chapters) if ch == 5)
        for stage in ("所得の制約", "各人の時間の制約", "育児・介護の時間の充足", "候補の保存"):
            self.assertIn(stage, text)

    def test_chapter8_benchmarks(self):
        """第8章に 4 テーマの性能評価があり、乱数シード固定・メモリ上の生成・中央値の測定を使う"""
        md_text = "\n".join(source(c) for c, ch in zip(self.cells, self.chapters) if ch == 8 and c["cell_type"] == "markdown")
        code_text = "\n".join(source(c) for c, ch in zip(self.cells, self.chapters) if ch == 8 and c["cell_type"] == "code")
        for heading in ("## 8.4 F-1A", "## 8.5 F-1B", "## 8.6 F-1C", "## 8.7 F-1D"):
            self.assertIn(heading, md_text)
        for term in ("O(N × T)", "O(k² × m)", "O(log N + K)", "O(M × D × T)", "O(N log N)"):
            self.assertIn(term, md_text)
        self.assertIn("perf_counter", code_text)
        self.assertIn("statistics.median", code_text)
        self.assertRegex(code_text, r"random\.Random\(seed\)")
        self.assertNotRegex(code_text, r"open\(|\.to_csv|savefig|write_text", "Benchmark Dataset をファイルに保存しない")
        for var in ("career_options", "tiny_careers", "work_options", "tiny_households", "CARE_SPLITS", "BASIC_HOURS",
                    "housing_options", "tiny_housing", "transfer_options", "tiny_members"):
            self.assertNotRegex(code_text, rf"\b{var}\b", f"第8章がテーマ章の変数 {var} を使っている")

    def test_outputs_are_empty(self):
        for c in self.cells:
            if c["cell_type"] == "code":
                self.assertEqual(c["outputs"], [])
                self.assertIsNone(c["execution_count"])


@unittest.skipUnless(HAS_NBFORMAT, "nbformat がない")
class TestRegeneration(unittest.TestCase):

    def run_build(self, output, *extra):
        return subprocess.run([sys.executable, str(BUILD), "--output", str(output), *extra],
                              capture_output=True, text=True, cwd=PROJECT_DIR)

    def test_regenerated_notebook_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "nb.ipynb"
            self.assertEqual(self.run_build(out).returncode, 0)
            self.assertEqual(out.read_text(encoding="utf-8"), NOTEBOOK.read_text(encoding="utf-8"))

    def _edited_copy(self, tmp, edit):
        out = Path(tmp) / "nb.ipynb"
        shutil.copy(NOTEBOOK, out)
        nb = load_nb(out)
        edit(nb)
        out.write_text(json.dumps(nb, ensure_ascii=False), encoding="utf-8")
        return out

    def test_refuses_edited_notebook(self):
        def edit(nb):
            for c in nb["cells"]:
                if c["cell_type"] == "code" and "【学生実装課題" in source(c):
                    c["source"] = source(c).replace('raise NotImplementedError("学生実装課題")', "return 0")
                    break
        with tempfile.TemporaryDirectory() as tmp:
            out = self._edited_copy(tmp, edit)
            before = out.read_text(encoding="utf-8")
            r = self.run_build(out)
            self.assertNotEqual(r.returncode, 0)
            self.assertEqual(out.read_text(encoding="utf-8"), before)

    def test_refuses_executed_notebook(self):
        def edit(nb):
            for c in nb["cells"]:
                if c["cell_type"] == "code":
                    c["execution_count"] = 1
                    c["outputs"] = [{"output_type": "stream", "name": "stdout", "text": "x"}]
                    break
        with tempfile.TemporaryDirectory() as tmp:
            out = self._edited_copy(tmp, edit)
            self.assertNotEqual(self.run_build(out).returncode, 0)
            self.assertEqual(self.run_build(out, "--force").returncode, 0)

    def test_unchanged_notebook_can_be_regenerated(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self._edited_copy(tmp, lambda nb: None)
            self.assertEqual(self.run_build(out).returncode, 0)


@unittest.skipUnless(CAN_EXECUTE, "nbformat・nbclient・ipykernel がない")
class TestExecution(unittest.TestCase):
    """未実装のまま実行しても止まらないこと、各テーマが単独で動くこと、data がなくても動くこと"""

    def execute(self, keep=lambda ch: True, workdir=PROJECT_DIR):
        import nbformat
        from nbclient import NotebookClient
        nb = nbformat.read(NOTEBOOK, as_version=4)
        chapters = chapter_of_cells([dict(cell_type=c.cell_type, source=c.source) for c in nb.cells])
        nb.cells = [c for c, ch in zip(nb.cells, chapters) if keep(ch)]
        NotebookClient(nb, timeout=300, kernel_name="python3",
                       resources={"metadata": {"path": str(workdir)}}).execute()
        return "\n".join(o.get("text", "") for c in nb.cells if c.cell_type == "code" for o in c.outputs)

    def test_run_all_unimplemented(self):
        text = self.execute()
        self.assertIn("[未実装]", text)
        # 第3章の例（わざと出す [エラー]）以外に [エラー] がない
        self.assertEqual(text.count("[エラー]"), 1)

    def test_each_theme_independently(self):
        for n in THEMES:
            with self.subTest(theme=THEMES[n]):
                self.execute(keep=lambda ch, n=n: ch is not None and (ch <= 3 or ch == n))

    def test_each_theme_with_chapter8(self):
        """担当テーマの章 + 第8章だけを実行しても止まらない（他のテーマの性能評価はスキップ）"""
        for n in THEMES:
            with self.subTest(theme=THEMES[n]):
                text = self.execute(keep=lambda ch, n=n: ch is not None and (ch <= 3 or ch in (n, 8)))
                self.assertIn("[スキップ]", text)
                self.assertEqual(text.count("[エラー]"), 1)

    def test_without_small_datasets(self):
        """公開統計（*_small.csv）がなくても、Tiny があれば全体を実行できる"""
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(PROJECT_DIR / "data", Path(tmp) / "data",
                            ignore=shutil.ignore_patterns("*_small.csv", "raw", "interim"))
            text = self.execute(workdir=Path(tmp))
            self.assertIn("Small Dataset がありません", text)
            self.assertEqual(text.count("[エラー]"), 1)

    def test_without_data_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = self.execute(workdir=Path(tmp))
            self.assertIn("data フォルダが見つかりません", text)


if __name__ == "__main__":
    unittest.main()
