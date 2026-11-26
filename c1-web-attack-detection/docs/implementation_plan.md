# 開発計画

最終更新：2026-11-26（Phase 1.5・Phase 2A 終了時）

## Phase の全体像

```text
Phase 1   監査・再設計・初期改訂                      完了（コミット df5a1dc）
Phase 1.5 教材の取り組みやすさの再確認                 完了
Phase 2A  既存データ・小規模公開ログの前処理（C-1B/C/D） 完了
Phase 2B  CIC-IDS2017 の取得と前処理（C-1A/E）        教員の取得・条件確認待ち
Phase 3   全5テーマの Starter Code 実装                ← Phase 2B を待たずに開始できる
Phase 4   共通評価機能（ベンチマーク・可視化）
Phase 5   統合検証・学生配布準備
```

**Phase 2B は Phase 3 の開始条件ではありません。** C-1A と C-1E の Level 1・2 は人工データ（Mini・Tiny）で完結しています。
Phase 2B が終わったら、第4章・第8章の STEP 5 に公開データのセルを追加するだけで済む設計です（読み込みセルは用意済み）。

## Phase 2B：CIC-IDS2017（C-1A・C-1E）

手順・ファイルの選び方・問い合わせメール案は `cic_ids2017_acquisition_guide.md`。

| 作業 | 担当 | 見積もり |
| --- | --- | --- |
| 登録フォームの入力、`GeneratedLabelledFlows.zip` の容量確認と取得、PortScan の CSV 1 ファイルだけを取り出す | 教員 | - |
| CIC への再配布条件の問い合わせ | 教員 | - |
| 列名・行数・ラベル・通信方向の確認、調査報告の更新 | Claude | 1 時間 |
| `preprocess_c1a.py`、`preprocess_c1e.py`、検証、テスト、Notebook 4.9・8.9 の更新 | Claude | 4〜7 時間 |

想定ダウンロード量：zip は数百 MB【推定】（100MB を超えるため、取得は教員の判断で行う）。取り出す CSV は約 77MB【推定】。
学生配布用の CSV（2,000〜5,000 行 × 2 ファイル）は合計 1MB 程度【推定】。

## Phase 3：全5テーマの Starter Code 実装

### Phase 1・1.5 で既に実装済みのもの

| 項目 | 状態 |
| --- | --- |
| 全10章の構成、学習ルート、セルの表示 | 済 |
| Level 1 の関数のひな形（5 テーマ × 4 = 20 関数）、説明、3 段階のヒント、Mini Dataset での動作確認 | 済（期待値はリポジトリ外の参照実装で全件確認） |
| Level 2 の関数のひな形（13 関数）と Mini Dataset での動作確認 | 済（ヒントはなし） |
| Tiny Dataset の読み込みと、Level 1 の関数を Tiny Dataset に適用する教員提供セル（結果の表示のみ） | 済 |
| Small Dataset／公開ログの読み込みセル（ファイルがなくても止まらない） | 済 |
| C-1B・C-1C で Level 1 の関数を公開ログ・人工ログに適用するセル | 済 |
| 第9章の `measure_time`、`evaluate_detection`、グラフの例 | 済 |

### Phase 3 で追加するもの

| 作業 | 見積もり |
| --- | --- |
| Tiny Dataset での動作確認（`check` による [OK]/[NG]。期待値は生成スクリプトの設計から決める）× 5 テーマ | 2〜3 時間 |
| Level 2 の 3 段階のヒント（13 関数） | 2〜3 時間 |
| Level 2 の「基本版と改良版の実行時間の比較」セル（小さな人工データで。Benchmark 生成は Phase 4 で一般化） | 2〜3 時間 |
| Level 3 の教員提供の例（時間窓の数え方の例、`evaluate_detection` を Tiny Dataset の label で使う例、公開ログの集計の例）× 5 テーマ | 4〜6 時間 |
| 教員用の完成解答（`solutions/`、Git 管理外）と、解答を差し込んで全チェックが [OK] になることを確かめるテスト | 2 時間 |
| 初学者の目での通し確認、文言の修正、テスト | 2〜3 時間 |
| **合計（見積もり）** | **14〜20 時間** |

## Phase 4：共通評価機能

- `generate_synthetic_data.py` に Benchmark Dataset の生成関数を追加（件数・通信元数・ユーザー数・ファイル数を指定、シード固定。旧 `benchmark.py` の `make_records` を一般化）。
- 件数 100〜100,000 での実行時間の計測（O(NK) の処理が長くなりすぎないよう上限を設定）、グラフ、`results/` への保存。
- C-1C は「ルール数 R と URL 数 N」を変えた計測。
- 閾値と検出件数のグラフ、混同行列の表示。

## Phase 5：統合検証・学生配布準備

- 全体実行・章ごとの独立実行・Google Colab・Windows・Python 3.11/3.13 での確認。
- `scripts/export_student_package.py`（配布物の抽出。`student_distribution_plan.md`）。
- README・TASKS の完成、学生向けデータ辞書、再配布条件の最終確認、最終検証報告書。
- 親 README の C1 の説明・★評価の更新を提案。

## 教員の判断が必要な事項

1. CIC-IDS2017 の取得（登録フォームへの入力）と、CIC への問い合わせメールの送信。
2. Loghub 由来の CSV を、授業内の限定配布（非公開リポジトリ・LMS・ZIP）で配布してよいか。公開 GitHub にするか。
3. Phase 1.5・2A の変更のコミットの可否（現在は未コミット）。
4. Phase 3 の開始の可否と優先順位（例：Tiny Dataset の動作確認と Level 2 のヒントを先に）。
5. 旧教材ファイル（`starter.py` 等）を将来 `legacy/` に移すか、削除するか。
6. 親 README（C1 の説明）の更新時期。
