# F4：パートナーシップの安定性と意思決定

**家事分担・経済的負担・コミュニケーション・関係継続のシミュレーション（Python + Google Colab）**

チーム課題 F「自由研究：身近な問題・社会の仕組みをアルゴリズムで考える」の starter repository です。

> **この教材は、教育用の架空データ・架空モデルによるシミュレーションです。**
> - Partner A・B は実在の人物ではなく、性別や役割を意味しません。
> - 満足度関数や関係解消確率の係数は、すべて架空の値です。
> - 実際の離婚確率や、特定の関係の将来を予測するものではありません。
>
> 詳しくは「[23. モデルの限界と倫理的配慮](#23-モデルの限界と倫理的配慮)」を必ず読んでください。

---

## 1. 研究テーマと目的

家事分担、経済的負担、コミュニケーションなどの条件が、パートナー関係の**満足度・公平性・協力行動・長期的な関係継続**にどう影響するかを、Python のアルゴリズムでモデル化します。

F3「出会いとマッチングのアルゴリズム」では、成立したペアの長期継続を、外から与えた簡易的な確率で扱いました。F4 ではこのモデルを発展させ、**関係解消確率を、家事・お金・コミュニケーション・交渉・外部ストレスによって変化する「関係状態（満足度）」から毎年計算します**。

### Research Questions

| RQ | 問い | 比べる条件 |
| --- | --- | --- |
| RQ1 | 家事分担の公平性は、関係満足度にどう影響するか | 50:50、労働時間に応じる、所得に応じる、一方に集中、2 人の希望。**公平性の定義によって評価が変わること**も調べる |
| RQ2 | 経済的負担の分担方法は、満足度にどう影響するか | 50:50、所得比例、交渉 |
| RQ3 | コミュニケーションは、負担の不均衡による影響を和らげるか | コミュニケーションが少ない、多い、定期的に分担を見直す |
| RQ4 | どの意思決定戦略が、長期的な満足度を高めるか | Fixed、Greedy、Fairness-aware、Adaptive |
| RQ5 | 外部ストレスは、関係継続にどう影響するか | 所得の減少、労働時間の増加、家事負担の増加、一時的な生活費の増加 |
| RQ6 | 短期的な満足度の最大化と、長期的な関係継続は一致するか | 毎年の満足度を最大化する戦略と、長期的な公平性・満足度を保つ戦略 |

**どの RQ の結果も、モデルの仮定に依存します。**どのシナリオや戦略が「最も安定する」かは、このリポジトリでは決めていません。実験して確かめてください。

### 学ぶこと

配列・リスト、辞書、条件分岐、ループ、全探索、Greedy 法、最大値探索、状態遷移、時系列シミュレーション、確率モデル、多目的評価、感度分析、アルゴリズムの計算量。

## 2. パートナーシップを動的システムとして考える

パートナーシップを、**2 人の意思決定主体が相互作用する動的システム**として表します。

```text
         ┌────────────── 1 年（1 ステップ） ──────────────┐
状態(t-1) → 生活条件（ストレスイベント）→ 分担 (x, y) を決める → 2 人の満足度 → 関係の状態(t) → 継続 / 解消
   ↑                                                                                     │
   └───────────────────────────── 次の年へ（解消したら止まる） ─────────────────────────┘
```

- **状態**：2 人の満足度、関係全体の満足度、外部ストレス、継続しているかどうか
- **入力**：家事の総時間・生活費・所得・労働時間（ストレスイベントで変わる）
- **意思決定**：毎年、2 人がどのように分担するか（戦略）
- **出力**：年ごとの記録、関係が継続した年数、5・10・20 年継続率

## 3. 2 人の意思決定主体

`partners.py` では、パートナー 1 人を辞書 1 つで表します。データは `data/sample_partnerships.json` にあり、**すべて架空の値**です。

| 項目 | 意味 | 範囲 |
| --- | --- | --- |
| `id` | `"A"` または `"B"` | — |
| `annual_income` | 年収（万円・額面・架空） | 0 以上 |
| `weekly_work_hours` | 1 週間の労働時間 | 0〜168 |
| `available_housework_hours` | 1 週間に家事に使える時間の上限 | 0〜168 |
| `preferred_housework_share` | 自分が担当したい家事の割合 | 0〜1 |
| `preferred_financial_share` | 自分が負担したい生活費の割合 | 0〜1 |
| `communication_score` | コミュニケーションを表す架空の指標 | 0〜1 |
| `fairness_weight` | 公平性を重視する程度 | 0〜1 |
| `satisfaction` | 関係満足度（シミュレーションの初期値） | 0〜1 |

`validate_partner` が入力を検証し、範囲外の値があれば `ValueError` を出します。検証する内容は、所得・労働時間・家事に使える時間が負でないこと、割合・指標・満足度が 0〜1 に収まっていることです。

**Partner A・B は区別のための名前です。**性別による役割を固定しません。

### サンプルのシナリオ（教育用の架空条件）

4 つのシナリオは、どれも同じ 2 人（`base_partners`）を使います。シナリオごとに変えているのは、分担のルール・コミュニケーション・戦略だけです。

| シナリオ | 家事分担 | 生活費の負担 | コミュニケーション | 戦略 |
| --- | --- | --- | --- | --- |
| A：均等分担 | 50:50 | 50:50 | 中程度（0.5） | Fixed |
| B：比例分担 | 労働時間に応じる | 所得比例 | 中程度（0.5） | Fixed |
| C：負担集中 | 80:20（A に集中） | 50:50 | 低い（0.2） | Fixed |
| D：適応的分担 | 50:50 から始めて定期的に見直す | 50:50 から始めて定期的に見直す | 高い（0.8） | Adaptive |

**どのシナリオが最も安定するかは決めつけていません。**シナリオ同士は複数の条件が同時に違うので、違いの原因を調べるには条件を 1 つずつ変えて比べてください（Experiment 6 の TODO）。

## 4. 家事分担

家事の総時間（例：30 時間/週）を 2 人で分けます。Partner A の分担率を $x$ とします。

```text
Housework_A = x × Total Housework
Housework_B = (1 − x) × Total Housework
```

| ルール | 関数 | A の分担率 $x$ |
| --- | --- | --- |
| 50:50 | `equal_share` | 0.5 |
| 労働時間に応じる | `work_hours_housework_share` | B の労働時間 ÷ 2 人の労働時間 |
| 所得に応じる | `income_housework_share` | B の所得 ÷ 2 人の所得 |
| 2 人の希望 | `preference_housework_share` | A の希望と「B の希望から決まる A の分担」の中間 |
| 固定の数値 | （シナリオに `0.8` などと書く） | その値 |

**実行可能性**：家事時間が「家事に使える時間」を超える分担は、実行不可能とします（`is_feasible`、`feasibility_report`）。

- 意思決定戦略は、実行可能な候補だけから選びます。
- Fixed 戦略で実行不可能な分担を続ける場合は、超過分を満足度の**ペナルティ**（減点）にします。
- 実行可能な候補が 1 つもない年もあります（例：家事が増えて、2 人の家事に使える時間の合計を超えた年）。そのときは、すべての候補の中からペナルティを含めて最も良い分担を選びます（`infeasible_fallback`）。

> **「所得に応じた家事分担」は比較のためのルールです。**所得の多い側が家事を少なくすることを、自動的に正当化するものではありません。

## 5. 経済的負担

年間の生活費（例：360 万円）を 2 人で分けます。Partner A の負担率を $y$ とします。

```text
Financial_A = y × Annual Household Expenses
Financial_B = (1 − y) × Annual Household Expenses
```

| ルール | 関数 | A の負担率 $y$ |
| --- | --- | --- |
| 50:50 | `equal_share` | 0.5 |
| 所得比例 | `income_share` | A の所得 ÷ 2 人の所得 |
| 2 人の希望 | `preference_financial_share` | 2 人の希望の中間 |
| 交渉 | `decision_strategies.fairness_allocation`（家事を固定し、生活費だけを候補から選ぶ） | 「平均満足度 − λ × 満足度の差」が最大になる $y$ |

- 生活費の負担が所得を超える分担は、実行不可能とします。
- **家事分担率 $x$ と生活費の負担率 $y$ は、同じである必要はありません**（別々に決めます）。

## 6. コミュニケーション

`communication_score`（0〜1）は、コミュニケーションを表す**架空の指標**です。満足度関数には、2 人の指標の平均 $c$ が次の 2 通りで入ります。

1. **直接の効果**：$+ w_3 \cdot c$
2. **不満を和らげる効果**：希望とのずれによる減点に $(1 - b \cdot c)$ を掛ける。$b$ は `communication_buffer`

2 の「話し合いで不満が和らぐ」は、このモデルの**仮定**です。$b = 0$ にすると、この効果はなくなります。RQ3 を調べるときは、この仮定を変えた場合も比べてください。

「定期的に分担を見直す」条件は、Adaptive 戦略で表します（9 章）。

## 7. 満足度モデル

`household_model.utility` は、各パートナーのその年の満足度（効用）を、教育用の重み付きモデルで計算します。

```text
U_i = clip( base
            − (1 − b × c) × (w1 × 家事の希望とのずれ_i + w2 × 生活費の希望とのずれ_i)
            + w3 × c
            − w4 × Stress
            + w5 × 自由時間_i
            − w6 × 超過_i
            − w7 × 公平性の重視度_i × 不公平感_i
            − w8 × 家計の圧迫_i ,  0, 1)
```

| 要素（0〜1） | 定義 |
| --- | --- |
| 家事・生活費の希望とのずれ | \|実際の分担 − 希望の分担\| |
| 自由時間 | (70 − 労働時間 − 家事時間) ÷ 70。「70 時間」は睡眠などを除いた 1 週間の時間（架空の値） |
| 超過 | 家事に使える時間を超えた時間 ÷ 10 時間 + 所得を超えた生活費 ÷ 生活費 |
| 不公平感 | 自分の（労働 + 家事）時間が相手より多い分 ÷ 20 時間 |
| 家計の圧迫 | （生活費の負担 ÷ 自分の所得 − 0.5）÷ 0.5。0 未満は 0 |
| Stress | その年の外部ストレス（13 章） |

| 係数 | 値（架空） | 係数 | 値（架空） |
| --- | --- | --- | --- |
| base | 0.6 | w5（自由時間） | 0.15 |
| w1（家事のずれ） | 0.6 | w6（超過） | 0.5 |
| w2（生活費のずれ） | 0.4 | w7（不公平感） | 0.3 |
| w3（コミュニケーション） | 0.2 | w8（家計の圧迫） | 0.3 |
| w4（ストレス） | 0.3 | b（communication_buffer） | 0.3 |

**係数はすべて教育用の架空の値です。**実際の夫婦関係の満足度を予測するものではありません。

### 2 人の満足度を区別する

`satisfaction_summary` と `evaluation.py` で、次の 5 つを区別して扱います。

- Partner A の満足度
- Partner B の満足度
- 平均満足度
- 最低満足度
- 満足度の差

**平均満足度だけで関係の公平性を評価しません。**平均が同じでも、一方だけが低いことがあります。

## 8. 公平性

`evaluation.fairness_index` は、教育用の公平性指標です。

$$
\text{Fairness} = 1 - \frac{w_h\,|x - x^*| + w_f\,|y - y^*| + w_s\,|S_A - S_B|}{w_h + w_f + w_s}
\qquad（1 = 最も公平）
$$

$(x^*, y^*)$ は「公平とみなす基準の分担」です。**何を公平とみなすかはモデル上の選択**で、基準を変えると同じ分担の評価が変わります（RQ1）。

| 基準（`reference`） | 家事 $x^*$ | 生活費 $y^*$ |
| --- | --- | --- |
| `workload`（既定） | 労働 + 家事 の時間が 2 人で等しくなる値 | 所得比例 |
| `equal` | 0.5 | 0.5 |
| `income` | 所得の少ない人が多く担当する（比較用） | 所得比例 |
| `preference` | 2 人の希望の中間 | 2 人の希望の中間 |

- **50:50 の分担が常に公平とは限りません。**労働時間や所得が違えば、50:50 でも負担の総量は違います。
- 逆に、「所得が多いから家事を少なくしてよい」とも限りません。
- 公平性指標の基準や重み（`weights`）を変えて、評価がどう変わるかを調べてください。

## 9. 意思決定戦略

`decision_strategies.py` に 4 つの戦略を実装しています。

| 戦略 | 関数 | 選び方 |
| --- | --- | --- |
| A：Fixed Allocation | `fixed_allocation` | 最初の分担をずっと続ける |
| B：Greedy Optimization | `greedy_allocation` | その年の**平均満足度**が最大の候補を選ぶ |
| C：Fairness-aware Negotiation | `fairness_allocation` | **平均満足度 − λ × 満足度の差** が最大の候補を選ぶ（λ = `fairness_lambda`、既定 1.0） |
| D：Adaptive Allocation | `adaptive_allocation` | 見直しの年だけ、今の分担から x・y を最大 1 目盛り動かした近くの候補から、C と同じ目的関数で選ぶ |

Adaptive が見直しをするのは、次のどちらかの年です（`needs_review`）。

- `review_interval` 年ごと（既定 2 年）の年で、関係満足度が前回の見直しより下がった、または `review_threshold`（0.6）を下回ったとき
- ストレスイベントが起きた年

λ の値による違い：

- λ = 0 なら、Fairness-aware は Greedy と同じになります。
- λ = 0.5 なら、「最低満足度の最大化」と同じ値になります（平均 − 0.5 × 差 = 最低）。

**すべての戦略で、同じ候補集合（`candidate_grid`）・同じ制約（`choice_set`）・同じ満足度関数を使います。**違うのは「選び方」だけなので、戦略の違いを比べられます。

ストレスイベントが起きると、各戦略はその年の新しい条件で分担を選び直せます。

- Greedy・Fairness-aware は毎年選び直します。
- Adaptive はイベントの年に見直します。
- Fixed は変えません。

## 10. Greedy 法と全探索

候補は、家事分担率と生活費の負担率の組 $(x, y)$ です。

```python
shares = ds.share_grid(0.1)          # [0.0, 0.1, 0.2, ..., 1.0]（整数から作るので誤差がない）
candidates = ds.candidate_grid(0.1)  # 11 × 11 = 121 通り
```

- **全探索**：候補すべての目的関数を計算する（`evaluate`）。
- **最大値探索**：教科書の `max_of` で最大値を求め、その値が最初に現れる位置を教科書の `seq_search`（線形探索）で探します（`best_candidate`）。同点なら候補の並び順で最初のものを選ぶので、結果は**決定的**です。
- **Greedy 法**：Greedy 戦略は「その年」の平均満足度だけを最大化し、将来への影響は考えません。毎年の最適な選択を積み重ねても、20 年後に最適になるとは限りません（RQ6）。
- 実行可能な候補が 1 つもないときの扱い：
  - `infeasible_fallback = False` なら、戦略は `None` を返し、シミュレーションでは前年の分担を続けます。
  - `infeasible_fallback = True`（既定）なら、全候補から選びます。

## 11. 関係状態の時間変化

`relationship_dynamics.simulate` が、1 年を 1 ステップとして 5・10・20 年をシミュレーションします。

```text
for t = 1 .. T:
    1. 生活条件（ストレスイベント）を求める          conditions_at
    2. 戦略が分担 (x, y) を決める                   decide
    3. その年の満足度 U_A(t), U_B(t)                 utilities
    4. 満足度の更新
         S_i(t) = clip((1 − alpha) × S_i(t−1) + alpha × U_i(t), 0, 1)
    5. 関係全体の満足度
         R(t) = (1 − m) × 平均(S_A, S_B) + m × 最低(S_A, S_B)
    6. 関係解消確率
         p(t) = clip(baseline + beta × (1 − R(t)) + gamma × Stress(t), 0, 1)
    7. 一様乱数 u(t) < p(t) なら解消 → 終了
```

| パラメータ | 値（架空） | 意味 |
| --- | --- | --- |
| `alpha` | 0.3 | 満足度の更新速度。大きいほど今年の条件にすぐ反応する |
| `relationship_min_weight`（m） | 0.5 | 関係全体の満足度で「低い方の満足度」を重視する程度 |
| `baseline_hazard` | 0.01 | 基準解消確率 |
| `beta` | 0.08 | 関係満足度が低いことの影響 |
| `gamma` | 0.06 | ストレスの影響 |
| `base_stress` | 0.1 | イベントのない年のストレス |
| `simulation_years` | 20 | 観測期間 |

### 年ごとの記録

各年の記録には、次の項目が入ります。

- 年
- 家事分担率、経済的負担率
- Partner A の満足度、Partner B の満足度
- 関係全体の満足度
- 外部ストレス
- 関係解消確率
- 関係継続状態

加えて、その分担が実行可能か、Adaptive が見直したか、ストレスイベントの年か、も記録します。0 年目の記録は初期状態です。

## 12. 関係継続・解消

- 各年に一様乱数を 1 つ生成し、**乱数が解消確率を下回ったら解消**と判定します。
- 一度解消した関係は、Core Research では再開しません。**解消後は意思決定も満足度の更新もしません。**
- 観測期間の終わりまで継続した関係は「**打ち切り**（censored）」として扱います。「解消が観測されなかった」だけで、その後どうなるかは分かりません。
- 乱数は (シード, シナリオ, 反復番号) で決まり、**戦略にはよりません（共通乱数）**。戦略の違いだけを比べられます。
- 同じシードなら、同じ結果を再現できます。

### モンテカルロ法と理論値

`monte_carlo` は、多数回の反復で継続率を求めます。

- Core モデルでは、乱数を解消の判定だけに使います。満足度の軌跡は乱数によらず決まります。
- そこで、軌跡は 1 回だけ計算し、反復ごとには「$u(t) < p(t)$ となる最初の年」だけを線形探索で探します。
- こうしても、`simulate` を何回も呼ぶのと同じ結果になります（unittest で確認）。

理論的な継続率は $\prod_{s \le t} (1 - p(s))$ です（`theoretical_survival`）。反復回数を増やすと、シミュレーションの継続率はこの値に近づきます。

## 13. 外部ストレスイベント

イベントは、発生年・種類・影響量で指定します（`data/sample_partnerships.json` の `stress_event_sets`）。

```json
{"year": 5, "type": "income_change", "partner": "A", "change": -0.2, "stress": 0.2}
{"year": 8, "type": "housework_change", "change": 10, "stress": 0.2}
```

| 種類 | 影響 |
| --- | --- |
| `income_change` | 所得 × (1 + change) |
| `work_hours_change` | 労働時間 + change。家事に使える時間は同じだけ減る（0 未満にはならない） |
| `housework_change` | 家事の総時間 + change |
| `expense_change` | 生活費 × (1 + change) |

- 条件の変化は、`duration` 年続きます。指定しなければ、発生年以降ずっと続きます。
- ストレス（`stress`）は、発生から `stress_duration` 年（既定 2 年）だけ加わります。
- 用意しているイベントの組：`none`、`combined`（Year 5：A の所得 −20%、Year 8：家事 +10 時間/週）、`income_drop`、`work_increase`、`housework_increase`、`expense_increase`（3 年間だけ +30%）

`combined` の Year 8 以降は、家事の総時間（40 時間）が 2 人の家事に使える時間の合計（37 時間）を超えます。つまり、実行可能な分担が 1 つもなくなります。そのとき各戦略が何を選ぶかも観察してください。

## 14. 評価指標

| 指標 | 関数 | 定義 |
| --- | --- | --- |
| Mean Satisfaction | `mean_satisfaction` | 2 人の平均満足度 |
| Minimum Satisfaction | `minimum_satisfaction` | 2 人のうち低い方 |
| Satisfaction Difference | `satisfaction_difference` | 2 人の満足度の差の絶対値 |
| Fairness Index | `fairness_index` | 8 章 |
| Relationship Continuation Rate | `continuation_rate` | T 年後に関係が継続している割合（観測期間が T 年未満の結果は数えない） |
| Dissolution Rate | `dissolution_rate` | 観測期間内に関係が解消した割合 |
| Relationship Duration | `duration_summary` | 解消した関係と、打ち切った関係を**分けて**数える |
| Robustness to Stress | `stress_response`、`robustness_to_stress` | イベントの前後 2 年の関係満足度の変化。イベントの有無による継続率の差 |

`compare_strategies` は、同じ初期条件・同じイベント・同じ乱数で、4 つの戦略を比べます。

- 満足度・公平性：「関係が続いた場合」の 20 年間の平均。解消した関係を除くと、生き残った関係だけの平均になって偏るため、こうしています。
- 継続率：シードごとの継続率の平均と、シード間の標準偏差（`_sd`）。
- `first_year_mean_utility`：1 年目の平均満足度。RQ6 の「短期」の指標です。

## 15. アルゴリズムと計算量

| 処理 | 計算量 | 説明 |
| --- | --- | --- |
| 1 つの分担の評価（家事・生活費・満足度） | $O(1)$ | 2 人分の四則演算 |
| T 年間の時系列シミュレーション（Fixed） | $O(T)$ | 1 年あたり $O(1)$（イベント数 E を数えるなら $O(TE)$） |
| K 個の分担候補の全探索 | $O(K)$ | 1 つの率だけを選ぶ場合 |
| 家事 K 個 × 生活費 L 個の全探索 | $O(KL)$ | 既定は 11 × 11 = 121 |
| Greedy・Fairness-aware で T 年 | $O(TKL)$ | **毎年、全候補を探索する**ため |
| Adaptive で T 年 | $O(TKL)$ | 見直しの年は、実行可能な候補を求める $O(KL)$ と近くの候補（最大 9 個）の探索。それ以外の年は $O(1)$ |
| M 回のモンテカルロ反復 | $O(MT)$ | 反復ごとに T 年分の乱数と線形探索 |
| M 回の反復（戦略が全探索する場合） | $O(TKL + MT)$ | 軌跡は乱数によらないので 1 回だけ計算する（12 章）。毎回シミュレーションし直すと $O(M \cdot TKL)$ |
| S 種類の戦略の比較 | $O(SMT)$ | 全探索を含めると $O(S(TKL + MT))$ |
| 戦略の順位付け | $O(S^2)$ | 教科書の単純挿入ソート（S = 4 なので十分） |

`share_step` を 0.1 から 0.05 にすると、K・L はそれぞれ 11 から 21 になり、全探索の候補は 121 から 441 に増えます（約 3.6 倍）。

## 16. 教科書との関連

教科書：柴田望洋『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』（SB クリエイティブ）

### 実際に使用した（改変せずに `textbook/` にコピーし、import している）コード

| ファイル | 原本 | 関数 | F4 での用途 |
| --- | --- | --- | --- |
| `textbook/max.py` | `chap02/max.py` | `max_of` | 最も高い評価値の選択（最大値探索）：`decision_strategies.best_candidate` |
| `textbook/ssearch_while.py` | `chap03/ssearch_while.py` | `seq_search` | 最大値の位置の探索（`best_candidate`）、関係解消年の検出（`relationship_dynamics.monte_carlo`、`evaluation.dissolution_year_of`） |
| `textbook/insertion_sort.py` | `chap06/insertion_sort.py` | `insertion_sort` | 複数戦略の順位付け（`decision_strategies.rank_strategies`。安定なソートなので、同点は名前順のまま） |

3 本とも、原本と SHA-256 が一致することを確認しています。どのファイルも `if __name__ == '__main__':` の中で対話入力を行うので、import しても入力待ちにはなりません。教科書のコードを使うためだけの Adapter は作っていません。

### 教科書の内容との対応

| F4 の処理 | 教科書の内容 | F4 のコード |
| --- | --- | --- |
| 1. 年次満足度の記録 | 配列・リスト（第2章） | `simulate` の `records`（年ごとの辞書のリスト） |
| 2. 家事分担候補の比較 | 全探索 | `candidate_grid`・`evaluate`（二重ループで K × L 通り） |
| 3. 最も高い満足度の選択 | 最大値探索（第2章 `max_of`） | `best_candidate` |
| 4. 複数戦略の順位付け | ソート（第6章 `insertion_sort`） | `rank_strategies` |
| 5. 関係解消年の検出 | 線形探索（第3章 `seq_search`） | `monte_carlo`・`dissolution_year_of` |
| 6. 時間経過による状態変化 | ループ・状態遷移 | `simulate` の `for t in range(1, years + 1)` |

### 参考にしただけのコード（コピー・import していない）

| ファイル | 理由 |
| --- | --- |
| `chap06/selection_sort.py` | 安定でない（同点の並び順が変わる）ので、順位付けには単純挿入ソートを使った |
| `chap02/max_of_test.py` など | 対話入力を伴うテスト用のサンプル |
| `chap05/`（再帰） | Core では使っていない。Advanced A（繰り返しゲームの探索）で参考にできる |

候補として挙がっていた `chap02/max_of.py` は、原本にはありません。`max_of` は `chap02/max.py` で定義されています。

> **教科書コードの公開再配布の条件は確認できていません。**`textbook/` を含むリポジトリを公開 GitHub に push しないでください（26 章）。

## 17. ファイル構成

```text
f4-partnership-simulation/
├── README.md                     … この文書
├── .gitignore
├── requirements-notebook.txt     … Notebook 用のライブラリ（Core には不要）
├── starter.py                    … 全体の流れを確認するデモ
├── partners.py                   … パートナーモデル、データの読み込み・検証、F3 のペアの読み込み（Advanced E）
├── household_model.py            … 家事・経済的負担、実行可能性、満足度（効用）の計算
├── decision_strategies.py        … 候補集合、全探索、4 つの意思決定戦略、戦略の順位付け
├── relationship_dynamics.py      … ストレスイベント、満足度の更新、関係解消確率、シミュレーション、モンテカルロ
├── evaluation.py                 … 評価指標、公平性、継続率、戦略の比較
├── experiments.py                … 学生向けの研究実験の入口（Experiment 1〜7）
├── partnership_charts.py         … Notebook 用のグラフ（matplotlib。Core には不要）
├── data/
│   ├── sample_partnerships.json  … 架空のパートナー、シナリオ A〜D、ストレスイベント、モデルのパラメータ
│   └── sample_f3_pairs.json      … F3 の出力形式の架空のサンプル（Advanced E）
├── notebooks/
│   ├── README.md
│   ├── 01_housework_and_financial_sharing.ipynb
│   ├── 02_satisfaction_and_fairness.ipynb
│   ├── 03_decision_strategies.ipynb
│   ├── 04_relationship_dynamics.ipynb
│   ├── 05_integrated_simulation.ipynb
│   └── 06_research_presentation.ipynb
├── textbook/                     … 教科書のコード（改変なし。公開しない）
│   ├── __init__.py
│   ├── max.py
│   ├── ssearch_while.py
│   └── insertion_sort.py
└── tests/
    ├── test_partners.py
    ├── test_household_model.py
    ├── test_decision_strategies.py
    ├── test_relationship_dynamics.py
    ├── test_evaluation.py
    └── test_partnership_charts.py  … グラフのテスト（matplotlib がなければスキップ）
```

## 18. Python プログラムの実行方法

Python 3.10 以上で動きます。Core は**標準ライブラリだけ**で動くので、追加のインストールは不要です。

```bash
cd f4-partnership-simulation

python3 starter.py                       # 全体の流れ（データ → 分担 → 満足度 → 4 戦略 → 20 年 → イベント → 継続率 → TODO）
python3 experiments.py                   # Experiment 1〜7 をすべて実行
python3 experiments.py 4                 # Experiment 4 だけ
python3 -m unittest discover -s tests -v # unittest
```

`starter.py` の出力の形（数値は実行して確認してください）：

```text
F4: Partnership Stability and Decision Making

Strategy       Mean Satisfaction  Min Sat  Fairness  5Y Cont.  10Y Continuation  20Y Cont.
Fixed                        ...      ...       ...       ...       ... ±...           ...
Greedy                       ...
Fairness-aware               ...
Adaptive                     ...

Student Research TODOs:
  1. ...
```

継続率は、5 シード × 200 回の反復から計算します。

## 19. Google Colab Notebook の実行方法

詳しくは [`notebooks/README.md`](notebooks/README.md) を参照してください。

| 項目 | 方法 |
| --- | --- |
| GitHub から clone する | 「準備」セルの `REPO_URL` に**自分たちのリポジトリの URL** を入れて実行する（このリポジトリには URL を書いていません） |
| ZIP をアップロードして展開する | F4 のフォルダを ZIP にして `/content` にアップロードし、「準備」セルを実行する |
| 作業ディレクトリの設定 | 「準備」セルが `household_model.py` のあるフォルダを探し、`os.chdir` する（WSL の絶対パスは使わない） |
| `.py` モジュールの import | 「準備」セルが `sys.path` に F4 のルートを追加し、`partners`・`household_model` などを import する |
| Notebook の実行順序 | 01 → 02 → 03 → 04 → 05 → 06（各 Notebook は単独でも実行できる） |

- Colab の CPU ランタイムで動きます（GPU・TPU は不要）。
- 必要なライブラリは `requirements-notebook.txt` にまとめていますが、Colab には最初から入っています。
- 計算は `.py` で行います。Notebook の中に同じ計算を書き直さないでください。

## 20. Core Research

全チームが取り組む必須課題です。それぞれに、対応する関数と実験の入口を用意してあります。

| # | 課題 | 関数・ファイル |
| --- | --- | --- |
| 1 | パートナーデータを読み込む | `partners.load_scenarios` |
| 2 | 家事分担を計算する | `household_model.housework_hours`、分担ルール |
| 3 | 経済的負担を計算する | `household_model.financial_amounts`、`income_share` |
| 4 | 満足度を計算する | `household_model.utility` |
| 5 | 公平性を計算する | `evaluation.fairness_index` |
| 6 | Fixed 戦略を実装する | `decision_strategies.fixed_allocation` |
| 7 | Greedy 戦略を実装する | `decision_strategies.greedy_allocation` |
| 8 | Fairness-aware 戦略を実装する | `decision_strategies.fairness_allocation` |
| 9 | Adaptive 戦略を実装する | `decision_strategies.adaptive_allocation`・`needs_review` |
| 10 | 満足度の時間変化を計算する | `relationship_dynamics.update_satisfaction`・`simulate` |
| 11 | ストレスイベントを導入する | `relationship_dynamics.conditions_at` |
| 12 | 関係解消確率を計算する | `relationship_dynamics.dissolution_probability` |
| 13 | 5 年・10 年・20 年継続率を計算する | `evaluation.continuation_rate`・`compare_strategies` |
| 14 | 複数シードで比較する | `compare_strategies(..., seeds=...)`、`experiments.py` |
| 15 | 結果をグラフにまとめる | Notebook 01〜06、`partnership_charts.py` |
| 16 | モデルの限界を考察する | 23 章、Notebook 06 の「モデルの限界」 |

各 `.py` の末尾と Notebook に **TODO** があります。starter に入っている実装は最小限です。たとえば、満足度の式・公平性の定義・Adaptive の見直し方法は、改良できる余地を残してあります。

### 実験の入口（`experiments.py`）

| Experiment | 内容 | 主な RQ |
| --- | --- | --- |
| 1 | 家事分担率を変えて、2 人の満足度と公平性（4 つの基準）を比べる | RQ1 |
| 2 | 生活費の負担を 50:50・所得比例・希望・交渉で比べる | RQ2 |
| 3 | コミュニケーション指標を変えて、満足度と継続率を比べる | RQ3 |
| 4 | Fixed・Greedy・Fairness-aware・Adaptive を比べる | RQ4・RQ6 |
| 5 | 所得の減少・労働時間の増加・家事負担の増加・生活費の増加を導入する | RQ5 |
| 6 | シナリオ A〜D の 5・10・20 年継続率を比べる | RQ4〜RQ6 |
| 7 | 満足度関数の重み・更新速度・基準解消確率などの感度分析 | 全 RQ |

## 21. Advanced Research

Advanced A〜F から 1 つ以上を選んで取り組みます（starter には実装していません）。

### Advanced A：繰り返しゲーム

2 人の協力・非協力の戦略を、繰り返しゲームとしてモデル化します。

- 例：毎年、2 人がそれぞれ「家事を多めに引き受ける（協力）」か「引き受けない（非協力）」かを選ぶ
- 例：しっぺ返し戦略・常に協力・常に非協力などを比べる
- 満足度の更新式（11 章）を、利得表に置き換えてみましょう。

### Advanced B：強化学習

過去の満足度や負担をもとに、分担の戦略を学習します。

- 例：状態 = （満足度の区分, ストレスの有無）、行動 = 分担の変更（±0.1）、報酬 = 翌年の関係満足度
- 例：Q 学習
- Adaptive 戦略と比べてください。

### Advanced C：動的ストレス

確率的な所得の変化、仕事量の変化、生活費の変化を導入します。

- 例：毎年、確率 q でイベントが起きる
- 乱数を解消の判定以外にも使うと、満足度の軌跡が反復ごとに変わります。その場合、12 章の「軌跡を 1 回だけ計算する」近道は使えません（計算量は $O(M \cdot TKL)$ になります）。

### Advanced D：多目的最適化

次の 4 つの指標を同時に評価します。

- 平均満足度
- 最低満足度
- 公平性
- 関係継続率

例：どの指標でも他の戦略に負けない戦略（パレート最適）を探す。重み付き和の重みを変えて、順位がどう変わるかを調べる。

### Advanced E：F3 との連携

F3「出会いとマッチングのアルゴリズム」で成立したペアを、F4 の初期条件として使います。

- 受け取るデータ形式（`f3-to-f4/1`）は、F3 の `export_pairs_for_f4` が出力する JSON と同じです。

  | フィールド | 内容 |
  | --- | --- |
  | `pair_id` | ペア ID |
  | `participant_ids` | 参加者 2 人の ID |
  | `initial_compatibility` | 初期適合度（0〜1） |
  | `initial_satisfaction` | 初期満足度（`null` 可） |
  | `matching_algorithm` | マッチングアルゴリズム |

  ```json
  {"format": "f3-to-f4/1",
   "pairs": [{"pair_id": "GS-1", "participant_ids": ["A1", "B1"], "initial_compatibility": 0.91,
              "initial_satisfaction": 0.8, "matching_algorithm": "gale_shapley"}]}
  ```

- `partners.load_f3_pairs` が形式を検証します。`partners.scenario_from_f3_pair` は、1 組のペアから F4 のシナリオを作ります。
  - 家事・所得などの条件は F3 にないので、F4 のシナリオ（テンプレート）から借ります。
  - 2 人の初期満足度は、`initial_satisfaction` を使います。`null` なら `initial_compatibility` を使います。
- **F3 のコードは import も変更もしていません。**F3 がなくても試せるよう、架空のサンプル `data/sample_f3_pairs.json` を用意しています。
- TODO：初期適合度を、希望の分担やコミュニケーションにも反映させる。マッチングのアルゴリズム別に、F4 での長期継続を比べる。

### Advanced F：意思決定の非対称性

2 人の交渉力・利用可能時間・所得・希望条件が違う場合を扱います。

- 例：交渉力の重み $\theta$ を使って、目的関数を $\theta U_A + (1 - \theta) U_B$ にする
- 例：ナッシュ交渉解 $\max (U_A - d_A)(U_B - d_B)$ を使う
- **公平性を、単純な 50:50 の分担と同一視しないでください。**

## 22. 実験条件と評価指標

### 実験上の約束

- **同じ初期条件**（同じパートナー・家計）で比べる。違いを調べたい条件以外は変えない。
- **同じストレスイベント**を使う。
- **複数の乱数シード**で反復する（既定：5 シード × 200 回）。共通乱数を使う。
- **平均とばらつき**（シード間の標準偏差）を報告する。
- **単一試行の結果だけで結論を出さない。**差がばらつきと同じくらいなら、「差があるとは言えない」と書く。
- **戦略の優劣はモデルの仮定に依存する**ことを明記する。感度分析で、順位が入れ替わる条件を探す。

### 報告する指標

| 区分 | 指標 |
| --- | --- |
| 短期 | 1 年目の平均満足度・最低満足度・満足度の差 |
| 長期（関係が続いた場合） | 20 年間の平均満足度・最低満足度・満足度の差・公平性 |
| 継続 | 5・10・20 年継続率（± シード間の標準偏差）、解消率、継続期間（打ち切りを区別） |
| ストレス | イベント前後の関係満足度の変化、イベントの有無による継続率の差 |

## 23. モデルの限界と倫理的配慮

- 本教材は**教育用の架空シミュレーション**です。
- **実際の離婚確率や、関係の将来を予測しません。**
- **満足度関数の係数は架空のもの**です。
- 家事分担と関係継続の関係は、**モデルの仮定に依存します**。
- **50:50 の分担が常に公平とは限りません。**
- **所得の多寡によって人間の価値を評価しません。**
- **性別による家事・経済的役割を固定しません。**Partner A・B は区別のための名前です。
- **実在する人物の関係満足度を推定しません。**このモデルを、自分や身近な人の関係に当てはめないでください。
- **実際の個人情報を使用しません。**データはすべて架空です。
- **関係の解消を、個人の失敗として扱いません。**
- **関係の継続が、常に望ましいとは限りません。**「継続率が高い = 良い」とは限りません。
- **強制・暴力・安全上の問題を、単なる満足度の最適化の問題として扱いません。**これらは安全と支援の問題です。
- 本モデルは、**現実の人間関係を大幅に単純化**しています。たとえば次のものは表していません。
  - 家事の種類（料理・育児・介護など）の違い
  - 感情、信頼、価値観
  - 家族・友人・地域とのつながり
  - 健康、住居、文化的な背景
- 乱数で決まる「解消」は、ある人の選択や責任を表すものではありません。

発表や考察では、結論を「**このモデルの仮定の下では**」という形で述べてください。

## 24. GitHub を用いたチーム開発

- チームのリポジトリに F4 のフォルダを置き、Issue と Pull Request で作業を分担します。
  - 例：RQ ごとに担当を決める
  - 例：Experiment ごとにブランチを作る
- `.py` を変更したら、`python3 -m unittest discover -s tests -v` を実行してから Pull Request を作ります。
- Notebook は、**出力を消してから**コミットすると、差分が見やすくなります（Jupyter の「Clear All Outputs」）。
- **`textbook/` を公開リポジトリに push しないでください**（26 章）。
  - 非公開リポジトリを使う。
  - または、`.gitignore` に `textbook/` を追加し、各自が教科書のサンプルからコピーする。
- GitHub のアクセストークンやパスワードを、コードや Notebook に書かないでください。

## 25. 成果物と提出方法

1. **コード**：変更・追加した `.py` と、すべて成功する unittest。
2. **Notebook**：実験に使った 01〜05（または追加の Notebook）と、研究発表用の 06。
3. **研究発表**：Notebook 06、またはそこから作ったスライド。次の内容を含めます。
   - RQ と、実験の前に立てた仮説
   - 実験条件（初期条件・イベント・シード数・反復回数・変えたパラメータ）
   - 結果（平均とばらつき）
   - 考察と、モデルの限界
   - 結論（仮定とともに）と、今後の課題
4. **Advanced Research**：選んだ課題（A〜F）の実装と結果。

提出方法（リポジトリの URL・提出期限など）は、授業の指示に従ってください。

## 26. 参考文献・著作権上の注意

- 柴田望洋『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』SB クリエイティブ
  - 第 2 章 配列（最大値）、第 3 章 探索（線形探索）、第 6 章 ソート（単純挿入ソート）
- F3「出会いとマッチングのアルゴリズム」starter repository（関係継続モデルの出発点、F3 → F4 のデータ形式）
- データ：`data/sample_partnerships.json`、`data/sample_f3_pairs.json`（**この教材のための架空のデータ**）

### 著作権上の注意

- `textbook/` の 3 本は、上記の教科書のサンプルコードを**改変せずに**コピーしたものです。原本との SHA-256 の一致を確認しています。
- **公開再配布の条件は確認できていません。**`textbook/` を含むリポジトリを、公開 GitHub に push しないでください。
- このリポジトリの満足度関数・関係解消確率の式と係数は、この教材のために作った**架空のモデル**です。特定の研究や統計に基づくものではありません。

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
| `chap06/insertion_sort.py` | `f4-partnership-simulation/textbook/insertion_sort.py` | `decision_strategies.py` |
| `chap02/max.py` | `f4-partnership-simulation/textbook/max.py` | `decision_strategies.py` |
| `chap03/ssearch_while.py` | `f4-partnership-simulation/textbook/ssearch_while.py` | `decision_strategies.py`、`evaluation.py`、`relationship_dynamics.py` |

### 3. 配置後のディレクトリ構成

```text
f4-partnership-simulation/
└── textbook/
    ├── __init__.py          （リポジトリに含まれる）
    ├── insertion_sort.py    （各自で配置）
    ├── max.py               （各自で配置）
    └── ssearch_while.py     （各自で配置）
```

### 4. コピーと確認のコマンド例

```bash
cd f4-partnership-simulation
SRC="<展開したフォルダ>"        # 各自の環境に合わせる

cp -i "$SRC/chap06/insertion_sort.py" textbook/insertion_sort.py
cp -i "$SRC/chap02/max.py" textbook/max.py
cp -i "$SRC/chap03/ssearch_while.py" textbook/ssearch_while.py

# 原本とコピーの SHA-256 が一致することを確認する
sha256sum "$SRC/chap06/insertion_sort.py" textbook/insertion_sort.py
sha256sum "$SRC/chap02/max.py" textbook/max.py
sha256sum "$SRC/chap03/ssearch_while.py" textbook/ssearch_while.py

python3 starter.py                          # 実行確認
python3 -m unittest discover -s tests -v    # テスト
```

配置した教科書のコードは、リポジトリ直下の `.gitignore` によって Git の追跡対象から除外されます（`git status` に表示されなければ正常です）。
`git add -f` などで教科書のコードを commit・push しないでください。
