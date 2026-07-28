# Product Line Profitability & Margin Performance Analysis for Nassau Candy Distributor

An interactive analytics system to evaluate SKU-level margins, division performance, and operational profitability.

[![Open Live Dashboard](https://img.shields.io/badge/Streamlit-Open_Live_Dashboard-FF4B4B?logo=streamlit&style=for-the-badge)](https://z8y7dduyr9u5ysnyb86oec.streamlit.app/)

---

## Background
Sales volume alone can be a highly misleading metric for distributors like Nassau Candy. While high-volume products generate significant top-line revenue, high underlying sourcing and logistical costs can result in thin or even negative margins that silently erode overall business profitability. Having granular visibility into gross margin performance is essential for identifying which items are truly driving profit and which are simply inflating revenue without generating value.

## Problem Statement
This project was initiated to address critical blind spots in Nassau Candy's product portfolio. Specifically, it resolves:
* Which product lines generate the highest gross margin %.
* Whether high-sales volume products are actually profitable or functioning as volume traps.
* How profitability and gross margin profiles vary across the major product divisions (Chocolate, Sugar, and Other).
* Which specific SKUs represent severe margin risks and require urgent pricing reviews, cost renegotiation, or rationalization.

## What This Project Delivers
1. **[Research Paper](file:///docs/Nassau_Candy_Research_Paper.docx)**: A comprehensive data analysis report detailing the exploratory data analysis (EDA), findings, and strategic recommendations.
2. **[Interactive Streamlit Dashboard](https://z8y7dduyr9u5ysnyb86oec.streamlit.app/)**: A live, user-friendly business intelligence tool to filter and drill down into order-level data in real-time.
3. **[Executive Summary](file:///docs/Nassau_Candy_Executive_Summary.docx)**: A concise, high-level summary of findings and strategic actions tailored for leadership.

## Key Findings
* **10,180** validated orders analyzed from January 2024 to December 2025, tracking **15** products across **3** divisions.
* **65.9%** overall gross margin.
* **5 of 15 products** (the Chocolate Wonka Bar line) generate **92.9%** of total revenue and **95.1%** of overall gross profit.
* **Chocolate division margin** is the highest at **67.4%**, while the **Other division** underperforms significantly with a **44.8%** margin.
* **Kazookles** is flagged as the top margin-risk product, carrying a low **7.7%** gross margin and an elevated **92.3%** cost-to-sales ratio.
* **16 of 59 states/provinces** generate **80%** of total revenue, led by California (CA), New York (NY), and Texas (TX).

## Dashboard Features
The interactive Streamlit application provides 5 diagnostic modules:
1. **Product Profitability**: Interactive product-level leaderboard and sales-vs-margin quadrant analysis classifying items into Stars, Volume Traps, Niches, or Laggards.
2. **Division Performance**: High-level KPI metrics comparing share of revenue against share of profit, margin volatility (box plots), and monthly historical margin trends.
3. **Cost vs Margin Diagnostics**: Cost structure scatter plots identifying products that exceed risk thresholds.
4. **Profit Concentration (Pareto)**: Concentration analysis showing cumulative sales/profit curves for both products and geographic regions.
5. **Factory & Geography**: Bubble map of sourcing factory locations scaled by profitability and table of factory statistics.

### Global Sidebar Filters:
* **Order Date Range**: Filter metrics and charts by a custom date window.
* **Division Selector**: Toggle between Chocolate, Sugar, and Other divisions.
* **Minimum Gross Margin %**: Filter order-level data by custom gross margin thresholds.
* **Product Search**: Real-time keyword filter to isolate specific candy lines (e.g., Wonka, Gum, Toffee).

## Repository Structure
```
/
├── app/
│   ├── app.py
│   ├── requirements.txt
│   └── data/
│       └── cleaned.csv
├── data/
│   ├── product_summary.csv
│   └── division_summary.csv
├── docs/
│   ├── Nassau_Candy_Research_Paper.docx
│   └── Nassau_Candy_Executive_Summary.docx
├── screenshots/
├── .gitignore
├── LICENSE
└── README.md
```

## How to Run Locally
1. Clone this repository:
   ```bash
   git clone https://github.com/deep1190/nassau-candy-profitability-analysis.git
   cd nassau-candy-profitability-analysis
   ```
2. Navigate to the application folder:
   ```bash
   cd app
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Streamlit dashboard:
   ```bash
   streamlit run app.py
   ```

## Data & Methodology
Data cleaning steps involved importing raw transaction logs, removing duplicates, and standardizing date formats for order and shipping entries. New KPI fields were derived, including Cost-to-Sales Ratio, Gross Profit, and Gross Margin %. Aggregations and outlier-filtering were performed to ensure accurate division and factory classification. The complete analytical methodology is documented in the [Research Paper](file:///docs/Nassau_Candy_Research_Paper.docx).

## Tech Stack
* **Python**
* **Pandas** & **NumPy** (Data cleaning & KPI calculations)
* **Plotly Express** & **Graph Objects** (Interactive visualizations)
* **Streamlit** (Web application framework)

## Author
* **[Deepika Gupta]**
* [deepikagupta1190@gmail.com]
* [9560616390]
