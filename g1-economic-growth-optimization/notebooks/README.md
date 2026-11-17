# G1 の Notebook（Google Colab・ローカル Jupyter：実験・可視化・研究発表用）

- **計算の本体は、リポジトリ直下の `.py` にあります**（`economic_model.py`・`simulation.py`・`allocation_strategies.py`・`optimization.py`・`evaluation.py`）。Notebook はそれらを import して、**実験・可視化・研究発表**を担当します。同じ計算を Notebook の中に書き直してはいません。
- グラフを描く関数は `growth_charts.py` にまとめています。色は固定です。
  - 分野：教育は青、研究開発はオレンジ、インフラは緑、医療は黄
  - アルゴリズム：全探索は濃い灰色、Greedy はピンク、局所探索は紫
- G1 は**補遺トピック**です。すべて**教育用の架空モデル**で、現実の国家の GDP・成長率・政策効果を予測しません。

## Notebook 一覧と実行順序

| 順 | Notebook | 内容 | 主なグラフ・表 |
| --- | --- | --- | --- |
| 1 | `01_economic_growth_model.ipynb` | 状態変数、投資効果（収穫逓減）、遅延のキュー、減耗、GDP、生活水準、20 年間のシミュレーション、GDP 変化の分解 | 状態変数の時系列（6 つのグラフ）、シナリオ別の GDP・人的資本・技術・生活水準の時系列 |
| 2 | `02_investment_allocation.ipynb` | 均等配分・教育重視・研究開発重視・インフラ重視・医療重視の比較（RQ1・RQ2） | 投資配分の積み上げ棒グラフ、GDP 成長曲線、GDP 指数と生活水準の比較、分野別の状態変数 |
| 3 | `03_optimization_algorithms.ipynb` | 全探索・Greedy 法・局所探索、目的関数、予算制約、計算量（刻みを変える）、初期配分の影響（RQ4） | 目的関数値・実行時間・評価候補数、各アルゴリズムの配分、Greedy 法・局所探索の途中経過 |
| 4 | `04_growth_vs_living_standard.ipynb` | GDP・1 人あたり GDP・健康指数・人的資本指数・生活水準、目的関数別の最適配分（RQ2・RQ6） | 目的関数別の最適配分、全配分候補の GDP と生活水準の散布図、GDP 重視と生活水準重視の比較 |
| 5 | `05_sensitivity_analysis.ipynb` | 投資効率・予算規模・評価期間・減耗率・遅延の感度分析（RQ3・RQ5） | 投資効率と最適配分、予算規模と GDP、評価期間と最適配分、パラメータ感度のヒートマップ |
| 6 | `06_research_presentation.ipynb` | 研究発表テンプレート（研究タイトル → 背景 → RQ → 仮説 → モデル → 配分 → アルゴリズム → 実験条件 → 結果 → 感度分析 → 考察 → 限界 → 結論 → 今後の課題） | 01〜05 の主なグラフ |

- 01〜05 で実験し、その結果を 06 にまとめて発表します。
- 各 Notebook には、条件を変える箇所（**TODO**）と考察欄があります。**研究の結論・考察は書いていません。**
- 保存した Notebook には実行結果を含めていません。開いたら「準備」セルから実行してください。

## 必要なもの

- Python 3.10 以上と、`requirements-notebook.txt` のライブラリ（matplotlib・numpy・pandas・jupyter）
- **Google Colab にはこれらが最初から入っています**。CPU ランタイムで十分です（GPU・TPU は不要）。
- pandas がない場合、表は文字で表示されます。
- Core の `.py`（`starter.py`・`experiments.py`・unittest）は標準ライブラリだけで動きます。

## ローカルで開く（Jupyter / JupyterLab / VSCode）

```bash
cd g1-economic-growth-optimization
pip install -r requirements-notebook.txt
jupyter notebook notebooks/          # または jupyter lab。VSCode なら .ipynb をそのまま開く
```

`notebooks/` の中で開いて、上から順に実行します。最初の「準備」セルが G1 のフォルダ（`notebooks/` の親フォルダ）を自動で見つけて**作業ディレクトリ**にし、`.py` を **import** します。

## Google Colab で開く

Colab からは自分の PC（WSL）のファイルを直接読めないので、次のどちらかで G1 のフォルダを用意します。Notebook に WSL の絶対パスは書いていません。

