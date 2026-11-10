"""
Unit Tests for ITC Data Loader and SQLite Operational Views
Module: tests/test_data_loader.py
Author: Ujjwal Deep (B.Tech Mechanical Engineering, BIT Mesra)
"""

import os
import sqlite3
import unittest
import pandas as pd

class TestDataLoaderAndDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'itc_operations.db')
        cls.raw_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')

    def test_csv_files_exist(self):
        """Verifies that all 4 raw operational CSV files are generated."""
        expected_files = [
            'distributor_orders.csv',
            'inventory_snapshot.csv',
            'shipment_dispatch_log.csv',
            'distance_matrix.csv'
        ]
        for fname in expected_files:
            fpath = os.path.join(self.raw_dir, fname)
            self.assertTrue(os.path.exists(fpath), f"Missing CSV: {fname}")

    def test_sqlite_database_integrity(self):
        """Verifies SQLite tables, indexes, and row counts."""
        self.assertTrue(os.path.exists(self.db_path), "Database file not found.")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Check tables
        tables = [row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        self.assertIn('distributor_orders', tables)
        self.assertIn('inventory_snapshot', tables)
        self.assertIn('shipment_dispatch_log', tables)
        self.assertIn('distance_matrix', tables)

        # Check views
        views = [row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='view'").fetchall()]
        self.assertIn('vw_stockout_risk_watchlist', views)
        self.assertIn('vw_carrier_otif_summary', views)
        self.assertIn('vw_order_cut_diagnostics', views)

        # Check row count of orders
        order_count = cur.execute("SELECT COUNT(*) FROM distributor_orders").fetchone()[0]
        self.assertGreaterEqual(order_count, 1000)

        conn.close()

    def test_otif_scorecard_view_math(self):
        """Verifies that OTIF metrics in SQLite view follow valid FMCG mathematical boundaries."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM vw_carrier_otif_summary", conn)
        conn.close()

        self.assertFalse(df.empty)
        for _, row in df.iterrows():
            self.assertGreaterEqual(row['case_fill_rate_pct'], 80.0)
            self.assertLessEqual(row['case_fill_rate_pct'], 100.0)
            self.assertGreaterEqual(row['on_time_shipment_pct'], 70.0)
            self.assertLessEqual(row['on_time_shipment_pct'], 100.0)
            self.assertGreaterEqual(row['composite_otif_pct'], 50.0)
            self.assertLessEqual(row['composite_otif_pct'], 100.0)

if __name__ == '__main__':
    unittest.main()
