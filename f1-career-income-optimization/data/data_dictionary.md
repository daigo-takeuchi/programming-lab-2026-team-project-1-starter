# データ辞書

金額は**万円**です。`_tiny.csv` は教材のために作った**人工データ（仮定値）**、
`_small.csv` は**公開統計を加工したデータ**です。数値の列の**空欄**は「統計がない・秘匿・該当なし」を表し、0 ではありません。

Notebook の Mini Dataset（第4〜7章）は、同じ意味の項目に同じキー名を使っています。

## ファイルの一覧（概要）

| ファイル | 種類 | 行数 | 列数 | 空欄（欠損） | 出典・利用条件 | 加工内容 |
| --- | --- | ---: | ---: | --- | --- | --- |
| `f1a/career_options_tiny.csv` | 人工データ | 25 | 7 | なし | 教材用に作成（仮定値） | ― |
| `f1b/work_options_tiny.csv` | 人工データ | 6 | 4 | なし | 同上 | ― |
| `f1b/household_scenarios_tiny.csv` | 人工データ | 25 | 6 | なし | 同上 | ― |
| `f1c/housing_options_tiny.csv` | 人工データ | 30 | 7 | なし | 同上 | ― |
| `f1d/family_members_tiny.csv` | 人工データ | 24 | 8 | なし | 同上 | ― |
| `f1d/transfer_scenarios_tiny.csv` | 人工データ | 32 | 6 | なし | 同上 | ― |
| `f1a/salary_by_age_small.csv` | 公開統計 | 84 | 12 | 34 個（年齢階級の端 14、統計がない「－」20） | 厚生労働省「令和7年賃金構造基本統計調査」（e-Stat 利用規約） | 男女計・産業計を抜き出し、千円 → 万円 |
| `f1b/household_expenses_small.csv` | 公開統計 | 156 | 8 | なし | 総務省統計局「家計調査（家計収支編）」2025 年（同上） | 二人以上の世帯を抜き出し、円 → 万円、縦長の形式 |
| `f1d/household_assets_small.csv` | 公開統計 | 39 | 10 | なし | 総務省統計局「令和6年全国家計構造調査」（同上） | 主な資産・負債を抜き出し、千円 → 万円 |
| `f1d/learning_cost_small.csv` | 公開統計 | 8 | 9 | 2 個（高等学校の学校給食費：調査対象外） | 文部科学省「令和5年度子供の学習費調査」（同上） | 学校種別の学習費を抜き出し、円 → 万円 |

- 出典の詳しい情報（公式 URL・統計表名・取得日・利用条件・出典の書き方）は `dataset_sources.md` にあります。
- **空欄は 0 ではありません。** `load_csv()` で読み込むと、数値の列の空欄は `None` になります。計算の前に、空欄の扱いを決めてください。
- 人工データの値は教材のための**仮定値**です。公開統計の値は**平均値**で、特定の人・家族を表しません。

## 入力例（各ファイルの 1 行目）

```text
f1a/career_options_tiny.csv        C01,high_school_job_1,18,60,255,0.02,0
f1b/work_options_tiny.csv          W1,full_time,400,40
f1b/household_scenarios_tiny.csv   S01,390,50,0,35,0
f1c/housing_options_tiny.csv       H01,area_A,3000,9.6,50,40,90
f1d/family_members_tiny.csv        F01-P,F01,1,parent,52,480,360,2900
f1d/transfer_scenarios_tiny.csv    T01,parent,child,0,1,0
f1a/salary_by_age_small.csv        all,学歴計,～19歳,,19,19,22.53,20.83,14.98,17868,2025,wage_census_2025
f1b/household_expenses_small.csv   ～34歳,household_size,世帯人員,3.28,人,2025,二人以上の世帯,family_income_expenditure_2025
f1d/household_assets_small.csv     all,総世帯,30歳未満,25.9,1.32,315.7,219.7,327.9,2024,national_survey_family_income_2024
f1d/learning_cost_small.csv        幼稚園,public,公立,18.4646,6.9362,1.5235,10.0049,2023年度,learning_cost_survey_2023
```

## モデル上の限界（データごと）

| ファイル | 注意すること |
| --- | --- |
| 人工データ（Tiny） | 実在の人・家族・住宅ではない。境界条件（同じ値、0、ちょうど条件を満たす値など）を確かめるために作った値 |
| `salary_by_age_small.csv` | 2025 年の異なる年齢の人の平均（横断的）。同じ人の生涯の推移ではない。学歴の差を因果関係と断定しない。賞与は前年分 |
| `household_expenses_small.csv` | 二人以上の世帯の平均。世帯人員は年齢階級で違う。月額なので年額にするには 12 倍する。教育費は消費支出に含まれる |
| `household_assets_small.csv` | 平均値は資産の多い世帯の影響で大きくなりがち。年齢階級の違う値は**別々の世帯**の平均で、親子のデータではない |
| `learning_cost_small.csv` | 子供 1 人・1 年あたりの平均。在学年数や進学先は自分で仮定する |

