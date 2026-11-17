# E3 Notebook（Google Colab・ローカル Jupyter 用）

E3「ANN・SNN 比較と Spiking Manifesto の実装」を、Notebook で**理解・可視化・実験**するための教材です。

- アルゴリズムの**基準実装**は、リポジトリ直下の `.py`（`ann.py`、`lif_snn.py`、`spike_encoding.py`、`spike_lut.py`、`benchmark.py`）にあります。Notebook はそれを **import して使う**だけで、同じアルゴリズムを Notebook の中に書き直していません。
- CPU・GPU・TPU 向けのバッチ（Tensor）実装は `tensor_backends.py` にあります（NumPy・PyTorch・JAX）。基準実装と結果が一致することを `tests/test_tensor_backends.py` で確認しています。
- この教材は Spiking Manifesto（arXiv:2512.11843）の中心的なアイデアを**教育用に簡略化**したものです。論文のモデル・著者の実装そのものではありません。

## Notebook 一覧と推奨実行順序

| 順 | Notebook | 目的 | 使う既存コード | CPU での目安時間 |
| --- | --- | --- | --- | --- |
| 1 | `01_ann_lif_basics.ipynb` | ANN（重み付き和・ReLU）と LIF ニューロン（膜電位・閾値・スパイク・発火率・latency）の基礎 | `ann.py`、`lif_snn.py` | 1 分以内 |
| 2 | `02_spike_timing_and_lut.ipynb` | spike timing・spike order、pairwise comparison → binary index → LUT 行の選択 → 出力 latency vector、ノイズへの頑健性 | `spike_encoding.py`、`spike_lut.py` | 1 分以内 |
| 3 | `03_ann_vs_snn_benchmark.ipynb` | ANN・LIF-SNN・LUT の演算回数・パラメータ数・メモリ・実行時間（純 Python、CPU） | 上記 ＋ `benchmark.py` | 1 分程度 |
| 4 | `04_colab_cpu_gpu_tpu.ipynb` | **ANN と LUT を CPU・GPU・TPU で比較**（NumPy・PyTorch・JAX、初回・コンパイル・転送・計算本体を区別） | `tensor_backends.py` ほか | 各ランタイム数分以内（安全上限 `TIME_BUDGET_S = 300` 秒） |
| 5 | `05_research_experiments.ipynb` | 学生が研究課題（Research A〜E）を選んで実験を追加するテンプレート（**結果は入っていません**） | すべて | ― |

目安時間は小さな初期条件での値です。Colab では最初のライブラリ読み込みや、ZIP のアップロードに別途時間がかかります。

## 必要ライブラリ

| ライブラリ | 使う Notebook | 備考 |
| --- | --- | --- |
| Python 3.10 以上 | すべて | 既存の `.py` は標準ライブラリだけで動きます |
| NumPy | すべて | Colab には最初から入っています |
| Matplotlib | すべて | Colab には最初から入っています |
| PyTorch | 04（なければスキップ） | Colab には通常入っています。GPU ランタイムでは CUDA 版 |
| JAX | 04（なければスキップ） | Colab には通常入っています。TPU ランタイムでは TPU 対応版が使われる想定です（下の「未検証」を参照） |

ローカルで Notebook を実行・検証する場合は、Jupyter（`jupyter`、または `nbclient` ＋ `ipykernel`）も必要です。

## ローカル Jupyter での実行方法

```bash
cd e3-ann-snn-comparison
python3 -m venv .venv && source .venv/bin/activate      # 任意
pip install numpy matplotlib jupyter                     # 04 で PyTorch・JAX も試すなら: pip install torch jax
jupyter notebook notebooks/                              # または jupyter lab
```

`notebooks/` の中で開けば、各 Notebook の最初の「実験環境」セルが**親フォルダ（E3 のルート）を自動で見つけて**作業ディレクトリに設定します。WSL などの絶対パスを Notebook に書く必要はありません。

## Google Colab での実行方法

Colab からは、自分の PC（WSL など）のファイルを直接読めません。次のどちらかで E3 のフォルダを Colab に用意します。

### 方法A：GitHub から clone

