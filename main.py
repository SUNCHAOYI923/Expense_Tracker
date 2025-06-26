import sys
import pandas as pd
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QTableView,
    QTabWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from database import ExpenseDatabase
from core.tracker import add_expense, add_income, get_transactions
from core.budget import (
    set_category_budget, list_budgets, remove_category_budget
)
from core.reports import (
    generate_monthly_report, generate_category_report,
    generate_budget_report, get_monthly_trend
)
from vis import (
    plot_monthly_summary, plot_category_spending,
    plot_budget_status, plot_monthly_trend
)

DB = ExpenseDatabase()

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(fig)
        fig.tight_layout()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Expense Tracker")
        self.resize(1000, 600)
        tabs = QTabWidget()
        tabs.addTab(self.make_tracker_tab(), "Transactions")
        tabs.addTab(self.make_budget_tab(), "Budgets")
        tabs.addTab(self.make_reports_tab(), "Reports")
        tabs.addTab(self.make_visual_tab(), "Visualization")
        self.setCentralWidget(tabs)

    # --- Transactions Tab ---
    def make_tracker_tab(self):
        widget = QWidget()
        v = QVBoxLayout()

        # Input form
        form = QHBoxLayout()
        self.date_in = QLineEdit(); self.date_in.setPlaceholderText("YYYY-MM-DD")
        self.amount_in = QLineEdit(); self.amount_in.setPlaceholderText("Amount")
        self.cat_in = QLineEdit(); self.cat_in.setPlaceholderText("Category")
        self.desc_in = QLineEdit(); self.desc_in.setPlaceholderText("Description")
        self.type_cb = QComboBox(); self.type_cb.addItems(["expense","income"])
        btn_add = QPushButton("Add")
        btn_add.clicked.connect(self.on_add_transaction)
        form.addWidget(QLabel("Date")); form.addWidget(self.date_in)
        form.addWidget(QLabel("Amount")); form.addWidget(self.amount_in)
        form.addWidget(QLabel("Category")); form.addWidget(self.cat_in)
        form.addWidget(QLabel("Desc")); form.addWidget(self.desc_in)
        form.addWidget(QLabel("Type")); form.addWidget(self.type_cb)
        form.addWidget(btn_add)

        # Table view
        self.tr_table = QTableView()
        v.addLayout(form)
        v.addWidget(self.tr_table)
        widget.setLayout(v)
        self.refresh_transactions()
        return widget

    def on_add_transaction(self):
        date = self.date_in.text()
        amt  = float(self.amount_in.text())
        cat  = self.cat_in.text()
        desc = self.desc_in.text()
        typ  = self.type_cb.currentText()
        if typ=="expense":
            add_expense(date, amt, cat, desc)
        else:
            add_income(date, amt, cat, desc)
        QMessageBox.information(self, "Success", f"{typ.capitalize()} added")
        self.refresh_transactions()

    def refresh_transactions(self):
        df = get_transactions()
        model = PandasModel(df)
        self.tr_table.setModel(model)

    # --- Budgets Tab ---
    def make_budget_tab(self):
        widget = QWidget()
        v = QVBoxLayout()
        h = QHBoxLayout()
        self.bcat_in = QLineEdit(); self.bcat_in.setPlaceholderText("Category")
        self.blim_in = QLineEdit(); self.blim_in.setPlaceholderText("Limit")
        btn_set = QPushButton("Set")
        btn_set.clicked.connect(self.on_set_budget)
        btn_remove = QPushButton("Remove")
        btn_remove.clicked.connect(self.on_remove_budget)
        h.addWidget(QLabel("Category")); h.addWidget(self.bcat_in)
        h.addWidget(QLabel("Limit"));    h.addWidget(self.blim_in)
        h.addWidget(btn_set); h.addWidget(btn_remove)
        self.bgt_table = QTableView()
        v.addLayout(h); v.addWidget(self.bgt_table)
        widget.setLayout(v)
        self.refresh_budgets()
        return widget

    def on_set_budget(self):
        cat = self.bcat_in.text()
        lim = float(self.blim_in.text())
        set_category_budget(cat, lim)
        QMessageBox.information(self, "Success", "Budget set")
        self.refresh_budgets()

    def on_remove_budget(self):
        cat = self.bcat_in.text()
        ok = remove_category_budget(cat)
        QMessageBox.information(self, "Removed" if ok else "Failed", f"Removed={ok}")
        self.refresh_budgets()

    def refresh_budgets(self):
        df = list_budgets()
        self.bgt_table.setModel(PandasModel(df))

    # --- Reports Tab ---
    def make_reports_tab(self):
        widget = QWidget()
        v = QVBoxLayout()
        # Month selector
        self.rmonth_cb = QComboBox()
        self.rmonth_cb.addItems(self.available_months())
        btn_month = QPushButton("Monthly")
        btn_month.clicked.connect(self.on_monthly_report)
        btn_cat = QPushButton("By Category")
        btn_cat.clicked.connect(self.on_category_report)
        btn_bud = QPushButton("Budget Report")
        btn_bud.clicked.connect(self.on_budget_report)
        self.r_table = QTableView()
        h = QHBoxLayout()
        h.addWidget(QLabel("Month")); h.addWidget(self.rmonth_cb)
        h.addWidget(btn_month); h.addWidget(btn_cat); h.addWidget(btn_bud)
        v.addLayout(h); v.addWidget(self.r_table)
        widget.setLayout(v)
        return widget

    def available_months(self):
        df = get_transactions()
        months = pd.to_datetime(df["date"]).dt.to_period("M").astype(str).unique()
        return sorted(months.tolist())

    def on_monthly_report(self):
        m = self.rmonth_cb.currentText()
        rep = generate_monthly_report(m)
        df = pd.DataFrame([rep])
        self.r_table.setModel(PandasModel(df))

    def on_category_report(self):
        m = self.rmonth_cb.currentText()
        df = generate_category_report(m)
        self.r_table.setModel(PandasModel(df))

    def on_budget_report(self):
        m = self.rmonth_cb.currentText()
        df = generate_budget_report(m)
        self.r_table.setModel(PandasModel(df))

    # --- Visualization Tab ---
    def make_visual_tab(self):
        widget = QWidget()
        v = QVBoxLayout()
        # Controls
        h = QHBoxLayout()
        self.vmonth_cb = QComboBox(); self.vmonth_cb.addItems(self.available_months())
        btn1 = QPushButton("Summary Chart"); btn1.clicked.connect(self.on_plot_summary)
        btn2 = QPushButton("Category Pie");    btn2.clicked.connect(self.on_plot_category)
        btn3 = QPushButton("Budget Status");   btn3.clicked.connect(self.on_plot_budget)
        btn4 = QPushButton("Year Trend");      btn4.clicked.connect(self.on_plot_trend)
        h.addWidget(QLabel("Month:")); h.addWidget(self.vmonth_cb)
        h.addWidget(btn1); h.addWidget(btn2); h.addWidget(btn3); h.addWidget(btn4)
        v.addLayout(h)
        # Canvas
        self.canvas = MplCanvas(self, width=6, height=4, dpi=100)
        v.addWidget(self.canvas)
        widget.setLayout(v)
        return widget

    def on_plot_summary(self):
        month = self.vmonth_cb.currentText()
        rep = generate_monthly_report(month)
        data = {"Income": rep["income"], "Expense": abs(rep["expense"])}
        self.canvas.ax.clear()
        self.canvas.ax.bar(data.keys(), data.values(), color=["green","red"])
        self.canvas.ax.set_title(f"Monthly Summary {month}")
        self.canvas.draw()

    def on_plot_category(self):
        month = self.vmonth_cb.currentText()
        df = generate_category_report(month)
        df = df[df["expense"]<0]
        self.canvas.ax.clear()
        self.canvas.ax.pie(-df["expense"], labels=df["category"], autopct="%1.1f%%")
        self.canvas.ax.set_title(f"Spending Distribution {month}")
        self.canvas.draw()

    def on_plot_budget(self):
        month = self.vmonth_cb.currentText()
        df = generate_budget_report(month)
        df = df.sort_values("remaining")
        self.canvas.ax.clear()
        self.canvas.ax.barh(df["category"], df["remaining"], color="blue")
        self.canvas.ax.set_title(f"Budget Remaining {month}")
        self.canvas.draw()

    def on_plot_trend(self):
        year = self.vmonth_cb.currentText()[:4]
        df = get_monthly_trend(year)
        self.canvas.ax.clear()
        self.canvas.ax.plot(df["month"], df["income"], label="Income")
        self.canvas.ax.plot(df["month"], df["expense"], label="Expense")
        self.canvas.ax.plot(df["month"], df["net"], label="Net")
        self.canvas.ax.legend()
        self.canvas.ax.set_title(f"Yearly Trend {year}")
        self.canvas.draw()

class PandasModel(QtCore.QAbstractTableModel):
    """A Qt model to interface a pandas DataFrame"""
    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(parent)
        self._df = df

    def rowCount(self, parent=None):
        return len(self._df.index)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            return str(self._df.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._df.columns[section]
            else:
                return str(self._df.index[section])
        return None

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())