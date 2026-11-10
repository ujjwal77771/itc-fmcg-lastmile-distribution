"""
Unit Tests for Inventory Analytics Engine
"""

import unittest
from src.inventory_engine.safety_stock import InventoryAnalyticsEngine

class TestInventoryEngine(unittest.TestCase):

    def test_periodic_safety_stock_reduction(self):
        engine = InventoryAnalyticsEngine()
        
        # Current Setup: R=12, L=4, d=36, sigma_d=14, sigma_L=3
        ss_cur = engine.calculate_periodic_safety_stock(12.0, 4.0, 36.0, 14.0, 3.0, 0.95)
        
        # Proposed Hub Setup: R=6, L=1.5, d=36, sigma_d=14, sigma_L=0.5
        ss_prop = engine.calculate_periodic_safety_stock(6.0, 1.5, 36.0, 14.0, 0.5, 0.95)
        
        # Verify safety stock reduces significantly (>65%)
        self.assertGreater(ss_cur, ss_prop)
        reduction_pct = (ss_cur - ss_prop) / ss_cur
        self.assertGreater(reduction_pct, 0.65)
        self.assertAlmostEqual(ss_cur, 207.0, delta=20.0) # Check reasonable range

    def test_reorder_point(self):
        engine = InventoryAnalyticsEngine()
        rop = engine.calculate_reorder_point(lead_time_days=2.0, daily_demand_mean=50.0, safety_stock=100.0)
        self.assertEqual(rop, 200.0)

    def test_abc_xyz_classification(self):
        engine = InventoryAnalyticsEngine()
        sample_skus = [
            {'sku_id': 'SKU-Aashirvaad-Atta', 'annual_revenue': 8000000, 'demand_mean': 100, 'demand_std': 20}, # AX
            {'sku_id': 'SKU-Sunfeast-Biscuits', 'annual_revenue': 1500000, 'demand_mean': 50, 'demand_std': 40}, # BY
            {'sku_id': 'SKU-Engage-Perfume', 'annual_revenue': 500000, 'demand_mean': 10, 'demand_std': 15}      # CZ
        ]
        classified = engine.classify_abc_xyz(sample_skus)
        clusters = {x['sku_id']: x['cluster'] for x in classified}
        self.assertEqual(clusters['SKU-Aashirvaad-Atta'], 'AX')
        self.assertEqual(clusters['SKU-Sunfeast-Biscuits'], 'BY')
        self.assertEqual(clusters['SKU-Engage-Perfume'], 'CZ')

if __name__ == '__main__':
    unittest.main()
