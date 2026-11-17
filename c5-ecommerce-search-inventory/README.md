# C5：ECサイトの商品検索・在庫管理

> ⚠️ **公開前の注意**
> `textbook/` 内のコードは第三者の著作物です（出典は「18. 参考文献・出典・著作権上の注意」参照）。
> 再配布の可否はまだ確認できていないため、このディレクトリは**ローカルの教材用**です。
> GitHub などで公開・配布する前に、必ず出版社の再配布条件を確認してください。

> 🛒 商品データはすべて**架空のもの**です。実際の EC サイト・決済システム・外部 API・データベースには接続しません。

---

## 1. 研究テーマと目的

**C5：ECサイトの商品検索・在庫管理**

EC サイト（電子商取引のショッピングサイト）を題材に、**商品検索・価格順ソート・在庫更新**を実装し、アルゴリズムとデータ構造の性能を比較します。
中心課題は、**リストの線形探索・ソート済みリストの二分探索・辞書による検索の性能差を実験的に調べる**ことです。

| | 問い |
| --- | --- |
| RQ1 | **商品検索アルゴリズムの性能差**：線形探索・二分探索・辞書検索で、商品数 N、検索時間、比較回数、検索の成功・失敗、索引の構築時間、メモリ使用量はどう違うか |
| RQ2 | **価格順ソートの計算量**：商品数 N とソート時間、アルゴリズムの違い、同じ価格の商品の扱い、ソート前後の整合性 |
| RQ3 | **在庫更新とデータ構造**：商品IDによる在庫の検索、増減、在庫不足の判定、更新の計算量、検索用データ構造との関係 |

学習段階に応じて、課題を2層に分けています。

- **Core Research（必須課題）**：商品IDの完全一致検索（3方式）、価格順ソート、在庫更新、N・Q を変えた性能比較
- **Advanced Research（発展課題）**：大規模データでの計算量評価、検索と更新の混合、複数条件検索、ソートアルゴリズムの比較、在庫の整合性とトランザクション

このリポジトリは、コマンドラインで動く小さな教材です。**完成済みの EC サイトやデータベースではありません。**

## 2. EC サイトの商品検索・在庫管理

EC サイトでは、次のような処理が大量に行われます。

- **商品検索**：商品ページを表示するとき、カートに入れるとき、注文を処理するときに、商品IDから商品の情報を探す
- **価格順ソート**：「価格の安い順」「高い順」で商品一覧を表示する
- **在庫更新**：購入されたら在庫を減らし、入荷したら増やす。在庫が足りなければ購入を断る

商品数が数十万、検索が1日に何百万回にもなると、**どのアルゴリズム・データ構造を使うか**で処理時間が大きく変わります。

## 3. 商品データの構造

各商品を辞書で表します（`products.py`）。

```python
{"id": 1001, "name": "Sticky Notes", "category": "Stationery", "price": 350, "stock": 40}
```

| 属性 | 意味 | 条件 |
| --- | --- | --- |
| `id` | 商品ID | 整数、重複なし |
| `name` | 商品名 | 文字列 |
| `category` | カテゴリ | 文字列 |
| `price` | 価格（円） | 0 以上の整数 |
| `stock` | 在庫数 | 0 以上の整数 |

### サンプルデータ（`data/sample_products.csv`）

架空の商品20件です。次の条件を満たしています。

- 商品ID（1001〜1020）は**重複せず**、**昇順に並んでいない**（1行目は 1007）
- **同じ価格の商品**が複数ある（120円 × 2、350円 × 2、700円 × 2、1200円 × 2、1800円 × 2）
- **在庫0の商品**がある（1010 Lunch Box、1016 Webcam、1019 Desk Lamp）
- 4つのカテゴリ（Stationery、Electronics、Kitchen、Furniture）

`products.load_products(path)` は、Python 標準の `csv` モジュールで読み込み、数値の列を整数に変換します。**数値でない値・負の価格・負の在庫数・重複した商品ID・列の不足**は `ValueError` になります。空のファイルや見出し行だけのファイルは、空のリストになります。

実験用には、`products.generate_products(n, seed)` で架空の商品を n 個作れます（商品IDは 1〜2n の範囲からばらばらに選ぶので、存在しない商品IDの検索も試せます）。

