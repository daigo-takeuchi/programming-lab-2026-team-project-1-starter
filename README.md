# Programming Lab 2026 — Team Project 1 Starter Repositories

## 1. プロジェクト全体の概要

Programming Lab 2026 の Team Project 1 で使う starter code（研究の出発点となるコード一式）を、1 つのリポジトリにまとめたものです。
各トピックは独立したサブディレクトリになっていて、それぞれに `README.md`・Python コード・`tests/`（unittest）があります。一部のトピックには Google Colab 用の Notebook（`notebooks/`）とサンプルデータ（`data/`）もあります。

## 2. 授業の目的

- 探索・ソート・スタック・キュー・再帰などの基本的なアルゴリズムとデータ構造を、身近な問題や社会の課題に応用する。
- 2 種類以上のアルゴリズムを同じ条件で実装・比較し、計算量と実測結果にもとづいて評価する。
- GitHub を使ったチーム開発と、研究成果の発表を経験する。

## 3. Starter Repository の使い方

1. 担当するトピックのディレクトリと `README.md` を確認する。
2. 教科書サンプルコードが必要なトピックでは、各自でダウンロードして `textbook/` に配置する（9〜11 章）。
3. `starter.py` と unittest が動くことを確認する。
4. `README.md` の研究課題・TODO に沿って研究を進める。

## 4. トピック一覧

### Team A：基本アルゴリズム

| Topic | テーマ名 | ディレクトリ | 主なアルゴリズム | README |
| --- | --- | --- | --- | --- |
| A1 | 線形探索と二分探索の性能比較 | `a1-search-algorithms/` | 線形探索・二分探索 | [README](a1-search-algorithms/README.md) |
| A2 | 基本的なソートアルゴリズムの性能比較 | `a2-sorting-algorithms/` | バブルソート・選択ソート・挿入ソート | [README](a2-sorting-algorithms/README.md) |
| A3 | スタックの実装方式と処理性能の比較 | `a3-stack-implementations/` | 固定長スタック（リスト）・deque 版スタック | [README](a3-stack-implementations/README.md) |
| A4 | キューの実装方式と処理性能の比較 | `a4-queue-implementations/` | 固定長キュー（リングバッファ）・deque 版キュー | [README](a4-queue-implementations/README.md) |

### Team B：パズル・問題解決

| Topic | テーマ名 | ディレクトリ | 主なアルゴリズム | README |
| --- | --- | --- | --- | --- |
| B1 | ルービックキューブの解法アルゴリズムと計算量の比較 | `b1-rubiks-cube-solving/` | BFS・A* | [README](b1-rubiks-cube-solving/README.md) |
| B2 | ジグソーパズルの解法と計算量 | `b2-jigsaw-puzzle-solving/` | 全探索・バックトラッキング・Greedy 法 | [README](b2-jigsaw-puzzle-solving/README.md) |

### Team C：情報・セキュリティ・システム

| Topic | テーマ名 | ディレクトリ | 主なアルゴリズム | README |
| --- | --- | --- | --- | --- |
| C1 | Web サーバーへのサイバー攻撃の検出 | `c1-web-attack-detection/` | 線形探索・辞書（ハッシュ）による集計 | [README](c1-web-attack-detection/README.md) |
| C2 | サイバー攻撃・障害に強いネットワーク構造の設計 | `c2-network-resilience/` | BFS・DFS | [README](c2-network-resilience/README.md) |
| C3 | RSA 暗号の仕組みと計算量 | `c3-rsa-cryptography/` | ユークリッドの互除法・拡張ユークリッド法・べき乗剰余 | [README](c3-rsa-cryptography/README.md) |
| C4 | ブロックチェーンの仕組みと計算量 | `c4-blockchain-algorithms/` | SHA-256・Merkle Tree | [README](c4-blockchain-algorithms/README.md) |
| C5 | EC サイトの商品検索・在庫管理 | `c5-ecommerce-search-inventory/` | 線形探索・二分探索・ソート | [README](c5-ecommerce-search-inventory/README.md) |

