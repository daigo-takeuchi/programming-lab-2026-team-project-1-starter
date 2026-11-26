# CLAUDE.md：F-1 Life Planning Programming Starter

このファイルは、Claude Code でこのディレクトリを開発するときのルールです。
**作業を始める前に、必ず次を読むこと。**

1. `CLAUDE.md`（このファイル）
2. `docs/development_status.md`（現在の Phase と、次にやること）
3. `docs/implementation_plan.md`（Phase の分け方と計画）
4. `docs/migration_plan.md`（旧教材からの移行計画）
5. データを扱うときは `docs/dataset_feasibility_report.md`・`docs/dataset_sources.md`

詳しい仕様は `docs/project_specification.md`、モデルの仮定は `docs/model_assumptions.md`・`docs/simulation_rules.md`。

## プロジェクトの目的

プログラミング演習Ⅰ（AI 専門学校、留学生を含む Python 初学者）のチーム開発課題 F-1
「キャリア・ライフイベント・世代間資源継承のシミュレーションと最適化」の教材。
身近な社会的問題を題材に、リスト・辞書・for/if・関数・CSV・線形探索・二分探索・ソート・全探索・計算量を学ぶ。
**経済学や金融の専門知識の習得が目的ではない。** 特定の進路・家族形態・住宅・相続方法を推奨しない。

### 4 テーマ（全チームに同じ Notebook を配布し、チームは 1 テーマを選ぶ）

| ID | テーマ | 章 | Mini の変数 | データフォルダ |
| --- | --- | --- | --- | --- |
| F-1A | キャリア選択・教育投資と生涯所得 | 第4章 | `career_options` | `data/f1a/` |
| F-1B | 家族形成・子育て・介護と資源配分 | 第5章 | `work_options`・`household` | `data/f1b/` |
| F-1C | 住宅取得・居住選択と長期家計設計 | 第6章 | `housing_options` | `data/f1c/` |
| F-1D | 世代間資源継承と次世代の生活設計 | 第7章 | `family`・`transfer_options` | `data/f1d/` |

- F-2（資産形成・FIRE）と重複させない：株式投資戦略、ポートフォリオ最適化、投資リターン最大化、FIRE 時期の最適化は中心課題にしない。
- F-4（パートナーシップ）・他トピックのディレクトリは**読み取り専用**。

## 既存プロジェクトの改訂方針

- このディレクトリ（`f1-career-income-optimization/`）は旧 F1「キャリア選択と生涯所得の最適化」を**改訂**したもの。新規ディレクトリを作らない。
  ディレクトリ名の変更は親 README のリンクに影響するため、教員の承認なしに行わない。
- Git ルートは親ディレクトリ（24 トピックのモノレポ、**公開リポジトリ**）。**他のトピックのディレクトリに触れない。C-1 は読み取り専用の参照対象。**
- 旧教材（`starter.py`、`career_model.py`、`scenarios.py`、`income_analysis.py`、`optimization.py`、`experiments.py`、
  `presentation_charts.py`、`notebooks/`、`data/sample_careers.json`、`tests/test_career_model.py` など 4 本、旧 `README.md`）は、
  移行完了まで動く状態で残す。削除・移動は教員の承認を得てから（`docs/migration_plan.md`）。
- 旧教材の `.py` は完成した実装（F-1A Level 1・2 の解答に相当する部分を含む）。新 Notebook の学生課題にそのまま移植しない。

## 教材の構成ルール

- Notebook：`F1_life_planning_starter.ipynb`（第0〜9章）。学生は第0〜3章 → 担当テーマ章 → 第8章。第9章は任意。
- 各テーマ章は同じ 10 節（N.1〜N.10）と 5 STEP。STEP 1〜3 = Level 1（必須）、STEP 4 = Level 2、STEP 5 = Level 3。
  章の冒頭に「解決する問題・入力・内部の計算・出力・完成イメージ・進め方・想定作業時間（設計上の見積もり）」の表。
- Level 1 は 1 テーマ 4 課題（1 関数 3〜15 行程度）。Level 2 は 2〜3 課題（Phase 3 で実装）。
- 各課題に：関数名・引数・戻り値・例・ひな形・TODO・3 段階のヒント（考え方／文法・データ構造／疑似コード）・Mini と Tiny の動作確認。
  **ヒントに完成解答を書かない。**
- 未実装は `raise NotImplementedError("学生実装課題")`。`check()` は `[OK]`・`[NG]`・`[未実装]`・`[エラー]` を区別し、
  `NotImplementedError` だけを未実装として扱う（他の例外は隠さない）。小数は許容誤差で比べる。引数の書き換えを `[NG]` にする。
- テーマ章は第0〜3章の共通関数（`load_csv`・`show_records`・`check`・`run_if_implemented`・`measure_time`・`compare_speed`・
  `jp`・`plot_lines`・`plot_bars`）だけに依存する。**他テーマの変数・関数・データを使わない**（`tests/test_f1_notebook.py` で検査）。