### データの持ち方（整合性のため）

商品の辞書そのものは**1つだけ**作り、3つの検索用の索引はどれも**同じ辞書を参照**します（コピーを作らない）。

```text
線形探索用  products[i]           ─┐
二分探索用  sorted_products[i]    ─┼─▶  商品の辞書 {"id": 1007, ..., "stock": 20}
辞書検索用  products_by_id[1007]  ─┘     （1つの商品につき、辞書は1つだけ）
```

在庫は、商品IDをキーとする辞書 `products_by_id` を**正本**として更新します。どの索引も同じ辞書を見ているので、**在庫を更新した後も、3つの検索方法で同じ在庫数が返ります**。商品情報のコピーを複数作って別々に更新すると、検索方法によって在庫数が違う、という不整合が起こります。

## 4. 線形探索（`search.linear_search`）

商品IDのリスト `ids` を**先頭から順に**調べます（教科書の `seq_search()`）。

```python
ids = search.build_linear_index(products)          # [1007, 1002, 1015, ...]（元の並び順）
search.linear_search(ids, products, 1013)          # ids の位置 i が分かれば products[i] を返す
```

- 前処理：ID のリストを作るだけ（O(N)）。**並べ替えは不要**です。
- 見つからない場合は、**全件を調べてから** `None` を返します（最悪の場合）。

## 5. 二分探索（`search.binary_search`）

商品IDの**昇順に並べた**リストを、範囲を半分ずつ絞り込んで調べます（教科書の `bin_search()`）。

```python
sorted_ids, sorted_products = search.build_sorted_index(products)
# sorted_ids      = [1001, 1002, 1003, ...]
# sorted_products = [商品1001, 商品1002, 商品1003, ...]  （同じ順に並べた商品）
search.binary_search(sorted_ids, sorted_products, 1013)
```

- **前処理として、商品IDの順に並べ替える必要があります**（`sorted()`、O(N log N)）。
- `sorted_ids[i]` と `sorted_products[i]` が同じ商品になるように、**キー列と商品データを同じ順に並べて**対応関係を保っています。
- 教科書の `bin_search()` は**空のリストを渡すと `IndexError`** になるため、`binary_search()` では先に空かどうかを確認しています。

## 6. 辞書検索（`search.dict_search`）

商品IDを**キー**とする辞書から取り出します。

```python
products_by_id = search.build_dict_index(products)   # {1007: 商品1007, 1002: 商品1002, ...}
search.dict_search(products_by_id, 1013)              # products_by_id.get(1013)
```

- **前処理として、辞書を作る必要があります**（平均 O(N)）。商品IDが重複していたら `ValueError` にします（後の商品で上書きされるのを防ぐため）。
- Python の辞書は内部で**ハッシュ表**を使っているので、キーから平均 O(1) で値を取り出せます（教科書 第3章のハッシュ法）。

### 検索と前処理

二分探索には**事前のソート**、辞書検索には**事前の辞書構築**が必要です。これらの前処理時間は、**検索時間と分けて**測ってください。
**1回だけ検索する場合**と、**同じ商品集合に何度も検索する場合**とでは、前処理を含めた総コストの比較結果が変わる可能性があります。

## 7. 価格順ソート（`sorting.py`）

並べる規則：**価格の順に並べ、同じ価格の商品は商品IDの小さい順**にします（毎回同じ結果になる）。

| 関数 | 方法 |
| --- | --- |
| `sort_by_price(products, descending=False)` | Python 標準の `sorted()`（キーは `(価格, 商品ID)`、降順は `(−価格, 商品ID)`） |
| `sort_by_price_insertion(products, descending=False)` | **教科書の挿入ソート**による例 |
| `sort_by_price_bubble`、`sort_by_price_selection` | **TODO（学生の課題）** |

どの関数も**新しいリストを返し**、元のリストの並び順は変えません。

### 教科書のソート関数を商品に使う方法

教科書のソート関数は、リストの要素どうしを `>` で比べて**その場で並べ替え**ます。商品の辞書は `>` で比べられないので、そのまま渡すことはできません。そこで `sort_by_price_insertion()` では、

