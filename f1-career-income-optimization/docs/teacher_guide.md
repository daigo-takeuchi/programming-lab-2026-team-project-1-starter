# 教員ガイド：F-1 キャリア・ライフイベント・世代間資源継承の意思決定と最適化

学生には配布しない文書です。学生向けの説明は `README.md`・`TASKS.md`、開発のルールは `CLAUDE.md` にあります。

## 1. 教材の構成

| 項目 | 内容 |
| --- | --- |
| Notebook | `F1_life_planning_starter.ipynb`（第0〜9章、Markdown 242・コード 124 セル）。マスターは `scripts/build_notebook.py` |
| 学生実装課題 | 28 関数（4 テーマ × Level 1 が 4・Level 2 が 3）。1 チームが実装するのは 7 関数 |
| 練習 | F-1B の【練習：Level 1】1 つ（関数を作らず、課題1〜4 を for 文で使う） |
| Level 3 | 各テーマに発展案 5、公開統計への橋渡し演習 1、独自機能の候補 4、モデルの妥当性と限界の表 |
| 性能評価 | 第8章 8.3（共通ルール）、8.4〜8.7（テーマ別） |
| 参照実装 | `solutions/reference_solutions.py`（Git 管理外）。誤りの例は `solutions/student_mistakes.py`（Git 管理外） |

`solutions/` は Git で管理していません。教員の PC を移す・複数の教員で共有する場合は、Git 以外の方法（LMS の教員用領域など）で渡してください。

## 2. 授業の前に教員が行うこと

### 2.1 事前試行（学生と同じ手順で）

`docs/educational_validation_report.md` の 4 章のチェックリストを使います。推奨する試行は次の 2 つです。

1. **F-1B**：Level 1（課題1〜4）→ 練習 → 課題5〜7（基本計算から制約付き探索への移行）
2. **F-1C**：課題4（線形探索）→ 課題5〜7（ソートと二分探索）→ 第8章 8.6（線形探索から二分探索への移行）

配布用 ZIP を展開した**別のフォルダ**で、学生と同じ環境（VS Code・Jupyter・Colab のうち授業で使うもの）で行います。
参照実装は見ずに実装し、つまずいた箇所とヒントの何段階目で解決したかを記録します。

### 2.2 TASKS.md の教員記入項目

| 項目 | 書く内容の例 |
| --- | --- |
| テーマの選び方 | 希望調査、抽選、テーマごとのチーム数の上限 |
| 提出方法・提出期限 | LMS／チームの GitHub リポジトリ、日時 |
| 発表資料の形式・発表時間 | スライド（PDF）、1 チーム 10 分＋質疑 5 分 |
| 正式な配点 | 100 点案（基本 30・改良 20・独自機能 20・テスト評価考察 15・発表 10・貢献 5）を確定 |
| 出典を示さない流用・説明できない場合の扱い | 学科の評価ルール |
| 生成 AI の利用ルール | 使ってよい場面、Notebook に記録すること |

記入後は `TASKS.md` を保存し、6 章の手順で配布物を作り直します。

### 2.3 Windows・Colab での実行確認

開発時は WSL（Linux、Python 3.12）の Jupyter（nbclient）だけで実行を確認しました。授業の前に、授業で使う環境で次を確かめてください。

- 配布用 ZIP を展開し、`F1_life_planning_starter.ipynb` を開いて上から実行できる（`[未実装]` が出て止まらない）。
- 第1章で「データフォルダ: OK」と表示される（Colab は `%cd` の後）。
- matplotlib があればグラフ、なければ表と文字で表示される。日本語フォントがなければ英語のラベルになる。

## 3. 学生の作業時間の記録方法

Notebook の作業時間（第0章 0.5、各章の冒頭）は**設計上の見積もり**です（Level 1：2〜3 時間、Level 2：1.5〜3 時間）。
実測するときは、チームごとに次の表を Notebook の最後に書いてもらうか、授業の最後にアンケートで集めます。

| テーマ | 段階 | 開始 | 終了 | 合計（分） | 最も時間がかかった課題 | 開いたヒントの段階 |
| --- | --- | --- | --- | ---: | --- | --- |
| F-1B | Level 1 | | | | | |

集めた値は `docs/educational_validation_report.md` の 5 章に記録し、次年度の見積もりを直します。

## 4. 公開統計の追加・更新

