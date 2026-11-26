# データ辞書（Tiny Dataset、初期版）

すべて教材のための人工データ（仮定値）です。金額は**万円**です。

## F-1A `f1a/career_options_tiny.csv`

| 列 | 型 | 単位 | 意味 |
| --- | --- | --- | --- |
| `career_id` | 文字列 | ― | 候補の ID（C01〜） |
| `career_name` | 文字列 | ― | 候補の名前（英語の識別名） |
| `start_age` | 整数 | 歳 | 就業開始年齢 |
| `retirement_age` | 整数 | 歳 | 退職年齢（この年齢の年からは所得なし） |
| `initial_salary` | 小数 | 万円／年 | 初年度年収（額面） |
| `annual_growth` | 小数 | 割合 | 年間昇給率（0.02 = 2%） |
| `education_cost` | 整数 | 万円 | 就業前の教育費の総額 |

## F-1B `f1b/work_options_tiny.csv`

| 列 | 型 | 単位 | 意味 |
| --- | --- | --- | --- |
| `option_id` | 文字列 | ― | 勤務形態の ID（W1〜） |
| `work_style` | 文字列 | ― | 勤務形態の名前 |
| `annual_income` | 整数 | 万円／年 | 年収（額面） |
| `weekly_work_hours` | 整数 | 時間／週 | 労働時間（通勤を含まない） |

## F-1B `f1b/household_scenarios_tiny.csv`

| 列 | 型 | 単位 | 意味 |
| --- | --- | --- | --- |
| `scenario_id` | 文字列 | ― | 世帯の条件の ID（S01〜） |
| `living_cost` | 整数 | 万円／年 | 生活費 |
| `childcare_cost` | 整数 | 万円／年 | 育児費（0 = 子どもがいない） |
| `eldercare_cost` | 整数 | 万円／年 | 介護費（0 = 介護がない） |
| `required_childcare_hours` | 整数 | 時間／週 | 世帯で必要な育児の時間 |
| `required_eldercare_hours` | 整数 | 時間／週 | 世帯で必要な介護の時間 |

## F-1C `f1c/housing_options_tiny.csv`

| 列 | 型 | 単位 | 意味 |
| --- | --- | --- | --- |
| `housing_id` | 文字列 | ― | 住宅の ID（H01〜） |
| `area` | 文字列 | ― | 地域の名前（架空） |
| `purchase_price` | 整数 | 万円 | 購入価格（総額） |
| `monthly_rent` | 小数 | 万円／月 | 同じ住宅を借りる場合の月額家賃 |
| `floor_area` | 整数 | ㎡ | 床面積 |
| `annual_maintenance_cost` | 整数 | 万円／年 | 購入した場合の年間維持費 |
| `commute_minutes` | 整数 | 分 | 通勤時間（片道） |

## F-1D `f1d/family_members_tiny.csv`

| 列 | 型 | 単位 | 意味 |
| --- | --- | --- | --- |
| `person_id` | 文字列 | ― | 人の ID（例：F01-P は家族 F01 の親） |
| `family_id` | 文字列 | ― | 家族の ID |
| `generation` | 整数 | ― | 世代（1 = 親、2 = 子） |
| `role` | 文字列 | ― | `parent`（親）／`child`（子） |
| `age` | 整数 | 歳 | シミュレーション開始時の年齢 |
| `annual_income` | 整数 | 万円／年 | 年収（額面） |
| `annual_expense` | 整数 | 万円／年 | 年間支出 |
| `initial_assets` | 整数 | 万円 | シミュレーション開始時の資産 |

## F-1D `f1d/transfer_scenarios_tiny.csv`

| 列 | 型 | 単位 | 意味 |
| --- | --- | --- | --- |
| `scenario_id` | 文字列 | ― | シナリオの ID（T01〜） |
| `sender_role` | 文字列 | ― | 資金を出す人（`parent`） |
| `receiver_role` | 文字列 | ― | 資金を受け取る人（`child`） |
| `annual_transfer` | 整数 | 万円／年 | 毎年の移転額 |
| `start_year` | 整数 | 年 | 移転を始める年（1 = 1 年目） |
| `duration_years` | 整数 | 年 | 移転を続ける年数 |
