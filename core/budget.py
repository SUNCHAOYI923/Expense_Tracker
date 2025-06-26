import sqlite3
import pandas as pd
from typing import Tuple
from database import ExpenseDatabase

db = ExpenseDatabase()

def set_category_budget(category: str, limit: float) -> None:
    """
    Set or update the monthly budget for a category.
    """
    db.set_budget(category, limit)

def get_category_budget(category: str) -> float:
    """
    Return the monthly_limit for the given category, or 0.0 if not defined.
    """
    budgets = db.get_budgets()
    row = budgets[budgets["category"] == category]
    return float(row["monthly_limit"].iloc[0]) if not row.empty else 0.0

def remove_category_budget(category: str) -> bool:
    """
    Remove a budget entry by category. Return True if deleted.
    """
    conn = sqlite3.connect(db.db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM budgets WHERE category = ?", (category,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted

def list_budgets() -> pd.DataFrame:
    """
    Return all budget entries as a DataFrame.
    """
    return db.get_budgets()

def check_budget(category: str) -> Tuple[bool, float]:
    """
    Check if a category is over its budget.
    Returns (is_over_budget, remaining_amount).
    """
    summary = db.get_spending_summary()
    row = summary[summary["category"] == category]
    if row.empty:
        return (False, 0.0)
    rem = float(row["remaining"].iloc[0])
    return (rem < 0, rem)

def budget_alerts(threshold: float = 0.0) -> pd.DataFrame:
    """
    Return categories whose remaining budget is <= threshold.
    """
    summary = db.get_spending_summary()
    return summary[summary["remaining"] <= threshold]