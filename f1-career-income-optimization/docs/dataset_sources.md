# データの出典一覧

## 1. 人工データ（教材用）

| ファイル | 生成方法 | 行数 | 性質 |
| --- | --- | ---: | --- |
| Notebook 内の Mini Dataset（第4〜7章） | 手で作成 | 2〜6 | 人工データ（仮定値）。手計算で確認できる値 |
| `data/f1a/career_options_tiny.csv` | `scripts/generate_synthetic_data.py`（シード 2026） | 25 | 昇給率 0、教育費 0、就業期間 0、同じ生涯所得、回収できない教育費を含む |
| `data/f1b/work_options_tiny.csv` | 同上（固定値） | 6 | 休業（年収 0）を含む |
| `data/f1b/household_scenarios_tiny.csv` | 同上（シード 2028） | 25 | 黒字・赤字、時間制約をちょうど満たす（S25）・違反する（S23）世帯を含む |
| `data/f1c/housing_options_tiny.csv` | 同上（シード 2029） | 30 | 3,000 万円ちょうどの物件 4 件、通勤 60 分超を含む |
| `data/f1d/family_members_tiny.csv` | 同上（シード 2030） | 24 | 12 家族 × 親子。赤字の親を含む |
| `data/f1d/transfer_scenarios_tiny.csv` | 同上（組合せ） | 32 | 移転額 0・50・100・150 × 開始年 1・3 × 期間 0・2・4・6 |

検証：`scripts/validate_datasets.py`（結果は `docs/data_validation_report.md`）。

## 2. 公開統計（Small Dataset）

| ファイル | 原データ | 提供機関 | URL（statInfId） | 利用条件 | 状態 |
| --- | --- | --- | --- | --- | --- |
| `data/f1a/salary_by_age_small.csv` | 賃金構造基本統計調査（令和7年）一般労働者 産業大分類「学歴、年齢階級別きまって支給する現金給与額、所定内給与額及び年間賞与その他特別給与額」 | 厚生労働省 | https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040420843&fileKind=4 | e-Stat 利用規約（政府標準利用規約 第2.0版、CC BY 4.0 互換） | **取得・前処理済み**（84 行） |
| `data/f1b/household_expenses_small.csv` | 家計調査（家計収支編）2025 年 第3-2表「世帯主の年齢階級別1世帯当たり1か月間の収入と支出」 | 総務省統計局 | statInfId=000040409533 | 同上 | **取得・前処理済み**（156 行） |
| `data/f1d/household_assets_small.csv` | 令和6年全国家計構造調査 表番号4-4 | 総務省統計局 | statInfId=000040488257 | 同上 | **取得・前処理済み**（39 行） |
| `data/f1d/learning_cost_small.csv` | 令和5年度子供の学習費調査「1 学校種別の学習費」 | 文部科学省 | statInfId=000040233659 | 同上（e-Stat 掲載の統計表） | **取得・前処理済み**（8 行） |
| `data/f1c/housing_prices_small.csv` | 不動産取引価格情報 | 国土交通省 | https://www.reinfolib.mlit.go.jp/realEstatePrices/ | 公共データ利用規約（第1.0版） | **未取得**（教員が Web 画面で取得。手順は `docs/preprocessing_report.md` 5 章） |
| （なし） | 令和3年社会生活基本調査（生活時間） | 総務省統計局 | toukei=00200533 | e-Stat 利用規約 | 取得していない（任意） |

e-Stat のダウンロード URL は `https://www.e-stat.go.jp/stat-search/file-download?statInfId=<ID>&fileKind=<種類>`（登録不要）。

出典の記載例（加工した場合）：
「出典：厚生労働省「令和7年賃金構造基本統計調査」（政府統計の総合窓口(e-Stat)、https://www.e-stat.go.jp/）を加工して作成」

## 3. 参照日・取得日

公式ページの閲覧と原データの取得は 2026-11-27。取得の記録は `data/raw/download_log.csv`（Git 管理外）。

## 4. 再配布条件の個別確認（2026-11-27、Phase 4・5 開始時）

4 ファイルとも e-Stat（政府統計の総合窓口）のファイルダウンロードで取得した。各ファイルについて、e-Stat と作成府省の利用規約を確認した。

