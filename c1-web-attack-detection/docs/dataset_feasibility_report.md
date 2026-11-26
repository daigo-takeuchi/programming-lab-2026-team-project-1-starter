# データセット調査報告（Phase 1、Phase 2A で更新）

調査日：2026-11-26

> **Phase 2A での更新（要点）：** C-1B・C-1D は Loghub の 2k ログで前処理を完了。C-1C は CSIC HTTP 2010 を保留し、旧教材の人工ログを CSV 化。C-1A・C-1E（CIC-IDS2017）は Phase 2B として、教員の取得後に実施（`cic_ids2017_acquisition_guide.md`）。CIC-Bell-DNS-EXF-2021 は今回取得しない（Level 3 の将来のオプション）。Loghub の利用条件の詳細は `student_distribution_plan.md` 3 章。
情報の確かさを次の 4 種類で区別する。

- **【公式】** 提供元の公式ページ・公式リポジトリで確認した事項
- **【実ファイル】** 実際にファイルを取得して確認した事項
- **【推定】** 一般的な知識・論文の記述などからの推定（未検証）
- **【未確認】** 確認できなかった事項

## 1. 結論（Phase 2 への推奨）

| テーマ | 推奨データ | 取得のしやすさ | 再配布 | 判断 |
| --- | --- | --- | --- | --- |
| C-1A | CIC-IDS2017（GeneratedLabelledFlows の Friday 午後） | 教員の登録フォーム入力が必要 | **【未確認】**（IDS2017 のページに再配布の文言なし） | 教員が取得 → 前処理。再配布条件の確認まで配布保留 |
| C-1B | Loghub OpenSSH_2k | 容易（GitHub から直接、225KB） | 条件付きで配布を想定（URL・論文の引用、ライセンス文の同梱）。公開 GitHub は未確認 | **採用・前処理済み（Phase 2A）** |
| C-1C | 既存 `sample_access.log`（人工）を CSV 化。CSIC HTTP 2010 は保留 | CSIC 公式サイトに接続できず | 人工データは問題なし。CSIC は【未確認】 | **人工データで実施済み（Phase 2A）** |
| C-1D | Loghub Linux_2k ＋ 人工ファイル状態データ | 容易（GitHub から直接、216KB） | C-1B と同じ。元の提供サイトは "use for whatever you want" | **採用・前処理済み（Phase 2A）** |
| C-1E | CIC-IDS2017（C-1A と共用）。CIC-Bell-DNS-EXF-2021 は Level 3 のオプション | 登録フォームが必要 | DNS-EXF は【公式】で再配布可（引用必須）。IDS2017 は【未確認】 | C-1A と同じ原データから作成 |

**必要なダウンロード量（推定）：** Loghub 2k ×2 で 1MB 未満（取得済み）。CIC-IDS2017 の GeneratedLabelledFlows.zip は数百 MB【推定】（500MB を超える場合は事前承認が必要）。CIC-Bell-DNS-EXF-2021 は全体 270.8MB【公式】。PCAP は取得しない。

## 2. C-1A：CIC-IDS2017

| 項目 | 内容 |
| --- | --- |
| 正式名称 | CIC-IDS2017（Intrusion Detection Evaluation Dataset）【公式】 |
| 提供元 | Canadian Institute for Cybersecurity（CIC）、University of New Brunswick【公式】 |
| 公式 URL | https://www.unb.ca/cic/datasets/ids-2017.html |
| ダウンロード URL | http://cicresearch.ca/CICDataset/CIC-IDS-2017/ 【公式】 |
| ダウンロード方法 | **登録フォーム**（First Name、Last Name、Email、Organization、Job Title、Country）に入力が必要【実ファイル：ダウンロードページを取得して確認】。公式ページ自体には登録の記載なし |
| ファイル | `GeneratedLabelledFlows.zip`、`MachineLearningCSV.zip`、PCAP【公式】。zip の容量は公式ページに記載なし【未確認】 |
| PCAP の容量 | 月 11GB、火 11GB、水 13GB、木 7.8GB、金 8.3GB【公式】→ **取得しない** |
| 収録内容 | 月：正常のみ。金曜午後：Port Scan（13:55–15:29）、DDoS LOIT（15:56–16:16）など【公式】 |
| カラム | 「80 以上のフロー特徴量」【公式】。GeneratedLabelledFlows には Flow ID・Source IP・Source Port・Destination IP・Destination Port・Protocol・Timestamp・パケット数・バイト数・Label が含まれ、MachineLearningCSV には IP・Timestamp が含まれない【推定】 |
| ラベル | あり（BENIGN、PortScan、DDoS など）【推定】。ラベル付けの誤りが論文で指摘されている【推定】 |
| ライセンス・再配布 | ページの "License" 節は "publicly available for researchers" と引用依頼のみ。**再配布の可否は明記なし**【公式】 |
| 引用 | Sharafaldin, Lashkari, Ghorbani, "Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization", ICISSP 2018【公式】 |
| 教育目的との適合 | 高い（ポートスキャン・DDoS のラベルがあり、IP・ポート・時刻がそろう） |
| 前処理 | Friday 午後の CSV から必要列だけを抽出、連続した時間区間を切り出し、IP を匿名化、ラベルを整理。難易度：中 |
| 教員の手動作業 | 登録フォームの入力とダウンロード、zip の容量確認、再配布条件の確認（CIC への問い合わせを含む） |
| 代替候補 | UNSW-NB15（CSV に srcip・sport・dstip・dsport・sbytes・stime・label を含む【推定】、利用条件【未確認】）、人工データの Small Dataset |

