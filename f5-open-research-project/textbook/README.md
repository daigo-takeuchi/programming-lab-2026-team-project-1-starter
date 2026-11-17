# textbook/：教科書サンプルコードの参照方法

教科書：柴田望洋『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』SB クリエイティブ

原本の入手：教科書の公式サイト（SB クリエイティブの書籍ページ <https://www.sbcr.jp/product/4815637217/>、または教科書に記載された案内）から、各自でサンプルソースコードをダウンロードして展開します。教科書のコードはこのリポジトリには含まれていません。

展開したフォルダ（以下 `<展開したフォルダ>`。授業の PC では次の構成）：

```text
<展開したフォルダ>/
├── chap01/  基本的なアルゴリズム（分岐・繰り返し）
├── chap02/  データ構造と配列（最大値、反転、基数変換、素数）
├── chap03/  探索（線形探索・番兵法・2 分探索・ハッシュ法）
├── chap04/  スタックとキュー（固定長スタック・固定長キュー・deque 版）
├── chap05/  再帰（階乗・最大公約数・ハノイの塔・8 王妃・メモ化）
├── chap06/  ソート（単純交換・単純選択・単純挿入・シェル・クイック・マージ・ヒープ・度数）
├── chap07/  文字列探索（力まかせ法・KMP 法・Boyer-Moore 法）
├── chap08/  線形リスト（配列カーソル版・連結リスト・循環重連結リスト）
└── chap09/  2 分探索木
```

## このフォルダの方針

- **F5 は研究テーマが未定なので、初期状態では教科書のコードをコピーしていません。**
  - 初期デモの線形探索・二分探索（`algorithms/`）は、教科書第 3 章の考え方を参考に、このリポジトリ用に書いたものです。
- チームのテーマが決まって、教科書のコードを**そのまま**使いたい場合は、**使用目的がはっきりした最小限のファイルだけ**をこのフォルダにコピーします。
- **改良する場合は、原本とは別のファイル**（例：`algorithms/my_quick_sort.py`）に書きます。`textbook/` のコピーは改変しません。

## 教科書のコードをコピーする手順

```bash
cd f5-open-research-project
SRC="<展開したフォルダ>"          # 例：SRC=~/Downloads/<展開したフォルダ名>（各自の環境に合わせる）

cp "$SRC/chap06/quick_sort1.py" textbook/            # 例：クイックソートを使う
touch textbook/__init__.py                           # import できるようにする（初回だけ）

sha256sum "$SRC/chap06/quick_sort1.py" textbook/quick_sort1.py   # 2 つの値が一致することを確認する
```

```python
from textbook.quick_sort1 import quick_sort          # コピーした原本をそのまま import する
```

- コピーしたファイルと用途を、README の「16. 教科書サンプルコードの活用」と `docs/experiment_log.md` に書きます。
- 対話入力（`input()`）を伴うファイルの扱い：
  - `if __name__ == '__main__':` の中だけで入力するファイルは、import しても入力待ちになりません。
  - ファイルの最上位で入力・表示するファイル（下の表で「不可」）は、import した時点で入力待ちになります。関数の考え方を参考にして、自分のファイルに書き直してください。
- `*_test.py` は、同じフォルダの別ファイル（例：`fixed_queue_test.py` は `fixed_queue.py`）を import します。対話メニューで動かすサンプルなので、研究のコードからは import しないでください。

## ⚠️ 著作権・再配布の注意

- 教科書のサンプルコードは著作物です。**公開再配布の条件は確認できていません。**
- **教科書のコードを含むリポジトリを、公開 GitHub に無条件でアップロード（push）しないでください。**
  - 非公開リポジトリを使う。
  - または、`.gitignore` に `textbook/*.py` を追加して、各自が原本からコピーする。

## 教科書サンプルコードの一覧（第 2 章〜第 9 章）

`import` 列の意味は次のとおりです。

| 値 | 意味 |
| --- | --- |
| 可 | 関数・クラスがあり、import しても入出力が起きない |
| 不可 | import した時点で入力・表示が起きる |
| — | 関数・クラスがない（実行して動きを見るサンプル） |

