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

### 1. App 01: Financial Architecture & Sales Reconciliation
* **Monthly Trajectory Line Chart:** Dynamic plotting of `Net Sales` vs. `Gross Profit` over time.
* **Financial Waterfall Bridge:** Full multi-step reconciliation mapping the exact journey from List Price down to Net Realized Profit.

### 2. App 08: Executive What-If Scenario Simulator
* Interactive decision engine modeling multi-variable financial strategies:
  * Factory inventory rescue & liquidation dynamics.
  * Customer win-back revenue velocity.
  * Wholesale discount capping impact on net EBITDA/EBIT.

### 3. Automated Board Audit & Reporting Engine
* One-click generation of audit documentation in Markdown (`.md`) and high-resolution PDF/HTML export formats for executive board presentations.

---

## 🎨 UI & Layout Engineering

To ensure error-proof UI rendering and eliminate visual clipping across high-resolution enterprise displays:
* **Custom Plotly Margins:** Configured explicit padding (`margin=dict(t=50, b=40, l=80, r=30)`) and axis title offsets (`standoff=15`) to resolve text overlaps.
* **Dynamic Range Auto-Scaling:** Auto-calculates Y-axis limits (`range=[0, max_y]`) and sets `cliponaxis=False` to prevent top-level Waterfall labels (e.g., `600M`) from being clipped by container boundaries.
* **Streamlit Responsive Layouts:** Built inside bordered containers with dark-themed editorial callouts for clear visual hierarchy.

---

## 👥 Project Credits & Team Collaboration

Special recognition and credit to **[اسم المهندس زميلك]** for outstanding engineering contributions, data modeling precision, and technical partnership throughout the architecture and deployment of this platform.

---

## 🚀 Quick Start & Installation

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/your-username/hvia-executive-suite.git](https://github.com/your-username/hvia-executive-suite.git)
   cd hvia-executive-suite