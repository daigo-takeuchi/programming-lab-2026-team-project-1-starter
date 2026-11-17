# E3：神経回路モデリング — ANN・SNN 比較と Spiking Manifesto の実装

> ⚠️ **公開前の注意**
> `textbook/` 内のコードは第三者の著作物です（出典は「20. 参考文献・著作権上の注意」参照）。
> 再配布の可否はまだ確認できていないため、このディレクトリは**ローカルの教材用**です。
> GitHub などで公開・配布する前に、必ず出版社の再配布条件を確認してください。

> 📄 この教材は、E. Izhikevich「Spiking Manifesto」（arXiv:2512.11843）の中心的なアイデアを、
> **教育用に小さく簡略化して** Python で実装したものです。**論文のモデル・著者の実装そのものではありません。**
> 論文と同じ点・違う点は「17. 論文との対応関係」にまとめています。

---

## 1. 研究テーマと目的

**E3：神経回路モデリング — ANN・SNN 比較と Spiking Manifesto**

従来型の人工ニューラルネットワーク（ANN）と、スパイキングニューラルネットワーク（SNN）の簡易モデルを実装し、情報表現・演算量・計算時間・メモリ使用量を比較します。

> **最終的な学習目標**：ANN の**重み付き和**による計算と、Spiking Manifesto が提案する**スパイクの相対的な発火時刻・順序に基づく Look-Up Table（LUT）演算**の違いを、実際のコードで説明できるようになること。

| | 問い |
| --- | --- |
| RQ1 | **ANN と SNN では情報表現がどう異なるか**：連続値の activation vector、LIF の膜電位と離散的なスパイク、各ニューロンの発火時刻（spike timing）、ニューロン間の発火順序（spike order） |
| RQ2 | **Spiking Manifesto の LUT はどのように動作するか**：anchor pair の選択 → latency の比較 → ビット列 → 整数 index → LUT の行の選択 → 出力 latency vector |
| RQ3 | **ANN と LUT 方式では計算コストがどう異なるか**：乗算・加算・比較・LUT 参照の回数、実行時間、パラメータ数、メモリ使用量 |
| RQ4 | **spike timing はどの程度の情報を表現できるか**：発火率表現と発火順序表現、n!、部分的な pairwise comparison による区別、LUT の行数と表現できる index の数 |

- **Core Research（必須課題）**：Python 標準ライブラリだけで、小さな ANN・LIF・LUT を動かし、演算構造とコストを比較する
- **Advanced Research（発展課題）**：表現容量、polychronization、学習可能な LUT、公開コードとの照合、公平な性能比較

このリポジトリには、各モデルの**最小限の forward 計算**とデモ・テストだけを用意しています。**LUT の学習（surrogate gradient・誤差逆伝播）、大規模な SNN、Transformer は含みません。**

## 2. ANN とは何か

ANN（Artificial Neural Network）の基本単位は、**入力の重み付き和に活性化関数をかけたもの**です（`ann.py`）。

```text
y = ReLU(Wx + b)
```

| 記号 | 意味 | サンプル（`data/sample_patterns.json`） |
| --- | --- | --- |
| x | 入力ベクトル（長さ n） | `[0.2, 0.5, 0.8]` |
| W | 重み行列（m 行 n 列） | `[[0.5, -0.2, 0.1], [-0.3, 0.8, -0.6]]` |
| b | バイアス（長さ m） | `[0.1, 0.05]` |
| ReLU | 活性化関数 max(0, v) | |
| y | 出力ベクトル（長さ m、連続値の activation） | `[0.18, 0.0]` |

`weighted_sum` は、出力1つごとに「バイアスから始めて、W[i][j] × x[j] を n 回足す」ので、**乗算 n 回・加算 n 回**です。出力が m 個あるので、全結合層1層の積和演算は **m × n 回 = O(nm)** です。パラメータ数は W の nm 個と b の m 個で **nm + m 個**で、forward のたびに**すべて**読み出します。

## 3. SNN とは何か

脳の神経細胞（ニューロン）は、連続値を出力し続けるのではなく、膜電位が閾値を超えたときに**スパイク（活動電位）**という短いパルスを出します。スパイクは「出たか・出ないか」の**全か無か**の信号です。SNN（Spiking Neural Network）は、このスパイクで情報をやりとりするモデルです。

スパイクで情報を表す方法には、主に次のものがあります。

| 表現 | 情報を持つもの | 例 |
| --- | --- | --- |
| 発火率（rate）表現 | 一定時間内のスパイクの**数** | 強い刺激ほど多く発火する |
| 発火時刻（timing）表現 | スパイクが**いつ**出たか（latency） | 強い刺激ほど**早く**発火する |
| 発火順序（order）表現 | どのニューロンが**どの順に**発火したか | Neuron 1 → Neuron 3 → Neuron 0 → … |

Spiking Manifesto は、**発火時刻・発火順序**の表現に注目しています（5章、6章）。

## 4. LIF ニューロン

`lif_snn.py` は、最も基本的なスパイキングニューロンのモデルである **LIF（Leaky Integrate-and-Fire）** を、離散時間（オイラー法）で実装しています。

```text
V[t+1] = V[t] + dt/tau * ( -(V[t] - V_rest) + R * I[t] )
V[t+1] >= V_th なら スパイクを出し、V[t+1] = V_reset にリセット
```

- **Leaky（漏れ）**：入力がないと、膜電位 V は静止電位 V_rest に戻っていく
- **Integrate（積分）**：入力電流 I を少しずつためる
- **Fire（発火）**：閾値 V_th に達したらスパイクを出し、リセットする

`simulate_lif` は、各ステップの**時刻・膜電位・入力電流・スパイクの有無**と、**スパイク時刻・スパイク数**を記録します。既定値（dt = 1, tau = 10, R = 1, V_th = 1）で一定の入力 I = 1.5 を与えると、t = 11, 22, 33, 44 に発火します。

R × I が閾値以下（I ≤ 1.0）だと、V は R × I に近づくだけで発火しません。入力が強いほど**最初のスパイクが早く**なります（`latency_encode([1.2, 1.5, 2.0, 3.0])` → `[18.0, 11.0, 7.0, 4.0]`）。これは「入力の強さ → 発火時刻（latency）」への変換の一例です。論文の Appendix VIII-E でも、皮質の錐体細胞が入力の強さを latency で表すことが紹介されています。

> ⚠️ **LIF は Spiking Manifesto のモデルそのものではありません。**
> LIF は「ニューロンがどう発火するか」を理解するための**導入モデル**です。
> 論文 Section II のモデルは、膜電位を時間ステップごとにシミュレーションせず、**latency vector から次の latency vector への変換を LUT で表します**（6章）。論文の Fig. 5 の説明にも、各スパイクパターンの中には時間の変数がない、とあります。

## 5. Spike timing と Spike order

`spike_encoding.py` では、**各ニューロンが観測時間内に1回だけ発火する**場合を考えます。

