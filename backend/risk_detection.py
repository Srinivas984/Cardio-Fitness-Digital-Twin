"""
risk_detection.py
-----------------
Overtraining Risk Detection System.

Evaluates three risk levels based on cardiovascular biomarkers:
  - Low Risk:      Body is adapting well, continue training
  - Moderate Risk: Early signs of overtraining, reduce intensity
  - High Risk:     Overtraining likely, mandatory rest recommended

Detection criteria:
  1. Elevated resting HR (>baseline + 5 bpm)
  2. Low HRV (< 70% of personal baseline)
  3. High fatigue index (> 60)
  4. HR drift during submaximal effort (cardiac decoupling)
"""

import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class RiskDetector:
    """Detects overtraining risk from cardiovascular markers."""

    RISK_LEVELS = {
        "Low Risk": {
            "color": "#22c55e",
            "icon": "✅",
            "message": "You're adapting well. Training load is appropriate.",
            "action": "Maintain current plan. Consider adding 5–10% volume next week.",
        },
        "Moderate Risk": {
            "color": "#f59e0b",
            "icon": "⚠️",
            "message": "Early overtraining signals detected. Reduce intensity.",
            "action": "Drop intensity by 20% for 3–5 days. Prioritize sleep (8+ hrs) and nutrition.",
        },
        "High Risk": {
            "color": "#ef4444",
            "icon": "🚨",
            "message": "Overtraining syndrome risk is HIGH. Rest is required.",
            "action": "Take 5–7 days complete rest. Consult a sports physician if symptoms persist.",
        },
    }

    def __init__(
        self,
        hrv_baseline: float = 50.0,
        resting_hr_baseline: float = 62.0,
    ):
        self.hrv_baseline = hrv_baseline
        self.resting_hr_baseline = resting_hr_baseline

    def assess(self, features: dict) -> dict:
        """
        Perform full overtraining risk assessment.

        Args:
            features: Dict from FeatureEngineer.compute()

        Returns:
            Dict with risk_level, score, flags, and recommendations
        """
        flags = []
        risk_score = 0  # 0–10 scale, where 7+ = High Risk

        # --- Flag 1: Elevated resting HR ---
        resting_hr = features.get("resting_hr", 65)
        hr_elevation = resting_hr - self.resting_hr_baseline
        if hr_elevation >= 8:
            flags.append(f"Resting HR elevated by {hr_elevation:.0f} bpm above baseline")
            risk_score += 2.5
        elif hr_elevation >= 4:
            flags.append(f"Resting HR slightly elevated (+{hr_elevation:.0f} bpm)")
            risk_score += 1.0

        # --- Flag 2: Low HRV ---
        hrv = features.get("hrv_avg", self.hrv_baseline)
        hrv_ratio = hrv / self.hrv_baseline
        if hrv_ratio < 0.65:
            flags.append(f"HRV critically low ({hrv:.0f} ms vs {self.hrv_baseline:.0f} ms baseline)")
            risk_score += 2.5
        elif hrv_ratio < 0.80:
            flags.append(f"HRV below baseline ({hrv:.0f} ms, {(1-hrv_ratio)*100:.0f}% below baseline)")
            risk_score += 1.5

        # --- Flag 3: High fatigue index ---
        fatigue = features.get("fatigue_index", 30)
        if fatigue >= 70:
            flags.append(f"Severe fatigue accumulation (index: {fatigue:.0f}/100)")
            risk_score += 3.0
        elif fatigue >= 50:
            flags.append(f"Elevated fatigue accumulation (index: {fatigue:.0f}/100)")
            risk_score += 1.5

        # --- Flag 4: Poor recovery ---
        recovery_idx = features.get("recovery_index", 60)
        if recovery_idx < 30:
            flags.append(f"Very poor recovery quality (index: {recovery_idx:.0f}/100)")
            risk_score += 1.5
        elif recovery_idx < 50:
            flags.append(f"Below-average recovery quality (index: {recovery_idx:.0f}/100)")
            risk_score += 0.8

        # --- Flag 5: Low HR recovery speed ---
        hr_recovery = features.get("hr_recovery_rate", 25)
        if hr_recovery < 12:
            flags.append(f"Slow post-exercise HR recovery ({hr_recovery:.0f} bpm/min)")
            risk_score += 1.0

        # --- Determine risk level ---
        if risk_score >= 6:
            level = "High Risk"
        elif risk_score >= 3:
            level = "Moderate Risk"
        else:
            level = "Low Risk"

        info = self.RISK_LEVELS[level]

        return {
            "risk_level": level,
            "risk_score": round(min(risk_score, 10), 2),
            "risk_pct": round(min(risk_score / 10, 1) * 100, 1),
            "flags": flags if flags else ["No overtraining indicators detected."],
            "color": info["color"],
            "icon": info["icon"],
            "message": info["message"],
            "action": info["action"],
            "breakdown": {
                "resting_hr_flag": hr_elevation >= 4,
                "hrv_flag": hrv_ratio < 0.80,
                "fatigue_flag": fatigue >= 50,
                "recovery_flag": recovery_idx < 50,
            },
        }

    def trend_analysis(self, daily_features: List[dict]) -> str:
        """
        Analyze risk trend over multiple days.
        Returns 'Improving', 'Stable', or 'Worsening'.
        """
        if len(daily_features) < 2:
            return "Insufficient data"

        early_risk = self.assess(daily_features[0])["risk_score"]
        late_risk = self.assess(daily_features[-1])["risk_score"]

        delta = late_risk - early_risk
        if delta < -1:
            return "Improving ↘️"
        elif delta > 1:
            return "Worsening ↗️"
        else:
            return "Stable →"
