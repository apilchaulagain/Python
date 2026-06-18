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

all_rows     = []
col_types    = {}   # col -> "int" | "float" | "text"
filter_widgets = {} # col -> widget reference
filter_vars    = {} # col -> tk variable

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


def col_range(col):
    vals = []
    for r in all_rows:
        try: vals.append(float(r[col]))
        except: pass
    return (min(vals), max(vals)) if vals else (0, 100)


def unique_vals(col):
    return sorted(set(r[col].strip() for r in all_rows if r[col].strip()))


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

    # global search
    kw = search_var.get().lower()
    if kw:
        result = [r for r in result if any(kw in str(v).lower() for v in r.values())]

    # column filters
    for col, var in filter_vars.items():
        ctype = col_types.get(col, "text")
        val   = var.get()

        if ctype in ("int", "float"):
            # val is the slider position (float)
            try:
                lo, hi = col_range(col)
                threshold = float(val)
                result = [r for r in result if _numeric(r[col]) >= threshold]
            except:
                pass
        else:
            # text / dropdown — filter if not "All"
            if val and val != "All":
                result = [r for r in result if r[col].strip() == val]

    populate_table(result)


def _numeric(v):
    try:    return float(v)
    except: return None


# ── Filter panel builder ──────────────────────────────────────

def build_filter_panel():
    """Rebuild the filter panel based on loaded CSV columns."""
    for w in filter_scroll_inner.winfo_children():
        w.destroy()
    filter_vars.clear()
    filter_widgets.clear()

    if not all_rows:
        return

    tk.Label(filter_scroll_inner, text="Column Filters",
             bg=SAND, fg=DARK, font=("Georgia", 11, "bold"),
             anchor="w").pack(fill="x", padx=10, pady=(10, 4))

    tk.Frame(filter_scroll_inner, bg=MUTED, height=1).pack(fill="x", padx=10, pady=(0, 8))

    for col in all_rows[0].keys():
        ctype = col_types.get(col, "text")
        frame = tk.Frame(filter_scroll_inner, bg=SAND)
        frame.pack(fill="x", padx=10, pady=4)

        # Column label + type badge
        top = tk.Frame(frame, bg=SAND)
        top.pack(fill="x")
        tk.Label(top, text=col, bg=SAND, fg=DARK,
                 font=("Calibri", 10, "bold"), anchor="w").pack(side="left")
        badge_color = TERRA if ctype in ("int","float") else SAGE
        tk.Label(top, text=f" {ctype} ",
                 bg=badge_color, fg="white",
                 font=("Calibri", 7, "bold")).pack(side="right")

        if ctype in ("int", "float"):
            lo, hi = col_range(col)
            var = tk.DoubleVar(value=lo)
            filter_vars[col] = var

            # value readout
            val_label = tk.Label(frame, text=f"≥ {lo:,.0f}" if ctype=="int" else f"≥ {lo:,.2f}",
                                  bg=SAND, fg=TERRA, font=("Consolas", 9))
            val_label.pack(anchor="w")

            def make_slider_cmd(v=var, lbl=val_label, ct=ctype, lo_=lo, hi_=hi):
                def cmd(val):
                    n = float(val)
                    lbl.config(text=f"≥ {n:,.0f}" if ct=="int" else f"≥ {n:,.2f}")
                    apply_filters()
                return cmd

            slider = ttk.Scale(frame, from_=lo, to=hi,
                               orient="horizontal",
                               variable=var,
                               command=make_slider_cmd())
            slider.pack(fill="x", pady=(2, 0))

            # range labels
            rl = tk.Frame(frame, bg=SAND)
            rl.pack(fill="x")
            tk.Label(rl, text=f"{lo:,.0f}" if ctype=="int" else f"{lo:,.1f}",
                     bg=SAND, fg=MUTED, font=("Calibri", 8)).pack(side="left")
            tk.Label(rl, text=f"{hi:,.0f}" if ctype=="int" else f"{hi:,.1f}",
                     bg=SAND, fg=MUTED, font=("Calibri", 8)).pack(side="right")

            # reset button
            def make_reset(v=var, lo_=lo, lbl=val_label, ct=ctype):
                def reset():
                    v.set(lo_)
                    lbl.config(text=f"≥ {lo_:,.0f}" if ct=="int" else f"≥ {lo_:,.2f}")
                    apply_filters()
                return reset

            tk.Button(frame, text="Reset", command=make_reset(),
                      bg=SAND, fg=MUTED, font=("Calibri", 8),
                      relief="flat", cursor="hand2", pady=0).pack(anchor="e")

        else:
            # Dropdown with unique values
            vals = ["All"] + unique_vals(col)
            var = tk.StringVar(value="All")
            filter_vars[col] = var

            cb = ttk.Combobox(frame, textvariable=var,
                              values=vals, state="readonly",
                              font=("Calibri", 10))
            cb.pack(fill="x", pady=(4, 0))
            var.trace_add("write", apply_filters)

        # divider
        tk.Frame(filter_scroll_inner, bg=LIGHT, height=1).pack(fill="x", padx=10, pady=2)

    # Reset all button
    tk.Button(filter_scroll_inner, text="Reset All Filters",
              command=reset_all_filters,
              bg=TERRA, fg="white",
              font=("Calibri", 10, "bold"),
              relief="flat", cursor="hand2",
              padx=10, pady=6).pack(fill="x", padx=10, pady=10)


def reset_all_filters():
    for col, var in filter_vars.items():
        ctype = col_types.get(col, "text")
        if ctype in ("int", "float"):
            lo, _ = col_range(col)
            var.set(lo)
        else:
            var.set("All")
    search_var.set("")
    apply_filters()


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
        build_filter_panel()
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
root.geometry("1200x700")
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

# ── Main body: filter panel (left) + table (right) ────────────
body = tk.Frame(root, bg=BG)
body.pack(fill="both", expand=True, padx=0, pady=0)

# Stats bar
stats_bar_var = tk.StringVar()
tk.Label(right_panel, textvariable=stats_bar_var,
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

#ADD fuction to readd exported database's