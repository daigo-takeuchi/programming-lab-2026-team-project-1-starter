# E2：CPU・GPU・TPU による計算性能とアルゴリズムの関係

> ⚠️ **公開前の注意**
> `textbook/` 内のコードは第三者の著作物です（出典は「20. 参考文献・著作権上の注意」参照）。
> 再配布の可否はまだ確認できていないため、このディレクトリは**ローカルの教材用**です。
> GitHub などで公開・配布する前に、必ず出版社の再配布条件を確認してください。

---

## 1. 研究テーマと目的

**E2：CPU・GPU・TPU による計算性能とアルゴリズムの関係を調べる**

Python の for ループ、NumPy のベクトル演算、GPU による並列処理、TPU による計算を比較し、**アルゴリズム・データ構造・実装方法・計算デバイス**が処理性能に与える影響を研究します。

| | 問い |
| --- | --- |
| RQ1 | **同じアルゴリズムでも実装方法で処理時間は変わるか**（Python の for ループ、NumPy、PyTorch） |
| RQ2 | **問題サイズによって最適な実行方法は変わるか**（$n$ = 100 〜 1,000,000） |
| RQ3 | **CPU・GPU・TPU では何が異なるか**（デバイスの違いと、ライブラリ・実装の違いを区別する） |
| RQ4 | **計算の種類によって高速化の効果は変わるか**（要素ごとの演算、総和、行列積、条件分岐、探索・ソート） |

> **最も大切な考え方**
> - **理論計算量が同じでも、実行時間は大きく違うことがある**（実装・データ構造・ハードウェアによる定数倍の差）。
> - 一方で、**ベクトル化や GPU 実行によって、アルゴリズムの計算量のオーダーが改善するわけではない**。$O(n^2)$ のアルゴリズムは、GPU で動かしても $O(n^2)$ のまま。

- **Core Research（必須課題）**：CPU だけで完了できる。Python ループと NumPy の比較、CPU 上の NumPy と PyTorch、（GPU があれば）GPU の行列積、探索・ソートの計算量
- **Advanced Research（発展課題）**：TPU と JAX、大規模行列積、アルゴリズムの並列化可能性、メモリ帯域とデータ転送、公平な比較

## 2. CPU・GPU・TPU の基本

| | CPU | GPU | TPU |
| --- | --- | --- | --- |
| 設計の考え方 | 少数の高性能コアで、どんな処理も速く | 数千の単純なコアで、同じ計算を一斉に | 行列積専用の回路（systolic array） |
| 得意 | 分岐・逐次処理・小さな計算・不規則なメモリアクセス | 大きな行列積、要素ごとの演算をまとめて大量に | 大きな行列積（特に bfloat16） |
| 苦手 | 大量の同じ計算（コア数が少ない） | 小さな計算（起動の固定コスト）、分岐の多い処理 | shape が変わる計算、細かい分岐 |
| メモリ | メインメモリ | GPU 専用メモリ（転送が必要） | TPU 専用メモリ（転送が必要） |
| Python から | Python・NumPy・PyTorch・JAX | PyTorch（CUDA）・JAX | JAX（・TensorFlow） |

**GPU・TPU は「速い CPU」ではありません**（参考 Notebook の README の言葉）。得意な計算の種類が違う装置です。CUDA は NVIDIA GPU 用の仕組みで、TPU ランタイムでは使いません。

## 3. Python の for ループ

`cpu_basics.py` は Python 標準ライブラリだけで、次の 4 つの計算を list と for ループで書いています。

| Task | 計算 | 関数 | 計算量 |
| --- | --- | --- | --- |
| A | $y_i = a_i b_i + c_i$ | `elementwise` | $O(n)$ |
| B | $s = \sum_i a_i$ | `total` | $O(n)$ |
| C | $C_{ij} = \sum_k A_{ik} B_{kj}$（3 重ループ） | `matmul` | $O(n^3)$（$n \times n$） |
| D | $x_i > 0$ なら $x_i^2$、それ以外は 0 | `conditional_square` | $O(n)$ |

Python の for ループが遅い主な理由：

- **インタプリタ**：1 要素ごとに「値の型を調べる → 対応する計算を選ぶ → 結果の新しいオブジェクトを作る」を実行する。
- **list のデータ構造**：要素は別々の Python オブジェクト（float 1 個で 24 バイト）で、list はそれへの参照を持つ。メモリ上でばらばらに置かれる。

