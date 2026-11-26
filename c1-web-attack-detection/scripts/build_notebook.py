"""統合 Notebook（C1_cybersecurity_starter.ipynb）を生成するスクリプト（教員用マスター）

- Notebook の内容は、このスクリプトの中に Python の文字列として書いてある。
  教材を直すときは、このスクリプトを直してから Notebook を再生成する（ipynb を直接編集しない）。
- 生成した Notebook は、学生に配布した後は**学生が直接編集する成果物**になる。
  学生が編集した Notebook に、このスクリプトで上書きしてはいけない。
  そのため、出力先の Notebook に実行結果（outputs）が残っている場合は、上書きを拒否する（--force で強制）。
- このスクリプトは学生への配布物に含めない（docs/student_distribution_plan.md）。

使い方（c1-web-attack-detection ディレクトリで実行する）:
    .venv/bin/python scripts/build_notebook.py                 # 教員用マスターを再生成する
    .venv/bin/python scripts/build_notebook.py --output x.ipynb  # 別のファイルに書き出す

必要なライブラリ: nbformat（教員の開発環境のみ。学生には不要）
"""

import argparse
import hashlib
import json

import textwrap
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT = PROJECT_DIR / "C1_cybersecurity_starter.ipynb"

TEACHER = "**【教員提供コード】** そのまま実行してください。"
LEVEL1 = "**【学生実装課題：Level 1】**"
LEVEL2 = "**【学生実装課題：Level 2】**"
LEVEL3 = "**【発展課題：Level 3】**"
CHECK = "**【動作確認】** 実装した後に実行してください。未実装のときは「[未実装]」と表示されます。"
HINT = "**【ヒント】**"
THINK = "**【考察課題】**"

cells = []


def md(text):
    cells.append(new_markdown_cell(textwrap.dedent(text).strip()))


def code(text):
    cells.append(new_code_cell(textwrap.dedent(text).strip()))


def hints(h1, h2, h3):
    """3 段階のヒントを、折りたたみ表示の Markdown として追加する"""
    md(f"""
    {HINT}（分からないときだけ、順番に開いてください）

    <details><summary>ヒント1：考え方</summary>

    {h1}

    </details>
    <details><summary>ヒント2：使う文法</summary>

    {h2}

    </details>
    <details><summary>ヒント3：疑似コード</summary>

    ```text
    {textwrap.indent(textwrap.dedent(h3).strip(), "    ").lstrip()}
    ```

    </details>
    """)


# ======================================================================
# 第0章
# ======================================================================
md("""
# C-1：サイバー攻撃の検出
## ― ネットワーク・Web・API・システムを対象としたセキュリティ監視システムの開発 ―

**C-1 Cybersecurity Programming Starter**（プログラミング演習Ⅰ チーム開発課題）

> **この Notebook について**
> Level 1・Level 2 の課題、動作確認、実行時間の比較、グラフは、すべてこの Notebook と `data` フォルダだけで実行できます。
> C-1A・C-1E の公開データ（Level 3 の一部）は準備中です。その部分は人工データで進めてください。

**最初にすること：** 第0章の「0.5 学習ルート」を読み、自分のチームが実行する章を確認してください。
""")

md("""
# 第0章　本演習の目的と進め方

## 0.1 この演習で何をするのか

会社や学校のコンピュータは、毎日たくさんの**記録（ログ）**を残しています。
「だれが、いつ、どこへ、何をしたか」という記録です。

セキュリティ担当者は、この記録の中から**いつもと違う動き**を探します。
これを**異常検出（Anomaly Detection）**と呼びます。

この演習では、Python を使って小さな**セキュリティ監視プログラム**を作ります。
目標はセキュリティの専門家になることではありません。
**現実の問題を、Python で処理できる小さな問題に分けて解く経験**をすることが目標です。

## 0.2 全5テーマの概要

| テーマ | 章 | 最初の問い | 主に使う Python |
| --- | --- | --- | --- |
| C-1A ネットワーク探索・異常通信の検出 | 第4章 | どのコンピュータが異常に多く通信しているか？ | for 文、if 文、辞書、集合 |
| C-1B 不正認証・アカウント悪用の検出 | 第5章 | どのユーザーが何度もログインに失敗しているか？ | for 文、if 文、辞書 |
| C-1C Web・APIへの不正アクセスの検出 | 第6章 | どの Web リクエストに通常と違う特徴があるか？ | 文字列処理、リスト |
| C-1D 不正操作・システム改変の検出 | 第7章 | 変更前と変更後で、どのファイルが追加・削除・変更されたか？ | リスト、集合、辞書 |
| C-1E 情報流出・異常データ転送の検出 | 第8章 | どのコンピュータが異常に大量のデータを送信しているか？ | for 文、合計、辞書 |

### C-1A と C-1E の違い

どちらも「通信のデータ」を使いますが、見るところが違います。

- **C-1A**：通信の**回数**、宛先ポートの**種類の数**、特定の相手への**集中**を見ます。
- **C-1E**：送信したデータの**量（バイト数）の合計**、送信先、**いつもとの違い**を見ます。

## 0.3 学習目標

- 変数、条件分岐、for 文、while 文、関数を使って、小さな処理を書ける。
- リスト、辞書、集合を目的に合わせて使い分けられる。
- CSV ファイルを読み込み、データを探す・数える・比べる処理を書ける。
- 閾値（Threshold）を使って、異常の候補を取り出せる。
- 同じ結果を出す 2 つのアルゴリズムを、実行時間と計算量で比べられる。
- テストで、プログラムが正しく動くことを確認できる。
- Git を使って、チームで開発を進められる。

## 0.4 3 つのレベル

| レベル | 位置づけ | 対応する STEP | 内容 |
| --- | --- | --- | --- |
| **Level 1：基本課題** | **必須** | STEP 1〜3 | 小さなデータで、異常の候補を見つけるプログラムを完成させる |
| **Level 2：改良課題** | 推奨 | STEP 4 | 辞書・集合などでプログラムを改良し、実行時間を比べる |
| **Level 3：発展課題** | 選択 | STEP 5 | 公開データへの適用、時間窓、検出性能の評価、独自機能 |

各テーマの章は、同じ 5 つの STEP でできています。

1. **STEP 1：データを見て理解する**（Level 1）
2. **STEP 2：数える・探す・比較する**（Level 1）
3. **STEP 3：異常を検出する**（Level 1）
4. **STEP 4：アルゴリズムを改良する**（Level 2）
5. **STEP 5：実データで評価・発展させる**（Level 3）

## 0.5 学習ルート（担当テーマ別）

**全5テーマを順番に実行する必要はありません。** 次の順に進めてください。

| 順番 | 内容 | 場所 | 必須？ |
| ---: | --- | --- | --- |
| 1 | 演習の目的と進め方 | 第0章 | 必須 |
| 2 | 実行環境の準備 | 第1章 | 必須 |
| 3 | データセットの概要 | 第2章 | 必須 |
| 4 | Python の基本操作と共通関数 | 第3章 | 必須（3.7 の共通関数のセルは必ず実行） |
| 5 | 担当テーマの **Level 1**（STEP 1〜3） | 担当章の N.1〜N.7 | **必須** |
| 6 | 担当テーマの **Level 2**（STEP 4） | 担当章の N.8 | 推奨 |
| 7 | 担当テーマの **Level 3**（STEP 5） | 担当章の N.9〜N.10 | 選択 |
| 8 | 評価と成果発表 | 第9章 | 必須 |

| 担当テーマ | 実行する章 | Level 1 の範囲 | Level 2 | Level 3 |
| --- | --- | --- | --- | --- |
| C-1A | 第0〜3章 → **第4章** → 第9章 | 4.1〜4.7 | 4.8 | 4.9〜4.10 |
| C-1B | 第0〜3章 → **第5章** → 第9章 | 5.1〜5.7 | 5.8 | 5.9〜5.10 |
| C-1C | 第0〜3章 → **第6章** → 第9章 | 6.1〜6.7 | 6.8 | 6.9〜6.10 |
| C-1D | 第0〜3章 → **第7章** → 第9章 | 7.1〜7.7 | 7.8 | 7.9〜7.10 |
| C-1E | 第0〜3章 → **第8章** → 第9章 | 8.1〜8.7 | 8.8 | 8.9〜8.10 |

> **Level 1 を完了すれば、「データを読む → 数える・集計する → 閾値で異常の候補を見つける」という、
> 基本的なセキュリティ監視プログラムが完成します。** Level 2・Level 3 は、それをより速く・より賢くする課題です。

他のチームの章も自由に読んでかまいません。Notebook を開き直したときは、第1章と 3.7 の共通関数のセルを実行してから、担当章に戻ってください。

## 0.6 セルの種類

| 表示 | 意味 |
| --- | --- |
| **【教員提供コード】** | そのまま実行できるコードです。変更する必要はありません。 |
| **【学生実装課題：Level 1】** | 基本課題です。`TODO` の部分を自分で書きます。 |
| **【学生実装課題：Level 2】** | 改良課題です。 |
| **【発展課題：Level 3】** | 発展課題です。チームで選んで取り組みます。 |
| **【動作確認】** | 期待される結果と、実際の結果を比べます。`[OK]`・`[NG]`・`[未実装]`・`[エラー]` のどれかが表示されます（3.7 で説明します）。 |
| **【ヒント】** | 考え方のヒントです。3 段階あるので、順番に開いてください。 |
| **【考察課題】** | 結果について考え、文章で答えます。 |

**あなたが編集するのは【学生実装課題】のセルだけです。** それ以外のセルは、上から順に実行するだけで大丈夫です。

学生実装課題の関数は、最初は `raise NotImplementedError("学生実装課題")` と書かれています。
このまま実行すると、動作確認のセルに **「[未実装]」** と表示されます。これはエラーではありません。
`raise NotImplementedError(...)` の行を消して、自分のコードを書いてください。

1 つの課題は、次の順に並んでいます。**課題に必要な説明は、すべてこのまとまりの中にあります。**

1. 課題の説明（何を作るか、入力と期待する出力の例）
2. 【学生実装課題】のセル（ここを編集する）
3. 【ヒント】（必要なときだけ開く）
4. 【動作確認】のセル（実行して [OK] になるか確かめる）

**ヒントの表示について：** ヒントは「▶ ヒント1：考え方」のような折りたたみ表示になっています。クリックすると開きます。
環境によって折りたたみが使えない場合は、ヒントがそのまま表示されます。その場合は、自分で考えてから順番に読んでください。

## 0.7 チーム開発の進め方

- まず全員で STEP 1 のデータを見て、問題を理解します。
- Level 1 の課題を分担して実装します。**全員が少なくとも 1 つの関数を実装**してください。
- 動作確認のセルで、全員の関数が正しく動くことを確認します。
- Level 2・Level 3 は、チームで相談して選びます。
- 詳しくは `TASKS.md` と第9章を読んでください。

## 0.8 安全性と倫理についての注意（必ず読むこと）

この演習で扱うのは、**保存済みのデータ・公開された研究用データ・人工的に作ったデータ**だけです。
すべて自分のコンピュータの中で分析します（オフライン分析）。

次のことは**絶対に行わないでください**。法律（不正アクセス禁止法など）に違反するおそれがあります。

- 許可なく、実際のネットワークやコンピュータを調べる（スキャンする）こと
- 実際の Web サイトや API に、攻撃に似たリクエストを送ること
- 他人のアカウントでログインを試すこと
- マルウェアを実行すること、ファイルを壊したり暗号化したりすること
- システムの設定を勝手に変えること、データを外部に持ち出すこと

データの中には、攻撃に似た文字列（例：`<script>`）が含まれることがあります。
これらは**ただの文字列として扱い**、絶対にプログラムやコマンドとして実行しないでください。

また、この演習で見つけるのは**「調べる必要がある候補」**です。
「攻撃者を特定した」「攻撃だと確定した」と考えてはいけません。
""")

# ======================================================================
# 第1章
# ======================================================================
md("""
# 第1章　実行環境の準備

この章のコードは、**全チームが最初に 1 回実行**します。

- Python のバージョン
- ライブラリが使えるかどうか
- データのフォルダの場所

を確認します。基本課題（Level 1）は、**Python の標準ライブラリだけ**で実行できます。
""")
md(TEACHER)
code('''
# 【教員提供コード】Python のバージョンと実行環境の確認
import sys
import platform

print("Python のバージョン:", platform.python_version())
print("OS:", platform.system(), platform.release())

if sys.version_info < (3, 10):
    print("[注意] Python 3.10 以上を推奨します（この教材は 3.11〜3.13 を想定しています）。")
''')
md(TEACHER)
code('''
# 【教員提供コード】基本的な import（すべて Python の標準ライブラリ）
import csv
import random
import statistics
import time
from pathlib import Path

# 追加のライブラリ（なくても基本課題は実行できる）
import importlib.util

HAS_MATPLOTLIB = importlib.util.find_spec("matplotlib") is not None
HAS_PANDAS = importlib.util.find_spec("pandas") is not None
print("matplotlib（グラフ表示）:", "使える" if HAS_MATPLOTLIB else "使えない（グラフ以外は実行できます）")
print("pandas（表の表示）     :", "使える" if HAS_PANDAS else "使えない（なくても実行できます）")
''')
md(TEACHER)
code('''
# 【教員提供コード】データフォルダの場所を決める
# この Notebook と同じフォルダにある data/ を使う（相対パス）。
BASE_DIR = Path.cwd()
if not (BASE_DIR / "data").exists() and (BASE_DIR / "c1-web-attack-detection" / "data").exists():
    # リポジトリ全体を取得して、その一番上のフォルダで実行した場合
    BASE_DIR = BASE_DIR / "c1-web-attack-detection"

DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"

print("作業フォルダ:", BASE_DIR)
if DATA_DIR.exists():
    print("データフォルダ: OK")
else:
    print("[注意] data フォルダが見つかりません。")
    print("  Notebook だけでなく、data フォルダを含む教材一式を取得してください（README.md 参照）。")
    print("  Mini Dataset（Notebook の中のデータ）だけなら、このまま演習を進められます。")
''')
md(TEACHER)
code('''
# 【教員提供コード】グラフの日本語表示の設定（matplotlib がある場合だけ）
JAPANESE_FONT = None
if HAS_MATPLOTLIB:
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    candidates = ["IPAexGothic", "IPAGothic", "Noto Sans CJK JP", "Noto Sans JP",
                  "Yu Gothic", "Meiryo", "Hiragino Sans", "MS Gothic"]
    installed = {font.name for font in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in installed:
            JAPANESE_FONT = name
            plt.rcParams["font.family"] = name
            break

if JAPANESE_FONT:
    print("グラフの日本語フォント:", JAPANESE_FONT)
else:
    print("日本語フォントがないため、グラフの文字は英語で表示します。")
''')

# ======================================================================
# 第2章
# ======================================================================
md("""
# 第2章　データセットの概要と使い方

## 2.1 4 種類のデータ

この教材では、データを**小さいものから順番に**使います。

| 名前 | 件数の目安 | 置き場所 | 作り方 | 主な使いみち |
| --- | --- | --- | --- | --- |
| **Mini Dataset** | 5〜10 件 | Notebook の中 | 人工データ | 手で数えて確認しながら、最初の関数を作る |
| **Tiny Dataset** | 20〜50 件 | `data/c1x/*_tiny.csv` | 人工データ | 正常・異常・境界の例でテストする |
| **Small Dataset** | 数百〜数千件 | `data/c1x/*_small.csv` など | 公開データを教員が加工（C-1C は人工データ） | Level 3 で実際のデータに使ってみる |
| **Benchmark Dataset** | 1,000〜100,000 件 | 必要なときに生成 | 人工データ | 実行時間と計算量の比較 |

使う順番：**Mini → Tiny → Small → Benchmark**

- 基本課題（Level 1）は、**Mini と Tiny だけで完了できます**。
- Small Dataset がまだない場合でも、演習は進められます。

| テーマ | Level 3 で使うデータ | 状態 |
| --- | --- | --- |
| C-1A | CIC-IDS2017（研究用の公開データ） | 準備中（なければ Tiny Dataset を使う） |
| C-1B | Loghub OpenSSH（実サーバーの公開ログ） | 用意済み |
| C-1C | 旧教材の人工アクセスログ | 用意済み |
| C-1D | Loghub Linux（実サーバーの公開ログ） | 用意済み |
| C-1E | CIC-IDS2017（C-1A と共用） | 準備中（なければ Tiny Dataset を使う） |

## 2.2 人工データと公開データの違い

| 種類 | 説明 | 注意 |
| --- | --- | --- |
| 人工データ | 教材のために作ったデータ。異常がどこにあるか分かっている | 人工データでうまく検出できても、実際の環境で同じように検出できるとは限らない |
| 公開データ（研究用） | 研究者が実験環境で集めて公開したデータ | 実験環境なので、実際の会社のネットワークとは違う |
| 公開データ（実運用のログ） | 実際に動いていたシステムのログ | 正解ラベル（攻撃かどうか）がないことが多い |

## 2.3 CSV ファイルの形

CSV（Comma-Separated Values）は、カンマで区切った表のデータです。
1 行目は**カラム名（列の名前）**、2 行目からが**レコード（1 件分のデータ）**です。

```text
record_id,timestamp,src_ip,dst_ip,dst_port,label
1,2026-11-20T10:04:47,192.0.2.11,198.51.100.10,443,benign
```

## 2.4 正解ラベル（label）の意味

`label` 列は「そのレコードが何であるか」の答えです（例：`benign` = 正常）。

- **検出プログラムの入力に `label` を使ってはいけません。** 答えを見ながら検出するのと同じだからです。
- `label` は、検出結果が正しかったかを**後で確かめる（評価する）**ためだけに使います。
- 公開データには `label` がないこともあります。そのときは「異常の候補」を見つけるところまでを行います。

## 2.5 データファイルの一覧

次のセルは、data フォルダにあるファイルの**名前と大きさだけ**を表示します（中身は読み込みません）。
各テーマのデータは、それぞれの章で読み込みます。
""")
md(TEACHER)
code('''
# 【教員提供コード】data フォルダにある CSV ファイルの一覧（中身は読み込まない）
if DATA_DIR.exists():
    for path in sorted(DATA_DIR.glob("*/*.csv")):
        print(f"{str(path.relative_to(DATA_DIR)):45s} {path.stat().st_size:>8,} バイト")
else:
    print("data フォルダがありません。")
''')

