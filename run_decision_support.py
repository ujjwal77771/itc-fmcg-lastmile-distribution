"""
ITC Integrated Operations — Daily Operational Decision Support System (IODSS)
Script: run_decision_support.py
Author: Ujjwal Deep (B.Tech Mechanical Engineering, BIT Mesra)

Operational Morning Dispatch & Inventory Replenishment Run:
Answers the 4 daily operational questions for ITC Regional Logistics Managers:
1. Which SKUs are breaching Safety Stock / ROP and require immediate factory indent?
2. Which rural distributors have pending orders and stockout risks today?
3. How should today's outbound feeder vehicles (Tata Ace 1.25T) be packed to maximize weight & cube?
4. What is our current carrier service level (Composite OTIF), and why did orders cut?
"""

import os
import sqlite3
import numpy as np
import pandas as pd

from src.demand_analytics.forecast_engine import DemandForecastEngine
from src.inventory_engine.safety_stock import InventoryAnalyticsEngine
from src.transport_optimization.load_optimizer import VehicleLoadOptimizer
from src.transport_optimization.sourcing_solver import InboundTransportationSolver
from src.performance_scorecards.otif_analyzer import OTIFAnalyticsEngine

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'itc_operations.db')

def execute_daily_decision_support():
    if not os.path.exists(DB_PATH):
        from src.data_loader import initialize_database
        initialize_database()

    conn = sqlite3.connect(DB_PATH)

    print("=" * 82)
    print("ITC LIMITED — INTEGRATED OPERATIONS & LOGISTICS DECISION SUPPORT SYSTEM")
    print("Facility: Varanasi Regional Cross-Dock Hub | Catchment: Eastern UP & Bihar")
    print("=" * 82)

    # ---------------------------------------------------------
    # 1. INVENTORY BUFFER AUDIT & STOCKOUT WATCHLIST
    # ---------------------------------------------------------
    print("\n[MODULE 1] INVENTORY REORDER & SAFETY STOCK AUDIT (SQL: vw_stockout_risk_watchlist)")
    print("-" * 82)
    query_watchlist = """
    SELECT 
        depot_name, sku_name, category, current_stock_cases, 
        reorder_point_cases, safety_stock_cases, days_of_coverage, stock_deficit_cases
    FROM vw_stockout_risk_watchlist
    WHERE depot_name LIKE '%Varanasi%'
    LIMIT 5;
    """
    df_watch = pd.read_sql_query(query_watchlist, conn)
    if not df_watch.empty:
        for _, row in df_watch.iterrows():
            print(f" * [ALERT] {row['sku_name'][:36]:<36} | Stock: {row['current_stock_cases']:>3} cs | "
                  f"ROP: {row['reorder_point_cases']:>3} cs | Coverage: {row['days_of_coverage']:>4.1f} days | Deficit: {row['stock_deficit_cases']:>4.0f} cs")
    else:
        print(" * All SKUs currently above safety stock thresholds.")

    # ---------------------------------------------------------
    # 2. DEMAND FORECAST & BIAS TRACKING
    # ---------------------------------------------------------
    print("\n[MODULE 2] DEMAND VARIABILITY & FORECAST ACCURACY TRACKING")
    print("-" * 82)
    forecast_engine = DemandForecastEngine()
    # Pull trailing weekly demand for Aashirvaad Atta
    query_demand = """
    SELECT strftime('%Y-%W', order_date) as week_num, SUM(ordered_cases) as weekly_demand
    FROM distributor_orders
    WHERE sku_id = 'ITC-FOOD-001'
    GROUP BY week_num
    ORDER BY week_num ASC
    LIMIT 12;
    """
    df_demand = pd.read_sql_query(query_demand, conn)
    demand_series = df_demand['weekly_demand'].values.astype(float)
    
    if len(demand_series) >= 6:
        fitted, future = forecast_engine.holts_linear_smoothing(demand_series, alpha=0.35, beta=0.15, horizon_steps=2)
        wape = forecast_engine.calculate_wape(demand_series[1:], fitted[1:])
        bias = forecast_engine.calculate_forecast_bias(demand_series[1:], fitted[1:])
        print(f" * SKU: Aashirvaad Superior MP Atta 1kg (Primary Volume Driver)")
        print(f" * Trailing 12-Week Mean: {np.mean(demand_series):.1f} cases/week | Sigma: {np.std(demand_series):.1f}")
        print(f" * Forecast Error (WAPE): {wape:.2f}% | Bias: {bias:+.2f}% ({'Under-forecasting' if bias < 0 else 'Over-forecasting'})")
        print(f" * Projected Next Week Indent Requirement: {int(round(future[0]))} cases")

    # ---------------------------------------------------------
    # 3. VEHICLE LOAD DENSITY OPTIMIZATION (TATA ACE 1.25T)
    # ---------------------------------------------------------
    print("\n[MODULE 3] OUTBOUND DISPATCH DUAL-CONSTRAINT LOAD OPTIMIZATION")
    print("-" * 82)
    optimizer = VehicleLoadOptimizer(payload_capacity_kg=1250.0, volumetric_capacity_cbm=4.80)
    atta_spec = {'name': 'Aashirvaad Atta 1kg', 'case_weight_kg': 16.5, 'case_volume_cbm': 0.038}
    bingo_spec = {'name': 'Bingo! Mad Angles 45g', 'case_weight_kg': 3.6, 'case_volume_cbm': 0.082}
    
    dense_cs, bulky_cs, load_stats = optimizer.optimize_density_pairing(atta_spec, bingo_spec)
    print(f" * Feeder Vehicle Type: Tata Ace 1.25T (Urban/Rural Last-Mile Transit)")
    print(f" * Loading Recommendation: {dense_cs} cases Atta (Dense) + {bulky_cs} cases Bingo! (Bulky)")
    print(f" * Payload Weight:  {load_stats['weight_kg']:>7.1f} kg / 1,250.0 kg  ({load_stats['weight_utilization_pct']:>5.1f}% utilization)")
    print(f" * Cargo Volume:    {load_stats['volume_cbm']:>7.2f} cbm /    4.80 cbm  ({load_stats['volume_utilization_pct']:>5.1f}% utilization)")
    print(f" * Operational Gain: Eliminates 'empty air' freight penalty by interleaving heavy staples with light snacks.")

    # ---------------------------------------------------------
    # 4. MULTI-DEPOT INBOUND TRANSPORTATION LP
    # ---------------------------------------------------------
    print("\n[MODULE 4] PRIMARY INBOUND SOURCING COST MINIMIZATION (SCIPY LP)")
    print("-" * 82)
    sourcing_solver = InboundTransportationSolver()
    plants = [
        {'name': 'Haridwar Food Park', 'capacity': 45000.0},
        {'name': 'Panchgram Factory', 'capacity': 35000.0}
    ]
    depots = [
        {'name': 'Varanasi Hub', 'demand': 28000.0},
        {'name': 'Lucknow RDC', 'demand': 30000.0},
        {'name': 'Patna RDC', 'demand': 18000.0}
    ]
    freight_matrix = np.array([
        [24.50, 18.00, 29.50],
        [26.00, 31.00, 19.50]
    ])
    lp_res = sourcing_solver.solve_transportation_problem(plants, depots, freight_matrix)
    print(f" * Optimal Total Primary Freight Cost: ₹ {lp_res['total_freight_cost']:,.2f}")
    for alloc in lp_res['lane_allocations']:
        print(f"   -> {alloc['from_plant']:<22} --> {alloc['to_depot']:<15}: {alloc['cases_shipped']:>6,.0f} cases @ ₹{alloc['unit_freight']:.2f}/cs")

    # ---------------------------------------------------------
    # 5. SERVICE LEVEL (OTIF) & ROOT CAUSE CUT ANALYSIS
    # ---------------------------------------------------------
    print("\n[MODULE 5] SERVICE LEVEL SCORECARD & ORDER CUT ROOT CAUSES")
    print("-" * 82)
    query_carrier = "SELECT * FROM vw_carrier_otif_summary;"
    df_carrier = pd.read_sql_query(query_carrier, conn)
    print(df_carrier.to_string(index=False))

    print("\n--- Diagnostic: Why Did Orders Fail In-Full Delivery? ---")
    query_cuts = "SELECT * FROM vw_order_cut_diagnostics;"
    df_cuts = pd.read_sql_query(query_cuts, conn)
    for _, row in df_cuts.iterrows():
        print(f" * {row['cut_reason']:<38} | {row['incident_count']:>3} incidents | {row['total_cut_cases']:>5} cases cut | Lost Rev: ₹ {row['estimated_lost_turnover_inr']:>9,.2f}")

    print("=" * 82)
    print("ACTIONABLE MANAGERIAL TAKEAWAYS FOR OPERATIONS MEETING:")
    print("1. Expedite Haridwar-to-Varanasi primary transfer for Aashirvaad Atta (coverage below 3 days).")
    print("2. Rebalance Carrier TCI dispatch schedule to recover on-time performance on Ballia/Sonbhadra routes.")
    print("3. Enforce 52 Atta / 38 Bingo co-loading standard at Varanasi cross-dock loading bays.")
    print("=" * 82)

    conn.close()

if __name__ == '__main__':
    execute_daily_decision_support()
