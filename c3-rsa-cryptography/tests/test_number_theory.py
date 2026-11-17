# C3：整数論の関数のテスト

import unittest

from number_theory import gcd, is_coprime, is_prime, mod_inverse


class TestNumberTheory(unittest.TestCase):

    def test_gcd(self):
        """1. 最大公約数（教科書の gcd）"""
        self.assertEqual(gcd(12, 18), 6)
        self.assertEqual(gcd(18, 12), 6)
        self.assertEqual(gcd(17, 3120), 1)
        self.assertEqual(gcd(3120, 17), 1)
        self.assertEqual(gcd(5, 0), 5)
        self.assertEqual(gcd(0, 5), 5)
        self.assertEqual(gcd(2 ** 64, 2 ** 40 * 3), 2 ** 40)

    def test_is_coprime(self):
        """2. 互いに素かの判定"""
        self.assertTrue(is_coprime(17, 3120))
        self.assertTrue(is_coprime(8, 15))
        self.assertFalse(is_coprime(6, 3120))
        self.assertFalse(is_coprime(12, 18))
        self.assertTrue(is_coprime(3, -4))      # 教科書の gcd は -1 を返すが、互いに素
        self.assertFalse(is_coprime(4, -6))

    def test_is_prime(self):
        """3. 素数判定"""
        primes = [2, 3, 5, 7, 11, 13, 53, 61, 97, 7919]
        composites = [4, 6, 9, 15, 21, 25, 49, 3233, 7917]
        for n in primes:
            self.assertTrue(is_prime(n), n)
        for n in composites:
            self.assertFalse(is_prime(n), n)
        # 100 以下の素数は 25 個
        self.assertEqual(sum(1 for n in range(101) if is_prime(n)), 25)

    def test_not_prime_small_and_negative(self):
        """4. 0、1、負の整数は素数ではない"""
        for n in [0, 1, -1, -2, -7, -61]:
            self.assertFalse(is_prime(n), n)

    def test_mod_inverse(self):
        """5. モジュラ逆元"""
        self.assertEqual(mod_inverse(17, 3120), 2753)
        self.assertEqual(mod_inverse(3, 11), 4)        # 3 × 4 = 12 ≡ 1 (mod 11)
        for a in range(1, 20):
            if is_coprime(a, 20):
                self.assertEqual(a * mod_inverse(a, 20) % 20, 1)

    def test_mod_inverse_not_exist(self):
        """6. 逆元が存在しない場合は ValueError"""
        with self.assertRaises(ValueError):
            mod_inverse(6, 3120)
        with self.assertRaises(ValueError):
            mod_inverse(0, 7)
        with self.assertRaises(ValueError):
            mod_inverse(3, 1)


if __name__ == "__main__":
    unittest.main()
