# 📊 HVIA Executive Intelligence & Sales Reconciliation Suite

> An enterprise-grade financial architecture, margin diagnostic platform, and executive analytics suite engineered for **EL-SHARNOUBY GROUP — LEO MODA**.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.0+-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=for-the-badge&logo=pandas&logoColor=white)

---

## 📌 Executive Overview & Financial Baseline

Standard Business Intelligence dashboards often fail to expose top-line profit erosion. The **HVIA Suite** bridges raw transactional manufacturing data with C-suite financial decision-making, providing real-time visibility into revenue realization and margin leakage.

### Core Financial Highlights:
* **Gross List Sales:** `~600.00M EGP` (catalog price valuation).
* **Invoiced Billing:** `420.70M EGP` (after `179.00M EGP` in commercial trade discounts).
* **Net Realized Receipts:** `411.27M EGP` (after deducting `9.43M EGP` in customer refunds).
* **Cost of Goods Sold (COGS):** `348.44M EGP`.
* **Gross Profit Realized:** `62.83M EGP` (**15.28% Gross Margin**).
* **Core Insight & Optimization:** Identified wholesale discount leakage as the primary margin compressor. Restructuring discount caps unlocks **+17.00M EGP** directly into bottom-line earnings.

---

## 🛠️ Key Modules & System Architecture

The suite features 8 comprehensive operational modules and a dedicated Client Portal:
* **App 01: Financials:** Financial Architecture & Sales Reconciliation (Monthly Trajectory & Waterfall Bridge).
* **App 02: Inventory:** Smart Replenishment Engine & Inter-Branch Stock Transfers.
* **App 03: Customers:** Customer 360, RFM Cohorts & Win-Back Triggers (with CSV Export).
* **App 04: Factory:** Digital Twin, Machine Downtime & Quality Scrap Root Causes.
* **App 05: Marketing:** Attribution ROAS, CPA Analysis & E-Commerce Funnel Leakage.
* **App 06: Branches:** Unit Economics & Regional Expansion Feasibility.
* **App 07: Suppliers:** Procurement Spend & On-Time Delivery (OTD) Risk Scorecard.
* **App 08: Simulator:** Executive What-If Scenario Simulator (Discount Caps, QC Rescue, Win-Back).
* **Client Portal:** Self-service loyalty tracking, live stock visibility, and AI size recommender.

---

## 🎨 UI & Layout Engineering

To ensure error-proof UI rendering and eliminate visual clipping across high-resolution enterprise displays:
* **Custom Plotly Margins:** Configured explicit padding (`margin=dict(t=50, b=40, l=80, r=30)`) and axis title offsets (`standoff=15`) to resolve text overlaps.
* **Dynamic Range Auto-Scaling:** Auto-calculates Y-axis limits (`range=[0, max_y]`) and sets `cliponaxis=False` to prevent top-level Waterfall labels (e.g., `600M`) from being clipped by container boundaries.
* **Streamlit Responsive Layouts:** Built inside bordered containers with dark-themed editorial callouts for clear visual hierarchy.
* **Bilingual Core (v2.4.2):** Seamless EN ⇄ AR toggle with optimized `on_change` callbacks for zero-lag layout updates.

[Live demo](https://el-sharnouby-uox5qlfobqupy69xmkmycy.streamlit.app/)
---

## 👥 Project Credits & Team Collaboration

Special recognition and credit to **[Ayman Abdelnasser]** for outstanding engineering contributions, data modeling precision, and technical partnership throughout the architecture and deployment of this platform.


---

## 🚀 Quick Start & Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/EyadMohamed07/El-sharnouby.git
   cd El-sharnouby