- 学習目標そのものになる処理（累積和、年次更新、探索）は、共通関数として先に提供しない。
- セルの表示：【教員提供コード】【学生実装課題：Level 1／2】【動作確認】【ヒント】【考察課題】【発展課題：Level 3】。
- 主要アルゴリズムは標準ライブラリで学生に実装させる。matplotlib は可視化用の任意依存。

## Notebook の編集方法

- Notebook は `scripts/build_notebook.py`（**教員用マスター**）から生成する。**ipynb を直接編集しない。**
- 生成スクリプトは、実行結果がある Notebook と、生成時の指紋（`metadata.f1_generator.source_fingerprint`）と内容が違う
  Notebook への上書きを拒否する（`--force` で強制）。セル ID は連番で固定。`build_notebook.py` は学生に配布しない。
- 変更後は：`<python> scripts/build_notebook.py` → `<python> -m unittest tests.test_f1_notebook tests.test_f1_synthetic_data`
  → `<python> scripts/run_reference_check.py`（参照実装がある場合）。
- 出力（outputs）を含めずにコミットする。

## 日本語表記

Markdown・コメント・docstring・TODO・ヒント・文書・グラフのラベルは**自然で短い日本語**。
変数名・関数名・ファイル名・CSV の列名は英語。専門用語は初出で日本語と英語を併記（例：二分探索（Binary Search））。
グラフは日本語フォントがあれば日本語、なければ `jp()` で英語に切り替える（フォントを追加インストールしない）。

## モデルの約束（詳細は docs/simulation_rules.md）

- 金額は万円、時間は時間／週（1 人 168 時間）、年齢は歳。`monthly_` と `annual_` で月額・年額を区別。
- 所得（額面）と可処分所得、資産残高と年間収支、初期状態と年末状態を区別する。シミュレーションの 1 年目は `year = 1`（年末の状態を記録）。
- 赤字・資産不足を 0 に置き換えない。資金移転は二重計上しない（親の減少額 = 子の増加額）。入力データを書き換えない。
- 仮定値と公開統計の値を区別する。税・社会保険・インフレ・資産価格変動は基本モデルでは省略し、限界として明記する。

## データ方針

- Mini（Notebook 内 3〜10 件、人工）→ Tiny（CSV 20〜50 件、人工、`scripts/generate_synthetic_data.py`、シード 2026）
  → Small（公開統計由来 50〜1,000 件、Phase 2）→ Benchmark（プログラム内で生成、ファイルに保存しない）。
- Level 1・2 は Mini と Tiny だけで完結すること。Small がなくても Notebook が止まらないこと。
- 人工データのファイル名は `_tiny`、公開統計由来は `_small`。原データは `data/raw/`（Git 管理外）。
- 学生が計算すべき集計値・累積値・探索結果を前処理で計算済みにしない。欠損値・秘匿値を 0 にしない。
- 公開統計は出典と「加工して作成」の旨を記載（e-Stat は政府標準利用規約 第2.0版、CC BY 4.0 互換）。再配布条件が未確認のデータは配布物に入れない。
- 不動産取引価格データには家賃・通勤時間がない。実測値のように追加しない。F-1D は個人の追跡データを使わず、集計統計をパラメータにする。
- e-Stat API・不動産情報ライブラリ API はユーザ登録・API キーが必要。**Claude が登録・キー発行をしない**（教員が行う）。

## ストレージ・依存関係

- Windows C: の空きは 7.8GB（2026-11-27、Phase 1 開始時）。WSL の仮想ディスクも C: 上にあるため、Linux 側の `df /` は判断に使わない（`df -h /mnt/c` を見る）。
  2GB 未満なら軽量な作業だけにし、減り続けるなら報告して止まる。
- 新しい仮想環境を作らない。大容量ライブラリをインストールしない。10MB を超える個別ファイル・合計 50MB を超えるデータ取得は事前に承認を得る。
- 教員側の開発・検証は C-1 の既存環境 `../c1-web-attack-detection/.venv/bin/python`（nbformat・nbclient・ipykernel・matplotlib）を**パス指定で借用**している。
  学生向け教材・テスト・スクリプトは C-1 のファイルに依存させない。シェル既定の `python3` は別プロジェクトの venv なので使わない（標準ライブラリだけなら `/usr/bin/python3`）。
- 同じテストの不要な繰り返しを避ける（Notebook 実行テストは一時ファイルを作る）。

## Git

- 作業ブランチ：`feature/f1-integrated-starter`（main `c911693` から作成）。コミットは教員の指示があるときだけ。
- 承認なしに行わない：push、マージ、`reset --hard`、`git clean`、stash、履歴の書き換え、force push、ブランチの削除、リモート設定・公開範囲の変更。
- Git 管理外：`solutions/`（教員用参照実装）、`dist/`、`data/raw/`、`data/interim/`、`results/`、仮想環境、秘密情報。
- 親リポジトリの `.gitignore` は `*.log` と `textbook/**/*.py` を除外している。`textbook/` の教科書コードは再配布未確認のため追跡しない。
