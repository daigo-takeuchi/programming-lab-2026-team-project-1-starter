# データ辞書

「種類」の列：**人工** = 教材用に作ったデータ、**公開** = 公開データを加工したデータ（Phase 2）。

## C-1A：`data/c1a/network_flows_tiny.csv`（人工、42 件）

| カラム | 型 | 意味 | 例 |
| --- | --- | --- | --- |
| `record_id` | 整数 | 教材用の通し番号（時刻順） | `1` |
| `timestamp` | 文字列（ISO 8601、タイムゾーンなし） | 通信の開始時刻 | `2026-11-20T10:04:47` |
| `src_ip` | 文字列 | 通信元 IP（RFC 5737） | `192.0.2.11` |
| `dst_ip` | 文字列 | 通信先 IP | `198.51.100.10` |
| `src_port` | 整数 | 通信元ポート（49152〜65535 の乱数） | `57205` |
| `dst_port` | 整数 | 宛先ポート | `443` |
| `protocol` | 文字列 | `TCP` のみ | `TCP` |
| `packet_count` | 整数 | パケット数 | `32` |
| `byte_count` | 整数 | バイト数 | `3589` |
| `label` | 文字列 | 教材上の役割：`benign`（正常）、`portscan`、`dos` | `benign` |

意図した特徴：`192.0.2.15` = 12 種類のポートへ各 1 パケット（ポートスキャン）、`192.0.2.16` = 10 秒間に 10 回（通信集中）、`192.0.2.14` = 正常だが通信回数がちょうど 8 回（閾値の境界例）。

## C-1B：`data/c1b/authentication_tiny.csv`（人工、32 件）

| カラム | 型 | 意味 | 例 |
| --- | --- | --- | --- |
| `record_id` | 整数 | 通し番号 | `1` |
| `timestamp` | 文字列（ISO 8601） | 認証の時刻 | `2026-11-20T10:06:20` |
| `user_id` | 文字列 | アカウント名 | `user05` |
| `src_host` | 文字列 | 接続元 IP | `192.0.2.25` |
| `dst_host` | 文字列 | 認証サーバー | `198.51.100.30` |
| `auth_type` | 文字列 | `password` のみ | `password` |
| `result` | 文字列 | 認証結果 `success` / `failure`（**攻撃ラベルではない**） | `failure` |
| `label` | 文字列 | 教材上の役割：`benign`、`bruteforce`、`spraying` | `benign` |

意図した特徴：`user04` = 8 回失敗の後に成功（総当たり）、`203.0.113.77` = 8 アカウントに 1 回ずつ失敗（パスワードスプレー）、`user05` = 本人の入力ミス 2 回＋スプレー 1 回で合計 3 回（誤検出の例）。

## C-1C：`data/c1c/http_requests_tiny.csv`（人工、32 件）

| カラム | 型 | 意味 | 例 |
| --- | --- | --- | --- |
| `request_id` | 整数 | 通し番号 | `1` |
| `timestamp` | 文字列（ISO 8601） | リクエストの時刻 | `2026-11-20T10:00:36` |
| `src_ip` | 文字列 | 接続元 IP | `192.0.2.33` |
| `method` | 文字列 | `GET` / `POST` | `GET` |
| `url` | 文字列 | パスとパラメータ（攻撃に似た文字列は**テキストとして保存**） | `/search?q=keyboard` |
| `status` | 整数 | HTTP ステータスコード | `200` |
| `label` | 文字列 | `benign`、`sqli`、`xss`、`traversal`、`long_url`、`scan` | `benign` |

意図した特徴：単純なルール（`'`、`<script`、`../`、長さ > 100）で見つかるもの／見つからないもの（`UNION SELECT`、`onerror=`、`..%2F`、`/admin` など）、正常なのに `'` を含む例（`it's`）。
`url_length` 等の派生列は、学生が計算する課題のため**含めない**。

## C-1D：`data/c1d/file_states_before_tiny.csv`（12 件）・`file_states_after_tiny.csv`（13 件）（人工）

| カラム | 型 | 意味 | 例 |
| --- | --- | --- | --- |
| `file_id` | 文字列 | ファイル名（教材用の架空の名前） | `config.ini` |
| `hash` | 文字列 | **教材用の疑似ハッシュ値**（本物のハッシュ値ではない） | `H001` |

変更内容：削除 `users.csv`／内容変更 `config.ini`・`app.log`・`hosts.txt`／名前の変化（ランサムウェアの兆候を模したもの）`photo_00x.jpg` → `photo_00x.jpg.locked`／追加 `unknown_tool.exe`・`README_RESTORE.txt`。

## C-1E：`data/c1e/data_transfer_tiny.csv`（人工、36 件）

| カラム | 型 | 意味 | 例 |
| --- | --- | --- | --- |
| `record_id` | 整数 | 通し番号 | `1` |
| `timestamp` | 文字列（ISO 8601） | 転送の時刻 | `2026-11-20T10:02:17` |
| `src_host` | 文字列 | 送信元 IP | `192.0.2.41` |
| `dst_host` | 文字列 | 送信先 IP（`203.0.113.x` は社外を想定） | `198.51.100.20` |
| `byte_count` | 整数 | 送信バイト数 | `26615` |
| `label` | 文字列 | `benign`、`exfiltration` | `benign` |

意図した特徴：`192.0.2.43` = 社外 `203.0.113.200` へ大量送信（情報流出を模したもの）、`192.0.2.44` = バックアップサーバー `198.51.100.90` へ大量送信（正常、誤検出の例）。

## C-1B：`data/c1b/authentication_small.csv`（公開ログ Loghub OpenSSH を加工、525 件、Git 管理外）

