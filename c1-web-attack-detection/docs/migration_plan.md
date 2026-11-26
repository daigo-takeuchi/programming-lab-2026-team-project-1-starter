# 移行計画：旧 C1（Web アクセスログ）→ C-1 統合教材（全5テーマ）

作成：Phase 1（2026-11-26）

## 1. 改訂前と改訂後

| | 改訂前（旧 C1） | 改訂後（C-1 統合教材） |
| --- | --- | --- |
| テーマ | Web サーバーのアクセスログ 1 テーマ | C-1A〜C-1E の 5 テーマ |
| 形式 | Python スクリプト（`starter.py` など） | 1 つの Jupyter Notebook（全10章） |
| 学生の作業 | 集計は完成済み。TODO はコメントのみ（閾値の変更、ベンチマーク等） | 基本アルゴリズムから小さな TODO で実装（1 テーマ Level 1 が 4 関数） |
| データ | 人工ログ 1 本 | Mini（Notebook 内）＋ Tiny（CSV）＋ Small（公開データ、Phase 2）＋ Benchmark（生成） |
| 外部依存 | 教科書コード（Git 管理外）が必要 | 標準ライブラリのみ（matplotlib は任意） |

## 2. 改訂後の構成（Phase 1 時点）

```text
c1-web-attack-detection/
├── CLAUDE.md, README.md, TASKS.md         新規（README は全面改訂）
├── requirements.txt, requirements-dev.txt 新規
├── .gitignore                             追記（原データ・results・解答・秘密情報）
├── C1_cybersecurity_starter.ipynb         新規（scripts/build_notebook.py で生成）
├── data/README.md, data/c1a〜c1e/*_tiny.csv  新規
├── data/sample_access.log                 維持
├── scripts/build_notebook.py, generate_synthetic_data.py, validate_datasets.py  新規
├── tests/__init__.py, test_notebook.py, test_synthetic_data.py  新規
├── tests/test_parser.py, test_detection.py  維持
├── docs/*.md                              新規（本文書を含む）
├── docs/legacy/README_web_access_log.md   旧 README を移動（git mv、内容は無変更）
├── results/.gitkeep                       新規
└── starter.py, detection.py, log_parser.py, benchmark.py, textbook/  維持（移行期間）
```

### 目標構成からの変更点と理由

| 変更 | 理由 |
| --- | --- |
| `scripts/build_notebook.py` を追加 | Notebook を Python から生成し、差分管理とテストを容易にするため |
| `requirements-dev.txt` を追加 | 学生用依存（matplotlib のみ）と教員用依存（nbformat 等）を分けるため |
| `docs/legacy/` を追加 | 旧 README を削除せずに保存するため |
| `download_datasets.py`、`preprocess_c1*.py` は未作成 | 中身のないスクリプトを作らない方針。Phase 2 で作成 |

## 3. 既存ファイルの移行先

| 既存ファイル | 移行先・扱い | 時期 |
| --- | --- | --- |
| `README.md` | `docs/legacy/README_web_access_log.md`（移動済み）。説明の要点は Notebook 第6章・各章の注意書きへ | Phase 1 済 |
| `data/sample_access.log` | そのまま。C-1C の追加データ（Level 3）。Phase 2 で `log_parser` を使い CSV 化を検討 | Phase 2 |
| `log_parser.py` | C-1C Level 3 の教員提供コードとして Notebook に取り込む（正規表現部分を含めて提供） | Phase 3 |
| `detection.py` | 考え方は C-1A/B/E STEP 3〜4 に移行済み。ファイル自体は旧教材として維持 → 学生配布物からは除外を推奨 | Phase 5 で判断 |
| `benchmark.py` | `make_records` を Benchmark Dataset 生成（`generate_synthetic_data.py`）に一般化 | Phase 4 |
| `starter.py` | Notebook に置き換え。旧教材として維持 → `legacy/` への移動を提案 | Phase 5 で判断（要承認） |
| `tests/test_*.py`（旧） | 旧教材の回帰テストとして維持 | 継続 |
| `textbook/` | 新教材は依存しない。旧教材を残す間は維持 | Phase 5 で判断 |

## 4. テーマ別の移行内容

| テーマ | 再利用する既存成果物 | 新規に必要なもの |
| --- | --- | --- |
| C-1A | 線形探索版 vs 辞書版の集計（`detection.py` の構成）、ベンチマーク手順 | 通信フローの Mini/Tiny、ポート種類数（集合）、CIC-IDS2017 の前処理 |
| C-1B | 同上（ユーザー別集計に置き換え） | 認証ログの Mini/Tiny、Loghub OpenSSH の前処理 |
| C-1C | `sample_access.log`、`log_parser.py`、404・アクセス集中の課題（旧 Advanced A/B） | URL 文字列ルールの課題、HTTP リクエストの Tiny、CSIC 2010 等の入手 |
| C-1D | （直接の再利用なし）線形探索 vs 集合の比較の考え方 | ファイル状態の Mini/Tiny、Loghub Linux の前処理 |
| C-1E | 集計の構成、ベンチマーク手順 | 転送量の Mini/Tiny、CIC-IDS2017（C-1A と共用）の前処理 |

## 5. 難易度の調整

| 既存機能 | 判断 |
| --- | --- |
| 正規表現によるログ解析（`log_parser.py`） | Level 1 から外し、Level 3 の教員提供コードへ |
| 並列リスト＋教科書 `seq_search` による集計 | Level 1 では「一覧を作る → 関数で数える」の 2 段階に単純化（タプルのリストを返す） |
| 辞書による集計（`count_dict`、完成済み） | Level 2 の学生実装課題に変更 |
| 404 エラー率、時間窓、動的閾値 | Level 3 へ |
| N・U を変えたベンチマーク（TODO 9 個） | Level 2（実行時間の比較）と第9章の教員提供コード `measure_time` へ |
| `datetime` とタイムゾーン | Level 3 のみで使用 |

## 6. 学生配布時に除外するファイル（提案）

`scripts/`、`tests/`、`docs/`（`dataset_sources.md` の出典部分は README に要約）、`CLAUDE.md`、`requirements-dev.txt`、`.venv/`、`solutions/`、`data/raw/`、旧教材（`detection.py` は Level 2 の解答に近いため特に）。
配布方法の比較は `docs/implementation_plan.md` 5 章を参照。

## 7. 移行に伴うリスクと対策

| リスク | 対策 |
| --- | --- |
| モノレポのため、ブランチが全トピックに影響する | C1 ディレクトリ以外を変更しない。マージは教員の判断 |
| 親 README の C1 の説明（「線形探索・辞書による集計」、★評価）が新教材と合わなくなる | 親 README の修正を Phase 5 で提案（今回は変更しない） |
| Notebook の生成スクリプトと ipynb の二重管理 | `CLAUDE.md` に「ipynb を直接編集しない」と明記。テストで構造を検査 |
| 旧教材が教科書コード（Git 管理外）に依存し、clone 後に動かない | 新教材は依存しない。旧教材を配布する場合は README の手順で配置 |
| 公開データの再配布条件が不明確 | 条件が確認できるまで学生配布物に含めない（`dataset_feasibility_report.md`） |
| 学生が Notebook を同時編集してマージが難しい | TASKS.md で担当セルの分担とこまめなコミットを指示。Phase 5 で `nbdime` 等の紹介を検討 |
