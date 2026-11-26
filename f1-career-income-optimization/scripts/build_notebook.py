"""統合 Notebook（F1_life_planning_starter.ipynb）を生成するスクリプト（教員用マスター）

- Notebook の内容は、このスクリプトの中に Python の文字列として書いてある。
  教材を直すときは、このスクリプトを直してから Notebook を再生成する（ipynb を直接編集しない）。
- 生成した Notebook は、学生に配布した後は**学生が直接編集する成果物**になる。
  学生が編集した Notebook に上書きしないよう、次の場合は上書きを拒否する（--force で強制）。
    * 実行結果（outputs）が残っている
    * 生成時の指紋（metadata.f1_generator.source_fingerprint）がない、または内容と一致しない
- C-1 の scripts/build_notebook.py の仕組み（md/code/hints、セル ID の連番固定、指紋による上書き防止）を
  F-1 向けに書き直したもの。C-1 のファイルには依存しない。
- このスクリプトは学生への配布物に含めない。

【構成】全 10 章。テーマ章（第4〜7章）は Level 1（4 課題）と Level 2（3 課題）、合計 28 の学生実装課題。
【期待値】Mini の期待値は手計算、Tiny の期待値は教員用参照実装（solutions/、Git 管理外）で計算した値を直接書いている。
          **Tiny Dataset（scripts/generate_synthetic_data.py）を作り直したら、Tiny の期待値を見直すこと。**

使い方（f1-career-income-optimization ディレクトリで実行する）:
    <python> scripts/build_notebook.py                    # 教員用マスターを再生成する
    <python> scripts/build_notebook.py --output x.ipynb   # 別のファイルに書き出す

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
OUTPUT = PROJECT_DIR / "F1_life_planning_starter.ipynb"
GENERATOR_KEY = "f1_generator"

TEACHER = "**【教員提供コード】** そのまま実行してください。"
LEVEL1 = "**【学生実装課題：Level 1】** このセルを編集します。"
LEVEL2 = "**【学生実装課題：Level 2】** このセルを編集します。"
LEVEL3 = "**【発展課題：Level 3】**"
CHECK = "**【動作確認】** 実装した後に実行してください。未実装のときは「[未実装]」と表示されます。"
HINT = "**【ヒント】**"
THINK = "**【考察課題】**"
STUB = 'raise NotImplementedError("学生実装課題")'

cells = []


def md(text):
    cells.append(new_markdown_cell(textwrap.dedent(text).strip()))


def code(text):
    cells.append(new_code_cell(textwrap.dedent(text).strip()))


def hints(h1, h2, h3):
    """3 段階のヒントを、折りたたみ表示の Markdown として追加する（完成解答は書かない）"""
    md(f"""
    {HINT}（分からないときだけ、順番に開いてください）

    <details><summary>ヒント1：考え方</summary>

    {h1}

    </details>
    <details><summary>ヒント2：使う文法・データ構造</summary>

    {h2}

    </details>
    <details><summary>ヒント3：処理の手順（疑似コード）</summary>

    ```text
    {textwrap.indent(textwrap.dedent(h3).strip(), "    ").lstrip()}
    ```

    </details>
    """)


# ======================================================================
# 第0章
# ======================================================================
md("""
# F-1：キャリア・ライフイベント・世代間資源継承のシミュレーションと最適化
## Simulation and Optimization of Career Paths, Life Events, and Intergenerational Resource Transfer

プログラミング演習Ⅰ　チーム開発課題　統合 Starter Notebook

> **最初に読んでください**
> - この Notebook のデータの多くは、**教材のために作った人工データ（仮定値）**です。公開統計を加工したデータ（Small Dataset）は、出典を示して区別しています。
> - 計算結果は、**設定した仮定によって変わります**。将来の所得・資産を予測するものではありません。
> - 特定の進学先、職業、家族の形、住宅の選び方、相続の方法を**すすめるものではありません**。
> - 自分や家族の実際の所得・資産・健康状態などを入力する必要はありません。**仮想の人物・家族**を使います。
""")
md("""
# 第0章　本演習の目的と進め方

## 0.1 この演習で学ぶこと

個人や家族は、**限られた所得・時間・資産**をどのように使うかを、長い期間にわたって考えます。
この演習では、そのような身近な問題を Python の小さなプログラムに分けて考えます。

- 社会的な問題を、データと計算の手順（モデル）で表す。
- リストと辞書でデータを整理する。
- for 文で、1 年ずつ状態（年収・資産など）を更新する（シミュレーション（Simulation））。
- 複数の選択肢（シナリオ）を作り、条件を満たすものを探す（線形探索・二分探索・全探索）。
- 結果を並べて比べる（ソート）。
- 実行時間を測り、時間計算量（Time Complexity）を考える。

> この演習の目的は、経済学や金融の知識を覚えることではなく、**Python とアルゴリズムを使って問題を解く経験**をすることです。

## 0.2 4 つのテーマ

チームで **1 つのテーマ**を選びます。4 つすべてに取り組む必要はありません。

| ID | テーマ | 中心となる問い | 主なアルゴリズム |
| --- | --- | --- | --- |
| F-1A | キャリア選択・教育投資と生涯所得 | 進学・就職などの選択で、長期的な所得はどう変わるか。教育費はいつ回収できるか | 累積和、線形探索、ソート |
| F-1B | 家族形成・子育て・介護と資源配分 | 所得と時間をどう配分すれば、生活と育児・介護を両立できるか | 組合せの全探索、条件による絞り込み、ソート |
| F-1C | 住宅取得・居住選択と長期家計設計 | 予算と通勤時間の条件を満たす住宅はどれか。賃貸と購入はどう違うか | **線形探索、二分探索**、ソート |
| F-1D | 世代間資源継承と次世代の生活設計 | 親から子への資金の移転は、親子の資産の推移にどう影響するか | 年次シミュレーション、全探索、条件による絞り込み |

## 0.3 テーマごとの最短の学習ルート

| 手順 | 全チーム共通 | F-1A | F-1B | F-1C | F-1D |
| --- | --- | --- | --- | --- | --- |
| 1 | 第0〜3章を上から実行する | | | | |
| 2 | | 第4章 | 第5章 | 第6章 | 第7章 |
| 3 | 第8章（性能評価・チーム開発） | | | | |
| 4（任意） | 第9章（複数テーマの統合） | | | | |

- 自分のテーマの章は、**他のテーマの章を実行しなくても**動きます。
- 各テーマの章は、次の 3 段階でできています。1 チームが実装する関数は **7 個**（Level 1 が 4 個、Level 2 が 3 個）です。

| レベル | STEP | 内容 | 位置づけ |
| --- | --- | --- | --- |
| Level 1（基本課題） | STEP 1〜3 | データの確認、基本的な計算、基本シミュレーション（4 課題） | **全チーム必須** |
| Level 2（改良課題） | STEP 4 | 探索・ソート・シナリオの比較（3 課題） | 推奨 |
| Level 3（発展課題） | STEP 5 | 公開統計の利用、チーム独自の機能 | 発展案は選択。**独自機能を 1 つ以上作ることは必須** |

## 0.4 セルの種類

| 表示 | 意味 | 編集するか |
| --- | --- | --- |
| 【教員提供コード】 | 準備・表示・グラフのためのコード | 編集しない（実行するだけ） |
| 【学生実装課題：Level 1／2】 | 関数を完成させる課題 | **編集する** |
| 【動作確認】 | 実装した関数の結果を確かめる | 編集しない |
| 【考察課題】 | 結果について考え、文章で答える | 答えを書く |
| 【発展課題：Level 3】 | チームで選ぶ発展的な課題 | チームで決める |

動作確認の結果は、次の 4 種類で表示されます。

| 表示 | 意味 |
| --- | --- |
| `[OK]` | 期待される結果と一致した |
| `[NG]` | 実行できたが、結果が違う（入力・期待値・違いを表示）。関数が元のデータを書き換えた場合も `[NG]` |
| `[未実装]` | まだ `raise NotImplementedError` のまま |
| `[エラー]` | 実装の中でエラーが起きた（場所を表示） |

## 0.5 作業時間の目安（設計上の見積もり）

| 段階 | 目安 |
| --- | --- |
| 第0〜3章 | 1〜1.5 時間 |
| 担当テーマの Level 1 | 2〜3 時間 |
| 担当テーマの Level 2 | 1.5〜3 時間 |
| Level 3・チーム独自の機能・発表準備 | チームで計画する |

> これは教材を設計したときの**見積もり**で、実際に測った時間ではありません。
""")

# ======================================================================
# 第1章
# ======================================================================
md("""
# 第1章　実行環境の準備

この章のコードは、**全チームが最初に 1 回実行**します。基本課題（Level 1・2）は、**Python の標準ライブラリだけ**で実行できます。
""")
md(TEACHER)
code('''
# 【教員提供コード】Python のバージョンと実行環境の確認
import sys
import platform

print("Python のバージョン:", platform.python_version())
print("OS:", platform.system(), platform.release())

if sys.version_info < (3, 10):
    print("[注意] Python 3.10 以上を推奨します。")
''')
md(TEACHER)
code('''
# 【教員提供コード】基本的な import（すべて Python の標準ライブラリ）
import copy
import csv
import math
import random
import statistics
import time
import traceback
from pathlib import Path

# 追加のライブラリ（なくても基本課題は実行できる）
import importlib.util

HAS_MATPLOTLIB = importlib.util.find_spec("matplotlib") is not None
print("matplotlib（グラフ表示）:", "使える" if HAS_MATPLOTLIB else "使えない（グラフ以外は実行できます）")
''')
md(TEACHER)
code('''
# 【教員提供コード】データフォルダの場所を決める
# この Notebook と同じフォルダにある data/ を使う（相対パス）。
BASE_DIR = Path.cwd()
for folder in ["f1-life-planning-starter", "f1-career-income-optimization"]:
    if not (BASE_DIR / "data").exists() and (BASE_DIR / folder / "data").exists():
        # 教材のフォルダの 1 つ上（例：Google Colab の /content）で実行した場合
        BASE_DIR = BASE_DIR / folder

DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"

print("作業フォルダ:", BASE_DIR)
if DATA_DIR.exists():
    print("データフォルダ: OK")
else:
    print("[注意] data フォルダが見つかりません。")
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
# 第2章　データセットの概要と読み込み

## 2.1 4 種類のデータ

| 種類 | 置き場所 | 件数の目安 | 由来 | 使う場面 |
| --- | --- | ---: | --- | --- |
| Mini Dataset | Notebook の中（リストと辞書） | 2〜6 件 | 人工データ | STEP 1〜4。**手で計算して確かめられる** |
| Tiny Dataset | `data/f1a/*_tiny.csv` など | 6〜32 件 | 人工データ（乱数のシードを固定） | STEP 3〜4。境界条件や制約違反を含む |
| Small Dataset | `data/f1a/*_small.csv` など | 8〜156 行 | **公開統計を加工したもの**（出典あり） | STEP 5（Level 3）。**なくても基本課題は進められる** |
| Benchmark Dataset | ファイルなし（プログラムの中で作る） | 数千〜数万件 | 人工データ | STEP 4・第8章。実行時間の比較 |

- Mini と Tiny は、同じ意味の項目に**同じキー名（列名）**を使っています（例：初期資産は `initial_assets`、移転期間は `duration_years`）。
- **人工データ**のファイル名は `_tiny`、**公開統計を加工したデータ**のファイル名は `_small` で終わります。

## 2.2 単位のルール（全テーマ共通）

| 量 | 単位 | 注意 |
| --- | --- | --- |
| 金額 | **万円** | 月額と年額を区別する（`monthly_` と `annual_` で始まる名前） |
| 年齢 | 歳（整数） | |
| 期間 | 年（整数） | シミュレーションの 1 年目は `year = 1` |
| 時間 | **時間／週** | 1 人が使える時間は **1 週間に 168 時間**（24 × 7） |
| 割合 | 小数 | 0.02 = 2% |

- 年収は、税金や社会保険料を引く前の**額面**です。実際に使えるお金（可処分所得）はもっと少なくなります。
- **年間収支**（1 年間の収入 − 支出）と**資産残高**（その時点で持っているお金）は別のものです。
- 赤字や資産不足（マイナスの値）は、**0 に置き換えずに**そのまま記録します。
- 公開統計の CSV の**空欄**は「統計がない・秘匿・該当なし」を表します。読み込むと `None` になります。**0 ではありません。**

## 2.3 データの置き場所

```text
data/
├── f1a/  career_options_tiny.csv               （F-1A：キャリア候補、人工）
│         salary_by_age_small.csv               （F-1A：賃金構造基本統計調査を加工）
├── f1b/  work_options_tiny.csv                 （F-1B：勤務形態、人工）
│         household_scenarios_tiny.csv          （F-1B：世帯の条件、人工）
│         household_expenses_small.csv          （F-1B：家計調査を加工）
├── f1c/  housing_options_tiny.csv              （F-1C：住宅候補、人工）
│         housing_prices_small.csv              （F-1C：不動産取引価格。教員が用意した場合だけ）
└── f1d/  family_members_tiny.csv               （F-1D：家族の構成、人工）
          transfer_scenarios_tiny.csv           （F-1D：資金移転のシナリオ、人工）
          household_assets_small.csv            （F-1D：全国家計構造調査を加工）
          learning_cost_small.csv               （F-1D：子供の学習費調査を加工）
```

各列の意味・単位・出典は `data/data_dictionary.md` を見てください。
""")

# ======================================================================
# 第3章
# ======================================================================
md("""
# 第3章　Python の基礎と共通シミュレーション関数

この章では、**全テーマで使う共通関数**を定義します。必ず上から実行してください。

## 3.1 辞書のリスト（この演習のデータの基本形）

1 件のデータ（1 人、1 つの住宅など）を**辞書**で表し、それを**リスト**に入れます。
""")
md(TEACHER)
code('''
# 【教員提供コード】辞書のリストの例（テーマとは関係のない例）
fruits = [
    {"name": "りんご", "price": 150, "stock": 10},
    {"name": "みかん", "price": 80, "stock": 0},
    {"name": "ぶどう", "price": 400, "stock": 3},
]

# 1 件ずつ取り出して、キーで値を読む
for fruit in fruits:
    print(fruit["name"], fruit["price"], "円")

# 条件を満たすものだけを集める（線形探索の基本形）
in_stock = []
for fruit in fruits:
    if fruit["stock"] > 0:
        in_stock.append(fruit["name"])
print("在庫があるもの:", in_stock)
''')
md("""
## 3.2 1 年ずつ状態を更新する（シミュレーションの基本形）

「前の年の値」に「今年の変化」を足して、新しい値を作ります。これを年数の分だけくり返します。

```text
状態 = 初期値
for 年 in 1, 2, ..., T:
    状態 = 状態 + その年の変化
    記録する
```

T 年分を計算すると、くり返しは T 回です。S 個のシナリオそれぞれを T 年分計算すると、**O(S × T)** になります。

> この形の具体的な関数は、各テーマの課題として**自分で書きます**。ここでは完成した関数は用意していません。

## 3.3 元のデータを変更しない

同じシナリオを何回も計算するとき、関数の中で引数の辞書を書き換えると、2 回目の結果が変わってしまいます。
""")
md(TEACHER)
code('''
# 【教員提供コード】引数の辞書を書き換えてしまう例と、書き換えない例
person = {"name": "仮想の人物", "assets": 100}

def add_bonus_bad(p):
    p["assets"] += 10          # 引数の辞書そのものを書き換えている
    return p["assets"]

def add_bonus_good(p):
    return p["assets"] + 10    # 新しい値を計算して返すだけ

print(add_bonus_good(person), add_bonus_good(person), "←何回呼んでも同じ")
print(add_bonus_bad(person), add_bonus_bad(person), "←呼ぶたびに変わる")
print("元のデータ:", person)
''')
md(f"""
## 3.4 共通関数（データの読み込み・表示・動作確認）

{TEACHER}

| 関数 | 何をするか |
| --- | --- |
| `load_csv(path, int_columns, float_columns)` | CSV を読み込み、辞書のリストにする（ファイルがなければ空のリスト。空欄は `None`） |
| `show_records(records, limit)` | 辞書のリストを表の形で表示する |
| `check(label, func, args, expected)` | 関数の結果を期待値と比べ、`[OK]`・`[NG]`・`[未実装]`・`[エラー]` を表示する。小数は小さな誤差を許す |
| `run_if_implemented(func, *args)` | 関数を実行する。未実装なら `None` を返す（グラフや Tiny Dataset への適用で使う） |
""")
code('''
# 【教員提供コード】共通関数（データの読み込み・表示・動作確認）

def load_csv(path, int_columns=(), float_columns=()):
    """CSV ファイルを読み込み、1 行を 1 つの辞書にしたリストを返す。

    引数:
        path: CSV ファイルの場所
        int_columns: 整数に変換する列の名前
        float_columns: 小数に変換する列の名前
    戻り値:
        辞書のリスト。ファイルがない場合は空のリスト。数値の列の空欄は None（0 ではない）
    """
    path = Path(path)
    if not path.exists():
        print(f"[注意] ファイルが見つかりません: {path.name}")
        return []
    records = []
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            for column in int_columns:
                row[column] = int(row[column]) if row[column] != "" else None
            for column in float_columns:
                row[column] = float(row[column]) if row[column] != "" else None
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
    widths = [min(w, 30) for w in widths]
    print("  ".join(str(c).ljust(w) for c, w in zip(columns, widths)))
    for r in shown:
        print("  ".join(str(r.get(c, ""))[:w].ljust(w) for c, w in zip(columns, widths)))
    if len(records) > limit:
        print(f"... ほか {len(records) - limit} 件（全 {len(records)} 件）")


def _is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _same(expected, actual):
    """期待値と結果が同じかを調べる。小数は小さな誤差（100 万分の 1 程度）を許す"""
    if _is_number(expected) and _is_number(actual):
        return math.isclose(expected, actual, rel_tol=1e-6, abs_tol=1e-6)
    if isinstance(expected, (list, tuple)):
        return (type(expected) is type(actual) and len(expected) == len(actual)
                and all(_same(e, a) for e, a in zip(expected, actual)))
    if isinstance(expected, dict):
        return (isinstance(actual, dict) and expected.keys() == actual.keys()
                and all(_same(expected[k], actual[k]) for k in expected))
    return expected == actual


def _short(value, width=70):
    if isinstance(value, list) and len(value) > 5:
        return f"リスト（{len(value)} 件）先頭: {repr(value[0])[:width]}"
    text = repr(value)
    return text if len(text) <= width else text[:width] + "…"


def _describe_difference(expected, actual):
    """期待される結果と実際の結果の違いを、日本語で短く説明する"""
    if actual is None and expected is not None:
        return "結果が None です（return を書き忘れていませんか？）"
    if _is_number(expected) and _is_number(actual):
        return f"値が違います：差 = {actual - expected:+g}"
    if type(expected) is not type(actual):
        return f"型が違います：期待 {type(expected).__name__}、実際 {type(actual).__name__}"
    if isinstance(expected, (list, tuple)):
        if len(expected) != len(actual):
            return f"要素の数が違います：期待 {len(expected)} 個、実際 {len(actual)} 個"
        for i, (e, a) in enumerate(zip(expected, actual)):
            if not _same(e, a):
                return f"{i} 番目（0 から数える）の要素が違います：期待 {_short(e)}、実際 {_short(a)}"
    if isinstance(expected, dict):
        missing = [k for k in expected if k not in actual]
        extra = [k for k in actual if k not in expected]
        if missing:
            return f"足りないキーがあります：{_short(missing)}"
        if extra:
            return f"余分なキーがあります：{_short(extra)}"
        for k in expected:
            if not _same(expected[k], actual[k]):
                return f"キー {k!r} の値が違います：期待 {_short(expected[k])}、実際 {_short(actual[k])}"
    return "値が違います"


def check(label, func, args, expected):
    """func(*args) の結果を expected と比べて表示する。

    戻り値: 一致すれば True、違えば（エラーを含む）False、未実装なら None
    """
    snapshot = copy.deepcopy(args)
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
    if args != snapshot:
        print(f"[NG] {label}：関数の中で引数（元のデータ）が書き換えられています。")
        return False
    if _same(expected, actual):
        print(f"[OK] {label}")
        return True
    print(f"[NG] {label}")
    print(f"     入力          : {', '.join(_short(a, 40) for a in args)}")
    print(f"     期待される結果: {_short(expected, 200)}")
    print(f"     実際の結果    : {_short(actual, 200)}")
    print(f"     違い          : {_describe_difference(expected, actual)}")
    return False


def run_if_implemented(func, *args):
    """func(*args) を実行して結果を返す。未実装なら [未実装] と表示して None を返す"""
    try:
        return func(*args)
    except NotImplementedError:
        print(f"[未実装] {func.__name__}() を実装すると、ここに結果が表示されます。")
        return None


print("共通関数を定義しました: load_csv, show_records, check, run_if_implemented")
''')
md("### 共通関数の使い方の例（テーマとは関係のない例）")
code('''
def double(x):
    return x * 2

def not_yet(x):
    raise NotImplementedError("学生実装課題")

def broken(x):
    return x * undefined_name   # わざとエラーを起こす

check("2 倍にする", double, (3,), 6)              # [OK]
check("小数（小さな誤差は許す）", double, (0.1,), 0.2)   # [OK]
check("わざと違う期待値", double, (3,), 7)        # [NG]
check("まだ作っていない関数", not_yet, (3,), 6)    # [未実装]
check("エラーが起きる関数", broken, (3,), 6)       # [エラー]
''')
md(f"""
## 3.5 実行時間とグラフの共通関数（Level 2・第8章で使う）

{TEACHER} Level 1 だけに取り組む場合は、実行するだけで大丈夫です。

| 関数 | 何をするか |
| --- | --- |
| `measure_time(func, args, repeat)` | `func(*args)` を何回か実行し、実行時間の**中央値**（秒）を返す |
| `compare_speed(baseline, improved, make_input, sizes)` | 2 つの関数を**同じ入力**で動かし、結果が同じか確かめてから実行時間を比べる |
| `jp(japanese, english)` | 日本語フォントがあれば日本語、なければ英語のラベルを返す |
| `plot_lines(x, series, title, xlabel, ylabel)` | 折れ線グラフ（matplotlib がなければ文字で表示） |
| `plot_bars(names, values, title, ylabel)` | 棒グラフ |
| `plot_scatter(points, title, xlabel, ylabel, highlight)` | 散布図。`highlight` の点を強調する |
| `plot_hist(values, title, xlabel, line)` | ヒストグラム（値の分布）。`line` の位置に縦線を引く |
""")
code('''
# 【教員提供コード】実行時間とグラフの共通関数

def measure_time(func, args, repeat=5):
    """func(*args) を repeat 回実行し、実行時間の中央値（秒）を返す。"""
    times = []
    for _ in range(repeat):
        start = time.perf_counter()
        func(*args)
        times.append(time.perf_counter() - start)
    return statistics.median(times)


def compare_speed(baseline, improved, make_input, sizes, repeat=3, time_limit=2.0, same=None):
    """2 つの関数を、同じ入力で実行時間を比べる。結果が違うときは比べない。

    same: 2 つの結果が同じかを判定する関数（省略すると == で比べる）
    戻り値: [(件数, 基本版の秒, 改良版の秒), ...]
    """
    rows = []
    for n in sizes:
        args = make_input(n)                       # データの生成は計測に含めない
        try:
            result_base = baseline(*args)
            result_improved = improved(*args)
        except NotImplementedError:
            print("[未実装] 基本版または改良版がまだ実装されていません。")
            return rows
        is_same = same(result_base, result_improved) if same else _same(result_base, result_improved)
        if not is_same:
            print(f"[NG] N = {n:,} のとき、2 つの関数の結果が一致しません。速さを比べる前に、結果を一致させてください。")
            return rows
        t_base = measure_time(baseline, args, repeat)
        t_improved = measure_time(improved, args, repeat)
        rows.append((n, t_base, t_improved))
        print(f"N = {n:>8,}　基本版 {t_base:.6f} 秒　改良版 {t_improved:.6f} 秒")
        if t_base > time_limit:
            print("基本版に時間がかかるため、これより大きい件数は試しません。")
            break
    if rows:
        print("結果は一致しました。時間はこのコンピュータでの実測値で、環境によって変わります。")
    return rows


def jp(japanese, english):
    """日本語フォントがあれば日本語、なければ英語のラベルを返す"""
    return japanese if JAPANESE_FONT else english


def plot_lines(x, series, title, xlabel, ylabel):
    """折れ線グラフ。series は {系列の名前: 値のリスト}"""
    if not HAS_MATPLOTLIB:
        for name, values in series.items():
            print(name, [round(v, 1) for v in values[:10]], "...")
        return
    fig, ax = plt.subplots(figsize=(7, 4))
    for name, values in series.items():
        ax.plot(x, values, marker="o", markersize=3, label=name)
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3)
    ax.legend()
    plt.show()


def plot_bars(names, values, title, ylabel):
    """棒グラフ（matplotlib がなければ文字で表示）"""
    if not HAS_MATPLOTLIB:
        for name, value in zip(names, values):
            print(f"{name:>10}: {value:,.1f}")
        return
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar([str(n) for n in names], values, color="#4C78A8")
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.3)
    plt.show()


def plot_scatter(points, title, xlabel, ylabel, highlight=()):
    """散布図。points は (x, y) のリスト、highlight は強調する (x, y) のリスト"""
    if not HAS_MATPLOTLIB:
        print(f"点の数: {len(points)}（強調: {len(highlight)}）")
        return
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter([p[0] for p in points], [p[1] for p in points], color="#9AA5B1", label=jp("すべて", "all"))
    if highlight:
        ax.scatter([p[0] for p in highlight], [p[1] for p in highlight], color="#D1495B",
                   label=jp("条件を満たす", "selected"))
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3)
    ax.legend()
    plt.show()


def plot_hist(values, title, xlabel, line=None):
    """ヒストグラム。line を指定すると、その位置に縦線を引く"""
    if not HAS_MATPLOTLIB:
        print(f"件数 {len(values)}、最小 {min(values)}、最大 {max(values)}")
        return
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(values, bins=10, color="#4C78A8", edgecolor="white")
    if line is not None:
        ax.axvline(line, color="#D1495B", linestyle="--", label=jp("予算", "budget"))
        ax.legend()
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(jp("件数", "count"))
    plt.show()


print("共通関数を定義しました: measure_time, compare_speed, jp, plot_lines, plot_bars, plot_scatter, plot_hist")
''')
md("""
## 3.6 時間計算量の記号

| 記号 | 意味 |
| --- | --- |
| N | 候補データの件数（キャリア候補、住宅候補など） |
| S | シナリオの数 |
| T | シミュレーションの年数 |
| P | 家族の人数 |
| K | 条件を満たした候補の件数 |
| Q | 同じデータで探索をくり返す回数 |

| 計算量 | 例 |
| --- | --- |
| O(T) | 1 つのシナリオを T 年分シミュレーションする |
| O(S × T) | S 個のシナリオをそれぞれ T 年分シミュレーションする |
| O(N) | N 件の候補を先頭から 1 件ずつ調べる（線形探索） |
| O(log N) | ソート済みの N 件から、境界の位置を二分探索で探す |
| O(N log N) | N 件をソートする（Python の `sorted()` など） |
| O(N²) | 単純な方法で N 件をソートする（挿入ソートなど） |

> 異なるアルゴリズムの速さを比べるときは、**同じ入力**で、**同じ結果**になることを確かめてから比べます。
""")


