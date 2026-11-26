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

## Phase 2 で作成予定の Small Dataset（暫定）

| ファイル | 予定カラム | 由来 | ラベル |
| --- | --- | --- | --- |
| `c1a/network_flows_small.csv` | Tiny と同じ | CIC-IDS2017 | 元の Label を `benign` / 攻撃名に整理 |
| `c1b/authentication_small.csv` | Tiny と同じ（`dst_host` は匿名 ID） | Loghub OpenSSH | **なし**（`label` 列は `unknown`） |
| `c1c/http_requests_small.csv` | Tiny と同じ | CSIC 2010（保留）／人工 | 由来による |
| `c1d/system_events_small.csv` | `record_id, timestamp, host_id, process_name, event_type, message, label` | Loghub Linux | **なし**（`unknown`） |
| `c1e/data_transfer_small.csv` | Tiny と同じ | CIC-IDS2017 | 情報流出ラベルはなし（`unknown` または元ラベル） |

`timestamp` は原データに年がない場合、仮の年を付けたことを記録する（Loghub）。
