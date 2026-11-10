# ITC FMCG Last-Mile Distribution: Solving the Rural Reach & Logistics Gap

> *A District-Level Supply Chain Strategy & Quantitative Distribution Logistics Model for Rural FMCG Distribution*  
> **Author:** Ujjwal Deep | B.Tech — Mechanical Engineering (3rd Year), BIT Mesra

---

## 📌 Executive Summary

This project investigates why **ITC Limited** — despite commanding a ₹20,000+ crore FMCG portfolio and deep rural brand trust built over two decades via e-Choupal — struggles with shelf availability in rural kirana stores.

* **The Observation:** An informal kirana store in rural Azamgarh, UP had stopped stocking Aashirvaad atta because shipments never arrived on time. The shopkeeper permanently switched shelf space to a regional competitor brand.
* **The Root Cause:** In standard FMCG logistics tiering (Primary, Secondary, and Tertiary freight, classified as K1, K2, and K3 in ITC Logistics operations): Primary K1 (plant to regional warehouse) and Secondary K2 (warehouse to wholesale distributor) operate with high efficiency. The breakdown occurs at Tertiary K3 (distributor to rural retailer). The sub-stockist layer is informal, unmapped in ITC's central Distributor Management System (DMS), and runs on an erratic 10–14 day cycle with an estimated ~75–80% distributor fill rate.
* **The Strategic Solution:** The **REACH Framework** formalizes the district-level last-mile network by deploying 150 Rural Hubs (cross-docks), digitizing replenishment signals, scheduling dedicated milk-runs, and formalizing sub-stockists with defined territories and service-level agreements.

> 💡 **Strategic Logistics Insight:** The Hub model is primarily an operational **service-level and revenue enabler** (lifting OTIF from ~56% to ~90% and cutting review cycle from 12d to 6d), **not a freight cost-cutting mechanism**. Net delivered logistics cost per case is essentially neutral (-3.6% saving or ₹2.69/case), as linehaul freight and cross-dock handling replace informal middleman markups.

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
| 6 | `Revenue_and_Financials` | Incremental Volume & Demand Recapture Build (flagged as Key Modeling Sensitivity), itemized Capex/Opex, 3-Year Cash Flows, NPV @ 12% WACC, IRR, and Payback. |
| 7 | `Sensitivity_Analysis` | Parametric stress testing (Conservative, Optimistic, High Freight, High Demand Variability) and direct-formula OOS-by-cycle lookup table (No Excel data tables). |
| 8 | `Scorecard_and_OTIF` | OTIF framework ($\text{OTIF} = \text{On-Time \%} \times \text{Fill Rate \%}$) and Transporter Benchmarking Scorecard across 4 district carrier vendors. |
| 9 | `Compliance` | Statutory & EHS compliance matrix for district warehousing and transportation operations. |
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
> 📌 **Key Sensitivity Parameter:** The Demand Recapture % on Prevented OOS (conservatively set at 50% in base case) depends on brand loyalty vs competitor substitution dynamics. This parameter serves as the primary test hypothesis for the 60-day district pilot.

### 4. Service Level Metric (OTIF)
$$\text{OTIF \%} = \text{On-Time Delivery \%} \times \text{Order Fill Rate \%}$$

---

## 📈 Key Findings & 3-Year Reconciled Targets

| Metric | Current Setup | Proposed Hub Setup | Operational & Strategic Impact |
|---|---|---|---|
| **K3 Replenishment Cycle ($R$)** | 10–14 days (est. 12d) | 5–7 days (target 6d) | Halved retailer exposure period to stockouts |
| **Distributor Fill Rate** | ~75–80% (est. 78%) | 90–92% | +14% order completeness at distribution nodes |
| **Composite OTIF (On-Time In-Full)** | ~56% | ~90% | Predictable weekly store replenishment |
| **Atta Safety Stock Days of Cover** | ~17.5 days | ~5.1 days | **70.7% reduction** in required channel buffer stock |
| **Delivered Cost per Case** | ₹74.55 / case | ₹71.86 / case | -₹2.69 / case net savings (essentially cost-neutral) |
| **Vehicle Route Load Factor** | Unscheduled / ~45-50% | 80.8% Vol / 86.9% Wt | Route-planned multi-constraint load optimization |
| **Mature Annual Incremental Revenue (Y3)** | — | **₹1,325.9 Crores / Year** | Top-line unlock across 150 district hubs |
| **Cumulative 3-Year Incremental Revenue** | — | **₹2,806.5 Crores** | Phased 3-year rollout (50 hubs Y1 $\rightarrow$ 150 hubs Y2/Y3) |
| **Total 3-Year Capex & Opex Investment** | — | **₹430.0 Crores** | Self-funding operational expansion |
| **3-Year Project NPV (@ 12% WACC)** | — | **₹379.9 Crores** | Discounted cash flow economic value creation |
| **Simple Payback Period** | — | **~20.5 Months** | Capital recovery within 2 years |

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
   Scans all 296 formulas, verifies OpenXML compatibility, checks cross-sheet references, and confirms zero formula errors.

---

## 📂 Repository File Directory

* [`ITC_LastMile_Project_Report.md`](file:///c:/Users/BIT/OneDrive/Desktop/ANTIGRAVITY%20BACKUP/scratch/itc-lastmile-project/ITC_LastMile_Project_Report.md): Full technical & managerial case study report (~6,000 words).
* [`ITC_LastMile_Presentation_Deck.md`](file:///c:/Users/BIT/OneDrive/Desktop/ANTIGRAVITY%20BACKUP/scratch/itc-lastmile-project/ITC_LastMile_Presentation_Deck.md): 15-slide executive presentation deck.
* [`InterviewtSheet.md`](file:///c:/Users/BIT/OneDrive/Desktop/ANTIGRAVITY%20BACKUP/scratch/itc-lastmile-project/InterviewtSheet.md): Operational logistics discussion guide — ITC supply chain terminology (K1/K2/K3, WSP, WD, TIT, OTIF), formulas, and technical question-and-answer frameworks.
* [`model/itc_model.xlsx`](file:///c:/Users/BIT/OneDrive/Desktop/ANTIGRAVITY%20BACKUP/scratch/itc-lastmile-project/model/itc_model.xlsx): 10-sheet quantitative supply chain and DCF valuation model.
* [`model/generate_sheets.py`](file:///c:/Users/BIT/OneDrive/Desktop/ANTIGRAVITY%20BACKUP/scratch/itc-lastmile-project/model/generate_sheets.py): Automated generator for the Excel workbook.
* [`model/verify_formulas.py`](file:///c:/Users/BIT/OneDrive/Desktop/ANTIGRAVITY%20BACKUP/scratch/itc-lastmile-project/model/verify_formulas.py): Automated audit script verifying formula syntax, cross-sheet links, and OpenXML compatibility.

---

## ⚠️ Limitations & Data Governance Note

All sample district data (distances, demand variability, store counts) are **ILLUSTRATIVE** benchmarks designed to test supply chain mechanics. They represent plausible estimates for eastern Uttar Pradesh (Azamgarh cluster) and must be replaced with audited field data prior to commercial capital deployment.
