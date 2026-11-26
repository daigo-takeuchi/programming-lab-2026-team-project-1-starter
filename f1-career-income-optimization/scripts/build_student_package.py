"""【教員用】学生配布用のフォルダと ZIP を作る

- **許可リスト方式**：下の ALLOWLIST に書いたファイルだけをコピーする。それ以外（旧教材の .py・notebooks・旧 README、
  solutions/（参照実装・誤りの例）、教員用スクリプト、テスト、docs、原データ data/raw/、F-1C の取引価格データ、
  仮想環境、キャッシュ、チェックポイントなど）は、何もしなくても含まれない。
- シンボリックリンクや、プロジェクトの外を指すパスはコピーしない（エラーにする）。
- Notebook は配布用のコピーで、実行結果・実行カウント・教員用のメタデータを消す（教員用の Notebook は変更しない）。
- 作成後に、学生実装課題が未実装のままであることと、参照実装（solutions/、あれば）が混ざっていないことを確かめる。
- ZIP は、中のファイルの日時を固定して作る（同じ内容なら同じ SHA-256 になる）。
- 既存の配布物は上書きしない（--force を付けたときだけ作り直す）。

出力（既定。dist/ は Git 管理外）:
    dist/f1-life-planning-starter/          学生配布用フォルダ（ZIP の中身。GitHub では既存のモノレポの f1-career-income-optimization/ で配布）
    dist/f1-life-planning-starter.zip       LMS 配布用 ZIP（中に f1-life-planning-starter/ フォルダが 1 つ）
    dist/f1-life-planning-starter.sha256    ZIP の SHA-256
    dist/f1-life-planning-starter_manifest.txt  ファイル一覧（容量と SHA-256）

使い方（f1-career-income-optimization ディレクトリで。標準ライブラリだけで動く）:
    python3 scripts/build_student_package.py
    python3 scripts/build_student_package.py --force               # 既存の配布物を作り直す
    python3 scripts/build_student_package.py --output-dir /tmp/x   # 別の場所に作る（テスト用）
"""

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
PACKAGE_NAME = "f1-life-planning-starter"
NOTEBOOK_NAME = "F1_life_planning_starter.ipynb"
N_TASKS = 28              # 学生実装課題の関数の数

ALLOWLIST = [
    "README.md",
    "TASKS.md",
    NOTEBOOK_NAME,
    "requirements.txt",
    "data/README.md",
    "data/data_dictionary.md",
    "data/dataset_sources.md",
    # Tiny Dataset（人工データ）
    "data/f1a/career_options_tiny.csv",
    "data/f1b/work_options_tiny.csv",
    "data/f1b/household_scenarios_tiny.csv",
    "data/f1c/housing_options_tiny.csv",
    "data/f1d/family_members_tiny.csv",
    "data/f1d/transfer_scenarios_tiny.csv",
    # Small Dataset（e-Stat 由来。再配布条件は docs/dataset_sources.md 4 章で確認済み）
    "data/f1a/salary_by_age_small.csv",
    "data/f1b/household_expenses_small.csv",
    "data/f1d/household_assets_small.csv",
    "data/f1d/learning_cost_small.csv",
    # F-1C の取引価格データ（housing_prices_small.csv）は、再配布条件を確認するまで含めない
]
FORBIDDEN_WORDS = ("/home/", "/mnt/", "C:\\Users", "solutions/", "reference_solutions", "student_mistakes",
                   "build_notebook", "run_reference_check", "c1-web-attack-detection")
ZIP_DATE = (2026, 1, 1, 0, 0, 0)   # ZIP 内のファイルの日時（固定）


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def checked_source(rel_path):
    """許可リストのパスを確かめて、コピー元の Path を返す（リンクやプロジェクト外は拒否）"""
    path = PROJECT_DIR / rel_path
    if path.is_symlink():
        raise SystemExit(f"シンボリックリンクはコピーしません: {rel_path}")
    if not path.is_file():
        raise SystemExit(f"許可リストのファイルがありません: {rel_path}")
    if PROJECT_DIR.resolve() not in path.resolve().parents:
        raise SystemExit(f"プロジェクトの外を指しています: {rel_path}")
    return path


def clean_notebook(data):
    """配布用 Notebook：実行結果・実行カウント・教員用メタデータを消す"""
    nb = json.loads(data.decode("utf-8"))
    for cell in nb["cells"]:
        cell["metadata"] = {}
        if cell["cell_type"] == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
    nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                      "language_info": {"name": "python"}}
    return (json.dumps(nb, ensure_ascii=False, indent=1) + "\n").encode("utf-8")


