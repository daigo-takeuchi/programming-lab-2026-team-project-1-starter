# F3：出会いとマッチングのアルゴリズム

> ⚠️ **最初に読んでください**
> - この教材は**教育用の架空シミュレーション**です。参加者・希望条件・関係継続モデルの係数はすべて**架空**です。
> - **実際の結婚成立率や離婚率を予測するものではありません。** 実在する人物の結婚適性や離婚リスクを評価するものでもありません。
> - **Group A・Group B はアルゴリズム上の区分**であり、性別や性的指向を意味しません。
> - Gale–Shapley 法の「安定（Blocking pair がない）」は数学的な性質で、**関係が長続きすることを保証しません**（7章・9章）。
> - `textbook/` 内のコードは第三者の著作物です。再配布の可否は未確認のため、このディレクトリは**ローカルの教材用**です（25章）。

---

## 1. 研究テーマと目的

**F3：出会いとマッチングのアルゴリズム**（チーム課題 F「自由研究：身近な問題・社会の仕組みをアルゴリズムで考える」）

架空の参加者の希望条件や選択戦略を設定し、異なるマッチングアルゴリズムによる**成立率・初期満足度・数学的安定性**を比較します。さらに、成立したペアについて時間経過に伴う関係継続・関係解消を**教育用の架空モデル**でシミュレーションし、**マッチング成立時点の評価と、長期的な関係継続可能性を統合的に分析**します。

### 3 つの段階

| 段階 | 内容 | 評価指標 | モジュール |
| --- | --- | --- | --- |
| **Stage 1：Matching Formation** | 参加者の属性・希望条件 → 希望順位 → 相互承諾 → Random / Greedy / Gale–Shapley | 成立数・成立率・初期満足度・Blocking pair 数・計算時間 | `participants.py`・`preferences.py`・`matching_algorithms.py`・`evaluation.py` |
| **Stage 2：Relationship Continuation** | 成立したペアに、年次関係解消確率による簡易時系列モデルを適用 | 5・10・20 年継続率、継続期間の分布 | `relationship_stability.py` |
| **Stage 3：Integrated Evaluation** | Stage 1 と Stage 2 を統合 | 成立率、長期継続率、長期成立率、初期満足度、Blocking pair、公平性、モデル仮定への感度 | `evaluation.py`・`experiments.py`・Notebook 05 |

### Research Questions

| | 問い |
| --- | --- |
| RQ1 | **マッチングアルゴリズムによって成立率は変わるか**（Random、Greedy、Gale–Shapley） |
| RQ2 | **希望条件の厳しさは成立率と初期満足度にどう影響するか**（閾値、候補者数、希望順位） |
| RQ3 | **アルゴリズムによって成立したペアの初期適合度は変わるか**（成立率が高いアルゴリズムが、適合度の高いペアを作るとは限らない） |
| RQ4 | **初期適合度と長期的な関係継続率には、モデル上どのような関係があるか**（※ この関係は**モデルの仮定**で定義したもので、実際の婚姻関係の因果関係を実証したものではない） |
| RQ5 | **成立率を最大化するアルゴリズムは、長期成立率も最大化するか**（成立時点と 10 年後の評価を比べる） |
| RQ6 | **Gale–Shapley 法の数学的安定性は、長期的な関係継続を保証するか**（2 つの概念をシミュレーションで区別する） |

### 構成：計算は `.py`、実験・可視化・発表は `.ipynb`

| | 担当 | 必要なもの |
| --- | --- | --- |
| `.py`（Core） | 計算ロジック、データ、テスト、テキストのデモ | **Python 3 の標準ライブラリのみ** |
| `notebooks/*.ipynb` | 実験・グラフ・研究発表（`.py` を import して使う） | matplotlib・numpy・pandas（Google Colab に標準で入っている。CPU ランタイムで十分） |

- **Core Research（必須課題）**：二部マッチング、3 つのアルゴリズム、一定ハザードの簡易な関係継続モデル（19章）
- **Advanced Research（発展課題）**：満足度の時間変化、ストレスイベント、確率モデルの拡張、再マッチング、多目的最適化、F4 との連携（20章）

## 2. 出会いとマッチングの問題

この教材では、**二部マッチング**のモデルを使います。

- 参加者は **Group A** と **Group B** に分かれ、**相手のグループの人とだけ**マッチングします（A・B はアルゴリズム上の区分で、性別や性的指向を意味しません）。
- 各参加者は**最大 1 人**とマッチングします。
- **双方が相手を受け入れ可能**と判断した場合だけ成立します（相互承諾）。
- 未マッチングの参加者がいても構いません。
- Core では、一度成立したペアについて、シミュレーション期間中の**再マッチングは行いません**（Advanced D）。

初期データ（`data/sample_participants.json`）は Group A・B 各 5 人の架空の参加者で、次のケースを含みます。