### Team D：社会インフラ・最適化

| Topic | テーマ名 | ディレクトリ | 主なアルゴリズム | README |
| --- | --- | --- | --- | --- |
| D1 | 携帯電話基地局・アンテナの最適配置 | `d1-cell-tower-placement/` | 全探索・Greedy 法 | [README](d1-cell-tower-placement/README.md) |
| D2 | 配送ルートの最適化 | `d2-delivery-route-optimization/` | 全探索・最近傍法・2-opt | [README](d2-delivery-route-optimization/README.md) |
| D3 | 東京圏での大地震発生時の交通規制・道路閉鎖を考慮した経路探索 | `d3-earthquake-route-planning/` | BFS・Dijkstra 法・A* | [README](d3-earthquake-route-planning/README.md) |

### Team E：AI・計算・ロボティクス

| Topic | テーマ名 | ディレクトリ | 主なアルゴリズム | README |
| --- | --- | --- | --- | --- |
| E1 | 自律移動ロボットの経路探索アルゴリズム | `e1-robot-path-planning/` | BFS・DFS・A* | [README](e1-robot-path-planning/README.md) |
| E2 | CPU・GPU・TPU による計算性能とアルゴリズムの関係 | `e2-computing-performance/` | 探索・ソート・行列積 | [README](e2-computing-performance/README.md) |
| E3 | 神経回路モデリング — ANN・SNN 比較と Spiking Manifesto の実装 | `e3-ann-snn-comparison/` | ANN・LIF ニューロン・Look-Up Table | [README](e3-ann-snn-comparison/README.md) |

### Team F：自由研究

| Topic | テーマ名 | ディレクトリ | 主なアルゴリズム | README |
| --- | --- | --- | --- | --- |
| F1 | キャリア選択と生涯所得の最適化 | `f1-career-income-optimization/` | NPV 計算・全探索・ソート | [README](f1-career-income-optimization/README.md) |
| F2 | 資産形成と早期リタイア（FIRE）のシミュレーション | `f2-financial-independence/` | シミュレーション・線形探索・ソート | [README](f2-financial-independence/README.md) |
| F3 | 出会いとマッチングのアルゴリズム | `f3-matching-algorithms/` | Gale-Shapley 法・Greedy 法・モンテカルロ法 | [README](f3-matching-algorithms/README.md) |
| F4 | パートナーシップの安定性と意思決定 | `f4-partnership-simulation/` | Greedy 法・シミュレーション・モンテカルロ法 | [README](f4-partnership-simulation/README.md) |
| F5 | 自由テーマによるアルゴリズム研究 | `f5-open-research-project/` | チームが選ぶ（初期デモは線形探索・二分探索） | [README](f5-open-research-project/README.md) |

## 5. Python プログラムの実行方法

Python 3 を使います。各トピックのディレクトリに移動してから実行します。

```bash
git clone <このリポジトリの URL>
cd programming-lab-2026-team-project-1-starter/a1-search-algorithms   # 担当トピックに移動

python3 starter.py
```

トピックによっては `benchmark.py`・`experiments.py` などもあります。詳しくは各トピックの `README.md` を参照してください。

## 6. Google Colab Notebook の利用方法

`notebooks/` があるトピック（E2・E3・F1〜F5・G1・G2）では、Notebook を Google Colab またはローカルの Jupyter / VSCode で開けます。
Notebook の最初の「準備」セルで、トピックの `.py` を import できるように設定します。手順は各トピックの `README.md` と Notebook の説明を参照してください。
Colab で実行するときも、教科書サンプルコードを `textbook/` に配置する必要があります。

## 7. unittest の実行方法

```bash
cd <トピックのディレクトリ>
python3 -m unittest discover -s tests -v
```

## 8. Core Research と Advanced Research

多くのトピックの `README.md` では、研究課題を次の 2 段階に分けています。

- **Core Research**：全チームが取り組む基本の研究課題。starter code を動かし、アルゴリズムを比較・評価する。
- **Advanced Research**：余力のあるチームが取り組む発展課題。

