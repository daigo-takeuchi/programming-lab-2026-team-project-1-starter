# F-1 のデータ

このフォルダには、F-1 の演習で使う CSV ファイルがあります。文字コードは UTF-8 です。

| 種類 | ファイル名の終わり | 内容 |
| --- | --- | --- |
| 人工データ（Tiny Dataset） | `_tiny.csv` | 教材のために作った**仮定値**。実際の統計・物件・人物ではありません。Level 1・2 で使います |
| 公開統計を加工したデータ（Small Dataset） | `_small.csv` | 政府の公開統計から必要な項目を取り出したもの。Level 3 で使います（なくても Level 1・2 は進められます） |

| フォルダ | ファイル | 行数 | 種類 |
| --- | --- | ---: | --- |
| `f1a/` | `career_options_tiny.csv` | 25 | 人工（キャリア候補） |
| `f1a/` | `salary_by_age_small.csv` | 84 | 公開統計（賃金構造基本統計調査） |
| `f1b/` | `work_options_tiny.csv` | 6 | 人工（勤務形態） |
| `f1b/` | `household_scenarios_tiny.csv` | 25 | 人工（世帯の条件） |
| `f1b/` | `household_expenses_small.csv` | 156 | 公開統計（家計調査） |
| `f1c/` | `housing_options_tiny.csv` | 30 | 人工（住宅候補） |
| `f1d/` | `family_members_tiny.csv` | 24 | 人工（12 家族 × 親子） |
| `f1d/` | `transfer_scenarios_tiny.csv` | 32 | 人工（資金移転のシナリオ） |
| `f1d/` | `household_assets_small.csv` | 39 | 公開統計（全国家計構造調査） |
| `f1d/` | `learning_cost_small.csv` | 8 | 公開統計（子供の学習費調査） |

- 各ファイルの行数・列数・列の意味・単位・入力例・欠損・限界は `data_dictionary.md`、公開統計の出典と利用条件は `dataset_sources.md` を見てください。
- 公開統計の平均値は、特定の人や家族の将来を予測するものではありません。
- 公開統計の CSV の空欄は「統計がない・秘匿・該当なし」を表します。0 ではありません。
- F-1C の実際の不動産取引価格（`f1c/housing_prices_small.csv`）は、授業で用意された場合だけあります。

## 公開統計の出典（Small Dataset）

次の統計を加工して作成しました（政府統計の総合窓口(e-Stat)、https://www.e-stat.go.jp/ 、2026年11月27日に利用）。
利用条件は e-Stat の利用規約（政府標準利用規約 第2.0版、CC BY 4.0 互換）です。加工したデータは、国が作成したものではありません。

| ファイル | 出典 | 加工内容 |
| --- | --- | --- |
| `f1a/salary_by_age_small.csv` | 厚生労働省「令和7年賃金構造基本統計調査」 | 男女計・産業計の学歴・年齢階級別の給与を抜き出し、万円に換算 |
| `f1b/household_expenses_small.csv` | 総務省統計局「家計調査（家計収支編）2025年」 | 二人以上の世帯の世帯主の年齢階級別の支出を抜き出し、万円／月に換算 |
| `f1d/household_assets_small.csv` | 総務省統計局「令和6年全国家計構造調査」 | 世帯主の年齢階級別の資産・負債を抜き出し、万円に換算 |
| `f1d/learning_cost_small.csv` | 文部科学省「令和5年度子供の学習費調査」 | 学校種別の学習費を抜き出し、万円に換算 |
