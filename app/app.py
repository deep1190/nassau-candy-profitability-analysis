"""
Nassau Candy Distributor — Product Line Profitability & Margin Performance Dashboard
Run with: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ----------------------------------------------------------------------------
# PAGE CONFIG & THEME
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Nassau Candy | Profitability & Margin Analytics",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded",
)

PALETTE = ["#F4A261", "#FF5A79", "#4EA8DE", "#C77D4F", "#06D6A0", "#9B5DE5"]
DIVISION_COLORS = {"Chocolate": "#C77D4F", "Sugar": "#FF5A79", "Other": "#4EA8DE"}

# Dark app background + surface colors reused across every Plotly figure so
# charts never fall back to a white canvas inside the dark shell.
APP_BG = "#0F172A"
SURFACE = "#1E293B"
GRID = "#334155"
TEXT = "#E2E8F0"
MUTED_TEXT = "#94A3B8"

CUSTOM_CSS = f"""
<style>

/* ==========================================================
   IMPORT FONT
========================================================== */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"]{{
    font-family:'Inter',sans-serif;
}}

/* Reset any default link styling so it can never leak through onto
   tabs/nav elements (this is what caused the unstyled red/gray tab text) */
a, a:visited, a:hover, a:active {{
    color: inherit !important;
    text-decoration: none !important;
}}

/* ==========================================================
   PAGE
========================================================== */

.stApp{{
    background:{APP_BG} !important;
    color:{TEXT} !important;
}}

[data-testid="stAppViewContainer"], [data-testid="stHeader"]{{
    background:{APP_BG} !important;
}}

[data-testid="stHeader"]{{
    background:transparent !important;
}}

/* ==========================================================
   SIDEBAR
========================================================== */
section[data-testid="stSidebar"]{{
    background:#020617 !important;
    border-right:1px solid {GRID};
}}

section[data-testid="stSidebar"] *{{
    color:{TEXT} !important;
}}

section[data-testid="stSidebar"] label{{
    color:{MUTED_TEXT} !important;
    font-weight:600;
    font-size:13px;
}}

section[data-testid="stSidebar"] [data-testid="stCaptionContainer"]{{
    color:#64748B !important;
}}

section[data-testid="stSidebar"] hr{{
    border-top:1px solid {GRID} !important;
}}

/* Sidebar inputs need explicit dark surfaces or they render as white boxes */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] [data-baseweb="input"]{{
    background:{SURFACE} !important;
    border:1px solid {GRID} !important;
    color:{TEXT} !important;
}}

section[data-testid="stSidebar"] [data-baseweb="tag"]{{
    background:#2563EB !important;
    color:white !important;
}}

/* ==========================================================
   TITLES
========================================================== */

h1, h2{{
    color:{TEXT} !important;
    font-weight:700 !important;
}}

h3{{
    color:{TEXT} !important;
    font-weight:600 !important;
}}

[data-testid="stHeading"]{{
    color:{TEXT} !important;
}}

p, span, label, .stMarkdown, [data-testid="stCaptionContainer"]{{
    color:{TEXT};
}}

/* ==========================================================
   METRIC CARDS
========================================================== */
div[data-testid="stMetric"]{{
    background:{SURFACE};
    border:1px solid {GRID};
    border-radius:16px;
    padding:14px 16px;
    box-shadow:none;
}}

[data-testid="stMetricLabel"]{{
    color:{MUTED_TEXT} !important;
    white-space:normal !important;
    overflow:visible !important;
    text-overflow:unset !important;
}}

[data-testid="stMetricLabel"] p{{
    white-space:normal !important;
    overflow:visible !important;
    text-overflow:unset !important;
}}

[data-testid="stMetricValue"]{{
    color:#60A5FA !important;
    white-space:normal !important;
    overflow:visible !important;
    text-overflow:unset !important;
    font-size:1.55rem !important;
    line-height:1.25 !important;
    word-break:break-word !important;
}}

