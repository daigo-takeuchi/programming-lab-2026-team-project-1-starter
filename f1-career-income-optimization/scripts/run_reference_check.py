"""【教員用】参照実装を差し込んで Notebook を実行し、すべての動作確認が [OK] になるかを確かめる

- 参照実装：solutions/reference_solutions.py（Git 管理外。学生に配布しない）
- 配布用 Notebook（F1_life_planning_starter.ipynb）は**書き換えない**。メモリ上のコピーに、
  学生実装課題のセルの直後に参照実装のセルを差し込んで実行する。
- 第3章の使い方の例（わざと [NG]・[未実装]・[エラー] を出すセル）は集計から除く。
- C-1 の scripts/run_reference_check.py を F-1 向けに書き直したもの（C-1 には依存しない）。

使い方（f1-career-income-optimization ディレクトリで）:
    <python> scripts/run_reference_check.py

終了コード：すべて [OK] なら 0、そうでなければ 1
必要なライブラリ：nbformat、nbclient、ipykernel（教員の開発環境のみ）
"""

import re
import sys
from collections import Counter
from pathlib import Path

import nbformat
from nbclient import NotebookClient

PROJECT_DIR = Path(__file__).resolve().parent.parent
NOTEBOOK = PROJECT_DIR / "F1_life_planning_starter.ipynb"
SOLUTIONS_DIR = PROJECT_DIR / "solutions"
TAGS = ("[OK]", "[NG]", "[未実装]", "[エラー]")


def load_solutions():
    sys.path.insert(0, str(SOLUTIONS_DIR))
    try:
        from reference_solutions import SOLUTIONS
    except ImportError:
        raise SystemExit("solutions/reference_solutions.py がありません（教員用の参照実装）。")
    return SOLUTIONS


def notebook_with_solutions(solutions, notebook_path=NOTEBOOK):
    nb = nbformat.read(notebook_path, as_version=4)
    cells, used = [], set()
    for cell in nb.cells:
        cells.append(cell)
        if cell.cell_type == "code" and "【学生実装課題" in cell.source:
            names = re.findall(r"^def (\w+)\(", cell.source, re.M)
            missing = [n for n in names if n not in solutions]
            if missing:
                raise SystemExit(f"参照実装がない関数: {missing}")
            used.update(names)
            cells.append(nbformat.v4.new_code_cell("\n".join(solutions[n] for n in names)))
    nb.cells = cells
    return nb, used


def run(nb):
    NotebookClient(nb, timeout=300, kernel_name="python3",
                   resources={"metadata": {"path": str(PROJECT_DIR)}}).execute()
    counts = Counter()
    for cell in nb.cells:
        if cell.cell_type != "code" or "わざと" in cell.source:
            continue
        for out in cell.get("outputs", []):
            text = out.get("text", "")
            for line in text.splitlines():
                for tag in TAGS:
                    if line.startswith(tag):
                        counts[tag] += 1
    return counts


def main():
    solutions = load_solutions()
    nb, used = notebook_with_solutions(solutions)
    counts = run(nb)
    print(f"参照実装を差し込んだ関数: {len(used)} 個")
    for tag in TAGS:
        print(f"{tag}: {counts[tag]}")
    ok = counts["[OK]"] > 0 and all(counts[t] == 0 for t in TAGS[1:])
    print("結果:", "すべて [OK]" if ok else "問題あり")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
