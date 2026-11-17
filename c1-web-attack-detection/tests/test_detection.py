# C1：集計と異常検出のテスト

import unittest
from pathlib import Path

import detection
import log_parser

SAMPLE_LOG = Path(__file__).parent.parent / "data" / "sample_access.log"


def rec(ip, status=200):
    """テスト用の簡単なレコード（集計に使う ip と status だけ）"""
    return {"ip": ip, "status": status}


RECORDS = [
    rec("192.0.2.1"),
    rec("192.0.2.2"),
    rec("192.0.2.1", 404),
    rec("192.0.2.3", 404),
    rec("192.0.2.1"),
    rec("192.0.2.2", 404),
    rec("192.0.2.1", 404),
]
EXPECTED_ACCESS = {"192.0.2.1": 4, "192.0.2.2": 2, "192.0.2.3": 1}
EXPECTED_404 = {"192.0.2.1": 2, "192.0.2.2": 1, "192.0.2.3": 1}


class TestCounting(unittest.TestCase):

    def test_linear_access_counts(self):
        """1. 線形探索版のアクセス回数が正しい（IPは初めて現れた順）"""
        ips, access, _ = detection.count_linear(RECORDS)
        self.assertEqual(ips, ["192.0.2.1", "192.0.2.2", "192.0.2.3"])
        self.assertEqual(access, [4, 2, 1])

    def test_dict_access_counts(self):
        """2. 辞書版のアクセス回数が正しい"""
        access, _ = detection.count_dict(RECORDS)
        self.assertEqual(access, EXPECTED_ACCESS)

    def test_linear_and_dict_match(self):
        """3. 線形探索版と辞書版の集計結果が一致する（サンプルログでも確認）"""
        records, _ = log_parser.load_log(SAMPLE_LOG)
        for data in (RECORDS, records):
            ips, linear_access, linear_404 = detection.count_linear(data)
            dict_access, dict_404 = detection.count_dict(data)
            self.assertEqual(dict(zip(ips, linear_access)), dict_access)
            self.assertEqual(dict(zip(ips, linear_404)), dict_404)

    def test_404_counts(self):
        """4. 404エラー回数が正しい（404がないIPは0）"""
        ips, _, linear_404 = detection.count_linear(RECORDS)
        self.assertEqual(dict(zip(ips, linear_404)), EXPECTED_404)
        _, dict_404 = detection.count_dict(RECORDS)
        self.assertEqual(dict_404, EXPECTED_404)
        _, no_errors = detection.count_dict([rec("192.0.2.9")])
        self.assertEqual(no_errors, {"192.0.2.9": 0})

    def test_empty_log(self):
        """7. 空のログでも安全に動作する"""
        self.assertEqual(detection.count_linear([]), ([], [], []))
        self.assertEqual(detection.count_dict([]), ({}, {}))
        self.assertEqual(detection.find_over_threshold({}, 1), [])

    def test_repeated_access(self):
        """8. 同じIPからの繰り返しアクセスを正しく集計できる"""
        records = [rec("203.0.113.7")] * 100
        ips, access, _ = detection.count_linear(records)
        self.assertEqual((ips, access), (["203.0.113.7"], [100]))
        self.assertEqual(detection.count_dict(records)[0], {"203.0.113.7": 100})

    def test_different_ips_not_mixed(self):
        """9. 異なるIPの集計が混ざらない（前方が同じ文字列のIPも区別する）"""
        records = [rec("192.0.2.1"), rec("192.0.2.10"), rec("192.0.2.100"), rec("192.0.2.10")]
        expected = {"192.0.2.1": 1, "192.0.2.10": 2, "192.0.2.100": 1}
        ips, access, _ = detection.count_linear(records)
        self.assertEqual(dict(zip(ips, access)), expected)
        self.assertEqual(detection.count_dict(records)[0], expected)


class TestDetection(unittest.TestCase):

    def test_access_threshold(self):
        """5. アクセス回数の閾値判定（閾値「以上」を検出する）"""
        self.assertEqual(detection.find_over_threshold(EXPECTED_ACCESS, 4), ["192.0.2.1"])
        self.assertEqual(detection.find_over_threshold(EXPECTED_ACCESS, 2), ["192.0.2.1", "192.0.2.2"])
        self.assertEqual(detection.find_over_threshold(EXPECTED_ACCESS, 5), [])

    def test_404_threshold(self):
        """6. 404エラー回数の閾値判定"""
        self.assertEqual(detection.find_over_threshold(EXPECTED_404, 2), ["192.0.2.1"])
        self.assertEqual(detection.find_over_threshold(EXPECTED_404, 1),
                         ["192.0.2.1", "192.0.2.2", "192.0.2.3"])

    def test_sample_log_detection(self):
        """サンプルログ：Pattern B（アクセス集中）と Pattern C（404エラー集中）を検出する"""
        records, _ = log_parser.load_log(SAMPLE_LOG)
        access, errors = detection.count_dict(records)
        self.assertEqual(detection.find_over_threshold(access, 10), ["203.0.113.50"])
        self.assertEqual(detection.find_over_threshold(errors, 5), ["198.51.100.66"])


if __name__ == "__main__":
    unittest.main()
