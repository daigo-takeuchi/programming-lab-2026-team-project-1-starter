# F4 の Notebook（Google Colab・ローカル Jupyter で使う実験・可視化・研究発表用）

- **計算の本体は、リポジトリ直下の `.py` にあります**（`partners.py`・`household_model.py`・`decision_strategies.py`・`relationship_dynamics.py`・`evaluation.py`）。Notebook はそれらを import して、**実験・可視化・研究発表**を担当します。同じ計算を Notebook の中に書き直してはいません。
- グラフを描く関数は `partnership_charts.py` にまとめています。
  - 戦略の色は固定：Fixed は青、Greedy はオレンジ、Fairness-aware は緑、Adaptive は黄
  - Partner A は紫、Partner B はピンク。性別とは関係のない、区別のための色です
- すべて**教育用の架空データ・架空モデル**です。実際の離婚確率や、特定の関係の将来を予測するものではありません。

## Notebook 一覧と実行順序

| 順 | Notebook | 内容 | 主なグラフ・表 |
| --- | --- | --- | --- |
| 1 | `01_housework_and_financial_sharing.ipynb` | 家事分担率、生活費の負担率、所得、労働時間、家事に使える時間、分担の実行可能性 | 家事時間の棒グラフ（家事に使える時間の上限つき）、生活費の負担の棒グラフ、所得と負担の比較 |
| 2 | `02_satisfaction_and_fairness.ipynb` | 満足度関数、希望とのずれ、平均・最低・差、公平性の定義（RQ1・RQ2） | 分担率と満足度、2 人の満足度の比較、公平性指標のヒートマップ |
| 3 | `03_decision_strategies.ipynb` | Fixed・Greedy・Fairness-aware・Adaptive、候補の全探索、λ の影響（RQ4） | 戦略別の満足度と公平性、選ばれた家事分担率・生活費の負担率の推移 |
| 4 | `04_relationship_dynamics.ipynb` | 満足度の更新、ストレスイベント、関係解消確率、継続の判定、継続期間 | 年ごとの満足度、年ごとの関係解消確率、ストレスイベント前後の満足度、継続率の曲線（理論値つき）、継続期間の分布（打ち切りを区別） |
| 5 | `05_integrated_simulation.ipynb` | 統合シミュレーション（RQ3・RQ5・RQ6）、感度分析 | 戦略別の平均満足度・最低満足度・公平性、5・10・20 年継続率、ストレス条件別の継続率、コミュニケーション条件別の継続率、パラメータの感度分析、短期の満足度と長期の継続 |
| 6 | `06_research_presentation.ipynb` | 研究発表テンプレート（研究タイトル → 背景 → RQ → 仮説 → モデル → 戦略 → 時間変化 → 実験条件 → 結果 → 考察 → 限界 → 結論 → 今後の課題） | 01〜05 の主なグラフ、チームの追加実験 |

01〜05 で実験し、その結果を 06 にまとめて発表します。

- 各 Notebook には、条件を変えて再実行する箇所（**TODO**）と考察欄があります。
- **研究の結論・考察は書いていません**。チームが実験して書く部分です。
- 保存してある Notebook には実行結果を含めていません。開いたら「準備」セルから順に実行してください。

## 必要なもの

- Python 3.10 以上と、`requirements-notebook.txt` のライブラリ（matplotlib・numpy・pandas・jupyter）
- **Google Colab にはこれらが最初から入っています**。CPU ランタイムで十分です（GPU・TPU は不要）。
- pandas がない場合、表は文字で表示されます。
- Core の `.py`（`starter.py`・`experiments.py`・unittest）は、標準ライブラリだけで動きます。

## ローカルで開く（Jupyter / JupyterLab / VSCode）

```bash
cd f4-partnership-simulation
pip install -r requirements-notebook.txt
jupyter notebook notebooks/          # または jupyter lab。VSCode なら .ipynb をそのまま開く
```

`notebooks/` の中で開いて、上から順に実行します。最初の「準備」セルが F4 のフォルダ（`notebooks/` の親フォルダ）を自動で見つけます。そのフォルダを**作業ディレクトリ**にして、`.py` を **import** します。

## Google Colab で開く

Colab からは自分の PC（WSL）のファイルを直接読めません。次の方法 A か B で F4 のフォルダを用意してください。Notebook の中に WSL の絶対パスは書いていません。

### 方法 A：GitHub から clone する

1. チームの F4 リポジトリを GitHub に用意する。
2. Colab で Notebook を開き、「準備」セルの 2 つの変数を設定して実行する。セルが `git clone` し、作業ディレクトリも設定する。
   - `REPO_URL`：**自分たちのリポジトリの URL**
   - `REPO_SUBDIR`：F4 のフォルダ名（リポジトリのルートが F4 なら `""`）