# ======================================================================
# 第3章
# ======================================================================
md("""
# 第3章　Python の基本操作と共通関数

この章では、演習で使う Python の文法を短い例で復習します。
例は、セキュリティとは関係のない簡単なものにしています。

最後に、全テーマで使う**共通関数**（CSV の読み込み、表示、動作確認）を定義します。
**3.7 の共通関数のセルは、必ず実行してください。**

## 3.1 リスト
""")
code('''
# リスト：順番のあるデータの並び
fruits = ["apple", "banana", "apple", "cherry"]
print(fruits[0])       # 先頭の要素
print(len(fruits))     # 要素の数
fruits.append("melon") # 末尾に追加
print(fruits)
''')
md("## 3.2 辞書（dict）\n\n辞書は「キー → 値」の組を保存します。キーを使うと、値をすぐに取り出せます。")
code('''
prices = {"apple": 120, "banana": 90}
print(prices["apple"])          # キーで値を取り出す
prices["cherry"] = 300          # 新しいキーを追加する
prices["apple"] = 130           # 値を書き換える
print("banana" in prices)       # キーがあるかどうか（True / False）
print(prices.get("melon", 0))   # キーがなければ 0 を返す
for name, price in prices.items():
    print(name, price)
''')
md("## 3.3 集合（set）\n\n集合は**重複のない**データの集まりです。順番はありません。")
code('''
colors = {"red", "blue", "red", "green"}
print(colors)              # "red" は 1 つだけになる
print(len(colors))         # 種類の数
a = {"red", "blue", "green"}
b = {"blue", "yellow"}
print(a - b)               # a にあって b にないもの（差集合）
print(a & b)               # 両方にあるもの（積集合）
''')
md("## 3.4 for 文と if 文")
code('''
scores = [72, 45, 90, 60, 38]
passed = []
for score in scores:
    if score >= 60:
        passed.append(score)
print("60点以上:", passed)
''')
md("## 3.5 関数と assert による確認\n\n`assert 条件` は、条件が False のときにエラーを出します。プログラムが正しいかを確かめるのに使います。")
code('''
def is_even(number):
    """number が偶数なら True、奇数なら False を返す"""
    return number % 2 == 0

assert is_even(4) == True
assert is_even(7) == False
print("is_even のテスト：すべて成功")
''')
md("""
## 3.6 while 文

while 文は「条件が True の間」くり返します。リストを先頭から 1 つずつ調べる**線形探索**にも使えます。
""")
code('''
numbers = [8, 3, 5, 9]
target = 5
i = 0
while i < len(numbers) and numbers[i] != target:
    i += 1
print("見つかった位置:", i if i < len(numbers) else "なし")
''')
md(f"""
## 3.7 共通関数（全テーマで使う）

{TEACHER}

| 関数 | 何をするか |
| --- | --- |
| `load_csv(path, int_columns)` | CSV を読み込み、辞書のリストにする。`int_columns` に書いた列は整数に変換する |
| `show_records(records, limit)` | 辞書のリストを表の形で表示する |
| `check(label, func, args, expected)` | 関数を実行し、期待される結果と比べて結果を表示する |

`check` の表示は 4 種類です。

| 表示 | 意味 | どうするか |
| --- | --- | --- |
| `[OK]` | 期待される結果と一致した | 次の課題へ進む |
| `[未実装]` | `raise NotImplementedError` が残っている | 関数を実装する |
| `[エラー]` | 関数の実行中にエラーが起きた（未実装ではない） | 表示された「場所」の行を見直す |
| `[NG]` | 実行できたが、結果が期待と違う | 「違い」の説明を読んで、処理を見直す |
""")
code('''
# 【教員提供コード】共通関数（データの読み込み・表示・動作確認）
import traceback


def load_csv(path, int_columns=()):
    """CSV ファイルを読み込み、1 行を 1 つの辞書にしたリストを返す。

    引数:
        path: CSV ファイルの場所
        int_columns: 整数に変換する列の名前（リストまたはタプル）
    戻り値:
        辞書のリスト。ファイルがない場合は空のリスト
    """
    path = Path(path)
    if not path.exists():
        print(f"[注意] ファイルが見つかりません: {path}")
        return []
    records = []
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            for column in int_columns:
                row[column] = int(row[column])
            records.append(row)
    return records


def show_records(records, limit=10):
    """辞書のリストを、表の形で先頭から limit 件まで表示する"""
    if not records:
        print("（データがありません）")
        return
    columns = list(records[0].keys())
    shown = records[:limit]
    widths = [max(len(str(c)), *(len(str(r.get(c, ""))) for r in shown)) for c in columns]
    widths = [min(w, 40) for w in widths]   # 長すぎる値は 40 文字で切る
    print("  ".join(str(c).ljust(w) for c, w in zip(columns, widths)))
    for r in shown:
        print("  ".join(str(r.get(c, ""))[:w].ljust(w) for c, w in zip(columns, widths)))
    if len(records) > limit:
        print(f"... ほか {len(records) - limit} 件（全 {len(records)} 件）")


def _short(value, width=70):
    """値を短い文字列にする（長いリストは件数だけを表示する）"""
    if isinstance(value, list) and len(value) > 5:
        return f"リスト（{len(value)} 件）"
    text = repr(value)
    return text if len(text) <= width else text[:width] + "…"


def _describe_difference(expected, actual):
    """期待される結果と実際の結果の違いを、日本語で短く説明する"""
    if type(expected) is not type(actual):
        hint = "（return を書き忘れていませんか？）" if actual is None else ""
        return f"型が違います：期待 {type(expected).__name__}、実際 {type(actual).__name__}{hint}"
    if isinstance(expected, list):
        if len(expected) != len(actual):
            return f"要素の数が違います：期待 {len(expected)} 個、実際 {len(actual)} 個"
        for i, (e, a) in enumerate(zip(expected, actual)):
            if e != a:
                return f"{i} 番目（0 から数える）の要素が違います：期待 {_short(e)}、実際 {_short(a)}"
    if isinstance(expected, dict):
        missing = [k for k in expected if k not in actual]
        extra = [k for k in actual if k not in expected]
        if missing:
            return f"足りないキーがあります：{_short(missing)}"
        if extra:
            return f"余分なキーがあります：{_short(extra)}"
        for k in expected:
            if expected[k] != actual[k]:
                return f"キー {k!r} の値が違います：期待 {_short(expected[k])}、実際 {_short(actual[k])}"
    return "値が違います"


def check(label, func, args, expected):
    """func(*args) の結果を expected と比べて表示する。

    戻り値: 一致すれば True、違えば（エラーを含む）False、未実装なら None
    """
    try:
        actual = func(*args)
    except NotImplementedError:
        print(f"[未実装] {label}：この課題はまだ実装されていません。")
        return None
    except Exception as error:   # 未実装とは区別して、エラーの内容と場所を表示する（隠さない）
        frame = traceback.extract_tb(error.__traceback__)[-1]
        print(f"[エラー] {label}：実行中にエラーが起きました（未実装ではなく、実装の中に問題があります）。")
        print(f"     {type(error).__name__}: {error}")
        print(f"     場所: {frame.name}() の中の「{frame.line}」")
        return False
    if actual == expected:
        print(f"[OK] {label}")
        return True
    print(f"[NG] {label}")
    print(f"     入力          : {', '.join(_short(a, 40) for a in args)}")
    print(f"     期待される結果: {_short(expected, 200)}")
    print(f"     実際の結果    : {_short(actual, 200)}")
    print(f"     違い          : {_describe_difference(expected, actual)}")
    return False


print("共通関数を定義しました: load_csv, show_records, check")
''')
md("### 共通関数の使い方の例（セキュリティとは関係のない例）")
code('''
def double(x):
    return x * 2

def not_yet(x):
    raise NotImplementedError("学生実装課題")

def broken(x):
    return x * undefined_name   # わざとエラーを起こす

check("2 倍にする", double, (3,), 6)              # [OK]
check("わざと違う期待値", double, (3,), 7)        # [NG]
check("まだ作っていない関数", not_yet, (3,), 6)    # [未実装]
check("エラーが起きる関数", broken, (3,), 6)       # [エラー]
''')
md(f"""
## 3.8 評価とグラフの共通関数（Level 2・3 で使う）

{TEACHER} Level 1 だけに取り組む場合は、実行するだけで大丈夫です（中身を理解する必要はありません）。

| 関数 | 何をするか | 使う場所 |
| --- | --- | --- |
| `measure_time(func, args, repeat)` | `func(*args)` を何回か実行し、実行時間の**中央値**（秒）を返す | STEP 4、第9章 |
| `compare_speed(baseline, improved, make_input, sizes)` | 基本版と改良版を**同じ入力**で動かし、結果が同じか確かめてから実行時間を比べる | STEP 4 |
| `evaluate_detection(detected, actual, all_items)` | 検出結果を正解と比べ、正しく検出・見逃し・誤検出などを数える | STEP 3〜5、第9章 |
| `plot_bars(names, values, title, ylabel)` | 棒グラフを表示する（matplotlib がなければ文字で表示） | STEP 3 |
| `plot_speed(rows, title)` | データ件数と実行時間のグラフを表示する | STEP 4 |
""")
code('''
# 【教員提供コード】評価とグラフの共通関数

def measure_time(func, args, repeat=5):
    """func(*args) を repeat 回実行し、実行時間の中央値（秒）を返す。"""
    times = []
    for _ in range(repeat):
        start = time.perf_counter()
        func(*args)
        times.append(time.perf_counter() - start)
    return statistics.median(times)


def compare_speed(baseline, improved, make_input, sizes, same=None, repeat=3, time_limit=2.0):
    """基本版と改良版を、同じ入力で実行時間を比べる。

    引数:
        baseline, improved: 比べる 2 つの関数
        make_input: 件数 n を受け取り、関数に渡す引数のタプルを作る関数
        sizes: 試すデータ件数のリスト
        same: 2 つの結果が同じかを判定する関数（省略すると == で比べる）
        time_limit: 基本版が 1 回でこの秒数を超えたら、それより大きい件数は試さない
    戻り値:
        [(件数, 基本版の秒, 改良版の秒), ...]
    """
    rows = []
    for n in sizes:
        args = make_input(n)                       # データの生成は計測に含めない
        try:
            result_base = baseline(*args)
            result_improved = improved(*args)
        except NotImplementedError:
            print("[未実装] 基本版または改良版がまだ実装されていません。両方を実装してから実行してください。")
            return rows
        is_same = same(result_base, result_improved) if same else result_base == result_improved
        if not is_same:
            print(f"[NG] N = {n:,} のとき、基本版と改良版の結果が一致しません。速さを比べる前に、結果を一致させてください。")
            return rows
        t_base = measure_time(baseline, args, repeat)
        t_improved = measure_time(improved, args, repeat)
        rows.append((n, t_base, t_improved))
        ratio = f"{t_base / t_improved:.1f}" if t_improved > 0 else "-"
        print(f"N = {n:>7,}　基本版 {t_base:.5f} 秒　改良版 {t_improved:.5f} 秒　"
              f"（基本版の時間 ÷ 改良版の時間 = {ratio}）")
        if t_base > time_limit:
            print("基本版に時間がかかるため、これより大きい件数は試しません。")
            break
    if rows:
        print("結果は一致しました（[OK]）。時間はこのコンピュータでの実測値で、環境によって変わります。")
    return rows


def evaluate_detection(detected, actual_anomalies, all_items):
    """検出結果を評価する。

    引数:
        detected: 検出したもの（通信元、ユーザーなど）の集まり
        actual_anomalies: 実際に異常なものの集まり（正解ラベルから作る）
        all_items: 評価の対象すべての集まり
    戻り値:
        TP, FP, FN, TN と各指標の辞書（0 で割る場合は None）
    """
    detected, actual, items = set(detected), set(actual_anomalies), set(all_items)
    tp = len(detected & actual)
    fp = len(detected - actual)
    fn = len(actual - detected)
    tn = len(items - detected - actual)

    def ratio(a, b):
        return a / b if b > 0 else None

    precision = ratio(tp, tp + fp)
    recall = ratio(tp, tp + fn)
    f1 = None
    if precision is not None and recall is not None and precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn,
            "Accuracy": ratio(tp + tn, len(items)), "Precision": precision,
            "Recall": recall, "F1": f1, "FPR": ratio(fp, fp + tn)}


def show_evaluation(result, unit):
    """evaluate_detection の結果を、日本語で分かりやすく表示する"""
    print(f"評価の単位：{unit}")
    print(f"  正しく検出できた異常（TP）           : {result['TP']}")
    print(f"  見逃した異常（FN、検出漏れ）         : {result['FN']}")
    print(f"  正常なのに検出したもの（FP、誤検出） : {result['FP']}")
    print(f"  正しく正常と判定したもの（TN）       : {result['TN']}")
    for key, name in [("Precision", "適合率"), ("Recall", "再現率")]:
        value = result[key]
        print(f"  {name}（{key}）: {'-' if value is None else f'{value:.2f}'}")


def jp(japanese, english):
    """日本語フォントがあれば日本語、なければ英語のラベルを返す（グラフ用）"""
    return japanese if JAPANESE_FONT else english


def plot_bars(names, values, title, ylabel, highlight=()):
    """棒グラフを表示する。highlight に入っている名前の棒は色を変える。"""
    if not HAS_MATPLOTLIB:
        largest = max(values) if values else 1
        print(title)
        for name, value in zip(names, values):
            mark = " ←" if name in highlight else ""
            print(f"  {str(name):18s} {'#' * max(1, round(30 * value / largest)) if value else ''} {value:,}{mark}")
        return
    colors = ["tab:red" if name in highlight else "tab:blue" for name in names]
    plt.figure(figsize=(7, 3.5))
    plt.bar([str(n) for n in names], values, color=colors)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


def plot_speed(rows, title):
    """compare_speed の結果を、データ件数と実行時間の折れ線グラフにする"""
    if not rows:
        return
    if not HAS_MATPLOTLIB:
        print("（matplotlib がないため、グラフの代わりに上の表で確認してください）")
        return
    ns = [r[0] for r in rows]
    plt.figure(figsize=(6, 3.5))
    plt.plot(ns, [r[1] for r in rows], marker="o", label=jp("基本版", "baseline"))
    plt.plot(ns, [r[2] for r in rows], marker="s", label=jp("改良版", "improved"))
    plt.xlabel(jp("データ件数 N", "number of records N"))
    plt.ylabel(jp("実行時間（秒）", "time (s)"))
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


print("評価とグラフの共通関数を定義しました")
''')



# ======================================================================
# テーマ章（第4章〜第8章）を作る関数
# ======================================================================
def theme_chapter(t):
    n = t["no"]
    md(f"""
    # 第{n}章　{t['code']} {t['title']}

    > この章は、第0章〜第3章を実行した後なら、**他のテーマの章を実行しなくても**使えます。

    | この章の進め方 | 節 | 内容 |
    | --- | --- | --- |
    | まず読む | {n}.1〜{n}.4 | 問題・背景・課題の一覧・データ。{n}.2 は、最初は表だけ読めば十分です |
    | **Level 1（必須）** | {n}.5〜{n}.7 | データを見る → 課題1〜4 を実装する → Tiny Dataset に適用する |
    | Level 2（推奨） | {n}.8 | 辞書・集合などで改良する |
    | Level 3（選択） | {n}.9〜{n}.10 | 公開データ・発展課題・考察 |
    """)
    md(f"## {n}.1 このテーマで何を解決するのか\n\n" + textwrap.dedent(t["problem"]).strip()
       + ("\n\n" + textwrap.dedent(t["goal"]).strip() if "goal" in t else ""))
    md(f"## {n}.2 社会的背景と必要な技術知識\n\n" + textwrap.dedent(t["background"]).strip())
    md(f"## {n}.3 学習目標と課題の全体像\n\n" + textwrap.dedent(t["overview"]).strip())
    md(f"## {n}.4 使用するデータ\n\n" + DATA_TABLE_HEAD + textwrap.dedent(t["data"]).strip())

    # STEP 1
    md(f"""
    ## {n}.5 STEP 1：データを見て理解する

    **対応レベル：Level 1（基本課題）**　／　**学習目標：** データの各列の意味を説明できる。

    まず Mini Dataset を表示します。Notebook の中に直接書いてあるので、CSV ファイルがなくても実行できます。
    """)
    md(TEACHER)
    code(t["mini_code"])
    md(f"{THINK}（手で確認しよう）\n\n" + textwrap.dedent(t["mini_questions"]).strip())
    md("次に Tiny Dataset（人工データの CSV）を読み込みます。\n\n" + TEACHER)
    code(t["tiny_code"])

    # STEP 2
    md(f"""
    ## {n}.6 STEP 2：数える・探す・比較する

    **対応レベル：Level 1（基本課題）**　／　**学習目標：** for 文と if 文で、データを探す・数える処理を書ける。
    """)
    for task in t["step2"]:
        emit_task(task, LEVEL1)

    # STEP 3
    md(f"""
    ## {n}.7 STEP 3：異常を検出する

    **対応レベル：Level 1（基本課題）**　／　**学習目標：** STEP 2 の関数を組み合わせ、閾値で異常の候補を取り出せる。

    > **注意：** ここで見つかるのは「調べる必要がある**候補**」です。攻撃だと確定したわけではありません。
    """ + ("\n" + textwrap.indent(textwrap.dedent(t["step3_note"]).strip(), "    ") if "step3_note" in t else ""))
    for task in t["step3"]:
        emit_task(task, LEVEL1)
    md("### Tiny Dataset に適用する\n\n課題をすべて実装したら、Tiny Dataset でも試してみましょう。\n\n" + TEACHER)
    code(t["tiny_apply"])
    if "tiny_check" in t:
        md("### Tiny Dataset で確認する\n\n" + CHECK + "\n\n"
           "Mini Dataset で `[OK]` になっても、もっと多いデータでは間違えることがあります。"
           "Tiny Dataset（人工データ）でも確かめましょう。")
        code(t["tiny_check"])
    if "viz" in t:
        md("### 結果をグラフで確認する\n\n" + TEACHER + " 自分の関数の結果をグラフにします（赤い棒が異常の候補）。")
        code(t["viz"])
    md(f"{THINK}\n\n" + textwrap.dedent(t["step3_think"]).strip())

    # STEP 4
    md(f"## {n}.8 STEP 4：アルゴリズムを改良する\n\n**対応レベル：Level 2（改良課題）**\n\n"
       + textwrap.dedent(t["step4"]).strip())
    for task in t["step4_tasks"]:
        emit_task(task, LEVEL2)
    if "l2_tiny_check" in t:
        md("### Tiny Dataset で確認する（Level 2）\n\n" + CHECK)
        code(t["l2_tiny_check"])
    for extra_md, extra_code in t.get("step4_extra", []):
        md(textwrap.dedent(extra_md).strip())
        code(extra_code)

    # STEP 5
    md(f"## {n}.9 STEP 5：実データで評価・発展させる\n\n**対応レベル：Level 3（発展課題）**\n\n"
       + textwrap.dedent(t["step5"]).strip())
    for extra_md, extra_code in t.get("evaluation", []):
        md(textwrap.dedent(extra_md).strip())
        code(extra_code)
    md(TEACHER)
    code(t["small_code"])
    for extra_md, extra_code in t.get("step5_extra", []):
        md(extra_md)
        code(extra_code)
    md(f"{LEVEL3}\n\n" + textwrap.dedent(t["step5_tasks"]).strip())

    md(f"## {n}.10 結果の考察とチーム独自の発展課題\n\n" + textwrap.dedent(t["discussion"]).strip())


def emit_task(task, level_label):
    md(f"### {task['title']}\n\n{level_label}\n\n" + textwrap.dedent(task["explain"]).strip())
    code(task["stub"])
    if "hints" in task:
        hints(*task["hints"])
    md(CHECK)
    code(task["check"])


def small_loader(var, rel_path, int_columns, note, title="Small Dataset（公開データを加工した CSV）",
                 path_var="SMALL_PATH"):
    return f'''
    # 【教員提供コード】{title}を読み込む
    {path_var} = DATA_DIR / "{rel_path}"
    if {path_var}.exists():
        {var} = load_csv({path_var}, int_columns={int_columns!r})
        print("{rel_path}:", len({var}), "件")
        show_records({var}, limit=5)
    else:
        {var} = []
        print("このデータはまだ用意されていません（{note}）。")
        print("Mini Dataset と Tiny Dataset（人工データ）で演習を続けてください。")
    '''


DATA_TABLE_HEAD = "| 種類 | 置き場所 | 件数 | 由来 | 状態 |\n| --- | --- | ---: | --- | --- |\n"