```python
latencies = [0.3, 0.1, 0.4, 0.2]    # latencies[i] = ニューロン i の発火時刻
spike_order(latencies)               # [1, 3, 0, 2]
# Neuron 1 → Neuron 3 → Neuron 0 → Neuron 2
```

ニューロンの番号は Python に合わせて **0 始まり**です。`spike_order` は (発火時刻, 番号) の組を教科書の**単純挿入ソート**で並べています（11章）。

### 発火数では区別できないが、順序では区別できる例

```python
pattern_a = [0.1, 0.2, 0.3, 0.4]    # 発火数 [1, 1, 1, 1]、順序 0 → 1 → 2 → 3
pattern_b = [0.4, 0.3, 0.2, 0.1]    # 発火数 [1, 1, 1, 1]、順序 3 → 2 → 1 → 0
```

どちらも全ニューロンが観測時間内に1回ずつ発火するので、**発火数（発火率）はまったく同じ**です。発火率だけを見ると、この2つは区別できません。しかし**発火順序は逆**です。時間の情報を捨てると、この違いは失われます。

### 順列数 n!

n 個のニューロンが1回ずつ、同時発火なしで発火するとき、発火順序は **n! 通り**あります（`num_orders`、`math.factorial`）。

| n | 3 | 4 | 5 | 6 | 10 |
| --- | ---: | ---: | ---: | ---: | ---: |
| n! | 6 | 24 | 120 | 720 | 3,628,800 |

論文の Fig. 1(b) は、60個のニューロンが1回ずつ発火するとき 60! 通りのパターンがあり得る、という例を示しています。

> ⚠️ **n! は理論上の順列の数です。** 発火時刻にはノイズがあり、近い時刻に発火した2つのニューロンの順序は入れ替わりやすくなります。実際に**安定して識別・学習・利用できるパターンの数は n! より少ない**のが普通です。

### 同時発火の規則（この教材での定義）

- 発火順序：発火時刻が等しいニューロンは、**番号の小さい方を先**に並べる
- pairwise comparison：`latencies[a] > latencies[b]` が偽なので、ビットは **0**
- `quantize(latencies, resolution)` で時刻を丸めると、同時発火が増えることを確かめられます

## 6. Spiking Manifesto の中心的アイデア

E. Izhikevich「Spiking Manifesto」（arXiv:2512.11843、v2 を参照）の主張を、この教材に関係する範囲でまとめます（論文の内容は、論文 v2 の HTML 版と著者の公開コードで確認しました）。

- 現在の AI モデルは**行列の掛け算（重み付き和）**を基本にしている。論文は、脳はそれとは違う方法で計算していると主張し、**スパイクの相対的な発火時刻（タイミング）**を情報の単位として考える（Section I）。
- 各ニューロンが1回ずつ発火するパターンを **latency vector x**（各ニューロンの発火時刻のベクトル）で表し、ネットワークの計算を「**ある latency vector x から次の latency vector y への変換**」とみなす（Fig. 5）。
- その変換を、重み付き和ではなく **LUT（Look-Up Table）** で行う（Section II、Fig. 6、式 (1)〜(3)）。
  1. 各 LUT に、初期化のときに**ランダムに選んだ nc 組の anchor pair (a, b)** を割り当てる
  2. 各組について、2つのニューロンの latency の差 x[a] − x[b] が正かどうかを調べる（**pairwise comparison**）
  3. nc 個の比較結果（0/1）を並べたビット列を **index** にする（**式 (1)**）
  4. その LUT の **index 行目**（パラメータのベクトル）を選ぶ
  5. **nt 個の LUT で選ばれた行を足し合わせた**ものを出力 y とする（**式 (2)・(3)**）。論文では y は入力と同じ次元で、そのまま次の latency vector になる
- forward 計算には**行列の掛け算が要らない**。必要なのは比較と、選ばれた行の読み出し・加算だけ。
- 比較は「どちらが先に発火したか」だけを見るので、**近い latency vector は高い確率で同じ index になる**。論文 Section VI は、これを **locality-sensitive hashing（LSH）** として説明している。

この教材の `spike_lut.py` は、この **forward 計算（上の 1〜5）だけ**を実装しています。

## 7. Pairwise comparison

```python
anchor_pairs = [(0, 1), (1, 2), (2, 3)]
latencies = [0.3, 0.1, 0.4, 0.2]

compare_pairs(latencies, anchor_pairs)
# (0,1): 0.3 > 0.1 → 1
# (1,2): 0.1 > 0.4 → 0
# (2,3): 0.4 > 0.2 → 1
# → [1, 0, 1]
```

- `latencies[a] > latencies[b]` なら **1**、そうでなければ **0**（**等しい場合は 0**）
- latency が大きい＝**後に**発火したことを意味するので、ビット 1 は「a が b より後に発火した」ことを表します
- 論文の式 (1) も、差 u = x[a] − x[b] が正（u > 0）かどうかでビットを決めています。等しい場合の規則は論文に明記されていないため、この教材では上のように定義しました

## 8. Look-Up Table

### Binary index（論文の式 (1)）

比較結果のビット列を2進数として読み、整数 index にします（`bits_to_index`）。

```text
bits = [0, 1, 1]  →  binary 011  →  index 3
```

- この教材では**1つ目の比較を最上位ビット**にしています（論文 Fig. 6 の例と同じ読み方）。
- nc 回の比較では index は 0〜2^nc − 1 なので、各 LUT は **2^nc 行**です（nc = 3 なら 8 行）。
- 注意：著者の公開コード（`main.c`）は、1つ目の比較を**最下位ビット**にしています（`j |= 1 << r`）。ビットの並べ方を変えると**行の並び順が入れ替わるだけ**で、モデルの表現力は変わりません。ただし、論文の図・著者コード・この教材の数値を比べるときは、この違いに注意してください。

### 行の選択と出力（論文の式 (2)・(3)）

```python
lut = [            # 2^3 = 8 行、各行が出力ベクトル（m = 2）
    [0.1, 0.2],    # index 0
    [0.3, 0.1],    # index 1
    ...
    [0.4, 0.4],    # index 5  ← bits [1, 0, 1] で選ばれる
    ...
]
```

LUT が複数（nt 個）あるときは、**各 LUT が自分の anchor pair の集合で index を計算し**、選ばれた行を足し合わせます（`lut_forward`）。

```text
y[k] = Σ_i LUT_i[index_i][k]
```

`starter.py` では、nt = 3、nc = 3、m = 4 の LUT（`make_random_tables`、seed = 2025）で、`[0.3, 0.1, 0.4, 0.2]` を次の latency vector `[0.47, 0.90, 0.77, 0.64]` に変換する例を示しています。

- `select_row` は、範囲外の index（負の数を含む）や整数でない index を **IndexError** にします。Python のリストは `rows[-1]` でもエラーにならないため、明示的に確認しています。
- `lut_forward` は、入力の次元が LUT の入力次元と違うと **ValueError** にします。
- 行の値は本来**学習で決める**ものです。このリポジトリでは動作確認のため、手で決めた値（`data/sample_patterns.json`）か、乱数（seed 固定）を入れています。学習は Advanced C の課題です。

