"""
ITC Integrated Operations — Synthetic Operational Data Generator & Database Loader
Module: src/data_loader.py
Author: Ujjwal Deep (B.Tech Mechanical Engineering, BIT Mesra)

Generates 1,200+ realistic FMCG operational transactions across Eastern UP & Bihar:
1. data/raw/distributor_orders.csv (Order fulfillment, cuts, and delivery tracking)
2. data/raw/inventory_snapshot.csv (Depot stock, safety stock thresholds, and coverage)
3. data/raw/shipment_dispatch_log.csv (Vehicle load utilization and cube-weight manifests)
4. data/raw/distance_matrix.csv (Lanes, transit distance, freight rates)
5. data/itc_operations.db (Embedded SQLite database with relational schema and indexes)
"""

import os
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
RAW_DIR = os.path.join(DATA_DIR, 'raw')
DB_PATH = os.path.join(DATA_DIR, 'itc_operations.db')

SKU_CATALOG = [
    {
        'sku_id': 'ITC-FOOD-001', 'sku_name': 'Aashirvaad Superior MP Atta 1kg',
        'category': 'Foods - Staples', 'density_type': 'Dense',
        'unit_cost_inr': 48.0, 'case_weight_kg': 16.5, 'case_volume_cbm': 0.038,
        'demand_mean': 52.0, 'demand_std': 12.0, 'lead_time': 1.5, 'lead_time_std': 0.4
    },
    {
        'sku_id': 'ITC-FOOD-002', 'sku_name': 'Aashirvaad Select Sharbati Atta 5kg',
        'category': 'Foods - Staples', 'density_type': 'Dense',
        'unit_cost_inr': 240.0, 'case_weight_kg': 25.0, 'case_volume_cbm': 0.052,
        'demand_mean': 22.0, 'demand_std': 7.5, 'lead_time': 1.5, 'lead_time_std': 0.4
    },
    {
        'sku_id': 'ITC-FOOD-003', 'sku_name': 'Sunfeast Dark Fantasy Choco Fills 300g',
        'category': 'Foods - Biscuits', 'density_type': 'Medium',
        'unit_cost_inr': 95.0, 'case_weight_kg': 7.2, 'case_volume_cbm': 0.045,
        'demand_mean': 34.0, 'demand_std': 8.0, 'lead_time': 2.0, 'lead_time_std': 0.5
    },
    {
        'sku_id': 'ITC-FOOD-004', 'sku_name': 'Sunfeast Bounce Cream 100g',
        'category': 'Foods - Biscuits', 'density_type': 'Medium',
        'unit_cost_inr': 30.0, 'case_weight_kg': 6.0, 'case_volume_cbm': 0.040,
        'demand_mean': 45.0, 'demand_std': 10.0, 'lead_time': 2.0, 'lead_time_std': 0.5
    },
    {
        'sku_id': 'ITC-FOOD-005', 'sku_name': 'Bingo! Mad Angles Achaari Masti 45g',
        'category': 'Foods - Snacks', 'density_type': 'Bulky',
        'unit_cost_inr': 20.0, 'case_weight_kg': 3.6, 'case_volume_cbm': 0.082,
        'demand_mean': 40.0, 'demand_std': 11.0, 'lead_time': 1.5, 'lead_time_std': 0.3
    },
    {
        'sku_id': 'ITC-FOOD-006', 'sku_name': 'Bingo! Tedhe Medhe Masala 50g',
        'category': 'Foods - Snacks', 'density_type': 'Bulky',
        'unit_cost_inr': 20.0, 'case_weight_kg': 4.0, 'case_volume_cbm': 0.085,
        'demand_mean': 48.0, 'demand_std': 13.0, 'lead_time': 1.5, 'lead_time_std': 0.3
    },
    {
        'sku_id': 'ITC-FOOD-007', 'sku_name': 'YiPPee! Magic Masala Noodles 280g',
        'category': 'Foods - Instant Noodles', 'density_type': 'Bulky',
        'unit_cost_inr': 55.0, 'case_weight_kg': 5.5, 'case_volume_cbm': 0.070,
        'demand_mean': 38.0, 'demand_std': 9.5, 'lead_time': 2.0, 'lead_time_std': 0.5
    },
    {
        'sku_id': 'ITC-PCP-001', 'sku_name': 'Fiama Gel Bar Peach & Avocado 125g',
        'category': 'Personal Care - Soaps', 'density_type': 'Dense',
        'unit_cost_inr': 68.0, 'case_weight_kg': 12.5, 'case_volume_cbm': 0.028,
        'demand_mean': 18.0, 'demand_std': 5.0, 'lead_time': 3.0, 'lead_time_std': 0.6
    },
    {
        'sku_id': 'ITC-PCP-002', 'sku_name': 'Savlon Moisture Shield Soap 100g',
        'category': 'Personal Care - Health', 'density_type': 'Dense',
        'unit_cost_inr': 38.0, 'case_weight_kg': 14.0, 'case_volume_cbm': 0.030,
        'demand_mean': 28.0, 'demand_std': 6.0, 'lead_time': 2.5, 'lead_time_std': 0.5
    },
    {
        'sku_id': 'ITC-AGB-001', 'sku_name': 'Mangaldeep Temple Gold Agarbatti',
        'category': 'Agarbatti & Dhoop', 'density_type': 'Bulky',
        'unit_cost_inr': 45.0, 'case_weight_kg': 4.8, 'case_volume_cbm': 0.065,
        'demand_mean': 24.0, 'demand_std': 7.0, 'lead_time': 2.0, 'lead_time_std': 0.4
    }
]