[data-testid="stMetricDelta"]{{
    color:#06D6A0 !important;
    white-space:normal !important;
    overflow:visible !important;
    text-overflow:unset !important;
}}

[data-testid="stMetricDelta"] div{{
    white-space:normal !important;
}}

div[data-testid="stMetric"]{{
    min-height:96px;
}}

/* ==========================================================
   TABS  (hardened — highest specificity + !important so the
   dark pill styling always wins, including on narrow viewports)
========================================================== */

.stTabs{{
    margin-top: 10px;
}}

div.stTabs [data-baseweb="tab-list"]{{
    background:{SURFACE} !important;
    padding:8px !important;
    border-radius:14px !important;
    gap:6px !important;
    flex-wrap:nowrap !important;
    overflow-x:auto !important;
    border-bottom:none !important;
}}

div.stTabs [data-baseweb="tab-list"] button[data-baseweb="tab"]{{
    background:transparent !important;
    color:{MUTED_TEXT} !important;
    border-radius:10px !important;
    padding:10px 18px !important;
    font-size:14px !important;
    font-weight:600 !important;
    white-space:nowrap !important;
    transition:all .2s ease !important;
    border:none !important;
}}

div.stTabs [data-baseweb="tab-list"] button[data-baseweb="tab"] p{{
    color:inherit !important;
    font-weight:600 !important;
}}

div.stTabs [data-baseweb="tab-list"] button[data-baseweb="tab"]:hover{{
    background:{GRID} !important;
    color:#FFFFFF !important;
}}

div.stTabs [data-baseweb="tab-list"] button[aria-selected="true"]{{
    background:#2563EB !important;
    color:white !important;
    box-shadow:0 4px 12px rgba(37,99,235,.35) !important;
}}

div.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p{{
    color:white !important;
}}

div.stTabs [data-baseweb="tab-highlight"]{{
    background:transparent !important;
}}

div.stTabs [data-baseweb="tab-border"]{{
    background:transparent !important;
}}

/* ==========================================================
   BUTTONS
========================================================== */

.stButton button{{
    background:#2563EB;
    color:white;
    border:none;
    border-radius:10px;
}}

.stButton button:hover{{
    background:#1D4ED8;
}}

/* ==========================================================
   INPUTS
========================================================== */

.stTextInput input,
.stDateInput input,
.stNumberInput input{{
    border-radius:10px !important;
    border:1px solid {GRID} !important;
    background:{SURFACE} !important;
    color:{TEXT} !important;
}}

.stMultiSelect div[data-baseweb="select"]{{
    border-radius:10px;
}}

/* ==========================================================
   DATAFRAME  (glide-data-grid canvas widget — needs the theme
   set via config.toml; these rules cover the HTML fallback
   tables rendered with .to_html() elsewhere in the app)
========================================================== */
[data-testid="stDataFrame"]{{
    background:{SURFACE};
    border:1px solid {GRID};
    border-radius:12px;
    overflow:hidden;
}}

table{{
    color:{TEXT} !important;
    border-collapse:collapse;
    width:100%;
}}

thead tr{{
    background:{GRID} !important;
}}

thead th{{
    color:white !important;
    padding:8px 10px !important;
}}

tbody tr{{
    background:{SURFACE} !important;
    color:{TEXT} !important;
}}

tbody tr:nth-child(even){{
    background:#243244 !important;
}}

tbody td{{
    padding:8px 10px !important;
    border-top:1px solid {GRID} !important;
}}

/* ==========================================================
   EXPANDERS
========================================================== */

.streamlit-expanderHeader{{
    font-weight:600;
    color:{TEXT} !important;
    background:{SURFACE} !important;
}}

/* ==========================================================
   ALERTS
========================================================== */

div[data-baseweb="notification"]{{
    border-radius:12px;
}}

/* ==========================================================
   RISK BADGES
========================================================== */