## 4. NumPy のベクトル演算

`numpy_benchmark.py` は同じ計算を NumPy で書いています（`a * b + c`、`np.sum`、`A @ B`、`np.where`）。

- 同じ型（dtype）の値が**連続したメモリ**に並ぶ（float64 は 1 個 8 バイト）。
- ループは C 言語の中で回り、**SIMD 命令**（1 命令で複数の値を計算）を使える。行列積は最適化された **BLAS** ライブラリが複数のコアを使って計算する。

**NumPy が必ず速いとは限りません。**

- 要素数が少ないと、関数呼び出しの固定コストの方が大きい（この教材の測定でも、$n = 100$ の総和では Python ループの方が速いことがある）。
- list → 配列の変換にも時間がかかる（この教材では「データ生成」として計算時間と分けて測る）。
- `np.where(x > 0, x * x, 0)` は**両方の分岐**を全要素について計算する。
- 前の結果を使って次を計算する**逐次的な処理**はベクトル化しにくい。

## 5. GPU による並列計算

- GPU は、同じ命令を多数のデータに同時に実行する（**データ並列**）。行列積の $n^3$ 回の乗算・加算はほぼ独立なので、非常に並列化しやすい。
- GPU で計算するには、データを CPU のメモリから GPU のメモリへ**転送**し、結果を戻す必要がある。
- GPU への命令（カーネル）の起動には固定コストがあるので、**小さな計算では CPU の方が速い**ことが多い。
- PyTorch の GPU 演算は**非同期**に実行される（10 章）。

## 6. TPU と JAX

- TPU は Google が設計した、行列積専用の回路を持つ装置です。
- **JAX** は NumPy とほぼ同じ書き方（`jax.numpy`）で、**同じ関数を CPU・GPU・TPU のどれでも実行**できます。これを使うと、ライブラリの違いを除いた「デバイスの違い」を比べやすくなります（Notebook 03）。
- `jax.jit` は関数を **XLA コンパイラ**でコンパイルします。1 回目の呼び出しはコンパイルを含むので遅く、2 回目以降は同じ shape・dtype ならコンパイル済みのものを使います。
- `jax.devices()` で使えるデバイスを調べ、`jax.device_put(x, device)` でデータを送り、`result.block_until_ready()` で計算の終了を待ちます。
- 参考 Notebook は TPU を TensorFlow（`TPUStrategy`）で使っていました。この教材は JAX を中心にし、TensorFlow の方法は Notebook 03 の任意セル（既定では実行しない、未検証）として残しています。

## 7. アルゴリズムと計算量

| 計算量 | 例（この教材） | $n$ が 10 倍になると |
| --- | --- | --- |
| $O(1)$ | 配列の添字アクセス | 変わらない |
| $O(\log n)$ | 二分探索 | 少し増える（$\log_2$ が約 3.3 増える） |
| $O(n)$ | 線形探索、総和、要素ごとの演算 | 10 倍 |
| $O(n \log n)$ | マージソート、`sorted()`、`np.sort()` | 10 倍強 |
| $O(n^2)$ | バブルソート、挿入ソート（平均・最悪） | 100 倍 |
| $O(n^3)$ | $n \times n$ の行列積（素朴な方法） | 1,000 倍 |

## 8. 実測時間と理論計算量

$$ \text{実行時間} \approx (\text{定数}) \times f(n) + (\text{固定コスト}) $$

- **理論計算量** $f(n)$ は、$n$ が大きくなったときの**増え方**を表す。
- **定数**は、実装（Python か C 言語か）、データ構造（list か配列か）、ハードウェア（CPU・GPU・TPU、キャッシュ、メモリ帯域）で決まる。
- **固定コスト**は、関数呼び出し、GPU のカーネル起動、データ転送、コンパイルなど。小さな $n$ では固定コストが支配的になる。
- 実測時間を $f(n)$ で割った値が $n$ によらずほぼ一定なら、理論どおりに増えている（`algorithm_benchmark.complexity_table`）。
- **ベクトル化・GPU は定数を小さくする（あるいは並列に処理する）が、$f(n)$ は変えない。** アルゴリズムを変える（$O(n^2)$ → $O(n \log n)$）と $f(n)$ が変わる。

