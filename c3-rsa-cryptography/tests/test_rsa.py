# C3：教科書的な RSA のテスト

import unittest

import rsa
from modular_power import modular_power_naive, modular_power_squaring


class TestRSA(unittest.TestCase):

    def setUp(self):
        self.public_key, self.private_key = rsa.generate_keys(61, 53, 17)

    def test_generate_keys(self):
        """1〜4. p=61, q=53, e=17 から n=3233, φ(n)=3120, d=2753 の鍵を作る"""
        self.assertEqual(self.public_key, (3233, 17))
        self.assertEqual(self.private_key, (3233, 2753))
        self.assertEqual(rsa.totient(61, 53), 3120)
        self.assertEqual(17 * 2753 % 3120, 1)

    def test_encrypt_known_value(self):
        """5. メッセージ 65 を暗号化すると 2790"""
        self.assertEqual(rsa.encrypt(65, self.public_key), 2790)

    def test_decrypt_known_value(self):
        """6. 2790 を復号すると 65 に戻る"""
        self.assertEqual(rsa.decrypt(2790, self.private_key), 65)

    def test_round_trip_many_messages(self):
        """7. いろいろなメッセージで暗号化・復号が成功する（計算方法を変えても同じ）"""
        for m in [2, 3, 42, 100, 1000, 2024, 3000]:
            for power in [modular_power_squaring, modular_power_naive, pow]:
                c = rsa.encrypt(m, self.public_key, power=power)
                self.assertEqual(rsa.decrypt(c, self.private_key, power=power), m)
        # 別の鍵
        public_key, private_key = rsa.generate_keys(11, 13, 7)
        for m in range(143):
            self.assertEqual(rsa.decrypt(rsa.encrypt(m, public_key), private_key), m)

    def test_boundary_messages(self):
        """8. 0 以上 n 未満の境界（0, 1, n − 1）と、範囲外の拒否"""
        n = self.public_key[0]
        for m in [0, 1, n - 1]:
            self.assertEqual(rsa.decrypt(rsa.encrypt(m, self.public_key), self.private_key), m)
        for bad in [-1, n, n + 1]:
            with self.assertRaises(ValueError):
                rsa.encrypt(bad, self.public_key)
            with self.assertRaises(ValueError):
                rsa.decrypt(bad, self.private_key)
        with self.assertRaises(TypeError):
            rsa.encrypt("65", self.public_key)

    def test_reject_invalid_primes(self):
        """9. 素数でない p, q や、同じ素数を拒否する"""
        for p, q in [(60, 53), (61, 51), (1, 53), (-61, 53), (61, 61)]:
            with self.assertRaises(ValueError):
                rsa.generate_keys(p, q, 17)

    def test_reject_invalid_e(self):
        """10. gcd(e, φ(n)) ≠ 1 や、範囲外の e を拒否する"""
        for e in [3, 5, 6, 10, 15]:          # どれも 3120 = 2^4 × 3 × 5 × 13 と共通の約数を持つ
            with self.assertRaises(ValueError):
                rsa.generate_keys(61, 53, e)
        for e in [1, 0, -17, 3120, 3121]:     # 1 < e < φ(n) を満たさない
            with self.assertRaises(ValueError):
                rsa.generate_keys(61, 53, e)


if __name__ == "__main__":
    unittest.main()
