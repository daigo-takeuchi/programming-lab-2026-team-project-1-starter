# 学生配布物の手引き（教員用）

## 1. 配布物の作り方

```bash
cd c1-web-attack-detection
.venv/bin/python scripts/build_student_package.py           # 初回（標準ライブラリだけでも動く：python3 でも可）
.venv/bin/python scripts/build_student_package.py --force   # 教材を直した後に作り直す
```

| 出力（`dist/`、Git 管理外） | 用途 |
| --- | --- |
| `dist/c1-cybersecurity-starter/` | 学生配布用 GitHub リポジトリの中身 |
| `dist/c1-cybersecurity-starter.zip` | LMS で配る ZIP（中に `c1-cybersecurity-starter/` フォルダが 1 つ） |
| `dist/c1-cybersecurity-starter.sha256` | ZIP の SHA-256 |
| `dist/c1-cybersecurity-starter_manifest.txt` | ファイル一覧（容量・SHA-256） |

- **許可リスト方式**（スクリプトの `ALLOWLIST`）。README、TASKS、Notebook、requirements、`data/README.md`、`data/data_dictionary.md`、人工データの CSV 7 個だけを入れます。
- 旧教材、参照実装（`solutions/`）、教員用スクリプト・テスト・docs、Loghub 由来の CSV、原データ、`.venv`、キャッシュは入りません。
- Notebook は配布用のコピーで、出力・実行カウント・教員用メタデータを消します。教員用の Notebook は変わりません。
- 作成時に、33 個の学生実装課題が未実装のままであること、参照実装が混ざっていないこと、教員環境のパスがないことを自動で確かめます。
- 同じ内容なら同じ ZIP（同じ SHA-256）になります。既存の配布物は `--force` なしでは上書きしません。

### 教材を直したときの順番

1. `scripts/build_notebook.py` を直して、Notebook を再生成する（学生が編集した Notebook には上書きしない仕組みあり）。
2. `.venv/bin/python -m unittest discover -s tests -t .`（参照実装の検証と、配布物のテストを含む）
3. `build_student_package.py --force` で配布物を作り直す。
4. 配布用リポジトリ・LMS の ZIP を差し替え、学生に知らせる（配布後の差し替えは、学生の作業と衝突しやすいので最小限に）。

## 2. GitHub の学生配布用リポジトリ（手順。教員が実施）

教員用モノレポの履歴は引き継ぎません。配布フォルダから新しいリポジトリを作ります。

1. GitHub で新しいリポジトリ `c1-cybersecurity-starter` を作る（README などは追加しない）。**公開／非公開は教員が判断**します。Loghub 由来のデータは入っていませんが、学生の解答が公開されないよう、学生が作業するリポジトリは非公開を推奨します。
2. 配布フォルダを Git リポジトリにして、最初のコミットをします。

   ```bash
   cp -r dist/c1-cybersecurity-starter ~/c1-cybersecurity-starter    # 教員用リポジトリの外にコピー
   cd ~/c1-cybersecurity-starter
   git init -b main
   git add .
   git commit -m "C-1 Cybersecurity Programming Starter"
   git remote add origin https://github.com/<組織またはユーザー>/c1-cybersecurity-starter.git
   git push -u origin main
   ```

3. 学生への配り方（どれか 1 つ）：
   - **テンプレートリポジトリ**にして、各チームが「Use this template」で自分たちのリポジトリ（非公開）を作る。
   - GitHub Classroom のグループ課題にする（チームごとにリポジトリが自動で作られる）。
4. チームでの開発：各チームのリポジトリで、`TASKS.md` の Git の手順（ブランチを作る → コミット → push → プルリクエスト）に従う。教員はチームのリポジトリに招待してもらう。

## 3. LMS での ZIP 配布（手順。教員が実施）

1. `dist/c1-cybersecurity-starter.zip` を LMS にアップロードする。
2. 説明文の例：「ZIP をダウンロードし、**展開してから** VS Code で `c1-cybersecurity-starter` フォルダを開いてください。手順は中の README.md にあります。」
3. 必要なら、`dist/c1-cybersecurity-starter.sha256` の値を書いておく（ファイルが壊れていないかの確認用）。

## 4. Loghub 由来の公開ログを授業内で配る場合（任意）

標準の配布物には入っていません。C-1B・C-1D の Level 3 で使わせる場合だけ、教員の PC で作って**授業内の限定配布**（LMS・非公開リポジトリ）で渡します。**公開 GitHub には入れません。**

```bash
python3 scripts/download_datasets.py     # Loghub の原データ（約 1.1MB）を data/raw/ に取得
python3 scripts/preprocess_c1b.py        # data/c1b/authentication_small.csv、ssh_events_small.csv
python3 scripts/preprocess_c1d.py        # data/c1d/system_events_small.csv
```

配るもの：上の 3 つの CSV と、`data/c1b/LICENSE_LOGHUB.txt`、`data/c1d/LICENSE_LOGHUB.txt`（**ライセンス文は必ず一緒に**）。
学生は、受け取ったファイルを自分の教材の `data/c1b/`・`data/c1d/` に置くだけで、Notebook の 5.9・7.9 が使えるようになります。

その他のデータの作り直し：`python3 scripts/generate_synthetic_data.py`（Tiny Dataset）、`python3 scripts/preprocess_c1c.py`（人工アクセスログ）、`python3 scripts/validate_datasets.py`（品質検証）。

## 5. 親モノレポの README の差し替え案（未適用）

親リポジトリ `README.md` の C1 の行は旧教材のままです。次の差し替えを提案します（今回は変更していません）。

- 一覧表の行：

  ```text
  | C1 | サイバー攻撃の検出（ネットワーク・Web・API・システムの監視） | `c1-web-attack-detection/` | 探索・集計（リスト・辞書・集合）、文字列処理、閾値による検出 | [README](c1-web-attack-detection/README.md) |
  ```

- 補足の文（表の下などに）：

  > C1 は、C-1A〜C-1E の 5 テーマを 1 つの Notebook（`C1_cybersecurity_starter.ipynb`）にまとめた教材に改訂しました。チームは 1 テーマを選び、Level 1（必須）→ Level 2（推奨）→ チーム独自の機能 の順に取り組みます。学生には配布用パッケージ（`c1-cybersecurity-starter`）を配ります。

- 難易度の目安の行（★は Phase 1 の作業時間の見積もりに基づく案。学生の試行後に見直す）：

  ```text
  | C1 | サイバー攻撃の検出 | ★★☆☆☆ | ★★☆☆☆ | ★★★☆☆ |
  ```
  （概念・実装の★は旧教材と同程度。チーム独自の機能開発を必須にしたため、総合負荷は ★★★ のまま）
