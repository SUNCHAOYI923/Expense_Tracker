import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, Union

class ExpenseDatabase:
    def __init__(self, db_path: str = "resources/data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    type TEXT CHECK(type IN ('income','expense'))
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    category TEXT PRIMARY KEY,
                    monthly_limit REAL NOT NULL
                )
            """)

    def add_transaction(self, data: Union[dict, pd.DataFrame]) -> None:
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        elif isinstance(data, pd.Series):
            df = data.to_frame().T
        else:
            df = data.copy()
        for col in ("date","amount","category","description","type"):
            if col not in df.columns:
                df[col] = "" if col=="description" else None
        df = df[["date","amount","category","description","type"]]
        with self._get_conn() as conn:
            df.to_sql("transactions", conn, if_exists="append", index=False)

    def get_transactions(self,
                         start_date: Optional[str]=None,
                         end_date:   Optional[str]=None
                        ) -> pd.DataFrame:
        sql = "SELECT * FROM transactions"
        params = []
        if start_date or end_date:
            cond = []
            if start_date:
                cond.append("date>=?"); params.append(start_date)
            if end_date:
                cond.append("date<=?"); params.append(end_date)
            sql += " WHERE " + " AND ".join(cond)
        with self._get_conn() as conn:
            return pd.read_sql(sql, conn, params=params or None, parse_dates=["date"])

    def set_budget(self, category: str, limit: float) -> None:
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO budgets(category, monthly_limit)
                VALUES(?,?)
                ON CONFLICT(category) DO UPDATE
                  SET monthly_limit = excluded.monthly_limit
            """, (category, limit))

    def get_budgets(self) -> pd.DataFrame:
        with self._get_conn() as conn:
            return pd.read_sql("SELECT category, monthly_limit FROM budgets", conn)

    def get_spending_summary(self) -> pd.DataFrame:
        with self._get_conn() as conn:
            spending = pd.read_sql(
                "SELECT category, SUM(amount) AS expense "
                "FROM transactions WHERE type='expense' GROUP BY category",
                conn
            )
            budgets = pd.read_sql("SELECT category, monthly_limit FROM budgets", conn)
        merged = pd.merge(budgets, spending, on="category", how="left").fillna(0)
        merged["remaining"] = merged["monthly_limit"] + merged["expense"]
        return merged[["category","expense","monthly_limit","remaining"]]

    def export_to_csv(self, filepath: str) -> None:
        df = self.get_transactions().drop(columns=["description"])  # drop empty column
        out = Path(filepath)
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out, index=False)