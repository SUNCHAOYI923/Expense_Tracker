import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from core.reports import (
    generate_monthly_report,
    generate_category_report,
    generate_budget_report,
    get_monthly_trend
)

def plot_monthly_summary(month: str) -> None:
    """
    Bar chart showing income vs expense for a given month.
    """
    report = generate_monthly_report(month)
    data = {"Income": report["income"], "Expense": abs(report["expense"])}
    plt.figure(figsize=(6, 4))
    sns.barplot(x=list(data.keys()), y=list(data.values()), palette="viridis")
    plt.ylabel("Amount (USD)")
    plt.title(f"Monthly Summary - {month}")
    plt.tight_layout()
    plt.show()

def plot_category_spending(month: str) -> None:
    """
    Pie chart showing spending distribution by category.
    """
    df = generate_category_report(month)
    expense_df = df[df["expense"] < 0]
    if expense_df.empty:
        print("No expense data to plot.")
        return
    plt.figure(figsize=(7, 7))
    plt.pie(
        -expense_df["expense"], labels=expense_df["category"], autopct="%1.1f%%", startangle=140
    )
    plt.title(f"Spending Distribution - {month}")
    plt.axis("equal")
    plt.tight_layout()
    plt.show()

def plot_budget_status(month: str) -> None:
    """
    Horizontal bar chart comparing budget vs actual spending.
    """
    df = generate_budget_report(month)
    if df.empty:
        print("No budget data to plot.")
        return
    df["spent"] = -df["spent"]
    df = df.sort_values(by="spent", ascending=False)
    plt.figure(figsize=(8, 5))
    sns.barplot(x="spent", y="category", data=df, color="salmon", label="Spent")
    sns.barplot(x="limit", y="category", data=df, color="lightgreen", alpha=0.6, label="Budget")
    plt.xlabel("Amount (USD)")
    plt.ylabel("Category")
    plt.title(f"Budget vs Spending - {month}")
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_monthly_trend(year: str) -> None:
    """
    Line chart showing income, expense, and net over the months in the year.
    """
    df = get_monthly_trend(year)
    if df.empty:
        print("No trend data to plot.")
        return
    plt.figure(figsize=(10, 5))
    sns.lineplot(x="month", y="income", data=df, label="Income", marker="o")
    sns.lineplot(x="month", y="expense", data=df, label="Expense", marker="o")
    sns.lineplot(x="month", y="net", data=df, label="Net", marker="o")
    plt.xticks(rotation=45)
    plt.ylabel("Amount (USD)")
    plt.title(f"Monthly Financial Trend - {year}")
    plt.tight_layout()
    plt.legend()
    plt.show()