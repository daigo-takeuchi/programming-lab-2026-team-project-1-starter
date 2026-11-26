# C-1：学生配布物（scripts/build_student_package.py）のテスト
#
# 一時フォルダに配布物を作り、ZIP を別の一時フォルダに展開して、教員用リポジトリから切り離した状態で確かめる。
# 配布物の中身のテストは標準ライブラリだけで動く。Notebook の実行テストには nbformat・nbclient・ipykernel が必要。

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
SCRIPT = PROJECT_DIR / "scripts" / "build_student_package.py"
PACKAGE = "c1-cybersecurity-starter"
CAN_EXECUTE = all(importlib.util.find_spec(m) for m in ("nbformat", "nbclient", "ipykernel"))
HAS_SOLUTIONS = (PROJECT_DIR / "solutions" / "reference_solutions.py").exists()

EXPECTED_FILES = {
    "README.md", "TASKS.md", "C1_cybersecurity_starter.ipynb", "requirements.txt",
    "data/README.md", "data/data_dictionary.md",
    "data/c1a/network_flows_tiny.csv", "data/c1b/authentication_tiny.csv",
    "data/c1c/http_requests_tiny.csv", "data/c1c/web_access_log_synthetic.csv",
    "data/c1d/file_states_before_tiny.csv", "data/c1d/file_states_after_tiny.csv",
    "data/c1e/data_transfer_tiny.csv",
}


def files_under(root):
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}


class PackageTestBase(unittest.TestCase):
    """配布物を 1 回だけ作り、ZIP を別のフォルダに展開しておく"""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        out = Path(cls.tmp.name) / "dist"
        result = subprocess.run([sys.executable, str(SCRIPT), "--output-dir", str(out)],
                                capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stdout + result.stderr)
        cls.out = out
        cls.package_dir = out / PACKAGE
        cls.zip_path = out / f"{PACKAGE}.zip"
        cls.extracted = Path(cls.tmp.name) / "student"          # 教員用リポジトリとは別の場所
        with zipfile.ZipFile(cls.zip_path) as zf:
            zf.extractall(cls.extracted)
        cls.student_root = cls.extracted / PACKAGE

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()