1. 各商品から **`(価格, 商品ID)` の組**を作る
2. 組のリストを教科書の `insertion_sort()` で並べ替える
3. 並んだ組の商品IDから、商品の辞書を取り出して並べる

という手順にしています。組に商品IDを入れているので、**価格と商品の対応が失われません**。また、価格が同じなら商品IDで順序が決まります。

> **注意**：「商品情報の価格順ソート」と、「価格だけの数値リストのソート実験」は別のものです。価格だけを並べ替えると、どの価格がどの商品のものか分からなくなります。

## 8. 在庫更新（`inventory.py`）

| 関数 | 内容 | 失敗したとき |
| --- | --- | --- |
| `get_stock(products_by_id, product_id)` | 現在の在庫数 | 商品がなければ `KeyError` |
| `purchase(products_by_id, product_id, quantity)` | 購入：在庫を減らす。成功なら `True` | 在庫不足なら **`False` を返し、在庫は変更しない** |
| `restock(products_by_id, product_id, quantity)` | 入荷：在庫を増やす | — |

- 数量は**正の整数**だけを受け付けます（0、負の数、小数などは `ValueError`）。
- 商品が存在しなければ `KeyError` です。
- 在庫不足のときは何も変更しないので、**在庫が負になることはありません**。

### 在庫更新とデータ構造

在庫を更新するには、まず**商品IDから更新する商品を見つける**必要があります。この「探す」部分のコストは検索方法によって変わり、「在庫数を書き換える」部分は O(1) です。

| 商品の特定に使う方法 | 1回の更新の計算量 |
| --- | --- |
| 線形探索 | O(N)（探す） + O(1)（書き換える） |
| 二分探索 | O(log N) + O(1) |
| 辞書検索 | 平均 O(1) + O(1) |

**既存の商品の在庫を変えるだけなら、商品IDの索引を作り直す必要はありません**（商品IDも並び順も変わらないから）。一方、**商品の追加・削除や商品IDの変更**をする場合は、すべての索引（ID のリスト、並べ替えたリスト、辞書）を更新する必要があります（Advanced B）。特に、ソート済みリストに商品を追加するには、正しい位置に挿入するために要素をずらす必要があり、O(N) かかります。

## 9. 理論計算量の比較

商品数を **N**、検索回数を **Q** とします。

| 方法 | 前処理 | 1回の検索 | Q 回の検索を含む総コスト |
| --- | --- | --- | --- |
| 線形探索 | なし（ID リストの作成 O(N)） | **O(N)** | **O(QN)** |
| 二分探索 | ソート：**O(N log N)**（`sorted()` の場合） | **O(log N)** | **O(N log N + Q log N)** |
| 辞書検索 | 辞書構築：**平均 O(N)** | **平均 O(1)** | **平均 O(N + Q)** |

- 二分探索の前処理に**教科書のバブルソート・選択ソート・挿入ソート**を使うと、最悪 **O(N²)** になります。どのソート方法を使ったかを必ず明記してください（このリポジトリの `build_sorted_index()` は `sorted()` を使っています）。
- 辞書の O(1) は**平均**の値です。多くのキーが同じハッシュ値になる（**ハッシュ衝突**が多い）と、最悪の場合は1回の検索が O(N) になり得ます。Python の辞書は衝突をうまく処理するよう設計されていますが、最悪の場合が存在することは知っておきましょう。
- **Q が小さい**（例：1回だけ検索する）と、前処理のコストが目立ち、線形探索が最も速いこともあります。**Q が大きい**と、前処理のコストを多くの検索で分け合えるので、二分探索や辞書が有利になります。前処理を無視して「二分探索や辞書は常に速い」と結論しないでください。
- Big-O は漸近的な評価であり、実測時間そのものではありません。

## 10. 教科書との関連

教科書：柴田望洋 著『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』SBクリエイティブ

### 実際に利用したコード（`textbook/` にコピーして import）