# ======================================================================
# テーマ章の共通部分
# ======================================================================
SECTIONS = [
    "社会的背景と解決すべき問題",
    "技術的背景と基本原理",
    "本演習の学習目標",
    "使用するデータセット",
    "STEP 1：データの読み込みと確認",
    "STEP 2：基本的な計算処理",
    "STEP 3：基本シミュレーションの完成",
    "STEP 4：探索アルゴリズムによる比較と改良",
    "STEP 5：公開統計データの利用と発展課題",
    "結果の考察とチーム独自の機能開発",
]
DATA_TABLE_HEAD = "| 種類 | 置き場所 | 件数 | 由来 | 状態 |\n| --- | --- | ---: | --- | --- |\n"


def emit_task(task, level_label):
    md(f"### {task['title']}\n\n{level_label}\n\n" + textwrap.dedent(task["explain"]).strip())
    code(task["stub"])
    hints(*task["hints"])
    md(CHECK)
    code(task["check"])


def theme_chapter(t):
    n = t["no"]
    md(f"""
    # 第{n}章　{t['code']} {t['title']}
    ## {t['english']}

    > この章は、第0章〜第3章を実行した後なら、**他のテーマの章を実行しなくても**使えます。

    | 項目 | 内容 |
    | --- | --- |
    | このテーマで解決する問題 | {t['summary']['problem']} |
    | 入力データ | {t['summary']['input']} |
    | プログラム内部で行う計算 | {t['summary']['process']} |
    | 出力結果 | {t['summary']['output']} |
    | 完成イメージ | {t['summary']['image']} |
    | 想定作業時間（設計上の見積もり） | Level 1：2〜3 時間、Level 2：1.5〜3 時間 |

    | この章の進め方 | 節 | 内容 |
    | --- | --- | --- |
    | まず読む | {n}.1〜{n}.4 | 問題・背景・学習目標・データ |
    | **Level 1（必須）** | {n}.5〜{n}.7 | データを見る → 課題1〜4 を実装する → Tiny Dataset で確かめる |
    | Level 2（推奨） | {n}.8 | 課題5〜7：探索・ソート・シナリオの比較 |
    | Level 3（選択） | {n}.9〜{n}.10 | 公開統計・発展課題・**チーム独自の機能**・考察 |
    """)
    md(f"## {n}.1 {SECTIONS[0]}\n\n" + textwrap.dedent(t["problem"]).strip())
    md(f"## {n}.2 {SECTIONS[1]}\n\n" + textwrap.dedent(t["background"]).strip())
    md(f"## {n}.3 {SECTIONS[2]}\n\n" + textwrap.dedent(t["goals"]).strip())
    md(f"## {n}.4 {SECTIONS[3]}\n\n" + DATA_TABLE_HEAD + textwrap.dedent(t["data"]).strip())

    # STEP 1
    md(f"""
    ## {n}.5 {SECTIONS[4]}

    **対応レベル：Level 1（基本課題）**　／　**学習目標：** データの各項目の意味と単位を説明できる。

    まず Mini Dataset を表示します。Notebook の中に直接書いてあるので、CSV ファイルがなくても実行できます。
    """)
    md(TEACHER)
    code(t["mini_code"])
    md(f"{THINK}（手で確認しよう）\n\n" + textwrap.dedent(t["mini_questions"]).strip())
    md("次に Tiny Dataset（人工データの CSV）を読み込みます。\n\n" + TEACHER)
    code(t["tiny_code"])

    # STEP 2・3（Level 1）
    md(f"## {n}.6 {SECTIONS[5]}\n\n**対応レベル：Level 1（基本課題）**\n\n" + textwrap.dedent(t["step2_intro"]).strip())
    for task in t["step2"]:
        emit_task(task, LEVEL1)
    md(f"## {n}.7 {SECTIONS[6]}\n\n**対応レベル：Level 1（基本課題）**\n\n" + textwrap.dedent(t["step3_intro"]).strip())
    for task in t["step3"]:
        emit_task(task, LEVEL1)
    md("### Tiny Dataset で確かめる（Level 1）\n\n" + CHECK + "\n\n"
       "Mini Dataset で `[OK]` になっても、もっと多いデータや境界条件では間違えることがあります。"
       "期待値は、教員が別の方法で確かめた値です。")
    code(t["tiny_check"])
    md("### Tiny Dataset に適用する\n\n" + TEACHER)
    code(t["tiny_apply"])
    md("### 結果をグラフで確認する\n\n" + TEACHER + " 関数が未実装のときは、グラフを表示せずに説明だけを表示します。")
    code(t["viz"])
    md(f"{THINK}\n\n" + textwrap.dedent(t["step3_think"]).strip())

    # STEP 4（Level 2）
    md(f"## {n}.8 {SECTIONS[7]}\n\n**対応レベル：Level 2（改良課題）**\n\n" + textwrap.dedent(t["step4"]).strip())
    for task in t["step4_tasks"]:
        emit_task(task, LEVEL2)
    md("### Tiny Dataset で確かめる（Level 2）\n\n" + CHECK)
    code(t["step4_tiny_check"])
    for extra_md, extra_code in t["step4_extra"]:
        md(textwrap.dedent(extra_md).strip() + "\n\n" + TEACHER)
        code(extra_code)
    md(f"{THINK}\n\n" + textwrap.dedent(t["step4_think"]).strip())

    # STEP 5（Level 3）
    md(f"## {n}.9 {SECTIONS[8]}\n\n**対応レベル：Level 3（発展課題）**\n\n" + textwrap.dedent(t["step5"]).strip())
    md(TEACHER)
    code(t["small_code"])
    md(f"{LEVEL3}\n\n" + textwrap.dedent(t["step5_tasks"]).strip())

    md(f"## {n}.10 {SECTIONS[9]}\n\n" + textwrap.dedent(t["discussion"]).strip()
       + "\n\n### チーム独自の機能の候補（1 つ以上を必ず実装する）\n\n" + textwrap.dedent(t["team_features"]).strip()
       + "\n\n独自の機能を作ったら、**入力・処理・出力**、使ったアルゴリズムと計算量、動作確認の方法、"
         "モデルの仮定と限界を Notebook に書いてください。旧教材や他の資料のコードを参考にした場合は、"
         "**出典と、自分たちが変更した点**を明記します。")


def small_loader(var, rel_path, int_columns, float_columns, note, show_filter=None):
    shown = f"[r for r in {var} if {show_filter}]" if show_filter else var
    return f'''
    # 【教員提供コード】Small Dataset（公開統計を加工した CSV）を読み込む
    small_path = DATA_DIR / "{rel_path}"
    if small_path.exists():
        {var} = load_csv(small_path, int_columns={int_columns!r}, float_columns={float_columns!r})
        print("{rel_path}:", len({var}), "行")
        show_records({shown}, limit=12)
    else:
        {var} = []
        print("Small Dataset がありません（{note}）。")
        print("Mini Dataset と Tiny Dataset（人工データ）で、Level 1・2 を進めてください。")
    '''