class TestPackageContents(PackageTestBase):

    def test_allowlist_only(self):
        """配布フォルダには許可リストのファイルだけがある（旧教材・解答・教員用ファイル・Loghub 由来の CSV を含まない）"""
        self.assertEqual(files_under(self.package_dir), EXPECTED_FILES)

    def test_zip_matches_directory(self):
        """ZIP の中身は配布フォルダと同じ（1 つのフォルダの下に、同じファイル・同じ内容）"""
        with zipfile.ZipFile(self.zip_path) as zf:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            self.assertTrue(all(n.startswith(PACKAGE + "/") for n in names))
            self.assertEqual({n[len(PACKAGE) + 1:] for n in names}, EXPECTED_FILES)
            for name in names:
                self.assertEqual(zf.read(name), (self.out / name).read_bytes(), name)

    def test_checksum_and_reproducible(self):
        """SHA-256 が記録されていて、作り直しても同じ ZIP になる"""
        recorded = (self.out / f"{PACKAGE}.sha256").read_text(encoding="utf-8").split()[0]
        self.assertEqual(recorded, hashlib.sha256(self.zip_path.read_bytes()).hexdigest())
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([sys.executable, str(SCRIPT), "--output-dir", tmp], capture_output=True, check=True)
            self.assertEqual((Path(tmp) / f"{PACKAGE}.zip").read_bytes(), self.zip_path.read_bytes())

    def test_refuses_to_overwrite(self):
        """既存の配布物は --force なしでは上書きしない"""
        before = self.zip_path.read_bytes()
        result = subprocess.run([sys.executable, str(SCRIPT), "--output-dir", str(self.out)],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.zip_path.read_bytes(), before)

    def test_notebook_is_clean(self):
        """配布用 Notebook：出力・実行カウントなし、教員用メタデータなし、課題は未実装のまま"""
        nb = json.loads((self.package_dir / "C1_cybersecurity_starter.ipynb").read_text(encoding="utf-8"))
        self.assertNotIn("c1_generator", nb["metadata"])
        stubs = 0
        for cell in nb["cells"]:
            if cell["cell_type"] == "code":
                self.assertEqual(cell["outputs"], [])
                self.assertIsNone(cell["execution_count"])
                text = "".join(cell["source"])
                if "【学生実装課題" in text:
                    stubs += len(re.findall(r"^def \w+\(", text, re.M))
                    self.assertEqual(len(re.findall(r"^def \w+\(", text, re.M)),
                                     text.count('raise NotImplementedError("学生実装課題")'))
        self.assertEqual(stubs, 33)

    def test_no_teacher_references(self):
        """配布物に教員環境のパス、参照実装、教員用スクリプトへの言及がない"""
        for rel in EXPECTED_FILES:
            text = (self.package_dir / rel).read_text(encoding="utf-8")
            with self.subTest(rel):
                for word in ("/home/", "solutions/", "reference_solutions", "scripts/", "build_notebook",
                             "docs/", "detection.py", "textbook"):
                    self.assertNotIn(word, text)

    @unittest.skipUnless(HAS_SOLUTIONS, "参照実装がない")
    def test_no_solution_bodies(self):
        spec = importlib.util.spec_from_file_location("ref", PROJECT_DIR / "solutions" / "reference_solutions.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        nb_text = (self.package_dir / "C1_cybersecurity_starter.ipynb").read_text(encoding="utf-8")
        for name, code in module.SOLUTIONS.items():
            body = "\n".join(code.strip().splitlines()[1:])
            with self.subTest(name):
                self.assertNotIn(json.dumps(body, ensure_ascii=False)[1:-1], nb_text)

    def test_symlink_is_refused(self):
        """許可リストのファイルがシンボリックリンクなら、コピーせずに止まる"""
        spec = importlib.util.spec_from_file_location("bsp", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "secret.txt"
            target.write_text("secret", encoding="utf-8")
            (Path(tmp) / "link.md").symlink_to(target)
            module.PROJECT_DIR = Path(tmp)
            with self.assertRaises(SystemExit):
                module.checked_source("link.md")


@unittest.skipUnless(CAN_EXECUTE, "nbformat・nbclient・ipykernel がない")
class TestPackageExecution(PackageTestBase):
    """ZIP を展開したフォルダだけで、配布用 Notebook を実行する（教員用リポジトリを参照しない）"""

    def run_cells(self, cells, workdir):
        import nbformat
        from nbclient import NotebookClient
        nb = nbformat.v4.new_notebook()
        nb.cells = [nbformat.from_dict({**c, "source": "".join(c["source"])}) for c in cells]
        env_backup = os.environ.pop("PYTHONPATH", None)
        try:
            NotebookClient(nb, timeout=300, kernel_name="python3",
                           resources={"metadata": {"path": str(workdir)}}).execute()
        finally:
            if env_backup is not None:
                os.environ["PYTHONPATH"] = env_backup
        return "\n".join(o.get("text", "") for c in nb.cells if c.cell_type == "code" for o in c.outputs)

    def cells_and_chapters(self):
        cells = json.loads((self.student_root / "C1_cybersecurity_starter.ipynb").read_text(encoding="utf-8"))["cells"]
        chapters, chapter = [], None
        for cell in cells:
            m = re.match(r"# 第(\d+)章", "".join(cell["source"])) if cell["cell_type"] == "markdown" else None
            if m:
                chapter = int(m.group(1))
            chapters.append(chapter)
        return cells, chapters

    def test_run_all_unimplemented(self):
        """展開した配布物で Notebook 全体が最後まで動き、未実装は [未実装] と表示される（公開ログなし）"""
        cells, _ = self.cells_and_chapters()
        output = self.run_cells(cells, self.student_root)
        self.assertIn("データフォルダ: OK", output)
        self.assertIn("[未実装]", output)
        self.assertIn("このデータはまだ用意されていません", output)      # 公開ログがない場合の表示
        self.assertNotIn("[注意] ファイルが見つかりません", output)

    def test_each_theme_independently(self):
        """展開した配布物で、第0〜3章＋各テーマの章だけを実行できる"""
        cells, chapters = self.cells_and_chapters()
        for n in range(4, 9):
            with self.subTest(chapter=n):
                subset = [c for c, ch in zip(cells, chapters) if ch is not None and (ch <= 3 or ch == n)]
                output = self.run_cells(subset, self.student_root)
                self.assertIn("[未実装]", output)
                self.assertNotIn("[注意] ファイルが見つかりません", output)

    def test_colab_style_parent_folder(self):
        """教材フォルダの 1 つ上（Colab の /content のような場所）で実行しても data を見つける"""
        cells, chapters = self.cells_and_chapters()
        subset = [c for c, ch in zip(cells, chapters) if ch is not None and ch <= 1]
        output = self.run_cells(subset, self.extracted)
        self.assertIn("データフォルダ: OK", output)

    @unittest.skipUnless(HAS_SOLUTIONS, "参照実装がない")
    def test_reference_solutions_on_package(self):
        """展開した配布用 Notebook のコピーに参照実装を差し込むと、すべて [OK]（配布物は書き換えない）"""
        nb_path = self.student_root / "C1_cybersecurity_starter.ipynb"
        before = nb_path.read_bytes()
        result = subprocess.run([sys.executable, str(PROJECT_DIR / "scripts" / "run_reference_check.py"),
                                 "--notebook", str(nb_path), "--workdir", str(self.student_root)],
                                capture_output=True, text=True, timeout=900)
        self.assertEqual(result.returncode, 0, result.stdout[-3000:] + result.stderr[-2000:])
        self.assertEqual(nb_path.read_bytes(), before)
        self.assertEqual(files_under(self.student_root), EXPECTED_FILES)   # 解答入りのファイルを残さない


if __name__ == "__main__":
    unittest.main()