## 9. データ転送・コンパイル・同期

| 用語 | 内容 | この教材での扱い |
| --- | --- | --- |
| **データ生成** | 乱数の list・配列を作る時間 | 計算時間に含めず、`data_gen_s` に別に記録 |
| **データ転送** | CPU のメモリ ⇔ GPU・TPU のメモリ | `to_device_s`・`transfer_s`、`to_host_s`・`fetch_s` として別に記録 |
| **コンパイル** | JAX の `jit`（XLA）が関数を機械語に変換する | 初回（コンパイル込み）`first_call_s` と、コンパイルだけ `compile_s` を記録 |
| **同期** | GPU・TPU は非同期に実行されるので、終わるまで待つ | PyTorch：`torch.cuda.synchronize()`、JAX：`block_until_ready()`。`benchmark_utils.measure` の `sync` 引数 |
| **ウォームアップ** | 最初の数回を捨てる（初期化・キャッシュの影響） | `measure` の `warmup` 引数 |

同期せずに測ると「命令を出した時間」しか測れず、GPU が実際より速く見えます。

## 10. 教科書との関連

教科書：柴田望洋『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』

### 実際に使用したコード（`textbook/`、改変せずにコピー）

| ファイル | 原本 | 関数 | 用途 | SHA-256（原本と一致） |
| --- | --- | --- | --- | --- |
| `textbook/ssearch_while.py` | `chap03/ssearch_while.py` | `seq_search` | 線形探索 $O(n)$（`algorithm_benchmark.linear_search`） | `6a11e6b6…806ea` |
| `textbook/bsearch.py` | `chap03/bsearch.py` | `bin_search` | 二分探索 $O(\log n)$（`algorithm_benchmark.binary_search`） | `2fdf0171…f93674` |
| `textbook/bubble_sort1.py` | `chap06/bubble_sort1.py` | `bubble_sort` | バブルソート $O(n^2)$ | `e7908e4f…f35c1` |
| `textbook/insertion_sort.py` | `chap06/insertion_sort.py` | `insertion_sort` | 挿入ソート $O(n^2)$（最良 $O(n)$） | `b90b8e07…d69e` |
| `textbook/merge_sort.py` | `chap06/merge_sort.py` | `merge_sort` | マージソート $O(n \log n)$（Python で書いた $O(n \log n)$ の例） | `5b735282…ac843` |

完全な SHA-256 は `sha256sum textbook/*.py` で確認できます（作成時に原本と一致することを確認済み。改行コードも原本どおり CRLF）。**編集しないでください。**

- どれも `from textbook.bsearch import bin_search` のように**直接 import** しています。原本の対話入力（`input()`）は `if __name__ == '__main__':` の中にあるので、import しても入力待ちになりません。
- Adapter やラッパークラスは作っていません。ただし次の 2 点だけ、`algorithm_benchmark.py` 側で小さな関数を用意しています。
  - `binary_search`：教科書の `bin_search` は**空のシーケンスで `IndexError`** になる（`pr = -1` のとき `a[-1]` を参照する）ため、空の場合だけ先に -1 を返してから `bin_search` を呼ぶ。
  - 教科書のソートは入力を**その場で**並べ替えるので、ベンチマークで同じ入力を繰り返し使えるように、コピーしてから呼ぶ（`SORTS`）。

### 参考にしただけのコード（コピーしていません）

| ファイル | 内容 | 使わなかった理由 |
| --- | --- | --- |
| `chap06/selection_sort.py` | 単純選択ソート $O(n^2)$ | $O(n^2)$ の例はバブル・挿入の 2 つで十分。学生の追加課題（Research D）にできる |
| `chap06/bubble_sort2.py`・`bubble_sort3.py` | 交換がなければ打ち切る改良版 | 最良の場合の違いを調べる追加課題にできる |
| `chap03/ssearch_for.py`・`ssearch_sentinel.py` | for 文・番兵法の線形探索 | 線形探索は while 版 1 つで十分 |
| `chap06/quick_sort1.py`、`heap_sort.py` など | $O(n \log n)$ のソート | $O(n \log n)$ の例はマージソートを使った |

### 教科書の内容との対応

