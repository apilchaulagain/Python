import csv
import statistics
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ── Palette ──────────────────────────────────────────────────
BG    = "#FAF7F2"
TERRA = "#C0533A"
SAGE  = "#7A9E87"
SAND  = "#E8DDD0"
DARK  = "#2B2B2B"
MUTED = "#8A8279"
LIGHT = "#F5EFE8"

all_rows  = []
col_types = {}   # col -> "int" | "float" | "text"

# ── Helpers ──────────────────────────────────────────────────

def detect_col_types(rows):
    types = {}
    for col in rows[0].keys():
        vals = [r[col] for r in rows if r[col].strip() != ""]
        int_ok = float_ok = True
        for v in vals:
            try:   int(v)
            except: int_ok = False
            try:   float(v)
            except: float_ok = False
        if int_ok:
            types[col] = "int"
        elif float_ok:
            types[col] = "float"
        else:
            types[col] = "text"
    return types


def _numeric(v):
    try:    return float(v)
    except: return None


def populate_table(rows):
    tree.delete(*tree.get_children())
    for i, row in enumerate(rows):
        tag = "odd" if i % 2 == 0 else "even"
        tree.insert("", "end", values=list(row.values()), tags=(tag,))
    status_var.set(f"  {len(rows)} of {len(all_rows)} records shown")


def apply_filters(*args):
    if not all_rows:
        return
    result = all_rows[:]
    kw = search_var.get().lower()
    if kw:
        result = [r for r in result if any(kw in str(v).lower() for v in r.values())]
    populate_table(result)


# ── Data load ─────────────────────────────────────────────────

def load_csv():
    global all_rows, col_types
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return
    try:
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            all_rows = list(reader)

        if not all_rows:
            messagebox.showwarning("Warning", "CSV file is empty.")
            return

        col_types = detect_col_types(all_rows)
        columns = list(all_rows[0].keys())
        tree["columns"] = columns
        tree["show"] = "headings"
        for col in columns:
            tree.heading(col, text=col, anchor="w")
            tree.column(col, width=130, anchor="w", minwidth=80)

        populate_table(all_rows)
        status_var.set(f"  Loaded {len(all_rows)} records  |  {len(columns)} columns")
        stats_bar_var.set("")

    except Exception as e:
        messagebox.showerror("Error", str(e))


def show_stats():
    if not all_rows:
        messagebox.showwarning("No Data", "Please load a CSV file first.")
        return
    possible = ["BaseSalary","Salary","salary","Base Pay","TotalPay",
                "base_salary","SALARY","Annual Salary","AnnualSalary",
                "Balance","Score"]
    salary_column = next((c for c in possible if c in all_rows[0]), None)
    if salary_column is None:
        numeric_cols = [c for c,t in col_types.items() if t in ("int","float")]
        if not numeric_cols:
            messagebox.showerror("Error", "No numeric columns found.")
            return
        salary_column = numeric_cols[0]
    try:
        vals = [float(r[salary_column]) for r in all_rows if r[salary_column].strip() != ""]
        stats_bar_var.set(
            f"  {salary_column}  —  "
            f"Mean: {statistics.mean(vals):,.2f}   |   "
            f"Median: {statistics.median(vals):,.2f}   |   "
            f"Std Dev: {statistics.stdev(vals):,.2f}   |   "
            f"Min: {min(vals):,.2f}   |   "
            f"Max: {max(vals):,.2f}   |   "
            f"Variance: {statistics.variance(vals):,.0f}"
        )
    except Exception as e:
        messagebox.showerror("Error", str(e))


# ── Window ────────────────────────────────────────────────────
root = tk.Tk()
root.title("Salary CSV Viewer")
root.geometry("1000x700")
root.configure(bg=BG)
root.resizable(True, True)

# Title bar
title_bar = tk.Frame(root, bg=TERRA, height=52)
title_bar.pack(fill="x")
title_bar.pack_propagate(False)
tk.Label(title_bar, text="Salary CSV Viewer", bg=TERRA, fg="white",
         font=("Georgia", 15, "bold"), padx=16).pack(side="left", pady=10)
