# 既存 F-1 教材の監査（Phase 1、2026-11-27）

## 1. 対象と状態

| 項目 | 内容 |
| --- | --- |
| ディレクトリ | `programming-lab-2026-team-project-1-starter/f1-career-income-optimization/`（親 README の表で F1 として参照） |
| 旧テーマ名 | F1：キャリア選択と生涯所得の最適化（RQ1〜RQ4、Core / Advanced A〜E） |
| Git 履歴 | `7e2966d`（Initial commit）だけ。以後の変更なし。**公開リポジトリの main に含まれている** |
| 容量 | 約 256KB（教科書コードを含むローカル） |
| 未コミットの変更 | なし（Phase 1 開始時） |
| CLAUDE.md・requirements・docs | なし（Phase 1 で新規作成） |
| 依存 | 標準ライブラリ。`presentation_charts.py` と Notebook だけ matplotlib |
| テスト | `tests/test_*.py` 4 本、51 件。Phase 1 開始時・終了時ともに全件成功（C-1 の `.venv` の Python 3.12.3 で実行） |

## 2. ファイルの分類

分類：①そのまま再利用 ②改訂して再利用 ③共通関数として再利用 ④新規作成が必要 ⑤旧教材として保存 ⑥学生配布対象から除外

| ファイル | 内容 | 分類 | 備考 |
| --- | --- | --- | --- |
| `README.md`（523 行） | 旧 F1 の学生向け説明（RQ、モデル、Core/Advanced、倫理、著作権） | ⑤ → ② | 倫理（17 章）・限界・著作権の記述は新 README に再利用。旧本文は Phase 5 で `docs/legacy/` へ移す案（承認後） |
| `career_model.py` | 年齢別所得モデル（`salary_at`、`income_by_age`、入力検証） | ⑤⑥ | **F-1A Level 1 課題2・3 の完成解答に相当**。年収の式・退職年齢の規則は新モデルに採用 |
| `scenarios.py` | 進学・資格・転職のシナリオ辞書、`with_changes`（コピーして変更） | ⑤⑥（考え方は②） | 「元のシナリオを変更しない」設計は simulation_rules に採用。資格・転職のモデルは F-1A Level 2・3 の素材 |
| `income_analysis.py` | 生涯所得・累積純収入・NPV・回収年齢（線形探索） | ⑤⑥ | **F-1A 課題3・4、Level 2 の回収年齢の完成解答に相当**。「差は単調でないので二分探索を使わない」説明は Notebook に採用済み |
| `optimization.py` | 転職年齢の全探索、`max_of`+`seq_search`、挿入ソートによる順位付け | ⑤⑥ | F-1A Level 2（全探索・ソート）の素材。教科書コードを import する（下記） |
| `experiments.py` | Experiment 1〜5（進学・資格・転職・割引率・感度分析）と TODO | ⑤ | 感度分析・割引率は F-1A Level 3 の候補。NPV は F-2 との境界に注意 |
| `presentation_charts.py` | matplotlib の発表用グラフ | ⑤ | 色の統一・グラフ種類は Phase 4 の可視化で参考 |
| `starter.py` | 旧教材のデモ | ⑤⑥ | |
| `notebooks/01〜04_*.ipynb`、`notebooks/README.md` | 旧 RQ 別の分析・発表用 Notebook（出力なし） | ⑤⑥ | 04 の発表テンプレート（問い→仮定→方法→結果→限界）は TASKS・第8章の発表構成に参考 |
| `data/sample_careers.json` | 架空のキャリア 5 件（早期就職・専門・大学・資格・転職） | ② | 新 Mini（A/B/C）と値が近い。Tiny の分布（20 歳・22 歳就職の年収・費用）の参考にした |
| `textbook/__init__.py`（追跡）、`max.py`・`ssearch_while.py`・`insertion_sort.py`（ローカルのみ） | 柴田望洋『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』のサンプル | ⑤⑥ | 再配布未確認のため Git 管理外（親 `.gitignore`）。**新 Notebook は教科書コードに依存しない** |
| `tests/test_career_model.py` ほか 3 本 | 旧モジュールのテスト | ⑤⑥ | 旧教材の動作確認用として残す（教科書コードがないと `ModuleNotFoundError`） |
| `.gitignore` | Python キャッシュ・results など | ② | Phase 1 で solutions/・dist/・data/raw/ を追記 |

## 3. 既存サブトピック（旧 RQ と Advanced）

| 旧 | 内容 | 新テーマ |
| --- | --- | --- |
| RQ1 | 就職と進学（18・20・22 歳就職、教育費、機会費用） | F-1A Level 1（Mini の A/B/C）・Level 2（回収年齢） |
| RQ2 | 資格取得の費用対効果 | F-1A Level 2（組合せ）・Level 3 |
| RQ3 | 転職年齢の全探索 | F-1A Level 2（全探索）・Level 3（転職時期の最適化） |
| RQ4 | 生涯所得と NPV | F-1A Level 3（任意。割引の考え方。投資収益の最大化にはしない） |
| Advanced A | モンテカルロ（昇給率・資格の成功確率） | F-1A Level 3（失業・休職のリスク）。プログラミング演習Ⅱへの発展 |
| Advanced B | 動的計画法 | 演習Ⅱ以降の発展（必須にしない） |
| Advanced C | 所得以外の評価（労働時間・満足度） | F-1A Level 3、F-1B の自由時間の指標 |
| Advanced D | 公的統計（賃金構造基本統計調査など） | F-1A STEP 5（Small Dataset） |
| Advanced E | リスクと最適化 | F-1A Level 3（任意） |

## 4. 重要な所見

1. **完成解答の公開**：旧 `career_model.py`・`income_analysis.py`・`optimization.py` は完成した実装で、新 F-1A の Level 1 課題2〜4 と
   Level 2（回収年齢・順位付け・転職年齢の全探索）の解答に相当する。`7e2966d` 以降、公開リポジトリの main で公開されている。
   ファイルを削除しても**公開 Git 履歴からは消えない**。
   → 対策案：新 Notebook の関数名・データ構造・引数を旧コードと変えてある（例：`salary_at_age(career, age, retirement_age)`、
   Mini の昇給率 B 2.5%・C 3% など）。旧コードを写しても `check()` はそのままでは通らない。評価では「説明できること」を重視する（TASKS で明記予定）。
2. **教科書コード**：`textbook/*.py` は Git 管理外で、公開履歴にも含まれていない（`git ls-files` で `__init__.py` のみ）。
3. **親 README**：F1 の名称・説明・難易度（★）が旧教材のまま。Phase 5 で更新が必要（親 README は本 Phase では変更しない）。
4. **ディレクトリ名**：`f1-career-income-optimization` は新テーマ（4 テーマ統合）と名称が合わない。変更する場合は親 README のリンク・難易度表も直す（教員判断）。
5. **Notebook の実行**：旧 Notebook 4 本は出力なし。新 Notebook とは独立（相互の import なし）。

## 5. 他トピックとの関係（読み取りのみ）

| トピック | 関係 |
| --- | --- |
| F2 `f2-financial-independence` | 資産形成・FIRE。F-1 では投資戦略・リターン最大化・FIRE 時期を扱わない |
| F4 `f4-partnership-simulation` | 家事分担・経済的負担・関係満足度。F-1B は「時間と所得の配分の制約充足」に絞り、満足度・関係継続はモデル化しない |
| C-1 `c1-web-attack-detection` | 教材生成・テスト・配布機構の参照元（`docs/c1_reuse_report.md`） |
