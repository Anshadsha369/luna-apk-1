"""
Finance Tracking - monitors expenses, bills, budgets, and provides insights.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path

FINANCE_DIR = Path.home() / ".luna_memory" / "finance"
FINANCE_DIR.mkdir(parents=True, exist_ok=True)
EXPENSES_FILE = FINANCE_DIR / "expenses.json"
BUDGETS_FILE = FINANCE_DIR / "budgets.json"
BILLS_FILE = FINANCE_DIR / "bills.json"


class FinanceAgent:
    def __init__(self):
        self.expenses = self._load(EXPENSES_FILE, [])
        self.budgets = self._load(BUDGETS_FILE, {})
        self.bills = self._load(BILLS_FILE, [])

    def _load(self, path, default):
        if path.exists():
            try:
                return json.loads(path.read_text())
            except Exception:
                pass
        return default

    def _save_expenses(self):
        EXPENSES_FILE.write_text(json.dumps(self.expenses, indent=2))

    def _save_budgets(self):
        BUDGETS_FILE.write_text(json.dumps(self.budgets, indent=2))

    def _save_bills(self):
        BILLS_FILE.write_text(json.dumps(self.bills, indent=2))

    def add_expense(self, amount, category, description=""):
        expense = {
            "amount": amount,
            "category": category,
            "description": description,
            "date": datetime.now().isoformat(),
            "id": int(time.time())
        }
        self.expenses.append(expense)
        self._save_expenses()
        return f"Logged: {description} for ${amount} in {category}"

    def get_monthly_spending(self):
        this_month = datetime.now().strftime("%Y-%m")
        monthly = [e for e in self.expenses if e["date"].startswith(this_month)]
        total = sum(e["amount"] for e in monthly)
        by_category = {}
        for e in monthly:
            cat = e["category"]
            by_category[cat] = by_category.get(cat, 0) + e["amount"]
        return {"total": total, "by_category": by_category, "count": len(monthly)}

    def set_budget(self, category, amount):
        self.budgets[category] = {"amount": amount, "period": "monthly"}
        self._save_budgets()
        return f"Budget set: ${amount}/month for {category}"

    def check_budgets(self):
        spending = self.get_monthly_spending()
        alerts = []
        for category, budget in self.budgets.items():
            spent = spending["by_category"].get(category, 0)
            if spent > budget["amount"]:
                alerts.append(f"⚠ {category}: ${spent} spent of ${budget['amount']} budget (OVER!)")
            elif spent > budget["amount"] * 0.8:
                alerts.append(f"⚠ {category}: ${spent} / ${budget['amount']} (80% used)")
        return alerts or ["All budgets on track"]

    def add_bill(self, name, amount, due_day, category="general"):
        bill = {
            "name": name,
            "amount": amount,
            "due_day": due_day,
            "category": category,
            "paid": False
        }
        self.bills.append(bill)
        self._save_bills()
        return f"Added bill: {name} - ${amount} due on day {due_day}"

    def get_upcoming_bills(self, days=7):
        today = datetime.now().day
        upcoming = []
        for bill in self.bills:
            if not bill.get("paid"):
                due = bill["due_day"]
                if due >= today and due <= today + days:
                    upcoming.append(bill)
                elif due < today and due + 30 <= today + days:
                    upcoming.append(bill)
        return upcoming

    def mark_bill_paid(self, name):
        for bill in self.bills:
            if bill["name"].lower() == name.lower():
                bill["paid"] = True
                self._save_bills()
                return f"Marked '{name}' as paid"
        return f"Bill '{name}' not found"

    def get_summary(self):
        monthly = self.get_monthly_spending()
        upcoming = self.get_upcoming_bills(7)
        alerts = self.check_budgets()
        return {
            "monthly_spending": monthly,
            "upcoming_bills": upcoming,
            "alerts": alerts,
        }
