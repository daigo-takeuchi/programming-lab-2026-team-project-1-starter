# 最終検証報告：F-1 統合 Starter v1.0（2026-11-27）

## 1. 対象

| 項目 | 内容 |
| --- | --- |
| 教材 | キャリア・ライフイベント・世代間資源継承の意思決定と最適化（Decision-Making and Optimization of Career Paths, Life Events, and Intergenerational Resource Transfer） |
| ブランチ | `feature/f1-integrated-starter`（Phase 1 `fff67e5`、Phase 2・3 `e5bffc6`。Phase 4・5 は未コミット、未 push） |
| 検証環境 | WSL2（Linux x86_64）、Python 3.12.3（C-1 の既存環境 `../c1-web-attack-detection/.venv` を借用。nbformat・nbclient・ipykernel・matplotlib）、標準ライブラリだけのスクリプトは `/usr/bin/python3` |

## 2. 完了条件の確認

| 完了条件 | 結果 |
| --- | --- |
| 全 4 テーマの基本課題が維持されている | ○ 28 関数（Level 1 16・Level 2 12）、Level 3 各 5 案、独自機能の候補 各 4 案 |
| 全 28 関数が参照実装で検証されている | ○ 128 件すべて [OK]（122 件 ＋ 練習 6 件） |
| 全テーマに性能評価がある | ○ 第8章 8.4〜8.7 |
| F-1C の線形探索・二分探索の比較が完成している | ○ 比較1〜4 ＋ ソートの方法の比較（8.6） |
| F-1B の難易度調整が完了している | ○ Level 1 の練習、課題6 の 4 段階 |
| 公開統計への橋渡し演習がある | ○ 各テーマの N.9（F-1C は取得方法と変換方法） |
| モデルの仮定と限界が明示されている | ○ 各テーマ N.9 の「モデルの妥当性と限界」、第0章・README の注意 |
| README と TASKS が完成している | ○（TASKS の【教員記入】は教員が記入） |
| データ辞書と出典情報が完成している | ○ `data/data_dictionary.md`、`data/dataset_sources.md` |
| 学生配布フォルダと ZIP が生成されている | ○ 4 章 |
| 配布物に完成解答が混入していない | ○ 作成時の自動確認とテスト |
| 再配布条件が未確認のデータが含まれていない | ○ F-1C の取引価格データ・原データ・textbook を含まない |
| ZIP 展開後のクリーン環境検証が成功している | ○ 5 章 |
| 全 4 テーマを独立実行できる | ○ |
| 公開統計なしでも基本課題を実行できる | ○ |
| 既存教材が破損していない | ○ 旧テスト 51 件成功（旧 README は `docs/legacy/` に移動） |
| 他トピックを変更していない | ○ 親 README の F1 の 2 行だけ |
| 教員向け文書が完成している | ○ `teacher_guide`・`educational_validation_report`・`student_distribution_plan`・`student_package_guide`・本報告 |
| ストレージ制約を遵守している | ○ C: 9.1GB → 9.0GB。追加ファイル 約 0.6MB（dist を含む） |

## 3. テスト

| テスト | 件数 | 結果 |
| --- | ---: | --- |
| `tests.test_f1_notebook`（構造・再生成・実行・第8章・練習） | 22 | 成功 |
| `tests.test_f1_synthetic_data`（Tiny の再現性・検証・キー名） | 9 | 成功 |
| `tests.test_f1_student_mistakes`（誤り 17 種類の検出、ソートしていない入力） | 3 | 成功 |
| `tests.test_f1_student_package`（許可リスト・除外・出力消去・解答の非混入・ZIP の再現性・クリーン環境での実行） | 15 | 成功 |
| 旧教材（4 モジュール） | 51 | 成功 |
| **合計** | **100** | **すべて成功** |

その他：`generate_synthetic_data.py --check` 6 ファイル一致、`validate_datasets.py` エラー 0 件・境界条件 19 件。

## 4. 学生配布物

