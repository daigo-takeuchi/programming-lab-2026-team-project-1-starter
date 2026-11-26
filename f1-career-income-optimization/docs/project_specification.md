# F-1 開発仕様（Phase 1 で確定した設計）

## 1. 概要

| 項目 | 内容 |
| --- | --- |
| 名称 | キャリア・ライフイベント・世代間資源継承のシミュレーションと最適化 |
| 英語名 | Simulation and Optimization of Career Paths, Life Events, and Intergenerational Resource Transfer |
| 対象 | プログラミング演習Ⅰ（Python 基礎、留学生を含む） |
| 配布物 | 統合 Notebook `F1_life_planning_starter.ipynb`（全 4 テーマ）、データ、README・TASKS（Phase 5） |
| 進め方 | 全チームが第0〜3章 → 担当テーマ章（1 つ）→ 第8章。第9章は任意 |

## 2. Notebook の章構成

| 章 | 内容 | 状態（Phase 1） |
| --- | --- | --- |
| 第0章 | 目的、4 テーマ、最短の学習ルート表、セルの種類、作業時間の見積もり | 作成 |
| 第1章 | 実行環境の確認、import、データフォルダの探索、日本語フォント | 作成 |
| 第2章 | 4 種類のデータ、単位のルール、データの置き場所 | 作成 |
| 第3章 | 辞書のリスト、年次更新の考え方、入力を変更しない、共通関数、計算量の記号 | 作成 |
| 第4〜7章 | F-1A〜D（10 節、Level 1 の 4 課題、Level 2・3 の候補） | 骨格 + Level 1 |
| 第8章 | 組合せ数と計算量、実行時間の測り方、チーム開発、成果物 | 骨格 |
| 第9章 | 複数テーマの統合（任意） | 骨格 |

## 3. 各テーマの設計

### F-1A キャリア選択・教育投資と生涯所得

| 項目 | 内容 |
| --- | --- |
| 中心的な問題 | 進学・就職などの選択で長期的な所得はどう変わるか。教育費はいつ回収できるか |
| Level 1 | ① `calculate_working_years(start_age, retirement_age)` ② `salary_at_age(career, age, retirement_age)` ③ `lifetime_income(career, retirement_age)`（累積和） ④ `summarize_careers(careers, retirement_age)`（生涯所得と教育費控除後） |
| Level 2 | `filter_careers()`（線形探索）、`rank_careers()`（ソート）、`find_payback_age()`（累積和 + 線形探索）、`search_career_plans()`（全探索）から 2〜3 個 |
| Level 3 | IT エンジニアのキャリアパス、転職時期、資格、費用対効果、失業・休職リスク、労働時間 |
| データ | Mini 3 件、Tiny `career_options_tiny.csv` 24 件、Small 賃金構造基本統計調査（予定） |
| アルゴリズム | 累積和 O(T)、N 候補 O(N×T)、線形探索、ソート、全探索 |

### F-1B 家族形成・子育て・介護と資源配分

| 項目 | 内容 |
| --- | --- |
| 中心的な問題 | 成人 2 人の世帯で、所得と時間をどう配分すれば生活と育児・介護を両立できるか |
| Level 1 | ① `household_income(option_a, option_b)` ② `household_expense(household)` ③ `annual_balance(option_a, option_b, household)` ④ `free_hours(weekly_work_hours, weekly_care_hours, basic_hours)` |
| Level 2 | `generate_work_pairs()`（k² の全探索）、`find_feasible_pairs()`（収支 ≥ 0 かつ各人の時間制約）、`rank_pairs()`、`simulate_household()`（複数年） |
| Level 3 | 子の年齢と育児費、育児休業とキャリア、保育サービス、介護と就業、所得と自由時間、多指標 |
| データ | Mini 3 + 1、Tiny `work_options_tiny.csv` 6 件・`household_scenarios_tiny.csv` 24 件、Small 家計調査・社会生活基本調査（予定） |
| アルゴリズム | 組合せの全探索 O(k²)、条件による絞り込み、ソート、年次シミュレーション |

### F-1C 住宅取得・居住選択と長期家計設計

