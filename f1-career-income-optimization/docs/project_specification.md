# F-1 開発仕様（v1.0、Phase 5 終了時点）

## 1. 概要

| 項目 | 内容 |
| --- | --- |
| 名称 | キャリア・ライフイベント・世代間資源継承の意思決定と最適化 |
| 英語名 | Decision-Making and Optimization of Career Paths, Life Events, and Intergenerational Resource Transfer |
| 対象 | プログラミング演習Ⅰ（Python 基礎、留学生を含む） |
| 配布物 | `dist/f1-life-planning-starter/`（17 ファイル）：統合 Notebook `F1_life_planning_starter.ipynb`（全 4 テーマ）、README・TASKS・requirements、data の文書 3、Tiny 6、Small 4 |
| 進め方 | 全チームが第0〜3章 → 担当テーマ章（1 つ）→ 第8章。第9章は任意 |
| 学生実装課題 | 28 関数（各テーマ Level 1 が 4、Level 2 が 3）。1 チームが担当するのは 7 関数 |

## 2. Notebook の章構成

| 章 | 内容 | 状態 |
| --- | --- | --- |
| 第0章 | 目的、4 テーマ、最短の学習ルート表、セルの種類、作業時間の見積もり | 完成 |
| 第1章 | 実行環境の確認、import、データフォルダの探索、日本語フォント | 完成 |
| 第2章 | 4 種類のデータ、単位のルール、データの置き場所 | 完成 |
| 第3章 | 辞書のリスト、年次更新の考え方、入力を変更しない、共通関数、計算量の記号 | 完成 |
| 第4〜7章 | F-1A〜D（10 節、Level 1・2 の課題、Mini と Tiny の動作確認、グラフ、Small Dataset、公開統計への橋渡し演習、モデルの妥当性と限界、Level 3、独自機能の候補）。F-1B に Level 1 の練習 | 完成 |
| 第8章 | 組合せ数と計算量、実行時間の測り方、性能評価の共通ルール（8.3）、F-1A〜D の性能評価（8.4〜8.7：規模と時間の表・対数グラフ、結果の一致の確認、目的関数による結果の比較）、チーム開発、成果物 | 完成（Phase 4） |
| 第9章 | 複数テーマの統合（任意） | 骨格 |

## 3. 各テーマの設計

| | F-1A キャリア | F-1B 家族・時間 | F-1C 住宅 | F-1D 世代間移転 |
| --- | --- | --- | --- | --- |
| Level 1 | `calculate_working_years`、`salary_at_age`、`lifetime_income`、`summarize_careers` | `household_income`、`household_expense`、`annual_balance`、`free_hours` | `annual_rent`、`cumulative_rent`、`ownership_cost`、`find_candidates` | `annual_balance_of`、`transfer`、`update_assets`、`simulate_transfer` |
| Level 2 | `filter_careers`（線形探索）、`rank_careers`（ソート）、`find_payback_age`（累積和 + 線形探索） | `generate_work_pairs`（k² の全探索）、`find_feasible_plans`（制約による絞り込み）、`rank_plans`（ソート） | `sort_by_price`（安定な挿入ソート）、`count_affordable`（二分探索・upper bound）、`affordable_ids_binary`（境界 + 取り出し） | `generate_transfer_scenarios`（全探索）、`count_shortage_years`（数え上げ）、`find_feasible_transfers`（制約による絞り込み） |
| 教員提供の比較・表示 | Tiny の順位、回収年齢の一覧、累積所得のグラフ | Tiny 全世帯の判定表、収支と自由時間の散布図、`make_care_splits` | 賃貸と購入の表、価格のヒストグラムと散布図、線形と二分の結果比較、1 回／Q 回の時間比較 | シナリオ比較、親子の資産のグラフ、制約を守れるシナリオの表 |
| Level 3 の候補 | 公開賃金統計、資格取得の時期、転職時期、IT エンジニア、労働時間・失業リスク | 公開統計（家計調査）、子の年齢と支出、育児休業、外部サービス、所得と自由時間 | 実取引価格の探索、賃貸と購入の長期比較、ローン、複数条件、取得時期 | 教育資金、住宅の継承、3 世代、事業承継、子から親への支援 |
| Small Dataset | 賃金構造基本統計調査（84 行） | 家計調査（156 行） | 不動産取引価格（未取得） | 全国家計構造調査（39 行）、子供の学習費調査（8 行） |
| グラフ | 年齢別の累積所得 | 世帯所得と支出、計画の収支と自由時間 | 価格の分布、通勤時間と価格 | 親子の年次資産残高 |

## 4. 難易度の比較（Phase 3 終了時点、作業時間は設計上の見積もり）

