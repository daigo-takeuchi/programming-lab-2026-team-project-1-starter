# 旧サブトピックの 4 分類への統合と移行計画（Phase 1）

## 1. 旧サブトピックと新テーマの対応表

旧 F1 の RQ・Advanced と、従来の F-1 のサブトピック候補を、次の 4 テーマに統合する。

| 旧サブトピック（候補） | 新テーマ | 位置づけ | 備考 |
| --- | --- | --- | --- |
| 職業選択 | F-1A | Level 1（候補の比較） | |
| 教育投資（進学・専門学校・大学） | F-1A | Level 1（Mini A/B/C）、Level 2（回収年齢） | 旧 RQ1 |
| 資格取得 | F-1A | Level 2（組合せ）・Level 3 | 旧 RQ2 |
| 転職 | F-1A | Level 2（全探索）・Level 3（時期の最適化） | 旧 RQ3 |
| 生涯所得と現在価値（NPV） | F-1A | Level 3（任意） | 旧 RQ4。F-2 との重複に注意 |
| 失業・休職のリスク（乱数） | F-1A | Level 3 | 旧 Advanced A・E |
| 所得以外の評価（労働時間） | F-1A／F-1B | Level 3 | 旧 Advanced C |
| 結婚・家族形成 | F-1B | Level 1（成人 2 人の世帯） | F-4 と重複しないよう、関係満足度は扱わない |
| 共働き・時短勤務・育児休業 | F-1B | Level 1・2（勤務形態の組合せ） | |
| 子育て（育児費・育児時間） | F-1B | Level 1（支出・時間）、Level 3（子の年齢で変化） | |
| 介護（家族内・外部サービス） | F-1B | Level 1（費用・時間）、Level 3（比較） | 子から親への介護支援は F-1D Level 3 とも関係 |
| 住宅取得（購入・賃貸） | F-1C | Level 1・2 | |
| 居住地の選択（通勤時間） | F-1C | Level 1（条件による探索） | |
| 住宅ローン | F-1C | Level 3 | 式の意味を説明してから使う |
| 住み替え | F-1C | Level 3 | |
| 世代間の人的資本の継承（教育資金） | F-1D | Level 1（資金移転）、Level 3 | 教育→所得の関係は仮定と明記 |
| 住宅・不動産の継承 | F-1D | Level 3 | |
| 金融資産の継承 | F-1D | Level 1（資産の移転）、Level 3 | 税・相続制度は扱わない |
| 事業承継・知的財産 | F-1D | Level 3 | |
| 子から親への生活支援・介護 | F-1D | Level 3 | |
| 3 世代モデル | F-1D | Level 3 | |
| 動的計画法による最適化 | ― | 演習Ⅱ以降の発展 | 必須にしない |
| 投資戦略・FIRE | ― | F-2 の範囲 | F-1 では扱わない |

## 2. 既存コード・データの移行先

| 既存 | 移行先 | 方法 |
| --- | --- | --- |
| 年収の式（`career_model.salary_at`） | F-1A 課題2 | 式・退職年齢の規則だけ採用し、学生が実装する（コードは移植しない） |
| 累積和（`income_analysis.total`・`cumulative`） | F-1A 課題3 | 同上 |
| 回収年齢（`income_analysis.payback_age`） | F-1A Level 2 `find_payback_age()` | 説明（単調でないので線形探索）を採用。Phase 3 でひな形化 |
| 順位付け（`optimization.rank`） | F-1A Level 2 `rank_careers()` | 安定ソートの説明を採用 |
| 転職年齢の全探索（`optimization.evaluate_switch_ages`） | F-1A Level 2 `search_career_plans()` | 全探索の構造を採用 |
| シナリオのコピー（`scenarios.with_changes`） | 全テーマの「入力を変更しない」規則 | simulation_rules に記載、`check()` で検出 |
| 感度分析・割引率（`experiments.py`） | F-1A Level 3 の候補 | 文書で紹介 |
| `data/sample_careers.json` | F-1A Tiny の分布の参考 | 値の範囲を参考にした |
| 倫理・限界（旧 README 17 章） | 新 README・第0章・各章 N.1 | Phase 5 で README に統合 |
| 教科書コード（`textbook/`） | 使わない | 新 Notebook は標準ライブラリだけで完結 |

## 3. 旧教材の扱い（教員の承認が必要）

| 対象 | 案 | 時期 |
| --- | --- | --- |
| 旧 `.py` 7 本・`tests/test_*.py` 4 本・`notebooks/`・`data/sample_careers.json` | `legacy/` へ移動、または現状維持（新 README で旧教材と明記） | Phase 5（承認後） |
| 旧 `README.md` | `docs/legacy/README_career_income.md` へ移し、新 README を作成 | Phase 5（承認後） |
| 親 README の F1 行・難易度 | 新名称・新難易度に更新 | Phase 5（承認後） |
| ディレクトリ名 | 現状維持（推奨）、または `f1-life-planning` などへ変更 | 教員判断 |

- 旧教材は**学生配布物（dist/）に含めない**（許可リスト方式）。
- 旧コードの完成解答は公開履歴に残る。削除しても履歴からは消えない。