| ケース | 例（サンプルデータ） |
| --- | --- |
| 相互に第 1 希望のペア | A1 と B1 |
| 複数人が同じ候補を希望する | A2・A3 の両方が B2 を第 1 希望にする（B2 は A3 を好む） |
| 希望条件が厳しく成立しない | A5（min_score = 0.85 で、受け入れ可能な相手がいない） |
| Greedy と Gale–Shapley で結果が異なる | Greedy：A2–B2・A3–B3、Gale–Shapley：A3–B2・A2–B3 |
| 初期適合度の高いペアと低いペア | A3–B2（0.92）、A1–B1（0.91） ／ A4–B2（0.48）、A1–B5（0.52） |

## 3. 希望条件と希望順位

`participants.py`・`preferences.py`

各参加者は `id`・`group`・`age`・`interests`（趣味タグ）・`lifestyle`（生活スタイル、各 0〜1）・`values`（価値観、各 0〜1）・`preferences`（希望条件）・`acceptable_candidates`（会ってみてもよい相手）を持ちます。読み込み時に、ID の重複、グループ、候補者の存在、同じグループの候補、重複などを検証します。

### 希望スコア（Compatibility Score）

```text
Compatibility Score(p → q)
= w1 × Interest Similarity + w2 × Lifestyle Similarity + w3 × Value Similarity + w4 × Age Compatibility
```

| 項目（0〜1） | 計算 |
| --- | --- |
| Interest Similarity | 趣味タグの Jaccard 係数（共通のタグ数 ÷ どちらかが持つタグ数） |
| Lifestyle / Value Similarity | 共通の項目について 1 − \|差\| の平均 |
| Age Compatibility | 相手の年齢が希望範囲内なら 1、範囲から d 歳離れると 1 − d/10（0 未満は 0） |

- 重み w1〜w4 は**その人自身の希望条件**（0 以上、合計 1）。p から見た q と、q から見た p でスコアは異なります。
- **受け入れ可能** = `acceptable_candidates` にいて、かつ **スコア ≥ `min_score`**（希望条件の厳しさ）。
- **希望順位** = 受け入れ可能な相手をスコアの高い順に並べたもの。**同点は ID の昇順**（決定的な規則）。厳密な順位になります。
- **相互承諾可能** = 双方が相手を受け入れ可能。
- **ペアの初期適合度** = 2 方向の希望スコアの平均（関係継続モデルで使う）。

> 希望スコアは**教育用の人工的な指標**であり、実際の結婚適性を表すものではありません。

## 4. Random Matching

相互承諾可能な組をすべて列挙し、**乱数シード**で並べ替えて、先頭から「2 人とも空いていれば成立」させます（`random_matching(rankings, a_ids, b_ids, seed)`）。

- 1 人が複数人とマッチングすることはありません。結果は**極大マッチング**（これ以上組を足せない）になります。
- 「すべてのマッチングから一様に 1 つ選ぶ」方法ではないことに注意してください。
- シードで結果が変わるので、**複数のシードで平均**して比べます。

## 5. Greedy Matching

Group A の参加者を**順番に**処理し、各参加者について、相互承諾可能で未マッチングの候補者のうち**希望順位が最も高い相手**と成立させます。**一度成立したペアは変更しません**（`greedy_matching`）。

- 希望順位のリストを先頭から調べ、最初に条件を満たす相手を、教科書の**線形探索**（`seq_search`）で見つけます。
- **処理順序**によって結果が変わります（先に処理された人が有利）。`greedy_order(a_ids, seed)` で処理順序を変えて実験できます。

## 6. Gale–Shapley Matching

**受け入れ保留方式（Deferred Acceptance Algorithm）**です（`gale_shapley`、Group A が提案）。

1. 相手のいない提案者を**キュー**に入れる（教科書の `FixedQueue`）。
2. キューから 1 人取り出し、まだ提案していない相手のうち希望順位が最も高い人に**提案**する（**受け入れ可能な相手にだけ**、**同じ相手には高々 1 回**）。
3. 受け手は、仮の相手がいなければ**仮に受け入れ**る。いれば、**順位辞書**（ハッシュ表、平均 O(1)）で現在の相手と新しい提案者を比べ、好む方を残して、もう一方を**拒否**する。
4. 拒否された人は、まだ提案できる相手がいれば**キューに戻り再提案**する。
5. キューが空になったら終了。

- `gale_shapley(..., record=True)` で、各ステップ（提案・受け入れ・入れ替え・拒否・仮マッチング）を記録できます（Notebook 03）。
- 提案側（Group A）にとって、すべての安定マッチングの中で最良の結果になります（**提案側最適**）。Group B が提案する版（`swap_sides`）と比べると、公平性を考えられます。

**3 つのアルゴリズムは、同じ参加者データ・同じ希望順位・同じ受け入れ可能性を使って比較します。**

## 7. 数学的な安定性

マッチングが**安定（stable）**であるとは、**Blocking pair が 1 つもない**ことです。Gale–Shapley 法は、必ず安定マッチングを出力します（Gale & Shapley, 1962）。

> **数学的な安定性は、マッチングを作った「時点」の、希望順位についての性質です。** 成立した関係がその後「長続きする」かどうか（関係継続の安定性、9章）とは**別の概念**です。同じ「安定」という言葉でも意味が違うので、報告では区別してください（RQ6）。

