"""
ITC Integrated Operations — Regional Logistics Decision Support Control Tower
File: app.py
Author: Ujjwal Deep (B.Tech Mechanical Engineering, BIT Mesra)

Interactive Operations Dashboard & Decision Support System:
- Tab 1: Operational Summary & Regional KPIs
- Tab 2: Stochastic Safety Stock & Inventory Buffer Calculator
- Tab 3: Dual-Constraint Vehicle Packing Optimizer (Tata Ace 1.25T)
- Tab 4: Multi-Depot Inbound Sourcing Optimizer (SciPy LP)
- Tab 5: Distributor OTIF & Order Cut Diagnostics

Launch:
    streamlit run app.py
"""

import sys
import os

try:
    import streamlit as st
    import pandas as pd
    import numpy as np
    import sqlite3
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

if not STREAMLIT_AVAILABLE:
    print("=" * 75)
    print("ITC Integrated Operations Decision Support System")
    print("=" * 75)
    print("Note: 'streamlit' is not currently installed in this environment.")
    print("To launch the interactive web dashboard:")
    print("    pip install streamlit")
    print("    streamlit run app.py")
    print("-" * 75)
    print("Launching terminal decision support engine instead...\n")
    import run_decision_support
    run_decision_support.execute_daily_decision_support()
    sys.exit(0)

# -------------------------------------------------------------
# STREAMLIT APPLICATION LOGIC
# -------------------------------------------------------------
st.set_page_config(
    page_title="ITC Integrated Operations Control Tower",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'itc_operations.db')

@st.cache_data
def get_db_connection():
    if not os.path.exists(DB_PATH):
        from src.data_loader import initialize_database
        initialize_database()
    return sqlite3.connect(DB_PATH, check_same_thread=False)

conn = get_db_connection()

# Sidebar
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/ITC_Limited_Logo.svg/300px-ITC_Limited_Logo.svg.png", width=120)
st.sidebar.title("ITC Integrated Operations")
st.sidebar.markdown("**Decision Support System (IODSS)**")
st.sidebar.markdown("*Varanasi Rural Cross-Dock Hub*")
st.sidebar.markdown("---")

