# データ品質の検証結果

`scripts/validate_datasets.py --report` が自動で作成する。

- エラー（データの破損）：0 件
- 境界条件（意図的に含めたケース。学生が検出する対象）：19 件

## エラー

- なし

## 境界条件（意図的）

- F-1A 昇給率 0 の候補
- F-1A 教育費 0 の候補
- F-1A 就業期間 0 年の候補
- F-1A 同じ生涯所得になる候補（条件がすべて同じ候補）
- F-1A 教育費を回収できない候補（比較対象 C21 に退職まで追いつかない：['C22']）
- F-1B 年間収支が黒字になる組合せ
- F-1B どの組合せでも赤字になる世帯
- F-1B 2 人とも休業しても必要な育児・介護時間を満たせない世帯（必要時間 > 182）
- F-1B 時間制約をちょうど満たす世帯（フルタイム 2 人で残り時間が 0、必要時間 102）
- F-1B フルタイム 2 人では時間制約に違反する世帯
- F-1B 所得の制約と時間の制約の両方を満たせる世帯
- F-1C 同じ価格の物件が複数
- F-1C 予算 3,000 万円と価格が等しい物件
- F-1C 通勤時間 60 分を超える物件（通勤時間の制約違反）
- F-1D 移転額 0
- F-1D 移転期間 0
- F-1D 親の年間収支が赤字
- F-1D 移転がなければ 5 年以内に子の資産不足が起きる家族
- F-1D 最低生活資金（例：1,000 万円）を維持できる親

## 情報

- f1a/career_options_tiny.csv：25 行 × 7 列、人工データ（Tiny）
- f1b/work_options_tiny.csv：6 行 × 4 列、人工データ（Tiny）
- f1b/household_scenarios_tiny.csv：25 行 × 6 列、人工データ（Tiny）
- f1c/housing_options_tiny.csv：30 行 × 7 列、人工データ（Tiny）
- f1d/family_members_tiny.csv：24 行 × 8 列、人工データ（Tiny）
- f1d/transfer_scenarios_tiny.csv：32 行 × 6 列、人工データ（Tiny）
- f1a/salary_by_age_small.csv：84 行 × 12 列、公開統計を加工（Small）、空欄 34 個（欠損・秘匿・該当なし）
- f1b/household_expenses_small.csv：156 行 × 8 列、公開統計を加工（Small）
- f1d/household_assets_small.csv：39 行 × 10 列、公開統計を加工（Small）
- f1d/learning_cost_small.csv：8 行 × 9 列、公開統計を加工（Small）、空欄 2 個（欠損・秘匿・該当なし）
- f1c/housing_prices_small.csv：なし（教員が手動で取得するデータ）
- F-1C 価格の範囲 1800〜5200 万円：予算 1700 ならすべて予算超過、5200 ならすべて予算以内（Notebook の動作確認で使う）