.risk-badge-high{{
    background:#450A0A;
    color:#FCA5A5;
    padding:4px 10px;
    border-radius:999px;
    font-weight:600;
    font-size:12px;
}}

.risk-badge-ok{{
    background:#052E16;
    color:#86EFAC;
    padding:4px 10px;
    border-radius:999px;
    font-weight:600;
    font-size:12px;
}}

/* ==========================================================
   HORIZONTAL RULE
========================================================== */

hr{{
    border:none;
    border-top:1px solid {GRID};
}}

/* ==========================================================
   SCROLLBAR
========================================================== */

::-webkit-scrollbar{{
    width:10px;
}}

::-webkit-scrollbar-thumb{{
    background:{GRID};
    border-radius:20px;
}}

::-webkit-scrollbar-thumb:hover{{
    background:{MUTED_TEXT};
}}

</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def style_fig(fig, height=450, legend_top=False):
    """Apply the shared dark theme to every Plotly figure so charts never
    render a white canvas inside the dark app shell."""
    layout_kwargs = dict(
        height=height,
        paper_bgcolor=APP_BG,
        plot_bgcolor=SURFACE,
        font=dict(color=TEXT, family="Inter, sans-serif"),
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID, color=TEXT),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID, color=TEXT),
    )
    if legend_top:
        layout_kwargs["legend"] = dict(orientation="h", y=1.12, font=dict(color=TEXT))
    fig.update_layout(**layout_kwargs)
    # scatter_geo / choropleth figures don't use xaxis/yaxis — harmless if unused
    return fig


FACTORY_COORDS = {
    "Lot's O' Nuts": (32.881893, -111.768036),
    "Wicked Choccy's": (32.076176, -81.088371),
    "Sugar Shack": (48.11914, -96.18115),
    "Secret Factory": (41.446333, -90.565487),
    "The Other Factory": (35.1175, -89.971107),
}

# ----------------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------------
@st.cache_data
def load_data():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "data", "cleaned.csv")
    df = pd.read_csv(path, parse_dates=["Order Date", "Ship Date"])
    return df

df_raw = load_data()

# ----------------------------------------------------------------------------
# SIDEBAR — FILTERS
# ----------------------------------------------------------------------------
st.sidebar.markdown("## 🍬 Nassau Candy")
st.sidebar.caption("Product Line Profitability & Margin Performance Analysis")
st.sidebar.divider()