# ======================================================================
# C-1A
# ======================================================================
C1A = {
    "no": 4, "code": "C-1A", "title": "ネットワーク探索・異常通信の検出",
    "problem": """
    この章では、次の 2 つの問いに答えるプログラムを作ります。

    1. **どのコンピュータが、異常に多く通信しているか？**
    2. **どのコンピュータが、多数の異なる宛先ポートに通信しているか？**

    1 つ目は「回数を数える」問題、2 つ目は「種類を数える」問題です。

    > C-1E（第8章）も通信のデータを使いますが、C-1E は送ったデータの「**量**」を見ます。C-1A は「**回数**」と「**種類**」を見ます。
    """,
    "background": """
    ### なぜ必要か

    攻撃者は、攻撃の前にネットワークを調べます。
    「どのコンピュータが動いているか」「どのサービスが開いているか」を順番に試すのです。
    これを**ネットワーク探索**や**ポートスキャン（Port Scan）**と呼びます。

    また、1 つのサーバーに大量の通信を送り、サービスを止める攻撃もあります。
    これを **DoS 攻撃**（Denial of Service）と呼びます。
    多数のコンピュータから一斉に行うものは **DDoS 攻撃**（Distributed DoS）です。

    ### 必要な知識（この演習で必要な範囲だけ）

    | 用語 | 意味 |
    | --- | --- |
    | IP アドレス | ネットワーク上のコンピュータの住所。例：`192.0.2.11` |
    | 通信元（src） / 通信先（dst） | 通信を始めた側 / 受けた側。src は source、dst は destination の略 |
    | ポート番号 | 1 台のコンピュータの中の「サービスの窓口」の番号。例：80 = HTTP、443 = HTTPS、22 = SSH、3389 = リモートデスクトップ |
    | プロトコル | 通信の約束事。TCP や UDP など |
    | フロー（flow） | 同じ相手との、ひとまとまりの通信の記録 |

    ### 注意：通信が多い = 攻撃 ではない

    ソフトウェアの更新、バックアップ、多くの人が 1 つの出口（NAT・プロキシ）を共有している場合なども、通信は多くなります。
    この章で見つけるのは「**調べる必要がある候補**」です。
    """,
    "overview": """
    | レベル | STEP | 課題 | 関数名 |
    | --- | --- | --- | --- |
    | Level 1 | STEP 2 | 課題1：指定された通信元のレコードを取り出す | `filter_by_source()` |
    | Level 1 | STEP 2 | 課題2：指定された通信元の通信回数を数える | `count_connections()` |
    | Level 1 | STEP 3 | 課題3：全通信元の通信回数を集計する（基本版） | `summarize_connections_baseline()` |
    | Level 1 | STEP 3 | 課題4：閾値以上の通信元を異常候補として取り出す | `detect_high_frequency_sources()` |
    | Level 2 | STEP 4 | 辞書で通信回数を集計する（改良版） | `summarize_connections_optimized()` |
    | Level 2 | STEP 4 | 集合で宛先ポートの種類数を数える | `count_unique_ports()` |
    | Level 2 | STEP 4 | ポートスキャンの候補を取り出す | `detect_port_scan_candidates()` |
    | Level 3 | STEP 5 | 時間窓、スライディングウィンドウ、通信集中、DDoS の兆候 | チームで設計 |
    """,
    "data": """\
    | Mini Dataset | Notebook の中（`network_records`） | 9 | 人工データ | 用意済み |
    | Tiny Dataset | `data/c1a/network_flows_tiny.csv` | 42 | 人工データ | 用意済み |
    | Small Dataset | `data/c1a/network_flows_small.csv` | 500〜5,000（予定） | CIC-IDS2017 を加工（予定） | 公開データの取得待ち（Phase 2B） |
    | Benchmark Dataset | 必要なときに生成 | 1,000〜100,000 | 人工データ | Phase 4 で準備 |

    Mini Dataset の `PC-A` や `Server-1` は教材用の名前で、実際の IP アドレスではありません。
    Tiny Dataset の IP アドレスは、説明用に予約されたアドレス（`192.0.2.x` など）で、実在のコンピュータではありません。
    """,
    "mini_code": '''
    # 【教員提供コード】C-1A の Mini Dataset（人工データ 9 件）
    # PC-A などは教材用の名前で、実際の IP アドレスではない。
    network_records = [
        {"src_ip": "PC-A", "dst_ip": "Server-1", "dst_port": 80},
        {"src_ip": "PC-B", "dst_ip": "Server-1", "dst_port": 443},
        {"src_ip": "PC-C", "dst_ip": "Server-1", "dst_port": 22},
        {"src_ip": "PC-C", "dst_ip": "Server-1", "dst_port": 80},
        {"src_ip": "PC-C", "dst_ip": "Server-1", "dst_port": 443},
        {"src_ip": "PC-C", "dst_ip": "Server-1", "dst_port": 8080},
        {"src_ip": "PC-A", "dst_ip": "Server-1", "dst_port": 443},
        {"src_ip": "PC-C", "dst_ip": "Server-1", "dst_port": 3389},
        {"src_ip": "PC-C", "dst_ip": "Server-1", "dst_port": 80},
    ]
    show_records(network_records)
    ''',
    "mini_questions": """
    表を見て、**プログラムを使わずに**答えてください。答えは後で動作確認に使います。

    1. `PC-A`、`PC-B`、`PC-C` は、それぞれ何回通信していますか？
    2. `PC-C` は、何種類の宛先ポートに通信していますか？（同じポートは 1 種類と数えます）
    3. どのコンピュータが「いつもと違う」と思いますか？ その理由は？
    """,
    "tiny_code": '''
    # 【教員提供コード】C-1A の Tiny Dataset（人工データ）を読み込む
    network_tiny = load_csv(DATA_DIR / "c1a" / "network_flows_tiny.csv",
                            int_columns=["record_id", "src_port", "dst_port", "packet_count", "byte_count"])
    print("Tiny Dataset:", len(network_tiny), "件")
    show_records(network_tiny, limit=8)
    ''',
    "step2": [
        {
            "title": "課題1：指定された通信元のレコードを取り出す",
            "explain": """
            **何を作るか：** `records` の中から、通信元（`src_ip`）が `target_src` のレコードだけを取り出します。

            **なぜ必要か：** 気になるコンピュータの通信だけを見たいときに使います。

            | 入力 | 期待する出力 |
            | --- | --- |
            | `filter_by_source(network_records, "PC-B")` | `[{"src_ip": "PC-B", "dst_ip": "Server-1", "dst_port": 443}]` |
            | `filter_by_source(network_records, "PC-Z")` | `[]`（一致なし） |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題1
            def filter_by_source(records, target_src):
                """
                指定された通信元のレコードだけを取り出す。

                引数:
                    records: 通信データのリスト（各要素は辞書）
                    target_src: 調べたい通信元（例: "PC-A"）

                戻り値:
                    通信元が target_src と一致するレコードのリスト（元の順序のまま）
                """
                # TODO:
                # records の各レコードを順番に調べる。
                # 通信元（"src_ip"）が target_src と一致するレコードを、結果のリストに追加する。

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "空のリストを用意し、1 件ずつ調べて、条件に合うものだけを追加します。",
                "`result = []`、`for record in records:`、`if 条件:`、`result.append(record)`、`return result`",
                """
                結果 ← 空のリスト
                records の各 record について:
                    もし record の "src_ip" が target_src と等しいなら:
                        結果に record を追加する
                結果を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題1
            check("PC-B のレコードを取り出す", filter_by_source, (network_records, "PC-B"), [network_records[1]])
            check("PC-A のレコードを取り出す", filter_by_source, (network_records, "PC-A"),
                  [network_records[0], network_records[6]])
            check("一致する通信元がない", filter_by_source, (network_records, "PC-Z"), [])
            check("空のデータ", filter_by_source, ([], "PC-A"), [])
            ''',
        },
        {
            "title": "課題2：指定された通信元の通信回数を数える",
            "explain": """
            **何を作るか：** 通信元が `target_src` のレコードが何件あるかを数えます。

            **なぜ必要か：** 「通信が多すぎるか」を判断するための基本になる数です。

            | 入力 | 期待する出力 |
            | --- | --- |
            | `count_connections(network_records, "PC-C")` | `6` |
            | `count_connections(network_records, "PC-Z")` | `0` |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題2
            def count_connections(records, target_src):
                """
                指定された通信元の通信回数を数える。

                引数:
                    records: 通信データのリスト
                    target_src: 調べたい通信元

                戻り値:
                    通信回数を表す整数
                """
                # TODO:
                # records の各レコードを順番に調べる。
                # 通信元が target_src と一致する場合に回数を数える。

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "数を数える変数（カウンター）を 0 から始め、一致するたびに 1 増やします。",
                "`count = 0`、`count += 1`。課題1の `filter_by_source` と `len()` を組み合わせる方法もあります。",
                """
                count ← 0
                records の各 record について:
                    もし record の "src_ip" が target_src と等しいなら:
                        count を 1 増やす
                count を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題2
            check("PC-C の通信回数", count_connections, (network_records, "PC-C"), 6)
            check("PC-A の通信回数", count_connections, (network_records, "PC-A"), 2)
            check("一致する通信元がない", count_connections, (network_records, "PC-Z"), 0)
            check("空のデータ", count_connections, ([], "PC-A"), 0)
            ''',
        },
    ],
    "step3": [
        {
            "title": "課題3：全通信元の通信回数を集計する（基本版）",
            "explain": """
            **何を作るか：** すべての通信元について、通信回数を `(通信元, 回数)` の組のリストにします。
            通信元は、**データに初めて出てきた順**に並べます。

            **作り方（基本版 / Baseline）：**
            1. 通信元の一覧（重複なし）をリストで作る。
            2. 一覧の通信元ごとに、課題2の `count_connections()` で回数を数える。

            | 入力 | 期待する出力 |
            | --- | --- |
            | `summarize_connections_baseline(network_records)` | `[("PC-A", 2), ("PC-B", 1), ("PC-C", 6)]` |
            | `summarize_connections_baseline([])` | `[]` |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題3
            def summarize_connections_baseline(records):
                """
                全通信元の通信回数を集計する（基本版）。

                引数:
                    records: 通信データのリスト

                戻り値:
                    (通信元, 通信回数) のタプルのリスト。通信元はデータに初めて出てきた順。
                """
                # TODO:
                # 1. 通信元の一覧（重複なし）を作る。まだ一覧にない通信元だけを追加する。
                # 2. 一覧の各通信元について count_connections() で回数を数え、結果に追加する。

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "まず「どんな通信元があるか」の一覧を作り、次に 1 つずつ回数を数えます。",
                "`if src not in sources:` で、一覧にまだないかを調べられます。タプルは `(src, count)` と書きます。",
                """
                sources ← 空のリスト
                records の各 record について:
                    もし record の "src_ip" が sources にないなら: sources に追加
                summary ← 空のリスト
                sources の各 src について:
                    summary に (src, count_connections(records, src)) を追加
                summary を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題3
            check("Mini Dataset の集計", summarize_connections_baseline, (network_records,),
                  [("PC-A", 2), ("PC-B", 1), ("PC-C", 6)])
            check("空のデータ", summarize_connections_baseline, ([],), [])
            ''',
        },
        {
            "title": "課題4：閾値以上の通信元を異常候補として取り出す",
            "explain": """
            **何を作るか：** 課題3の集計結果から、通信回数が**閾値（threshold）以上**の通信元を取り出します。

            **閾値（Threshold）** とは、「これ以上なら注意する」という境目の値です。

            | 入力 | 期待する出力 |
            | --- | --- |
            | `detect_high_frequency_sources([("PC-A", 2), ("PC-B", 1), ("PC-C", 6)], 3)` | `["PC-C"]` |
            | 同じ集計結果で閾値 `2` | `["PC-A", "PC-C"]`（ちょうど 2 も含む） |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題4
            def detect_high_frequency_sources(summary, threshold):
                """
                通信回数が閾値以上の通信元を、異常候補として取り出す。

                引数:
                    summary: (通信元, 通信回数) のタプルのリスト（課題3の戻り値）
                    threshold: 閾値（整数）

                戻り値:
                    通信回数が threshold 以上の通信元のリスト（summary の順序のまま）
                """
                # TODO:
                # summary の各 (通信元, 回数) を調べ、回数が threshold 以上なら結果に追加する。

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "課題1と同じ「条件に合うものだけを集める」形です。",
                "`for src, count in summary:` と書くと、タプルを 2 つの変数に分けて取り出せます。「以上」は `>=` です。",
                """
                結果 ← 空のリスト
                summary の各 (src, count) について:
                    もし count >= threshold なら: 結果に src を追加
                結果を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題4
            sample_summary = [("PC-A", 2), ("PC-B", 1), ("PC-C", 6)]
            check("閾値 3", detect_high_frequency_sources, (sample_summary, 3), ["PC-C"])
            check("閾値 2（ちょうど閾値と等しい場合も含む）", detect_high_frequency_sources,
                  (sample_summary, 2), ["PC-A", "PC-C"])
            check("該当なし", detect_high_frequency_sources, (sample_summary, 10), [])
            ''',
        },
    ],
    "tiny_apply": '''
    # 【教員提供コード】Tiny Dataset で異常候補を検出する（課題3・4 を使う）
    THRESHOLD_C1A = 8   # 教育用の仮の値（実際の基準ではない）
    try:
        tiny_summary_c1a = summarize_connections_baseline(network_tiny)
        for src, count in tiny_summary_c1a:
            print(f"{src:15s} {count:3d} 回")
        print(f"閾値 {THRESHOLD_C1A} 回以上の通信元（調べる必要がある候補）:",
              detect_high_frequency_sources(tiny_summary_c1a, THRESHOLD_C1A))
    except NotImplementedError:
        print("[未実装] 課題3・4 を実装した後に、もう一度実行してください。")
    ''',
    "step3_think": """
    1. 閾値を 8 から 9、12 に変えると、検出結果はどう変わりますか？
    2. `192.0.2.14` は通信回数がちょうど 8 回です。この端末は異常でしょうか？ `label` 列を見て確かめてください。
    3. `192.0.2.15` と `192.0.2.16` はどちらも候補になります。2 台の通信には、どんな違いがありますか？ `dst_port` 列に注目してください。（STEP 4 へ）
    """,
    "step4": """
    **学習目標：** 辞書・集合を使って処理を改良し、基本版と同じ結果になることを確かめる。計算量の考え方を理解する。

    ### 基本版の何が遅いのか

    基本版（課題3）は、通信元が K 種類あると、データ全体（N 件）を **K 回** 調べます。
    調べる回数はおよそ **N × K 回** です。これを **O(NK)**（オー・エヌ・ケー）と書きます。

    例：データが 100 件、通信元が 10 種類なら、およそ 100 × 10 = 1,000 回調べます。
    辞書を使うと、データを **1 回** 調べるだけ（およそ 100 回）で集計できます。これは **O(N)** です。
    （辞書の検索と更新は、平均すると一定の時間 **O(1)** でできる、と考えます。）

    > **2 種類の「改良」を区別しよう**
    > - **計算の速さの改良**：同じ結果を、より短い時間で求める（例：辞書による集計）。
    > - **判定ルールの改良**：検出の条件を変えて、より適切な候補を見つける（例：ポートの種類数で判定する）。
    """,
    "step4_tasks": [
        {
            "title": "改良課題A：辞書で通信回数を集計する",
            "explain": """
            基本版と同じ集計を、辞書を使ってデータを 1 回だけ調べて行います。

            | 入力 | 期待する出力 |
            | --- | --- |
            | `summarize_connections_optimized(network_records)` | `{"PC-A": 2, "PC-B": 1, "PC-C": 6}` |
            """,
            "stub": '''
            # 【学生実装課題：Level 2】改良課題A
            def summarize_connections_optimized(records):
                """
                全通信元の通信回数を、辞書を使って集計する（改良版）。

                戻り値:
                    {通信元: 通信回数} の辞書
                """
                # TODO: 辞書を使い、records を 1 回だけ調べて集計する。

                raise NotImplementedError("学生実装課題")
            ''',
            "check": '''
            # 【動作確認】改良課題A
            check("辞書による集計", summarize_connections_optimized, (network_records,),
                  {"PC-A": 2, "PC-B": 1, "PC-C": 6})
            check("基本版と改良版の結果が一致する",
                  lambda records: dict(summarize_connections_baseline(records)) == summarize_connections_optimized(records),
                  (network_records,), True)
            ''',
        },
        {
            "title": "改良課題B：宛先ポートの種類数を数え、ポートスキャンの候補を見つける",
            "explain": """
            通信元ごとに、宛先ポートが**何種類**あるかを数えます。同じポートへの通信は 1 種類と数えます。
            種類数が閾値以上の通信元を、ポートスキャンの候補とします（判定ルールの改良）。

            | 入力 | 期待する出力 |
            | --- | --- |
            | `count_unique_ports(network_records)` | `{"PC-A": 2, "PC-B": 1, "PC-C": 5}` |
            | `detect_port_scan_candidates({"PC-A": 2, "PC-B": 1, "PC-C": 5}, 5)` | `["PC-C"]` |
            """,
            "stub": '''
            # 【学生実装課題：Level 2】改良課題B
            def count_unique_ports(records):
                """
                通信元ごとに、宛先ポートの種類数を数える。

                戻り値:
                    {通信元: 宛先ポートの種類数} の辞書
                """
                # TODO: 通信元ごとに、宛先ポートの集合（set）を作る。最後に集合の大きさを数える。

                raise NotImplementedError("学生実装課題")


            def detect_port_scan_candidates(unique_ports, threshold):
                """
                宛先ポートの種類数が閾値以上の通信元を取り出す。

                引数:
                    unique_ports: {通信元: 種類数} の辞書（count_unique_ports の戻り値）
                    threshold: 閾値
                戻り値:
                    通信元のリスト（辞書に入っている順）
                """
                # TODO

                raise NotImplementedError("学生実装課題")
            ''',
            "check": '''
            # 【動作確認】改良課題B
            check("ポートの種類数", count_unique_ports, (network_records,), {"PC-A": 2, "PC-B": 1, "PC-C": 5})
            check("ポートスキャンの候補", detect_port_scan_candidates,
                  ({"PC-A": 2, "PC-B": 1, "PC-C": 5}, 5), ["PC-C"])
            ''',
        },
    ],
    "step5": """
    **学習目標：** 公開データに適用し、時間の情報を使った検出や、検出性能の評価を行う。

    Small Dataset は、研究用の公開データ **CIC-IDS2017**（カナダ・ニューブランズウィック大学）から、教員が必要な列だけを取り出して作る予定です（Phase 2B。公開データの取得と利用条件の確認が終わってから）。
    **まだ用意されていない場合は、Tiny Dataset（人工データ）を使って発展課題に取り組んでください。** 下のセルは、ファイルがなくてもエラーになりません。
    研究用の実験環境で集めたデータなので、実際の会社のネットワークとは違うことに注意してください。
    """,
    "small_code": small_loader("network_small", "c1a/network_flows_small.csv",
                               ["record_id", "src_port", "dst_port", "packet_count", "byte_count"],
                               "公開データ CIC-IDS2017 の取得待ち"),
    "step5_tasks": """
    次の中から選んで取り組みます。

    - **固定時間窓（Fixed Window）**：1 分ごとに区切って通信回数を数え、短時間の集中を見つける。
    - **スライディングウィンドウ（Sliding Window）**：「直近 60 秒間」の回数を、時間をずらしながら数える。
    - **通信先への集中**：通信先（`dst_ip`）ごとに、通信元の種類数を数える（DDoS の兆候）。
    - **検出性能の評価**：`label` を使い、適合率（Precision）や再現率（Recall）を計算する（第9章の `evaluate_detection`）。
    - **閾値の検討**：閾値を変えたとき、検出件数・誤検出・検出漏れがどう変わるかをグラフにする。

    > 通信回数が多いことだけを理由に、攻撃と断定しないこと。
    """,
    "discussion": f"""
    {THINK}

    1. 通信回数による検出と、ポートの種類数による検出は、それぞれどんな異常を見つけやすいですか？
    2. 正常な通信なのに候補になってしまう（誤検出）のは、どんな場合ですか？
    3. 攻撃なのに見つけられない（検出漏れ）のは、どんな場合ですか？

    **チーム独自の発展課題の例：** 時間帯ごとの通信量のグラフ、複数の条件を組み合わせた判定、検出結果のレポート出力。
    """,
}

