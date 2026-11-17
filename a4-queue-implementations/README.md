# A4：キューの実装方式と処理性能の比較

> ⚠️ **公開前の注意**
> `textbook/` 内のコードは第三者の著作物です（出典は下記参照）。
> 再配布の可否はまだ確認できていないため、このディレクトリは**ローカルの教材用**です。
> GitHub などで公開・配布する前に、必ず出版社の再配布条件を確認してください。

## 1. 研究テーマ

**A4：キューの実装方式と処理性能の比較**

同じ「キュー」という仕組みを、異なる2つの方法で実装したクラスを比べます。
動作の正しさ（特に境界条件とリングバッファの循環）と処理性能（時間・メモリ）を実験で調べ、計算量の観点から考察します。

## 2. 研究の背景

### キューとは

キュー（queue）は、データを一時的にためておくデータ構造のひとつです。
データは**末尾（rear）から入れて、先頭（front）から取り出し**ます。

| 操作 | 教科書のメソッド | 意味 |
| --- | --- | --- |
| エンキュー（enqueue） | `enque(x)` | 末尾にデータを入れる |
| デキュー（dequeue） | `deque()` | 先頭のデータを取り出す |
| ピーク | `peek()` | 先頭のデータを取り出さずに見る |
| 空の判定 | `is_empty()` | キューが空かどうか調べる |
| 満杯の判定 | `is_full()` | キューが満杯かどうか調べる |
| データ数 | `len(q)` | 現在入っているデータの個数 |

※ 教科書ではメソッド名が `enque` / `deque` と綴られています。

### FIFOとは

FIFO（First In, First Out：先入れ先出し）とは、**最初に入れたデータが最初に取り出される**という規則です。
レジに並ぶ行列をイメージしてください。先に並んだ人から順に会計します。

```text
enque(10) → enque(20) → enque(30)

  先頭(front)              末尾(rear)
   [ 10 ][ 20 ][ 30 ]  ← ここから入れる
    ↑
  ここから取り出す     deque() の順番：10 → 20 → 30
```

### キューの利用例

- プリンタの印刷待ち（先に送った文書から印刷される）
- OS のプロセススケジューリング、キーボード入力のバッファ
- ネットワークのパケット送受信、Web サーバのリクエスト待ち行列
- 幅優先探索（BFS）
- 音声・動画のストリーミング再生用バッファ

### 配列版リングバッファとdeque版の内部実装の違い

| | 配列版 `FixedQueue` | deque版 `Queue` |
| --- | --- | --- |
| ファイル | `textbook/fixed_queue.py` | `textbook/queue.py` |
| コンストラクタ | `FixedQueue(capacity)`（**省略不可**） | `Queue(maxlen=256)` |
| データの保存先 | Pythonのリスト `[None] * capacity` を最初に確保 | `collections.deque([], maxlen)` |
| 位置の管理 | `front`（先頭）、`rear`（末尾の次）、`no`（データ数）を自分で管理 | `deque` が内部で管理 |
| `enque` | `que[rear]` に代入し、`rear` を1進める（末尾まで来たら0に戻す） | `deque.append()` |
| `deque` | `que[front]` を返し、`front` を1進める（末尾まで来たら0に戻す） | `deque.popleft()` |
| `len()` / `is_full()` / `is_empty()` | `no` で判定 | `deque` の長さと `maxlen` で判定 |
| **満杯時の `enque`** | 例外 `FixedQueue.Full` を送出 | **例外を出さず、先頭の（最も古い）データが捨てられる** |
| 空のときの `deque` | 例外 `FixedQueue.Empty` を送出 | 例外 `IndexError` を送出 |

満杯時・空のときの動作が異なる点が、この研究での大切なポイントです。
特に deque版は、満杯で `enque` すると**次に取り出されるはずだったデータが黙って消えます**。
そのため、この教材では **`enque` の前に `is_full()`、`deque` の前に `is_empty()` を確認する**というルールで両方を使います。

```python
if queue.is_full():
    print("Full: cannot enqueue", value)
else:
    queue.enque(value)

while not queue.is_empty():
    print(queue.deque())
```

### リングバッファの front / rear の循環

