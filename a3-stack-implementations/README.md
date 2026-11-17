# A3：スタックの実装方式と処理性能の比較

> ⚠️ **公開前の注意**
> `textbook/` 内のコードは第三者の著作物です（出典は下記参照）。
> 再配布の可否はまだ確認できていないため、このディレクトリは**ローカルの教材用**です。
> GitHub などで公開・配布する前に、必ず出版社の再配布条件を確認してください。

## 1. 研究テーマ

**A3：スタックの実装方式と処理性能の比較**

同じ「スタック」という仕組みを、異なる2つの方法で実装したクラスを比べます。
動作の正しさ（特に境界条件）と処理性能（時間・メモリ）を実験で調べ、計算量の観点から考察します。

## 2. 研究の背景

### スタックとは

スタック（stack）は、データを一時的にためておくデータ構造のひとつです。
データの出し入れは、**いちばん上（頂上）からだけ**行います。

| 操作 | 意味 |
| --- | --- |
| `push` | 頂上にデータを積む |
| `pop` | 頂上のデータを取り出す |
| `peek` | 頂上のデータを取り出さずに見る |
| `is_empty` | スタックが空かどうか調べる |
| `is_full` | スタックが満杯かどうか調べる |

### LIFOとは

LIFO（Last In, First Out：後入れ先出し）とは、**最後に入れたデータが最初に取り出される**という規則です。
お皿を積み重ねて、上から順に取っていく様子をイメージしてください。

```text
push(10) → push(20) → push(30)      pop() の順番
                                      30  ← 最後に入れたものが最初に出る
   | 30 |  ← 頂上                     20
   | 20 |                             10
   | 10 |  ← 底
   +----+
```

### スタックの利用例

- 関数呼び出しの管理（コールスタック）：関数が呼ばれるたびに積まれ、終わると取り出される
- エディタの「元に戻す（Undo）」機能
- ブラウザの「戻る」ボタン
- 括弧の対応チェック、数式（逆ポーランド記法）の計算
- 深さ優先探索（DFS）、再帰処理を繰り返しで書き直すとき

### 配列版とdeque版の内部実装の違い

| | 配列版 `FixedStack` | deque版 `Stack` |
| --- | --- | --- |
| ファイル | `textbook/fixed_stack.py` | `textbook/stack.py` |
| データの保存先 | Pythonのリスト `[None] * capacity` を最初に確保 | `collections.deque([], maxlen)` |
| 頂上の管理 | スタックポインタ `ptr` で自分で管理 | `deque` が内部で管理 |
| `push` | `stk[ptr]` に代入して `ptr += 1` | `deque.append()` |
| `pop` | `ptr -= 1` して `stk[ptr]` を返す | `deque.pop()` |
| **満杯時の `push`** | 例外 `FixedStack.Full` を送出 | **例外を出さず、底の（最も古い）データが捨てられる** |
| 空のときの `pop` | 例外 `FixedStack.Empty` を送出 | 例外 `IndexError` を送出 |
| コンストラクタ | `FixedStack(capacity=256)` | `Stack(maxlen=256)` |

満杯時・空のときの動作が異なる点が、この研究での大切なポイントです。
そのため、この教材では **`push` の前に `is_full()`、`pop` の前に `is_empty()` を確認する**というルールで両方を使います。

```python
if stack.is_full():
    print("Full: cannot push", value)
else:
    stack.push(value)

while not stack.is_empty():
    print(stack.pop())
```

## 3. 使用する教科書コード

出典：柴田望洋『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』SBクリエイティブ　第4章「スタックとキュー」

| ファイル | 内容 | 教科書のサンプルファイル |
| --- | --- | --- |
| `textbook/fixed_stack.py` | 固定長スタッククラス `FixedStack`（リストを利用） | `chap04/fixed_stack.py` |
| `textbook/stack.py` | 固定長スタッククラス `Stack`（`collections.deque` を利用） | `chap04/stack.py` |

- この2ファイルは教科書のサンプルコードを**そのままコピー**したものです（SHA-256で原本との一致を確認済み）。
- `textbook/__init__.py` は、`from textbook.fixed_stack import FixedStack` のように import するための空ファイルです。
- **教科書コードは原則として編集しないでください。** 動作を変えたいときは、`starter.py` や自分たちで作るファイルの側で工夫してください。
- 教科書コードは第三者の著作物です。公開リポジトリへ push する前に、再配布条件を必ず確認してください。

## 4. 実行方法

このディレクトリ（`a3-stack-implementations/`）で実行してください。

```bash
python3 starter.py
python3 -m unittest discover -s tests -v
```

`starter.py` の実行結果（例）：

```text
Array
Full: cannot push 40
30
20
10

Deque
Full: cannot push 40
30
20
10
```

## 5. 研究の進め方

次の順番で進めることをおすすめします。

