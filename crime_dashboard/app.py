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
    /* ── NCRB NEUTRAL DARK PALETTE ── */
    :root {
        --midnight:   #0F1117;
        --charcoal:   #161B22;
        --slate:      #1C2333;
        --graphite:   #242C3A;
        --storm:      #2D3748;
        --silver:     #E2E8F0;
        --ash:        #A0AEC0;
        --pewter:     #718096;
        --smoke:      #4A5568;
        --alert:      #E53E3E;
        --caution:    #ED8936;
        --safe:       #48BB78;
        --intel:      #4299E1;
        --forensic:   #9F7AEA;
    }

    /* Main background */
    .stApp { 
        background: radial-gradient(circle at top right, #1C2333 0%, #0F1117 100%);
        color: #E2E8F0; 
    }
    section[data-testid="stSidebar"] { 
        background-color: #161B22; 
        border-right: 1px solid rgba(226, 232, 240, 0.05); 
    }

    /* KPI Cards - Glassmorphism */
    .kpi-card {
        background: rgba(22, 27, 34, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(226, 232, 240, 0.1);
        border-radius: 20px;
        padding: 32px 24px;
        text-align: center;
        margin-bottom: 16px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 4px;
        background: linear-gradient(90deg, transparent, var(--accent-color), transparent);
        opacity: 0.5;
    }
    .kpi-card:hover { 
        transform: translateY(-8px); 
        border-color: var(--accent-color);
        box-shadow: 0 12px 30px rgba(0,0,0,0.4);
        background: rgba(28, 35, 51, 0.8);
    }
    .kpi-value  { 
        font-size: 2.5rem; font-weight: 900; margin: 0; 
        font-family: 'JetBrains Mono', monospace;
        background: linear-gradient(135deg, #fff 30%, var(--accent-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .kpi-label  { 
        font-size: 0.7rem; color: #A0AEC0; margin-top: 10px; 
        letter-spacing: 0.15em; text-transform: uppercase; 
        font-weight: 700; opacity: 0.8;
    }
    .kpi-icon {
        font-size: 1.5rem;
        margin-bottom: 15px;
        opacity: 0.9;
    }
    .kpi-delta  { 
        font-size: 0.8rem; margin-top: 12px; 
        font-weight: 700; border-radius: 20px;
        padding: 4px 12px; display: inline-block;
        background: rgba(0,0,0,0.2);
    }
    .kpi-up     { color: #E53E3E; border: 1px solid rgba(229, 62, 62, 0.2); }
    .kpi-down   { color: #48BB78; border: 1px solid rgba(72, 187, 120, 0.2); }

    /* Section headers */
    .section-header {
        font-size: 0.95rem; font-weight: 800;
        color: #A0AEC0;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        margin: 40px 0 20px 0;
        display: flex;
        align-items: center;
    }
    .section-header::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, #2D3748, transparent);
        margin-left: 20px;
    }

    /* Search Bar Styling */
    .search-container {
        background: rgba(22, 27, 34, 0.6);
        backdrop-filter: blur(8px);
        border: 1px solid #2D3748;
        border-radius: 16px;
        padding: 16px 24px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }

    /* Prediction Card */
    .prediction-card {
        background: linear-gradient(135deg, #1C2333 0%, #161B22 100%);
        border-radius: 16px;
        padding: 24px;
        border-top: 4px solid #9F7AEA;
    }
</style>
""", unsafe_allow_html=True)

PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(22,27,34,0.4)",
        font=dict(color="#E2E8F0", family="'Inter', sans-serif"),
        xaxis=dict(gridcolor="#2D3748", linecolor="#2D3748", zerolinecolor="#2D3748"),
        yaxis=dict(gridcolor="#2D3748", linecolor="#2D3748", zerolinecolor="#2D3748"),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#2D3748"),
        margin=dict(l=40, r=20, t=40, b=40),
        colorway=["#4299E1","#9F7AEA","#ED8936","#E53E3E","#48BB78","#63B3ED","#F6AD55"],
    )
)
COLORS = ["#4299E1","#9F7AEA","#ED8936","#E53E3E","#48BB78","#63B3ED","#F6AD55","#CBD5E0",
          "#A0AEC0","#718096","#4A5568","#2D3748","#1C2333","#161B22","#0F1117"]

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

# ─────────────────────────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────────────────────────
if "search_q" not in st.session_state:
    st.session_state.search_q = ""
if "page" not in st.session_state:
    st.session_state.page = "📊 Overview"

# ─────────────────────────────────────────────────────────────────
# GLOBAL SEARCH LOGIC (Vectorized & Session Persistent)
# ─────────────────────────────────────────────────────────────────
st.write("") # Spacer

def clear_search():
    st.session_state.search_q = ""
    st.rerun()

# Modern Header Container
with st.container():
    c1, c2, c3 = st.columns([0.1, 3, 1])
    with c2:
        search_query = st.text_input(
            "🔍", 
            placeholder="Search categories, crimes, or districts...", 
            label_visibility="collapsed",
            key="search_q"
        )
    with c3:
        if search_query:
            st.button("✖ Clear Search", on_click=clear_search)

if search_query:
    # Vectorized filtering for all datasets
    delhi_query_mask = delhi_df["Crime_Head"].str.contains(search_query, case=False, na=False)
    kerala_query_mask = kerala_df["Crime_Head"].str.contains(search_query, case=False, na=False)
    posco_query_mask = posco_df["District"].str.contains(search_query, case=False, na=False)

    delhi_filt_df = delhi_df[delhi_query_mask]
    kerala_filt_df = kerala_df[kerala_query_mask]
    posco_filt_df = posco_df[posco_query_mask]
    
    # Update global references
    delhi_df = delhi_filt_df
    kerala_df = kerala_filt_df
    posco_df = posco_filt_df
    
    # Also filter raw data
    delhi_raw = delhi_raw[delhi_raw["Crime_Head"].str.contains(search_query, case=False, na=False)]
    kerala_raw = kerala_raw[kerala_raw["Crime_Head"].str.contains(search_query, case=False, na=False)]
    posco_raw = posco_raw[posco_raw["District"].str.contains(search_query, case=False, na=False)]

    # Result count indicator
    d_matches = list(delhi_df["Crime_Head"].unique())
    k_matches = list(kerala_df["Crime_Head"].unique())
    total_matches = len(d_matches) + len(k_matches)

    if total_matches > 0:
        with st.expander(f"✨ Found **{total_matches}** categories matching **'{search_query}'**. Click to preview details.", expanded=True):
            st.markdown("### 🗺️ Quick Navigation & Preview")
            col_d, col_k = st.columns(2)
            
            with col_d:
                if d_matches:
                    st.success(f"🏙️ Delhi: {len(d_matches)} matches")
                    if st.button("Jump to Delhi Results", key="goto_delhi"):
                        st.session_state.page = "🏙️ Delhi"
                        st.rerun()
                    st.write(", ".join(d_matches[:5]) + ("..." if len(d_matches) > 5 else ""))
                else:
                    st.info("🏙️ Delhi: 0 matches")

            with col_k:
                if k_matches:
                    st.success(f"🌴 Kerala: {len(k_matches)} matches")
                    if st.button("Jump to Kerala Results", key="goto_kerala"):
                        st.session_state.page = "🌴 Kerala"
                        st.rerun()
                    st.write(", ".join(k_matches[:5]) + ("..." if len(k_matches) > 5 else ""))
                else:
                    st.info("🌴 Kerala: 0 matches")
    else:
        st.warning(f"🚫 No categories found matching **'{search_query}'**. Try a different keyword.")
        st.stop()

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
    st.markdown("## 📊 Navigation")
    st.markdown("---")

    # Map current session state page to index
    page_options = ["📊 Overview", "🏙️ Delhi", "🌴 Kerala", "🔬 Detailed Analysis", "⚔️ Comparison"]
    try:
        page_index = page_options.index(st.session_state.page)
    except ValueError:
        page_index = 0

    page = st.radio(
        "Navigate to", 
        page_options,
        index=page_index,
        key="nav_radio"
    )
    st.session_state.page = page

    if st.button("🔄 Reset All Filters"):
        st.session_state.search_q = ""
        st.session_state.page = "📊 Overview"
        st.rerun()

    st.markdown("---")

    # Year range for Delhi
    delhi_years = sorted(delhi_df["Year"].unique()) if not delhi_df.empty else [2001, 2021]
    kerala_years = sorted(kerala_df["Year"].unique()) if not kerala_df.empty else [2016, 2021]

    if page == "🏙️ Delhi":
        year_range = st.slider("📅 Year Range", min_value=delhi_years[0], max_value=delhi_years[-1],
                               value=(delhi_years[0], delhi_years[-1]))
        crime_heads = sorted(delhi_df["Crime_Head"].unique())
        crime_sel = st.multiselect("📂 Crime Categories",
                                    crime_heads,
                                    default=crime_heads[:10]) # Default to first 10 for performance

    elif page == "🌴 Kerala":
        year_range = st.slider("📅 Year Range", min_value=kerala_years[0], max_value=kerala_years[-1],
                               value=(kerala_years[0], kerala_years[-1]))

        crime_heads = sorted(kerala_df["Crime_Head"].unique())
        # Filter core crimes to only those that exist in current filtered set
        core_crimes = ["Murder","Rape","Kidnapping & abduction","Dacoity","Robbery",
                       "Burglary","Theft","Riots","Hurt","Cheating","Molestation",
                       "Cyber Cases","Missing Cases","Cruelty by husband or relatives",
                       "NDPS Act","POSCO Acts"]
        available_core = [c for c in core_crimes if c in crime_heads]
        
        crime_sel = st.multiselect("📂 Crime Categories",
                                    crime_heads,
                                    default=available_core if available_core else crime_heads[:10])

    elif page == "🔬 Detailed Analysis":
        region = st.selectbox("🌎 Select Region", ["Delhi", "Kerala"])
        if region == "Delhi":
            cat_options = sorted(delhi_df["Crime_Head"].unique())
        else:
            cat_options = sorted(kerala_df["Crime_Head"].unique())
        
        target_cat = st.selectbox("🔍 Select Crime Category for Analysis", cat_options)
        predict_btn = st.checkbox("🔮 Show 3-Year Forecast", value=True)

    elif page == "⚔️ Comparison":
        overlap = sorted(set(delhi_years) & set(kerala_years))
        if not overlap:
            st.error("No overlapping years found for these filters.")
            st.stop()
        year_range = st.slider("📅 Year Range", min_value=overlap[0], max_value=overlap[-1],
                               value=(overlap[0], overlap[-1]))

    st.markdown("---")
    
    # ── Export System ──────────────────────────────────────────
    st.markdown("### 📤 Export Data")
    # Determine export source
    if page == "🏙️ Delhi":
        export_df = delhi_df[(delhi_df["Year"].between(*year_range)) & (delhi_df["Crime_Head"].isin(crime_sel))]
        filename = f"delhi_crime_{year_range[0]}_{year_range[1]}.csv"
    elif page == "🌴 Kerala":
        export_df = kerala_df[(kerala_df["Year"].between(*year_range)) & (kerala_df["Crime_Head"].isin(crime_sel))]
        filename = f"kerala_crime_{year_range[0]}_{year_range[1]}.csv"
    elif page == "🔬 Detailed Analysis":
        if region == "Delhi":
            export_df = delhi_df[delhi_df["Crime_Head"] == target_cat]
        else:
            export_df = kerala_df[kerala_df["Crime_Head"] == target_cat]
        filename = f"{target_cat.lower().replace(' ', '_')}_analysis.csv"
    else:
        export_df = None

    if export_df is not None and not export_df.empty:
        csv = export_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Download Filtered CSV",
            data=csv,
            file_name=filename,
            mime='text/csv',
        )

    st.markdown("---")
    st.markdown("<small style='color:#555'>Data: NCRB | Delhi 2001–2022 | Kerala 2016–2022</small>",
                unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.markdown("# 📊 India Crime Analytics Dashboard")
    if search_query:
        st.markdown(f"Filtering view by: `{search_query}`")
    else:
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
        st.markdown(f"""<div class="kpi-card" style="--accent-color: #9F7AEA">
            <div class="kpi-icon">🏛️</div>
            <p class="kpi-value">{fmt(delhi_total)}</p>
            <p class="kpi-label">Delhi Cumulative</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        arr, cls = ("↑", "kpi-up") if d_delta > 0 else ("↓", "kpi-down")
        st.markdown(f"""<div class="kpi-card" style="--accent-color: #E53E3E">
            <div class="kpi-icon">🏙️</div>
            <p class="kpi-value">{fmt(delhi_latest)}</p>
            <p class="kpi-label">Delhi (2021)</p>
            <p class="kpi-delta {cls}">{arr} {abs(d_delta):.1f}% YoY</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card" style="--accent-color: #4299E1">
            <div class="kpi-icon">🌴</div>
            <p class="kpi-value">{fmt(kerala_total)}</p>
            <p class="kpi-label">Kerala Cumulative</p>
        </div>""", unsafe_allow_html=True)
    with c4:
        arr, cls = ("↑", "kpi-up") if k_delta > 0 else ("↓", "kpi-down")
        st.markdown(f"""<div class="kpi-card" style="--accent-color: #48BB78">
            <div class="kpi-icon">🌊</div>
            <p class="kpi-value">{fmt(kerala_latest)}</p>
            <p class="kpi-label">Kerala (2021)</p>
            <p class="kpi-delta {cls}">{arr} {abs(k_delta):.1f}% YoY</p>
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
    if search_query:
        st.markdown(f"Filtering view by: `{search_query}`")
    else:
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
    if search_query:
        st.markdown(f"Filtering view by: `{search_query}`")
    else:
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
# PAGE 4 — DETAILED ANALYSIS & PREDICTION
# ═══════════════════════════════════════════════════════════════════
elif page == "🔬 Detailed Analysis":
    st.markdown(f"# 🔬 Analysis: {target_cat}")
    st.markdown(f"In-depth statistical profile and forecasting for **{region}**.")
    st.markdown("---")

    # Filter data for specific category
    if region == "Delhi":
        data = delhi_df[delhi_df["Crime_Head"] == target_cat].sort_values("Year")
    else:
        data = kerala_df[kerala_df["Crime_Head"] == target_cat].sort_values("Year")

    if data.empty:
        st.warning("No data found for this category.")
        st.stop()

    # ── Statistical Calculations ─────────────────────────────────
    counts = data["Count"].values
    years = data["Year"].values
    
    total = np.sum(counts)
    mean = np.mean(counts)
    median = np.median(counts)
    std_dev = np.std(counts)
    mx_val = np.max(counts)
    mx_yr = years[np.argmax(counts)]
    
    # CAGR calculation
    first, last = counts[0], counts[-1]
    n_years = len(years) - 1
    cagr = ((last / first)**(1/n_years) - 1) * 100 if first > 0 and n_years > 0 else 0

    # Anomaly Detection (1.5 Sigma)
    anomalies = data[np.abs(data["Count"] - mean) > 1.5 * std_dev]

    # ── KPI Row ──────────────────────────────────────────────────
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="kpi-card">
            <p class="kpi-value" style="color:#4299E1">{fmt(total)}</p>
            <p class="kpi-label">Cumulative Total</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card">
            <p class="kpi-value" style="color:#48BB78">{fmt(mean)}</p>
            <p class="kpi-label">Average / Year</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        color = "#E53E3E" if cagr > 0 else "#48BB78"
        arr = "↑" if cagr > 0 else "↓"
        st.markdown(f"""<div class="kpi-card">
            <p class="kpi-value" style="color:{color}">{arr}{abs(cagr):.1f}%</p>
            <p class="kpi-label">CAGR (Growth Rate)</p>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="kpi-card">
            <p class="kpi-value" style="color:#ED8936">{fmt(std_dev)}</p>
            <p class="kpi-label">Volatility (Std Dev)</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Linear Regression Forecasting ────────────────────────────
    fig = go.Figure()

    # Actual Data
    fig.add_trace(go.Scatter(
        x=years, y=counts,
        mode="lines+markers",
        name="Historical Records",
        line=dict(color="#4299E1", width=3),
        marker=dict(size=8)
    ))

    # Anomaly Markers
    if not anomalies.empty:
        fig.add_trace(go.Scatter(
            x=anomalies["Year"], y=anomalies["Count"],
            mode="markers",
            name="Statistical Anomaly",
            marker=dict(color="#E53E3E", size=12, symbol="circle-open", line=dict(width=2)),
            hovertemplate="Anomaly Detected<br>Year: %{x}<br>Value: %{y:,}<extra></extra>"
        ))

    # Forecast
    if predict_btn and len(years) > 2:
        z = np.polyfit(years, counts, 1)
        p = np.poly1d(z)
        
        last_yr = years[-1]
        future_yrs = np.array([last_yr + 1, last_yr + 2, last_yr + 3])
        future_preds = p(future_yrs)
        
        # Connect last actual point to first prediction
        x_pred = np.concatenate([[years[-1]], future_yrs])
        y_pred = np.concatenate([[counts[-1]], future_preds])
        
        # Confidence Band (±1 Std Dev)
        fig.add_trace(go.Scatter(
            x=np.concatenate([x_pred, x_pred[::-1]]),
            y=np.concatenate([y_pred + std_dev, (y_pred - std_dev)[::-1]]),
            fill='toself',
            fillcolor='rgba(159, 122, 234, 0.1)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=True,
            name="Confidence Zone (±1σ)"
        ))

        fig.add_trace(go.Scatter(
            x=x_pred, y=y_pred,
            mode="lines",
            name="Linear Forecast",
            line=dict(color="#9F7AEA", width=3, dash="dash"),
        ))

    fig.update_layout(
        PLOTLY_TEMPLATE["layout"],
        height=500,
        xaxis_title="Year",
        yaxis_title="Case Count",
        hovermode="x unified",
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Details Table ────────────────────────────────────────────
    col_x, col_y = st.columns([2, 1])
    
    with col_x:
        st.markdown('<p class="section-header">Yearly Breakdown & Anomaly Flags</p>', unsafe_allow_html=True)
        display_df = data[["Year", "Count"]].copy()
        display_df["Status"] = "Normal"
        display_df.loc[display_df["Year"].isin(anomalies["Year"]), "Status"] = "⚠️ Anomaly"
        
        st.dataframe(display_df.set_index("Year").style.applymap(
            lambda x: "color: #E53E3E; font-weight: bold" if x == "⚠️ Anomaly" else "",
            subset=["Status"]
        ), use_container_width=True)

    with col_y:
        st.markdown('<p class="section-header">Forecast Insights</p>', unsafe_allow_html=True)
        if predict_btn:
            for y, v in zip(future_yrs, future_preds):
                v_clamped = max(0, int(v))
                st.markdown(f"""
                <div style="background:#1C2333; padding:15px; border-radius:10px; border:1px solid #2D3748; margin-bottom:10px">
                    <span class="prediction-badge">ESTIMATE</span>
                    <h3 style="margin:5px 0; color:#9F7AEA">{y}</h3>
                    <p style="margin:0; font-size:1.4rem; font-weight:700">{fmt(v_clamped)} Cases</p>
                </div>
                """, unsafe_allow_html=True)
            st.info("ℹ️ Predictions based on linear regression of historical records.")
        else:
            st.info("Enable 'Show 3-Year Forecast' in the sidebar to see predictions.")

# ═══════════════════════════════════════════════════════════════════
# PAGE 5 — COMPARISON
# ═══════════════════════════════════════════════════════════════════
elif page == "⚔️ Comparison":
    st.markdown("# ⚔️ Delhi vs Kerala — Comparison")
    if search_query:
        st.markdown(f"Filtering view by: `{search_query}`")
    else:
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
                 color_discrete_map={"Delhi":"#9F7AEA","Kerala":"#4299E1"})
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
                               color_discrete_map={"Delhi":"#9F7AEA","Kerala":"#4299E1"},
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
