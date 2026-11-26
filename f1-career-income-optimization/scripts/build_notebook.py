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

【Phase 1 の範囲】
  全 10 章の骨格、共通関数（第3章）、4 テーマの Mini Dataset、Level 1 の学生実装課題のひな形
  （NotImplementedError）、動作確認、Level 2・3 の課題候補の一覧。
  Level 2 の関数のひな形・ヒントの最終版・可視化の完成は Phase 3 以降。

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
> - この Notebook のデータは、**教材のために作った人工データ（仮定値）**です。実際の統計ではありません。
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
| F-1A | キャリア選択・教育投資と生涯所得 | 進学・就職・転職などの選択で、長期的な所得はどう変わるか | 累積和、線形探索、ソート、全探索 |
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
- 各テーマの章は、次の 3 段階でできています。

| レベル | STEP | 内容 | 位置づけ |
| --- | --- | --- | --- |
| Level 1（基本課題） | STEP 1〜3 | データの確認、基本的な計算、基本シミュレーション | **全チーム必須** |
| Level 2（改良課題） | STEP 4 | 探索・ソート・シナリオの比較 | 推奨 |
| Level 3（発展課題） | STEP 5 | 公開統計の利用、チーム独自の機能 | 発展案は選択。**独自機能の開発は必須** |

## 0.4 セルの種類

| 表示 | 意味 | 編集するか |
| --- | --- | --- |
| 【教員提供コード】 | 準備のためのコード | 編集しない（実行するだけ） |
| 【学生実装課題：Level 1／2】 | 関数を完成させる課題 | **編集する** |
| 【動作確認】 | 実装した関数の結果を確かめる | 編集しない |
| 【考察課題】 | 結果について考え、文章で答える | 答えを書く |
| 【発展課題：Level 3】 | チームで選ぶ発展的な課題 | チームで決める |

動作確認の結果は、次の 4 種類で表示されます。

| 表示 | 意味 |
| --- | --- |
| `[OK]` | 期待される結果と一致した |
| `[NG]` | 実行できたが、結果が違う（入力・期待値・違いを表示） |
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
| Mini Dataset | Notebook の中（リストと辞書） | 3〜10 件 | 人工データ | STEP 1〜3。**手で計算して確かめられる** |
| Tiny Dataset | `data/f1a/` などの CSV | 20〜50 件 | 人工データ（乱数のシードを固定） | STEP 3〜4。境界条件や制約違反を含む |
| Small Dataset | `data/f1a/*_small.csv` など | 50〜1,000 件 | 公開統計を加工したもの | STEP 5（Level 3）。**なくても基本課題は進められる** |
| Benchmark Dataset | ファイルなし（プログラムの中で作る） | 数千〜数十万件 | 人工データ | 第8章。実行時間の比較 |

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

## 2.3 データの置き場所

```text
data/
├── f1a/  career_options_tiny.csv               （F-1A：キャリア候補）
├── f1b/  work_options_tiny.csv                 （F-1B：勤務形態）
│         household_scenarios_tiny.csv          （F-1B：世帯の条件）
├── f1c/  housing_options_tiny.csv              （F-1C：住宅候補）
└── f1d/  family_members_tiny.csv               （F-1D：家族の構成）
          transfer_scenarios_tiny.csv           （F-1D：資金移転のシナリオ）
```

各列の意味と単位は `data/data_dictionary.md` を見てください。
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
| `load_csv(path, int_columns, float_columns)` | CSV を読み込み、辞書のリストにする（ファイルがなければ空のリスト） |
| `show_records(records, limit)` | 辞書のリストを表の形で表示する |
| `check(label, func, args, expected)` | 関数の結果を期待値と比べ、`[OK]`・`[NG]`・`[未実装]`・`[エラー]` を表示する。小数は小さな誤差を許す |
| `run_if_implemented(func, *args)` | 関数を実行する。未実装なら `None` を返す（Tiny Dataset への適用で使う） |
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
        辞書のリスト。ファイルがない場合は空のリスト
    """
    path = Path(path)
    if not path.exists():
        print(f"[注意] ファイルが見つかりません: {path.name}")
        return []
    records = []
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            for column in int_columns:
                row[column] = int(row[column])
            for column in float_columns:
                row[column] = float(row[column])
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


def _same(expected, actual, tol=1e-6):
    """期待値と結果が同じかを調べる。小数は小さな誤差（tol）を許す"""
    if _is_number(expected) and _is_number(actual):
        return math.isclose(expected, actual, rel_tol=1e-9, abs_tol=tol)
    if isinstance(expected, (list, tuple)):
        return (type(expected) is type(actual) and len(expected) == len(actual)
                and all(_same(e, a, tol) for e, a in zip(expected, actual)))
    if isinstance(expected, dict):
        return (isinstance(actual, dict) and expected.keys() == actual.keys()
                and all(_same(expected[k], actual[k], tol) for k in expected))
    return expected == actual


def _short(value, width=70):
    if isinstance(value, list) and len(value) > 5:
        return f"リスト（{len(value)} 件）"
    text = repr(value)
    return text if len(text) <= width else text[:width] + "…"


def _describe_difference(expected, actual):
    """期待される結果と実際の結果の違いを、日本語で短く説明する"""
    if actual is None:
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
| `plot_bars(names, values, title, ylabel)` | 棒グラフ（matplotlib がなければ文字で表示） |
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


def compare_speed(baseline, improved, make_input, sizes, repeat=3, time_limit=2.0):
    """2 つの関数を、同じ入力で実行時間を比べる。結果が違うときは比べない。

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
        if not _same(result_base, result_improved):
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


