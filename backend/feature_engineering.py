"""
feature_engineering.py
-----------------------
Extracts physiological features from preprocessed wearable data.

Features computed:
  - avg_hr, max_hr, min_hr (resting)
  - hrv_avg, hrv_min
  - fatigue_index: high HR with low HRV signals fatigue
  - recovery_index: HRV-based recovery quality
  - activity_load: volume × intensity proxy
  - hr_recovery_rate: how fast HR drops after peak
  - training_monotony: coefficient of variation of loads
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Computes cardiovascular performance features from cleaned data."""

    def __init__(self, max_hr_formula: float = 220.0, age: int = 30):
        self.age = age
        self.theoretical_max_hr = max_hr_formula - age  # 220 - age formula

    def compute(self, df: pd.DataFrame) -> dict:
        """
        Run all feature computations.
        Returns a dict of feature name → value.
        """
        features = {}

        features.update(self._hr_features(df))
        features.update(self._hrv_features(df))
        features.update(self._fatigue_features(df))
        features.update(self._activity_features(df))
        features.update(self._recovery_features(df))

        logger.info(f"Computed {len(features)} physiological features.")
        return features

    def _hr_features(self, df: pd.DataFrame) -> dict:
        """Heart rate statistics."""
        hr = df["heart_rate"].dropna()
        return {
            "avg_hr": float(hr.mean()),
            "max_hr": float(hr.max()),
            "min_hr": float(hr[hr > 0].min()),          # resting proxy
            "hr_range": float(hr.max() - hr.min()),
            "hr_std": float(hr.std()),
            "theoretical_max_hr": float(self.theoretical_max_hr),
        }

    def _hrv_features(self, df: pd.DataFrame) -> dict:
        """HRV-based autonomic nervous system markers."""
        hrv = df["hrv_sdnn"].dropna()
        if hrv.empty:
            return {"hrv_avg": 45.0, "hrv_min": 20.0, "hrv_std": 10.0}
        return {
            "hrv_avg": float(hrv.mean()),
            "hrv_min": float(hrv.min()),
            "hrv_std": float(hrv.std()),
        }

    def _fatigue_features(self, df: pd.DataFrame) -> dict:
        """
        Fatigue index: high resting HR + low HRV = high fatigue.
        Scale 0–100 where 100 = maximum fatigue.
        """
        # Identify rest periods
        rest_mask = df["heart_rate"] < 80
        rest_df = df[rest_mask]

        if rest_df.empty:
            resting_hr = df["heart_rate"].quantile(0.1)
            resting_hrv = df["hrv_sdnn"].quantile(0.9) if "hrv_sdnn" in df else 45.0
        else:
            resting_hr = rest_df["heart_rate"].mean()
            resting_hrv = rest_df["hrv_sdnn"].mean() if "hrv_sdnn" in df else 45.0

        # Normalize: higher resting HR and lower HRV → higher fatigue
        hr_fatigue = np.clip((resting_hr - 50) / 40, 0, 1)    # 50 bpm baseline
        hrv_fatigue = np.clip(1 - (resting_hrv - 10) / 80, 0, 1)  # 90 ms ideal
        fatigue_index = (hr_fatigue * 0.6 + hrv_fatigue * 0.4) * 100

        return {
            "fatigue_index": float(fatigue_index),
            "resting_hr": float(resting_hr),
            "resting_hrv": float(resting_hrv),
        }

    def _activity_features(self, df: pd.DataFrame) -> dict:
        """Activity load and intensity distribution."""
        steps = df["steps"].sum() if "steps" in df.columns else 0
        total_records = len(df)

        # HR zones (% of theoretical max)
        hr = df["heart_rate"].dropna()
        zone1 = ((hr < 0.6 * self.theoretical_max_hr).sum() / total_records) * 100
        zone2 = (((hr >= 0.6 * self.theoretical_max_hr) & (hr < 0.7 * self.theoretical_max_hr)).sum() / total_records) * 100
        zone3 = (((hr >= 0.7 * self.theoretical_max_hr) & (hr < 0.8 * self.theoretical_max_hr)).sum() / total_records) * 100
        zone4 = ((hr >= 0.8 * self.theoretical_max_hr).sum() / total_records) * 100

        # Activity load = sum of HR × duration proxy
        activity_load = float((hr * (hr / self.theoretical_max_hr)).sum())

        return {
            "total_steps": float(steps),
            "activity_load": activity_load,
            "zone1_pct": float(zone1),   # Easy
            "zone2_pct": float(zone2),   # Aerobic
            "zone3_pct": float(zone3),   # Threshold
            "zone4_pct": float(zone4),   # Anaerobic
        }

    def _recovery_features(self, df: pd.DataFrame) -> dict:
        """
        Recovery index based on HRV trend and HR drop after peaks.
        Higher is better (0–100 scale).
        """
        hrv = df["hrv_sdnn"].dropna() if "hrv_sdnn" in df.columns else pd.Series([45.0])
        hr = df["heart_rate"].dropna()

        # HR recovery: peak-to-following-low ratio
        hr_values = hr.values
        peaks = []
        for i in range(1, len(hr_values) - 1):
            if hr_values[i] > hr_values[i-1] and hr_values[i] > hr_values[i+1]:
                if hr_values[i] > 120:
                    # Look 1–3 records ahead for recovery
                    future_idx = min(i + 3, len(hr_values) - 1)
                    recovery = hr_values[i] - hr_values[future_idx]
                    peaks.append(recovery)

        hr_recovery_rate = float(np.mean(peaks)) if peaks else 20.0

        # HRV-based recovery (50+ ms SDNN = good recovery)
        hrv_recovery = float(np.clip((hrv.mean() - 20) / 60, 0, 1) * 100)

        recovery_index = float(
            0.5 * np.clip(hr_recovery_rate / 50, 0, 1) * 100 +
            0.5 * hrv_recovery
        )

        return {
            "hr_recovery_rate": hr_recovery_rate,
            "hrv_recovery_score": hrv_recovery,
            "recovery_index": recovery_index,
        }