---

## 人工データ（Tiny Dataset）

### F-1A `f1a/career_options_tiny.csv`（25 行）

| 列 | 型 | 単位 | 意味 |
| --- | --- | --- | --- |
| `career_id` | 文字列 | ― | 候補の ID（C01〜C25） |
| `career_name` | 文字列 | ― | 候補の名前（英語の識別名） |
| `start_age` | 整数 | 歳 | 就業開始年齢（この年は初年度年収。昇給は翌年から） |
| `retirement_age` | 整数 | 歳 | 退職年齢（この年齢の年からは所得なし） |
| `initial_salary` | 小数 | 万円／年 | 初年度年収（額面） |
| `annual_growth` | 小数 | 割合 | 年間昇給率（0.02 = 2%） |
| `education_cost` | 整数 | 万円 | 教育費の総額（この教材では 18 歳の年にまとめて払うと仮定） |

境界条件：C21 昇給率 0、C21・C24 同じ条件（同じ生涯所得）、C22 教育費を回収できない、C25 就業期間 0。

### F-1B `f1b/work_options_tiny.csv`（6 行）

| 列 | 型 | 単位 | 意味 |
| --- | --- | --- | --- |
| `option_id` | 文字列 | ― | 勤務形態の ID（W1〜W6） |
| `work_style` | 文字列 | ― | 勤務形態の名前 |
| `annual_income` | 整数 | 万円／年 | 年収（額面） |
| `weekly_work_hours` | 整数 | 時間／週 | 労働時間（**通勤を含む**） |

### F-1B `f1b/household_scenarios_tiny.csv`（25 行）

| 列 | 型 | 単位 | 意味 |
| --- | --- | --- | --- |
| `scenario_id` | 文字列 | ― | 世帯の条件の ID（S01〜S25） |
| `living_cost` | 整数 | 万円／年 | 生活費 |
| `childcare_cost` | 整数 | 万円／年 | 育児費（0 = 子どもがいない） |
| `eldercare_cost` | 整数 | 万円／年 | 介護費（0 = 介護がない） |
| `required_childcare_hours` | 整数 | 時間／週 | 世帯で必要な育児の時間（育児に直接伴う家事を含む） |
| `required_eldercare_hours` | 整数 | 時間／週 | 世帯で必要な介護の時間（介護に直接伴う家事を含む） |

境界条件：S23 2 人とも休業しても時間が足りない、S24 どの組合せでも赤字、S25 フルタイム 2 人で残り時間がちょうど 0。

### F-1C `f1c/housing_options_tiny.csv`（30 行）

| 列 | 型 | 単位 | 意味 |
| --- | --- | --- | --- |
| `housing_id` | 文字列 | ― | 住宅の ID（H01〜H30） |
| `area` | 文字列 | ― | 地域の名前（架空） |
| `purchase_price` | 整数 | 万円 | 購入価格（総額） |
| `monthly_rent` | 小数 | 万円／月 | 同じ住宅を借りる場合の月額家賃 |
| `floor_area` | 整数 | ㎡ | 床面積 |
| `annual_maintenance_cost` | 整数 | 万円／年 | 購入した場合の年間維持費 |
| `commute_minutes` | 整数 | 分 | 通勤時間（片道） |

境界条件：3,000 万円ちょうどの物件 4 件（同じ価格の物件が複数）、通勤 60 分超の物件。価格の範囲 1,800〜5,200 万円。

### F-1D `f1d/family_members_tiny.csv`（24 行 = 12 家族 × 親子）

| 列 | 型 | 単位 | 意味 |
| --- | --- | --- | --- |
| `person_id` | 文字列 | ― | 人の ID（例：F01-P は家族 F01 の親、F01-C は子） |
| `family_id` | 文字列 | ― | 家族の ID |
| `generation` | 整数 | ― | 世代（1 = 親、2 = 子） |
| `role` | 文字列 | ― | `parent`（親）／`child`（子） |
| `age` | 整数 | 歳 | シミュレーション開始時の年齢 |
| `annual_income` | 整数 | 万円／年 | 年収（額面） |
| `annual_expense` | 整数 | 万円／年 | 年間支出 |
| `initial_assets` | 整数 | 万円 | シミュレーション開始時の資産（初期資産） |

### F-1D `f1d/transfer_scenarios_tiny.csv`（32 行）

| 列 | 型 | 単位 | 意味 |
| --- | --- | --- | --- |
| `scenario_id` | 文字列 | ― | シナリオの ID（T01〜T32） |
| `sender_role` | 文字列 | ― | 資金を出す人（`parent`） |
| `receiver_role` | 文字列 | ― | 資金を受け取る人（`child`） |
| `annual_transfer` | 整数 | 万円／年 | 毎年の移転額（0 を含む） |
| `start_year` | 整数 | 年 | 移転を始める年（1 = 1 年目。3 は発展課題用） |
| `duration_years` | 整数 | 年 | 移転を続ける年数（0 を含む） |

---

## 公開統計を加工したデータ（Small Dataset）