それぞれの内容はトピックごとに異なります。各トピックの `README.md` を参照してください。

## 9. 教科書サンプルコードの利用方法

本プロジェクトでは、柴田望洋『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』（SB クリエイティブ）のサンプルコードを学習・研究に活用します。

ただし、教科書サンプルコードのうち、再配布許諾が確認できないものは、本 GitHub リポジトリには含めていません。

学生は、教科書に案内されている公式 Web サイトから、各自でサンプルコードをダウンロードしてください。

ダウンロード後は、各トピックの README に従い、教員のローカル VSCode 環境と同じ相対ディレクトリ構成になるように必要なファイルを配置してください。

必要なファイル名と配置先については、各トピックの README を参照してください。

ダウンロードしたコードの利用にあたっては、公式サイトの利用条件を守ってください。

## 10. 教科書コードのダウンロード方法

1. 指定教科書（第2版）を手元に用意する。
2. 教科書に案内されている公式サイトにアクセスする。SB クリエイティブの書籍ページは <https://www.sbcr.jp/product/4815637217/> です（ISBN 978-4-8156-3721-7）。ダウンロードの具体的な場所は、書籍ページまたは教科書に記載された案内に従ってください。
3. サンプルソースコードを各自ダウンロードし、展開する。展開したフォルダには `chap01/`〜`chap09/` があります。

## 11. 教科書コードの配置方法

教科書のコードは、各トピックの `textbook/` の**直下**に、**ファイル名を変えずに**置きます。原本の `chapXX/` の階層は作りません。

```text
<トピックのディレクトリ>/textbook/<ファイル名>.py
```

例：原本の `chap03/bsearch.py` → `a1-search-algorithms/textbook/bsearch.py`

各トピックのコードは `from textbook.bsearch import bin_search` のように import します。この配置にすれば、コードを変更せずに実行できます。
トピックごとに必要なファイルの一覧・コピーのコマンド例・確認方法は、各トピックの `README.md` の「教科書サンプルコードの準備（GitHub から clone した場合）」にあります。

教科書のコードを使わないトピック（B2・C4・D1・D2・F5）では、配置しなくても `starter.py` と unittest を実行できます。

## 12. 著作権上の注意

- 教科書のサンプルコードは著作物です。このリポジトリには含めていません。
- `.gitignore` によって、`textbook/` に配置した教科書のコード（`*.py`）は Git の追跡対象から除外されます（`textbook/__init__.py` と `textbook/README.md` は追跡します）。
- `git add -f` などで教科書のコードを commit・push しないでください。チームのリポジトリでも同じです。
- 教科書のコードを改良する場合は、`textbook/` のファイルを書き換えずに、別のファイルとして自分のコードを書いてください。

## 13. GitHub を用いたチーム開発

- 作業はブランチを作って行い、Pull Request でレビューしてから `main` に取り込む。
- commit message には、何を変更したかを具体的に書く。
- commit 前に `python3 -m unittest discover -s tests -v` を実行し、テストが通ることを確認する。
- `git status` で、教科書のコード・`.venv/`・`__pycache__/`・秘密情報などが含まれていないことを確認する。

詳しくは各トピックの `README.md` を参照してください。

## 14. 補遺トピックの位置づけ

G1 および G2 は、通常の課題一覧には含まれない補遺・発展研究用トピックです。

| Topic | テーマ名 | ディレクトリ | 主なアルゴリズム | README |
| --- | --- | --- | --- | --- |
| G1 | 国家・世界経済の成長と資源配分の最適化 | `g1-economic-growth-optimization/` | 経済成長シミュレーション・全探索・Greedy 法 | [README](g1-economic-growth-optimization/README.md) |
| G2 | 国際紛争の抑止と協調戦略のシミュレーション | `g2-conflict-cooperation-simulation/` | ゲーム理論・状態遷移・モンテカルロ法・BFS/DFS・全探索・Greedy 法 | [README](g2-conflict-cooperation-simulation/README.md) |

G1・G2 のデータはすべて教育用の架空の値で、現実の経済・国際関係を予測するものではありません。
