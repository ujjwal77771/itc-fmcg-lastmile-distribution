# ITC FMCG Last-Mile Distribution: Solving the Rural Reach & Logistics Gap

> *A rigorous supply chain case study & financial model for campus recruitment — ITC GET (Logistics & Warehousing)*  
> **Author:** Ujjwal Deep | B.Tech — Mechanical Engineering (3rd Year), BIT Mesra

---

## 📌 Executive Summary

This project investigates why **ITC Limited** — despite commanding a ₹20,000+ crore FMCG portfolio and deep rural brand trust built over two decades via e-Choupal — struggles with shelf availability in rural kirana stores.

* **The Observation:** An informal kirana store in rural Azamgarh, UP had stopped stocking Aashirvaad atta because shipments never arrived on time. The shopkeeper permanently switched shelf space to a regional competitor brand.
* **The Root Cause:** In FMCG logistics terminology, **K1** (primary freight: plant to mother warehouse) and **K2** (secondary freight: warehouse to wholesale distributor) operate with high efficiency. The breakdown occurs at **K3** (tertiary freight: distributor to rural retailer). The sub-stockist layer is informal, unmapped in ITC's Distributor Management System (DMS), and runs on an erratic 10–14 day cycle with an estimated ~78% distributor fill rate.
* **The Strategic Solution:** The **REACH Framework** formalizes the district-level last-mile network by deploying 150 Rural Hubs (cross-docks), digitizing replenishment signals, scheduling dedicated milk-runs, and formalizing sub-stockists with defined territories and service-level agreements.

---

## 📊 The Quantitative Model (`model/itc_model.xlsx`)

A comprehensive, formula-driven supply chain and financial model has been built in `model/itc_model.xlsx` complying with professional corporate finance and logistics modeling standards (zero hardcoded formula constants, zero circular references, automated audit checks).

### Model Architecture (10 Sheets)

| # | Sheet Name | Core Supply Chain / Financial Contents |
|---|---|---|
| 1 | `Summary_Dashboard` | High-level operational, service-level (OTIF), and DCF financial variance: Current vs Proposed Hub Setup. |
| 2 | `Assumptions_Inputs` | Central parameter repository. Blue font for inputs, units on every cell, operational notes and citations. |
| 3 | `District_Baseline` | Inter-node Distance Matrix, route circuity factor (1.20×), milk-run stop itinerary, and vehicle utilization (`MIN(Capacity, Orders)`) by weight and volume. |
| 4 | `Inventory_Logic` | Stochastic periodic-review $(R, S)$ inventory model: $SS = z \cdot \sqrt{(R+L)\sigma_d^2 + \bar{d}^2\sigma_L^2}$. Stockout probability and expected fill rate across ABC SKUs. |
| 5 | `Delivered_Cost_Build` | End-to-end delivered logistics cost per case: Trunk Linehaul + Hub Handling + Facility Rent + Inventory Holding + Milk-Run Freight + Driver Labor + Transit Damage. |
| 6 | `Revenue_and_Financials` | Rule 4 Incremental Volume Build (flagged as **Weakest Assumption**), itemized Capex/Opex, 3-Year Cash Flows, NPV @ 12% WACC, IRR, and Payback. |
| 7 | `Sensitivity_Analysis` | Parametric stress testing (Conservative, Optimistic, High Freight, High Demand Variability) and direct-formula OOS-by-cycle lookup table (No Excel What-If data tables). |
| 8 | `Scorecard_and_OTIF` | OTIF framework ($\text{OTIF} = \text{On-Time \%} \times \text{Fill Rate \%}$) and Transporter Benchmarking Scorecard across 4 district carrier vendors. |
| 9 | `Compliance` | Statutory & EHS compliance matrix for district warehousing and transportation (Rule 8: legal section column left blank). |
| 10 | `Checks` | 10 automated mathematical integrity checks displaying `PASS`/`FAIL` and master system integrity indicator. |

---

## 🔬 Core Supply Chain Formulas Documented in Model

### 1. Periodic-Review Safety Stock (Stochastic Demand & Lead Time)
$$SS = z \times \sqrt{(R + L)\,\sigma_d^2 + \bar{d}^2\,\sigma_L^2}$$
* **$R$:** Replenishment review cycle (Current: 12 days $\rightarrow$ Proposed Hub: 6 days)
* **$L$:** Delivery lead time in transit (Current: 4 days $\rightarrow$ Proposed Hub: 1.5 days)
* **$\sigma_d$:** Daily demand standard deviation
* **$\bar{d}$:** Average daily demand
* **$\sigma_L$:** Delivery arrival lead-time variability (Current: 3.0 days $\rightarrow$ Proposed Hub: 0.5 days)
* **$z$:** Service level factor (1.645 for 95% cycle service level)

### 2. Vehicle Capacity & Route Utilization
$$\text{Cases Delivered per Trip} = \min(\text{Truck Capacity in Cases},\,\text{Orders on Route})$$
$$\text{Volumetric Utilization} = \frac{\text{Cases Delivered}}{\text{Case Capacity}} \quad\Big|\quad \text{Weight Utilization} = \frac{\text{Delivered Weight}}{\text{Rated Payload}}$$

