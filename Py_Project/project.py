"""
NCRB Crime Analysis — Chart Generator
Datasets: Delhi Crime Records (2001 . 2021) + Kerala Criminal Cases (2016. 2021) + POCSO District-wise
NOTE: 2022 column excluded from all charts (partial year — data only up to Aug 2022)
"""
#imports 
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import os

os.makedirs("figures", exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 150,
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})

C = {
    "blue":   "#2E86AB",
    "red":    "#C73E1D",
    "orange": "#F18F01",
    "green":  "#44BBA4",
    "purple": "#7B2D8B",
    "dark":   "#393E41",
    "pink":   "#A23B72",
    "yellow": "#F5A623",
}

FULL_YEARS = ['2016','2017','2018','2019','2020','2021']

# ── Load Data ──────────────────────────────────────────────────────────────────
delhi  = pd.read_csv('Py_Project4/Delhi crime records.csv', index_col='CRIME HEAD')
kerala = pd.read_csv('Py_Project4/kerala criminal cases  - crimes  accidents.csv')
pocso  = pd.read_csv('Py_Project4/kerala criminal cases  - POSCO ACTS(district wise).csv', index_col='District')

delhi  = delhi.drop(columns=['Aug 2022'], errors='ignore')
kerala = kerala.drop(columns=['2022 (Up to Aug)'], errors='ignore')
pocso  = pocso.drop(columns=['2022 (Up to Aug)'], errors='ignore')

kerala_idx = kerala.set_index('Crime Heads')
kerala_idx = kerala_idx[~kerala_idx.index.duplicated(keep='first')]  # keep first Rape/Molestation (IPC section)
delhi_years = list(delhi.columns)


# ══════════════════════════════════════════════════════════════════════════════
# FIG 1 — Line: Delhi Major Crime Trends (2001–2021)
# ══════════════════════════════════════════════════════════════════════════════
crimes_to_plot = ['MURDER', 'RAPE', 'ROBBERY', 'BURGLARY', 'SNATCHING']
colors_line    = [C['red'], C['purple'], C['orange'], C['blue'], C['green']]

fig, ax = plt.subplots(figsize=(13, 6))
for crime, col in zip(crimes_to_plot, colors_line):
    vals = delhi.loc[crime, delhi_years].astype(int)
    ax.plot(delhi_years, vals, marker='o', markersize=4, linewidth=2,
            label=crime.title(), color=col)

ax.set_title("Delhi — Major Crime Trends (2001–2021)", fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Cases Registered", fontsize=11)
ax.set_xticks(range(0, len(delhi_years), 2))
ax.set_xticklabels(delhi_years[::2], rotation=45, ha='right')
ax.legend(fontsize=9, loc='upper left')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
covid_idx = delhi_years.index('2020')
ax.axvspan(covid_idx - 0.4, covid_idx + 0.4, alpha=0.12, color='gray')
ax.text(covid_idx + 0.5, ax.get_ylim()[1] * 0.88, 'COVID-19', fontsize=8, color='gray')
plt.tight_layout()
plt.savefig("figures/fig1_delhi_crime_trends.png", bbox_inches='tight')
plt.close()
print("✓ fig1 — Delhi major crime trends (line)")


# ══════════════════════════════════════════════════════════════════════════════
# FIG 2 — Horizontal Bar: Delhi Crime Snapshot 2021
# ══════════════════════════════════════════════════════════════════════════════
exclude = ['FATAL ACCIDENT', 'SIMPLE ACCIDENT']
delhi_2021 = delhi['2021'].astype(int).drop(labels=exclude, errors='ignore').sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(10, 7))
bar_colors = [C['red'] if v >= 10000 else C['blue'] for v in delhi_2021.values]
bars = ax.barh(delhi_2021.index, delhi_2021.values, color=bar_colors)
ax.set_title("Delhi — Crime Snapshot (2021)", fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel("Cases Registered", fontsize=11)
for bar, val in zip(bars, delhi_2021.values):
    ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height()/2,
            f'{val:,}', va='center', fontsize=8.5)
ax.set_xlim(0, delhi_2021.max() * 1.18)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
ax.legend(handles=[
    mpatches.Patch(color=C['red'],  label='≥ 10,000 cases'),
    mpatches.Patch(color=C['blue'], label='< 10,000 cases'),
], fontsize=9)
plt.tight_layout()
plt.savefig("figures/fig2_delhi_2021_snapshot.png", bbox_inches='tight')
plt.close()
print("✓ fig2 — Delhi 2021 snapshot (horizontal bar)")


# ══════════════════════════════════════════════════════════════════════════════
# FIG 3 — Histogram: Delhi Theft Categories Distribution (2001–2021)
# ══════════════════════════════════════════════════════════════════════════════
mv_theft    = delhi.loc['M.V.THEFT',   delhi_years].astype(int).values
burglary    = delhi.loc['BURGLARY',    delhi_years].astype(int).values
other_theft = delhi.loc['OTHER THEFT', delhi_years].astype(int).values

