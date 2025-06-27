import sys
from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFormLayout, QHBoxLayout,
    QVBoxLayout, QLabel, QLineEdit, QComboBox, QDateEdit,
    QDoubleSpinBox, QPushButton, QTableView, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from database import ExpenseDatabase
from core.tracker import add_expense, add_income, get_transactions, remove_transaction
from core.budget import set_category_budget, list_budgets, remove_category_budget
from core.reports import (
    generate_monthly_report, generate_category_report,
    generate_budget_report, get_monthly_trend
)

sns.set_style("whitegrid")
DB = ExpenseDatabase()

class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(parent)
        self._df = df.reset_index(drop=True)

    def update(self, df):
        self.beginResetModel()
        self._df = df.reset_index(drop=True)
        self.endResetModel()

    def rowCount(self, parent=None):
        return len(self._df)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._df.iat[index.row(), index.column()])

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._df.columns[section]
            else:
                return str(section)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Expense Tracker")
        self.resize(900, 600)

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self._make_transactions_tab(), "Transactions")
        tabs.addTab(self._make_budgets_tab(), "Budgets")
        tabs.addTab(self._make_reports_tab(), "Reports")
        tabs.addTab(self._make_visual_tab(), "Visualization")
        self.setCentralWidget(tabs)

        # initial population
        self._update_months()
        self._update_categories()

    def _show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)

    def _update_months(self):
        df = get_transactions()
        months = sorted(pd.to_datetime(df["date"]).dt.to_period("M").astype(str).unique().tolist())
        if hasattr(self, "rmonth_cb"):
            self.rmonth_cb.clear()
            self.rmonth_cb.addItems(months)
        if hasattr(self, "vmonth_cb"):
            self.vmonth_cb.clear()
            self.vmonth_cb.addItems(months)

    def _update_categories(self):
        tx_cats = set(get_transactions()["category"].dropna().unique())
        bg_df = list_budgets()
        bg_cats = set(bg_df["category"].dropna().unique()) if not bg_df.empty else set()
        all_cats = sorted(tx_cats | bg_cats)
        if hasattr(self, "cat_cb"):
            self.cat_cb.clear()
            self.cat_cb.addItems(all_cats)

    # ---- Transactions Tab ----
    def _make_transactions_tab(self):
        w = QWidget()
        layout = QVBoxLayout()
        form = QFormLayout()

        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.amt_spin = QDoubleSpinBox()
        self.amt_spin.setMaximum(1e6)
        self.typ_cb = QComboBox()
        self.typ_cb.addItems(["expense", "income"])
        self.cat_cb = QComboBox()
        self.cat_cb.setEditable(True)
        self.desc_cb = QComboBox()
        self.desc_cb.setEditable(True)

        btn_add = QPushButton("Add Transaction")
        btn_add.clicked.connect(self._add_transaction)

        form.addRow("Date", self.date_edit)
        form.addRow("Amount", self.amt_spin)
        form.addRow("Type", self.typ_cb)
        form.addRow("Category", self.cat_cb)
        form.addRow("Description", self.desc_cb)
        form.addRow("", btn_add)

        self.tr_model = PandasModel()
        self.tr_table = QTableView()
        self.tr_table.setModel(self.tr_model)
        btn_del = QPushButton("Delete Selected")
        btn_del.clicked.connect(self._delete_transaction)

        layout.addLayout(form)
        layout.addWidget(self.tr_table)
        layout.addWidget(btn_del)
        w.setLayout(layout)

        self._refresh_transactions()
        return w

    def _add_transaction(self):
        try:
            d = self.date_edit.date()
            if d > QDate.currentDate():
                raise ValueError("Date cannot be in the future.")
            category = self.cat_cb.currentText().strip()
            if not category:
                raise ValueError("Category cannot be empty.")
            amount = self.amt_spin.value()
            if amount == 0:
                raise ValueError("Amount must not be zero.")
            typ = self.typ_cb.currentText()
            val = -abs(amount) if typ == "expense" else abs(amount)
            data = {
                "date": d.toString("yyyy-MM-dd"),
                "amount": val,
                "category": category,
                "description": self.desc_cb.currentText().strip()
            }
            if typ == "expense":
                add_expense(**data)
            else:
                add_income(**data)

            QMessageBox.information(self, "Success", f"{typ.capitalize()} recorded.")
            self.amt_spin.setValue(0)
            self.desc_cb.setCurrentText("")
            self._refresh_transactions()
            self._update_categories()
            self._update_months()
        except Exception as e:
            self._show_error(str(e))

    def _refresh_transactions(self):
        df = get_transactions()
        self.tr_model.update(df)

    def _delete_transaction(self):
        try:
            row = self.tr_table.currentIndex().row()
            if row < 0:
                return
            tx_id = int(self.tr_model._df.iloc[row]["id"])
            ok = remove_transaction(tx_id)
            QMessageBox.information(self, "Deleted", f"Deleted={ok}")
            self._refresh_transactions()
            self._update_categories()
            self._update_months()
        except Exception as e:
            self._show_error(str(e))

    # ---- Budgets Tab ----
    def _make_budgets_tab(self):
        w = QWidget()
        layout = QVBoxLayout()
        top = QHBoxLayout()

        self.bcat_edit = QLineEdit()
        self.blim_spin = QDoubleSpinBox()
        self.blim_spin.setMaximum(1e6)

        btn_set = QPushButton("Set Budget")
        btn_set.clicked.connect(self._set_budget)
        btn_delete = QPushButton("Delete Selected Budget")
        btn_delete.clicked.connect(self._delete_selected_budget)

        top.addWidget(QLabel("Category"))
        top.addWidget(self.bcat_edit)
        top.addWidget(QLabel("Limit"))
        top.addWidget(self.blim_spin)
        top.addWidget(btn_set)

        self.b_model = PandasModel()
        self.b_table = QTableView()
        self.b_table.setModel(self.b_model)

        layout.addLayout(top)
        layout.addWidget(self.b_table)
        layout.addWidget(btn_delete)
        w.setLayout(layout)

        self._refresh_budgets()
        return w

    def _set_budget(self):
        try:
            cat = self.bcat_edit.text().strip()
            lim = self.blim_spin.value()
            if not cat:
                raise ValueError("Budget category cannot be empty.")
            if lim <= 0:
                raise ValueError("Limit must be positive.")
            set_category_budget(cat, lim)
            QMessageBox.information(self, "Success", "Budget set.")
            self.bcat_edit.clear()
            self.blim_spin.setValue(0)
            self._refresh_budgets()
            self._update_categories()
        except Exception as e:
            self._show_error(str(e))

    def _delete_selected_budget(self):
        try:
            row = self.b_table.currentIndex().row()
            if row < 0:
                return
            cat = self.b_model._df.iloc[row]["category"]
            ok = remove_category_budget(cat)
            QMessageBox.information(self, "Removed", f"Removed={ok}")
            self._refresh_budgets()
            self._update_categories()
        except Exception as e:
            self._show_error(str(e))

    def _refresh_budgets(self):
        df = list_budgets()
        self.b_model.update(df)

    # ---- Reports Tab ----
    def _make_reports_tab(self):
        w = QWidget()
        layout = QVBoxLayout()
        ctrl = QHBoxLayout()

        self.rmonth_cb = QComboBox()
        self.rmonth_cb.addItems(self._months())
        btn1 = QPushButton("Monthly")
        btn1.clicked.connect(self._show_monthly_report)
        btn2 = QPushButton("By Category")
        btn2.clicked.connect(self._show_category_report)
        btn3 = QPushButton("Budget")
        btn3.clicked.connect(self._show_budget_report)

        ctrl.addWidget(QLabel("Month"))
        ctrl.addWidget(self.rmonth_cb)
        ctrl.addWidget(btn1)
        ctrl.addWidget(btn2)
        ctrl.addWidget(btn3)

        self.r_model = PandasModel()
        self.r_table = QTableView()
        self.r_table.setModel(self.r_model)

        layout.addLayout(ctrl)
        layout.addWidget(self.r_table)
        w.setLayout(layout)
        return w

    def _months(self):
        df = get_transactions()
        return sorted(pd.to_datetime(df["date"]).dt.to_period("M").astype(str).unique())

    def _show_monthly_report(self):
        try:
            rep = generate_monthly_report(self.rmonth_cb.currentText())
            self.r_model.update(pd.DataFrame([rep]))
        except Exception as e:
            self._show_error(str(e))

    def _show_category_report(self):
        try:
            df = generate_category_report(self.rmonth_cb.currentText())
            self.r_model.update(df)
        except Exception as e:
            self._show_error(str(e))

    def _show_budget_report(self):
        try:
            df = generate_budget_report(self.rmonth_cb.currentText())
            self.r_model.update(df)
        except Exception as e:
            self._show_error(str(e))

    # ---- Visualization Tab ----
    def _make_visual_tab(self):
        w = QWidget()
        layout = QVBoxLayout()
        ctrl = QHBoxLayout()

        self.vmonth_cb = QComboBox()
        self.vmonth_cb.addItems(self._months())
        btn1 = QPushButton("Summary")
        btn1.clicked.connect(self._plot_summary)
        btn2 = QPushButton("Category")
        btn2.clicked.connect(self._plot_category)
        btn3 = QPushButton("Budget")
        btn3.clicked.connect(self._plot_budget)
        btn4 = QPushButton("Trend")
        btn4.clicked.connect(self._plot_trend)

        ctrl.addWidget(QLabel("Month"))
        ctrl.addWidget(self.vmonth_cb)
        ctrl.addWidget(btn1)
        ctrl.addWidget(btn2)
        ctrl.addWidget(btn3)
        ctrl.addWidget(btn4)

        self.canvas = FigureCanvas(plt.figure(figsize=(6, 4)))
        layout.addLayout(ctrl)
        layout.addWidget(self.canvas)
        w.setLayout(layout)
        return w

    def _plot_summary(self):
        try:
            month = self.vmonth_cb.currentText()
            rep = generate_monthly_report(month)
            fig = self.canvas.figure; fig.clear()
            ax = fig.add_subplot(111)
            sns.barplot(x=["Income", "Expense"],
                        y=[rep["income"], abs(rep["expense"])],
                        palette=["#4caf50", "#f44336"], ax=ax)
            ax.set_title(f"Summary {month}")
            self.canvas.draw()
        except Exception as e:
            self._show_error(str(e))

    def _plot_category(self):
        try:
            month = self.vmonth_cb.currentText()
            df = generate_category_report(month)
            df = df[df["expense"] < 0]
            fig = self.canvas.figure; fig.clear()
            ax = fig.add_subplot(111)
            if df.empty:
                raise ValueError("No expenses to plot.")
            ax.pie(-df["expense"], labels=df["category"], autopct="%1.1f%%")
            ax.set_title(f"Category {month}")
            self.canvas.draw()
        except Exception as e:
            self._show_error(str(e))

    def _plot_budget(self):
        try:
            month = self.vmonth_cb.currentText()
            df = generate_budget_report(month)
            fig = self.canvas.figure; fig.clear()
            ax = fig.add_subplot(111)
            if df.empty:
                raise ValueError("No budget data.")
            df = df.sort_values("remaining")
            sns.barplot(x="remaining", y="category", data=df, palette="Blues_d", ax=ax)
            ax.set_title(f"Remaining {month}")
            self.canvas.draw()
        except Exception as e:
            self._show_error(str(e))

    def _plot_trend(self):
        try:
            year = self.vmonth_cb.currentText()[:4]
            df = get_monthly_trend(year)
            fig = self.canvas.figure; fig.clear()
            ax = fig.add_subplot(111)
            if df.empty:
                raise ValueError("No trend data.")
            df_m = df.melt(id_vars=["month"],
                           value_vars=["income", "expense", "net"],
                           var_name="variable",
                           value_name="value")
            sns.lineplot(data=df_m, x="month", y="value", hue="variable",
                         marker="o", ax=ax)
            ax.set_title(f"Trend {year}")
            ax.tick_params(axis="x", rotation=45)
            self.canvas.draw()
        except Exception as e:
            self._show_error(str(e))


if __name__ == "__main__":
    Path("data").mkdir(exist_ok=True)
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())