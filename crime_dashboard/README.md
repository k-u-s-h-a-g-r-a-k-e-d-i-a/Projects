# 🔍 India Crime Analytics Dashboard

An interactive Streamlit dashboard analyzing NCRB crime data for **Delhi** (2001–2022) and **Kerala** (2016–2022).

## 📁 File Structure

```
crime_dashboard/
├── app.py
├── requirements.txt
├── README.md
├── Delhi_crime_records.csv
├── kerala_criminal_cases__-_crimes__accidents.csv
└── kerala_criminal_cases__-_POSCO_ACTS_district_wise_.csv
```

> ⚠️ Place all 3 CSV files in the **same folder** as `app.py`.

---

## 🚀 Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the dashboard
streamlit run app.py
```

The app opens at `http://localhost:8501`

---

## 📊 Features

| Page | What You Get |
|------|-------------|
| **Overview** | KPI cards, annual trend lines, top crime category charts for both states |
| **Delhi** | Year-range filter, crime selector, multi-line trends, pie chart, stacked bar, heatmap |
| **Kerala** | Crime trends, POSCO district breakdown, top districts trend, crime treemap |
| **Comparison** | Delhi vs Kerala grouped bar, side-by-side line charts per crime, summary table with ratio |

---

## 📦 Libraries Used

- `streamlit` — web dashboard framework  
- `plotly` — interactive charts (line, bar, pie, heatmap, treemap)  
- `pandas` — data loading and manipulation  
- `numpy` — numerical operations  

---

## 🗂️ Data Sources

- **Delhi**: NCRB crime head data, 2001–Aug 2022
- **Kerala**: NCRB crime category data, 2016–Aug 2022
- **Kerala POSCO**: District-wise POSCO Act cases, 2016–Aug 2022
