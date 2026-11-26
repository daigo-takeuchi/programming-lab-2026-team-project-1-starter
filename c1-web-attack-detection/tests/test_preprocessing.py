# C-1：Phase 2A の前処理（C-1B・C-1C・C-1D）のテスト
#
# 実行（c1-web-attack-detection ディレクトリで）:
#   python3 -m unittest tests.test_preprocessing -v
#
# 原データ（data/raw/loghub/、Git 管理外）がない環境では、再現性のテストだけをスキップする。

import csv
import ipaddress
import re
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
SCRIPTS = PROJECT_DIR / "scripts"
RAW_LOGHUB = DATA_DIR / "raw" / "loghub"
IPV4 = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
DOC_NETS = [ipaddress.ip_network(n) for n in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")]

PUBLIC_OUTPUTS = ["c1b/authentication_small.csv", "c1b/ssh_events_small.csv", "c1d/system_events_small.csv"]


def read(rel_path):
    with open(DATA_DIR / rel_path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


class TestReproducible(unittest.TestCase):

    def run_check(self, script):
        result = subprocess.run([sys.executable, str(SCRIPTS / script), "--check"],
                                capture_output=True, text=True, cwd=PROJECT_DIR)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless((RAW_LOGHUB / "OpenSSH_2k.log_structured.csv").exists(), "原データがない")
    def test_c1b(self):
        self.run_check("preprocess_c1b.py")

    def test_c1c(self):
        self.run_check("preprocess_c1c.py")

    @unittest.skipUnless((RAW_LOGHUB / "Linux_2k.log_structured.csv").exists(), "原データがない")
    def test_c1d(self):
        self.run_check("preprocess_c1d.py")


@unittest.skipUnless(all((DATA_DIR / f).exists() for f in PUBLIC_OUTPUTS),
                     "Loghub 由来の CSV がない（Git 管理外。前処理スクリプトで作成する）")
class TestPublicLogOutputs(unittest.TestCase):

    def test_no_real_ip_addresses(self):
        """公開ログ由来の CSV に、匿名化されていない IP アドレスが残っていない"""
        for rel_path in PUBLIC_OUTPUTS:
            text = (DATA_DIR / rel_path).read_text(encoding="utf-8")
            with self.subTest(rel_path):
                self.assertEqual(IPV4.findall(text), [])

    def test_labels_are_unknown(self):
        """公開ログには正解ラベルがないので、label はすべて unknown（正常に置き換えていない）"""
        for rel_path in PUBLIC_OUTPUTS:
            with self.subTest(rel_path):
                self.assertEqual({r["label"] for r in read(rel_path)}, {"unknown"})

    def test_auth_result_is_not_label(self):
        """認証結果（result）と攻撃ラベル（label）は別の列で、result は success / failure だけ"""
        rows = read("c1b/authentication_small.csv")
        self.assertEqual({r["result"] for r in rows}, {"success", "failure"})
        self.assertEqual(len(rows), 525)
        self.assertEqual(sum(r["result"] == "success" for r in rows), 1)   # 比率は調整していない

    def test_auth_rows_are_attempts_only(self):
        """認証の試行の行だけを含み、pam_unix などの重複記録を含まない"""
        rows = read("c1b/authentication_small.csv")
        self.assertTrue(all(re.search(r"(Accepted|Failed) (password|none) for", r["message"]) for r in rows))
        repeated = [r for r in rows if r["event_type"] == "failed_password_repeated"]
        self.assertEqual([int(r["repeat_count"]) for r in repeated], [5, 5])

    def test_source_lines_point_to_original(self):
        """source_line が原データの行番号として正しい範囲にある"""
        for rel_path in PUBLIC_OUTPUTS:
            lines = [int(r["source_line"]) for r in read(rel_path)]
            with self.subTest(rel_path):
                self.assertTrue(all(1 <= n <= 2000 for n in lines))
                self.assertEqual(lines, sorted(lines))

    def test_license_notice_included(self):
        """Loghub のライセンス文が、出力 CSV と同じフォルダにある（全コピーへの同梱が条件）"""
        for folder in ("c1b", "c1d"):
            text = (DATA_DIR / folder / "LICENSE_LOGHUB.txt").read_text(encoding="utf-8")
            with self.subTest(folder):
                self.assertIn("LICENSE OF LOGHUB", text)
                self.assertIn("https://github.com/logpai/loghub", text)

    def test_no_year_fabricated(self):
        """原データに年がないため、日付は MM-DD だけで、年を付けていない"""
        for rel_path in PUBLIC_OUTPUTS:
            row = read(rel_path)[0]
            with self.subTest(rel_path):
                self.assertNotIn("timestamp", row)
                self.assertRegex(row["log_date"], r"^\d\d-\d\d$")


class TestSyntheticAccessLog(unittest.TestCase):

    def test_named_as_synthetic(self):
        """人工データは、公開データ由来の _small.csv と区別できる名前にする"""
        self.assertTrue((DATA_DIR / "c1c" / "web_access_log_synthetic.csv").exists())
        self.assertFalse((DATA_DIR / "c1c" / "http_requests_small.csv").exists())

    def test_matches_legacy_parser(self):
        """旧教材のパーサーと同じ件数（47 件）で、scenario は攻撃ラベル（label）として扱っていない"""
        rows = read("c1c/web_access_log_synthetic.csv")
        self.assertEqual(len(rows), 47)
        self.assertNotIn("label", rows[0])
        self.assertEqual(sum(r["scenario"] == "access_concentration" for r in rows), 15)
        self.assertEqual(sum(r["scenario"] == "error_404_concentration" for r in rows), 9)
        for r in rows:
            self.assertTrue(any(ipaddress.ip_address(r["src_ip"]) in net for net in DOC_NETS))


if __name__ == "__main__":
    unittest.main()
