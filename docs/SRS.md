# Software Requirements Specification (SRS) - NCRB Crime Analysis Web Frontend

## Version 1.0 · June 2025

### 2.1 Introduction

#### 2.1.1 Purpose
This document specifies the functional and non-functional requirements for the **web-based frontend** of the NCRB Crime Analysis platform. The frontend replaces the existing Tkinter desktop GUI and Streamlit prototype with a production-grade, responsive web application for visualizing and analyzing crime records data from Delhi (2001–2021) and Kerala (2016–2021).

#### 2.1.2 Scope
The system will provide:
- An interactive crime data dashboard with filterable charts
- Statistical analysis panels (mean, median, CAGR, anomaly detection)
- A crime prediction/forecasting module with visual output
- Data export capabilities (CSV, PNG)
- Responsive design for desktop and tablet viewports

#### 2.1.3 Intended Audience
| Audience | Use |
|----------|-----|
| Developers | Implementation reference |
| UI/UX Designers | Component & interaction specs |
| Project Evaluators (UPES) | Academic assessment |
| End Users | Researchers, journalists, policy students |

#### 2.1.4 Tech Stack (Recommended)

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Framework | **Next.js 14** or **React 18** | SSR for SEO, component model |
| Styling | **Tailwind CSS** | Utility-first, matches our palette system |
| Charts | **Recharts** or **Chart.js** | React-native, good for crime line/bar/pie |
| State | **Zustand** or React Context | Lightweight, sufficient for dashboard state |
| Data | **Static JSON** (pre-processed from CSV) | No backend needed; CSVs converted at build time |
| Export | **html2canvas** + **FileSaver.js** | Client-side PNG/CSV export |
| Deployment | **Vercel** | Free tier, instant deploys from GitHub |

---

### 2.2 Overall Description

#### 2.2.1 System Architecture

```
┌──────────────────────────────────────────────────────┐
│                    USER (Browser)                      │
├──────────────────────────────────────────────────────┤
│                                                        │
│  ┌─────────┐  ┌──────────┐  ┌────────────────────┐   │
│  │ Sidebar  │  │ Dashboard │  │  Detail/Predict    │   │
│  │ Nav +    │  │ Grid of   │  │  Panel             │   │
│  │ Filters  │  │ Stat Cards│  │  (Charts + Stats)  │   │
│  │          │  │ + Charts  │  │                    │   │
│  └─────────┘  └──────────┘  └────────────────────┘   │
│                                                        │
├──────────────────────────────────────────────────────┤
│               DATA LAYER (Static JSON)                 │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────────┐  │
│  │ delhi.json   │ │ kerala.json  │ │ pocso.json    │  │
│  └─────────────┘ └──────────────┘ └───────────────┘  │
└──────────────────────────────────────────────────────┘
```

#### 2.2.2 User Classes

| User Class | Description | Access Level |
|-----------|-------------|-------------|
| General Visitor | Browses charts, reads stats | Read-only |
| Researcher | Uses filters, exports data, runs predictions | Read + Export |

#### 2.2.3 Design Constraints
- No authentication required (public data)
- No backend server (all processing client-side or at build time)
- Must work on Chrome, Firefox, Edge (latest 2 versions)
- Minimum viewport: 768px (tablet). Mobile is secondary.

---

### 2.3 Functional Requirements

#### FR-01: Navigation & Layout

| ID | Requirement | Priority |
|----|------------|----------|
| FR-01.1 | Collapsible sidebar with region selector (Delhi / Kerala) | HIGH |
| FR-01.2 | Top bar showing current region, year range, and active filters | HIGH |
| FR-01.3 | Dark theme by default using the defined neutral palette | HIGH |
| FR-01.4 | Optional light theme toggle | LOW |
| FR-01.5 | Responsive grid layout: sidebar collapses to hamburger on tablet | MEDIUM |

#### FR-02: Dashboard Overview Page

| ID | Requirement | Priority |
|----|------------|----------|
| FR-02.1 | Display 4 summary stat cards: Total Cases, Peak Year, Average/Year, YoY Change | HIGH |
| FR-02.2 | Stat cards use semantic colors: red for increase, green for decrease | HIGH |
| FR-02.3 | Primary chart area: Line chart of top 5 crime categories over time | HIGH |
| FR-02.4 | Secondary chart area: Horizontal bar chart of latest year snapshot | HIGH |
| FR-02.5 | All charts animate on load (fade-in + draw) | MEDIUM |
| FR-02.6 | Hover tooltip on all charts showing exact value + year | HIGH |