この列はスクリプトで自動判定したものです。使う前に、ファイルの中身を確認してください。

### chap02

| ファイル | 内容（先頭のコメント） | 定義（関数・クラス） | import |
| --- | --- | --- | --- |
| `chap02/builtin_max.py` | シーケンスの要素の最大値を表示する（組込みのmax関数を利用） | — | — |
| `chap02/card_conv.py` | 読み込んだ10進整数を2進数～36進数へと基数変換して表示 | `card_conv` | 可 |
| `chap02/card_conv_verbose.py` | 読み込んだ10進整数を2進数～36進数へと基数変換して表示（変換過程を詳細に表示） | `card_conv` | 可 |
| `chap02/list1.py` | リストの全要素を走査（要素数を事前に取得） | — | — |
| `chap02/list2.py` | リストの全要素をenumerate関数で走査 | — | — |
| `chap02/list2str.py` | リストの文字列化と表示 | — | — |
| `chap02/list3.py` | リストの全要素をenumerate関数で走査（1からカウント） | — | — |
| `chap02/list4.py` | リストの全要素を走査（インデックス値を使わない） | — | — |
| `chap02/list_element.py` | リストの要素の型が揃う必要がないことを確認 | — | — |
| `chap02/list_tuple.py` | リストとタプルの生成 | — | — |
| `chap02/max.py` | シーケンスの要素の最大値を表示する | `max_of` | 可 |
| `chap02/max_error.py` | 配列の要素の最大値を表示する（エラー） | — | — |
| `chap02/max_of_test.py` | 配列の要素の最大値を求めて表示（タプル／文字列／文字列のリスト） | — | — |
| `chap02/max_of_test_input.py` | 配列の要素の最大値を求めて表示（要素の値を読み込む） | — | — |
| `chap02/max_of_test_randint.py` | 配列の要素の最大値を求めて表示（要素の値を乱数で生成） | — | — |
| `chap02/pass_list.py` | リストの任意の要素の値を更新する | `change` | 不可（import 時に入出力） |
| `chap02/prime1.py` | 1,000以下の素数を列挙（第１版） | — | — |
| `chap02/prime2.py` | 1,000以下の素数を列挙（第２版） | — | — |
| `chap02/prime3.py` | 1,000以下の素数を列挙（第３版） | — | — |
| `chap02/prime3a.py` | 1,000以下の素数を列挙（第３版の別解：配列primeの要素数を事前に決定しない） | — | — |
| `chap02/reverse.py` | ミュータブルなシーケンスの要素の並びを反転 | `reverse_array` | 可 |
| `chap02/reverse1a.py` | ミュータブルなシーケンスの要素の並びを反転（変数nを使わない） | `reverse_array` | 可 |
| `chap02/reverse2.py` | 配列（リスト）の要素の並びを反転（reverseメソッド） | — | — |
| `chap02/reverse3.py` | 配列（リスト）の要素の並びを反転（reversed関数＋list関数） | — | — |
| `chap02/sum_1ton.py` | 1からnまでの整数の総和を求めるプログラム | `sum_1ton` | 不可（import 時に入出力） |
| `chap02/total.py` | ５人の点数の合計点・平均点を表示 | — | — |
| `chap02/tuple1.py` | タプルの全要素を走査（要素数を事前に取得） | — | — |
| `chap02/tuple2.py` | タプルの全要素をenumerate関数で走査 | — | — |
| `chap02/tuple3.py` | タプルの全要素をenumerate関数で走査（1からカウント） | — | — |
| `chap02/tuple4.py` | タプルの全要素を走査（インデックス値を使わない） | — | — |

### chap03

