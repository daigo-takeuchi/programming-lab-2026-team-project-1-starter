# 前処理報告書（Phase 2A）

実施日：2026-11-26　／　対象：C-1B（Loghub OpenSSH_2k）、C-1C（旧教材の人工アクセスログ）、C-1D（Loghub Linux_2k）
C-1A・C-1E（CIC-IDS2017）は Phase 2B（`cic_ids2017_acquisition_guide.md`）。

## 1. 再現手順

```bash
cd c1-web-attack-detection
python3 scripts/download_datasets.py      # Loghub の原データ 5 ファイル（約 1.1MB）を data/raw/loghub/ に取得し、SHA-256 を確認
python3 scripts/preprocess_c1b.py         # C-1B
python3 scripts/preprocess_c1c.py         # C-1C（原データはリポジトリ内の data/sample_access.log）
python3 scripts/preprocess_c1d.py         # C-1D
python3 scripts/validate_datasets.py      # 品質検証
# 再生成結果と一致するかの確認：各 preprocess_c1x.py に --check を付ける
```

すべて Python 標準ライブラリだけで動く（乱数は使っていない）。原データと匿名化の対応表は `data/raw/`（Git 管理外）に置く。

## 2. 結果の比較

| | C-1B | C-1C | C-1D |
| --- | --- | --- | --- |
| 原データ | Loghub OpenSSH_2k（構造化版 CSV＋生ログ） | `data/sample_access.log` | Loghub Linux_2k（構造化版 CSV＋生ログ） |
| データの種類 | **公開ログ（実運用）**：Loghub の研究室の SSH サーバー | **人工データ**（旧 C1 教材のために教員が作成） | **公開ログ（実運用）**：Public Security Log Sharing Site → Loghub |
| 原データの件数 | 2,000 行 | 48 行（うち形式エラー 1 行） | 2,000 行 |
| 出力 | `c1b/authentication_small.csv`／`c1b/ssh_events_small.csv` | `c1c/web_access_log_synthetic.csv` | `c1d/system_events_small.csv` |
| 出力件数 | 525 行／2,000 行 | 47 行 | 2,000 行 |
| カラム数 | 14／11 | 9 | 11 |
| 容量 | 77,935 B／269,725 B | 4,033 B | 258,508 B |
| 正解ラベル | なし（`label = unknown`） | なし（作成者の意図を `scenario` 列に記録） | なし（`label = unknown`） |
| 匿名化 | IP 30 個 → `ip-001`…、ホスト名 6 個 → `host-001`…、実アカウント 1 個 → `user-001` | 不要（RFC 5737 のアドレス） | IP 67 個、ホスト名 31 個 |
| Git 管理 | **管理外**（再配布条件の確認待ち） | 管理対象 | **管理外**（再配布条件の確認待ち） |

## 3. C-1B の詳細

### 抽出の考え方

OpenSSH では、1 回のログイン失敗が複数の行に記録される（例：`Failed password ...` と `pam_unix(sshd:auth): authentication failure ...`）。
すべての行を数えると二重に数えてしまうため、`authentication_small.csv` には **sshd の認証試行の行**だけを入れた。

| Loghub EventId | 内容 | event_type | auth_type | result | 行数 |
| --- | --- | --- | --- | --- | ---: |
| E1 | Accepted password for … | accepted_password | password | success | 1 |
| E8 | Failed none for invalid user … | failed_none_invalid_user | none | failure | 4 |
| E9 | Failed password for … | failed_password | password | failure | 383 |
| E10 | Failed password for invalid user … | failed_password_invalid_user | password | failure | 135 |
| E14 | message repeated N times: [ Failed password … ] | failed_password_repeated | password | failure | 2（repeat_count = 5） |

- `repeat_count` の合計は 533（行数 525 + 2 行 × 4 回分）。行を増やして展開することはしていない。
- ユーザー名は 64 種類、接続元は 25 種類。`invalid_user = yes`（サーバーに存在しないユーザー名）は 139 行。
- 試行されたユーザー名には空白で始まるもの（` 0101`）があり、原データのまま残した。
- **成功は 1 行だけ**（原データのとおり。比率は調整していない）。「失敗の後の成功」の課題は人工の Tiny Dataset で扱う。
- `ssh_events_small.csv` は全 2,000 行に、Loghub の EventId ごとの大まかな種類（`auth_failure`、`pam_auth_failure`、`disconnect`、`invalid_user` など 11 種類）を付けたもの。**イベントの種類であって、攻撃の判定ではない**。