3. 非公開リポジトリには GitHub のアクセストークンなどが必要です。トークンを Notebook に書いたまま共有しないでください。

> ⚠️ **教科書のコード（`textbook/`）は公開リポジトリに含めないでください**（再配布の許諾を確認できていないため）。`textbook/` がないと `decision_strategies.py` などの import が失敗します。その場合は方法 B を使ってください。

### 方法 B：ZIP をアップロードして展開する

1. 自分の PC で F4 のフォルダを ZIP にする（例：`zip -r f4.zip f4-partnership-simulation -x '*/__pycache__/*' '*/.venv/*'`）。
2. Colab で Notebook を開き、左側の「ファイル」から ZIP を `/content` にアップロードする。「準備」セルの実行中に表示されるアップロード欄を使ってもかまいません。
3. 「準備」セルを実行する。セルは ZIP を `/content/f4_upload` に展開し、`household_model.py` のあるフォルダを作業ディレクトリにして、`.py` を import します。

ランタイムが切断・リセットされると、アップロードしたファイルや保存した図は消えます。

Colab では、「準備」セルとグラフのセルは**フォーム表示（コードが隠れた状態）**になります。中身を見たり変えたりするときは、セルをダブルクリックしてください。条件を変える TODO のセルは、コードが見える状態にしてあります。

## 研究発表（Notebook 06）

1. タイトルにチーム名とメンバーを書く。
2. 「研究背景」「Research Question」「仮説」の **TODO** を埋める。仮説は実験の**前**に書いたものにする。
3. 「実験条件」のセル（ストレスイベント・シード数・反復回数など）を、チームの実験に合わせる。
4. 「結果：チームの追加実験」を、チームの実験に置き換える。
5. 「考察」「結論」「今後の課題」を書く。**どの仮定の下での結論か**を必ず添える。
6. 「モデルの限界」のスライドは削らない。

| 発表の方法 | 手順 |
| --- | --- |
| Notebook をそのまま見せる | 「すべてのセルを実行」して、見出し（`##`）ごとにスクロールする |
| HTML スライドにする | `pip install nbconvert` のあと `jupyter nbconvert notebooks/06_research_presentation.ipynb --to slides --no-input --execute` を実行し、`notebooks/06_research_presentation.slides.html` をブラウザで開く（「使い方」「準備」とコードは表示されない） |
| PowerPoint・Google スライドに貼る | 「準備」セルで `SAVE_FIGURES = True` にすると、図が `notebooks/figures/*.png` に保存される |

## 注意

- 関係の時間変化と継続率のグラフは、すべて**架空モデル**の結果です（図のタイトルに `model` と書いています）。家事分担・コミュニケーションと関係継続の関係は**モデルの仮定**であり、実証された因果関係ではありません。
- 継続率は乱数によってばらつきます。**単一のシードや少ない反復回数の結果から、戦略の優劣を断定しないでください。**誤差棒（シード間の標準偏差）と比べて判断してください。
- 図の文字は英語です（Colab には日本語フォントがないことが多いため）。

## 検証状況

| 項目 | 状況 |
| --- | --- |
| 6 つの Notebook の形式（nbformat v4、JSON） | `nbformat.validate` で確認済み |
| ローカル（WSL2、Python 3.12、CPU）で全セルを実行 | `nbclient` で確認済み（pandas がある環境・ない環境の両方でエラーなし） |
| `.py` の import、グラフの生成、計算結果の表示 | 確認済み |
| 06 の HTML スライドへの変換 | 確認済み |
| 保存した `.ipynb` に出力（計算結果）が含まれていない | 確認済み |
| **Google Colab 上での実行・フォーム表示** | **未検証** |

## トラブルシューティング

| 症状 | 対処 |
| --- | --- |
| `RuntimeError: F4 のフォルダが見つかりません` | ローカルなら `notebooks/` の中で開く。Colab なら `REPO_URL` を設定するか、ZIP をアップロードする |
| `ModuleNotFoundError: No module named 'textbook'` | `textbook/` がない。上の注意を参照 |
| `ModuleNotFoundError: No module named 'matplotlib'` | `pip install -r requirements-notebook.txt` を実行する |
| `.py` を変えたのに結果が変わらない | カーネル（ランタイム）を再起動し、「準備」セルから実行し直す |
| 継続率が 100% や 0% に張り付く | 係数が大きすぎて、解消確率が 0〜1 の範囲で切り詰められている（clip）。`baseline_hazard`・`beta`・`gamma` を見直す |
| 戦略を変えても分担が変わらない | 実行可能な候補が 1 つもないか、候補が 1 つしかない可能性がある。Notebook 01 の「実行可能性」で確認する |