DISTRIBUTORS = [
    {'distributor_id': 'DIST-GHAZIPUR', 'distributor_name': 'Ghazipur Rural Distribution Depot', 'district': 'Ghazipur', 'distance_from_hub_km': 72.0},
    {'distributor_id': 'DIST-JAUNPUR', 'distributor_name': 'Jaunpur Consumer Supplies Hub', 'district': 'Jaunpur', 'distance_from_hub_km': 65.0},
    {'distributor_id': 'DIST-MIRZAPUR', 'distributor_name': 'Mirzapur Commercial Trading Co.', 'district': 'Mirzapur', 'distance_from_hub_km': 58.0},
    {'distributor_id': 'DIST-CHANDAULI', 'distributor_name': 'Chandauli Last-Mile Agency', 'district': 'Chandauli', 'distance_from_hub_km': 32.0},
    {'distributor_id': 'DIST-BHADOHI', 'distributor_name': 'Bhadohi Rural Agro-Retailer', 'district': 'Bhadohi', 'distance_from_hub_km': 45.0},
    {'distributor_id': 'DIST-AZAMGARH', 'distributor_name': 'Azamgarh Regional FMCG Point', 'district': 'Azamgarh', 'distance_from_hub_km': 105.0},
    {'distributor_id': 'DIST-BALLIA', 'distributor_name': 'Ballia Border FMCG Stockist', 'district': 'Ballia', 'distance_from_hub_km': 140.0},
    {'distributor_id': 'DIST-SONBHADRA', 'distributor_name': 'Sonbhadra Mining Belt Logistics', 'district': 'Sonbhadra', 'distance_from_hub_km': 115.0}
]

CARRIERS = [
    {'carrier_id': 'CARR-TCI', 'carrier_name': 'Transport Corporation of India (TCI)'},
    {'carrier_id': 'CARR-VRL', 'carrier_name': 'VRL Logistics Eastern Fleet'},
    {'carrier_id': 'CARR-GATI', 'carrier_name': 'Gati KWE Express Cargo'},
    {'carrier_id': 'CARR-LOCAL', 'carrier_name': 'Varanasi Regional Dedicated Fleet'}
]

