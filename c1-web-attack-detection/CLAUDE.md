# CLAUDE.md：C-1 Cybersecurity Programming Starter

このファイルは、Claude Code でこのディレクトリを開発するときのルールです。
**作業を始める前に、必ず次の 3 つを読むこと。**

1. `CLAUDE.md`（このファイル）
2. `docs/development_status.md`（現在の Phase と、次にやること）
3. `docs/migration_plan.md`（旧教材からの移行計画）

詳しい仕様は `docs/project_specification.md` にある。

## プロジェクトの目的

プログラミング演習Ⅰ（AI・情報系専門学校、留学生を含む Python 初学者）のチーム開発課題 C-1 の教材。
サイバーセキュリティを題材に、for 文・if 文・リスト・辞書・集合・関数・CSV・計算量の基礎を学ぶ。
セキュリティ技術の習得ではなく、**実社会の問題を Python の小さな問題に変換する経験**が目的。

- 対象テーマ：C-1A ネットワーク探索・異常通信／C-1B 不正認証／C-1C Web・API 不正アクセス／C-1D 不正操作・システム改変／C-1E 情報流出。
  C-1F は C-2 と重複するため**含めない**。
- 学生の主な配布物：`C1_cybersecurity_starter.ipynb`（全5テーマ統合、全10章）＋ `data/` ＋ README.md ＋ TASKS.md。

## 既存プロジェクトの改訂方針

- このディレクトリは、旧 C1「Web サーバーへのサイバー攻撃の検出」を**改訂**したもの。新規ディレクトリを作らない。ディレクトリ名・リモート設定は変更しない。
- Git リポジトリのルートは親ディレクトリ（24 トピックのモノレポ `programming-lab-2026-team-project-1-starter`）。**他のトピックのディレクトリに触れない。**
- 旧教材（`starter.py`、`detection.py`、`log_parser.py`、`benchmark.py`、`tests/test_*.py`、`data/sample_access.log`）は、移行完了まで動く状態で残す。削除・移動は教員の承認を得てから。
- 旧 README は `docs/legacy/README_web_access_log.md` に移した。

## 教材の構成ルール

- 各テーマの章は同じ 10 節（N.1〜N.10）と 5 STEP。STEP 1〜3 = Level 1（必須）、STEP 4 = Level 2、STEP 5 = Level 3。
- Level 1 は 1 テーマ 3〜5 個の小さな TODO（1 関数 = 1 つの処理、数行〜15 行程度）。基本アルゴリズムも学生が実装する。
- 各 TODO に：関数名・引数・戻り値・入出力形式・具体例・期待される出力・3 段階のヒント・動作確認方法。
- **学生用 TODO の完成解答を Notebook やリポジトリに入れない。** 教員用解答は `solutions/`（Git 管理外）に置く。
- 未実装の関数は `raise NotImplementedError("学生実装課題")`。動作確認は共通関数 `check()` を使い、`NotImplementedError` だけを捕捉する（他の例外は隠さない）。
- 各テーマの章は第0〜3章だけに依存する。他テーマの変数・関数・データファイルを使わない（`tests/test_notebook.py` で検査）。
- セルの表示：【教員提供コード】【学生実装課題：Level 1】【学生実装課題：Level 2】【発展課題：Level 3】【動作確認】【ヒント】【考察課題】。
- 主要アルゴリズムは標準ライブラリで実装させる（pandas の groupby などで済ませない）。matplotlib・pandas は可視化・確認用の任意依存。

## Notebook の編集方法

- Notebook は `scripts/build_notebook.py` から生成する。**ipynb を直接編集しない**（再生成で上書きされる）。
- 変更後は必ず：`.venv/bin/python scripts/build_notebook.py` → `.venv/bin/python -m unittest discover -s tests -t .`
- 出力（outputs）を含めずにコミットする（ビルドスクリプトは出力なしで書き出す）。

## 日本語表記

教材として読む部分（Markdown、コメント、docstring、TODO、ヒント、文書、グラフのラベル）は**自然で短い日本語**。
プログラムとして扱う部分（変数名、関数名、ファイル名、CSV カラム名、ライブラリ名、コマンド、データセットの正式名称、原データのラベル値）は英語。
専門用語は初出で日本語と英語を併記する（例：閾値（Threshold））。留学生向けに長い文・難しい語を避ける。

## データ方針（B：教育用簡略版）

- Mini（Notebook 内 5〜10 件、人工）→ Tiny（CSV 20〜50 件、人工）→ Small（公開データ由来 500〜5,000 件、Phase 2）→ Benchmark（生成、Phase 4）。
- Level 1 は Mini と Tiny だけで完了できること。Small がなくても Notebook が止まらないこと。
- 人工データ・公開データ（研究用／実運用）・加工データを明確に区別する。存在しない情報を捏造しない。未知ラベルを正常に置き換えない。
- 学生が計算すべき集計値や異常度を前処理で計算済みにしない。
- **再配布条件が確認できない公開データは、学生配布用ファイルに入れない。** 原データは `data/raw/`（Git 管理外）。
- Tiny Dataset は `scripts/generate_synthetic_data.py`（シード固定）で生成し、`scripts/validate_datasets.py` で検証する。

## ストレージ・依存関係

- 次の作業は事前に教員の承認を得る：500MB 超のファイルのダウンロード、合計 2GB 超の取得・展開、PCAP の取得、大規模な依存パッケージの追加。
- Windows 側 C: ドライブの空きは少ない（Phase 1 時点で約 6GB）。WSL の Linux 側に保存する。
- 開発用の Python 環境はこのディレクトリの `.venv/`（Git 管理外、`requirements-dev.txt`）。グローバル環境や他プロジェクトの仮想環境を変更しない。
- CIC 系データのダウンロードには氏名・メールアドレス等の登録フォームがある。**Claude が教員の個人情報をフォームに送信しない。**教員が手動で行う。

## Git

- 作業ブランチ：`feature/c1-integrated-starter`。コミットは教員の指示があるときだけ。
- 承認なしに行わない：push、マージ、`reset --hard`、`git clean`、履歴の書き換え、force push、ブランチ・タグの削除、リモート設定・リポジトリ名・公開範囲の変更、外部リポジトリの作成。
- 親リポジトリの `.gitignore` は `*.log` と `textbook/**/*.py` を除外している点に注意。

## 安全性と倫理

オフライン分析のみ。実ネットワークのスキャン、実サービスへの攻撃リクエスト、不正認証、マルウェア実行、ファイルの破壊・暗号化、設定変更、データの持ち出しを行う機能は作らない。
データ内の攻撃に似た文字列は安全なテキストとして扱い、実行・評価しない。検出結果は「調べる必要がある候補」と表現する。
