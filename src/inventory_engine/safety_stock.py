"""
ITC Integrated Operations — Inventory Analytics & Dynamic Safety Stock Engine
Module: src/inventory_engine/safety_stock.py
Author: Ujjwal Deep (B.Tech Mechanical Engineering, BIT Mesra)

Provides stochastic periodic-review inventory optimization, ABC-XYZ classification,
reorder point (ROP) calculation, and stockout probability modeling for FMCG networks.
"""

import math
from typing import Dict, List, Tuple
import numpy as np
from scipy.stats import norm

class InventoryAnalyticsEngine:
    """
    Inventory Analytics Engine for Multi-Echelon FMCG Distribution.
    Implements standard periodic-review (R, S) and continuous-review (s, Q) policies.
    """

    @staticmethod
    def calculate_periodic_safety_stock(
        review_cycle_days: float,
        lead_time_days: float,
        daily_demand_mean: float,
        daily_demand_std: float,
        lead_time_std: float,
        service_level: float = 0.95
    ) -> float:
        """
        Calculates stochastic periodic-review safety stock accounting for both
        demand variability and delivery arrival lead-time variability:
        SS = z * sqrt((R + L) * sigma_d^2 + d_bar^2 * sigma_L^2)
        """
        z = norm.ppf(service_level)
        exposure_time = review_cycle_days + lead_time_days
        variance_term = (exposure_time * (daily_demand_std ** 2)) + ((daily_demand_mean ** 2) * (lead_time_std ** 2))
        safety_stock = z * math.sqrt(variance_term)
        return float(safety_stock)

    @staticmethod
    def calculate_reorder_point(
        lead_time_days: float,
        daily_demand_mean: float,
        safety_stock: float
    ) -> float:
        """
        Continuous review Reorder Point: ROP = (d_bar * L) + SS
        """
        return (daily_demand_mean * lead_time_days) + safety_stock

    @staticmethod
    def calculate_order_up_to_level(
        review_cycle_days: float,
        lead_time_days: float,
        daily_demand_mean: float,
        safety_stock: float
    ) -> float:
        """
        Periodic review Order-Up-To Level: S = d_bar * (R + L) + SS
        """
        return (daily_demand_mean * (review_cycle_days + lead_time_days)) + safety_stock

    @staticmethod
    def calculate_cycle_stockout_probability(
        safety_stock: float,
        review_cycle_days: float,
        lead_time_days: float,
        daily_demand_mean: float,
        daily_demand_std: float,
        lead_time_std: float
    ) -> float:
        """
        Calculates empirical stockout probability per cycle: 1 - Phi(SS / sigma_total)
        """
        exposure_time = review_cycle_days + lead_time_days
        total_std = math.sqrt((exposure_time * (daily_demand_std ** 2)) + ((daily_demand_mean ** 2) * (lead_time_std ** 2)))
        if total_std == 0:
            return 0.0
        z_achieved = safety_stock / total_std
        stockout_prob = 1.0 - norm.cdf(z_achieved)
        return float(stockout_prob)

    @staticmethod
    def classify_abc_xyz(
        sku_data: List[Dict[str, float]]
    ) -> List[Dict[str, str]]:
        """
        Classifies SKUs into a 9-box ABC-XYZ matrix based on annual revenue
        contribution (ABC) and demand coefficient of variation (XYZ: CV = std / mean).
        """
        # Sort descending by annual revenue for ABC
        sorted_skus = sorted(sku_data, key=lambda x: x['annual_revenue'], reverse=True)
        total_rev = sum(x['annual_revenue'] for x in sorted_skus)
        
        cum_rev = 0.0
        results = []
        for sku in sorted_skus:
            cum_rev += sku['annual_revenue']
            rev_share = cum_rev / total_rev
            
            # ABC classification
            if rev_share <= 0.80:
                abc = 'A'
            elif rev_share <= 0.95:
                abc = 'B'
            else:
                abc = 'C'
                
            # XYZ classification
            cv = sku['demand_std'] / sku['demand_mean'] if sku['demand_mean'] > 0 else 0
            if cv < 0.50:
                xyz = 'X'
            elif cv <= 1.00:
                xyz = 'Y'
            else:
                xyz = 'Z'
                
            results.append({
                'sku_id': sku['sku_id'],
                'abc': abc,
                'xyz': xyz,
                'cluster': f"{abc}{xyz}",
                'cv': round(cv, 3)
            })
        return results

if __name__ == '__main__':
    # Operational test verification for Azamgarh District Hub
    engine = InventoryAnalyticsEngine()
    
    # Current Informal Setup
    ss_current = engine.calculate_periodic_safety_stock(
        review_cycle_days=12.0,
        lead_time_days=4.0,
        daily_demand_mean=36.0,
        daily_demand_std=14.0,
        lead_time_std=3.0,
        service_level=0.95
    )
    
    # Proposed Hub Setup
    ss_proposed = engine.calculate_periodic_safety_stock(
        review_cycle_days=6.0,
        lead_time_days=1.5,
        daily_demand_mean=36.0,
        daily_demand_std=14.0,
        lead_time_std=0.5,
        service_level=0.95
    )
    
    print(f"Safety Stock Current Setup:  {ss_current:.1f} cases (Days of cover: {ss_current/36.0:.1f}d)")
    print(f"Safety Stock Proposed Setup: {ss_proposed:.1f} cases (Days of cover: {ss_proposed/36.0:.1f}d)")
    print(f"Buffer Stock Reduction:      {((ss_current - ss_proposed) / ss_current) * 100:.1f}%")

