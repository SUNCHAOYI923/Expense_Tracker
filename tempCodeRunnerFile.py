# main.py
from database import ExpenseDatabase
import pandas as pd
from pathlib import Path

def print_table(df: pd.DataFrame, title: str) -> None:
    print(f"\n=== {title} ===")
    if df.empty:
        print("No data")
    else:
        print(df.to_string(index=False))

def test_database() -> None:
    print("=== Expense Database Test ===")
    db = ExpenseDatabase()

    # 1. Add sample transactions
    print("\n1. Adding Transactions...")
    samples = [
        {"date":"2023-01-10","amount":-150.0,"category":"food","type":"expense"},
        {"date":"2023-01-15","amount":5000.0,"category":"salary","type":"income"},
        {"date":"2023-01-20","amount":-200.0,"category":"transport","type":"expense"}
    ]
    for t in samples:
        db.add_transaction(t)
    print_table(db.get_transactions(), "All Transactions")

    # 2. Set budgets
    print("\n2. Setting Budgets...")
    db.set_budget("food",500.0)
    db.set_budget("transport",300.0)
    print_table(db.get_budgets(), "Current Budgets")

    # 3. Spending summary
    print("\n3. Spending Summary:")
    summary = db.get_spending_summary()
    print_table(summary, "Detailed Summary")

    # 4. Export
    print("\n4. Exporting data...")
    export_path = "data/transactions.csv"
    db.export_to_csv(export_path)
    print(f"Data exported to {export_path}")

if __name__ == "__main__":
    # ensure data folder exists
    Path("data").mkdir(exist_ok=True)
    test_database()
    print("\nAll tests completed!")