### 正確さに関する注意：行数 ≠ 区別できる発火順序の数

- n 個のニューロンの発火順序は n! 通りありますが、LUT は nc 回の比較しか見ないので、**区別できるのは高々 2^nc 通り**です。違う発火順序でも、anchor pair の比較結果が同じなら同じ行が選ばれます。
- 逆に、**2^nc 個の index がすべて実現できるとは限りません**。比較どうしが依存していると、到達できない index（使われない行）が生じます。
  - 例：`starter.py` の LUT 1 は、anchor pair に (2, 3) と (3, 2) の両方を持っています。同時発火でない限り、この2つのビットは必ず逆になるので、8 行のうち半分は使われません。
  - (0, 1)、(1, 2)、(0, 2) のように**推移律**でつながる組でも、到達できない組み合わせが生じます（どれが到達できないかは Experiment 4 の TODO で調べてください）。
- したがって、**LUT の行数**（保存容量）と、**実際に識別できる発火順序の数**は区別して考えてください。

## 9. ANN と LUT の演算構造

```text
ANN                                   Spiking Manifesto 型 LUT
x（連続値の activation）              x（latency vector）
   ↓ W[i][j] × x[j] を全部足す           ↓ x[a] > x[b] を nt × nc 回比べる
   ↓ + b                                 ↓ ビット列 → index（LUT ごと）
   ↓ ReLU                                ↓ 各 LUT の index 行目を読む
y = ReLU(Wx + b)                      y = Σ_i LUT_i[index_i]
```

| | ANN（入力 n、出力 m） | LUT（nt 個、各 nc 比較、出力 m） |
| --- | --- | --- |
| 乗算 | nm | **0** |
| 加算 | nm | nt × m |
| 比較 | m（ReLU） | nt × nc |
| LUT 参照 | 0 | nt |
| 保存するパラメータ | nm + m | **nt × 2^nc × m**（+ anchor の番号 2 × nt × nc 個） |
| 1回の forward で読む値 | nm + m（**全部**） | nt × m（**選ばれた行だけ**） |

`starter.py`（n = m = 4、nt = 3、nc = 3）では、ANN は乗算 16 回・保存 20 値、LUT は乗算 0 回・比較 9 回・参照 3 回・保存 96 値・読み出し 12 値です。

### 公平な比較について

- ANN と LUT は**計算の意味が違います**。出力次元が同じでも、同じ性能のモデルとはいえません。Core Research では、まず**演算構造と計算コストの違い**を調べます。分類精度などの性能比較は Advanced E の課題です。
- Python の for ループで書いた ANN と、Python のリストで書いた LUT の処理時間は、**実装方法に強く依存**します（NumPy を使えば ANN は大幅に速くなります）。
- **この教材の測定だけから、「SNN の方がハードウェア上で高速・低消費電力である」とは結論できません。** 消費電力はこの教材では測っていません。論文の効率に関する数値も、多くは理論的な見積もりや演算回数の比較であり、消費電力の実測ではありません（17章）。

## 10. 表現容量と計算量

### ANN

入力 n、出力 m の全結合層は、乗算・加算がそれぞれ nm 回で **O(nm)** です。

### LUT

LUT 数 nt、各 LUT の比較回数 nc、出力次元 m とすると、この実装の forward は

- 比較処理：**O(nt × nc)**
- LUT 行の読み出しと出力への加算：**O(nt × m)**

で、全体は概ね **O(nt × (nc + m))** です。

> これは**この実装を仮定した forward 計算の計算量**です。ANN と同じ機能・精度を達成するために必要なモデルの大きさ（nt、nc）を保証するものではありません。

### LUT の保存容量

各 LUT が 2^nc 行、各行が m 次元なので、nt 個の LUT に保存する値の数は

```text
nt × 2^nc × m
```

です。**nc が1増えるごとに保存容量は2倍**になります（指数関数的な増加）。nc = 6 なら 64 行、nc = 10 なら 1024 行、nc = 20 なら 約100万行です。

### 保存容量と、1回の forward で読み出す量

| | 保存している値の総数 | 1回の forward で読む値の数 |
| --- | --- | --- |
| ANN | nm + m | nm + m（全部） |
| LUT | nt × 2^nc × m | nt × m（選ばれた行だけ） |

LUT は**保存容量は大きくなりがち**ですが、1回の forward で**読み出すのはごく一部**です（`benchmark.py` の例：n = 32、nt = 8、nc = 6 で、保存 16,384 値に対し、読み出し 256 値）。**保存容量（メモリの大きさ）と、読み出す量（メモリ帯域）の違い**は Spiking Manifesto の重要な論点です。論文の Table IV でも、SNN 側の**保存容量（footprint）は ANN より大きく**、**トークンあたりの読み出し量（bandwidth）は小さい**という見積もりが示されています。ただし、実際のメモリ帯域や消費電力はハードウェアの構成に依存します。

### 表現容量

| 表現 | 区別できるパターンの数（理論上） |
| --- | --- |
| 発火率（1回発火のモデル、発火する／しない） | 2^n |
| 発火順序（同時発火なし） | n! |
| nt 個の LUT の index の組（nt × nc 回の比較） | 最大 2^(nt × nc)（実現できない組み合わせがあり得る） |
| 1つの LUT の index | 最大 2^nc |

### メモリ計算量（Python の実装）

`tracemalloc` で測る Python のメモリは、float 1つが約 24 バイト、リストの管理領域もあるため、「値の数 × 4 バイト（float32）」のような理論値とは大きく違います。比較するときは、**値の数（理論値）と Python での測定値を分けて**記録してください。

## 11. 教科書との関連

教科書：柴田望洋『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』

### 実際に使用したコード（`textbook/`）

| ファイル | 原本 | 用途 |
| --- | --- | --- |
| `textbook/insertion_sort.py` | 第6章 `chap06/insertion_sort.py`（単純挿入ソート） | **発火順序の計算**（`spike_encoding.spike_order`）。(発火時刻, 番号) の組を並べる |
| `textbook/ssearch_while.py` | 第3章 `chap03/ssearch_while.py`（線形探索） | **LUT の行を線形探索で探す比較実験**（`benchmark.compare_direct_index_and_linear_search`） |

- どちらも**直接 import** しています（`from textbook.insertion_sort import insertion_sort`）。Adapter やラッパークラスは作っていません。
- 原本どおり、入力を受け付ける処理は `if __name__ == '__main__':` の中にあるので、import しても副作用はありません。
- 教科書のサンプルコードを**そのままコピー**したものです（SHA-256 で原本との一致を確認済み。改行コードも原本どおり CRLF）。**編集しないでください。**

### 参考にしただけのコード（コピーしていません）