def verify(files):
    """配布物の内容を確かめる。問題があればエラーにする。"""
    nb = json.loads(files[NOTEBOOK_NAME].decode("utf-8"))
    n_stubs = 0
    for cell in nb["cells"]:
        text = "".join(cell["source"])
        if cell["cell_type"] == "code":
            if cell["outputs"] or cell["execution_count"] is not None:
                raise SystemExit("Notebook に実行結果が残っています")
            if "【学生実装課題" in text:
                n_defs = len(re.findall(r"^def \w+\(", text, re.M))
                n_stubs += n_defs
                if n_defs != text.count('raise NotImplementedError("学生実装課題")') or "TODO" not in text:
                    raise SystemExit("学生実装課題が未実装の状態になっていません: " + text.splitlines()[0])
            if "【練習：" in text and "= None" not in text:
                raise SystemExit("練習のセルが未完成の状態になっていません: " + text.splitlines()[0])
    if n_stubs != N_TASKS:
        raise SystemExit(f"学生実装課題の関数の数が {n_stubs} です（{N_TASKS} のはず）")
    all_text = "\n".join(b.decode("utf-8") for b in files.values())
    for word in FORBIDDEN_WORDS:
        if word in all_text:
            raise SystemExit(f"配布物に教員環境の情報が含まれています: {word}")
    solutions_path = PROJECT_DIR / "solutions" / "reference_solutions.py"
    if solutions_path.exists():
        spec = importlib.util.spec_from_file_location("reference_solutions", solutions_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        notebook_json = files[NOTEBOOK_NAME].decode("utf-8")
        bodies = {name: "\n".join(code.strip().splitlines()[1:]) for name, code in module.SOLUTIONS.items()}
        bodies.update({f"練習 {k}": code.strip() for k, code in getattr(module, "PRACTICE", {}).items()})
        for name, body in bodies.items():
            if body in all_text or json.dumps(body, ensure_ascii=False)[1:-1] in notebook_json:
                raise SystemExit(f"参照実装（{name}）が配布物に含まれています")
        return len(bodies)
    return 0


def main():
    parser = argparse.ArgumentParser(description="学生配布用のフォルダと ZIP を作る（教員用）")
    parser.add_argument("--output-dir", default=str(PROJECT_DIR / "dist"), help="出力先（既定：dist/）")
    parser.add_argument("--force", action="store_true", help="既存の配布物を作り直す")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    package_dir = out_dir / PACKAGE_NAME
    zip_path = out_dir / f"{PACKAGE_NAME}.zip"
    sha_path = out_dir / f"{PACKAGE_NAME}.sha256"
    manifest_path = out_dir / f"{PACKAGE_NAME}_manifest.txt"
    existing = [p for p in (package_dir, zip_path, sha_path, manifest_path) if p.exists()]
    if existing and not args.force:
        raise SystemExit("配布物がすでにあります（上書きしません）: " + ", ".join(str(p) for p in existing)
                         + "\n作り直す場合は --force を付けてください。")

    files = {}
    for rel_path in ALLOWLIST:
        if "/raw/" in rel_path or rel_path.startswith(("solutions/", "scripts/", "tests/", "docs/")):
            raise SystemExit(f"配布しないフォルダのファイルが許可リストにあります: {rel_path}")
        data = checked_source(rel_path).read_bytes()
        files[rel_path] = clean_notebook(data) if rel_path == NOTEBOOK_NAME else data
    n_checked = verify(files)

    if package_dir.exists():
        shutil.rmtree(package_dir)        # --force のときだけここに来る（このスクリプトが作ったフォルダ）
    for rel_path, data in files.items():
        dest = package_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel_path in sorted(files):
            info = zipfile.ZipInfo(f"{PACKAGE_NAME}/{rel_path}", date_time=ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, files[rel_path])
    zip_sha = sha256_bytes(zip_path.read_bytes())
    sha_path.write_text(f"{zip_sha}  {zip_path.name}\n", encoding="utf-8")

    lines = [f"{PACKAGE_NAME}：{len(files)} ファイル、合計 {sum(len(d) for d in files.values()):,} バイト",
             f"ZIP：{zip_path.name}、{zip_path.stat().st_size:,} バイト、SHA-256 {zip_sha}", ""]
    for rel_path in sorted(files):
        lines.append(f"{len(files[rel_path]):>9,}  {sha256_bytes(files[rel_path])}  {rel_path}")
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines[:2]))
    print(f"作成: {package_dir}")
    print(f"作成: {zip_path}")
    print("確認: Notebook の実行結果なし、学生実装課題は未実装のまま、"
          + (f"参照実装 {n_checked} 関数の混入なし" if n_checked else "参照実装がないため混入チェックは省略"))


if __name__ == "__main__":
    sys.exit(main())