# ======================================================================
# C-1B
# ======================================================================
C1B = {
    "no": 5, "code": "C-1B", "title": "不正認証・アカウント悪用の検出",
    "problem": """
    この章では、次の問いに答えるプログラムを作ります。

    **どのユーザーが、何度もログインに失敗しているか？**
    """,
    "background": """
    ### なぜ必要か

    攻撃者は、他人のアカウントでログインしようとします。
    パスワードを何度も試す**総当たり攻撃（Brute Force）**や、
    よく使われるパスワードを多くのアカウントで 1 回ずつ試す**パスワードスプレー（Password Spraying）**があります。
    盗んだパスワードで、本人のふりをしてログインすることもあります（アカウントの悪用）。

    ### 必要な知識

    | 用語 | 意味 |
    | --- | --- |
    | 認証（Authentication） | 「本人であること」を確かめること。ログインのこと |
    | 認証ログ | ログインの成功・失敗の記録 |
    | ユーザー ID（`user_id`） | アカウントの名前 |
    | 認証結果（`result`） | `success`（成功）または `failure`（失敗） |
    | 接続元（`src_host`） | ログインを試したコンピュータ |

    ### 注意

    - 認証の**失敗 = 攻撃ではありません**。パスワードの入力ミスはよくあります。
    - 認証の**成功 = 安全でもありません**。盗まれたパスワードでのログインは「成功」として記録されます。
    - `result`（認証結果）は**攻撃かどうかの正解ラベルではありません**。
    """,
    "overview": """
    | レベル | STEP | 課題 | 関数名 |
    | --- | --- | --- | --- |
    | Level 1 | STEP 2 | 課題1：認証失敗のレコードを取り出す | `filter_failed_logins()` |
    | Level 1 | STEP 2 | 課題2：指定ユーザーの認証失敗回数を数える | `count_failed_logins()` |
    | Level 1 | STEP 3 | 課題3：全ユーザーの認証失敗回数を集計する（基本版） | `summarize_failures_baseline()` |
    | Level 1 | STEP 3 | 課題4：閾値以上のユーザーを不審な候補として取り出す | `detect_suspicious_users()` |
    | Level 2 | STEP 4 | 辞書で失敗回数を集計する（改良版） | `summarize_failures_optimized()` |
    | Level 2 | STEP 4 | ユーザー別の成功・失敗回数、接続元別の失敗回数 | `summarize_auth_results()`、`summarize_failures_by_source()` |
    | Level 3 | STEP 5 | 時間内の失敗集中、スプレー攻撃、失敗後の成功、異常度 | チームで設計 |
    """,
    "data": """\
    | Mini Dataset | Notebook の中（`auth_records`） | 8 | 人工データ | 用意済み |
    | Tiny Dataset | `data/c1b/authentication_tiny.csv` | 32 | 人工データ | 用意済み |
    | Small Dataset | `data/c1b/authentication_small.csv` | 525 | 公開ログ（Loghub OpenSSH）を加工 | 用意済み |
    | （参考）全イベント | `data/c1b/ssh_events_small.csv` | 2,000 | 公開ログ（Loghub OpenSSH）を加工 | 用意済み |
    | Benchmark Dataset | 必要なときに生成 | 1,000〜100,000 | 人工データ | Phase 4 で準備 |

    **基本課題（Level 1・2）は Mini と Tiny（人工データ）で行います。** 公開ログは Level 3 で使います。
    公開ログは実際に動いていたサーバーの記録で、**正解ラベル（攻撃かどうか）はありません**（5.9 で説明します）。
    """,
    "mini_code": '''
    # 【教員提供コード】C-1B の Mini Dataset（人工データ 8 件）
    auth_records = [
        {"user_id": "user01", "result": "success"},
        {"user_id": "user02", "result": "failure"},
        {"user_id": "user02", "result": "failure"},
        {"user_id": "user03", "result": "success"},
        {"user_id": "user02", "result": "failure"},
        {"user_id": "user02", "result": "success"},
        {"user_id": "user03", "result": "failure"},
        {"user_id": "user04", "result": "success"},
    ]
    show_records(auth_records)
    ''',
    "mini_questions": """
    1. 認証に失敗したレコードは何件ありますか？
    2. `user02` は何回失敗していますか？ 最後のログインは成功ですか、失敗ですか？
    3. `user02` の動きは、どんな状況が考えられますか？（入力ミス？ 攻撃？）
    """,
    "tiny_code": '''
    # 【教員提供コード】C-1B の Tiny Dataset（人工データ）を読み込む
    auth_tiny = load_csv(DATA_DIR / "c1b" / "authentication_tiny.csv", int_columns=["record_id"])
    print("Tiny Dataset:", len(auth_tiny), "件")
    show_records(auth_tiny, limit=8)
    ''',
    "step2": [
        {
            "title": "課題1：認証失敗のレコードを取り出す",
            "explain": """
            **何を作るか：** `result` が `"failure"` のレコードだけを取り出します。

            | 入力 | 期待する出力 |
            | --- | --- |
            | `filter_failed_logins(auth_records)` | 2・3・5・7 件目のレコード（4 件）のリスト |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題1
            def filter_failed_logins(records):
                """
                認証に失敗したレコードだけを取り出す。

                引数:
                    records: 認証ログのリスト（各要素は辞書）
                戻り値:
                    result が "failure" のレコードのリスト（元の順序のまま）
                """
                # TODO: 各レコードの "result" を調べ、"failure" なら結果に追加する。

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "空のリストを用意し、失敗のレコードだけを追加します。",
                "`for record in records:`、`if record[\"result\"] == \"failure\":`、`append()`",
                """
                結果 ← 空のリスト
                records の各 record について:
                    もし record の "result" が "failure" なら: 結果に追加
                結果を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題1
            check("認証失敗の取り出し", filter_failed_logins, (auth_records,),
                  [auth_records[1], auth_records[2], auth_records[4], auth_records[6]])
            check("全件成功のデータ", filter_failed_logins, ([{"user_id": "u", "result": "success"}],), [])
            check("空のデータ", filter_failed_logins, ([],), [])
            ''',
        },
        {
            "title": "課題2：指定ユーザーの認証失敗回数を数える",
            "explain": """
            **何を作るか：** ユーザーが `target_user` で、かつ認証に失敗したレコードの件数を数えます。
            条件が **2 つ**あることに注意してください。

            | 入力 | 期待する出力 |
            | --- | --- |
            | `count_failed_logins(auth_records, "user02")` | `3` |
            | `count_failed_logins(auth_records, "user01")` | `0` |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題2
            def count_failed_logins(records, target_user):
                """
                指定されたユーザーの認証失敗回数を数える。

                戻り値:
                    認証失敗回数（整数）
                """
                # TODO: user_id が target_user で、result が "failure" のレコードを数える。

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "カウンターを 0 から始め、2 つの条件が両方とも正しいときだけ 1 増やします。",
                "2 つの条件は `and` でつなぎます：`if 条件A and 条件B:`",
                """
                count ← 0
                records の各 record について:
                    もし user_id が target_user と等しい かつ result が "failure" なら:
                        count を 1 増やす
                count を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題2
            check("user02 の失敗回数", count_failed_logins, (auth_records, "user02"), 3)
            check("user03 の失敗回数", count_failed_logins, (auth_records, "user03"), 1)
            check("失敗していないユーザー", count_failed_logins, (auth_records, "user01"), 0)
            check("存在しないユーザー", count_failed_logins, (auth_records, "nobody"), 0)
            ''',
        },
    ],
    "step3_note": """
    > **認証の失敗 ≠ 不正認証。** 失敗が多いユーザーは「調べる必要がある候補」です。入力ミスかもしれません。
    > 反対に、盗まれたパスワードによる不正なログインは「成功」として記録されるため、失敗回数だけでは見つかりません。
    """,
    "step3": [
        {
            "title": "課題3：全ユーザーの認証失敗回数を集計する（基本版）",
            "explain": """
            **何を作るか：** **すべてのユーザー**（失敗 0 回のユーザーも含む）について、`(ユーザー, 失敗回数)` のリストを作ります。
            ユーザーは、データに初めて出てきた順に並べます。

            | 入力 | 期待する出力 |
            | --- | --- |
            | `summarize_failures_baseline(auth_records)` | `[("user01", 0), ("user02", 3), ("user03", 1), ("user04", 0)]` |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題3
            def summarize_failures_baseline(records):
                """
                全ユーザーの認証失敗回数を集計する（基本版）。

                戻り値:
                    (ユーザー, 失敗回数) のタプルのリスト。ユーザーはデータに初めて出てきた順。
                """
                # TODO:
                # 1. ユーザーの一覧（重複なし）を作る。
                # 2. 各ユーザーについて count_failed_logins() で失敗回数を数える。

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "「ユーザーの一覧を作る」と「1 人ずつ数える」の 2 段階に分けます。",
                "`if user not in users:` で重複を防ぎます。数えるのは課題2の関数を使います。",
                """
                users ← 空のリスト
                records の各 record について:
                    もし user_id が users にないなら: users に追加
                summary ← 空のリスト
                users の各 user について:
                    summary に (user, count_failed_logins(records, user)) を追加
                summary を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題3
            check("Mini Dataset の集計", summarize_failures_baseline, (auth_records,),
                  [("user01", 0), ("user02", 3), ("user03", 1), ("user04", 0)])
            check("空のデータ", summarize_failures_baseline, ([],), [])
            ''',
        },
        {
            "title": "課題4：閾値以上のユーザーを不審な候補として取り出す",
            "explain": """
            **何を作るか：** 失敗回数が閾値**以上**のユーザーを取り出します。

            | 入力 | 期待する出力 |
            | --- | --- |
            | `detect_suspicious_users([("user01", 0), ("user02", 3), ("user03", 1), ("user04", 0)], 3)` | `["user02"]` |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題4
            def detect_suspicious_users(summary, threshold):
                """
                失敗回数が閾値以上のユーザーを、不審な認証行動の候補として取り出す。

                引数:
                    summary: (ユーザー, 失敗回数) のタプルのリスト（課題3の戻り値）
                    threshold: 閾値
                戻り値:
                    ユーザーのリスト（summary の順序のまま）
                """
                # TODO

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "条件に合うものだけを集める形です。",
                "`for user, count in summary:`、「以上」は `>=`",
                """
                結果 ← 空のリスト
                summary の各 (user, count) について:
                    もし count >= threshold なら: 結果に user を追加
                結果を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題4
            sample_failures = [("user01", 0), ("user02", 3), ("user03", 1), ("user04", 0)]
            check("閾値 3（ちょうど閾値と等しい）", detect_suspicious_users, (sample_failures, 3), ["user02"])
            check("閾値 1", detect_suspicious_users, (sample_failures, 1), ["user02", "user03"])
            check("該当なし", detect_suspicious_users, (sample_failures, 5), [])
            ''',
        },
    ],
    "tiny_apply": '''
    # 【教員提供コード】Tiny Dataset で不審なユーザーの候補を検出する
    THRESHOLD_C1B = 3   # 教育用の仮の値
    try:
        tiny_summary_c1b = summarize_failures_baseline(auth_tiny)
        for user, count in tiny_summary_c1b:
            print(f"{user:8s} 失敗 {count:2d} 回")
        print(f"閾値 {THRESHOLD_C1B} 回以上のユーザー（調べる必要がある候補）:",
              detect_suspicious_users(tiny_summary_c1b, THRESHOLD_C1B))
    except NotImplementedError:
        print("[未実装] 課題3・4 を実装した後に、もう一度実行してください。")
    ''',
    "step3_think": """
    1. `user05` は候補になりました。しかし、本人の入力ミス（2 回）と、接続元 `203.0.113.77` からの失敗（1 回）が混ざっています。`src_host` と `label` 列を見て確かめてください。ユーザー別の失敗回数だけで判断すると、どんな問題がありますか？
    2. `user04` は 8 回失敗した後に成功しています。この「成功」は安全だと言えますか？
    3. 接続元 `203.0.113.77` は、多くのユーザーで 1 回ずつ失敗しています。ユーザー別の集計で見つけられますか？（STEP 4 へ）
    """,
    "step4": """
    **学習目標：** 辞書を使った集計で処理を改良し、集計の「切り口」（ユーザー別・接続元別）を変える意味を理解する。

    基本版（課題3）は、ユーザーが K 人いると、データ全体（N 件）を K 回調べます（**O(NK)**）。
    辞書を使うと、データを 1 回調べるだけで集計できます（**O(N)**、辞書の操作を平均 O(1) と考えた場合）。

    また、**ユーザー別**ではなく**接続元別**に集計すると、パスワードスプレーのように
    「1 つの接続元が多くのユーザーを少しずつ試す」動きが見えるようになります（判定ルールの改良）。
    """,
    "step4_tasks": [
        {
            "title": "改良課題A：辞書で失敗回数を集計する",
            "explain": """
            | 入力 | 期待する出力 |
            | --- | --- |
            | `summarize_failures_optimized(auth_records)` | `{"user01": 0, "user02": 3, "user03": 1, "user04": 0}` |
            | `summarize_auth_results(auth_records)` | `{"user01": {"success": 1, "failure": 0}, "user02": {"success": 1, "failure": 3}, ...}` |
            """,
            "stub": '''
            # 【学生実装課題：Level 2】改良課題A
            def summarize_failures_optimized(records):
                """全ユーザーの認証失敗回数を、辞書を使って 1 回の走査で集計する（失敗 0 回のユーザーも含む）。"""
                # TODO

                raise NotImplementedError("学生実装課題")


            def summarize_auth_results(records):
                """ユーザーごとに、成功回数と失敗回数を集計する。

                戻り値: {ユーザー: {"success": 成功回数, "failure": 失敗回数}} の辞書
                """
                # TODO

                raise NotImplementedError("学生実装課題")
            ''',
            "check": '''
            # 【動作確認】改良課題A
            check("辞書による失敗回数の集計", summarize_failures_optimized, (auth_records,),
                  {"user01": 0, "user02": 3, "user03": 1, "user04": 0})
            check("基本版と改良版の結果が一致する",
                  lambda records: dict(summarize_failures_baseline(records)) == summarize_failures_optimized(records),
                  (auth_records,), True)
            check("成功・失敗回数の集計", summarize_auth_results, (auth_records,),
                  {"user01": {"success": 1, "failure": 0}, "user02": {"success": 1, "failure": 3},
                   "user03": {"success": 1, "failure": 1}, "user04": {"success": 1, "failure": 0}})
            ''',
        },
        {
            "title": "改良課題B：接続元別に失敗回数と対象ユーザー数を集計する",
            "explain": """
            Tiny Dataset には接続元（`src_host`）の列があります。接続元ごとに、失敗回数と、失敗したユーザーの**種類数**を数えます。

            例（3 件のデータ）：`203.0.113.77` が user01・user02 に 1 回ずつ失敗、`192.0.2.22` が user02 に 1 回失敗
            → `{"203.0.113.77": {"failures": 2, "users": 2}, "192.0.2.22": {"failures": 1, "users": 1}}`
            """,
            "stub": '''
            # 【学生実装課題：Level 2】改良課題B
            def summarize_failures_by_source(records):
                """接続元ごとに、認証失敗回数と、失敗したユーザーの種類数を集計する。

                戻り値: {接続元: {"failures": 失敗回数, "users": ユーザーの種類数}} の辞書
                        （失敗したレコードがある接続元だけを含める）
                """
                # TODO: ユーザーの種類数は、集合（set）を使うと数えやすい。

                raise NotImplementedError("学生実装課題")
            ''',
            "check": '''
            # 【動作確認】改良課題B
            sample_auth = [
                {"user_id": "user01", "src_host": "203.0.113.77", "result": "failure"},
                {"user_id": "user02", "src_host": "203.0.113.77", "result": "failure"},
                {"user_id": "user02", "src_host": "192.0.2.22", "result": "failure"},
                {"user_id": "user02", "src_host": "192.0.2.22", "result": "success"},
            ]
            check("接続元別の集計", summarize_failures_by_source, (sample_auth,),
                  {"203.0.113.77": {"failures": 2, "users": 2}, "192.0.2.22": {"failures": 1, "users": 1}})
            ''',
        },
    ],
    "step5": """
    **学習目標：** 実際のサーバーのログに適用し、正解ラベルがないデータの扱い方を学ぶ。

    ### 公開ログ：Loghub OpenSSH

    | 項目 | 内容 |
    | --- | --- |
    | 出典 | **Loghub**（LogPAI）の OpenSSH ログ。研究室の SSH サーバーで約 4 時間に記録された 2,000 行 |
    | データの種類 | **実際に動いていたサーバーのログ**（人工データではない） |
    | ファイル | `authentication_small.csv`：認証の試行の行だけ（525 行）／`ssh_events_small.csv`：全 2,000 行 |
    | 正解ラベル | **なし**（`label` 列はすべて `unknown`）。「攻撃かどうか」の答えはありません |
    | 人工データとの違い | 成功は 1 行、失敗は 524 行で、**ほとんどが失敗**です（インターネット上の自動ログイン試行が多いため）。比率は調整していません |

    **列の意味（Tiny Dataset と同じ列名は、同じ意味です）**

    | 列 | 意味 |
    | --- | --- |
    | `log_date`、`log_time` | 日付（月-日）と時刻。**原データに年がないため、年はありません** |
    | `user_id` | ログインに使われたユーザー名。`root` や `admin` など、攻撃でよく試される名前が多い |
    | `src_host` | 接続元。実在の IP アドレスを `ip-001` のような匿名 ID に置き換えています |
    | `result` | `success` / `failure`。**認証の結果であって、攻撃かどうかの答えではありません** |
    | `invalid_user` | `yes` = サーバーに存在しないユーザー名での試行 |
    | `repeat_count` | 通常は 1。「message repeated 5 times」の行は 5（同じ失敗が 5 回あったことを 1 行にまとめた記録） |
    | `event_type`、`message` | 記録の種類と、元のメッセージ（IP アドレスは匿名化済み） |

    **注意：** 1 回のログイン失敗は、ログの中では複数の行（`Failed password` の行と `pam_unix` の行など）に記録されます。
    `authentication_small.csv` は二重に数えないよう、試行 1 回につき 1 行になるように選んであります。
    `ssh_events_small.csv` は全部の行で、`event_type` は「どんな種類の記録か」の分類です（成功・失敗の分類とは別です）。

    出典：Loghub（https://github.com/logpai/loghub）。ライセンス文は `data/c1b/LICENSE_LOGHUB.txt` にあります。
    """,
    "small_code": small_loader("auth_small", "c1b/authentication_small.csv",
                               ["record_id", "source_line", "repeat_count"],
                               "教員が scripts/preprocess_c1b.py で作成する",
                               title="公開ログ（Loghub OpenSSH）の認証の試行"),
    "step5_extra": [
        ("### Level 1 の関数を公開ログに使ってみる\n\n"
         "STEP 2・3 で作った関数は、列名が同じなので公開ログにもそのまま使えます。\n\n" + TEACHER,
         '''
         # 【教員提供コード】自分で作った関数を公開ログに適用する（課題3・4 を実装した後に実行）
         if auth_small:
             try:
                 small_summary_c1b = summarize_failures_baseline(auth_small)
                 print("ユーザーの種類:", len(small_summary_c1b))
                 print("失敗が 20 回以上のユーザー（調べる必要がある候補）:",
                       detect_suspicious_users(small_summary_c1b, 20))
             except NotImplementedError:
                 print("[未実装] 課題3・4 を実装した後に、もう一度実行してください。")
         else:
             print("公開ログがないため、このセルは何もしません。")
         '''),
    ],
    "step5_tasks": """
    - **時間内の失敗集中**：「5 分間に 5 回以上失敗」のように、時間の条件を加える。
    - **複数アカウントへの試行**：1 つの接続元が試したユーザーの種類数を調べる（パスワードスプレー）。
    - **失敗の後の成功**：何度も失敗した直後に成功したログインを探す。
    - **異常度（スコア）**：失敗回数・ユーザーの種類数・時間の集中などを点数にして合計する。
    - **接続元別の集計**：改良課題B の `summarize_failures_by_source()` を公開ログに使い、どの接続元が多くのユーザー名を試したかを調べる。
    - **イベントの種類の集計**：`ssh_events_small.csv` の `event_type` ごとに件数を数える。
    - **正解ラベルがないデータ**：Precision などは計算できません。候補の件数や、閾値による変化を調べます。
    - 「失敗の後の成功」は、公開ログには成功が 1 回しかないため、Tiny Dataset（`user04`）で調べます。
    """,
    "discussion": f"""
    {THINK}

    1. 「失敗回数が多いユーザー」と「失敗回数が多い接続元」は、それぞれどんな攻撃を見つけやすいですか？
    2. 認証に成功したログインの中から、不正なものを見つけるにはどんな情報が必要でしょうか？
    3. 閾値を厳しくしすぎると、どんな問題がありますか？

    **チーム独自の発展課題の例：** 時間帯別の失敗回数のグラフ、アカウントロック機能のシミュレーション。
    """,
}

# ======================================================================
# C-1C
# ======================================================================
C1C = {
    "no": 6, "code": "C-1C", "title": "Web・APIへの不正アクセスの検出",
    "problem": """
    この章では、次の問いに答えるプログラムを作ります。

    **どの Web リクエストに、通常とは異なる特徴があるか？**

    最初は「URL が長すぎる」「特定の文字列を含む」という簡単な特徴から始めます。
    """,
    "background": """
    ### なぜ必要か

    Web サイトや API（プログラム同士が通信する窓口）は、インターネットから誰でもアクセスできます。
    攻撃者は、URL や入力欄に特別な文字列を入れて、サーバーをだまそうとします。

    - **SQL Injection**：データベースへの命令（SQL）を入力に混ぜて、データを盗み見る。
    - **Cross-Site Scripting（XSS）**：Web ページに不正なスクリプトを埋め込む。
    - **パストラバーサル（Path Traversal）**：`../` を使って、見せてはいけないファイルを読もうとする。

    基本課題では、これらの専門的な知識は**必要ありません**。「普通の URL と何が違うか」に注目します。

    ### 必要な知識

    | 用語 | 意味 |
    | --- | --- |
    | Web ブラウザ / Web サーバー | ページを見る側 / ページを送る側 |
    | HTTP リクエスト | ブラウザからサーバーへの「このページをください」というお願い |
    | URL | ページの場所。例：`/search?q=keyboard`。`?` の後ろは**パラメータ**（入力値） |
    | GET / POST | HTTP の**メソッド**。GET はページの取得、POST はフォームの送信などに使う |

    ### 安全上の注意

    データに含まれる攻撃に似た文字列は、**ただの文字列**として扱います。
    実際の Web サイトに送ったり、ブラウザで開いたり、プログラムとして実行したりしてはいけません。
    """,
    "overview": """
    | レベル | STEP | 課題 | 関数名 |
    | --- | --- | --- | --- |
    | Level 1 | STEP 2 | 課題1：URL の文字数を求める | `get_url_length()` |
    | Level 1 | STEP 2 | 課題2：指定した長さを超える URL を取り出す | `detect_long_urls()` |
    | Level 1 | STEP 3 | 課題3：URL が注意する文字列のどれかを含むか調べる | `contains_any_pattern()` |
    | Level 1 | STEP 3 | 課題4：条件に合う不審なリクエストの候補を取り出す | `detect_suspicious_requests()` |
    | Level 2 | STEP 4 | 判定ルールをリストで管理し、異常度（スコア）を計算する | `calculate_risk_score()`、`detect_by_score()` |
    | Level 3 | STEP 5 | 誤検出と検出漏れの分析、ルールの比較、検出性能の評価 | チームで設計 |

    C-1C では、辞書による集計ではなく、**文字列処理と判定ルールの設計**が中心です。
    """,
    "data": """\
    | Mini Dataset | Notebook の中（`http_records`） | 8 | 人工データ | 用意済み |
    | Tiny Dataset | `data/c1c/http_requests_tiny.csv` | 32 | 人工データ | 用意済み |
    | アクセスログ（CSV） | `data/c1c/web_access_log_synthetic.csv` | 47 | **人工データ**（旧 C1 教材の `sample_access.log` を CSV にしたもの） | 用意済み |
    | Small Dataset（公開データ） | `data/c1c/http_requests_small.csv` | - | CSIC HTTP 2010 など | **保留**（入手方法と利用条件を確認中） |

    C-1C では、公開データの代わりに**人工データ**を使って発展課題まで進められるようにしています。
    """,
    "mini_code": '''
    # 【教員提供コード】C-1C の Mini Dataset（人工データ 8 件）
    # 攻撃に似た文字列は「ただの文字列」として保存しているだけである。実行しないこと。
    http_records = [
        {"method": "GET", "url": "/home"},
        {"method": "GET", "url": "/products"},
        {"method": "POST", "url": "/login"},
        {"method": "GET", "url": "/search?q=example"},
        {"method": "GET", "url": "/search?q=" + "a" * 200},
        {"method": "GET", "url": "/products?id=1' OR '1'='1"},
        {"method": "GET", "url": "/search?q=<script>alert(1)</script>"},
        {"method": "GET", "url": "/about"},
    ]
    show_records(http_records)
    ''',
    "mini_questions": """
    1. 一番長い URL はどれですか？ だいたい何文字ですか？
    2. 普通の URL と比べて、5 件目・6 件目・7 件目は何が違いますか？
    3. 「普通の URL では使われにくい文字」には、どんなものがありそうですか？
    """,
    "tiny_code": '''
    # 【教員提供コード】C-1C の Tiny Dataset（人工データ）を読み込む
    http_tiny = load_csv(DATA_DIR / "c1c" / "http_requests_tiny.csv", int_columns=["request_id", "status"])
    print("Tiny Dataset:", len(http_tiny), "件")
    show_records(http_tiny, limit=8)
    ''',
    "step2": [
        {
            "title": "課題1：URL の文字数を求める",
            "explain": """
            **何を作るか：** URL の文字数を返します。

            | 入力 | 期待する出力 |
            | --- | --- |
            | `get_url_length("/home")` | `5` |
            | `get_url_length("")` | `0` |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題1
            def get_url_length(url):
                """
                URL の文字数を求める。

                引数:
                    url: URL の文字列
                戻り値:
                    文字数（整数）
                """
                # TODO: url の文字数を返す。（for 文で 1 文字ずつ数えてみるのもよい練習です）

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "文字列は 1 文字ずつ並んだものです。並んでいる数を数えます。",
                "`len(文字列)` で文字数が分かります。for 文で `for ch in url:` と書けば 1 文字ずつ取り出せます。",
                """
                url の文字数を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題1
            check("/home の文字数", get_url_length, ("/home",), 5)
            check("空の文字列", get_url_length, ("",), 0)
            check("長い URL", get_url_length, (http_records[4]["url"],), 210)
            ''',
        },
        {
            "title": "課題2：指定した長さを超える URL を取り出す",
            "explain": """
            **何を作るか：** URL の文字数が `max_length` **より長い**リクエストの URL を取り出します。

            | 入力 | 期待する出力 |
            | --- | --- |
            | `detect_long_urls(http_records, 100)` | 5 件目の URL（`"/search?q=aaaa…"`）だけのリスト |
            | `detect_long_urls(http_records, 300)` | `[]` |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題2
            def detect_long_urls(records, max_length):
                """
                URL の文字数が max_length より長いリクエストの URL を取り出す。

                戻り値:
                    URL（文字列）のリスト（元の順序のまま）
                """
                # TODO: get_url_length() を使って、各リクエストの URL の長さを調べる。

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "1 件ずつ URL の長さを調べ、長すぎるものの URL だけを集めます。",
                "「より長い」は `>` です（「以上」の `>=` とは違います）。",
                """
                結果 ← 空のリスト
                records の各 record について:
                    もし get_url_length(record の "url") > max_length なら: 結果に URL を追加
                結果を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題2
            check("100 文字より長い URL", detect_long_urls, (http_records, 100), [http_records[4]["url"]])
            check("該当なし", detect_long_urls, (http_records, 300), [])
            check("ちょうど同じ長さは含めない", detect_long_urls, ([{"method": "GET", "url": "/abc"}], 4), [])
            ''',
        },
    ],
    "step3": [
        {
            "title": "課題3：URL が注意する文字列のどれかを含むか調べる",
            "explain": """
            **何を作るか：** `patterns`（文字列のリスト）のうち、**どれか 1 つでも** `url` に含まれていれば `True`、
            1 つも含まれていなければ `False` を返します。

            **なぜ必要か：** 攻撃に使われやすい文字（例：`'` や `<script`）は何種類もあります。リストにまとめて一度に調べます。

            「文字列 A が文字列 B の中にあるか」は、`A in B` で調べられます。例：`"ab" in "cabd"` → `True`

            | 入力 | 期待する出力 |
            | --- | --- |
            | `contains_any_pattern("/search?q=<script>", ["'", "<script"])` | `True` |
            | `contains_any_pattern("/home", ["'", "<script"])` | `False` |
            | `contains_any_pattern("/home", [])` | `False`（調べる文字列がない） |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題3
            def contains_any_pattern(url, patterns):
                """
                patterns のうち、どれか 1 つでも url に含まれているかを調べる。

                引数:
                    url: URL の文字列
                    patterns: 注意する文字列のリスト（例: ["'", "<script"]）
                戻り値:
                    1 つでも含まれていれば True、1 つも含まれていなければ False
                """
                # TODO: patterns を for 文で 1 つずつ調べる。含まれていたら、その時点で True を返す。

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "パターンを 1 つずつ調べ、見つかった時点で「含む」と答えます。最後まで見つからなければ「含まない」です。",
                "`if pattern in url:` で調べます。関数の途中でも `return True` と書くと、そこで関数が終わります。`return False` は for 文の**外**に書きます。",
                """
                patterns の各 pattern について:
                    もし pattern が url に含まれるなら: True を返す
                False を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題3
            check("<script を含む", contains_any_pattern, ("/search?q=<script>", ["'", "<script"]), True)
            check("シングルクォートを含む", contains_any_pattern, (http_records[5]["url"], ["'", "<script"]), True)
            check("どれも含まない", contains_any_pattern, ("/home", ["'", "<script"]), False)
            check("2 つ目のパターンだけ含む", contains_any_pattern, ("/a<script", ["'", "<script"]), True)
            check("パターンが空", contains_any_pattern, ("/home", []), False)
            ''',
        },
        {
            "title": "課題4：不審なリクエストの候補を取り出す",
            "explain": """
            **何を作るか：** 次の**どちらか**に当てはまるリクエストの URL を取り出します。

            - URL が `max_length` より長い（課題1 の `get_url_length()` を使う）
            - URL が `patterns` のどれかを含む（課題3 の `contains_any_pattern()` を使う）

            | 入力 | 期待する出力 |
            | --- | --- |
            | `detect_suspicious_requests(http_records, 100, ["'", "<script"])` | 5・6・7 件目の URL のリスト |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題4
            def detect_suspicious_requests(records, max_length, patterns):
                """
                長すぎる URL、または patterns のどれかを含む URL を、不審なリクエストの候補として取り出す。

                引数:
                    records: HTTP リクエストのリスト
                    max_length: URL の長さの上限
                    patterns: 注意する文字列のリスト
                戻り値:
                    URL のリスト（元の順序のまま。同じリクエストを 2 回入れない）
                """
                # TODO: get_url_length() と contains_any_pattern() を、or でつないで判定する。

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "課題1 と課題3 の関数がすでにあるので、2 つの条件を「または」でつなぐだけです。",
                "「どちらか」は `or` です：`if 条件A or 条件B:`",
                """
                結果 ← 空のリスト
                records の各 record について:
                    url ← record の "url"
                    もし (url の長さ > max_length) または (url が patterns のどれかを含む) なら:
                        結果に url を追加
                結果を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題4
            check("長さと文字列の条件", detect_suspicious_requests, (http_records, 100, ["'", "<script"]),
                  [http_records[4]["url"], http_records[5]["url"], http_records[6]["url"]])
            check("長さの条件だけ（パターンが空）", detect_suspicious_requests,
                  (http_records, 100, []), [http_records[4]["url"]])
            check("条件なし（長さの上限が大きく、パターンも空）", detect_suspicious_requests,
                  (http_records, 1000, []), [])
            ''',
        },
    ],
    "tiny_apply": '''
    # 【教員提供コード】Tiny Dataset で不審なリクエストの候補を検出する
    MAX_LENGTH_C1C = 100                       # 教育用の仮の値
    PATTERNS_C1C = ["'", "<script", "../"]     # 教育用の簡単なルール
    try:
        found = detect_suspicious_requests(http_tiny, MAX_LENGTH_C1C, PATTERNS_C1C)
        print(f"候補: {len(found)} 件")
        for url in found:
            print("  ", url[:80] + ("…" if len(url) > 80 else ""))
    except NotImplementedError:
        print("[未実装] 課題1〜4 を実装した後に、もう一度実行してください。")
    ''',
    "step3_think": """
    1. `/search?q=it's+a+gift` は候補になりますか？ これは攻撃でしょうか？（誤検出）
    2. `UNION SELECT` や `onerror=` を含むリクエストは見つけられましたか？（検出漏れ）
    3. `..%2F` のように、文字を別の書き方（エンコード）にしたものは見つけられますか？
    """,
    "step4": """
    **学習目標：** 判定ルールをデータとして管理し、ルールを変えたときの結果の違いを比べる。

    C-1C の改良は、主に**判定ルールの改良**です。

    - ルールを `(文字列, 点数)` のリストで管理すると、プログラムを書き換えずにルールを追加できます。
    - 1 つの条件で「怪しい / 怪しくない」を決める代わりに、**異常度（スコア）**の合計で判断します。
    - 大文字・小文字を区別しないで調べる（`url.lower()`）と、`UNION` と `union` を同じように見つけられます。

    計算量の面では、リクエストが N 件、ルールが R 個、URL の長さが L 文字のとき、
    すべてのルールを調べる処理はおよそ **N × R × L** に比例します。ルールが増えると処理も増えることに注意します。
    """,
    "step4_tasks": [
        {
            "title": "改良課題A：判定ルールのリストで異常度（スコア）を計算する",
            "explain": """
            `rules` は `(文字列, 点数)` のリストです。URL に含まれる文字列の点数を合計します。
            同じルールは、何回出てきても 1 回だけ数えます。**大文字・小文字は区別しません。**

            ```python
            rules = [("'", 2), ("<script", 3), ("union", 3), ("../", 3)]
            ```

            | 入力 | 期待する出力 |
            | --- | --- |
            | `calculate_risk_score("/products?id=1' OR '1'='1", rules)` | `2` |
            | `calculate_risk_score("/p?id=1 UNION SELECT", rules)` | `3` |
            | `detect_by_score(http_records, rules, 2)` | 6・7 件目の URL のリスト |
            """,
            "stub": '''
            # 【学生実装課題：Level 2】改良課題A
            def calculate_risk_score(url, rules):
                """URL に含まれるルールの点数を合計する（大文字・小文字を区別しない）。"""
                # TODO

                raise NotImplementedError("学生実装課題")


            def detect_by_score(records, rules, min_score):
                """異常度が min_score 以上のリクエストの URL を取り出す（元の順序のまま）。"""
                # TODO

                raise NotImplementedError("学生実装課題")
            ''',
            "check": '''
            # 【動作確認】改良課題A
            rules = [("'", 2), ("<script", 3), ("union", 3), ("../", 3)]
            check("シングルクォート", calculate_risk_score, ("/products?id=1' OR '1'='1", rules), 2)
            check("大文字の UNION", calculate_risk_score, ("/p?id=1 UNION SELECT", rules), 3)
            check("該当なし", calculate_risk_score, ("/home", rules), 0)
            check("スコアによる検出", detect_by_score, (http_records, rules, 2),
                  [http_records[5]["url"], http_records[6]["url"]])
            ''',
        },
    ],
    "step5": """
    **学習目標：** 正解ラベル付きのデータで、判定ルールの良し悪しを数値で比べる。

    ### アクセスログ：`web_access_log_synthetic.csv`（人工データ）

    | 項目 | 内容 |
    | --- | --- |
    | 出典 | 旧 C1 教材のために作成した人工のアクセスログ `data/sample_access.log`（48 行）を CSV にしたもの |
    | データの種類 | **人工データ**（実在の Web サイトの記録ではない）。IP アドレスは説明用のアドレス |
    | 件数 | 47 件（形式が正しくない 1 行は除外） |
    | 正解ラベル | なし。代わりに `scenario` 列があります（作成者が意図したパターン。攻撃の答えではありません） |

    | 列 | 意味 |
    | --- | --- |
    | `timestamp` | 日時（日本時間 +09:00） |
    | `src_ip`、`method`、`url` | 接続元、HTTP メソッド、URL（Tiny Dataset と同じ意味） |
    | `status` | HTTP ステータスコード（200 = 成功、404 = ページが見つからない） |
    | `response_bytes` | サーバーが返したデータの大きさ（バイト）。空欄はデータなし |
    | `scenario` | `normal`（通常）／`access_concentration`（アクセス集中）／`error_404_concentration`（404 エラー集中） |

    Tiny Dataset が「1 件ずつの URL の特徴」を見るデータなのに対し、このログは「**同じ接続元からのアクセスの集まり**」を見るのに向いています。

    > 研究用の公開データ **CSIC HTTP 2010**（正常・異常のラベル付き HTTP リクエスト）は、入手方法と利用条件を確認中のため、現在は使いません。
    """,
    "small_code": small_loader("web_log", "c1c/web_access_log_synthetic.csv",
                               ["request_id", "source_line", "status"],
                               "教員が scripts/preprocess_c1c.py で作成する",
                               title="人工のアクセスログ（CSV）", path_var="WEB_LOG_PATH"),
    "step5_extra": [
        ("### Level 1 の関数をアクセスログに使ってみる\n\n" + TEACHER,
         '''
         # 【教員提供コード】自分で作った関数をアクセスログに適用する（課題1〜4 を実装した後に実行）
         if web_log:
             try:
                 found = detect_suspicious_requests(web_log, 100, ["'", "<script", "../"])
                 print("URL の特徴による候補:", len(found), "件")
                 print("→ このログの異常は URL の文字列ではなく、アクセスの「回数」や「404 の多さ」に現れます。")
             except NotImplementedError:
                 print("[未実装] 課題1〜4 を実装した後に、もう一度実行してください。")
         else:
             print("アクセスログがないため、このセルは何もしません。")
         '''),
    ],
    "step5_tasks": """
    - **誤検出と検出漏れの分析**：Tiny Dataset の `label` と比べ、どのリクエストを間違えたかを調べる。
    - **ルールの比較**：ルールを増やす・減らす・点数を変えると、結果がどう変わるかを比べる。
    - **閾値の調整**：`max_length` や `min_score` を変えたときの、検出件数の変化をグラフにする。
    - **検出性能の評価**：第9章の `evaluate_detection` で、Precision・Recall を計算する。
    - **アクセスログの分析**：`web_access_log_synthetic.csv` で、接続元ごとのアクセス回数と 404 エラーの回数を数え、`scenario` 列と比べる。

    > すべて保存済みデータの分析に限ります。実際の Web サイトや API にリクエストを送ってはいけません。
    """,
    "discussion": f"""
    {THINK}

    1. 文字列のルールだけで攻撃を見つけることの、良い点と限界は何ですか？
    2. ルールを増やすほど、良い検出ができると言えますか？
    3. 人工データでうまくいったルールは、実際の Web サイトでもうまくいくでしょうか？

    **チーム独自の発展課題の例：** ルールの種類ごとの検出件数のグラフ、パラメータ部分（`?` の後ろ）だけを調べる処理。
    """,
}

