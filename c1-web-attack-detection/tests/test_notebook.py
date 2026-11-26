# C-1：統合 Notebook の構造と実行のテスト
#
# 構造のテストは Python 標準ライブラリだけで実行できる。
# 実行のテストには nbformat・nbclient・ipykernel が必要（なければスキップする）。
#
# 実行（c1-web-attack-detection ディレクトリで）:
#   .venv/bin/python -m unittest tests.test_notebook -v

import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
NOTEBOOK = PROJECT_DIR / "C1_cybersecurity_starter.ipynb"

THEMES = {4: "C-1A", 5: "C-1B", 6: "C-1C", 7: "C-1D", 8: "C-1E"}
THEME_DATA = {4: "c1a", 5: "c1b", 6: "c1c", 7: "c1d", 8: "c1e"}
SECTION_TITLES = [
    "このテーマで何を解決するのか", "社会的背景と必要な技術知識", "学習目標と課題の全体像",
    "使用するデータ", "STEP 1：データを見て理解する", "STEP 2：数える・探す・比較する",
    "STEP 3：異常を検出する", "STEP 4：アルゴリズムを改良する", "STEP 5：実データで評価・発展させる",
    "結果の考察とチーム独自の発展課題",
]
CAN_EXECUTE = all(importlib.util.find_spec(m) for m in ("nbformat", "nbclient", "ipykernel"))


def load_cells():
    return json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]


def source(cell):
    return "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]


def chapter_of_cells(cells):
    """各セルが何章に属するかのリストを返す"""
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
        cls.cells = load_cells()
        cls.chapters = chapter_of_cells(cls.cells)
        cls.markdown = "\n".join(source(c) for c in cls.cells if c["cell_type"] == "markdown")

    def test_valid_json_notebook(self):
        nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
        self.assertEqual(nb["nbformat"], 4)

    def test_ten_chapters(self):
        self.assertEqual(sorted(set(c for c in self.chapters if c is not None)), list(range(10)))

    def test_theme_sections(self):
        """全テーマに 10 個の節（N.1〜N.10）が同じ順序である"""
        for n, code in THEMES.items():
            with self.subTest(code):
                self.assertIn(f"# 第{n}章　{code}", self.markdown)
                for i, title in enumerate(SECTION_TITLES, start=1):
                    self.assertIn(f"## {n}.{i} {title}", self.markdown)

    def test_levels_marked(self):
        for n in THEMES:
            text = "\n".join(source(c) for c, ch in zip(self.cells, self.chapters) if ch == n)
            with self.subTest(chapter=n):
                for label in ["【学生実装課題：Level 1】", "【学生実装課題：Level 2】", "【発展課題：Level 3】",
                              "【教員提供コード】", "【動作確認】", "【ヒント】", "【考察課題】"]:
                    self.assertIn(label, text)

    def test_level1_task_count(self):
        """各テーマの Level 1 の関数は 3〜5 個"""
        for n in THEMES:
            stubs = [source(c) for c, ch in zip(self.cells, self.chapters)
                     if ch == n and c["cell_type"] == "code" and "【学生実装課題：Level 1】" in source(c)]
            with self.subTest(chapter=n):
                self.assertTrue(3 <= len(stubs) <= 5, len(stubs))

    def test_student_stubs_are_unimplemented(self):
        """学生実装課題のセルには完成解答を入れない（各関数が NotImplementedError で終わる）"""
        for cell in self.cells:
            text = source(cell)
            if cell["cell_type"] != "code" or "【学生実装課題" not in text:
                continue
            n_defs = len(re.findall(r"^def \w+\(", text, re.M))
            self.assertEqual(n_defs, text.count('raise NotImplementedError("学生実装課題")'), text[:80])
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith(("return", "for ", "if ", "while ")):
                    self.fail(f"学生実装課題のセルに実装らしい行があります: {stripped}")

    def test_no_absolute_paths(self):
        all_text = "\n".join(source(c) for c in self.cells)
        self.assertNotIn("/home/", all_text)
        self.assertNotIn("C:\\", all_text)

    def test_theme_chapters_do_not_reference_other_themes(self):
        """テーマ章のコードは、他のテーマのデータ変数やデータフォルダを使わない"""
        own_vars = {4: "network_", 5: "auth_", 6: "http_", 7: "file", 8: "transfer_"}
        for n in THEMES:
            code_text = "\n".join(source(c) for c, ch in zip(self.cells, self.chapters)
                                  if ch == n and c["cell_type"] == "code")
            for other, prefix in own_vars.items():
                if other == n:
                    continue
                with self.subTest(chapter=n, other=other):
                    self.assertNotIn(f'"{THEME_DATA[other]}"', code_text)
                    self.assertIsNone(re.search(rf"\b{prefix}(records|tiny|small)\b", code_text))