| ファイル | 内容（先頭のコメント） | 定義（関数・クラス） | import |
| --- | --- | --- | --- |
| `chap03/bsearch.py` | ２分探索 | `bin_search` | 可 |
| `chap03/bsearch_ve.py` | ２分探索（探索失敗時にValueErrorを送出） | `bin_search` | 可 |
| `chap03/bsearch_verbose.py` | ２分探索（途中経過を表示） | `bin_search` | 可 |
| `chap03/chained_hash.py` | チェイン法によるハッシュ | `Node`, `ChainedHash` | 可 |
| `chap03/chained_hash_test.py` | チェイン法を実現するハッシュクラスChainedHashの利用例 | `select_menu` | 不可（import 時に入出力） |
| `chap03/chained_hash_test2.py` | チェイン法を実現するハッシュクラスChainedHashの利用例（その２） | `select_menu` | 不可（import 時に入出力） |
| `chap03/open_hash.py` | オープンアドレス法によるハッシュ | `Status`, `Bucket`, `OpenHash` | 可 |
| `chap03/open_hash_test.py` | オープンアドレス法によるハッシュの利用例 | `select_menu` | 不可（import 時に入出力） |
| `chap03/open_hash_test2.py` | オープンアドレス法によるハッシュの利用例（その２） | `select_menu` | 不可（import 時に入出力） |
| `chap03/ssearch_for.py` | 線形探索（for文） | `seq_search` | 可 |
| `chap03/ssearch_sentinel.py` | 線形探索（番兵法） | `seq_search` | 可 |
| `chap03/ssearch_sentinel2.py` | 線形探索（番兵法：別解） | `seq_search` | 可 |
| `chap03/ssearch_test1.py` | 線形探索を行う関数seq_searchの利用例（その１） | — | — |
| `chap03/ssearch_test2.py` | 線形探索を行う関数seq_searchの利用例（その２） | — | — |
| `chap03/ssearch_ve.py` | 線形探索（for文：探索失敗時にValueErrorを送出） | `seq_search` | 可 |
| `chap03/ssearch_while.py` | 線形探索（while文） | `seq_search` | 可 |

### chap04

| ファイル | 内容（先頭のコメント） | 定義（関数・クラス） | import |
| --- | --- | --- | --- |
| `chap04/fixed_queue.py` | 固定長キュークラス | `FixedQueue` | 可 |
| `chap04/fixed_queue_test.py` | 固定長キュークラスFixedQueueの利用例 | `select_menu` | 不可（import 時に入出力） |
| `chap04/fixed_stack.py` | 固定長スタッククラスFixedStack | `FixedStack` | 可 |
| `chap04/fixed_stack_test.py` | 固定長スタッククラスFixedStackの利用例 | `select_menu` | 不可（import 時に入出力） |
| `chap04/last_elements.py` | 好きな個数だけ値を読み込んで要素数nの配列に最新（最後）のn個を格納 | — | — |
| `chap04/queue.py` | 固定長キュークラス（collections.dequeを利用） | `Queue` | 可 |
| `chap04/queue_test.py` | 固定長キューQueの利用例 | `select_menu` | 不可（import 時に入出力） |
| `chap04/stack.py` | 固定長スタッククラスStack（collections.dequeを利用） | `Stack` | 可 |
| `chap04/stack_test.py` | 固定長スタッククラスStackの利用例 | `select_menu` | 不可（import 時に入出力） |

### chap05