### F-1A `f1a/salary_by_age_small.csv`（84 行）

出典：厚生労働省「令和7年賃金構造基本統計調査」（政府統計の総合窓口(e-Stat)、https://www.e-stat.go.jp/）を加工して作成。
一般労働者、民営事業所、企業規模 10 人以上、産業計、男女計の平均値。

| 列 | 型 | 単位 | 意味 |
| --- | --- | --- | --- |
| `education_code` | 文字列 | ― | 学歴の識別名（`all`、`junior_high`、`high_school`、`vocational`、`college`、`university`、`graduate`） |
| `education` | 文字列 | ― | 学歴（原データの区分名） |
| `age_group` | 文字列 | ― | 年齢階級（原データの区分名） |
| `age_min`・`age_max` | 整数 | 歳 | 年齢階級の下限・上限（「～19歳」の下限と「70歳～」の上限は空欄） |
| `mean_age` | 小数 | 歳 | 平均年齢 |
| `monthly_cash_earnings` | 小数 | 万円／月 | きまって支給する現金給与額（残業代などを含む月額） |
| `monthly_scheduled_earnings` | 小数 | 万円／月 | 所定内給与額（残業代などを含まない月額） |
| `annual_special_earnings` | 小数 | 万円／年 | 年間賞与その他特別給与額（前年 1 年間の額） |
| `workers_10` | 小数 | 十人 | 労働者数（推計） |
| `survey_year` | 整数 | 年 | 調査年（2025） |
| `source` | 文字列 | ― | 出典の識別名 |

### F-1B `f1b/household_expenses_small.csv`（156 行）

出典：総務省統計局「家計調査（家計収支編）」2025 年（e-Stat）を加工して作成。二人以上の世帯、1 世帯当たり 1 か月間の平均。

| 列 | 型 | 単位 | 意味 |
| --- | --- | --- | --- |
| `age_group` | 文字列 | ― | 世帯主の年齢階級 |
| `category_code` | 文字列 | ― | 項目の識別名（`consumption_total`、`food`、`housing`、`education` など） |
| `category` | 文字列 | ― | 項目（原データの名前） |
| `value` | 小数 | `unit` の列 | 値 |
| `unit` | 文字列 | ― | `万円/月`（支出）または `人`（世帯人員・18 歳未満人員） |
| `survey_year` | 整数 | 年 | 調査年（2025） |
| `household_type` | 文字列 | ― | 世帯の種類（二人以上の世帯） |
| `source` | 文字列 | ― | 出典の識別名 |

### F-1D `f1d/household_assets_small.csv`（39 行）

出典：総務省統計局「令和6年全国家計構造調査」（e-Stat）を加工して作成。1 世帯当たりの平均（世帯区分は全世帯、世帯主の性別は平均）。

| 列 | 型 | 単位 | 意味 |
| --- | --- | --- | --- |
| `household_type_code`・`household_type` | 文字列 | ― | 世帯の種類（`all` 総世帯、`two_or_more` 二人以上の世帯、`single` 単身世帯） |
| `head_age_group` | 文字列 | ― | 世帯主の年齢階級（5 歳階級） |
| `head_mean_age` | 小数 | 歳 | 世帯主の平均年齢 |
| `household_size` | 小数 | 人 | 世帯人員 |
| `financial_assets` | 小数 | 万円 | 金融資産残高（貯蓄現在高） |
| `financial_liabilities` | 小数 | 万円 | 金融負債残高 |
| `housing_land_assets` | 小数 | 万円 | 住宅・宅地資産額 |
| `survey_year` | 整数 | 年 | 調査年（2024） |
| `source` | 文字列 | ― | 出典の識別名 |

### F-1D `f1d/learning_cost_small.csv`（8 行）

出典：文部科学省「令和5年度子供の学習費調査」（e-Stat）を加工して作成。子供 1 人当たりの年間の平均額。

| 列 | 型 | 単位 | 意味 |
| --- | --- | --- | --- |
| `school_type` | 文字列 | ― | 学校種（幼稚園・小学校・中学校・高等学校（全日制）） |
| `ownership_code`・`ownership` | 文字列 | ― | 設置者（`public` 公立、`private` 私立） |
| `total_cost` | 小数 | 万円／年 | 学習費総額 |
| `school_education_cost` | 小数 | 万円／年 | 学校教育費 |
| `school_lunch_cost` | 小数 | 万円／年 | 学校給食費（高等学校は空欄：調査対象外） |
| `out_of_school_cost` | 小数 | 万円／年 | 学校外活動費 |
| `survey_year` | 文字列 | ― | 調査年度（2023年度） |
| `source` | 文字列 | ― | 出典の識別名 |

### F-1C `f1c/housing_prices_small.csv`（教員が用意した場合だけ）

出典：国土交通省「不動産情報ライブラリ」不動産取引価格情報を加工。取引価格（`price`、万円）、面積（`floor_area`、㎡）、
取引時期、市区町村名、地区名、種類、建築年。**家賃・通勤時間は含まれません。**