| ファイル | 内容 | 用途 |
| --- | --- | --- |
| `textbook/ssearch_while.py`（第3章 `chap03/ssearch_while.py`） | 線形探索 `seq_search(a, key)`：見つかれば添字、なければ `-1` | `search.linear_search()` |
| `textbook/bsearch.py`（第3章 `chap03/bsearch.py`） | 二分探索 `bin_search(a, key)`：見つかれば添字、なければ `-1`（**空リストでは `IndexError`**） | `search.binary_search()` |
| `textbook/insertion_sort.py`（第6章 `chap06/insertion_sort.py`） | 単純挿入ソート `insertion_sort(a)`（in-place、戻り値 `None`） | `sorting.sort_by_price_insertion()` |
| `textbook/bubble_sort1.py`（第6章 `chap06/bubble_sort1.py`） | 単純交換ソート `bubble_sort(a)` | **学生の課題**（`sorting.sort_by_price_bubble` の TODO、Advanced D）で使う |
| `textbook/selection_sort.py`（第6章 `chap06/selection_sort.py`） | 単純選択ソート `selection_sort(a)` | **学生の課題**（`sorting.sort_by_price_selection` の TODO、Advanced D）で使う |

- 5ファイルとも、教科書のサンプルコードを**そのままコピー**したものです（SHA-256で原本との一致を確認済み）。**編集しないでください。**
- 各ファイル末尾のキーボード入力で試す部分は `if __name__ == '__main__':` の中にあるので、import しても実行されません。
- 教科書のソート関数は `>`・`<` で要素を比べるので、`(価格, 商品ID)` の組のリストにもそのまま使えます（7章）。

### 参考にしたコード（コピー・import はしていない）

| ファイル | 本課題との関係 |
| --- | --- |
| 第3章 `chap03/chained_hash.py`、`open_hash.py` | ハッシュ法（チェイン法・オープンアドレス法）。Python の辞書の仕組みと、ハッシュ衝突の理解に使う。辞書検索には Python 標準の `dict` を使うため、コピーしていない |
| 第6章 `chap06/binary_insort.py` ほか | `bisect` を使った二分挿入、改良版のソート。Advanced B（ソート済みの索引への商品の追加）、Advanced D の参考 |

## 11. ファイル構成

```text
c5-ecommerce-search-inventory/
├── README.md                  この説明
├── .gitignore
├── starter.py                 Demo A（検索）・Demo B（価格順ソート）・Demo C（在庫更新）
├── products.py                商品データの読み込み（load_products）と生成（generate_products）
├── search.py                  線形探索・二分探索・辞書検索と、それぞれの索引の作成
├── sorting.py                 価格順ソート（sorted 版、挿入ソート版、TODO：バブル・選択）
├── inventory.py               在庫の確認・購入・入荷
├── benchmark.py               性能比較の入口（1回だけの測定例、TODO付き）
├── data/
│   └── sample_products.csv    架空の商品20件
├── textbook/                  教科書のサンプルコード（編集しない）
│   ├── __init__.py
│   ├── ssearch_while.py
│   ├── bsearch.py
│   ├── bubble_sort1.py
│   ├── selection_sort.py
│   └── insertion_sort.py
└── tests/
    ├── test_products.py
    ├── test_search.py
    ├── test_sorting.py         （バブル・選択ソート版のテストは未実装の間スキップ）
    └── test_inventory.py
```

## 12. 実行方法

このディレクトリ（`c5-ecommerce-search-inventory/`）で実行してください。Python 標準ライブラリだけで動作します。

```bash
python3 starter.py
python3 -m unittest discover -s tests -v
python3 benchmark.py        # 性能比較の入口（1回だけの測定例）
```

`starter.py` の実行結果（抜粋）：

```text
--- Demo A：商品検索 ---
商品数: 20
商品ID 1013 を検索
  線形探索: 1013 Headphones / Electronics / 4800円 / 在庫 5
  二分探索: 1013 Headphones / Electronics / 4800円 / 在庫 5
  辞書検索: 1013 Headphones / Electronics / 4800円 / 在庫 5
  3方式の結果が一致: True
...
--- Demo B：価格順ソート（同じ価格は商品IDの小さい順） ---
価格の安い順 上位5件:
  1002 Ballpoint Pen / Stationery / 120円 / 在庫 50
  1006 Eraser / Stationery / 120円 / 在庫 60
  ...
--- Demo C：在庫更新 ---
商品ID 1007 の在庫: 20
3個購入 → 成功、在庫: 17
100個購入 → 在庫不足（在庫は変更しない）、在庫: 17
10個入荷 → 在庫: 27
3つの検索方法で得た在庫数: [27, 27, 27]  一致: True
```