1. **線形探索と二分探索の計算量**：線形探索（第3章）は先頭から順に調べるので最悪 $n$ 回の比較、$O(n)$。二分探索は範囲を半分ずつに絞るので最悪 $\lfloor \log_2 n \rfloor + 1$ 回、$O(\log n)$。ただし**ソート済み**が前提で、ソートには $O(n \log n)$ かかる。
2. **$O(n)$ と $O(\log n)$ の違い**：$n$ = 1,000,000 で、線形探索は最悪 1,000,000 回、二分探索は約 20 回の比較。Notebook 04 で実測します。
3. **$O(n^2)$ のソートと $O(n \log n)$ のソート**：バブル・挿入（第6章）は $O(n^2)$、マージソートは $O(n \log n)$。$n$ = 3,000 で、比較回数の目安は約 900 万と約 3.5 万。
4. **Python ループと NumPy のベクトル演算**：教科書のアルゴリズムは list と for / while ループで書かれている。同じ計算を NumPy で書くと、オーダーは同じでも定数倍が何十〜何百倍も変わる（Notebook 01）。探索・ソートは逐次的で単純にはベクトル化できないが、`np.sort`・`np.searchsorted` のように C 言語で実装された関数を使うことはできる。
5. **アルゴリズム改善と実装高速化の違い**：$O(n^2)$ → $O(n \log n)$（アルゴリズム改善）は $n$ が大きいほど差が広がる。Python → C 言語・NumPy・GPU（実装高速化）は定数倍の改善。Notebook 04 では、Python で書いたマージソートが、C 言語の `sorted()` より何十倍も遅いこと、それでも大きな $n$ では Python のバブルソートよりずっと速いことを確かめられる。

## 11. 参考リポジトリとの関係

参考：`ai-programming-2026-team-project-1-starter` の `A_cpu_gpu_tpu/A_cpu_gpu_tpu_benchmark/`（MIT License, Copyright (c) 2026 Daigo Takeuchi。リポジトリ直下の `LICENSE`）

> 作業指示にあったパス `.../ai-programming-2026-team-project-1-starter/A_cpu_gpu_tpu_benchmark/` は存在せず、実際には `.../A_cpu_gpu_tpu/A_cpu_gpu_tpu_benchmark/` にありました。

### 参考リポジトリの内容

| ファイル | 内容 |
| --- | --- |
| `README.md` | 課題概要、学習目標、「GPU/TPU は速い CPU ではない」、Colab のランタイム切替、TODO・Challenge |
| `starter.ipynb` | ① PyTorch・TensorFlow のバージョンと CUDA・TPU の検出、② for ループの総和（$N$ = 2,000,000）、③ `np.arange(N).sum()`、④ NumPy の行列積（SIZE = 1024）、⑤ PyTorch CUDA の行列積（`torch.cuda.synchronize()` で同期）、⑥ TensorFlow `TPUStrategy` の行列積、⑦ 結果の棒グラフ（使えない値は `np.nan`）、⑧ 分析 TODO |
| `.py`・requirements・データ・テスト | **なし**（この A ディレクトリには README と Notebook だけ）。JAX は使っていない。ウォームアップ・複数回測定・メモリ測定はしていない |

### 再利用の方針

| 分類 | 内容 | E2 での利用先 |
| --- | --- | --- |
| **そのまま再利用**（考え方） | 「GPU/TPU は速い CPU ではない」「CUDA は NVIDIA GPU 用で TPU では使わない」という説明、Colab ランタイム切替の流れ、`torch.cuda.is_available()` による GPU の検出、`torch.cuda.synchronize()` での同期 | README 2 章・Notebook 02・`notebooks/README.md` |
| **改変して再利用** | for ループの総和 vs `np.sum`（データ生成を計算時間から外し、ウォームアップ＋複数回測定の中央値に、$N$ を 1,000,000 に） | Notebook 01 の 5-3 |
| | NumPy と PyTorch CUDA の行列積（SIZE = 1024 を含む複数サイズ、転送・初回・計算本体・取り出しを分離、結果の一致を確認） | Notebook 02 |
| | TensorFlow の TPU 行列積（任意セル、ウォームアップ後に複数回測定、既定では実行しない） | Notebook 03 の参考セル |
| | 棒グラフ（使えないデバイスを `np.nan` で残すのではなく、**測定できたものだけ**を描く） | Notebook 02・03 |
| | 分析 TODO・Challenge（サイズを変える、GPU が有利になる条件、ウォームアップ後だけで比較） | 各 Notebook の TODO、Advanced Research |
| **簡略化** | 環境チェックを 1 つの関数（`show_environment`）にまとめた | Notebook 01〜03・05 |
| **今回は使用しない** | TensorFlow を必須の依存にすること（JAX を中心にしたため）、`!pip install torch tensorflow`（Colab の標準パッケージを使う） | ― |