### 方法 A：GitHub から clone する

1. チームの G1 リポジトリを GitHub に用意する。
2. Colab で Notebook を開き、「準備」セルに次の 2 つを入れて実行する。セルが `git clone` し、作業ディレクトリを設定します。
   - `REPO_URL`：**自分たちのリポジトリの URL**
   - `REPO_SUBDIR`：G1 のフォルダ名（リポジトリのルートが G1 なら `""`）
3. 非公開リポジトリには、GitHub のアクセストークンなどが必要です。トークンを Notebook に書いたまま共有しないでください。

> ⚠️ **教科書のコード（`textbook/`）は、公開リポジトリに含めないでください**（再配布の許諾が未確認のため）。`textbook/` がないと import が失敗します。その場合は方法 B を使ってください。

### 方法 B：ZIP をアップロードして展開する

1. 自分の PC で G1 のフォルダを ZIP にする（例：`zip -r g1.zip g1-economic-growth-optimization -x '*/__pycache__/*' '*/.venv/*'`）。
2. Colab の左側の「ファイル」から、ZIP を `/content` にアップロードする（「準備」セルの実行中に表示されるアップロード欄でもよい）。
3. 「準備」セルを実行する。セルが ZIP を `/content/g1_upload` に展開し、`economic_model.py` のあるフォルダを作業ディレクトリにします。

ランタイムが切断・リセットされると、アップロードしたファイルや保存した図は消えます。

Colab では、「準備」セルとグラフのセルが**フォーム表示（コードが隠れた状態）**になります。中身を見るときはダブルクリックしてください。条件を変える TODO のセルは、コードが見える状態です。

## 研究発表（Notebook 06）

| 発表の方法 | 手順 |
| --- | --- |
| Notebook をそのまま見せる | 「すべてのセルを実行」して、見出し（`##`）ごとにスクロール |
| HTML スライドにする | `pip install nbconvert` のあと `jupyter nbconvert notebooks/06_research_presentation.ipynb --to slides --no-input --execute`。`notebooks/06_research_presentation.slides.html` をブラウザで開く（「使い方」「準備」とコードは表示されない） |
| PowerPoint・Google スライドに貼る | 「準備」セルで `SAVE_FIGURES = True` にすると、図が `notebooks/figures/*.png` に保存される |

## 注意

- グラフはすべて**架空モデル**の計算結果です（タイトルに `model` と書いています）。
- 実行時間のグラフ（Notebook 03）だけは、その PC での**実測値**です。実行するたびに少し変わります。評価候補数と一緒に見てください。
- 「最適配分」は、**目的関数・評価期間・刻み・パラメータ**によって変わります。必ず条件を添えて報告してください。
- 図の文字は英語です（Colab には日本語フォントがないことが多いため）。

## 検証状況

| 項目 | 状況 |
| --- | --- |
| 6 つの Notebook の形式（nbformat v4、JSON） | `nbformat.validate` で確認済み |
| ローカル（WSL2、Python 3.12、CPU）での全セル実行 | `nbclient` で確認済み（pandas あり／なしの両方でエラーなし） |
| `.py` の import、グラフの生成 | 確認済み |
| 06 の HTML スライドへの変換 | 確認済み |
| 保存した `.ipynb` に出力（計算結果）が含まれていない | 確認済み |
| **Google Colab 上での実行・フォーム表示** | **未検証** |

## トラブルシューティング

| 症状 | 対処 |
| --- | --- |
| `RuntimeError: G1 のフォルダが見つかりません` | ローカル：`notebooks/` の中で開く。Colab：`REPO_URL` を設定するか、ZIP をアップロードする |
| `ModuleNotFoundError: No module named 'textbook'` | `textbook/` がない。上の注意を参照 |
| `ValueError: 配分率の合計は 1 にしてください` | 新しい配分シナリオの合計を 1 にする |
| `ValueError: 刻み … は 1 を割り切りません` | 刻みは 0.05・0.1・0.2・0.25 など、1 を割り切る値にする |
| 全探索に時間がかかる | 刻みを大きくする（0.05 で 1,771 通り、0.02 で 23,426 通り） |
| `.py` を変えたのに結果が変わらない | カーネル（ランタイム）を再起動して、「準備」セルから実行し直す |