@unittest.skipUnless(importlib.util.find_spec("nbformat"), "nbformat がないためスキップ")
class TestBuildScript(unittest.TestCase):

    def run_build(self, *args):
        import subprocess
        import sys
        return subprocess.run([sys.executable, str(PROJECT_DIR / "scripts" / "build_notebook.py"), *args],
                              capture_output=True, text=True)

    def test_regenerated_notebook_matches(self):
        """生成スクリプトから作り直した Notebook が、リポジトリの Notebook と同じ（再生成可能）"""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "nb.ipynb"
            result = self.run_build("--output", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(out.read_text(encoding="utf-8"), NOTEBOOK.read_text(encoding="utf-8"))

    def test_refuses_to_overwrite_executed_notebook(self):
        """実行結果が残っている（学生が使った）Notebook は上書きしない"""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "student.ipynb"
            nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
            first_code = next(c for c in nb["cells"] if c["cell_type"] == "code")
            first_code["outputs"] = [{"output_type": "stream", "name": "stdout", "text": "学生の実行結果"}]
            first_code["execution_count"] = 1
            out.write_text(json.dumps(nb, ensure_ascii=False), encoding="utf-8")
            before = out.read_text(encoding="utf-8")
            result = self.run_build("--output", str(out))
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(out.read_text(encoding="utf-8"), before)


@unittest.skipUnless(CAN_EXECUTE, "nbformat・nbclient・ipykernel がないため実行テストをスキップ")
class TestExecution(unittest.TestCase):

    def run_cells(self, cells, workdir):
        import nbformat
        from nbclient import NotebookClient
        nb = nbformat.v4.new_notebook()
        nb.cells = [nbformat.from_dict({**c, "source": source(c)}) for c in cells]
        for c in nb.cells:
            if c.cell_type == "code":
                c.outputs, c.execution_count = [], None
        NotebookClient(nb, timeout=180, kernel_name="python3",
                       resources={"metadata": {"path": str(workdir)}}).execute()
        return "\n".join(o.get("text", "") for c in nb.cells if c.cell_type == "code" for o in c.outputs)

    def test_run_all(self):
        """Notebook 全体が、学生実装課題が未実装のままでもエラーなく最後まで実行できる"""
        output = self.run_cells(load_cells(), PROJECT_DIR)
        self.assertIn("[未実装]", output)
        self.assertNotIn("[注意] ファイルが見つかりません", output)

    def test_each_theme_independently(self):
        """第0〜3章 + 1 つのテーマ章だけを、そのテーマのデータだけがある環境で実行できる"""
        cells = load_cells()
        chapters = chapter_of_cells(cells)
        for n, data_dir in THEME_DATA.items():
            with self.subTest(theme=THEMES[n]), tempfile.TemporaryDirectory() as tmp:
                shutil.copytree(PROJECT_DIR / "data" / data_dir, Path(tmp) / "data" / data_dir)
                subset = [c for c, ch in zip(cells, chapters) if ch is not None and (ch <= 3 or ch == n)]
                output = self.run_cells(subset, tmp)
                self.assertNotIn("[注意] ファイルが見つかりません", output)

    def test_each_theme_without_small_dataset(self):
        """Small Dataset（公開データ・人工ログ）がなく、Tiny Dataset だけがある場合も実行できる"""
        cells = load_cells()
        chapters = chapter_of_cells(cells)
        for n, data_dir in THEME_DATA.items():
            with self.subTest(theme=THEMES[n]), tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / "data" / data_dir
                dest.mkdir(parents=True)
                for csv_path in (PROJECT_DIR / "data" / data_dir).glob("*_tiny.csv"):
                    shutil.copy(csv_path, dest)
                subset = [c for c, ch in zip(cells, chapters) if ch is not None and (ch <= 3 or ch == n)]
                output = self.run_cells(subset, tmp)
                self.assertIn("このデータはまだ用意されていません", output)
                self.assertIn("Tiny Dataset", output)

    def test_without_data_folder(self):
        """data フォルダがなくても（Notebook だけを開いた場合）、エラーで止まらない"""
        with tempfile.TemporaryDirectory() as tmp:
            output = self.run_cells(load_cells(), tmp)
            self.assertIn("data フォルダが見つかりません", output)


if __name__ == "__main__":
    unittest.main()
