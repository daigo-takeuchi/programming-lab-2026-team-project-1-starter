# 開発状況

最終更新：2026-11-26（Phase 1 終了時）
現在の Phase：**Phase 1 完了 → 教員の確認待ち**（Phase 2 には未着手）

## 1. 開発環境

| 項目 | 内容 |
| --- | --- |
| 作業ディレクトリ | `/home/daigo/Programming_Lab_2026/programming-lab-2026-team-project-1-starter/c1-web-attack-detection` |
| OS | Ubuntu 24.04.4 LTS on WSL2（kernel 6.18.58.1-microsoft-standard-WSL2） |
| Python | 3.12.3（`/usr/bin/python3`）。シェルの既定の `python3` は別プロジェクトの仮想環境（`~/AI_programming_2026/.venv`）を指していたため、**使用・変更していない** |
| 開発用仮想環境 | `c1-web-attack-detection/.venv`（Git 管理外）：nbformat 5.11.1、nbclient 0.11.0、ipykernel 7.4.0、matplotlib 3.11.2 |
| Git | 2.43.0。ブランチ `feature/c1-integrated-starter`（`main` の `e3f993e` から作成）。**Phase 1 の変更は未コミット** |
| ディスク | WSL（Linux 側）：空き 926GB。**Windows C: ドライブ：空き 6.2GB（使用率 98%）** |
| 日本語フォント | IPAexGothic などが利用可能（グラフの日本語表示を確認） |

## 2. 実装済み事項

| 項目 | ファイル |
| --- | --- |
| 既存プロジェクトの監査 | `docs/existing_project_audit.md` |
| 移行計画 | `docs/migration_plan.md` |
| 開発ルール | `CLAUDE.md` |
| 仕様書・開発計画・前処理方針 | `docs/project_specification.md`、`implementation_plan.md`、`preprocessing_policy.md` |
| データセット調査 | `docs/dataset_feasibility_report.md`、`dataset_sources.md`、`data_dictionary.md` |
| 統合 Notebook の骨格（全10章、日本語） | `C1_cybersecurity_starter.ipynb`（Markdown 194 セル、コード 92 セル、出力なし、約 195KB）、生成元 `scripts/build_notebook.py` |
| Mini Dataset（5 テーマ） | Notebook 内（C-1A 9 件、C-1B 8 件、C-1C 8 件、C-1D 3+3 件と状態 3+3 件、C-1E 6 件） |
| Tiny Dataset（5 テーマ、6 ファイル、合計約 11KB） | `data/c1a〜c1e/*_tiny.csv`、生成 `scripts/generate_synthetic_data.py` |
| データ品質検証 | `scripts/validate_datasets.py` |
| 共通関数 | Notebook 第3章 `load_csv`、`show_records`、`check`／第9章 `measure_time`、`evaluate_detection` |
| Level 1 の学生課題（関数のひな形・ヒント 3 段階・動作確認） | 各テーマ 4 関数、合計 20 関数 |
| Level 2 の学生課題（ひな形・動作確認） | C-1A 3、C-1B 3、C-1C 2、C-1D 3、C-1E 2 関数 |
| テスト | `tests/test_notebook.py`、`tests/test_synthetic_data.py`、`tests/__init__.py` |
| 学生向け文書（草案） | `README.md`、`TASKS.md`、`data/README.md` |
| 依存関係 | `requirements.txt`（matplotlib のみ、任意）、`requirements-dev.txt` |

## 3. 部分的に実装済みの事項

- **Level 3**：課題の説明と Small Dataset の読み込みセル（ファイルがない場合はメッセージを表示）のみ。分析用の教員提供コードは Phase 3。
- **実行時間の比較**：第9章に `measure_time` と、リスト vs 集合の例（教員提供）。各テーマの基本版 vs 改良版の比較セルは Phase 4。
- **TASKS.md**：提出物・期限・発表時間は【教員記入】のまま。
- **旧教材**：維持しているが、新教材との統合（`log_parser` の取り込み等）は Phase 3。

## 4. 未実装事項

- Small Dataset（全テーマ）、`scripts/download_datasets.py`、`scripts/preprocess_c1a〜c1e.py`
- Benchmark Dataset の生成
- 各テーマの Tiny Dataset での [OK]/[NG] 判定セル（現在は結果の表示のみ）
- 教員用の完成解答（`solutions/`）
- `docs/preprocessing_report.md`、`docs/final_validation_report.md`

## 5. 未確認事項

- CIC-IDS2017 の zip 容量・列名・再配布可否／CSIC HTTP 2010 の入手経路と利用条件／CIC-Bell-DNS-EXF-2021 の列名（`dataset_feasibility_report.md` 7 章）
- Google Colab・Windows ネイティブ・Python 3.11/3.13 での実行（今回は WSL の Python 3.12.3 のみで確認）
- 学生の実際の作業時間（難易度レビューの時間は見積もり）

## 6. テスト結果（Phase 1）