| 確認先 | 規約 | 統計の数値表について | 例外（別の利用ルール・第三者の権利） |
| --- | --- | --- | --- |
| e-Stat https://www.e-stat.go.jp/terms-of-use | 政府標準利用規約（第2.0版）準拠、CC BY 4.0 互換。複製・公衆送信・翻案・商用利用が可能 | 「数値データ、簡単な表・グラフ等は著作権の対象ではありません」と明記 | ロゴ・キャラクター、API・GIS・e-Micro・調査票情報提供の規約。統計表のファイルは対象外 |
| 厚生労働省 https://www.mhlw.go.jp/chosakuken/index.html ・別紙 exhibit.html | 公共データ利用規約（第1.0版）準拠 | 数値データの明記はない（e-Stat の規約で確認） | 別紙はシンボルマーク 3 種と労働委員会のデータベース 2 種だけ。賃金構造基本統計調査は含まれない |
| 総務省統計局 https://www.stat.go.jp/info/riyou.html | 公共データ利用規約（第1.0版）準拠 | 「数値データ、簡単な表・グラフ等は著作権の対象ではありません」と明記 | 別紙はシンボルマーク・キャラクターと、「日本の統計」等の写真・画像。家計調査・全国家計構造調査の統計表は含まれない |
| 文部科学省 https://www.mext.go.jp/b_menu/1351168.htm | 公共データ利用規約（第1.0版）準拠、CC BY 4.0 互換 | 同上の明記あり | ロゴ・キャラクター、第三者の権利を持つ写真等。子供の学習費調査の統計表は該当しない |

原データの Excel を検索し、「著作」「転載」「第三者」などの権利表記がないことを確かめた（注記は数値の定義だけ）。

| ファイル | 統計表 | 調査年 | 公式 URL | 取得日 | 加工内容 | 判断 |
| --- | --- | --- | --- | --- | --- | --- |
| `salary_by_age_small.csv` | 賃金構造基本統計調査 一般労働者 産業大分類「学歴、年齢階級別きまって支給する現金給与額、所定内給与額及び年間賞与その他特別給与額」（産業計） | 令和7年（2025） | https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040420843&fileKind=4 | 2026-11-27 | 男女計・産業計だけを抜き出し、千円を万円に換算。列名を英語に | **収録可** |
| `household_expenses_small.csv` | 家計調査（家計収支編）二人以上の世帯 詳細結果表「世帯主の年齢階級別」 | 2025 年 | https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040409533&fileKind=0 | 2026-11-27 | 二人以上の世帯の年齢階級 12 × 13 項目（世帯人員・消費支出・10 大費目など）を抜き出し、円を万円に換算、縦長の形式に | **収録可** |
| `household_assets_small.csv` | 全国家計構造調査 表番号4-4「世帯主の年齢階級，資産・負債の種類別1世帯当たり資産現在高・負債現在高」 | 令和6年（2024） | https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040488257&fileKind=0 | 2026-11-27 | 全世帯・性別平均の世帯の種類 3 × 年齢階級 13 の主な資産・負債を抜き出し、千円を万円に換算（純資産などの計算値は除外） | **収録可** |
| `learning_cost_small.csv` | 子供の学習費調査「1 学校種別の学習費」 | 令和5年度（2023） | https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040233659&fileKind=0 | 2026-11-27 | 幼稚園〜高等学校 × 公立・私立の学習費総額と内訳を抜き出し、円を万円に換算 | **収録可** |

除外したファイルはない。不動産取引価格（F-1C）は未取得のため収録しない。原データ（`data/raw/`）は引き続き Git 管理外。

配布物での出典の記載（`data/README.md` と Notebook の Small Dataset の節）：

- 出典：厚生労働省「令和7年賃金構造基本統計調査」、総務省統計局「家計調査（家計収支編）2025年」「令和6年全国家計構造調査」、文部科学省「令和5年度子供の学習費調査」（政府統計の総合窓口(e-Stat)、https://www.e-stat.go.jp/ 、2026年11月27日に利用）を加工して作成
- 加工したデータを国が作成したものとして示さない。