## 8. Blocking Pair

**Blocking pair** = 次の条件をすべて満たす 2 人 (a, b)：

- a と b は**相互に受け入れ可能**で、今は**ペアではない**
- a は b を**今の相手より好む**（a が未マッチングなら、受け入れ可能な相手との成立を未マッチングより好むものとする）
- b も a を同様に**今の相手より好む**

`evaluation.blocking_pairs` で列挙します（O(N²)。順位の比較は辞書で O(1)）。サンプルデータでは、Greedy に 1 つ（A3–B2）、Gale–Shapley に 0 です。

## 9. 関係継続の安定性

`relationship_stability.py`（本改訂で追加した中心のモジュール）

Stage 1 で成立したペアについて、関係が時間とともに続くかを、**毎年一定の確率で関係を解消する簡単な離散時間モデル**でシミュレーションします。

| パラメータ（0〜1） | 意味（すべて架空） |
| --- | --- |
| `initial_compatibility` | 初期適合度（ペアの 2 方向の希望スコアの平均） |
| `value_similarity`・`lifestyle_similarity` | 価値観・生活スタイルの一致度。**初期適合度にすでに含まれている**ので、Core の解消確率には別に加えない（二重に数えない） |
| `conflict_resolution` | 葛藤対処能力を表す**架空の指標**。Core では全ペア共通の値（`default_conflict_resolution`）。**実在の人物について推定しない** |
| `annual_stress` | 年次ストレス（架空）。Core では毎年一定 |
| `baseline_hazard` | 基準となる年次関係解消確率（架空） |

Core では、**初期適合度・葛藤対処能力・年次ストレスを独立した説明要素**として扱います。

## 10. 年次関係解消確率

```text
Annual Dissolution Probability
= clip(baseline_hazard − alpha × initial_compatibility − beta × conflict_resolution + gamma × annual_stress, 0, 1)
```

- `clip(x, 0, 1)` は、確率を 0〜1 に制限する操作です。係数を大きくしすぎると式の値が負になり 0 に制限されます（継続率 100%）。
- 係数（`data/relationship_parameters.json`）：

| 名前 | 値 | 意味 |
| --- | --- | --- |
| `baseline_hazard` | 0.08 | 基準の年次解消確率 |
| `alpha` | 0.04 | 初期適合度が 1 高いと、解消確率が 0.04 下がる |
| `beta` | 0.02 | 葛藤対処が 1 高いと、0.02 下がる |
| `gamma` | 0.03 | ストレスが 1 高いと、0.03 上がる |
| `default_annual_stress` | 0.3 | 年次ストレス |
| `default_conflict_resolution` | 0.5 | 葛藤対処（全ペア共通。作業指示のパラメータに追加した項目） |
| `simulation_years` | 20 | 観測期間（年） |
| `random_seed` | 42 | 乱数シード |

> **これらの数値は完全に架空のもので、現実の離婚率・関係解消率を表していません。係数は教育用の仮定で、実証された因果効果ではありません。** 学生が各係数を変えて感度分析できるようにしています（`rs.with_changes(params, alpha=...)`）。

この設定では、初期適合度 0.5 で年次解消確率 0.059（理論上の 10 年継続確率 54.4%）、0.9 で 0.043（64.4%）です。

## 11. 関係継続シミュレーション

- 各年 t = 1, 2, …, T について 0〜1 の一様乱数 u を生成し、**u < p ならその年に関係解消**と判定します。
- **一度解消したペアは、再び継続状態に戻しません**（Core）。
- **観測期間の終わりまで解消しなかったペア**は「観測期間内に関係解消が発生しなかった」（**打ち切り＝censored**）として扱い、その後いつ解消するかは推測しません。観測期間より後の継続状態は「不明（None）」です。
- 各ペアについて、Pair ID、マッチングアルゴリズム、初期適合度、初期満足度、年次解消確率、継続年数、解消の有無、解消年、5・10・20 年時点の継続状態、打ち切りの有無を記録します（`simulate_pairs`）。
- **乱数シード**を指定でき、同じシードなら同じ結果になります。
- **共通乱数**：乱数の生成器を「シード・反復番号・ペアの 2 人の ID」から作るので、**同じペア・同じ年・同じ反復**なら、どのアルゴリズムで成立しても**同じ乱数**を使います。**違うペアの乱数は独立**です。アルゴリズム間の差が「どんなペアを作ったか」によるのか、乱数の偶然によるのかを区別しやすくなります。
- **確率計算の検証**：解消確率が一定 p のとき、T 年後の理論的な継続確率は **(1 − p)^T** です。多数（4,000 組）のシミュレーションがこの理論値に近づくことを unittest で確認しています。

## 12. 成立率と長期成立率

`evaluation.py`

