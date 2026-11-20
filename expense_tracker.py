"""Expense Tracker CLI - track personal expenses stored in a JSON file.

Usage:
    python expense_tracker.py add 12.50 Food "Lunch"
    python expense_tracker.py list
    python expense_tracker.py summary
"""
import argparse
import json
import os
import sys
from datetime import date


class ExpenseTracker:
    """Stores expenses as JSON and provides add/list/summary operations."""

    def __init__(self, storage_path="expenses.json"):
        self.storage_path = storage_path
        self.expenses = self._load()

    def _load(self):
        if not os.path.exists(self.storage_path):
            return []
        with open(self.storage_path, "r", encoding="utf-8") as fh:
            try:
                data = json.load(fh)
            except json.JSONDecodeError:
                return []
        return data if isinstance(data, list) else []

    def _save(self):
        with open(self.storage_path, "w", encoding="utf-8") as fh:
            json.dump(self.expenses, fh, indent=2)

    def add(self, amount, category, note="", on=None):
        try:
            amount = round(float(amount), 2)
        except (TypeError, ValueError):
            raise ValueError("Amount must be a number.")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        if not category or not str(category).strip():
            raise ValueError("Category is required.")
        entry = {
            "amount": amount,
            "category": str(category).strip(),
            "note": str(note).strip(),
            "date": (on or date.today()).isoformat(),
        }
        self.expenses.append(entry)
        self._save()
        return entry

    def list_all(self):
        return list(self.expenses)

    def total(self):
        return round(sum(e["amount"] for e in self.expenses), 2)

    def total_by_category(self):
        totals = {}
        for e in self.expenses:
            totals[e["category"]] = round(totals.get(e["category"], 0) + e["amount"], 2)
        return totals


def main(argv=None):
    parser = argparse.ArgumentParser(description="Track personal expenses from the command line.")
    parser.add_argument("--file", default="expenses.json", help="Path to the JSON storage file.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add an expense.")
    p_add.add_argument("amount", type=float)
    p_add.add_argument("category")
    p_add.add_argument("note", nargs="?", default="")

    sub.add_parser("list", help="List all expenses.")
    sub.add_parser("summary", help="Show totals overall and per category.")

    args = parser.parse_args(argv)
    tracker = ExpenseTracker(args.file)

    if args.command == "add":
        try:
            entry = tracker.add(args.amount, args.category, args.note)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        print(f"Added: {entry['amount']:.2f} [{entry['category']}] {entry['note']}".rstrip())
    elif args.command == "list":
        if not tracker.list_all():
            print("No expenses recorded yet.")
        for e in tracker.list_all():
            print(f"{e['date']}  {e['amount']:>8.2f}  {e['category']:<15} {e['note']}".rstrip())
    elif args.command == "summary":
        print(f"Total spent: {tracker.total():.2f} across {len(tracker.list_all())} expense(s).")
        for category, amount in sorted(tracker.total_by_category().items()):
            print(f"  {category:<15} {amount:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