| ファイル | 内容 | 使わなかった理由 |
| --- | --- | --- |
| 第3章 `chap03/bsearch.py` | 二分探索 | LUT は index で直接読めるので、探索そのものが不要。行のキーを並べて二分探索する方法との比較は学生の課題にできる |
| 第3章 `chap03/chained_hash.py`、`open_hash.py` | ハッシュ法 | 下の「ハッシュ法と LUT」の説明に使った。LUT の実装には不要 |
| 第6章 `chap06/selection_sort.py` | 単純選択ソート | **安定でない**（等しい要素の順序が保たれない）。発火順序の計算は (時刻, 番号) の組で行うので実害はないが、安定な挿入ソートを選んだ |
| 第5章 `chap05/factorial.py`、`math_factorial.py` | 階乗（再帰、`math.factorial`） | n! は `math.factorial` を直接使った。`math_factorial.py` は import すると入力待ちになるため import できない |

### 教科書との対応

1. **線形探索と LUT 参照の違い**：「ビット列をキーにして、表の中から一致する行を**探す**」と、線形探索では O(2^nc) かかります。LUT は、比較結果のビット列を**そのまま行番号（index）にする**ので、探索せずに O(1) で行を読めます（教科書のハッシュ法の「直接アドレス表」に近い考え方）。`benchmark.py` で、nc = 12（4096 行）のとき、線形探索は index による直接の読み出しより数十〜百倍程度遅くなります（作成時の測定では約 90 倍）。
2. **辞書・ハッシュ法と LUT の関係**：ハッシュ法は「キー → ハッシュ値 → 表の位置」で、LUT は「latency vector → 比較のビット列 → index → 行」です。どちらも**値から表の位置を直接計算する**点が共通です。Python の `dict` や `set` もハッシュ表です。
   - **違い**：教科書のハッシュ法は、**違うキーをなるべくばらばらの位置に散らし**、衝突（違うキーが同じ位置になること）は**避けるべきもの**として、チェイン法やオープンアドレス法で解決します。キーそのものも表に保存し、完全に一致するものだけを探します。
   - 論文の LUT は、**似た latency vector（発火順序がほとんど同じ入力）を、わざと同じ index に集める** locality-sensitive hashing（LSH）的な仕組みです（Section VI）。「衝突」は避けるものではなく、**似た入力に同じ出力を返す（汎化する）ための性質**です。キーは保存せず、衝突の解決もしません。
3. **ソートとスパイク発火順序**：発火順序は、発火時刻を昇順に並べたときのニューロン番号の列です。**安定なソート**（挿入ソート）を使い、同時発火の扱いを明確にしています。ソートは O(n²)（挿入ソート）や O(n log n) かかりますが、LUT は**全体をソートせず**、選んだ nc 組だけを比べます。
4. **組合せ・順列と情報表現容量**：n 個の発火順序は順列の数 n!（第5章の階乗）、nc 回の比較の結果は 2^nc 通り、n 個から2つを選ぶ組は n(n−1)/2 通り（組合せ）です。
5. **データ構造と計算量**：ANN は**2次元配列（リストのリスト）を全部走査**するので O(nm)、LUT は**配列の添字アクセス**を nt 回行うので読み出しは O(nt × m) です。その代わり、保存容量は 2^nc に比例します（時間と記憶容量のトレードオフ）。

## 12. ファイル構成

```text
e3-ann-snn-comparison/
├── README.md               この説明
├── .gitignore
├── starter.py              一連のデモ（ANN → LIF → spike timing/order → LUT → 演算回数 → TODO）
├── ann.py                  簡易 ANN（y = ReLU(Wx + b)、for ループ）と演算回数
├── lif_snn.py              LIF ニューロン、発火率、最初のスパイク時刻（latency）
├── spike_encoding.py       発火順序、発火数、n!、同時発火の規則、時刻の丸め
├── spike_lut.py            Spiking Manifesto 型 LUT（比較 → ビット → index → 行 → 加算）
├── benchmark.py            ANN と LUT の演算回数・時間・メモリの比較の入口
├── experiments.py          学生向け研究実験 Experiment 1〜5 の入口
├── tensor_backends.py      ANN・LUT のバッチ（Tensor）版：NumPy・PyTorch・JAX（Notebook 04・05 用、21〜22章）
├── notebooks/              Google Colab・Jupyter 用 Notebook 01〜05 と README（21章）
├── data/
│   └── sample_patterns.json  人工のスパイクパターン・ANN と LUT の例
├── textbook/               教科書のサンプルコード（編集しない）
│   ├── __init__.py
│   ├── insertion_sort.py
│   └── ssearch_while.py
└── tests/
    ├── test_ann.py
    ├── test_lif_snn.py
    ├── test_spike_encoding.py
    ├── test_spike_lut.py
    └── test_tensor_backends.py   NumPy・PyTorch・JAX 版が基準実装と一致するか（ライブラリがなければスキップ）
```

## 13. 実行方法

このディレクトリ（`e3-ann-snn-comparison/`）で実行してください。Python 3 の標準ライブラリだけで動作します（NumPy などは不要）。

```bash
python3 starter.py
python3 -m unittest discover -s tests -v
python3 experiments.py          # Experiment 1〜5（python3 experiments.py 4 のように番号指定も可）
python3 benchmark.py            # ANN と LUT の比較の例
```

> Notebook（`notebooks/`）と `tensor_backends.py` は NumPy・Matplotlib を使います（PyTorch・JAX は任意）。上のコマンドと Core Research は、これまでどおり標準ライブラリだけで動きます。`tests/test_tensor_backends.py` は NumPy がなければ自動でスキップされます。Notebook の使い方は 21章を参照してください。

`starter.py` の実行結果（抜粋）：

```text
=== Spike Timing ===
Pattern A: [0.1, 0.2, 0.3, 0.4]   counts: [1, 1, 1, 1]   order: [0, 1, 2, 3]
Pattern B: [0.4, 0.3, 0.2, 0.1]   counts: [1, 1, 1, 1]   order: [3, 2, 1, 0]
Spike counts: same
Spike order: different

=== Spike LUT ===
Anchor pairs: [(0, 1), (1, 2), (2, 3)]   (nc = 3, rows = 2^3 = 8)
Latency example: [0.3, 0.1, 0.4, 0.2]
  Comparisons: x[0]>x[1]:1, x[1]>x[2]:0, x[2]>x[3]:1
  Comparison bits: [1, 0, 1]  → binary 101
  LUT index: 5
  Output (selected row): [0.4, 0.4]
```

`benchmark.py` の実行結果の例（時間は環境・実行ごとに変わります）：

```text
ANN: n = 32, m = 32     LUT: nt = 8, nc = 6, m = 32（seed = 0、各 200 回測定の中央値）
                                     ANN           LUT
multiplications                    1,024             0
comparisons                           32            48
parameters (stored)                1,056        16,384
values read / forward              1,056           256
forward time [µs]                  34.60         15.65
```

## 14. Core Research

すべてのチームが取り組む課題です。

