"""
fatigue_model.py & recovery_model.py (combined)
------------------------------------------------
Standalone models for fatigue accumulation and recovery dynamics.
These complement the cardiac twin by providing independent estimates.
"""

import numpy as np
import pandas as pd
from typing import List


class FatigueModel:
    """
    Banister Impulse-Response model for training fatigue.

    Models cumulative fatigue as a decaying exponential:
        Fatigue(t) = Fatigue(t-1) × decay + training_load(t) × sensitivity
    """

    def __init__(self, tau_fatigue: float = 15.0, sensitivity: float = 1.0):
        """
        Args:
            tau_fatigue: Fatigue decay time constant in days (default 15 days)
            sensitivity: How quickly fatigue builds per unit load
        """
        self.decay = np.exp(-1 / tau_fatigue)
        self.sensitivity = sensitivity
        self.fatigue_series: List[float] = [0.0]

    def update(self, training_load: float) -> float:
        """
        Update fatigue given today's training load (0–100 arbitrary units).
        Returns current fatigue level.
        """
        current = self.fatigue_series[-1]
        new_fatigue = current * self.decay + training_load * self.sensitivity
        self.fatigue_series.append(round(new_fatigue, 3))
        return new_fatigue

    def simulate_days(self, loads: List[float]) -> pd.DataFrame:
        """
        Simulate fatigue over multiple days.
        Args:
            loads: Daily training loads (AU)
        Returns:
            DataFrame with day, load, fatigue columns
        """
        self.fatigue_series = [0.0]
        records = []
        for day, load in enumerate(loads, start=1):
            fatigue = self.update(load)
            records.append({"day": day, "training_load": load, "fatigue": fatigue})
        return pd.DataFrame(records)

    @property
    def current_fatigue(self) -> float:
        return self.fatigue_series[-1]


class RecoveryModel:
    """
    HRV-based recovery model.

    Estimates daily recovery quality (0–100%) based on:
      - HRV relative to personal baseline
      - Sleep quality proxy (resting HR at night)
      - Accumulated fatigue
    """

    def __init__(self, hrv_baseline: float = 50.0, resting_hr_baseline: float = 62.0):
        self.hrv_baseline = hrv_baseline
        self.resting_hr_baseline = resting_hr_baseline

    def estimate(self, hrv: float, resting_hr: float, fatigue: float) -> dict:
        """
        Estimate recovery quality for a single day.

        Args:
            hrv: Current morning HRV (ms SDNN)
            resting_hr: Current resting HR (bpm)
            fatigue: Fatigue score from FatigueModel (0–100 AU)

        Returns:
            dict with recovery_score, readiness, and recommendation
        """
        # HRV component: higher HRV relative to baseline = better recovery
        hrv_score = np.clip((hrv / self.hrv_baseline), 0.5, 1.5) * 50  # 0–75

        # HR component: lower resting HR relative to baseline = better recovery
        hr_ratio = self.resting_hr_baseline / max(resting_hr, 40)
        hr_score = np.clip(hr_ratio, 0.8, 1.2) * 25  # 0–30

        # Fatigue penalty
        fatigue_penalty = np.clip(fatigue / 100, 0, 0.5) * 30

        recovery_score = np.clip(hrv_score + hr_score - fatigue_penalty, 0, 100)

        if recovery_score >= 75:
            readiness = "Excellent"
            recommendation = "High-intensity training recommended"
        elif recovery_score >= 55:
            readiness = "Good"
            recommendation = "Moderate training or tempo work"
        elif recovery_score >= 35:
            readiness = "Fair"
            recommendation = "Zone 2 steady cardio or light session"
        else:
            readiness = "Poor"
            recommendation = "Active recovery or rest day"

        return {
            "recovery_score": round(recovery_score, 1),
            "readiness": readiness,
            "recommendation": recommendation,
            "hrv_contribution": round(hrv_score, 1),
            "hr_contribution": round(hr_score, 1),
            "fatigue_penalty": round(fatigue_penalty, 1),
        }

    def simulate_recovery_curve(
        self, hrv_values: List[float], resting_hr_values: List[float], fatigue_values: List[float]
    ) -> pd.DataFrame:
        """Simulate recovery over multiple days."""
        records = []
        for i, (hrv, rhr, fat) in enumerate(zip(hrv_values, resting_hr_values, fatigue_values)):
            result = self.estimate(hrv, rhr, fat)
            result["day"] = i + 1
            records.append(result)
        return pd.DataFrame(records)
