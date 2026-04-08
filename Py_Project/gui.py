"""
NCRB Crime Predictor Dashboard
===============================
A weather-app style dashboard for Indian crime data.
Pick a crime → instantly see stats, trend, anomalies, and prediction.

Features:
  1. Live Search — find any crime/district instantly
  2. Dashboard Cards — at-a-glance stats (total, peak, trend, predicted next year)
  3. Anomaly Detection — flags years with unusual spikes/drops
  4. Forecast — linear regression predicts next year's value
  5. Export — save filtered data as CSV

Run:  python gui.py  (from Py_Project folder)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
from datetime import datetime

# ══════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_data():
    delhi = pd.read_csv(os.path.join(BASE_DIR, 'Delhi crime records.csv'), index_col='CRIME HEAD')
    delhi = delhi.drop(columns=['Aug 2022'], errors='ignore')
    for c in delhi.columns:
        delhi[c] = pd.to_numeric(delhi[c], errors='coerce').fillna(0).astype(int)

    kerala = pd.read_csv(os.path.join(BASE_DIR, 'kerala criminal cases  - crimes  accidents.csv'))
    kerala = kerala.drop(columns=['Sl.No', '2022 (Up to Aug)'], errors='ignore')
    kerala = kerala.set_index('Crime Heads')
    kerala = kerala[~kerala.index.duplicated(keep='first')]
    for c in kerala.columns:
        kerala[c] = pd.to_numeric(kerala[c], errors='coerce').fillna(0).astype(int)

    pocso = pd.read_csv(
        os.path.join(BASE_DIR, 'kerala criminal cases  - POSCO ACTS(district wise).csv'),
        index_col='District'
    )
    pocso = pocso.drop(columns=['2022 (Up to Aug)'], errors='ignore')
    for c in pocso.columns:
        pocso[c] = pd.to_numeric(pocso[c], errors='coerce').fillna(0).astype(int)

    return delhi, kerala, pocso

delhi, kerala, pocso = load_data()


# ══════════════════════════════════════════════════════════════════
# ANALYSIS ENGINE
# ══════════════════════════════════════════════════════════════════

def analyze(series):
    """Full analysis of a time-series: stats + anomalies + forecast."""
    vals = series.values.astype(float)
    years = series.index.tolist()
    n = len(vals)

    # --- Basic stats ---
    result = {
        'total':     int(np.sum(vals)),
        'mean':      round(np.mean(vals), 1),
        'median':    round(np.median(vals), 1),
        'std_dev':   round(np.std(vals), 1),
        'min_val':   int(np.min(vals)),
        'min_year':  years[int(np.argmin(vals))],
        'max_val':   int(np.max(vals)),
        'max_year':  years[int(np.argmax(vals))],
    }

    # --- Trend (CAGR) ---
    if vals[0] > 0 and n > 1:
        result['cagr'] = round(((vals[-1] / vals[0]) ** (1/(n-1)) - 1) * 100, 1)
    else:
        result['cagr'] = 0.0

    # --- Year-over-year change (last year) ---
    if n >= 2 and vals[-2] > 0:
        result['last_yoy'] = round((vals[-1] - vals[-2]) / vals[-2] * 100, 1)
    else:
        result['last_yoy'] = 0.0

    # --- Anomalies (>1.5 std dev from mean) ---
    mean, std = np.mean(vals), np.std(vals)
    anomalies = []
    if std > 0:
        for yr, v in zip(years, vals):
            z = (v - mean) / std
            if abs(z) > 1.5:
                anomalies.append({
                    'year': yr,
                    'value': int(v),
                    'type': "SPIKE ↑" if z > 0 else "DROP ↓",
                    'severity': f"{abs(z):.1f}σ"
                })
    result['anomalies'] = anomalies

    # --- Forecast (linear regression) ---
    x = np.arange(n)
    slope, intercept = np.polyfit(x, vals, 1)
    pred_years = []
    for p in range(1, 4):  # predict 3 years ahead
        pred_val = max(0, int(slope * (n - 1 + p) + intercept))
        try:
            pred_yr = str(int(years[-1]) + p)
        except:
            pred_yr = f"+{p}"
        pred_years.append((pred_yr, pred_val))

    result['predictions'] = pred_years
    result['trend_slope'] = round(slope, 1)
    result['trend_dir'] = "Rising" if slope > 5 else ("Falling" if slope < -5 else "Stable")

    return result


# ══════════════════════════════════════════════════════════════════
# THEME
# ══════════════════════════════════════════════════════════════════
T = {
    "bg":      "#0f0f1a",    "bg2":     "#161625",
    "sidebar": "#111120",    "card":    "#1a1a30",
    "border":  "#2a2a50",    "text":    "#e0e0f0",
    "dim":     "#7777aa",    "accent":  "#c084fc",
    "accent2": "#50c8f0",    "red":     "#ff6b6b",
    "green":   "#51cf66",    "orange":  "#f4a742",
    "pink":    "#e05c8a",    "entry":   "#16213e",
    "btn":     "#7c5cbf",
}


# ══════════════════════════════════════════════════════════════════
# APP
# ══════════════════════════════════════════════════════════════════
class CrimePredictor:
    def __init__(self, root):
        self.root = root
        self.root.title("NCRB Crime Predictor")
        self.root.geometry("1350x780")
        self.root.configure(bg=T["bg"])
        self.root.minsize(1050, 600)
        self.current_ds = "Delhi"
        self.canvas_widget = None
        self.current_fig = None

        # Styles
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Dark.Treeview", background=T["card"], foreground=T["text"],
                     fieldbackground=T["card"], borderwidth=0, font=("Segoe UI", 10), rowheight=25)
        s.configure("Dark.Treeview.Heading", background=T["sidebar"], foreground=T["accent"],
                     font=("Segoe UI", 10, "bold"), borderwidth=0)
        s.map("Dark.Treeview", background=[("selected", T["btn"])], foreground=[("selected","white")])

        self._build_sidebar()
        self._build_main()
        self._refresh_list()

    # ── SIDEBAR ──────────────────────────────────────────────────
    def _build_sidebar(self):
        sb = tk.Frame(self.root, bg=T["sidebar"], width=200)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        tk.Label(sb, text="📊 Crime\nPredictor", bg=T["sidebar"], fg=T["accent"],
                 font=("Segoe UI", 17, "bold"), justify="center").pack(pady=(20,15))
        tk.Frame(sb, bg=T["border"], height=1).pack(fill="x", padx=12)

        tk.Label(sb, text="DATASET", bg=T["sidebar"], fg=T["dim"],
                 font=("Segoe UI", 8, "bold")).pack(padx=18, pady=(14,4), anchor="w")

        self.ds_var = tk.StringVar(value="Delhi")
        for name, icon in [("Delhi","🏙"), ("Kerala","🌴"), ("POCSO","🛡")]:
            tk.Radiobutton(
                sb, text=f" {icon} {name}", variable=self.ds_var, value=name,
                bg=T["sidebar"], fg=T["text"], selectcolor=T["card"],
                activebackground=T["sidebar"], activeforeground=T["accent"],
                font=("Segoe UI", 11), indicatoron=0, borderwidth=0,
                padx=18, pady=7, relief="flat", command=self._on_ds_change
            ).pack(fill="x", padx=8, pady=1)

        tk.Frame(sb, bg=T["border"], height=1).pack(fill="x", padx=12, pady=12)

        # Export button
        exp_btn = tk.Button(sb, text="📋 Export Data to CSV", bg=T["card"], fg=T["text"],
                            activebackground=T["border"], activeforeground=T["accent"],
                            font=("Segoe UI", 9), relief="flat", anchor="w",
                            padx=14, pady=6, borderwidth=0, command=self._export)
        exp_btn.pack(fill="x", padx=10, pady=4)
        exp_btn.bind("<Enter>", lambda e: exp_btn.config(bg=T["border"]))
        exp_btn.bind("<Leave>", lambda e: exp_btn.config(bg=T["card"]))

        # Info
        tk.Label(sb, text="How it works:\n\n"
                 "1. Pick a dataset\n"
                 "2. Search or click\n"
                 "   any crime\n"
                 "3. See prediction,\n"
                 "   stats & anomalies\n"
                 "   instantly",
                 bg=T["sidebar"], fg=T["dim"], font=("Segoe UI", 8),
                 justify="left").pack(side="bottom", padx=18, pady=15, anchor="w")

    # ── MAIN AREA ────────────────────────────────────────────────
    def _build_main(self):
        self.main = tk.Frame(self.root, bg=T["bg"])
        self.main.pack(side="right", fill="both", expand=True)

        # ── TOP: Search ─────────────────────────────────────
        sf = tk.Frame(self.main, bg=T["card"])
        sf.pack(fill="x", padx=12, pady=(12,0))

        tk.Label(sf, text=" 🔍", bg=T["card"], fg=T["accent"],
                 font=("Segoe UI", 13)).pack(side="left", padx=(8,4))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(sf, textvariable=self.search_var, bg=T["entry"],
                                      fg=T["text"], insertbackground=T["accent"],
                                      font=("Segoe UI", 12), relief="flat", borderwidth=0)
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=7, padx=4)
        self._set_placeholder()
        self.search_entry.bind("<FocusIn>", self._clear_placeholder)
        self.search_entry.bind("<FocusOut>", self._maybe_set_placeholder)
        self.search_var.trace_add("write", lambda *a: self._refresh_list())

        # ── MIDDLE: Crime list (left) + Dashboard (right) ───
        mid = tk.PanedWindow(self.main, orient="horizontal", bg=T["border"],
                              sashwidth=3, sashrelief="flat")
        mid.pack(fill="both", expand=True, padx=12, pady=8)

        # Left pane — crime list
        left = tk.Frame(mid, bg=T["bg"])
        mid.add(left, width=320)

        self.list_status = tk.StringVar(value="")
        tk.Label(left, textvariable=self.list_status, bg=T["bg"], fg=T["dim"],
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0,3))

        tree_f = tk.Frame(left, bg=T["border"])
        tree_f.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tree_f, style="Dark.Treeview", selectmode="browse",
                                  columns=("latest",), show="tree headings")
        self.tree.heading("#0", text="Crime / District", anchor="w")
        self.tree.heading("latest", text="Latest Year")
        self.tree.column("#0", width=200, minwidth=150)
        self.tree.column("latest", width=90, anchor="center")
        sy = ttk.Scrollbar(tree_f, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sy.set)
        sy.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Right pane — dashboard
        right_outer = tk.Frame(mid, bg=T["bg"])
        mid.add(right_outer, width=700)

        # Scrollable dashboard
        dash_canvas = tk.Canvas(right_outer, bg=T["bg"], highlightthickness=0)
        dash_scroll = ttk.Scrollbar(right_outer, orient="vertical", command=dash_canvas.yview)
        self.dash = tk.Frame(dash_canvas, bg=T["bg"])

        self.dash.bind("<Configure>", lambda e: dash_canvas.configure(scrollregion=dash_canvas.bbox("all")))
        dash_canvas.create_window((0, 0), window=self.dash, anchor="nw")
        dash_canvas.configure(yscrollcommand=dash_scroll.set)

        dash_scroll.pack(side="right", fill="y")
        dash_canvas.pack(side="left", fill="both", expand=True)

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            dash_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        dash_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Placeholder
        self.dash_placeholder = tk.Label(
            self.dash, text="👈  Select a crime from the list\nto see predictions and analysis",
            bg=T["bg"], fg=T["dim"], font=("Segoe UI", 14), justify="center"
        )
        self.dash_placeholder.pack(expand=True, pady=80)

    # ── PLACEHOLDER HELPERS ─────────────────────────────────────
    def _set_placeholder(self):
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "Search crimes or districts...")
        self.search_entry.config(fg=T["dim"])

    def _clear_placeholder(self, e):
        if self.search_entry.get() == "Search crimes or districts...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=T["text"])

    def _maybe_set_placeholder(self, e):
        if not self.search_entry.get():
            self._set_placeholder()

    # ── DATASET CHANGE ──────────────────────────────────────────
    def _on_ds_change(self):
        self.current_ds = self.ds_var.get()
        self._refresh_list()
        self._clear_dashboard()

    def _get_df(self):
        if self.current_ds == "Delhi":  return delhi
        if self.current_ds == "Kerala": return kerala
        return pocso

    # ── REFRESH LIST ─────────────────────────────────────────────
    def _refresh_list(self):
        q = self.search_var.get().strip().lower()
        if q == "search crimes or districts...":
            q = ""

        df = self._get_df()
        if q:
            mask = df.index.str.lower().str.contains(q, na=False)
            df = df[mask]

        self.tree.delete(*self.tree.get_children())
        last_col = df.columns[-1]
        for idx, row in df.iterrows():
            latest = f"{int(row[last_col]):,}"
            self.tree.insert("", "end", text=str(idx), values=(latest,))

        n = len(df)
        if q:
            self.list_status.set(f"🔍 {n} result{'s' if n!=1 else ''} for \"{q}\"")
        else:
            self.list_status.set(f"{self.current_ds} — {n} categories")

    # ── ON SELECT → BUILD DASHBOARD ─────────────────────────────
    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        name = self.tree.item(sel[0])["text"]
        df = self._get_df()
        if name not in df.index:
            return

        series = df.loc[name]
        result = analyze(series)
        self._build_dashboard(name, series, result)

    # ── CLEAR DASHBOARD ─────────────────────────────────────────
    def _clear_dashboard(self):
        for w in self.dash.winfo_children():
            w.destroy()
        self.dash_placeholder = tk.Label(
            self.dash, text="👈  Select a crime from the list\nto see predictions and analysis",
            bg=T["bg"], fg=T["dim"], font=("Segoe UI", 14), justify="center"
        )
        self.dash_placeholder.pack(expand=True, pady=80)

    # ══════════════════════════════════════════════════════════════
    # THE DASHBOARD — weather-app style
    # ══════════════════════════════════════════════════════════════
    def _build_dashboard(self, name, series, result):
        # Clear
        for w in self.dash.winfo_children():
            w.destroy()

        # ── Header ────────────────────────────────────────
        hdr = tk.Frame(self.dash, bg=T["bg"])
        hdr.pack(fill="x", padx=8, pady=8)

        tk.Label(hdr, text=name, bg=T["bg"], fg=T["accent"],
                 font=("Segoe UI", 18, "bold"), anchor="w").pack(side="left")

        trend = result['trend_dir']
        t_color = T["red"] if trend == "Rising" else (T["green"] if trend == "Falling" else T["orange"])
        t_arrow = "📈" if trend == "Rising" else ("📉" if trend == "Falling" else "➡️")
        tk.Label(hdr, text=f"{t_arrow} {trend}", bg=T["bg"], fg=t_color,
                 font=("Segoe UI", 13, "bold")).pack(side="right")

        # ── KPI Cards Row ─────────────────────────────────
        cards = tk.Frame(self.dash, bg=T["bg"])
        cards.pack(fill="x", padx=8, pady=(6,4))

        # Predicted next year (the big one)
        pred_yr, pred_val = result['predictions'][0]
        last_yr = series.index[-1]
        last_val = int(series.iloc[-1])

        kpi_data = [
            (f"🔮 {pred_yr} Prediction", f"{pred_val:,}", T["pink"],
             f"Based on {len(series)} years of data"),
            (f"📌 Latest ({last_yr})", f"{last_val:,}", T["accent"],
             f"{'+' if result['last_yoy']>0 else ''}{result['last_yoy']}% vs prev year"),
            ("📊 Average / Year", f"{result['mean']:,.0f}", T["accent2"],
             f"Std Dev: {result['std_dev']:,.0f}"),
            ("🏔 Peak", f"{result['max_val']:,}", T["orange"],
             f"Year: {result['max_year']}"),
        ]

        for i, (label, value, color, sub) in enumerate(kpi_data):
            card = tk.Frame(cards, bg=T["card"], padx=16, pady=12, highlightbackground=T["border"],
                            highlightthickness=1)
            card.grid(row=0, column=i, padx=4, sticky="nsew")
            cards.columnconfigure(i, weight=1)

            tk.Label(card, text=label, bg=T["card"], fg=T["dim"],
                     font=("Segoe UI", 8, "bold")).pack(anchor="w")
            tk.Label(card, text=value, bg=T["card"], fg=color,
                     font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(4,2))
            tk.Label(card, text=sub, bg=T["card"], fg=T["dim"],
                     font=("Segoe UI", 8)).pack(anchor="w")

        # ── Trend Chart with Forecast ─────────────────────
        chart_frame = tk.Frame(self.dash, bg=T["card"], highlightbackground=T["border"],
                                highlightthickness=1)
        chart_frame.pack(fill="x", padx=8, pady=(6,4))

        fig = Figure(figsize=(9, 2.8), dpi=100, facecolor=T["card"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(T["bg"])
        ax.tick_params(colors=T["dim"], labelsize=8)
        for sp in ["top","right"]: ax.spines[sp].set_visible(False)
        for sp in ["bottom","left"]: ax.spines[sp].set_color(T["border"])
        ax.grid(True, alpha=0.15, linestyle="--", color=T["dim"])

        years = series.index.tolist()
        vals = series.values.astype(float)

        # Actual data
        ax.plot(years, vals, marker="o", markersize=5, linewidth=2.2,
                color=T["accent"], label="Actual", zorder=3)
        ax.fill_between(years, vals, alpha=0.08, color=T["accent"])

        # Highlight anomalies
        for a in result['anomalies']:
            yr_idx = years.index(a['year']) if a['year'] in years else None
            if yr_idx is not None:
                c = T["red"] if "SPIKE" in a['type'] else T["green"]
                ax.plot(years[yr_idx], vals[yr_idx], 'o', markersize=10,
                        color=c, alpha=0.5, zorder=2)

        # Forecast line
        pred_x = [years[-1]] + [p[0] for p in result['predictions']]
        pred_y = [vals[-1]]  + [p[1] for p in result['predictions']]
        ax.plot(pred_x, pred_y, marker="D", markersize=5, linewidth=2,
                linestyle="--", color=T["pink"], alpha=0.7, label="Forecast", zorder=3)

        # Forecast labels
        for yr, v in result['predictions']:
            ax.annotate(f"{v:,}", (yr, v), textcoords="offset points",
                        xytext=(0, 12), fontsize=7, color=T["pink"],
                        ha="center", fontweight="bold")

        ax.legend(fontsize=8, loc="upper left", framealpha=0.4, labelcolor=T["text"])
        ax.set_ylabel("Cases", fontsize=9, color=T["dim"])
        ax.set_title(f"{name} — Trend & 3-Year Forecast", fontsize=11,
                      color=T["text"], fontweight="bold", pad=8)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()
        self.current_fig = fig

        # ── Forecast Table ────────────────────────────────
        fc_frame = tk.Frame(self.dash, bg=T["card"], padx=16, pady=12,
                            highlightbackground=T["border"], highlightthickness=1)
        fc_frame.pack(fill="x", padx=8, pady=(4,4))

        tk.Label(fc_frame, text="🔮 Prediction Details", bg=T["card"], fg=T["accent2"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(fc_frame, text=f"Method: Linear Regression  •  Slope: {result['trend_slope']:+.1f} cases/year  •  Based on {len(series)} data points",
                 bg=T["card"], fg=T["dim"], font=("Segoe UI", 8)).pack(anchor="w", pady=(2,8))

        # Table header
        tbl = tk.Frame(fc_frame, bg=T["card"])
        tbl.pack(fill="x")

        for j, h in enumerate(["Year", "Predicted Cases", "Change from Latest"]):
            tk.Label(tbl, text=h, bg=T["border"], fg=T["accent"],
                     font=("Segoe UI", 9, "bold"), padx=12, pady=4).grid(row=0, column=j, sticky="ew", padx=1)
            tbl.columnconfigure(j, weight=1)

        for i, (yr, val) in enumerate(result['predictions']):
            change = val - last_val
            pct = round(change / last_val * 100, 1) if last_val > 0 else 0
            sign = "+" if change >= 0 else ""
            c = T["red"] if change > 0 else T["green"]

            tk.Label(tbl, text=yr, bg=T["card"], fg=T["text"],
                     font=("Segoe UI", 10), padx=12, pady=4).grid(row=i+1, column=0, sticky="ew", padx=1)
            tk.Label(tbl, text=f"{val:,}", bg=T["card"], fg=T["text"],
                     font=("Segoe UI", 10, "bold"), padx=12, pady=4).grid(row=i+1, column=1, sticky="ew", padx=1)
            tk.Label(tbl, text=f"{sign}{change:,}  ({sign}{pct}%)", bg=T["card"], fg=c,
                     font=("Segoe UI", 10), padx=12, pady=4).grid(row=i+1, column=2, sticky="ew", padx=1)

        # ── Anomalies Section ─────────────────────────────
        anom_frame = tk.Frame(self.dash, bg=T["card"], padx=16, pady=12,
                              highlightbackground=T["border"], highlightthickness=1)
        anom_frame.pack(fill="x", padx=8, pady=(4,8))

        anomalies = result['anomalies']
        if anomalies:
            tk.Label(anom_frame, text=f"⚠️ {len(anomalies)} Anomal{'y' if len(anomalies)==1 else 'ies'} Detected",
                     bg=T["card"], fg=T["orange"], font=("Segoe UI", 11, "bold")).pack(anchor="w")
            tk.Label(anom_frame, text="Years where cases deviated more than 1.5 standard deviations from the average",
                     bg=T["card"], fg=T["dim"], font=("Segoe UI", 8)).pack(anchor="w", pady=(2,8))

            for a in anomalies:
                c = T["red"] if "SPIKE" in a['type'] else T["green"]
                row_f = tk.Frame(anom_frame, bg=T["bg2"], pady=6, padx=12)
                row_f.pack(fill="x", pady=2)
                tk.Label(row_f, text=f"{a['year']}", bg=T["bg2"], fg=T["text"],
                         font=("Segoe UI", 10, "bold")).pack(side="left")
                tk.Label(row_f, text=f"    {a['value']:,} cases", bg=T["bg2"], fg=T["text"],
                         font=("Segoe UI", 10)).pack(side="left")
                tk.Label(row_f, text=f"{a['type']}  ({a['severity']})", bg=T["bg2"],
                         fg=c, font=("Segoe UI", 10, "bold")).pack(side="right")
        else:
            tk.Label(anom_frame, text="✅ No Anomalies Detected", bg=T["card"],
                     fg=T["green"], font=("Segoe UI", 11, "bold")).pack(anchor="w")
            tk.Label(anom_frame, text="All values are within the normal range (±1.5σ from mean).",
                     bg=T["card"], fg=T["dim"], font=("Segoe UI", 9)).pack(anchor="w", pady=(2,0))

        # ── Stats Summary ─────────────────────────────────
        stat_frame = tk.Frame(self.dash, bg=T["card"], padx=16, pady=12,
                               highlightbackground=T["border"], highlightthickness=1)
        stat_frame.pack(fill="x", padx=8, pady=(0,12))

        tk.Label(stat_frame, text="📋 Full Statistics", bg=T["card"], fg=T["accent2"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0,8))

        stats_list = [
            ("Total Cases (all years)", f"{result['total']:,}"),
            ("Average per Year", f"{result['mean']:,.1f}"),
            ("Median", f"{result['median']:,.1f}"),
            ("Standard Deviation", f"{result['std_dev']:,.1f}"),
            ("Lowest", f"{result['min_val']:,} ({result['min_year']})"),
            ("Highest", f"{result['max_val']:,} ({result['max_year']})"),
            ("Growth Rate (CAGR)", f"{'+' if result['cagr']>0 else ''}{result['cagr']}% / year"),
            ("Last Year Change", f"{'+' if result['last_yoy']>0 else ''}{result['last_yoy']}% vs previous"),
        ]

        for i, (label, val) in enumerate(stats_list):
            bg = T["bg2"] if i % 2 == 0 else T["card"]
            row = tk.Frame(stat_frame, bg=bg, pady=4, padx=8)
            row.pack(fill="x")
            tk.Label(row, text=label, bg=bg, fg=T["dim"],
                     font=("Segoe UI", 9)).pack(side="left")
            tk.Label(row, text=val, bg=bg, fg=T["text"],
                     font=("Segoe UI", 10, "bold")).pack(side="right")

    # ── EXPORT ───────────────────────────────────────────────────
    def _export(self):
        df = self._get_df()
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile=f"{self.current_ds}_data.csv"
        )
        if path:
            df.to_csv(path)
            messagebox.showinfo("Exported", f"Saved {len(df)} rows to:\n{path}")


# ══════════════════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    app = CrimePredictor(root)
    root.mainloop()