## 3. C-1B：Loghub OpenSSH

| 項目 | 内容 |
| --- | --- |
| 正式名称 | Loghub（OpenSSH） |
| 提供元 | LogPAI（The Chinese University of Hong Kong ほか）【公式】。OpenSSH ログは Loghub の研究室で収集【公式：OpenSSH/README.md】 |
| 公式 URL | https://github.com/logpai/loghub （OpenSSH の 2k サンプルは `OpenSSH/OpenSSH_2k.log`） |
| 全体版 | 655,146 行、70.02MiB、Zenodo（https://zenodo.org/records/8196385）【公式】。Loghub-2.0 は https://github.com/logpai/loghub-2.0 |
| 取得結果 | `OpenSSH_2k.log`（225,216 B）と `OpenSSH_2k.log_structured.csv`（357,677 B）を取得【実ファイル】 |
| カラム（structured） | `LineId, Date, Day, Time, Component, Pid, Content, EventId, EventTemplate`【実ファイル】 |
| 時刻 | `Dec 10 06:55:46` 〜 `Dec 10 11:04:45`（約 4 時間）。**年の情報なし**【実ファイル】 |
| 内容 | ホスト 1 台（LabSZ）。`Failed password` 518 行（うち invalid user 135 行）、`Invalid user` 113 行、`Accepted` **1 行のみ**、接続元 IP 27 種類（最多 580 行）【実ファイル】 |
| ラベル | **なし**【公式：README の Labeled 列が空欄】 |
| ライセンス | "freely available for research or academic work"。利用・配布時はリポジトリ URL と Loghub 論文（ISSRE 2023）を引用し、ライセンス文を全コピーに含めること【公式：LICENSE ファイル】 |
| 個人情報 | 実在の IP アドレス・ホスト名を含む（README によると "NOT sanitized"）【公式】→ 一貫した匿名 ID に変換する |
| 教育目的との適合 | 高い（ユーザー別・接続元別の失敗集中が明確）。ただし成功ログインがほぼないため「失敗の後の成功」の分析には不向き → 人工 Tiny Dataset で補う |
| 前処理 | `Content` から user_id・接続元 IP・結果（success/failure）を正規表現で抽出。難易度：低〜中 |
| 代替候補 | LANL Authentication（https://csr.lanl.gov/data/cyber1/、大容量のため不採用）、Loghub Linux の `sshd(pam_unix)` 行 |

## 4. C-1C：既存データ・CSIC HTTP 2010

### 4.1 既存データ `data/sample_access.log`

教員が作成した人工ログ（48 行、RFC 5737 アドレス）。再配布に問題なし。アクセス集中・404 集中の例を含むが、SQL Injection・XSS などの文字列は含まない【実ファイル】。

### 4.2 CSIC HTTP 2010

| 項目 | 内容 |
| --- | --- |
| 正式名称 | HTTP DATASET CSIC 2010 |
| 提供元 | スペイン国立研究協議会（CSIC）【推定】 |
| 公式 URL | https://www.isi.csic.es/dataset/ （別名 https://www.tic.itefi.csic.es/dataset/） |
| 取得結果 | 2026-11-26 に両 URL とも **接続拒否（ECONNREFUSED）**。curl でも応答なし【実ファイル：取得失敗】 |
| 規模 | 正常 36,000 件・異常 25,000 件程度、ファイル `normalTrafficTraining.txt`・`normalTrafficTest.txt`・`anomalousTrafficTest.txt`【推定：論文・ミラーの記述】 |
| 形式 | 生の HTTP リクエスト（ヘッダーと本文）をテキストで連結【推定】 |
| ライセンス・再配布 | **【未確認】** |
| ミラー | 4TU.ResearchData に同名ファイルを含むデータがあるが、一部ファイルの容量が極端に小さく、完全版かどうか不明【推定】 |
| 判断 | 再配布条件が確認できるまで学生配布物に含めない。Phase 2 は人工の Small Dataset（別ファイル）と `sample_access.log` で進める |
| 教員の手動作業 | 公式サイトへの再アクセス（時間をおいて／別ネットワークから）、利用条件の確認 |

