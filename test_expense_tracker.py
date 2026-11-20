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


if __name__ == "__main__":
    unittest.main()