| 項目 | 内容 |
| --- | --- |
| 中心的な問題 | 予算・通勤時間の条件を満たす住宅はどれか。賃貸と購入の長期的な支出はどう違うか |
| Level 1 | ① `annual_rent(monthly_rent)` ② `cumulative_rent(monthly_rent, years)` ③ `ownership_cost(option, years)` ④ `find_candidates(options, budget, max_commute)`（線形探索） |
| Level 2 | `sort_by_price()`（安定ソート）、`count_affordable()`（**二分探索**、upper bound）、`affordable_options()`（O(log N + K)）、線形探索との速度比較（1 回／Q 回）、`search_housing_plans()` |
| Level 3 | 賃貸と持ち家の長期比較、住宅ローン（元利均等）、取得時期、通勤時間と価格、維持費と残存価値、住み替え |
| データ | Mini 5 件（同じ価格 2 件）、Tiny `housing_options_tiny.csv` 30 件（同じ価格を含む）、Small 不動産取引価格情報（予定） |
| アルゴリズム | 線形探索 O(N)、ソート O(N log N)、二分探索 O(log N)、Q 回の探索での比較 |

### F-1D 世代間資源継承と次世代の生活設計

| 項目 | 内容 |
| --- | --- |
| 中心的な問題 | 親から子への資金移転は、親子それぞれの資産の推移にどう影響するか |
| Level 1 | ① `annual_balance_of(person)` ② `transfer(parent_assets, child_assets, amount)`（タプル、合計不変） ③ `update_assets(assets, annual_income, annual_expense)` ④ `simulate_transfer(parent, child, annual_transfer, years)` |
| Level 2 | `generate_transfer_scenarios()`（額 × 期間）、`find_feasible_transfers()`（親の最低資産）、`count_shortage_years()`、`rank_transfers()` |
| Level 3 | 教育資金と人的資本、住宅・金融資産・事業の継承、子から親への支援、3 世代、複数イベント（1 つ選ぶ） |
| データ | Mini 2 人 + 3 シナリオ、Tiny `family_members_tiny.csv` 24 人・`transfer_scenarios_tiny.csv` 24 件、Small 全国家計構造調査（予定） |
| アルゴリズム | 年次シミュレーション O(T)、O(S×P×T)、全探索、数え上げ、ソート |

## 4. 難易度の比較（作業11）

| 観点 | F-1A | F-1B | F-1C | F-1D |
| --- | --- | --- | --- | --- |
| Level 1 の課題数 | 4 | 4 | 4 | 4 |
| 必要な Python の知識 | if、for、range、累乗、辞書、リスト | 辞書、関数の組合せ、定数 | 掛け算、for、if（and）、リスト | 辞書、タプル、for、関数の組合せ |
| 数学的な難易度 | 中（累乗による成長） | 低（加減算） | 低（Level 1）／中（Level 3 のローン） | 低（加減算） |
| 経済・制度の前提知識 | 低（額面と手取りの区別） | 低 | 低〜中（月額・年額・総額・資産価値の区別） | 低（税・相続は扱わない） |
| 学生のコード量（Level 1 合計の目安） | 20〜30 行 | 10〜15 行 | 15〜20 行 | 20〜30 行 |
| 想定作業時間（見積もり） | L1 2.5〜3 h、L2 2〜3 h | L1 2 h、L2 2〜3 h | L1 2 h、L2 2.5〜3 h | L1 2.5〜3 h、L2 2〜3 h |
| Level 2 への発展性 | 高（回収年齢・全探索・ソート） | 高（k² 組合せ・制約充足） | 非常に高（二分探索・速度比較） | 高（S×T の全探索・多指標） |
| 独自機能の開発可能性 | 高 | 高 | 高 | 高（ただし範囲を絞る指導が必要） |

