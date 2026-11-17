# C3：剰余べき乗のテスト

import unittest

from modular_power import MAX_NAIVE_EXPONENT, modular_power_naive, modular_power_squaring

FUNCTIONS = [modular_power_naive, modular_power_squaring]


class TestModularPower(unittest.TestCase):

    def test_naive(self):
        """1. 通常の反復乗算の結果が正しい"""
        self.assertEqual(modular_power_naive(2, 10, 1000), 24)      # 1024 mod 1000
        self.assertEqual(modular_power_naive(65, 17, 3233), 2790)

    def test_squaring(self):
        """2. 繰返し二乗法の結果が正しい"""
        self.assertEqual(modular_power_squaring(2, 10, 1000), 24)
        self.assertEqual(modular_power_squaring(65, 17, 3233), 2790)
        self.assertEqual(modular_power_squaring(2790, 2753, 3233), 65)

    def test_match_builtin_pow(self):
        """3. 両者が Python 標準の pow と一致する"""
        for base in [0, 1, 2, 3, 65, 2790, 3232, 10 ** 12]:
            for exponent in [0, 1, 2, 3, 16, 17, 100, 2753]:
                for modulus in [1, 2, 7, 3233, 2 ** 31 - 1]:
                    expected = pow(base, exponent, modulus)
                    for f in FUNCTIONS:
                        self.assertEqual(f(base, exponent, modulus), expected,
                                         (f.__name__, base, exponent, modulus))
        # 大きな指数（繰返し二乗法と pow だけ）
        big = 2 ** 200 + 12345
        self.assertEqual(modular_power_squaring(65, big, 3233), pow(65, big, 3233))

    def test_exponent_zero(self):
        """4. 指数 0 の結果は 1 % modulus"""
        for f in FUNCTIONS:
            self.assertEqual(f(5, 0, 7), 1)
            self.assertEqual(f(0, 0, 7), 1)      # pow(0, 0, 7) と同じく 1
            self.assertEqual(f(5, 0, 1), 0)

    def test_exponent_one(self):
        """5. 指数 1 の結果は base % modulus"""
        for f in FUNCTIONS:
            self.assertEqual(f(5, 1, 7), 5)
            self.assertEqual(f(12, 1, 7), 5)

    def test_even_and_odd_exponents(self):
        """6・7. 偶数指数・奇数指数"""
        for f in FUNCTIONS:
            self.assertEqual(f(3, 4, 100), 81)
            self.assertEqual(f(3, 8, 1000), 6561 % 1000)
            self.assertEqual(f(3, 5, 100), 43)        # 243 mod 100
            self.assertEqual(f(3, 13, 1000), 1594323 % 1000)

    def test_modulus_one(self):
        """8. modulus = 1 なら結果は常に 0"""
        for f in FUNCTIONS:
            for base, exponent in [(0, 0), (5, 0), (5, 3), (-2, 7)]:
                self.assertEqual(f(base, exponent, 1), 0)

    def test_negative_base(self):
        """base が負の整数でも pow と一致する"""
        for f in FUNCTIONS:
            self.assertEqual(f(-2, 5, 13), pow(-2, 5, 13))
            self.assertEqual(f(-7, 4, 10), pow(-7, 4, 10))

    def test_invalid_input(self):
        """9. 不正な入力は例外になる"""
        for f in FUNCTIONS:
            with self.assertRaises(ValueError):
                f(2, -1, 7)              # 負の指数
            with self.assertRaises(ValueError):
                f(2, 3, 0)               # modulus が 0
            with self.assertRaises(ValueError):
                f(2, 3, -5)              # modulus が負
            with self.assertRaises(TypeError):
                f(2.0, 3, 7)             # 整数でない
            with self.assertRaises(TypeError):
                f(2, "3", 7)
        with self.assertRaises(ValueError):
            modular_power_naive(2, MAX_NAIVE_EXPONENT + 1, 7)    # 反復乗算の安全上限


if __name__ == "__main__":
    unittest.main()