1. チームの E3 リポジトリを GitHub に用意する。
2. Colab で Notebook を開く（GitHub から開く、または `.ipynb` をアップロード）。
3. 最初の「実験環境」セルの `REPO_URL` に**自分たちのリポジトリの URL** を入れ、`REPO_SUBDIR` に E3 のフォルダ名（リポジトリのルートが E3 なら `""`）を入れて実行する。
   - 非公開リポジトリの場合は、GitHub のアクセストークンなどが必要です。トークンを Notebook に書いたまま共有しないでください。

> ⚠️ **教科書コード（`textbook/`）の扱い**
> `textbook/` は第三者の著作物で、公開再配布の許諾は確認できていません。**公開リポジトリには含めないでください。**
> `textbook/` がないと `spike_encoding.py`・`benchmark.py` の import が失敗します（Notebook はその旨を表示します）。
> 方法A で使う場合は、非公開リポジトリにするか、授業で配布された `textbook/` を Colab 上の同じ場所に置いてください。

### 方法B：ZIP をアップロード

1. 自分の PC で `e3-ann-snn-comparison` フォルダを ZIP にする（例：`zip -r e3.zip e3-ann-snn-comparison -x '*/__pycache__/*' '*/.venv/*'`）。
2. Colab で Notebook を開き、左側の「ファイル」から ZIP を `/content` にアップロードする（または「実験環境」セルの実行中に表示されるアップロード欄を使う）。
3. 「実験環境」セルを実行すると、ZIP を展開して `spike_lut.py` のあるフォルダを探し、そこを作業ディレクトリにします。

> Colab のランタイムが切断・リセットされると、アップロードしたファイルは消えます。そのときはもう一度アップロードしてください。

## ランタイムの設定

Colab のメニュー名・画面の表記は変更されることがあります。ここでは一般的な手順だけを示します。

| ランタイム | 設定 | 確認方法 |
| --- | --- | --- |
| **CPU** | ランタイムのタイプの設定で、ハードウェア アクセラレータを「なし」または CPU にする | Notebook 04 の環境表示で `CUDA GPU: not available`、`TPU: not available` |
| **GPU** | ランタイムのタイプの設定で、GPU（例：T4）を選ぶ | Notebook 04 で `CUDA GPU:` に GPU 名が表示される。`JAX devices` に `gpu` が出ることもある |
| **TPU** | ランタイムのタイプの設定で、TPU を選ぶ | Notebook 04 で `JAX devices` に `tpu:...` が表示され、`TPU: available` になる |

- 無料プランでは、GPU・TPU は**混雑状況により使えない**ことや、利用時間に制限があることがあります。使えなかった場合は「使えなかった」と記録してください。
- ランタイムを変更すると、変数・アップロードしたファイル・保存した結果は**消えます**。結果は必ず先に保存してください。
- Notebook 01〜03・05 は CPU ランタイムで十分です。GPU・TPU を使うのは Notebook 04（と Research C）だけです。

## 実験結果の保存方法

- Notebook 04 は、測定結果を `notebooks/results/04_benchmark_<cpu|gpu|tpu>.csv` に保存します（ランタイムの種類でファイル名が変わります）。
- Colab では、次のいずれかで手元に残してください。
  - セル内の `files.download(out_path)` のコメントを外して実行し、ダウンロードする
  - Google Drive をマウントしてコピーする（`from google.colab import drive; drive.mount('/content/drive')`）
- 3 つのランタイムの CSV を `notebooks/results/` に集めてから Notebook 04 の 6-5 や Notebook 05 の Research C を実行すると、ランタイムをまたいで比較できます。
- グラフは `plt.savefig("notebooks/results/xxx.png", dpi=150)` で保存できます。
- 報告には、**実行環境（Notebook 04 の環境表示）・問題規模・乱数シード・測定回数**を必ず一緒に書いてください。
- GitHub に提出する Notebook は、不要な出力を消して軽くしてください（必要な図と表だけ残す）。

## 測定についての注意

