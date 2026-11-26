# 実装計画

各 Phase の終わりに実装状況を報告し、教員の承認を得てから次に進む。

| Phase | 内容 | 主な成果物 | 状態 |
| --- | --- | --- | --- |
| 1 | 既存教材の監査、C-1 の再利用調査、4 分類への統合、仕様、公開統計の調査、Notebook の骨格、Mini、Tiny の初期設計 | `CLAUDE.md`、`docs/*`、`scripts/build_notebook.py`、`F1_life_planning_starter.ipynb`、Tiny 初期版、テスト | **完了（2026-11-27、未コミット）** |
| 2 | データセットの準備 | Tiny の完成、`validate_datasets.py`、公開統計の取得と前処理（`download_datasets.py`・`preprocess_f1a〜d.py`）、`data/data_dictionary.md`、`docs/preprocessing_policy.md`・`preprocessing_report.md` | 未着手 |
| 3 | Starter Code の実装 | 全 4 テーマの Level 2（2〜3 課題）、ヒントの見直し、Tiny の期待値つき動作確認、Level 3 の発展案、チーム独自機能の候補 | 未着手 |
| 4 | 性能評価・参照実装・教育的検証 | `solutions/reference_solutions.py`（全関数）、探索の比較（特に F-1C）、計算量の説明、可視化、難易度の調整、テストの拡充 | 未着手（Level 1 の参照実装は Phase 1 で作成済み） |
| 5 | 学生配布準備・最終検証 | README・TASKS（100 点の評価案）、`docs/teacher_guide.md`・`student_package_guide.md`、`build_student_package.py`、`dist/f1-life-planning-starter/` と ZIP、`final_validation_report.md` | 未着手 |

## Phase 2 の詳細

1. Tiny の見直し：件数・分布・境界条件（F-1A：回収年齢が存在しない候補、F-1C：予算と同じ価格、F-1D：親の最低資産を下回る家族）。
2. `scripts/validate_datasets.py`：列・型・単位の範囲・ID の重複・境界条件の存在を検査。
3. 公開統計（API は使わず、画面からの Excel/CSV のダウンロード）：
   - F-1A 賃金構造基本統計調査（年齢階級別）→ `salary_by_age_small.csv`
   - F-1C 不動産取引価格情報（1〜2 市区町村）→ `housing_prices_small.csv`
   - F-1B・F-1D は取得が容易な表が見つかった場合のみ（人工データを優先）
4. 前処理スクリプトは `data/raw/`（Git 管理外）から読み、学生が計算すべき集計値を作らない。
5. Excel の読み込みに追加ライブラリ（openpyxl など）が必要な場合は、事前に教員の承認を得る（標準ライブラリの `zipfile` + XML で読む方法も検討）。

## Phase 3 の詳細

- Level 2 の関数（`docs/project_specification.md` の候補から各テーマ 2〜3 個）に、ひな形・3 段階のヒント・Mini と Tiny の動作確認を付ける。
- F-1C は二分探索（upper bound）の課題と、線形探索との比較（1 回／Q 回、ソートの時間を含む）を必ず入れる。
- Tiny の期待値を `build_notebook.py` に直接書く（データを作り直したら見直す）。
- Mini と Tiny のキー名の違い（`assets`/`initial_assets` など）の扱いを決める。

## 想定作業量（見積もり）

| Phase | 規模 |
| --- | --- |
| 2 | 中（公開統計 2 種類の取得・前処理が中心。表の構造の調査に時間がかかる可能性） |
| 3 | 大（Level 2 の 10 前後の関数、ヒント、期待値） |
| 4 | 中 |
| 5 | 中（C-1 の配布機構を改訂） |