tk.Label(title_bar, text="Python GUI Application", bg=TERRA, fg="#F5EFE8",
         font=("Calibri", 10, "italic"), padx=4).pack(side="left", pady=10)

# Toolbar
toolbar = tk.Frame(root, bg=SAND, pady=8)
toolbar.pack(fill="x")

def make_btn(parent, text, cmd, bg, fg):
    return tk.Button(parent, text=text, command=cmd,
                     bg=bg, fg=fg, font=("Calibri", 10, "bold"),
                     relief="flat", cursor="hand2", padx=14, pady=5,
                     activebackground=DARK, activeforeground="white")

make_btn(toolbar, "  Load CSV  ", load_csv, TERRA, "white").pack(side="left", padx=(12,6), pady=2)
make_btn(toolbar, "  Show Stats  ", show_stats, SAGE, "white").pack(side="left", padx=6, pady=2)
tk.Frame(toolbar, bg=MUTED, width=1).pack(side="left", fill="y", padx=10, pady=4)
tk.Label(toolbar, text="Search:", bg=SAND, fg=DARK, font=("Calibri", 10)).pack(side="left")

search_var = tk.StringVar()
search_var.trace_add("write", apply_filters)
search_entry = tk.Entry(toolbar, textvariable=search_var,
                        font=("Calibri", 10), bg="white", fg=DARK,
                        relief="flat", bd=0, highlightthickness=1,
                        highlightbackground=MUTED, highlightcolor=TERRA, width=28)
search_entry.pack(side="left", padx=(4,4), ipady=5)
make_btn(toolbar, "✕", lambda: search_var.set(""), SAND, MUTED).pack(side="left", padx=(0,6), pady=2)

# ── Full-width table area ──────────────────────────────────────
table_outer = tk.Frame(root, bg=SAND, padx=1, pady=1)
table_outer.pack(fill="both", expand=True, padx=8, pady=(10, 0))

table_frame = tk.Frame(table_outer, bg=BG)
table_frame.pack(fill="both", expand=True)

style = ttk.Style()
style.theme_use("clam")
style.configure("Custom.Treeview",
    background=BG, fieldbackground=BG, foreground=DARK,
    rowheight=30, font=("Calibri", 10), borderwidth=0)
style.configure("Custom.Treeview.Heading",
    background=DARK, foreground="white",
    font=("Calibri", 10, "bold"), relief="flat", padding=(8, 6))
style.map("Custom.Treeview",
    background=[("selected", TERRA)], foreground=[("selected", "white")])
style.map("Custom.Treeview.Heading",
    background=[("active", TERRA)])

scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
scroll_y.pack(side="right", fill="y")
scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
scroll_x.pack(side="bottom", fill="x")

tree = ttk.Treeview(table_frame, style="Custom.Treeview",
                    yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
                    selectmode="browse")
tree.pack(fill="both", expand=True)
scroll_y.config(command=tree.yview)
scroll_x.config(command=tree.xview)
tree.tag_configure("odd",  background=BG)
tree.tag_configure("even", background=LIGHT)

# Stats bar
stats_bar_var = tk.StringVar()
tk.Label(root, textvariable=stats_bar_var,
         bg=DARK, fg=SAND, font=("Consolas", 9),
         anchor="w", padx=8, pady=5).pack(fill="x", padx=8, pady=(4,0))

# Status bar
status_bar = tk.Frame(root, bg=SAND)
status_bar.pack(fill="x")
status_var = tk.StringVar(value="  No file loaded — click Load CSV to begin")
tk.Label(status_bar, textvariable=status_var,
         bg=SAND, fg=MUTED, font=("Calibri", 9), anchor="w").pack(side="left", padx=4, pady=4)
tk.Label(status_bar, text="CSV Viewer  ·  Python  ",
         bg=SAND, fg=MUTED, font=("Calibri", 9), anchor="e").pack(side="right", padx=4, pady=4)

root.mainloop()