参考リポジトリのファイルは変更していません。コードを大量にコピーせず、E2 の計測方法（`benchmark_utils.measure`）に合わせて書き直しました。

## 12. ファイル構成

```text
e2-computing-performance/
├── README.md                 この説明
├── .gitignore
├── requirements.txt          依存ライブラリ（NumPy・Matplotlib。PyTorch・JAX は任意で、入れ方の注意つき）
├── starter.py                一連のデモ（Python ループ → NumPy → 探索 → ソート → PyTorch があれば行列積）
├── cpu_basics.py             Task A〜D の Python ループ版（標準ライブラリのみ）、データ生成、演算回数
├── numpy_benchmark.py        Task A〜D の NumPy 版、Python との比較（結果の一致・時間・speedup・安全上限）
├── algorithm_benchmark.py    教科書の探索・ソート、sorted・np.sort、計算量の比較
├── benchmark_utils.py        計測（warmup・repeats・中央値・平均・標準偏差・sync）、表の整形、CSV 保存
├── notebooks/
│   ├── README.md             Notebook の使い方、Colab、ランタイム、トラブルシューティング
│   ├── 01_python_vs_numpy.ipynb
│   ├── 02_cpu_vs_gpu.ipynb
│   ├── 03_cpu_gpu_tpu.ipynb
│   ├── 04_algorithms_and_complexity.ipynb
│   └── 05_research_experiments.ipynb
├── textbook/                 教科書のサンプルコード（編集しない）
│   ├── __init__.py
│   ├── ssearch_while.py
│   ├── bsearch.py
│   ├── bubble_sort1.py
│   ├── insertion_sort.py
│   └── merge_sort.py
└── tests/
    ├── test_cpu_basics.py
    ├── test_numpy_benchmark.py
    └── test_algorithm_benchmark.py
```

## 13. ローカル実行方法

このディレクトリ（`e2-computing-performance/`）で実行してください。

```bash
pip install -r requirements.txt          # NumPy・Matplotlib（入っていなければ）
python3 starter.py                       # 一連のデモ（数秒）
python3 -m unittest discover -s tests -v # テスト
python3 numpy_benchmark.py               # Python ループ vs NumPy の表
python3 algorithm_benchmark.py           # 探索・ソートと計算量の表
```

- `cpu_basics.py` と `benchmark_utils.py` は標準ライブラリだけで動きます。それ以外は NumPy が必要です。
- PyTorch がインストールされていれば、`starter.py` は CPU（と GPU があれば GPU）の行列積も測ります。なければスキップします。
- Notebook をローカルで開く方法は `notebooks/README.md` を参照してください。

`starter.py` の出力の例（作成時の WSL2・Intel Core i5-1240P での 1 回の測定。時間は環境・実行ごとに変わります）：

```text
=== 2. Python ループ vs NumPy（numpy_benchmark.py、float64、seed = 0）===
       task        n   Python    NumPy  speedup  match
elementwise      100  4.25 µs  1.32 µs     3.23   True
elementwise  100,000  6.03 ms   367 µs     16.4   True
      total      100  1.52 µs  1.87 µs    0.814   True   ← 小さい n では NumPy の方が遅い
      total  100,000   1.3 ms  24.7 µs     52.5   True
     matmul      100  37.5 ms  36.1 µs    1,040   True
```

## 14. Google Colab 実行方法

Colab からは、自分の PC（WSL）のファイルを直接読めません。各 Notebook の最初の「実験環境」セルが、次のどちらかで E2 のフォルダを見つけて作業ディレクトリにします。詳しくは `notebooks/README.md` を参照してください。

### 方法A：GitHub から clone

チームの E2 リポジトリを GitHub に用意し、Notebook の `REPO_URL` に**自分たちのリポジトリの URL** を入れて実行します（この教材には URL を書いていません）。**教科書コード（`textbook/`）は公開リポジトリに含めないでください。** `textbook/` がないと Notebook 04 と 05 の一部が動かないので、その場合は方法B を使ってください。

