"""
prediction_engine.py
--------------------
30-Day Cardiac Performance Prediction Engine.

Models how CES evolves over 30 days of consistent training using:
  - Progressive overload adaptation curve
  - Banister fitness-fatigue model
  - Strategy-specific adaptation rates
"""

import numpy as np
import pandas as pd
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Adaptation rates per strategy (daily CES improvement %)
ADAPTATION_RATES = {
    "HIIT":             0.018,  # 1.8% per day (high intensity, high adaptation)
    "Steady Cardio":    0.012,  # 1.2% per day (foundational aerobic)
    "Recovery Day":     0.004,  # 0.4% per day (maintenance)
    "Tempo Run":        0.015,  # 1.5% per day (threshold adaptation)
    "Strength Circuit": 0.010,  # 1.0% per day (mixed)
}

# Weekly fatigue accumulation per strategy
FATIGUE_ACCUM = {
    "HIIT": 0.08, "Steady Cardio": 0.04, "Recovery Day": 0.01,
    "Tempo Run": 0.06, "Strength Circuit": 0.05,
}


class PredictionEngine:
    """Simulates 30-day cardiovascular improvement trajectory."""

    def __init__(self, days: int = 30):
        self.days = days

    def predict(
        self,
        baseline_ces: float,
        strategy: str,
        current_fatigue: float = 0.3,
        current_hrv: float = 50.0,
    ) -> pd.DataFrame:
        """
        Predict daily CES over the specified number of days.

        Args:
            baseline_ces: Current CES score (0–100)
            strategy: Training strategy name
            current_fatigue: Starting fatigue level (0–1)
            current_hrv: Starting HRV (ms)

        Returns:
            DataFrame with day-by-day predictions
        """
        adaptation_rate = ADAPTATION_RATES.get(strategy, 0.012)
        fatigue_rate = FATIGUE_ACCUM.get(strategy, 0.04)

        records = []
        ces = baseline_ces
        fatigue = current_fatigue
        hrv = current_hrv

        for day in range(1, self.days + 1):
            # Adaptation follows a sigmoid curve (diminishing returns)
            # The body adapts quickly initially, then plateaus
            saturation = 1 - (ces / 100)  # room for improvement
            daily_gain = adaptation_rate * saturation * 100

            # Fatigue accumulates, partially blunting adaptation
            fatigue_penalty = fatigue * daily_gain * 0.4
            net_gain = max(0, daily_gain - fatigue_penalty)

            # Weekend recovery bonus (days 6, 7, 13, 14, etc.)
            is_rest_day = (day % 7 in [0, 6])
            if is_rest_day:
                net_gain *= 0.3    # minimal gain on rest
                fatigue = max(0, fatigue - 0.15)  # recover fatigue
                hrv = min(100, hrv + 5)            # HRV improves
            else:
                fatigue = min(1, fatigue + fatigue_rate)
                hrv = max(15, hrv - 2 + np.random.normal(0, 1))

            # Natural noise in adaptation
            noise = np.random.normal(0, 0.5)
            ces = float(np.clip(ces + net_gain + noise, 0, 98))

            records.append({
                "day": day,
                "ces": round(ces, 2),
                "fatigue": round(fatigue, 3),
                "hrv": round(hrv, 1),
                "daily_gain": round(net_gain, 3),
                "is_rest_day": is_rest_day,
                "week": (day - 1) // 7 + 1,
            })

        df = pd.DataFrame(records)
        df["ces_smooth"] = df["ces"].rolling(window=3, min_periods=1).mean().round(2)
        return df

    def compare_strategies(self, baseline_ces: float, features: dict) -> pd.DataFrame:
        """
        Run 30-day predictions for all strategies and return a comparison.
        """
        fatigue = features.get("fatigue_index", 30) / 100
        hrv = features.get("hrv_avg", 50)

        comparison = []
        for strategy in ADAPTATION_RATES:
            df = self.predict(baseline_ces, strategy, fatigue, hrv)
            final_ces = df["ces"].iloc[-1]
            improvement = final_ces - baseline_ces
            comparison.append({
                "strategy": strategy,
                "start_ces": round(baseline_ces, 1),
                "end_ces": round(final_ces, 1),
                "improvement": round(improvement, 1),
                "peak_ces": round(df["ces"].max(), 1),
            })

        return pd.DataFrame(comparison).sort_values("improvement", ascending=False)

    def weekly_plan(self, strategy: str, days: int = 28) -> pd.DataFrame:
        """
        Generate a structured weekly training plan.
        Inserts rest/recovery days automatically.
        """
        plan = []
        week_pattern = {
            "HIIT":          ["HIIT", "Rest", "Steady Cardio", "HIIT", "Tempo Run", "Steady Cardio", "Rest"],
            "Steady Cardio": ["Steady Cardio"] * 5 + ["Recovery Day", "Rest"],
            "Tempo Run":     ["Easy Run", "Tempo Run", "Rest", "Steady Cardio", "Tempo Run", "Long Run", "Rest"],
            "HIIT":          ["HIIT", "Recovery Day", "Steady Cardio", "HIIT", "Steady Cardio", "Recovery Day", "Rest"],
        }
        default_pattern = ["Training", "Training", "Recovery Day", "Training", "Training", "Recovery Day", "Rest"]
        pattern = week_pattern.get(strategy, default_pattern)

        for day in range(1, days + 1):
            week_day = (day - 1) % 7
            plan.append({
                "day": day,
                "week": (day - 1) // 7 + 1,
                "day_of_week": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][week_day],
                "workout": pattern[week_day],
            })

        return pd.DataFrame(plan)