| ファイル | 内容（先頭のコメント） | 定義（関数・クラス） | import |
| --- | --- | --- | --- |
| `chap05/8queen.py` | ８王妃問題 | `set` | 可 |
| `chap05/8queen2.py` | ８王妃問題（盤面と王妃を記号文字□と■で表示） | `set` | 可 |
| `chap05/8queen_b.py` | 各列に１個の王妃を配置する組合せを再帰的に列挙 | `put`, `set` | 可 |
| `chap05/8queen_bb.py` | 各行・各列に１個の王妃を配置する組合せを再帰的に列挙 | `set` | 可 |
| `chap05/factorial.py` | 非負の整数の階乗値を求める | `factorial` | 可 |
| `chap05/factorial2.py` | 非負の整数の階乗値を求める（別解：条件演算子） | `factorial` | 可 |
| `chap05/factorial_ve.py` | 非負の整数の階乗値を求める（nが負であればValueErrorを送出） | `factorial` | 可 |
| `chap05/gcd.py` | ユークリッドの互除法によって最大公約数を求める | `gcd` | 可 |
| `chap05/hanoi.py` | ハノイの塔 | `move` | 不可（import 時に入出力） |
| `chap05/math_factorial.py` | 非負の整数の階乗値を求める（math.factorialを利用） | — | — |
| `chap05/math_gcd1.py` | 最大公約数を求める（math.gcdを利用） | — | — |
| `chap05/math_gcd2.py` | 多値の最大公約数を求める | — | — |
| `chap05/recur1.py` | 真に再帰的な関数 | `recur` | 不可（import 時に入出力） |
| `chap05/recur1_count.py` | 真に再帰的な関数（呼び出し回数をカウント） | `recur` | 不可（import 時に入出力） |
| `chap05/recur1a.py` | 真に再帰的な関数（末尾再帰を除去） | `recur` | 不可（import 時に入出力） |
| `chap05/recur1b.py` | 真に再帰的な関数（再帰を除去） | `recur` | 不可（import 時に入出力） |
| `chap05/recur2.py` | 真に再帰的な関数（呼出しの順序が逆） | `recur` | 不可（import 時に入出力） |
| `chap05/recur_memo.py` | 真に再帰的な関数recurをメモ化して実現 | `recur` | 不可（import 時に入出力） |
| `chap05/recur_memo_count.py` | 真に再帰的な関数recurをメモ化して実現（呼び出し回数をカウント） | `recur` | 不可（import 時に入出力） |
| `chap05/stack.py` | 固定長スタッククラスStack（collections.dequeを利用） | `Stack` | 可 |

### chap06

| ファイル | 内容（先頭のコメント） | 定義（関数・クラス） | import |
| --- | --- | --- | --- |
| `chap06/binary_insertion_sort.py` | ２分挿入ソート | `binary_insertion_sort` | 可 |
| `chap06/binary_insort.py` | ２分挿入ソート（bisect.insortを利用） | `binary_insertion_sort` | 可 |
| `chap06/bubble_sort1.py` | 単純交換ソート | `bubble_sort` | 可 |
| `chap06/bubble_sort1_verbose.py` | 単純交換ソート《ソート過程を表示》 | `bubble_sort_verbose` | 可 |
| `chap06/bubble_sort2.py` | 単純交換ソート（第２版：交換回数による打切り） | `bubble_sort` | 可 |
| `chap06/bubble_sort2_verbose.py` | 単純交換ソート（第２版：交換回数による打切り）《ソート過程を表示》 | `bubble_sort` | 可 |
| `chap06/bubble_sort3.py` | 単純交換ソート（第３版：走査範囲を限定） | `bubble_sort` | 可 |
| `chap06/bubble_sort3_verbose.py` | 単純交換ソート（第３版：走査範囲を限定）《ソート過程を表示》 | `bubble_sort` | 可 |
| `chap06/counting_sort.py` | 度数ソート | `fsort`, `counting_sort` | 可 |
| `chap06/heap_sort.py` | ヒープソート | `heap_sort` | 可 |
| `chap06/heap_sort_heapq.py` | ヒープソート（heapq.pushとheapq.popを利用） | `heap_sort` | 可 |
| `chap06/insertion_sort.py` | 単純挿入ソート | `insertion_sort` | 可 |
| `chap06/merge.py` | ソートずみ配列のマージ | `merge_sorted_list` | 可 |
| `chap06/merge_heapq.py` | ソートずみ配列のマージ（heap.mergeを利用） | — | — |
| `chap06/merge_ls.py` | ソートずみ配列のマージ（list関数とsorted関数を組み合わせる） | — | — |
| `chap06/merge_sort.py` | マージソート | `merge_sort` | 可 |
| `chap06/merge_sort_heapq.py` | マージソート（heapq.mergeを利用） | `merge_sort` | 可 |
| `chap06/partition.py` | 配列の分割 | `partition` | 可 |
| `chap06/quick_sort1.py` | クイックソート | `qsort`, `quick_sort` | 可 |
| `chap06/quick_sort1_non_recur.py` | クイックソート（非再帰版） | `qsort`, `quick_sort` | 可 |
| `chap06/quick_sort1_verbose.py` | クイックソート（配列の分割過程を表示） | `qsort`, `quick_sort` | 可 |
| `chap06/quick_sort2.py` | クイックソート（第２版） | `sort3`, `insertion_sort`, `qsort`, `quick_sort` | 可 |
| `chap06/selection_sort.py` | 単純選択ソート | `selection_sort` | 可 |
| `chap06/shaker_sort.py` | シェーカーソート（双方向バブルソート） | `shaker_sort` | 可 |
| `chap06/shaker_sort_verbose.py` | シェーカーソート（双方向バブルソート）《ソート過程を表示》 | `shaker_sort` | 可 |
| `chap06/shell_sort1.py` | シェルソート | `shell_sort` | 可 |
| `chap06/shell_sort2.py` | シェルソート（第２版：h = …, 40, 13, 4, 1） | `shell_sort` | 可 |
| `chap06/sorted_sort.py` | sorted関数によるソート | — | — |
| `chap06/stack.py` | 固定長スタッククラスStack（collections.dequeを利用） | `Stack` | 可 |

