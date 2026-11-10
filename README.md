# ITC FMCG Last-Mile Distribution: Inventory Buffering & Logistics Decision Support

> A supply chain analytics and logistics decision-support project modeling multi-echelon inventory, vehicle loading constraints, and rural service levels for ITC Limited.  
> **Author:** Ujjwal Deep | 3rd Year B.Tech in Mechanical Engineering, BIT Mesra  
> **Project Scope:** Integrated Operations, Warehousing & Last-Mile Logistics

---

## 📌 How This Started: Field Observation in Eastern UP

In January 2024, during a visit to a village kirana store in Azamgarh district (eastern Uttar Pradesh, about 60 km off the national highway), I noticed the retailer had a single variant of Sunfeast biscuits delivered fortnightly by an informal trader, but **zero packets of Aashirvaad Atta**. 

When I asked the shopkeeper why he wasn't stocking India's leading atta brand, he said:
> *"Ek baar mangaya tha, aaya hi nahi. Phir doosra le liya."*  
> *(I ordered it once, it never arrived, so I switched to a competitor brand.)*

That conversation stuck with me. ITC is an enterprise with ₹20,000+ crore FMCG revenue and deep rural credibility through e-Choupal. Yet on the retail shelf 60 km off the highway, it loses sales to local brands simply because the physical distribution pipeline cannot reliably deliver cases on time.

I built this project to investigate the mechanics of that breakdown and to design a practical, data-driven decision support system that an operations analyst could actually use to fix it.

---

## ⚙️ The Operational Problem: Why Informal Sub-Stockists Fail

In multi-echelon FMCG logistics, products move through distinct layers:

```
[ ITC Manufacturing Plant / Integrated Food Park ]
  (Haridwar / Panchgram / Pune)
        │
        │── Primary Freight (30-40T Multi-Axle Trucks / FTL) ── Works smoothly
        ▼
[ Regional Distribution Centre (RDC) ]
  (Varanasi / Lucknow / Patna)
        │
        │── Secondary Freight (9-14T Commercial Trucks) ── Tracked in ERP/DMS
        ▼
[ Preferred Wholesale Stockist (WD) ]
        │
        │── The Breakdown: Informal Sub-Stockists (Tempos / Motorcycles)
        ▼
[ Rural Kirana Stores ] (Azamgarh / Jaunpur / Ballia / Mirzapur)
```

1. **The Math of Channel Buffering:**  
   Under the current informal setup, rural replenishment happens on an erratic 10–14 day cycle ($R = 12$ days) with high delivery lead-time variability ($\sigma_L \approx 3.0$ days). Under periodic-review inventory theory:
   $$SS = z \cdot \sqrt{(R + L)\sigma_d^2 + \bar{d}^2\sigma_L^2}$$
   To guarantee a 95% service level ($z = 1.645$) for a high-velocity staple like Aashirvaad Atta, a stockist must hold approximately **635 cases of buffer stock**.

2. **The Working Capital Reality:**  
   Informal sub-stockists operate on ₹5,000 to ₹10,000 of working capital and carry fewer than 15 cases. Because they cannot absorb channel volatility, small delivery delays trigger instant stockouts at retail stores, producing the **~20% out-of-stock (OOS) rate** observed in the field.

3. **The Freight Cost Truth:**  
   Establishing a dedicated rural cross-dock hub in Varanasi is **an availability and OTIF enabler, not a freight cost-cutting exercise**. The delivered logistics cost drops from ₹74.55 to ₹71.86 per case—a net variance of just -₹2.69/case (-3.6%). The hub pays for itself not through cheap freight, but by lifting composite distributor OTIF from ~56% to ~90% and protecting shelf share.

---

## 💻 System Architecture & Analytics Engine (`src/`)

Rather than writing generic strategy slides, I implemented the operational logic in Python (`src/`) backed by an embedded SQLite database (`data/itc_operations.db`).

```
                    ┌───────────────────────────────────────────────┐
                    │      data/itc_operations.db (SQLite)          │
                    │  1,200 Orders | 150 Inventory | 300 Dispatches │
                    └───────────────────────┬───────────────────────┘
                                            │ SQL Queries & Views
                                            ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                                 src/ (Analytics Modules)                                   │
├───────────────────────────┬───────────────────────────┬───────────────────────────────────┤
│ demand_analytics/         │ inventory_engine/         │ transport_optimization/           │
│ • Holt's Linear Smoothing │ • Periodic Review (R, S)  │ • Dual-Constraint Load Optimizer  │
│ • WAPE & Forecast Bias    │ • Stochastic Safety Stock │   (Tata Ace Weight & Cube)        │
│                           │ • 9-Box ABC-XYZ Matrix    │ • Sourcing LP (SciPy HiGHS)       │
└───────────────────────────┴───────────────────────────┴───────────────────────────────────┘
                                            │
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │           Execution & Control Interfaces       │
                    │ • run_decision_support.py (07:00 AM CLI)      │
                    │ • app.py (Streamlit Web Control Tower)        │
                    └───────────────────────────────────────────────┘
```