def generate_distributor_orders(n_orders: int = 1200) -> pd.DataFrame:
    """Generates realistic order fulfillment records across 90 operating days."""
    np.random.seed(42)
    start_date = datetime(2026, 8, 1)
    
    rows = []
    for i in range(1, n_orders + 1):
        order_id = f"ORD-{20260000 + i}"
        day_offset = np.random.randint(0, 90)
        order_date = start_date + timedelta(days=int(day_offset))
        
        dist = np.random.choice(DISTRIBUTORS)
        sku = np.random.choice(SKU_CATALOG)
        carrier = np.random.choice(CARRIERS)
        
        # Demand calculation
        ordered_cases = int(max(5, round(np.random.normal(sku['demand_mean'] * 0.7, sku['demand_std'] * 0.5))))
        
        # Cut calculation (simulating stockouts, vehicle capacity limits, credit checks)
        cut_prob = np.random.rand()
        if cut_prob < 0.88:
            cut_cases = 0
            cut_reason = "None"
        elif cut_prob < 0.95:
            cut_cases = int(np.random.choice([2, 5, 10]))
            cut_cases = min(cut_cases, ordered_cases)
            cut_reason = "Depot Stockout (Safety Stock Breached)"
        elif cut_prob < 0.98:
            cut_cases = int(round(ordered_cases * 0.3))
            cut_reason = "Vehicle Weight/Cube Constraint"
        else:
            cut_cases = ordered_cases
            cut_reason = "Distributor Credit Limit Hold"
            
        delivered_cases = ordered_cases - cut_cases
        
        # On-Time delivery simulation
        committed_lead_time_days = 2
        committed_date = order_date + timedelta(days=committed_lead_time_days)
        
        # Delay probabilities based on carrier and distance
        delay_chance = 0.08 if dist['distance_from_hub_km'] < 80 else 0.16
        if np.random.rand() < delay_chance:
            delay_days = int(np.random.choice([1, 2, 3]))
        else:
            delay_days = 0
            
        actual_date = committed_date + timedelta(days=delay_days)
        
        on_time_flag = 1 if actual_date <= committed_date else 0
        in_full_flag = 1 if (ordered_cases > 0 and delivered_cases == ordered_cases) else 0
        otif_flag = 1 if (on_time_flag == 1 and in_full_flag == 1) else 0
        
        rows.append({
            'order_id': order_id,
            'order_date': order_date.strftime('%Y-%m-%d'),
            'distributor_id': dist['distributor_id'],
            'distributor_name': dist['distributor_name'],
            'district': dist['district'],
            'sku_id': sku['sku_id'],
            'sku_name': sku['sku_name'],
            'category': sku['category'],
            'ordered_cases': ordered_cases,
            'delivered_cases': delivered_cases,
            'cut_cases': cut_cases,
            'cut_reason': cut_reason,
            'order_value_inr': round(ordered_cases * sku['unit_cost_inr'], 2),
            'delivered_value_inr': round(delivered_cases * sku['unit_cost_inr'], 2),
            'committed_delivery_date': committed_date.strftime('%Y-%m-%d'),
            'actual_delivery_date': actual_date.strftime('%Y-%m-%d'),
            'carrier_id': carrier['carrier_id'],
            'carrier_name': carrier['carrier_name'],
            'on_time_flag': on_time_flag,
            'in_full_flag': in_full_flag,
            'otif_flag': otif_flag
        })
        
    return pd.DataFrame(rows)