単純な配列でキューを作ると、先頭を取り出すたびに残りのデータを1つずつ前へずらす必要があり、O(n) の時間がかかります。
リングバッファ（環状バッファ）は、**データを動かさず、`front` と `rear` の位置だけを進める**ことで、enque も deque も O(1) にする工夫です。
配列の末尾まで進んだら、添字 0 に戻ります（配列の両端がつながった輪のように扱う）。

容量3で `starter.py` と同じ操作をしたときの様子：

```text
操作              que[0] que[1] que[2]   front rear  no
初期状態           -      -      -        0     0    0
enque(10)         10      -      -        0     1    1
enque(20)         10     20      -        0     2    2
enque(30)         10     20     30        0     0    3   ← rear が 3 → 0 に戻る
enque(40) 拒否    （is_full() が True なので追加しない）
deque() → 10     (10)    20     30        1     0    2   ← front が進む（データは動かない）
enque(40)         40     20     30        1     1    3   ← 40 は添字0に入る
deque() → 20      40    (20)    30        2     1    2
deque() → 30      40     -     (30)       0     1    1   ← front も 3 → 0 に戻る
deque() → 40     (40)    -      -         1     1    0
```

※ 取り出した位置のデータは消されず配列に残りますが、`front` と `no` により「無効なデータ」として扱われます。

## 3. 使用する教科書コード

出典：柴田望洋 著『新・明解 Pythonで学ぶアルゴリズムとデータ構造（第2版）』SBクリエイティブ　第4章「スタックとキュー」

| ファイル | 内容 | 教科書のサンプルファイル |
| --- | --- | --- |
| `textbook/fixed_queue.py` | 固定長キュークラス `FixedQueue`（リングバッファ） | `chap04/fixed_queue.py` |
| `textbook/queue.py` | 固定長キュークラス `Queue`（`collections.deque` を利用） | `chap04/queue.py` |

- この2ファイルは教科書のサンプルコードを**そのままコピー**したものです（SHA-256で原本との一致を確認済み）。
- `textbook/__init__.py` は、`from textbook.fixed_queue import FixedQueue` のように import するための空ファイルです。
- **教科書コードは原則として編集しないでください。** 動作を変えたいときは、`starter.py` や自分たちで作るファイルの側で工夫してください。
- 教科書コードは第三者の著作物です。公開リポジトリへ push する前に、再配布条件を必ず確認してください。
- `textbook/queue.py` は Python 標準ライブラリの `queue` モジュールと同じ名前です。必ず `from textbook.queue import Queue` の形で import し、`textbook/` フォルダの中に移動して実行しないでください。

## 4. 実行方法

このディレクトリ（`a4-queue-implementations/`）で実行してください。

```bash
python3 starter.py
python3 -m unittest discover -s tests -v
```

`starter.py` の実行結果（例）：

```text
Array (Ring Buffer)
Full: cannot enqueue 40
Dequeued: 10
Enqueued: 40
Dequeued: 20
Dequeued: 30
Dequeued: 40

Deque
Full: cannot enqueue 40
Dequeued: 10
Enqueued: 40
Dequeued: 20
Dequeued: 30
Dequeued: 40
```

## 5. 研究の進め方

次の順番で進めることをおすすめします。

1. **教科書の2つのクラスの実装を読む。** `enque`・`deque`・`is_full` などがどう書かれているか、違いを書き出す。
2. **`starter.py` を実行して FIFO を確認する。**
3. **リングバッファの循環動作を確認する。** `FixedQueue` の `front`・`rear`・`no` を操作ごとに表示し、上の表と比べる。
4. **容量上限・空状態を検証する。** 容量 1、3、10 などで試す。`is_full()` で確認しないで enque するとどうなるかも（別ファイルで）調べてみる。
5. **同じ条件で enqueue/dequeue の処理時間を測定する。**
6. **データ数 N を増やして比較する。** 例：N = 1,000 / 10,000 / 100,000 / 1,000,000
7. **計算量と実測結果を考察する。**

`starter.py` の末尾に TODO 1〜6 があります。ここから実験を広げてください。

## 6. 比較実験での注意