min_d, max_d = df_raw["Order Date"].min().date(), df_raw["Order Date"].max().date()
date_range = st.sidebar.date_input(
    "Order Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_d, max_d

all_divisions = sorted(df_raw["Division"].unique())
sel_divisions = st.sidebar.multiselect("Division", all_divisions, default=all_divisions)

margin_thresh = st.sidebar.slider(
    "Minimum Gross Margin % (order-level filter)", min_value=0, max_value=100, value=0, step=5
)

search_term = st.sidebar.text_input("🔎 Product Search", placeholder="e.g. Wonka, Gum, Toffee...")

st.sidebar.divider()
st.sidebar.caption("Data: Nassau Candy Distributor order-level dataset, cleaned & validated "
                    f"({len(df_raw):,} orders, {df_raw['Order Date'].min().date()} – {df_raw['Order Date'].max().date()}).")

# ----------------------------------------------------------------------------
# APPLY FILTERS
# ----------------------------------------------------------------------------
mask = (
    (df_raw["Order Date"].dt.date >= start_date)
    & (df_raw["Order Date"].dt.date <= end_date)
    & (df_raw["Division"].isin(sel_divisions))
    & (df_raw["Gross Margin %"] >= margin_thresh)
)
df = df_raw[mask].copy()
if search_term:
    df = df[df["Product Name"].str.contains(search_term, case=False, na=False)]

if df.empty:
    st.warning("No records match the current filters. Please broaden your selection.")
    st.stop()

TOTAL_SALES = df["Sales"].sum()
TOTAL_PROFIT = df["Gross Profit"].sum()
TOTAL_COST = df["Cost"].sum()
TOTAL_UNITS = df["Units"].sum()
OVERALL_MARGIN = TOTAL_PROFIT / TOTAL_SALES * 100 if TOTAL_SALES else 0

# ----------------------------------------------------------------------------
# HEADER + KPI STRIP
# ----------------------------------------------------------------------------
st.title("Product Line Profitability & Margin Performance Analysis")
st.caption("Nassau Candy Distributor — turning sales volume into a true picture of profit.")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Sales", f"${TOTAL_SALES:,.0f}")
k2.metric("Total Gross Profit", f"${TOTAL_PROFIT:,.0f}")
k3.metric("Overall Gross Margin", f"{OVERALL_MARGIN:,.1f}%")
k4.metric("Units Sold", f"{int(TOTAL_UNITS):,}")
k5.metric("Active Products", f"{df['Product Name'].nunique()}")

st.divider()

# ----------------------------------------------------------------------------
# PRODUCT-LEVEL AGGREGATION (used across tabs)
# ----------------------------------------------------------------------------
prod = df.groupby("Product Name").agg(
    Sales=("Sales", "sum"),
    Cost=("Cost", "sum"),
    Gross_Profit=("Gross Profit", "sum"),
    Units=("Units", "sum"),
    Orders=("Order ID", "nunique"),
    Division=("Division", "first"),
    Factory=("Factory", "first"),
).reset_index()
prod["Gross Margin %"] = prod["Gross_Profit"] / prod["Sales"] * 100
prod["Profit per Unit"] = prod["Gross_Profit"] / prod["Units"]
prod["Revenue Contribution %"] = prod["Sales"] / TOTAL_SALES * 100
prod["Profit Contribution %"] = prod["Gross_Profit"] / TOTAL_PROFIT * 100
prod["Cost-to-Sales %"] = prod["Cost"] / prod["Sales"] * 100

sales_med = prod["Sales"].median()
margin_med = prod["Gross Margin %"].median()

def classify(row):
    hs = row["Sales"] >= sales_med
    hm = row["Gross Margin %"] >= margin_med
    if hs and hm: return "⭐ Star (High-Sales / High-Margin)"
    if hs and not hm: return "⚠️ Volume Trap (High-Sales / Low-Margin)"
    if not hs and hm: return "💎 Niche (Low-Sales / High-Margin)"
    return "🚩 Laggard (Low-Sales / Low-Margin)"

prod["Quadrant"] = prod.apply(classify, axis=1)

cost_flag_thresh = prod["Cost-to-Sales %"].median() + prod["Cost-to-Sales %"].std()
prod["Cost Risk"] = np.where(prod["Cost-to-Sales %"] >= cost_flag_thresh, "High Cost Risk", "Normal")

# ----------------------------------------------------------------------------
# TABS
# ----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 Product Profitability",
    "🏭 Division Performance",
    "📉 Cost vs Margin Diagnostics",
    "📊 Profit Concentration (Pareto)",
    "🗺️ Factory & Geography",
])

