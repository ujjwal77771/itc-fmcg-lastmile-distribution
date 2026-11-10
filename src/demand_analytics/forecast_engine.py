"""
ITC Integrated Operations — Demand Analytics & Forecast Error Engine
Module: src/demand_analytics/forecast_engine.py
Author: Ujjwal Deep (B.Tech Mechanical Engineering, BIT Mesra)

Provides operational demand forecasting and error quantification (WAPE, Bias, Tracking Signal)
for regional FMCG sales and operations planning (S&OP).
"""

from typing import Dict, List, Tuple
import numpy as np

class DemandForecastEngine:
    """
    S&OP Demand Forecasting and Accuracy Analytics Engine.
    Implements Holt's Linear Exponential Smoothing and WAPE/Bias metrics.
    """

    @staticmethod
    def calculate_wape(actuals: np.ndarray, forecasts: np.ndarray) -> float:
        """
        Weighted Absolute Percentage Error: sum(|A - F|) / sum(A) * 100
        Standard metric in FMCG S&OP preventing zero-division anomalies.
        """
        sum_actual = np.sum(actuals)
        if sum_actual == 0:
            return 0.0
        return float((np.sum(np.abs(actuals - forecasts)) / sum_actual) * 100.0)

    @staticmethod
    def calculate_forecast_bias(actuals: np.ndarray, forecasts: np.ndarray) -> float:
        """
        Structural Forecast Bias %: sum(F - A) / sum(A) * 100
        Positive = structural over-forecasting (leads to inventory bloat)
        Negative = structural under-forecasting (leads to retail stockouts)
        """
        sum_actual = np.sum(actuals)
        if sum_actual == 0:
            return 0.0
        return float((np.sum(forecasts - actuals) / sum_actual) * 100.0)

    @staticmethod
    def holts_linear_smoothing(
        series: np.ndarray,
        alpha: float = 0.3,
        beta: float = 0.1,
        horizon_steps: int = 4
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Holt's Double Exponential Smoothing for trended demand time-series.
        level: L_t = alpha * Y_t + (1 - alpha) * (L_{t-1} + b_{t-1})
        trend: b_t = beta * (L_t - L_{t-1}) + (1 - beta) * b_{t-1}
        forecast: F_{t+k} = L_t + k * b_t
        """
        n = len(series)
        if n < 2:
            raise ValueError("Time series requires at least 2 historical data points.")

        levels = np.zeros(n)
        trends = np.zeros(n)
        fitted = np.zeros(n)

        # Initial values
        levels[0] = series[0]
        trends[0] = series[1] - series[0]
        fitted[0] = series[0]

        for t in range(1, n):
            levels[t] = alpha * series[t] + (1 - alpha) * (levels[t - 1] + trends[t - 1])
            trends[t] = beta * (levels[t] - levels[t - 1]) + (1 - beta) * trends[t - 1]
            fitted[t] = levels[t - 1] + trends[t - 1]

        # Forecast future steps
        future_forecasts = np.zeros(horizon_steps)
        for k in range(1, horizon_steps + 1):
            future_forecasts[k - 1] = levels[-1] + (k * trends[-1])

        return fitted, future_forecasts

if __name__ == '__main__':
    # 12 weeks historical atta case orders for Azamgarh cluster
    weekly_actuals = np.array([3200, 3400, 3350, 3600, 3800, 3750, 4100, 4200, 4150, 4400, 4600, 4750], dtype=float)

    engine = DemandForecastEngine()
    fitted, future_4w = engine.holts_linear_smoothing(weekly_actuals, alpha=0.35, beta=0.15, horizon_steps=4)

    wape = engine.calculate_wape(weekly_actuals[1:], fitted[1:])
    bias = engine.calculate_forecast_bias(weekly_actuals[1:], fitted[1:])

    print(f"Historical Demand Tracking: WAPE = {wape:.2f}% | Bias = {bias:+.2f}%")
    print(f"4-Week Forward Forecast: {np.round(future_4w, 0).astype(int)} cases")