- **同じ容量・同じ操作列を使う。** 条件をそろえないと公平な比較になりません。
- **処理時間の測定では、原則として容量上限を超えない。** 容量を N 以上に設定してから N 回 enque してください。
- **大量の `print()` を計測対象に含めない。** 画面表示はとても遅いため、データ構造の速さではなく表示の速さを測ってしまいます。
- **`deque` は Python 標準ライブラリの実装（C言語で書かれている）を利用している。** 実行時間の差を、そのままデータ構造の理論的計算量の差だと考えないでください。
- **満杯時の内部動作は2つの実装で異なる。** 追加前に必ず `is_full()` を確認してください。
- **リングバッファの循環を検証する場合は、容量を超えずに enqueue/dequeue を繰り返す。** 例：容量より少ない個数を入れた状態で「1個入れて1個出す」を何度も繰り返すと、`front` と `rear` が何周もします。
- **計算量は「理論的な分析」と「実測結果」を区別して書く。** 例：「理論上はどちらの enqueue も O(1) である。実測では……だった。その理由として……が考えられる。」
- 測定は複数回行い、平均値や最小値を使うと結果が安定します。

## 7. 学生への課題

### 研究課題

少なくとも **2つの実装方式**（配列版リングバッファ `FixedQueue` と deque版 `Queue`）について、次を比較してください。

1. **動作の正確性**：FIFO、満杯・空の境界条件、容量1、リングバッファの循環
2. **処理時間**：データ数 N を変えたときの enqueue/dequeue の時間
3. **メモリ使用量**：データ数 N や容量を変えたときのメモリ使用量

報告には、次の3つを必ず含めてください。

- **実験条件**：Python のバージョン、PC 環境、容量、データ数 N、測定回数、測定方法
- **結果**：表やグラフ
- **考察**：Big-O による理論と実測結果の比較、違いが生じた理由

余裕があれば、Python のリストの `append()` と `pop(0)` だけを使ったキューなど、3つ目の実装方式を加えて比較してもかまいません（`pop(0)` の計算量に注目してください）。

### GitHub を用いたチーム開発

チームで GitHub を使って研究を進めてください（公開設定については冒頭の注意を参照）。

- **役割分担**：例）実装担当、測定担当、テスト担当、README・考察担当
- **Issue**：やること（実験・不具合・調べ物）を Issue として登録し、担当者を割り当てる
- **branch**：作業ごとに branch を作成する（例：`feature/measure-time`、`test/ring-buffer`）
- **Pull Request**：変更は Pull Request で提出し、他のメンバーがレビューしてから merge する
- **README 更新**：実験条件・結果・考察を、この README（または別の報告ファイル）に追記していく

## 8. ディレクトリ構成

```text
a4-queue-implementations/
├── README.md            この説明
├── .gitignore
├── starter.py           2つのキューを同じ操作で動かすサンプル（TODO付き）
├── textbook/            教科書のサンプルコード（編集しない）
│   ├── __init__.py
│   ├── fixed_queue.py
│   └── queue.py
└── tests/
    └── test_queue.py    unittest によるテスト
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
| `chap04/fixed_queue.py` | `a4-queue-implementations/textbook/fixed_queue.py` | `starter.py`、`tests/test_queue.py` |
| `chap04/queue.py` | `a4-queue-implementations/textbook/queue.py` | `starter.py`、`tests/test_queue.py` |

### 3. 配置後のディレクトリ構成

```text
a4-queue-implementations/
└── textbook/
    ├── __init__.py          （リポジトリに含まれる）
    ├── fixed_queue.py       （各自で配置）
    └── queue.py             （各自で配置）
```

### 4. コピーと確認のコマンド例

```bash
cd a4-queue-implementations
SRC="<展開したフォルダ>"        # 各自の環境に合わせる

cp -i "$SRC/chap04/fixed_queue.py" textbook/fixed_queue.py
cp -i "$SRC/chap04/queue.py" textbook/queue.py

# 原本とコピーの SHA-256 が一致することを確認する
sha256sum "$SRC/chap04/fixed_queue.py" textbook/fixed_queue.py
sha256sum "$SRC/chap04/queue.py" textbook/queue.py

python3 starter.py                          # 実行確認
python3 -m unittest discover -s tests -v    # テスト
```

配置した教科書のコードは、リポジトリ直下の `.gitignore` によって Git の追跡対象から除外されます（`git status` に表示されなければ正常です）。
`git add -f` などで教科書のコードを commit・push しないでください。
