# 学生配布パッケージの作り方と中身

## 1. 作り方

```bash
cd f1-career-income-optimization
/usr/bin/python3 scripts/build_student_package.py            # 標準ライブラリだけで動く
/usr/bin/python3 scripts/build_student_package.py --force    # 既存の配布物を作り直す
/usr/bin/python3 scripts/build_student_package.py --output-dir <別の場所>   # テスト用
```

| 出力（`dist/` は Git 管理外） | 内容 |
| --- | --- |
| `dist/f1-life-planning-starter/` | 学生配布用フォルダ（ZIP の中身。GitHub では既存のモノレポで配布するため、このフォルダは GitHub に置かない） |
| `dist/f1-life-planning-starter.zip` | LMS 配布用 ZIP（中に `f1-life-planning-starter/` フォルダが 1 つ） |
| `dist/f1-life-planning-starter.sha256` | ZIP の SHA-256 |
| `dist/f1-life-planning-starter_manifest.txt` | ファイル一覧（容量と SHA-256） |

- **許可リスト方式**：`ALLOWLIST` に書いたファイルだけをコピーします。
- 既存の配布物は `--force` なしでは上書きしません。
- シンボリックリンクと、プロジェクトの外を指すパスはコピーしません（エラーで止まる）。
- Notebook は配布用のコピーで、実行結果・実行カウント・教員用メタデータ（生成時の指紋）を消します。教員用マスターは変更しません。
- ZIP の中のファイルの日時を固定しているので、同じ内容なら同じ SHA-256 になります。

## 2. 作成時の自動確認

| 確認 | 内容 |
| --- | --- |
| 未実装の状態 | 学生実装課題のセルの関数が 28 個で、すべて `raise NotImplementedError("学生実装課題")` と TODO が残っている。練習のセルは `None` のまま |
| 出力の消去 | すべてのコードセルの出力が空で、実行カウントが `None` |
| 教員環境の情報 | `/home/`、`/mnt/`、`C:\Users`、`solutions/`、`reference_solutions`、`student_mistakes`、`build_notebook`、`run_reference_check`、`c1-web-attack-detection` を含まない |
| 完成解答の混入 | 参照実装 28 関数と練習 1 つの本体が、配布物のどこにも含まれない |
| 配布しないフォルダ | 許可リストに `solutions/`・`scripts/`・`tests/`・`docs/`・`data/raw/` のファイルがない |

## 3. 含めるもの（17 ファイル）

| ファイル | 種類 |
| --- | --- |
| `README.md`、`TASKS.md`、`requirements.txt` | 学生向けの説明・課題・依存ライブラリ（matplotlib、任意） |
| `F1_life_planning_starter.ipynb` | 配布用 Notebook（出力なし・未実装） |
| `data/README.md`、`data/data_dictionary.md`、`data/dataset_sources.md` | データの説明・データ辞書・公開統計の出典と利用条件 |
| `data/f1a/career_options_tiny.csv` ほか Tiny 6 ファイル | 人工データ |
| `data/f1a/salary_by_age_small.csv` ほか Small 4 ファイル | e-Stat 由来（再配布条件は `docs/dataset_sources.md` 4 章で確認済み） |

## 4. 含めないもの

| 含めないもの | 理由 |
| --- | --- |
| `solutions/`（参照実装・練習の解答・誤りの例） | 完成解答 |
| 旧教材：`career_model.py`、`income_analysis.py`、`optimization.py`、`scenarios.py`、`experiments.py`、`presentation_charts.py`、`starter.py`、`notebooks/`、`data/sample_careers.json`、`docs/legacy/README_legacy.md` | 完成したコード（新 F-1A の解答に相当する部分を含む） |
| `scripts/`、`tests/`、`docs/`、`CLAUDE.md`、`requirements-dev.txt` | 教員用 |
| `data/raw/`（原データの Excel） | 原データ（学生には加工済みの Small だけを配る） |
| `data/f1c/housing_prices_small.csv` | 未取得。取得後も再配布条件を確認するまで含めない |
| `textbook/` | 再配布条件が未確認 |
| `.venv`、`__pycache__`、`.ipynb_checkpoints`、一時ファイル、API キー・秘密情報、Git の履歴 | 配布物に不要・含めてはいけない |

## 5. 配布後の検証（`tests/test_f1_student_package.py`）

配布物を一時フォルダに作り、ZIP を教員用リポジトリの**外**に展開して確かめます。

- 許可リストどおりの 17 ファイル、ZIP と配布フォルダの内容が一致、SHA-256 の記録と再現性、上書きの拒否
- Notebook の出力なし・28 関数が未実装・教員用メタデータなし、教員用マスターが変わらない
- 教員環境の情報・完成解答・シンボリックリンクがない、出典の文書がある
- 展開したフォルダで：全体の実行、第0〜3章＋各テーマ（＋第8章）の単独実行、Small なしの実行、1 つ上のフォルダ（Colab 想定）からの実行
- 展開した Notebook のコピーに参照実装を差し込むと 128 件すべて `[OK]`（配布物は書き換えず、解答入りのファイルを残さない）
