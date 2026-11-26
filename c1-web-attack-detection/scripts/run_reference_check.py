"""【教員用】参照実装を差し込んで Notebook を実行し、すべての動作確認が [OK] になるかを確かめる

- 参照実装：solutions/reference_solutions.py（Git 管理外。学生に配布しない）
- 配布用 Notebook（C1_cybersecurity_starter.ipynb）は**書き換えない**。メモリ上のコピーに、
  学生実装課題のセルの直後に参照実装のセルを差し込んで実行する。
- 第3章の使い方の例（わざと [NG]・[未実装]・[エラー] を出すセル）は集計から除く。

使い方（c1-web-attack-detection ディレクトリで実行する）:
    .venv/bin/python scripts/run_reference_check.py
    .venv/bin/python scripts/run_reference_check.py --save results/reference_run.ipynb   # 実行結果を保存して目で確認する
      （results/ は Git 管理外。保存したファイルには参照実装が含まれるので、学生に配布しないこと）

終了コード：すべて [OK] なら 0、そうでなければ 1
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import nbformat
from nbclient import NotebookClient

PROJECT_DIR = Path(__file__).resolve().parent.parent
NOTEBOOK = PROJECT_DIR / "C1_cybersecurity_starter.ipynb"
SOLUTIONS_DIR = PROJECT_DIR / "solutions"
TAGS = ("[OK]", "[NG]", "[未実装]", "[エラー]")


def load_solutions():
    sys.path.insert(0, str(SOLUTIONS_DIR))
    try:
        from reference_solutions import SOLUTIONS
    except ImportError:
        raise SystemExit("solutions/reference_solutions.py がありません（教員用の参照実装）。")
    return SOLUTIONS


def build_notebook_with_solutions(solutions, notebook_path=NOTEBOOK):
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
    unused = set(solutions) - used
    if unused:
        raise SystemExit(f"Notebook に存在しない関数の参照実装: {sorted(unused)}")
    return nb, used


def run(nb, workdir):
    NotebookClient(nb, timeout=600, kernel_name="python3",
                   resources={"metadata": {"path": str(workdir)}}).execute()
    chapter, counts, problems = None, Counter(), []
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            m = re.match(r"# 第(\d+)章", cell.source)
            if m:
                chapter = int(m.group(1))
            continue
        for output in cell.get("outputs", []):
            if output.get("output_type") == "error":
                problems.append(f"第{chapter}章：例外 {output.get('ename')}: {output.get('evalue')}")
            text = output.get("text", "")
            if chapter is None or chapter < 4:      # 第3章までの使い方の例は集計しない
                continue
            for tag in TAGS:
                counts[(chapter, tag)] += text.count(tag)
            for line in text.splitlines():
                if line.startswith(("[NG]", "[未実装]", "[エラー]")):
                    problems.append(f"第{chapter}章：{line}")
    return counts, problems


def main():
    parser = argparse.ArgumentParser(description="参照実装による Notebook の検証（教員用）")
    parser.add_argument("--save", help="実行済みのコピーを保存するパス（例：results/reference_run.ipynb）")
    parser.add_argument("--workdir", default=str(PROJECT_DIR), help="Notebook を実行するフォルダ（data/ がある場所）")
    parser.add_argument("--notebook", default=str(NOTEBOOK), help="検証する Notebook（例：学生配布用フォルダの Notebook）。ファイルは書き換えない")
    args = parser.parse_args()

    nb, used = build_notebook_with_solutions(load_solutions(), Path(args.notebook))
    counts, problems = run(nb, Path(args.workdir))
    print(f"参照実装を差し込んだ関数: {len(used)} 個")
    for chapter in range(4, 10):
        row = "  ".join(f"{tag} {counts[(chapter, tag)]}" for tag in TAGS)
        print(f"第{chapter}章: {row}")
    if args.save:
        if Path(args.save).resolve() in (NOTEBOOK.resolve(), Path(args.notebook).resolve()):
            raise SystemExit("配布用 Notebook には保存できません。")
        nbformat.write(nb, args.save)
        print("保存:", args.save, "（参照実装を含むので配布しないこと）")
    if problems:
        print("問題:")
        for p in problems:
            print("  ", p)
        sys.exit(1)
    print("すべての動作確認が [OK] でした。")


if __name__ == "__main__":
    main()