| 項目 | 内容 |
| --- | --- |
| 配布フォルダ | `f1-career-income-optimization/dist/f1-life-planning-starter/`（17 ファイル、406,654 バイト） |
| ZIP | `f1-career-income-optimization/dist/f1-life-planning-starter.zip`（102,067 バイト。2026-11-27 に README の取得手順を既存モノレポ向けに直して再生成。旧 SHA-256 4f11c59e…7462） |
| SHA-256 | `7fe5dc0dfde8fff8605e4c99442b219ae1f7fa1b124d7144019b4caeb08033c1` |
| ファイル一覧 | `dist/f1-life-planning-starter_manifest.txt` |

含めるもの・含めないものは `docs/student_package_guide.md` 3・4 章。

## 5. クリーン環境での検証

| 検証 | 結果 |
| --- | --- |
| 実際の ZIP を教員用リポジトリの外（一時フォルダ）に展開 | 17 ファイル。配布フォルダと内容が一致 |
| 作り直した ZIP との比較 | SHA-256 が一致（再現性） |
| 展開した Notebook のコピーに参照実装を差し込んで実行 | 128 件すべて [OK]。配布物の Notebook は変わらず、解答入りのファイルは残らない |
| 未実装のまま全体を実行（テスト） | 最後まで動く。[エラー] は第3章のわざと出す例だけ |
| 第0〜3章＋各テーマ（＋第8章）の単独実行（テスト） | 4 テーマとも成功。他テーマの性能評価は「[スキップ]」 |
| Small Dataset を消して実行（テスト） | 成功（「Small Dataset がありません」と表示） |
| 1 つ上のフォルダから実行（Colab 想定、テスト） | 「データフォルダ: OK」 |

## 6. 性能評価の結果（参照実装、検証環境での実測。Notebook には保存していない）

| テーマ | 結果 |
| --- | --- |
| F-1A | N = 10,000（T = 43）：所得計算 0.096 秒、線形探索 0.0006 秒、挿入ソート（参照実装）4.6 秒。比較のたびに所得を計算し直すと約 10 倍遅い（N = 1,000） |
| F-1B | k = 100：全候補 60,000、実行可能 31,578、0.025 秒。収支最大と自由時間最大で 1 位の計画が違う |
| F-1C | 比較1（件数、ソート済み）：N = 100,000 で線形 0.0064 秒、二分 0.000003 秒。比較3（ソート込みで 1 回）：すべての N で線形探索が速い。比較4（N = 100,000）：Q = 100 で線形 0.68 秒、ソート 1 回 + 二分 0.021 秒。挿入ソートは N = 10,000 で 4.1 秒、`sorted()` は 0.003 秒 |
| F-1D | M × D × T を 2 倍にすると時間もほぼ 2 倍。T = 40 では移転しなくても親の最低生活資金を守れない |

すべての比較で、2 つの方法の結果が一致することを先に確かめています。

## 7. 未検証事項と教員の残作業

| 事項 | 状態 |
| --- | --- |
| 教員による事前試行 | 未実施。`docs/educational_validation_report.md` 4 章のチェックリスト |
| TASKS.md の【教員記入】の確定 | 未実施（テーマの選び方、提出、期限、発表、正式な配点、評価ルール、生成 AI の利用ルール） |
| Windows ネイティブ（VS Code・Jupyter）・Google Colab での実行 | **未検証**（手順は README に記載。構文・実行の確認は WSL の Python 3.12 だけ） |
| F-1C の実データの取得 | 未取得。`preprocess_f1c.py` は実データで未検証（`docs/teacher_guide.md` 5 章） |
| GitHub での公開 | 方針変更（2026-11-27）：F-1 専用リポジトリは作らず、既存のモノレポに統合する（`docs/student_distribution_plan.md`） |
| LMS への配布 | 未実施 |
| 初回授業での学生の試行・作業時間の実測 | 未実施（作業時間は見積もり） |
| Phase 4・5 のコミット、push、main へのマージ | 未実施（教員の指示待ち） |
