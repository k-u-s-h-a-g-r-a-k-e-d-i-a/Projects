import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# Always resolve CSVs relative to this script's folder
BASE = Path(__file__).parent

# ─────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="India Crime Analytics",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# THEME / CSS
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0e0e1a; color: #e0e0f0; }
    section[data-testid="stSidebar"] { background-color: #13131f; border-right: 1px solid #2a2a40; }

    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #2d2d5e;
        border-radius: 14px;
        padding: 22px 18px;
        text-align: center;
        margin-bottom: 8px;
    }
    .kpi-value  { font-size: 2.1rem; font-weight: 800; margin: 0; }
    .kpi-label  { font-size: 0.78rem; color: #8888aa; margin-top: 4px; letter-spacing: 0.05em; text-transform: uppercase; }
    .kpi-delta  { font-size: 0.85rem; margin-top: 6px; }
    .kpi-up     { color: #ff6b6b; }
    .kpi-down   { color: #51cf66; }

    /* Section headers */
    .section-header {
        font-size: 1.25rem; font-weight: 700;
        color: #c0c0ff;
        border-left: 4px solid #7c5cbf;
        padding-left: 12px;
        margin: 24px 0 12px 0;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"]  { gap: 6px; background: transparent; }
    .stTabs [data-baseweb="tab"]       { background: #1a1a2e; border-radius: 8px 8px 0 0; padding: 8px 20px; color: #8888aa; font-weight: 600; }
    .stTabs [aria-selected="true"]     { background: #2d2d5e !important; color: #c0c0ff !important; }

    /* Plotly chart bg transparency */
    .js-plotly-plot { border-radius: 12px; }

    /* Divider */
    hr { border-color: #2a2a40; }

    /* Sidebar labels */
    .css-16huue1, label { color: #aaaacc !important; font-size: 0.85rem !important; }

    /* Select boxes */
    .stMultiSelect [data-baseweb="tag"] { background: #3a3a6e; }
</style>
""", unsafe_allow_html=True)

PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(20,20,40,0.6)",
        font=dict(color="#c0c0e8", family="Inter, sans-serif"),
        xaxis=dict(gridcolor="#2a2a40", linecolor="#3a3a50"),
        yaxis=dict(gridcolor="#2a2a40", linecolor="#3a3a50"),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#3a3a50"),
        margin=dict(l=40, r=20, t=40, b=40),
        colorway=["#7c5cbf","#e05c8a","#50c8f0","#f4a742","#51cf66","#ff6b6b","#c084fc","#22d3ee"],
    )
)
COLORS = ["#7c5cbf","#e05c8a","#50c8f0","#f4a742","#51cf66","#ff6b6b","#c084fc","#22d3ee",
          "#fb7185","#a3e635","#f59e0b","#10b981","#3b82f6","#8b5cf6","#ec4899","#14b8a6"]

# ─────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    # ── Delhi ─────────────────────────────────────────────────────
    delhi_raw = pd.read_csv(BASE / "../Py_Project/Delhi crime records.csv")
    delhi_raw.columns = [c.strip() for c in delhi_raw.columns]
    delhi_raw = delhi_raw.rename(columns={"CRIME HEAD": "Crime_Head", "Aug 2022": "2022"})
    year_cols_d = [c for c in delhi_raw.columns if c != "Crime_Head"]
    for c in year_cols_d:
        delhi_raw[c] = pd.to_numeric(delhi_raw[c], errors="coerce").fillna(0)
    delhi_long = delhi_raw.melt(id_vars="Crime_Head", value_vars=year_cols_d,
                                var_name="Year", value_name="Count")
    delhi_long["Year"]  = delhi_long["Year"].astype(int)
    delhi_long["State"] = "Delhi"

    # ── Kerala Crimes ─────────────────────────────────────────────
    kerala_raw = pd.read_csv(BASE / "../Py_Project/kerala criminal cases  - crimes  accidents.csv")
    kerala_raw.columns = [c.strip() for c in kerala_raw.columns]
    if "Sl.No" in kerala_raw.columns:
        kerala_raw = kerala_raw.drop(columns=["Sl.No"])
    kerala_raw = kerala_raw.rename(columns={"Crime Heads": "Crime_Head", "2022 (Up to Aug)": "2022"})
    year_cols_k = [c for c in kerala_raw.columns if c != "Crime_Head"]
    for c in year_cols_k:
        kerala_raw[c] = pd.to_numeric(kerala_raw[c], errors="coerce").fillna(0)
    kerala_long = kerala_raw.melt(id_vars="Crime_Head", value_vars=year_cols_k,
                                  var_name="Year", value_name="Count")
    kerala_long["Year"]  = kerala_long["Year"].astype(int)
    kerala_long["State"] = "Kerala"

    # ── Kerala POSCO (District-wise) ──────────────────────────────
    posco_raw = pd.read_csv(BASE / "../Py_Project/kerala criminal cases  - POSCO ACTS(district wise).csv")
    posco_raw.columns = [c.strip() for c in posco_raw.columns]
    posco_raw = posco_raw.rename(columns={"2022 (Up to Aug)": "2022"})
    year_cols_p = [c for c in posco_raw.columns if c != "District"]
    for c in year_cols_p:
        posco_raw[c] = pd.to_numeric(posco_raw[c], errors="coerce").fillna(0)
    posco_long = posco_raw.melt(id_vars="District", value_vars=year_cols_p,
                                var_name="Year", value_name="Count")
    posco_long["Year"] = posco_long["Year"].astype(int)

    return delhi_long, kerala_long, posco_long, delhi_raw, kerala_raw, posco_raw

delhi_df, kerala_df, posco_df, delhi_raw, kerala_raw, posco_raw = load_data()

# Helper
def fmt(n):
    if n >= 1_000_000: return f"{n/1_000_000:.2f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(int(n))

def apply_template(fig):
    fig.update_layout(PLOTLY_TEMPLATE["layout"])
    return fig

# ─────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 India Crime Dashboard")
    st.markdown("---")

    page = st.radio("Navigate to", ["📊 Overview", "🏙️ Delhi", "🌴 Kerala", "⚔️ Comparison"],
                    label_visibility="collapsed")

    st.markdown("---")

    # Year range for Delhi
    delhi_years = sorted(delhi_df["Year"].unique())
    kerala_years = sorted(kerala_df["Year"].unique())

    if page == "🏙️ Delhi":
        year_range = st.slider("Year Range", min_value=delhi_years[0], max_value=delhi_years[-1],
                               value=(delhi_years[0], delhi_years[-1]))
        crime_sel = st.multiselect("Crime Categories",
                                    sorted(delhi_df["Crime_Head"].unique()),
                                    default=sorted(delhi_df["Crime_Head"].unique()))

    elif page == "🌴 Kerala":
        year_range = st.slider("Year Range", min_value=kerala_years[0], max_value=kerala_years[-1],
                               value=(kerala_years[0], kerala_years[-1]))

        # curated list for readability
        core_crimes = ["Murder","Rape","Kidnapping & abduction","Dacoity","Robbery",
                       "Burglary","Theft","Riots","Hurt","Cheating","Molestation",
                       "Cyber Cases","Missing Cases","Cruelty by husband or relatives",
                       "NDPS Act","POSCO Acts"]
        crime_sel = st.multiselect("Crime Categories",
                                    sorted(kerala_df["Crime_Head"].unique()),
                                    default=core_crimes)

    elif page == "⚔️ Comparison":
        overlap = sorted(set(delhi_years) & set(kerala_years))
        year_range = st.slider("Year Range", min_value=overlap[0], max_value=overlap[-1],
                               value=(overlap[0], overlap[-1]))

    st.markdown("---")
    st.markdown("<small style='color:#555'>Data: NCRB | Delhi 2001–2022 | Kerala 2016–2022</small>",
                unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.markdown("# 📊 India Crime Analytics Dashboard")
    st.markdown("Exploring crime trends across **Delhi** and **Kerala** using NCRB data.")
    st.markdown("---")

    # ── KPI Row ──────────────────────────────────────────────────
    # Exclude non-crime / aggregate rows from Kerala for cleaner totals
    KERALA_EXCLUDE = ["No. of accidents","Death in accidents","Total Injuries in accidents",
                      "Cigarettes and Other Tobacco -Section 4","Cigarettes and Other Tobacco-Section 5",
                      "Cigarettes and Other Tobacco-Section 6(a)","Cigarettes and Other Tobacco-Section 6(b)",
                      "Cigarettes and Other Tobacco-Section 7","Other IPC Crimes","Other SLL Crimes",
                      "Abkari ACT"]
    k_filtered = kerala_df[~kerala_df["Crime_Head"].isin(KERALA_EXCLUDE)]

    delhi_total  = int(delhi_df["Count"].sum())
    kerala_total = int(k_filtered["Count"].sum())
    delhi_latest = int(delhi_df[delhi_df["Year"] == 2021]["Count"].sum())
    kerala_latest= int(k_filtered[k_filtered["Year"] == 2021]["Count"].sum())
    delhi_prev   = int(delhi_df[delhi_df["Year"] == 2020]["Count"].sum())
    kerala_prev  = int(k_filtered[k_filtered["Year"] == 2020]["Count"].sum())

    d_delta = ((delhi_latest - delhi_prev) / delhi_prev * 100) if delhi_prev else 0
    k_delta = ((kerala_latest - kerala_prev) / kerala_prev * 100) if kerala_prev else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="kpi-card">
            <p class="kpi-value" style="color:#c084fc">{fmt(delhi_total)}</p>
            <p class="kpi-label">Delhi Total Crimes (2001–2022)</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        arr = "↑" if d_delta > 0 else "↓"
        cls = "kpi-up" if d_delta > 0 else "kpi-down"
        st.markdown(f"""<div class="kpi-card">
            <p class="kpi-value" style="color:#e05c8a">{fmt(delhi_latest)}</p>
            <p class="kpi-label">Delhi Crimes in 2021</p>
            <p class="kpi-delta {cls}">{arr} {abs(d_delta):.1f}% vs 2020</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card">
            <p class="kpi-value" style="color:#50c8f0">{fmt(kerala_total)}</p>
            <p class="kpi-label">Kerala Total Crimes (2016–2022)</p>
        </div>""", unsafe_allow_html=True)
    with c4:
        arr = "↑" if k_delta > 0 else "↓"
        cls = "kpi-up" if k_delta > 0 else "kpi-down"
        st.markdown(f"""<div class="kpi-card">
            <p class="kpi-value" style="color:#f4a742">{fmt(kerala_latest)}</p>
            <p class="kpi-label">Kerala Crimes in 2021</p>
            <p class="kpi-delta {cls}">{arr} {abs(k_delta):.1f}% vs 2020</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Trend Lines Side by Side ──────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="section-header">Delhi — Annual Crime Trend (2001–2022)</p>', unsafe_allow_html=True)
        d_trend = delhi_df.groupby("Year")["Count"].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=d_trend["Year"], y=d_trend["Count"],
            mode="lines+markers",
            line=dict(color="#c084fc", width=2.5),
            marker=dict(size=6, color="#e040fb"),
            fill="tozeroy", fillcolor="rgba(192,132,252,0.12)",
            name="Total Crimes"
        ))
        fig.update_layout(
            PLOTLY_TEMPLATE["layout"],
            xaxis_title="Year", yaxis_title="Total Cases",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<p class="section-header">Kerala — Annual Crime Trend (2016–2022)</p>', unsafe_allow_html=True)
        k_trend = k_filtered.groupby("Year")["Count"].sum().reset_index()
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=k_trend["Year"], y=k_trend["Count"],
            mode="lines+markers",
            line=dict(color="#50c8f0", width=2.5),
            marker=dict(size=6, color="#22d3ee"),
            fill="tozeroy", fillcolor="rgba(80,200,240,0.12)",
            name="Total Crimes"
        ))
        fig2.update_layout(
            PLOTLY_TEMPLATE["layout"],
            xaxis_title="Year", yaxis_title="Total Cases",
            height=300
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Top Crime Categories ──────────────────────────────────────
    st.markdown("---")
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown('<p class="section-header">Delhi — Top Crime Categories (All Years)</p>', unsafe_allow_html=True)
        d_top = delhi_df.groupby("Crime_Head")["Count"].sum().sort_values(ascending=True).tail(10).reset_index()
        fig3 = px.bar(d_top, x="Count", y="Crime_Head", orientation="h",
                      color="Count", color_continuous_scale=["#3b1f7e","#c084fc","#f0abfc"])
        fig3.update_layout(PLOTLY_TEMPLATE["layout"], showlegend=False,
                           coloraxis_showscale=False, height=380,
                           yaxis_title=None, xaxis_title="Total Cases")
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        st.markdown('<p class="section-header">Kerala — Top Crime Categories (2016–2022)</p>', unsafe_allow_html=True)
        core = ["Murder","Rape","Kidnapping & abduction","Dacoity","Robbery","Burglary",
                "Theft","Riots","Hurt","Cheating","Molestation","Cruelty by husband or relatives",
                "NDPS Act","Cyber Cases","POSCO Acts","Missing Cases"]
        k_top = kerala_df[kerala_df["Crime_Head"].isin(core)].groupby("Crime_Head")["Count"].sum() \
                    .sort_values(ascending=True).reset_index()
        fig4 = px.bar(k_top, x="Count", y="Crime_Head", orientation="h",
                      color="Count", color_continuous_scale=["#0c4a6e","#0ea5e9","#7dd3fc"])
        fig4.update_layout(PLOTLY_TEMPLATE["layout"], showlegend=False,
                           coloraxis_showscale=False, height=380,
                           yaxis_title=None, xaxis_title="Total Cases")
        st.plotly_chart(fig4, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# PAGE 2 — DELHI
# ═══════════════════════════════════════════════════════════════════
elif page == "🏙️ Delhi":
    st.markdown("# 🏙️ Delhi Crime Analysis")
    st.markdown(f"Showing data for **{year_range[0]}–{year_range[1]}**")
    st.markdown("---")

    # Filter
    df = delhi_df[
        (delhi_df["Year"].between(*year_range)) &
        (delhi_df["Crime_Head"].isin(crime_sel if crime_sel else delhi_df["Crime_Head"].unique()))
    ]

    # KPIs
    total = int(df["Count"].sum())
    top_crime = df.groupby("Crime_Head")["Count"].sum().idxmax()
    peak_year = df.groupby("Year")["Count"].sum().idxmax()
    avg_yr = int(df.groupby("Year")["Count"].sum().mean())

    c1,c2,c3,c4 = st.columns(4)
    for col, val, label, color in [
        (c1, fmt(total),     "Total Cases",          "#c084fc"),
        (c2, top_crime,      "Most Reported Crime",  "#e05c8a"),
        (c3, str(peak_year), "Peak Year",            "#f4a742"),
        (c4, fmt(avg_yr),    "Avg Cases / Year",     "#50c8f0"),
    ]:
        with col:
            col.markdown(f"""<div class="kpi-card">
                <p class="kpi-value" style="color:{color}">{val}</p>
                <p class="kpi-label">{label}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Multi-line trend ──────────────────────────────────────────
    st.markdown('<p class="section-header">Crime Trends Over Time</p>', unsafe_allow_html=True)
    trend = df.groupby(["Year","Crime_Head"])["Count"].sum().reset_index()
    fig = px.line(trend, x="Year", y="Count", color="Crime_Head",
                  color_discrete_sequence=COLORS, markers=True)
    fig.update_layout(PLOTLY_TEMPLATE["layout"], height=420,
                      xaxis_title="Year", yaxis_title="Reported Cases",
                      legend_title="Crime Type")
    st.plotly_chart(fig, use_container_width=True)

    # ── Pie + Stacked Bar ─────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="section-header">Crime Share (Selected Period)</p>', unsafe_allow_html=True)
        pie_data = df.groupby("Crime_Head")["Count"].sum().reset_index().sort_values("Count", ascending=False)
        fig2 = px.pie(pie_data, names="Crime_Head", values="Count",
                      color_discrete_sequence=COLORS, hole=0.42)
        fig2.update_layout(PLOTLY_TEMPLATE["layout"], height=380, showlegend=True,
                           legend=dict(font=dict(size=10)))
        fig2.update_traces(textinfo="percent", hovertemplate="%{label}: %{value:,}<br>%{percent}")
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        st.markdown('<p class="section-header">Stacked Bar — Year-wise Breakdown</p>', unsafe_allow_html=True)
        fig3 = px.bar(trend, x="Year", y="Count", color="Crime_Head",
                      color_discrete_sequence=COLORS)
        fig3.update_layout(PLOTLY_TEMPLATE["layout"], height=380,
                           xaxis_title="Year", yaxis_title="Cases",
                           legend_title="Crime", barmode="stack",
                           legend=dict(font=dict(size=10)))
        st.plotly_chart(fig3, use_container_width=True)

    # ── Heatmap ───────────────────────────────────────────────────
    st.markdown('<p class="section-header">Heatmap — Crime × Year</p>', unsafe_allow_html=True)
    pivot = df.pivot_table(index="Crime_Head", columns="Year", values="Count", aggfunc="sum").fillna(0)
    fig4 = go.Figure(data=go.Heatmap(
        z=pivot.values.tolist(),
        x=[str(c) for c in pivot.columns],
        y=pivot.index.tolist(),
        colorscale="Purples",
        hoverongaps=False,
        hovertemplate="Crime: %{y}<br>Year: %{x}<br>Cases: %{z:,}<extra></extra>"
    ))
    fig4.update_layout(PLOTLY_TEMPLATE["layout"], height=max(300, 35 * len(pivot)),
                       xaxis_title="Year", yaxis_title=None,
                       margin=dict(l=160, r=20, t=30, b=40))
    st.plotly_chart(fig4, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# PAGE 3 — KERALA
# ═══════════════════════════════════════════════════════════════════
elif page == "🌴 Kerala":
    st.markdown("# 🌴 Kerala Crime Analysis")
    st.markdown(f"Showing data for **{year_range[0]}–{year_range[1]}**")
    st.markdown("---")

    df = kerala_df[
        (kerala_df["Year"].between(*year_range)) &
        (kerala_df["Crime_Head"].isin(crime_sel if crime_sel else kerala_df["Crime_Head"].unique()))
    ]

    total = int(df["Count"].sum())
    top_crime = df.groupby("Crime_Head")["Count"].sum().idxmax() if not df.empty else "N/A"
    peak_year = df.groupby("Year")["Count"].sum().idxmax() if not df.empty else "N/A"

    c1,c2,c3,c4 = st.columns(4)
    for col, val, label, color in [
        (c1, fmt(total),     "Total Cases (Selected)",   "#50c8f0"),
        (c2, top_crime[:20], "Top Crime Category",       "#e05c8a"),
        (c3, str(peak_year), "Peak Year",                "#f4a742"),
        (c4, str(len(crime_sel if crime_sel else [])), "Categories Selected", "#51cf66"),
    ]:
        with col:
            col.markdown(f"""<div class="kpi-card">
                <p class="kpi-value" style="color:{color}; font-size:1.5rem">{val}</p>
                <p class="kpi-label">{label}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Trend lines ───────────────────────────────────────────────
    st.markdown('<p class="section-header">Crime Trends Over Time</p>', unsafe_allow_html=True)
    trend = df.groupby(["Year","Crime_Head"])["Count"].sum().reset_index()
    fig = px.line(trend, x="Year", y="Count", color="Crime_Head",
                  color_discrete_sequence=COLORS, markers=True)
    fig.update_layout(PLOTLY_TEMPLATE["layout"], height=420,
                      xaxis_title="Year", yaxis_title="Reported Cases",
                      legend_title="Crime Type")
    st.plotly_chart(fig, use_container_width=True)

    # ── Pie + Bar ─────────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="section-header">Crime Share (Selected Period)</p>', unsafe_allow_html=True)
        pie_data = df.groupby("Crime_Head")["Count"].sum().reset_index().sort_values("Count", ascending=False)
        # Show top 12 for readability
        top12 = pie_data.head(12)
        others = pie_data.iloc[12:]["Count"].sum()
        if others > 0:
            top12 = pd.concat([top12, pd.DataFrame([{"Crime_Head":"Others","Count":others}])], ignore_index=True)
        fig2 = px.pie(top12, names="Crime_Head", values="Count",
                      color_discrete_sequence=COLORS, hole=0.42)
        fig2.update_layout(PLOTLY_TEMPLATE["layout"], height=380,
                           legend=dict(font=dict(size=10)))
        fig2.update_traces(textinfo="percent", hovertemplate="%{label}: %{value:,}")
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        st.markdown('<p class="section-header">Stacked Bar — Year-wise Breakdown</p>', unsafe_allow_html=True)
        fig3 = px.bar(trend, x="Year", y="Count", color="Crime_Head",
                      color_discrete_sequence=COLORS)
        fig3.update_layout(PLOTLY_TEMPLATE["layout"], height=380,
                           xaxis_title="Year", yaxis_title="Cases",
                           barmode="stack", legend=dict(font=dict(size=10)))
        st.plotly_chart(fig3, use_container_width=True)

    # ── POSCO District Breakdown ──────────────────────────────────
    st.markdown("---")
    st.markdown('<p class="section-header">POSCO Act Cases — District-wise Breakdown</p>', unsafe_allow_html=True)
    st.markdown("Protection of Children from Sexual Offences Act — district-level data across Kerala")

    posco_filt = posco_df[posco_df["Year"].between(*year_range)]
    posco_yr = st.selectbox("Select Year for District Map",
                            sorted(posco_filt["Year"].unique(), reverse=True),
                            key="posco_yr")

    col_e, col_f = st.columns([3, 2])

    with col_e:
        posco_yr_data = posco_filt[posco_filt["Year"] == posco_yr].sort_values("Count", ascending=True)
        posco_yr_data = posco_yr_data[posco_yr_data["District"] != "RAILWAY POLICE"]
        fig5 = px.bar(posco_yr_data, x="Count", y="District", orientation="h",
                      color="Count",
                      color_continuous_scale=["#1e3a5f","#2563eb","#93c5fd"],
                      title=f"POSCO Cases by District ({posco_yr})")
        fig5.update_layout(PLOTLY_TEMPLATE["layout"], height=520,
                           coloraxis_showscale=False, yaxis_title=None,
                           xaxis_title="No. of Cases")
        st.plotly_chart(fig5, use_container_width=True)

    with col_f:
        st.markdown(f"**All Years Trend — Top 6 Districts**")
        top6 = posco_df[posco_df["District"] != "RAILWAY POLICE"] \
                   .groupby("District")["Count"].sum().nlargest(6).index.tolist()
        posco_top6 = posco_df[
            posco_df["District"].isin(top6) &
            posco_df["Year"].between(*year_range)
        ]
        fig6 = px.line(posco_top6, x="Year", y="Count", color="District",
                       color_discrete_sequence=COLORS, markers=True)
        fig6.update_layout(PLOTLY_TEMPLATE["layout"], height=520,
                           xaxis_title="Year", yaxis_title="Cases",
                           legend=dict(font=dict(size=11)))
        st.plotly_chart(fig6, use_container_width=True)

    # ── Treemap of crime categories ───────────────────────────────
    st.markdown("---")
    st.markdown('<p class="section-header">Crime Category Treemap</p>', unsafe_allow_html=True)
    EXCLUDE = ["Other IPC Crimes","Other SLL Crimes","Abkari ACT",
               "Cigarettes and Other Tobacco -Section 4","Cigarettes and Other Tobacco-Section 5",
               "Cigarettes and Other Tobacco-Section 6(a)","Cigarettes and Other Tobacco-Section 6(b)",
               "Cigarettes and Other Tobacco-Section 7"]
    tree_data = kerala_df[
        (~kerala_df["Crime_Head"].isin(EXCLUDE)) &
        kerala_df["Year"].between(*year_range)
    ].groupby("Crime_Head")["Count"].sum().reset_index()
    tree_data = tree_data[tree_data["Count"] > 0]
    fig7 = px.treemap(tree_data, path=["Crime_Head"], values="Count",
                      color="Count", color_continuous_scale="Blues",
                      title="Crime Proportions — Kerala (Excluding Misc/Aggregates)")
    fig7.update_layout(PLOTLY_TEMPLATE["layout"], height=480)
    fig7.update_traces(hovertemplate="<b>%{label}</b><br>Cases: %{value:,}")
    st.plotly_chart(fig7, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# PAGE 4 — COMPARISON
# ═══════════════════════════════════════════════════════════════════
elif page == "⚔️ Comparison":
    st.markdown("# ⚔️ Delhi vs Kerala — Side-by-Side Comparison")
    st.markdown(f"Overlapping years: **{year_range[0]}–{year_range[1]}**")
    st.markdown("---")

    # Mapping Delhi → Kerala crime names
    CRIME_MAP = {
        "MURDER":          "Murder",
        "RAPE":            "Rape",
        "DACOITY":         "Dacoity",
        "ROBBERY":         "Robbery",
        "RIOT":            "Riots",
        "BURGLARY":        "Burglary",
        "HURT":            "Hurt",
        "M. O. WOMEN":     "Molestation",
    }

    overlap_crimes = list(CRIME_MAP.keys())
    selected = st.multiselect("Select crimes to compare",
                              list(CRIME_MAP.keys()),
                              default=list(CRIME_MAP.keys())[:6])

    d_comp = delhi_df[
        delhi_df["Crime_Head"].isin(selected) &
        delhi_df["Year"].between(*year_range)
    ].copy()
    d_comp["State"] = "Delhi"
    d_comp["Mapped"] = d_comp["Crime_Head"].map(CRIME_MAP)

    k_comp = kerala_df[
        kerala_df["Crime_Head"].isin([CRIME_MAP[s] for s in selected]) &
        kerala_df["Year"].between(*year_range)
    ].copy()
    k_comp["State"] = "Kerala"
    k_comp["Mapped"] = k_comp["Crime_Head"]

    combined = pd.concat([
        d_comp[["Year","Mapped","Count","State"]],
        k_comp[["Year","Mapped","Count","State"]]
    ], ignore_index=True)

    # ── Grouped bar per crime ──────────────────────────────────────
    st.markdown('<p class="section-header">Total Crimes (Selected Period) — Grouped by Category</p>', unsafe_allow_html=True)
    agg = combined.groupby(["Mapped","State"])["Count"].sum().reset_index()
    fig = px.bar(agg, x="Mapped", y="Count", color="State", barmode="group",
                 color_discrete_map={"Delhi":"#c084fc","Kerala":"#50c8f0"})
    fig.update_layout(PLOTLY_TEMPLATE["layout"], height=420,
                      xaxis_title="Crime Category", yaxis_title="Total Cases",
                      legend_title="State")
    st.plotly_chart(fig, use_container_width=True)

    # ── Year-wise dual line per crime ──────────────────────────────
    st.markdown('<p class="section-header">Year-wise Trends per Crime Category</p>', unsafe_allow_html=True)
    crimes_to_show = combined["Mapped"].unique()
    n = len(crimes_to_show)
    cols_per_row = 2
    rows = (n + cols_per_row - 1) // cols_per_row

    for i in range(0, n, cols_per_row):
        cols = st.columns(cols_per_row)
        for j, crime in enumerate(crimes_to_show[i:i+cols_per_row]):
            with cols[j]:
                sub = combined[combined["Mapped"] == crime]
                fig2 = px.line(sub, x="Year", y="Count", color="State", markers=True,
                               color_discrete_map={"Delhi":"#c084fc","Kerala":"#50c8f0"},
                               title=crime)
                fig2.update_layout(PLOTLY_TEMPLATE["layout"], height=280,
                                   showlegend=True, margin=dict(l=30,r=10,t=40,b=30),
                                   legend=dict(font=dict(size=10), orientation="h", y=1.15))
                st.plotly_chart(fig2, use_container_width=True)

    # ── Summary table ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<p class="section-header">Summary Table</p>', unsafe_allow_html=True)
    table = agg.pivot(index="Mapped", columns="State", values="Count").fillna(0).astype(int)
    if "Delhi" in table.columns and "Kerala" in table.columns:
        table["Ratio (D/K)"] = (table["Delhi"] / table["Kerala"].replace(0, np.nan)).round(2)
    table = table.sort_values("Delhi", ascending=False) if "Delhi" in table.columns else table
    st.dataframe(table.style.background_gradient(cmap="Purples", subset=["Delhi"] if "Delhi" in table.columns else [])
                             .background_gradient(cmap="Blues",   subset=["Kerala"] if "Kerala" in table.columns else [])
                             .format("{:,}", subset=["Delhi","Kerala"] if all(c in table.columns for c in ["Delhi","Kerala"]) else []),
                 use_container_width=True)
