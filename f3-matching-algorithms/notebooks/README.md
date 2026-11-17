# F3 Notebook（Google Colab・ローカル Jupyter：実験・可視化・研究発表用）

- **計算ロジックはリポジトリ直下の `.py`**（`participants.py`・`preferences.py`・`matching_algorithms.py`・`relationship_stability.py`・`evaluation.py`）にあります。Notebook はそれを import して、**実験・可視化・研究発表**を担当します。同じ計算を Notebook の中に書き直していません。
- グラフは `matching_charts.py` にまとめています（アルゴリズムの色は固定：Random オレンジ、Greedy 青、Gale–Shapley 緑）。
- すべて**教育用の架空データ・架空モデル**です。実際の結婚成立率・離婚率を予測するものではありません。

## Notebook 一覧と実行順序

| 順 | Notebook | 段階 | 内容 | 主なグラフ・表 |
| --- | --- | --- | --- | --- |
| 1 | `01_preferences_and_matching.ipynb` | Stage 1 の準備 | 架空の参加者、希望条件、希望スコア、希望順位、相互承諾 | スコアのヒートマップ（A→B、B→A、ペアの初期適合度）、希望順位の表、重みを変える TODO |
| 2 | `02_random_vs_greedy.ipynb` | Stage 1 | Random と Greedy、処理順序、成立率・初期満足度、複数シードの反復 | 成立率・満足度の棒グラフ、試行間のばらつき |
| 3 | `03_stable_matching.ipynb` | Stage 1 | Gale–Shapley の提案・仮マッチング・拒否・再提案、Blocking pair、**数学的安定性と関係継続の違い** | ステップごとの図、Greedy と Gale–Shapley の Blocking pair |
| 4 | `04_relationship_continuation.ipynb` | Stage 2 | **関係継続の時系列シミュレーション**（架空モデル）、5・10・20 年継続率、継続期間 | 初期適合度別・ストレス別の継続率曲線（理論値つき）、継続期間の分布（打ち切りを区別） |
| 5 | `05_integrated_comparison.ipynb` | Stage 3 | 成立時点と長期継続の統合比較（RQ5・RQ6）、感度分析、公平性 | 成立率・満足度・Blocking pair、初期適合度の分布、アルゴリズム別の継続率曲線、成立率と長期成立率、alpha の感度分析 |
| 6 | `06_research_presentation.ipynb` | 発表 | 研究発表テンプレート（背景 → RQ → 仮説 → アルゴリズム → 関係継続モデル → 実験条件 → 結果 → 統合評価 → 考察 → 限界 → 結論 → 今後の課題） | 成立時点・継続率・統合評価・チームの実験 |

01〜05 で実験し、その結果を 06 にまとめて発表します。各 Notebook に **TODO**（条件を変えて再実行する箇所）と考察欄があります。**研究の結論・考察は書いていません**（チームが実験して書く部分です）。

## 必要なもの

- Python 3.10 以上、`requirements-notebook.txt`（matplotlib・numpy・pandas・jupyter）
- **Google Colab には最初から入っています**。CPU ランタイムで十分です（GPU・TPU は不要）。
- pandas がない場合、表は文字で表示されます。
- Core の `.py`（`starter.py`・`experiments.py`・unittest）は標準ライブラリだけで動きます。

## ローカル（Jupyter / JupyterLab / VSCode）

```bash
cd f3-matching-algorithms
pip install -r requirements-notebook.txt
jupyter notebook notebooks/          # または jupyter lab、VSCode で .ipynb を開く
```

`notebooks/` の中で開いて、上から実行します。最初の「準備」セルが F3 のフォルダ（親フォルダ）を自動で見つけて**作業ディレクトリ**にし、`.py` を **import** します。

## Google Colab

Colab からは自分の PC（WSL）のファイルを直接読めないので、次のどちらかで F3 のフォルダを用意します。Notebook に WSL の絶対パスは書いていません。

### 方法A：GitHub から clone

1. チームの F3 リポジトリを GitHub に用意する。
2. Colab で Notebook を開き、「準備」セルの `REPO_URL` に**自分たちのリポジトリの URL**、`REPO_SUBDIR` に F3 のフォルダ名（リポジトリのルートが F3 なら `""`）を入れて実行する（`git clone` して作業ディレクトリを設定する）。
   - 非公開リポジトリでは GitHub のアクセストークンなどが必要です。トークンを Notebook に書いたまま共有しないでください。