### 方法B：ZIP アップロード

E2 フォルダを ZIP にして Colab の `/content` にアップロードし、「実験環境」セルを実行します。ZIP を展開し、`cpu_basics.py` のあるフォルダを作業ディレクトリにして、既存の `.py` を import できるようにします。

### ランタイム（CPU・GPU・TPU）の切り替え

Colab のメニューから「ランタイムのタイプ」を変更する設定を開き、ハードウェア アクセラレータとして「なし（CPU）」「GPU」「TPU」のいずれかを選びます。ランタイムが再起動されるので、Notebook を最初から実行し直します。画面の表記は変わることがあるので、**各 Notebook の環境表示**（`CUDA GPU`、`JAX devices`、`TPU`）で実際のデバイスを確認してください。GPU・TPU は無料プランでは使えないことがあります。

## 15. Core Research

すべてのチームが取り組む課題です。**GPU が使えなくても、CPU だけで完了できます。**

| # | 課題 | 使うもの |
| --- | --- | --- |
| 1 | Python の for ループを実行する | `cpu_basics.py`、Notebook 01 |
| 2 | NumPy のベクトル演算を実行する | `numpy_benchmark.py`、Notebook 01 |
| 3 | 同じ計算の結果が一致することを検証する（`np.allclose`） | `numpy_benchmark.results_match`、Notebook 01 |
| 4 | 実行時間を比較する（中央値、speedup） | `benchmark_utils.measure`、Notebook 01 |
| 5 | データサイズを変更する（100 〜 1,000,000） | Notebook 01 |
| 6 | CPU 上の NumPy と PyTorch を比較する | Notebook 02（CPU ランタイムで可） |
| 7 | GPU が利用可能なら GPU 演算を実行する（使えなければ「使えなかった」と記録） | Notebook 02（GPU ランタイム） |
| 8 | 行列積の性能を測定する | Notebook 01・02 |
| 9 | 探索・ソートの理論計算量を調べる | `algorithm_benchmark.py`、Notebook 04 |
| 10 | 結果を表・グラフにまとめる | 各 Notebook、`save_csv` |
| 11 | 理論計算量と実測結果を考察する | Notebook 04、`complexity_table` |

研究テンプレート：Notebook 05 の Research A（Python と NumPy）・B（CPU と GPU）・D（アルゴリズムと計算量）。

## 16. Advanced Research

Core Research を終えたチームが取り組む課題です。**Advanced A〜E のうち 1 つ以上を選択**してください。

### Advanced A：TPU と JAX

- Notebook 03 を CPU・GPU・TPU の各ランタイムで実行し、**同じ JAX 関数**で比較する（Research C）。
- 初回コンパイル時間、JIT の効果、shape を変えたときの再コンパイルを調べる。
- TPU の行列積精度（`jax_default_matmul_precision`）や bfloat16 の影響を調べる。
- （任意）参考 Notebook の TensorFlow `TPUStrategy` の方法と比べる（未検証のセル）。

### Advanced B：大規模行列積

- 行列サイズを安全上限の範囲で大きくし、CPU（NumPy・PyTorch）と GPU・TPU で FLOPS（1 秒あたりの演算回数 $2n^3 / t$）を計算する。
- どのサイズから GPU・TPU が有利になるか、どこで頭打ちになるかを調べる。
- メモリ不足にならないよう、メモリ使用量を見積もってから実行する（$n \times n$ の float32 は $4n^2$ バイト）。

### Advanced C：アルゴリズムの並列化可能性

- 要素ごとの演算（完全に独立）、総和（木構造で並列化できる reduction）、行列積（独立な積和が多い）、二分探索（各ステップが前のステップに依存）、挿入ソート（逐次的）を比べる。
- 「並列にできる部分」と「逐次的な依存関係」を、データの依存関係の図で説明する。
- 並列ソート（例：バイトニックソート、`torch.sort`・`jnp.sort`）を調べ、GPU で計算量や実行時間がどうなるかを考察する。

### Advanced D：メモリ帯域とデータ転送

