# 開発状況

## 現在：F-1 統合 Starter v1.0 開発完了（Phase 1〜5、2026-11-27）→ 既存の GitHub モノレポへの統合作業中（feature ブランチ → Pull Request → main）

未実施・未検証（検証済みではない）：F-1C の実データの取得と `preprocess_f1c.py` の実データでの検証、Windows ネイティブ・Google Colab の実機、教員・学生による試行。

| 項目 | 状態 |
| --- | --- |
| ブランチ | `feature/f1-integrated-starter`。Phase 1 `fff67e5`、Phase 2・3 `e5bffc6`（ローカルのみ、未 push）。Phase 4・5 は**未コミット** |
| Notebook | `F1_life_planning_starter.ipynb`：第0〜9章、Markdown 242・コード 124 セル。学生実装課題 28 + F-1B の練習 1。第8章に 4 テーマの性能評価 |
| Tiny Dataset | 6 ファイル（25・6・25・30・24・32 行）。検証：エラー 0 件、境界条件 19 件 |
| Small Dataset | e-Stat 由来 4 ファイル（84・156・39・8 行）。再配布条件を個別に確認し、Git 管理・配布に収録。F-1C の実データは未取得 |
| 参照実装 | `solutions/`（Git 管理外）：28 関数 + 練習 1、動作確認 128 件すべて [OK]。誤りの例 17 種類（`student_mistakes.py`） |
| テスト | 新教材 49 件（Notebook 22、データ 9、誤りの検出 3、配布物 15）＋ 旧教材 51 件 = 100 件すべて成功 |
| 学生配布物 | `dist/f1-life-planning-starter/`（17 ファイル、406,654 バイト）と ZIP（102,067 バイト、SHA-256 `7fe5dc0d…33c1`。README を既存モノレポの取得手順に直して再生成）。Git 管理外。再生成：`/usr/bin/python3 scripts/build_student_package.py --force` |
| 学生向け文書 | `README.md`（新）、`TASKS.md`（新）、`data/README.md`・`data_dictionary.md`・`dataset_sources.md`。旧 README は `docs/legacy/README_legacy.md` |
| 親 README | F1 の説明行 2 行だけを更新 |
| 旧教材・C-1・他トピック | 変更なし（旧テスト 51 件成功） |
| C: の空き | Phase 4・5 開始時 9.1GB → 終了時 9.0GB |

## 検証コマンド（教員の開発環境）

```bash
cd f1-career-income-optimization
PY=../c1-web-attack-detection/.venv/bin/python     # C-1 の既存環境を借用（新しい仮想環境は作らない）
/usr/bin/python3 scripts/generate_synthetic_data.py --check
/usr/bin/python3 scripts/validate_datasets.py --report
$PY scripts/build_notebook.py
$PY -m unittest tests.test_f1_notebook tests.test_f1_synthetic_data tests.test_f1_student_mistakes tests.test_f1_student_package
$PY scripts/run_reference_check.py                 # 128 件 [OK]（第8章の性能評価も実行、約 20 秒）
$PY -m unittest tests.test_career_model tests.test_income_analysis tests.test_optimization tests.test_presentation_charts   # 旧教材
/usr/bin/python3 scripts/build_student_package.py --force
```

`tests/` に `__init__.py` がない（旧教材の構成）ため、`unittest discover` は使えない。モジュール名を指定する。

## 未検証・未実施

- `scripts/preprocess_f1c.py`（実際の CSV がないため一度も実行していない）
- 学生・教員による試行（チェックリストは `docs/educational_validation_report.md` 4 章）、作業時間の実測
- Windows ネイティブの VS Code・Jupyter、Google Colab、Python 3.12 以外での実行（WSL の nbclient でのみ実行）
- LMS へのアップロード（教員が行う）。GitHub は既存のモノレポに統合する方針（F-1 専用リポジトリは作らない）

## 教員の残作業

`docs/final_validation_report.md` 7 章。