> ⚠️ **教科書コード（`textbook/`）は公開リポジトリに含めないでください**（再配布の許諾が未確認）。`textbook/` がないと `preferences.py`・`matching_algorithms.py` の import が失敗します。その場合は方法B を使ってください。

### 方法B：ZIP をアップロードして展開

1. 自分の PC で F3 フォルダを ZIP にする（例：`zip -r f3.zip f3-matching-algorithms -x '*/__pycache__/*' '*/.venv/*'`）。
2. Colab で Notebook を開き、左側の「ファイル」から ZIP を `/content` にアップロードする（または「準備」セルの実行中に表示されるアップロード欄を使う）。
3. 「準備」セルを実行すると、ZIP を `/content/f3_upload` に展開し、`matching_algorithms.py` のあるフォルダを作業ディレクトリにして `.py` を import します。

ランタイムが切断・リセットされると、アップロードしたファイルや保存した図は消えます。

「準備」セルとグラフのセルは、Colab では**フォーム表示（コードが隠れた状態）**です。中身を見る・変えるときはセルをダブルクリックしてください。条件を変える TODO のセルは、コードが見える状態です。

## 研究発表（06）

1. タイトルにチーム名・メンバーを書く。
2. 「研究背景」「Research Question」「仮説」の **TODO** を埋める（仮説は実験の**前**に書いたもの）。
3. 「実験条件」のセル（シード数・反復回数など）を、チームの実験に合わせる。
4. 「統合評価：チームの追加実験」を、チームの実験に置き換える。
5. 「考察」「結論」「今後の課題」を書く。**どの仮定の下での結論か**を必ず添える。
6. 「モデルの限界」のスライドは削らない。

| 発表の方法 | 手順 |
| --- | --- |
| Notebook をそのまま見せる | 「すべてのセルを実行」して、見出し（`##`）ごとにスクロール |
| HTML スライドにする | `pip install nbconvert` のあと `jupyter nbconvert notebooks/06_research_presentation.ipynb --to slides --no-input --execute`。`notebooks/06_research_presentation.slides.html` をブラウザで開く（「使い方」「準備」とコードは表示されない） |
| PowerPoint・Google スライドに貼る | 「準備」セルの `SAVE_FIGURES = True` で、`notebooks/figures/*.png` に保存 |

## 注意

- 関係継続のグラフはすべて**架空モデル**の結果です（図のタイトルに `model` と書いています）。初期適合度と継続の関係は**モデルの仮定**で、実証された因果関係ではありません。
- ペアが 4 組と少ないので、結果は乱数で大きくばらつきます。**単一のシード・少ない反復回数の結果から優劣を断定しないでください。**
- 図の文字は英語です（Colab には日本語フォントがないことが多いため）。

## 検証状況

| 項目 | 状況 |
| --- | --- |
| 6 つの Notebook の形式（nbformat v4、JSON） | `nbformat.validate` で確認済み |
| ローカル（WSL2、Python 3.12、CPU）での全セル実行 | `nbclient` で確認済み（pandas あり／なしの両方でエラーなし） |
| `.py` の import、グラフの生成、計算結果の表示 | 確認済み |
| 06 の HTML スライド変換 | 確認済み |
| 保存した `.ipynb` に出力（計算結果）が含まれていない | 確認済み |
| **Google Colab 上での実行・フォーム表示** | **未検証** |

## トラブルシューティング

| 症状 | 対処 |
| --- | --- |
| `RuntimeError: F3 のフォルダが見つかりません` | ローカル：`notebooks/` の中で開く。Colab：`REPO_URL` を設定するか ZIP をアップロード |
| `ModuleNotFoundError: No module named 'textbook'` | `textbook/` がない。上の注意を参照 |
| `ModuleNotFoundError: No module named 'matplotlib'` | `pip install -r requirements-notebook.txt` |
| `.py` を変えたのに結果が変わらない | カーネル（ランタイム）を再起動して「準備」セルから実行し直す |
| 継続率が 100% になる | 係数が大きすぎて解消確率が負になり、0 に制限（clip）されている。Notebook 04 の TODO を参照 |