print("共通関数を定義しました: measure_time, compare_speed, jp, plot_lines, plot_bars")
''')
md("""
## 3.6 時間計算量の記号

| 記号 | 意味 |
| --- | --- |
| N | 候補データの件数（キャリア候補、住宅候補など） |
| S | シナリオの数 |
| T | シミュレーションの年数 |
| P | 家族の人数 |

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
    | **Level 1（必須）** | {n}.5〜{n}.7 | データを見る → 課題1〜4 を実装する → Tiny Dataset に適用する |
    | Level 2（推奨） | {n}.8 | 探索・ソート・シナリオの比較 |
    | Level 3（選択） | {n}.9〜{n}.10 | 公開統計・発展課題・チーム独自の機能・考察 |
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

    # STEP 2
    md(f"## {n}.6 {SECTIONS[5]}\n\n**対応レベル：Level 1（基本課題）**\n\n" + textwrap.dedent(t["step2_intro"]).strip())
    for task in t["step2"]:
        emit_task(task, LEVEL1)

    # STEP 3
    md(f"## {n}.7 {SECTIONS[6]}\n\n**対応レベル：Level 1（基本課題）**\n\n" + textwrap.dedent(t["step3_intro"]).strip())
    for task in t["step3"]:
        emit_task(task, LEVEL1)
    md("### Tiny Dataset に適用する\n\n課題をすべて実装したら、Tiny Dataset でも試してみましょう。\n\n" + TEACHER)
    code(t["tiny_apply"])
    md("### 結果をグラフで確認する\n\n" + TEACHER)
    code(t["viz"])
    md(f"{THINK}\n\n" + textwrap.dedent(t["step3_think"]).strip())

    # STEP 4
    md(f"## {n}.8 {SECTIONS[7]}\n\n**対応レベル：Level 2（改良課題）**\n\n" + textwrap.dedent(t["step4"]).strip())

    # STEP 5
    md(f"## {n}.9 {SECTIONS[8]}\n\n**対応レベル：Level 3（発展課題）**\n\n" + textwrap.dedent(t["step5"]).strip())
    md(TEACHER)
    code(small_loader(t["small"]))
    md(f"{LEVEL3}\n\n" + textwrap.dedent(t["step5_tasks"]).strip())

    md(f"## {n}.10 {SECTIONS[9]}\n\n" + textwrap.dedent(t["discussion"]).strip())


def small_loader(spec):
    var, rel_path, note = spec
    return f'''
    # 【教員提供コード】Small Dataset（公開統計を加工した CSV）を読み込む
    small_path = DATA_DIR / "{rel_path}"
    if small_path.exists():
        {var} = load_csv(small_path)
        print("{rel_path}:", len({var}), "件")
        show_records({var}, limit=5)
    else:
        {var} = []
        print("Small Dataset はまだ用意されていません（{note}）。")
        print("Mini Dataset と Tiny Dataset（人工データ）で、Level 1・2 を進めてください。")
    '''


STUB = 'raise NotImplementedError("学生実装課題")'

# ======================================================================
# 第4章　F-1A
# ======================================================================
F1A = {
    "no": 4, "code": "F-1A", "title": "キャリア選択・教育投資と生涯所得",
    "english": "Career Choice, Education Investment and Lifetime Income",
    "summary": {
        "problem": "進学・就職などの選択によって、長期的な所得がどう変わるかを比べる",
        "input": "キャリア候補（就業開始年齢、初年度年収、昇給率、教育費）",
        "process": "年齢ごとの年収、就業年数、生涯所得、教育費を引いた累積所得",
        "output": "キャリア候補ごとの生涯所得と累積所得の表・グラフ",
        "image": "「高校卒業後に就職」「専門学校卒業後に就職」「大学卒業後に就職」の所得の推移を 1 つのグラフで比べる",
    },
    "problem": """
    進学、資格取得、就職、転職などの選択によって、将来の所得や働き方は変わります。
    教育やスキルへの投資には**費用と時間**が必要ですが、将来の所得を増やす可能性もあります。

    この章では、複数のキャリアの候補を、**長期的な所得の推移**という観点から比べるプログラムを作ります。

    > 中心となる問い：**どのキャリアの候補が、どの年齢で、どれだけの所得になるか。教育費を回収できるのは何歳か。**

    注意：
    - 金額は教材のための仮定値です。実際の職業別・学歴別の所得ではありません。
    - 所得だけでキャリアの価値は決まりません。やりたいこと、学ぶこと自体の価値、働く時間、健康なども大切です。
    """,
    "background": """
    | 用語 | この教材での意味 |
    | --- | --- |
    | 年収 | その年齢の 1 年間の給与（額面、万円） |
    | 昇給率（`annual_growth`） | 年収が毎年増える割合（0.02 = 2%） |
    | 就業年数 | 就業開始年齢から退職年齢の前の年までの年数 |
    | 生涯所得 | 就業期間の年収の**合計**（教育費は引かない） |
    | 累積所得（教育費控除後） | 生涯所得 − 教育費 |
    | 投資の回収 | 教育費を払った候補の累積額が、比較する候補に追いつくこと |

    **年収のモデル（この教材の仮定）**

    ```text
    年齢 a の年収 = initial_salary × (1 + annual_growth) ^ (a − start_age)   （start_age ≤ a < 退職年齢）
    年齢 a の年収 = 0                                                     （それ以外）
    ```

    - 退職年齢（`RETIREMENT_AGE`）の年からは計算しません。65 歳なら 64 歳の 1 年間までです。
    - 生涯所得は、年齢を 1 つずつ増やしながら年収を足していく**累積和**で計算します。T 年分なら O(T)。
    - N 個の候補を比べると O(N × T) です。
    """,
    "goals": """
    | レベル | STEP | 学習目標 | 学生実装課題 |
    | --- | --- | --- | --- |
    | Level 1 | STEP 1 | キャリア候補のデータの意味と単位を説明できる | ― |
    | Level 1 | STEP 2 | 条件分岐と計算で、就業年数・年収を求められる | 課題1 `calculate_working_years()`、課題2 `salary_at_age()` |
    | Level 1 | STEP 3 | ループで累積和を計算し、候補を比べられる | 課題3 `lifetime_income()`、課題4 `summarize_careers()` |
    | Level 2 | STEP 4 | 線形探索・ソート・全探索で候補を比べられる | 4.8 の候補から 2〜3 個 |
    | Level 3 | STEP 5 | 公開統計や発展的なモデルで、チーム独自の機能を作れる | 4.9 から選ぶ |
    """,
    "data": """
    | Mini Dataset | Notebook の中の `career_options` | 3 | 人工データ（仮定値） | 利用可 |
    | Tiny Dataset | `data/f1a/career_options_tiny.csv` | 24 | 人工データ（シード固定） | 初期版 |
    | Small Dataset | `data/f1a/salary_by_age_small.csv` | 未定 | 賃金構造基本統計調査（予定） | 未作成 |
    | Benchmark Dataset | プログラムの中で生成 | 可変 | 人工データ | 第8章 |
    """,
    "mini_code": '''
    # 【教員提供コード】F-1A の Mini Dataset（人工データ。金額は万円、年齢は歳）
    RETIREMENT_AGE = 65    # 退職年齢（この年齢の年からは所得なし）

    career_options = [
        {"career_id": "A", "name": "高校卒業後に就職",
         "start_age": 18, "initial_salary": 250, "annual_growth": 0.02, "education_cost": 0},
        {"career_id": "B", "name": "専門学校卒業後に就職",
         "start_age": 20, "initial_salary": 300, "annual_growth": 0.025, "education_cost": 200},
        {"career_id": "C", "name": "大学卒業後に就職",
         "start_age": 22, "initial_salary": 330, "annual_growth": 0.03, "education_cost": 400},
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
            check("課題1：開始と退職が同じ年齢", calculate_working_years, (65, 65), 0)
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

            `career` の辞書は書き換えないでください（読むだけにします）。
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
    "tiny_apply": '''
    # 【教員提供コード】Tiny Dataset の各候補の生涯所得を計算する（各候補の退職年齢を使う）
    for career in tiny_careers[:10]:
        total = run_if_implemented(lifetime_income, career, career["retirement_age"])
        if total is None:
            break
        print(f'{career["career_id"]:>4}  {career["career_name"]:<24}  生涯所得 {total:>9,.1f} 万円')
    ''',
    "viz": '''
    # 【教員提供コード】Mini Dataset の年齢別の年収（課題2 を実装すると表示される）
    ages = list(range(18, RETIREMENT_AGE))
    if run_if_implemented(salary_at_age, career_options[0], 18, RETIREMENT_AGE) is not None:
        series = {}
        for career in career_options:
            series[career["career_id"]] = [salary_at_age(career, a, RETIREMENT_AGE) for a in ages]
        plot_lines(ages, series, jp("年齢別の年収（人工データ）", "Salary by age (synthetic)"),
                   jp("年齢", "age"), jp("年収（万円）", "salary (10k JPY)"))
    ''',
    "step3_think": """
    1. 退職年齢 65 歳のとき、生涯所得が最も大きい候補はどれですか。教育費を引いた累積所得ではどうですか。
    2. 昇給率を 0.01 変えると、結果はどう変わりますか。どの仮定に結果が敏感ですか。
    3. このモデルに含まれていないもの（税金、失業、労働時間など）を 3 つ挙げてください。
    """,
    "step4": """
    > Phase 3 で、次の候補から 2〜3 個を学生実装課題として用意します（関数のひな形・ヒント・動作確認つき）。

    | 候補 | 関数名（予定） | アルゴリズム | 計算量 |
    | --- | --- | --- | --- |
    | 条件を満たすキャリア候補を抽出する（例：教育費が予算以下、生涯所得が基準以上） | `filter_careers()` | 線形探索 | O(N × T) |
    | 生涯所得などの指標で候補を並べる | `rank_careers()` | ソート | O(N log N)（`sorted`）／O(N²)（挿入ソート） |
    | 教育投資の回収年齢を求める（累積額が比較対象に追いつく最初の年齢） | `find_payback_age()` | 線形探索（累積和） | O(T) |
    | 進学・資格取得・転職時期の組合せをすべて試す | `search_career_plans()` | 全探索 | O(組合せ数 × T) |

    - 回収年齢の探索では、累積額の差が**単調に増えるとは限らない**（転職などで逆転する）ため、二分探索ではなく線形探索を基本にします。
    """,
    "step5": """
    公開統計（例：厚生労働省「賃金構造基本統計調査」の年齢階級別の賃金）を使うと、仮定値ではなく統計にもとづく年収の推移を試せます。

    - 統計の平均値は、**個人の将来を予測するものではありません**。
    - 学歴別・職種別の賃金の差を、そのまま進学や資格取得の**効果（因果関係）**とみなさないでください。
    """,
    "small": ("salary_small", "f1a/salary_by_age_small.csv", "Phase 2 で公開統計から作成予定"),
    "step5_tasks": """
    次の中から、チームで関心のあるものを選びます（すべてを実装する必要はありません）。

    - IT エンジニアのキャリアパス（職種ごとの年収の仮定を作る）
    - 転職時期の最適化（転職する年齢をすべて試す）
    - 資格取得の費用と所得の関係、教育投資の費用対効果
    - 失業や休職のリスク（乱数を使う場合はシードを固定する）
    - 所得だけでなく労働時間も考えたキャリアの比較
    """,
    "discussion": """
    - 生涯所得が最大の候補と、教育費を引いた累積所得が最大の候補は同じでしたか。違う場合、なぜですか。
    - どの仮定（初年度年収、昇給率、教育費、退職年齢）を変えると、順位が入れ替わりましたか。
    - チーム独自の機能：どんな問いに答える機能を作りましたか。入力・処理・出力を説明してください。
    - モデルの限界：税金・社会保険料・物価・失業・健康などを含めていないことが、結果にどう影響しますか。
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
        "input": "勤務形態（年収、週の労働時間）、世帯の支出と必要な育児・介護時間",
        "process": "世帯の年間所得・支出・収支、1 人ごとの残り時間",
        "output": "勤務形態の組合せごとの年間収支と自由時間",
        "image": "「フルタイム＋時短」「フルタイム＋フルタイム」などの組合せを、収支と自由時間の表で比べる",
    },
    "problem": """
    家族の生活を続けるには、お金（所得）と同時に、**時間**も必要です。
    仕事、家事、育児、介護に使う時間の合計は、1 人あたり **1 週間に 168 時間**を超えることはできません。

    この章では、成人 2 人の世帯を例に、勤務形態の組合せ（フルタイム、時短勤務、休業など）ごとに、
    **年間の収支**と**1 人ごとの残り時間**を計算して比べます。

    注意：
    - 金額と時間は教材のための仮定値です。実際の育児休業給付金や社会保障制度は表していません。
    - 特定の家族の形や、性別による役割分担を「望ましい」とするものではありません。Adult 1・Adult 2 は性別や役割を意味しません。
    - 家族の生活には、金額や時間では表せない価値があります。
    """,
    "background": """
    | 用語 | この教材での意味 |
    | --- | --- |
    | 世帯の年間所得 | 2 人の年収（額面）の合計（万円／年） |
    | 世帯の年間支出 | 生活費 + 育児費 + 介護費（万円／年） |
    | 年間収支 | 年間所得 − 年間支出。マイナスなら赤字 |
    | 基本生活時間 | 睡眠・食事・身の回りの時間（この教材では 1 人 **77 時間／週** と仮定） |
    | 残り時間（自由時間） | 168 − 基本生活時間 − 労働時間 − 育児・介護時間（時間／週） |

    - 2 人の**合計**の時間だけでなく、**1 人ごと**の時間の制約（168 時間）も確かめます。
    - 勤務形態が k 種類なら、2 人の組合せは k × k 通りです（全探索）。
    """,
    "goals": """
    | レベル | STEP | 学習目標 | 学生実装課題 |
    | --- | --- | --- | --- |
    | Level 1 | STEP 1 | 勤務形態と世帯のデータの意味と単位を説明できる | ― |
    | Level 1 | STEP 2 | 辞書の値を使って、世帯の所得と支出を計算できる | 課題1 `household_income()`、課題2 `household_expense()` |
    | Level 1 | STEP 3 | 収支と時間の制約を計算できる | 課題3 `annual_balance()`、課題4 `free_hours()` |
    | Level 2 | STEP 4 | 組合せの全探索と条件による絞り込みができる | 5.8 の候補から 2〜3 個 |
    | Level 3 | STEP 5 | 公開統計や発展的なモデルで、チーム独自の機能を作れる | 5.9 から選ぶ |
    """,
    "data": """
    | Mini Dataset | Notebook の中の `work_options`・`household` | 3 + 1 | 人工データ（仮定値） | 利用可 |
    | Tiny Dataset | `data/f1b/work_options_tiny.csv`、`data/f1b/household_scenarios_tiny.csv` | 6 + 24 | 人工データ（シード固定） | 初期版 |
    | Small Dataset | `data/f1b/household_expenses_small.csv` | 未定 | 家計調査・社会生活基本調査（予定） | 未作成 |
    | Benchmark Dataset | プログラムの中で生成 | 可変 | 人工データ | 第8章 |
    """,
    "mini_code": '''
    # 【教員提供コード】F-1B の Mini Dataset（人工データ。金額は万円／年、時間は時間／週）
    HOURS_PER_WEEK = 168        # 1 人が 1 週間に使える時間
    BASIC_HOURS = 77            # 睡眠・食事・身の回りの時間（この教材の仮定：1 日 11 時間 × 7 日）

    work_options = [
        {"option_id": "W1", "name": "フルタイム勤務", "annual_income": 400, "weekly_work_hours": 40},
        {"option_id": "W2", "name": "時短勤務", "annual_income": 280, "weekly_work_hours": 28},
        {"option_id": "W3", "name": "休業", "annual_income": 0, "weekly_work_hours": 0},
    ]
    household = {"scenario_id": "S1", "living_cost": 360, "childcare_cost": 60, "eldercare_cost": 0,
                 "required_care_hours": 30}   # 必要な育児・介護の時間（世帯全体で 時間／週）
    show_records(work_options)
    print(household)
    ''',
    "mini_questions": """
    1. 2 人とも「フルタイム勤務」のとき、世帯の年間所得はいくらですか。
    2. この世帯の年間支出はいくらですか。
    3. フルタイム勤務の人が育児に週 15 時間使うと、残り時間は何時間ですか。
    """,
    "tiny_code": '''
    # 【教員提供コード】F-1B の Tiny Dataset を読み込む
    tiny_work_options = load_csv(DATA_DIR / "f1b" / "work_options_tiny.csv",
                                 int_columns=["annual_income", "weekly_work_hours"])
    tiny_households = load_csv(DATA_DIR / "f1b" / "household_scenarios_tiny.csv",
                               int_columns=["living_cost", "childcare_cost", "eldercare_cost",
                                            "required_childcare_hours", "required_eldercare_hours"])
    print("勤務形態:", len(tiny_work_options), "件　世帯の条件:", len(tiny_households), "件")
    show_records(tiny_work_options)
    show_records(tiny_households, limit=5)
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
            | 引数 | 労働時間・育児と介護の時間・基本生活時間（すべて 時間／週） |
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
                      "第5章の最初で定義した定数 `HOURS_PER_WEEK` を使います。",
                      "HOURS_PER_WEEK − basic_hours − weekly_work_hours − weekly_care_hours を返す"),
            "check": '''
            # 【動作確認】
            check("課題4：フルタイム、育児 15 時間", free_hours, (40, 15, BASIC_HOURS), 36)
            check("課題4：休業、育児 30 時間", free_hours, (0, 30, BASIC_HOURS), 61)
            check("課題4：時間が足りない場合（マイナス）", free_hours, (40, 60, BASIC_HOURS), -9)
            ''',
        },
    ],
    "tiny_apply": '''
    # 【教員提供コード】Tiny Dataset：最初の世帯について、勤務形態の 1 つの組合せの収支を計算する
    if tiny_work_options and tiny_households:
        h = tiny_households[0]
        a, b = tiny_work_options[0], tiny_work_options[1]
        result = run_if_implemented(annual_balance, a, b, h)
        if result is not None:
            print(f'{h["scenario_id"]}：{a["work_style"]} ＋ {b["work_style"]} の年間収支 = {result:,} 万円')
    ''',
    "viz": '''
    # 【教員提供コード】Mini Dataset：2 人とも同じ勤務形態の場合の、世帯所得と支出（課題1・2 を実装すると表示される）
    names, incomes = [], []
    for option in work_options:
        value = run_if_implemented(household_income, option, option)
        if value is None:
            break
        names.append(option["option_id"])
        incomes.append(value)
    expense = run_if_implemented(household_expense, household)
    if incomes and expense is not None:
        plot_bars(names + [jp("支出", "expense")], incomes + [expense],
                  jp("世帯の年間所得と年間支出（人工データ）", "Household income and expense (synthetic)"),
                  jp("万円／年", "10k JPY / year"))
    ''',
    "step3_think": """
    1. 年間収支が最も大きい組合せと、2 人の残り時間の合計が最も大きい組合せは同じですか。
    2. 育児・介護に必要な時間（`required_care_hours`）を 2 人でどう分けるかで、1 人ごとの残り時間はどう変わりますか。
    3. 所得と自由時間のどちらを重視するかは、誰がどう決めるべきでしょうか。
    """,
    "step4": """
    > Phase 3 で、次の候補から 2〜3 個を学生実装課題として用意します。

    | 候補 | 関数名（予定） | アルゴリズム | 計算量 |
    | --- | --- | --- | --- |
    | 2 人の勤務形態の組合せをすべて作る | `generate_work_pairs()` | 二重の for 文（全探索） | O(k²) |
    | 収支が 0 以上、かつ 2 人とも残り時間が基準以上の組合せを探す | `find_feasible_pairs()` | 全探索 + 条件による絞り込み | O(k²) |
    | 所得や自由時間で組合せを並べる | `rank_pairs()` | ソート | O(k² log k) |
    | 複数年の家計収支（子どもの年齢で育児費が変わる） | `simulate_household()` | 年次シミュレーション | O(T) |

    - 育児・介護の時間の分け方（半分ずつ、労働時間に応じて、など）は**仮定**です。分け方によって結果が変わることを確かめます。
    """,
    "step5": """
    公開統計（例：総務省「家計調査」の支出、「社会生活基本調査」の生活時間）を使うと、仮定値の代わりに統計にもとづく値を試せます。

    - 統計の平均値は、特定の家族の生活を表すものではありません。
    - 異なる調査の値を組み合わせるときは、調査年・対象（個人か世帯か）・単位（月額か年額か、1 日か 1 週間か）をそろえます。
    """,
    "small": ("expense_small", "f1b/household_expenses_small.csv", "Phase 2 で公開統計から作成予定"),
    "step5_tasks": """
    - 子どもの年齢に応じた育児費の変化
    - 育児休業とキャリアの継続（休業した年の所得と、その後の所得）
    - 保育サービスを使う場合と使わない場合の比較（費用と時間）
    - 家族内の介護と外部の介護サービスの比較
    - 所得と自由時間の両立、複数の評価指標による比較
    """,
    "discussion": """
    - 所得が最大の組合せと、自由時間を重視した組合せは同じでしたか。違う場合、何が違いを生みましたか。
    - 1 人の時間が 168 時間を超えてしまう組合せはありましたか。2 人の合計だけを見ると、何を見落としますか。
    - チーム独自の機能：どんな問いに答える機能を作りましたか。
    - モデルの限界：金額や時間で表せない家族の価値を、どのように考察に含めましたか。
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
        "process": "年間家賃、累積家賃、購入費用＋維持費、条件による探索",
        "output": "条件を満たす住宅候補の一覧、賃貸と購入の累積支出の比較",
        "image": "「予算 3,500 万円以下・通勤 50 分以内」の住宅を探し、賃貸した場合と購入した場合の 30 年間の支出を比べる",
    },
    "problem": """
    どこに、いつ、どのような住宅に住むかは、長期的な家計に大きく影響します。
    この章では、住宅候補のデータから**条件を満たす住宅を探す**プログラムと、
    **賃貸と購入の支出を長期的に比べる**プログラムを作ります。

    この章は、**線形探索（Linear Search）と二分探索（Binary Search）**を特に詳しく扱います。

    注意：
    - 価格・家賃・通勤時間は教材のための仮定値です。実際の物件や地域を表すものではありません。
    - 住宅の将来の価値には不確実性があります。持ち家と賃貸のどちらが良いかを決めるものではありません。
    """,
    "background": """
    | 用語 | この教材での意味 |
    | --- | --- |
    | 購入価格（`purchase_price`） | 住宅を買うときの価格（万円）。**1 回だけ**の支出 |
    | 月額家賃（`monthly_rent`） | 賃貸の 1 か月の家賃（万円／月）。年額は × 12 |
    | 年間維持費（`annual_maintenance_cost`） | 購入した場合の修繕・税などの費用（万円／年、仮定値） |
    | 累積住宅費 | 指定した年数の住宅の支出の合計 |
    | 住宅資産価値 | 購入した住宅のその時点の価値。**支出とは別のもの**（Level 3） |

    - Level 1 では、住宅ローン（借入と返済）は扱いません。購入価格を最初に全額払うと単純化します。
    - **住宅の購入費用の総額、毎年の現金の支出、住宅の資産価値を混同しない**ようにします。

    **探索アルゴリズム**

    | 方法 | 前提 | 1 回の探索の計算量 |
    | --- | --- | --- |
    | 線形探索 | なし（並び順はどうでもよい） | O(N) |
    | 二分探索 | データが**価格の順にソート済み** | 境界の位置を見つけるのに O(log N) |

    - 予算以下の**すべての物件**を返す場合、境界を見つけるのは O(log N) でも、結果を取り出すのに O(K)（K は該当件数）かかります。
    - ソートには O(N log N) かかります。**1 回だけ**探すなら線形探索で十分なこともあり、**同じデータで何回も**探すときに二分探索が有利になります。
    """,
    "goals": """
    | レベル | STEP | 学習目標 | 学生実装課題 |
    | --- | --- | --- | --- |
    | Level 1 | STEP 1 | 住宅候補のデータの意味と単位（月額・年額・総額）を説明できる | ― |
    | Level 1 | STEP 2 | 月額・年額・累積額を区別して計算できる | 課題1 `annual_rent()`、課題2 `cumulative_rent()` |
    | Level 1 | STEP 3 | 購入の費用を計算し、条件を満たす候補を線形探索で探せる | 課題3 `ownership_cost()`、課題4 `find_candidates()` |
    | Level 2 | STEP 4 | ソートと二分探索で境界を見つけ、線形探索と比べられる | 6.8 の候補から 2〜3 個 |
    | Level 3 | STEP 5 | 公開データや住宅ローンなどで、チーム独自の機能を作れる | 6.9 から選ぶ |
    """,
    "data": """
    | Mini Dataset | Notebook の中の `housing_options` | 5 | 人工データ（仮定値） | 利用可 |
    | Tiny Dataset | `data/f1c/housing_options_tiny.csv` | 30 | 人工データ（シード固定、同じ価格の物件を含む） | 初期版 |
    | Small Dataset | `data/f1c/housing_prices_small.csv` | 未定 | 不動産情報ライブラリ（予定。家賃・通勤時間は含まれない） | 未作成 |
    | Benchmark Dataset | プログラムの中で生成 | 可変 | 人工データ | 第8章 |
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
    3. H02 と H04 は価格が同じです。価格の順に並べたとき、どちらが先になるかは何で決まりますか。
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
    "tiny_apply": '''
    # 【教員提供コード】Tiny Dataset から、予算 3,000 万円以下・通勤 45 分以内の住宅を探す
    found = run_if_implemented(find_candidates, tiny_housing, 3000, 45)
    if found is not None:
        print("条件を満たす住宅:", len(found), "件", found)
    ''',
    "viz": '''
    # 【教員提供コード】賃貸と購入の累積支出（H02 の例。課題2・3 を実装すると表示される）
    H02 = housing_options[1]
    years = list(range(0, 41))
    if run_if_implemented(cumulative_rent, H02["monthly_rent"], 1) is not None \\
            and run_if_implemented(ownership_cost, H02, 1) is not None:
        plot_lines(years,
                   {jp("賃貸", "rent"): [cumulative_rent(H02["monthly_rent"], y) for y in years],
                    jp("購入（ローンなし）", "buy (no loan)"): [ownership_cost(H02, y) for y in years]},
                   jp("H02 の累積住宅費（人工データ）", "Cumulative housing cost of H02 (synthetic)"),
                   jp("住む年数", "years"), jp("万円", "10k JPY"))
    ''',
    "step3_think": """
    1. H02 では、何年住むと購入の費用が賃貸の累積家賃より小さくなりますか。グラフから読み取ってみましょう。
    2. この比較に含まれていないもの（売却価格、ローンの利息、家賃の値上がりなど）は、結果にどう影響しますか。
    3. 課題4 の線形探索では、候補が N 件のとき何回比較しますか。
    """,
    "step4": """
    > Phase 3 で、次の候補から 2〜3 個を学生実装課題として用意します。

    | 候補 | 関数名（予定） | アルゴリズム | 計算量 |
    | --- | --- | --- | --- |
    | 住宅候補を購入価格の順に並べる（同じ価格は元の順番） | `sort_by_price()` | ソート（安定） | O(N log N)／O(N²) |
    | ソート済みのリストで、予算以下の物件が何件あるか（境界の位置）を求める | `count_affordable()` | **二分探索** | O(log N) |
    | 予算以下のすべての物件を返す | `affordable_options()` | 二分探索 + 取り出し | O(log N + K) |
    | 線形探索と二分探索の実行時間を比べる（1 回だけ探す場合と、同じデータで何回も探す場合） | ― | 性能評価 | O(Q × N) と O(N log N + Q × log N) |
    | 予算・通勤時間・床面積を組み合わせた探索、住宅と取得時期の組合せ | `search_housing_plans()` | 全探索 | O(N × 時期の数 × T) |

    - 二分探索では、**予算と同じ価格の物件が複数ある**場合と、**該当する物件がない**場合も正しく動くことを確かめます。
    """,
    "step5": """
    公開データ（例：国土交通省「不動産情報ライブラリ」の不動産取引価格情報）を使うと、実際の取引価格の分布で探索を試せます。

    - 取引価格のデータには、**家賃や通勤時間は含まれていません**。それらを実測値のように追加しないでください。
    - 別の資料の値や仮定値を組み合わせる場合は、出典と「仮定値である」ことを明記します。
    """,
    "small": ("prices_small", "f1c/housing_prices_small.csv", "Phase 2 で公開データから作成予定"),
    "step5_tasks": """
    - 賃貸と持ち家の長期比較（売却価格・残存価値を含める）
    - 住宅ローンの返済シミュレーション（元利均等返済。式の意味を説明してから使う）
    - 住宅を取得する時期の比較
    - 通勤時間と住宅価格の関係（散布図）
    - 家族構成の変化に伴う住み替え
    - 複数の条件を考えた住宅選択（重み付きの評価など）
    """,
    "discussion": """
    - 線形探索と二分探索は、どのような場面でどちらが有利でしたか。ソートにかかる時間も含めて説明してください。
    - 賃貸と購入の比較で、結果が逆転する年数はどの仮定に敏感でしたか。
    - チーム独自の機能：どんな問いに答える機能を作りましたか。
    - モデルの限界：住宅の価値の変化、金利、引っ越し、家族の変化などをどう考えますか。
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
        "input": "親子の年収・年間支出・資産、資金移転のシナリオ（毎年の金額、年数）",
        "process": "1 年ごとの収支、資金の移転、資産残高の更新",
        "output": "年ごとの親子の資産残高、資産不足の有無",
        "image": "毎年の移転額が 0・50・100 万円の 3 つのシナリオで、4 年間の親子の資産の推移を比べる",
    },
    "problem": """
    親の世代の選択や資源の使い方は、子の世代の生活にも影響します。
    教育資金、生活の支援、住宅、金融資産、事業などが、世代を越えて受け継がれます。

    この章では、まず**親子 2 人・資金の移転 1 種類**だけを扱い、
    毎年の収支と移転によって、親子それぞれの資産がどう変わるかをシミュレーションします。

    注意：
    - 金額は教材のための仮定値です。税金・相続制度・贈与の制度は扱いません。
    - 親から子への支援の「正しい額」を決めるものではありません。
    """,
    "background": """
    | 用語 | この教材での意味 |
    | --- | --- |
    | 年間収支 | 年収 − 年間支出（万円／年）。資金の移転は含めない |
    | 資金の移転（`annual_transfer`） | 親の資産から子の資産へ、毎年移すお金（万円／年） |
    | 資産残高 | その年の終わりに持っているお金（万円）。マイナスなら資産不足 |

    **この教材のルール（1 年の流れ）**

    ```text
    親の資産 ← 親の資産 + 親の年間収支 − 移転額
    子の資産 ← 子の資産 + 子の年間収支 + 移転額
    ```

    - 親から減った額と子に増えた額は**必ず同じ**です（お金が消えたり増えたりしない）。
    - 家族全体の所得を計算するとき、家族の中の資金の移転を**新しい所得として二重に数えない**ようにします。
    - T 年のシミュレーションは O(T)、P 人の家族なら O(P × T)、S 個のシナリオなら O(S × P × T) です。
    """,
    "goals": """
    | レベル | STEP | 学習目標 | 学生実装課題 |
    | --- | --- | --- | --- |
    | Level 1 | STEP 1 | 家族と資金移転のデータの意味と単位を説明できる | ― |
    | Level 1 | STEP 2 | 年間収支と資金の移転を計算できる（合計が変わらないことを確かめる） | 課題1 `annual_balance_of()`、課題2 `transfer()` |
    | Level 1 | STEP 3 | 資産を 1 年ずつ更新するシミュレーションを作れる | 課題3 `update_assets()`、課題4 `simulate_transfer()` |
    | Level 2 | STEP 4 | 移転の額・期間の組合せを全探索し、条件を満たすシナリオを探せる | 7.8 の候補から 2〜3 個 |
    | Level 3 | STEP 5 | 3 世代モデルや公開統計などで、チーム独自の機能を作れる | 7.9 から 1 つ選ぶ |
    """,
    "data": """
    | Mini Dataset | Notebook の中の `family`・`transfer_options` | 2 + 3 | 人工データ（仮定値） | 利用可 |
    | Tiny Dataset | `data/f1d/family_members_tiny.csv`、`data/f1d/transfer_scenarios_tiny.csv` | 24 + 24 | 人工データ（シード固定） | 初期版 |
    | Small Dataset | `data/f1d/household_assets_small.csv` | 未定 | 全国家計構造調査（予定。集計統計をパラメータとして使う） | 未作成 |
    | Benchmark Dataset | プログラムの中で生成 | 可変 | 人工データ | 第8章 |
    """,
    "mini_code": '''
    # 【教員提供コード】F-1D の Mini Dataset（人工データ。金額は万円、年齢は歳）
    family = [
        {"person_id": "P01", "generation": 1, "role": "親", "age": 45,
         "annual_income": 500, "annual_expense": 350, "assets": 1000},
        {"person_id": "P02", "generation": 2, "role": "子", "age": 18,
         "annual_income": 0, "annual_expense": 80, "assets": 0},
    ]
    transfer_options = [
        {"annual_transfer": 0, "years": 4},
        {"annual_transfer": 50, "years": 4},
        {"annual_transfer": 100, "years": 4},
    ]
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
    print("家族の構成員:", len(tiny_members), "人　資金移転のシナリオ:", len(tiny_transfers), "件")
    show_records(tiny_members, limit=4)
    show_records(tiny_transfers, limit=4)
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
            | 関数 | `simulate_transfer(parent, child, annual_transfer, years)` |
            | 引数 | 親と子の辞書、毎年の移転額（万円／年）、年数（整数） |
            | 戻り値 | 年ごとの辞書 `{"year": 年, "parent_assets": 親の資産, "child_assets": 子の資産}` のリスト |
            | 例 | 移転額 50、2 年 → `[{"year": 1, "parent_assets": 1100, "child_assets": -30}, {"year": 2, "parent_assets": 1200, "child_assets": -60}]` |

            - 資産の初期値は、辞書の `assets` を使います。**辞書そのものは書き換えません。**
            - 1 年の流れ：課題3 で収支を反映 → 課題2 で移転する。
            - 年数が 0 なら、空のリストを返します。
            """,
            "stub": f'''
            # 【学生実装課題：Level 1】課題4
            def simulate_transfer(parent, child, annual_transfer, years):
                """親子の資産の推移（年の終わりの資産）を、年ごとの辞書のリストで返す。"""
                # TODO: 親と子の資産を、それぞれの辞書の "assets" から変数にコピーする。
                # TODO: 1 年目から years 年目まで、収支の反映（課題3）と移転（課題2）をくり返す。
                # TODO: 毎年の終わりに {{"year": ..., "parent_assets": ..., "child_assets": ...}} を記録する。
                {STUB}
            ''',
            "hints": ("年の初めの資産を変数に入れ、for 文で 1 年ずつ更新し、そのたびに記録します。",
                      "`for year in range(1, years + 1):`、課題2 のタプルは `p, c = transfer(...)` で受け取れます。",
                      "p ← parent の assets、c ← child の assets\nhistory ← 空のリスト\n"
                      "for year in 1 から years まで:\n    p ← update_assets(p, 親の年収, 親の支出)\n"
                      "    c ← update_assets(c, 子の年収, 子の支出)\n    p, c ← transfer(p, c, annual_transfer)\n"
                      "    {year, parent_assets: p, child_assets: c} を history に追加\nhistory を返す"),
            "check": '''
            # 【動作確認】
            check("課題4：移転額 50、2 年", simulate_transfer, (parent, child, 50, 2),
                  [{"year": 1, "parent_assets": 1100, "child_assets": -30},
                   {"year": 2, "parent_assets": 1200, "child_assets": -60}])
            check("課題4：移転額 100、2 年", simulate_transfer, (parent, child, 100, 2),
                  [{"year": 1, "parent_assets": 1050, "child_assets": 20},
                   {"year": 2, "parent_assets": 1100, "child_assets": 40}])
            check("課題4：0 年", simulate_transfer, (parent, child, 50, 0), [])
            ''',
        },
    ],
    "tiny_apply": '''
    # 【教員提供コード】Mini Dataset の 3 つの移転シナリオで、4 年後の資産を比べる
    for option in transfer_options:
        history = run_if_implemented(simulate_transfer, parent, child, option["annual_transfer"], option["years"])
        if history is None:
            break
        last = history[-1]
        total = last["parent_assets"] + last["child_assets"]
        print(f'移転額 {option["annual_transfer"]:>3} 万円／年：親 {last["parent_assets"]:>6}　子 {last["child_assets"]:>5}　合計 {total}')
    print("（Tiny Dataset の家族への適用は Phase 3 で追加します）")
    ''',
    "viz": '''
    # 【教員提供コード】移転額ごとの子の資産の推移（課題4 を実装すると表示される）
    series = {}
    for option in transfer_options:
        history = run_if_implemented(simulate_transfer, parent, child, option["annual_transfer"], option["years"])
        if history is None:
            break
        series[f'{option["annual_transfer"]}'] = [h["child_assets"] for h in history]
    if series:
        plot_lines(list(range(1, transfer_options[0]["years"] + 1)), series,
                   jp("移転額ごとの子の資産（人工データ）", "Child assets by transfer (synthetic)"),
                   jp("年", "year"), jp("万円", "10k JPY"))
    ''',
    "step3_think": """
    1. 3 つのシナリオで、4 年後の親子の資産の**合計**は同じですか。それはなぜですか。
    2. 子の資産がマイナスになるのは、どのシナリオの何年目ですか。マイナスを 0 に置き換えると、何が分からなくなりますか。
    3. 親の老後の生活資金（例：最低 1,000 万円を残す）という条件を加えると、選べるシナリオはどう変わりますか。
    """,
    "step4": """
    > Phase 3 で、次の候補から 2〜3 個を学生実装課題として用意します。

    | 候補 | 関数名（予定） | アルゴリズム | 計算量 |
    | --- | --- | --- | --- |
    | 移転額と期間（開始年・年数）の組合せをすべて作る | `generate_transfer_scenarios()` | 二重の for 文（全探索） | O(額の数 × 期間の数) |
    | 親の最低資産などの制約を満たすシナリオを探す | `find_feasible_transfers()` | 全探索 + 条件による絞り込み | O(S × T) |
    | 資産不足が起きた年数を数える | `count_shortage_years()` | 線形探索・数え上げ | O(T) |
    | 複数の評価指標（子の最終資産、親の最低資産、資産不足の年数）で比べる | `rank_transfers()` | ソート | O(S log S) |
    """,
    "step5": """
    実際の複数世代の家族を追跡した個人データは使いません。
    公開された**集計統計**（例：総務省「全国家計構造調査」の年齢階級別の資産、文部科学省「子供の学習費調査」）を
    パラメータとして使い、**仮想の家族**でシミュレーションします。

    - 教育費から将来の所得が増えるモデルを作る場合、その関係は**教材上の仮定**であることを明記します。
    - 統計で見られる相関関係を、そのまま因果関係として扱わないでください。
    - 税金・相続制度・事業の評価などの複雑な制度は、基本課題では扱いません。
    """,
    "small": ("assets_small", "f1d/household_assets_small.csv", "Phase 2 で公開統計から作成予定"),
    "step5_tasks": """
    次のうち、チームで関心のある **1 つ**を選んで発展させます。

    - 教育資金と人的資本の世代間の継承
    - 住宅・不動産の継承
    - 金融資産の継承
    - 事業・知的財産の承継
    - 子の世代から親の世代への生活支援・介護支援
    - 祖父母・親・子の 3 世代モデル
    - 複数のライフイベントを含む長期シミュレーション
    """,
    "discussion": """
    - 移転額を変えると、親と子のどちらの資産不足が起きやすくなりましたか。
    - 親の最低生活資金の条件を満たしながら、子の資産不足を防げるシナリオはありましたか。
    - チーム独自の機能：どんな問いに答える機能を作りましたか。
    - モデルの限界：税金、物価、健康、親子の関係など、含めていないものが結果にどう影響しますか。
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

## 8.3 テーマごとの性能評価（Phase 4 で追加予定）

| テーマ | 比べるもの（予定） |
| --- | --- |
| F-1A | キャリアの組合せの数と全探索の時間 |
| F-1B | 勤務形態の種類 k と組合せ k² の探索時間 |
| F-1C | 線形探索と二分探索（1 回だけ探す場合・何回も探す場合）、ソートの時間を含めた比較 |
| F-1D | シナリオ数 S・年数 T と、シミュレーションの時間 |

## 8.4 チーム開発の進め方

| 段階 | 内容 |
| --- | --- |
| 第1段階 | 基本プログラムの完成（Level 1 の動作確認がすべて `[OK]`） |
| 第2段階 | アルゴリズムの改良とシナリオの比較（Level 2） |
| 第3段階 | チーム独自の機能の開発（Level 3） |
| 第4段階 | 結果の評価と成果発表 |

**全員が少なくとも 1 つの関数を実装してください。**

## 8.5 成果物（Notebook に含めるもの）

- チームが選んだテーマと、解決しようとする問題
- 使ったデータ（人工データか、公開統計か）とモデルの仮定
- 実装したアルゴリズムと動作確認の結果
- シミュレーションの結果（表・グラフ）
- 実行時間と計算量の評価
- チーム独自の機能
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
    print(f"作成: {output.name}（Markdown セル {n_md} 個、コードセル {n_code} 個）")


if __name__ == "__main__":
    main()
