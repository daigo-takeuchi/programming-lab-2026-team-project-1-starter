# TASKS：C-1 チーム開発課題

> **Phase 1 の草案です。** 提出期限・評価方法・発表時間などは、担当教員が確定した後に記入します（`【教員記入】`の部分）。

## 1. 進め方の全体像

1. チームで担当テーマ（C-1A〜C-1E）を 1 つ決める。
2. 全員で Notebook の第0章〜第3章と、担当テーマの STEP 1 を実行し、データの意味を理解する。
3. **Level 1（必須）**の課題を分担して実装する。全員が少なくとも 1 つの関数を実装する。
4. 動作確認のセルがすべて `[OK]` になったら、Level 2・Level 3 から取り組む課題をチームで選ぶ。
5. 結果をまとめ、発表する。

## 2. テーマ別の Level 1 課題

| テーマ | 課題1 | 課題2 | 課題3 | 課題4 |
| --- | --- | --- | --- | --- |
| C-1A | `filter_by_source` | `count_connections` | `summarize_connections_baseline` | `detect_high_frequency_sources` |
| C-1B | `filter_failed_logins` | `count_failed_logins` | `summarize_failures_baseline` | `detect_suspicious_users` |
| C-1C | `get_url_length` | `detect_long_urls` | `contains_any_pattern` | `detect_suspicious_requests` |
| C-1D | `file_exists` | `find_added_files` | `find_deleted_files` | `compare_file_lists_baseline` |
| C-1E | `filter_transfers_by_source` | `sum_transfer_bytes` | `summarize_transfer_baseline` | `detect_large_transfers` |

課題1・2 は他の課題に依存しません。課題3・4 は、テーマによって前の課題の関数や結果を使います（各課題の説明に書いてあります）。
Level 1 だけで、「データを読む → 数える → 閾値で候補を見つける」基本的な監視プログラムが完成します。
**4 人チームなら 1 人 1 課題**、3 人なら課題3・4 を 2 人で分担する、などの分け方ができます。

## 3. 役割分担の例

| 役割 | 主な仕事 | 実装も担当する課題の例 |
| --- | --- | --- |
| データ理解・分析 | データの意味を調べ、チームに説明する | 課題1 |
| 基本アルゴリズム実装 | Level 1 の中心 | 課題2・3 |
| 改良アルゴリズム実装 | Level 2 の中心 | 改良課題A |
| テスト・性能評価 | テストの追加、実行時間の計測 | 課題4、自作テスト |
| 可視化・結果整理 | グラフと表の作成 | 閾値と検出件数のグラフ |
| Git 管理・ドキュメント | ブランチ管理、README・発表資料 | 改良課題B |

**プログラムを書かない役割だけの人がいないようにしてください。**

## 4. 成果物

**Level 1 は必須、Level 2 は推奨、Level 3 は選択です。**

| 成果物 | 内容 | レベル |
| --- | --- | --- |
| 実装した Notebook | 担当テーマの関数を実装し、実行結果を残した Notebook | 必須 |
| 基本課題の動作確認 | Level 1 の【動作確認】（Mini Dataset と Tiny Dataset）がすべて `[OK]` | 必須 |
| 検出結果 | Tiny Dataset で見つけた「調べる必要がある候補」と、グラフ（STEP 3 の「結果をグラフで確認する」） | 必須 |
| 説明と考察 | 処理の流れの説明、閾値を変えたときの変化、誤検出・検出漏れの例 | 必須 |
| 改良課題の動作確認 | Level 2 の【動作確認】（Mini・Tiny）がすべて `[OK]` | 推奨 |
| 基本版と改良版の比較 | **効率化**の課題：結果が同じことの確認、実行時間の表とグラフ、計算量の説明／**検出方法の改良**の課題：何が見つかるようになったか（結果が変わってよい） | 推奨 |
| 発展課題 | 公開ログへの適用、時間窓、評価指標など、1 つ以上 | 選択 |
| 問題点と改善案 | 残っている問題と、次に改良するならどうするか | 必須 |

**評価の目安（教員が調整します）：** Level 1 の完成と説明で合格。Level 2 の比較と考察で加点。Level 3 は内容に応じて加点。

提出物：【教員記入】（例：Notebook、発表資料、チームの作業記録）
提出期限：【教員記入】

## 5. 発表の構成

1. どのような社会的問題を対象としたか。
2. どのようなデータを使用したか。
3. どのようなアルゴリズムを実装したか。
4. どのような結果が得られたか。
5. どのような改良を行ったか。
6. 何が問題として残っているか。
7. 今後どのように発展させられるか。

発表時間：【教員記入】

## 6. Git の使い方（例）

```bash
git switch -c feature/c1b-count-failed-logins
# Notebook を編集して保存
git add C1_cybersecurity_starter.ipynb
git commit -m "C-1B 課題2 count_failed_logins を実装"
git push -u origin feature/c1b-count-failed-logins   # チームのリポジトリへ（教員の指示に従う）
```

Notebook は同時に編集するとマージが難しくなります。**担当する章・セルを決め、こまめにコミット**してください。

## 7. 守ること

- 保存済みデータのオフライン分析だけを行う。実際のネットワーク・Web サイト・アカウントに対して何かを試さない。
- `label` 列を検出プログラムの入力に使わない（評価にだけ使う）。
- 「攻撃を確定した」ではなく「調べる必要がある候補を見つけた」と表現する。