- **測っていないデバイスの数値を書かないでください。** Notebook 04 は、実際に測定できたデバイス・フレームワークだけを表とグラフに表示します。
- ANN の forward、LIF の時間発展、LUT の forward は**計算の内容が違います**。実行時間が同じでも、同じ機能・精度という意味ではありません。
- Colab の CPU・GPU・TPU の実行時間から、**SNN 専用ニューロモルフィックハードウェアの電力効率は結論できません**。消費電力は測っていません。

## トラブルシューティング

| 症状 | 原因と対処 |
| --- | --- |
| `RuntimeError: E3 のフォルダが見つかりません` | ローカル：`notebooks/` の中で Notebook を開く。Colab：`REPO_URL` を設定する（方法A）か、ZIP をアップロードする（方法B） |
| `ModuleNotFoundError: No module named 'textbook'` | `textbook/` がない（公開リポジトリから clone した場合など）。上の「教科書コードの扱い」を参照 |
| `ModuleNotFoundError: No module named 'torch'`／`'jax'` | ローカルでは Notebook 04 のその部分が自動でスキップされます。試したい場合は `pip install torch jax` |
| GPU を選んだのに `CUDA GPU: not available` | ランタイムの設定が反映されていない、または GPU が割り当てられなかった。ランタイムを再接続して確認する |
| TPU を選んだのに `JAX devices` が `cpu` だけ | TPU が割り当てられなかった、または JAX が TPU を認識していない。Colab の JAX・TPU に関する最新の案内を確認する |
| JAX の最初の実行がとても遅い | `jit` のコンパイルです（正常）。Notebook 04 ではコンパイル時間と計算本体を分けて記録しています |
| GPU で 1 回目だけ遅い | CUDA の初期化などを含むため（正常）。ウォームアップ後の中央値で比べます |
| 結果の一致チェック（`assert_allclose`）で失敗する | dtype や行列積の精度設定（TPU の bfloat16 など）を変えた場合は、許容誤差を見直す。LUT の index は整数なので完全一致するはずです |
| グラフの日本語が文字化けする | Colab には日本語フォントがないことが多いので、この教材の図の文字は英語にしています |
| メモリ不足・時間がかかりすぎる | `MAX_BYTES`・`TIME_BUDGET_S`・`BATCH_SIZES`・`nc` を小さくする（LUT の大きさは $2^{n_c}$ に比例） |

## 検証状況

| 項目 | 状況 |
| --- | --- |
| 5 つの Notebook の形式（nbformat v4 として妥当、JSON として読める） | `nbformat.validate` で確認済み |
| CPU での全セルの実行（ローカル WSL2、Python 3.12、NumPy・Matplotlib・PyTorch CPU 版・JAX CPU 版） | `nbclient` で実行し、エラーなしを確認済み |
| ANN・LIF・spike timing・LUT index の値 | Notebook 内の `assert`（README の値と一致）で確認済み |
| NumPy・PyTorch（CPU）・JAX（CPU）版と基準実装の一致 | `tests/test_tensor_backends.py`、Notebook 04 内の確認で確認済み |
| GPU・TPU がない環境でのスキップ | 確認済み（PyTorch・JAX が**ない**環境、ある環境の両方） |
| **Google Colab 上での実行** | **未検証** |
| **GPU（CUDA）での実行** | **未検証** |
| **TPU（JAX）での実行** | **未検証** |

GPU・TPU で実行したら、エラーの有無と結果を記録し、教員に報告してください。

## 出典

- 論文：E. Izhikevich, "Spiking Manifesto", arXiv:2512.11843, 2025.（arXiv の表示ライセンス：CC BY-NC-SA 4.0）
- Notebook 04 は、授業の `ai-programming-2026-team-project-1-starter` リポジトリの `A_cpu_gpu_tpu/A_cpu_gpu_tpu_benchmark/starter.ipynb`（MIT License, Copyright (c) 2026 Daigo Takeuchi）の構成（環境チェック、CUDA の同期、使えないデバイスのスキップ、棒グラフ）を参考にし、E3 向けに書き直しました。コードをそのままコピーしてはいません。
- 教科書：柴田望洋『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』SBクリエイティブ（`textbook/` の扱いは上の注意を参照）
