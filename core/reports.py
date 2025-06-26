# core/reports.py

import pandas as pd
from typing import Dict, Any
from database import ExpenseDatabase
from core.budget import get_category_budget

db = ExpenseDatabase()

def generate_monthly_report(month: str) -> Dict[str, float]:
    """
    Generate a report for a given month with total income, expense, and net.
    Month format: "YYYY-MM"
    """
    start_date = f"{month}-01"
    end_date = f"{month}-31"

    df = db.get_transactions(start_date=start_date, end_date=end_date)

    income = df[df["type"] == "income"]["amount"].sum()
    expense = df[df["type"] == "expense"]["amount"].sum()
    net = income + expense  # expense is negative

    return {"income": income, "expense": expense, "net": net}


def generate_category_report(month: str) -> pd.DataFrame:
    """
    Generate a category-wise report for a given month.
    Returns DataFrame with columns: category, income, expense, net
    """
    start_date = f"{month}-01"
    end_date = f"{month}-31"

    df = db.get_transactions(start_date=start_date, end_date=end_date)

    def pivot_and_format(category_type: str) -> pd.DataFrame:
        sub_df = df[df["type"] == category_type]
        return sub_df.groupby("category")["amount"].sum().reset_index().rename(
            columns={"amount": category_type}
        )

    income_df = pivot_and_format("income")
    expense_df = pivot_and_format("expense")

    merged = pd.merge(income_df, expense_df, on="category", how="outer").fillna(0)
    merged["net"] = merged["income"] + merged["expense"]

    return merged[["category", "income", "expense", "net"]]


def generate_budget_report(month: str) -> pd.DataFrame:
    """
    Generate a budget vs actual spending report.
    Returns DataFrame with columns: category, limit, spent, remaining
    """
    budget_df = db.get_budgets()
    if budget_df.empty:
        return pd.DataFrame(columns=["category", "limit", "spent", "remaining"])

    # Get spending for the month
    start_date = f"{month}-01"
    end_date = f"{month}-31"
    trans_df = db.get_transactions(start_date=start_date, end_date=end_date)
    spending = trans_df[trans_df["type"] == "expense"].groupby("category")["amount"].sum()
    spending.name = "spent"

    # Merge with budgets and fill missing spending as 0
    report = budget_df.set_index("category").join(spending).fillna(0)
    report["remaining"] = report["monthly_limit"] + report["spent"]  # expense is negative

    report = report.reset_index()
    report = report.rename(columns={"monthly_limit": "limit"})
    return report[["category", "limit", "spent", "remaining"]]


def get_monthly_trend(year: str) -> pd.DataFrame:
    """
    Get monthly income, expense, and net for a given year.
    Returns DataFrame with columns: month, income, expense, net
    """
    df = db.get_transactions()
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)

    trend = df.pivot_table(
        index="month",
        columns="type",
        values="amount",
        aggfunc="sum"
    ).fillna(0)

    trend["net"] = trend["income"] + trend["expense"]
    trend = trend.reset_index()
    trend = trend[trend["month"].str.startswith(year)]
    return trend[["month", "income", "expense", "net"]]