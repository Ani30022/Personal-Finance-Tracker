import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import math
from datetime import datetime

# ─── Database Setup ──────────────────────────────────────────────
DB_FILE = "finance.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            type      TEXT NOT NULL,
            category  TEXT NOT NULL,
            amount    REAL NOT NULL,
            note      TEXT,
            date      TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            category TEXT PRIMARY KEY,
            limit_amount REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect(DB_FILE)

# ─── Constants ───────────────────────────────────────────────────
INCOME_CATEGORIES  = ["Salary", "Freelance", "Investment", "Gift", "Other Income"]
EXPENSE_CATEGORIES = ["Food", "Rent", "Transport", "Shopping", "Health",
                      "Entertainment", "Utilities", "Education", "Other Expense"]

COLORS = {
    "bg":       "#1e1e2e",
    "panel":    "#313244",
    "accent1":  "#89b4fa",
    "accent2":  "#a6e3a1",
    "red":      "#f38ba8",
    "text":     "#cdd6f4",
    "subtext":  "#a6adc8",
    "input_bg": "#45475a",
}

CHART_COLORS = ["#89b4fa","#a6e3a1","#f38ba8","#fab387","#f9e2af",
                "#cba6f7","#94e2d5","#eba0ac","#89dceb"]

# ─── Main App ────────────────────────────────────────────────────
class FinanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        init_db()
        self.title("💰 Personal Finance Tracker")
        self.geometry("950x650")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])
        self._build_ui()
        self.refresh_all()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=COLORS["panel"], pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="💰  Personal Finance Tracker",
                 font=("Segoe UI", 18, "bold"), bg=COLORS["panel"], fg=COLORS["text"]).pack()
        tk.Label(hdr, text="Track income, expenses and stay on budget",
                 font=("Segoe UI", 10), bg=COLORS["panel"], fg=COLORS["subtext"]).pack()

        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=16, pady=12)

        self._build_form(body)
        self._build_chart(body)
        self._build_table()
        self._build_summary()

    def _build_form(self, parent):
        frame = tk.Frame(parent, bg=COLORS["panel"], padx=16, pady=16)
        frame.pack(side="left", fill="y", padx=(0, 12))

        tk.Label(frame, text="Add Transaction", font=("Segoe UI", 12, "bold"),
                 bg=COLORS["panel"], fg=COLORS["text"]).grid(row=0, column=0, columnspan=2, pady=(0,10))

        lbl_style   = {"bg": COLORS["panel"], "fg": COLORS["subtext"], "font": ("Segoe UI", 9)}
        input_style = {"bg": COLORS["input_bg"], "fg": COLORS["text"], "font": ("Segoe UI", 10),
                       "relief": "flat", "insertbackground": "white"}

        tk.Label(frame, text="Type", **lbl_style).grid(row=1, column=0, sticky="w", pady=4)
        self.type_var = tk.StringVar(value="Expense")
        type_menu = ttk.Combobox(frame, textvariable=self.type_var, values=["Income", "Expense"],
                                 state="readonly", width=18, font=("Segoe UI", 10))
        type_menu.grid(row=1, column=1, pady=4)
        type_menu.bind("<<ComboboxSelected>>", self.update_categories)

        tk.Label(frame, text="Category", **lbl_style).grid(row=2, column=0, sticky="w", pady=4)
        self.cat_var = tk.StringVar(value=EXPENSE_CATEGORIES[0])
        self.cat_menu = ttk.Combobox(frame, textvariable=self.cat_var,
                                     values=EXPENSE_CATEGORIES, state="readonly",
                                     width=18, font=("Segoe UI", 10))
        self.cat_menu.grid(row=2, column=1, pady=4)

        tk.Label(frame, text="Amount (₹)", **lbl_style).grid(row=3, column=0, sticky="w", pady=4)
        self.amount_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.amount_var, width=20, **input_style).grid(row=3, column=1, pady=4)

        tk.Label(frame, text="Note", **lbl_style).grid(row=4, column=0, sticky="w", pady=4)
        self.note_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.note_var, width=20, **input_style).grid(row=4, column=1, pady=4)

        tk.Label(frame, text="Date (YYYY-MM-DD)", **lbl_style).grid(row=5, column=0, sticky="w", pady=4)
        self.date_var = tk.StringVar(value=datetime.today().strftime("%Y-%m-%d"))
        tk.Entry(frame, textvariable=self.date_var, width=20, **input_style).grid(row=5, column=1, pady=4)

        btn_frame = tk.Frame(frame, bg=COLORS["panel"])
        btn_frame.grid(row=6, column=0, columnspan=2, pady=14)
        tk.Button(btn_frame, text="➕ Add", command=self.add_transaction,
                  bg=COLORS["accent2"], fg="#1e1e2e", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=14, pady=6, cursor="hand2").pack(side="left", padx=4)
        tk.Button(btn_frame, text="🗑️ Delete", command=self.delete_selected,
                  bg=COLORS["red"], fg="#1e1e2e", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=14, pady=6, cursor="hand2").pack(side="left", padx=4)

        tk.Label(frame, text="─────────────────", bg=COLORS["panel"], fg=COLORS["input_bg"]).grid(
            row=7, column=0, columnspan=2)
        tk.Label(frame, text="Set Budget Limit", font=("Segoe UI", 11, "bold"),
                 bg=COLORS["panel"], fg=COLORS["text"]).grid(row=8, column=0, columnspan=2, pady=6)

        tk.Label(frame, text="Category", **lbl_style).grid(row=9, column=0, sticky="w", pady=4)
        self.budget_cat_var = tk.StringVar(value=EXPENSE_CATEGORIES[0])
        ttk.Combobox(frame, textvariable=self.budget_cat_var, values=EXPENSE_CATEGORIES,
                     state="readonly", width=18, font=("Segoe UI", 10)).grid(row=9, column=1, pady=4)

        tk.Label(frame, text="Limit (₹)", **lbl_style).grid(row=10, column=0, sticky="w", pady=4)
        self.budget_limit_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.budget_limit_var, width=20, **input_style).grid(row=10, column=1, pady=4)

        tk.Button(frame, text="💾 Save Budget", command=self.save_budget,
                  bg=COLORS["accent1"], fg="#1e1e2e", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=12, pady=5, cursor="hand2").grid(row=11, column=0, columnspan=2, pady=8)

    def _build_chart(self, parent):
        frame = tk.Frame(parent, bg=COLORS["panel"], padx=10, pady=10)
        frame.pack(side="right", fill="both", expand=True)
        tk.Label(frame, text="Expense Breakdown", font=("Segoe UI", 11, "bold"),
                 bg=COLORS["panel"], fg=COLORS["text"]).pack()
        self.chart_frame = frame

    def refresh_chart(self):
        # Clear previous chart widgets
        for widget in self.chart_frame.winfo_children()[1:]:
            widget.destroy()

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT category, SUM(amount) FROM transactions WHERE type='Expense' GROUP BY category")
        rows = c.fetchall()
        conn.close()

        if not rows:
            tk.Label(self.chart_frame, text="No expense data yet",
                     bg=COLORS["panel"], fg=COLORS["subtext"], font=("Segoe UI", 10)).pack(expand=True)
            return

        canvas = tk.Canvas(self.chart_frame, width=380, height=300,
                           bg=COLORS["panel"], highlightthickness=0)
        canvas.pack(pady=4)

        total = sum(r[1] for r in rows)
        cx, cy, r = 130, 150, 110
        start_angle = 90  # start from top

        for i, (cat, amt) in enumerate(rows):
            extent = (amt / total) * 360
            # tkinter uses degrees, starting from 3 o'clock, going counter-clockwise
            canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                              start=start_angle, extent=-extent,
                              fill=CHART_COLORS[i % len(CHART_COLORS)],
                              outline=COLORS["bg"], width=2)
            # Legend on the right
            lx, ly = 265, 30 + i * 26
            canvas.create_rectangle(lx, ly, lx + 12, ly + 12,
                                    fill=CHART_COLORS[i % len(CHART_COLORS)], outline="")
            pct = (amt / total) * 100
            canvas.create_text(lx + 16, ly + 6,
                               text=f"{cat}  {pct:.0f}%",
                               fill=COLORS["text"], font=("Segoe UI", 8), anchor="w")
            start_angle -= extent

    def _build_table(self):
        frame = tk.Frame(self, bg=COLORS["bg"], padx=16)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="Recent Transactions", font=("Segoe UI", 11, "bold"),
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")

        cols = ("ID", "Date", "Type", "Category", "Amount (₹)", "Note")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=7)
        widths = [40, 100, 80, 120, 100, 200]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center" if col != "Note" else "w")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=COLORS["panel"], foreground=COLORS["text"],
                        fieldbackground=COLORS["panel"], rowheight=24)
        style.configure("Treeview.Heading", background=COLORS["input_bg"], foreground=COLORS["text"])
        self.tree.tag_configure("income",  foreground="#a6e3a1")
        self.tree.tag_configure("expense", foreground="#f38ba8")

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def _build_summary(self):
        frame = tk.Frame(self, bg=COLORS["panel"], pady=10)
        frame.pack(fill="x", padx=16, pady=8)
        self.lbl_income  = tk.Label(frame, text="Income: ₹0",   font=("Segoe UI", 11, "bold"),
                                    bg=COLORS["panel"], fg=COLORS["accent2"])
        self.lbl_expense = tk.Label(frame, text="Expenses: ₹0", font=("Segoe UI", 11, "bold"),
                                    bg=COLORS["panel"], fg=COLORS["red"])
        self.lbl_balance = tk.Label(frame, text="Balance: ₹0",  font=("Segoe UI", 11, "bold"),
                                    bg=COLORS["panel"], fg=COLORS["accent1"])
        self.lbl_alert   = tk.Label(frame, text="",             font=("Segoe UI", 10, "bold"),
                                    bg=COLORS["panel"], fg="#fab387")
        self.lbl_income.pack(side="left",  padx=24)
        self.lbl_expense.pack(side="left", padx=24)
        self.lbl_balance.pack(side="left", padx=24)
        self.lbl_alert.pack(side="right",  padx=16)

    def update_categories(self, event=None):
        if self.type_var.get() == "Income":
            self.cat_menu["values"] = INCOME_CATEGORIES
            self.cat_var.set(INCOME_CATEGORIES[0])
        else:
            self.cat_menu["values"] = EXPENSE_CATEGORIES
            self.cat_var.set(EXPENSE_CATEGORIES[0])

    def add_transaction(self):
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid", "Enter a valid positive amount.")
            return
        try:
            datetime.strptime(self.date_var.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid", "Date must be YYYY-MM-DD format.")
            return

        conn = get_conn()
        conn.execute("INSERT INTO transactions (type, category, amount, note, date) VALUES (?,?,?,?,?)",
                     (self.type_var.get(), self.cat_var.get(), float(self.amount_var.get()),
                      self.note_var.get(), self.date_var.get()))
        conn.commit()
        conn.close()
        self.amount_var.set("")
        self.note_var.set("")
        self.refresh_all()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a transaction to delete.")
            return
        if not messagebox.askyesno("Confirm", "Delete selected transaction?"):
            return
        tx_id = self.tree.item(selected[0])["values"][0]
        conn = get_conn()
        conn.execute("DELETE FROM transactions WHERE id=?", (tx_id,))
        conn.commit()
        conn.close()
        self.refresh_all()

    def save_budget(self):
        try:
            limit = float(self.budget_limit_var.get())
            if limit <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid", "Enter a valid budget limit.")
            return
        conn = get_conn()
        conn.execute("INSERT OR REPLACE INTO budgets (category, limit_amount) VALUES (?,?)",
                     (self.budget_cat_var.get(), limit))
        conn.commit()
        conn.close()
        messagebox.showinfo("Saved", f"Budget for {self.budget_cat_var.get()} set to ₹{limit:,.0f}")
        self.check_budgets()

    def check_budgets(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT category, limit_amount FROM budgets")
        budgets = c.fetchall()
        alerts = []
        for cat, limit in budgets:
            c.execute("SELECT SUM(amount) FROM transactions WHERE type='Expense' AND category=?", (cat,))
            spent = c.fetchone()[0] or 0
            if spent > limit:
                alerts.append(f"⚠️ {cat}: ₹{spent:,.0f} spent (limit ₹{limit:,.0f})")
        conn.close()
        self.lbl_alert.config(text="  |  ".join(alerts) if alerts else "✅ All within budget")

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, date, type, category, amount, note FROM transactions ORDER BY date DESC LIMIT 100")
        for row in c.fetchall():
            tag = "income" if row[2] == "Income" else "expense"
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3],
                                                f"₹{row[4]:,.2f}", row[5] or ""), tags=(tag,))
        conn.close()

    def refresh_summary(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT SUM(amount) FROM transactions WHERE type='Income'")
        income = c.fetchone()[0] or 0
        c.execute("SELECT SUM(amount) FROM transactions WHERE type='Expense'")
        expense = c.fetchone()[0] or 0
        conn.close()
        balance = income - expense
        self.lbl_income.config(text=f"Income: ₹{income:,.2f}")
        self.lbl_expense.config(text=f"Expenses: ₹{expense:,.2f}")
        self.lbl_balance.config(text=f"Balance: ₹{balance:,.2f}",
                                fg=COLORS["accent2"] if balance >= 0 else COLORS["red"])

    def refresh_all(self):
        self.refresh_table()
        self.refresh_summary()
        self.refresh_chart()
        self.check_budgets()

# ─── Run ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    FinanceApp().mainloop()