| 指標 | 定義 |
| --- | --- |
| Matching Rate（成立率） | 2 × 成立ペア数 / 全参加者数 |
| Initial Satisfaction（初期満足度） | 受け入れ可能な相手が L 人いて、k 番目の相手とマッチング → 1 − (k − 1)/L（第 1 希望 = 1）。**未マッチングは 0**（受け入れ可能な相手がいない人も 0）。平均は**全参加者**で取る（マッチングした人だけの平均も別に出す） |
| Blocking Pair Count | 8章 |
| Continuation Rate(T)（継続率） | T 年後も継続しているペア数 / 最初に成立したペア数。**成立ペアが 0 組なら未定義（None）**で、0% とは断定しない |
| Long-term Matching Rate(T)（長期成立率） | 2 × T 年後も継続しているペア数 / 全参加者数（＝ 成立率 × 継続率） |
| 継続期間 | 解消したペアと、観測終了まで継続したペア（打ち切り）を**区別**して数える。平均は「観測期間内に継続した年数」（打ち切りのペアは観測期間の長さ）と「解消したペアだけの継続年数」を分けて出す |

**単一の乱数シードの結果から優劣を断定しないでください。** Random はマッチング自体が乱数で変わるので複数シードで、関係継続は複数の反復で平均します（`compare_algorithms`）。

## 13. 公平性

長期継続率だけで公平性を判断しないでください。`satisfaction_summary` で次を比べます。

- Group A の平均初期満足度と Group B の平均初期満足度
- 最低初期満足度（全員、マッチングした人だけ）
- 希望順位の分布（第何希望の相手とマッチングしたかの人数）
- 未マッチング率（グループ別）

Gale–Shapley は**提案側に有利**です。Greedy は**処理順序の早い人に有利**です。

## 14. アルゴリズムと計算量

N = 各グループの参加者数、P = 成立ペア数、T = 観測年数、M = 反復回数、K = パラメータ条件数とします。

| 処理 | 計算量 | 説明 |
| --- | --- | --- |
| 希望スコアの計算（前処理） | O(N²) | すべての組 × 2 方向（`score_table`） |
| 希望順位の生成（前処理） | O(N³)（この実装） | 各人 N 人を挿入ソート O(N²) × 2N 人。比較ソートなら各人 O(N log N) で全体 O(N² log N) |
| 順位辞書の作成（前処理） | O(N²) | 全員の希望順位を辞書に |
| Random Matching | 実装方法によって異なる。この実装は O(N²) | 相互承諾可能な組の列挙とシャッフル |
| Greedy Matching | 単純実装では O(N²) 程度 | 各人について希望順位を線形探索（この実装は相互承諾の確認に `in` を使うので、最悪 O(N³)） |
| Gale–Shapley | 提案回数 O(N²) | 各提案者は同じ相手に高々 1 回。受け手の比較は順位辞書で O(1) |
| Blocking pair の検出 | 単純実装では O(N²) | すべての組 × O(1) の比較 |
| 関係継続シミュレーション | O(PT) | P 組 × T 年 |
| モンテカルロ反復 | O(MPT) | M 回 |
| パラメータ探索 | O(KMPT) | K 条件 |

前処理（希望スコア・希望順位・順位辞書）は、どのアルゴリズムでも共通に 1 回だけ計算します。**理論計算量と実測時間は別のもの**です。この教材の規模（N = 5）ではどれも一瞬で終わります（`evaluation.time_algorithm` で計測できます）。参加者を増やす（TODO）と違いが見えてきます。

## 15. 教科書との関連

教科書：柴田望洋『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』

### 実際に使用したコード（`textbook/`、改変せずにコピー）

| ファイル | 原本 | クラス・関数 | 用途 | SHA-256（原本と一致を確認） |
| --- | --- | --- | --- | --- |
| `textbook/ssearch_while.py` | `chap03/ssearch_while.py` | `seq_search` | Greedy で、希望順に見て**最初に条件を満たす候補**（空いていて相互承諾可能）を探す | `6a11e6b6…806ea` |
| `textbook/insertion_sort.py` | `chap06/insertion_sort.py` | `insertion_sort` | **希望順位の生成**（(−スコア, ID) を安定に並べる。同点は ID 順） | `b90b8e07…d69e` |
| `textbook/fixed_queue.py` | `chap04/fixed_queue.py` | `FixedQueue` | Gale–Shapley の**提案順序の管理**（相手のいない提案者のキュー） | `3a2efeda…db23e7b21` |

- `preferences.py`・`matching_algorithms.py` から**直接 import** しています。`ssearch_while.py`・`insertion_sort.py` の対話入力は `if __name__ == '__main__':` の中にあり、`fixed_queue.py` はクラスの定義だけなので、import しても入力待ちになりません。Adapter やラッパーは作っていません。
- 完全な SHA-256 は `sha256sum textbook/*.py` で確認できます（改行コードも原本どおり CRLF）。**編集しないでください。**

### 参考にしただけのコード（コピーしていません）