- 要素ごとの演算の時間から見かけのメモリ帯域（GB/s）を求め、配列サイズ（CPU のキャッシュに入る／入らない）で変わるかを調べる（Research E）。
- CPU → GPU の転送帯域を測り、転送込みでも GPU が有利になる条件を求める。
- dtype（float64・float32・float16）とメモリ使用量・時間の関係を調べる。

### Advanced E：CPU・GPU・TPU の公平な比較

- 同じ計算・同じ dtype・同じ精度設定・同じデータで比べる。
- 何を測るか（計算本体だけか、転送・コンパイル込みか）を明確にし、それぞれで比較する。
- ライブラリの差（NumPy・PyTorch・JAX）とデバイスの差を切り分ける。
- 使えなかったデバイス・測っていない指標（消費電力など）を明記する。**実測していない値で結論を出さない。**

## 17. 実験条件と評価指標

### 記録すべき実験条件

- 実行環境：ランタイム（ローカル／Colab の CPU・GPU・TPU）、CPU・GPU・TPU の名前、Python・NumPy・PyTorch・JAX のバージョン（各 Notebook の環境表示）
- 問題サイズ（$n$、行列サイズ、バッチサイズ）
- dtype（float64・float32 など）
- 乱数シード
- 反復回数（`repeats`）とウォームアップ回数（`warmup`）、代表値（中央値）
- 入力データの性質（ランダム・ソート済みなど）

### 評価指標

| 指標 | 内容 |
| --- | --- |
| 実行時間 | `time.perf_counter()` で測り、ウォームアップ後の**中央値**。平均・標準偏差も記録（`measure`） |
| 高速化率 | $\text{Speedup} = t_\text{Python} / t_\text{NumPy}$ など（同じ計算どうし） |
| 結果の正しさ | `np.allclose`（dtype に応じた許容誤差）、探索・ソートは期待値との一致 |
| 時間 / $f(n)$ | 理論計算量どおりかを確かめる（`complexity_table`） |
| 転送・コンパイル・取り出し | 計算本体と分けて記録 |
| メモリ使用量 | `arr.nbytes`、`sys.getsizeof`（Research A・E） |

### 計測の注意

- データ生成時間と計算時間を分ける（`data_gen_s`、`measure` の `setup`）。
- 小さな処理（数 µs 以下）は計測誤差が大きい。反復回数を増やすか、まとめて実行して 1 回あたりに直す。
- Python ループには**安全上限**があります（`numpy_benchmark.PYTHON_MAX_N`、`algorithm_benchmark.QUADRATIC_MAX_N`）。上限を超える条件は実行せず、表では `-` になります。

## 18. GitHub を用いたチーム開発

チームで GitHub を使って研究を進めてください（公開設定については冒頭の注意を参照）。

- **役割分担を明確にする**：例）Python・NumPy 担当、GPU 担当、TPU・JAX 担当、アルゴリズム担当、測定・グラフ担当、README・考察担当
- **GitHub Issues でタスク管理**：実装・実験・調査・不具合を Issue に登録し、担当者を割り当てる
- **branch を分けて実装**：例）`feature/dtype-experiment`、`experiment/gpu-batch-size`、`experiment/sort-input-order`
- **Pull Request でコードレビュー**：テスト（`python3 -m unittest discover -s tests -v`）が通ることを確認してから merge する
- **結果の管理**：測定した CSV・グラフと、実行環境の情報をセットで残す（`notebooks/results/` は `.gitignore` に入っているので、提出用のものを選んで追加する）
- **最終成果物の Release**：研究が完成したら Release（例：`v1.0`）を作る

## 19. 成果物と提出方法

1. **コード**：追加した実験・関数（テストが通ること）、実行した Notebook（不要な出力は消す）
2. **実験結果**：表・グラフ（実験条件と実行環境を併記）
3. **報告**（README への追記、または別の報告ファイル）
   - Core Research 1〜11 の結果と考察
   - 選択した Advanced Research のテーマ、方法、結果、考察
   - RQ1〜RQ4 に対するチームとしての答え
   - 「理論計算量が同じでも実行時間が違う例」と「実装を速くしてもオーダーは変わらない例」
   - 使えなかったデバイス・未検証の項目
   - 参考にした文献・Web ページの出典
4. **GitHub の記録**：Issue、branch、Pull Request、Release

提出方法（期限・提出先）は、授業で指示します。

## 20. 参考文献・著作権上の注意

### 教科書コード

