# F5 の Notebook（Google Colab・ローカル Jupyter：研究計画・実装・比較・研究発表用）

- **計算の本体は `.py` にあります。**
  - `algorithms/`：アルゴリズム
  - `experiments/benchmark.py`：実行時間の測定
  - `experiments/compare_algorithms.py`：比較
  - `experiments/plots.py`：グラフ
- Notebook はこれらを import して、**研究計画・検証・実験・可視化・発表**を担当します。アルゴリズムを Notebook の中に書き直さないでください。
- 初期デモ（**線形探索 vs 二分探索**）は、比較の方法を示す**教材例**です。研究テーマを固定するものではありません。

## Notebook 一覧と実行順序

| 順 | Notebook | 内容 | 主なグラフ・表 |
| --- | --- | --- | --- |
| 1 | `01_research_question.ipynb` | 研究計画のテンプレート（研究タイトル、背景、解決したい問題、Research Question、仮説、入力、出力、使用するアルゴリズム、比較対象、評価指標）。初期デモの記入例つき | 入力データの例 |
| 2 | `02_algorithm_implementation.ipynb` | Algorithm A・B の説明、入力と出力、実行、比較回数、正しさの検証（ランダムな入力・境界条件・unittest）、計算量の考察 | 比較回数の表、検証結果 |
| 3 | `03_algorithm_comparison.ipynb` | 入力サイズ・反復測定・前処理の有無を区別した比較、理論計算量と実測の比較、アルゴリズムの追加例 | 入力サイズと実行時間、サイズごとの A・B 比較（前処理なし／あり）、理論計算量の増え方、実測と理論の比較、比較回数、反復測定のばらつき、3 つのアルゴリズムの比較 |
| 4 | `04_research_presentation.ipynb` | 研究発表テンプレート（研究タイトル → 背景 → RQ → 仮説 → 使用したアルゴリズム → 実験方法 → 理論計算量 → 実測結果 → グラフ → 考察 → 結論 → 今後の課題） | 理論計算量、実測結果の表、入力サイズと実行時間、A・B の比較、比較回数 |

- 各 Notebook に、条件を変える箇所（**TODO**）と考察欄があります。
- **研究の結論や考察は書いていません。**チームが実験して書く部分です。
- 保存してある Notebook には、実行結果（実測値）を含めていません。実測値は、自分の環境で実行して得てください。

## 研究テーマを変えたとき

1. 「準備」セルの `from algorithms import algorithm_a as alg_a` などを、チームのモジュールに変える。
2. 03・04 の `ca.make_search_task(...)` を、チームの課題（task）に変える（README「研究テーマを変更する方法」）。
3. 02 の説明・検証のセルを、チームのアルゴリズムに合わせて書き換える。

## 必要なもの

- Python 3.10 以上と、`requirements-notebook.txt` のライブラリ（matplotlib・numpy・pandas・jupyter）
- **Google Colab には最初から入っています。**CPU ランタイムで十分です（GPU・TPU は不要）。
- pandas がない場合、表は文字で表示されます。

## ローカルで開く（Jupyter / JupyterLab / VSCode）

```bash
cd f5-open-research-project
pip install -r requirements-notebook.txt
jupyter notebook notebooks/          # または jupyter lab。VSCode なら .ipynb をそのまま開く
```

`notebooks/` の中で開いて、上から順に実行します。最初の「準備」セルが F5 のフォルダ（`notebooks/` の親フォルダ）を自動で見つけて**作業ディレクトリ**にし、`algorithms`・`experiments` を **import** します。

## Google Colab で開く

Colab からは自分の PC（WSL）のファイルを直接読めないので、次のどちらかで F5 のフォルダを用意します。Notebook に WSL の絶対パスは書いていません。

### 方法 A：GitHub から clone する

1. チームの F5 リポジトリを GitHub に用意する。
2. Colab で Notebook を開き、「準備」セルに次の 2 つを入れて実行する。セルが `git clone` し、作業ディレクトリを設定します。
   - `REPO_URL`：**自分たちのリポジトリの URL**
   - `REPO_SUBDIR`：F5 のフォルダ名（リポジトリのルートが F5 なら `""`）
3. 非公開リポジトリには、GitHub のアクセストークンなどが必要です。トークンを Notebook に書いたまま共有しないでください。

### 方法 B：ZIP をアップロードして展開する

1. 自分の PC で F5 のフォルダを ZIP にする（例：`zip -r f5.zip f5-open-research-project -x '*/__pycache__/*' '*/.venv/*'`）。
2. Colab の左側の「ファイル」から、ZIP を `/content` にアップロードする（「準備」セルの実行中に表示されるアップロード欄でもよい）。
3. 「準備」セルを実行する。セルが ZIP を `/content/f5_upload` に展開し、`algorithms/algorithm_a.py` のあるフォルダを作業ディレクトリにします。

ランタイムが切断・リセットされると、アップロードしたファイルや保存した図は消えます。

Colab では、「準備」セルとグラフのセルが**フォーム表示（コードが隠れた状態）**になります。中身を見るときはダブルクリックしてください。条件を変える TODO のセルは、コードが見える状態です。

## 実行時間について

- Colab とローカルでは、実行時間が違います。Colab では、同じ Notebook を実行するたびに違うこともあります（共有の計算機のため）。
- 比べるアルゴリズムは、**同じ環境・同じ実行の中で**測ってください。
- 実行環境は「準備」セルの出力（`ca.environment()`）で確認し、`docs/experiment_log.md` に記録してください。

## 研究発表（Notebook 04）

| 発表の方法 | 手順 |
| --- | --- |
| Notebook をそのまま見せる | 「すべてのセルを実行」して、見出し（`##`）ごとにスクロール |
| HTML スライドにする | `pip install nbconvert` のあと `jupyter nbconvert notebooks/04_research_presentation.ipynb --to slides --no-input --execute`。`notebooks/04_research_presentation.slides.html` をブラウザで開く（「使い方」「準備」とコードは表示されない） |
| PowerPoint・Google スライドに貼る | 「準備」セルで `SAVE_FIGURES = True` にすると、`notebooks/figures/*.png` に保存される |

## 検証状況

| 項目 | 状況 |
| --- | --- |
| 4 つの Notebook の形式（nbformat v4、JSON） | `nbformat.validate` で確認済み |
| ローカル（WSL2、Python 3.12、CPU）での全セル実行 | `nbclient` で確認済み（pandas あり／なしの両方でエラーなし） |
| `.py` の import、グラフの生成 | 確認済み |
| 04 の HTML スライドへの変換 | 確認済み |
| 保存した `.ipynb` に出力（実測値）が含まれていない | 確認済み |
| **Google Colab 上での実行・フォーム表示** | **未検証** |

## トラブルシューティング

| 症状 | 対処 |
| --- | --- |
| `RuntimeError: F5 のフォルダが見つかりません` | ローカル：`notebooks/` の中で開く。Colab：`REPO_URL` を設定するか、ZIP をアップロードする |
| `ModuleNotFoundError: No module named 'algorithms'` | 「準備」セルを先に実行する |
| `.py` を変えたのに結果が変わらない | カーネル（ランタイム）を再起動して、「準備」セルから実行し直す |
| 実行時間が毎回大きく違う | REPEAT を増やす。他のプログラムを閉じる。中央値と最小〜最大を報告する |
| 測定に時間がかかりすぎる | SIZES・REPEAT・QUERIES を小さくして試してから増やす |
