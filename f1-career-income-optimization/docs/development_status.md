# 開発状況

## 現在：Phase 1 完了（2026-11-27、未コミット）→ 教員の承認待ち

| 項目 | 状態 |
| --- | --- |
| ブランチ | `feature/f1-integrated-starter`（main `c911693` から作成）。**未コミット・未 push** |
| Notebook | `F1_life_planning_starter.ipynb`：第0〜9章、Markdown 146・コード 63 セル。Level 1 の 16 課題（各テーマ 4）にひな形・ヒント・Mini の動作確認 |
| データ | Mini（Notebook 内）4 テーマ分。Tiny 初期版 6 ファイル（計 132 行、48KB 未満） |
| スクリプト | `build_notebook.py`、`generate_synthetic_data.py`、`run_reference_check.py` |
| 参照実装 | `solutions/reference_solutions.py`（Git 管理外）：Level 1 の 16 関数。動作確認 42 件すべて [OK] |
| テスト | 新規 21 件（構造 9・再生成 4・実行 3・データ 5）、旧教材 51 件。計 72 件すべて成功 |
| 文書 | `CLAUDE.md`、`docs/` 10 本、`data/README.md`・`data/data_dictionary.md`、`requirements.txt`・`requirements-dev.txt` |
| 旧教材 | 変更なし（`.gitignore` への追記のみ）。旧テスト 51 件成功、`starter.py` 実行可 |
| C-1・他トピック | 変更なし（`git status` で確認） |
| C: の空き | 開始時 7.8GB → 終了時 7.6GB |

## 検証コマンド（教員の開発環境）

```bash
cd f1-career-income-optimization
PY=../c1-web-attack-detection/.venv/bin/python     # C-1 の既存環境を借用（新しい仮想環境は作らない）
$PY scripts/build_notebook.py
$PY -m unittest tests.test_f1_notebook tests.test_f1_synthetic_data -v
$PY scripts/run_reference_check.py
```

`tests/` に `__init__.py` がない（旧教材の構成）ため、`unittest discover -s tests -t .` は使えない。モジュール名を指定する。

## 未検証・未実施

- Level 2 の課題（候補の一覧のみ）、Tiny の期待値つき動作確認、テーマ別の性能評価（第8章）
- Small Dataset（公開統計）の取得・前処理
- 学生配布パッケージ、README・TASKS の改訂、Google Colab での実行
- Windows 側の Jupyter / VS Code での表示確認（WSL の nbclient でのみ実行）

## 教員の判断が必要な事項

1. ディレクトリ名（`f1-career-income-optimization` のまま／変更）と、親 README の F1 の行・難易度の更新時期
2. 旧教材（`.py`・`notebooks/`・旧 README）の移動先と時期（`docs/migration_plan.md`）
3. 旧コードの完成解答が公開履歴にあることへの対応（評価で説明を重視する、など）
4. Mini と Tiny のキー名の違い（`assets`/`initial_assets`、`years`/`duration_years`）を統一するか
5. Phase 2 の公開統計の範囲（推奨：F-1A 賃金構造基本統計調査、F-1C 不動産取引価格情報。F-1B・F-1D は人工データを優先）
6. F-1B の基本生活時間 77 時間／週などの仮定値

## 次にやること（承認後）

Phase 2：Tiny の完成と `validate_datasets.py`、公開統計の取得・前処理（`docs/implementation_plan.md`）。
