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

PALETTE = ["#52362B", "#FF5A79", "#4EA8DE", "#F4A261", "#06D6A0", "#9B5DE5"]
DIVISION_COLORS = {"Chocolate": "#52362B", "Sugar": "#FF5A79", "Other": "#4EA8DE"}

CUSTOM_CSS = """
<style>
.stApp { background-color: #FDFBF7; }
h1, h2, h3 { color: #52362B; font-family: 'Outfit', 'Georgia', serif; }
[data-testid="stMetricValue"] { color: #52362B; font-weight: 700; }
[data-testid="stMetricLabel"] { color: #7D6B60; }
.stTabs [data-baseweb="tab"] { font-size: 15px; font-weight: 600; color: #7D6B60; }
.stTabs [aria-selected="true"] { color: #FF5A79 !important; border-bottom-color: #FF5A79 !important; }
div[data-testid="stSidebar"] { background-color: #F8F3EB; }
.risk-badge-high { background:#FFF0F2; color:#FF3366; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:600;}
.risk-badge-ok { background:#E6F7ED; color:#00A86B; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:600;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

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
            color="Gross Margin %", color_continuous_scale=["#FF5A79", "#F4A261", "#52362B"],
            text=p_sorted["Gross Margin %"].round(1).astype(str) + "%",
        )
        fig.add_vline(x=margin_med, line_dash="dash", line_color="grey",
                       annotation_text=f"Median {margin_med:.1f}%")
        fig.update_layout(height=460, showlegend=False, coloraxis_showscale=False,
                           plot_bgcolor="white", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = px.pie(prod, values="Gross_Profit", names="Product Name", hole=0.45,
                       color_discrete_sequence=PALETTE)
        fig2.update_layout(height=460, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
        fig2.update_traces(textinfo="label+percent", textfont_size=9)
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
            "🚩 Laggard (Low-Sales / Low-Margin)": "#A59489",
        },
    )
    fig3.add_vline(x=sales_med, line_dash="dash", line_color="grey")
    fig3.add_hline(y=margin_med, line_dash="dash", line_color="grey")
    fig3.update_layout(height=520, plot_bgcolor="white")
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
        fig.add_bar(name="Profit Share %", x=div["Division"], y=div["Profit Share %"], marker_color="#52362B")
        fig.update_layout(barmode="group", height=420, plot_bgcolor="white",
                           legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, use_container_width=True)
        st.caption("A division whose profit-share bar is shorter than its revenue-share bar "
                   "is contributing disproportionately less profit than its sales volume implies.")

    with c2:
        st.markdown("**Order-Level Margin Distribution by Division**")
        fig = px.box(df, x="Division", y="Gross Margin %", color="Division",
                     color_discrete_map=DIVISION_COLORS, points=False)
        fig.update_layout(height=420, showlegend=False, plot_bgcolor="white")
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
    fig.update_layout(height=400, plot_bgcolor="white", legend=dict(orientation="h", y=1.1))
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
        fig = px.scatter(df, x="Cost", y="Sales", color="Division", opacity=0.4,
                          color_discrete_map=DIVISION_COLORS)
        max_v = max(df["Sales"].max(), df["Cost"].max()) * 1.05
        fig.add_trace(go.Scatter(x=[0, max_v], y=[0, max_v], mode="lines",
                                  line=dict(color="grey", dash="dash"), name="Breakeven line"))
        fig.update_layout(height=480, plot_bgcolor="white", legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("**Product Cost-Risk Map**")
        fig = px.scatter(
            prod, x="Sales", y="Cost-to-Sales %", size="Units", color="Cost Risk",
            hover_name="Product Name", size_max=45,
            color_discrete_map={"High Cost Risk": "#FF5A79", "Normal": "#06D6A0"},
        )
        fig.add_hline(y=cost_flag_thresh, line_dash="dash", line_color="grey",
                       annotation_text="High cost-risk threshold")
        fig.update_layout(height=480, plot_bgcolor="white", legend=dict(orientation="h", y=1.1))
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
        fig.add_hline(y=80, line_dash="dash", line_color="grey", yref="y2")
        fig.update_layout(
            height=450, plot_bgcolor="white",
            yaxis2=dict(overlaying="y", side="right", range=[0, 105], title="Cumulative %"),
            legend=dict(orientation="h", y=1.15), xaxis=dict(tickangle=-45),
        )
        st.plotly_chart(fig, use_container_width=True)
        n80 = (pr["Cumulative %"] <= 80).sum() + 1
        st.info(f"**{n80} of {len(pr)} products ({n80/len(pr)*100:.0f}%)** generate 80% of total revenue.")

    with c2:
        st.markdown("**Profit Concentration by Product**")
        pp = pareto_table(prod, "Gross_Profit", "Product Name")
        fig = go.Figure()
        fig.add_bar(x=pp["Product Name"], y=pp["Gross_Profit"], marker_color="#52362B", name="Gross Profit")
        fig.add_trace(go.Scatter(x=pp["Product Name"], y=pp["Cumulative %"], yaxis="y2",
                                  mode="lines+markers", line=dict(color="#FF5A79"), name="Cumulative %"))
        fig.add_hline(y=80, line_dash="dash", line_color="grey", yref="y2")
        fig.update_layout(
            height=450, plot_bgcolor="white",
            yaxis2=dict(overlaying="y", side="right", range=[0, 105], title="Cumulative %"),
            legend=dict(orientation="h", y=1.15), xaxis=dict(tickangle=-45),
        )
        st.plotly_chart(fig, use_container_width=True)
        n80p = (pp["Cumulative %"] <= 80).sum() + 1
        st.info(f"**{n80p} of {len(pp)} products ({n80p/len(pp)*100:.0f}%)** generate 80% of total gross profit.")

    st.subheader("Geographic Dependency — Revenue Concentration by State")
    state_rev = df.groupby("State/Province")["Sales"].sum().sort_values(ascending=False).reset_index()
    state_pareto = pareto_table(state_rev, "Sales", "State/Province")
    n_states_80 = (state_pareto["Cumulative %"] <= 80).sum() + 1
    fig = px.bar(state_rev.head(15), x="State/Province", y="Sales", color="Sales",
                 color_continuous_scale=["#FDFBF7", "#FF5A79"])
    fig.update_layout(height=420, plot_bgcolor="white", coloraxis_showscale=False, xaxis=dict(tickangle=-45))
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
            hover_name="Factory", scope="usa", color_continuous_scale=["#FF5A79", "#F4A261", "#52362B"],
            hover_data={"Sales": ":$,.0f", "Gross_Profit": ":$,.0f", "Lat": False, "Lon": False},
        )
        fig.update_layout(height=460, margin=dict(l=0, r=0, t=0, b=0))
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