認証の**試行**を表す行だけ（1 行 = 1 回の試行の記録）。抽出基準は `docs/preprocessing_report.md` 3 章。

| カラム | 型 | 意味 | 例 |
| --- | --- | --- | --- |
| `record_id` | 整数 | 教材用の通し番号 | `1` |
| `source_line` | 整数 | 原データ（OpenSSH_2k.log）の行番号 | `6` |
| `log_date` | 文字列 MM-DD | 日付。**原データに年がないため年なし** | `12-10` |
| `log_time` | 文字列 HH:MM:SS | 時刻 | `06:55:48` |
| `user_id` | 文字列 | 試行されたユーザー名（原データのまま。実在アカウント 1 件のみ `user-001` に匿名化）。空白で始まるもの（` 0101`）もある | `root` |
| `src_host` | 文字列 | 接続元 IP の匿名 ID | `ip-001` |
| `dst_host` | 文字列 | サーバー名（原データのまま） | `LabSZ` |
| `auth_type` | 文字列 | `password` / `none` | `password` |
| `result` | 文字列 | `success` / `failure`。**認証の結果であって、攻撃の正解ではない** | `failure` |
| `invalid_user` | 文字列 | `yes` = サーバーに存在しないユーザー名での試行 | `yes` |
| `repeat_count` | 整数 | 通常 1。「message repeated N times」の行は N | `5` |
| `event_type` | 文字列 | `accepted_password`、`failed_password`、`failed_password_invalid_user`、`failed_none_invalid_user`、`failed_password_repeated` | `failed_password` |
| `message` | 文字列 | 元のメッセージ（IP・ホスト名は匿名化済み） | `Failed password for root from ip-005 port 42393 ssh2` |
| `label` | 文字列 | 常に `unknown`（正解ラベルなし） | `unknown` |

## C-1B：`data/c1b/ssh_events_small.csv`（同上、2,000 件、Git 管理外）

sshd の全イベント。列は `record_id, source_line, log_date, log_time, host_id（LabSZ）, process_name（sshd）, pid, event_id（Loghub の EventId）, event_type, message, label（unknown）`。
`event_type`（11 種類）：`auth_failure` 524、`disconnect` 513、`pam_auth_failure` 504、`invalid_user` 226、`pam_unknown_user` 135、`reverse_dns_failed` 85、`max_retries` 7、`too_many_failures` 3、`auth_success`・`session_opened`・`session_closed` 各 1。
**イベントの種類の分類であり、`authentication_small.csv` の `result`（成功・失敗）とは別のもの。**

## C-1C：`data/c1c/web_access_log_synthetic.csv`（人工データ、47 件）

旧 C1 教材の `data/sample_access.log` を変換したもの。

| カラム | 型 | 意味 | 例 |
| --- | --- | --- | --- |
| `request_id` | 整数 | 通し番号 | `1` |
| `source_line` | 整数 | sample_access.log の行番号 | `1` |
| `timestamp` | 文字列（ISO 8601、+09:00） | 日時 | `2026-11-15T10:00:05+09:00` |
| `src_ip` | 文字列 | 接続元（RFC 5737） | `192.0.2.10` |
| `method`、`url` | 文字列 | HTTP メソッド、パス | `GET`、`/index.html` |
| `status` | 整数 | HTTP ステータスコード | `404` |
| `response_bytes` | 整数または空欄 | 応答サイズ。空欄 = 原ログで `-`（データなし）。このログでは空欄の行はない | `2048` |
| `scenario` | 文字列 | 作成者が IP ごとに意図したパターン：`normal`、`access_concentration`、`error_404_concentration`。**攻撃の正解ラベルではない** | `normal` |

列名は Tiny Dataset（`http_requests_tiny.csv`）と同じものを使い、学生の関数を両方に使えるようにした。

## C-1D：`data/c1d/system_events_small.csv`（公開ログ Loghub Linux を加工、2,000 件、Git 管理外）

| カラム | 型 | 意味 | 例 |
| --- | --- | --- | --- |
| `record_id`、`source_line` | 整数 | 通し番号、原データの行番号 | `1` |
| `log_date`、`log_time` | 文字列 | 日付（MM-DD、年なし）と時刻 | `06-14`、`15:16:01` |
| `host_id` | 文字列 | ホスト名（原データの Level 列の値） | `combo` |
| `process_name` | 文字列 | Loghub の Component（30 種類） | `sshd(pam_unix)` |
| `pid` | 文字列（空欄あり） | プロセス ID。原データにない行（151 行）は空欄 | `19939` |
| `event_id` | 文字列 | Loghub の EventId | `E16` |
| `event_type` | 文字列 | メッセージの文言による分類（12 種類。`preprocess_c1d.py` の RULES） | `auth_failure` |
| `message` | 文字列 | 元のメッセージ（IP・ホスト名は匿名化済み） | `authentication failure; ... rhost=ip-001` |
| `label` | 文字列 | 常に `unknown` | `unknown` |

ファイル変更・ランサムウェアの記録やラベルは**含まれない**。

## Phase 2B で作成予定（CIC-IDS2017）

| ファイル | 予定カラム | ラベル |
| --- | --- | --- |
| `c1a/network_flows_small.csv` | Tiny と同じ（`packet_count` と `byte_count` の定義は取得後に確定） | 元の Label を整理（BENIGN → `benign` など） |
| `c1e/data_transfer_small.csv` | Tiny と同じ（`byte_count` = 順方向のバイト数の予定。定義を確認してから確定） | 情報流出のラベルはなし（`unknown` または元のラベル） |