### chap07

| ファイル | 内容（先頭のコメント） | 定義（関数・クラス） | import |
| --- | --- | --- | --- |
| `chap07/bf_match.py` | 力まかせ法による文字列探索 | `bf_match` | 可 |
| `chap07/bm_match.py` | Boyer-Moore法による文字列探索（対象は0～255の文字） | `bm_match` | 可 |
| `chap07/kmp_match.py` | KMP法による文字列探索 | `kmp_match` | 可 |
| `chap07/str_find.py` | 文字列に含まれる文字列を探索（find系メソッド） | — | — |
| `chap07/str_in.py` | 帰属性判定演算子による文字列が含まれるかどうかの判定 | — | — |
| `chap07/str_index.py` | 文字列に含まれる文字列を探索（indexメソッド） | — | — |

### chap08

| ファイル | 内容（先頭のコメント） | 定義（関数・クラス） | import |
| --- | --- | --- | --- |
| `chap08/array_list.py` | 線形リスト（配列カーソル版） | `Node`, `ArrayLinkedList`, `ArrayLinkedListIterator` | 可 |
| `chap08/array_list_test.py` | 配列カーソル版線形リストクラスArrayLinkedListの利用例 | `select_Menu` | 不可（import 時に入出力） |
| `chap08/double_list.py` | 循環・重連結リスト | `Node`, `DoubleLinkedList`, `DoubleLinkedListIterator`, `DoubleLinkedListReverseIterator` | 可 |
| `chap08/double_list_test.py` | 循環・重連結リストクラスDoubleLinkedListの利用例 | `select_Menu` | 不可（import 時に入出力） |
| `chap08/linked_list.py` | 線形リスト | `Node`, `LinkedList`, `LinkedListIterator` | 可 |
| `chap08/linked_list_test.py` | 線形リストクラスLinkedListの利用例 | `select_Menu` | 不可（import 時に入出力） |

### chap09

| ファイル | 内容（先頭のコメント） | 定義（関数・クラス） | import |
| --- | --- | --- | --- |
| `chap09/bs_tree.py` | ２分探索木 | `Node`, `BinarySearchTree` | 可 |
| `chap09/bs_tree2.py` | ２分探索木 | `Node`, `BinarySearchTree` | 可 |
| `chap09/bs_tree2_test.py` | ２分探索木クラスBinarySearchTreeの利用例（その２） | `select_Menu` | 不可（import 時に入出力） |
| `chap09/bs_tree_test.py` | ２分探索木クラスBinarySearchTreeの利用例 | `select_Menu` | 不可（import 時に入出力） |
| `chap09/bs_tree_test_int.py` | ２分探索木クラスBinarySearchTreeの利用例（データはint型のキーのみ） | `select_Menu` | 不可（import 時に入出力） |