#### FR-03: Filtering & Search

| ID | Requirement | Priority |
|----|------------|----------|
| FR-03.1 | Live search input to filter crime categories (debounced, 200ms) | HIGH |
| FR-03.2 | Multi-select dropdown for crime categories | HIGH |
| FR-03.3 | Year range slider (min–max from dataset) | HIGH |
| FR-03.4 | District selector (Kerala POCSO data only) | MEDIUM |
| FR-03.5 | "Reset Filters" button restores defaults | MEDIUM |
| FR-03.6 | Active filter pills shown below the search bar | LOW |

#### FR-04: Detailed Analysis Panel

| ID | Requirement | Priority |
|----|------------|----------|
| FR-04.1 | Click any crime category to open a detail panel | HIGH |
| FR-04.2 | Detail panel shows: line chart, stats table, anomaly markers | HIGH |
| FR-04.3 | Stats table includes: Total, Mean, Median, Std Dev, Min, Max, CAGR | HIGH |
| FR-04.4 | Anomaly detection: highlight years where value > 1.5σ from mean | HIGH |
| FR-04.5 | Anomaly markers shown as red dots on the line chart | MEDIUM |

#### FR-05: Crime Prediction / Forecasting

| ID | Requirement | Priority |
|----|------------|----------|
| FR-05.1 | "Predict" button generates a 3-year linear regression forecast | HIGH |
| FR-05.2 | Forecast line shown as dashed extension on the chart | HIGH |
| FR-05.3 | Confidence interval shaded band (±1σ) around forecast | MEDIUM |
| FR-05.4 | Predicted values displayed in a card below the chart | HIGH |
| FR-05.5 | Disclaimer text: "Based on linear regression. Not a definitive prediction." | HIGH |

#### FR-06: Chart Types Page

| ID | Requirement | Priority |
|----|------------|----------|
| FR-06.1 | Dedicated page reproducing all 9 original charts from `project.py` | HIGH |
| FR-06.2 | Each chart is interactive (hover, zoom on click) | MEDIUM |
| FR-06.3 | Chart descriptions/captions below each visualization | HIGH |
| FR-06.4 | Grid layout: 2 columns on desktop, 1 column on tablet | MEDIUM |

#### FR-07: Data Export

| ID | Requirement | Priority |
|----|------------|----------|
| FR-07.1 | "Export CSV" button downloads filtered data as `.csv` | HIGH |
| FR-07.2 | "Export PNG" button saves current chart as image | MEDIUM |
| FR-07.3 | Exported CSV includes metadata header (region, date, filters) | LOW |

#### FR-08: Comparison View

| ID | Requirement | Priority |
|----|------------|----------|
| FR-08.1 | Side-by-side chart comparing Delhi vs Kerala for overlapping years (2016–2021) | HIGH |
| FR-08.2 | Synchronized tooltip: hovering one chart highlights the same year on both | MEDIUM |
| FR-08.3 | Comparison stat cards showing which region has higher rate | MEDIUM |

---

### 2.4 Non-Functional Requirements

#### NFR-01: Performance

| ID | Requirement | Target |
|----|------------|--------|
| NFR-01.1 | First Contentful Paint (FCP) | < 1.5s |
| NFR-01.2 | Time to Interactive (TTI) | < 3.0s |
| NFR-01.3 | Chart render after filter change | < 300ms |
| NFR-01.4 | Bundle size (gzipped) | < 500KB |
| NFR-01.5 | Lighthouse Performance score | > 90 |

#### NFR-02: Accessibility

| ID | Requirement |
|----|------------|
| NFR-02.1 | WCAG 2.1 AA contrast ratios on all text (verified with palette above) |
| NFR-02.2 | All charts have `aria-label` descriptions |
| NFR-02.3 | Keyboard navigable: Tab through filters, Enter to select |
| NFR-02.4 | Screen reader support for stat cards |

#### NFR-03: Maintainability