1. **ANN を実行する。**（`ann.dense_forward`）
2. **LIF ニューロンを実行する。**（`lif_snn.simulate_lif`）
3. **spike timing を記録する。**（スパイク時刻、最初のスパイク時刻）
4. **spike order を比較する。**（発火数が同じで順序が違うパターン）
5. **LUT index を計算する。**（`compare_pairs` → `bits_to_index`）
6. **LUT 出力を計算する。**（`lut_forward`）
7. **ANN と LUT の演算構造を比較する。**（乗算・加算・比較・参照の回数、保存容量と読み出し量）
8. **入力次元や LUT 数を変更する。**（n、m、nt、nc）
9. **計算時間を測定する。**（`time.perf_counter()`、複数回測定して中央値）
10. **結果を表・グラフにまとめる。**
11. **論文の主張との対応を考察する。**（17章の表を使い、何を再現し、何を再現していないかを明記する）

### 研究実験（`experiments.py`）

| 実験 | 目的 | 操作変数 | 評価指標 | 予想される結果 | 学生向け TODO |
| --- | --- | --- | --- | --- | --- |
| **Experiment 1**：ANN の情報表現 | 連続値の入力に対する ANN の出力を観察する | 入力の大きさ、重み、バイアス | 出力の値、0 になる出力 | 入力に対して出力が連続的に変わる。ReLU で 0 になる出力がある | 入力を少しずつ変えてグラフ化、入力の順序を入れ替えた場合 |
| **Experiment 2**：LIF の発火 | 入力電流と膜電位・スパイクの関係を調べる | 入力電流、tau、dt、V_th | スパイク数、発火率、最初のスパイク時刻 | R×I ≤ V_th では発火しない。入力が強いほど発火が多く、早い | 発火しない理由を式で説明、パラメータを変えて表にする |
| **Experiment 3**：Spike order | 発火率が同じで順序が違う入力を比べる | 発火時刻、ノイズの大きさ、分解能 | 発火数、発火順序、順序の変化率 | 発火数は同じでも順序で区別できる。ノイズが大きいと順序が変わる | 他の例を作る、ノイズによる順序の変化率、分解能と同時発火 |
| **Experiment 4**：LUT index | spike timing を変えたとき、選ばれる index がどう変わるか | 発火時刻、anchor pair | ビット列、index、出力 | 比較する2つの発火時刻の大小が入れ替わるところで index が変わる。同時発火ではビット 0 | 同時発火の影響、変わりやすい入力の特徴、到達できない index の列挙 |
| **Experiment 5**：計算コスト | ANN と LUT の演算回数と forward 時間を比べる | n、m、nt、nc | 乗算・比較・参照の回数、時間（中央値）、保存容量、読み出し量 | LUT は乗算 0。保存容量は nc とともに指数的に増えるが、読み出し量は nt × m | 系統的に変えて表・グラフ化、保存容量と読み出し量の違い |

## 15. Advanced Research

必須課題を終えたチームが挑戦する課題です。**Advanced A〜E のうち1つ以上を選択**してください。すべてを実装する必要はありません。

### Advanced A：Spike order の情報表現容量

- n! の増加を調べる（n = 1〜20 程度、対数グラフ）。
- 実現可能な発火順序を列挙する（小さな n で、`itertools.permutations` など）。
- 各発火順序がどの LUT index になるかを調べ、**index の衝突**（違う順序が同じ index になること）と**到達できない index** を数える。
- anchor pair の数 nc、選び方（ランダム／隣どうし／推移律でつながる組）を変える。
- 発火時刻にノイズを加えて、順序や index が変わる割合を調べる（乱数シードを記録）。
- **理論上の容量（n!、2^nc）と、実際に安定して識別できるパターンの数を区別**して考察する。

### Advanced B：Polychronization と時間パターン

- 複数のニューロンの発火順序（時間パターン）を扱う。
- 複数の時間パターンを生成し、ノイズを加えても再現されるか（時間的な再現性）を調べる。
- 時間ノイズへの頑健性を、発火率表現と比較する。
- LIF ニューロンどうしを**軸索伝導遅延**つきでつなぐ拡張を検討する。

> polychronization（多時性）は、Izhikevich が 2006 年に提唱した、**軸索伝導遅延のあるスパイキングネットワークの中で、特定の時間関係を持った発火パターン（polychronous group）が繰り返し現れる**現象です（論文 Appendix VIII-C でも扱われています）。**単に発火順序を列挙することと、生物学的なネットワークでの polychronization は同じではありません。** 違いを意識して研究してください。

### Advanced C：学習可能な LUT

- 簡単な教師あり分類課題を設定する（例：発火順序のパターンをクラスに分ける人工データ）。
- 出力と正解の誤差を計算する。
- **選ばれた行だけを誤差の方向に少し動かす**、といった単純な学習則を自分たちで考えて実装する。
- 論文 Section III の **surrogate gradient** による学習を調査する。論文では、|x[a] − x[b]| が最も小さい（最も入れ替わりやすい）比較のビットを反転させた行との差と、関数 U(u)（論文のシミュレーションでは U(u) = 0.5 / (1 + |u|)）を使って、latency に対する勾配を近似しています（式 (4)〜(8)）。
- ANN（同じデータ、同じ課題）と、分類精度・学習時間を比較する。

> **自分たちで考えた単純な学習則と、論文の surrogate gradient による誤差逆伝播は別物です。** 報告では明確に区別してください。

### Advanced D：論文の公開コードとの照合

著者の公開コード：<https://github.com/izhikevich/SNN>（C 言語の1ファイル `main.c` で SNN Transformer を実装）

- README とライセンス（`LICENSE` ファイル）を確認する。
- LUT の構造（表の大きさ、行の値の初期化）を調べる。
- anchor pair の選び方を調べる。
- forward 処理（index の計算、行の加算）を調べる。
- この教材の簡易モデルとの違いを整理する（例：ビットの並べ方、出力次元、行の初期値）。
- 論文と公開コードの仕様の違いがあれば記録する（README 自体にも、論文との違いがいくつか書かれています）。

> 著者のコードを**この Starter にそのまま組み込まないでください**。公開コードの実行・学習は必須ではありません（学習には大きなテキストデータと計算時間が必要です）。

### Advanced E：ANN と LUT の公平な性能比較

- 同じ入力データ・同じ分類課題を使う。
- 精度、学習時間、推論時間、パラメータ数（保存容量と読み出し量）、メモリ使用量、演算量を比較する。
- NumPy などを使った高速な実装と比較する（外部ライブラリは Advanced のみ）。

> モデルの容量や精度が違う場合は、その違いを明示してください。**実測していない電力効率を、推定値だけで断定しないでください。**

## 16. 実験条件と評価指標

### 記録すべき実験条件

