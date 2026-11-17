# G2：国際紛争の抑止と協調戦略のシミュレーション

> **補遺トピック**
> G2 は、通常の課題一覧には含まれない補遺・発展研究用トピックです。正式な学生向け課題ではありません。

> **教育用の抽象的な仮想モデルです。**
> 国家（Country A〜E）・利得行列・状態遷移確率・係数はすべて架空の値です（`data/*.json`）。現実の国際関係・紛争や特定国家の行動を予測するものではありません。扱うのは協調・対話・信頼形成・緊張緩和だけです。

## 1. 研究テーマ

ゲーム理論、状態遷移（確率モデル）、確率シミュレーション（モンテカルロ法）、ネットワーク科学を組み合わせて、架空国家間の協調の安定性や紛争リスクを分析する教育用モデルです。

コードで実装されている内容は次のとおりです。

| 要素 | 内容 | ファイル |
| --- | --- | --- |
| ゲーム理論 | 2×2 の利得行列（協調 C／非協調 N）、4 つの戦略（Always Cooperate・Always Non-cooperate・Tit-for-Tat・Conditional）、一回限りのゲームの Nash 均衡、繰り返しゲーム | `game_theory.py` |
| 信頼度 | 国家ペアの信頼度（0〜1）を、行動・対話・協定の効果で更新する | `trust_model.py` |
| 状態遷移 | 国家ペアの関係を Cooperation・Neutral・Tension・Conflict の 4 状態で表し、確率で遷移させる | `state_transitions.py` |
| シミュレーション | 1 ステップ = 1 年の反復シミュレーションと、モンテカルロ法による平均・ばらつき | `simulation.py` |
| ネットワーク | 国家をノード、国家ペアをエッジとする無向グラフ（Line・Ring・Star・Random）、DFS・BFS、連結成分 | `network_model.py` |
| 協調支援の最適化 | 予算 K 本のエッジに協調支援を行うとき、どのエッジを選ぶかを全探索と Greedy 法で比べる | `cooperation_policies.py` |
| 評価指標 | 協調率・緊張率・紛争状態率・継続期間など | `evaluation.py` |

## 2. ファイル構成

```text
g2-conflict-cooperation-simulation/
├── README.md
├── requirements-notebook.txt     Notebook と conflict_charts.py で使うライブラリ
├── starter.py                    全体の流れを確認するデモ
├── experiments.py                研究実験の入口（Experiment 1〜7）
├── agents.py                     架空の国家と国家ペアの関係
├── game_theory.py                利得行列・戦略・繰り返しゲーム・Nash 均衡
├── trust_model.py                信頼度の更新
├── state_transitions.py          関係の状態遷移（確率モデル）
├── simulation.py                 反復シミュレーションとモンテカルロ法
├── network_model.py              国家間ネットワークと DFS・BFS
├── cooperation_policies.py       協調支援の最適化（全探索・Greedy 法）
├── evaluation.py                 評価指標
├── conflict_charts.py            Notebook 用のグラフ（matplotlib）
├── data/
│   ├── payoff_matrix.json        架空の 2×2 利得行列
│   ├── sample_countries.json     架空の国家（Country A〜E）
│   └── simulation_parameters.json  シミュレーションのパラメータ（架空の値）
├── notebooks/
│   ├── 01_game_theory.ipynb
│   ├── 02_state_transitions.ipynb
│   ├── 03_monte_carlo_simulation.ipynb
│   ├── 04_network_cooperation.ipynb
│   ├── 05_cooperation_policy_optimization.ipynb
│   └── 06_research_presentation.ipynb
├── tests/                        unittest（test_*.py と共通設定 _helpers.py）
└── textbook/                     教科書サンプルコードの配置先（下の「教科書サンプルコードの準備」を参照）
    └── __init__.py
```

## 3. 実行方法

Core（`starter.py`・`experiments.py`・unittest）は Python 3 の標準ライブラリだけで動きます。ただし、事前に教科書サンプルコードを `textbook/` に配置する必要があります（下の「教科書サンプルコードの準備」を参照）。

```bash
cd g2-conflict-cooperation-simulation

python3 starter.py                          # 全体の流れを確認するデモ
python3 experiments.py                      # Experiment 1〜7 をすべて実行
python3 experiments.py 6                    # Experiment 6 だけ実行
python3 -m unittest discover -s tests -v    # unittest
```

## 4. Notebook

`notebooks/` の Notebook は、計算をすべて既存の `.py` で行い、グラフを `conflict_charts.py` で描きます。

```bash
pip install -r requirements-notebook.txt    # matplotlib・numpy・pandas・jupyter
```

各 Notebook の最初の「準備」セルを必ず実行してください。G2 のルートを自動で探して import できるようにします。

| 実行場所 | 準備 |
| --- | --- |
| ローカルの Jupyter / VSCode | `notebooks/` の中で開けば、そのまま動きます |
| Colab（方法A：GitHub から clone） | 準備セルの `REPO_URL` に自分たちのリポジトリの URL を入れる |
| Colab（方法B：ZIP をアップロード） | G2 フォルダを ZIP にして `/content` にアップロードする |