| 観点 | F-1A | F-1B | F-1C | F-1D |
| --- | --- | --- | --- | --- |
| Level 1 の主な文法 | if、for、range、累乗、辞書のリスト | 辞書、関数の組合せ、定数とパラメータ | 掛け算、for、if（and） | タプル、for、if、関数の組合せ |
| Level 2 の主な文法 | 線形探索、挿入ソート／`sorted`、2 つの累積和 | 二重 for、`continue`、制約の組合せ、`sorted(key=)` | 挿入ソート（安定）、while による二分探索、スライス | 二重 for、数え上げ、`history[-1]` |
| 数学 | 中（累乗） | 低 | 低（二分探索の境界の考え方は中） | 低 |
| 制度の前提知識 | 低 | 低（時間の 4 区分の理解） | 低〜中（月額・年額・総額） | 低 |
| 学生のコード量（参照実装の関数本体の行数：L1 + L2） | 18 + 22 = 40 行 | 4 + 22 = 26 行 | 11 + 25 = 36 行 | 12 + 21 = 33 行 |
| 最も長い関数 | 9 行（課題6） | **16 行（課題6）** | 9 行（課題5） | 11 行（課題7） |
| 作業時間（見積もり） | L1 2.5〜3 h、L2 2〜3 h | L1 2 h、L2 2.5〜3 h | L1 2 h、L2 2.5〜3 h | L1 2.5〜3 h、L2 2〜3 h |

- F-1B は Level 1 が各 1 行の加減算で、4 テーマで最も短い。Phase 4 で、課題1〜4 を for 文で繰り返し使う**練習**（【練習：Level 1】、新しい関数なし、TODO 6 か所）を 5.7 に加え、Tiny 25 世帯の所得・支出・収支・各人の残り時間・時間の制約違反を `tiny_results` にまとめさせた（期待値つきの確認 6 件）。課題6 は分割せず、説明・TODO・ヒントを「所得の制約 → 各人の時間の制約 → 育児・介護の時間の充足 → 候補の保存」の 4 段階にした。
- F-1D は親子 2 人のモデルを維持し、移転期間（`duration_years`）だけを Level 1 課題4 に入れた。
- 実際の難易度は、Phase 4 で参照実装の行数・学生の試行で再調整する。

## 5. 共通データ構造（Mini と Tiny で統一）

辞書とリストだけを使う（クラスは使わない）。Mini の辞書のキーは、同じ意味の Tiny の列名と一致させた（`tests/test_f1_synthetic_data.py` で検査）。

| データ | 主なキー |
| --- | --- |
| キャリア候補 | `career_id`, `career_name`, `start_age`, `retirement_age`, `initial_salary`, `annual_growth`, `education_cost` |
| 勤務形態 | `option_id`, `work_style`, `annual_income`, `weekly_work_hours` |
| 世帯の条件 | `scenario_id`, `living_cost`, `childcare_cost`, `eldercare_cost`, `required_childcare_hours`, `required_eldercare_hours` |
| 住宅候補 | `housing_id`, `area`, `purchase_price`, `monthly_rent`, `floor_area`, `annual_maintenance_cost`, `commute_minutes` |
| 家族構成 | `person_id`, `family_id`, `generation`, `role`（`parent`/`child`）, `age`, `annual_income`, `annual_expense`, `initial_assets` |
| 資源移転シナリオ | `annual_transfer`, `start_year`, `duration_years`（Tiny はさらに `scenario_id`, `sender_role`, `receiver_role`） |
| 候補の集計結果（F-1A） | `career_id`, `lifetime_income`, `net_income` |
| 計画（F-1B） | `option_a`, `option_b`, `care_a`, `care_b`, `balance`, `free_a`, `free_b`, `free_total` |
| 年次資産残高（F-1D） | `year`, `parent_assets`, `child_assets` |
| シナリオ評価（F-1D） | `annual_transfer`, `duration_years`, `parent_final_assets`, `child_final_assets`, `child_shortage_years` |

## 6. 学生実装課題の形式

- 表（関数・引数・戻り値・例）→ ひな形（TODO + `raise NotImplementedError("学生実装課題")`）→ 3 段階のヒント（折りたたみ）→ Mini の動作確認。
- 各テーマに Tiny の動作確認を 2 か所（Level 1・Level 2）。期待値は手計算または教員用参照実装で確かめた値を直接書く。
- 動作確認の入力（組合せのリストなど）は、学生の関数を使わずに**リテラルで**用意する（解答の形を見せない）。Tiny の Level 2 の一部は、学生の前の課題の結果を `run_if_implemented` で使う。
- `check()` は引数を `deepcopy` して比べ、関数が入力を書き換えたら `[NG]`。小数は相対誤差 1e-6 まで許す。

## 7. 評価指標

| テーマ | 指標（実装済み） |
| --- | --- |
| F-1A | 生涯所得、教育費控除後の累積所得、回収年齢 |
| F-1B | 年間収支、各人の残り時間、2 人の残り時間の合計、育児・介護時間の充足 |
| F-1C | 累積家賃、購入費用、予算・通勤の条件の充足、予算以下の件数 |
| F-1D | 親子の年末資産、親の最低生活資金の充足、子の資産不足の年数 |
| 共通 | シナリオ数、実行時間（6.8 の簡易比較。本格的な比較は Phase 4） |