- PC 環境（CPU、メモリ）、OS、Python のバージョン
- モデルの大きさ（ANN：n、m／LUT：nt、nc、m）
- anchor pair の選び方と**乱数シード**
- 入力データ（発火時刻、ノイズの大きさ、分解能、乱数シード）
- LIF のパラメータ（dt、tau、V_th、V_reset、R）
- 測定の繰り返し回数と、使った統計量（中央値など）

### 評価指標

| 指標 | 内容 |
| --- | --- |
| 乗算・加算・比較・LUT 参照の回数 | `ann_operation_counts`、`lut_operation_counts`（この実装での回数） |
| 処理時間 | `time.perf_counter()` で複数回測定し、**中央値**（外れ値に強い）を使う |
| パラメータ数 | 保存している値の総数 |
| 読み出し量 | 1回の forward で読み出す値の数 |
| メモリ使用量 | 値の数からの理論値と、`tracemalloc` による Python での測定値を分けて記録 |
| 区別できるパターン数 | 発火順序の数、index の種類、衝突の数 |

## 17. 論文との対応関係

論文：E. Izhikevich, "Spiking Manifesto", arXiv:2512.11843v2（2025年12月31日版の HTML を参照）。図・式の番号は v2 の本文と照合しました。

| 論文 | 内容 | この教材 |
| --- | --- | --- |
| Section I | 宣言（AI の効率、スパイクのタイミング） | README 6章 |
| **Fig. 1** | (b) 60 個のニューロンが1回ずつ発火すると 60! 通りのパターン（spike timing の情報表現） | `spike_encoding.num_orders`、README 5章 |
| **Fig. 5** | ある発火パターン x から次のパターンへの変換（latency vector の変換） | `lut_forward` の入力と出力 |
| **Fig. 6** | anchor pair と LUT の例（nt = 3、nc = 3、入力 10 次元、anchor は初期化時にランダム） | `SpikeLUT`、`make_random_tables`、`starter.py` |
| **式 (1)** | 比較結果 (x[a] − x[b] > 0) を並べて index にする | `compare_pairs`、`bits_to_index` |
| **式 (2)・(3)** | 各 LUT で選ばれた行を足して出力 y とする | `lut_forward` |
| Section III（式 (4)〜(8)） | surrogate gradient と誤差逆伝播（学習則） | **実装していない**（Advanced C） |
| Section IV-A（式 (9)・(10)） | deep SNN：残差つき MLP の行列積を LUT に置き換える（x^{l+1} = x^l + S^l_{x^l}） | **実装していない**（Advanced。starter の「次の latency vector」は1層分だけ） |
| Section IV-B〜D、V | spiking RNN、SNN Transformer、実験結果 | 扱わない |
| Section VI | spiking を locality-sensitive hashing として見る | README 11章（ハッシュ法との違い） |
| Appendix VIII-A・B | ANN と SNN の表現容量 | README 10章、Advanced A |
| Appendix VIII-C | polychrony（時間ビンでの容量の議論を含む） | Advanced B |
| Appendix VIII-D | spiking network を LUT として見る | README 8章 |
| Appendix VIII-E | latency（発火しないニューロンは大きな latency、入力の強さを latency で表す） | `lif_snn.latency_encode`、README 4章 |

### 論文のモデルと、この教材の簡略モデルの違い

| 項目 | 論文 | この教材 |
| --- | --- | --- |
| 出力の次元 | 入力と同じ（y がそのまま次の latency vector） | 任意の m（`starter.py` の複数 LUT の例は m = n = 4、Fig. 6 風の単一 LUT の例は m = 2） |
| ビットの並び | Fig. 6 の例は1つ目の比較が上位ビット。著者コードは1つ目が最下位ビット（Appendix VIII-C の式も最下位側から重みをつける形） | 1つ目の比較を最上位ビット |
| 同時発火 | 比較の規則として明記されていない（式 (1) は u > 0）。学習の説明では、u = 0 のときは2つの行の平均がよいだろう、と述べている | ビット 0 と定義 |
| latency の基準 | 区間の中心からの時刻（負の値もあり得る） | 観測区間の始まりからの時刻（0 以上） |
| 行の値 | 学習で決める（著者コードは 0 で初期化） | 手で決めた値、または乱数（seed 固定） |
| 学習 | surrogate gradient による誤差逆伝播 | なし（Advanced C） |
| 規模 | 例：spiking RNN で nt = 64、nc = 10、SNN Transformer で約 8 億パラメータ（論文 Table I〜III） | nt = 3、nc = 3 程度 |

### 効率に関する論文の主張の読み方

- 論文は、現在の AI モデルは脳より**約1000倍効率が悪い**とし、スパイクの考え方で**1000倍の改善の可能性**がある、と述べています。これは**主張・見通し**であり、論文の中で消費電力を測定した結果ではありません。
- 論文 Table IV などの ANN と SNN の比較は、**演算回数・保存容量・読み出し量を式から計算した見積もり**です。保存容量（footprint）は SNN の方が**大きく**、トークンあたりの読み出し量（bandwidth）と演算回数が**小さい**、という内容です。
- この教材でも、**消費電力は測定していません**。報告では「測ったもの」と「論文の見積もり」を区別して書いてください。

## 18. GitHub を用いたチーム開発

チームで GitHub を使って研究を進めてください（公開設定については冒頭の注意を参照）。

- **役割分担を明確にする**：例）ANN・LIF 担当、spike encoding 担当、LUT 担当、実験・測定担当、論文調査担当、README・考察担当
- **GitHub Issues でタスク管理**：やること（実装・実験・論文の調べ物・不具合）を Issue に登録し、担当者を割り当てる
- **branch を分けて実装**：例）`feature/spike-noise`、`feature/lut-reachability`、`experiment/ann-vs-lut-cost`
- **Pull Request でコードレビュー**：変更は Pull Request で提出し、他のメンバーがレビューしてから merge する。テストが通ることを確認する
- **README への追記**：実験条件・結果・考察を README（または別の報告ファイル）に追記していく
- **最終成果物の Release**：研究が完成したら、成果物をまとめて Release（例：`v1.0`）として公開する

## 19. 成果物と提出方法

提出する成果物：

1. **コード**：実験用プログラム、追加したパターン、選択した発展課題の実装（テストが通ること）
2. **実験結果**：表・グラフ（実験条件を併記）
3. **報告**（README への追記、または別の報告ファイル）
   - Core Research 1〜11 の結果と考察
   - 選択した Advanced Research のテーマ、方法、結果、考察
   - RQ1〜RQ4 に対するチームとしての答え
   - 「ANN の重み付き和」と「LUT 演算」の違いを、自分たちのコードを使って説明した節
   - 論文のどの部分を再現し、どの部分を再現していないか
   - 参考にした文献・Web ページの出典
4. **GitHub の記録**：Issue、branch、Pull Request、Release

提出方法（期限・提出先）は、授業で指示します。

## 20. 参考文献・著作権上の注意

### 論文と公開コード

