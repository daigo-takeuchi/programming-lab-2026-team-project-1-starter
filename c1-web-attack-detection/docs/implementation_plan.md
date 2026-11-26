# 開発計画

最終更新：2026-11-27（Phase 5 終了時）

## Phase の全体像

```text
Phase 1   監査・再設計・初期改訂                      完了（df5a1dc）
Phase 1.5 教材の取り組みやすさの再確認                 完了（6b2ff9d）
Phase 2A  既存データ・小規模公開ログの前処理            完了（6b2ff9d）
Phase 2B  CIC-IDS2017 の取得と前処理（C-1A/E）        保留（教員の判断）
Phase 3+4 Starter Code の完成と共通評価機能            完了（e87c01b）
Phase 5   学生配布準備・最終検証                       完了（未コミット）
```

## 教員の残作業（順番どおり）

| 順番 | 作業 | 手順 | 想定時間 |
| ---: | --- | --- | --- |
| 1 | Phase 5 の変更の確認とコミットの判断 | `git diff`、`docs/final_validation_report.md` を読む | 30 分 |
| 2 | 教材の最終確認（教員による試行） | `teacher_guide.md` 10 章。ZIP を展開し、C-1A と C-1C の Level 1 を学生と同じ手順で解く | 60〜90 分 |
| 3 | Windows・Colab での確認 | `teacher_guide.md` 12 章 | 30〜60 分 |
| 4 | `TASKS.md` の【教員記入】 | 提出期限、発表時間、正式な配点、テーマの選び方、提出方法、生成 AI のルールを記入 | 30 分 |
| 5 | 配布物の作り直し | 2〜4 で直した場合：`python3 scripts/build_student_package.py --force` | 5 分 |
| 6 | GitHub の公開・非公開の判断と、配布用リポジトリの作成 | `student_package_guide.md` 2 章（`git init` → 初回コミット → `push`。テンプレートまたは Classroom） | 30〜60 分 |
| 7 | LMS への ZIP のアップロード | `student_package_guide.md` 3 章 | 15 分 |
| 8 | （任意）Loghub の公開ログを授業内で配る準備 | `student_package_guide.md` 4 章 | 15 分 |
| 9 | 初回授業での学生試行と記録 | `teacher_guide.md` 11 章の表に実測値を記入 | 授業 1 回 |
| 10 | 試行後の改善 | `build_notebook.py` を修正 → テスト → 配布物の作り直し | 内容による（2〜6 時間） |

## 今後の発展（必要になったとき）

- Phase 2B（CIC-IDS2017）：教員がデータを取得し、利用条件を確認した後に前処理（4〜7 時間）。
- Level 3 の教員提供の例（時間窓の数え方など、1 テーマ 2〜3 時間）。
- 親モノレポの README の更新（差し替え案は `student_package_guide.md` 5 章）。
