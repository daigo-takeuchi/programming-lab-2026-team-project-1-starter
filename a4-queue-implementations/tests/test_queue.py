# A4：教科書の2つのキュークラスのテスト
#
# 教科書のクラスはそのまま使い、starter.py と同じ運用ルール
# 「enque の前に is_full() を確認する」「deque の前に is_empty() を確認する」
# に従って検証する。

import unittest

from textbook.fixed_queue import FixedQueue
from textbook.queue import Queue

QUEUE_CLASSES = [FixedQueue, Queue]


def enque_values(queue, values):
    """満杯でなければ enque する。追加を拒否した値のリストを返す。"""
    rejected = []
    for value in values:
        if queue.is_full():
            rejected.append(value)
        else:
            queue.enque(value)
    return rejected


def deque_all(queue):
    """空になるまで deque し、取り出した順のリストを返す。"""
    result = []
    while not queue.is_empty():
        result.append(queue.deque())
    return result


class TestQueue(unittest.TestCase):

    def test_enque_and_deque(self):
        """1. enque したデータを deque で取り出せる"""
        for cls in QUEUE_CLASSES:
            with self.subTest(cls=cls.__name__):
                queue = cls(3)
                queue.enque(10)
                self.assertEqual(len(queue), 1)
                self.assertEqual(queue.peek(), 10)
                self.assertEqual(queue.deque(), 10)
                self.assertEqual(len(queue), 0)

    def test_fifo_order(self):
        """2. 先に入れたデータから先に出てくる（FIFO）"""
        for cls in QUEUE_CLASSES:
            with self.subTest(cls=cls.__name__):
                queue = cls(5)
                enque_values(queue, [1, 2, 3, 4, 5])
                self.assertEqual(deque_all(queue), [1, 2, 3, 4, 5])

    def test_reject_enque_when_full(self):
        """3. 容量上限に達すると is_full() が True になり、追加を拒否できる"""
        for cls in QUEUE_CLASSES:
            with self.subTest(cls=cls.__name__):
                queue = cls(3)
                rejected = enque_values(queue, [10, 20, 30, 40])
                self.assertTrue(queue.is_full())
                self.assertEqual(rejected, [40])
                self.assertEqual(len(queue), 3)

    def test_data_kept_after_rejected_enque(self):
        """4. 追加を拒否しても、既存のデータは失われない"""
        for cls in QUEUE_CLASSES:
            with self.subTest(cls=cls.__name__):
                queue = cls(3)
                enque_values(queue, [10, 20, 30, 40, 50])
                self.assertEqual(queue.peek(), 10)
                self.assertEqual(deque_all(queue), [10, 20, 30])

    def test_is_empty(self):
        """5. 空の状態では is_empty() が True になる"""
        for cls in QUEUE_CLASSES:
            with self.subTest(cls=cls.__name__):
                queue = cls(3)
                self.assertTrue(queue.is_empty())
                self.assertFalse(queue.is_full())
                queue.enque(1)
                self.assertFalse(queue.is_empty())
                queue.deque()
                self.assertTrue(queue.is_empty())

    def test_capacity_one(self):
        """6. 容量1でも正しく動作する"""
        for cls in QUEUE_CLASSES:
            with self.subTest(cls=cls.__name__):
                queue = cls(1)
                self.assertTrue(queue.is_empty())
                rejected = enque_values(queue, [7, 8])
                self.assertTrue(queue.is_full())
                self.assertEqual(rejected, [8])
                self.assertEqual(deque_all(queue), [7])
                self.assertTrue(queue.is_empty())

    def test_enque_after_deque(self):
        """7. deque の後に enque しても、正しい順序で取り出せる（starter.py と同じ操作列）"""
        for cls in QUEUE_CLASSES:
            with self.subTest(cls=cls.__name__):
                queue = cls(3)
                rejected = enque_values(queue, [10, 20, 30, 40])
                self.assertEqual(rejected, [40])
                self.assertEqual(queue.deque(), 10)
                rejected = enque_values(queue, [40])
                self.assertEqual(rejected, [])
                self.assertEqual(deque_all(queue), [20, 30, 40])

    def test_fifo_with_ring_buffer_wraparound(self):
        """8. front / rear が何周も循環しても FIFO が維持される"""
        for cls in QUEUE_CLASSES:
            with self.subTest(cls=cls.__name__):
                queue = cls(3)
                enque_values(queue, [0, 1])
                taken = []
                # 2個入った状態で「1個入れて1個出す」を繰り返す（容量は超えない）
                for value in range(2, 12):
                    enque_values(queue, [value])
                    taken.append(queue.deque())
                taken.extend(deque_all(queue))
                self.assertEqual(taken, list(range(12)))

    def test_ring_buffer_cursors(self):
        """8. （補足）FixedQueue の front / rear が配列の末尾から先頭へ戻る"""
        queue = FixedQueue(3)
        enque_values(queue, [10, 20, 30])
        self.assertEqual((queue.front, queue.rear), (0, 0))   # rear が 3 → 0 に戻った
        self.assertEqual(queue.deque(), 10)
        self.assertEqual((queue.front, queue.rear), (1, 0))
        enque_values(queue, [40])
        self.assertEqual(queue.que[0], 40)                     # 40 は添字0に格納される
        self.assertEqual((queue.front, queue.rear), (1, 1))
        self.assertEqual(deque_all(queue), [20, 30, 40])
        self.assertEqual((queue.front, queue.rear), (1, 1))   # front も 3 → 0 → 1 と一周した


if __name__ == "__main__":
    unittest.main()