| テスト | 実行方法 | 結果 |
| --- | --- | --- |
| 全テスト | `.venv/bin/python -m unittest discover -s tests -t .` | **36 件すべて成功** |
| 　うち旧教材の回帰テスト | `test_parser.py`、`test_detection.py` | 17 件成功（改訂前と同じ） |
| 　Notebook の構造 | `test_notebook.TestStructure`（10 章、全テーマに N.1〜N.10、セルの表示、Level 1 が 3〜5 関数、ひな形に解答がない、絶対パスなし、他テーマへの依存なし） | 8 件成功 |
| 　Notebook の実行 | `test_notebook.TestExecution`：全体の一括実行（未実装のまま）、テーマごとの独立実行（第0〜3章＋1 章、そのテーマのデータだけ）、data フォルダなしでの実行 | 3 件成功（独立実行は 5 テーマとも成功） |
| 　人工データ | 再生成との一致、品質検証、意図した特徴（境界例・誤検出例など） | 8 件成功 |
| 旧 README のコマンド | `/usr/bin/python3 -m unittest discover -s tests -v`（nbclient なし） | 36 件成功（実行テスト 3 件はスキップ） |
| データ品質検証 | `python3 scripts/validate_datasets.py` | 6 ファイルすべて OK |
| 期待値の検証（リポジトリ外） | 一時的な参照実装を Notebook に差し込んで実行 | テーマの動作確認 72 件すべて [OK]。参照実装はリポジトリに含めていない |
| 旧教材の実行 | `python3 starter.py`、`python3 benchmark.py` | 成功（`textbook/ssearch_while.py` がある環境） |

## 7. 難易度レビュー（見積もり）

| | C-1A | C-1B | C-1C | C-1D | C-1E |
| --- | --- | --- | --- | --- | --- |
| 最初の問題 | 通信元のレコードを取り出す | 失敗レコードを取り出す | URL の文字数 | ファイルがあるか調べる | 通信元のレコードを取り出す |
| 必要な文法 | for、if、append、タプル | for、if、`and` | `len`、`in`、for、`or` | for、if、早期 return、`not` | for、if、`+=` |
| 必要な専門知識 | IP・ポート（表で説明） | 認証・成功／失敗 | URL・パラメータ | ファイル・ハッシュ（概念のみ） | バイト・送信元／先 |
| Level 1 の課題数 | 4 | 4 | 4 | 4 | 4 |
| 実装の分量（推定） | 各 3〜8 行、計 約 25 行 | 計 約 25 行 | 計 約 20 行（課題4 が最も複雑） | 計 約 20 行 | 計 約 25 行 |
| 想定時間（見積もり） | 2〜3 時間 | 2〜3 時間 | 2〜3 時間 | 1.5〜2.5 時間 | 2〜3 時間 |
| Level 2 | 辞書・集合（ポート種類数） | 辞書・入れ子の辞書・集合 | ルールのリスト・スコア・`lower()` | 集合・辞書（ハッシュ） | 辞書（2 種類の集計） |
| つまずきやすい点 | タプルの分解、「以上」と「より大きい」、重複のない一覧 | 失敗 0 回のユーザーも含める | 課題4 の「どれか 1 つでも」（フラグ変数） | ループ内で `return False` してしまうバグ | CSV の数値を整数にする（教員提供の `load_csv` で対応済み） |
| 教員の補足が必要な点 | ポート番号の意味 | `result` は攻撃ラベルではないこと | 攻撃文字列を実行しないこと | 疑似ハッシュと本物のハッシュの違い | 回数（C-1A）と量（C-1E）の違い |

**評価：**
- 専門知識なしで開始できる（各章 N.2 の表で必要な用語のみ説明）。Mini Dataset はすべて手計算で確認できる大きさ。
- Level 1 だけで「データ → 集計 → 閾値 → 候補の表示」まで動く検出プログラムになる。Tiny Dataset への適用セルで確認できる。
- 公開データがなくても Level 1・2 は完了できる（data フォルダなしでも Notebook は止まらない）。
- テーマ間の難易度の差は小さい。C-1D がやや易しく、C-1C 課題4 がやや難しい。

**調整の提案（Phase 3 で判断）：**
1. C-1C 課題4 を「1 件の URL が怪しいかを判定する `is_suspicious_url()`」と「リクエスト全体に適用する関数」に分ける（課題が 5 つになる）。
2. C-1D に「内容が変更されたファイル」を Level 1 の任意課題として追加し、他テーマと分量をそろえる。
3. C-1C の Level 2 は計算量の比較が弱いため、「ルール数 R と URL 数 N を増やしたときの実行時間」を Phase 4 のベンチマークに入れる。

## 8. 既知の制約

- Notebook は `scripts/build_notebook.py` から生成している。ipynb を直接編集すると次の生成で上書きされる。
- Loghub OpenSSH_2k には成功ログインが 1 行しかない。「失敗の後の成功」は人工データで扱う。
- 旧教材（`detection.py` 等）は、Git 管理外の教科書コードがないと動かない（改訂前からの制約）。
- 親リポジトリ README の C1 の説明は旧教材のまま（変更していない）。

## 9. 次の Phase で必要な作業

`implementation_plan.md` の Phase 2 と「教員の判断が必要な事項」を参照。