# ======================================================================
# 第4章　F-1A
# ======================================================================
F1A = {
    "no": 4, "code": "F-1A", "title": "キャリア選択・教育投資と生涯所得",
    "english": "Career Choice, Education Investment and Lifetime Income",
    "summary": {
        "problem": "進学・就職などの選択によって、長期的な所得がどう変わるかを比べる",
        "input": "キャリア候補（就業開始年齢、退職年齢、初年度年収、昇給率、教育費）",
        "process": "年齢ごとの年収、就業年数、生涯所得（累積和）、教育費を引いた累積所得、回収年齢の探索",
        "output": "キャリア候補ごとの生涯所得・累積所得の表とグラフ、順位、教育費の回収年齢",
        "image": "「高校卒業後に就職」「専門学校卒業後に就職」「大学卒業後に就職」の累積所得の推移を 1 つのグラフで比べる",
    },
    "problem": """
    進学、資格取得、就職、転職などの選択によって、将来の所得や働き方は変わります。
    教育やスキルへの投資には**費用と時間**が必要ですが、将来の所得を増やす可能性もあります。

    この章では、複数のキャリアの候補を、**長期的な所得の推移**という観点から比べるプログラムを作ります。

    > 中心となる問い：**どのキャリアの候補が、どの年齢で、どれだけの所得になるか。教育費を回収できるのは何歳か。**

    注意：
    - Mini・Tiny の金額は教材のための仮定値です。実際の職業別・学歴別の所得ではありません。
    - 所得だけでキャリアの価値は決まりません。やりたいこと、学ぶこと自体の価値、働く時間、健康なども大切です。
    """,
    "background": """
    | 用語 | この教材での意味 |
    | --- | --- |
    | 年収 | その年齢の 1 年間の給与（額面、万円） |
    | 昇給率（`annual_growth`） | 年収が毎年増える割合（0.02 = 2%） |
    | 就業年数 | 就業開始年齢から退職年齢の**前の年**までの年数 |
    | 生涯所得 | 就業期間の年収の**合計**（教育費は引かない） |
    | 累積所得（教育費控除後） | 生涯所得 − 教育費。**税金を引いた所得や、実際の貯金（資産残高）とは違います** |
    | 教育費の回収年齢 | 教育費を引いた累積額が、比較する候補に**追いつく（以上になる）最初の年齢** |

    **年収のモデル（この教材の仮定）**

    ```text
    年齢 a の年収 = initial_salary × (1 + annual_growth) ^ (a − start_age)   （start_age ≤ a < 退職年齢）
    年齢 a の年収 = 0                                                     （それ以外）
    ```

    - 就業開始年齢の年は初年度年収のまま。**昇給は 2 年目（start_age + 1 歳）から**です。
    - 退職年齢（`retirement_age`）の年からは計算しません。65 歳なら 64 歳の 1 年間までです。
    - **教育費は 18 歳の年にまとめて払う**と単純化します（実際は在学中に少しずつ払います）。
    - 生涯所得は、年齢を 1 つずつ増やしながら年収を足していく**累積和**で計算します。T 年分なら O(T)、N 個の候補なら O(N × T)。
    """,
    "goals": """
    | レベル | STEP | 学習目標 | 学生実装課題 |
    | --- | --- | --- | --- |
    | Level 1 | STEP 1 | キャリア候補のデータの意味と単位を説明できる | ― |
    | Level 1 | STEP 2 | 条件分岐と計算で、就業年数・年収を求められる | 課題1 `calculate_working_years()`、課題2 `salary_at_age()` |
    | Level 1 | STEP 3 | ループで累積和を計算し、候補を比べられる | 課題3 `lifetime_income()`、課題4 `summarize_careers()` |
    | Level 2 | STEP 4 | 線形探索・ソートで候補を比べ、回収年齢を探せる | 課題5 `filter_careers()`、課題6 `rank_careers()`、課題7 `find_payback_age()` |
    | Level 3 | STEP 5 | 公開統計や発展的なモデルで、チーム独自の機能を作れる | 4.9 から選ぶ |
    """,
    "data": """
    | Mini Dataset | Notebook の中の `career_options` | 3 | 人工データ（仮定値） | 利用可 |
    | Tiny Dataset | `data/f1a/career_options_tiny.csv` | 25 | 人工データ（シード固定。昇給率 0、教育費 0、就業期間 0、同じ生涯所得、回収できない候補を含む） | 利用可 |
    | Small Dataset | `data/f1a/salary_by_age_small.csv` | 84 | 厚生労働省「令和7年賃金構造基本統計調査」を加工 | 利用可 |
    | Benchmark Dataset | プログラムの中で生成 | 可変 | 人工データ | 第8章 |
    """,
    "mini_code": '''
    # 【教員提供コード】F-1A の Mini Dataset（人工データ。金額は万円、年齢は歳）
    RETIREMENT_AGE = 65    # 退職年齢（この年齢の年からは所得なし）。変えて試してよいパラメータ

    career_options = [
        {"career_id": "A", "career_name": "高校卒業後に就職", "start_age": 18, "retirement_age": 65,
         "initial_salary": 250, "annual_growth": 0.02, "education_cost": 0},
        {"career_id": "B", "career_name": "専門学校卒業後に就職", "start_age": 20, "retirement_age": 65,
         "initial_salary": 300, "annual_growth": 0.025, "education_cost": 200},
        {"career_id": "C", "career_name": "大学卒業後に就職", "start_age": 22, "retirement_age": 65,
         "initial_salary": 330, "annual_growth": 0.03, "education_cost": 400},
    ]
    show_records(career_options)
    ''',
    "mini_questions": """
    1. 候補 A の 18 歳、19 歳、20 歳の年収はいくらですか（手で計算してみましょう）。
    2. 候補 C の就業年数（22 歳〜64 歳）は何年ですか。
    3. 退職年齢を 21 歳とした場合（計算練習のための仮の設定）、候補 A の 18〜20 歳の年収の合計はいくらですか。
    """,
    "tiny_code": '''
    # 【教員提供コード】F-1A の Tiny Dataset を読み込む
    tiny_careers = load_csv(DATA_DIR / "f1a" / "career_options_tiny.csv",
                            int_columns=["start_age", "retirement_age", "education_cost"],
                            float_columns=["initial_salary", "annual_growth"])
    tiny_career_by_id = {c["career_id"]: c for c in tiny_careers}   # ID から候補を取り出す辞書
    print("キャリア候補:", len(tiny_careers), "件")
    show_records(tiny_careers, limit=5)
    ''',
    "step2_intro": "**学習目標：** 条件分岐と計算式で、1 人・1 年分の値を求められる。",
    "step2": [
        {
            "title": "課題1：就業年数を計算する",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `calculate_working_years(start_age, retirement_age)` |
            | 引数 | `start_age`：就業開始年齢（整数）、`retirement_age`：退職年齢（整数） |
            | 戻り値 | 就業年数（整数）。働く期間がない場合は 0 |
            | 例 | `calculate_working_years(18, 65)` → `47` |
            """,
            "stub": f'''
            # 【学生実装課題：Level 1】課題1
            def calculate_working_years(start_age, retirement_age):
                """就業開始年齢から退職年齢の前の年までの年数を返す。働く期間がなければ 0。"""
                # TODO: 退職年齢 − 就業開始年齢 を計算する。
                # TODO: 結果が 0 より小さくなる場合は 0 を返す。
                {STUB}
            ''',
            "hints": ("18 歳から 64 歳まで働くと、何年になりますか。指で数えずに、引き算で求められます。",
                      "引き算と `if` 文。",
                      "years ← retirement_age − start_age\nもし years < 0 なら 0 を返す\nyears を返す"),
            "check": '''
            # 【動作確認】
            check("課題1：18 歳から 65 歳", calculate_working_years, (18, 65), 47)
            check("課題1：22 歳から 65 歳", calculate_working_years, (22, 65), 43)
            check("課題1：開始と退職が同じ年齢（就業期間 0）", calculate_working_years, (65, 65), 0)
            check("課題1：開始が退職より後", calculate_working_years, (66, 65), 0)
            ''',
        },
        {
            "title": "課題2：年齢に応じた年収を計算する",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `salary_at_age(career, age, retirement_age)` |
            | 引数 | `career`：キャリア候補の辞書、`age`：年齢、`retirement_age`：退職年齢 |
            | 戻り値 | その年齢の 1 年間の年収（万円、小数）。働いていない年齢は 0 |
            | 例 | 候補 A、20 歳 → `250 × 1.02 × 1.02 = 260.1` |

            - 退職年齢は、辞書の `retirement_age` ではなく**引数**を使います（退職年齢を変えて試せるようにするため）。
            - `career` の辞書は書き換えないでください（読むだけにします）。
            """,
            "stub": f'''
            # 【学生実装課題：Level 1】課題2
            def salary_at_age(career, age, retirement_age):
                """career の、age 歳の 1 年間の年収（万円）を返す。就業前・退職後は 0。"""
                # TODO: age が就業開始年齢より前、または退職年齢以降なら 0 を返す。
                # TODO: 何年目か（age − start_age）を求め、昇給率を使って年収を計算する。
                {STUB}
            ''',
            "hints": ("就職した年は初年度年収のままです。1 年たつごとに (1 + 昇給率) 倍になります。",
                      "`career[\"start_age\"]` のように辞書から値を読みます。累乗は `**` です。",
                      "もし age < start_age または age >= retirement_age なら 0 を返す\n"
                      "k ← age − start_age\n年収 ← initial_salary × (1 + annual_growth) の k 乗\n年収を返す"),
            "check": '''
            # 【動作確認】
            A, B, C = career_options
            check("課題2：候補 A、18 歳（就職した年）", salary_at_age, (A, 18, RETIREMENT_AGE), 250)
            check("課題2：候補 A、20 歳", salary_at_age, (A, 20, RETIREMENT_AGE), 260.1)
            check("課題2：候補 C、21 歳（就職前）", salary_at_age, (C, 21, RETIREMENT_AGE), 0)
            check("課題2：候補 A、65 歳（退職年齢）", salary_at_age, (A, 65, RETIREMENT_AGE), 0)
            ''',
        },
    ],
    "step3_intro": """
    **学習目標：** ループで年収を 1 年ずつ足し（累積和）、複数の候補をまとめて比べられる。

    > 生涯所得（教育費を引かない）と、累積所得（教育費を引いた値）を**区別**します。
    """,
    "step3": [
        {
            "title": "課題3：生涯所得を計算する",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `lifetime_income(career, retirement_age)` |
            | 引数 | `career`：キャリア候補の辞書、`retirement_age`：退職年齢 |
            | 戻り値 | 就業開始年齢から退職年齢の前の年までの年収の合計（万円） |
            | 例 | 候補 A、退職年齢 21 歳（計算練習のための仮の設定） → `250 + 255 + 260.1 = 765.1` |

            課題2 の `salary_at_age()` を使います。
            """,
            "stub": f'''
            # 【学生実装課題：Level 1】課題3
            def lifetime_income(career, retirement_age):
                """career の生涯所得（就業期間の年収の合計、万円）を返す。"""
                # TODO: 合計を 0 から始める。
                # TODO: 就業開始年齢から退職年齢の前の年まで、年齢を 1 つずつ増やしながら年収を足す。
                {STUB}
            ''',
            "hints": ("年齢を 1 つずつ進めながら、その年の年収を合計に足していきます（累積和）。",
                      "`for age in range(開始, 終了):` の `range` は「終了」を含みません。",
                      "total ← 0\nfor age in range(start_age, retirement_age):\n    total ← total + salary_at_age(career, age, retirement_age)\ntotal を返す"),
            "check": '''
            # 【動作確認】
            A, B, C = career_options
            check("課題3：候補 A、退職年齢 21 歳（手で計算できる例）", lifetime_income, (A, 21), 765.1)
            check("課題3：候補 B、退職年齢 23 歳", lifetime_income, (B, 23), 922.6875)
            check("課題3：候補 C、退職年齢 22 歳（就業期間 0 年）", lifetime_income, (C, 22), 0)
            ''',
        },
        {
            "title": "課題4：複数のキャリア候補をまとめて比べる",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `summarize_careers(careers, retirement_age)` |
            | 引数 | `careers`：キャリア候補の辞書のリスト、`retirement_age`：退職年齢 |
            | 戻り値 | 候補ごとの辞書 `{"career_id": ..., "lifetime_income": ..., "net_income": ...}` のリスト（入力と同じ順番） |
            | 例 | 退職年齢 23 歳の候補 C → `{"career_id": "C", "lifetime_income": 330.0, "net_income": -70.0}` |

            - `net_income` は「生涯所得 − 教育費」です。マイナスになっても、そのまま返します。
            - 課題3 の `lifetime_income()` を使います。
            """,
            "stub": f'''
            # 【学生実装課題：Level 1】課題4
            def summarize_careers(careers, retirement_age):
                """各候補の生涯所得と、教育費を引いた累積所得をまとめたリストを返す。"""
                # TODO: 結果を入れる空のリストを用意する。
                # TODO: 各候補について、生涯所得と「生涯所得 − 教育費」を計算し、辞書にして追加する。
                {STUB}
            ''',
            "hints": ("候補が 3 つなら、結果の辞書も 3 つです。1 つずつ作ってリストに追加します。",
                      "`for career in careers:`、辞書は `{\"career_id\": ..., ...}`、追加は `append()`。",
                      "results ← 空のリスト\nfor career in careers:\n    gross ← lifetime_income(career, retirement_age)\n    net ← gross − career の education_cost\n    {career_id, lifetime_income, net_income} の辞書を results に追加\nresults を返す"),
            "check": '''
            # 【動作確認】
            expected_23 = [
                {"career_id": "A", "lifetime_income": 1301.01004, "net_income": 1301.01004},
                {"career_id": "B", "lifetime_income": 922.6875, "net_income": 722.6875},
                {"career_id": "C", "lifetime_income": 330.0, "net_income": -70.0},
            ]
            check("課題4：Mini Dataset、退職年齢 23 歳", summarize_careers, (career_options, 23), expected_23)
            check("課題4：候補が 0 件", summarize_careers, ([], RETIREMENT_AGE), [])
            ''',
        },
    ],
    "tiny_check": '''
    # 【動作確認】Tiny Dataset（境界条件）
    if tiny_careers:
        T = tiny_career_by_id
        check("Tiny：C21 昇給率 0（300 × 47 年）", lifetime_income, (T["C21"], 65), 14100)
        check("Tiny：C25 就業期間 0（65 歳開始・65 歳退職）", lifetime_income, (T["C25"], 65), 0)
        check("Tiny：C01 自分の退職年齢（60 歳）まで", lifetime_income, (T["C01"], T["C01"]["retirement_age"]), 16539.8669)
        check("Tiny：C22 30 歳の年収（就職した年）", salary_at_age, (T["C22"], 30, 65), 300)
        check("Tiny：同じ生涯所得になる C21・C24 と就業期間 0 の C25", summarize_careers,
              ([T["C21"], T["C24"], T["C25"]], 65),
              [{"career_id": "C21", "lifetime_income": 14100, "net_income": 14100},
               {"career_id": "C24", "lifetime_income": 14100, "net_income": 14100},
               {"career_id": "C25", "lifetime_income": 0, "net_income": 0}])
    else:
        print("Tiny Dataset がないため、確認をスキップしました。")
    ''',
    "tiny_apply": '''
    # 【教員提供コード】Tiny Dataset の各候補の生涯所得（各候補の退職年齢を使う）
    for career in tiny_careers[:10]:
        total = run_if_implemented(lifetime_income, career, career["retirement_age"])
        if total is None:
            break
        print(f'{career["career_id"]:>4}  {career["career_name"]:<24}  退職 {career["retirement_age"]} 歳  生涯所得 {total:>9,.1f} 万円')
    ''',
    "viz": '''
    # 【教員提供コード】Mini Dataset の年齢別の累積所得（教育費を引く前）
    # lifetime_income(career, a + 1) は「a 歳までの年収の合計」になる（課題3 を実装すると表示される）
    ages = list(range(18, RETIREMENT_AGE))
    if run_if_implemented(lifetime_income, career_options[0], 19) is not None:
        series = {}
        for career in career_options:
            series[career["career_id"]] = [lifetime_income(career, a + 1) for a in ages]
        plot_lines(ages, series, jp("年齢別の累積所得（人工データ、教育費を引く前）", "Cumulative income by age (synthetic)"),
                   jp("年齢", "age"), jp("累積所得（万円）", "cumulative income (10k JPY)"))
    ''',
    "step3_think": """
    1. 退職年齢 65 歳のとき、生涯所得が最も大きい候補はどれですか。教育費を引いた累積所得ではどうですか。
    2. グラフで、候補 A の累積所得が候補 B・C に追い抜かれるのは何歳ごろですか。
    3. このモデルに含まれていないもの（税金、失業、労働時間など）を 3 つ挙げてください。
    """,
    "step4": """
    STEP 3 で計算した結果を使って、**探す・並べる・追いつく年齢を見つける**処理を作ります。

    | 課題 | 関数 | アルゴリズム | 計算量 |
    | --- | --- | --- | --- |
    | 課題5 | `filter_careers(summaries, min_net_income)` | 線形探索（条件による抽出） | O(N) |
    | 課題6 | `rank_careers(summaries, key)` | ソート（降順・安定） | 挿入ソートなら O(N²)、`sorted()` なら O(N log N) |
    | 課題7 | `find_payback_age(career, baseline, retirement_age)` | 累積和 + 線形探索 | O(T) |

    > 回収年齢の探索では、累積額の差が**単調に増えるとは限りません**（転職などで逆転することがある）。
    > そのため、二分探索ではなく、若い年齢から順に調べる線形探索を使います。
    """,
    "step4_tasks": [
        {
            "title": "課題5：条件を満たすキャリア候補を探す（線形探索）",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `filter_careers(summaries, min_net_income)` |
            | 引数 | `summaries`：課題4 の結果の形のリスト、`min_net_income`：累積所得（教育費控除後）の下限（万円） |
            | 戻り値 | `net_income` が下限**以上**の候補の `career_id` のリスト（入力と同じ順番）。なければ `[]` |
            | 例 | 下限 20000 → Mini（退職 65 歳）では `["B", "C"]` |
            """,
            "stub": f'''
            # 【学生実装課題：Level 2】課題5
            def filter_careers(summaries, min_net_income):
                """累積所得（教育費控除後）が min_net_income 以上の候補の career_id のリストを返す。"""
                # TODO: 先頭から 1 件ずつ調べ、条件を満たす候補の ID を集める。
                {STUB}
            ''',
            "hints": ("すべての候補を先頭から順に調べます。下限と**同じ値**の候補も含めます。",
                      "`for s in summaries:`、`if s[\"net_income\"] >= ...:`、`append()`。",
                      "result ← 空のリスト\nfor s in summaries:\n    もし s の net_income >= min_net_income なら\n        s の career_id を result に追加\nresult を返す"),
            "check": '''
            # 【動作確認】課題4 の結果の形のデータ（数値は手で作った例）
            sample = [
                {"career_id": "A", "lifetime_income": 19000, "net_income": 19000},
                {"career_id": "B", "lifetime_income": 24000, "net_income": 23800},
                {"career_id": "C", "lifetime_income": 28000, "net_income": 27600},
            ]
            check("課題5：下限 20000", filter_careers, (sample, 20000), ["B", "C"])
            check("課題5：下限と同じ値（23800）を含む", filter_careers, (sample, 23800), ["B", "C"])
            check("課題5：該当なし", filter_careers, (sample, 99999), [])
            check("課題5：候補が 0 件", filter_careers, ([], 0), [])
            ''',
        },
        {
            "title": "課題6：キャリア候補を指標で並べる（ソート）",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `rank_careers(summaries, key)` |
            | 引数 | `summaries`：課題4 の結果の形のリスト、`key`：並べる指標の名前（`"lifetime_income"` か `"net_income"`） |
            | 戻り値 | 指標の**大きい順**に並べた**新しいリスト**。値が同じなら、元の順番を保つ（安定なソート） |
            | 例 | `key="net_income"` → C、B、A の順 |

            - 元のリスト `summaries` の順番を変えないでください（コピーを並べ替える）。
            - 授業で学んだ**挿入ソート**を自分で書いても、`sorted()` を使ってもかまいません。どちらを使ったかと、計算量を説明できるようにします。
            """,
            "stub": f'''
            # 【学生実装課題：Level 2】課題6
            def rank_careers(summaries, key):
                """指標 key の大きい順に並べた新しいリストを返す（同じ値なら元の順番）。"""
                # TODO: 元のリストのコピーを作る。
                # TODO: key の値の大きい順に並べ替える（同じ値の順番は変えない）。
                {STUB}
            ''',
            "hints": ("元のリストを直接並べ替えると、呼び出した側のデータが変わってしまいます。まずコピーを作ります。",
                      "コピーは `list(summaries)`。挿入ソートなら while 文で前の要素と比べます。"
                      "`sorted()` なら `key=` と `reverse=True` を調べてみましょう。",
                      "ranked ← summaries のコピー\n挿入ソート：i = 1 から最後まで\n    tmp ← ranked[i]\n"
                      "    前の要素の key が tmp の key より小さい間、前の要素を 1 つ後ろへずらす\n    空いた位置に tmp を入れる\nranked を返す"),
            "check": '''
            # 【動作確認】
            sample = [
                {"career_id": "A", "lifetime_income": 19000, "net_income": 19000},
                {"career_id": "B", "lifetime_income": 24000, "net_income": 23800},
                {"career_id": "C", "lifetime_income": 28000, "net_income": 27600},
                {"career_id": "D", "lifetime_income": 24000, "net_income": 24000},
            ]
            check("課題6：net_income の大きい順", lambda s, k: [x["career_id"] for x in rank_careers(s, k)],
                  (sample, "net_income"), ["C", "D", "B", "A"])
            check("課題6：同じ値（B と D）は元の順番", lambda s, k: [x["career_id"] for x in rank_careers(s, k)],
                  (sample, "lifetime_income"), ["C", "B", "D", "A"])
            check("課題6：候補が 0 件", rank_careers, ([], "net_income"), [])
            ''',
        },
        {
            "title": "課題7：教育費の回収年齢を探す",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `find_payback_age(career, baseline, retirement_age)` |
            | 引数 | `career`：教育に投資する候補、`baseline`：比較する候補、`retirement_age`：退職年齢 |
            | 戻り値 | 「18 歳からその年齢までの年収の合計 − 教育費」が、`baseline` の同じ値**以上**になる最初の年齢。退職年齢の前の年までに追いつかなければ `None` |
            | 例 | Mini、候補 B と候補 A（退職 65 歳）→ `32` |

            - 教育費は 18 歳の年にまとめて払うと仮定します（両方の候補で、18 歳の時点で引く）。
            - 18 歳の時点で既に以上なら `18` を返します（回収する必要がない）。
            - 18 歳から順に年齢を 1 つずつ進め、2 つの累積額を同時に更新しながら比べます（線形探索）。
            """,
            "stub": f'''
            # 【学生実装課題：Level 2】課題7
            def find_payback_age(career, baseline, retirement_age):
                """career の累積額（教育費控除後）が baseline 以上になる最初の年齢。追いつかなければ None。"""
                # TODO: 2 つの累積額を「− 教育費」から始める。
                # TODO: 18 歳から退職年齢の前の年まで、それぞれの年収（課題2）を足しながら比べる。
                # TODO: career の累積額が baseline 以上になったら、その年齢を返す。
                {STUB}
            ''',
            "hints": ("年齢を 1 つ進めるたびに 2 人分の累積額を更新し、そのたびに比べます。最後まで追いつかなければ `None`。",
                      "`for age in range(18, retirement_age):`、課題2 の `salary_at_age()`、比較 `>=`、`return None`。",
                      "total_c ← −career の教育費、total_b ← −baseline の教育費\nfor age in 18 から retirement_age − 1 まで:\n"
                      "    total_c ← total_c + salary_at_age(career, age, retirement_age)\n    total_b ← total_b + （baseline の同じ年齢の年収）\n"
                      "    もし total_c >= total_b なら age を返す\nNone を返す"),
            "check": '''
            # 【動作確認】
            A, B, C = career_options
            check("課題7：候補 B と候補 A", find_payback_age, (B, A, RETIREMENT_AGE), 32)
            check("課題7：候補 C と候補 A", find_payback_age, (C, A, RETIREMENT_AGE), 36)
            check("課題7：同じ候補どうし（18 歳で既に以上）", find_payback_age, (A, A, RETIREMENT_AGE), 18)
            check("課題7：退職年齢 25 歳では追いつかない", find_payback_age, (C, A, 25), None)
            ''',
        },
    ],
    "step4_tiny_check": '''
    # 【動作確認】Tiny Dataset（Level 2）
    if tiny_careers:
        T = tiny_career_by_id
        check("Tiny：回収できない候補（C22 と C21）→ None", find_payback_age, (T["C22"], T["C21"], 65), None)
        check("Tiny：教育費 0 で同じ条件（C24 と C21）→ 18 歳", find_payback_age, (T["C24"], T["C21"], 65), 18)
        sample = [{"career_id": "C21", "lifetime_income": 14100, "net_income": 14100},
                  {"career_id": "C22", "lifetime_income": 12498.9, "net_income": 10998.9},
                  {"career_id": "C24", "lifetime_income": 14100, "net_income": 14100}]
        check("Tiny：同じ値の C21・C24 は元の順番", lambda s, k: [x["career_id"] for x in rank_careers(s, k)],
              (sample, "net_income"), ["C21", "C24", "C22"])
        check("Tiny：下限 14100（同じ値を含む）", filter_careers, (sample, 14100), ["C21", "C24"])
    else:
        print("Tiny Dataset がないため、確認をスキップしました。")
    ''',
    "step4_extra": [
        ("""
        ### Tiny Dataset の候補を並べて比べる

        課題4〜6 を組み合わせて、Tiny Dataset の全候補（退職 65 歳にそろえる）を累積所得の大きい順に表示します。
        """, '''
        # 【教員提供コード】Tiny Dataset の候補の順位（課題4・5・6 を実装すると表示される）
        summaries = run_if_implemented(summarize_careers, tiny_careers, 65)
        if summaries is not None:
            ranked = run_if_implemented(rank_careers, summaries, "net_income")
            if ranked is not None:
                for i, s in enumerate(ranked[:5], start=1):
                    print(f'{i} 位  {s["career_id"]}  累積所得 {s["net_income"]:>9,.1f}  生涯所得 {s["lifetime_income"]:>9,.1f}')
            found = run_if_implemented(filter_careers, summaries, 18000)
            if found is not None:
                print("累積所得が 18,000 万円以上:", len(found), "件", found)
        '''),
        ("""
        ### 教育費の回収年齢を一覧にする
        """, '''
        # 【教員提供コード】Mini Dataset の回収年齢（課題7 を実装すると表示される）
        A, B, C = career_options
        for career in (B, C):
            age = run_if_implemented(find_payback_age, career, A, RETIREMENT_AGE)
            if age is None:
                print(f'{career["career_name"]}：退職までに回収できない、または未実装')
            else:
                print(f'{career["career_name"]}：{A["career_name"]} に {age} 歳で追いつく')
        '''),
    ],
    "step4_think": """
    1. 累積所得の順位と、生涯所得（教育費を引く前）の順位は同じでしたか。
    2. 回収年齢は、教育費・初年度年収・昇給率のどれに最も敏感ですか。1 つずつ値を変えて調べてください。
    3. 「回収年齢が早い候補ほど良い」と言えますか。モデルに含まれていない要素を挙げて考えてください。
    """,
    "step5": """
    `data/f1a/salary_by_age_small.csv` は、厚生労働省「令和7年賃金構造基本統計調査」の一般労働者（民営事業所、企業規模 10 人以上、
    産業計、男女計）について、**学歴別・年齢階級別**の賃金を取り出したものです。

    | 列 | 意味 | 単位 |
    | --- | --- | --- |
    | `monthly_cash_earnings` | きまって支給する現金給与額（月額。残業代などを含む） | 万円／月 |
    | `monthly_scheduled_earnings` | 所定内給与額（月額。残業代などを含まない） | 万円／月 |
    | `annual_special_earnings` | 年間賞与その他特別給与額（ボーナスなど。**前年 1 年間**の額） | 万円／年 |

    - 統計上の年収の目安は「月額 × 12 + 年間賞与」で計算できます（**この計算は自分で行います**）。月額だけを 12 倍した値と区別してください。
    - これは**同じ年（2025 年）の異なる年齢の人たち**の平均です。**同じ人の生涯の所得を追いかけたデータではありません。**
    - 学歴別の差を、そのまま進学の**効果（因果関係）**とみなさないでください（進学する人としない人のもともとの違い、時代・産業の違いなどを含む）。
    - 空欄は「統計がない」ことを表します（例：大学卒の 19 歳以下）。0 ではありません。
    - 出典：厚生労働省「令和7年賃金構造基本統計調査」（政府統計の総合窓口(e-Stat)、https://www.e-stat.go.jp/）を加工して作成。
    """,
    "small_code": small_loader("salary_small", "f1a/salary_by_age_small.csv", ["age_min", "age_max", "survey_year"],
                               ["mean_age", "monthly_cash_earnings", "monthly_scheduled_earnings",
                                "annual_special_earnings", "workers_10"],
                               "data/f1a/salary_by_age_small.csv が配布物に含まれていない場合があります",
                               show_filter='r["education_code"] == "university"'),
    "step5_tasks": """
    次の中から、チームで関心のあるものを選びます（すべてを実装する必要はありません。**完成コードは提供しません**）。

    1. **公開賃金統計の利用**：Small Dataset から学歴別の年齢階級ごとの年収の目安を計算し、Mini の仮定（昇給率一定）と比べる。
    2. **資格取得の時期の比較**：ある年齢で費用を払い、翌年から年収が増えるモデルを作り、取得年齢を全探索する。
    3. **転職時期の探索**：転職する年齢（例：25〜50 歳）をすべて試し、累積所得が最大になる年齢を探す（全探索 O(K × T)）。
    4. **IT エンジニアのキャリアモデル**：職種・役職ごとの年収の仮定を作り、昇進の時期を比べる。
    5. **労働時間・失業リスクを含む比較**：所得だけでなく労働時間や休職の年を入れて比べる（乱数を使う場合はシードを固定する）。
    """,
    "discussion": """
    - 生涯所得が最大の候補と、教育費を引いた累積所得が最大の候補は同じでしたか。違う場合、なぜですか。
    - どの仮定（初年度年収、昇給率、教育費、退職年齢）を変えると、順位や回収年齢が変わりましたか。
    - モデルの限界：税金・社会保険料・物価・失業・健康などを含めていないことが、結果にどう影響しますか。
    """,
    "team_features": """
    - 転職年齢の全探索と、評価指標（生涯所得・累積所得）ごとの最適な年齢の比較
    - 資格取得の費用と効果（年収の増加額）を変えたときの回収年齢の表
    - 公開賃金統計（Small Dataset）にもとづく年収カーブと、仮定値のモデルの比較グラフ
    - 労働時間を含めた「時間あたりの所得」による比較
    """,
}

# ======================================================================
# 第5章　F-1B
# ======================================================================
F1B = {
    "no": 5, "code": "F-1B", "title": "家族形成・子育て・介護と資源配分",
    "english": "Family Formation, Childcare, Elderly Care and Resource Allocation",
    "summary": {
        "problem": "成人 2 人の世帯で、所得と時間をどう配分すれば生活と育児・介護を両立できるかを比べる",
        "input": "勤務形態（年収、週の労働時間）、世帯の支出と必要な育児・介護時間、育児・介護の分担の候補",
        "process": "世帯の年間所得・支出・収支、1 人ごとの残り時間、勤務形態の組合せの全探索、制約による絞り込み",
        "output": "制約（収支・時間）を満たす組合せの一覧と、指標（収支・自由時間）による比較",
        "image": "「フルタイム＋時短」「時短＋時短」などの組合せを、収支と自由時間の散布図で比べる",
    },
    "problem": """
    家族の生活を続けるには、お金（所得）と同時に、**時間**も必要です。
    仕事、育児、介護に使う時間の合計は、1 人あたり **1 週間に 168 時間**を超えることはできません。

    この章では、成人 2 人の世帯を例に、勤務形態の組合せ（フルタイム、時短勤務、休業など）と、
    育児・介護の分担のしかたごとに、**年間の収支**と**1 人ごとの残り時間**を計算して比べます。

    注意：
    - 金額と時間は教材のための仮定値です。実際の育児休業給付金や社会保障制度は表していません。
    - 特定の家族の形や、性別による役割分担を「望ましい」とするものではありません。Adult A・Adult B は性別や役割を意味しません。
    - 家族の生活には、金額や時間では表せない価値があります。
    """,
    "background": """
    **お金の計算**（単位：万円／年）

    | 用語 | この教材での意味 |
    | --- | --- |
    | 世帯の年間所得 | 2 人の年収（額面）の合計 |
    | 世帯の年間支出 | 生活費 + 育児費 + 介護費 |
    | 年間収支 | 年間所得 − 年間支出。マイナスなら赤字 |

    **時間の計算**（単位：時間／週。1 人 168 時間）— **同じ時間を 2 回数えないよう、次の 4 つに分けます**

    | 区分 | 含むもの | 変数 |
    | --- | --- | --- |
    | 基本生活時間 | 睡眠・食事・身支度（入浴など） | `basic_hours`（初期値 77 = 1 日 11 時間。**教材の仮定値で、変えてよいパラメータ**） |
    | 労働時間 | 仕事と**通勤**の時間 | 勤務形態の `weekly_work_hours` |
    | 育児・介護時間 | 育児・介護と、それに直接伴う家事 | 分担した時間 `care_a`・`care_b` |
    | 残り時間（自由時間） | 上の 3 つ以外。**育児・介護以外の家事**、休養、趣味、学習など | `168 − 基本生活 − 労働 − 育児・介護` |

    - 2 人の**合計**の時間だけでなく、**1 人ごと**の時間の制約（残り時間が 0 以上）も確かめます。
    - 世帯全体で、育児・介護に必要な時間（`required_childcare_hours + required_eldercare_hours`）以上を 2 人で分担する必要があります。
    - 勤務形態が k 種類なら、2 人の組合せは **k × k 通り**です（全探索）。分担の候補が m 通りなら k² × m 通りを調べます。
    """,
    "goals": """
    | レベル | STEP | 学習目標 | 学生実装課題 |
    | --- | --- | --- | --- |
    | Level 1 | STEP 1 | 勤務形態と世帯のデータの意味と単位を説明できる | ― |
    | Level 1 | STEP 2 | 辞書の値を使って、世帯の所得と支出を計算できる | 課題1 `household_income()`、課題2 `household_expense()` |
    | Level 1 | STEP 3 | 収支と時間の制約を計算し、Tiny Dataset の複数の世帯で確かめられる | 課題3 `annual_balance()`、課題4 `free_hours()` |
    | Level 2 | STEP 4 | 組合せの全探索、制約による絞り込み、指標による比較ができる | 課題5 `generate_work_pairs()`、課題6 `find_feasible_plans()`、課題7 `rank_plans()` |
    | Level 3 | STEP 5 | 公開統計や発展的なモデルで、チーム独自の機能を作れる | 5.9 から選ぶ |
    """,
    "data": """
    | Mini Dataset | Notebook の中の `work_options`・`household`・`CARE_SPLITS` | 3 + 1 + 6 | 人工データ（仮定値） | 利用可 |
    | Tiny Dataset | `data/f1b/work_options_tiny.csv`、`data/f1b/household_scenarios_tiny.csv` | 6 + 25 | 人工データ（黒字・赤字、時間制約をちょうど満たす・違反する世帯を含む） | 利用可 |
    | Small Dataset | `data/f1b/household_expenses_small.csv` | 156 | 総務省「家計調査」2025 年（二人以上の世帯、世帯主の年齢階級別）を加工 | 利用可 |
    | Benchmark Dataset | プログラムの中で生成 | 可変 | 人工データ | 第8章 |
    """,
    "mini_code": '''
    # 【教員提供コード】F-1B の Mini Dataset（人工データ。金額は万円／年、時間は時間／週）
    HOURS_PER_WEEK = 168        # 1 人が 1 週間に使える時間（変えない）
    BASIC_HOURS = 77            # 基本生活時間（睡眠・食事・身支度）。教材の仮定値。変えて試してよいパラメータ

    work_options = [
        {"option_id": "W1", "work_style": "フルタイム勤務", "annual_income": 400, "weekly_work_hours": 40},
        {"option_id": "W2", "work_style": "時短勤務", "annual_income": 280, "weekly_work_hours": 28},
        {"option_id": "W3", "work_style": "休業", "annual_income": 0, "weekly_work_hours": 0},
    ]
    household = {"scenario_id": "S00", "living_cost": 360, "childcare_cost": 60, "eldercare_cost": 0,
                 "required_childcare_hours": 30, "required_eldercare_hours": 0}
    # 育児・介護の分担の候補 (Adult A の時間, Adult B の時間)。最後の (10, 10) は合計が必要時間に足りない例
    CARE_SPLITS = [(30, 0), (20, 10), (15, 15), (10, 20), (0, 30), (10, 10)]
    show_records(work_options)
    print(household)
    ''',
    "mini_questions": """
    1. 2 人とも「フルタイム勤務」のとき、世帯の年間所得はいくらですか。
    2. この世帯の年間支出はいくらですか。
    3. フルタイム勤務の人が育児に週 15 時間使うと、残り時間は何時間ですか（基本生活時間 77 時間）。
    """,
    "tiny_code": '''
    # 【教員提供コード】F-1B の Tiny Dataset を読み込む
    tiny_work_options = load_csv(DATA_DIR / "f1b" / "work_options_tiny.csv",
                                 int_columns=["annual_income", "weekly_work_hours"])
    tiny_households = load_csv(DATA_DIR / "f1b" / "household_scenarios_tiny.csv",
                               int_columns=["living_cost", "childcare_cost", "eldercare_cost",
                                            "required_childcare_hours", "required_eldercare_hours"])
    tiny_work_by_id = {w["option_id"]: w for w in tiny_work_options}
    tiny_household_by_id = {h["scenario_id"]: h for h in tiny_households}
    print("勤務形態:", len(tiny_work_options), "件　世帯の条件:", len(tiny_households), "件")
    show_records(tiny_work_options)
    show_records(tiny_households, limit=5)


    def make_care_splits(required_hours, parts=6):
        """育児・介護の必要時間を、2 人で分担する候補を作る（教員提供。分担の割合を 0/6, 1/6, ..., 6/6 で変える）"""
        return [(required_hours * i / parts, required_hours * (parts - i) / parts) for i in range(parts + 1)]
    ''',
    "step2_intro": "**学習目標：** 辞書から値を取り出して、世帯の所得と支出を計算できる。",
    "step2": [
        {
            "title": "課題1：世帯の年間所得を計算する",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `household_income(option_a, option_b)` |
            | 引数 | `option_a`・`option_b`：2 人それぞれの勤務形態の辞書 |
            | 戻り値 | 2 人の年収の合計（万円／年） |
            | 例 | フルタイム（400）＋時短（280） → `680` |
            """,
            "stub": f'''
            # 【学生実装課題：Level 1】課題1
            def household_income(option_a, option_b):
                """2 人の勤務形態から、世帯の年間所得（万円／年）を返す。"""
                # TODO: 2 人の annual_income を足す。
                {STUB}
            ''',
            "hints": ("世帯の所得は、2 人の年収の合計です。",
                      "`option_a[\"annual_income\"]` で年収を読めます。",
                      "option_a の年収 + option_b の年収 を返す"),
            "check": '''
            # 【動作確認】
            W1, W2, W3 = work_options
            check("課題1：フルタイム＋時短", household_income, (W1, W2), 680)
            check("課題1：休業＋休業（所得 0）", household_income, (W3, W3), 0)
            ''',
        },
        {
            "title": "課題2：世帯の年間支出を計算する",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `household_expense(household)` |
            | 引数 | `household`：世帯の条件の辞書（`living_cost`・`childcare_cost`・`eldercare_cost`） |
            | 戻り値 | 生活費 + 育児費 + 介護費（万円／年） |
            | 例 | Mini Dataset の `household` → `420` |
            """,
            "stub": f'''
            # 【学生実装課題：Level 1】課題2
            def household_expense(household):
                """世帯の年間支出（生活費 + 育児費 + 介護費、万円／年）を返す。"""
                # TODO: 3 つの費用を足す。
                {STUB}
            ''',
            "hints": ("支出は 3 種類あります。すべてを足します。",
                      "辞書のキー `living_cost`・`childcare_cost`・`eldercare_cost`。",
                      "生活費 + 育児費 + 介護費 を返す"),
            "check": '''
            # 【動作確認】
            check("課題2：Mini Dataset の世帯", household_expense, (household,), 420)
            check("課題2：介護費がある世帯", household_expense,
                  ({"living_cost": 300, "childcare_cost": 0, "eldercare_cost": 90},), 390)
            ''',
        },
    ],
    "step3_intro": """
    **学習目標：** 課題1・2 を組み合わせて年間収支を求め、1 人ごとの時間の制約を確かめられる。

    > 赤字（マイナスの収支）や、時間が足りない（マイナスの残り時間）場合も、**0 に置き換えずに**そのまま返します。
    """,
    "step3": [
        {
            "title": "課題3：年間収支を計算する",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `annual_balance(option_a, option_b, household)` |
            | 引数 | 2 人の勤務形態の辞書と、世帯の条件の辞書 |
            | 戻り値 | 世帯の年間所得 − 世帯の年間支出（万円／年）。赤字ならマイナス |
            | 例 | フルタイム＋時短、Mini の世帯 → `680 − 420 = 260` |

            課題1・2 の関数を使います。
            """,
            "stub": f'''
            # 【学生実装課題：Level 1】課題3
            def annual_balance(option_a, option_b, household):
                """世帯の年間収支（所得 − 支出、万円／年）を返す。赤字はマイナスのまま返す。"""
                # TODO: 課題1 と課題2 の関数を使って、所得 − 支出 を計算する。
                {STUB}
            ''',
            "hints": ("収支 = 入ってくるお金 − 出ていくお金 です。",
                      "自分で作った関数 `household_income()` と `household_expense()` を呼び出します。",
                      "income ← household_income(option_a, option_b)\nexpense ← household_expense(household)\nincome − expense を返す"),
            "check": '''
            # 【動作確認】
            W1, W2, W3 = work_options
            check("課題3：フルタイム＋時短", annual_balance, (W1, W2, household), 260)
            check("課題3：時短＋休業（赤字）", annual_balance, (W2, W3, household), -140)
            ''',
        },
        {
            "title": "課題4：1 人の 1 週間の残り時間を計算する",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `free_hours(weekly_work_hours, weekly_care_hours, basic_hours)` |
            | 引数 | 労働時間（通勤を含む）・育児と介護の時間・基本生活時間（すべて 時間／週） |
            | 戻り値 | 168 − 基本生活時間 − 労働時間 − 育児と介護の時間（時間／週）。足りなければマイナス |
            | 例 | `free_hours(40, 15, 77)` → `36` |
            """,
            "stub": f'''
            # 【学生実装課題：Level 1】課題4
            def free_hours(weekly_work_hours, weekly_care_hours, basic_hours):
                """1 人の 1 週間の残り時間（時間／週）を返す。足りなければマイナスのまま返す。"""
                # TODO: 1 週間の時間（HOURS_PER_WEEK）から、使った時間を引く。
                {STUB}
            ''',
            "hints": ("1 週間は 168 時間です。使った時間をすべて引くと、残りの時間になります。",
                      "第5章の最初で定義した定数 `HOURS_PER_WEEK` を使います。基本生活時間は**引数**の値を使います。",
                      "HOURS_PER_WEEK − basic_hours − weekly_work_hours − weekly_care_hours を返す"),
            "check": '''
            # 【動作確認】
            check("課題4：フルタイム、育児 15 時間", free_hours, (40, 15, BASIC_HOURS), 36)
            check("課題4：休業、育児 30 時間", free_hours, (0, 30, BASIC_HOURS), 61)
            check("課題4：時間が足りない場合（マイナス）", free_hours, (40, 60, BASIC_HOURS), -9)
            check("課題4：基本生活時間を 70 に変えた場合", free_hours, (40, 15, 70), 43)
            ''',
        },
    ],
    "tiny_check": '''
    # 【動作確認】Tiny Dataset（境界条件）
    if tiny_households:
        W, H = tiny_work_by_id, tiny_household_by_id
        check("Tiny：全 25 世帯の年間支出", lambda hs: [household_expense(h) for h in hs], (tiny_households,),
              [440, 350, 430, 390, 470, 540, 390, 460, 390, 430, 550, 410, 480, 420, 490,
               360, 380, 530, 520, 420, 550, 380, 520, 1000, 500])
        check("Tiny：S24 は 2 人ともフルタイムでも赤字", annual_balance, (W["W1"], W["W1"], H["S24"]), -200)
        check("Tiny：S25 はフルタイムで 51 時間ずつ分担すると残り時間がちょうど 0", free_hours, (40, 51, BASIC_HOURS), 0)
    else:
        print("Tiny Dataset がないため、確認をスキップしました。")
    ''',
    "tiny_apply": '''
    # 【教員提供コード】Tiny Dataset の全世帯を、2 人ともフルタイム（W1）・育児介護を半分ずつ分担した場合で確かめる
    # 収支が赤字の世帯と、1 人の残り時間がマイナスになる（時間の制約に違反する）世帯を表示する
    if tiny_households and run_if_implemented(annual_balance, tiny_work_by_id["W1"], tiny_work_by_id["W1"], tiny_households[0]) is not None \\
            and run_if_implemented(free_hours, 40, 0, BASIC_HOURS) is not None:
        full = tiny_work_by_id["W1"]
        print("世帯  収支（万円/年）  1 人の残り時間（時間/週）  判定")
        for h in tiny_households:
            need = h["required_childcare_hours"] + h["required_eldercare_hours"]
            balance = annual_balance(full, full, h)
            free = free_hours(full["weekly_work_hours"], need / 2, BASIC_HOURS)
            problems = []
            if balance < 0:
                problems.append("赤字")
            if free < 0:
                problems.append("時間が足りない")
            print(f'{h["scenario_id"]}  {balance:>8}  {free:>8.1f}  {"、".join(problems) or "OK"}')
    ''',
    "viz": '''
    # 【教員提供コード】Mini Dataset：2 人とも同じ勤務形態の場合の世帯所得と支出（課題1・2 を実装すると表示される）
    names, incomes = [], []
    for option in work_options:
        value = run_if_implemented(household_income, option, option)
        if value is None:
            break
        names.append(option["option_id"] + "+" + option["option_id"])
        incomes.append(value)
    expense = run_if_implemented(household_expense, household)
    if incomes and expense is not None:
        plot_bars(names + [jp("支出", "expense")], incomes + [expense],
                  jp("世帯の年間所得と年間支出（人工データ）", "Household income and expense (synthetic)"),
                  jp("万円／年", "10k JPY / year"))
    ''',
    "step3_think": """
    1. Tiny Dataset で「赤字」になった世帯と「時間が足りない」世帯は、同じ世帯でしたか。
    2. 育児・介護の時間を半分ずつではなく、片方が多く担当すると、1 人ごとの残り時間はどう変わりますか。
    3. 基本生活時間（`BASIC_HOURS`）を 77 から変えると、判定はどう変わりますか。この値は誰がどう決めるべきでしょうか。
    """,
    "step4": """
    勤務形態の組合せと、育児・介護の分担の候補を**全探索**し、制約を満たすもの（実行可能な計画）を探して比べます。

    | 課題 | 関数 | アルゴリズム | 計算量 |
    | --- | --- | --- | --- |
    | 課題5 | `generate_work_pairs(options)` | 二重の for 文（全探索） | O(k²) |
    | 課題6 | `find_feasible_plans(work_pairs, household, care_splits, basic_hours, min_free_hours)` | 全探索 + 条件による絞り込み | O(k² × m) |
    | 課題7 | `rank_plans(plans, key)` | ソート（降順・安定） | O(P log P)（P は計画の数） |

    **実行可能な計画の条件**（課題6）

    1. 年間収支が 0 以上（年間所得 ≥ 年間支出）
    2. 分担した育児・介護の時間の合計 `care_a + care_b` が、世帯で必要な時間以上
    3. **2 人それぞれの**残り時間が `min_free_hours` 以上（`min_free_hours = 0` なら、1 人 168 時間の制約を守ること）
    """,
    "step4_tasks": [
        {
            "title": "課題5：勤務形態の組合せをすべて作る（全探索）",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `generate_work_pairs(options)` |
            | 引数 | `options`：勤務形態の辞書のリスト（k 件） |
            | 戻り値 | `(Adult A の勤務形態, Adult B の勤務形態)` のタプルのリスト（k × k 件）。A の順番 → B の順番で並べる |
            | 例 | 3 種類 → `(W1, W1), (W1, W2), (W1, W3), (W2, W1), ...` の 9 組 |

            同じ勤務形態どうし（W1 と W1）も、順番が逆の組（W1・W2 と W2・W1）も含めます（2 人は別の人なので）。
            """,
            "stub": f'''
            # 【学生実装課題：Level 2】課題5
            def generate_work_pairs(options):
                """2 人の勤務形態のすべての組合せ (a, b) のリストを返す。"""
                # TODO: 二重の for 文で、Adult A と Adult B の勤務形態の組をすべて作る。
                {STUB}
            ''',
            "hints": ("A の選び方が k 通り、それぞれについて B の選び方が k 通りあります。",
                      "for 文の中に for 文を書きます（入れ子）。タプルは `(a, b)`。",
                      "pairs ← 空のリスト\nfor a in options:\n    for b in options:\n        (a, b) を pairs に追加\npairs を返す"),
            "check": '''
            # 【動作確認】結果を ID の組にして確かめる
            ids = lambda opts: [(a["option_id"], b["option_id"]) for a, b in generate_work_pairs(opts)]
            check("課題5：3 種類 → 9 組", ids, (work_options,),
                  [("W1", "W1"), ("W1", "W2"), ("W1", "W3"), ("W2", "W1"), ("W2", "W2"), ("W2", "W3"),
                   ("W3", "W1"), ("W3", "W2"), ("W3", "W3")])
            check("課題5：1 種類 → 1 組", ids, (work_options[:1],), [("W1", "W1")])
            check("課題5：0 種類 → 0 組", generate_work_pairs, ([],), [])
            ''',
        },
        {
            "title": "課題6：制約を満たす計画を探す",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `find_feasible_plans(work_pairs, household, care_splits, basic_hours, min_free_hours)` |
            | 引数 | 課題5 の組合せ、世帯の辞書、分担の候補 `[(care_a, care_b), ...]`、基本生活時間、1 人の残り時間の下限 |
            | 戻り値 | 3 つの条件をすべて満たす計画の辞書のリスト（組合せの順 → 分担の候補の順） |

            計画の辞書のキー：`option_a`・`option_b`（勤務形態の ID）、`care_a`・`care_b`（育児・介護の時間）、
            `balance`（年間収支）、`free_a`・`free_b`（それぞれの残り時間）、`free_total`（2 人の残り時間の合計）

            課題3 の `annual_balance()` と課題4 の `free_hours()` を使います。
            """,
            "stub": f'''
            # 【学生実装課題：Level 2】課題6
            def find_feasible_plans(work_pairs, household, care_splits, basic_hours, min_free_hours):
                """収支・必要な育児介護時間・1 人ごとの残り時間の条件を満たす計画のリストを返す。"""
                # TODO: 世帯で必要な育児・介護の時間（2 種類の合計）を求める。
                # TODO: 各組合せ (a, b) について収支を計算し、赤字なら次の組合せへ。
                # TODO: 各分担 (care_a, care_b) について、合計が必要時間以上か、2 人の残り時間が下限以上かを確かめる。
                # TODO: すべて満たせば、計画の辞書をリストに追加する。
                {STUB}
            ''',
            "hints": ("組合せ（k² 通り）× 分担（m 通り）をすべて調べ、条件に合わないものを除きます。"
                      "1 人ごとの時間を別々に確かめることが大切です。",
                      "二重の for 文、`continue`（次のくり返しへ進む）、`and`、辞書の作成と `append()`。",
                      "required ← 必要な育児時間 + 必要な介護時間\nplans ← 空のリスト\nfor (a, b) in work_pairs:\n"
                      "    balance ← annual_balance(a, b, household)\n    もし balance < 0 なら continue\n"
                      "    for (care_a, care_b) in care_splits:\n        もし care_a + care_b < required なら continue\n"
                      "        free_a ← free_hours(a の労働時間, care_a, basic_hours)、free_b も同様\n"
                      "        もし free_a >= min_free_hours かつ free_b >= min_free_hours なら\n"
                      "            計画の辞書を plans に追加\nplans を返す"),
            "check": '''
            # 【動作確認】
            plans_35 = [
                {"option_a": "W1", "option_b": "W1", "care_a": 15, "care_b": 15, "balance": 380, "free_a": 36, "free_b": 36, "free_total": 72},
                {"option_a": "W1", "option_b": "W2", "care_a": 15, "care_b": 15, "balance": 260, "free_a": 36, "free_b": 48, "free_total": 84},
                {"option_a": "W1", "option_b": "W2", "care_a": 10, "care_b": 20, "balance": 260, "free_a": 41, "free_b": 43, "free_total": 84},
                {"option_a": "W2", "option_b": "W1", "care_a": 20, "care_b": 10, "balance": 260, "free_a": 43, "free_b": 41, "free_total": 84},
                {"option_a": "W2", "option_b": "W1", "care_a": 15, "care_b": 15, "balance": 260, "free_a": 48, "free_b": 36, "free_total": 84},
                {"option_a": "W2", "option_b": "W2", "care_a": 20, "care_b": 10, "balance": 140, "free_a": 43, "free_b": 53, "free_total": 96},
                {"option_a": "W2", "option_b": "W2", "care_a": 15, "care_b": 15, "balance": 140, "free_a": 48, "free_b": 48, "free_total": 96},
                {"option_a": "W2", "option_b": "W2", "care_a": 10, "care_b": 20, "balance": 140, "free_a": 53, "free_b": 43, "free_total": 96},
            ]
            W1, W2, W3 = work_options
            all_pairs = [(W1, W1), (W1, W2), (W1, W3), (W2, W1), (W2, W2), (W2, W3),
                         (W3, W1), (W3, W2), (W3, W3)]                     # 課題5 とは別に用意した入力
            check("課題6：残り時間の下限 35 時間", find_feasible_plans, (all_pairs, household, CARE_SPLITS, BASIC_HOURS, 35), plans_35)
            check("課題6：下限 60 時間（該当なし）", find_feasible_plans, (all_pairs, household, CARE_SPLITS, BASIC_HOURS, 60), [])
            check("課題6：合計が足りない分担 (10, 10) だけ（該当なし）", find_feasible_plans,
                  ([(W3, W3)], {**household, "living_cost": 0, "childcare_cost": 0}, [(10, 10)], BASIC_HOURS, 0), [])
            ''',
        },
        {
            "title": "課題7：実行可能な計画を指標で比べる（ソート）",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `rank_plans(plans, key)` |
            | 引数 | `plans`：課題6 の結果、`key`：並べる指標（`"balance"`、`"free_total"` など） |
            | 戻り値 | 指標の**大きい順**に並べた新しいリスト。値が同じなら元の順番を保つ |
            | 例 | `key="balance"` → 収支が最も大きい計画が先頭 |

            元のリスト `plans` の順番は変えないでください。挿入ソートを自分で書いても、`sorted()` を使ってもかまいません。
            """,
            "stub": f'''
            # 【学生実装課題：Level 2】課題7
            def rank_plans(plans, key):
                """指標 key の大きい順に並べた新しいリストを返す（同じ値なら元の順番）。"""
                # TODO: 元のリストを変えずに、key の大きい順に並べた新しいリストを作る。
                {STUB}
            ''',
            "hints": ("収支で並べた 1 位と、自由時間で並べた 1 位は、同じとは限りません。",
                      "`sorted(リスト, key=..., reverse=True)` は新しいリストを返し、同じ値の順番を保ちます。"
                      "`key=` には「1 つの計画から指標の値を取り出す関数」を渡します。",
                      "コピーを作る\nkey の値が大きい順に並べる（同じ値は元の順番のまま）\n並べたリストを返す"),
            "check": '''
            # 【動作確認】
            sample = [{"option_a": "W1", "option_b": "W1", "balance": 380, "free_total": 72},
                      {"option_a": "W1", "option_b": "W2", "balance": 260, "free_total": 84},
                      {"option_a": "W2", "option_b": "W1", "balance": 260, "free_total": 84},
                      {"option_a": "W2", "option_b": "W2", "balance": 140, "free_total": 96}]
            order = lambda p, k: [(x["option_a"], x["option_b"]) for x in rank_plans(p, k)]
            check("課題7：収支の大きい順", order, (sample, "balance"),
                  [("W1", "W1"), ("W1", "W2"), ("W2", "W1"), ("W2", "W2")])
            check("課題7：自由時間の大きい順（同じ値は元の順番）", order, (sample, "free_total"),
                  [("W2", "W2"), ("W1", "W2"), ("W2", "W1"), ("W1", "W1")])
            check("課題7：計画が 0 件", rank_plans, ([], "balance"), [])
            ''',
        },
    ],
    "step4_tiny_check": '''
    # 【動作確認】Tiny Dataset（Level 2）
    if tiny_households:
        W, H = tiny_work_by_id, tiny_household_by_id
        check("Tiny：6 種類 → 36 組", lambda opts: len(generate_work_pairs(opts)), (tiny_work_options,), 36)
        check("Tiny：S25 を 2 人ともフルタイムで（残り時間がちょうど 0 の計画だけ）", find_feasible_plans,
              ([(W["W1"], W["W1"])], H["S25"], make_care_splits(102), BASIC_HOURS, 0),
              [{"option_a": "W1", "option_b": "W1", "care_a": 51, "care_b": 51, "balance": 300,
                "free_a": 0, "free_b": 0, "free_total": 0}])
        all_pairs = run_if_implemented(generate_work_pairs, tiny_work_options)   # 課題5 の結果を使う
        if all_pairs is not None:
            for sid, expected in [("S01", 168), ("S23", 0), ("S24", 0), ("S25", 19)]:
                need = H[sid]["required_childcare_hours"] + H[sid]["required_eldercare_hours"]
                check(f"Tiny：{sid} の実行可能な計画の数（課題5 の組合せを使う）", lambda *a: len(find_feasible_plans(*a)),
                      (all_pairs, H[sid], make_care_splits(need), BASIC_HOURS, 0), expected)
    else:
        print("Tiny Dataset がないため、確認をスキップしました。")
    ''',
    "step4_extra": [
        ("""
        ### 収支が最大の計画と、自由時間が最大の計画を比べる
        """, '''
        # 【教員提供コード】Mini Dataset の実行可能な計画を、2 つの指標で並べる（課題5〜7 を実装すると表示される）
        pairs = run_if_implemented(generate_work_pairs, work_options)
        plans = run_if_implemented(find_feasible_plans, pairs, household, CARE_SPLITS, BASIC_HOURS, 35) if pairs else None
        if plans:
            for key, label in [("balance", "収支が最大"), ("free_total", "2 人の自由時間の合計が最大")]:
                ranked = run_if_implemented(rank_plans, plans, key)
                if ranked:
                    best = ranked[0]
                    print(f'{label}：{best["option_a"]}+{best["option_b"]}　分担 {best["care_a"]}/{best["care_b"]} 時間　'
                          f'収支 {best["balance"]} 万円　自由時間 {best["free_a"]}/{best["free_b"]} 時間')
            plot_scatter([(p["free_total"], p["balance"]) for p in plans],
                         jp("実行可能な計画の収支と自由時間（人工データ）", "Balance vs free time (synthetic)"),
                         jp("2 人の自由時間の合計（時間／週）", "free time (h/week)"), jp("年間収支（万円）", "balance (10k JPY)"))
        '''),
    ],
    "step4_think": """
    1. 収支が最大の計画と、自由時間が最大の計画は同じでしたか。どちらを選ぶかは、何によって決まりますか。
    2. 実行可能な計画が 0 件になった世帯（Tiny の S23・S24）には、どのような支援や選択肢が考えられますか（例：外部サービス）。
    3. 組合せの数は k² × m です。勤務形態が 10 種類、分担の候補が 11 通りなら、何通りを調べますか。
    """,
    "step5": """
    `data/f1b/household_expenses_small.csv` は、総務省統計局「家計調査（家計収支編）」2025 年の
    **二人以上の世帯**について、世帯主の年齢階級別の**1 世帯当たり 1 か月間**の消費支出（大分類）を取り出したものです。

    - 単位は**万円／月**です（世帯人員などは「人」）。この教材の年額（万円／年）と比べるには、**自分で 12 倍**します。
    - 平均値は、特定の家族の生活を表すものではありません。「教育」などの費目は、子どもがいない世帯も含めた平均です。
    - 生活時間（家事・育児の時間）の公開統計（総務省「社会生活基本調査」）は、今回の教材には含めていません。
      使う場合は、調査年・対象（個人か世帯か）・単位（1 日か 1 週間か）をそろえ、**仮想の世帯のパラメータ**として使います。
    - 出典：総務省統計局「家計調査（家計収支編）」2025 年（政府統計の総合窓口(e-Stat)、https://www.e-stat.go.jp/）を加工して作成。
    """,
    "small_code": small_loader("expense_small", "f1b/household_expenses_small.csv", ["survey_year"], ["value"],
                               "data/f1b/household_expenses_small.csv が配布物に含まれていない場合があります",
                               show_filter='r["category_code"] == "consumption_total"'),
    "step5_tasks": """
    次の中から、チームで関心のあるものを選びます（**完成コードは提供しません**）。

    1. **公開統計の利用**：Small Dataset の消費支出（月額 → 年額）を、世帯主の年齢階級ごとの生活費の目安として使う。
    2. **子どもの年齢に応じた支出**：子どもの年齢（0〜18 歳）ごとに育児費・必要時間が変わる複数年のシミュレーション。
    3. **育児休業と就業の継続**：休業する年数と復帰後の勤務形態を変え、複数年の収支を比べる。
    4. **外部の保育・介護サービス**：サービスを使うと費用が増え、必要な家族の時間が減るモデル。
    5. **所得と自由時間の両立**：2 つの指標の重み付きの評価や、どちらの指標でも他より悪くない計画（パレート最適）を探す。
    """,
    "discussion": """
    - 所得が最大の計画と、自由時間を重視した計画は同じでしたか。違う場合、何が違いを生みましたか。
    - 1 人の時間が 168 時間を超えてしまう計画はありましたか。2 人の合計だけを見ると、何を見落としますか。
    - モデルの限界：金額や時間で表せない家族の価値を、どのように考察に含めましたか。
    """,
    "team_features": """
    - 子どもの年齢に応じて育児費・育児時間が変わる 10 年間のシミュレーション
    - 外部サービスの利用（費用と時間の交換）を分担の候補に加えた全探索
    - 収支と自由時間の両方を考えた計画の比較（重み付き和、パレート最適）
    - 家計調査（Small Dataset）にもとづく生活費を使った収支の判定
    """,
}

