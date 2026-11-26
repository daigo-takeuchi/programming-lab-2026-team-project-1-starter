# データセットの出典と利用条件

出力 CSV ごとの出典記録。Phase 2 で公開データ由来の CSV を作るときに、空欄を埋める。
（調査の詳細は `dataset_feasibility_report.md`）

## 1. 人工データ（教員作成）

| 出力ファイル | 作成方法 | 件数 | 利用条件 |
| --- | --- | ---: | --- |
| `data/c1a/network_flows_tiny.csv` | `scripts/generate_synthetic_data.py`（シード 2026） | 42 | 教材の一部として自由に配布可 |
| `data/c1b/authentication_tiny.csv` | 同上 | 32 | 同上 |
| `data/c1c/http_requests_tiny.csv` | 同上 | 32 | 同上 |
| `data/c1d/file_states_before_tiny.csv` | 同上 | 12 | 同上 |
| `data/c1d/file_states_after_tiny.csv` | 同上 | 13 | 同上 |
| `data/c1e/data_transfer_tiny.csv` | 同上 | 36 | 同上 |
| `data/sample_access.log` | 旧 C1 教材で手作業により作成 | 48 行 | 同上 |
| Notebook 内の Mini Dataset | Notebook に直接記述 | 各 3〜9 | 同上 |

IP アドレスは RFC 5737 のドキュメント用アドレスのみ。

## 2. 公開データ（Phase 2 で記入）

### Loghub（C-1B：OpenSSH、C-1D：Linux）

| 項目 | 内容 |
| --- | --- |
| 名称 | Loghub — OpenSSH_2k / Linux_2k |
| 提供元 | LogPAI |
| 公式 URL | https://github.com/logpai/loghub |
| ダウンロード URL | https://raw.githubusercontent.com/logpai/loghub/master/OpenSSH/OpenSSH_2k.log ／ .../Linux/Linux_2k.log |
| 取得日 | 2026-11-26（Phase 1 の調査用。Phase 2 で再取得して記録） |
| SHA-256（Phase 1 取得時） | `OpenSSH_2k.log`: `1e4912727fa88245113d41b16a0cd25ceadba7f931e1c406542885b91254264f`<br>`Linux_2k.log`: `b3e20bc1afe732ab1bf3ed1de4bf9c809e4194e02f7dea911d918e5342e8e173` |
| 利用条件 | 研究・学術目的で無償利用可。利用・配布時はリポジトリ URL の明記と論文の引用、ライセンス文の同梱 |
| 引用 | Jieming Zhu, Shilin He, Pinjia He, Jinyang Liu, Michael R. Lyu. Loghub: A Large Collection of System Log Datasets for AI-driven Log Analytics. In ISSRE, 2023. |
| 再配布 | 上記条件付きで可。**学生配布物に含める前に、教育利用の扱いを教員が確認** |
| 前処理・抽出条件・レコード数・ラベル | Phase 2 で記入 |

### CIC-IDS2017（C-1A、C-1E）

| 項目 | 内容 |
| --- | --- |
| 公式 URL | https://www.unb.ca/cic/datasets/ids-2017.html |
| ダウンロード | http://cicresearch.ca/CICDataset/CIC-IDS-2017/（登録フォーム） |
| 引用 | Iman Sharafaldin, Arash Habibi Lashkari, Ali A. Ghorbani. Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization. ICISSP 2018. |
| 再配布 | **未確認 → 学生配布物への格納は保留** |
| その他 | Phase 2 で記入 |

### CIC-Bell-DNS-EXF-2021（C-1E Level 3、オプション）

| 項目 | 内容 |
| --- | --- |
| 公式 URL | https://www.unb.ca/cic/datasets/dns-exf-2021.html |
| 引用 | Samaneh Mahdavifar, Amgad Hanafy Salem, Princy Victor, Miguel Garzon, Amir H. Razavi, Natasha Hellberg, Arash Habibi Lashkari. Lightweight Hybrid Detection of Data Exfiltration using DNS based on Machine Learning. IEEE ICCNS 2021. |
| 再配布 | 公式ページに再配布・ミラーを認める記載あり（データセットと論文の引用が条件） |

### CSIC HTTP 2010（C-1C、保留）

公式サイトに接続できず、利用条件は未確認。入手経路の確認後に記入する。
