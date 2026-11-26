# data/：C-1 教材のデータ

| フォルダ | テーマ | ファイル | 件数 | 種類 | 状態 |
| --- | --- | --- | ---: | --- | --- |
| `c1a/` | C-1A ネットワーク探索・異常通信 | `network_flows_tiny.csv` | 42 | **人工データ** | 用意済み |
| | | `network_flows_small.csv` | - | 公開データ（CIC-IDS2017）を加工 | 取得待ち（Phase 2B） |
| `c1b/` | C-1B 不正認証・アカウント悪用 | `authentication_tiny.csv` | 32 | **人工データ** | 用意済み |
| | | `authentication_small.csv` | 525 | 公開ログ（Loghub OpenSSH）を加工 | 用意済み（Git 管理外。下記） |
| | | `ssh_events_small.csv` | 2,000 | 公開ログ（Loghub OpenSSH）を加工 | 用意済み（Git 管理外） |
| `c1c/` | C-1C Web・APIへの不正アクセス | `http_requests_tiny.csv` | 32 | **人工データ** | 用意済み |
| | | `web_access_log_synthetic.csv` | 47 | **人工データ**（`sample_access.log` を CSV にしたもの） | 用意済み |
| | | `http_requests_small.csv` | - | 公開データ（CSIC HTTP 2010） | 保留 |
| `c1d/` | C-1D 不正操作・システム改変 | `file_states_before_tiny.csv` / `file_states_after_tiny.csv` | 12 / 13 | **人工データ** | 用意済み |
| | | `system_events_small.csv` | 2,000 | 公開ログ（Loghub Linux）を加工 | 用意済み（Git 管理外） |
| `c1e/` | C-1E 情報流出・異常データ転送 | `data_transfer_tiny.csv` | 36 | **人工データ** | 用意済み |
| | | `data_transfer_small.csv` | - | 公開データ（CIC-IDS2017）を加工 | 取得待ち（Phase 2B） |
| （直下） | 旧 C1 教材（Web アクセスログ） | `sample_access.log` | 48 行 | **人工データ** | 旧教材のまま維持 |

## 人工データについて

- ファイル名が `_tiny` で終わる CSV は、すべて**教材用に人工的に作ったデータ**です。実在のネットワーク・利用者・Web サイト・ファイルとは関係ありません。
- IP アドレスは、説明用に予約されたアドレス（RFC 5737：`192.0.2.x`、`198.51.100.x`、`203.0.113.x`）だけを使っています。
- `label` 列は「教材として意図した役割」です。**実環境の攻撃ラベルではありません**。人工データでの検出結果を、実際の環境での性能と考えないでください。
- C-1D の `hash` 列（`H001` など）は**教材用の疑似ハッシュ値**で、本物のハッシュ値ではありません。
- C-1C のデータには、攻撃に似た文字列が**ただのテキスト**として入っています。実行したり、Web サイトに送ったりしないでください。表計算ソフトで開く場合も、編集・保存はしないでください。

## 公開ログ（Loghub）について

- `c1b/*_small.csv` と `c1d/system_events_small.csv` は、公開ログ集 **Loghub**（https://github.com/logpai/loghub）のログを教員が加工したものです。**実際に動いていたサーバーのログ**で、正解ラベルはありません（`label` は `unknown`）。
- IP アドレスとホスト名は `ip-001`、`host-001` のような匿名 ID に置き換えています。
- 利用条件：Loghub のライセンス文（各フォルダの `LICENSE_LOGHUB.txt`）に従います。データを使った成果を発表するときは、次の論文を引用してください。
  Jieming Zhu, Shilin He, Pinjia He, Jinyang Liu, Michael R. Lyu. Loghub: A Large Collection of System Log Datasets for AI-driven Log Analytics. ISSRE 2023.
- C-1D の Linux ログの元の提供者は、Public Security Log Sharing Site（Anton Chuvakin 氏）です。
- 公開ログには、表計算ソフトで数式と誤解される値（例：`-- root`）が含まれます。**表計算ソフトで開いて編集・保存しないでください。**
- これらの CSV は、再配布の条件を確認中のため Git では管理していません。教員が次の「作り直し方」で作成します。

## 作り直し方（教員向け）

```bash
python3 scripts/generate_synthetic_data.py          # Tiny Dataset を作り直す（乱数シード固定）
python3 scripts/generate_synthetic_data.py --check  # 現在のファイルと一致するか確認する
python3 scripts/download_datasets.py               # Loghub の原データを data/raw/ に取得（約 1.1MB）
python3 scripts/preprocess_c1b.py                  # C-1B（Loghub OpenSSH）
python3 scripts/preprocess_c1c.py                  # C-1C（sample_access.log → CSV）
python3 scripts/preprocess_c1d.py                  # C-1D（Loghub Linux）
python3 scripts/validate_datasets.py                # データ品質の検証
```

各列の意味は `docs/data_dictionary.md`、公開データの出典と利用条件は `docs/dataset_sources.md` を参照してください。
公開データの原データ（`data/raw/`）は Git で管理しません。
