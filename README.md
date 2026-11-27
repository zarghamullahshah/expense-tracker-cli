# Expense Tracker CLI (Python)

A small, dependency-free command-line expense tracker. Expenses are stored in a local JSON file — add them, list them, and see totals overall and per category.

## Requirements

- Python 3.9+ (standard library only)

## Usage

```bash
# Add expenses: amount, category, optional note
python expense_tracker.py add 12.50 Food "Lunch with team"
python expense_tracker.py add 3.20 Transport "Bus fare"

# List everything
python expense_tracker.py list

# Totals overall and per category
python expense_tracker.py summary

# Monthly summary: per-category totals, overall total and count for one month
# (defaults to the current month when no month is given)
python expense_tracker.py monthly 2026-11
python expense_tracker.py monthly

# Export expenses to CSV (header: date,amount,category,note)
python expense_tracker.py export expenses.csv
python expense_tracker.py export nov.csv 2026-11   # one month only

# Use a different storage file
python expense_tracker.py --file my-expenses.json list
```

## Run the tests

```bash
python -m unittest test_expense_tracker -v
```

## Project structure

```
├── expense_tracker.py        # CLI + ExpenseTracker class
└── test_expense_tracker.py   # Unit tests (unittest, temp-file storage)
```

## Author

**Zargham Ullah Shah** — Full Stack Web Developer | Salesforce CRM Specialist
GitHub: [@zarghamullahshah](https://github.com/zarghamullahshah)
