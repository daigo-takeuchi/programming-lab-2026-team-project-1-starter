# CIC-IDS2017 取得の手引き（Phase 2B の準備・教員向け）

調査日：2026-11-26
**Claude は登録フォームに個人情報を入力していないため、登録後の画面とファイル構成は確認していません。**
記号：【公式】公式ページで確認／【推定】第三者のミラーや論文の記述／【未確認】確認できていない

## 1. 何のために、何が必要か

C-1A（通信の回数・宛先ポートの種類）と C-1E（送信データ量）の両方の Level 3 を、**1 つの CSV ファイル**で成り立たせることが目標です。
必要な情報は、通信元 IP、通信先 IP、宛先ポート、時刻、パケット数、バイト数、ラベルです。

## 2. 手順

| 手順 | 内容 |
| --- | --- |
| 1 | 公式ページ https://www.unb.ca/cic/datasets/ids-2017.html を開き、「Download this dataset」をクリックする【公式】 |
| 2 | http://cicresearch.ca/CICDataset/CIC-IDS-2017/ の登録フォームに、First Name、Last Name、Email、Organization/Company、Job Title、Country を入力する【公式：フォームの項目は Phase 1 で確認】 |
| 3 | 送信後に表示されるファイル一覧から、**`GeneratedLabelledFlows.zip`** を選ぶ（`MachineLearningCSV.zip` と PCAP は選ばない）。表示される容量を記録する【未確認】 |
| 4 | **ダウンロードする前に容量を確認する。** 100MB を超える場合は、Claude との作業を始める前に容量を記録しておく（このプロジェクトでは、100MB を超える取得は教員の判断で行うルール） |
| 5 | 保存先：`c1-web-attack-detection/data/raw/cic_ids2017/`（Git 管理外）。Windows 側から保存する場合は `\\wsl$\Ubuntu\home\daigo\...` 経由でもよい |
| 6 | zip を全部展開しない。必要な 1 ファイルだけを取り出す（下記 4 章） |
| 7 | 使い終わった zip は、教員の判断で削除する |

### ストレージの注意

- 2026-11-26 時点で **Windows C: ドライブの空きは 2.6GB** です。WSL の仮想ディスクも C: 上にあるため、Linux 側の「空き 926GB」は実際には使えません。
- zip 全体を展開すると、1GB を超える可能性があります【推定】。必要な 1 ファイルだけを取り出してください。
- 一時的に必要な最大容量（推定）：zip（数百 MB）＋ 取り出した CSV（約 77MB）。

## 3. ファイルの選び方

| ファイル | 中身 | IP・時刻 | このプロジェクトでの判断 |
| --- | --- | --- | --- |
| `GeneratedLabelledFlows.zip` | 曜日・時間帯ごとのフロー CSV（`TrafficLabelling/` フォルダ）【推定】 | **あり**（Flow ID、Source IP、Destination IP、Timestamp）【推定】 | **これを使う** |
| `MachineLearningCSV.zip` | 機械学習用に識別子を除いたフロー CSV【推定】 | **なし**【推定】 | 通信元ごとの集計ができないため使わない |
| PCAP（1 日 7.8〜13GB）【公式】 | パケットそのもの | あり | 取得しない |

### 必要な最小限のファイル

**第一候補：`Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv`**（第三者のミラーでは約 76.9MB【推定】）

- 金曜午後（13:55〜15:29）のポートスキャン（PortScan）と、正常な通信（BENIGN）を含みます【公式：攻撃の時間帯】。
- 1 つのファイルで、C-1A（正常な端末と、多数のポートに接続する端末の比較）と C-1E（端末ごとの送信量）の両方に使えます。

**第二候補（必要な場合のみ）：`Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv`**

- DDoS LOIT（15:56〜16:16）を含みます【公式：時間帯】。容量は【未確認】。
- C-1A の「通信先への集中」の発展課題を充実させたい場合だけ追加します。

## 4. 取り出しのコマンド例（教員が実行）

```bash
cd c1-web-attack-detection/data/raw/cic_ids2017
unzip -l GeneratedLabelledFlows.zip                 # まず中身の一覧と容量を確認する（展開しない）
unzip -j GeneratedLabelledFlows.zip '*Friday-WorkingHours-Afternoon-PortScan*'   # 1 ファイルだけ取り出す
sha256sum *.zip *.csv > SHA256SUMS.txt              # チェックサムを記録する
```

## 5. 列の意味（取得後に必ず確認すること）

CICFlowMeter が作るフロー CSV の主な列【推定：列名はコピーによって違いがあり、先頭に空白が付く場合もある】：

| 列 | 意味 | 使うテーマ |
| --- | --- | --- |
| `Source IP`、`Destination IP` | 通信元・通信先 | C-1A、C-1E |
| `Source Port`、`Destination Port`、`Protocol` | ポート番号、プロトコル番号（6 = TCP など） | C-1A |
| `Timestamp` | フローの開始時刻 | 時間窓（Level 3） |
| `Total Fwd Packets`、`Total Backward Packets` | 順方向・逆方向のパケット数 | C-1A（参考） |
| `Total Length of Fwd Packets`、`Total Length of Bwd Packets` | 順方向・逆方向のバイト数の合計 | **C-1E** |
| `Label` | BENIGN、PortScan、DDoS など | 評価（Level 3） |