# =====================  TAB 1: PRODUCT PROFITABILITY  =======================
with tab1:
    st.subheader("Product-Level Margin Leaderboard")
    c1, c2 = st.columns([1.3, 1])

    with c1:
        p_sorted = prod.sort_values("Gross Margin %")
        fig = px.bar(
            p_sorted, x="Gross Margin %", y="Product Name", orientation="h",
            color="Gross Margin %", color_continuous_scale=["#FF5A79", "#F4A261", "#C77D4F"],
            text=p_sorted["Gross Margin %"].round(1).astype(str) + "%",
        )
        fig.add_vline(x=margin_med, line_dash="dash", line_color=MUTED_TEXT,
                       annotation_text=f"Median {margin_med:.1f}%", annotation_font_color=TEXT)
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        style_fig(fig, height=460)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = px.pie(prod, values="Gross_Profit", names="Product Name", hole=0.45,
                       color_discrete_sequence=PALETTE)
        fig2.update_layout(showlegend=False)
        fig2.update_traces(textinfo="label+percent", textfont_size=9, textfont_color=TEXT,
                            marker=dict(line=dict(color=APP_BG, width=2)))
        style_fig(fig2, height=460)
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Profit contribution by product")

    st.subheader("Portfolio Quadrant: Sales vs. Margin")
    st.caption("Bubble size = total gross profit. Products above the median margin line "
               "and to the right of the median sales line are your Stars.")
    fig3 = px.scatter(
        prod, x="Sales", y="Gross Margin %", size="Gross_Profit", color="Quadrant",
        hover_name="Product Name", size_max=55,
        color_discrete_map={
            "⭐ Star (High-Sales / High-Margin)": "#06D6A0",
            "⚠️ Volume Trap (High-Sales / Low-Margin)": "#FF5A79",
            "💎 Niche (Low-Sales / High-Margin)": "#4EA8DE",
            "🚩 Laggard (Low-Sales / Low-Margin)": "#94A3B8",
        },
    )
    fig3.add_vline(x=sales_med, line_dash="dash", line_color=MUTED_TEXT)
    fig3.add_hline(y=margin_med, line_dash="dash", line_color=MUTED_TEXT)
    style_fig(fig3, height=520, legend_top=False)
    fig3.update_layout(legend=dict(font=dict(color=TEXT)))
    st.plotly_chart(fig3, use_container_width=True)

    cA, cB = st.columns(2)
    with cA:
        st.markdown("**⚠️ High-Sales / Low-Margin — 'Volume Traps'**")
        traps = prod[prod["Quadrant"].str.contains("Volume Trap")][
            ["Product Name", "Sales", "Gross Margin %", "Profit Contribution %"]
        ].sort_values("Sales", ascending=False)
        st.dataframe(traps.style.format({"Sales": "${:,.0f}", "Gross Margin %": "{:.1f}%",
                                          "Profit Contribution %": "{:.1f}%"}),
                     use_container_width=True, hide_index=True)
    with cB:
        st.markdown("**🚩 Low-Sales / Low-Margin — 'Laggards' (rationalization candidates)**")
        laggards = prod[prod["Quadrant"].str.contains("Laggard")][
            ["Product Name", "Sales", "Gross Margin %", "Profit Contribution %"]
        ].sort_values("Sales")
        st.dataframe(laggards.style.format({"Sales": "${:,.0f}", "Gross Margin %": "{:.1f}%",
                                             "Profit Contribution %": "{:.1f}%"}),
                     use_container_width=True, hide_index=True)

    st.subheader("Full Product Table")
    show_cols = ["Product Name", "Division", "Sales", "Gross_Profit", "Gross Margin %",
                 "Profit per Unit", "Units", "Revenue Contribution %", "Profit Contribution %", "Quadrant"]
    st.dataframe(
        prod[show_cols].sort_values("Gross_Profit", ascending=False).rename(columns={"Gross_Profit": "Gross Profit"})
        .style.format({"Sales": "${:,.0f}", "Gross Profit": "${:,.0f}", "Gross Margin %": "{:.1f}%",
                        "Profit per Unit": "${:.2f}", "Revenue Contribution %": "{:.1f}%",
                        "Profit Contribution %": "{:.1f}%"}),
        use_container_width=True, hide_index=True,
    )