| ファイル | 内容 | 使わなかった理由 |
| --- | --- | --- |
| `chap03/chained_hash.py`・`open_hash.py` | ハッシュ法（チェイン法・オープンアドレス法） | 受け手の**順位辞書**には Python の `dict`（ハッシュ表）を使った。教科書のハッシュ法は、`dict` がなぜ平均 O(1) で検索できるかの説明に使う |
| `chap03/bsearch.py` | 二分探索 | 希望順位はスコア順のリストで、ID で検索するには辞書の方が適している（順位辞書） |
| `chap06/selection_sort.py` | 単純選択ソート | **安定でない**。同点を ID 順にする規則を (−スコア, ID) の組で表しているので結果は同じになるが、安定な挿入ソートを選んだ |
| `chap04/queue.py` | `collections.deque` を使うキュー | どちらでもよい。固定長の配列でキューのしくみ（先頭・末尾のカーソル、リングバッファ）が見える `FixedQueue` を使った |
| `chap02/max.py` | 最大値（`max_of`） | 希望順位をスコア順に一度並べておけば、「最適候補」は先頭からの線形探索で見つかる（毎回最大値を探さなくてよい） |

### アルゴリズムと教科書の対応

| 処理 | アルゴリズム・データ構造 | この教材 |
| --- | --- | --- |
| 希望条件を満たす候補者の探索 | **線形探索** | Greedy：希望順位を先頭から調べ、最初に「空いていて相互承諾可能」な相手を `seq_search` で探す。受け入れ可能な相手の判定もリストを順に調べる |
| 希望順位の生成 | **ソート** | (−スコア, ID) を `insertion_sort` で並べる（安定、同点は ID 順） |
| 提案順序の管理 | **キュー** | Gale–Shapley：相手のいない提案者を `FixedQueue` に入れ、先に入った人から提案する。拒否されたらキューの末尾に戻る |
| 希望順位の高速検索 | **辞書・ハッシュ** | 受け手の順位辞書 `{相手の ID: 順位}`（`rank_index`）。「A と B のどちらを好むか」を平均 O(1) で比べる。リストの `index` なら O(N) |
| 最適候補の選択 | **最大値探索** | 希望スコアが最大の相手が第 1 希望。一度ソートしておけば、最大値の探索を繰り返さずに済む（ソートと線形探索の組合せ） |
| 長期継続率の計算 | **ループと配列** | 年ごとのループで継続・解消を判定し、各年の継続率を配列（`survival_curve`）に入れる |
| パラメータ比較 | **全探索** | 係数・ストレス・希望条件の候補をすべて試す（Experiment E、Notebook 05） |

## 16. ファイル構成

```text
f3-matching-algorithms/
├── README.md
├── .gitignore
├── requirements-notebook.txt   Notebook 用のライブラリ（Core は不要）
├── starter.py                  一連のデモ（読み込み → スコア → 順位 → 3 つのマッチング → 評価 → 関係継続 → 比較 → TODO）
├── participants.py             参加者モデル、読み込みと検証
├── preferences.py              希望スコア、希望順位、相互承諾、初期適合度
├── matching_algorithms.py      Random・Greedy・Gale–Shapley
├── relationship_stability.py   関係継続モデル（架空）、シミュレーション、F4 への受け渡し
├── evaluation.py               成立率・満足度・Blocking pair・継続率・長期成立率・公平性・統合比較
├── experiments.py              学生向け研究実験 Experiment A〜F の入口
├── matching_charts.py          Notebook 用のグラフ（matplotlib。計算は上の .py に任せる）
├── data/
│   ├── sample_participants.json      架空の参加者（Group A・B 各 5 人）
│   └── relationship_parameters.json  関係継続モデルの架空のパラメータ
├── notebooks/
│   ├── README.md
│   ├── 01_preferences_and_matching.ipynb
│   ├── 02_random_vs_greedy.ipynb
│   ├── 03_stable_matching.ipynb
│   ├── 04_relationship_continuation.ipynb
│   ├── 05_integrated_comparison.ipynb
│   └── 06_research_presentation.ipynb
├── textbook/                   教科書のサンプルコード（編集しない）
│   ├── __init__.py
│   ├── ssearch_while.py
│   ├── insertion_sort.py
│   └── fixed_queue.py
└── tests/
    ├── test_participants.py
    ├── test_preferences.py
    ├── test_matching_algorithms.py
    ├── test_relationship_stability.py
    ├── test_evaluation.py
    └── test_matching_charts.py   グラフが描けるか（matplotlib がなければスキップ）
```

作業指示の構成に、Notebook のグラフを 1 か所にまとめる `matching_charts.py` とそのテストを加えています（6 つの Notebook で同じグラフのコードを重複させないため）。

## 17. Python プログラムの実行方法

このディレクトリで実行してください。**Python 3 の標準ライブラリだけ**で動きます。

```bash
python3 starter.py
python3 -m unittest discover -s tests -v
python3 experiments.py          # Experiment A〜F（python3 experiments.py C のように指定も可）
```

`starter.py` の実行結果（抜粋。架空データ・架空モデル。Random は 20 シードの平均、継続率は 200 回の反復の平均）：