nav_option = st.sidebar.radio(
    "Navigation Modules:",
    [
        "1. Executive Control Tower",
        "2. Safety Stock & Buffer Optimizer",
        "3. Dual-Constraint Vehicle Loading",
        "4. Inbound Primary Sourcing (LP)",
        "5. Service Level & OTIF Diagnostics"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Author:** Ujjwal Deep\n\n"
    "B.Tech Mechanical Engineering, BIT Mesra\n\n"
    "*Role Scope:* Integrated Operations / Logistics & Warehousing"
)

# -------------------------------------------------------------
# TAB 1: EXECUTIVE CONTROL TOWER
# -------------------------------------------------------------
if nav_option == "1. Executive Control Tower":
    st.title("📦 ITC Integrated Operations Control Tower")
    st.caption("Real-Time Visibility across Eastern UP & Bihar FMCG Last-Mile Distribution")

    # High-level Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Delivered Cases (90d)", value="28,197 cs", delta="+12.4% vs LY")
    with col2:
        st.metric(label="Composite OTIF", value="78.1%", delta="+22.1% pts (Post-Hub)")
    with col3:
        st.metric(label="Safety Stock Buffer Reduction", value="68.4%", delta="-₹41.2L Working Capital")
    with col4:
        st.metric(label="Logistics Cost per Case", value="₹ 63.22", delta="-₹ 14.51 / case (-18.7%)")

    st.markdown("---")
    
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("🚨 Immediate Stockout & Replenishment Watchlist")
        df_watch = pd.read_sql_query("SELECT * FROM vw_stockout_risk_watchlist LIMIT 6", conn)
        st.dataframe(
            df_watch[['depot_name', 'sku_name', 'current_stock_cases', 'reorder_point_cases', 'days_of_coverage', 'stock_deficit_cases']],
            column_config={
                'depot_name': 'Depot / Hub',
                'sku_name': 'SKU Description',
                'current_stock_cases': 'On-Hand (cs)',
                'reorder_point_cases': 'ROP (cs)',
                'days_of_coverage': 'Coverage (d)',
                'stock_deficit_cases': 'Deficit (cs)'
            },
            hide_index=True,
            use_container_width=True
        )

    with col_right:
        st.subheader("🚚 Carrier Fulfillment Performance")
        df_carrier = pd.read_sql_query("SELECT * FROM vw_carrier_otif_summary", conn)
        st.dataframe(
            df_carrier[['carrier_name', 'total_orders', 'case_fill_rate_pct', 'on_time_shipment_pct', 'composite_otif_pct']],
            column_config={
                'carrier_name': 'Logistics Service Provider',
                'total_orders': 'Orders',
                'case_fill_rate_pct': 'Fill Rate %',
                'on_time_shipment_pct': 'On-Time %',
                'composite_otif_pct': 'Composite OTIF %'
            },
            hide_index=True,
            use_container_width=True
        )

# -------------------------------------------------------------
# TAB 2: SAFETY STOCK OPTIMIZER
# -------------------------------------------------------------
elif nav_option == "2. Safety Stock & Buffer Optimizer":
    st.title("📊 Stochastic Inventory Buffer & Safety Stock Simulator")
    st.markdown("Quantifying inventory reduction via **Square-Root Lead Time Law** and **Periodic Review Optimization**.")

    from src.inventory_engine.safety_stock import InventoryAnalyticsEngine
    engine = InventoryAnalyticsEngine()

    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Operational Parameters")
        sku_choice = st.selectbox("Select Benchmark SKU:", [
            "Aashirvaad Superior MP Atta 1kg (High Volume Staple)",
            "Sunfeast Dark Fantasy 300g (Medium Velocity)",
            "Bingo! Mad Angles 45g (High Volatility Snack)"
        ])
        
        d_mean = st.slider("Daily Demand Mean (cases/day):", 10.0, 100.0, 36.0, 1.0)
        d_std = st.slider("Daily Demand Std Dev (cases/day):", 2.0, 30.0, 14.0, 1.0)
        csl = st.select_slider("Target Cycle Service Level:", options=[0.90, 0.95, 0.98, 0.99], value=0.95)

    with c2:
        st.subheader("Current Setup vs Proposed Regional Hub Comparison")
        
        # Current Setup: R=12d, L=4d, sigma_L=3d
        ss_cur = engine.calculate_periodic_safety_stock(12.0, 4.0, d_mean, d_std, 3.0, csl)
        rop_cur = engine.calculate_reorder_point(4.0, d_mean, ss_cur)
        
        # Proposed Hub: R=6d, L=1.5d, sigma_L=0.5d
        ss_prop = engine.calculate_periodic_safety_stock(6.0, 1.5, d_mean, d_std, 0.5, csl)
        rop_prop = engine.calculate_reorder_point(1.5, d_mean, ss_prop)
        
        red_cases = ss_cur - ss_prop
        red_pct = (red_cases / ss_cur) * 100.0

        m1, m2, m3 = st.columns(3)
        m1.metric("Current Safety Stock", f"{int(round(ss_cur))} cases", "R=12d, L=4.0d, σ_L=3.0d")
        m2.metric("Proposed Hub Safety Stock", f"{int(round(ss_prop))} cases", f"-{red_pct:.1f}% reduction")
        m3.metric("Buffer Freed", f"{int(round(red_cases))} cases", "Working Capital Unlocked")

        chart_data = pd.DataFrame({
            'Setup': ['Current Informal Depots', 'Proposed Cross-Dock Hub'],
            'Safety Stock (cases)': [round(ss_cur, 1), round(ss_prop, 1)],
            'Reorder Point (cases)': [round(rop_cur, 1), round(rop_prop, 1)]
        })
        st.bar_chart(chart_data.set_index('Setup'))

# -------------------------------------------------------------
# TAB 3: VEHICLE PACKING OPTIMIZER
# -------------------------------------------------------------
elif nav_option == "3. Dual-Constraint Vehicle Loading":
    st.title("🚛 Outbound Vehicle Cube & Payload Density Pairing")
    st.markdown("Eliminating 'Empty Air' freight penalties by interleaving dense staples with volumetric snacks.")

    from src.transport_optimization.load_optimizer import VehicleLoadOptimizer
    opt = VehicleLoadOptimizer(payload_capacity_kg=1250.0, volumetric_capacity_cbm=4.80)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Vehicle Specifications: Tata Ace 1.25T")
        st.write("- **Gross Payload Limit:** 1,250 kg")
        st.write("- **Volumetric Cube Limit:** 4.80 m³")
        st.write("- **Dense Cargo:** Aashirvaad Atta (16.5 kg/cs, 0.038 m³/cs, Density: 434 kg/m³)")
        st.write("- **Bulky Cargo:** Bingo! Snacks (3.6 kg/cs, 0.082 m³/cs, Density: 44 kg/m³)")

    with col2:
        dense_spec = {'name': 'Atta', 'case_weight_kg': 16.5, 'case_volume_cbm': 0.038}
        bulky_spec = {'name': 'Bingo', 'case_weight_kg': 3.6, 'case_volume_cbm': 0.082}
        atta_cs, bingo_cs, stats = opt.optimize_density_pairing(dense_spec, bulky_spec)

        st.subheader("Optimized Manifest Recommendation")
        st.success(f"**Load Plan:** {atta_cs} cases Atta + {bingo_cs} cases Bingo!")
        
        g1, g2 = st.columns(2)
        g1.metric("Weight Utilization", f"{stats['weight_utilization_pct']}%", f"{stats['weight_kg']:.1f} kg")
        g2.metric("Cube Utilization", f"{stats['volume_utilization_pct']}%", f"{stats['volume_cbm']:.2f} m³")

# -------------------------------------------------------------
# TAB 4: PRIMARY SOURCING LP
# -------------------------------------------------------------
elif nav_option == "4. Inbound Primary Sourcing (LP)":
    st.title("🏭 Plant-to-Depot Inbound Transportation Optimizer")
    st.markdown("Formulated as a classic Hitchcock-Koopmans Transportation Linear Program solved via SciPy Simplex.")

    from src.transport_optimization.sourcing_solver import InboundTransportationSolver
    solver = InboundTransportationSolver()

    plants = [
        {'name': 'Haridwar Integrated Food Park', 'capacity': 45000.0},
        {'name': 'Panchgram Manufacturing Unit', 'capacity': 35000.0}
    ]
    depots = [
        {'name': 'Varanasi RDC / Hub', 'demand': 28000.0},
        {'name': 'Lucknow RDC', 'demand': 30000.0},
        {'name': 'Patna RDC', 'demand': 18000.0}
    ]
    freight_costs = np.array([
        [24.50, 18.00, 29.50],
        [26.00, 31.00, 19.50]
    ])
    
    lp_res = solver.solve_transportation_problem(plants, depots, freight_costs)
    
    st.metric("Total Optimal Network Freight Cost", f"₹ {lp_res['total_freight_cost']:,.2f}")
    df_alloc = pd.DataFrame(lp_res['lane_allocations'])
    st.dataframe(df_alloc, use_container_width=True)

# -------------------------------------------------------------
# TAB 5: SERVICE LEVEL & OTIF
# -------------------------------------------------------------
elif nav_option == "5. Service Level & OTIF Diagnostics":
    st.title("🎯 Service Level (OTIF) & Order Cut Diagnostics")
    st.markdown("Decoupling warehouse availability failures from carrier logistics delays.")

    df_cuts = pd.read_sql_query("SELECT * FROM vw_order_cut_diagnostics", conn)
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("Root Causes of Order Incompleteness")
        st.dataframe(df_cuts, use_container_width=True)
        
    with c2:
        st.subheader("Lost Turnover Impact (INR)")
        st.bar_chart(df_cuts.set_index('cut_reason')['estimated_lost_turnover_inr'])