# =====================  TAB 2: DIVISION PERFORMANCE  ========================
with tab2:
    st.subheader("Division-Level Performance")
    div = df.groupby("Division").agg(
        Sales=("Sales", "sum"), Cost=("Cost", "sum"), Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum"), Orders=("Order ID", "nunique"), Products=("Product Name", "nunique"),
    ).reset_index()
    div["Gross Margin %"] = div["Gross_Profit"] / div["Sales"] * 100
    div["Revenue Share %"] = div["Sales"] / TOTAL_SALES * 100
    div["Profit Share %"] = div["Gross_Profit"] / TOTAL_PROFIT * 100
    div["Imbalance"] = div["Profit Share %"] - div["Revenue Share %"]
    div = div.sort_values("Gross_Profit", ascending=False)

    cols = st.columns(len(div))
    for c, (_, r) in zip(cols, div.iterrows()):
        with c:
            st.metric(r["Division"], f"{r['Gross Margin %']:.1f}% margin",
                      f"{r['Imbalance']:+.1f} pp profit vs revenue share")
            st.caption(f"${r['Sales']:,.0f} sales · ${r['Gross_Profit']:,.0f} profit · {r['Products']} products")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Revenue Share vs. Profit Share**")
        fig = go.Figure()
        fig.add_bar(name="Revenue Share %", x=div["Division"], y=div["Revenue Share %"], marker_color="#4EA8DE")
        fig.add_bar(name="Profit Share %", x=div["Division"], y=div["Profit Share %"], marker_color="#C77D4F")
        fig.update_layout(barmode="group")
        style_fig(fig, height=420, legend_top=True)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("A division whose profit-share bar is shorter than its revenue-share bar "
                   "is contributing disproportionately less profit than its sales volume implies.")

    with c2:
        st.markdown("**Order-Level Margin Distribution by Division**")
        fig = px.box(df, x="Division", y="Gross Margin %", color="Division",
                     color_discrete_map=DIVISION_COLORS, points=False)
        fig.update_layout(showlegend=False)
        style_fig(fig, height=420)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Wider boxes / longer whiskers indicate less predictable, more volatile margins.")

    st.markdown("**Monthly Gross Margin Trend by Division**")
    trend = df.copy()
    trend["Order Month"] = trend["Order Date"].dt.to_period("M").astype(str)
    trend_g = trend.groupby(["Order Month", "Division"]).apply(
        lambda g: g["Gross Profit"].sum() / g["Sales"].sum() * 100, include_groups=False
    ).reset_index(name="Margin %").sort_values("Order Month")
    fig = px.line(trend_g, x="Order Month", y="Margin %", color="Division", markers=True,
                  color_discrete_map=DIVISION_COLORS)
    style_fig(fig, height=400, legend_top=True)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Division Summary Table**")
    st.dataframe(
        div[["Division", "Sales", "Gross_Profit", "Gross Margin %", "Revenue Share %",
             "Profit Share %", "Imbalance", "Orders", "Products"]].rename(columns={"Gross_Profit": "Gross Profit"})
        .style.format({"Sales": "${:,.0f}", "Gross Profit": "${:,.0f}", "Gross Margin %": "{:.1f}%",
                        "Revenue Share %": "{:.1f}%", "Profit Share %": "{:.1f}%", "Imbalance": "{:+.1f} pp"}),
        use_container_width=True, hide_index=True,
    )