# ======================================================================
# C-1D
# ======================================================================
C1D = {
    "no": 7, "code": "C-1D", "title": "不正操作・システム改変の検出",
    "problem": """
    この章では、次の問いに答えるプログラムを作ります。

    **変更前と変更後のファイル一覧を比べたとき、どのファイルが追加・削除・変更されたか？**

    複雑なシステムログではなく、「2 つの一覧を比べる」という分かりやすい問題から始めます。
    """,
    "background": """
    ### なぜ必要か

    攻撃者がコンピュータに侵入すると、次のようなことが起こります。

    - 見たことのないプログラムが**追加**される
    - 記録や大切なファイルが**削除**される
    - 設定ファイルの中身が**変更（改ざん）**される
    - **ランサムウェア**によって、多くのファイルが暗号化される（名前が変わったり、身代金の要求文が置かれたりする）

    そのため、「いつもの状態」と「今の状態」を比べて、変化を見つけることが大切です。

    ### 必要な知識

    | 用語 | 意味 |
    | --- | --- |
    | ファイル一覧 | ある時点で存在するファイルの名前のリスト |
    | ハッシュ値 | ファイルの中身から計算する「指紋」のような値。中身が 1 文字でも変わると、別の値になる |
    | 追加 / 削除 / 変更 | 変更後だけにある / 変更前だけにある / 両方にあるがハッシュ値が違う |

    この教材の `H001` などは**教材用の疑似ハッシュ値**で、本物のハッシュ値ではありません。

    ### 安全上の注意

    この章では、実際のシステムのファイルを変更・削除・暗号化することは**一切しません**。
    ファイルの一覧は、すべてデータとして用意したものです。
    """,
    "overview": """
    | レベル | STEP | 課題 | 関数名 |
    | --- | --- | --- | --- |
    | Level 1 | STEP 2 | 課題1：ファイルが一覧に存在するか確認する | `file_exists()` |
    | Level 1 | STEP 2 | 課題2：追加されたファイルを取り出す | `find_added_files()` |
    | Level 1 | STEP 3 | 課題3：削除されたファイルを取り出す | `find_deleted_files()` |
    | Level 1 | STEP 3 | 課題4：変更前後の差分をまとめる | `compare_file_lists_baseline()` |
    | Level 2 | STEP 4 | 集合で追加ファイルを速く求める | `find_added_files_optimized()` |
    | Level 2 | STEP 4 | 辞書でハッシュ値を管理し、内容の変更を見つける | `build_hash_table()`、`find_modified_files()` |
    | Level 3 | STEP 5 | Linux システムログの分析、変更の集中、ランサムウェアの兆候 | チームで設計 |
    """,
    "data": """\
    | Mini Dataset | Notebook の中（`files_before` など） | 3 + 3 | 人工データ | 用意済み |
    | Tiny Dataset | `data/c1d/file_states_before_tiny.csv`、`file_states_after_tiny.csv` | 12 + 13 | 人工データ | 用意済み |
    | Small Dataset | `data/c1d/system_events_small.csv` | 2,000 | 公開ログ（Loghub Linux）を加工 | 用意済み |

    **基本課題（Level 1・2）は、人工のファイル状態データ（Mini・Tiny）で行います。**
    公開されている Linux のシステムログ（Small Dataset）は**別のデータ**で、Level 3 だけで使います。
    公開ログには、ファイルの変更やランサムウェアの記録・正解ラベルはありません。
    """,
    "mini_code": '''
    # 【教員提供コード】C-1D の Mini Dataset（人工データ）
    # 1. ファイル名だけの一覧
    files_before = ["config.txt", "report.txt", "users.txt"]
    files_after = ["config.txt", "report.txt", "unknown.txt"]

    # 2. ファイル名と疑似ハッシュ値（H001 などは教材用の値で、本物のハッシュ値ではない）
    file_states_before = [
        {"file_id": "config.txt", "hash": "H001"},
        {"file_id": "report.txt", "hash": "H002"},
        {"file_id": "users.txt", "hash": "H003"},
    ]
    file_states_after = [
        {"file_id": "config.txt", "hash": "H004"},
        {"file_id": "report.txt", "hash": "H002"},
        {"file_id": "unknown.txt", "hash": "H005"},
    ]
    print("変更前:", files_before)
    print("変更後:", files_after)
    print()
    show_records(file_states_before)
    print()
    show_records(file_states_after)
    ''',
    "mini_questions": """
    1. 変更後にだけあるファイル（追加されたファイル）はどれですか？
    2. 変更前にだけあるファイル（削除されたファイル）はどれですか？
    3. 名前は同じなのに、中身が変わったファイルはどれですか？（ハッシュ値を比べてください）
    """,
    "tiny_code": '''
    # 【教員提供コード】C-1D の Tiny Dataset（人工データ）を読み込む
    file_states_before_tiny = load_csv(DATA_DIR / "c1d" / "file_states_before_tiny.csv")
    file_states_after_tiny = load_csv(DATA_DIR / "c1d" / "file_states_after_tiny.csv")
    # ファイル名だけのリストも作っておく
    files_before_tiny = [row["file_id"] for row in file_states_before_tiny]
    files_after_tiny = [row["file_id"] for row in file_states_after_tiny]
    print("変更前:", len(files_before_tiny), "ファイル　／　変更後:", len(files_after_tiny), "ファイル")
    show_records(file_states_after_tiny, limit=13)
    ''',
    "step2": [
        {
            "title": "課題1：ファイルが一覧に存在するか確認する",
            "explain": """
            **何を作るか：** `files` の中に `target` があれば `True`、なければ `False` を返します。
            ここでは**線形探索**（先頭から 1 つずつ調べる方法）で作ります。

            | 入力 | 期待する出力 |
            | --- | --- |
            | `file_exists(files_before, "report.txt")` | `True` |
            | `file_exists(files_before, "unknown.txt")` | `False` |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題1
            def file_exists(files, target):
                """
                ファイル一覧の中に target があるかを、先頭から順に調べる（線形探索）。

                引数:
                    files: ファイル名のリスト
                    target: 探すファイル名
                戻り値:
                    見つかれば True、見つからなければ False
                """
                # TODO: for 文（または while 文）で 1 つずつ比べる。見つかったらすぐに True を返す。

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "先頭から順番に比べ、同じ名前が見つかった時点で「ある」と答えます。最後まで見つからなければ「ない」です。",
                "関数の途中でも `return True` と書くと、そこで関数が終わります。第3章 3.6 の while 文の例も参考になります。",
                """
                files の各 name について:
                    もし name が target と等しいなら: True を返す
                False を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題1
            check("存在するファイル", file_exists, (files_before, "report.txt"), True)
            check("存在しないファイル", file_exists, (files_before, "unknown.txt"), False)
            check("空の一覧", file_exists, ([], "report.txt"), False)
            ''',
        },
        {
            "title": "課題2：追加されたファイルを取り出す",
            "explain": """
            **何を作るか：** 変更後の一覧にあって、変更前の一覧にないファイルを取り出します。

            | 入力 | 期待する出力 |
            | --- | --- |
            | `find_added_files(files_before, files_after)` | `["unknown.txt"]` |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題2
            def find_added_files(before, after):
                """
                追加されたファイル（after にあり、before にないファイル）を取り出す。

                戻り値:
                    ファイル名のリスト（after の順序のまま）
                """
                # TODO: after の各ファイルについて、file_exists() で before にあるか調べる。

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "変更後の一覧を 1 つずつ見て、変更前の一覧に「ない」ものを集めます。",
                "「ない」は `not` を使います：`if not file_exists(before, name):`",
                """
                結果 ← 空のリスト
                after の各 name について:
                    もし before に name がないなら: 結果に name を追加
                結果を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題2
            check("追加されたファイル", find_added_files, (files_before, files_after), ["unknown.txt"])
            check("変化なし", find_added_files, (files_before, files_before), [])
            ''',
        },
    ],
    "step3": [
        {
            "title": "課題3：削除されたファイルを取り出す",
            "explain": """
            **何を作るか：** 変更前の一覧にあって、変更後の一覧にないファイルを取り出します。
            課題2と「どちらを基準に調べるか」が逆になります。

            | 入力 | 期待する出力 |
            | --- | --- |
            | `find_deleted_files(files_before, files_after)` | `["users.txt"]` |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題3
            def find_deleted_files(before, after):
                """
                削除されたファイル（before にあり、after にないファイル）を取り出す。

                戻り値:
                    ファイル名のリスト（before の順序のまま）
                """
                # TODO

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "課題2とほとんど同じです。調べる一覧が入れ替わります。",
                "`for name in before:` と `file_exists(after, name)`",
                """
                結果 ← 空のリスト
                before の各 name について:
                    もし after に name がないなら: 結果に name を追加
                結果を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題3
            check("削除されたファイル", find_deleted_files, (files_before, files_after), ["users.txt"])
            check("すべて削除された", find_deleted_files, (files_before, []), files_before)
            ''',
        },
        {
            "title": "課題4：変更前後の差分をまとめる",
            "explain": """
            **何を作るか：** 次の 3 つを、1 つの辞書にまとめて返します。

            - `"added"`：追加されたファイル（課題2 の関数を使う）
            - `"deleted"`：削除されたファイル（課題3 の関数を使う）
            - `"kept"`：変更前にも変更後にもあるファイル（**ここは新しく for 文で書く**。before の順序）

            **なぜ `kept` が必要か：** 名前が残っていても、中身が書き換えられているかもしれません。
            `kept` のファイルが、Level 2 で中身（ハッシュ値）を比べる対象になります。

            | 入力 | 期待する出力 |
            | --- | --- |
            | `compare_file_lists_baseline(files_before, files_after)` | `{"added": ["unknown.txt"], "deleted": ["users.txt"], "kept": ["config.txt", "report.txt"]}` |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題4
            def compare_file_lists_baseline(before, after):
                """
                変更前後のファイル一覧の差分をまとめる（基本版）。

                戻り値:
                    {"added": 追加されたファイルのリスト,
                     "deleted": 削除されたファイルのリスト,
                     "kept": 変更前後の両方にあるファイルのリスト（before の順序）}
                """
                # TODO:
                # "added" と "deleted" は、課題2と課題3の関数を使う。
                # "kept" は、before の各ファイルについて、after にもあるものを集める。

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "added と deleted は、作った関数を呼ぶだけです。kept は課題3 と反対で、after に「ある」ものを集めます。",
                "辞書は `{\"added\": ..., \"deleted\": ..., \"kept\": ...}` の形で作れます。kept には `file_exists(after, name)` が使えます。",
                """
                kept ← 空のリスト
                before の各 name について:
                    もし after に name があるなら: kept に name を追加
                {"added": find_added_files(before, after),
                 "deleted": find_deleted_files(before, after),
                 "kept": kept} を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題4
            check("差分のまとめ", compare_file_lists_baseline, (files_before, files_after),
                  {"added": ["unknown.txt"], "deleted": ["users.txt"], "kept": ["config.txt", "report.txt"]})
            check("変化なし", compare_file_lists_baseline, (files_before, files_before),
                  {"added": [], "deleted": [], "kept": files_before})
            ''',
        },
    ],
    "tiny_apply": '''
    # 【教員提供コード】Tiny Dataset で追加・削除されたファイルを調べる
    try:
        diff = compare_file_lists_baseline(files_before_tiny, files_after_tiny)
        print("追加されたファイル:", diff["added"])
        print("削除されたファイル:", diff["deleted"])
        print("両方にあるファイル:", len(diff["kept"]), "個（中身が変わったかは Level 2 で調べる）")
    except NotImplementedError:
        print("[未実装] 課題1〜4 を実装した後に、もう一度実行してください。")
    ''',
    "step3_think": """
    1. `photo_001.jpg` が削除され、`photo_001.jpg.locked` が追加されています。これは何を意味していると考えられますか？
    2. `README_RESTORE.txt` という名前のファイルが追加されています。どんな可能性がありますか？
    3. ファイル名だけを比べる方法では、見つけられない変化は何ですか？（STEP 4 へ）
    """,
    "step4": """
    **学習目標：** リストの線形探索と、集合・辞書による探索の速さの違いを理解する。ハッシュ値で内容の変更を見つける。

    ### 基本版の何が遅いのか

    課題2の基本版は、変更後の M 個のファイルそれぞれについて、変更前の N 個の一覧を先頭から調べます。
    調べる回数は最大で **N × M 回**（**O(NM)**）です。ファイルが 1 万個ずつなら、最大 1 億回です。

    集合（set）や辞書は、「ある名前が含まれているか」を平均して**一定の時間（O(1)）**で調べられます。
    そのため、全体ではおよそ **N + M 回**（**O(N + M)**）で済みます。

    ### 名前だけでは見つからない変化

    名前が同じでも、中身が書き換えられていることがあります。ハッシュ値を比べると見つけられます。
    """,
    "step4_tasks": [
        {
            "title": "改良課題A：集合で追加ファイルを速く求める",
            "explain": """
            `find_added_files()` と**同じ結果**を、集合を使って求めます。順序は after の順序のままにします。

            | 入力 | 期待する出力 |
            | --- | --- |
            | `find_added_files_optimized(files_before, files_after)` | `["unknown.txt"]` |
            """,
            "stub": '''
            # 【学生実装課題：Level 2】改良課題A
            def find_added_files_optimized(before, after):
                """追加されたファイルを、集合を使って求める（結果は find_added_files と同じ）。"""
                # TODO: before を集合に変換してから、after の各ファイルを調べる。

                raise NotImplementedError("学生実装課題")
            ''',
            "check": '''
            # 【動作確認】改良課題A
            check("集合による追加ファイルの検出", find_added_files_optimized, (files_before, files_after), ["unknown.txt"])
            check("基本版と改良版の結果が一致する",
                  lambda b, a: find_added_files(b, a) == find_added_files_optimized(b, a),
                  (files_before_tiny, files_after_tiny), True)
            ''',
        },
        {
            "title": "改良課題B：ハッシュ値で内容の変更を見つける",
            "explain": """
            | 入力 | 期待する出力 |
            | --- | --- |
            | `build_hash_table(file_states_before)` | `{"config.txt": "H001", "report.txt": "H002", "users.txt": "H003"}` |
            | `find_modified_files(file_states_before, file_states_after)` | `["config.txt"]` |
            """,
            "stub": '''
            # 【学生実装課題：Level 2】改良課題B
            def build_hash_table(states):
                """[{"file_id": ..., "hash": ...}, ...] を {ファイル名: ハッシュ値} の辞書に変換する。"""
                # TODO

                raise NotImplementedError("学生実装課題")


            def find_modified_files(states_before, states_after):
                """両方に存在し、ハッシュ値が異なるファイルを取り出す（states_after の順序のまま）。"""
                # TODO: build_hash_table() を使う。

                raise NotImplementedError("学生実装課題")
            ''',
            "check": '''
            # 【動作確認】改良課題B
            check("ハッシュ値の辞書", build_hash_table, (file_states_before,),
                  {"config.txt": "H001", "report.txt": "H002", "users.txt": "H003"})
            check("内容が変更されたファイル", find_modified_files, (file_states_before, file_states_after), ["config.txt"])
            ''',
        },
    ],
    "step5": """
    **学習目標：** 実際の Linux のシステムログを読み、通常と違うイベントを探す。

    ### 公開ログ：Loghub Linux

    | 項目 | 内容 |
    | --- | --- |
    | 出典 | Public Security Log Sharing Site（Anton Chuvakin 氏）で公開された Linux サーバーのログを、**Loghub** が再配布したもの |
    | データの種類 | **実際に動いていたサーバーのログ**（`/var/log/messages`）。2,000 行、6 月 14 日〜7 月 27 日 |
    | 正解ラベル | **なし**（`label` 列はすべて `unknown`）。**ファイル変更やランサムウェアの記録もありません** |
    | 主な記録 | FTP の接続（909 行）、認証の失敗（537 行）、セッションの開始・終了（各 123 行）など |

    | 列 | 意味 |
    | --- | --- |
    | `log_date`、`log_time` | 日付（月-日）と時刻。**原データに年がないため、年はありません** |
    | `host_id` | 記録したサーバーの名前（`combo`） |
    | `process_name` | 記録を書いたプログラム。例：`sshd(pam_unix)`（リモートログイン）、`su(pam_unix)`（ユーザーの切り替え）、`ftpd`（ファイル転送） |
    | `event_id` | Loghub がメッセージの形で分類した番号 |
    | `event_type` | 教員がメッセージの文言で付けた大まかな種類（例：`auth_failure`、`session_opened`）。**攻撃かどうかの判定ではありません** |
    | `message` | 元のメッセージ（IP アドレスとホスト名は匿名化済み） |

    出典：Loghub（https://github.com/logpai/loghub）。ライセンス文は `data/c1d/LICENSE_LOGHUB.txt` にあります。
    """,
    "small_code": small_loader("system_events_small", "c1d/system_events_small.csv", ["record_id", "source_line"],
                               "教員が scripts/preprocess_c1d.py で作成する",
                               title="公開ログ（Loghub Linux）のシステムイベント"),
    "step5_tasks": """
    - **プロセス別のイベント数**：`process_name` ごとにイベントを数え、普段と違うものを探す。
    - **イベントの種類別の集計**：`event_type` ごとに件数を数える。
    - **不審なイベントの候補**：`root_login`、`auth_failure` が続く時間帯などを探す。
    - **短時間のイベント集中**：1 分ごとに区切って件数を数え、急に増えた時間帯を探す（`log_date` と `log_time` を使う）。
    - **複数の手がかりの組み合わせ**：「拡張子の変化」「要求文らしいファイルの追加」「大量の変更」を組み合わせる。
    - **本物のハッシュ値**：教材用に作った安全なファイルだけを対象に、`hashlib` でハッシュ値を計算してみる。

    > 実際のシステムファイルを変更・削除・暗号化したり、権限を変更したりしてはいけません。
    """,
    "discussion": f"""
    {THINK}

    1. ファイル名の比較とハッシュ値の比較は、それぞれどんな変化を見つけられますか？
    2. 正常な作業（ソフトウェアの更新など）でも、たくさんのファイルが変わります。異常と区別するには何が必要ですか？
    3. 集合を使うと速くなるのはなぜですか？ 自分の言葉で説明してください。

    **チーム独自の発展課題の例：** 拡張子ごとの変更件数の集計、変更レポートの出力。
    """,
}