- E. Izhikevich, "Spiking Manifesto", arXiv:2512.11843, 2025. <https://arxiv.org/abs/2512.11843>（本文 HTML：<https://arxiv.org/html/2512.11843v2>）
  - arXiv のページには、論文のライセンスとして **CC BY-NC-SA 4.0** が表示されています。図や文章を報告に使う場合は、出典を明記し、ライセンスの条件を守ってください。
- 著者の公開コード：<https://github.com/izhikevich/SNN>
  - GitHub のページには **MIT License** と表示され、`LICENSE` ファイルがあります（この教材の作成時には、`LICENSE` ファイルの本文までは確認していません。利用する前に本文を確認してください）。README には「Hardware patent pending」との記載もあります。
  - **この Starter には著者のコードをコピーしていません。** 参照するだけにしています。
- E. M. Izhikevich, "Polychronization: Computation with Spikes", *Neural Computation*, 18(2), 2006（Advanced B）
- W. Gerstner, W. M. Kistler, R. Naud, L. Paninski, *Neuronal Dynamics*, Cambridge University Press, 2014（LIF モデル）
- P. Indyk, R. Motwani, "Approximate Nearest Neighbors: Towards Removing the Curse of Dimensionality", *STOC*, 1998（locality-sensitive hashing）
- Python 標準ライブラリ `math`、`random`、`json`、`time`、`statistics`、`tracemalloc` のドキュメント

### 教科書コード

- 出典：柴田望洋 著『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』SBクリエイティブ　第3章「探索」、第6章「ソート」
- 使用ファイル：`textbook/insertion_sort.py`（原本 `chap06/insertion_sort.py`）、`textbook/ssearch_while.py`（原本 `chap03/ssearch_while.py`）
- 参考にしただけのファイル：11章の表を参照（このリポジトリにはコピーしていません）
- 教科書コードは第三者の著作物です。公開再配布の許諾はまだ確認していません。**将来 GitHub で配布する前に、再配布条件を必ず確認してください。**

### Notebook 04 で参考にした Notebook・ライブラリ

- 授業の `ai-programming-2026-team-project-1-starter` リポジトリ `A_cpu_gpu_tpu/A_cpu_gpu_tpu_benchmark/starter.ipynb`（MIT License, Copyright (c) 2026 Daigo Takeuchi）。環境チェック、CUDA の同期、使えないデバイスのスキップ、棒グラフの構成を参考にし、E3 向けに書き直した（コードのコピーはしていない）。
- NumPy、Matplotlib、PyTorch、JAX のドキュメント（非同期実行と同期、`jax.jit`、`block_until_ready`）

### サンプルデータ

- `data/sample_patterns.json` は、この教材のために作成した**人工のデータ**です。実際の神経活動の記録ではありません。

研究で他の文献や Web ページを使った場合は、出典と参照日を記録してください。

## 21. Google Colab Notebook

`notebooks/` に、Google Colab とローカルの Jupyter で実行できる Notebook を追加しました。**アルゴリズムの本体は既存の `.py` にあり、Notebook はそれを import して説明・可視化・実験を行います**（同じアルゴリズムを Notebook に書き直していません）。詳しい使い方・ランタイム設定・トラブルシューティングは [`notebooks/README.md`](notebooks/README.md) を参照してください。

| Notebook | 内容 |
| --- | --- |
| `01_ann_lif_basics.ipynb` | ANN（Wx + b、ReLU）と LIF ニューロン（膜電位・閾値・スパイク時刻・発火率・latency）の可視化 |
| `02_spike_timing_and_lut.ipynb` | spike raster、発火順序と n!、pairwise comparison → binary index → LUT 行 → 出力 latency vector、ノイズへの頑健性。論文モデルと簡略モデルの違い |
| `03_ann_vs_snn_benchmark.ipynb` | ANN・LIF-SNN・LUT の演算回数・パラメータ数・メモリ・実行時間（純 Python、CPU）。「計算原理」「実装の処理時間」「同一タスクでの性能」を区別 |
| `04_colab_cpu_gpu_tpu.ipynb` | ANN と LUT のバッチ計算を CPU（NumPy・PyTorch・JAX）・GPU（PyTorch CUDA・JAX）・TPU（JAX）で比較。初回・コンパイル・転送・計算本体を分けて測定 |
| `05_research_experiments.ipynb` | 学生が Research A〜E を選んで実験を追加するテンプレート（結果は入っていない） |

### 実行方法（概要）

- **ローカル**：`pip install numpy matplotlib jupyter` のあと、`jupyter notebook notebooks/`。各 Notebook の最初のセルが E3 のルートを自動で見つけます。
- **Colab（方法A：GitHub から clone）**：最初のセルの `REPO_URL` に自分たちのリポジトリの URL を入れて実行。**`textbook/` は公開リポジトリに含めない**でください（なければ `spike_encoding.py` などの import が失敗します）。
- **Colab（方法B：ZIP をアップロード）**：E3 フォルダを ZIP にして `/content` にアップロードし、最初のセルを実行すると展開して作業ディレクトリを設定します。

Notebook には WSL などの固定の絶対パスを書いていません。

### 追加したコード

- `tensor_backends.py`：`ann.dense_forward` と `spike_lut.lut_forward` と**同じ計算**を、バッチ（2次元配列）でまとめて行う NumPy・PyTorch・JAX 版。LUT も Python の for ループではなく、比較・整数演算・gather（index による行の読み出し）・総和の Tensor 演算で書いています。環境検出（`detect_environment`）と、ウォームアップ・同期つきの時間測定（`time_call`）も含みます。
- `tests/test_tensor_backends.py`：上の各版が基準実装と一致すること（LUT index は完全一致、出力は許容誤差つき）を確認します。PyTorch・JAX がなければその部分はスキップされます。
- 既存の `.py`・テスト・Core Research・Advanced Research の内容は変更していません。

## 22. CPU・GPU・TPU 比較

Notebook 04 の背景となる考え方です。

### CPU と GPU の計算特性

- **CPU**：少数の高性能なコア。分岐の多い処理、逐次処理、不規則なメモリアクセスに強く、1 回の計算を始めるまでの遅延（オーバーヘッド）が小さい。
- **GPU**：数千の単純なコアで、**同じ計算を大量のデータに一斉に**行う。命令は**非同期**に実行され（命令を出したらすぐ次に進む）、CPU のメモリとは別の GPU のメモリを使うため、**データ転送**が必要。
- そのため、小さな計算（バッチ 1 など）では CPU の方が速いことがよくあり、大きなバッチ・大きな行列ほど GPU が有利になりやすい。

### TPU の計算特性

- Google が設計した、**行列積専用の回路**（systolic array）を持つ装置。bfloat16 などの低精度の行列積が特に速い。
- **XLA コンパイラ**で計算全体をコンパイルしてから実行する。配列の **shape が固定（静的）** されていることが前提で、shape が変わるとコンパイルし直す。最初の実行にはコンパイル時間がかかる。
- Notebook 04 では TPU を **JAX**（`jax.jit`、`block_until_ready()`）で使います（参考にした授業の Notebook は TensorFlow を使っていました）。