# =====================  TAB 3: COST VS MARGIN DIAGNOSTICS  ==================
with tab3:
    st.subheader("Cost Structure Diagnostics")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Order-Level Cost vs. Sales**")
        fig = px.scatter(df, x="Cost", y="Sales", color="Division", opacity=0.5,
                          color_discrete_map=DIVISION_COLORS)
        max_v = max(df["Sales"].max(), df["Cost"].max()) * 1.05
        fig.add_trace(go.Scatter(x=[0, max_v], y=[0, max_v], mode="lines",
                                  line=dict(color=MUTED_TEXT, dash="dash"), name="Breakeven line"))
        style_fig(fig, height=480, legend_top=True)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("**Product Cost-Risk Map**")
        fig = px.scatter(
            prod, x="Sales", y="Cost-to-Sales %", size="Units", color="Cost Risk",
            hover_name="Product Name", size_max=45,
            color_discrete_map={"High Cost Risk": "#FF5A79", "Normal": "#06D6A0"},
        )
        fig.add_hline(y=cost_flag_thresh, line_dash="dash", line_color=MUTED_TEXT,
                       annotation_text="High cost-risk threshold", annotation_font_color=TEXT)
        style_fig(fig, height=480, legend_top=True)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Margin Risk Flags")
    risk_tbl = prod[["Product Name", "Division", "Sales", "Cost-to-Sales %", "Gross Margin %", "Cost Risk"]].copy()
    risk_tbl = risk_tbl.sort_values("Cost-to-Sales %", ascending=False)

    def badge(v):
        cls = "risk-badge-high" if v == "High Cost Risk" else "risk-badge-ok"
        return f'<span class="{cls}">{v}</span>'

    risk_tbl_display = risk_tbl.copy()
    risk_tbl_display["Cost Risk"] = risk_tbl_display["Cost Risk"].apply(badge)
    risk_tbl_display["Sales"] = risk_tbl_display["Sales"].map("${:,.0f}".format)
    risk_tbl_display["Cost-to-Sales %"] = risk_tbl_display["Cost-to-Sales %"].map("{:.1f}%".format)
    risk_tbl_display["Gross Margin %"] = risk_tbl_display["Gross Margin %"].map("{:.1f}%".format)
    st.markdown(risk_tbl_display.to_html(escape=False, index=False), unsafe_allow_html=True)

    n_risk = (prod["Cost Risk"] == "High Cost Risk").sum()
    if n_risk:
        st.warning(f"⚠️ {n_risk} product(s) flagged for repricing, cost renegotiation, or "
                    f"discontinuation review based on elevated cost-to-sales ratio.")
    else:
        st.success("No products currently exceed the high cost-risk threshold under the active filters.")

# =====================  TAB 4: PARETO / PROFIT CONCENTRATION  ===============
with tab4:
    st.subheader("Profit Concentration (Pareto) Analysis")

    def pareto_table(frame, value_col, name_col):
        t = frame.sort_values(value_col, ascending=False).reset_index(drop=True)
        t["Cumulative %"] = t[value_col].cumsum() / t[value_col].sum() * 100
        t["Item Rank %"] = (t.index + 1) / len(t) * 100
        return t

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Revenue Concentration by Product**")
        pr = pareto_table(prod, "Sales", "Product Name")
        fig = go.Figure()
        fig.add_bar(x=pr["Product Name"], y=pr["Sales"], marker_color="#4EA8DE", name="Sales")
        fig.add_trace(go.Scatter(x=pr["Product Name"], y=pr["Cumulative %"], yaxis="y2",
                                  mode="lines+markers", line=dict(color="#FF5A79"), name="Cumulative %"))
        fig.add_hline(y=80, line_dash="dash", line_color=MUTED_TEXT, yref="y2")
        fig.update_layout(
            yaxis2=dict(overlaying="y", side="right", range=[0, 105], title="Cumulative %",
                        color=TEXT, gridcolor=GRID),
            xaxis=dict(tickangle=-45),
        )
        style_fig(fig, height=450, legend_top=True)
        st.plotly_chart(fig, use_container_width=True)
        n80 = (pr["Cumulative %"] <= 80).sum() + 1
        st.info(f"**{n80} of {len(pr)} products ({n80/len(pr)*100:.0f}%)** generate 80% of total revenue.")

    with c2:
        st.markdown("**Profit Concentration by Product**")
        pp = pareto_table(prod, "Gross_Profit", "Product Name")
        fig = go.Figure()
        fig.add_bar(x=pp["Product Name"], y=pp["Gross_Profit"], marker_color="#C77D4F", name="Gross Profit")
        fig.add_trace(go.Scatter(x=pp["Product Name"], y=pp["Cumulative %"], yaxis="y2",
                                  mode="lines+markers", line=dict(color="#FF5A79"), name="Cumulative %"))
        fig.add_hline(y=80, line_dash="dash", line_color=MUTED_TEXT, yref="y2")
        fig.update_layout(
            yaxis2=dict(overlaying="y", side="right", range=[0, 105], title="Cumulative %",
                        color=TEXT, gridcolor=GRID),
            xaxis=dict(tickangle=-45),
        )
        style_fig(fig, height=450, legend_top=True)
        st.plotly_chart(fig, use_container_width=True)
        n80p = (pp["Cumulative %"] <= 80).sum() + 1
        st.info(f"**{n80p} of {len(pp)} products ({n80p/len(pp)*100:.0f}%)** generate 80% of total gross profit.")

    st.subheader("Geographic Dependency — Revenue Concentration by State")
    state_rev = df.groupby("State/Province")["Sales"].sum().sort_values(ascending=False).reset_index()
    state_pareto = pareto_table(state_rev, "Sales", "State/Province")
    n_states_80 = (state_pareto["Cumulative %"] <= 80).sum() + 1
    fig = px.bar(state_rev.head(15), x="State/Province", y="Sales", color="Sales",
                 color_continuous_scale=["#3B2A22", "#FF5A79"])
    fig.update_layout(coloraxis_showscale=False, xaxis=dict(tickangle=-45))
    style_fig(fig, height=420)
    st.plotly_chart(fig, use_container_width=True)
    st.info(f"**{n_states_80} of {len(state_pareto)} states ({n_states_80/len(state_pareto)*100:.0f}%)** "
            f"account for 80% of total revenue — indicating meaningful geographic dependency risk.")

