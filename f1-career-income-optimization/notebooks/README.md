# F1 Notebook（分析・発表用）

F1「キャリア選択と生涯所得の最適化」の研究を、**グラフで確かめ、そのまま発表する**ための Notebook です。

- **計算の本体は、これまでどおりリポジトリ直下の `.py`** です（`career_model.py`・`scenarios.py`・`income_analysis.py`・`optimization.py`）。Notebook はそれを import して使うだけで、同じ計算を Notebook の中に書き直していません。`.py` を直せば Notebook の結果も変わります。
- グラフは `presentation_charts.py` にまとめています（どの Notebook でも同じキャリアは同じ色、文字は大きめ）。
- すべて**架空のデータによる教育用シミュレーション**です。発表でも、そのことを必ず伝えてください。

## Notebook 一覧

| Notebook | 内容 | 主なグラフ |
| --- | --- | --- |
| `01_rq1_income_and_education.ipynb` | RQ1：18・20・22 歳で就職。年齢別所得、累積純収入、投資回収年齢、仮定の変更 | 年齢別の年収、累積純収入（回収年齢の点）、差の推移 |
| `02_rq2_rq3_certificate_and_job_change.ipynb` | RQ2：資格取得の効果と取得年齢。RQ3：転職年齢の全探索、評価基準で最適解が分かれる例 | 回収の様子、取得年齢ごとの純増加、全探索の曲線 |
| `03_rq4_npv_and_sensitivity.ipynb` | RQ4：生涯所得と NPV の順位、割引率と順位の入れ替わり、感度分析 | 指標別の棒グラフ、NPV と割引率、順位の変化、トルネード図 |
| `04_presentation.ipynb` | **発表用テンプレート**（タイトル → 問い → 仮定 → 方法 → 結果 1〜6 → 発展 → 結論 → 限界 → 参考文献）。TODO を埋めて使う | 上のグラフから発表向けに選んだ 6 枚 |

推奨の順序：01 → 02 → 03 で分析し、その結果を 04 にまとめて発表します。

## 必要なもの

- Python 3.10 以上、**matplotlib**（Notebook のグラフ用）、Jupyter（ローカルで開く場合）
- `.py` の計算部分（`starter.py`・`experiments.py`・unittest）は、これまでどおり**標準ライブラリだけ**で動きます。matplotlib が必要なのは Notebook と `presentation_charts.py` だけです。
- Google Colab には matplotlib が最初から入っています。

```bash
pip install matplotlib jupyter          # ローカルで使う場合
jupyter notebook notebooks/             # または VSCode で .ipynb を開く
```

## 開き方

### ローカル（VSCode・Jupyter）

`notebooks/` の中の `.ipynb` を開いて、上から実行します。最初の「準備」セルが F1 のフォルダ（親フォルダ）を自動で見つけます。

### Google Colab

Colab からは自分の PC のファイルを読めないので、次のどちらかで F1 のフォルダを用意します。

- **方法A：GitHub から clone**：「準備」セルの `REPO_URL` に**自分たちのリポジトリの URL** を入れる。
- **方法B：ZIP をアップロード**：F1 フォルダを ZIP にして（例：`zip -r f1.zip f1-career-income-optimization -x '*/__pycache__/*'`）、Colab の `/content` にアップロードしてから「準備」セルを実行する。

> ⚠️ `textbook/`（教科書のコード）は公開リポジトリに含めないでください。`textbook/` がないと `optimization.py` の import が失敗します。その場合は方法B を使ってください。

「準備」セルは Colab では**フォーム表示（コードが隠れた状態）**になっています。中身を見るときはセルをダブルクリックしてください。

## 発表のしかた

### 方法 1：Notebook をそのまま見せる（いちばん簡単）

1. `04_presentation.ipynb` を開き、「ランタイム → すべてのセルを実行」（Jupyter なら Run All）。
2. 見出し（`##`）ごとにスクロールしながら説明する。グラフのセルは**コードが折りたたまれて**います（Colab：フォーム表示、JupyterLab：`source_hidden`）。
3. Colab では、目次（左側のアイコン）から見出しへジャンプできます。

