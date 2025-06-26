from typing import Optional
import pandas as pd
import sqlite3
from database import ExpenseDatabase

db = ExpenseDatabase()

def add_expense(date: str, amount: float, category: str, description: str) -> int:
    """Add an expense transaction and return its ID."""
    data = {
        "date": date,
        "amount": -abs(float(amount)),
        "category": category,
        "description": description,
        "type": "expense"
    }
    db.add_transaction(data)
    return _get_last_id()

def add_income(date: str, amount: float, category: str, description: str) -> int:
    """Add an income transaction and return its ID."""
    data = {
        "date": date,
        "amount": abs(float(amount)),
        "category": category,
        "description": description,
        "type": "income"
    }
    db.add_transaction(data)
    return _get_last_id()

def remove_transaction(tx_id: int) -> bool:
    """Remove a transaction by ID."""
    with sqlite3.connect(db.db_path) as conn:
        return conn.execute(
            "DELETE FROM transactions WHERE id = ?", (tx_id,)
        ).rowcount > 0

def get_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None
) -> pd.DataFrame:
    """Retrieve transactions with optional filters."""
    df = db.get_transactions(start_date, end_date)
    return df[df["category"] == category] if category else df

def _get_last_id() -> int:
    """Internal helper to get last inserted ID."""
    with sqlite3.connect(db.db_path) as conn:
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]