# ITC FMCG Last-Mile Distribution: Supply Chain Analytics & Network Optimization Platform

> *An Enterprise Integrated Operations Analytics Suite for Multi-Echelon FMCG Distribution, Inventory Buffering & Logistics Optimization*  
> **Author:** Ujjwal Deep | B.Tech — Mechanical Engineering (3rd Year), BIT Mesra  
> **Target Profile:** ITC Limited — Integrated Operations & Supply Chain Analytics

---

## 📌 Executive Summary & Operational Problem

This platform investigates the mechanical breakdown in **ITC Limited's** tertiary last-mile distribution network across rural districts.

* **The Ground Reality:** An informal kirana retailer in rural Azamgarh, UP had stopped stocking Aashirvaad atta because shipments never arrived on time. The retailer permanently shifted scarce shelf space to a regional competitor brand.
* **The Root Cause:** In multi-echelon FMCG logistics:
  - **Primary Freight (K1: Factory $\rightarrow$ Central Warehouse):** High-efficiency bulk FTL linehaul.
  - **Secondary Freight (K2: Warehouse $\rightarrow$ Wholesale Distributor):** Route-planned and system-tracked via DMS.
  - **Tertiary Last-Mile Freight (K3: Distributor $\rightarrow$ Rural Kirana):** Breaks down into an informal sub-stockist layer. Cash-constrained sub-stockists (operating on ₹5k–10k working capital) carry $<15$ cases buffer against a mathematical requirement of 635 cases under an erratic 10–14 day cycle ($\sigma_L \approx 3.0$ days), producing the **~20% retail store stockout rate** observed in the field.
* **The Integrated Operations Solution:** The **REACH Platform** deploys district-level cross-dock hubs, compresses replenishment review cycles from 12 to 6 days ($\sigma_L = 0.5$ days), cuts required safety stock by 70.7%, optimizes vehicle weight-cube loading to >80%, and lifts composite distributor OTIF from 56% to 90%.

> 💡 **Core Operational Truth:** The Rural Hub is primarily an **availability and OTIF enabler**, not a freight cost-reduction mechanism. Delivered cost per case is essentially cost-neutral (-₹2.69/case or -3.6%), as linehaul freight and cross-dock handling replace informal middleman markups.

---

## 🏭 Multi-Echelon FMCG Network Architecture

```
[ ITC Manufacturing Plant / Integrated Food Park ]
  (Haridwar / Pune / Malur / Panchgram)
        │
        │── Primary Freight (30-40T Multi-Axle FTL / Rail Container)
        ▼
[ Central / Mother Warehouse (CW) ]
  (Palletized high-density storage, national buffer stock)
        │
        │── Secondary Linehaul (16-24T Heavy Commercial Vehicles)
        ▼
[ Regional Distribution Centre (RDC) ]
  (Varanasi / Lucknow / Patna — Cross-dock staging, order consolidation)
        │
        │── Secondary Trunk Freight (9-14T Medium Trucks)
        ▼
[ District Rural Hub / Preferred Stockist (WD) ]
  (Azamgarh / Jaunpur / Ballia — Buffer stock, mixed-case picking, credit control)
        │
        │── Tertiary Milk-Runs (1.25-2.5T Tata Ace / Bolero Pickups)
        ▼
[ Rural Kirana Stores ]
  (Weekly beat orders, cash/UPI on delivery, 10-15 sq ft retail display)
```

---

## 💻 Python Analytics & Optimization Modules (`src/`)

The repository includes a production-grade Python analytics package implementing operations research algorithms:

1. **Dynamic Inventory Engine (`src/inventory_engine/safety_stock.py`):**
   - Stochastic periodic-review $(R, S)$ safety stock calculation: $SS = z \sqrt{(R+L)\sigma_d^2 + \bar{d}^2\sigma_L^2}$.
   - 9-box **ABC-XYZ Matrix Classification** based on revenue volume (ABC) and demand coefficient of variation (XYZ).
   - Dynamic Reorder Point ($ROP$) and Order-Up-To ($S$) calculation.

2. **Dual-Constraint Vehicle Load Optimizer (`src/transport_optimization/load_optimizer.py`):**
   - Mixed-cargo optimization balancing payload weight (KG) and volumetric space (CBM).
   - Solves cargo-pairing heuristics (e.g., dense Aashirvaad Atta + bulky Bingo! potato chips) to achieve $>80-90\%$ utilization on both constraints simultaneously.

3. **Inbound Sourcing Linear Program (`src/transport_optimization/sourcing_solver.py`):**
   - Solves multi-factory to multi-depot transportation cost minimization using `scipy.optimize.linprog` (Highs solver).

4. **OTIF & Carrier Scorecard Engine (`src/performance_scorecards/otif_analyzer.py`):**
   - Computes On-Time %, Case Fill Rate %, Order Fill Rate %, and composite OTIF ($\text{On-Time \%} \times \text{Fill Rate \%}$).
   - Decouples warehouse stockout losses from carrier transit delays.

5. **Demand Analytics & S&OP Error Tracking (`src/demand_analytics/forecast_engine.py`):**
   - Implements Holt's Double Exponential Smoothing for trended demand.
   - Calculates Weighted Absolute Percentage Error (WAPE) and Forecast Bias %.