def generate_inventory_snapshot() -> pd.DataFrame:
    """Generates snapshot of warehouse stock, safety stock thresholds, and coverage."""
    np.random.seed(42)
    rows = []
    
    # We audit 2 primary facilities: Proposed Varanasi Rural Cross-Dock Hub vs Lucknow Central RDC
    facilities = [
        {'depot_id': 'HUB-VARANASI', 'depot_name': 'Varanasi Rural Cross-Dock Hub (Integrated)', 'cycle_review_days': 6.0},
        {'depot_id': 'RDC-LUCKNOW', 'depot_name': 'Lucknow Mother RDC (Traditional Setup)', 'cycle_review_days': 12.0}
    ]
    
    for fac in facilities:
        for sku in SKU_CATALOG:
            d_mean = sku['demand_mean']
            d_std = sku['demand_std']
            l_mean = sku['lead_time'] if fac['depot_id'] == 'HUB-VARANASI' else sku['lead_time'] * 2.2
            l_std = sku['lead_time_std'] if fac['depot_id'] == 'HUB-VARANASI' else sku['lead_time_std'] * 2.5
            r_days = fac['cycle_review_days']
            
            # Stochastic formula: SS = z * sqrt((R+L)*sigma_d^2 + d^2 * sigma_L^2)
            z_95 = 1.645
            variance_demand = (r_days + l_mean) * (d_std ** 2)
            variance_lead = (d_mean ** 2) * (l_std ** 2)
            ss = z_95 * np.sqrt(variance_demand + variance_lead)
            
            rop = (d_mean * l_mean) + ss
            order_up_to = (d_mean * (r_days + l_mean)) + ss
            
            # Simulate current physical stock
            stock_ratio = np.random.uniform(0.70, 1.35)
            current_stock = int(round(ss * stock_ratio))
            in_transit = int(round(d_mean * l_mean * np.random.choice([0.0, 0.5, 1.0])))
            
            days_coverage = round((current_stock + in_transit) / max(1.0, d_mean), 1)
            stockout_risk = 1 if current_stock < (rop * 0.75) else 0
            replenish_trigger = 1 if (current_stock + in_transit) <= rop else 0
            
            rows.append({
                'depot_id': fac['depot_id'],
                'depot_name': fac['depot_name'],
                'sku_id': sku['sku_id'],
                'sku_name': sku['sku_name'],
                'category': sku['category'],
                'unit_cost_inr': sku['unit_cost_inr'],
                'daily_demand_mean': d_mean,
                'daily_demand_std': d_std,
                'lead_time_days': round(l_mean, 1),
                'safety_stock_cases': int(round(ss)),
                'reorder_point_cases': int(round(rop)),
                'order_up_to_cases': int(round(order_up_to)),
                'current_stock_cases': current_stock,
                'in_transit_cases': in_transit,
                'days_of_coverage': days_coverage,
                'stockout_risk_flag': stockout_risk,
                'replenish_trigger_flag': replenish_trigger
            })
            
    return pd.DataFrame(rows)

def generate_shipment_dispatch_log(n_dispatches: int = 300) -> pd.DataFrame:
    """Generates vehicle manifests showing weight and cube utilization."""
    np.random.seed(42)
    start_date = datetime(2026, 8, 1)
    
    rows = []
    vehicle_types = [
        {'type': 'Tata Ace 1.25T (Last-Mile Feeder)', 'weight_cap_kg': 1250.0, 'cube_cap_cbm': 4.80, 'cost_per_km': 18.0},
        {'type': 'Eicher 14T (Hub Linehaul / Milk-run)', 'weight_cap_kg': 9000.0, 'cube_cap_cbm': 32.0, 'cost_per_km': 42.0}
    ]
    
    for i in range(1, n_dispatches + 1):
        dispatch_id = f"DISP-{2026000 + i}"
        day_offset = np.random.randint(0, 90)
        disp_date = start_date + timedelta(days=int(day_offset))
        
        veh = np.random.choice(vehicle_types)
        dist = np.random.choice(DISTRIBUTORS)
        
        # Dual-constraint density optimization: Atta (dense) paired with Bingo/Noodles (bulky)
        # Ratio determined by weight and volume balance
        if 'Tata Ace' in veh['type']:
            atta_cases = int(np.random.randint(45, 65))
            bingo_cases = int(np.random.randint(25, 45))
        else:
            atta_cases = int(np.random.randint(350, 480))
            bingo_cases = int(np.random.randint(220, 310))
            
        total_weight = (atta_cases * 16.5) + (bingo_cases * 3.6)
        total_cube = (atta_cases * 0.038) + (bingo_cases * 0.082)
        
        weight_util = round((total_weight / veh['weight_cap_kg']) * 100.0, 1)
        cube_util = round((total_cube / veh['cube_cap_cbm']) * 100.0, 1)
        
        transit_cost = round(dist['distance_from_hub_km'] * 2.0 * veh['cost_per_km'], 2)
        total_cases = atta_cases + bingo_cases
        cost_per_case = round(transit_cost / max(1, total_cases), 2)
        
        rows.append({
            'dispatch_id': dispatch_id,
            'dispatch_date': disp_date.strftime('%Y-%m-%d'),
            'origin_node': 'Varanasi Rural Cross-Dock Hub',
            'destination_node': dist['distributor_name'],
            'vehicle_type': veh['type'],
            'distance_km': dist['distance_from_hub_km'],
            'cases_dense_atta': atta_cases,
            'cases_bulky_bingo': bingo_cases,
            'total_cases': total_cases,
            'actual_payload_kg': round(total_weight, 1),
            'payload_capacity_kg': veh['weight_cap_kg'],
            'weight_utilization_pct': weight_util,
            'actual_cube_cbm': round(total_cube, 2),
            'cube_capacity_cbm': veh['cube_cap_cbm'],
            'cube_utilization_pct': cube_util,
            'transit_cost_inr': transit_cost,
            'freight_cost_per_case_inr': cost_per_case
        })
        
    return pd.DataFrame(rows)

