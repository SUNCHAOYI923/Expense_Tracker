# main_cli.py – Interactive CLI for Smart Expense Tracker

import os
from pathlib import Path
import pandas as pd

from database import ExpenseDatabase
from core.tracker import add_expense, add_income, get_transactions, remove_transaction
from core.budget import (
    set_category_budget,
    get_category_budget,
    remove_category_budget,
    list_budgets,
    check_budget,
    budget_alerts
)
from core.reports import (
    generate_monthly_report,
    generate_category_report,
    generate_budget_report,
    get_monthly_trend
)

EXPORT_CSV = "data/transactions_export.csv"

def print_table(df: pd.DataFrame, title: str = ""):
    if title:
        print(f"\n=== {title} ===")
    if df.empty:
        print("No data")
    else:
        print(df.to_string(index=False))

def reset_test_environment():
    """
    Clear all data in the database tables (no file deletion)
    and remove old CSV export.
    """
    print("🔄 Resetting test environment...")
    db = ExpenseDatabase()
    db.clear_all()  
    print("All tables cleared.")
    if os.path.exists(EXPORT_CSV):
        os.remove(EXPORT_CSV)
        print(f"Removed old CSV: {EXPORT_CSV}")
    Path("data").mkdir(exist_ok=True)
    Path("resources").mkdir(exist_ok=True)

def menu():
    print("""
Please select an option:
1. Add expense
2. Add income
3. List transactions
4. Remove a transaction
5. Export to CSV
6. Set budget
7. List budgets
8. Remove a budget
9. Show spending summary
10. Monthly report
11. Category report
12. Budget report
13. Yearly trend report
0. Exit
""")

def main():
    reset_test_environment()
    db = ExpenseDatabase()
    while True:
        menu()
        choice = input("Enter choice: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        try:
            if choice == "1":
                d   = input("Date (YYYY-MM-DD): ").strip()
                amt = float(input("Amount: "))
                cat = input("Category: ").strip()
                desc= input("Description: ").strip()
                add_expense(d, amt, cat, desc)
                print("Expense added.")
            elif choice == "2":
                d   = input("Date (YYYY-MM-DD): ").strip()
                amt = float(input("Amount: "))
                cat = input("Category: ").strip()
                desc= input("Description: ").strip()
                add_income(d, amt, cat, desc)
                print("Income added.")
            elif choice == "3":
                df = get_transactions()
                print_table(df, "All Transactions")
            elif choice == "4":
                tx_id = int(input("Transaction ID to remove: "))
                ok = remove_transaction(tx_id)
                print("Removed." if ok else "ID not found.")
            elif choice == "5":
                db.export_to_csv(EXPORT_CSV)
                print(f"Exported to {EXPORT_CSV}")
            elif choice == "6":
                cat = input("Budget Category: ").strip()
                lim = float(input("Monthly limit: "))
                set_category_budget(cat, lim)
                print("Budget set.")
            elif choice == "7":
                df = list_budgets()
                print_table(df, "Budgets")
            elif choice == "8":
                cat = input("Budget category to remove: ").strip()
                ok = remove_category_budget(cat)
                print("Removed." if ok else "Not found.")
            elif choice == "9":
                df = db.get_spending_summary()
                print_table(df, "Spending Summary")
            elif choice == "10":
                month = input("Month (YYYY-MM): ").strip()
                rep   = generate_monthly_report(month)
                print(rep)
            elif choice == "11":
                month = input("Month (YYYY-MM): ").strip()
                df = generate_category_report(month)
                print_table(df, "Category Report")
            elif choice == "12":
                month = input("Month (YYYY-MM): ").strip()
                df = generate_budget_report(month)
                print_table(df, "Budget Report")
            elif choice == "13":
                year = input("Year (YYYY): ").strip()
                df = get_monthly_trend(year)
                print_table(df, f"Trend for {year}")
            else:
                print("Invalid choice, try again.")
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()