調整の方針：
- **F-1D が難しくなりすぎない**よう、Level 1 は親子 2 人・移転 1 種類・移転の順番を固定（収支 → 移転）。開始年・期間・3 世代は Level 2・3 に回した。
- **F-1C だけが探索課題にならない**よう、F-1A は線形探索（回収年齢）とソート、F-1B・F-1D は全探索と制約による絞り込みを Level 2 に置いた。
- **F-1B の Level 1 が単純すぎる**（加減算のみ）ため、Phase 3 で Tiny Dataset の検査（全世帯の収支の計算）と、Level 2 の各人の時間制約を厚くする。
- 作業時間は**設計上の見積もり**で、実測値ではない。Phase 4 で参照実装と行数を確認して再調整する。

## 5. 共通データ構造（作業7）

辞書とリストだけを使う（クラスは使わない）。キー名は英語、単位は `docs/simulation_rules.md`。

| データ | 形 | 主なキー | 共通／固有 |
| --- | --- | --- | --- |
| キャリア候補 | 辞書のリスト | `career_id`, `name`/`career_name`, `start_age`, `retirement_age`(Tiny), `initial_salary`, `annual_growth`, `education_cost` | F-1A 固有 |
| 勤務形態 | 辞書のリスト | `option_id`, `name`/`work_style`, `annual_income`, `weekly_work_hours` | F-1B 固有 |
| 世帯の条件 | 辞書 | `scenario_id`, `living_cost`, `childcare_cost`, `eldercare_cost`, `required_care_hours`（Mini）/`required_childcare_hours`・`required_eldercare_hours`（Tiny） | F-1B 固有 |
| 住宅候補 | 辞書のリスト | `housing_id`, `area`, `purchase_price`, `monthly_rent`, `floor_area`, `annual_maintenance_cost`, `commute_minutes` | F-1C 固有 |
| 家族構成 | 辞書のリスト | `person_id`, `family_id`(Tiny), `generation`, `role`, `age`, `annual_income`, `annual_expense`, `assets`（Mini）/`initial_assets`（Tiny） | F-1D 固有 |
| 資源移転シナリオ | 辞書のリスト | `annual_transfer`, `years`（Mini）/`scenario_id`, `sender_role`, `receiver_role`, `start_year`, `duration_years`（Tiny） | F-1D 固有 |
| 年次収支 | 数値 | 収入 − 支出（万円／年） | **共通の概念**（各テーマで学生が計算） |
| 年次資産残高（履歴） | 辞書のリスト | `year`, `<主体>_assets` | **共通の形**（F-1D 課題4、F-1B・F-1C Level 2） |
| シミュレーション結果 | 辞書 | シナリオの ID、指標の値 | **共通の形** |
| シナリオ評価結果 | 辞書のリスト | `<id>`, 指標の値, `feasible`（制約を満たすか） | **共通の形**（Level 2） |

- Mini と Tiny でキー名が一部異なる（`assets` / `initial_assets`、`years` / `duration_years`）。
  Tiny は「初期状態」であることを列名で明示するため。**Phase 3 で統一するか、Notebook で対応を説明するかを決める**（教員判断事項）。
- 全テーマを統合するシミュレーションエンジンは作らない。第9章も小さな組合せから始める。

## 6. 学生実装課題の形式

- 関数の目的・引数・戻り値・例を表で示す → ひな形（TODO + `raise NotImplementedError("学生実装課題")`）→ 3 段階のヒント → 動作確認（Mini）。
- Tiny での動作確認（期待値つき）は Phase 3 で追加（Phase 1 は Tiny に適用して表示するだけ）。
- `check()` は引数を `deepcopy` して比べ、関数が入力を書き換えたら `[NG]` にする。

## 7. 評価指標（Phase 3〜4 で実装）

| テーマ | 指標 |
| --- | --- |
| F-1A | 生涯所得、教育費控除後の累積所得、回収年齢 |
| F-1B | 世帯所得、年間収支、各人の自由時間、育児・介護時間の充足 |
| F-1C | 累積住宅費、年間住宅関連支出、（Level 3）資産価値、通勤時間、予算制約の充足 |
| F-1D | 各世代の資産残高、累積移転額、資産不足の年数、最低生活資金の充足 |
| 共通 | シナリオ数、実行時間、計算量、制約を満たした候補数 |

複数の指標が対立する場合（所得最大と自由時間重視など）は、どちらも「仮定の下での結果」として示す。