### Why I Made These Technical Choices:

* **Periodic Review $(R, S)$ over Continuous Review $(s, Q)$:**  
  Continuous review models assume real-time IoT or telemetry signals on store shelves. Rural kiranas in eastern UP do not have RFID or automated order triggers; they are visited once a week or once a fortnight on fixed salesperson beats. Periodic review is the only realistic representation of how FMCG beat distribution works.

* **Dual-Constraint Weight-Cube Pairing over Single Knapsack:**  
  Delivery vehicles face two physical boundaries simultaneously: gross vehicle payload (kg) and volumetric capacity (m³).
  * *Aashirvaad Atta 1kg:* Dense cargo ($434\text{ kg/m}^3$). If you fill a 1.25T Tata Ace with only Atta, you hit the 1,250 kg weight limit while utilizing less than 60% of vehicle volume.
  * *Bingo! Snacks 45g:* Volumetric cargo ($44\text{ kg/m}^3$). If you load only Bingo, the cargo bay fills up ("cubes out") at just 210 kg payload (17% weight utilization), meaning you pay freight for shipping empty air.
  * *The Pairing Heuristic:* My optimizer calculates the integer case balance (e.g., 70 cases Atta + 26 cases Bingo!) to drive both weight and volume utilization into the 80–90% range under real-world crate stacking constraints.

* **SciPy HiGHS Linear Programming over PuLP / Proprietary Solvers:**  
  Inbound factory-to-depot sourcing is modeled as a classic transportation problem minimizing $\sum c_{ij} X_{ij}$. I chose `scipy.optimize.linprog` with the HiGHS simplex method because it runs on standard Python without requiring external commercial solver binaries (like Gurobi or CPLEX) and solves in under 5 milliseconds.

* **Embedded SQLite Database with Analytical SQL Views:**  
  Instead of hardcoding Python dictionaries, `src/data_loader.py` generates 1,200 synthetic orders across 8 districts in Eastern UP & Bihar and loads them into `data/itc_operations.db`. Pre-compiled SQL views isolate analytical reporting from raw transactional data:
  * `vw_stockout_risk_watchlist`: Flags items below reorder point and computes the daily case deficit.
  * `vw_carrier_otif_summary`: Calculates Fill Rate %, On-Time %, and composite OTIF % across transporter vendors.
  * `vw_order_cut_diagnostics`: Isolates why orders failed delivery (Depot Stockout vs. Vehicle Capacity vs. Credit Hold) and quantifies lost turnover in rupees.

---

## 📊 The Financial & Supply Chain Model (`model/itc_model.xlsx`)

The financial model is a 10-sheet dynamic Excel workbook built from scratch in `model/generate_sheets.py` and validated by `model/verify_formulas.py` (296 verified formulas, 0 circular references, 0 `#NAME?` errors).

### Workbook Structure:
1. `Summary_Dashboard`: High-level operational, service-level, and financial variance (Current vs. Hub Setup).
2. `Assumptions_Inputs`: Sourced parameters (volumes, distances, freight rates, margins, holding costs).
3. `District_Baseline`: Inter-node distance matrix (Azamgarh cluster), circuity factor (1.20×), and vehicle payload/cube factors.
4. `Inventory_Logic`: Stochastic periodic safety stock formulas and stockout probability modeling.
5. `Delivered_Cost_Build`: Step-by-step cost build per case (Trunk + Handling + Rent + Carrying + Milk-Run + Transit Loss).
6. `Revenue_and_Financials`: 3-year phased DCF cash flow build, NPV @ 12% WACC, IRR, and Simple Payback.
7. `Sensitivity_Analysis`: Scenario stress-testing across demand variance, freight inflation, and out-of-stock recapture rates.
8. `Scorecard_and_OTIF`: Composite OTIF framework ($\text{On-Time \%} \times \text{Fill Rate \%}$) and carrier vendor benchmarking.
9. `Compliance`: Statutory warehousing and logistics EHS compliance matrix.
10. `Checks`: 10 automated mathematical integrity checks (all reading `PASS`).

### Defending the Numbers in an Interview:

| Metric | Modeled Value | Honest Engineering Defense |
|---|---|---|
| **Simple Payback** | **15.1 Months** | Matches formula `=ABS(B33)/(C23-C28)*12`. It takes ~15 months to recover the initial leased hub capex from operational margin generation. |
| **Modeled IRR** | **~114%** | This high return is an output of an **asset-light leased cross-dock model** (low upfront capex of ~₹65 Cr across 150 hubs) paired with high operating leverage. |
| **Underlying Assumptions** | **50% Recapture & 800 Outlets** | The returns rest on two working assumptions: recapturing 50% of currently lost stockout sales, and onboarding 800 new rural outlets per hub (~5 cases/month). If recapture drops to 25%, payback doubles to ~30 months. I treat this as an optimistic scenario projection, not a guaranteed finding. |
| **Delivered Cost** | **₹74.55 $\rightarrow$ ₹71.86/case** | The saving is only ₹2.69/case (3.6%). The business justification for the hub is **service reliability and shelf presence**, not dramatic freight cost reduction. |

---

## 🛠️ How to Run and Test the Project

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Requires Python 3.9+, pandas, numpy, scipy, openpyxl, plotly, streamlit)*

### 2. Run Automated Unit Tests (8/8 Passing in ~0.02s)
```bash
python -m unittest discover tests
```
Validates:
* Stochastic periodic safety stock formulas and ROP calculations.
* Dual-constraint vehicle weight and volume boundaries.
* SciPy linear program convergence and lane allocations.
* SQLite transactional database integrity, row counts, and OTIF mathematical limits.

### 3. Run the Daily Decision Support System (Terminal CLI)
```bash
python run_decision_support.py
```
Outputs the 07:00 AM morning operational brief:
* Immediate stockout risk alerts and case replenishment requirements.
* Demand forecast error (WAPE) and bias tracking on Aashirvaad Atta.
* Tata Ace dual-constraint load plan (cases Atta + cases Bingo!).
* Haridwar/Panchgram primary plant sourcing allocations.
* Transporter OTIF rankings and order cut root causes.

### 4. Launch the Web Control Tower (Streamlit)
```bash
streamlit run app.py
```
*(Note: If Streamlit is not installed, running `python app.py` automatically falls back to the terminal decision runner).*

### 5. Verify the Excel Workbook Formulas
```bash
python model/verify_formulas.py
```
Audits all 296 formulas in `model/itc_model.xlsx` to confirm zero broken links or invalid function names.

---

## 📂 Repository Structure

```
itc-lastmile-project/
├── app.py                           # Interactive Streamlit operations dashboard & control tower
├── run_decision_support.py          # Daily 07:00 AM dispatch & replenishment CLI runner
├── requirements.txt                 # Project dependencies
├── ITC_LastMile_Project_Report.md   # Comprehensive technical project report (~6,000 words)
├── ITC_LastMile_Presentation_Deck.md# 15-slide presentation deck
├── data/
│   ├── itc_operations.db            # Embedded SQLite relational database
│   └── raw/                         # 4 transactional CSV datasets (orders, stock, dispatch, lanes)
├── src/
│   ├── data_loader.py               # Generates synthetic FMCG datasets and builds SQLite views
│   ├── pipeline.py                  # Master orchestration pipeline chaining all engines
│   ├── demand_analytics/            # Holt's linear smoothing, WAPE, and forecast bias
│   ├── inventory_engine/            # Stochastic safety stock, periodic review (R, S), ABC-XYZ
│   ├── transport_optimization/      # Weight-cube load optimizer & SciPy sourcing LP solver
│   └── performance_scorecards/      # Composite OTIF and carrier benchmarking
├── model/
│   ├── generate_sheets.py           # Automated formula-driven Excel generator
│   ├── verify_formulas.py           # Automated OpenXML formula syntax auditor
│   └── itc_model.xlsx               # 10-sheet quantitative supply chain model
└── tests/
    ├── test_inventory_engine.py     # Unit tests for safety stock and ABC-XYZ
    ├── test_transport_optimization.py# Unit tests for vehicle loading and sourcing LP
    └── test_data_loader.py          # Unit tests for database integrity and OTIF views
```

---

## ⚠️ Limitations & Notes for an Interview

1. **Synthetic Data Calibration:**  
   The 1,200 orders and distance matrix are realistic synthetic benchmarks calibrated to public FMCG disclosures and eastern Uttar Pradesh geography. In an actual deployment at ITC, these scripts would connect directly to live SAP ERP / DMS extraction tables.
2. **Physical Packaging Realities:**  
   The load optimizer uses a dual-constraint mathematical knapsack. In an actual warehouse bay, corrugated box stackability (crush resistance), pallet footprints, and parcel orientation mean achieved utilization is typically 80–88%, which is accounted for in the model.
3. **Pilot Before Rollout:**  
   A capital investment of ₹430 Cr across 150 hubs should never be committed all at once. The recommended roadmap begins with a single cluster pilot (Azamgarh / Jaunpur / Varanasi) to validate actual retail demand recapture before expanding regionally.

---
*Developed by Ujjwal Deep (BIT Mesra, Mechanical Engineering) for Integrated Operations & Supply Chain Analytics evaluation.*
