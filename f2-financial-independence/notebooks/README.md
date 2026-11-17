# F2 Notebook（Google Colab・ローカル Jupyter：実験・可視化・発表用）

- **計算ロジックはリポジトリ直下の `.py`**（`financial_model.py`・`fire_analysis.py`・`retirement_model.py`・`optimization.py`）にあります。Notebook はそれを import して、**実験・可視化・発表**を担当します。同じ計算を Notebook の中に書き直していません。
- グラフは `fire_charts.py` にまとめています（シナリオの色は固定、順序のある条件は青の濃淡、未達成は値と区別して表示）。
- すべて**架空のデータによる教育用シミュレーション**です。将来の投資収益の予測や、投資・金融商品の推奨ではありません。

## Notebook 一覧と推奨順序

| 順 | Notebook | 目的 | 主なグラフ・表 |
| --- | --- | --- | --- |
| 1 | `01_savings_and_compound_interest.ipynb` | 貯蓄率と複利による資産形成（RQ1・RQ2） | 年齢別資産、貯蓄率別・収益率別の推移、拠出額と投資収益の内訳 |
| 2 | `02_fire_age_comparison.ipynb` | FIRE 目標資産と達成年齢（RQ1〜RQ3） | 目標ライン付きの資産推移、貯蓄率・収益率・生活費と FIRE 達成年齢、所得固定／貯蓄率固定の表 |
| 3 | `03_retirement_withdrawal.ipynb` | リタイア後の資産の持続（RQ4・RQ5） | FIRE 年齢でリタイアした後の推移、目標ちょうどでの収益率別推移、生活費別・収益率別、リタイア年齢別の表 |
| 4 | `04_sensitivity_analysis.ipynb` | 感度分析 | 貯蓄率 × 収益率のヒートマップ（未達成は N/A）、生活費と FIRE 年齢、トルネード図、条件別の比較表 |
| 5 | `05_research_presentation.ipynb` | **研究発表用テンプレート**（タイトル → 背景 → RQ → 仮説 → 方法 → 結果 → 考察 → 結論 → 今後の課題） | 結果 1〜4（チームの実験に差し替える） |

01〜04 で実験し、その結果を 05 にまとめて発表します。01〜04 にも **TODO**（条件を変えて再実行する箇所）と考察欄があります。

## 必要なもの

- Python 3.10 以上、`requirements-notebook.txt`（matplotlib・numpy・pandas・jupyter）
- **Google Colab には最初から入っています**。CPU ランタイムで十分です（GPU・TPU は不要）。
- pandas がない場合、表は文字で表示されます（Notebook はそのまま動きます）。
- Core の `.py`（`starter.py`・`experiments.py`・unittest）は標準ライブラリだけで動きます。

## ローカル（Jupyter / JupyterLab / VSCode）

```bash
cd f2-financial-independence
pip install -r requirements-notebook.txt
jupyter notebook notebooks/          # または jupyter lab、VSCode で .ipynb を開く
```

`notebooks/` の中で開いて、上から実行します。最初の「準備」セルが F2 のフォルダ（親フォルダ）を自動で見つけて作業ディレクトリにし、`.py` を import します。

## Google Colab

Colab からは自分の PC（WSL）のファイルを直接読めないので、次のどちらかで F2 のフォルダを用意します。

### 方法A：GitHub から clone

1. チームの F2 リポジトリを GitHub に用意する。
2. Colab で Notebook を開き、「準備」セルの `REPO_URL` に**自分たちのリポジトリの URL**、`REPO_SUBDIR` に F2 のフォルダ名（リポジトリのルートが F2 なら `""`）を入れて実行する。
   - 非公開リポジトリでは GitHub のアクセストークンなどが必要です。トークンを Notebook に書いたまま共有しないでください。

> ⚠️ **教科書コード（`textbook/`）は公開リポジトリに含めないでください**（再配布の許諾が未確認）。`textbook/` がないと `fire_analysis.py`・`optimization.py` の import が失敗します。その場合は方法B を使うか、授業で配布された `textbook/` を同じ場所に置いてください。

### 方法B：ZIP をアップロード

1. 自分の PC で F2 フォルダを ZIP にする（例：`zip -r f2.zip f2-financial-independence -x '*/__pycache__/*' '*/.venv/*'`）。
2. Colab で Notebook を開き、左側の「ファイル」から ZIP を `/content` にアップロードする（または「準備」セルの実行中に表示されるアップロード欄を使う）。
3. 「準備」セルを実行すると、ZIP を展開して `financial_model.py` のあるフォルダを作業ディレクトリにします。