# ======================================================================
# 第6章　F-1C
# ======================================================================
F1C = {
    "no": 6, "code": "F-1C", "title": "住宅取得・居住選択と長期家計設計",
    "english": "Housing Choice and Long-term Household Financial Planning",
    "summary": {
        "problem": "予算と通勤時間の条件を満たす住宅を探し、賃貸と購入の長期的な支出を比べる",
        "input": "住宅候補（購入価格、月額家賃、床面積、年間維持費、通勤時間）",
        "process": "年間家賃、累積家賃、購入費用＋維持費、線形探索、価格順のソート、二分探索による境界探索",
        "output": "条件を満たす住宅候補の一覧、賃貸と購入の累積支出の比較、線形探索と二分探索の比較",
        "image": "「予算 3,000 万円以下」の住宅を、線形探索と二分探索の両方で探し、同じ結果になることを確かめる",
    },
    "problem": """
    どこに、いつ、どのような住宅に住むかは、長期的な家計に大きく影響します。
    この章では、住宅候補のデータから**条件を満たす住宅を探す**プログラムと、
    **賃貸と購入の支出を長期的に比べる**プログラムを作ります。

    この章は、**線形探索（Linear Search）と二分探索（Binary Search）**を特に詳しく扱います。

    注意：
    - Mini・Tiny の価格・家賃・通勤時間は教材のための仮定値です。実際の物件や地域を表すものではありません。
    - 住宅の将来の価値には不確実性があります。持ち家と賃貸のどちらが良いかを決めるものではありません。
    """,
    "background": """
    | 用語 | この教材での意味 |
    | --- | --- |
    | 購入価格（`purchase_price`） | 住宅を買うときの価格（万円）。**1 回だけ**の支出 |
    | 月額家賃（`monthly_rent`） | 賃貸の 1 か月の家賃（万円／月）。年額は × 12 |
    | 年間維持費（`annual_maintenance_cost`） | 購入した場合の修繕・税などの費用（万円／年、仮定値） |
    | 比較期間 | 住む年数 `years`。賃貸と購入は**同じ年数**で比べる |
    | 累積住宅費 | 比較期間の住宅の支出の合計 |
    | 住宅資産価値 | 購入した住宅のその時点の価値。**支出とは別のもの**（Level 3） |

    - Level 1・2 では住宅ローン（借入と利息）を考えず、購入価格を最初に全額払うと単純化します。
      実際には利息の分だけ支出が増え、売却すればお金が戻るため、**この比較は購入の費用を正しく表していません**（モデルの限界）。
    - **住宅の購入費用の総額、毎年の現金の支出、住宅の資産価値を混同しない**ようにします。

    **探索アルゴリズム**

    | 処理 | 前提 | 計算量 |
    | --- | --- | --- |
    | 線形探索（予算以下をすべて集める） | なし（並び順はどうでもよい） | O(N) |
    | ソート（価格の安い順） | なし | O(N log N)（`sorted()`）、O(N²)（挿入ソート） |
    | 二分探索（予算以下の件数＝境界の位置を求める） | データが**価格の順にソート済み** | O(log N) |
    | 予算以下の K 件を取り出す | 境界の位置が分かっている | O(K) → 合計 O(log N + K) |

    - **1 回だけ**探すなら、ソートの O(N log N) を含めると線形探索 O(N) の方が速いこともあります。
    - **同じデータで Q 回**探すなら、線形探索は O(Q × N)、ソート 1 回 + 二分探索は O(N log N + Q × log N) です。
    - 予算以外の条件（通勤時間など）を加えると、二分探索で取り出した候補を、さらに 1 件ずつ調べる（追加の絞り込み）必要があります。
    """,
    "goals": """
    | レベル | STEP | 学習目標 | 学生実装課題 |
    | --- | --- | --- | --- |
    | Level 1 | STEP 1 | 住宅候補のデータの意味と単位（月額・年額・総額）を説明できる | ― |
    | Level 1 | STEP 2 | 月額・年額・累積額を区別して計算できる | 課題1 `annual_rent()`、課題2 `cumulative_rent()` |
    | Level 1 | STEP 3 | 購入の費用を計算し、条件を満たす候補を線形探索で探せる | 課題3 `ownership_cost()`、課題4 `find_candidates()` |
    | Level 2 | STEP 4 | ソートと二分探索で境界を見つけ、線形探索と結果を比べられる | 課題5 `sort_by_price()`、課題6 `count_affordable()`、課題7 `affordable_ids_binary()` |
    | Level 3 | STEP 5 | 公開データや住宅ローンなどで、チーム独自の機能を作れる | 6.9 から選ぶ |
    """,
    "data": """
    | Mini Dataset | Notebook の中の `housing_options` | 5 | 人工データ（仮定値。同じ価格 2 件） | 利用可 |
    | Tiny Dataset | `data/f1c/housing_options_tiny.csv` | 30 | 人工データ（3,000 万円ちょうどの物件 4 件、通勤 60 分超を含む） | 利用可 |
    | Small Dataset | `data/f1c/housing_prices_small.csv` | ― | 国土交通省「不動産情報ライブラリ」の不動産取引価格情報（教員が用意した場合だけ） | 未作成 |
    | Benchmark Dataset | プログラムの中で生成 | 可変 | 人工データ | 6.8・第8章 |
    """,
    "mini_code": '''
    # 【教員提供コード】F-1C の Mini Dataset（人工データ）
    # 単位：purchase_price 万円、monthly_rent 万円／月、floor_area ㎡、
    #       annual_maintenance_cost 万円／年、commute_minutes 分（片道）
    housing_options = [
        {"housing_id": "H01", "area": "地域A", "purchase_price": 2500, "monthly_rent": 10,
         "floor_area": 60, "annual_maintenance_cost": 20, "commute_minutes": 60},
        {"housing_id": "H02", "area": "地域B", "purchase_price": 3500, "monthly_rent": 13,
         "floor_area": 65, "annual_maintenance_cost": 25, "commute_minutes": 40},
        {"housing_id": "H03", "area": "地域C", "purchase_price": 4500, "monthly_rent": 16,
         "floor_area": 70, "annual_maintenance_cost": 30, "commute_minutes": 25},
        {"housing_id": "H04", "area": "地域D", "purchase_price": 3500, "monthly_rent": 12,
         "floor_area": 55, "annual_maintenance_cost": 25, "commute_minutes": 50},
        {"housing_id": "H05", "area": "地域E", "purchase_price": 2800, "monthly_rent": 11,
         "floor_area": 58, "annual_maintenance_cost": 20, "commute_minutes": 45},
    ]
    show_records(housing_options)
    ''',
    "mini_questions": """
    1. H01 を 1 年間借りると、家賃はいくらですか。
    2. 予算 3,500 万円以下の住宅はどれですか（価格が予算と**同じ**物件も含みます）。
    3. H02 と H04 は価格が同じです。価格の順に並べたとき、どちらを先にするかを決めるには、どのようなルールが必要ですか。
    """,
    "tiny_code": '''
    # 【教員提供コード】F-1C の Tiny Dataset を読み込む
    tiny_housing = load_csv(DATA_DIR / "f1c" / "housing_options_tiny.csv",
                            int_columns=["purchase_price", "floor_area", "annual_maintenance_cost", "commute_minutes"],
                            float_columns=["monthly_rent"])
    print("住宅候補:", len(tiny_housing), "件")
    show_records(tiny_housing, limit=5)
    ''',
    "step2_intro": "**学習目標：** 月額・年額・累積額を区別して計算できる。",
    "step2": [
        {
            "title": "課題1：月額家賃から年間家賃を計算する",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `annual_rent(monthly_rent)` |
            | 引数 | `monthly_rent`：月額家賃（万円／月） |
            | 戻り値 | 年間家賃（万円／年） |
            | 例 | `annual_rent(10)` → `120` |
            """,
            "stub": f'''
            # 【学生実装課題：Level 1】課題1
            def annual_rent(monthly_rent):
                """月額家賃（万円／月）から年間家賃（万円／年）を返す。"""
                # TODO: 1 年は 12 か月。
                {STUB}
            ''',
            "hints": ("1 年は 12 か月です。", "掛け算 `*`。", "monthly_rent × 12 を返す"),
            "check": '''
            # 【動作確認】
            check("課題1：月 10 万円", annual_rent, (10,), 120)
            check("課題1：月 12.5 万円", annual_rent, (12.5,), 150)
            ''',
        },
        {
            "title": "課題2：指定した年数の累積家賃を計算する",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `cumulative_rent(monthly_rent, years)` |
            | 引数 | `monthly_rent`：月額家賃（万円／月）、`years`：住む年数（整数） |
            | 戻り値 | `years` 年間の家賃の合計（万円）。0 年なら 0 |
            | 例 | `cumulative_rent(10, 3)` → `360` |

            Level 3 で「毎年家賃が上がる」場合に広げられるよう、**for 文で 1 年ずつ足す**形で書きましょう。課題1 を使います。
            """,
            "stub": f'''
            # 【学生実装課題：Level 1】課題2
            def cumulative_rent(monthly_rent, years):
                """years 年間の家賃の合計（万円）を返す。"""
                # TODO: 合計を 0 から始め、1 年ごとに年間家賃を足す。
                {STUB}
            ''',
            "hints": ("1 年目、2 年目、… と、毎年の家賃を合計に足していきます。",
                      "`for year in range(years):` と、課題1 の `annual_rent()`。",
                      "total ← 0\nyears 回くり返す:\n    total ← total + annual_rent(monthly_rent)\ntotal を返す"),
            "check": '''
            # 【動作確認】
            check("課題2：月 10 万円、3 年", cumulative_rent, (10, 3), 360)
            check("課題2：0 年", cumulative_rent, (10, 0), 0)
            ''',
        },
    ],
    "step3_intro": """
    **学習目標：** 購入した場合の費用を計算し、条件を満たす住宅を線形探索で探せる。
    """,
    "step3": [
        {
            "title": "課題3：購入した場合の費用を計算する",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `ownership_cost(option, years)` |
            | 引数 | `option`：住宅候補の辞書、`years`：住む年数（整数） |
            | 戻り値 | 購入価格 + 年間維持費 × 年数（万円） |
            | 例 | H01 に 10 年住む → `2500 + 20 × 10 = 2700` |

            ローン（借入）・住宅の売却価格・資産価値は、ここでは考えません。
            """,
            "stub": f'''
            # 【学生実装課題：Level 1】課題3
            def ownership_cost(option, years):
                """住宅を購入して years 年住む場合の費用の合計（万円）を返す（ローンは考えない）。"""
                # TODO: 購入価格に、年間維持費 × 年数 を足す。
                {STUB}
            ''',
            "hints": ("購入価格は最初に 1 回だけ、維持費は毎年かかります。",
                      "`option[\"purchase_price\"]` と `option[\"annual_maintenance_cost\"]`。",
                      "購入価格 + 年間維持費 × years を返す"),
            "check": '''
            # 【動作確認】
            H01 = housing_options[0]
            check("課題3：H01 に 10 年", ownership_cost, (H01, 10), 2700)
            check("課題3：H01 に 0 年（購入価格だけ）", ownership_cost, (H01, 0), 2500)
            ''',
        },
        {
            "title": "課題4：予算と通勤時間の条件を満たす住宅を探す（線形探索）",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `find_candidates(options, budget, max_commute)` |
            | 引数 | `options`：住宅候補のリスト、`budget`：予算（万円）、`max_commute`：通勤時間の上限（分） |
            | 戻り値 | 購入価格が予算**以下**、かつ通勤時間が上限**以下**の住宅の `housing_id` のリスト（入力と同じ順番） |
            | 例 | 予算 3500、通勤 50 分 → `["H02", "H04", "H05"]` |

            条件を満たす住宅がなければ、空のリスト `[]` を返します。
            """,
            "stub": f'''
            # 【学生実装課題：Level 1】課題4
            def find_candidates(options, budget, max_commute):
                """予算以下・通勤時間が上限以下の住宅の housing_id のリストを返す（線形探索）。"""
                # TODO: 先頭から 1 件ずつ調べ、2 つの条件を両方満たすものだけを集める。
                {STUB}
            ''',
            "hints": ("すべての候補を先頭から順に調べます（線形探索）。価格が予算と**同じ**ものも含みます。",
                      "`for option in options:`、`if 条件1 and 条件2:`、`<=`、`append()`。",
                      "result ← 空のリスト\nfor option in options:\n    もし 価格 <= budget かつ 通勤時間 <= max_commute なら\n        housing_id を result に追加\nresult を返す"),
            "check": '''
            # 【動作確認】
            check("課題4：予算 3500、通勤 50 分", find_candidates, (housing_options, 3500, 50), ["H02", "H04", "H05"])
            check("課題4：予算と価格が同じ（2500）", find_candidates, (housing_options, 2500, 60), ["H01"])
            check("課題4：該当なし", find_candidates, (housing_options, 2000, 60), [])
            check("課題4：候補が 0 件", find_candidates, ([], 3000, 60), [])
            ''',
        },
    ],
    "tiny_check": '''
    # 【動作確認】Tiny Dataset（境界条件）
    if tiny_housing:
        check("Tiny：予算 3000（ちょうど 3000 の物件を含む）・通勤 45 分", find_candidates, (tiny_housing, 3000, 45), ["H02"])
        check("Tiny：すべて予算超過（予算 1700）", find_candidates, (tiny_housing, 1700, 999), [])
        check("Tiny：すべて予算以内・通勤の制約なし", lambda *a: len(find_candidates(*a)), (tiny_housing, 5200, 999), 30)
        check("Tiny：予算 3000・通勤時間の制約なし", find_candidates, (tiny_housing, 3000, 999),
              ["H01", "H02", "H03", "H04", "H05", "H08", "H11", "H12", "H18", "H24", "H27"])
    else:
        print("Tiny Dataset がないため、確認をスキップしました。")
    ''',
    "tiny_apply": '''
    # 【教員提供コード】賃貸と購入の累積支出を、比較期間を変えて表にする（H02 の例。課題2・3 を実装すると表示される）
    H02 = housing_options[1]
    if run_if_implemented(cumulative_rent, H02["monthly_rent"], 1) is not None \\
            and run_if_implemented(ownership_cost, H02, 1) is not None:
        print("年数  賃貸の累積家賃  購入（ローンなし）の費用")
        for years in [0, 10, 20, 30, 40]:
            print(f"{years:>4}  {cumulative_rent(H02['monthly_rent'], years):>12,.0f}  {ownership_cost(H02, years):>12,.0f}")
    ''',
    "viz": '''
    # 【教員提供コード】Tiny Dataset の価格の分布と、価格と通勤時間の関係（課題4 を実装すると、条件を満たす住宅を赤で表示）
    BUDGET, MAX_COMMUTE = 3000, 45
    if tiny_housing:
        plot_hist([h["purchase_price"] for h in tiny_housing],
                  jp("住宅候補の価格の分布（人工データ）", "Price distribution (synthetic)"), jp("購入価格（万円）", "price (10k JPY)"), line=BUDGET)
        found = run_if_implemented(find_candidates, tiny_housing, BUDGET, MAX_COMMUTE) or []
        points = [(h["commute_minutes"], h["purchase_price"]) for h in tiny_housing]
        chosen = [(h["commute_minutes"], h["purchase_price"]) for h in tiny_housing if h["housing_id"] in found]
        plot_scatter(points, jp("通勤時間と価格（赤：予算 3,000・通勤 45 分以内）", "Commute vs price (red: selected)"),
                     jp("通勤時間（分）", "commute (min)"), jp("購入価格（万円）", "price (10k JPY)"), highlight=chosen)
    ''',
    "step3_think": """
    1. H02 では、何年住むと購入の費用が賃貸の累積家賃より小さくなりますか。この比較に含まれていないもの（売却価格、ローンの利息、家賃の値上がりなど）は、結果にどう影響しますか。
    2. 散布図で、通勤時間が短い住宅ほど価格が高い傾向はありますか。この傾向は、この教材で置いた**仮定**です。
    3. 課題4 の線形探索では、候補が N 件のとき何回比較しますか。
    """,
    "step4": """
    予算の条件だけで探す場合、住宅候補を**価格の順に並べておけば**、二分探索で「予算以下の物件が何件あるか（境界の位置）」を
    少ない比較の回数で求められます。

    | 課題 | 関数 | アルゴリズム | 計算量 |
    | --- | --- | --- | --- |
    | 課題5 | `sort_by_price(options)` | 挿入ソート（安定） | O(N²) |
    | 課題6 | `count_affordable(sorted_prices, budget)` | **二分探索**（upper bound） | O(log N) |
    | 課題7 | `affordable_ids_binary(sorted_options, budget)` | 二分探索 + 取り出し | O(N)（価格のリスト作り）+ O(log N) + O(K) |

    **境界の位置（upper bound）とは**：ソート済みの価格のリストで、「予算以下の物件がその前にすべて並んでいる位置」です。
    その位置の数は、予算以下の物件の**件数**と同じです。

    ```text
    価格:   [1800, 2200, 2200, 3000, 3000, 3300]     予算 3000
    位置:      0     1     2     3     4     5
                                         ↑ 境界の位置 = 5（予算以下は 5 件）
    ```
    """,
    "step4_tasks": [
        {
            "title": "課題5：住宅候補を価格の安い順に並べる（挿入ソート）",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `sort_by_price(options)` |
            | 引数 | `options`：住宅候補の辞書のリスト |
            | 戻り値 | `purchase_price` の**安い順**に並べた**新しいリスト** |

            - **同じ価格の物件は、元の順番を保ちます**（安定なソート）。例：H02 と H04 はどちらも 3500 → H02、H04 の順。
            - 元のリスト `options` は変えません。
            - この課題では、授業で学んだ**挿入ソートを自分で書きます**（`sorted()` は課題の後で比べるために使います）。
            """,
            "stub": f'''
            # 【学生実装課題：Level 2】課題5
            def sort_by_price(options):
                """購入価格の安い順に並べた新しいリストを返す（同じ価格は元の順番。挿入ソート）。"""
                # TODO: 元のリストのコピーを作る。
                # TODO: 挿入ソートで、purchase_price の安い順に並べる。同じ価格のときは動かさない。
                {STUB}
            ''',
            "hints": ("左側を「並べ終わった部分」とし、右から 1 件ずつ取り出して、正しい位置に差し込みます。"
                      "同じ価格の物件を追い越さないことが、元の順番を保つ（安定）ポイントです。",
                      "コピーは `list(options)`。while 文で、前の要素の価格が**大きい**間だけずらします（`>` を使い、`>=` は使わない）。",
                      "result ← options のコピー\nfor i in 1 から 最後まで:\n    tmp ← result[i]、j ← i\n"
                      "    j > 0 かつ result[j−1] の価格 > tmp の価格 の間:\n        result[j] ← result[j−1]、j ← j − 1\n"
                      "    result[j] ← tmp\nresult を返す"),
            "check": '''
            # 【動作確認】
            ids = lambda opts: [h["housing_id"] for h in sort_by_price(opts)]
            check("課題5：価格の安い順（H02 と H04 は同じ価格）", ids, (housing_options,), ["H01", "H05", "H02", "H04", "H03"])
            check("課題5：1 件だけ", ids, (housing_options[:1],), ["H01"])
            check("課題5：0 件", sort_by_price, ([],), [])
            ''',
        },
        {
            "title": "課題6：二分探索で予算以下の件数（境界の位置）を求める",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `count_affordable(sorted_prices, budget)` |
            | 引数 | `sorted_prices`：**安い順にソート済み**の価格（数値）のリスト、`budget`：予算（万円） |
            | 戻り値 | 予算**以下**の価格の件数（＝境界の位置、0〜N の整数） |
            | 例 | `count_affordable([2500, 2800, 3500, 3500, 4500], 3500)` → `4` |

            - **二分探索**で求めます（先頭から数えると O(N) になってしまいます）。
            - 空のリスト、1 件だけ、同じ価格が複数、予算と価格が等しい、すべて予算以内、すべて予算超過の場合も正しく動くようにします。
            """,
            "stub": f'''
            # 【学生実装課題：Level 2】課題6
            def count_affordable(sorted_prices, budget):
                """ソート済みの価格のリストで、budget 以下の件数（境界の位置）を二分探索で返す。"""
                # TODO: 探す範囲を left = 0、right = 件数 で始める（答えは left 以上 right 以下）。
                # TODO: 範囲が空になるまで、真ん中の価格と予算を比べて、範囲を半分にする。
                {STUB}
            ''',
            "hints": ("真ん中の価格が予算**以下**なら、答えはそれより右にあります。予算より**大きい**なら、答えは真ん中かそれより左です。"
                      "予算と同じ価格は「以下」に入るので、右へ進みます。",
                      "`while left < right:`、`mid = (left + right) // 2`、`if sorted_prices[mid] <= budget:`。",
                      "left ← 0、right ← 件数\nleft < right の間:\n    mid ← (left + right) // 2\n"
                      "    もし sorted_prices[mid] <= budget なら left ← mid + 1\n    そうでなければ right ← mid\nleft を返す"),
            "check": '''
            # 【動作確認】
            prices = [2500, 2800, 3500, 3500, 4500]
            check("課題6：同じ価格が複数・予算と価格が等しい", count_affordable, (prices, 3500), 4)
            check("課題6：予算が価格の間", count_affordable, (prices, 3000), 2)
            check("課題6：すべて予算以内", count_affordable, (prices, 9999), 5)
            check("課題6：すべて予算超過", count_affordable, (prices, 1000), 0)
            check("課題6：1 件だけ（予算と同じ）", count_affordable, ([3000], 3000), 1)
            check("課題6：1 件だけ（予算超過）", count_affordable, ([3000], 2999), 0)
            check("課題6：空のリスト", count_affordable, ([], 3000), 0)
            ''',
        },
        {
            "title": "課題7：二分探索で予算以下の住宅を取り出す",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `affordable_ids_binary(sorted_options, budget)` |
            | 引数 | `sorted_options`：課題5 で**価格の順に並べた**住宅候補のリスト、`budget`：予算（万円） |
            | 戻り値 | 予算以下の住宅の `housing_id` のリスト（価格の安い順） |
            | 例 | Mini を並べたリスト、予算 3500 → `["H01", "H05", "H02", "H04"]` |

            1. 価格だけのリストを作る。
            2. 課題6 の `count_affordable()` で境界の位置 k を求める（**境界の探索**）。
            3. 先頭から k 件の ID を取り出す（**候補の取り出し**）。

            課題4 の線形探索（通勤の条件を外したもの）と、**同じ住宅の集合**になるはずです（並び順は違います）。
            """,
            "stub": f'''
            # 【学生実装課題：Level 2】課題7
            def affordable_ids_binary(sorted_options, budget):
                """ソート済みの住宅候補から、予算以下の住宅の housing_id を価格の安い順に返す。"""
                # TODO: 価格だけのリストを作る。
                # TODO: count_affordable() で境界の位置 k を求める。
                # TODO: 先頭から k 件の housing_id をリストにして返す。
                {STUB}
            ''',
            "hints": ("境界の位置 k が分かれば、予算以下の住宅は「先頭から k 件」です。それ以降を調べる必要はありません。",
                      "for 文で価格のリストを作る、`count_affordable()`、スライス `sorted_options[:k]`。",
                      "prices ← sorted_options の各住宅の価格のリスト\nk ← count_affordable(prices, budget)\n"
                      "result ← 空のリスト\nfor option in sorted_options の先頭 k 件:\n    housing_id を result に追加\nresult を返す"),
            "check": '''
            # 【動作確認】課題5 とは別に、価格の順に並べた入力を用意して確かめる
            by_id = {h["housing_id"]: h for h in housing_options}
            sorted_mini = [by_id[i] for i in ["H01", "H05", "H02", "H04", "H03"]]
            check("課題7：予算 3500", affordable_ids_binary, (sorted_mini, 3500), ["H01", "H05", "H02", "H04"])
            check("課題7：予算 2499（該当なし）", affordable_ids_binary, (sorted_mini, 2499), [])
            check("課題7：予算 4500（すべて）", affordable_ids_binary, (sorted_mini, 4500), ["H01", "H05", "H02", "H04", "H03"])
            check("課題7：空のリスト", affordable_ids_binary, ([], 3000), [])
            ''',
        },
    ],
    "step4_tiny_check": '''
    # 【動作確認】Tiny Dataset（Level 2）
    if tiny_housing:
        check("Tiny：価格の順（同じ価格は元の順番）", lambda o: [h["housing_id"] for h in sort_by_price(o)], (tiny_housing,),
              ["H11", "H24", "H27", "H04", "H08", "H05", "H12", "H01", "H02", "H03", "H18", "H10", "H28", "H25", "H09",
               "H15", "H17", "H21", "H06", "H14", "H16", "H23", "H13", "H19", "H29", "H30", "H07", "H20", "H22", "H26"])
        tiny_prices = sorted(h["purchase_price"] for h in tiny_housing)   # 確認用に sorted() で用意した価格のリスト
        check("Tiny：予算 3000（3000 ちょうどが 4 件）", count_affordable, (tiny_prices, 3000), 11)
        check("Tiny：予算 2999", count_affordable, (tiny_prices, 2999), 7)
        check("Tiny：すべて予算以内（5200）", count_affordable, (tiny_prices, 5200), 30)
        check("Tiny：すべて予算超過（1700）", count_affordable, (tiny_prices, 1700), 0)
    else:
        print("Tiny Dataset がないため、確認をスキップしました。")
    ''',
    "step4_extra": [
        ("""
        ### 線形探索と二分探索の結果を比べる

        同じ入力と同じ予算で、線形探索（課題4。通勤の条件は外す）と二分探索（課題5〜7）が**同じ住宅の集合**を返すことを確かめます。
        並び順は違う（線形探索は入力の順、二分探索は価格の順）ので、集合（`set`）にして比べます。
        """, '''
        # 【教員提供コード】線形探索と二分探索の結果の比較（課題4〜7 を実装すると表示される）
        NO_LIMIT = 10 ** 9      # 通勤時間の条件を外すための大きな値
        sorted_tiny = run_if_implemented(sort_by_price, tiny_housing) if tiny_housing else None
        if sorted_tiny is not None and run_if_implemented(find_candidates, tiny_housing, 0, NO_LIMIT) is not None:
            for budget in [1700, 2999, 3000, 4000, 5200]:
                linear = find_candidates(tiny_housing, budget, NO_LIMIT)
                binary = run_if_implemented(affordable_ids_binary, sorted_tiny, budget)
                if binary is None:
                    break
                mark = "[OK] 同じ集合" if set(linear) == set(binary) else "[NG] 集合が違う"
                print(f"予算 {budget:>5}：線形探索 {len(linear):>2} 件、二分探索 {len(binary):>2} 件　{mark}")
        '''),
        ("""
        ### 1 回だけ探す場合と、何回も探す場合（実行時間の目安）

        Benchmark Dataset（人工の価格 N 件）を**メモリ上で作り**、Q 個の予算で探す時間を比べます。
        本格的な比較（件数を変えたグラフなど）は第8章で行います。
        """, '''
        # 【教員提供コード】線形探索（Q × N）と、ソート 1 回 + 二分探索（N log N + Q × log N）の比較
        def make_prices(n, seed=2026):
            rng = random.Random(seed)
            return [rng.randrange(1000, 8000, 10) for _ in range(n)]

        def count_linear(prices, budgets):         # 比較用：線形探索で件数を数える（教員提供）
            return [sum(1 for p in prices if p <= b) for b in budgets]

        def count_binary(prices, budgets):         # 比較用：ソート 1 回 + 課題6 の二分探索
            s = sorted(prices)
            return [count_affordable(s, b) for b in budgets]

        N = 5000
        prices_bench = make_prices(N)
        for Q in [1, 100]:
            budgets = make_prices(Q, seed=7)
            if run_if_implemented(count_affordable, [1, 2, 3], 2) is None:
                break
            same = count_linear(prices_bench, budgets) == count_binary(prices_bench, budgets)
            t_lin = measure_time(count_linear, (prices_bench, budgets), repeat=3)
            t_bin = measure_time(count_binary, (prices_bench, budgets), repeat=3)
            print(f"N = {N}、Q = {Q:>3}：線形探索 {t_lin:.5f} 秒、ソート + 二分探索 {t_bin:.5f} 秒　結果が同じ: {same}")
        '''),
    ],
    "step4_think": """
    1. 課題5 の挿入ソートと Python の `sorted()` の計算量の違いを説明してください。N が 10 倍になると、それぞれの時間はおよそ何倍になりますか。
    2. 1 回だけ探す場合と、100 回探す場合で、どちらの方法が有利でしたか。ソートの時間を含めて説明してください。
    3. 「予算以下、かつ通勤 45 分以内」を二分探索で求めるには、どのような追加の処理が必要ですか。その計算量は？
    """,
    "step5": """
    公開データ（国土交通省「不動産情報ライブラリ」の不動産取引価格情報）を使うと、実際の取引価格の分布で探索を試せます。

    - このデータは Web 画面の操作で取得するため、**教員が用意した場合だけ** `data/f1c/housing_prices_small.csv` があります。
    - 取引価格のデータには、**家賃や通勤時間は含まれていません**。それらを実測値のように追加しないでください。
      実データで探索するときは、**実際にある列**（取引価格、面積、取引時期など）だけで条件を作ります。
    - 人工の住宅候補（Tiny）と、実際の取引価格（Small）は、**別の種類のデータ**として扱います。
    - 出典を表示する場合の例：「出典：国土交通省　不動産情報ライブラリ（https://www.reinfolib.mlit.go.jp/）を加工して作成」
    """,
    "small_code": small_loader("prices_small", "f1c/housing_prices_small.csv", [], ["price", "floor_area"],
                               "教員が不動産情報ライブラリから取得した場合だけ用意されます"),
    "step5_tasks": """
    次の中から、チームで関心のあるものを選びます（**完成コードは提供しません**）。

    1. **実際の取引価格データの探索**：Small Dataset がある場合、価格の分布を調べ、二分探索で予算以下の件数を求める（実在する列だけを使う）。
    2. **賃貸と購入の長期比較**：家賃の値上がり、売却価格（残存価値）を入れて、比較期間ごとの差を調べる。
    3. **住宅ローンの返済シミュレーション**：元利均等返済（毎月の返済額が同じ）の式の意味を説明してから使い、残高を 1 か月ずつ更新する。
    4. **複数条件の探索**：予算・通勤時間・床面積を組み合わせた探索、条件の重み付けによる順位付け。
    5. **住宅を取得する時期の比較**：何年後に購入するか（その間は賃貸）を全探索する。
    """,
    "discussion": """
    - 線形探索と二分探索は、どのような場面でどちらが有利でしたか。ソートにかかる時間も含めて説明してください。
    - 賃貸と購入の比較で、結果が逆転する年数はどの仮定に敏感でしたか。
    - モデルの限界：住宅の価値の変化、金利、引っ越し、家族の変化などをどう考えますか。
    """,
    "team_features": """
    - 予算を何回も変えて探すための「ソート 1 回 + 二分探索」の検索機能と、線形探索との速度比較
    - 住宅ローンの返済額と残高の表（元利均等返済）
    - 賃貸と購入の累積支出が逆転する年数の探索（家賃の値上がり率を変えて）
    - 実際の取引価格データ（Small）を使った価格の分布と予算の関係のグラフ
    """,
}

# ======================================================================
# 第7章　F-1D
# ======================================================================
F1D = {
    "no": 7, "code": "F-1D", "title": "世代間資源継承と次世代の生活設計",
    "english": "Intergenerational Resource Transfer and Multigenerational Life Planning",
    "summary": {
        "problem": "親から子への資金の移転が、親子それぞれの資産の推移にどう影響するかを比べる",
        "input": "親子の年収・年間支出・初期資産、資金移転のシナリオ（毎年の移転額、移転期間）",
        "process": "1 年ごとの収支、資金の移転、資産残高の更新、シナリオの全探索、資産不足の年数の数え上げ",
        "output": "年ごとの親子の資産残高、親の最低生活資金を守れるシナリオの一覧",
        "image": "毎年の移転額が 0・50・100 万円のシナリオで、4 年間の親子の資産の推移を比べる",
    },
    "problem": """
    親の世代の選択や資源の使い方は、子の世代の生活にも影響します。
    教育資金、生活の支援、住宅、金融資産、事業などが、世代を越えて受け継がれます。

    この章では、まず**親子 2 人・資金の移転 1 種類**だけを扱い、
    毎年の収支と移転によって、親子それぞれの資産がどう変わるかをシミュレーションします。

    注意：
    - Mini・Tiny の金額は教材のための仮定値です。税金・相続制度・贈与の制度は扱いません。
    - 親から子への支援の「正しい額」を決めるものではありません。**親の生活を犠牲にして子への移転額を最大にすることを、唯一の正解とはしません。**
    """,
    "background": """
    | 用語 | この教材での意味 |
    | --- | --- |
    | 初期資産（`initial_assets`） | シミュレーションを始める時点の資産（万円）。`year = 0` に当たる |
    | 年間収支 | 年収 − 年間支出（万円／年）。資金の移転は含めない |
    | 資金の移転（`annual_transfer`） | 親の資産から子の資産へ、毎年移すお金（万円／年） |
    | 移転期間（`duration_years`） | 移転を続ける年数。1 年目から `duration_years` 年目まで移転する |
    | 年末の資産 | その年の終わりに持っているお金（万円）。**マイナスなら資産不足** |

    **この教材のルール（1 年の流れ）**

    ```text
    1. 親の資産 ← 親の資産 + 親の年間収支
       子の資産 ← 子の資産 + 子の年間収支
    2. 移転期間中（year ≤ duration_years）なら：親の資産 − 移転額、子の資産 + 移転額
    3. 年末の資産を記録する（year = 1, 2, ...）
    ```

    - 親から減った額と子に増えた額は**必ず同じ**です（お金が消えたり増えたりしない。合計は保存される）。
    - 家族全体の所得を計算するとき、家族の中の資金の移転を**新しい所得として二重に数えない**ようにします。
    - 資産がマイナスになっても 0 にしません。**マイナスは「お金が足りない状態」を表す教材上の記録**で、実際に借入ができることを意味しません。
    - T 年のシミュレーションは O(T)、S 個のシナリオなら O(S × T) です。
    """,
    "goals": """
    | レベル | STEP | 学習目標 | 学生実装課題 |
    | --- | --- | --- | --- |
    | Level 1 | STEP 1 | 家族と資金移転のデータの意味と単位を説明できる | ― |
    | Level 1 | STEP 2 | 年間収支と資金の移転を計算できる（合計が変わらないことを確かめる） | 課題1 `annual_balance_of()`、課題2 `transfer()` |
    | Level 1 | STEP 3 | 資産を 1 年ずつ更新するシミュレーションを作れる | 課題3 `update_assets()`、課題4 `simulate_transfer()` |
    | Level 2 | STEP 4 | 移転額と期間の組合せを全探索し、制約を満たすシナリオを探せる | 課題5 `generate_transfer_scenarios()`、課題6 `count_shortage_years()`、課題7 `find_feasible_transfers()` |
    | Level 3 | STEP 5 | 3 世代モデルや公開統計などで、チーム独自の機能を作れる | 7.9 から 1 つ選ぶ |
    """,
    "data": """
    | Mini Dataset | Notebook の中の `family`・`transfer_options` | 2 + 3 | 人工データ（仮定値） | 利用可 |
    | Tiny Dataset | `data/f1d/family_members_tiny.csv`、`data/f1d/transfer_scenarios_tiny.csv` | 24 + 32 | 人工データ（移転額 0、期間 0、赤字の親、資産不足を含む） | 利用可 |
    | Small Dataset | `data/f1d/household_assets_small.csv`、`data/f1d/learning_cost_small.csv` | 39 + 8 | 総務省「全国家計構造調査」令和6年、文部科学省「子供の学習費調査」令和5年度を加工 | 利用可 |
    | Benchmark Dataset | プログラムの中で生成 | 可変 | 人工データ | 第8章 |
    """,
    "mini_code": '''
    # 【教員提供コード】F-1D の Mini Dataset（人工データ。金額は万円、年齢は歳）
    family = [
        {"person_id": "P01", "family_id": "F00", "generation": 1, "role": "parent", "age": 45,
         "annual_income": 500, "annual_expense": 350, "initial_assets": 1000},
        {"person_id": "P02", "family_id": "F00", "generation": 2, "role": "child", "age": 18,
         "annual_income": 0, "annual_expense": 80, "initial_assets": 0},
    ]
    transfer_options = [
        {"annual_transfer": 0, "start_year": 1, "duration_years": 4},
        {"annual_transfer": 50, "start_year": 1, "duration_years": 4},
        {"annual_transfer": 100, "start_year": 1, "duration_years": 4},
    ]
    YEARS = 4                       # シミュレーションの年数。変えて試してよいパラメータ
    parent, child = family
    show_records(family)
    show_records(transfer_options)
    ''',
    "mini_questions": """
    1. 親と子の年間収支はそれぞれいくらですか。
    2. 移転額が 0 のとき、1 年後の子の資産はいくらですか。
    3. 移転額が 50 のとき、1 年後の親と子の資産の**合計**は、移転額が 0 のときと比べてどうなりますか。
    """,
    "tiny_code": '''
    # 【教員提供コード】F-1D の Tiny Dataset を読み込む
    tiny_members = load_csv(DATA_DIR / "f1d" / "family_members_tiny.csv",
                            int_columns=["generation", "age", "annual_income", "annual_expense", "initial_assets"])
    tiny_transfers = load_csv(DATA_DIR / "f1d" / "transfer_scenarios_tiny.csv",
                              int_columns=["annual_transfer", "start_year", "duration_years"])
    tiny_person_by_id = {m["person_id"]: m for m in tiny_members}
    print("家族の構成員:", len(tiny_members), "人　資金移転のシナリオ:", len(tiny_transfers), "件")
    show_records(tiny_members, limit=4)
    show_records(tiny_transfers, limit=4)
    # Level 1・2 では、1 年目から移転するシナリオ（start_year = 1）だけを使う。start_year = 3 は Level 3 用
    tiny_transfers_from_year1 = [t for t in tiny_transfers if t["start_year"] == 1]
    ''',
    "step2_intro": "**学習目標：** 1 人の年間収支と、親から子への資金の移転を計算できる。",
    "step2": [
        {
            "title": "課題1：1 人の年間収支を計算する",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `annual_balance_of(person)` |
            | 引数 | `person`：家族の 1 人の辞書（`annual_income`・`annual_expense`） |
            | 戻り値 | 年収 − 年間支出（万円／年）。マイナスならそのまま |
            | 例 | 親 → `150`、子 → `-80` |
            """,
            "stub": f'''
            # 【学生実装課題：Level 1】課題1
            def annual_balance_of(person):
                """1 人の年間収支（年収 − 年間支出、万円／年）を返す。"""
                # TODO: 年収から年間支出を引く。
                {STUB}
            ''',
            "hints": ("収支 = 入ってくるお金 − 出ていくお金。",
                      "`person[\"annual_income\"]` と `person[\"annual_expense\"]`。",
                      "年収 − 年間支出 を返す"),
            "check": '''
            # 【動作確認】
            check("課題1：親", annual_balance_of, (parent,), 150)
            check("課題1：子（マイナス）", annual_balance_of, (child,), -80)
            ''',
        },
        {
            "title": "課題2：親から子へ資金を移転する",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `transfer(parent_assets, child_assets, amount)` |
            | 引数 | 親の資産、子の資産、移転額（すべて万円） |
            | 戻り値 | 移転後の `(親の資産, 子の資産)` の**タプル** |
            | 例 | `transfer(1000, 0, 50)` → `(950, 50)` |

            親から減った額と、子に増えた額が同じになるようにします（合計は変わらない）。
            """,
            "stub": f'''
            # 【学生実装課題：Level 1】課題2
            def transfer(parent_assets, child_assets, amount):
                """親から子へ amount を移した後の (親の資産, 子の資産) を返す。"""
                # TODO: 親の資産から amount を引き、子の資産に amount を足す。
                {STUB}
            ''',
            "hints": ("お金は移動するだけで、消えたり増えたりしません。",
                      "2 つの値をまとめて返すには、タプル `return a, b` を使います。",
                      "new_parent ← parent_assets − amount\nnew_child ← child_assets + amount\n(new_parent, new_child) を返す"),
            "check": '''
            # 【動作確認】
            check("課題2：50 万円を移転", transfer, (1000, 0, 50), (950, 50))
            check("課題2：移転額が 0", transfer, (1000, 0, 0), (1000, 0))
            check("課題2：親の資産より多く移転（マイナスのまま）", transfer, (30, 0, 50), (-20, 50))
            check("課題2：移転の前後で合計が同じ", lambda p, c, a: sum(transfer(p, c, a)), (1000, 200, 150), 1200)
            ''',
        },
    ],
    "step3_intro": """
    **学習目標：** 1 年ずつ資産を更新し、年ごとの資産残高を記録するシミュレーションを作れる。

    > 年の終わりの資産を記録します。1 年目の終わりが `year = 1` です。資産不足（マイナス）は 0 に置き換えません。
    """,
    "step3": [
        {
            "title": "課題3：1 年分の資産を更新する",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `update_assets(assets, annual_income, annual_expense)` |
            | 引数 | 年の初めの資産、年収、年間支出（すべて万円） |
            | 戻り値 | 年の終わりの資産（万円）（資金の移転は含めない） |
            | 例 | `update_assets(0, 0, 80)` → `-80` |
            """,
            "stub": f'''
            # 【学生実装課題：Level 1】課題3
            def update_assets(assets, annual_income, annual_expense):
                """1 年分の収支を反映した、年の終わりの資産（万円）を返す。"""
                # TODO: 年の初めの資産に、その年の収支を足す。
                {STUB}
            ''',
            "hints": ("年の終わりの資産 = 年の初めの資産 + その年の収支。",
                      "足し算と引き算だけで書けます。",
                      "assets + annual_income − annual_expense を返す"),
            "check": '''
            # 【動作確認】
            check("課題3：親の 1 年目", update_assets, (1000, 500, 350), 1150)
            check("課題3：子の 1 年目（資産不足）", update_assets, (0, 0, 80), -80)
            ''',
        },
        {
            "title": "課題4：親子の資産の推移をシミュレーションする",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `simulate_transfer(parent, child, annual_transfer, duration_years, years)` |
            | 引数 | 親と子の辞書、毎年の移転額（万円／年）、移転期間（年）、シミュレーションの年数（年） |
            | 戻り値 | 年ごとの辞書 `{"year": 年, "parent_assets": 親の資産, "child_assets": 子の資産}` のリスト |
            | 例 | 移転額 50、期間 2、2 年 → `[{"year": 1, "parent_assets": 1100, "child_assets": -30}, {"year": 2, "parent_assets": 1200, "child_assets": -60}]` |

            - 資産の初期値は、辞書の `initial_assets` を使います。**辞書そのものは書き換えません。**
            - 1 年の流れ：課題3 で収支を反映 → **移転期間中なら**課題2 で移転する（`year <= duration_years`）。
            - 年数が 0 なら、空のリストを返します。移転期間が 0 なら、移転しません。
            """,
            "stub": f'''
            # 【学生実装課題：Level 1】課題4
            def simulate_transfer(parent, child, annual_transfer, duration_years, years):
                """親子の資産の推移（年の終わりの資産）を、年ごとの辞書のリストで返す。"""
                # TODO: 親と子の資産を、それぞれの辞書の "initial_assets" から変数にコピーする。
                # TODO: 1 年目から years 年目まで、収支の反映（課題3）をくり返す。
                # TODO: 移転期間中（year <= duration_years）の年だけ、移転（課題2）をする。
                # TODO: 毎年の終わりに {{"year": ..., "parent_assets": ..., "child_assets": ...}} を記録する。
                {STUB}
            ''',
            "hints": ("年の初めの資産を変数に入れ、for 文で 1 年ずつ更新し、そのたびに記録します。移転は if 文で期間中だけ行います。",
                      "`for year in range(1, years + 1):`、`if year <= duration_years:`、課題2 のタプルは `p, c = transfer(...)` で受け取れます。",
                      "p ← parent の initial_assets、c ← child の initial_assets\nhistory ← 空のリスト\n"
                      "for year in 1 から years まで:\n    p ← update_assets(p, 親の年収, 親の支出)\n"
                      "    c ← update_assets(c, 子の年収, 子の支出)\n    もし year <= duration_years なら p, c ← transfer(p, c, annual_transfer)\n"
                      "    {year, parent_assets: p, child_assets: c} を history に追加\nhistory を返す"),
            "check": '''
            # 【動作確認】
            check("課題4：移転額 50、期間 2、2 年", simulate_transfer, (parent, child, 50, 2, 2),
                  [{"year": 1, "parent_assets": 1100, "child_assets": -30},
                   {"year": 2, "parent_assets": 1200, "child_assets": -60}])
            check("課題4：移転額 100、期間 1、3 年（2 年目からは移転しない）", simulate_transfer, (parent, child, 100, 1, 3),
                  [{"year": 1, "parent_assets": 1050, "child_assets": 20},
                   {"year": 2, "parent_assets": 1200, "child_assets": -60},
                   {"year": 3, "parent_assets": 1350, "child_assets": -140}])
            check("課題4：移転期間 0（移転しない）", simulate_transfer, (parent, child, 50, 0, 2),
                  [{"year": 1, "parent_assets": 1150, "child_assets": -80},
                   {"year": 2, "parent_assets": 1300, "child_assets": -160}])
            check("課題4：0 年", simulate_transfer, (parent, child, 50, 2, 0), [])
            ''',
        },
    ],
    "tiny_check": '''
    # 【動作確認】Tiny Dataset（境界条件）
    if tiny_members:
        P = tiny_person_by_id
        check("Tiny：F03 の親は赤字（収支 −10）", annual_balance_of, (P["F03-P"],), -10)
        check("Tiny：F01 の親子、移転額 100、期間 2、3 年", simulate_transfer, (P["F01-P"], P["F01-C"], 100, 2, 3),
              [{"year": 1, "parent_assets": 2920, "child_assets": 110},
               {"year": 2, "parent_assets": 2940, "child_assets": 80},
               {"year": 3, "parent_assets": 3060, "child_assets": -50}])
        check("Tiny：移転額 150 でも合計は移転額 0 と同じ（F01、6 年後）",
              lambda p, c: [h["parent_assets"] + h["child_assets"] for h in simulate_transfer(p, c, 150, 6, 6)][-1],
              (P["F01-P"], P["F01-C"]), 2980)
    else:
        print("Tiny Dataset がないため、確認をスキップしました。")
    ''',
    "tiny_apply": '''
    # 【教員提供コード】Mini Dataset の 3 つの移転シナリオで、YEARS 年後の資産を比べる（課題4 を実装すると表示される）
    for option in transfer_options:
        history = run_if_implemented(simulate_transfer, parent, child, option["annual_transfer"], option["duration_years"], YEARS)
        if not history:
            break
        last = history[-1]
        total = last["parent_assets"] + last["child_assets"]
        print(f'移転額 {option["annual_transfer"]:>3} 万円／年：親 {last["parent_assets"]:>6}　子 {last["child_assets"]:>5}　合計 {total}')
    ''',
    "viz": '''
    # 【教員提供コード】親子の年次資産残高（移転額 100・期間 4 年の例。課題4 を実装すると表示される）
    history = run_if_implemented(simulate_transfer, parent, child, 100, 4, 8)
    if history:
        years = [h["year"] for h in history]
        plot_lines(years, {jp("親", "parent"): [h["parent_assets"] for h in history],
                           jp("子", "child"): [h["child_assets"] for h in history]},
                   jp("親子の年末の資産（移転額 100、期間 4 年、人工データ）", "Assets of parent and child (synthetic)"),
                   jp("年", "year"), jp("万円", "10k JPY"))
    ''',
    "step3_think": """
    1. 3 つのシナリオで、4 年後の親子の資産の**合計**は同じですか。それはなぜですか。
    2. 子の資産がマイナスになるのは、どのシナリオの何年目ですか。マイナスを 0 に置き換えると、何が分からなくなりますか。
    3. 移転期間が終わった後（グラフの 5 年目以降）、子の資産はどう変わりますか。
    """,
    "step4": """
    移転額と移転期間の組合せ（シナリオ）を**全探索**し、親の最低生活資金を守れるシナリオを探して比べます。

    | 課題 | 関数 | アルゴリズム | 計算量 |
    | --- | --- | --- | --- |
    | 課題5 | `generate_transfer_scenarios(amounts, durations)` | 二重の for 文（全探索） | O(額の数 × 期間の数) |
    | 課題6 | `count_shortage_years(history, key, min_assets)` | 線形探索・数え上げ | O(T) |
    | 課題7 | `find_feasible_transfers(parent, child, scenarios, years, parent_min_assets)` | 全探索 + 条件による絞り込み | O(S × T) |

    - 親の**最低生活資金**（`parent_min_assets`）：親の年末の資産がこの額を 1 年でも下回るシナリオは選ばない、という制約です（値は仮定）。
    - 子への移転額が大きいシナリオほど良い、とは限りません。親の生活と子の生活の両方を見て比べます。
    """,
    "step4_tasks": [
        {
            "title": "課題5：移転額と期間の組合せをすべて作る（全探索）",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `generate_transfer_scenarios(amounts, durations)` |
            | 引数 | `amounts`：移転額の候補のリスト、`durations`：移転期間の候補のリスト |
            | 戻り値 | `{"annual_transfer": 額, "duration_years": 期間}` の辞書のリスト（額の順 → 期間の順） |
            | 例 | `([0, 50], [2, 4])` → 0・2、0・4、50・2、50・4 の 4 件 |
            """,
            "stub": f'''
            # 【学生実装課題：Level 2】課題5
            def generate_transfer_scenarios(amounts, durations):
                """移転額と移転期間のすべての組合せを、辞書のリストで返す。"""
                # TODO: 二重の for 文で、すべての (額, 期間) の組を辞書にして追加する。
                {STUB}
            ''',
            "hints": ("額の候補が a 個、期間の候補が d 個なら、組合せは a × d 個です。",
                      "for 文の中に for 文を書きます。辞書 `{\"annual_transfer\": ..., \"duration_years\": ...}`。",
                      "scenarios ← 空のリスト\nfor amount in amounts:\n    for duration in durations:\n        {annual_transfer: amount, duration_years: duration} を追加\nscenarios を返す"),
            "check": '''
            # 【動作確認】
            check("課題5：2 × 2 = 4 件", generate_transfer_scenarios, ([0, 50], [2, 4]),
                  [{"annual_transfer": 0, "duration_years": 2}, {"annual_transfer": 0, "duration_years": 4},
                   {"annual_transfer": 50, "duration_years": 2}, {"annual_transfer": 50, "duration_years": 4}])
            check("課題5：期間 0 を含む", generate_transfer_scenarios, ([100], [0]), [{"annual_transfer": 100, "duration_years": 0}])
            check("課題5：候補が空", generate_transfer_scenarios, ([], [2, 4]), [])
            ''',
        },
        {
            "title": "課題6：資産不足の年数を数える",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `count_shortage_years(history, key, min_assets)` |
            | 引数 | `history`：課題4 の結果の形のリスト、`key`：`"parent_assets"` か `"child_assets"`、`min_assets`：下限（万円） |
            | 戻り値 | `key` の資産が `min_assets` **より小さい**年の数（整数） |
            | 例 | 子の資産が [-30, -60] で下限 0 → `2` |

            資産がマイナスの年も、隠さずに数えます。
            """,
            "stub": f'''
            # 【学生実装課題：Level 2】課題6
            def count_shortage_years(history, key, min_assets):
                """key の資産が min_assets より小さい年の数を返す。"""
                # TODO: 年ごとの記録を 1 件ずつ調べ、条件に合う年を数える。
                {STUB}
            ''',
            "hints": ("下限と**同じ**額の年は、不足に入れません（「より小さい」だけを数える）。",
                      "`for row in history:`、`if row[key] < min_assets:`、カウンタ変数。",
                      "count ← 0\nfor row in history:\n    もし row[key] < min_assets なら count ← count + 1\ncount を返す"),
            "check": '''
            # 【動作確認】
            hist = [{"year": 1, "parent_assets": 1050, "child_assets": 20},
                    {"year": 2, "parent_assets": 1100, "child_assets": -60},
                    {"year": 3, "parent_assets": 1000, "child_assets": -140}]
            check("課題6：子の資産不足（下限 0）", count_shortage_years, (hist, "child_assets", 0), 2)
            check("課題6：親が下限 1100 を下回る年（1100 ちょうどは数えない）", count_shortage_years, (hist, "parent_assets", 1100), 2)
            check("課題6：記録が 0 年", count_shortage_years, ([], "child_assets", 0), 0)
            ''',
        },
        {
            "title": "課題7：親の最低生活資金を守れるシナリオを探す",
            "explain": """
            | 項目 | 内容 |
            | --- | --- |
            | 関数 | `find_feasible_transfers(parent, child, scenarios, years, parent_min_assets)` |
            | 引数 | 親と子の辞書、課題5 の形のシナリオのリスト、シミュレーションの年数、親の最低生活資金（万円） |
            | 戻り値 | 親の資産が**1 年も**下限を下回らないシナリオについての辞書のリスト（シナリオの順） |

            結果の辞書のキー：`annual_transfer`・`duration_years`、`parent_final_assets`・`child_final_assets`（最後の年の資産）、
            `child_shortage_years`（子の資産がマイナスの年の数）

            - 課題4 の `simulate_transfer()` と課題6 の `count_shortage_years()` を使います。
            - 年数が 0 の場合は、初期資産を「最後の資産」とします。
            """,
            "stub": f'''
            # 【学生実装課題：Level 2】課題7
            def find_feasible_transfers(parent, child, scenarios, years, parent_min_assets):
                """親の資産が下限を下回らないシナリオについて、最後の資産と子の資産不足の年数を返す。"""
                # TODO: 各シナリオを simulate_transfer() でシミュレーションする。
                # TODO: 親の資産が下限を下回る年が 1 年でもあれば、そのシナリオは除く。
                # TODO: 残ったシナリオについて、最後の年の資産と、子の資産不足の年数を辞書にして追加する。
                {STUB}
            ''',
            "hints": ("全探索です。シナリオを 1 つずつシミュレーションし、条件（制約）に合わないものを除きます。",
                      "`for s in scenarios:`、`continue`、`history[-1]`（最後の要素）、空のリストの判定 `if history:`。",
                      "result ← 空のリスト\nfor s in scenarios:\n    history ← simulate_transfer(parent, child, s の移転額, s の期間, years)\n"
                      "    もし count_shortage_years(history, \"parent_assets\", parent_min_assets) > 0 なら continue\n"
                      "    last ← history の最後（空なら初期資産）\n    {移転額, 期間, 親の最後の資産, 子の最後の資産, 子の不足年数} を追加\nresult を返す"),
            "check": '''
            # 【動作確認】Mini の親子、4 年、親の最低生活資金 1100 万円
            scenarios = [{"annual_transfer": 0, "duration_years": 0}, {"annual_transfer": 0, "duration_years": 4},
                         {"annual_transfer": 50, "duration_years": 0}, {"annual_transfer": 50, "duration_years": 4},
                         {"annual_transfer": 100, "duration_years": 0}, {"annual_transfer": 100, "duration_years": 4}]
            expected = [
                {"annual_transfer": 0, "duration_years": 0, "parent_final_assets": 1600, "child_final_assets": -320, "child_shortage_years": 4},
                {"annual_transfer": 0, "duration_years": 4, "parent_final_assets": 1600, "child_final_assets": -320, "child_shortage_years": 4},
                {"annual_transfer": 50, "duration_years": 0, "parent_final_assets": 1600, "child_final_assets": -320, "child_shortage_years": 4},
                {"annual_transfer": 50, "duration_years": 4, "parent_final_assets": 1400, "child_final_assets": -120, "child_shortage_years": 4},
                {"annual_transfer": 100, "duration_years": 0, "parent_final_assets": 1600, "child_final_assets": -320, "child_shortage_years": 4},
            ]
            check("課題7：下限 1100（移転額 100・期間 4 は 1 年目に 1050 になるので除く）", find_feasible_transfers,
                  (parent, child, scenarios, 4, 1100), expected)
            check("課題7：下限が高すぎる（該当なし）", find_feasible_transfers, (parent, child, scenarios, 4, 5000), [])
            check("課題7：0 年（初期資産のまま）", find_feasible_transfers, (parent, child, scenarios[:1], 0, 0),
                  [{"annual_transfer": 0, "duration_years": 0, "parent_final_assets": 1000, "child_final_assets": 0, "child_shortage_years": 0}])
            ''',
        },
    ],
    "step4_tiny_check": '''
    # 【動作確認】Tiny Dataset（Level 2）
    if tiny_members:
        P = tiny_person_by_id
        check("Tiny：F03 は親が赤字で初期資産 600（下限 1000 を守れるシナリオなし）", find_feasible_transfers,
              (P["F03-P"], P["F03-C"], tiny_transfers_from_year1, 6, 1000), [])
        check("Tiny：F02 はすべてのシナリオ（16 件）で下限 1000 を守れる",
              lambda *a: len(find_feasible_transfers(*a)), (P["F02-P"], P["F02-C"], tiny_transfers_from_year1, 6, 1000), 16)
        check("Tiny：F04 の 6 年後、子の資産不足がなくなるシナリオ",
              lambda *a: [(r["annual_transfer"], r["duration_years"]) for r in find_feasible_transfers(*a) if r["child_shortage_years"] == 0],
              (P["F04-P"], P["F04-C"], tiny_transfers_from_year1, 6, 1000), [(100, 6), (150, 4)])
        check("Tiny：F01 の子の資産不足の年数（移転なし、6 年）", count_shortage_years,
              ([{"year": y, "child_assets": 140 - 130 * y} for y in range(1, 7)], "child_assets", 0), 5)
    else:
        print("Tiny Dataset がないため、確認をスキップしました。")
    ''',
    "step4_extra": [
        ("""
        ### 子の最後の資産で比べる（親の制約を守れるシナリオだけ）
        """, '''
        # 【教員提供コード】Tiny の F04 家族で、親の最低生活資金 1000 万円を守れるシナリオを、子の最後の資産の大きい順に表示する
        if tiny_members:
            P = tiny_person_by_id
            found = run_if_implemented(find_feasible_transfers, P["F04-P"], P["F04-C"], tiny_transfers_from_year1, 6, 1000)
            if found is not None:
                print("制約を守れるシナリオ:", len(found), "件 / 全", len(tiny_transfers_from_year1), "件")
                for r in sorted(found, key=lambda r: r["child_final_assets"], reverse=True)[:5]:
                    print(f'移転額 {r["annual_transfer"]:>3}・期間 {r["duration_years"]} 年：親 {r["parent_final_assets"]:>5}　'
                          f'子 {r["child_final_assets"]:>5}　子の資産不足 {r["child_shortage_years"]} 年')
        '''),
    ],
    "step4_think": """
    1. 親の最低生活資金の下限を上げると、選べるシナリオはどう変わりますか。
    2. 「子の最後の資産が最大」のシナリオと、「親の最後の資産が最大」のシナリオは、それぞれどれですか。どちらを選ぶべきかは、何によって決まりますか。
    3. シナリオの数（S）と年数（T）を 2 倍にすると、計算の回数はおよそ何倍になりますか。
    """,
    "step5": """
    実際の複数世代の家族を追跡した個人データは使いません。公開された**集計統計**を、**仮想の家族のパラメータ**として使います。

    | ファイル | 内容 | 単位 |
    | --- | --- | --- |
    | `household_assets_small.csv` | 総務省「令和6年全国家計構造調査」：世帯主の年齢階級別の 1 世帯当たりの金融資産残高（貯蓄）・金融負債残高・住宅・宅地資産額 | 万円 |
    | `learning_cost_small.csv` | 文部科学省「令和5年度子供の学習費調査」：学校種別（公立・私立）の子供 1 人当たりの年間の学習費 | 万円／年 |

    - 資産の**平均値**は、少数の大きな資産を持つ世帯の影響を受けて大きくなりがちです。典型的な世帯の値とは限りません。
    - 純資産（資産 − 負債）は**自分で計算**します。
    - 「教育費をかけると子の将来の所得が増える」モデルを作る場合、その関係は**教材上の仮定**であることを明記します。統計で見られる相関関係を、因果関係として扱わないでください。
    - 税金・相続制度・事業の評価などの複雑な制度は、基本課題では扱いません。
    - 出典：総務省統計局「令和6年全国家計構造調査」、文部科学省「令和5年度子供の学習費調査」（政府統計の総合窓口(e-Stat)、https://www.e-stat.go.jp/）を加工して作成。
    """,
    "small_code": small_loader("assets_small", "f1d/household_assets_small.csv", ["survey_year"],
                               ["head_mean_age", "household_size", "financial_assets", "financial_liabilities",
                                "housing_land_assets"],
                               "data/f1d/household_assets_small.csv が配布物に含まれていない場合があります",
                               show_filter='r["household_type_code"] == "two_or_more"') + '''

    learning_path = DATA_DIR / "f1d" / "learning_cost_small.csv"
    learning_small = load_csv(learning_path, float_columns=["total_cost", "school_education_cost", "school_lunch_cost",
                                                            "out_of_school_cost"]) if learning_path.exists() else []
    show_records(learning_small)
    ''',
    "step5_tasks": """
    次のうち、チームで関心のある **1 つ**を選んで発展させます（**完成コードは提供しません**）。

    1. **教育資金の移転**：子の学校段階（Small Dataset の学習費）に合わせて、年ごとに移転額が変わるモデル。
    2. **住宅の継承**：ある年に住宅（資産価値）を子に移す。資産価値は現金と別に記録する。
    3. **3 世代モデル**：祖父母・親・子の 3 人に広げ、2 種類の移転（祖父母→親、親→子）を扱う。
    4. **事業・知的財産の承継**：毎年の事業収入を生む資産を、ある年に子に引き継ぐ。
    5. **子の世代から親の世代への支援**：親が高齢になった後、子から親への支援（介護費など）を加える。
    """,
    "discussion": """
    - 移転額を変えると、親と子のどちらの資産不足が起きやすくなりましたか。
    - 親の最低生活資金の条件を満たしながら、子の資産不足を防げるシナリオはありましたか。
    - モデルの限界：税金、物価、健康、親子の関係など、含めていないものが結果にどう影響しますか。
    """,
    "team_features": """
    - 移転を始める時期（Tiny の `start_year`）を変えたシナリオの全探索
    - 子の学校段階ごとの教育費（Small Dataset）にもとづく移転額の計画
    - 祖父母・親・子の 3 世代モデル（移転を 2 種類にする）
    - 親の最低生活資金と子の資産の両方を考えた、シナリオの順位付け（複数の指標）
    """,
}

for theme in (F1A, F1B, F1C, F1D):
    theme_chapter(theme)

# ======================================================================
# 第8章
# ======================================================================
md("""
# 第8章　アルゴリズムの性能評価とチーム開発課題

この章は、担当テーマの Level 1（できれば Level 2）を終えてから使います。

## 8.1 シナリオの数と計算量

選択肢が増えると、組合せ（シナリオ）の数は**掛け算**で増えます。
""")
md(TEACHER)
code('''
# 【教員提供コード】組合せの数の増え方（テーマとは関係のない例）
for choices in [2, 3, 5]:
    for decisions in [1, 2, 4, 8]:
        print(f"選択肢 {choices} 個 × 判断 {decisions} 回 → 組合せ {choices ** decisions:>8,} 通り")
    print()
''')
md("""
- S 個のシナリオをそれぞれ T 年分シミュレーションすると O(S × T) です。
- 判断の回数が増えると S は急に大きくなります（指数的な増加）。全探索がすぐに現実的でなくなる理由です。

## 8.2 実行時間の測り方
""")
md(TEACHER)
code('''
# 【教員提供コード】実行時間の測り方の例（テーマとは関係のない例：1 から n までの合計）
def sum_by_loop(n):
    total = 0
    for i in range(1, n + 1):
        total += i
    return total

def sum_by_formula(n):
    return n * (n + 1) // 2

rows = compare_speed(sum_by_loop, sum_by_formula, lambda n: (n,), [1_000, 10_000, 100_000])
''')
md("""
**注意**

- 速さを比べるのは、**同じ入力で同じ結果**になる 2 つの方法だけです。
- 評価のしかた（評価指標）やモデルを変えた結果の違いを、「アルゴリズムが速くなった」と混同しないでください。
- 実行時間はコンピュータによって変わります。測った環境を記録します。

## 8.3 テーマごとの性能評価

| テーマ | 比べるもの | 使う関数 |
| --- | --- | --- |
| F-1A | 候補の数 N と、全候補の生涯所得の計算時間（O(N × T)） | 課題4 |
| F-1B | 勤務形態の種類 k と、組合せ k² × 分担 m の探索時間 | 課題5・6 |
| F-1C | 線形探索と二分探索（1 回だけ探す場合・何回も探す場合）、ソートの時間を含めた比較 | 課題4〜7 |
| F-1D | シナリオ数 S・年数 T と、シミュレーションの時間（O(S × T)） | 課題4・7 |

Benchmark Dataset は、ファイルに保存せず、`random.Random(シード)` でプログラムの中で作ります（例：6.8 の `make_prices()`）。
グラフは `plot_lines()` で「件数と実行時間」を描きます。

## 8.4 チーム開発の進め方

| 段階 | 内容 |
| --- | --- |
| 第1段階 | 基本プログラムの完成（Level 1 の動作確認がすべて `[OK]`） |
| 第2段階 | アルゴリズムの改良とシナリオの比較（Level 2） |
| 第3段階 | チーム独自の機能の開発（Level 3。**1 つ以上は必須**） |
| 第4段階 | 結果の評価と成果発表 |

**全員が少なくとも 1 つの関数を実装してください。**

## 8.5 成果物（Notebook に含めるもの）

- チームが選んだテーマと、解決しようとする問題
- 使ったデータ（人工データか、公開統計か。公開統計なら出典）とモデルの仮定
- 実装したアルゴリズムと動作確認の結果
- シミュレーションの結果（表・グラフ）
- 実行時間と計算量の評価
- チーム独自の機能（入力・処理・出力、テスト）
- 他の資料のコードを参考にした場合は、その出典と変更した点
- 結果の考察、モデルの限界と今後の課題
- 各メンバーの担当

評価の方法・提出期限・発表時間は `TASKS.md` と授業の指示を確認してください。
""")

# ======================================================================
# 第9章
# ======================================================================
md("""
# 第9章　複数テーマを統合したライフプランニング（発展・任意）

この章は**任意**です。担当テーマを終えたチームが、他のテーマの考え方を組み合わせる場合に使います。

## 9.1 統合の例

| 組合せ | 問いの例 |
| --- | --- |
| F-1A + F-1C | キャリアの選択によって、住宅を購入できる時期はどう変わるか |
| F-1B + F-1C | 子育ての期間に、通勤時間と住宅費のどちらを優先するか |
| F-1A + F-1D | 親の教育資金の支援は、子のキャリアの選択肢をどう広げるか（教材上の仮定として） |
| F-1B + F-1D | 親の介護と、子の世代の就業の両立 |

## 9.2 進め方

1. 年ごとの「出来事（ライフイベント）」を辞書のリストで表します（例：`{"year": 5, "event": "住宅購入"}`）。
2. 担当テーマで作った関数を使い、1 年ずつ収支と資産を更新します。
3. 出来事の時期を変えた複数のシナリオを比べます。

> 最初から大きなシミュレーションを作らず、**2 つのテーマの小さな組合せ**から始めてください。
> 他のテーマの関数を使う場合は、自分たちで実装し、動作確認をしてから使います。

## 9.3 注意

- モデル上の「最適な人生設計」は、設定した仮定と評価指標の下での結果にすぎません。
- 実際の進路・家族・住宅・資産の判断の代わりにはなりません。
""")


# ======================================================================
# 書き出し
# ======================================================================
def source_fingerprint(nb_cells):
    """セルの種類と内容（source）だけから作る指紋。メタデータや実行結果は含めない。"""
    payload = json.dumps([[c["cell_type"], c["source"]] for c in nb_cells], ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def overwrite_problem(path):
    """path の Notebook を上書きしてはいけない理由を返す（上書きしてよければ None）。"""
    existing = nbformat.read(path, as_version=4)
    if any(c.get("outputs") or c.get("execution_count") for c in existing.cells if c.cell_type == "code"):
        return "実行結果が残っています"
    stored = existing.metadata.get(GENERATOR_KEY, {}).get("source_fingerprint")
    if stored is None:
        return "生成スクリプトの記録（指紋）がありません"
    if source_fingerprint(existing.cells) != stored:
        return "生成した後にセルの内容が編集されています"
    return None


def build():
    nb = new_notebook(cells=cells)
    for i, cell in enumerate(nb.cells, start=1):
        cell.id = f"cell-{i:03d}"   # 再生成しても同じ内容になるよう、セル ID を連番で固定する
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nb.metadata["language_info"] = {"name": "python"}
    nb.metadata[GENERATOR_KEY] = {
        "note": "scripts/build_notebook.py で生成。再生成時に、生成後の編集を検出するための指紋。",
        "source_fingerprint": source_fingerprint(nb.cells),
    }
    nbformat.validate(nb)
    return nb


def main():
    parser = argparse.ArgumentParser(description="F-1 統合 Notebook の生成（教員用マスター）")
    parser.add_argument("--output", default=str(OUTPUT), help="出力先（既定：F1_life_planning_starter.ipynb）")
    parser.add_argument("--force", action="store_true", help="編集・実行された Notebook でも上書きする")
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists() and not args.force:
        problem = overwrite_problem(output)
        if problem:
            raise SystemExit(f"{output.name}：{problem}。学生が編集した Notebook の可能性があるため、上書きしません。\n"
                             "別のファイルに出力する場合は --output、上書きしてよい場合は --force を指定してください。")
    nb = build()
    nbformat.write(nb, output)
    n_md = sum(c.cell_type == "markdown" for c in cells)
    n_code = sum(c.cell_type == "code" for c in cells)
    n_tasks = sum(c.cell_type == "code" and "【学生実装課題" in c.source for c in cells)
    print(f"作成: {output.name}（Markdown セル {n_md} 個、コードセル {n_code} 個、学生実装課題 {n_tasks} 個）")


if __name__ == "__main__":
    main()
