# 学生配布計画

採用する方式：**教員用モノレポで開発を続け、学生配布用ファイルだけを抽出する**（Phase 1 の提案を教員が採用）。
抽出スクリプトの本格実装は Phase 5。外部リポジトリの作成・push・公開範囲の変更は、教員の指示があるまで行わない。

## 1. 配布するもの

| ファイル | 状態 | 備考 |
| --- | --- | --- |
| `C1_cybersecurity_starter.ipynb` | 配布可 | 学生が直接編集する成果物。出力なしの状態で配布 |
| `README.md` | 配布可（Phase 5 で学生向けに最終調整） | 旧教材への言及は配布版では削除予定 |
| `TASKS.md` | 配布可（【教員記入】を埋めてから） | |
| `requirements.txt` | 配布可 | matplotlib のみ（任意） |
| `data/README.md` | 配布可 | 学生向けのデータの説明 |
| Mini Dataset | 配布可 | Notebook の中 |
| Tiny Dataset（`data/c1x/*_tiny.csv` 6 ファイル） | 配布可 | 人工データ |
| `data/c1c/web_access_log_synthetic.csv` | 配布可 | 人工データ |
| `data/c1b/authentication_small.csv`、`ssh_events_small.csv`、`data/c1d/system_events_small.csv` | **授業内の限定配布のみ**（下記 3 章） | Loghub 由来。`LICENSE_LOGHUB.txt` を必ず同じフォルダに入れる。**公開 GitHub には含めない**（教員の方針、2026-11-27） |
| `data/c1a/network_flows_small.csv`、`data/c1e/data_transfer_small.csv` | **保留**（未作成） | CIC-IDS2017 の取得を保留（Phase 2B） |
| 学生向けデータ辞書 | Phase 5 で作成 | `docs/data_dictionary.md` から学生向けの部分を抜き出す |
| 学生が実行できるテスト | Phase 5 で検討 | Notebook の【動作確認】セルが中心。必要なら学生用の簡単なテストを追加 |

## 2. 配布しないもの

| ファイル | 理由 |
| --- | --- |
| `detection.py`、`starter.py`、`log_parser.py`、`benchmark.py`、旧 `tests/test_*.py` | 旧教材。`detection.py` は Level 2 の解答に近い完成コード |
| `textbook/` | 第三者の著作物（再配布の許諾なし） |
| `scripts/`（`build_notebook.py`、`run_reference_check.py`、`download_datasets.py`、`preprocess_*.py` など） | 教員用。`build_notebook.py` で学生の Notebook を上書きしないため |
| `tests/`（教員用テスト） | 教員の検証用 |
| `docs/`、`CLAUDE.md`、`requirements-dev.txt` | 開発管理文書 |
| `data/raw/`、匿名化の対応表 | 原データと、匿名化を元に戻せる情報 |
| `.venv/`、`results/` の中身 | 仮想環境、実行結果（`run_reference_check.py --save` の出力は**解答を含む**） |
| `solutions/` | 教員用の参照実装（全 33 関数の完成解答）。Git 管理外 |
| `docs/teacher_guide.md`、`docs/educational_validation_report.md` | 教員専用文書 |
| モノレポの Git 履歴 | 旧教材の完成コードや他トピックを含むため。配布用リポジトリは新しい履歴で作る |

## 3. Loghub 由来データの扱い

| 項目 | 確認結果 |
| --- | --- |
| リポジトリのライセンス | LICENSE ファイルは**データセットのライセンス**（"LICENSE OF LOGHUB"）。GitHub 上の表示は "Other"。コードに対する別のライセンスはない【公式】 |
| データセット固有の条件 | OpenSSH・Linux の各 README は、論文の引用を求めるのみ【公式】 |
| 元のデータ提供者 | OpenSSH：Loghub の研究室で収集。Linux：Public Security Log Sharing Site（Anton Chuvakin 氏）。同サイトの条件は "public; use for whatever you want"（出典の明記を推奨）【公式：2026-11-26 に確認】 |
| 学術利用 | "freely available for research or academic work"【公式】 |
| 授業での利用 | 明記なし。**教員の方針として、利用条件を満たす範囲で教育に利用する** |
| 加工した CSV の再配布 | "For any usage or distribution … refer to the loghub repository URL … and cite"、"The above license notice shall be included in all copies of the datasets"【公式】。条件付きで配布を想定している |
| GitHub での公開配布 | **明記なし【未確認】**。公開すると学術目的以外の第三者も入手できる |
| 必要な引用 | Jieming Zhu, Shilin He, Pinjia He, Jinyang Liu, Michael R. Lyu. Loghub: A Large Collection of System Log Datasets for AI-driven Log Analytics. ISSRE 2023.（Loghub-2.0 を使う場合は ISSTA 2024 の論文も） |
| ライセンス文の同梱 | 必要。`data/c1b/LICENSE_LOGHUB.txt`、`data/c1d/LICENSE_LOGHUB.txt`（原文のまま） |

**現在の扱い：**

- 前処理済み CSV は **Git 管理外**（`.gitignore`）。スクリプトでいつでも再生成できる。
- **授業内の限定配布**（非公開のリポジトリ、学内の LMS、ZIP の配布）：教員の方針の範囲で配布可能と考える（ライセンス文の同梱と引用が条件）。
- **公開 GitHub**：確認できるまで含めない。必要なら Loghub の GitHub Discussions で問い合わせる。

## 4. 配布方法の手順案（Phase 5）

1. `scripts/export_student_package.py`（Phase 5 で作成）が、上の「配布するもの」だけを `dist/c1-student/` にコピーする。
2. 配布物の容量を確認する（目標 10〜20MB。現時点の見込みは 1MB 未満〜2MB）。
3. 新しい Git 履歴で配布用リポジトリを作る（教員の承認後）か、ZIP にする。
4. Colab 用の手順を README に記載する。