### ANN の行列演算

- ANN の forward は $Y = \mathrm{ReLU}(XW^\top + b)$ という**行列積**が中心です。計算が規則的で、同じ重みを多くの入力で再利用できるので、GPU・TPU が最も得意とする形です。

### LUT の比較演算とメモリアクセス

- LUT の forward は、**比較**（$x_a > x_b$）→ **ビットを整数にする** → **index で行を読み出す（gather）** → **和** です。乗算はありません。
- 比較と和は並列化できますが、読み出す行は**入力によって変わる**（不規則なメモリアクセス）ため、行列積ほどハードウェアの性能を引き出せないことがあります。
- そのため、**行列演算に最適化された GPU・TPU 上で LUT が ANN より速くなるとは限りません**。どうなるかは Notebook 04 で実際に測ってください。

### 実行時間測定の注意点

| 注意 | 対処（Notebook 04） |
| --- | --- |
| GPU・TPU は非同期に実行される | PyTorch は `torch.cuda.synchronize()`、JAX は `block_until_ready()` で終了を待ってから時計を止める |
| 初回は初期化・コンパイルを含む | 初回時間、コンパイル時間（`lower().compile()`）、ウォームアップ後の中央値を分けて記録 |
| データ転送に時間がかかる | パラメータの転送時間と入力の転送時間を、計算本体と別に記録 |
| 測定値はぶれる | ウォームアップのあと複数回測って中央値。乱数シードを固定 |
| 精度設定で結果も時間も変わる | dtype（float32）を記録。PyTorch の TF32 を無効化、JAX の行列積精度を `highest` に設定。PyTorch・JAX・NumPy・基準実装の結果が許容誤差内で一致することを確認 |
| 大きすぎる条件で止まる | メモリ（`MAX_BYTES`）と時間（`TIME_BUDGET_S`）の安全上限 |

### ハードウェア性能比較の限界

- 測っているのは **Colab の共有マシン上での実行時間**です。割り当てられる機種や混雑状況で結果が変わります。
- 実装の違い（純 Python か、NumPy か、PyTorch か、JAX か）による差は、デバイスの違いによる差と同じくらい大きいことがあります。**デバイスの差と実装の差を混同しないでください。**
- GPU・TPU は ANN の行列演算向けに設計されたハードウェアです。**Colab の CPU・GPU・TPU の処理時間比較から、SNN 専用ニューロモルフィックハードウェアの性能や電力効率を結論することはできません。** この教材では消費電力を測定していません（9章・17章も参照）。
- 測定できなかったデバイスの値を推測で補わないでください。Notebook 04 は、実際に測定できたデバイスだけを表示します。

## 23. 教科書との関連（Notebook・Tensor 実装との対応）

11章の内容（線形探索と LUT 参照、ハッシュ法と LUT、ソートと発火順序、順列・組合せと表現容量、データ構造と計算量）に加えて、Notebook と Tensor 実装では次の対応があります。

| 教科書の内容 | ANN・SNN・LUT の実装との関係 | 確認できる場所 |
| --- | --- | --- |
| **探索**（第3章：線形探索・二分探索） | LUT は比較結果のビット列を**そのまま行番号**にするので、行を探索しない（O(1) の添字アクセス）。Tensor 版では、この添字アクセスをバッチ全体でまとめて行う **gather**（`rows[t, index]`）になる | `benchmark.compare_direct_index_and_linear_search`、Notebook 04 |
| **ハッシュ法**（第3章：チェイン法・オープンアドレス法） | 「値 → 計算 → 表の位置」という点で LUT はハッシュ表に近い。ただし LUT は**似た入力を同じ index に集める**（locality-sensitive hashing 的）ので、衝突は避けるものではなく汎化のための性質。Notebook 02 のノイズ実験で、近い入力が同じ index になりやすいことを確かめられる | 11章、Notebook 02 |
| **ソート**（第6章：単純挿入ソート） | 発火順序は (発火時刻, 番号) を**安定に**並べたもの（`spike_order`）。LUT は全体をソートせず、選んだ $n_c$ 組を**比較するだけ**。Tensor 版の比較 `X[:, a] > X[:, b]` は、ソートの比較操作を多数同時に行うものと見ることができる | `spike_encoding.spike_order`、Notebook 02 |
| **再帰・階乗**（第5章） | 発火順序の数 $n!$、比較結果の数 $2^{n_c}$、anchor pair の候補 $n(n-1)/2$ | Notebook 02 の $n!$ と $2^n$ のグラフ |
| **配列とデータ構造・計算量** | ANN は 2 次元配列（重み行列）を**全部**読む $O(nm)$。LUT は 3 次元配列（$n_t \times 2^{n_c} \times m$）の**一部の行だけ**を読む。保存容量と読み出し量のトレードオフ。Python のリストと NumPy 配列では同じ値の数でもメモリ量が大きく違う | Notebook 03（tracemalloc と理論値）、Notebook 05 Research D |
| **for ループとベクトル化** | 同じアルゴリズムでも、1 入力ずつの for ループ（`lut_forward`）と、バッチの配列演算（`tensor_backends`）で実行時間が何桁も変わる。計算量のオーダーが同じでも、定数倍（実装・ハードウェア）が大きく違う | Notebook 04（Python と NumPy の比較） |

> Notebook でも、教科書のコードは `textbook/` から import して使うだけで、コピー・改変はしていません（`spike_encoding.py` 経由で単純挿入ソート、`benchmark.py` 経由で線形探索）。

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
| `chap06/insertion_sort.py` | `e3-ann-snn-comparison/textbook/insertion_sort.py` | `spike_encoding.py` |
| `chap03/ssearch_while.py` | `e3-ann-snn-comparison/textbook/ssearch_while.py` | `benchmark.py` |

### 3. 配置後のディレクトリ構成

```text
e3-ann-snn-comparison/
└── textbook/
    ├── __init__.py          （リポジトリに含まれる）
    ├── insertion_sort.py    （各自で配置）
    └── ssearch_while.py     （各自で配置）
```

### 4. コピーと確認のコマンド例

```bash
cd e3-ann-snn-comparison
SRC="<展開したフォルダ>"        # 各自の環境に合わせる

cp -i "$SRC/chap06/insertion_sort.py" textbook/insertion_sort.py
cp -i "$SRC/chap03/ssearch_while.py" textbook/ssearch_while.py

# 原本とコピーの SHA-256 が一致することを確認する
sha256sum "$SRC/chap06/insertion_sort.py" textbook/insertion_sort.py
sha256sum "$SRC/chap03/ssearch_while.py" textbook/ssearch_while.py

python3 starter.py                          # 実行確認
python3 -m unittest discover -s tests -v    # テスト
```

配置した教科書のコードは、リポジトリ直下の `.gitignore` によって Git の追跡対象から除外されます（`git status` に表示されなければ正常です）。
`git add -f` などで教科書のコードを commit・push しないでください。
