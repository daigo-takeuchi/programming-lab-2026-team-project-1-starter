# C-1：教員用参照実装による検証（教員の環境だけで実行される）
#
# solutions/reference_solutions.py（Git 管理外）がない環境ではスキップする。
# 参照実装を Notebook のコピーに差し込んで実行し、第4〜8章の動作確認がすべて [OK] になることを確かめる。
# あわせて、参照実装（完成解答）が配布用 Notebook に混ざっていないことを確かめる。

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
SOLUTIONS = PROJECT_DIR / "solutions" / "reference_solutions.py"
NOTEBOOK = PROJECT_DIR / "C1_cybersecurity_starter.ipynb"
CAN_EXECUTE = all(importlib.util.find_spec(m) for m in ("nbformat", "nbclient", "ipykernel"))


def load_solutions():
    spec = importlib.util.spec_from_file_location("reference_solutions", SOLUTIONS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.SOLUTIONS


@unittest.skipUnless(SOLUTIONS.exists(), "参照実装（教員用、Git 管理外）がない")
class TestReferenceSolutions(unittest.TestCase):

    def test_all_student_functions_have_reference(self):
        """Level 1（20 関数）・Level 2（13 関数）のすべてに参照実装がある"""
        self.assertEqual(len(load_solutions()), 33)

    def test_solutions_not_in_notebook(self):
        """参照実装の本体（def 行以外）が、配布用 Notebook のどこにも含まれていない"""
        notebook_text = json.dumps(json.loads(NOTEBOOK.read_text(encoding="utf-8")), ensure_ascii=False)
        for name, code in load_solutions().items():
            body = "\n".join(code.strip().splitlines()[1:])
            with self.subTest(name=name):
                self.assertNotIn(json.dumps(body, ensure_ascii=False)[1:-1], notebook_text)

    @unittest.skipUnless(CAN_EXECUTE, "nbformat・nbclient・ipykernel がない")
    def test_notebook_all_ok_with_reference(self):
        """参照実装を差し込むと、第4〜8章の動作確認（Mini・Tiny・Level 1・2・速度比較）がすべて [OK]"""
        result = subprocess.run([sys.executable, str(PROJECT_DIR / "scripts" / "run_reference_check.py")],
                                capture_output=True, text=True, cwd=PROJECT_DIR, timeout=900)
        self.assertEqual(result.returncode, 0, result.stdout[-3000:] + result.stderr[-2000:])
        self.assertIn("すべての動作確認が [OK] でした", result.stdout)


if __name__ == "__main__":
    unittest.main()