### 確認したこと

- 構造化版と生ログの行数（2,000）と内容が一致する（スクリプトで毎回確認）。
- 欠損値なし、完全な重複行なし、時刻は単調増加（12 月 10 日 06:55:46〜11:04:45）。
- 出力に匿名化されていない IPv4 アドレスがない（テストで確認）。

## 4. C-1C の詳細

- 原データの由来：旧 C1 教材の README（`docs/legacy/README_web_access_log.md`）に「架空のデータ」と明記。IP は RFC 5737 のアドレスのみ。
- 旧教材の `log_parser.parse_line` をそのまま使って解析した（旧テスト 17 件も引き続き成功）。29 行目（ステータスコードが `-`）は出力せず、ログに表示。
- `scenario` 列：旧 README の表に記録された、作成者が IP ごとに意図したパターン（`normal` 23 行、`access_concentration` 15 行、`error_404_concentration` 9 行）。攻撃の正解ラベルとしては扱わない。
- ファイル名は人工データであることが分かる `web_access_log_synthetic.csv` とした（公開データ由来の `_small.csv` と区別）。
- URL の長さや IP 別の回数などは、学生が計算する課題なので含めていない。
- 列名は Tiny Dataset（`http_requests_tiny.csv`）に合わせて `src_ip`、`status` とした（指示文の候補 `src_host`、`status_code` から変更）。学生の関数を両方のデータに使えるようにするため。

## 5. C-1D の詳細

- `process_name` は Loghub の Component をそのまま使用（30 種類。例：`ftpd`、`sshd(pam_unix)`、`su(pam_unix)`、`kernel`）。
- `host_id` は Loghub の Level 列の値（このログではホスト名 `combo` が入っている）。
- `event_type` はメッセージの文言に対する規則（`preprocess_c1d.py` の RULES）で付けた 12 種類：
  ftp_connection 909、auth_failure 537、session_opened 123、session_closed 123、auth_unknown_user 117、kernel_message 75、process_error 43、other 40、service_start 24、service_stop 6、ftp_anonymous_login 2、root_login 1。
- `pid` が空欄の行が 151 行ある（原データに PID がない行。空欄を許可する列として検証）。
- 時刻が前後している箇所が 3 か所（7 月 27 日 14:41 台の起動時のメッセージで、5 秒程度）。原データの順序のまま残した。
- 完全な重複行はない。同じ内容が続く記録も、実際のイベントの繰り返しなので削除していない。
- `rpc.statd`、`rpc.idmapd`（プロセス名）と `bugs.build.redhat.com`（Linux カーネルを作成したビルドサーバー名）は、ドメイン名に見えるが個人やサーバーを特定する情報ではないため、匿名化の対象から外した。
- **ファイル変更・ランサムウェアの記録やラベルは含まれない。** 人工のファイル状態データとは統合していない。

## 6. データ品質検証（`validate_datasets.py`）

| ファイル | 件数 | 容量 | 結果 |
| --- | ---: | ---: | --- |
| `data/c1b/authentication_small.csv` | 525 | 77,935 B | OK |
| `data/c1b/ssh_events_small.csv` | 2000 | 269,725 B | OK |
| `data/c1c/web_access_log_synthetic.csv` | 47 | 4,033 B | OK |
| `data/c1d/system_events_small.csv` | 2000 | 258,508 B | OK（警告 1 件） |

警告：`system_events_small.csv` の 900 行目、`process_name` の値 `-- root` は、表計算ソフトで数式として解釈されるおそれがある（`-` で始まる）。
原データの値なので変更せず、`data/README.md` で「表計算ソフトで編集・保存しない」と注意している。

（Phase 1 の Tiny Dataset 6 ファイルも、すべて OK。）

## 7. 既知の制約

- Loghub のログには**年がない**ため、`log_date`（MM-DD）と `log_time` に分けて記録した。年をまたぐ分析はできない。
- C-1B の公開ログは約 4 時間・1 台のサーバー分で、成功ログインがほぼない。
- 匿名化の対応表（`data/raw/loghub/anonymization_map_c1b.csv`、`_c1d.csv`）は配布しない。
- ドメイン名の検出は正規表現による。将来ログを差し替える場合は、匿名化された文字列の一覧を目で確認すること（Phase 2A では全件を確認した）。