### 3. Incremental Volume Build
$$\text{Incremental Cases} = \Big[\text{Baseline Cases} \times (\text{OOS}_{\text{before}} - \text{OOS}_{\text{after}}) \times \text{Recapture \%}\Big] + \big[\text{New Outlets} \times \text{Cases/Outlet}\big]$$
> ⚠️ **Weakest Assumption Flag:** The Demand Recapture % on Prevented OOS (assumed at 50% in base case) depends heavily on whether rural consumers substitute competitor brands permanently or wait for stock. Must be verified in district pilot testing.

### 4. Service Level Metric (OTIF)
$$\text{OTIF \%} = \text{On-Time Delivery \%} \times \text{Order Fill Rate \%}$$

---

## 📈 Key Findings & 3-Year Reconciled Targets

| Metric | Current Setup | Proposed Hub Setup | 3-Year Impact |
|---|---|---|---|
| **K3 Replenishment Cycle ($R$)** | 10–14 days (est. 12d) | 5–7 days (target 6d) | Halved exposure period |
| **Distributor Fill Rate** | ~75–80% (est. 78%) | 90–92% | +14% order completeness |
| **Composite OTIF** | ~56% | ~90% | Predictable retailer delivery |
| **Atta Safety Stock Days of Cover** | ~17.5 days | ~5.1 days | **70.7% reduction** in buffer stock |
| **Delivered Cost per Case** | ₹74.55 / case | ₹71.86 / case | -₹2.69 / case net savings |
| **Vehicle Load Factor** | Erratic / Sub-optimal | 80.8% Vol / 86.9% Wt | High capacity utilization |
| **Cumulative 3-Year Incremental Revenue** | — | **₹2,806.5 Crores** | Within ₹2,500–3,500 Cr target range |
| **Total 3-Year Capital & Opex Investment** | — | **₹430.0 Crores** | Within ₹400–470 Cr budget |
| **3-Year Project NPV (@ 12% WACC)** | — | **₹379.9 Crores** | Strong economic value add |
| **Simple Payback Period** | — | **~20.5 Months** | Within 18–24 month target |

---

## 🛠️ How to Reproduce & Run the Model

1. **Prerequisites:** Python 3.9+ with `openpyxl`:
   ```bash
   pip install openpyxl
   ```
2. **Generate the Excel Workbook:**
   ```bash
   python model/generate_sheets.py
   ```
   Outputs clean workbook at `model/itc_model.xlsx`.
3. **Verify Formula Integrity & Cross-Sheet Links:**
   ```bash
   python model/verify_formulas.py
   ```
4. **Simulate Mathematical Logic & Verify All 10 Checks:**
   ```bash
   python model/simulate_math.py
   ```

---

## 📂 Repository File Directory

* [`ITC_LastMile_Project_Report.md`](file:///c:/Users/BIT/OneDrive/Desktop/ANTIGRAVITY%20BACKUP/scratch/itc-lastmile-project/ITC_LastMile_Project_Report.md): Full technical & managerial case study report (~6,000 words).
* [`ITC_LastMile_Presentation_Deck.md`](file:///c:/Users/BIT/OneDrive/Desktop/ANTIGRAVITY%20BACKUP/scratch/itc-lastmile-project/ITC_LastMile_Presentation_Deck.md): 15-slide executive presentation deck.
* [`HR_Interview_CheatSheet.md`](file:///c:/Users/BIT/OneDrive/Desktop/ANTIGRAVITY%20BACKUP/scratch/itc-lastmile-project/HR_Interview_CheatSheet.md): Interview preparation guide — ITC logistics terminology (K1/K2/K3, WSP, WD, TIT, OTIF), formulas, and top 10 hardest interviewer questions with grounded answers.
* [`model/itc_model.xlsx`](file:///c:/Users/BIT/OneDrive/Desktop/ANTIGRAVITY%20BACKUP/scratch/itc-lastmile-project/model/itc_model.xlsx): 10-sheet quantitative supply chain and DCF valuation model.
* [`model/generate_sheets.py`](file:///c:/Users/BIT/OneDrive/Desktop/ANTIGRAVITY%20BACKUP/scratch/itc-lastmile-project/model/generate_sheets.py): Automated generator for the Excel workbook.
* [`model/simulate_math.py`](file:///c:/Users/BIT/OneDrive/Desktop/ANTIGRAVITY%20BACKUP/scratch/itc-lastmile-project/model/simulate_math.py): Verification script confirming all 10 automated integrity checks pass.

---

## ⚠️ Limitations & Data Governance Note

All sample district data (distances, demand variability, store counts) are **ILLUSTRATIVE** benchmarks designed to test supply chain mechanics. They represent plausible estimates for eastern Uttar Pradesh (Azamgarh cluster) and must be replaced with audited field data prior to commercial capital deployment.