| ID | Requirement |
|----|------------|
| NFR-03.1 | Component-based architecture (1 component = 1 file) |
| NFR-03.2 | All colors referenced via CSS variables / Tailwind config (no hardcoded hex) |
| NFR-03.3 | Data layer abstracted: swap JSON source without touching UI components |
| NFR-03.4 | ESLint + Prettier configured |

---

### 2.5 Page & Component Breakdown

```
src/
├── app/
│   ├── layout.tsx              # Root layout (sidebar + top bar)
│   ├── page.tsx                # Dashboard overview (FR-02)
│   ├── charts/
│   │   └── page.tsx            # All 9 charts gallery (FR-06)
│   ├── analysis/
│   │   └── page.tsx            # Detail + Prediction panel (FR-04, FR-05)
│   └── compare/
│       └── page.tsx            # Delhi vs Kerala comparison (FR-08)
│
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx         # Region selector, nav links, filters
│   │   ├── TopBar.tsx          # Breadcrumb, active filters, theme toggle
│   │   └── Footer.tsx          # Data source attribution
│   │
│   ├── dashboard/
│   │   ├── StatCard.tsx        # Single stat card (value, label, trend arrow)
│   │   ├── StatCardGrid.tsx    # 4-card grid layout
│   │   └── QuickInsight.tsx    # Text blurb: "Theft increased 12% since 2019"
│   │
│   ├── charts/
│   │   ├── LineChart.tsx       # Reusable line chart wrapper
│   │   ├── BarChart.tsx        # Horizontal + vertical bar
│   │   ├── PieChart.tsx        # Pie / donut
│   │   ├── HeatmapChart.tsx    # District × year heatmap
│   │   ├── AreaChart.tsx       # Stacked area
│   │   ├── HistogramChart.tsx  # Distribution histogram
│   │   ├── ForecastOverlay.tsx # Dashed line + confidence band
│   │   └── AnomalyMarker.tsx   # Red dot + tooltip for anomalies
│   │
│   ├── filters/
│   │   ├── SearchInput.tsx     # Live debounced search
│   │   ├── YearSlider.tsx      # Range slider for year filtering
│   │   ├── CategorySelect.tsx  # Multi-select dropdown
│   │   ├── DistrictSelect.tsx  # Kerala district picker
│   │   └── FilterPills.tsx     # Active filter tags
│   │
│   ├── analysis/
│   │   ├── StatsTable.tsx      # Full statistics table
│   │   ├── AnomalyList.tsx     # List of detected anomalies
│   │   └── PredictionCard.tsx  # 3-year forecast display
│   │
│   └── common/
│       ├── ExportButton.tsx    # CSV / PNG export
│       ├── Tooltip.tsx         # Reusable tooltip
│       ├── Badge.tsx           # Colored label (e.g., "HIGH", "Spike")
│       └── EmptyState.tsx      # "No data matches filters" display
│
├── data/
│   ├── delhi.json              # Pre-processed from CSV
│   ├── kerala.json
│   └── pocso.json
│
├── lib/
│   ├── statistics.ts           # Mean, median, stddev, CAGR calculations
│   ├── forecast.ts             # Linear regression logic
│   ├── anomaly.ts              # Anomaly detection (1.5σ rule)
│   └── exportUtils.ts          # CSV generation, canvas-to-PNG
│
├── styles/
│   └── globals.css             # CSS variables, base styles
│
└── hooks/
    ├── useFilteredData.ts      # Central filter state + derived data
    └── useDebounce.ts          # Debounce hook for search
```

---

### 2.6 Wireframe Descriptions

#### Dashboard Page (Desktop — 1440px)
```
┌──────────────────────────────────────────────────────────────┐
│ [☰] NCRB Crime Analysis          Delhi ▾  │ 2001-2021 │ 🌙  │
├────────┬─────────────────────────────────────────────────────┤
│        │                                                      │
│  NAV   │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐              │
│        │  │12,847│ │ 2019 │ │  612 │ │+3.2% │              │
│  🏠 Dash│  │Total │ │ Peak │ │ Avg  │ │ YoY  │              │
│  📊 Charts│ └──────┘ └──────┘ └──────┘ └──────┘              │
│  🔬 Analysis│                                                 │
│  ⚖️ Compare│ ┌────────────────────────────────────────┐      │
│        │  │                                            │      │
│ ──────── │  │         LINE CHART                       │      │
│ FILTERS│  │     Top 5 Crime Trends Over Time          │      │
│        │  │                                            │      │
│ 🔍 Search│  └────────────────────────────────────────┘      │
│ Category│                                                     │
│ [Multi] │  ┌───────────────────┐ ┌───────────────────┐      │
│ Year    │  │                   │ │                   │      │
│ ├──●──┤ │  │  BAR CHART 2021  │ │  PIE CHART 2021  │      │
│        │  │                   │ │                   │      │
│ [Reset]│  └───────────────────┘ └───────────────────┘      │
│        │                                                      │
├────────┴─────────────────────────────────────────────────────┤
│  Data: NCRB  │  Built by Kushagra Kedia  │  UPES · 2025     │
└──────────────────────────────────────────────────────────────┘
```