Colab の CPU ランタイムで動きます（GPU・TPU は不要）。教科書のコードはリポジトリに含まれないため、Colab でも `textbook/` に各自で配置してください（方法B では、配置済みの G2 フォルダを ZIP にします）。

## 5. 研究実験（experiments.py）

| Experiment | 内容 |
| --- | --- |
| 1 | 戦略比較：同じ相手・同じ初期条件で 4 戦略を比べる（2 国、繰り返しゲーム） |
| 2 | 信頼度：初期信頼度を変える（5 国・リング） |
| 3 | 対話：対話・協定の有無。対照条件（対話が遷移確率に影響しないモデル）も比べる |
| 4 | 外部ショック：確率を変える |
| 5 | ネットワーク構造：Line・Ring・Star・Random |
| 6 | 協調支援の最適化：全探索と Greedy 法を、同じ候補集合・予算・評価関数で比べる |
| 7 | 感度分析：遷移確率・信頼度の更新係数・協調支援の効果を変える |

結論は、モデルの仮定（利得・遷移確率・係数）の下でだけ成り立つことに注意してください。

<!-- textbook-setup-section -->

## 教科書サンプルコードの準備（GitHub から clone した場合）

教科書：柴田望洋『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』SB クリエイティブ

再配布の許諾が確認できていないため、教科書のサンプルコードは**この GitHub リポジトリには含まれていません**。
clone した直後は `textbook/` に `__init__.py` しかなく、`starter.py` と unittest は `ModuleNotFoundError: No module named 'textbook....'` で止まります。
次の手順で、各自が教科書のコードを配置してください。

### 1. ダウンロード

1. 指定教科書（第2版）を手元に用意する。
2. 教科書に案内されている公式サイト（SB クリエイティブの書籍ページ <https://www.sbcr.jp/product/4815637217/>、または教科書に記載された案内）から、サンプルソースコードを各自ダウンロードする。
3. ダウンロードしたファイルを展開する。展開したフォルダ（以下 `<展開したフォルダ>`）には `chap01/`〜`chap09/` があります。
4. 公式サイトの利用条件を守って使ってください。

### 2. 必要なファイルと配置先

原本の `chapXX/` の階層は作らず、`textbook/` の直下にファイル名を変えずに置きます（授業の PC と同じ構成）。ファイルの中身は変更しないでください。

| 原本（展開したフォルダ内） | 配置先（リポジトリのルートから） | 使っているコード |
| --- | --- | --- |
| `chap04/fixed_queue.py` | `g2-conflict-cooperation-simulation/textbook/fixed_queue.py` | `network_model.py` |
| `chap04/fixed_stack.py` | `g2-conflict-cooperation-simulation/textbook/fixed_stack.py` | `network_model.py` |
| `chap06/insertion_sort.py` | `g2-conflict-cooperation-simulation/textbook/insertion_sort.py` | `game_theory.py` |
| `chap02/max.py` | `g2-conflict-cooperation-simulation/textbook/max.py` | `cooperation_policies.py` |
| `chap03/ssearch_while.py` | `g2-conflict-cooperation-simulation/textbook/ssearch_while.py` | `cooperation_policies.py` |

### 3. 配置後のディレクトリ構成

```text
g2-conflict-cooperation-simulation/
└── textbook/
    ├── __init__.py          （リポジトリに含まれる）
    ├── fixed_queue.py       （各自で配置）
    ├── fixed_stack.py       （各自で配置）
    ├── insertion_sort.py    （各自で配置）
    ├── max.py               （各自で配置）
    └── ssearch_while.py     （各自で配置）
```

### 4. コピーと確認のコマンド例

```bash
cd g2-conflict-cooperation-simulation
SRC="<展開したフォルダ>"        # 各自の環境に合わせる

cp -i "$SRC/chap04/fixed_queue.py" textbook/fixed_queue.py
cp -i "$SRC/chap04/fixed_stack.py" textbook/fixed_stack.py
cp -i "$SRC/chap06/insertion_sort.py" textbook/insertion_sort.py
cp -i "$SRC/chap02/max.py" textbook/max.py
cp -i "$SRC/chap03/ssearch_while.py" textbook/ssearch_while.py

# 原本とコピーの SHA-256 が一致することを確認する
sha256sum "$SRC/chap04/fixed_queue.py" textbook/fixed_queue.py
sha256sum "$SRC/chap04/fixed_stack.py" textbook/fixed_stack.py
sha256sum "$SRC/chap06/insertion_sort.py" textbook/insertion_sort.py
sha256sum "$SRC/chap02/max.py" textbook/max.py
sha256sum "$SRC/chap03/ssearch_while.py" textbook/ssearch_while.py

python3 starter.py                          # 実行確認
python3 -m unittest discover -s tests -v    # テスト
```

配置した教科書のコードは、リポジトリ直下の `.gitignore` によって Git の追跡対象から除外されます（`git status` に表示されなければ正常です）。
`git add -f` などで教科書のコードを commit・push しないでください。
