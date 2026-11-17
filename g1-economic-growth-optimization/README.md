# G1：国家・世界経済の成長と資源配分の最適化

**補遺トピック／Python + Google Colab／経済成長シミュレーションと最適化アルゴリズムの比較**

> **この教材は、教育用の架空モデルです。**
> - 国名（Country G）・経済指標・投資効果の係数は、すべて架空です。
> - 現実の国家の GDP、経済成長率、政策効果を予測するものではありません。
> - **実際の政策判断には使わないでください。**
>
> 詳しくは「[25. モデルの限界](#25-モデルの限界)」を必ず読んでください。

---

## 1. 補遺トピック G1 の位置づけ

- G1 は、チーム課題 A〜F の課題リストには含まれていない**補遺トピック**（Supplementary / Optional Research Topic）です。学生には正式に案内していません。
- 既存の A〜F の課題リスト・案内文書・README は変更していません。
- 扱い方は授業の判断によります。たとえば、F 課題（自由研究）を発展させたいチーム向けの選択肢として提示することが考えられます。
- リポジトリの構成は F1〜F5 と同じです。
  - 計算は `.py`、実験・可視化・発表は `.ipynb`。
  - Core は標準ライブラリだけで動く。
  - unittest を使う。
  - 教科書のコードは改変せずに `textbook/` に置く。

## 2. 研究テーマと目的

教育・研究開発・インフラ・医療への**公共投資の配分**が、経済成長や生活水準にどう影響するかを、簡単な数理モデルと Python のアルゴリズムで比較・分析します。

1. 限られた予算を、複数の分野に配分する。
2. 各分野への投資が、将来の経済・社会の指標に与える効果をモデル化する。
3. 10〜30 年間の経済成長をシミュレーションする。
4. 異なる投資配分の戦略を比べる。
5. 全探索・Greedy 法・局所探索などの最適化アルゴリズムを比べる。
6. GDP の成長と生活水準の改善が、必ずしも一致しないことを確かめる。
7. モデルの仮定や目的関数によって、最適解が変わることを分析する。

### Research Questions

| RQ | 問い | 主な実験・Notebook |
| --- | --- | --- |
| RQ1 | 投資配分によって、経済成長はどのように変化するか | Experiment 1、Notebook 01・02 |
| RQ2 | GDP 成長率を最大にする配分は、生活水準も最大にするか | Experiment 4、Notebook 04 |
| RQ3 | 短期的な最適配分と長期的な最適配分は一致するか（5・10・20・30 年） | Experiment 3、Notebook 05 |
| RQ4 | 全探索・Greedy 法・局所探索で得られる解は、どう違うか | Experiment 2、Notebook 03 |
| RQ5 | 予算制約や投資効果の仮定によって、最適配分は変わるか | Experiment 5〜7、Notebook 05 |
| RQ6 | 複数の経済・社会指標を同時に改善できるか | Experiment 4、Notebook 04 |

**どの配分が最もよいかは、このリポジトリでは決めていません。**実験して確かめてください。

### 学ぶこと

予算制約、資源配分、経済成長の簡易モデル、状態変数と状態更新、時系列シミュレーション、全探索、Greedy 法、局所探索、ソートとランキング、目的関数、制約付き最適化、計算量、感度分析、多目的評価。

経済学の高度な知識は前提にしていません。

## 3. 国家経済と資源配分

国の予算には限りがあります（**予算制約**）。ある分野に多く配分すれば、他の分野への配分は減ります。このモデルでは、毎年の公共投資予算（例：100 の架空の単位）を 4 つの分野に配分します。

```text
Education Share + R&D Share + Infrastructure Share + Healthcare Share = 1     （各 0〜1）
```

| 分野 | 投資が改善する状態変数 | 状態変数が影響するもの |
| --- | --- | --- |
| 教育 Education | 人的資本 Human Capital | GDP、生活水準 |
| 研究開発 R&D | 技術 Technology | GDP |
| インフラ Infrastructure | インフラ Infrastructure | GDP |
| 医療 Healthcare | 健康 Health | GDP、生活水準 |

比較用のシナリオは `data/investment_scenarios.json` にあります。どれも架空のシナリオです。

| シナリオ | 内容 |
| --- | --- |
| Equal Allocation | 4 分野に 25% ずつ（Baseline） |
| Education Priority | 教育 55%、他の 3 分野に 15% ずつ |
| R&D Priority | 研究開発 55%、他の 3 分野に 15% ずつ |
| Infrastructure Priority | インフラ 55%、他の 3 分野に 15% ずつ |
| Healthcare Priority | 医療 55%、他の 3 分野に 15% ずつ |
| Optimized Allocation | アルゴリズム（全探索・Greedy 法・局所探索）で求める |

## 4. 教育投資

- 教育への投資は**人的資本**を高めます（効率 `education_efficiency` = 0.02）。
- 効果が現れるまでに**遅延**があります（`education_delay` = 3 年）。
- 人的資本は、GDP（弾力性 0.25）と生活水準（重み 0.25）の両方に影響します。
- 減耗率は 0.02 です（知識や技能の陳腐化）。

## 5. 研究開発投資

- 研究開発への投資は**技術水準**を高めます（効率 `rd_efficiency` = 0.03）。
- 遅延は 2 年（`rd_delay`）、減耗率は 0.01 です。
- 技術は GDP への弾力性が最も大きい（0.30）一方で、生活水準には GDP を通してしか影響しません。

## 6. インフラ投資

- インフラへの投資は、**すぐに**インフラの水準を高めます（効率 0.025、遅延 0 年）。
- ただし減耗率が大きい（0.05：老朽化）ので、投資を続けないと水準は下がります。
- インフラは GDP（弾力性 0.25）に影響します。

## 7. 医療投資

- 医療への投資は、すぐに**健康**を高めます（効率 0.02、遅延 0 年、減耗率 0.03）。
- 健康は、GDP への弾力性は小さい（0.15）ものの、生活水準への重みが大きい（0.35）指標です。

> 4〜7 章の効率・遅延・減耗率・弾力性・重みは、**すべて教育用の架空の値**です（`data/baseline_economy.json`）。現実の政策効果を表すものではありません。

## 8. 経済成長モデル

`economic_model.py` と `simulation.py` で、1 年を 1 ステップとして計算します。

```text
for t = 1 .. T:
    投資_k(t)  = 予算 × 配分率_k                          （k = 4 分野）
    効果_k(t)  = 効率_k × 投資_k(t) ^ r                   （r = 0.5：収穫逓減。10 章）
    届く効果_k = d_k 年前の効果                            （遅延。9 章）
    X_k(t)     = (1 − 減耗率_k) × X_k(t−1) + 届く効果_k    （状態変数の更新）
    人口(t)    = 初期人口 × (1 + 人口増加率)^t
    GDP(t)     = 初期GDP × (人口(t) / 初期人口) × H^0.25 × A^0.30 × I^0.25 × S^0.15
    生活水準(t) = 0.4 × 1 人あたりGDP指数 + 0.35 × 健康指数 + 0.25 × 人的資本指数
```

### 状態変数

`gdp`・`human_capital`・`technology`・`infrastructure`・`health`・`living_standard` を使います。人的資本 H・技術 A・インフラ I・健康 S は、すべて「初期値 = 1 の指数」です。

### モデルの仮定

| 仮定 | 内容 |
| --- | --- |
| 生産能力 | 投資は状態変数（将来の生産能力）を変え、GDP は状態変数から決まる。**投資額そのものは GDP に足さない**（二重計上しない） |
| 生産関数 | 乗法的（Cobb-Douglas 型）。どれか 1 つの状態変数だけを大きくしても、効果は弾力性の分しか増えない |
| 単位 | GDP は「架空の GDP 単位」、予算は「架空の予算単位」、状態変数は単位のない指数。互いに区別する |
| 非負性 | 状態変数は 0 未満にならず、GDP も非負 |
| GDP の説明 | $\log \text{GDP}$ の変化 = 人口の寄与 + Σ 弾力性 × $\log$(状態変数の比)。`gdp_decomposition` で、どの状態変数が GDP を動かしたかを説明できる |
| 決定的 | 乱数を使わない（Core では確率的なショックなし）。同じ入力なら必ず同じ結果 |
| 予算 | 毎年一定（GDP が増えても予算は変わらない） |
| 人口 | 毎年 0.5% 増える（架空）。そのため GDP と 1 人あたり GDP は違う |

## 9. 投資効果の遅延

- 教育（3 年）と研究開発（2 年）の投資効果は、すぐには現れません。
- `DelayLine` は、教科書第 4 章の **`FixedQueue`（固定長キュー）** を使って遅延を管理します。
  1. 最初に遅延年数 d 個の 0 をキューに入れておく。
  2. 毎年「今年の効果を enque し、d 年前の効果を deque する」。
- 遅延があると、**短い評価期間**では教育・研究開発への投資の効果が見えにくくなります。そのため、評価期間によって最適配分が変わる可能性があります（RQ3、Experiment 5）。

## 10. 収穫逓減

- 投資効果 = 効率 × 投資額^r です。r = 0.5（平方根）なら、投資額を 4 倍にしても効果は 2 倍にしかなりません（**収穫逓減**）。
- 投資額 0 でも正しく動きます（効果 0）。
- r = 1 にすると収穫逓減がなくなり、配分が特定の分野に集中しやすくなる可能性があります（Experiment 6）。
- 生産関数の弾力性（1 未満）も、状態変数の水準に対する収穫逓減として働きます。

## 11. GDP と生活水準

| 指標 | 定義 |
| --- | --- |
| GDP | 状態変数と人口から計算する生産量（架空の単位） |
| 1 人あたり GDP 指数 | (GDP / 人口) ÷ 初年度の値 |
| 健康指数・人的資本指数 | 状態変数 ÷ 初期値 |
| 生活水準 | 0.4 × 1 人あたり GDP 指数 + 0.35 × 健康指数 + 0.25 × 人的資本指数（重みの合計 1、初年度 = 1） |

- **生活水準は教育用の人工的な指標**です。現実の幸福度や社会的厚生を直接表すものではありません。
- 重みは、モデル上の選択です（`living_standard_weight_*`）。
- GDP と生活水準は別の指標なので、**GDP を最大にする配分が生活水準も最大にするとは限りません**（RQ2）。Notebook 04 で、すべての配分候補の GDP と生活水準を散布図にして確かめます。

## 12. 投資配分戦略

`allocation_strategies.py`：

| 戦略 | 関数 | 内容 |
| --- | --- | --- |
| A：Equal Allocation | `equal_allocation` | 4 分野に 25% ずつ |
| B：Priority Allocation | `priority_allocation(sector, share)` | 特定の分野に share、残りを均等に |
| C：Random Allocation | `random_allocation(seed, step)` | 予算制約を満たすランダムな配分（シードで再現できる。step を指定すると格子点から選ぶ） |
| D：Greedy Allocation | `greedy_allocation` | 14 章 |
| E：Exhaustive Search | `exhaustive_allocation` | 13 章 |
| F：Local Search | `local_search_allocation` | 15 章 |

### 配分の表し方：整数単位

- 予算を **M = 1 / 刻み** 個の単位に分け、配分を整数の組 $(u_1, u_2, u_3, u_4)$（合計 M）で表します。
  - 例：刻み 10% なら M = 10、(2, 3, 3, 2) = 教育 20%・研究開発 30%・インフラ 30%・医療 20%。
- 整数で列挙・更新するので、**配分率の合計がちょうど 1** になり、浮動小数点の誤差で制約を破りません。
- 刻みに乗らない配分（例：25% を 10% 刻みで表す）は、最大剰余法で最も近い格子点に丸めます（`units_from_shares`）。
  - 均等配分は、10% 刻みでは (3, 3, 2, 2) になります（同点は分野の順）。

## 13. 全探索

- 合計 M になる 4 つの整数の組を、**再帰**ですべて列挙します（`enumerate_allocations`）。
- 列挙したすべての候補をシミュレーションで評価し、目的関数が最大の配分を選びます。
- 候補の数は $C(M + K - 1, K - 1)$ です（K = 4 分野）。
  - M = 10（刻み 10%）：286 通り
  - M = 20（刻み 5%）：1,771 通り
- 最大値は教科書の `max_of`（第 2 章）で求め、その位置は `seq_search`（第 3 章）で探します。同点なら列挙順で最初の候補になり、結果は**決定的**です。
- **離散化した探索空間の中では最適**であることが保証されます。ただし、刻みの間にある配分（例：23%）は調べていないので、連続的な真の最適とは限りません。
- 候補のランキングは、教科書の `insertion_sort`（第 6 章、安定）で作ります（`rank_candidates`）。

## 14. Greedy 法

- 予算を 1 単位ずつ、**目的関数が最も大きくなる分野**に足していきます（M ステップ × 4 分野 = 4M 回の評価）。
- 途中の段階では、予算の一部だけを投資した状態として評価します。各候補の評価には、全探索と同じ経済シミュレーションを使います。
- 一度足した単位は戻さないので、**全体の最適は保証されません**。
- このモデルの基本設定では、全探索と同じ配分になることがあります。条件を変えると違う配分になる場合もあります（Experiment 2）。

## 15. 局所探索

- 初期配分から始めて、**近傍**（ある分野から別の分野へ 1 単位移した配分。最大 12 通り）を評価します。最も良い近傍が今より良ければ、そこへ移ります（山登り法）。
- 予算の合計は常に M のままです。
- 改善がなくなるか、最大反復回数に達したら終わります。
- 止まった配分は**局所最適解**です。近傍の中では最良ですが、全体の最適とは限りません。**初期配分によって結果が変わる**ことがあります（Notebook 03、Experiment 2）。

## 16. 目的関数と制約条件

### 目的関数

`optimization.objective_value`。すべて大きいほど良い指標です。

| 名前 | 内容 |
| --- | --- |
| `final_gdp` | 最終年の GDP |
| `cumulative_gdp` | 1〜T 年の GDP の合計 |
| `final_living_standard` | 最終年の生活水準 |
| `average_living_standard` | 1〜T 年の生活水準の平均 |
| `weighted` | gdp_weight × GDP 指数 + (1 − gdp_weight) × 生活水準 |

`weighted` の GDP 指数は「最終 GDP ÷ 初期 GDP」です。生活水準と同じく初年度 = 1 の指数にそろえて、単位とスケールを正規化しています。

### 制約条件

```text
0 <= allocation_i <= 1
sum(allocation_i) = 1
```

- 配分率の検証（`simulation.validate_allocation`）では、浮動小数点の誤差を 1e-9 まで許します。
- 最適化では整数単位を使うので、合計はちょうど M（= 100%）になります。
- 合計が M を超える配分は、`Evaluator` がエラーにします。

**最適解は、目的関数・制約条件・モデルの仮定によって変わります。**「最適配分」と言うときは、どの目的関数で、どの仮定の下での最適かを必ず添えてください。

## 17. アルゴリズムと計算量

最適化アルゴリズムの計算量と、経済シミュレーション 1 回の計算量を**区別**します。シミュレーション 1 回のコストを $S = O(TK)$ とします。

| 処理 | 計算量 | 説明 |
| --- | --- | --- |
| 時系列シミュレーション（T 年、K 分野） | $O(TK)$ | 毎年、K 分野の効果・遅延・状態更新を計算する |
| 全探索 | $O(C(M+K-1, K-1) \times TK)$ | 候補数 × シミュレーション。K = 4 では候補数は約 $M^3/6$ |
| Greedy 法 | $O(M \times K \times S)$ | M ステップ × K 分野の評価 |
| 局所探索 | $O(I \times N \times S)$ | I 回の反復 × 近傍 N 個（N ≤ K(K−1) = 12） |
| 候補のランキング | $O(C^2)$ | 教科書の単純挿入ソート（C = 候補数） |

| 刻み | M | 全探索の候補数 | Greedy 法の評価回数 |
| --- | --- | --- | --- |
| 25% | 4 | 35 | 16 |
| 20% | 5 | 56 | 20 |
| 10% | 10 | 286 | 40 |
| 5% | 20 | 1,771 | 80 |
| 1% | 100 | 176,851 | 400 |

刻みを半分にすると、全探索の候補数は約 8 倍になります。Notebook 03 では、実行時間（実測）と評価回数を比べます。**実行時間は実行環境で変わります。**評価回数（シミュレーションの回数）は環境によりません。

## 18. 教科書との関連

教科書：柴田望洋『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』（SB クリエイティブ）

### 実際に使用したコード

改変せずに `textbook/` にコピーし、import しています。

| ファイル | 原本 | 関数・クラス | G1 での用途 |
| --- | --- | --- | --- |
| `textbook/max.py` | `chap02/max.py` | `max_of` | 最も目的関数値の高い配分を探す（`optimization.best_index`） |
| `textbook/ssearch_while.py` | `chap03/ssearch_while.py` | `seq_search` | 最大値が最初に現れる位置を探す（同点の処理を決定的にする） |
| `textbook/insertion_sort.py` | `chap06/insertion_sort.py` | `insertion_sort` | 配分候補・シナリオのランキング（`optimization.rank_candidates`。安定なソート） |
| `textbook/fixed_queue.py` | `chap04/fixed_queue.py` | `FixedQueue` | 投資効果の遅延（`economic_model.DelayLine`） |

- 4 本とも、原本と SHA-256 が一致することを確認しています。
- `max.py`・`ssearch_while.py`・`insertion_sort.py` の対話入力は `if __name__ == '__main__':` の中だけにあり、`fixed_queue.py` には対話入力がありません。どれも import しても入力待ちになりません。
- 教科書のコードを使うためだけの Adapter は作っていません。

### 参考にしただけのコード（コピー・import していない）

| ファイル | 理由 |
| --- | --- |
| `chap06/selection_sort.py` | 安定でない（同点の順序が変わる）ので、ランキングには単純挿入ソートを使った |
| `chap04/queue.py`（`collections.deque` 版のキュー） | 遅延の管理には容量の決まった `FixedQueue` が合う |
| `chap05/`（再帰：`8queen.py` など） | 配分候補の再帰的な列挙の考え方の参考。コードは使っていない |

指定の候補にあった `chap02/max_of.py` は、原本にはありません。`max_of` は `chap02/max.py` で定義されています。

### 教科書の内容との対応

| G1 の処理 | 教科書の内容 | G1 のコード |
| --- | --- | --- |
| 1. 配分候補の列挙 | ループ・再帰（第5章） | `enumerate_allocations`（再帰）、`neighbors`（二重ループ） |
| 2. 最適配分の探索 | 最大値探索（第2章） | `best_index`（`max_of` + `seq_search`） |
| 3. 候補のランキング | ソート（第6章） | `rank_candidates`（`insertion_sort`） |
| 4. 投資効果の遅延 | キュー（第4章） | `DelayLine`（`FixedQueue`） |
| 5. 年次経済指標の保存 | 配列・リスト（第2章） | `simulate` の `records`（年ごとの辞書のリスト） |
| 6. 最適化 | 全探索・Greedy 法 | `exhaustive`・`greedy`・`local_search` |
| 7. アルゴリズム比較 | 計算量と実行時間 | `compare_algorithms`（評価回数・実行時間・反復回数・ギャップ） |

> **教科書コードの公開再配布の条件は確認できていません。**`textbook/` を含むリポジトリを公開 GitHub に push しないでください（28 章）。

## 19. ファイル構成

```text
g1-economic-growth-optimization/
├── README.md                     … この文書
├── .gitignore
├── requirements-notebook.txt     … Notebook 用のライブラリ（Core には不要）
├── starter.py                    … 全体の流れを確認するデモ
├── economic_model.py             … 状態変数、投資効果（収穫逓減）、遅延（FixedQueue）、減耗、GDP、生活水準
├── simulation.py                 … 時系列シミュレーション、配分の検証、年次記録
├── allocation_strategies.py      … 戦略 A〜F、整数単位と配分率の変換、シナリオの読み込み
├── optimization.py               … 目的関数、全探索・Greedy 法・局所探索、アルゴリズム比較、ランキング
├── evaluation.py                 … 成長率、累積 GDP、生活水準、投資効率、最適化ギャップ、計算コスト
├── experiments.py                … 学生向け実験の入口（Experiment 1〜7）
├── growth_charts.py              … Notebook 用のグラフ（matplotlib。Core には不要）
├── data/
│   ├── baseline_economy.json     … 架空の国家のパラメータ
│   └── investment_scenarios.json … 比較用の配分シナリオ
├── notebooks/
│   ├── README.md
│   ├── 01_economic_growth_model.ipynb
│   ├── 02_investment_allocation.ipynb
│   ├── 03_optimization_algorithms.ipynb
│   ├── 04_growth_vs_living_standard.ipynb
│   ├── 05_sensitivity_analysis.ipynb
│   └── 06_research_presentation.ipynb
├── textbook/                     … 教科書のコード（改変なし。公開しない）
│   ├── __init__.py
│   ├── max.py
│   ├── ssearch_while.py
│   ├── insertion_sort.py
│   └── fixed_queue.py
└── tests/
    ├── test_economic_model.py
    ├── test_simulation.py
    ├── test_allocation_strategies.py
    ├── test_optimization.py
    ├── test_evaluation.py
    └── test_growth_charts.py     … グラフのテスト（matplotlib がなければスキップ）
```

## 20. Python プログラムの実行方法

Python 3.10 以上で動きます。Core は**標準ライブラリだけ**で動きます。

```bash
cd g1-economic-growth-optimization

python3 starter.py                        # 全体の流れ（シナリオ比較 → 全探索・Greedy 法・局所探索 → TODO）
python3 experiments.py                    # Experiment 1〜7
python3 experiments.py 3                  # Experiment 3 だけ
python3 -m unittest discover -s tests -v  # unittest
```

`starter.py` の出力の形は次のとおりです。数値は実行して確認してください。Runtime は実測値です。

```text
G1: Economic Growth and Resource Allocation

Scenario                   Final GDP  GDP/yr  Living Standard  Allocation
Equal Allocation                 ...     ...              ...  ...
...
Optimization:（目的関数 = final GDP、刻み 10%、候補 … 通り、20 年）
Algorithm             Objective      Gap    Runtime  Evaluations  Allocation
Exhaustive Search           ...      ...        ...          ...  ...
Greedy                      ...
Local Search                ...

Student Research TODOs:
  1. ...
```

## 21. Google Colab Notebook の実行方法

詳しくは [`notebooks/README.md`](notebooks/README.md) を参照してください。

| 項目 | 方法 |
| --- | --- |
| ローカル Jupyter での実行 | `pip install -r requirements-notebook.txt` → `jupyter notebook notebooks/` で開き、上から実行 |
| Google Colab での実行 | Notebook を Colab で開き、「準備」セルから実行（CPU ランタイムで十分） |
| ZIP アップロード | G1 のフォルダを ZIP にして `/content` にアップロード。「準備」セルが `/content/g1_upload` に展開する |
| GitHub からの clone | 「準備」セルの `REPO_URL` に**自分たちのリポジトリの URL** を入れる（このリポジトリには URL を書いていません） |
| 作業ディレクトリの設定 | 「準備」セルが `economic_model.py` のあるフォルダを探し、`os.chdir` する（WSL の絶対パスは使わない） |
| `.py` モジュールの import | 「準備」セルが `sys.path` に G1 のルートを加え、`economic_model`・`optimization` などを import する |

Notebook の順番：01 → 02 → 03 → 04 → 05 → 06（各 Notebook は単独でも実行できます）。

## 22. Core Research

| # | 必須課題 | 関数・ファイル |
| --- | --- | --- |
| 1 | 架空の経済データを読み込む | `economic_model.load_economy`、`allocation_strategies.load_scenarios` |
| 2 | 4 分野への投資配分を設定する | `allocation_strategies`、`simulation.validate_allocation` |
| 3 | 経済成長モデルを実装する | `economic_model.py` |
| 4 | 20 年間のシミュレーションを実行する | `simulation.simulate` |
| 5 | GDP と生活水準を計算する | `compute_gdp`・`living_standard`、`evaluation.summarize_run` |
| 6 | 複数の投資配分を比べる | Experiment 1、Notebook 02 |
| 7 | 全探索を実装する | `optimization.exhaustive` |
| 8 | Greedy 法を実装する | `optimization.greedy` |
| 9 | 局所探索を実装する | `optimization.local_search` |
| 10 | 最適配分を求める | `compare_algorithms`、Experiment 2〜4 |
| 11 | 目的関数値を比べる | `evaluation.optimization_gap` |
| 12 | 計算量を分析する | 17 章、Notebook 03 |
| 13 | 実行時間を比べる | `runtime_s`・`evaluations`、Notebook 03 |
| 14 | 感度分析を行う | Experiment 5〜7、Notebook 05 |
| 15 | 結果をグラフにまとめる | Notebook 01〜06、`growth_charts.py` |
| 16 | モデルの限界を考察する | 25 章、Notebook 06 の「モデルの限界」 |

各 `.py` の末尾と Notebook に **TODO** があります。starter の実装は最小限で、改良できる余地を残しています。

## 23. Advanced Research

A〜G から 1 つ以上を選んで取り組みます（starter には実装していません）。

### Advanced A：複数国家モデル

複数の架空の国家を用意し、国家ごとに初期 GDP・人口・人的資本・技術水準などを変えます。

- ヒント：`baseline_economy.json` を国家ごとに用意し、`with_changes` でパラメータを変える。

### Advanced B：世界全体の資源配分

限られた国際予算を、複数の国家へ配分します。次の目的関数を比べます。

- 世界全体の GDP の最大化
- 世界全体の生活水準の最大化
- 最も生活水準の低い国家の改善（最低値の最大化）
- 国家間の格差の縮小

### Advanced C：国際的な技術波及

ある国家への研究開発投資が、他の国家の技術水準にも影響するモデルを考えます。

- 例：他国の技術との差の一定割合が毎年移る。

### Advanced D：確率的な経済ショック

景気後退・災害・技術革新などの架空のイベントを入れます。乱数のシードを指定して再現できるようにし、複数回の平均とばらつきを報告します。

### Advanced E：動的な投資配分

毎年の経済状態に応じて、投資配分を変えます。

- 例：健康指数が下がったら医療を増やす。
- 例：最初の 10 年と後の 10 年で配分を変える。

### Advanced F：多目的最適化

GDP・生活水準・健康・格差などの複数の指標を同時に最適化します。

- Notebook 04 の散布図で、**Pareto 最適**（どの指標も悪くせずには改善できない配分）を求めてみましょう。

### Advanced G：公開統計との比較

世界銀行・OECD・UNDP などの公開統計を使い、モデルの初期条件や妥当性を検討します。

- 実データを使う場合は、**出典・対象年・単位・定義**を明記してください。
- **統計的な相関を、政策の因果効果と解釈しないでください。**

## 24. 実験条件と評価指標

### 実験の約束

- **同じ初期条件**（`baseline_economy.json`）、**同じ予算**、**同じ評価期間**で比べる。違いを調べたい条件以外は変えない。
- アルゴリズムを比べるときは、**同じ目的関数・同じ刻み（探索空間）・同じシミュレーション**を使う。
- 全探索の最良値は、**離散化した探索空間の中での基準値**として使う。Greedy 法・局所探索が全探索と同じになると仮定しない。
- 実行時間は**実測値**で、実行環境で変わる。評価回数と一緒に報告する。
- 「最適配分」には、**目的関数・評価期間・刻み・パラメータ**を必ず添える。

### 評価指標（`evaluation.py`）

| 指標 | 関数 | 内容 |
| --- | --- | --- |
| GDP Growth Rate | `growth_rate`・`annual_growth_rate`・`gdp_growth` | 期間全体の成長率と年平均成長率 |
| Cumulative GDP | `cumulative_gdp` | 1〜T 年の GDP の合計 |
| Final Living Standard | `final_living_standard` | 最終年の生活水準 |
| Average Living Standard | `average_living_standard` | 期間中の平均 |
| Investment Efficiency | `investment_efficiency` | （指標の改善量）÷（総投資額）。遅延でまだ届いていない投資・減耗・人口増加の影響も含む単純な比率なので、解釈に注意 |
| Optimization Gap | `optimization_gap` | 全探索の最良値 − その値（絶対値と相対値） |
| Computational Cost | `computational_cost` | 実行時間・評価回数・反復回数 |

分母が 0 になる場合（初期 GDP が 0、投資額が 0、期間が 0 年）は `None` を返します。

## 25. モデルの限界

- 本教材は、**教育用の架空モデル**です。
- **現実の国家の GDP や経済成長率を予測しません。**
- **投資効果の係数は架空の値**です（効率・遅延・減耗率・弾力性・重み）。
- 投資配分と経済成長の関係は、**モデルの仮定に依存します**（生産関数の形、収穫逓減、遅延、予算一定など）。
- **GDP の最大化は、必ずしも社会的厚生の最大化を意味しません。**
- **生活水準指標は、人工的な評価指標です。**重みはモデル上の選択です。
- **教育・医療などの社会的価値を、GDP だけで評価しません。**
- **実際の政策判断に直接使わないでください。**
- 公開統計を使う場合は、**出典を明記**してください。
- **相関関係と因果関係を区別してください。**
- **最適解は、目的関数・制約条件・モデルの仮定によって変わります。**
- このモデルにないもの：
  - 税・財政赤字・民間投資・貿易・物価・失業
  - 分野間の相互作用（例：健康が教育の効果を高める）
  - 地域や所得の分布（格差）
  - 政治的・制度的な制約

## 26. GitHub を用いたチーム開発

- Issue で作業を分け、ブランチと Pull Request で統合します。
  - 例：「経済モデルの改良」「Greedy 法」「局所探索」「感度分析」「発表」
- `.py` を変えたら `python3 -m unittest discover -s tests -v` がすべて成功することを確かめてから、Pull Request を作ります。
- Notebook は**出力を消してから**コミットすると、差分が見やすくなります。
- **`textbook/` を公開リポジトリに push しないでください**（28 章）。
  - 非公開リポジトリを使う。
  - または、`.gitignore` に `textbook/` を追加し、各自が教科書のサンプルからコピーする。
- アクセストークンやパスワードを、コードや Notebook に書かないでください。

## 27. 成果物と提出方法

1. **コード**：変更・追加した `.py` と、すべて成功する unittest（新しい関数にはテストを追加する）。
2. **Notebook**：実験に使った 01〜05（または追加の Notebook）と、研究発表用の 06。
3. **研究発表**：Notebook 06、またはそこから作ったスライド。次の内容を含めます。
   - RQ と、実験前に立てた仮説
   - モデルと仮定
   - 実験条件（目的関数・評価期間・刻み・パラメータ）
   - 結果、考察、モデルの限界
   - 結論（仮定とともに）、今後の課題
4. **Advanced Research**：選んだ課題（A〜G）の実装と結果。

提出方法（リポジトリの URL・提出期限など）は、授業の指示に従ってください。

## 28. 参考文献・著作権上の注意

- 柴田望洋『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』SB クリエイティブ
  - 第 2 章 最大値、第 3 章 線形探索、第 4 章 キュー、第 5 章 再帰、第 6 章 ソート
- データ：`data/baseline_economy.json`、`data/investment_scenarios.json`（**この教材のための架空のデータ**。現実の国家統計ではありません）
- 経済成長モデルについて：本教材の生産関数（Cobb-Douglas 型）・収穫逓減・減耗の考え方は、経済学の入門的な成長モデルの考え方を、教育用に大幅に単純化したものです。特定の研究や統計に基づく係数ではありません。

### 著作権上の注意

- `textbook/` の 4 本は、上記の教科書のサンプルコードを**改変せずに**コピーしたものです。原本との SHA-256 の一致を確認しています。
- **公開再配布の条件は確認できていません。**`textbook/` を含むリポジトリを、公開 GitHub に push しないでください。
- 公開統計（Advanced G）を使う場合は、各機関の利用条件に従い、出典・対象年・単位・定義を明記してください。

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
| `chap04/fixed_queue.py` | `g1-economic-growth-optimization/textbook/fixed_queue.py` | `economic_model.py` |
| `chap06/insertion_sort.py` | `g1-economic-growth-optimization/textbook/insertion_sort.py` | `optimization.py` |
| `chap02/max.py` | `g1-economic-growth-optimization/textbook/max.py` | `optimization.py` |
| `chap03/ssearch_while.py` | `g1-economic-growth-optimization/textbook/ssearch_while.py` | `optimization.py` |

### 3. 配置後のディレクトリ構成

```text
g1-economic-growth-optimization/
└── textbook/
    ├── __init__.py          （リポジトリに含まれる）
    ├── fixed_queue.py       （各自で配置）
    ├── insertion_sort.py    （各自で配置）
    ├── max.py               （各自で配置）
    └── ssearch_while.py     （各自で配置）
```

### 4. コピーと確認のコマンド例

```bash
cd g1-economic-growth-optimization
SRC="<展開したフォルダ>"        # 各自の環境に合わせる

cp -i "$SRC/chap04/fixed_queue.py" textbook/fixed_queue.py
cp -i "$SRC/chap06/insertion_sort.py" textbook/insertion_sort.py
cp -i "$SRC/chap02/max.py" textbook/max.py
cp -i "$SRC/chap03/ssearch_while.py" textbook/ssearch_while.py

# 原本とコピーの SHA-256 が一致することを確認する
sha256sum "$SRC/chap04/fixed_queue.py" textbook/fixed_queue.py
sha256sum "$SRC/chap06/insertion_sort.py" textbook/insertion_sort.py
sha256sum "$SRC/chap02/max.py" textbook/max.py
sha256sum "$SRC/chap03/ssearch_while.py" textbook/ssearch_while.py

python3 starter.py                          # 実行確認
python3 -m unittest discover -s tests -v    # テスト
```

配置した教科書のコードは、リポジトリ直下の `.gitignore` によって Git の追跡対象から除外されます（`git status` に表示されなければ正常です）。
`git add -f` などで教科書のコードを commit・push しないでください。