#### Analysis Page (with Prediction)
```
┌──────────────────────────────────────────────────────────────┐
│ [☰] NCRB Crime Analysis    Analysis > Theft    │ Export ▾    │
├────────┬─────────────────────────────────────────────────────┤
│        │                                                      │
│  NAV   │  ┌──────────────────────────────────────────────┐   │
│        │  │                                              │   │
│        │  │   LINE CHART + FORECAST                      │   │
│        │  │   ─── Actual    ╌╌╌ Predicted               │   │
│        │  │   🔴 Anomaly markers                         │   │
│        │  │   ░░ Confidence interval                     │   │
│        │  │                                              │   │
│        │  └──────────────────────────────────────────────┘   │
│        │                                                      │
│        │  ┌─────── STATS ────────┐ ┌──── ANOMALIES ─────┐   │
│        │  │ Total    │   8,432   │ │ ⚠ 2020 — Spike     │   │
│        │  │ Mean     │     401   │ │   1,247 (2.1σ)     │   │
│        │  │ Median   │     389   │ │ ⚠ 2005 — Drop      │   │
│        │  │ Std Dev  │      87   │ │   203 (−1.8σ)      │   │
│        │  │ CAGR     │   +2.1%   │ │                     │   │
│        │  └──────────────────────┘ └─────────────────────┘   │
│        │                                                      │
│        │  ┌────────── FORECAST ──────────┐                   │
│        │  │ 2022: ~634  │ 2023: ~651     │                   │
│        │  │ 2024: ~668  │                │                   │
│        │  │ ⓘ Linear regression estimate │                   │
│        │  └──────────────────────────────┘                   │
└────────┴─────────────────────────────────────────────────────┘
```

---

### 2.7 Acceptance Criteria

| # | Criteria | Verification |
|---|---------|-------------|
| AC-01 | Dashboard loads and shows stat cards within 2s | Lighthouse audit |
| AC-02 | Selecting "Kerala" swaps all data and charts | Manual test |
| AC-03 | Search input filters categories with <200ms perceived lag | Manual test |
| AC-04 | Anomalies are correctly flagged (values > mean ± 1.5σ) | Unit test against known data |
| AC-05 | Forecast values match Python `numpy.polyfit` output (±1% tolerance) | Cross-validation with `gui.py` |
| AC-06 | Exported CSV opens correctly in Excel with proper headers | Manual test |
| AC-07 | All text passes WCAG AA contrast ratio (4.5:1 for normal, 3:1 for large) | Contrast checker tool |
| AC-08 | Works on Chrome, Firefox, Edge (latest 2 versions) | Cross-browser test |

---

### 2.8 Milestones

| Phase | Deliverables | Duration |
|-------|-------------|----------|
| **M1: Foundation** | Project setup, palette/theme system, layout shell, sidebar, routing | 3 days |
| **M2: Data Layer** | CSV → JSON pipeline, filter hooks, statistics/forecast utilities | 2 days |
| **M3: Dashboard** | Stat cards, primary line chart, bar chart, all with filters | 4 days |
| **M4: Analysis** | Detail panel, stats table, anomaly detection, prediction UI | 4 days |
| **M5: Charts Gallery** | All 9 chart types ported to Recharts, interactive tooltips | 3 days |
| **M6: Comparison** | Delhi vs Kerala side-by-side, synced tooltips | 2 days |
| **M7: Polish** | Animations, export, accessibility audit, performance optimization | 3 days |
| **Total** | | **~3 weeks** |
