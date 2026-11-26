# 開発状況

最終更新：2026-11-27（Phase 5 終了時）
現在の状態：**Phase 5 完了（学生配布物の生成・検証済み）→ 教員の確認待ち（未コミット）**。Phase 2B は保留。

## 1. 環境

| 項目 | 内容 |
| --- | --- |
| Git | ブランチ `feature/c1-integrated-starter`。Phase 1：`df5a1dc`、Phase 1.5・2A：`6b2ff9d`、Phase 3・4：`e87c01b`。**Phase 5 は未コミット**。push していない |
| Python | 3.12.3。既存の `.venv` を再利用（新しいライブラリ・仮想環境は追加していない） |
| ディスク | Windows C: の空き：作業開始時 2.3GB → 終了時 **1.8GB**。今回作ったファイルは配布物（`dist/`、約 0.5MB）を含めて 1MB 程度。減少の原因は、VS Code・Claude Code の拡張機能の自動更新（直近 24 時間に作られた大きなファイルを確認）と、テストの一時ファイルによる WSL の仮想ディスク（vhdx）の拡大が考えられる（vhdx は自動では縮まない）。特定はできていない |

## 2. Phase 5 で行ったこと

| 区分 | 内容 |
| --- | --- |
| 学生向け文書 | `README.md`（学生が最初に読む文書。教員用の情報を除いた）、`TASKS.md`（4 段階の進め方、チーム独自の機能を必須に、成果物 10 項目を Notebook にまとめる、100 点の評価案、【教員記入】）、`data/README.md`（学生向けに書き直し）、`data/data_dictionary.md`（新規）、`requirements.txt`（ipykernel と matplotlib） |
| Notebook の最小限の修正 | 0.7 にチーム課題の 4 段階、各章 N.10 にチーム独自の機能の例、公開ログは「授業で配布された場合のみ」、学生が見るメッセージから教員用スクリプト名を削除、第1章で配布用のフォルダ名も探す |
| 配布物の生成 | `scripts/build_student_package.py`（許可リスト、シンボリックリンクの拒否、Notebook の初期化、解答の混入チェック、決まった ZIP、上書きの拒否） |
| 検証 | `tests/test_student_package.py`（12 件）、`run_reference_check.py --notebook`（配布用 Notebook のコピーで検証） |
| 教員用文書 | `student_package_guide.md`（作り方、GitHub・LMS の手順、Loghub の限定配布、親 README の差し替え案）、`final_validation_report.md`、`teacher_guide.md`（試行の手順、初回授業の確認項目、環境のチェックリスト） |

## 3. 学生配布物

`dist/c1-cybersecurity-starter/`（13 ファイル、321,308 バイト）と `dist/c1-cybersecurity-starter.zip`（77,303 バイト）。詳細は `final_validation_report.md`。

## 4. テスト結果

教員環境 83 件すべて成功（既存 71＋新規 12）。システムの Python では 68 件成功、15 件スキップ。参照実装による検証 114 件すべて `[OK]`（教員用 Notebook と、配布用 Notebook のコピーの両方）。

## 5. 未検証

Windows ネイティブ、Google Colab、Python 3.11・3.13（3.9・3.10 は構文のみ確認）、matplotlib の日本語表示、学生・教員による試行。

## 6. 次にやること（教員）

`implementation_plan.md` の「教員の残作業」を参照。
