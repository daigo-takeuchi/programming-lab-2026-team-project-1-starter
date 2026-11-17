# E2 Notebook（Google Colab・ローカル Jupyter 用）

E2「CPU・GPU・TPU による計算性能とアルゴリズムの関係」を、Notebook で測定・可視化・考察するための教材です。

- 計算の本体（Python ループ・NumPy・探索・ソート・計測）は、リポジトリ直下の `.py`（`cpu_basics.py`、`numpy_benchmark.py`、`algorithm_benchmark.py`、`benchmark_utils.py`）にあります。Notebook はそれを **import して使います**。
- PyTorch・JAX による GPU・TPU の計算は、その場で説明しながら書くために Notebook 02・03 の中にあります。

## Notebook 一覧と推奨実行順序

| 順 | Notebook | 目的 | 区分 | ランタイム | CPU での目安時間 |
| --- | --- | --- | --- | --- | --- |
| 1 | `01_python_vs_numpy.ipynb` | 同じ計算（要素ごとの演算・総和・行列積・条件分岐）を Python ループと NumPy で実行し、結果の一致・実行時間・高速化率をデータサイズごとに比べる | Core | CPU | 1 分以内 |
| 2 | `02_cpu_vs_gpu.ipynb` | PyTorch で行列積・バッチ行列積を CPU と GPU で実行。転送・初回・計算本体・取り出しを分けて測る | Core（GPU 部分は GPU がある場合のみ） | CPU / GPU | 1〜2 分 |
| 3 | `03_cpu_gpu_tpu.ipynb` | **同じ JAX 関数**を CPU とアクセラレータ（GPU・TPU）で実行。NumPy・PyTorch とも比較。コンパイル・JIT の効果 | Advanced（CPU だけでも実行可） | CPU / GPU / TPU | 1〜3 分（安全上限 300 秒） |
| 4 | `04_algorithms_and_complexity.ipynb` | 教科書の線形探索・二分探索・バブルソート・挿入ソート・マージソートと `sorted()`・`np.sort()`。理論計算量と実測時間 | Core | CPU | 1 分以内 |
| 5 | `05_research_experiments.ipynb` | Research A〜E の研究テンプレート（**結果は入っていません**） | ― | 必要に応じて | ― |

目安時間は小さな初期条件での値です（Colab では最初の import やファイルの準備に別途時間がかかります）。

## 必要ライブラリ

| ライブラリ | 使う Notebook | 備考 |
| --- | --- | --- |
| Python 3.10 以上 | すべて | `.py` の Python ループ部分は標準ライブラリだけで動く |
| NumPy、Matplotlib | すべて | Colab に標準で入っている |
| PyTorch | 02、03（なければスキップ） | Colab に標準で入っている（GPU ランタイムでは CUDA 版） |
| JAX | 03（なければスキップ） | Colab に標準で入っている（ランタイムに合った版） |
| TensorFlow | 03 の任意セル（既定では実行しない） | 参考 Notebook の TPU コードを試す場合のみ |

**Notebook は GPU・TPU 用のパッケージを自動でインストールしません。** PyTorch・JAX は CPU / GPU（CUDA のバージョン）/ TPU で正しいインストール方法が違うため、Colab では標準のものをそのまま使ってください。ローカルの CPU で試す場合の例は `requirements.txt` にあります。

## ローカル Jupyter での実行方法

```bash
cd e2-computing-performance
python3 -m venv .venv && source .venv/bin/activate     # 任意
pip install -r requirements.txt jupyter
jupyter notebook notebooks/                             # または jupyter lab
```

`notebooks/` の中で開けば、最初の「実験環境」セルが親フォルダ（E2 のルート）を自動で見つけて作業ディレクトリにします。Notebook に WSL などの絶対パスは書いていません。

## Google Colab での実行方法

Colab からは自分の PC のファイルを直接読めません。次のどちらかで E2 のフォルダを用意します。

### 方法A：GitHub から clone

1. チームの E2 リポジトリを GitHub に用意する。
2. Colab で Notebook を開き、最初の「実験環境」セルの `REPO_URL` に**自分たちのリポジトリの URL** を、`REPO_SUBDIR` に E2 のフォルダ名（リポジトリのルートが E2 なら `""`）を入れて実行する。
   - 非公開リポジトリでは GitHub のアクセストークンなどが必要です。トークンを Notebook に書いたまま共有しないでください。

> ⚠️ **教科書コード（`textbook/`）は公開リポジトリに含めないでください**（再配布の許諾が未確認）。
> `textbook/` がないと `algorithm_benchmark.py` の import が失敗し、Notebook 04 と 05 の一部が動きません。方法B を使うか、授業で配布された `textbook/` を同じ場所に置いてください。

### 方法B：ZIP をアップロード