1. `scripts/download_datasets.py` の `SOURCES` に e-Stat の statInfId を追加する（ファイルダウンロードは登録不要。10MB を超えるファイルは取得前に確認）。
2. `<python> scripts/download_datasets.py` → `data/raw/`（Git 管理外）に保存される。
3. `scripts/preprocess_*.py` で Small Dataset を作る。学生が行う計算（年額への変換・純資産・累積）は前処理で行わない。欠損を 0 にしない。
4. 利用規約（e-Stat と作成府省）の例外を確認し、`docs/dataset_sources.md` 4 章と `data/dataset_sources.md` に出典・URL・統計表名・調査年・取得日・加工内容を書く。
5. `data/data_dictionary.md`・`data/README.md` を更新し、`scripts/validate_datasets.py --report` を実行する。
6. 配布するなら `scripts/build_student_package.py` の `ALLOWLIST` に追加し、`tests/test_f1_student_package.py` の `EXPECTED_FILES` も直す。

## 5. F-1C の実データを後日追加する方法

1. 不動産情報ライブラリ（https://www.reinfolib.mlit.go.jp/realEstatePrices/ ）で、地域（1〜2 市区町村）・取引時期（直近 1〜2 年）・種類を選び、CSV をダウンロードする（手順の詳細は `docs/preprocessing_report.md` 5 章）。API の利用申請・内部 URL の利用はしない。
2. ファイルを `data/raw/f1c/` に置き、`<python> scripts/preprocess_f1c.py` で `data/f1c/housing_prices_small.csv` を作る。
   **このスクリプトは実データで一度も実行していません。** 列名が違うときは、スクリプトの `CANDIDATES` に実際の列名を追加します。
3. 結果を目で確かめる（件数、価格の単位が万円になっているか、数値でない値が除外されているか）。
4. 公共データ利用規約（第1.0版）と、ダウンロード画面の注意事項を確認する。**確認できるまで Git 管理・配布しない。**
5. 配布する場合は、`ALLOWLIST`・`EXPECTED_FILES`・`data/dataset_sources.md`・`data/data_dictionary.md` を更新する。
   Notebook は、ファイルがあれば 6.9 で読み込み、なければメッセージを出して先に進む（作り直しは不要）。

## 6. 配布物の再生成

```bash
cd f1-career-income-optimization
PY=../c1-web-attack-detection/.venv/bin/python        # 教員の開発環境（nbformat など）。学生の配布物はこれに依存しない
$PY scripts/build_notebook.py                          # Notebook を変えた場合（実行済み・編集済みの Notebook には上書きしない）
$PY -m unittest tests.test_f1_notebook tests.test_f1_synthetic_data tests.test_f1_student_mistakes tests.test_f1_student_package
$PY scripts/run_reference_check.py                     # 参照実装で 128 件 [OK]
/usr/bin/python3 scripts/build_student_package.py --force   # dist/ に配布フォルダと ZIP（既存を作り直すときだけ --force）
```

配布物：`dist/f1-life-planning-starter/`、`dist/f1-life-planning-starter.zip`、`.sha256`、`_manifest.txt`（いずれも Git 管理外）。
詳細は `docs/student_package_guide.md`。

## 7. GitHub への公開

C-1 と同じく、既存のモノレポ（https://github.com/daigo-takeuchi/programming-lab-2026-team-project-1-starter ）の
`f1-career-income-optimization/` で公開します。F-1 専用のリポジトリは作りません（2026-11-27 の方針変更。`docs/student_distribution_plan.md`）。
教材を更新したら、feature ブランチ → Pull Request → main へのマージの順で反映します。

> **注意**：教員用モノレポ（公開リポジトリ）には、旧 F1 教材の完成したコード（`career_model.py` など。新 F-1A の Level 1・2 の解答に相当する部分を含む）が履歴とともに残っています。
> 方針として履歴は書き換えず、学生が参考にした場合は出典・変更点・説明を評価します（`TASKS.md` 8 章）。

## 8. LMS へのアップロード

1. `dist/f1-life-planning-starter.zip` と `dist/f1-life-planning-starter.sha256` をアップロードする。
2. 案内文の例：「ZIP をダウンロードし、展開してからフォルダごと VS Code で開いてください。最初に README.md を読んでください。」
3. Colab を使う場合は README 6 章の手順（`!unzip`、`%cd`）を案内する。

## 9. 授業での注意

- 「最適な計画」は、設定した仮定と評価指標の下での結果にすぎないことを、発表で区別させる。
- 公開統計の平均値を、特定の家族や同じ人のデータとして扱わせない。
- 自分や家族の実際の情報を入力させない。
- 初回の授業で、学生の試行（第0〜3章と Level 1 の課題1）の時間とつまずきを記録する（3 章）。
