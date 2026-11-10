"""
ITC Integrated Operations — Master Pipeline Orchestration Runner
Module: src/pipeline.py
Author: Ujjwal Deep (B.Tech Mechanical Engineering, BIT Mesra)

Chains the daily operational decision workflow end-to-end:
1. Ingests daily distributor orders & inventory snapshots
2. Executes demand forecast error analysis (WAPE / Bias)
3. Computes stochastic periodic-review safety stock & ABC-XYZ matrix
4. Optimizes dual-constraint vehicle loading (Tata Ace / 14T trucks)
5. Solves multi-depot inbound sourcing cost minimization (LP)
6. Evaluates composite OTIF and generates carrier scorecards
"""

from typing import Dict, List, Any
import numpy as np

from src.demand_analytics.forecast_engine import DemandForecastEngine
from src.inventory_engine.safety_stock import InventoryAnalyticsEngine
from src.transport_optimization.load_optimizer import VehicleLoadOptimizer
from src.transport_optimization.sourcing_solver import InboundTransportationSolver
from src.performance_scorecards.otif_analyzer import OTIFAnalyticsEngine

class IntegratedOperationsPipeline:
    """
    Master Decision Support Pipeline for ITC Regional Distribution.
    Executes automated daily replenishment, dispatch, and service level auditing.
    """

    def __init__(self):
        self.forecast_engine = DemandForecastEngine()
        self.inventory_engine = InventoryAnalyticsEngine()
        self.load_optimizer = VehicleLoadOptimizer(payload_capacity_kg=1250.0, volumetric_capacity_cbm=4.80)
        self.sourcing_solver = InboundTransportationSolver()
        self.otif_engine = OTIFAnalyticsEngine()

    def run_daily_operational_cycle(self) -> Dict[str, Any]:
        """
        Runs the daily morning operational planning cycle.
        Returns actionable managerial recommendations.
        """
        results = {}

        # 1. Demand Tracking for Key SKU (Aashirvaad Atta 1kg)
        history = np.array([3200, 3400, 3350, 3600, 3800, 3750, 4100, 4200, 4150, 4400, 4600, 4750], dtype=float)
        fitted, future_4w = self.forecast_engine.holts_linear_smoothing(history, alpha=0.35, beta=0.15, horizon_steps=4)
        wape = self.forecast_engine.calculate_wape(history[1:], fitted[1:])
        bias = self.forecast_engine.calculate_forecast_bias(history[1:], fitted[1:])
        results['demand'] = {
            'wape_pct': round(wape, 2),
            'bias_pct': round(bias, 2),
            'next_week_forecast_cases': int(round(future_4w[0]))
        }

        # 2. Inventory Health & Safety Stock Optimization
        # Current Setup: R=12d, L=4d, d=36/d, sigma_d=14, sigma_L=3d
        ss_cur = self.inventory_engine.calculate_periodic_safety_stock(12.0, 4.0, 36.0, 14.0, 3.0, 0.95)
        # Proposed Hub: R=6d, L=1.5d, d=36/d, sigma_d=14, sigma_L=0.5d
        ss_prop = self.inventory_engine.calculate_periodic_safety_stock(6.0, 1.5, 36.0, 14.0, 0.5, 0.95)
        rop_prop = self.inventory_engine.calculate_reorder_point(lead_time_days=1.5, daily_demand_mean=36.0, safety_stock=ss_prop)
        s_level = self.inventory_engine.calculate_order_up_to_level(6.0, 1.5, 36.0, ss_prop)

        results['inventory'] = {
            'ss_current_cases': round(ss_cur, 1),
            'ss_proposed_cases': round(ss_prop, 1),
            'capital_buffer_reduction_pct': round(((ss_cur - ss_prop) / ss_cur) * 100.0, 1),
            'reorder_point_cases': round(rop_prop, 1),
            'order_up_to_cases': round(s_level, 1)
        }

        # 3. Vehicle Load Optimization (Tata Ace 1.25T)
        atta_sku = {'name': 'Aashirvaad Atta 1kg', 'case_weight_kg': 16.5, 'case_volume_cbm': 0.038}
        snack_sku = {'name': 'Bingo! Mad Angles 45g', 'case_weight_kg': 3.6, 'case_volume_cbm': 0.082}
        dense_cases, bulky_cases, load_stats = self.load_optimizer.optimize_density_pairing(atta_sku, snack_sku)
        results['dispatch_manifest'] = {
            'atta_cases': dense_cases,
            'bingo_cases': bulky_cases,
            'payload_kg': load_stats['weight_kg'],
            'payload_utilization_pct': load_stats['weight_utilization_pct'],
            'volume_cbm': load_stats['volume_cbm'],
            'volume_utilization_pct': load_stats['volume_utilization_pct']
        }

        # 4. Multi-Depot Inbound Transportation Sourcing
        plants = [
            {'name': 'Haridwar Integrated Food Park', 'capacity': 45000.0},
            {'name': 'Panchgram Manufacturing Unit', 'capacity': 35000.0}
        ]
        depots = [
            {'name': 'Varanasi RDC', 'demand': 28000.0},
            {'name': 'Lucknow RDC', 'demand': 30000.0},
            {'name': 'Patna RDC', 'demand': 18000.0}
        ]
        freight_costs = np.array([
            [24.50, 18.00, 29.50],
            [26.00, 31.00, 19.50]
        ])
        sourcing_res = self.sourcing_solver.solve_transportation_problem(plants, depots, freight_costs)
        results['sourcing'] = {
            'total_inbound_freight_cost': sourcing_res['total_freight_cost'],
            'allocations': sourcing_res['lane_allocations']
        }

        # 5. Service Level & OTIF Tracking
        sample_orders = [
            {'order_id': 'ORD-101', 'ordered_cases': 250, 'delivered_cases': 250, 'committed_delivery_date': '2026-11-01', 'actual_delivery_date': '2026-11-01'},
            {'order_id': 'ORD-102', 'ordered_cases': 180, 'delivered_cases': 178, 'committed_delivery_date': '2026-11-01', 'actual_delivery_date': '2026-11-01'},
            {'order_id': 'ORD-103', 'ordered_cases': 320, 'delivered_cases': 260, 'committed_delivery_date': '2026-11-02', 'actual_delivery_date': '2026-11-02'},
            {'order_id': 'ORD-104', 'ordered_cases': 140, 'delivered_cases': 140, 'committed_delivery_date': '2026-11-02', 'actual_delivery_date': '2026-11-04'},
            {'order_id': 'ORD-105', 'ordered_cases': 400, 'delivered_cases': 395, 'committed_delivery_date': '2026-11-03', 'actual_delivery_date': '2026-11-03'}
        ]
        otif_res = self.otif_engine.calculate_order_otif(sample_orders)
        results['service_levels'] = {
            'case_fill_rate_pct': otif_res['case_fill_rate_pct'],
            'on_time_rate_pct': otif_res['on_time_rate_pct'],
            'composite_otif_pct': otif_res['composite_otif_pct']
        }

        return results

