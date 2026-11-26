# C-1 教材からの再利用（Phase 1、2026-11-27）

C-1（`../c1-web-attack-detection/`、main `c911693`）は**読み取り専用**で参照した。ファイルのコピーはせず、必要な部分を F-1 向けに書き直した。
F-1 の学生向け Notebook・スクリプト・テストは C-1 のファイルに依存しない（教員の開発環境として C-1 の `.venv` を借用しているだけ）。

| C-1 の機能・ファイル | F-1 での利用方法 | 再利用・改訂・新規作成 | 実装状況 |
| --- | --- | --- | --- |
| `scripts/build_notebook.py` の `md()`・`code()`・`hints()` | 同じ仕組みで F-1 の Notebook を生成 | 改訂（ヒント2 を「文法・データ構造」に） | Phase 1 実装済み |
| 同 `theme_chapter()`・`emit_task()` | 10 節・5 STEP のテーマ章テンプレート。章冒頭の要約表を追加 | 改訂 | Phase 1 実装済み（Level 2 のひな形は Phase 3） |
| 同 セル ID の連番固定・`source_fingerprint`・`overwrite_problem` | 再生成の再現性と、学生が編集した Notebook の上書き防止。メタデータのキーを `f1_generator` に | 再利用（キー名のみ変更） | Phase 1 実装済み・テスト済み |
| 第1章（環境確認、`BASE_DIR` の探索、日本語フォント） | フォルダ名の候補を F-1 用に変更 | 改訂 | Phase 1 実装済み |
| 第3章 `load_csv`・`show_records` | `float_columns` を追加（年収・昇給率・家賃） | 改訂 | Phase 1 実装済み |
| 第3章 `check`（[OK]／[NG]／[未実装]／[エラー]） | 小数の許容誤差（`math.isclose`）、引数の書き換えの検出を追加 | 改訂 | Phase 1 実装済み |
| `_describe_difference` | 数値の差を表示する分岐を追加 | 改訂 | Phase 1 実装済み |
| `measure_time`・`compare_speed` | 第8章・Level 2 の速度比較。結果の一致判定を許容誤差つきに | 改訂 | Phase 1 実装済み（テーマ別の比較は Phase 4） |
| `plot_bars`・`plot_speed`・`jp` | `plot_lines`（年次推移）を追加 | 改訂・新規 | Phase 1 実装済み（`plot_speed` 相当は Phase 4） |
| `evaluate_detection`・`show_evaluation`（混同行列） | **使わない**（F-1 はシミュレーションの評価） | 不採用 | ― |
| `small_loader()`（Small がなくても止まらない） | 同じ方式 | 再利用 | Phase 1 実装済み |
| Mini（Notebook 内）／Tiny（CSV）／Small／Benchmark の 4 層 | 同じ方針 | 再利用 | Mini・Tiny 初期版は Phase 1、Small は Phase 2、Benchmark は Phase 4 |
| `scripts/generate_synthetic_data.py`（シード固定） | F-1 の Tiny 6 ファイル。`--check` で再現性を確認 | 新規作成（方式のみ再利用） | Phase 1 初期版 |
| `scripts/validate_datasets.py` | Tiny・Small の検証 | 改訂予定 | Phase 2（Phase 1 は unittest で代用） |
| `scripts/download_datasets.py`・`preprocess_*.py`・`preprocess_common.py` | 公開統計の取得・前処理（Excel の読み込みが必要になる可能性） | 改訂予定 | Phase 2 |
| `scripts/run_reference_check.py` | 参照実装をメモリ上のコピーに差し込んで実行 | 改訂 | Phase 1 実装済み（Level 1 の 16 関数、42 件 [OK]） |
| `solutions/reference_solutions.py`（Git 管理外） | 同じ形式（関数名 → ソースの文字列） | 新規作成 | Phase 1：Level 1 の 16 関数 |
| `tests/test_notebook.py` | 10 章・10 節・課題数・ひな形・ヒント・絶対パス・テーマの独立性・再生成・上書き防止・実行 | 改訂（`tests/test_f1_notebook.py`） | Phase 1 実装済み（16 件） |
| `tests/test_synthetic_data.py` | Tiny の再現性・列・ID・境界条件 | 改訂（`tests/test_f1_synthetic_data.py`） | Phase 1 実装済み（5 件） |
| `tests/test_student_package.py` | 配布物の検査（許可リスト、解答の混入、独立実行） | 改訂予定 | Phase 5 |
| `scripts/build_student_package.py`（許可リスト、ZIP の日時固定、SHA-256、上書き防止） | `dist/f1-life-planning-starter/` と ZIP | 改訂予定 | Phase 5 |
| `.gitignore`（solutions/、dist/、data/raw/） | F-1 の `.gitignore` に追記 | 改訂 | Phase 1 実装済み |
| `CLAUDE.md`・`docs/` の構成 | 同じ文書構成 | 改訂 | Phase 1 で主要文書を作成 |
| `README.md`・`TASKS.md`（100 点満点の評価案）・`docs/teacher_guide.md` | 学生向け・教員向け文書の構成 | 改訂予定 | Phase 5 |

## C-1 の開発で得た注意点（F-1 に引き継ぐ）

- 学生向け文書（README・TASKS・data/README・data_dictionary・requirements）に教員用情報を書かない。
- 期待値は生成スクリプトに直接書く → データを作り直したら期待値を見直す（Tiny の期待値は Phase 3 で追加）。
- テストの繰り返しで WSL の仮想ディスクが広がる。実行テストは必要な回数にとどめる。
- 登録フォームのあるデータは教員が取得する。
