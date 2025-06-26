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
from vis import (
    plot_monthly_summary,
    plot_category_spending,
    plot_budget_status,
    plot_monthly_trend
)

# Constants
EXPORT_CSV = "data/transactions_export.csv"
DB_PATH = "resources/data.db"

def print_table(df: pd.DataFrame, title: str) -> None:
    """Print DataFrame with a title."""
    print(f"\n=== {title} ===")
    if df.empty:
        print("No data")
    else:
        print(df.to_string(index=False))

# ———————————————————————————————
# Clean up old data
# ———————————————————————————————
def reset_test_environment():
    print("🔄 Resetting test environment...")
    # 1. Remove old database
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed old database: {DB_PATH}")

    # 2. Remove old CSV
    if os.path.exists(EXPORT_CSV):
        os.remove(EXPORT_CSV)
        print(f"Removed old CSV: {EXPORT_CSV}")

    # 3. Ensure required folders exist
    Path("data").mkdir(exist_ok=True)
    Path("resources").mkdir(exist_ok=True)

# ———————————————————————————————
# 1. Test database.py and tracker.py
# ———————————————————————————————
def test_database_operations() -> None:
    print("=== Expense Tracker Test Suite ===")
    db = ExpenseDatabase()

    print("\n1. Adding sample transactions...")
    add_expense("2023-01-10", 150.0, "food", "Lunch with team")
    add_income("2023-01-15", 5000.0, "salary", "January salary")
    add_expense("2023-01-20", 200.0, "transport", "Monthly pass")
    print_table(get_transactions(), "All Transactions")

    print("\n2. Exporting data to CSV...")
    db.export_to_csv(EXPORT_CSV)
    print(f"Exported to: {EXPORT_CSV}")

    print("\n3. Removing transaction with ID=1...")
    success = remove_transaction(1)
    print(f"Transaction removed: {success}")
    print_table(get_transactions(), "Transactions after removal")

# ———————————————————————————————
# 2. Test budget.py
# ———————————————————————————————
def test_budget_module() -> None:
    print("\n=== Budget Module Test ===")

    print("\n4. Setting category budgets...")
    set_category_budget("food", 500.0)
    set_category_budget("transport", 300.0)
    set_category_budget("entertainment", 200.0)
    print_table(list_budgets(), "Budgets after setting")

    print("\n5. Getting category budget limits:")
    for cat in ["food", "transport", "entertainment", "salary"]:
        limit = get_category_budget(cat)
        print(f"- {cat}: {limit}")

    print("\n6. Removing 'entertainment' budget...")
    removed = remove_category_budget("entertainment")
    print(f"Removed entertainment: {removed}")
    print_table(list_budgets(), "Budgets after removal")

    print("\n7. Checking budget status:")
    for cat in ["food", "transport", "salary"]:
        over, rem = check_budget(cat)
        print(f"- {cat}: over={over}, remaining={rem}")

    print("\n8. Budget alerts (threshold=0):")
    alerts = budget_alerts(threshold=0)
    print_table(alerts, "Categories over or at limit")

# ———————————————————————————————
# 3. Test reports.py
# ———————————————————————————————
def test_report_module() -> None:
    print("\n=== Reports Module Test ===")

    print("\n9. Monthly report for 2023-01:")
    report = generate_monthly_report("2023-01")
    print(report)

    print("\n10. Category report for 2023-01:")
    print_table(generate_category_report("2023-01"), "Category Report")

    print("\n11. Budget report for 2023-01:")
    print_table(generate_budget_report("2023-01"), "Budget Report")

    print("\n12. Monthly trend report for 2023:")
    print_table(get_monthly_trend("2023"), "Monthly Trend")

# ———————————————————————————————
# 4. Test vis.py (visualization)
# ———————————————————————————————
def test_visualization() -> None:
    print("\n=== Visualization Test ===")

    print("13. Plotting monthly summary for 2023-01")
    plot_monthly_summary("2023-01")

    print("14. Plotting category spending for 2023-01")
    plot_category_spending("2023-01")

    print("15. Plotting budget status for 2023-01")
    plot_budget_status("2023-01")

    print("16. Plotting monthly trend for 2023")
    plot_monthly_trend("2023")

# ———————————————————————————————
# Main Entry Point
# ———————————————————————————————
if __name__ == "__main__":
    reset_test_environment()
    test_database_operations()
    test_budget_module()
    test_report_module()
    test_visualization()
    print("\n🎉 All modules tested successfully!")