fig, axes = plt.subplots(1, 3, figsize=(14, 5))
for ax, data, label, col in zip(axes,
    [mv_theft, burglary, other_theft],
    ['MV Theft', 'Burglary', 'Other Theft'],
    [C['blue'], C['orange'], C['red']]):
    ax.hist(data, bins=8, color=col, edgecolor='white', linewidth=0.8, zorder=3)
    mean_val = np.mean(data)
    ax.axvline(mean_val, color='black', linestyle='--', linewidth=1.5,
               label=f'Mean: {mean_val:,.0f}')
    ax.set_title(f'{label}\n(2001–2021)', fontsize=11, fontweight='bold')
    ax.set_xlabel("Cases per Year", fontsize=10)
    ax.set_ylabel("Frequency",      fontsize=10)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.legend(fontsize=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

fig.suptitle("Delhi — Theft Category Distributions Across Years", fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig("figures/fig3_delhi_theft_histograms.png", bbox_inches='tight')
plt.close()
print("✓ fig3 — Delhi theft histograms")


# ══════════════════════════════════════════════════════════════════════════════
# FIG 4 — Pie: Kerala IPC Crime Composition (2021)
# ══════════════════════════════════════════════════════════════════════════════
ipc_crimes = ['Murder', 'Rape', 'Kidnapping & abduction', 'Dacoity',
              'Robbery', 'Burglary', 'Theft', 'Riots', 'Cheating',
              'Hurt', 'Arson', 'Molestation']
pie_colors = [C['red'], C['purple'], C['orange'], C['dark'], C['blue'],
              C['green'], C['pink'], C['yellow'], C['blue'], C['green'],
              C['orange'], C['red']]

vals_2021 = []
for c in ipc_crimes:
    try:
        vals_2021.append(int(kerala_idx.loc[c, '2021']))
    except:
        vals_2021.append(0)

max_val  = max(vals_2021)
sec_val  = sorted(vals_2021)[-2]
explode  = [0.06 if v in (max_val, sec_val) else 0 for v in vals_2021]

fig, ax = plt.subplots(figsize=(10, 8))
wedges, texts, autotexts = ax.pie(
    vals_2021, labels=ipc_crimes, autopct='%1.1f%%',
    colors=pie_colors, explode=explode, startangle=140,
    wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
    textprops={'fontsize': 8.5}
)
for at in autotexts:
    at.set_fontsize(8)
ax.set_title("Kerala — IPC Crime Composition (2021)\n[Excluding 'Other IPC Crimes']",
             fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig("figures/fig4_kerala_ipc_pie.png", bbox_inches='tight')
plt.close()
print("✓ fig4 — Kerala IPC pie chart")


# ══════════════════════════════════════════════════════════════════════════════
# FIG 5 — Line: Kerala Crimes Against Women (2016–2021)
# ══════════════════════════════════════════════════════════════════════════════
caw_crimes = ['Rape', 'Molestation', 'Sexual harassment',
              'Cruelty by husband or relatives', 'Dowry Deaths(304(B) IPC)']
caw_colors = [C['red'], C['purple'], C['orange'], C['pink'], C['dark']]

fig, ax = plt.subplots(figsize=(11, 6))
for crime, col in zip(caw_crimes, caw_colors):
    try:
        vals = kerala_idx.loc[crime, FULL_YEARS].astype(int)
        ax.plot(FULL_YEARS, vals, marker='o', markersize=6, linewidth=2.2,
                label=crime, color=col)
    except:
        pass

ax.set_title("Kerala — Crimes Against Women (2016–2021)", fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Cases Registered", fontsize=11)
ax.legend(fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.tight_layout()
plt.savefig("figures/fig5_kerala_caw_trends.png", bbox_inches='tight')
plt.close()
print("✓ fig5 — Kerala crimes against women (line)")


# ══════════════════════════════════════════════════════════════════════════════
# FIG 6 — Stacked Bar: Kerala Road Accidents (2016–2021)
# ══════════════════════════════════════════════════════════════════════════════
acc_total    = kerala_idx.loc['No. of accidents',          FULL_YEARS].astype(int)
acc_deaths   = kerala_idx.loc['Death in accidents',        FULL_YEARS].astype(int)
acc_injuries = kerala_idx.loc['Total Injuries in accidents', FULL_YEARS].astype(int)

x = np.arange(len(FULL_YEARS))
fig, ax = plt.subplots(figsize=(11, 6))
ax.bar(x, acc_deaths,   0.55, label='Deaths',   color=C['red'],    zorder=3)
ax.bar(x, acc_injuries, 0.55, bottom=acc_deaths, label='Injuries', color=C['orange'], zorder=3)

for i, (xi, d, inj, tot) in enumerate(zip(x, acc_deaths, acc_injuries, acc_total)):
    ax.text(xi, d + inj + 300, f'Total: {tot:,}', ha='center', fontsize=8, color=C['dark'])

ax.set_title("Kerala — Road Accident Deaths & Injuries (2016–2021)",
             fontsize=15, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(FULL_YEARS, fontsize=10)
ax.set_ylabel("Count", fontsize=11)
ax.legend(fontsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.tight_layout()
plt.savefig("figures/fig6_kerala_accidents_stacked.png", bbox_inches='tight')
plt.close()
print("✓ fig6 — Kerala accidents (stacked bar)")


# ══════════════════════════════════════════════════════════════════════════════
# FIG 7 — Heatmap: POCSO Cases by Kerala District (2016–2021)
# ══════════════════════════════════════════════════════════════════════════════
pocso_data = pocso[FULL_YEARS].astype(int).drop(index='RAILWAY POLICE', errors='ignore')
pocso_data = pocso_data.sort_values('2021', ascending=False)

fig, ax = plt.subplots(figsize=(11, 8))
im = ax.imshow(pocso_data.values, cmap='YlOrRd', aspect='auto')
ax.set_xticks(range(len(FULL_YEARS)))
ax.set_xticklabels(FULL_YEARS, fontsize=10)
ax.set_yticks(range(len(pocso_data.index)))
ax.set_yticklabels(pocso_data.index, fontsize=9)

for i in range(len(pocso_data.index)):
    for j in range(len(FULL_YEARS)):
        val = pocso_data.values[i, j]
        ax.text(j, i, str(val), ha='center', va='center', fontsize=8.5,
                color='white' if val > 300 else 'black', fontweight='bold')

plt.colorbar(im, ax=ax, label='POCSO Cases', shrink=0.8)
ax.set_title("Kerala — POCSO Cases by District (2016–2021)\n[Sorted by 2021 count]",
             fontsize=14, fontweight='bold', pad=15)
ax.spines[:].set_visible(False)
plt.tight_layout()
plt.savefig("figures/fig7_pocso_heatmap.png", bbox_inches='tight')
plt.close()
print("✓ fig7 — POCSO heatmap")


# ══════════════════════════════════════════════════════════════════════════════
# FIG 8 — Grouped Bar: Delhi vs Kerala Common Crime Comparison (2021)
# ══════════════════════════════════════════════════════════════════════════════
common = {
    'Murder':     ('MURDER',         'Murder'),
    'Rape':       ('RAPE',           'Rape'),
    'Robbery':    ('ROBBERY',        'Robbery'),
    'Burglary':   ('BURGLARY',       'Burglary'),
    'Dacoity':    ('DACOITY',        'Dacoity'),
    'Kidnapping': ('OTHER KID./ABD', 'Kidnapping & abduction'),
}
delhi_vals  = [int(delhi.loc[v[0], '2021']) for v in common.values()]
kerala_vals = [int(kerala_idx.loc[v[1], '2021']) for v in common.values()]

x, width = np.arange(len(common)), 0.38
fig, ax = plt.subplots(figsize=(12, 6))
b1 = ax.bar(x - width/2, delhi_vals,  width, label='Delhi',  color=C['blue'],   zorder=3)
b2 = ax.bar(x + width/2, kerala_vals, width, label='Kerala', color=C['orange'], zorder=3)

for bar, col in [(b1, C['blue']), (b2, C['orange'])]:
    for b in bar:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 30,
                f'{int(b.get_height()):,}', ha='center', fontsize=8, color=col)

ax.set_title("Delhi vs Kerala — Crime Comparison (2021)", fontsize=15, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(list(common.keys()), fontsize=10)
ax.set_ylabel("Cases Registered", fontsize=11)
ax.legend(fontsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.tight_layout()
plt.savefig("figures/fig8_delhi_vs_kerala.png", bbox_inches='tight')
plt.close()
print("✓ fig8 — Delhi vs Kerala grouped bar")


# ══════════════════════════════════════════════════════════════════════════════
# FIG 9 — Area Chart: Kerala Cyber Crime & Missing Cases (2016–2021)
# ══════════════════════════════════════════════════════════════════════════════
cyber   = kerala_idx.loc['Cyber Cases',   FULL_YEARS].astype(int)
missing = kerala_idx.loc['Missing Cases', FULL_YEARS].astype(int)

fig, ax = plt.subplots(figsize=(11, 5))
ax.fill_between(FULL_YEARS, cyber,   alpha=0.35, color=C['blue'])
ax.fill_between(FULL_YEARS, missing, alpha=0.35, color=C['red'])
ax.plot(FULL_YEARS, cyber,   marker='o', color=C['blue'],  linewidth=2.2, label='Cyber Cases')
ax.plot(FULL_YEARS, missing, marker='s', color=C['red'],   linewidth=2.2, label='Missing Cases')

for i, (cy, mi) in enumerate(zip(cyber, missing)):
    ax.text(i, int(cy) + 150,  f'{cy:,}', ha='center', fontsize=8.5, color=C['blue'])
    ax.text(i, int(mi) + 150, f'{mi:,}', ha='center', fontsize=8.5, color=C['red'])

ax.set_title("Kerala — Cyber Crime & Missing Cases (2016–2021)",
             fontsize=15, fontweight='bold', pad=15)
ax.set_ylabel("Cases", fontsize=11)
ax.legend(fontsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.tight_layout()
plt.savefig("figures/fig9_kerala_cyber_missing.png", bbox_inches='tight')
plt.close()
print("✓ fig9 — Kerala cyber & missing (area chart)")


print("\n✅ All 9 figures saved to figures/")
print("Upload the figures/ folder to Overleaf alongside main.tex")