- 出典：柴田望洋 著『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』SBクリエイティブ　第3章「探索」、第6章「ソート」
- 使用ファイル：`textbook/ssearch_while.py`（原本 `chap03/ssearch_while.py`）、`textbook/bsearch.py`（原本 `chap03/bsearch.py`）、`textbook/bubble_sort1.py`（原本 `chap06/bubble_sort1.py`）、`textbook/insertion_sort.py`（原本 `chap06/insertion_sort.py`）、`textbook/merge_sort.py`（原本 `chap06/merge_sort.py`）
- 参考にしただけのファイル：10 章の表を参照（このリポジトリにはコピーしていません）
- 教科書コードは第三者の著作物です。公開再配布の許諾はまだ確認していません。**GitHub で公開・配布する前に、再配布条件を必ず確認してください。**

### 参考リポジトリ

- `ai-programming-2026-team-project-1-starter/A_cpu_gpu_tpu/A_cpu_gpu_tpu_benchmark/`（`README.md`、`starter.ipynb`）。MIT License, Copyright (c) 2026 Daigo Takeuchi。再利用の範囲は 11 章を参照（考え方と構成を参考にし、E2 向けに書き直した。コードの大量コピーはしていない）。

### ライブラリ・ドキュメント

- NumPy <https://numpy.org/doc/>
- PyTorch：CUDA semantics（非同期実行と同期）<https://pytorch.org/docs/stable/notes/cuda.html>
- JAX：Asynchronous dispatch、Just-in-time compilation、`jax.devices` <https://docs.jax.dev/>
- Python 標準ライブラリ `time`（`perf_counter`）、`statistics`、`random`、`csv`、`unittest` のドキュメント

研究で他の文献や Web ページを使った場合は、出典と参照日を記録してください。

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
| `chap03/bsearch.py` | `e2-computing-performance/textbook/bsearch.py` | `algorithm_benchmark.py` |
| `chap06/bubble_sort1.py` | `e2-computing-performance/textbook/bubble_sort1.py` | `algorithm_benchmark.py` |
| `chap06/insertion_sort.py` | `e2-computing-performance/textbook/insertion_sort.py` | `algorithm_benchmark.py` |
| `chap06/merge_sort.py` | `e2-computing-performance/textbook/merge_sort.py` | `algorithm_benchmark.py` |
| `chap03/ssearch_while.py` | `e2-computing-performance/textbook/ssearch_while.py` | `algorithm_benchmark.py` |

### 3. 配置後のディレクトリ構成

```text
e2-computing-performance/
└── textbook/
    ├── __init__.py          （リポジトリに含まれる）
    ├── bsearch.py           （各自で配置）
    ├── bubble_sort1.py      （各自で配置）
    ├── insertion_sort.py    （各自で配置）
    ├── merge_sort.py        （各自で配置）
    └── ssearch_while.py     （各自で配置）
```

### 4. コピーと確認のコマンド例

```bash
cd e2-computing-performance
SRC="<展開したフォルダ>"        # 各自の環境に合わせる

cp -i "$SRC/chap03/bsearch.py" textbook/bsearch.py
cp -i "$SRC/chap06/bubble_sort1.py" textbook/bubble_sort1.py
cp -i "$SRC/chap06/insertion_sort.py" textbook/insertion_sort.py
cp -i "$SRC/chap06/merge_sort.py" textbook/merge_sort.py
cp -i "$SRC/chap03/ssearch_while.py" textbook/ssearch_while.py

# 原本とコピーの SHA-256 が一致することを確認する
sha256sum "$SRC/chap03/bsearch.py" textbook/bsearch.py
sha256sum "$SRC/chap06/bubble_sort1.py" textbook/bubble_sort1.py
sha256sum "$SRC/chap06/insertion_sort.py" textbook/insertion_sort.py
sha256sum "$SRC/chap06/merge_sort.py" textbook/merge_sort.py
sha256sum "$SRC/chap03/ssearch_while.py" textbook/ssearch_while.py

python3 starter.py                          # 実行確認
python3 -m unittest discover -s tests -v    # テスト
```

配置した教科書のコードは、リポジトリ直下の `.gitignore` によって Git の追跡対象から除外されます（`git status` に表示されなければ正常です）。
`git add -f` などで教科書のコードを commit・push しないでください。