```text
Algorithm      Match Rate  Satisfaction  Blocking Pairs  Compat.  5Y Cont.  10Y Continuation  20Y Cont.  10Y Long-term Match
Random                80%          0.48            6.15     0.63     75.9%             57.3%      33.8%                45.9%
Greedy                80%          0.74            1.00     0.84     79.8%             62.9%      41.1%                50.3%
Gale-Shapley          80%          0.78            0.00     0.87     78.5%             62.5%      41.1%                50.0%
```

（この数値は、この架空のモデルとパラメータ・シード・反復回数での計算結果です。現実の予測ではありません。また、Greedy と Gale–Shapley の差は反復のばらつきと同程度の大きさなので、この表だけから優劣は判断できません。）

## 18. Google Colab Notebook の実行方法

Notebook の詳細は [`notebooks/README.md`](notebooks/README.md) を参照してください。Colab の **CPU ランタイム**で動きます（GPU・TPU は不要）。

### 実行順序

01（希望条件）→ 02（Random・Greedy）→ 03（Gale–Shapley）→ 04（関係継続）→ 05（統合比較）→ 06（研究発表）

### 方法A：GitHub から clone

チームの F3 リポジトリを GitHub に用意し、各 Notebook の最初の「準備」セルの `REPO_URL` に**自分たちのリポジトリの URL** を入れて実行します（この教材には URL を書いていません）。セルが `git clone` し、F3 のフォルダを**作業ディレクトリ**に設定して `.py` を **import** します。**教科書コード（`textbook/`）は公開リポジトリに含めないでください。** `textbook/` がないと import が失敗するので、その場合は方法B を使ってください。

### 方法B：ZIP をアップロードして展開

F3 フォルダを ZIP にして Colab の `/content` にアップロードし、「準備」セルを実行します。ZIP を展開し、`matching_algorithms.py` のあるフォルダを作業ディレクトリにして、`.py` を import します。

### ローカル

```bash
pip install -r requirements-notebook.txt
jupyter notebook notebooks/          # または JupyterLab、VSCode
```

Notebook に WSL の絶対パスは書いていません。計算ロジックは `.py` を import して使い、Notebook の中に重複して実装していません。

## 19. Core Research

すべてのチームが取り組む課題です。

| # | 課題 | 使うもの |
| --- | --- | --- |
| 1 | 参加者データを読み込む | `participants.load_participants` |
| 2 | 希望スコアを計算する | `preferences.score_table`、Notebook 01 |
| 3 | 希望順位を生成する | `preferences.build_rankings` |
| 4 | 3 種類のマッチングを実行する | `matching_algorithms.run`、Notebook 02・03 |
| 5 | 成立率を計算する | `evaluation.matching_rate` |
| 6 | 初期満足度を計算する | `evaluation.satisfaction_summary` |
| 7 | Blocking pair を検出する | `evaluation.blocking_pairs`、Notebook 03 |
| 8 | 成立ペアの初期適合度を計算する | `preferences.pair_compatibility`、Experiment B |
| 9 | 簡易的な関係継続シミュレーションを実行する | `relationship_stability.simulate_pairs`、Notebook 04 |
| 10 | 5 年・10 年・20 年継続率を計算する | `evaluation.continuation_rate` |
| 11 | 10 年長期成立率を計算する | `evaluation.long_term_matching_rate` |
| 12 | 複数シードで比較する | `evaluation.compare_algorithms`、Notebook 02・05 |
| 13 | 感度分析を行う | Experiment E・F、Notebook 05 |
| 14 | 結果をグラフにまとめる | Notebook 01〜05、`matching_charts.py` |
| 15 | モデルの限界を考察する | 22章、Notebook 06 |

### 研究実験（`experiments.py`）

| 実験 | 内容 | 関連 RQ |
| --- | --- | --- |
| Experiment A：成立率 | 3 つのアルゴリズムの成立率・満足度。希望条件（min_score）を厳しくした場合 | RQ1・RQ2 |
| Experiment B：初期適合度 | 各アルゴリズムが作ったペアの初期適合度の分布 | RQ3 |
| Experiment C：10 年継続率 | 同じ関係継続モデルを適用して比べる | RQ4 |
| Experiment D：長期成立率 | 成立率 × 継続率で比べる | RQ5 |
| Experiment E：感度分析 | alpha・baseline_hazard・gamma・beta・年次ストレスを変える | RQ4・RQ5 |
| Experiment F：仮定の変更 | 初期適合度と解消確率が**無関係**なモデル（alpha = 0）を対照条件にする | RQ4〜RQ6 |

**比較の公平性**：参加者集合、希望順位、受け入れ可能性、関係継続モデルの係数、観測期間、試行回数をそろえます。Random は複数シード、関係継続は複数反復で平均し、共通乱数を使います。

## 20. Advanced Research

Core Research を終えたチームが取り組む課題です。**Advanced A〜F のうち 1 つ以上を選択**してください。すべてを実装する必要はありません。

### Advanced A：時間とともに変化する関係満足度

関係満足度を**時間変化する状態変数**としてモデル化します（例：毎年、初期適合度・ストレス・乱数で満足度が上下し、満足度が低いほど解消確率が高い）。