def generate_distance_matrix() -> pd.DataFrame:
    """Generates supply chain lane distances, transit times, and freight benchmark costs."""
    lanes = [
        # Primary Inbound (Plants to Regional Hubs)
        {'origin': 'PLANT-HARIDWAR', 'origin_name': 'Haridwar Integrated Food Park', 'destination': 'RDC-VARANASI', 'dest_name': 'Varanasi RDC / Hub', 'lane_type': 'Primary Freight (K1)', 'distance_km': 820.0, 'transit_time_hrs': 24.0, 'rate_per_ton_km': 2.80, 'cost_per_case': 24.50},
        {'origin': 'PLANT-HARIDWAR', 'origin_name': 'Haridwar Integrated Food Park', 'destination': 'RDC-LUCKNOW', 'dest_name': 'Lucknow RDC', 'lane_type': 'Primary Freight (K1)', 'distance_km': 540.0, 'transit_time_hrs': 16.0, 'rate_per_ton_km': 2.75, 'cost_per_case': 18.00},
        {'origin': 'PLANT-HARIDWAR', 'origin_name': 'Haridwar Integrated Food Park', 'destination': 'RDC-PATNA', 'dest_name': 'Patna RDC', 'lane_type': 'Primary Freight (K1)', 'distance_km': 1050.0, 'transit_time_hrs': 32.0, 'rate_per_ton_km': 2.90, 'cost_per_case': 29.50},
        {'origin': 'PLANT-PANCHGRAM', 'origin_name': 'Panchgram Manufacturing Unit', 'destination': 'RDC-VARANASI', 'dest_name': 'Varanasi RDC / Hub', 'lane_type': 'Primary Freight (K1)', 'distance_km': 680.0, 'transit_time_hrs': 20.0, 'rate_per_ton_km': 2.70, 'cost_per_case': 26.00},
        {'origin': 'PLANT-PANCHGRAM', 'origin_name': 'Panchgram Manufacturing Unit', 'destination': 'RDC-LUCKNOW', 'dest_name': 'Lucknow RDC', 'lane_type': 'Primary Freight (K1)', 'distance_km': 940.0, 'transit_time_hrs': 28.0, 'rate_per_ton_km': 2.85, 'cost_per_case': 31.00},
        {'origin': 'PLANT-PANCHGRAM', 'origin_name': 'Panchgram Manufacturing Unit', 'destination': 'RDC-PATNA', 'dest_name': 'Patna RDC', 'lane_type': 'Primary Freight (K1)', 'distance_km': 420.0, 'transit_time_hrs': 12.0, 'rate_per_ton_km': 2.65, 'cost_per_case': 19.50},
        
        # Tertiary Last-Mile (Varanasi Hub to Rural Distributors)
        {'origin': 'HUB-VARANASI', 'origin_name': 'Varanasi Hub', 'destination': 'DIST-GHAZIPUR', 'dest_name': 'Ghazipur Rural Depot', 'lane_type': 'Tertiary Freight (K3)', 'distance_km': 72.0, 'transit_time_hrs': 2.5, 'rate_per_ton_km': 4.50, 'cost_per_case': 6.80},
        {'origin': 'HUB-VARANASI', 'origin_name': 'Varanasi Hub', 'destination': 'DIST-JAUNPUR', 'dest_name': 'Jaunpur Rural Point', 'lane_type': 'Tertiary Freight (K3)', 'distance_km': 65.0, 'transit_time_hrs': 2.0, 'rate_per_ton_km': 4.50, 'cost_per_case': 6.20},
        {'origin': 'HUB-VARANASI', 'origin_name': 'Varanasi Hub', 'destination': 'DIST-MIRZAPUR', 'dest_name': 'Mirzapur Central Depot', 'lane_type': 'Tertiary Freight (K3)', 'distance_km': 58.0, 'transit_time_hrs': 1.8, 'rate_per_ton_km': 4.50, 'cost_per_case': 5.70},
        {'origin': 'HUB-VARANASI', 'origin_name': 'Varanasi Hub', 'destination': 'DIST-CHANDAULI', 'dest_name': 'Chandauli Depot', 'lane_type': 'Tertiary Freight (K3)', 'distance_km': 32.0, 'transit_time_hrs': 1.0, 'rate_per_ton_km': 4.80, 'cost_per_case': 4.20},
        {'origin': 'HUB-VARANASI', 'origin_name': 'Varanasi Hub', 'destination': 'DIST-BHADOHI', 'dest_name': 'Bhadohi Depot', 'lane_type': 'Tertiary Freight (K3)', 'distance_km': 45.0, 'transit_time_hrs': 1.5, 'rate_per_ton_km': 4.60, 'cost_per_case': 4.90},
        {'origin': 'HUB-VARANASI', 'origin_name': 'Varanasi Hub', 'destination': 'DIST-AZAMGARH', 'dest_name': 'Azamgarh Depot', 'lane_type': 'Tertiary Freight (K3)', 'distance_km': 105.0, 'transit_time_hrs': 3.5, 'rate_per_ton_km': 4.40, 'cost_per_case': 8.90},
        {'origin': 'HUB-VARANASI', 'origin_name': 'Varanasi Hub', 'destination': 'DIST-BALLIA', 'dest_name': 'Ballia Border Point', 'lane_type': 'Tertiary Freight (K3)', 'distance_km': 140.0, 'transit_time_hrs': 4.5, 'rate_per_ton_km': 4.30, 'cost_per_case': 11.20},
        {'origin': 'HUB-VARANASI', 'origin_name': 'Varanasi Hub', 'destination': 'DIST-SONBHADRA', 'dest_name': 'Sonbhadra Depot', 'lane_type': 'Tertiary Freight (K3)', 'distance_km': 115.0, 'transit_time_hrs': 4.0, 'rate_per_ton_km': 4.40, 'cost_per_case': 9.80}
    ]
    return pd.DataFrame(lanes)

