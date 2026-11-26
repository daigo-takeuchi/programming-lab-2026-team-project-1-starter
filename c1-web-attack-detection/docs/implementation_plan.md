# 開発計画（Phase 1〜5）

## Phase 1：監査・再設計・初期改訂（完了）

詳細は `development_status.md`。

## Phase 2：公開データ取得・前処理

**前提（教員の判断が必要）：** 末尾の「教員の判断が必要な事項」。

| 作業 | 成果物 | 想定工数（見積もり） |
| --- | --- | --- |
| Loghub OpenSSH_2k を取得し、認証イベントを抽出 | `scripts/preprocess_c1b.py`、`data/c1b/authentication_small.csv`（約 600 件） | 2〜3 時間 |
| Loghub Linux_2k を取得し、プロセスイベントを整理 | `scripts/preprocess_c1d.py`、`data/c1d/system_events_small.csv`（2,000 件） | 2 時間 |
| CIC-IDS2017 GeneratedLabelledFlows（金曜午後）から抽出 | `scripts/preprocess_c1a.py`、`preprocess_c1e.py`、`network_flows_small.csv`、`data_transfer_small.csv`（各 2,000〜5,000 件） | 4〜6 時間（教員の取得作業を除く） |
| C-1C：`sample_access.log` の CSV 化、人工 Small Dataset（別ファイル）、CSIC 2010 は入手できた場合のみ | `scripts/preprocess_c1c.py`、`http_requests_small.csv` | 2〜4 時間 |
| 公開データの取得手順をスクリプト化（登録が必要なものは手順の表示のみ） | `scripts/download_datasets.py` | 1 時間 |
| 品質検証の拡張と報告 | `validate_datasets.py`、`docs/preprocessing_report.md` | 1〜2 時間 |
| 出典・データ辞書の確定 | `dataset_sources.md`、`data_dictionary.md` | 1 時間 |

想定ダウンロード量：Loghub 1MB 未満。CIC-IDS2017 の zip は数百 MB（推定。500MB を超える場合は再度承認を得る）。
学生配布用 CSV の想定容量：全テーマ合計 2MB 程度（推定）。

## Phase 3：全5テーマの Starter Code 実装

- Tiny Dataset を使った動作確認（期待値は生成スクリプトの設計から決める）を各テーマに追加。
- Level 2 の実行時間比較セル（Benchmark Dataset を使う教員提供コード）。
- Level 3 の教員提供コード（時間窓の例、`log_parser` の取り込み、Small Dataset の読み込みと表示）。
- 教員用の完成解答（`solutions/`、Git 管理外）と、解答を差し込んで全チェックが [OK] になることを確かめるテスト。
- 必要に応じて C-1C 課題4 を分割（難易度レビューの結果による）。

## Phase 4：共通評価機能

- `generate_synthetic_data.py` に Benchmark Dataset の生成関数を追加（件数・通信元数・ユーザー数・ファイル数を指定、シード固定。`benchmark.py` の `make_records` を一般化）。
- 実行時間の計測（100〜100,000 件、O(NK) の処理が長くなりすぎないよう上限を設定）、グラフ、`results/` への保存。
- 閾値と検出件数のグラフ、混同行列の表示。

## Phase 5：統合検証・学生配布準備

- 全体実行・章ごとの独立実行・Colab での実行確認。
- 初学者による試行（可能なら）と、TODO・ヒントの見直し。
- README・TASKS の完成、再配布条件の最終確認、学生配布物の軽量化、最終検証報告書。
- 親 README の C1 の説明・★評価の更新を提案。

## 学生への配布方法の比較

| 方法 | 長所 | 短所 |
| --- | --- | --- |
| 1. 既存リポジトリをそのまま利用 | 準備が最小。更新を `git pull` で配れる | 24 トピック・教員用文書・旧教材（Level 2 の解答に近い `detection.py`）・開発履歴が見える |
| 2. 配布用ファイルだけを別リポジトリに抽出 | 学生に必要なものだけを公開できる。Colab で `git clone` しやすい。GitHub Classroom と組み合わせられる | 抽出の手順（スクリプト）が必要。教員用リポジトリとの同期が必要 |
| 3. Git 履歴を含まない ZIP | 最も簡単。履歴が見えない | 更新の配布が手作業。Colab では ZIP のアップロードと展開が必要。学生が Git を使い始めるきっかけにならない |

**推奨：方法 2**（教員用は現在のモノレポで開発を続け、Phase 5 で配布用ファイルを抽出するスクリプトを作る）。ZIP を予備として用意する。
今回の Phase 1 では外部リポジトリを作成していない。

## 教員の判断が必要な事項（Phase 2 開始前）

1. CIC-IDS2017 と CIC-Bell-DNS-EXF-2021 の登録フォームへの入力とダウンロード（Claude は個人情報を送信しない）。
2. CIC-IDS2017 由来の CSV を学生に配布してよいか（再配布条件の確認、必要なら CIC への問い合わせ）。
3. Loghub の「研究・学術目的」に授業での利用が含まれると判断してよいか。
4. CSIC HTTP 2010 の入手を続けるか、C-1C の Small Dataset を人工データ＋既存ログで代替するか。
5. 作業ブランチ `feature/c1-integrated-starter` へのコミットの可否（Phase 1 の変更は未コミット）。
6. 旧教材ファイル（`starter.py` 等）を将来 `legacy/` に移すか、削除するか。
