import tkinter as tk
from tkinter import ttk
#Added by Samrachana
# Colors
BG = "#FAF7F2"
TERRA = "#C0533A"
SAGE = "#7A9E87"
SAND = "#E8DDD0"
DARK = "#2B2B2B"
MUTED = "#8A8279"
LIGHT = "#F5EFE8"

root = tk.Tk()
root.title("CSV Viewer")
root.geometry("1200x700")
root.configure(bg=BG)

# Title Bar
title_bar = tk.Frame(root, bg=TERRA, height=50)
title_bar.pack(fill="x")

tk.Label(
    title_bar,
    text="CSV Viewer",
    bg=TERRA,
    fg="white",
    font=("Georgia", 15, "bold")
).pack(side="left", padx=15, pady=10)

# Toolbar
toolbar = tk.Frame(root, bg=SAND, pady=8)
toolbar.pack(fill="x")

tk.Button(
    toolbar,
    text="Load CSV",
    bg=TERRA,
    fg="white",
    font=("Calibri", 10, "bold")
).pack(side="left", padx=10)

tk.Button(
    toolbar,
    text="Show Stats",
    bg=SAGE,
    fg="white",
    font=("Calibri", 10, "bold")
).pack(side="left", padx=5)

tk.Label(
    toolbar,
    text="Search:",
    bg=SAND,
    fg=DARK
).pack(side="left", padx=(20, 5))

search_entry = tk.Entry(toolbar, width=30)
search_entry.pack(side="left")

# Main Area
body = tk.Frame(root, bg=BG)
body.pack(fill="both", expand=True)

# Left Panel
filter_panel = tk.Frame(body, bg=SAND, width=220)
filter_panel.pack(side="left", fill="y")
filter_panel.pack_propagate(False)

tk.Label(
    filter_panel,
    text="Filters",
    bg=SAND,
    fg=DARK,
    font=("Calibri", 12, "bold")
).pack(pady=10)

# Dummy Filters
for i in range(5):
    tk.Label(
        filter_panel,
        text=f"Filter {i+1}",
        bg=SAND
    ).pack(anchor="w", padx=10, pady=5)

# Right Panel
table_panel = tk.Frame(body, bg=BG)
table_panel.pack(side="left", fill="both", expand=True)

# Table
columns = ("Column1", "Column2", "Column3", "Column4")

tree = ttk.Treeview(
    table_panel,
    columns=columns,
    show="headings"
)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)

# Dummy Data
for i in range(20):
    tree.insert(
        "",
        "end",
        values=(
            f"Data {i}",
            f"Value {i}",
            f"Item {i}",
            f"Info {i}"
        )
    )

tree.pack(fill="both", expand=True, padx=10, pady=10)

# Stats Bar
stats_bar = tk.Label(
    root,
    text="Statistics will appear here",
    bg=DARK,
    fg="white",
    anchor="w"
)
stats_bar.pack(fill="x")

# Status Bar
status_bar = tk.Label(
    root,
    text="Ready",
    bg=SAND,
    fg=MUTED,
    anchor="w"
)
status_bar.pack(fill="x")

root.mainloop()
#my name is nischal shrestha