def initialize_database():
    """Generates raw CSVs and builds embedded SQLite database with tables and indexes."""
    os.makedirs(RAW_DIR, exist_ok=True)
    
    print("[1/5] Generating synthetic operational datasets...")
    df_orders = generate_distributor_orders(1200)
    df_inventory = generate_inventory_snapshot()
    df_dispatch = generate_shipment_dispatch_log(300)
    df_distance = generate_distance_matrix()
    
    # Save CSVs
    df_orders.to_csv(os.path.join(RAW_DIR, 'distributor_orders.csv'), index=False)
    df_inventory.to_csv(os.path.join(RAW_DIR, 'inventory_snapshot.csv'), index=False)
    df_dispatch.to_csv(os.path.join(RAW_DIR, 'shipment_dispatch_log.csv'), index=False)
    df_distance.to_csv(os.path.join(RAW_DIR, 'distance_matrix.csv'), index=False)
    print(f"      Saved 4 CSVs to {RAW_DIR}")
    
    print("[2/5] Building embedded SQLite operational database...")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Store dataframes to SQLite
    df_orders.to_sql('distributor_orders', conn, if_exists='replace', index=False)
    df_inventory.to_sql('inventory_snapshot', conn, if_exists='replace', index=False)
    df_dispatch.to_sql('shipment_dispatch_log', conn, if_exists='replace', index=False)
    df_distance.to_sql('distance_matrix', conn, if_exists='replace', index=False)
    
    print("[3/5] Creating operational SQL indexes for sub-second query performance...")
    cursor.execute("CREATE INDEX idx_orders_distributor ON distributor_orders(distributor_id);")
    cursor.execute("CREATE INDEX idx_orders_sku ON distributor_orders(sku_id);")
    cursor.execute("CREATE INDEX idx_orders_date ON distributor_orders(order_date);")
    cursor.execute("CREATE INDEX idx_inventory_depot ON inventory_snapshot(depot_id);")
    cursor.execute("CREATE INDEX idx_inventory_sku ON inventory_snapshot(sku_id);")
    cursor.execute("CREATE INDEX idx_dispatch_dest ON shipment_dispatch_log(destination_node);")
    
    print("[4/5] Creating Analytical Views for Daily Operations...")
    # View 1: Stockout Risk Watchlist
    cursor.execute("""
    CREATE VIEW vw_stockout_risk_watchlist AS
    SELECT 
        depot_name,
        sku_id,
        sku_name,
        category,
        current_stock_cases,
        reorder_point_cases,
        safety_stock_cases,
        days_of_coverage,
        ROUND((reorder_point_cases - current_stock_cases), 1) AS stock_deficit_cases
    FROM inventory_snapshot
    WHERE stockout_risk_flag = 1 OR replenish_trigger_flag = 1
    ORDER BY days_of_coverage ASC;
    """)
    
    # View 2: Carrier OTIF Scorecard
    cursor.execute("""
    CREATE VIEW vw_carrier_otif_summary AS
    SELECT 
        carrier_name,
        COUNT(order_id) AS total_orders,
        SUM(ordered_cases) AS total_ordered_cases,
        SUM(delivered_cases) AS total_delivered_cases,
        ROUND((SUM(delivered_cases) * 100.0 / SUM(ordered_cases)), 2) AS case_fill_rate_pct,
        ROUND((SUM(on_time_flag) * 100.0 / COUNT(order_id)), 2) AS on_time_shipment_pct,
        ROUND((SUM(otif_flag) * 100.0 / COUNT(order_id)), 2) AS composite_otif_pct
    FROM distributor_orders
    GROUP BY carrier_name
    ORDER BY composite_otif_pct DESC;
    """)
    
    # View 3: Order Cut Reason Diagnostics
    cursor.execute("""
    CREATE VIEW vw_order_cut_diagnostics AS
    SELECT 
        cut_reason,
        COUNT(order_id) AS incident_count,
        SUM(cut_cases) AS total_cut_cases,
        ROUND(SUM(cut_cases * (order_value_inr / ordered_cases)), 2) AS estimated_lost_turnover_inr
    FROM distributor_orders
    WHERE cut_cases > 0
    GROUP BY cut_reason
    ORDER BY total_cut_cases DESC;
    """)
    
    conn.commit()
    conn.close()
    print(f"[5/5] Relational database initialized successfully: {DB_PATH}")

if __name__ == '__main__':
    initialize_database()
