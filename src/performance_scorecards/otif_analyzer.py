"""
ITC Integrated Operations — OTIF Service Level & Carrier Scorecard Engine
Module: src/performance_scorecards/otif_analyzer.py
Author: Ujjwal Deep (B.Tech Mechanical Engineering, BIT Mesra)

Provides industrial calculation of On-Time In-Full (OTIF), Line Item Fill Rate (LIFR),
Order Fill Rate (OFR), and root-cause loss waterfall decomposition for FMCG logistics.
"""

from typing import Dict, List
import pandas as pd
import numpy as np

class OTIFAnalyticsEngine:
    """
    Enterprise Service Level & OTIF Evaluation Engine.
    Decouples warehouse stock availability from transporter delivery reliability.
    """

    @staticmethod
    def calculate_order_otif(
        order_records: List[Dict[str, any]]
    ) -> Dict[str, float]:
        """
        Calculates composite OTIF and components from a list of order deliveries.
        Each record must contain:
          - 'order_id': str
          - 'ordered_cases': float
          - 'delivered_cases': float
          - 'committed_delivery_date': str (YYYY-MM-DD)
          - 'actual_delivery_date': str (YYYY-MM-DD)
        """
        total_orders = len(order_records)
        if total_orders == 0:
            return {'otif_pct': 0.0, 'on_time_pct': 0.0, 'in_full_pct': 0.0}

        on_time_count = 0
        in_full_count = 0
        otif_count = 0
        total_ordered_cases = 0.0
        total_delivered_cases = 0.0

        for r in order_records:
            total_ordered_cases += r['ordered_cases']
            total_delivered_cases += r['delivered_cases']

            is_on_time = r['actual_delivery_date'] <= r['committed_delivery_date']
            # Standard FMCG tolerance: >= 98% cases delivered considered in-full
            is_in_full = (r['delivered_cases'] / r['ordered_cases']) >= 0.98 if r['ordered_cases'] > 0 else False

            if is_on_time:
                on_time_count += 1
            if is_in_full:
                in_full_count += 1
            if is_on_time and is_in_full:
                otif_count += 1

        on_time_rate = (on_time_count / total_orders) * 100.0
        order_in_full_rate = (in_full_count / total_orders) * 100.0
        case_fill_rate = (total_delivered_cases / total_ordered_cases) * 100.0 if total_ordered_cases > 0 else 0.0
        composite_otif = (otif_count / total_orders) * 100.0

        return {
            'total_orders': total_orders,
            'total_ordered_cases': total_ordered_cases,
            'total_delivered_cases': total_delivered_cases,
            'case_fill_rate_pct': round(case_fill_rate, 2),
            'order_in_full_rate_pct': round(order_in_full_rate, 2),
            'on_time_rate_pct': round(on_time_rate, 2),
            'composite_otif_pct': round(composite_otif, 2),
            'loss_due_to_delay_orders': total_orders - on_time_count,
            'loss_due_to_stockout_orders': total_orders - in_full_count
        }

    @staticmethod
    def generate_transporter_scorecard(
        transporter_data: List[Dict[str, any]]
    ) -> List[Dict[str, any]]:
        """
        Ranks logistics carriers based on OTIF compliance, transit damage rate,
        and detention/dock adherence.
        """
        scorecard = []
        for t in transporter_data:
            # Weighted carrier performance index: 40% On-time, 40% In-full, 20% Damage-free
            score = (t['on_time_pct'] * 0.40) + (t['fill_rate_pct'] * 0.40) + ((100.0 - t['damage_pct']) * 0.20)
            
            if score >= 90.0:
                tier = 'Preferred / Tier 1 (Bonus Eligible)'
            elif score >= 80.0:
                tier = 'Standard / Tier 2 (Compliant)'
            else:
                tier = 'Probation / Tier 3 (SLA Penalty)'

            scorecard.append({
                'transporter_name': t['name'],
                'fleet_type': t['fleet_type'],
                'composite_score': round(score, 1),
                'tier_status': tier,
                'otif_pct': round(t['on_time_pct'] * (t['fill_rate_pct'] / 100.0), 1)
            })

        return sorted(scorecard, key=lambda x: x['composite_score'], reverse=True)

if __name__ == '__main__':
    # Test sample simulating district deliveries across East UP
    test_orders = [
        {'order_id': 'ORD-101', 'ordered_cases': 250, 'delivered_cases': 250, 'committed_delivery_date': '2026-11-01', 'actual_delivery_date': '2026-11-01'},
        {'order_id': 'ORD-102', 'ordered_cases': 180, 'delivered_cases': 178, 'committed_delivery_date': '2026-11-01', 'actual_delivery_date': '2026-11-01'},
        {'order_id': 'ORD-103', 'ordered_cases': 320, 'delivered_cases': 260, 'committed_delivery_date': '2026-11-02', 'actual_delivery_date': '2026-11-02'}, # Under-fulfilled
        {'order_id': 'ORD-104', 'ordered_cases': 140, 'delivered_cases': 140, 'committed_delivery_date': '2026-11-02', 'actual_delivery_date': '2026-11-04'}, # Delayed
        {'order_id': 'ORD-105', 'ordered_cases': 400, 'delivered_cases': 395, 'committed_delivery_date': '2026-11-03', 'actual_delivery_date': '2026-11-03'},
    ]

    metrics = OTIFAnalyticsEngine.calculate_order_otif(test_orders)
    print("District Order Fulfillment Summary:")
    print(f" - Case Fill Rate:    {metrics['case_fill_rate_pct']}%")
    print(f" - On-Time Rate:      {metrics['on_time_rate_pct']}%")
    print(f" - Composite OTIF:    {metrics['composite_otif_pct']}%")