テスト結果には `skipped=1` と表示されます。これは、学生が実装するバブルソート版・選択ソート版のテストが未実装のためスキップされているものです。実装すると自動的に実行されます。

## 13. Core Research：必須課題

すべてのチームが取り組む課題です。

1. **商品データを読み込む。**（`products.load_products`）
2. **線形探索で商品を検索する。**
3. **二分探索で商品を検索する。**
4. **辞書で商品を検索する。**
5. **3方式の検索結果を比較する。**（存在しない商品IDも）
6. **商品を価格順にソートする。**（バブルソート版・選択ソート版の実装を含む）
7. **商品の在庫を更新する。**
8. **商品数 N を変更して検索時間を比較する。**（`benchmark.py` の TODO）
9. **検索回数 Q を変更して、前処理を含めた総コストを比較する。**
10. **結果を表・グラフにまとめる。**
11. **理論計算量と実測結果を考察する。**

## 14. Advanced Research：発展課題

必須課題を終えたチームが挑戦する課題です。**Advanced A〜E のうち、チームの能力と時間に応じて1つ以上を選択**してください。すべてを実装する必要はありません。

### Advanced A：商品数と検索アルゴリズムの計算量

**目的**：商品数 N の増加に伴う検索時間の変化を定量的に評価する。

1. N = 100、1,000、10,000、100,000 の商品データを生成する（`products.generate_products`、架空の商品ID）。
2. 線形探索・二分探索・辞書検索を比較する。
3. 検索成功・失敗の両方を測定する。
4. 検索回数 Q を変更する。
5. 前処理時間を含む総コストを比較する（どの Q から順位が入れ替わるか）。
6. 理論計算量と実測結果を比較する（比較回数を数える版の関数を作るとよい）。

### Advanced B：検索と在庫更新の混合ワークロード

**目的**：検索だけでなく、在庫更新が頻繁に起こる状況を分析する。

1. 検索操作と在庫更新操作を組み合わせる。
2. 検索と更新の比率を変更する。
3. 線形探索・二分探索・辞書検索の総処理時間を比較する。
4. 商品の追加・削除を発展的に実装する。
5. 索引の更新コストを測定する（ソート済みリストへの挿入、辞書への追加）。
6. 検索性能と更新性能のトレードオフを考察する。

> **商品IDによる検索用の索引**と、**価格順に並べるための索引**は別物です。在庫の更新ではどちらも作り直す必要はありませんが、価格の変更では価格順の索引の更新が必要になります。区別して考えてください。

### Advanced C：商品名・カテゴリ・価格帯検索

**目的**：商品IDの完全一致検索から、複数条件による検索へ発展させる。

1. 商品名の部分一致検索を実装する（例：`"Mouse"` で Wireless Mouse と Mouse Pad）。
2. カテゴリ別検索を実装する。
3. 価格帯による絞り込みを実装する（価格順に並べたリストで、二分探索を使って範囲の端を探す方法も考えられる）。
4. 複数条件を組み合わせる。
5. 検索結果を価格順に並べる。
6. 検索条件と処理時間の関係を調べる。

> 辞書検索の**平均 O(1) は、商品IDの完全一致検索についての性質**です。「名前に `"Mouse"` を含む商品」のような部分一致検索には、そのままは使えません（すべての商品名を調べる必要がある）。カテゴリ別の辞書を作るなど、検索条件に合わせた索引を考えてみましょう。

### Advanced D：ソートアルゴリズムの比較

**目的**：価格順ソートでのアルゴリズムの違いを調べる。

1. バブルソートを実装する（`sorting.sort_by_price_bubble`）。
2. 選択ソートを実装する（`sorting.sort_by_price_selection`）。
3. 挿入ソートを使う（`sorting.sort_by_price_insertion`）。
4. Python 標準の `sorted` と比較する。
5. 商品数 N を変更する。
6. すでにソート済みのデータを試す。
7. 逆順のデータを試す。
8. 同じ価格の商品を多く含むデータを試す。
9. 処理時間と比較回数を分析する。

