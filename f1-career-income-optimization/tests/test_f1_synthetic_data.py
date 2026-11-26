# F-1：Tiny Dataset（人工データ）の再現性・境界条件、データ検証、Mini と Tiny のキー名の一致のテスト。
#   <python> -m unittest tests.test_f1_synthetic_data -v

import csv
import importlib.util
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

spec = importlib.util.spec_from_file_location("gen", PROJECT_DIR / "scripts" / "generate_synthetic_data.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

COLUMNS = {
    "f1a/career_options_tiny.csv": ["career_id", "career_name", "start_age", "retirement_age",
                                    "initial_salary", "annual_growth", "education_cost"],
    "f1b/work_options_tiny.csv": ["option_id", "work_style", "annual_income", "weekly_work_hours"],
    "f1b/household_scenarios_tiny.csv": ["scenario_id", "living_cost", "childcare_cost", "eldercare_cost",
                                         "required_childcare_hours", "required_eldercare_hours"],
    "f1c/housing_options_tiny.csv": ["housing_id", "area", "purchase_price", "monthly_rent", "floor_area",
                                     "annual_maintenance_cost", "commute_minutes"],
    "f1d/family_members_tiny.csv": ["person_id", "family_id", "generation", "role", "age", "annual_income",
                                    "annual_expense", "initial_assets"],
    "f1d/transfer_scenarios_tiny.csv": ["scenario_id", "sender_role", "receiver_role", "annual_transfer",
                                        "start_year", "duration_years"],
}


def read(rel):
    with open(DATA_DIR / rel, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


class TestTinyDatasets(unittest.TestCase):

    def test_files_match_generator(self):
        """CSV は生成スクリプトの結果と一致する（シード固定で再現できる）"""
        for rel, text in gen.generate_all().items():
            self.assertEqual((DATA_DIR / rel).read_text(encoding="utf-8"), text, rel)

    def test_reproducible(self):
        self.assertEqual(gen.generate_all(), gen.generate_all())

    def test_columns_and_unique_ids(self):
        for rel, cols in COLUMNS.items():
            rows = read(rel)
            self.assertEqual(list(rows[0].keys()), cols, rel)
            ids = [r[cols[0]] for r in rows]
            self.assertEqual(len(ids), len(set(ids)), f"{rel} の ID が重複")

    def test_row_counts(self):
        sizes = {rel: len(read(rel)) for rel in COLUMNS}
        for rel, n in sizes.items():
            if rel != "f1b/work_options_tiny.csv":   # 勤務形態は種類の一覧なので少ない
                self.assertTrue(20 <= n <= 50, f"{rel}: {n} 件")

    def test_boundary_cases_present(self):
        prices = [int(r["purchase_price"]) for r in read("f1c/housing_options_tiny.csv")]
        self.assertLess(len(set(prices)), len(prices), "同じ価格の物件がない")
        self.assertIn("0", {r["annual_transfer"] for r in read("f1d/transfer_scenarios_tiny.csv")})
        self.assertIn("0.0", {r["annual_growth"] for r in read("f1a/career_options_tiny.csv")})
        hh = read("f1b/household_scenarios_tiny.csv")
        self.assertTrue(any(int(r["required_childcare_hours"]) + int(r["required_eldercare_hours"]) > 2 * (168 - 77)
                            for r in hh), "時間の制約に違反する世帯がない")
        members = read("f1d/family_members_tiny.csv")
        self.assertTrue(any(int(r["annual_income"]) < int(r["annual_expense"]) for r in members
                            if r["role"] == "parent"), "赤字の親がいない")


class TestValidationAndSchema(unittest.TestCase):

    def test_validate_datasets_has_no_errors(self):
        """validate_datasets.py：データの破損 0 件、意図的な境界条件がすべて存在する"""
        spec = importlib.util.spec_from_file_location("val", PROJECT_DIR / "scripts" / "validate_datasets.py")
        val = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(val)
        res = val.validate(val.Result())
        self.assertEqual(res.errors, [])
        self.assertGreaterEqual(len(res.boundaries), 19)

    def test_mini_keys_match_tiny_columns(self):
        """Notebook の Mini Dataset のキーが、同じ意味の Tiny Dataset の列名と一致する"""
        import importlib
        if importlib.util.find_spec("nbformat") is None:
            self.skipTest("nbformat がない")
        spec = importlib.util.spec_from_file_location("nb", PROJECT_DIR / "scripts" / "build_notebook.py")
        nb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(nb)
        import textwrap
        ns = {"show_records": lambda *a, **k: None, "print": lambda *a, **k: None}
        for theme in (nb.F1A, nb.F1B, nb.F1C, nb.F1D):
            exec(textwrap.dedent(theme["mini_code"]), ns)
        pairs = [
            (ns["career_options"], "f1a/career_options_tiny.csv", set()),
            (ns["work_options"], "f1b/work_options_tiny.csv", set()),
            ([ns["household"]], "f1b/household_scenarios_tiny.csv", set()),
            (ns["housing_options"], "f1c/housing_options_tiny.csv", set()),
            (ns["family"], "f1d/family_members_tiny.csv", set()),
            # Tiny の移転シナリオには ID と送り手・受け手の列が追加されている
            (ns["transfer_options"], "f1d/transfer_scenarios_tiny.csv", {"scenario_id", "sender_role", "receiver_role"}),
        ]
        for mini, rel, tiny_only in pairs:
            columns = set(read(rel)[0].keys())
            for row in mini:
                self.assertEqual(set(row.keys()), columns - tiny_only, rel)


if __name__ == "__main__":
    unittest.main()