### フロー数とパケット数の違い

- **1 行 = 1 つのフロー**（同じ相手との、ひとまとまりの通信）です。1 つのフローには、多くのパケットが含まれます。
- C-1A の「通信回数」は、**フローの数（行数）**として数えます。パケット数ではありません。教材ではこの違いを明記します。

### C-1E の「送信量」の定義（要確認）

- CICFlowMeter の説明では、Fwd（順方向）は「フローの最初のパケットを送った側 → 受けた側」の方向、`Total Length of Fwd Packets` はその方向のパケットの大きさの合計です【推定：CICFlowMeter の ReadMe の写し】。
- したがって「通信元（Source IP）の送信量 = `Total Length of Fwd Packets`」と定義できる見込みですが、次の点を取得後に確認します。
  1. Source IP がフローの開始側になっているか（数行を見て、ポート番号の大小などから判断）。
  2. バイト数にヘッダーが含まれるか（CICFlowMeter のソースコード `BasicFlow` で確認）。
- 確認できない場合は、教材では「順方向のバイト数」と書き、「送信量」と言い切らない。

### 既知の問題【推定】

- ラベルの誤り、特徴量の計算誤り、重複が論文で指摘されている（例：2022 年の分析論文）。
- 値に `Infinity` や `NaN` が含まれる列がある。
- C-1E の情報流出のラベルは**含まれない**（PortScan や DDoS のラベルを情報流出の正解として使わない）。

## 6. 再配布条件

| 項目 | 状況 |
| --- | --- |
| 公式の利用条件 | 公式ページの "License" 節は「研究者向けに公開されている」ことと、論文の引用依頼のみ【公式】 |
| 引用 | Iman Sharafaldin, Arash Habibi Lashkari, Ali A. Ghorbani. "Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization", ICISSP 2018【公式】 |
| 加工した CSV の再配布 | **記載なし【未確認】** |
| 授業内の限定配布 | **記載なし【未確認】** |
| GitHub での公開配布 | **記載なし【未確認】**。第三者のミラー（Hugging Face など）が存在するが、それは許可の根拠にならない |

参考：同じ CIC の CIC-Bell-DNS-EXF-2021 のページには「再配布・ミラーを認める（引用が条件）」と明記されているが、CIC-IDS2017 のページにはない。

**結論：** 再配布の可否が分かるまで、CIC-IDS2017 から作った CSV は Git 管理外とし、学生配布物に入れない。下の英文メールで CIC に問い合わせることを推奨する。

## 7. 問い合わせメールの案（英語・自動送信しない）

宛先：CIC の公式ページに記載された連絡先（教員が確認する）

```text
Subject: Permission to redistribute a small processed subset of CIC-IDS2017 for classroom teaching

Dear Canadian Institute for Cybersecurity team,

I am an instructor at a vocational college for AI and information technology in Japan.
I am preparing an introductory Python programming course in which students learn basic
algorithms (counting, searching, thresholds) through cybersecurity examples.

I would like to use CIC-IDS2017 in this course, and I would be grateful if you could tell me
whether the following use is permitted:

1. Extracting a small subset (a few thousand flows) from one CSV file in
   GeneratedLabelledFlows (Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv),
   keeping only a few columns (source/destination IP, ports, timestamp,
   packet and byte counts, label).
2. Anonymizing the IP addresses with consistent pseudonyms where appropriate.
3. Distributing this small CSV to enrolled students for educational purposes only.
4. Distributing it through a GitHub repository. Please let me know whether a public
   repository is acceptable, or whether it should be limited to a private repository
   accessible only to the students.

In all materials, we would clearly cite the dataset page and the following paper:
Iman Sharafaldin, Arash Habibi Lashkari, and Ali A. Ghorbani, "Toward Generating a New
Intrusion Detection Dataset and Intrusion Traffic Characterization", ICISSP 2018.

If there are any additional conditions (for example, a specific citation format or a
statement to include with the data), we will follow them.

Thank you very much for providing this dataset to the research and education community.

Best regards,
[Name]
[Title, Department]
[School name, Country]
[Email address]
```

## 8. Phase 2B の作業計画（取得後）

| 順番 | 作業 | 見積もり |
| ---: | --- | --- |
| 1 | 教員：ファイルの取得、容量とチェックサムの記録、問い合わせメールの送信 | 教員の作業 |
| 2 | 列名・行数・ラベルの内訳・Source IP の向きを確認し、`dataset_feasibility_report.md` を更新 | 1 時間 |
| 3 | `scripts/preprocess_c1a.py`：連続した時間区間（例：PortScan の前後を含む 30〜60 分）を切り出し、必要な列に絞り、IP を匿名化 → `network_flows_small.csv`（2,000〜5,000 行） | 2〜3 時間 |
| 4 | `scripts/preprocess_c1e.py`：同じ原データから `src_host, dst_host, byte_count, timestamp` を作る（byte_count の定義を明記）→ `data_transfer_small.csv` | 1〜2 時間 |
| 5 | 検証・テスト・Notebook の 4.9 と 8.9 の更新 | 1〜2 時間 |

**Phase 2B は Phase 3 の開始条件ではありません。** C-1A と C-1E の Level 1・2 は人工データで完結しています。