---

## 📊 The Quantitative Model (`model/itc_model.xlsx`)

A comprehensive, formula-driven supply chain and financial workbook built in `model/itc_model.xlsx` complying with professional corporate finance and logistics modeling standards (zero hardcoded formula constants, zero circular references, automated audit checks).

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

## 📈 Operational Metrics & Service-Level Performance (Current vs. Proposed Hub)

| Metric | Current Setup | Proposed Hub Setup | Operational & Strategic Impact |
|---|---|---|---|
| **Last-Mile Replenishment Cycle ($R$)** | 10–14 days (est. 12d) | 5–7 days (target 6d) | Halved retailer exposure period to stockouts |
| **Distributor Fill Rate** | ~75–80% (est. 78%) | 90–92% | +14% order completeness at distribution nodes |
| **Composite OTIF (On-Time In-Full)** | ~56% | ~90% | Predictable weekly store replenishment |
| **Atta Safety Stock Days of Cover** | ~17.5 days | ~5.1 days | **70.7% reduction** in required channel buffer stock |
| **Delivered Cost per Case** | ₹74.55 / case | ₹71.86 / case | -₹2.69 / case net savings (essentially cost-neutral) |
| **Vehicle Route Load Factor** | Unscheduled / ~45-50% | 80.8% Vol / 86.9% Wt | Route-planned multi-constraint load optimization |

---

### 💵 Base-Case Financial Scenario Projections (150 District Hubs)

> ⚠️ **Methodological Note on Financial Outputs:** The financial returns below (NPV ₹379.9 Cr, Payback 15.1 months, IRR 114%) are **indicative base-case scenario projections**, not empirical findings. They depend heavily on two operational working assumptions: (1) a **50% Demand Recapture Rate** on prevented retail out-of-stock events, and (2) **800 new direct retail outlets added per district hub** averaging ~5 cases/month (~65 cases/year). These assumptions represent planning hypotheses to be calibrated during district pilot testing.

| Financial Metric | Base-Case Scenario Output | Modeling Mechanics & Assumptions |
|---|---|---|
| **Mature Annual Incremental Revenue (Y3)** | **₹1,325.9 Crores / Year** | Top-line unlock across 150 mature district hubs (~9.1M cases/yr) |
| **Cumulative 3-Year Incremental Revenue** | **₹2,806.5 Crores** | Phased 3-year rollout (50 hubs Y1 $\rightarrow$ 150 hubs Y2/Y3) |
| **Total 3-Year Capex & Opex Investment** | **₹430.0 Crores** | Hub leases, sub-stockist SLAs, SFA rollout, and VLE onboarding |
| **3-Year Project NPV (@ 12% WACC)** | **₹379.9 Crores** | Discounted cash flow return at 12% working hurdle rate |
| **Modeled Simple Payback Period** | **15.1 Months** | Matches workbook formula `=ABS(B33)/(C23-C28)*12` |
| **Modeled IRR** | **~114%** | Operating leverage on asset-light leased cross-dock facilities |

---

## 🛠️ How to Reproduce & Run the Test Suite

1. **Prerequisites:** Python 3.9+ with `openpyxl`, `numpy`, `scipy`, `pandas`:
   ```bash
   pip install openpyxl numpy scipy pandas
   ```
2. **Execute Automated Unit Tests:**
   ```bash
   python -m unittest discover tests
   ```
   Validates inventory formulas, vehicle loading constraints, and linear programming solver.
3. **Generate the Excel Workbook:**
   ```bash
   python model/generate_sheets.py
   ```
   Outputs clean workbook at `model/itc_model.xlsx`.
4. **Verify Formula Integrity & Cross-Sheet Links:**
   ```bash
   python model/verify_formulas.py
   ```
   Scans all 296 formulas, verifies OpenXML compatibility, checks cross-sheet references, and confirms zero formula errors.

---

## 📂 Repository File Directory

* [Project Report](ITC_LastMile_Project_Report.md): Full technical & managerial case study report (~6,000 words).
* [Executive Presentation Deck](ITC_LastMile_Presentation_Deck.md): 15-slide executive presentation deck.
* [Operational Analytics Modules](src/): Python package containing inventory, transportation, sourcing, and scorecard engines.
* [Automated Unit Test Suite](tests/): Unit test coverage validating optimization algorithms and boundary limits.
* [Quantitative Supply Chain Model](model/itc_model.xlsx): 10-sheet quantitative supply chain and DCF valuation model.
* [Model Generator Script](model/generate_sheets.py): Automated generator for the Excel workbook.
* [Formula Verification Script](model/verify_formulas.py): Automated audit script verifying formula syntax, cross-sheet links, and OpenXML compatibility.

---

## ⚠️ Limitations & Data Governance Note

All sample district data (distances, demand variability, store counts) are **ILLUSTRATIVE** benchmarks designed to test supply chain mechanics. They represent plausible estimates for eastern Uttar Pradesh (Azamgarh cluster) and must be replaced with audited field data prior to commercial capital deployment.
