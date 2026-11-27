import csv
import os
import tempfile
import unittest
from datetime import date

from expense_tracker import ExpenseTracker


class ExpenseTrackerTests(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.remove(self.path)  # tracker should handle a missing file
        self.tracker = ExpenseTracker(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_starts_empty(self):
        self.assertEqual(self.tracker.list_all(), [])
        self.assertEqual(self.tracker.total(), 0)

    def test_add_and_total(self):
        self.tracker.add(10.50, "Food", "Lunch", on=date(2026, 1, 1))
        self.tracker.add(2.50, "Food", "Coffee", on=date(2026, 1, 1))
        self.assertEqual(len(self.tracker.list_all()), 2)
        self.assertEqual(self.tracker.total(), 13.00)

    def test_total_by_category(self):
        self.tracker.add(20, "Transport")
        self.tracker.add(5, "Food")
        self.tracker.add(5, "Transport")
        self.assertEqual(self.tracker.total_by_category(), {"Transport": 25, "Food": 5})

    def test_persists_to_disk(self):
        self.tracker.add(9.99, "Books")
        reloaded = ExpenseTracker(self.path)
        self.assertEqual(reloaded.total(), 9.99)

    def test_rejects_invalid_amounts(self):
        for bad in (0, -5, "abc", None):
            with self.assertRaises(ValueError):
                self.tracker.add(bad, "Food")

    def test_rejects_empty_category(self):
        with self.assertRaises(ValueError):
            self.tracker.add(10, "  ")

    def test_monthly_summary_multiple_categories(self):
        self.tracker.add(12.50, "Food", "Lunch", on=date(2026, 11, 3))
        self.tracker.add(5.00, "Food", "Coffee", on=date(2026, 11, 10))
        self.tracker.add(30.00, "Transport", "Monthly pass", on=date(2026, 11, 1))
        self.tracker.add(99.00, "Food", "Groceries", on=date(2026, 10, 28))
        result = self.tracker.monthly_summary("2026-11")
        self.assertEqual(result["month"], "2026-11")
        self.assertEqual(result["total"], 47.50)
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["by_category"], {"Food": 17.50, "Transport": 30.00})

    def test_monthly_summary_empty_month(self):
        self.tracker.add(12.50, "Food", "Lunch", on=date(2026, 11, 3))
        result = self.tracker.monthly_summary("2026-09")
        self.assertEqual(result["month"], "2026-09")
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["by_category"], {})

    def test_monthly_summary_defaults_to_current_month(self):
        today = date.today()
        self.tracker.add(20.00, "Food", "Dinner", on=today)
        other_month = date(2025, 1, 15) if today.month != 1 else date(2025, 2, 15)
        self.tracker.add(50.00, "Books", "Novel", on=other_month)
        result = self.tracker.monthly_summary()
        self.assertEqual(result["month"], today.strftime("%Y-%m"))
        self.assertEqual(result["total"], 20.00)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["by_category"], {"Food": 20.00})

    def test_monthly_summary_rejects_bad_month(self):
        for bad in ("2026-13", "Nov 2026", "2026-1", 202611):
            with self.assertRaises(ValueError):
                self.tracker.monthly_summary(bad)

    def _read_csv(self, path):
        with open(path, newline="", encoding="utf-8") as fh:
            return list(csv.reader(fh))

    def test_export_csv_writes_all_expenses(self):
        self.tracker.add(12.50, "Food", "Lunch", on=date(2026, 11, 3))
        self.tracker.add(5.00, "Transport", "Bus fare", on=date(2026, 11, 10))
        out = self.path + ".csv"
        try:
            self.assertEqual(self.tracker.export_csv(out), 2)
            rows = self._read_csv(out)
        finally:
            if os.path.exists(out):
                os.remove(out)
        self.assertEqual(rows[0], ["date", "amount", "category", "note"])
        self.assertEqual(rows[1], ["2026-11-03", "12.50", "Food", "Lunch"])
        self.assertEqual(rows[2], ["2026-11-10", "5.00", "Transport", "Bus fare"])

    def test_export_csv_filters_by_month_and_quotes_notes(self):
        self.tracker.add(12.50, "Food", 'Lunch, "with team"', on=date(2026, 11, 3))
        self.tracker.add(99.00, "Food", "Groceries", on=date(2026, 10, 28))
        out = self.path + ".csv"
        try:
            self.assertEqual(self.tracker.export_csv(out, "2026-11"), 1)
            rows = self._read_csv(out)
        finally:
            if os.path.exists(out):
                os.remove(out)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1], ["2026-11-03", "12.50", "Food", 'Lunch, "with team"'])

    def test_export_csv_empty_tracker_writes_header_only(self):
        out = self.path + ".csv"
        try:
            self.assertEqual(self.tracker.export_csv(out), 0)
            rows = self._read_csv(out)
        finally:
            if os.path.exists(out):
                os.remove(out)
        self.assertEqual(rows, [["date", "amount", "category", "note"]])

    def test_export_csv_rejects_bad_month(self):
        for bad in ("2026-13", "Nov 2026", "2026-1"):
            with self.assertRaises(ValueError):
                self.tracker.export_csv(self.path + ".csv", bad)


if __name__ == "__main__":
    unittest.main()