# ======================================================================
# C-1E
# ======================================================================
C1E = {
    "no": 8, "code": "C-1E", "title": "情報流出・異常データ転送の検出",
    "problem": """
    この章では、次の問いに答えるプログラムを作ります。

    **どのコンピュータが、異常に大量のデータを送信しているか？**

    C-1A は通信の「**回数**」を数えました。C-1E では、送ったデータの「**量（バイト数）**」を合計します。
    """,
    "background": """
    ### なぜ必要か

    攻撃者が会社のコンピュータに侵入すると、顧客情報や機密情報を外部に持ち出そうとします。
    これを**情報流出（データの持ち出し、Exfiltration）**と呼びます。
    持ち出しのときには、普段よりも多くのデータが、普段とは違う相手に送られることがあります。

    ### 必要な知識

    | 用語 | 意味 |
    | --- | --- |
    | バイト（byte） | データの量の単位。1,000 バイト ≒ 1 KB、1,000,000 バイト ≒ 1 MB |
    | 通信元（`src_host`） / 通信先（`dst_host`） | データを送った側 / 受け取った側 |
    | 累積送信量 | ある通信元が送ったデータ量の合計 |
    | DNS | 名前（例：`example.com`）を IP アドレスに変換するしくみ。これを悪用して情報を持ち出す手口もある（発展課題） |

    ### 注意：送信量が多い = 情報流出 ではない

    バックアップ、動画のアップロード、大きなファイルの共有なども、送信量は多くなります。
    この章で見つけるのは「**調べる必要がある候補**」です。

    ### C-1A との違い

    | | C-1A | C-1E |
    | --- | --- | --- |
    | 注目するもの | 通信の**回数**、宛先ポートの種類 | 送信したデータの**量**、通信先 |
    | 見つけたい例 | ポートスキャン、通信の集中 | 大量のデータの持ち出し |
    """,
    "overview": """
    | レベル | STEP | 課題 | 関数名 |
    | --- | --- | --- | --- |
    | Level 1 | STEP 2 | 課題1：指定された通信元のレコードを取り出す | `filter_transfers_by_source()` |
    | Level 1 | STEP 2 | 課題2：指定された通信元の送信量を合計する | `sum_transfer_bytes()` |
    | Level 1 | STEP 3 | 課題3：全通信元の累積送信量を集計する（基本版） | `summarize_transfer_baseline()` |
    | Level 1 | STEP 3 | 課題4：閾値以上の通信元を異常候補として取り出す | `detect_large_transfers()` |
    | Level 2 | STEP 4 | 辞書で累積送信量を集計する（改良版） | `summarize_transfer_optimized()` |
    | Level 2 | STEP 4 | 通信先別の送信量を集計する | `summarize_by_destination()` |
    | Level 3 | STEP 5 | 通常時との比較、時間窓、移動平均、DNS を使った持ち出し | チームで設計 |
    """,
    "data": """\
    | Mini Dataset | Notebook の中（`transfer_records`） | 6 | 人工データ | 用意済み |
    | Tiny Dataset | `data/c1e/data_transfer_tiny.csv` | 36 | 人工データ | 用意済み |
    | Small Dataset | `data/c1e/data_transfer_small.csv` | 500〜5,000（予定） | CIC-IDS2017 を加工（予定。C-1A と同じ元データ） | 公開データの取得待ち（Phase 2B） |

    **注意：** CIC-IDS2017 のラベルは「一般的な攻撃」のラベルで、**情報流出のラベルではありません**。
    情報流出の評価には、Tiny Dataset（人工データ）や、DNS を使った持ち出しの研究用データ（発展課題）を使います。
    """,
    "mini_code": '''
    # 【教員提供コード】C-1E の Mini Dataset（人工データ 6 件）
    transfer_records = [
        {"src_host": "PC-A", "dst_host": "Server-1", "byte_count": 1000},
        {"src_host": "PC-B", "dst_host": "Server-1", "byte_count": 2000},
        {"src_host": "PC-C", "dst_host": "Server-2", "byte_count": 50000},
        {"src_host": "PC-A", "dst_host": "Server-1", "byte_count": 1500},
        {"src_host": "PC-C", "dst_host": "Server-2", "byte_count": 80000},
        {"src_host": "PC-B", "dst_host": "Server-3", "byte_count": 500},
    ]
    show_records(transfer_records)
    ''',
    "mini_questions": """
    1. `PC-A`、`PC-B`、`PC-C` は、それぞれ合計で何バイト送信していますか？
    2. 通信の**回数**で比べると、どのコンピュータも 2 回です。**量**で比べるとどうなりますか？
    3. `PC-C` が送っている相手は、ほかのコンピュータと同じですか？
    """,
    "tiny_code": '''
    # 【教員提供コード】C-1E の Tiny Dataset（人工データ）を読み込む
    transfer_tiny = load_csv(DATA_DIR / "c1e" / "data_transfer_tiny.csv", int_columns=["record_id", "byte_count"])
    print("Tiny Dataset:", len(transfer_tiny), "件")
    show_records(transfer_tiny, limit=8)
    ''',
    "step2": [
        {
            "title": "課題1：指定された通信元のレコードを取り出す",
            "explain": """
            | 入力 | 期待する出力 |
            | --- | --- |
            | `filter_transfers_by_source(transfer_records, "PC-A")` | 1 件目と 4 件目のレコードのリスト |
            | `filter_transfers_by_source(transfer_records, "PC-Z")` | `[]` |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題1
            def filter_transfers_by_source(records, target_host):
                """
                指定された通信元のレコードだけを取り出す。

                引数:
                    records: 通信データのリスト（各要素は辞書）
                    target_host: 調べたい通信元（例: "PC-A"）
                戻り値:
                    通信元（"src_host"）が target_host と一致するレコードのリスト（元の順序のまま）
                """
                # TODO

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "空のリストを用意し、条件に合うレコードだけを追加します。",
                "`for record in records:`、`if record[\"src_host\"] == target_host:`",
                """
                結果 ← 空のリスト
                records の各 record について:
                    もし record の "src_host" が target_host と等しいなら: 結果に追加
                結果を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題1
            check("PC-A のレコード", filter_transfers_by_source, (transfer_records, "PC-A"),
                  [transfer_records[0], transfer_records[3]])
            check("一致なし", filter_transfers_by_source, (transfer_records, "PC-Z"), [])
            ''',
        },
        {
            "title": "課題2：指定された通信元の送信量を合計する",
            "explain": """
            **何を作るか：** 通信元が `target_host` のレコードの `byte_count` を合計します。
            C-1A の「回数を数える」と違い、「**量を足す**」ことに注意してください。

            | 入力 | 期待する出力 |
            | --- | --- |
            | `sum_transfer_bytes(transfer_records, "PC-C")` | `130000` |
            | `sum_transfer_bytes(transfer_records, "PC-Z")` | `0` |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題2
            def sum_transfer_bytes(records, target_host):
                """
                指定された通信元の送信データ量（バイト）を合計する。

                戻り値:
                    合計バイト数（整数）
                """
                # TODO

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "合計を入れる変数を 0 から始め、一致するレコードの `byte_count` を足していきます。",
                "`total = 0`、`total += record[\"byte_count\"]`",
                """
                total ← 0
                records の各 record について:
                    もし src_host が target_host と等しいなら:
                        total に record の "byte_count" を足す
                total を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題2
            check("PC-C の送信量", sum_transfer_bytes, (transfer_records, "PC-C"), 130000)
            check("PC-A の送信量", sum_transfer_bytes, (transfer_records, "PC-A"), 2500)
            check("一致なし", sum_transfer_bytes, (transfer_records, "PC-Z"), 0)
            ''',
        },
    ],
    "step3": [
        {
            "title": "課題3：全通信元の累積送信量を集計する（基本版）",
            "explain": """
            | 入力 | 期待する出力 |
            | --- | --- |
            | `summarize_transfer_baseline(transfer_records)` | `[("PC-A", 2500), ("PC-B", 2500), ("PC-C", 130000)]` |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題3
            def summarize_transfer_baseline(records):
                """
                全通信元の累積送信量を集計する（基本版）。

                戻り値:
                    (通信元, 合計バイト数) のタプルのリスト。通信元はデータに初めて出てきた順。
                """
                # TODO:
                # 1. 通信元の一覧（重複なし）を作る。
                # 2. 各通信元について sum_transfer_bytes() で合計する。

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "「通信元の一覧を作る」と「1 つずつ合計する」の 2 段階に分けます。",
                "`if host not in hosts:` で重複を防ぎます。",
                """
                hosts ← 空のリスト
                records の各 record について:
                    もし src_host が hosts にないなら: hosts に追加
                summary ← 空のリスト
                hosts の各 host について:
                    summary に (host, sum_transfer_bytes(records, host)) を追加
                summary を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題3
            check("Mini Dataset の集計", summarize_transfer_baseline, (transfer_records,),
                  [("PC-A", 2500), ("PC-B", 2500), ("PC-C", 130000)])
            check("空のデータ", summarize_transfer_baseline, ([],), [])
            ''',
        },
        {
            "title": "課題4：閾値以上の通信元を異常候補として取り出す",
            "explain": """
            | 入力 | 期待する出力 |
            | --- | --- |
            | `detect_large_transfers([("PC-A", 2500), ("PC-B", 2500), ("PC-C", 130000)], 100000)` | `["PC-C"]` |
            """,
            "stub": '''
            # 【学生実装課題：Level 1】課題4
            def detect_large_transfers(summary, threshold):
                """
                累積送信量が閾値以上の通信元を、異常候補として取り出す。

                引数:
                    summary: (通信元, 合計バイト数) のタプルのリスト（課題3の戻り値）
                    threshold: 閾値（バイト）
                戻り値:
                    通信元のリスト（summary の順序のまま）
                """
                # TODO

                raise NotImplementedError("学生実装課題")
            ''',
            "hints": (
                "条件に合うものだけを集める形です。",
                "`for host, total in summary:`、「以上」は `>=`",
                """
                結果 ← 空のリスト
                summary の各 (host, total) について:
                    もし total >= threshold なら: 結果に host を追加
                結果を返す
                """,
            ),
            "check": '''
            # 【動作確認】課題4
            sample_transfer = [("PC-A", 2500), ("PC-B", 2500), ("PC-C", 130000)]
            check("閾値 100000", detect_large_transfers, (sample_transfer, 100000), ["PC-C"])
            check("閾値 2500（ちょうど閾値と等しい場合も含む）", detect_large_transfers,
                  (sample_transfer, 2500), ["PC-A", "PC-B", "PC-C"])
            ''',
        },
    ],
    "tiny_apply": '''
    # 【教員提供コード】Tiny Dataset で大量送信の候補を検出する
    THRESHOLD_C1E = 1_000_000   # 教育用の仮の値（約 1 MB）
    try:
        tiny_summary_c1e = summarize_transfer_baseline(transfer_tiny)
        for host, total in tiny_summary_c1e:
            print(f"{host:15s} {total:>12,} バイト")
        print(f"閾値 {THRESHOLD_C1E:,} バイト以上の通信元（調べる必要がある候補）:",
              detect_large_transfers(tiny_summary_c1e, THRESHOLD_C1E))
    except NotImplementedError:
        print("[未実装] 課題3・4 を実装した後に、もう一度実行してください。")
    ''',
    "step3_think": """
    1. 候補になった通信元は、どの相手（`dst_host`）にデータを送っていますか？
    2. `192.0.2.44` は夜間バックアップで大量に送信しています（`label` は `benign`）。これを候補から外すには、どんな条件が必要でしょうか？
    3. 「送信量の合計」だけでなく、「どこへ送ったか」を調べるにはどうすればよいですか？（STEP 4 へ）
    """,
    "step4": """
    **学習目標：** 辞書で集計を改良し、通信先という別の切り口で集計する。

    基本版（課題3）は、通信元が K 種類あると、データ全体（N 件）を K 回調べます（**O(NK)**）。
    辞書を使うと、1 回調べるだけで済みます（**O(N)**、辞書の操作を平均 O(1) と考えた場合）。

    また、**通信先別**に集計すると、「普段は通信しない社外の相手へ大量に送っている」ことが見えるようになります。
    """,
    "step4_tasks": [
        {
            "title": "改良課題A：辞書で累積送信量を集計する",
            "explain": """
            | 入力 | 期待する出力 |
            | --- | --- |
            | `summarize_transfer_optimized(transfer_records)` | `{"PC-A": 2500, "PC-B": 2500, "PC-C": 130000}` |
            | `summarize_by_destination(transfer_records)` | `{"Server-1": 4500, "Server-2": 130000, "Server-3": 500}` |
            """,
            "stub": '''
            # 【学生実装課題：Level 2】改良課題A
            def summarize_transfer_optimized(records):
                """全通信元の累積送信量を、辞書を使って 1 回の走査で集計する。"""
                # TODO

                raise NotImplementedError("学生実装課題")


            def summarize_by_destination(records):
                """通信先（dst_host）ごとの受信データ量の合計を、辞書で集計する。"""
                # TODO

                raise NotImplementedError("学生実装課題")
            ''',
            "check": '''
            # 【動作確認】改良課題A
            check("辞書による集計", summarize_transfer_optimized, (transfer_records,),
                  {"PC-A": 2500, "PC-B": 2500, "PC-C": 130000})
            check("基本版と改良版の結果が一致する",
                  lambda records: dict(summarize_transfer_baseline(records)) == summarize_transfer_optimized(records),
                  (transfer_records,), True)
            check("通信先別の集計", summarize_by_destination, (transfer_records,),
                  {"Server-1": 4500, "Server-2": 130000, "Server-3": 500})
            ''',
        },
    ],
    "step5": """
    **学習目標：** 通常時との比較や時間の情報を使い、より適切な判定ルールを考える。

    Small Dataset は、C-1A と同じ公開データ **CIC-IDS2017** から、通信量の列を中心に取り出して作る予定です（Phase 2B）。
    **まだ用意されていない場合は、Tiny Dataset（人工データ）を使って発展課題に取り組んでください。**
    DNS を使った情報流出の研究用データ（**CIC-Bell-DNS-EXF-2021**）は、発展課題の候補です。
    """,
    "small_code": small_loader("transfer_small", "c1e/data_transfer_small.csv", ["record_id", "byte_count"],
                               "公開データ CIC-IDS2017 の取得待ち"),
    "step5_tasks": """
    - **通常時との比較**：各通信元の「いつもの送信量」（平均や中央値）を求め、それより大きく増えたものを探す。
    - **固定時間窓**：10 分ごとの送信量を集計し、急に増えた時間帯を探す。
    - **移動平均による動的閾値**：直近の平均の何倍かを閾値にする。
    - **通信元・通信先の組み合わせ**：「初めて通信する社外の相手」への大量送信を探す。
    - **DNS を使った持ち出し**：問い合わせる名前の長さ（`query_length`）や回数に注目する（データの準備状況による）。

    > 送信量が多いことだけを理由に、情報流出と断定しないこと。
    """,
    "discussion": f"""
    {THINK}

    1. 送信量の合計だけで判断すると、どんな誤検出が起きますか？
    2. 少しずつ長い時間をかけて持ち出された場合、この方法で見つけられますか？
    3. C-1A（回数）と C-1E（量）の両方を使うと、どんな利点がありますか？

    **チーム独自の発展課題の例：** 通信元別の送信量のグラフ、時間帯別の送信量の変化、レポート出力。
    """,
}

# ======================================================================
# Phase 3・4 で追加した内容（完成イメージ、Tiny での確認、グラフ、Level 2 のヒント、速度比較、評価）
# Tiny Dataset の期待値は、scripts/generate_synthetic_data.py が作るデータの設計から決めたもの。
# 教員用参照実装（solutions/、Git 管理外）で全件 [OK] になることを tests/test_reference_check.py で確認する。
# ======================================================================
KIND_EFFICIENCY = ("**改良の種類：効率化** ― 結果は基本版と**同じ**になります。"
                   "同じ結果を、より少ない手間（計算量）で求めます。")
KIND_DETECTION = ("**改良の種類：検出方法の改良** ― 判定のしかたを変えるので、結果は Level 1 と**違ってもかまいません**。"
                  "結果が違うことは誤りではありません。何が見つかるようになったかを比べます。")


def add_hints_and_kind(task, kind, h1, h2, h3):
    task["explain"] = kind + "\n\n" + textwrap.dedent(task["explain"]).strip()
    task["hints"] = (h1, h2, h3)


def speed_section(intro, code_text):
    return ("### 基本版と改良版の実行時間を比べる\n\n" + TEACHER + " 基本版と改良版の両方を実装した後に実行してください。\n\n"
            + textwrap.dedent(intro).strip(), code_text)


# ---------------------------------------------------------------- C-1A
C1A["goal"] = """
### 完成イメージ

| 項目 | 内容 |
| --- | --- |
| 扱う問題 | ネットワーク探索（ポートスキャン）や、通信の集中 |
| 入力 | 通信の記録のリスト（通信元、通信先、宛先ポート） |
| 計算すること | 通信元ごとの通信回数（Level 1）、宛先ポートの種類数（Level 2） |
| 出力 | 閾値以上の通信元（＝調べる必要がある候補）のリスト |
| 学ぶ Python | for 文、if 文、リスト、タプル、関数、辞書、集合 |

Level 1 を完成させると、Mini Dataset（9 件）から次のような結果が出せるようになります。

```text
通信元ごとの通信回数: PC-A 2 回、PC-B 1 回、PC-C 6 回
閾値 3 回以上の通信元（調べる必要がある候補）: ['PC-C']
```
"""
C1A["tiny_check"] = '''
# 【動作確認】Tiny Dataset（人工データ 42 件）で Level 1 の関数を確かめる
if network_tiny:
    check("Tiny：192.0.2.16 のレコードの数", lambda r, s: len(filter_by_source(r, s)), (network_tiny, "192.0.2.16"), 10)
    check("Tiny：192.0.2.15 の通信回数", count_connections, (network_tiny, "192.0.2.15"), 12)
    check("Tiny：全通信元の集計", summarize_connections_baseline, (network_tiny,),
          [("192.0.2.11", 4), ("192.0.2.14", 8), ("192.0.2.13", 5), ("192.0.2.12", 3),
           ("192.0.2.15", 12), ("192.0.2.16", 10)])
    check("Tiny：閾値 8 回以上（ちょうど 8 回の 192.0.2.14 も含む）", detect_high_frequency_sources,
          ([("192.0.2.11", 4), ("192.0.2.14", 8), ("192.0.2.13", 5), ("192.0.2.12", 3),
            ("192.0.2.15", 12), ("192.0.2.16", 10)], 8),
          ["192.0.2.14", "192.0.2.15", "192.0.2.16"])
else:
    print("Tiny Dataset がないため、確認できません。")
'''
C1A["viz"] = '''
# 【教員提供コード】通信元ごとの通信回数のグラフ（課題3・4 を使う）
try:
    viz_summary_c1a = summarize_connections_baseline(network_tiny)
    viz_found_c1a = detect_high_frequency_sources(viz_summary_c1a, THRESHOLD_C1A)
    plot_bars([s for s, c in viz_summary_c1a], [c for s, c in viz_summary_c1a],
              jp(f"通信元ごとの通信回数（閾値 {THRESHOLD_C1A} 回）", f"Connections per source (threshold {THRESHOLD_C1A})"),
              jp("通信回数", "connections"), highlight=viz_found_c1a)
except NotImplementedError:
    print("[未実装] 課題3・4 を実装した後に、もう一度実行してください。")
'''
add_hints_and_kind(C1A["step4_tasks"][0], KIND_EFFICIENCY,
    "辞書に「通信元 → 回数」を記録しながら、データを先頭から 1 回だけ調べます。",
    "`counts = {}`、`counts[src] = counts.get(src, 0) + 1`（`get` は、キーがなければ 0 を返します）",
    """
    counts ← 空の辞書
    records の各 record について:
        src ← record の "src_ip"
        counts[src] ← （counts にある src の回数、なければ 0）+ 1
    counts を返す
    """)
add_hints_and_kind(C1A["step4_tasks"][1], KIND_DETECTION,
    "通信元ごとに「宛先ポートの集合」を作ります。集合は同じ値を 1 つしか持たないので、最後に大きさを数えれば種類数になります。",
    "`ports[src] = set()` で空の集合、`ports[src].add(port)` で追加、`len(集合)` で種類数。辞書は `for src, count in d.items():` で 1 組ずつ取り出せます。",
    """
    ports ← 空の辞書
    records の各 record について:
        もし src が ports にないなら: ports[src] ← 空の集合
        ports[src] に record の "dst_port" を追加
    結果 ← 空の辞書
    ports の各 (src, 集合) について: 結果[src] ← 集合の大きさ
    結果を返す
    """)
C1A["l2_tiny_check"] = '''
# 【動作確認】Tiny Dataset で Level 2 の関数を確かめる
if network_tiny:
    check("Tiny：辞書による集計", summarize_connections_optimized, (network_tiny,),
          {"192.0.2.11": 4, "192.0.2.14": 8, "192.0.2.13": 5, "192.0.2.12": 3, "192.0.2.15": 12, "192.0.2.16": 10})
    check("Tiny：宛先ポートの種類数", count_unique_ports, (network_tiny,),
          {"192.0.2.11": 3, "192.0.2.14": 3, "192.0.2.13": 3, "192.0.2.12": 2, "192.0.2.15": 12, "192.0.2.16": 1})
    check("Tiny：ポートスキャンの候補（10 種類以上）", detect_port_scan_candidates,
          ({"192.0.2.11": 3, "192.0.2.14": 3, "192.0.2.13": 3, "192.0.2.12": 2, "192.0.2.15": 12, "192.0.2.16": 1}, 10),
          ["192.0.2.15"])
else:
    print("Tiny Dataset がないため、確認できません。")
'''
C1A["step4_extra"] = [speed_section("""
    人工データ（Benchmark Dataset）を**メモリの中で**作り、基本版（課題3）と改良版（改良課題A）を同じデータで比べます（ファイルは作りません）。
    通信元の種類 K を 50 に固定し、データ件数 N だけを増やします。基本版はおよそ N × K 回、改良版はおよそ N 回の処理です。

    **考えてみよう：** `n_sources` を 50 から 200 に変えると、基本版と改良版の時間はそれぞれどう変わるでしょうか？
    """, '''
# 【教員提供コード】基本版と改良版の実行時間の比較（C-1A）
def make_network_benchmark(n, n_sources=50, seed=2026):
    """通信の記録を n 件作る（通信元は n_sources 種類）。関数に渡す引数のタプルを返す。"""
    rng = random.Random(seed)                 # 乱数のシードを固定して、毎回同じデータにする
    sources = [f"PC-{i:03d}" for i in range(n_sources)]
    records = [{"src_ip": rng.choice(sources), "dst_ip": "Server-1", "dst_port": rng.choice([22, 80, 443, 8080])}
               for _ in range(n)]
    return (records,)

speed_rows_c1a = compare_speed(summarize_connections_baseline, summarize_connections_optimized,
                               make_network_benchmark, [100, 1_000, 5_000, 10_000],
                               same=lambda base, improved: dict(base) == improved)
plot_speed(speed_rows_c1a, jp("C-1A 通信回数の集計（通信元 50 種類）", "C-1A counting (50 sources)"))
''')]
C1A["evaluation"] = [("""
    ### 正解ラベルを使った評価（人工データ）

    """ + TEACHER + """ Tiny Dataset は人工データなので、`label` 列に「教材として意図した答え」があります。
    **`label` は検出には使わず、検出が終わった後の答え合わせだけに使います。** 評価の単位は「通信元」です。
    （人工データでの評価なので、実際のネットワークでも同じ結果になるとは限りません。）
    """, '''
# 【教員提供コード】通信元ごとの評価（課題3・4、改良課題B を使う）
eval_sources_c1a = {r["src_ip"] for r in network_tiny}
eval_actual_c1a = {r["src_ip"] for r in network_tiny if r["label"] != "benign"}   # 答え合わせ用
try:
    found_by_count = detect_high_frequency_sources(summarize_connections_baseline(network_tiny), THRESHOLD_C1A)
    show_evaluation(evaluate_detection(found_by_count, eval_actual_c1a, eval_sources_c1a), "通信元（Level 1：通信回数）")
    found_by_ports = detect_port_scan_candidates(count_unique_ports(network_tiny), 10)
    eval_scan_c1a = {r["src_ip"] for r in network_tiny if r["label"] == "portscan"}
    show_evaluation(evaluate_detection(found_by_ports, eval_scan_c1a, eval_sources_c1a), "通信元（Level 2：ポートの種類数で、ポートスキャンだけを答えとする）")
except NotImplementedError:
    print("[未実装] 必要な関数を実装した後に、もう一度実行してください。")
''')]

# ---------------------------------------------------------------- C-1B
C1B["goal"] = """
### 完成イメージ

| 項目 | 内容 |
| --- | --- |
| 扱う問題 | パスワードの総当たりなど、不正ログインの試み |
| 入力 | 認証ログのリスト（ユーザー、認証結果） |
| 計算すること | ユーザーごとの認証失敗回数（Level 1）、接続元ごとの失敗回数と対象ユーザー数（Level 2） |
| 出力 | 失敗回数が閾値以上のユーザー（＝調べる必要がある候補）のリスト |
| 学ぶ Python | for 文、if 文、`and`、リスト、タプル、関数、辞書、入れ子の辞書、集合 |

Level 1 を完成させると、Mini Dataset（8 件）から次のような結果が出せるようになります。

```text
ユーザーごとの失敗回数: user01 0 回、user02 3 回、user03 1 回、user04 0 回
失敗 3 回以上のユーザー（調べる必要がある候補）: ['user02']
```
"""
C1B["tiny_check"] = '''
# 【動作確認】Tiny Dataset（人工データ 32 件）で Level 1 の関数を確かめる
if auth_tiny:
    check("Tiny：認証失敗のレコードの数", lambda r: len(filter_failed_logins(r)), (auth_tiny,), 19)
    check("Tiny：user04 の失敗回数", count_failed_logins, (auth_tiny, "user04"), 8)
    check("Tiny：全ユーザーの集計", summarize_failures_baseline, (auth_tiny,),
          [("user05", 3), ("user03", 1), ("user06", 1), ("user01", 1), ("user02", 2), ("user04", 8),
           ("user07", 1), ("user08", 1), ("admin", 1)])
    check("Tiny：失敗 3 回以上（ちょうど 3 回の user05 も含む）", detect_suspicious_users,
          ([("user05", 3), ("user03", 1), ("user06", 1), ("user01", 1), ("user02", 2), ("user04", 8),
            ("user07", 1), ("user08", 1), ("admin", 1)], 3),
          ["user05", "user04"])
else:
    print("Tiny Dataset がないため、確認できません。")
'''
C1B["viz"] = '''
# 【教員提供コード】ユーザーごとの認証失敗回数のグラフ（課題3・4 を使う）
try:
    viz_summary_c1b = summarize_failures_baseline(auth_tiny)
    viz_found_c1b = detect_suspicious_users(viz_summary_c1b, THRESHOLD_C1B)
    plot_bars([u for u, c in viz_summary_c1b], [c for u, c in viz_summary_c1b],
              jp(f"ユーザーごとの認証失敗回数（閾値 {THRESHOLD_C1B} 回）", f"Failed logins per user (threshold {THRESHOLD_C1B})"),
              jp("失敗回数", "failures"), highlight=viz_found_c1b)
except NotImplementedError:
    print("[未実装] 課題3・4 を実装した後に、もう一度実行してください。")
'''
add_hints_and_kind(C1B["step4_tasks"][0], KIND_EFFICIENCY + "（`summarize_auth_results` は、成功回数も数えるように集計を広げる課題です。）",
    "辞書に「ユーザー → 失敗回数」を記録しながら、データを 1 回だけ調べます。失敗 0 回のユーザーも辞書に入れるので、まずユーザーを 0 で登録します。",
    "`if user not in failures: failures[user] = 0`。成功・失敗の両方を数えるときは、値を辞書にします：`{\"success\": 0, \"failure\": 0}`。`results[user][record[\"result\"]] += 1` と書けます。",
    """
    failures ← 空の辞書
    records の各 record について:
        user ← record の "user_id"
        もし user が failures にないなら: failures[user] ← 0
        もし record の "result" が "failure" なら: failures[user] を 1 増やす
    failures を返す
    """)
add_hints_and_kind(C1B["step4_tasks"][1], KIND_DETECTION,
    "集計の「切り口」をユーザーから接続元に変えます。失敗のレコードだけを見て、接続元ごとに回数とユーザーの集合を作ります。",
    "`continue` で成功のレコードを飛ばせます。ユーザーの種類数は、接続元ごとの集合（`set()`）に `add` して `len` で数えます。",
    """
    failures ← 空の辞書、users ← 空の辞書
    records の各 record について:
        もし result が "failure" でないなら: 次へ
        src ← record の "src_host"
        failures[src] を 1 増やす（なければ 0 から）
        users[src] の集合に user_id を追加（なければ空の集合を作る）
    各 src について {"failures": failures[src], "users": users[src] の大きさ} をまとめて返す
    """)
C1B["l2_tiny_check"] = '''
# 【動作確認】Tiny Dataset で Level 2 の関数を確かめる
if auth_tiny:
    check("Tiny：辞書による失敗回数の集計", summarize_failures_optimized, (auth_tiny,),
          {"user05": 3, "user03": 1, "user06": 1, "user01": 1, "user02": 2, "user04": 8,
           "user07": 1, "user08": 1, "admin": 1})
    check("Tiny：user04 の成功・失敗回数", lambda r: summarize_auth_results(r)["user04"], (auth_tiny,),
          {"success": 1, "failure": 8})
    check("Tiny：接続元別の集計", summarize_failures_by_source, (auth_tiny,),
          {"192.0.2.25": {"failures": 2, "users": 1}, "192.0.2.22": {"failures": 1, "users": 1},
           "203.0.113.50": {"failures": 8, "users": 1}, "203.0.113.77": {"failures": 8, "users": 8}})
else:
    print("Tiny Dataset がないため、確認できません。")
'''
C1B["step4_extra"] = [speed_section("""
    人工データをメモリの中で作り、基本版（課題3）と改良版（`summarize_failures_optimized`）を同じデータで比べます。
    ユーザーの種類 K を 50 に固定し、データ件数 N だけを増やします。
    """, '''
# 【教員提供コード】基本版と改良版の実行時間の比較（C-1B）
def make_auth_benchmark(n, n_users=50, seed=2026):
    """認証ログを n 件作る（ユーザーは n_users 人、失敗は約 10%）。関数に渡す引数のタプルを返す。"""
    rng = random.Random(seed)
    users = [f"user{i:03d}" for i in range(n_users)]
    records = [{"user_id": rng.choice(users), "result": "failure" if rng.random() < 0.1 else "success"}
               for _ in range(n)]
    return (records,)

speed_rows_c1b = compare_speed(summarize_failures_baseline, summarize_failures_optimized,
                               make_auth_benchmark, [100, 1_000, 5_000, 10_000],
                               same=lambda base, improved: dict(base) == improved)
plot_speed(speed_rows_c1b, jp("C-1B 失敗回数の集計（ユーザー 50 人）", "C-1B failure counting (50 users)"))
''')]
C1B["evaluation"] = [("""
    ### 正解ラベルを使った評価（人工データ）

    """ + TEACHER + """ Tiny Dataset の `label` を答え合わせだけに使います。評価の単位は「**接続元**」です。
    ユーザー別の集計（Level 1）では、パスワードスプレーで 1 回ずつ失敗したユーザーは目立ちません。
    接続元別の集計（Level 2）にすると、何が見つかるようになるでしょうか。
    """, '''
# 【教員提供コード】接続元ごとの評価（改良課題B を使う）
eval_sources_c1b = {r["src_host"] for r in auth_tiny}
eval_actual_c1b = {r["src_host"] for r in auth_tiny if r["label"] != "benign"}   # 答え合わせ用
try:
    by_source = summarize_failures_by_source(auth_tiny)
    found_sources = [src for src, v in by_source.items() if v["failures"] >= THRESHOLD_C1B]
    print("失敗 3 回以上の接続元:", found_sources)
    show_evaluation(evaluate_detection(found_sources, eval_actual_c1b, eval_sources_c1b), "接続元（Level 2：接続元別の失敗回数）")
except NotImplementedError:
    print("[未実装] 改良課題B を実装した後に、もう一度実行してください。")
''')]

# ---------------------------------------------------------------- C-1C
C1C["goal"] = """
### 完成イメージ

| 項目 | 内容 |
| --- | --- |
| 扱う問題 | Web サイトへの不審なリクエスト（攻撃に使われやすい文字列、長すぎる入力） |
| 入力 | HTTP リクエストのリスト（メソッド、URL） |
| 計算すること | URL の長さ、注意する文字列を含むかどうか（Level 1）、ルールの点数の合計（Level 2） |
| 出力 | 不審なリクエストの候補（URL）のリスト |
| 学ぶ Python | 文字列、`len`、`in`、for 文、`or`、早期 `return`、関数、タプルのリスト、`lower()` |

Level 1 を完成させると、Mini Dataset（8 件）から次のような結果が出せるようになります。

```text
不審なリクエストの候補（長さ 100 文字超、または ' か <script を含む）: 3 件
  /search?q=aaaaaaaaaa…（210 文字）
  /products?id=1' OR '1'='1
  /search?q=<script>alert(1)</script>
```
"""
C1C["tiny_check"] = '''
# 【動作確認】Tiny Dataset（人工データ 32 件）で Level 1 の関数を確かめる
# 期待値は「何件目か」で示しています（0 から数えます）。
if http_tiny:
    check("Tiny：長い URL の文字数", get_url_length, (http_tiny[15]["url"],), 230)
    check("Tiny：100 文字より長い URL", detect_long_urls, (http_tiny, 100),
          [http_tiny[15]["url"], http_tiny[17]["url"]])
    check("Tiny：UNION SELECT は、この 3 つのパターンでは見つからない", contains_any_pattern,
          (http_tiny[9]["url"], ["'", "<script", "../"]), False)
    check("Tiny：不審なリクエストの候補", detect_suspicious_requests, (http_tiny, 100, ["'", "<script", "../"]),
          [http_tiny[i]["url"] for i in (8, 10, 11, 13, 15, 17, 29)])
else:
    print("Tiny Dataset がないため、確認できません。")
'''
C1C["viz"] = '''
# 【教員提供コード】判定ルールごとの検出件数（課題1・3 を使う）
try:
    rule_names, rule_counts = [], []
    for pattern in PATTERNS_C1C:
        rule_names.append(pattern)
        rule_counts.append(sum(1 for r in http_tiny if contains_any_pattern(r["url"], [pattern])))
    rule_names.append(jp(f"長さ>{MAX_LENGTH_C1C}", f"len>{MAX_LENGTH_C1C}"))
    rule_counts.append(sum(1 for r in http_tiny if get_url_length(r["url"]) > MAX_LENGTH_C1C))
    plot_bars(rule_names, rule_counts, jp("判定ルールごとの検出件数（Tiny Dataset）", "Requests matched by each rule"),
              jp("件数", "requests"))
except NotImplementedError:
    print("[未実装] 課題1・3 を実装した後に、もう一度実行してください。")
'''
add_hints_and_kind(C1C["step4_tasks"][0], KIND_DETECTION,
    "ルールを 1 つずつ調べ、URL に含まれていたらその点数を足します。大文字・小文字をそろえてから比べます。",
    "`url.lower()` で小文字にできます。`for pattern, points in rules:` でタプルを 2 つの変数に分けられます。`detect_by_score` は、課題2 と同じ「条件に合うものを集める」形です。",
    """
    lower_url ← url を小文字にしたもの
    score ← 0
    rules の各 (pattern, points) について:
        もし pattern を小文字にしたものが lower_url に含まれるなら: score に points を足す
    score を返す
    """)
C1C["l2_tiny_check"] = '''
# 【動作確認】Tiny Dataset で Level 2 の関数を確かめる
rules_c1c = [("'", 2), ("<script", 3), ("union", 3), ("../", 3)]
if http_tiny:
    check("Tiny：UNION SELECT のスコア（大文字でも見つかる）", calculate_risk_score, (http_tiny[9]["url"], rules_c1c), 3)
    check("Tiny：スコア 2 以上のリクエスト", detect_by_score, (http_tiny, rules_c1c, 2),
          [http_tiny[i]["url"] for i in (8, 9, 10, 11, 13, 29)])
else:
    print("Tiny Dataset がないため、確認できません。")
'''
C1C["step4_extra"] = [("""
    ### Level 1 と Level 2 の検出結果を比べる

    """ + TEACHER + """ C-1C の改良は「速さ」ではなく「**何を見つけられるか**」の改良です。
    そのため、実行時間ではなく、`label` 列（人工データの答え）を使って検出結果を比べます。評価の単位は「リクエスト 1 件」です。
    （`label` は検出には使わず、答え合わせだけに使います。）

    **考えてみよう：** Level 2 で新しく見つかったものと、見つからなくなったものは何ですか？
    2 つの方法を組み合わせる（例：長さのルールにも点数を付ける）と、結果はどう変わるでしょうか。
    """, '''
# 【教員提供コード】2 つの検出方法の比較（課題4 と改良課題A を使う）
eval_urls_c1c = [r["url"] for r in http_tiny]
eval_actual_c1c = [r["url"] for r in http_tiny if r["label"] != "benign"]   # 答え合わせ用
try:
    found_rule = detect_suspicious_requests(http_tiny, MAX_LENGTH_C1C, PATTERNS_C1C)
    found_score = detect_by_score(http_tiny, rules_c1c, 2)
    result_rule = evaluate_detection(found_rule, eval_actual_c1c, eval_urls_c1c)
    result_score = evaluate_detection(found_score, eval_actual_c1c, eval_urls_c1c)
    show_evaluation(result_rule, "リクエスト（Level 1：長さ＋文字列のルール）")
    show_evaluation(result_score, "リクエスト（Level 2：スコア 2 以上）")
    print("Level 2 だけが見つけたもの:", [u[:40] for u in found_score if u not in found_rule])
    print("Level 1 だけが見つけたもの:", [u[:40] for u in found_rule if u not in found_score])
    plot_bars([jp("Level 1 正しく検出", "L1 TP"), jp("Level 1 誤検出", "L1 FP"),
               jp("Level 2 正しく検出", "L2 TP"), jp("Level 2 誤検出", "L2 FP")],
              [result_rule["TP"], result_rule["FP"], result_score["TP"], result_score["FP"]],
              jp("検出方法による違い（Tiny Dataset）", "Detection results by method"), jp("件数", "requests"))
except NotImplementedError:
    print("[未実装] 課題4 と改良課題A を実装した後に、もう一度実行してください。")
''')]

# ---------------------------------------------------------------- C-1D
C1D["goal"] = """
### 完成イメージ

| 項目 | 内容 |
| --- | --- |
| 扱う問題 | 不正な操作によるファイルの追加・削除・書き換え（ランサムウェアの兆候など） |
| 入力 | 変更前と変更後のファイル一覧（ファイル名、疑似ハッシュ値） |
| 計算すること | 追加・削除・両方にあるファイル（Level 1）、中身が変わったファイル（Level 2） |
| 出力 | 変化したファイルの一覧（＝調べる必要がある候補） |
| 学ぶ Python | 線形探索、早期 `return`、`not`、リスト、辞書、集合 |

Level 1 を完成させると、Mini Dataset から次のような結果が出せるようになります。

```text
追加されたファイル: ['unknown.txt']
削除されたファイル: ['users.txt']
両方にあるファイル: ['config.txt', 'report.txt']（中身が変わったかは Level 2 で調べる）
```
"""
C1D["tiny_check"] = '''
# 【動作確認】Tiny Dataset（人工データ 12 + 13 ファイル）で Level 1 の関数を確かめる
if files_before_tiny and files_after_tiny:
    check("Tiny：変更前に users.csv がある", file_exists, (files_before_tiny, "users.csv"), True)
    check("Tiny：変更後に users.csv はない", file_exists, (files_after_tiny, "users.csv"), False)
    check("Tiny：追加されたファイル", find_added_files, (files_before_tiny, files_after_tiny),
          ["photo_001.jpg.locked", "photo_002.jpg.locked", "unknown_tool.exe", "README_RESTORE.txt"])
    check("Tiny：削除されたファイル", find_deleted_files, (files_before_tiny, files_after_tiny),
          ["users.csv", "photo_001.jpg", "photo_002.jpg"])
    check("Tiny：差分のまとめ", lambda b, a: compare_file_lists_baseline(b, a)["kept"],
          (files_before_tiny, files_after_tiny),
          ["config.ini", "report_2026_10.docx", "report_2026_11.docx", "budget.xlsx", "memo.txt",
           "schedule.txt", "app.log", "readme.txt", "hosts.txt"])
else:
    print("Tiny Dataset がないため、確認できません。")
'''
C1D["viz"] = '''
# 【教員提供コード】追加・削除・両方にあるファイルの数（課題4 を使う）
try:
    viz_diff_c1d = compare_file_lists_baseline(files_before_tiny, files_after_tiny)
    plot_bars([jp("追加", "added"), jp("削除", "deleted"), jp("両方にある", "kept")],
              [len(viz_diff_c1d["added"]), len(viz_diff_c1d["deleted"]), len(viz_diff_c1d["kept"])],
              jp("ファイルの変化（Tiny Dataset）", "File changes (Tiny Dataset)"), jp("ファイル数", "files"),
              highlight=[jp("追加", "added"), jp("削除", "deleted")])
except NotImplementedError:
    print("[未実装] 課題1〜4 を実装した後に、もう一度実行してください。")
'''
add_hints_and_kind(C1D["step4_tasks"][0], KIND_EFFICIENCY,
    "変更前の一覧を、先に集合に変換しておきます。集合は「含まれているか」をすぐに調べられます。",
    "`before_set = set(before)`、`if name not in before_set:`。結果は after の順序のままにするので、for 文は after について回します。",
    """
    before_set ← before を集合にしたもの
    結果 ← 空のリスト
    after の各 name について:
        もし name が before_set にないなら: 結果に name を追加
    結果を返す
    """)
add_hints_and_kind(C1D["step4_tasks"][1], KIND_DETECTION + "（ファイル名の比較 → ハッシュ値の比較）",
    "まず「ファイル名 → ハッシュ値」の辞書を作ります。変更後の各ファイルについて、変更前にもあり、ハッシュ値が違うものを集めます。",
    "`table[row[\"file_id\"]] = row[\"hash\"]` で辞書を作れます。「両方にある、かつ値が違う」は `if name in before_hashes and before_hashes[name] != row[\"hash\"]:`",
    """
    before_hashes ← build_hash_table(states_before)
    結果 ← 空のリスト
    states_after の各 row について:
        name ← row の "file_id"
        もし name が before_hashes にあり、かつハッシュ値が違うなら: 結果に name を追加
    結果を返す
    """)
C1D["l2_tiny_check"] = '''
# 【動作確認】Tiny Dataset で Level 2 の関数を確かめる
if file_states_before_tiny and file_states_after_tiny:
    check("Tiny：集合による追加ファイルの検出", find_added_files_optimized, (files_before_tiny, files_after_tiny),
          ["photo_001.jpg.locked", "photo_002.jpg.locked", "unknown_tool.exe", "README_RESTORE.txt"])
    check("Tiny：ハッシュ値の辞書（config.ini）", lambda s: build_hash_table(s)["config.ini"], (file_states_before_tiny,), "H001")
    check("Tiny：中身が変わったファイル", find_modified_files, (file_states_before_tiny, file_states_after_tiny),
          ["config.ini", "app.log", "hosts.txt"])
else:
    print("Tiny Dataset がないため、確認できません。")
'''
C1D["step4_extra"] = [("""
    ### 名前が同じ ≠ 中身が同じ

    """ + TEACHER + """ Level 1 の「両方にあるファイル」のうち、何個の中身が書き換えられていたかを確かめます。
    """, '''
# 【教員提供コード】ファイルの変化のまとめ（課題4 と改良課題B を使う）
try:
    summary_diff_c1d = compare_file_lists_baseline(files_before_tiny, files_after_tiny)
    modified_c1d = find_modified_files(file_states_before_tiny, file_states_after_tiny)
    print("両方にあるファイル:", len(summary_diff_c1d["kept"]), "個")
    print("そのうち中身が変わったファイル:", modified_c1d)
    plot_bars([jp("追加", "added"), jp("削除", "deleted"), jp("中身が変化", "modified"), jp("変化なし", "unchanged")],
              [len(summary_diff_c1d["added"]), len(summary_diff_c1d["deleted"]), len(modified_c1d),
               len(summary_diff_c1d["kept"]) - len(modified_c1d)],
              jp("ファイルの変化（ハッシュ値で比較）", "File changes (with hashes)"), jp("ファイル数", "files"),
              highlight=[jp("追加", "added"), jp("削除", "deleted"), jp("中身が変化", "modified")])
except NotImplementedError:
    print("[未実装] 課題4 と改良課題B を実装した後に、もう一度実行してください。")
'''), speed_section("""
    ファイル一覧をメモリの中で作り、基本版（課題2：リストの線形探索）と改良版（改良課題A：集合）を同じデータで比べます。
    基本版は「変更後の各ファイル × 変更前の一覧」を調べるので、およそ N × N 回です。**件数が増えると急に遅くなる**ため、件数は小さめにしています。
    """, '''
# 【教員提供コード】基本版と改良版の実行時間の比較（C-1D）
def make_file_benchmark(n):
    """変更前 n ファイル、変更後は 1 割を削除・1 割を追加した一覧を作る。関数に渡す引数のタプルを返す。"""
    before = [f"file_{i:05d}.txt" for i in range(n)]
    after = [name for i, name in enumerate(before) if i % 10 != 0] + [f"new_{i:05d}.txt" for i in range(n // 10)]
    return (before, after)

speed_rows_c1d = compare_speed(find_added_files, find_added_files_optimized,
                               make_file_benchmark, [100, 500, 1_000, 2_000])
plot_speed(speed_rows_c1d, jp("C-1D 追加ファイルの検出（リストと集合）", "C-1D added files (list vs set)"))
''')]

# ---------------------------------------------------------------- C-1E
C1E["goal"] = """
### 完成イメージ

| 項目 | 内容 |
| --- | --- |
| 扱う問題 | 情報の持ち出しにつながるおそれのある、異常に大量のデータ送信 |
| 入力 | データ転送の記録のリスト（通信元、通信先、バイト数） |
| 計算すること | 通信元ごとの送信量の合計（Level 1）、通信先ごとの受信量の合計（Level 2） |
| 出力 | 送信量が閾値以上の通信元（＝調べる必要がある候補）のリスト |
| 学ぶ Python | for 文、if 文、合計（`+=`）、リスト、タプル、関数、辞書 |

Level 1 を完成させると、Mini Dataset（6 件）から次のような結果が出せるようになります。

```text
通信元ごとの送信量: PC-A 2,500 バイト、PC-B 2,500 バイト、PC-C 130,000 バイト
100,000 バイト以上の通信元（調べる必要がある候補）: ['PC-C']
```
"""
C1E["tiny_check"] = '''
# 【動作確認】Tiny Dataset（人工データ 36 件）で Level 1 の関数を確かめる
if transfer_tiny:
    check("Tiny：192.0.2.43 のレコードの数", lambda r, h: len(filter_transfers_by_source(r, h)), (transfer_tiny, "192.0.2.43"), 12)
    check("Tiny：192.0.2.43 の送信量", sum_transfer_bytes, (transfer_tiny, "192.0.2.43"), 3380387)
    check("Tiny：全通信元の集計", summarize_transfer_baseline, (transfer_tiny,),
          [("192.0.2.41", 138426), ("192.0.2.43", 3380387), ("192.0.2.42", 59983),
           ("192.0.2.44", 2801426), ("192.0.2.45", 74485)])
    check("Tiny：1,000,000 バイト以上", detect_large_transfers,
          ([("192.0.2.41", 138426), ("192.0.2.43", 3380387), ("192.0.2.42", 59983),
            ("192.0.2.44", 2801426), ("192.0.2.45", 74485)], 1_000_000),
          ["192.0.2.43", "192.0.2.44"])
else:
    print("Tiny Dataset がないため、確認できません。")
'''
C1E["viz"] = '''
# 【教員提供コード】通信元ごとの送信量のグラフ（課題3・4 を使う）
try:
    viz_summary_c1e = summarize_transfer_baseline(transfer_tiny)
    viz_found_c1e = detect_large_transfers(viz_summary_c1e, THRESHOLD_C1E)
    plot_bars([h for h, b in viz_summary_c1e], [b for h, b in viz_summary_c1e],
              jp(f"通信元ごとの送信量（閾値 {THRESHOLD_C1E:,} バイト）", f"Bytes sent per source (threshold {THRESHOLD_C1E:,})"),
              jp("バイト数", "bytes"), highlight=viz_found_c1e)
except NotImplementedError:
    print("[未実装] 課題3・4 を実装した後に、もう一度実行してください。")
'''
add_hints_and_kind(C1E["step4_tasks"][0], KIND_EFFICIENCY + "（`summarize_by_destination` は、集計の切り口を通信先に変える課題です。）",
    "辞書に「通信元 → 合計バイト数」を記録しながら、データを 1 回だけ調べます。通信先別も、キーを変えるだけで同じ形です。",
    "`totals[host] = totals.get(host, 0) + record[\"byte_count\"]`",
    """
    totals ← 空の辞書
    records の各 record について:
        host ← record の "src_host"（通信先別なら "dst_host"）
        totals[host] ← （totals にある host の合計、なければ 0）+ record の "byte_count"
    totals を返す
    """)
C1E["l2_tiny_check"] = '''
# 【動作確認】Tiny Dataset で Level 2 の関数を確かめる
if transfer_tiny:
    check("Tiny：辞書による集計", summarize_transfer_optimized, (transfer_tiny,),
          {"192.0.2.41": 138426, "192.0.2.43": 3380387, "192.0.2.42": 59983, "192.0.2.44": 2801426, "192.0.2.45": 74485})
    check("Tiny：通信先別の集計", summarize_by_destination, (transfer_tiny,),
          {"198.51.100.20": 230697, "198.51.100.10": 229350, "203.0.113.200": 3294660, "198.51.100.90": 2700000})
else:
    print("Tiny Dataset がないため、確認できません。")
'''
C1E["step4_extra"] = [speed_section("""
    人工データをメモリの中で作り、基本版（課題3）と改良版（改良課題A）を同じデータで比べます。
    通信元の種類 K を 50 に固定し、データ件数 N だけを増やします。
    """, '''
# 【教員提供コード】基本版と改良版の実行時間の比較（C-1E）
def make_transfer_benchmark(n, n_hosts=50, seed=2026):
    """データ転送の記録を n 件作る（通信元は n_hosts 種類）。関数に渡す引数のタプルを返す。"""
    rng = random.Random(seed)
    hosts = [f"PC-{i:03d}" for i in range(n_hosts)]
    records = [{"src_host": rng.choice(hosts), "dst_host": "Server-1", "byte_count": rng.randint(100, 50_000)}
               for _ in range(n)]
    return (records,)

speed_rows_c1e = compare_speed(summarize_transfer_baseline, summarize_transfer_optimized,
                               make_transfer_benchmark, [100, 1_000, 5_000, 10_000],
                               same=lambda base, improved: dict(base) == improved)
plot_speed(speed_rows_c1e, jp("C-1E 送信量の集計（通信元 50 種類）", "C-1E byte totals (50 sources)"))
''')]
C1E["evaluation"] = [("""
    ### 正解ラベルを使った評価（人工データ）

    """ + TEACHER + """ Tiny Dataset の `label` を答え合わせだけに使います。評価の単位は「通信元」です。
    **送信量が多いこと ＝ 情報流出、ではありません。** 誤検出（FP）になった通信元が何をしていたか、`dst_host` を見て考えましょう。
    """, '''
# 【教員提供コード】通信元ごとの評価（課題3・4 を使う）
eval_hosts_c1e = {r["src_host"] for r in transfer_tiny}
eval_actual_c1e = {r["src_host"] for r in transfer_tiny if r["label"] != "benign"}   # 答え合わせ用
try:
    found_c1e = detect_large_transfers(summarize_transfer_baseline(transfer_tiny), THRESHOLD_C1E)
    show_evaluation(evaluate_detection(found_c1e, eval_actual_c1e, eval_hosts_c1e), "通信元（Level 1：送信量の合計）")
except NotImplementedError:
    print("[未実装] 課題3・4 を実装した後に、もう一度実行してください。")
''')]


for theme in (C1A, C1B, C1C, C1D, C1E):
    theme_chapter(theme)

# ======================================================================
# 第9章
# ======================================================================
md("""
# 第9章　アルゴリズムの性能評価とチーム開発課題

この章は、Level 2・Level 3 の課題に取り組むときと、発表の準備をするときに使います。

## 9.1 基本アルゴリズムと改良アルゴリズムの比較

改良には 2 種類あります。**混ぜて考えないこと**が大切です。

| 種類 | 何を比べるか | 確認すること |
| --- | --- | --- |
| 計算の速さの改良 | 同じ入力で、実行時間がどう違うか | **同じ結果**になっていること |
| 判定ルールの改良 | 何を検出できたか、何を間違えたか | 正解ラベルとの比較（ある場合） |

## 9.2 計算量の基本的な考え方

| 書き方 | 意味 | 例 |
| --- | --- | --- |
| O(1) | データが増えても、時間はほぼ変わらない | 辞書でキーを調べる（平均） |
| O(N) | データが 2 倍になると、時間もおよそ 2 倍 | リストを 1 回、先頭から最後まで調べる |
| O(NK) | データ件数 N と種類数 K の両方に比例 | 種類ごとにリスト全体を調べる（基本版の集計） |
| O(N²) | データが 2 倍になると、時間はおよそ 4 倍 | 全部の組み合わせを調べる |

例：100 件のデータを、10 種類の IP アドレスについてくり返し調べると、およそ 1,000 回です。
辞書を使って 1 回だけ調べれば、およそ 100 回で済みます。

## 9.3 実行時間の計測

{TEACHER}

第3章 3.8 の `measure_time(func, args, repeat)` は、`func(*args)` を `repeat` 回実行し、実行時間の**中央値**（秒）を返します。
データの生成や読み込みの時間は含めず、**アルゴリズムの実行時間だけ**を測ります。
各テーマの STEP 4 では、`compare_speed` で基本版と改良版を比べます。ここでは、セキュリティとは関係のない例で計測の考え方を確認します。
""".replace("{TEACHER}", TEACHER))
code('''
# 【教員提供コード】実行時間の計測の例（measure_time は第3章 3.8 で定義済み）
# 使い方の例（セキュリティとは関係のない例）：リストと集合で「含まれているか」を調べる速さを比べる
def count_hits(container, queries):
    hits = 0
    for q in queries:
        if q in container:
            hits += 1
    return hits

rng = random.Random(0)                      # 乱数のシードを固定する
timing_rows = []
for n in [1_000, 2_000, 4_000, 8_000]:
    data_list = list(range(n))              # データの生成（計測に含めない）
    data_set = set(data_list)
    queries = [rng.randrange(2 * n) for _ in range(500)]
    assert count_hits(data_list, queries) == count_hits(data_set, queries)   # 同じ結果であることを確認
    t_list = measure_time(count_hits, (data_list, queries))
    t_set = measure_time(count_hits, (data_set, queries))
    timing_rows.append((n, t_list, t_set))
    print(f"N = {n:>5,}　リスト: {t_list:.5f} 秒　集合: {t_set:.6f} 秒")
''')
md("""
## 9.4 グラフによる結果の表示

グラフにすると、データが増えたときの時間の増え方が分かりやすくなります。
（matplotlib がない環境では、上の表で確認してください。）
""")
md(TEACHER)
code('''
# 【教員提供コード】データ件数と実行時間のグラフ（plot_speed は第3章 3.8 で定義済み）
plot_speed(timing_rows, jp("リスト（基本版）と集合（改良版）の比較", "list (baseline) vs. set (improved)"))
''')
md("""
## 9.5 異常検出の性能評価

正解ラベルがあるデータでは、検出結果を次の 4 つに分けて数えます。

| | 実際に異常 | 実際は正常 |
| --- | --- | --- |
| **検出した** | TP（正しく検出） | FP（誤検出） |
| **検出しなかった** | FN（検出漏れ） | TN（正しく見逃した） |

この表を**混同行列（Confusion Matrix）**と呼びます。

| 指標 | 計算式 | 意味 |
| --- | --- | --- |
| 適合率（Precision） | TP / (TP + FP) | 検出したもののうち、本当に異常だった割合 |
| 再現率（Recall） | TP / (TP + FN) | 本当の異常のうち、検出できた割合 |
| F1 Score | 2 × P × R / (P + R) | 適合率と再現率のバランス |
| 誤検出率（False Positive Rate） | FP / (FP + TN) | 正常なもののうち、間違えて検出した割合 |

**注意：**
- 評価の単位（レコード単位、ユーザー単位、通信元単位など）をそろえること。
- 正解ラベルを、検出プログラムの入力に使わないこと。
- 正解ラベルがないデータでは、これらの指標は計算できません。
- Level 1 では、期待される結果と実際の結果の比較（`check`）ができれば十分です。
""")
md(TEACHER)
code('''
# 【教員提供コード】検出性能の評価の例（evaluate_detection は第3章 3.8 で定義済み）
# 使い方の例（架空の例）：5 人のうち、B と C が本当に異常。検出したのは C と D。
result = evaluate_detection(detected=["C", "D"], actual_anomalies=["B", "C"], all_items=["A", "B", "C", "D", "E"])
show_evaluation(result, "人（架空の例）")
''')
md("""
## 9.6 テスト

- 各テーマの【動作確認】セルが、すべて **[OK]** になることを確認します。
- 自分で考えたテストも追加しましょう。例：空のデータ、1 件だけのデータ、閾値とちょうど同じ値、全件正常、全件異常。
- **[未実装]** は「まだ作っていない」、**[NG]** は「作ったが結果が違う（バグがある）」という意味です。

## 9.7 チーム開発の進め方

| 役割の例 | 主な仕事 |
| --- | --- |
| データ理解・分析 | データの意味を調べ、チームに説明する |
| 基本アルゴリズムの実装 | Level 1 の関数を実装する |
| 改良アルゴリズムの実装 | Level 2 の関数を実装する |
| テスト・性能評価 | テストを追加し、実行時間を比べる |
| 可視化・結果の整理 | グラフや表を作る |
| Git 管理・ドキュメント | ブランチの管理、README や発表資料をまとめる |

**全員が少なくとも 1 つの関数を実装してください。** プログラムを書かない役割だけの人がいないようにします。

### Git による作業管理（例）

```bash
git switch -c feature/c1a-count-connections   # 自分の作業用ブランチを作る
git add C1_cybersecurity_starter.ipynb
git commit -m "C-1A 課題2 count_connections を実装"
```

Notebook は複数人で同時に編集すると、変更をまとめる（マージする）のが難しくなります。
担当する章やセルを決め、こまめにコミットしましょう。

## 9.8 成果物のまとめ方

**チームの成果物の基本形**（詳しくは `TASKS.md`）

| 成果物 | 内容 | レベル |
| --- | --- | --- |
| 実装した Notebook | 担当テーマの関数を実装した Notebook（実行結果付き） | 必須 |
| 基本課題の動作確認 | Level 1 の【動作確認】（Mini と Tiny）がすべて `[OK]` | 必須 |
| 検出結果 | Tiny Dataset で見つけた「調べる必要がある候補」と、グラフまたは表 | 必須 |
| 説明と考察 | 処理の流れの説明、閾値を変えたときの変化、誤検出の例 | 必須 |
| 改良課題の動作確認 | Level 2 の【動作確認】がすべて `[OK]` | 推奨 |
| 基本版と改良版の比較 | 結果が同じことの確認、実行時間の表とグラフ、計算量の説明（効率化の場合）／検出結果の違い（検出方法の改良の場合） | 推奨 |
| 発展課題 | 公開ログへの適用、時間窓、評価指標など（1 つ以上） | 選択 |
| 問題点と改善案 | 残っている問題と、次に改良するならどうするか | 必須 |

## 9.9 発表の構成

1. どのような社会的問題を対象としたか。
2. どのようなデータを使用したか。
3. どのようなアルゴリズムを実装したか。
4. どのような結果が得られたか。
5. どのような改良を行ったか。
6. 何が問題として残っているか。
7. 今後どのように発展させられるか。

> 発表では「攻撃者を特定した」ではなく、「調べる必要がある候補を見つけた」と表現しましょう。
""")


def source_fingerprint(nb_cells):
    """セルの種類と内容（source）だけから作る指紋。メタデータや実行結果は含めない。"""
    payload = json.dumps([[c["cell_type"], c["source"]] for c in nb_cells], ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def overwrite_problem(path):
    """path の Notebook を上書きしてはいけない理由を返す（上書きしてよければ None）。

    - 実行結果が残っている（学生や教員が実行した）
    - 生成時の指紋がない（このスクリプト以外で作られた、または古い形式）
    - 生成後にセルの内容が編集されている（実行結果を消去していても、Markdown だけの編集でも検出する）
    """
    existing = nbformat.read(path, as_version=4)
    if any(c.get("outputs") or c.get("execution_count") for c in existing.cells if c.cell_type == "code"):
        return "実行結果が残っています"
    stored = existing.metadata.get("c1_generator", {}).get("source_fingerprint")
    if stored is None:
        return "生成スクリプトの記録（指紋）がありません"
    if source_fingerprint(existing.cells) != stored:
        return "生成した後にセルの内容が編集されています"
    return None


def main():
    parser = argparse.ArgumentParser(description="統合 Notebook の生成（教員用マスター）")
    parser.add_argument("--output", default=str(OUTPUT), help="出力先（既定：C1_cybersecurity_starter.ipynb）")
    parser.add_argument("--force", action="store_true", help="編集・実行された Notebook でも上書きする")
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists() and not args.force:
        problem = overwrite_problem(output)
        if problem:
            raise SystemExit(f"{output.name}：{problem}。学生が編集した Notebook の可能性があるため、上書きしません。\n"
                             "別のファイルに出力する場合は --output、上書きしてよい場合は --force を指定してください。")

    nb = new_notebook(cells=cells)
    for i, cell in enumerate(nb.cells, start=1):
        cell.id = f"cell-{i:03d}"   # 再生成しても同じ内容になるよう、セル ID を連番で固定する
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nb.metadata["language_info"] = {"name": "python"}
    nb.metadata["c1_generator"] = {
        "note": "scripts/build_notebook.py で生成。再生成時に、生成後の編集を検出するための指紋。",
        "source_fingerprint": source_fingerprint(nb.cells),
    }
    nbformat.validate(nb)
    nbformat.write(nb, output)
    n_md = sum(c.cell_type == "markdown" for c in cells)
    n_code = sum(c.cell_type == "code" for c in cells)
    print(f"作成: {output.name}（Markdown セル {n_md} 個、コードセル {n_code} 個）")


if __name__ == "__main__":
    main()
