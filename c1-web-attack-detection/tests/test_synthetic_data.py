# C-1：人工データ（Tiny Dataset）とデータ検証スクリプトのテスト
#
# 実行（c1-web-attack-detection ディレクトリで）:
#   python3 -m unittest tests.test_synthetic_data -v

import csv
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
SCRIPTS = PROJECT_DIR / "scripts"


def read(rel_path):
    with open(DATA_DIR / rel_path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


class TestGenerator(unittest.TestCase):

    def test_reproducible(self):
        """再生成した結果が、リポジトリ内の CSV と完全に一致する（シード固定）"""
        result = subprocess.run([sys.executable, str(SCRIPTS / "generate_synthetic_data.py"), "--check"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validation_passes(self):
        """データ品質検証スクリプトで問題が見つからない"""
        result = subprocess.run([sys.executable, str(SCRIPTS / "validate_datasets.py")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class TestTinyDesign(unittest.TestCase):
    """教材として意図した特徴（正常・異常・境界の例）がデータに含まれていることを確認する"""

    def test_sizes(self):
        for rel_path in ["c1a/network_flows_tiny.csv", "c1b/authentication_tiny.csv",
                         "c1c/http_requests_tiny.csv", "c1e/data_transfer_tiny.csv"]:
            with self.subTest(rel_path):
                self.assertTrue(20 <= len(read(rel_path)) <= 50)

    def test_c1a_has_scan_and_boundary(self):
        rows = read("c1a/network_flows_tiny.csv")
        ports = {r["dst_port"] for r in rows if r["src_ip"] == "192.0.2.15"}
        self.assertGreaterEqual(len(ports), 10)                                  # ポートスキャン
        self.assertEqual(sum(r["src_ip"] == "192.0.2.14" for r in rows), 8)     # 境界例
        self.assertTrue(all(r["label"] == "benign" for r in rows if r["src_ip"] == "192.0.2.14"))

    def test_c1b_success_after_failures(self):
        rows = [r for r in read("c1b/authentication_tiny.csv") if r["user_id"] == "user04"]
        self.assertEqual([r["result"] for r in rows], ["failure"] * 8 + ["success"])

    def test_c1c_contains_false_positive_example(self):
        rows = read("c1c/http_requests_tiny.csv")
        self.assertTrue(any("'" in r["url"] and r["label"] == "benign" for r in rows))

    def test_c1d_changes(self):
        before = {r["file_id"]: r["hash"] for r in read("c1d/file_states_before_tiny.csv")}
        after = {r["file_id"]: r["hash"] for r in read("c1d/file_states_after_tiny.csv")}
        self.assertEqual(sorted(before.keys() - after.keys()), ["photo_001.jpg", "photo_002.jpg", "users.csv"])
        self.assertEqual(len(after.keys() - before.keys()), 4)
        modified = [k for k in before.keys() & after.keys() if before[k] != after[k]]
        self.assertEqual(sorted(modified), ["app.log", "config.ini", "hosts.txt"])

    def test_c1e_benign_large_transfer_exists(self):
        rows = read("c1e/data_transfer_tiny.csv")
        self.assertTrue(any(r["label"] == "benign" and int(r["byte_count"]) >= 500_000 for r in rows))


if __name__ == "__main__":
    unittest.main()
