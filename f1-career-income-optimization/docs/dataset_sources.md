# データの出典一覧

## 1. 人工データ（教材用、Phase 1 初期版）

| ファイル | 生成方法 | 件数 | 性質 |
| --- | --- | ---: | --- |
| Notebook 内の Mini Dataset（第4〜7章） | 手で作成 | 3〜5 | 人工データ（仮定値）。手計算で確認できる値 |
| `data/f1a/career_options_tiny.csv` | `scripts/generate_synthetic_data.py`（シード 2026） | 24 | 人工データ。昇給率 0、回収できない教育費、就業 1 年、同じ値の候補を含む |
| `data/f1b/work_options_tiny.csv` | 同上（固定値） | 6 | 人工データ。休業（年収 0）を含む |
| `data/f1b/household_scenarios_tiny.csv` | 同上（シード 2028） | 24 | 人工データ。育児のみ・介護のみ・両方・なし、時間制約違反、支出過大を含む |
| `data/f1c/housing_options_tiny.csv` | 同上（シード 2029） | 30 | 人工データ。同じ価格の物件を含む |
| `data/f1d/family_members_tiny.csv` | 同上（シード 2030） | 24 | 人工データ。12 家族 × 親子。赤字の親を含む |
| `data/f1d/transfer_scenarios_tiny.csv` | 同上（組合せ） | 24 | 人工データ。移転額 0・50・100・150 × 開始年 1・3 × 期間 2・4・6 |

## 2. 公開統計（Phase 2 で取得予定。未取得）

| 予定ファイル | 原データ | 提供機関 | URL | 利用条件 | 状態 |
| --- | --- | --- | --- | --- | --- |
| `data/f1a/salary_by_age_small.csv` | 賃金構造基本統計調査（令和7年） | 厚生労働省 | https://www.e-stat.go.jp/stat-search/files?toukei=00450091 | e-Stat 利用規約（政府標準利用規約 第2.0版） | 未取得 |
| `data/f1b/household_expenses_small.csv` | 家計調査（家計収支編）、社会生活基本調査（令和3年） | 総務省 | toukei=00200561、00200533 | 同上 | 未取得 |
| `data/f1c/housing_prices_small.csv` | 不動産取引価格情報 | 国土交通省 | https://www.reinfolib.mlit.go.jp/ | 公共データ利用規約（第1.0版） | 未取得 |
| `data/f1d/household_assets_small.csv` | 全国家計構造調査（令和6年）、子供の学習費調査（令和5年度） | 総務省、文部科学省 | toukei=00200564、mext.go.jp | e-Stat 利用規約ほか（学習費調査の条件は未確認） | 未取得 |

出典の記載例（加工した場合）：
「出典：厚生労働省「令和7年賃金構造基本統計調査」（政府統計の総合窓口(e-Stat)、https://www.e-stat.go.jp/）を加工して作成」

## 3. 参照日

すべて 2026-11-27 に閲覧。