### Advanced B：ストレスイベント

転職、転居、家計の変動などの**架空のイベント**を、確率的に発生させ、その年のストレスを高めます。イベントの発生確率・影響の大きさは仮定であることを明記します。

### Advanced C：関係継続の確率モデル

**ロジスティック関数**（`p = 1 / (1 + exp(−(b0 + b1·x1 + …)))`、clip が不要になる）や、年数によって解消確率が変わる**離散時間ハザードモデル**へ拡張します。

### Advanced D：再マッチング

関係解消後に、未マッチングの参加者・解消したペアの参加者で、**新しい相手とのマッチング**を試みるモデルを検討します（何年ごとにマッチングを行うか、過去の相手をどう扱うか）。

### Advanced E：多目的最適化

成立率・初期満足度・長期成立率・公平性・計算時間を**同時に評価**します（重み付き和、パレート最適、制約付き最適化）。どの指標を重視するかで「良いアルゴリズム」が変わることを示します。

### Advanced F：F4 との連携

F4「パートナー関係の安定性シミュレーション」と連携します。F4 では、関係満足度の動態、相互作用、ストレスイベント、関係解消などを詳細に扱えるようにします。**今回 F4 のコードは作成・変更していません。**

F3 から F4 へ渡すデータ形式（`relationship_stability.export_pairs_for_f4` が作る辞書。`json.dump` でそのまま保存できる）：

```json
{
  "format": "f3-to-f4/1",
  "note": "F3 の教育用の架空データ。実在の人物・実際の関係を表すものではない",
  "relationship_parameters": {
    "baseline_hazard": 0.08, "alpha": 0.04, "beta": 0.02, "gamma": 0.03,
    "default_annual_stress": 0.3, "default_conflict_resolution": 0.5,
    "simulation_years": 20, "random_seed": 42
  },
  "pairs": [
    {
      "pair_id": "A1-B1",
      "participant_ids": ["A1", "B1"],
      "initial_compatibility": 0.91,
      "initial_satisfaction": 1.0,
      "matching_algorithm": "gale_shapley"
    }
  ]
}
```

| フィールド | 型 | 内容 |
| --- | --- | --- |
| `format` | 文字列 | 形式のバージョン（変更したら番号を上げる） |
| `relationship_parameters` | 辞書 | F3 の関係継続モデルのパラメータ |
| `pairs[].pair_id` | 文字列 | ペアの ID（`"A の ID-B の ID"`） |
| `pairs[].participant_ids` | 2 要素のリスト | [Group A の ID, Group B の ID] |
| `pairs[].initial_compatibility` | 数値（0〜1） | 初期適合度 |
| `pairs[].initial_satisfaction` | 数値（0〜1）または null | 2 人の初期満足度の平均 |
| `pairs[].matching_algorithm` | 文字列 | `"random"`・`"greedy"`・`"gale_shapley"` |

参加者の属性（趣味・価値観など）が必要なら、`data/sample_participants.json` を ID で参照する形を検討してください。

## 21. 実験条件と評価指標

### 記録すべき実験条件

- 参加者集合（人数・データファイル）、希望条件（重み・min_score・候補者数）
- アルゴリズム（Greedy の処理順序、Gale–Shapley の提案側）
- Random のシード（数）、関係継続の反復回数、乱数シード
- 関係継続モデルの係数（baseline_hazard・alpha・beta・gamma・ストレス・葛藤対処）と観測期間
- 対照条件（alpha = 0）を使ったか

### 評価指標

| 段階 | 指標 |
| --- | --- |
| Stage 1 | 成立数、成立率、初期満足度（全体・グループ別・最低）、Blocking pair 数、成立ペアの初期適合度、計算時間 |
| Stage 2 | 5・10・20 年継続率、継続率曲線、継続期間（解消・打ち切りを区別） |
| Stage 3 | 長期成立率、成立率との順位の比較、公平性、係数への感度、反復・シード間のばらつき（標準偏差） |

## 22. モデルの限界と倫理的配慮

- **本教材は教育用の架空シミュレーションです。**
- **実際の結婚成立率や離婚率を予測しません。**
- **関係継続確率の係数は架空のものです。** 初期適合度と関係継続の関係は**モデルの仮定**であり、実証された因果関係ではありません。
- **Blocking pair が存在しないことは、結婚後の安定性を保証しません。**
- **実際の個人情報を使用しません。** 架空の参加者のみを使います。
- **実在する人物の結婚適性や離婚リスクを評価しません。** 葛藤対処能力などの架空の特性を、実在の人物について推定しないでください。
- **性別、国籍、出身地などに基づく差別的な意思決定を推奨しません。** Group A・B は性別や性的指向を表しません。
- **関係解消を個人の失敗や劣等性として扱いません。**
- **関係の継続が常に望ましいとは限りません。** 関係を解消することが本人にとって良い選択である場合もあります。
- **本モデルは現実の人間関係を大幅に単純化しています。** 人の好みは変化し、相互作用し、数値化できない要素が多くあります。

## 23. GitHub を用いたチーム開発