ランタイムが切断・リセットされると、アップロードしたファイルや保存した図は消えます。

「準備」セルとグラフのセルは、Colab では**フォーム表示（コードが隠れた状態）**になっています。中身を見る・変えるときはセルをダブルクリックしてください。条件を変える TODO のセルは、コードが見える状態にしてあります。

## 研究発表（05）

1. タイトルのスライドにチーム名・メンバーを書く。
2. 「研究背景」「Research Question」「仮説」の **TODO** を埋める（仮説は実験の**前**に書いたものを載せる）。
3. 「方法」に、チームで変えた条件・仮定を追記する。
4. 「結果 4：チームの実験」のコードを、チームの実験に置き換える（セルを追加してもよい）。
5. 「考察」「結論」「今後の課題」を書く。**どの仮定の下での結論か**を必ず添える。
6. 「モデルの限界と注意」のスライドは削らない。

このテンプレートには、**研究の結論・考察は書いていません**（チームが書く部分です）。

### 発表のしかた

| 方法 | 手順 |
| --- | --- |
| Notebook をそのまま見せる | 「すべてのセルを実行」して、見出し（`##`）ごとにスクロール。Colab の目次から見出しへジャンプできる |
| HTML スライドにする | `pip install nbconvert` のあと `jupyter nbconvert notebooks/05_research_presentation.ipynb --to slides --no-input --execute`。`notebooks/05_research_presentation.slides.html` をブラウザで開き、矢印キーで移動（「使い方」「準備」のセルとコードは表示されない） |
| PowerPoint・Google スライドに貼る | 「準備」セルの `SAVE_FIGURES = True` にして実行すると、`notebooks/figures/*.png`（150 dpi）に保存される |

## 実験結果の保存

- グラフ：`SAVE_FIGURES = True`（`notebooks/figures/`）
- 表：`experiments.write_csv(rows, "notebooks/results.csv")` などで CSV に保存できる
- Colab では、ファイルを**ダウンロード**するか Google Drive にコピーしてください（ランタイムが切れると消える）
- 報告には、条件（貯蓄率・収益率・生活費・取り崩し率・年齢）と、**架空のデータであること**を必ず書く
- GitHub に提出する Notebook は、不要な出力を消して軽くする

## グラフの読み方

- **FIRE 未達成**：折れ線グラフでは上の灰色の帯の ×（縦軸の目盛りも「not reached」）、ヒートマップでは斜線の **N/A**。年齢の数値（0 や 80）とは別に表示しています。
- 資産推移の **点** は FIRE 達成年齢、**X** は資産が尽きた年齢です。
- 金額の単位は**万円**（軸の `[10k JPY]`）です。図の文字は英語です（Colab には日本語フォントがないことが多いため。日本語にする場合は `japanize-matplotlib` などを使う）。

## 検証状況

| 項目 | 状況 |
| --- | --- |
| 5 つの Notebook の形式（nbformat v4、JSON） | `nbformat.validate` で確認済み |
| ローカル（WSL2、Python 3.12、CPU）での全セル実行 | `nbclient` で確認済み（pandas あり／なしの両方でエラーなし） |
| `.py` の import、グラフの生成、計算結果の表示 | 確認済み |
| 05 の HTML スライド変換（`nbconvert --to slides --no-input --execute`） | 確認済み |
| 保存した `.ipynb` に出力（測定・計算結果）が含まれていない | 確認済み |
| **Google Colab 上での実行・フォーム表示** | **未検証** |

## トラブルシューティング

| 症状 | 対処 |
| --- | --- |
| `RuntimeError: F2 のフォルダが見つかりません` | ローカル：`notebooks/` の中で開く。Colab：`REPO_URL` を設定するか ZIP をアップロード |
| `ModuleNotFoundError: No module named 'textbook'` | `textbook/` がない。上の注意を参照 |
| `ModuleNotFoundError: No module named 'matplotlib'` | `pip install -r requirements-notebook.txt` |
| `.py` を変えたのに結果が変わらない | カーネル（ランタイム）を再起動して「準備」セルから実行し直す |
| グラフの日本語が文字化けする | 上の「グラフの読み方」を参照 |
