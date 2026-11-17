# C1：ログ読み込みのテスト

import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import log_parser

LINE = '192.0.2.10 - - [15/Nov/2026:10:00:01 +0900] "GET /index.html HTTP/1.1" 200 1024'
SAMPLE_LOG = Path(__file__).parent.parent / "data" / "sample_access.log"


class TestParseLine(unittest.TestCase):

    def test_valid_line(self):
        """1. 正常なログ行を読み込める"""
        record = log_parser.parse_line(LINE)
        self.assertIsNotNone(record)
        self.assertEqual(record["size"], 1024)

    def test_ip(self):
        """2. IPアドレスを正しく抽出できる"""
        self.assertEqual(log_parser.parse_line(LINE)["ip"], "192.0.2.10")

    def test_timestamp(self):
        """3. 日時を正しく抽出できる（タイムゾーン +0900 を含む）"""
        expected = datetime(2026, 11, 15, 10, 0, 1, tzinfo=timezone(timedelta(hours=9)))
        self.assertEqual(log_parser.parse_line(LINE)["timestamp"], expected)

    def test_method_and_path(self):
        """4. HTTPメソッドとURLパスを正しく抽出できる"""
        record = log_parser.parse_line(
            '198.51.100.7 - - [15/Nov/2026:10:00:02 +0900] "POST /cart/add?id=3 HTTP/1.1" 302 0')
        self.assertEqual(record["method"], "POST")
        self.assertEqual(record["path"], "/cart/add?id=3")

    def test_status(self):
        """5. ステータスコードを整数として正しく抽出できる"""
        record = log_parser.parse_line(
            '203.0.113.5 - - [15/Nov/2026:10:00:03 +0900] "GET /missing HTTP/1.1" 404 -')
        self.assertEqual(record["status"], 404)
        self.assertIsNone(record["size"])       # サイズ "-" は None

    def test_invalid_lines(self):
        """6. 不正なログ行は None になる（例外で止まらない）"""
        invalid = [
            "",
            "this is not a log line",
            '192.0.2.10 - - [15/Nov/2026:10:00:01 +0900] "GET /index.html HTTP/1.1" - 1024',  # ステータスなし
            '192.0.2.10 - - [15/Nov/2026:10:00:01 +0900] "GET /index.html HTTP/1.1" 200',     # サイズなし
            '999.0.2.10 - - [15/Nov/2026:10:00:01 +0900] "GET / HTTP/1.1" 200 10',          # 不正なIP
            '192.0.2.10 - - [32/Nov/2026:10:00:01 +0900] "GET / HTTP/1.1" 200 10',          # 不正な日付
            '192.0.2.10 - - [15/Nov/2026:10:00:01 +0900] "GET / HTTP/1.1" 2000 10',         # 4桁のステータス
        ]
        for line in invalid:
            with self.subTest(line=line):
                self.assertIsNone(log_parser.parse_line(line))


class TestLoadLog(unittest.TestCase):

    def test_sample_log(self):
        """サンプルログ：47件を読み込み、不正な1行（29行目）を別に記録する"""
        records, invalid_lines = log_parser.load_log(SAMPLE_LOG)
        self.assertEqual(len(records), 47)
        self.assertEqual(len(invalid_lines), 1)
        line_number, line = invalid_lines[0]
        self.assertEqual(line_number, 29)
        self.assertIn('" - 1024', line)
        # 不正な行は records に含まれない
        self.assertNotIn(datetime(2026, 11, 15, 10, 13, 0, tzinfo=timezone(timedelta(hours=9))),
                         [r["timestamp"] for r in records])


if __name__ == "__main__":
    unittest.main()