- **役割分担を明確にする**：例）参加者・希望条件担当、アルゴリズム担当、関係継続モデル担当、評価・統合比較担当、Notebook・グラフ担当、発表・README 担当
- **GitHub Issues でタスク管理**：実装・実験・調査・不具合を Issue に登録し、担当者を割り当てる
- **branch を分けて実装**：例）`feature/b-proposing`、`experiment/strict-preferences`、`advanced/logistic-hazard`
- **Pull Request でコードレビュー**：テスト（`python3 -m unittest discover -s tests -v`）が通ることを確認してから merge する
- **Notebook の扱い**：出力を消してから commit する。計算の変更は `.py` で行い、テストを追加する
- **README への追記**：実験条件・結果・考察を README（または別の報告ファイル）に追記する
- **最終成果物の Release**：研究が完成したら Release（例：`v1.0`）を作る

（公開設定については冒頭の注意と 25章を参照。）

## 24. 成果物と提出方法

1. **コード**：変更・追加したモデル、実験、選択した Advanced の実装（テストが通ること）
2. **Notebook**：実験に使った Notebook（01〜05 と追加分）
3. **発表資料**：`notebooks/06_research_presentation.ipynb` の TODO を埋めたもの（またはそこから作った HTML スライド・保存した図を使ったスライド）
4. **報告**（README への追記、または別の報告ファイル）
   - Core Research 1〜15 の結果と考察
   - RQ1〜RQ6 に対するチームとしての答え（**どの仮定・どの条件の下での答えか**を明記）
   - 選択した Advanced Research のテーマ、方法、結果、考察
   - モデルの限界と倫理的配慮
5. **GitHub の記録**：Issue、branch、Pull Request、Release

提出方法（期限・提出先）は、授業で指示します。

## 25. 参考文献・著作権上の注意

### 教科書コード

- 出典：柴田望洋 著『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』SBクリエイティブ　第3章「探索」、第4章「スタックとキュー」、第6章「ソート」
- 使用ファイル：`textbook/ssearch_while.py`（原本 `chap03/ssearch_while.py`）、`textbook/insertion_sort.py`（原本 `chap06/insertion_sort.py`）、`textbook/fixed_queue.py`（原本 `chap04/fixed_queue.py`）
- 参考にしただけのファイル：15章の表を参照（コピーしていません）
- 教科書コードは第三者の著作物です。公開再配布の許諾はまだ確認していません。**GitHub で公開・配布する前に、再配布条件を必ず確認してください。GitHub へ push しないでください。**

### 架空データ

- `data/sample_participants.json`・`data/relationship_parameters.json` は、この教材のために作成した**架空のデータ**です。実在の人物・実際の結婚・離婚の統計を表すものではありません。

### 参考文献

- D. Gale, L. S. Shapley, "College Admissions and the Stability of Marriage", *The American Mathematical Monthly*, 69(1), 9–15, 1962.（受け入れ保留方式と安定マッチング）
- Python 標準ライブラリ `json`、`random`、`statistics`、`copy`、`time`、`unittest` のドキュメント
- matplotlib、numpy、pandas、Jupyter、nbconvert のドキュメント（Notebook）

研究で他の文献・統計・Web ページを使った場合は、出典と参照日を記録してください。

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
| `chap04/fixed_queue.py` | `f3-matching-algorithms/textbook/fixed_queue.py` | `matching_algorithms.py` |
| `chap06/insertion_sort.py` | `f3-matching-algorithms/textbook/insertion_sort.py` | `preferences.py` |
| `chap03/ssearch_while.py` | `f3-matching-algorithms/textbook/ssearch_while.py` | `matching_algorithms.py` |

### 3. 配置後のディレクトリ構成

```text
f3-matching-algorithms/
└── textbook/
    ├── __init__.py          （リポジトリに含まれる）
    ├── fixed_queue.py       （各自で配置）
    ├── insertion_sort.py    （各自で配置）
    └── ssearch_while.py     （各自で配置）
```

### 4. コピーと確認のコマンド例

```bash
cd f3-matching-algorithms
SRC="<展開したフォルダ>"        # 各自の環境に合わせる

cp -i "$SRC/chap04/fixed_queue.py" textbook/fixed_queue.py
cp -i "$SRC/chap06/insertion_sort.py" textbook/insertion_sort.py
cp -i "$SRC/chap03/ssearch_while.py" textbook/ssearch_while.py

# 原本とコピーの SHA-256 が一致することを確認する
sha256sum "$SRC/chap04/fixed_queue.py" textbook/fixed_queue.py
sha256sum "$SRC/chap06/insertion_sort.py" textbook/insertion_sort.py
sha256sum "$SRC/chap03/ssearch_while.py" textbook/ssearch_while.py

python3 starter.py                          # 実行確認
python3 -m unittest discover -s tests -v    # テスト
```

配置した教科書のコードは、リポジトリ直下の `.gitignore` によって Git の追跡対象から除外されます（`git status` に表示されなければ正常です）。
`git add -f` などで教科書のコードを commit・push しないでください。