教科書のサンプルコード（`textbook/` の3つのソート関数）を、**改変せずに直接**使ってください。比較回数を数えたい場合は、教科書コードを参考にして自分たちのファイルに「数える版」を作ります。

### Advanced E：在庫整合性とトランザクション

**目的**：EC サイトの在庫管理に必要なデータ整合性を理解する。

1. 在庫不足の購入を拒否する。
2. 同じ商品に連続して購入処理を行う。
3. 商品の在庫が負にならないことを検証する。
4. 複数の商品を同時に購入する処理を設計する（カートの一括購入）。
5. 途中で購入に失敗した場合の**ロールバック**を検討する（`inventory.py` の TODO）。
6. **同時アクセス**による在庫の不整合を調査する（例：2人がほぼ同時に最後の1個を買おうとしたら？）。

発展的には、データベースの**トランザクション**や**排他制御**の必要性を考察してください。

> ⚠️ 実際の決済処理は実装しないでください。

## 15. 実験条件と評価指標

### 記録すべき実験条件

- PC 環境（CPU、メモリ）、OS、Python のバージョン
- 商品数 N、検索回数 Q、検索の成功率、乱数シード
- 前処理に使ったソート方法
- 測定回数と、平均値・中央値などの集計方法

### 評価指標

| 指標 | 内容 |
| --- | --- |
| 検索時間 | Q 回の検索の合計時間（前処理は含めない） |
| 前処理時間 | ソート・辞書構築の時間 |
| 総コスト | 前処理時間 + 検索時間 |
| 比較回数 | 何を1回と数えたかを明記する |
| 検索の成功・失敗 | 成功と失敗を分けて測る（失敗は線形探索の最悪の場合） |
| メモリ使用量 | `tracemalloc` などで測る（索引ごとの追加メモリ） |
| 正しさ | 3方式の結果が一致するか |

### 公平な比較の条件

- **同じ商品集合・同じ検索キー・同じ検索回数・同じ成功率**を使う。
- **前処理時間と検索時間を区別**する。
- **複数回測定**する。
- 商品データの生成時間は検索時間に含めない。

## 16. GitHub を用いたチーム開発

チームで GitHub を使って研究を進めてください（公開設定については冒頭の注意を参照）。

- **役割分担を明確にする**：例）検索担当、ソート担当、在庫管理担当、性能測定担当、README・考察担当
- **GitHub Issues でタスク管理**：やること（実装・実験・調べ物・不具合）を Issue に登録し、担当者を割り当てる
- **branch を分けて実装**：例）`feature/bubble-sort-by-price`、`feature/category-search`、`experiment/search-n-q`
- **Pull Request でコードレビュー**：変更は Pull Request で提出し、他のメンバーがレビューしてから merge する。テストが通ることを確認する
- **README への追記**：実験条件・結果・考察を README（または別の報告ファイル）に追記していく
- **最終成果物の Release**：研究が完成したら、成果物をまとめて Release（例：`v1.0`）として公開する

## 17. 成果物と提出方法

提出する成果物：

1. **コード**：バブル・選択ソート版、実験用プログラム、追加した機能（テストが通ること。スキップされていたテストも通ること）
2. **実験結果**：表・グラフ（実験条件を併記）
3. **報告**（README への追記、または別の報告ファイル）
   - Core Research 1〜11 の結果と考察
   - 選択した Advanced Research のテーマ、方法、結果、考察
   - RQ1〜RQ3 に対するチームとしての答え
   - 参考にした文献・Web ページの出典
4. **GitHub の記録**：Issue、branch、Pull Request、Release

提出方法（期限・提出先）は、授業で指示します。

## 18. 参考文献・出典・著作権上の注意

### 教科書コード

- 出典：柴田望洋 著『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』SBクリエイティブ
  - 第3章「探索」：`chap03/ssearch_while.py`、`chap03/bsearch.py`
  - 第6章「ソート」：`chap06/bubble_sort1.py`、`chap06/selection_sort.py`、`chap06/insertion_sort.py`
- 参考にしただけのファイル：10章の表を参照（このリポジトリにはコピーしていません）
- 教科書コードは第三者の著作物です。公開再配布の許諾はまだ確認していません。**将来 GitHub で配布する前に、再配布条件を必ず確認してください。**

### その他