if __name__ == '__main__':
    pipeline = IntegratedOperationsPipeline()
    res = pipeline.run_daily_operational_cycle()
    print("=" * 70)
    print("ITC INTEGRATED OPERATIONS — DAILY DECISION SUPPORT SUMMARY")
    print("=" * 70)
    print(f"1. Demand Baseline:   Next Week Forecast = {res['demand']['next_week_forecast_cases']} cases (WAPE: {res['demand']['wape_pct']}%, Bias: {res['demand']['bias_pct']}%)")
    print(f"2. Inventory Buffer:  Safety Stock cut from {res['inventory']['ss_current_cases']} to {res['inventory']['ss_proposed_cases']} cases (-{res['inventory']['capital_buffer_reduction_pct']}%)")
    print(f"                      Reorder Point = {res['inventory']['reorder_point_cases']} cases | Order-Up-To Level = {res['inventory']['order_up_to_cases']} cases")
    print(f"3. Vehicle Dispatch:  Optimal Tata Ace Manifest = {res['dispatch_manifest']['atta_cases']} Atta + {res['dispatch_manifest']['bingo_cases']} Bingo!")
    print(f"                      Utilization: {res['dispatch_manifest']['payload_utilization_pct']}% Weight | {res['dispatch_manifest']['volume_utilization_pct']}% Volume")
    print(f"4. Sourcing Network:  Total Inbound Linehaul Cost = ₹ {res['sourcing']['total_inbound_freight_cost']:,.2f}")
    print(f"5. Service Level:     OTIF = {res['service_levels']['composite_otif_pct']}% (Fill Rate: {res['service_levels']['case_fill_rate_pct']}%, On-Time: {res['service_levels']['on_time_rate_pct']}%)")
    print("=" * 70)

