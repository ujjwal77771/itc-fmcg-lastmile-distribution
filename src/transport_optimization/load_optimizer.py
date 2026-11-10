"""
ITC Integrated Operations — Fleet Load & Weight-Cube Optimization Engine
Module: src/transport_optimization/load_optimizer.py
Author: Ujjwal Deep (B.Tech Mechanical Engineering, BIT Mesra)

Solves dual-constraint (payload mass and volumetric space) cargo loading problems
for FMCG delivery vehicles (e.g. Tata Ace 1.25T, Tata 407, Eicher 14T).
"""

from typing import Dict, List, Tuple
import math

class VehicleLoadOptimizer:
    """
    Dual-Constraint Vehicle Loading Engine for FMCG Distribution Fleets.
    Optimizes cargo mix to prevent premature mass or volumetric max-out.
    """

    def __init__(
        self,
        payload_capacity_kg: float = 1250.0,
        volumetric_capacity_cbm: float = 4.80
    ):
        self.payload_max_kg = payload_capacity_kg
        self.vol_max_cbm = volumetric_capacity_cbm

    def evaluate_manifest(
        self,
        cargo_items: List[Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Evaluates a proposed cargo manifest against vehicle limits.
        Each item dict must specify: 'sku_name', 'cases', 'case_weight_kg', 'case_volume_cbm'.
        """
        total_weight_kg = sum(item['cases'] * item['case_weight_kg'] for item in cargo_items)
        total_volume_cbm = sum(item['cases'] * item['case_volume_cbm'] for item in cargo_items)
        total_cases = sum(item['cases'] for item in cargo_items)

        weight_util = (total_weight_kg / self.payload_max_kg) * 100.0
        vol_util = (total_volume_cbm / self.vol_max_cbm) * 100.0

        is_legal = total_weight_kg <= self.payload_max_kg and total_volume_cbm <= self.vol_max_cbm

        return {
            'total_cases': total_cases,
            'total_weight_kg': round(total_weight_kg, 2),
            'total_volume_cbm': round(total_volume_cbm, 3),
            'weight_utilization_pct': round(weight_util, 2),
            'volume_utilization_pct': round(vol_util, 2),
            'is_within_limits': is_legal,
            'limiting_constraint': 'Weight' if weight_util > vol_util else 'Volume'
        }

    def optimize_density_pairing(
        self,
        dense_sku: Dict[str, float],
        bulky_sku: Dict[str, float]
    ) -> Tuple[int, int, Dict[str, float]]:
        """
        Determines the optimal ratio of dense products (e.g., Aashirvaad Atta)
        to bulky volumetric products (e.g., Bingo! Chips / Yippee! Noodles)
        to maximize simultaneous vehicle utilization.
        """
        best_cases_dense = 0
        best_cases_bulky = 0
        max_combined_util = -1.0
        best_stats = {}

        # Grid search over integer case increments
        max_dense = int(self.payload_max_kg / dense_sku['case_weight_kg'])
        max_bulky = int(self.vol_max_cbm / bulky_sku['case_volume_cbm'])

        for c_dense in range(max_dense + 1):
            for c_bulky in range(max_bulky + 1):
                w = (c_dense * dense_sku['case_weight_kg']) + (c_bulky * bulky_sku['case_weight_kg'])
                v = (c_dense * dense_sku['case_volume_cbm']) + (c_bulky * bulky_sku['case_volume_cbm'])

                if w <= self.payload_max_kg and v <= self.vol_max_cbm:
                    w_util = w / self.payload_max_kg
                    v_util = v / self.vol_max_cbm
                    combined_util = (w_util + v_util) / 2.0

                    if combined_util > max_combined_util:
                        max_combined_util = combined_util
                        best_cases_dense = c_dense
                        best_cases_bulky = c_bulky
                        best_stats = {
                            'weight_kg': round(w, 1),
                            'volume_cbm': round(v, 2),
                            'weight_utilization_pct': round(w_util * 100.0, 1),
                            'volume_utilization_pct': round(v_util * 100.0, 1),
                            'average_utilization_pct': round(combined_util * 100.0, 1)
                        }

        return best_cases_dense, best_cases_bulky, best_stats

if __name__ == '__main__':
    # Tata Ace 1.25T Cargo Pairing Demonstration
    optimizer = VehicleLoadOptimizer(payload_capacity_kg=1250.0, volumetric_capacity_cbm=4.80)

    atta_sku = {'name': 'Aashirvaad Atta 1kg', 'case_weight_kg': 16.5, 'case_volume_cbm': 0.038}
    snack_sku = {'name': 'Bingo! Mad Angles 45g', 'case_weight_kg': 3.6, 'case_volume_cbm': 0.082}

    dense_cases, bulky_cases, stats = optimizer.optimize_density_pairing(atta_sku, snack_sku)

    print(f"Optimal Cargo Manifest for Tata Ace 1.25T:")
    print(f" - {dense_cases} cases of {atta_sku['name']}")
    print(f" - {bulky_cases} cases of {snack_sku['name']}")
    print(f"Stats: Weight: {stats['weight_kg']} kg ({stats['weight_utilization_pct']}%) | Volume: {stats['volume_cbm']} CBM ({stats['volume_utilization_pct']}%)")
    print(f"Combined Fleet Utilization: {stats['average_utilization_pct']}%")