- Python 標準ライブラリ `csv`、`bisect`、`time`、`tracemalloc` のドキュメント
- Python 公式 Wiki "TimeComplexity"（list・dict の操作の計算量）

### サンプルデータ

- `data/sample_products.csv` は、この教材のために作成した**架空のデータ**です。

研究で他の文献や Web ページを使った場合は、出典と参照日を記録してください。

<!-- textbook-setup-section -->

## 教科書サンプルコードの準備（GitHub から clone した場合）

教科書：柴田望洋『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』SB クリエイティブ

再配布の許諾が確認できていないため、教科書のサンプルコードは**この GitHub リポジトリには含まれていません**。
clone した直後は `textbook/` に `__init__.py` しかなく、`starter.py` と unittest は `ModuleNotFoundError: No module named 'textbook....'` で止まります。
次の手順で、各自が教科書のコードを配置してください。

### 1. ダウンロード

1. 指定教科書（第2版）を手元に用意する。
2. 教科書に案内されている公式サイト（SB クリエイティブの書籍ページ <https://www.sbcr.jp/product/4815637217/>、または教科書に記載された案内）から、サンプルソースコードを各自ダウンロードする。
3. ダウンロードしたファイルを展開する。展開したフォルダ（以下 `<展開したフォルダ>`）には `chap01/`〜`chap09/` があります。
4. 公式サイトの利用条件を守って使ってください。

### 2. 必要なファイルと配置先

原本の `chapXX/` の階層は作らず、`textbook/` の直下にファイル名を変えずに置きます（授業の PC と同じ構成）。ファイルの中身は変更しないでください。

| 原本（展開したフォルダ内） | 配置先（リポジトリのルートから） | 使っているコード |
| --- | --- | --- |
| `chap03/bsearch.py` | `c5-ecommerce-search-inventory/textbook/bsearch.py` | `search.py` |
| `chap06/bubble_sort1.py` | `c5-ecommerce-search-inventory/textbook/bubble_sort1.py` | — |
| `chap06/insertion_sort.py` | `c5-ecommerce-search-inventory/textbook/insertion_sort.py` | `sorting.py` |
| `chap06/selection_sort.py` | `c5-ecommerce-search-inventory/textbook/selection_sort.py` | — |
| `chap03/ssearch_while.py` | `c5-ecommerce-search-inventory/textbook/ssearch_while.py` | `search.py` |

### 3. 配置後のディレクトリ構成

```text
c5-ecommerce-search-inventory/
└── textbook/
    ├── __init__.py          （リポジトリに含まれる）
    ├── bsearch.py           （各自で配置）
    ├── bubble_sort1.py      （各自で配置）
    ├── insertion_sort.py    （各自で配置）
    ├── selection_sort.py    （各自で配置）
    └── ssearch_while.py     （各自で配置）
```

### 4. コピーと確認のコマンド例

```bash
cd c5-ecommerce-search-inventory
SRC="<展開したフォルダ>"        # 各自の環境に合わせる

cp -i "$SRC/chap03/bsearch.py" textbook/bsearch.py
cp -i "$SRC/chap06/bubble_sort1.py" textbook/bubble_sort1.py
cp -i "$SRC/chap06/insertion_sort.py" textbook/insertion_sort.py
cp -i "$SRC/chap06/selection_sort.py" textbook/selection_sort.py
cp -i "$SRC/chap03/ssearch_while.py" textbook/ssearch_while.py

# 原本とコピーの SHA-256 が一致することを確認する
sha256sum "$SRC/chap03/bsearch.py" textbook/bsearch.py
sha256sum "$SRC/chap06/bubble_sort1.py" textbook/bubble_sort1.py
sha256sum "$SRC/chap06/insertion_sort.py" textbook/insertion_sort.py
sha256sum "$SRC/chap06/selection_sort.py" textbook/selection_sort.py
sha256sum "$SRC/chap03/ssearch_while.py" textbook/ssearch_while.py

python3 starter.py                          # 実行確認
python3 -m unittest discover -s tests -v    # テスト
```

配置した教科書のコードは、リポジトリ直下の `.gitignore` によって Git の追跡対象から除外されます（`git status` に表示されなければ正常です）。
`git add -f` などで教科書のコードを commit・push しないでください。