1. 自分の PC で E2 フォルダを ZIP にする（例：`zip -r e2.zip e2-computing-performance -x '*/__pycache__/*' '*/.venv/*'`）。
2. Colab で Notebook を開き、左側の「ファイル」から ZIP を `/content` にアップロードする（または「実験環境」セルの実行中に表示されるアップロード欄を使う）。
3. 「実験環境」セルを実行すると、ZIP を展開して `cpu_basics.py` のあるフォルダを作業ディレクトリにします。

ランタイムが切断・リセットされると、アップロードしたファイルは消えます。

## ランタイムの切り替え（CPU・GPU・TPU）

Colab のメニュー名・画面の表記は変更されることがあるので、一般的な手順だけを示します。

1. Colab のメニューから「ランタイムのタイプ」を変更する設定を開く。
2. ハードウェア アクセラレータとして、**なし（CPU）**、**GPU**（例：T4）、**TPU** のいずれかを選んで保存する。
3. ランタイムが再起動されるので、Notebook を**最初のセルから**実行し直す。
4. 各 Notebook の環境表示（`CUDA GPU`、`JAX devices`、`TPU`）で、実際に使われているデバイスを確認する。

- 無料プランでは、GPU・TPU は混雑状況により**使えないこと**や、利用時間に制限があることがあります。使えなかった場合は「使えなかった」と記録してください。
- ランタイムを変更すると、変数・アップロードしたファイル・保存した結果は**消えます**。結果は先に保存してください。
- Notebook 01・04 は CPU で十分です。GPU は 02・03、TPU は 03 で使います。

## 実験結果の保存方法

- Notebook 03 は `notebooks/results/03_cpu_gpu_tpu_<cpu|gpu|tpu>.csv` に結果を保存します。他の Notebook でも `benchmark_utils.save_csv(rows, "notebooks/results/xxx.csv")` で保存できます。
- グラフは `plt.savefig("notebooks/results/xxx.png", dpi=150)` で保存できます。
- Colab では、`files.download(path)`（`from google.colab import files`）でダウンロードするか、Google Drive をマウントしてコピーしてください。
- 報告には**実行環境（環境表示の出力）・問題サイズ・dtype・乱数シード・反復回数・統計量**を必ず書いてください。
- `notebooks/results/` は `.gitignore` に入れてあります。提出する結果だけを選んで、別の場所にコピーするか `.gitignore` を調整してください。
- GitHub に提出する Notebook は、不要な出力を消して軽くしてください。

## トラブルシューティング

| 症状 | 原因と対処 |
| --- | --- |
| `RuntimeError: E2 のフォルダが見つかりません` | ローカル：`notebooks/` の中で開く。Colab：`REPO_URL` を設定する（方法A）か ZIP をアップロードする（方法B） |
| `ModuleNotFoundError: No module named 'textbook'` | `textbook/` がない。上の注意を参照 |
| PyTorch・JAX がないと表示される | ローカルでは該当部分が自動でスキップされる。試す場合は `requirements.txt` の例を参照 |
| GPU を選んだのに `CUDA GPU: not available` | GPU が割り当てられていない。ランタイムを再接続して確認する |
| TPU を選んだのに `JAX devices` が `cpu` だけ | TPU が割り当てられていない、または JAX が TPU を認識していない。Colab の JAX・TPU に関する最新の案内を確認する |
| JAX の最初の実行がとても遅い | `jit` のコンパイル（正常）。Notebook 03 ではコンパイルと計算本体を分けて記録している |
| 結果の一致チェック（`np.allclose`）で失敗する | float32 や TPU の精度設定で誤差が大きくなった可能性。許容誤差と dtype を見直す |
| メモリ不足・ランタイムが止まる | `MAX_MATRIX_N`・`MAX_VECTOR_N`・サイズのリストを小さくする |
| グラフの日本語が文字化けする | Colab には日本語フォントがないことが多いので、図の文字は英語にしている |

## 検証状況

| 項目 | 状況 |
| --- | --- |
| 5 つの Notebook の形式（nbformat v4、JSON として読める） | `nbformat.validate` で確認済み |
| CPU での全セルの実行（ローカル WSL2、Python 3.12） | `nbclient` で確認済み（PyTorch・JAX の CPU 版が**ある**環境、**ない**環境の両方でエラーなし） |
| 計算結果の正しさ | Notebook 内の `assert` と `np.allclose` で確認済み |
| GPU・TPU がない場合のスキップ | 確認済み |
| **Google Colab 上での実行** | **未検証** |
| **GPU（CUDA）での実行** | **未検証** |
| **TPU（JAX）での実行** | **未検証** |
| **TensorFlow TPU の任意セル** | **未検証**（既定では実行しない） |

GPU・TPU で実行したら、エラーの有無と結果を記録し、教員に報告してください。
