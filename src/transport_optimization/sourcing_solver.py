"""
ITC Integrated Operations — Multi-Depot Inbound Sourcing Optimizer
Module: src/transport_optimization/sourcing_solver.py
Author: Ujjwal Deep (B.Tech Mechanical Engineering, BIT Mesra)

Solves the multi-echelon transportation allocation problem minimizing total linehaul
freight cost from manufacturing plants / Integrated Food Parks to Regional Distribution Centres.
Utilizes Linear Programming (Simplex / Interior Point via scipy.optimize.linprog).
"""

from typing import Dict, List, Tuple
import numpy as np
from scipy.optimize import linprog

class InboundTransportationSolver:
    """
    Linear Programming Solver for Plant-to-Depot Inbound Logistics.
    Minimizes: sum(c_ij * X_ij)
    Subject to:
      sum_j(X_ij) <= Supply_i  (Plant production capacity)
      sum_i(X_ij) >= Demand_j  (Depot indent requirement)
    """

    @staticmethod
    def solve_transportation_problem(
        supply_nodes: List[Dict[str, float]],
        demand_nodes: List[Dict[str, float]],
        cost_matrix: np.ndarray
    ) -> Dict[str, any]:
        """
        Solves the classic Hitchcock-Koopmans transportation linear program.
        
        Args:
            supply_nodes: List of dicts with 'name' and 'capacity'
            demand_nodes: List of dicts with 'name' and 'demand'
            cost_matrix: 2D numpy array of shape (num_supply, num_demand) with unit freight rates
        """
        num_s = len(supply_nodes)
        num_d = len(demand_nodes)

        # Objective vector c: flatten cost_matrix row-wise
        c = cost_matrix.flatten()

        # Supply constraints: sum_j(X_ij) <= Supply_i
        A_ub = []
        b_ub = []
        for i in range(num_s):
            row = [0] * (num_s * num_d)
            for j in range(num_d):
                row[i * num_d + j] = 1
            A_ub.append(row)
            b_ub.append(supply_nodes[i]['capacity'])

        # Demand constraints: sum_i(X_ij) >= Demand_j  =>  -sum_i(X_ij) <= -Demand_j
        for j in range(num_d):
            row = [0] * (num_s * num_d)
            for i in range(num_s):
                row[i * num_d + j] = -1
            A_ub.append(row)
            b_ub.append(-demand_nodes[j]['demand'])

        # Non-negativity bounds
        bounds = [(0, None) for _ in range(num_s * num_d)]

        res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

        if not res.success:
            raise RuntimeError(f"Linear program failed to converge: {res.message}")

        flow_matrix = res.x.reshape((num_s, num_d))

        allocations = []
        for i in range(num_s):
            for j in range(num_d):
                if flow_matrix[i, j] > 0.01:
                    allocations.append({
                        'from_plant': supply_nodes[i]['name'],
                        'to_depot': demand_nodes[j]['name'],
                        'cases_shipped': round(float(flow_matrix[i, j]), 1),
                        'unit_freight': float(cost_matrix[i, j]),
                        'total_lane_cost': round(float(flow_matrix[i, j] * cost_matrix[i, j]), 2)
                    })

        return {
            'total_freight_cost': round(float(res.fun), 2),
            'flow_matrix': flow_matrix,
            'lane_allocations': allocations,
            'solver_status': res.message
        }

if __name__ == '__main__':
    # Practical example: Supplying Eastern UP / Bihar Depots
    # Plants: Haridwar Food Park, Panchgram (WB)
    plants = [
        {'name': 'Haridwar Integrated Food Park', 'capacity': 45000.0},
        {'name': 'Panchgram Manufacturing Unit', 'capacity': 35000.0}
    ]

    # Depots: Varanasi RDC, Lucknow RDC, Patna RDC
    depots = [
        {'name': 'Varanasi RDC', 'demand': 28000.0},
        {'name': 'Lucknow RDC', 'demand': 30000.0},
        {'name': 'Patna RDC', 'demand': 18000.0}
    ]

    # Freight cost per case (₹) based on road distance & lane tolls
    freight_costs = np.array([
        [24.50, 18.00, 29.50],  # From Haridwar
        [26.00, 31.00, 19.50]   # From Panchgram
    ])

    solver = InboundTransportationSolver()
    result = solver.solve_transportation_problem(plants, depots, freight_costs)

    print(f"Optimal Total Network Freight Cost: ₹ {result['total_freight_cost']:,.2f}")
    print("\nOptimal Lane Allocation Matrix:")
    for lane in result['lane_allocations']:
        print(f" - {lane['from_plant']} -> {lane['to_depot']}: {lane['cases_shipped']:,.0f} cases @ ₹{lane['unit_freight']}/case (₹{lane['total_lane_cost']:,.2f})")

