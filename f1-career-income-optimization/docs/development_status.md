# 開発状況

## 現在：Phase 2・3 完了（2026-11-27、未コミット）→ 教員の承認待ち

| 項目 | 状態 |
| --- | --- |
| ブランチ | `feature/f1-integrated-starter`。Phase 1 は `fff67e5`（ローカルのみ）。Phase 2・3 は**未コミット・未 push** |
| Notebook | `F1_life_planning_starter.ipynb`：第0〜9章、Markdown 200・コード 101 セル。学生実装課題 28（各テーマ Level 1 が 4、Level 2 が 3） |
| Tiny Dataset | 6 ファイル（25・6・25・30・24・32 行、計 約 4.5KB）。`generate_synthetic_data.py` でシード固定 |
| データ検証 | `validate_datasets.py`：エラー 0 件、意図的な境界条件 19 件（`docs/data_validation_report.md`） |
| Small Dataset | 取得・前処理済み 4 ファイル（F-1A 84 行、F-1B 156 行、F-1D 39 行・8 行、計 約 30KB）。F-1C は**未取得**（教員の手動取得） |
| 原データ | `data/raw/`（Git 管理外）Excel 4 個、約 2.1MB |
| 参照実装 | `solutions/reference_solutions.py`（Git 管理外）：28 関数。`run_reference_check.py` で動作確認 122 件すべて [OK] |
| テスト | 新教材 27 件（Notebook 18、データ 9）、旧教材 51 件。計 78 件すべて成功 |
| 旧教材 | 変更なし。旧テスト 51 件成功 |
| C-1・他トピック | 変更なし |
| C: の空き | Phase 2・3 開始時 7.6GB → 終了時 9.2GB（他の要因による増加） |

## 検証コマンド（教員の開発環境）

```bash
cd f1-career-income-optimization
PY=../c1-web-attack-detection/.venv/bin/python     # C-1 の既存環境を借用（新しい仮想環境は作らない）
/usr/bin/python3 scripts/generate_synthetic_data.py --check
/usr/bin/python3 scripts/validate_datasets.py --report
$PY scripts/build_notebook.py
$PY -m unittest tests.test_f1_notebook tests.test_f1_synthetic_data -v
$PY scripts/run_reference_check.py
$PY -m unittest tests.test_career_model tests.test_income_analysis tests.test_optimization tests.test_presentation_charts   # 旧教材
```

`tests/` に `__init__.py` がない（旧教材の構成）ため、`unittest discover` は使えない。モジュール名を指定する。

## 検証済み

- 参照実装による全課題の Mini・Tiny の動作確認（122 件 [OK]）
- 未実装のままの Notebook 全体の実行（[エラー] は第3章の例の 1 件だけ）
- 各テーマの単独実行（第0〜3章 + 担当章）、data フォルダなし、Small Dataset なし
- 入力データの書き換えの検出、Mini と Tiny のキー名の一致、参照実装の行が Notebook のコードセルにないこと
- Notebook の再生成の再現性、編集・実行済みの Notebook への上書きの拒否

## 未検証・未実施

- `scripts/preprocess_f1c.py`（実際の CSV がないため一度も実行していない）
- 学生役による試行（ヒントの分かりやすさ、作業時間の実測）
- Windows 側の Jupyter・VS Code、Google Colab での表示と実行（WSL の nbclient でのみ実行）
- テーマ別の本格的な性能比較（Phase 4）、学生配布パッケージ（Phase 5）

## 教員の判断・作業が必要な事項

1. F-1C の不動産取引価格 CSV の手動取得（手順は `docs/preprocessing_report.md` 5 章）と、取得後の再配布条件の確認
2. Small Dataset 4 ファイル（e-Stat 由来）を Git 管理し、学生配布物に含めてよいか（e-Stat 利用規約上は出典と加工の記載で可能）
3. F-1B 課題6（16 行）の分割、または F-1B Level 1 の強化（Phase 4）
4. F-1D 課題4 に `duration_years` を加えた変更（Phase 1 の 16 関数のうち、引数を変えた唯一の関数）
5. 社会生活基本調査（生活時間）を使うか

## 次にやること（承認後）

Phase 4：テーマ別の性能評価、難易度の調整、テストの拡充（`docs/implementation_plan.md`）。
