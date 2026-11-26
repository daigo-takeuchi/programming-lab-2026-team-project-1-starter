# 実装計画

各 Phase の終わりに実装状況を報告し、教員の承認を得てから次に進む。

| Phase | 内容 | 主な成果物 | 状態 |
| --- | --- | --- | --- |
| 1 | 既存教材の監査、C-1 の再利用調査、4 分類への統合、仕様、公開統計の調査、Notebook の骨格、Mini、Tiny の初期設計 | `CLAUDE.md`、`docs/*`、`scripts/build_notebook.py`、Notebook、Tiny 初期版、テスト | 完了（`fff67e5`） |
| 2 | データセットの準備 | Tiny の完成、`validate_datasets.py`、`download_datasets.py`・`xlsx_reader.py`・`preprocess_*.py`、Small 4 ファイル、データ辞書、前処理の方針と結果 | **完了（2026-11-27、未コミット）**。F-1C の実データは教員の手動取得待ち |
| 3 | Starter Code の実装 | 全 4 テーマの Level 1・2（28 関数）、3 段階のヒント、Mini と Tiny の動作確認、可視化、Level 3 の発展案、独自機能の候補、参照実装（28 関数） | **完了（2026-11-27、未コミット）** |
| 4 | 性能評価・参照実装・教育的検証 | テーマ別の性能比較（第8章、件数と時間のグラフ）、計算量の説明の充実、難易度の調整、テストの拡充、学生役による試行 | 未着手 |
| 5 | 学生配布準備・最終検証 | README・TASKS（100 点の評価案。出典・変更点・説明・テスト・独自機能を評価）、`docs/teacher_guide.md`・`student_package_guide.md`、`build_student_package.py`、`dist/f1-life-planning-starter/` と ZIP、親 README の F1 の更新、`final_validation_report.md` | 未着手 |

## Phase 4 の詳細

1. 第8章：F-1A（N 候補の O(N × T)）、F-1B（k² × m）、F-1C（線形探索と二分探索、Q を変える、ソートの時間を含む）、F-1D（S × T）の
   Benchmark Dataset をメモリ上で生成し、件数と実行時間のグラフ（`plot_lines`）を作る。結果が同じことを確かめてから比べる。
2. 難易度の調整：参照実装の行数、ヒントの量、各テーマの作業時間の見積もりの見直し。F-1B の Level 1 の厚み。
3. 学生が書きそうな誤り（境界の `<` と `<=`、安定でないソート、入力の書き換え）で `[NG]` になることのテスト。
4. Notebook の表示確認（Windows の VS Code・Jupyter、Google Colab）。

## Phase 5 の詳細

- C-1 の `build_student_package.py` を改訂（許可リスト：Notebook、README、TASKS、requirements、data/README、data_dictionary、Tiny 6、Small 4）。
- 旧教材・`scripts/`・`docs/`・`solutions/`・`data/raw/` は配布しない。
- README を新教材の内容にし、旧 README を `docs/legacy/` へ（承認済みの方針に従い、移動・削除は改めて確認）。