# =====================  TAB 5: FACTORY & GEOGRAPHY  ==========================
with tab5:
    st.subheader("Factory-Level Rollup")
    fac = df.groupby("Factory").agg(
        Sales=("Sales", "sum"), Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum"), Products=("Product Name", "nunique"),
    ).reset_index()
    fac["Gross Margin %"] = fac["Gross_Profit"] / fac["Sales"] * 100
    fac["Lat"] = fac["Factory"].map(lambda f: FACTORY_COORDS.get(f, (None, None))[0])
    fac["Lon"] = fac["Factory"].map(lambda f: FACTORY_COORDS.get(f, (None, None))[1])

    c1, c2 = st.columns([1.3, 1])
    with c1:
        st.markdown("**Sourcing Factory Locations** (bubble size = total gross profit)")
        fig = px.scatter_geo(
            fac, lat="Lat", lon="Lon", size="Gross_Profit", color="Gross Margin %",
            hover_name="Factory", scope="usa", color_continuous_scale=["#FF5A79", "#F4A261", "#C77D4F"],
            hover_data={"Sales": ":$,.0f", "Gross_Profit": ":$,.0f", "Lat": False, "Lon": False},
        )
        fig.update_geos(
            bgcolor=APP_BG, landcolor=SURFACE, subunitcolor=GRID,
            lakecolor=APP_BG, showland=True, showsubunits=True,
        )
        fig.update_layout(
            height=460, margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor=APP_BG, font=dict(color=TEXT),
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("**Factory Profitability**")
        st.dataframe(
            fac[["Factory", "Sales", "Gross_Profit", "Gross Margin %", "Products"]]
            .rename(columns={"Gross_Profit": "Gross Profit"}).sort_values("Gross Profit", ascending=False)
            .style.format({"Sales": "${:,.0f}", "Gross Profit": "${:,.0f}", "Gross Margin %": "{:.1f}%"}),
            use_container_width=True, hide_index=True,
        )
        st.caption("Products are mapped to their sourcing factory per the Nassau Candy "
                   "product–factory correlation table.")

st.divider()
st.caption("Nassau Candy Distributor · Product Line Profitability & Margin Performance Analysis · "
           "Built with Streamlit")
