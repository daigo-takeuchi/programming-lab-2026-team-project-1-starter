# 既存プロジェクトの監査報告（Phase 1）

調査日：2026-11-26　／　調査対象：`c1-web-attack-detection/`（改訂前の状態＝コミット `e3f993e`）

## 1. 所在と Git 管理状態

| 項目 | 結果 |
| --- | --- |
| 絶対パス | `/home/daigo/Programming_Lab_2026/programming-lab-2026-team-project-1-starter/c1-web-attack-detection` |
| Git リポジトリのルート | 親ディレクトリ `programming-lab-2026-team-project-1-starter`（A1〜G2 の 24 トピックを含むモノレポ） |
| 調査時のブランチ | `main`（`origin/main` と同期） |
| 未コミット変更・未追跡ファイル | なし（`git status` がクリーン） |
| Git 管理外（ignore）のファイル | `textbook/ssearch_while.py`、`__pycache__/` |
| コミット履歴 | `7e2966d` Initial commit（全トピック）、`e3f993e` 親 README に難易度の目安を追加。C1 の変更は初回コミットのみ |
| リモート | `origin` = `https://github.com/daigo-takeuchi/programming-lab-2026-team-project-1-starter.git` |
| 大容量ファイル | なし（C1 全体で 84KB） |

**影響：** 改訂用ブランチはモノレポ全体のブランチになる。C1 以外のディレクトリには変更を加えないこと。

## 2. 改訂前のディレクトリ構成

```text
c1-web-attack-detection/
├── .gitignore            Python・仮想環境・エディタ等の除外（25 行）
├── README.md             旧教材の説明（457 行、27.5KB、日本語）
├── starter.py            実行例：読み込み → 2 方式で集計 → 比較 → 固定閾値で検出
├── log_parser.py         Apache Common Log 形式に近いログの読み込み（正規表現、ipaddress、datetime）
├── detection.py          IP 別集計（count_linear：線形探索版、count_dict：辞書版）、閾値判定
├── benchmark.py          合成ログ生成（RFC 5737 アドレス、シード固定）と 1 回の測定例、TODO 9 個
├── data/sample_access.log  人工アクセスログ 48 行（うち 1 行は意図的な不正行）
├── textbook/__init__.py  空ファイル
├── textbook/ssearch_while.py  教科書（柴田望洋『新・明解 Pythonで学ぶアルゴリズムとデータ構造』）の線形探索。Git 管理外
└── tests/test_parser.py, tests/test_detection.py  unittest 17 件
```

CLAUDE.md、Jupyter Notebook、requirements.txt、設計文書は存在しなかった。

## 3. 動作確認の結果（改訂前のコードに対して実行）

| 確認 | コマンド | 結果 |
| --- | --- | --- |
| 単体テスト | `python3 -m unittest tests.test_detection tests.test_parser` | **17 件すべて成功** |
| 旧 README 記載のコマンド | `python3 -m unittest discover -s tests -v` | 成功（17 件） |
| `-t .` を付けた discover | `python3 -m unittest discover -s tests -t .` | 失敗（`tests/__init__.py` がないため）→ Phase 1 で `tests/__init__.py` を追加して解消 |
| 実行例 | `python3 starter.py` | 成功。47 件読み込み、不正 1 行、アクセス集中 `203.0.113.50`、404 集中 `198.51.100.66` を検出 |
| ベンチマーク | `python3 benchmark.py` | 成功。N=2,000、U=200 で線形探索版 0.0133 秒、辞書版 0.00046 秒 |

外部通信・ファイル変更を伴う処理は既存コードに含まれないことを、実行前にコードを読んで確認した。

## 4. 既存コードの主要機能と評価

| ファイル | 主な機能 | 品質 | 新教材の難易度との関係 |
| --- | --- | --- | --- |
| `log_parser.py` | 正規表現によるログ解析、IP・日時の検証、不正行の分離 | 良好（テスト 7 件） | 正規表現・`datetime`・タイムゾーンは Level 1 には難しい。**教員提供コード**として C-1C の Level 3 で利用するのが適切 |
| `detection.py` | `count_linear`（教科書の `seq_search` で線形探索、並列リスト）、`count_dict`、`find_over_threshold` | 良好（テスト 10 件） | **完成済み**のため学生 TODO にならない。考え方（基本版 O(N×U) vs 辞書版 O(N)）は新教材の C-1A/B/E の STEP 3〜4 にそのまま引き継いだ |
| `benchmark.py` | 合成データ生成（RFC 5737 アドレス、シード固定）、`perf_counter` による測定例 | 良好 | Benchmark Dataset 生成と実行時間計測の**共通機能**の原型として再利用できる（Phase 4） |
| `starter.py` | 一連の処理の実行例 | 良好 | Notebook に置き換わる。移行期間は維持 |
| `textbook/ssearch_while.py` | 線形探索（while 文） | 第三者の著作物 | **Git 管理外**のため、リポジトリを clone しただけでは `detection.py`・`starter.py`・`tests/test_detection.py` が動かない（ImportError）。新 Notebook はこれに依存しない設計にした |
| `data/sample_access.log` | 人工ログ（アクセス集中、404 集中、正常、不正行） | 良好、再配布上の問題なし（教員作成・RFC 5737 アドレス） | C-1C の追加データとして再利用可。ただし SQL Injection・XSS などの文字列は含まない |
| `README.md` | 研究課題（RQ1〜3）、計算量、誤検知の説明、Core/Advanced 課題 | 充実 | 「検出 ≠ 攻撃の確定」「正常な 404・アクセス集中」の説明は新教材の各章の注意書きに反映した |

## 5. 既存成果物の分類

| 分類 | 成果物 |
| --- | --- |
| 1. そのまま再利用 | `data/sample_access.log`、`tests/test_parser.py`、`tests/test_detection.py`（旧教材の回帰テストとして）、`.gitignore` の既存設定 |
| 2. 一部改訂して再利用 | `README.md`（`docs/legacy/` に移し、新 README を作成）、`benchmark.py` の `make_ip`・`make_records`（Benchmark 生成の原型） |
| 3. 全テーマの共通機能として再利用 | 線形探索 vs 辞書の比較という教材構成、`perf_counter` による計測手順、「候補であって確定ではない」という表現方針、RFC 5737 アドレスの使用 |
| 4. 発展課題として再利用 | `log_parser.py`（C-1C Level 3：アクセスログの解析）、`detection.find_over_threshold`、404 エラー率・時間窓の課題（旧 Advanced A〜D） |
| 5. 新規実装が必要 | C-1A/B/D/E のすべて、C-1C の文字列ルール課題、統合 Notebook、Tiny Dataset、データ検証、Small Dataset の前処理 |
| 6. 不要・削除候補 | `starter.py`（Notebook 移行後）、`textbook/`（教科書コードへの依存をやめる場合）。**削除は教員の承認後** |

## 6. 学生配布上の注意点

- Git 履歴（2 コミット）に、秘密情報・完成解答・再配布不可のデータは含まれていない（`textbook/*.py` は初回から除外済み）。
- `detection.py` には旧教材の「集計の完成コード」が入っている。新教材の Level 2 改良課題（辞書による集計）の答えに近いため、新教材のみを学生に配布する場合は除外を検討する（移行計画 6 章）。
