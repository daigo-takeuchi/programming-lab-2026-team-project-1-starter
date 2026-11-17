# A3：教科書の2つのスタッククラスのテスト
#
# 教科書のクラスはそのまま使い、starter.py と同じ運用ルール
# 「push の前に is_full() を確認する」「pop の前に is_empty() を確認する」
# に従って検証する。

import unittest

from textbook.fixed_stack import FixedStack
from textbook.stack import Stack

STACK_CLASSES = [FixedStack, Stack]


def push_values(stack, values):
    """満杯でなければ push する。追加を拒否した値のリストを返す。"""
    rejected = []
    for value in values:
        if stack.is_full():
            rejected.append(value)
        else:
            stack.push(value)
    return rejected


def pop_all(stack):
    """空になるまで pop し、取り出した順のリストを返す。"""
    result = []
    while not stack.is_empty():
        result.append(stack.pop())
    return result


class TestStack(unittest.TestCase):

    def test_push_and_pop(self):
        """1. push したデータを pop で取り出せる"""
        for cls in STACK_CLASSES:
            with self.subTest(cls=cls.__name__):
                stack = cls(3)
                stack.push(10)
                self.assertEqual(len(stack), 1)
                self.assertEqual(stack.peek(), 10)
                self.assertEqual(stack.pop(), 10)
                self.assertEqual(len(stack), 0)

    def test_lifo_order(self):
        """2. 後に入れたデータから先に出てくる（LIFO）"""
        for cls in STACK_CLASSES:
            with self.subTest(cls=cls.__name__):
                stack = cls(5)
                push_values(stack, [1, 2, 3, 4, 5])
                self.assertEqual(pop_all(stack), [5, 4, 3, 2, 1])

    def test_reject_push_when_full(self):
        """3. 容量上限に達すると is_full() が True になり、追加を拒否できる"""
        for cls in STACK_CLASSES:
            with self.subTest(cls=cls.__name__):
                stack = cls(3)
                rejected = push_values(stack, [10, 20, 30, 40])
                self.assertTrue(stack.is_full())
                self.assertEqual(rejected, [40])
                self.assertEqual(len(stack), 3)

    def test_data_kept_after_rejected_push(self):
        """4. 追加を拒否しても、既存のデータは失われない"""
        for cls in STACK_CLASSES:
            with self.subTest(cls=cls.__name__):
                stack = cls(3)
                push_values(stack, [10, 20, 30, 40, 50])
                self.assertEqual(stack.peek(), 30)
                self.assertEqual(pop_all(stack), [30, 20, 10])

    def test_is_empty(self):
        """5. 空の状態では is_empty() が True になる"""
        for cls in STACK_CLASSES:
            with self.subTest(cls=cls.__name__):
                stack = cls(3)
                self.assertTrue(stack.is_empty())
                self.assertFalse(stack.is_full())
                stack.push(1)
                self.assertFalse(stack.is_empty())
                stack.pop()
                self.assertTrue(stack.is_empty())

    def test_capacity_one(self):
        """6. 容量1でも正しく動作する"""
        for cls in STACK_CLASSES:
            with self.subTest(cls=cls.__name__):
                stack = cls(1)
                self.assertTrue(stack.is_empty())
                rejected = push_values(stack, [7, 8])
                self.assertTrue(stack.is_full())
                self.assertEqual(rejected, [8])
                self.assertEqual(pop_all(stack), [7])
                self.assertTrue(stack.is_empty())


if __name__ == "__main__":
    unittest.main()
