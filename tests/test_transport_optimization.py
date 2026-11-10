"""
Unit Tests for Transport Optimization & Sourcing Solver
"""

import unittest
import numpy as np
from src.transport_optimization.load_optimizer import VehicleLoadOptimizer
from src.transport_optimization.sourcing_solver import InboundTransportationSolver

class TestTransportOptimization(unittest.TestCase):

    def test_dual_constraint_loading(self):
        optimizer = VehicleLoadOptimizer(payload_capacity_kg=1250.0, volumetric_capacity_cbm=4.80)
        
        # Test legal load
        manifest = [
            {'sku_name': 'Atta 1kg', 'cases': 50, 'case_weight_kg': 16.5, 'case_volume_cbm': 0.038},
            {'sku_name': 'Biscuits', 'cases': 30, 'case_weight_kg': 5.0, 'case_volume_cbm': 0.050}
        ]
        res = optimizer.evaluate_manifest(manifest)
        self.assertTrue(res['is_within_limits'])
        self.assertLessEqual(res['total_weight_kg'], 1250.0)
        self.assertLessEqual(res['total_volume_cbm'], 4.80)

    def test_sourcing_linear_program(self):
        solver = InboundTransportationSolver()
        plants = [
            {'name': 'Plant A', 'capacity': 100.0},
            {'name': 'Plant B', 'capacity': 100.0}
        ]
        depots = [
            {'name': 'Depot 1', 'demand': 80.0},
            {'name': 'Depot 2', 'demand': 70.0}
        ]
        # Plant A is cheaper for Depot 1, Plant B cheaper for Depot 2
        costs = np.array([
            [10.0, 25.0],
            [30.0, 12.0]
        ])
        res = solver.solve_transportation_problem(plants, depots, costs)
        self.assertIn('Optimal', res['solver_status'])
        # Optimal cost: 80 * 10 + 70 * 12 = 800 + 840 = 1640
        self.assertAlmostEqual(res['total_freight_cost'], 1640.0)

if __name__ == '__main__':
    unittest.main()