### 方法 2：スライド（HTML）にする

各セルにスライド用の情報（`slideshow` メタデータ）を付けてあります。`##` の見出しごとに 1 枚のスライドになり、「使い方」「準備」のセルはスライドに含まれません。

```bash
pip install nbconvert
cd f1-career-income-optimization
jupyter nbconvert notebooks/04_presentation.ipynb --to slides --no-input --execute
# → notebooks/04_presentation.slides.html をブラウザで開く（矢印キーで移動）
```

- `--no-input`：コードを表示せず、グラフと文章だけにする
- `--execute`：変換の前に全セルを実行する（最新の計算結果で作る）
- 「**TODO**：〜」の一部は、前のスライドの後に順に表示される（fragment）設定になっています
- JupyterLab の拡張機能（RISE など）でもスライドとして表示できます（任意）

### 方法 3：PowerPoint・Google スライドに図を貼る

「準備」セルの `SAVE_FIGURES = False` を `True` にして実行すると、すべてのグラフが `notebooks/figures/*.png`（150 dpi）に保存されます。これをスライドに貼ってください。

## 発表用テンプレート（04）の埋め方

1. タイトルのスライドに、チーム名・メンバーを書く。
2. 「モデルと仮定」に、チームで変えた仮定を追記する。
3. 各「結果」のコードセルの条件（`sc.with_changes(...)` など）を、研究で使った条件に変える。
4. 「**TODO**：〜」を、グラフから読み取れる**1 行のメッセージ**に書き換える（1 枚のスライドで伝えることは 1 つ）。
5. 「発展研究」に Advanced のグラフを追加する（セルを追加したら、Markdown の見出しセルのスライドの種類を「Slide」にする）。
6. 「結論」では、**どの仮定の下での結論か**を必ず書く。
7. 「モデルの限界と注意」を削らない（架空のデータ、手取りではない、所得だけで人生を評価しない、など）。

## グラフについて

- 図の文字は英語です（Colab には日本語フォントがないことが多いため）。日本語にしたい場合は、日本語フォントを用意して `plt.rcParams["font.family"]` を設定してください（例：`pip install japanize-matplotlib` して `import japanize_matplotlib`）。
- キャリアの色は固定です（Early Job：青、Vocational：オレンジ、University：緑、Certificate：黄、Job Change：ピンク）。線の終わりにも名前を書いているので、色だけに頼らずに読めます。
- 単位：金額は**万円**（軸の `[10k JPY]`）、年齢は**歳**。
- 文字をさらに大きくしたい場合は、「準備」セルの `pc.setup_style()` を `pc.setup_style(1.3)` にします。

## 検証状況

| 項目 | 状況 |
| --- | --- |
| 4 つの Notebook の形式（nbformat v4、JSON） | `nbformat.validate` で確認済み |
| ローカル（WSL2、Python 3.12、matplotlib）での全セル実行 | `nbclient` で確認済み（エラーなし） |
| `jupyter nbconvert --to slides --no-input --execute` | 確認済み（04 で 14 枚のスライド、コード・準備セルは非表示） |
| `presentation_charts.py` | `tests/test_presentation_charts.py` で確認済み（matplotlib がなければスキップ） |
| **Google Colab 上での実行・フォーム表示** | **未検証** |

## トラブルシューティング

| 症状 | 対処 |
| --- | --- |
| `RuntimeError: F1 のフォルダが見つかりません` | ローカル：`notebooks/` の中で開く。Colab：`REPO_URL` を設定するか ZIP をアップロード |
| `ModuleNotFoundError: No module named 'textbook'` | `textbook/` がない。上の注意を参照 |
| `ModuleNotFoundError: No module named 'matplotlib'` | `pip install matplotlib` |
| `.py` を変えたのに結果が変わらない | カーネルを再起動して「準備」セルから実行し直す（import 済みのモジュールは自動で読み直されない） |
| スライドでグラフが古い | `--execute` を付けて変換する |
| グラフの日本語が文字化けする | 上の「グラフについて」を参照 |
