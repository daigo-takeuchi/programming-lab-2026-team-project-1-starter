# 学生配布の計画

2026-11-27 に方針を変更しました。F-1 専用の学生配布用リポジトリは**作りません**。C-1 と同じく、既存のモノレポで配布し、LMS の ZIP を併用します。

## 1. 配布の方法

| 方法 | 配るもの | 状態 |
| --- | --- | --- |
| GitHub（既存のモノレポ） | https://github.com/daigo-takeuchi/programming-lab-2026-team-project-1-starter の `f1-career-income-optimization/`（README、TASKS、`F1_life_planning_starter.ipynb`、requirements、`data/`） | C-1 と同じ手順（feature ブランチ → Pull Request → main へのマージ）で統合する |
| LMS | `dist/f1-life-planning-starter.zip`（と `.sha256`） | ZIP は作成済み（Git 管理外、GitHub にはコミットしない）。**アップロードは教員が行う** |

- GitHub のフォルダには、旧 F1 教材のファイル（`career_model.py`、`notebooks/` など）と教員用のスクリプト・テスト・文書も残っています。学生が使うのは README 3 章のファイルです。
- ZIP は、教員用ファイルと旧教材を含まない**クリーンな教材パッケージ**です（`docs/student_package_guide.md`）。
- 旧 F1 教材の完成したコードは、公開の履歴とともにモノレポに残っています。方針（教員の決定）：履歴は書き換えない。
  学生が旧コードを参考にした場合は、出典・変更点・処理の意味の説明を求める（`TASKS.md` 8 章）。
- 参照実装（`solutions/`）・原データ（`data/raw/`）・`dist/` は Git 管理外で、GitHub に置きません。

## 2. 学生の取得手順（README 5 章と同じ）

```bash
git clone https://github.com/daigo-takeuchi/programming-lab-2026-team-project-1-starter.git
cd programming-lab-2026-team-project-1-starter/f1-career-income-optimization
code .
```

既に clone している学生は、自分の変更がない場合に限り `git switch main` → `git pull --ff-only origin main` で更新します。
Notebook を編集している場合は、先に作業を保存・コミットするよう案内します（`git reset --hard` などは案内しない）。

## 3. 教材を更新するとき

1. `feature/` ブランチで修正し、テストと参照実装の確認を行う。
2. 学生配布の対象ファイル（README・TASKS・Notebook・data）を変えたら、`build_student_package.py --force` で ZIP を作り直す。
3. Pull Request を作り、差分（F-1 と親 README の F-1 の記述だけか、解答・原データが含まれないか）を確かめて main にマージする。
4. LMS の ZIP を差し替える。