1. **教科書の2つのクラスの実装を読む。** `push`・`pop`・`is_full` などがどう書かれているか、違いを書き出す。
2. **`starter.py` を実行して LIFO を確認する。**
3. **容量上限・空状態を検証する。** 容量 1、3、10 などで試す。`is_full()` で確認しないで push するとどうなるかも（別ファイルで）調べてみる。
4. **同じ条件で push/pop の処理時間を測定する。**
5. **データ数 N を増やして比較する。** 例：N = 1,000 / 10,000 / 100,000 / 1,000,000
6. **計算量と実測結果を考察する。**

`starter.py` の末尾に TODO 1〜5 があります。ここから実験を広げてください。

## 6. 比較実験での注意

- **同じ容量・同じ操作列を使う。** 条件をそろえないと公平な比較になりません。
- **処理時間の測定では、原則として容量上限を超えない。** 容量を N 以上に設定してから N 回 push してください。
- **大量の `print()` を計測対象に含めない。** 画面表示はとても遅いため、データ構造の速さではなく表示の速さを測ってしまいます。
- **`deque` は Python 標準ライブラリの実装（C言語で書かれている）を利用している。** 実行時間の差を、そのままデータ構造の理論的計算量の差だと考えないでください。
- **満杯時の内部動作は2つの実装で異なる。** 今回の比較では、追加前に必ず `is_full()` を確認してください。
- **計算量は「理論的な分析」と「実測結果」を区別して書く。** 例：「理論上はどちらの push も O(1) である。実測では……だった。その理由として……が考えられる。」
- 測定は複数回行い、平均値や最小値を使うと結果が安定します。

## 7. 学生への課題

### 研究課題

少なくとも **2つの実装方式**（配列版 `FixedStack` と deque版 `Stack`）について、次を比較してください。

1. **動作の正確性**：LIFO、満杯・空の境界条件、容量1などの特殊な場合
2. **処理時間**：データ数 N を変えたときの push/pop の時間
3. **（発展）メモリ使用量**

報告には、次の3つを必ず含めてください。

- **実験条件**：Python のバージョン、PC 環境、容量、データ数 N、測定回数、測定方法
- **結果**：表やグラフ
- **考察**：Big-O による理論と実測結果の比較、違いが生じた理由

余裕があれば、Python のリストの `append()` / `pop()` だけを使ったスタックなど、3つ目の実装方式を加えて比較してもかまいません。

### GitHub を用いたチーム開発

チームで GitHub を使って研究を進めてください（公開設定については冒頭の注意を参照）。

- **役割分担**：例）実装担当、測定担当、テスト担当、README・考察担当
- **Issue**：やること（実験・不具合・調べ物）を Issue として登録し、担当者を割り当てる
- **branch**：作業ごとに branch を作成する（例：`feature/measure-time`、`test/capacity-one`）
- **Pull Request**：変更は Pull Request で提出し、他のメンバーがレビューしてから merge する
- **README 更新**：実験条件・結果・考察を、この README（または別の報告ファイル）に追記していく

## 8. ディレクトリ構成

```text
a3-stack-implementations/
├── README.md            この説明
├── .gitignore
├── starter.py           2つのスタックを同じ操作で動かすサンプル（TODO付き）
├── textbook/            教科書のサンプルコード（編集しない）
│   ├── __init__.py
│   ├── fixed_stack.py
│   └── stack.py
└── tests/
    └── test_stack.py    unittest によるテスト
```

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
| `chap04/fixed_stack.py` | `a3-stack-implementations/textbook/fixed_stack.py` | `starter.py`、`tests/test_stack.py` |
| `chap04/stack.py` | `a3-stack-implementations/textbook/stack.py` | `starter.py`、`tests/test_stack.py` |

### 3. 配置後のディレクトリ構成

```text
a3-stack-implementations/
└── textbook/
    ├── __init__.py          （リポジトリに含まれる）
    ├── fixed_stack.py       （各自で配置）
    └── stack.py             （各自で配置）
```

### 4. コピーと確認のコマンド例

```bash
cd a3-stack-implementations
SRC="<展開したフォルダ>"        # 各自の環境に合わせる

cp -i "$SRC/chap04/fixed_stack.py" textbook/fixed_stack.py
cp -i "$SRC/chap04/stack.py" textbook/stack.py

# 原本とコピーの SHA-256 が一致することを確認する
sha256sum "$SRC/chap04/fixed_stack.py" textbook/fixed_stack.py
sha256sum "$SRC/chap04/stack.py" textbook/stack.py

python3 starter.py                          # 実行確認
python3 -m unittest discover -s tests -v    # テスト
```

配置した教科書のコードは、リポジトリ直下の `.gitignore` によって Git の追跡対象から除外されます（`git status` に表示されなければ正常です）。
`git add -f` などで教科書のコードを commit・push しないでください。