## 5. C-1D：Loghub Linux

| 項目 | 内容 |
| --- | --- |
| 公式 URL | https://github.com/logpai/loghub （`Linux/Linux_2k.log`） |
| 全体版 | 25,567 行、2.25MiB、263.9 日分【公式】→ 全体版でも小さい |
| 元の提供者 | Public Security Log Sharing Site（Anton Chuvakin 氏）の `/var/log/messages`【公式：Linux/README.md】。同サイトの条件は "public; use for whatever you want"、出典の明記を推奨【公式：同サイトを 2026-11-26 に確認】 |
| 取得結果 | `Linux_2k.log`（216,485 B）、`Linux_2k.log_structured.csv`（327,804 B）【実ファイル】 |
| カラム | `LineId, Month, Date, Time, Level, Component, PID, Content, EventId, EventTemplate`【実ファイル】 |
| 時刻 | `Jun 14 15:16:01` 〜 `Jul 27 14:42:00`。年の情報なし【実ファイル】 |
| 内容 | Component 別：ftpd 916、sshd(pam_unix) 677、su(pam_unix) 172、kernel 76、klogind 46、logrotate 43 など。`session opened` 123 行【実ファイル】 |
| ラベル | なし。**ファイル変更・ランサムウェアの記録やラベルは含まれない**【実ファイル】 |
| ライセンス | C-1B と同じ（Loghub LICENSE）【公式】 |
| 前処理 | `Component` を `process_name` に、EventTemplate から `event_type` を作る。年がないため timestamp は「月日時刻」のまま、または仮の年を明示して付与。難易度：低 |
| 代替候補 | LANL Process Events、DARPA OpTC（いずれも大容量のため不採用）|

ファイル変更（追加・削除・変更・ランサムウェアの兆候）は**人工データ**（Tiny Dataset）で扱い、公開ログとは別ファイルで管理する。

## 6. C-1E：CIC-IDS2017（共用）と CIC-Bell-DNS-EXF-2021

### 6.1 C-1A との共用

CIC-IDS2017 のフロー CSV には送信・受信のバイト数の列がある【推定】。同じ原データから `data_transfer_small.csv`（`src_host, dst_host, byte_count, timestamp`）を作れる。
ただし CIC-IDS2017 に**情報流出のラベルはない**。ラベルは `unknown` または元の攻撃ラベルとして扱い、情報流出の正解として使わない。

### 6.2 CIC-Bell-DNS-EXF-2021

| 項目 | 内容 |
| --- | --- |
| 公式 URL | https://www.unb.ca/cic/datasets/dns-exf-2021.html |
| ダウンロード | http://cicresearch.ca/CICDataset/CICBellEXFDNS2021/ 。**登録フォームあり**【実ファイル】 |
| 容量 | DNS トラフィック 270.8MB【公式】。ページ内の数値に不整合あり（表の合計は約 321MB）【公式】 |
| 形式 | 構造化 CSV と PCAP【公式】。ファイル名・列名は記載なし【未確認】 |
| 特徴量 | 30 個（stateless 14：subdomain_length、entropy、labels など／stateful 16：rr_type、ttl_mean など）【公式】 |
| 時刻・識別子 | 行は timestamp 付きの DNS パケット【公式】。列名・送信元/送信先の識別子は【未確認】 |
| ラベル | benign / light attack / heavy attack【公式】。列名は【未確認】 |
| 再配布 | "You may redistribute, republish, and mirror ... in any form"、引用必須【公式】 |
| 引用 | Mahdavifar ほか, "Lightweight Hybrid Detection of Data Exfiltration using DNS based on Machine Learning", IEEE ICCNS 2021【公式】 |
| 判断 | Level 3 のオプション。教員が取得後、`query_length` 等の列を確認して `data/c1e/dns_queries_small.csv` を別ファイルで作成 |

## 7. 未確認事項の一覧

1. CIC-IDS2017 の zip の容量、列名、前処理済み CSV の再配布可否。
2. CSIC HTTP 2010 の入手経路と利用条件。
3. CIC-Bell-DNS-EXF-2021 の CSV のファイル名・列名・識別子の有無。
4. Loghub の「research or academic work」に専門学校の授業利用が含まれるかの解釈（教員判断）。
5. UNSW-NB15 等の代替候補の利用条件。
