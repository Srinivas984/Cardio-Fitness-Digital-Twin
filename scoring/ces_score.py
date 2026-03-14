"""
ces_score.py
------------
Cardiac Enhancement Score (CES) — a composite performance metric (0–100).

CES components (weighted):
  1. Resting HR Score       (20%): Lower resting HR = better cardiovascular fitness
  2. HR Recovery Score      (25%): Faster HR recovery = stronger heart
  3. HRV Score              (25%): Higher HRV = better autonomic balance
  4. Fatigue Score          (15%): Lower fatigue = higher readiness
  5. Training Efficiency    (15%): Ratio of aerobic work to total load

A CES of 80+ = elite; 60–79 = fit; 40–59 = average; <40 = needs improvement.
"""

import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# CES tier labels
CES_TIERS = [
    (80, "Elite Performer", "🏆"),
    (65, "Advanced Fitness", "⭐"),
    (50, "Good Baseline", "✅"),
    (35, "Developing", "📈"),
    (0,  "Beginner",   "🌱"),
]


class CESScorer:
    """Computes the Cardiac Enhancement Score from physiological features."""

    # Reference values for elite athletes vs untrained individuals
    BENCHMARKS = {
        "resting_hr":     {"elite": 40, "poor": 85},
        "recovery_rate":  {"elite": 60, "poor": 10},   # bpm drop in 1 min
        "hrv_avg":        {"elite": 100, "poor": 15},   # ms SDNN
        "fatigue_index":  {"elite": 5,  "poor": 80},   # lower = better
        "efficiency":     {"elite": 0.8, "poor": 0.2},  # aerobic fraction
    }

    def score(self, features: dict) -> dict:
        """
        Compute CES from extracted features.

        Args:
            features: Dict from FeatureEngineer.compute()

        Returns:
            Dict with ces, tier, label, emoji, component_scores
        """
        components = {
            "resting_hr_score":  self._score_resting_hr(features),
            "recovery_score":    self._score_recovery(features),
            "hrv_score":         self._score_hrv(features),
            "fatigue_score":     self._score_fatigue(features),
            "efficiency_score":  self._score_efficiency(features),
        }

        # Weighted sum
        weights = {
            "resting_hr_score": 0.20,
            "recovery_score":   0.25,
            "hrv_score":        0.25,
            "fatigue_score":    0.15,
            "efficiency_score": 0.15,
        }
        ces = sum(components[k] * weights[k] for k in components)
        ces = round(float(np.clip(ces, 0, 100)), 1)

        tier_label, emoji = self._get_tier(ces)

        logger.info(f"CES computed: {ces} ({tier_label})")

        return {
            "ces": ces,
            "tier": tier_label,
            "emoji": emoji,
            "components": {k: round(v, 1) for k, v in components.items()},
            "interpretation": self._interpret(ces, components),
        }

    def _normalize(self, value: float, good: float, poor: float) -> float:
        """Linear normalization to 0–100. good → 100, poor → 0."""
        if good == poor:
            return 50.0
        score = (value - poor) / (good - poor) * 100
        return float(np.clip(score, 0, 100))

    def _score_resting_hr(self, features: dict) -> float:
        rhr = features.get("resting_hr", 65)
        return self._normalize(rhr, good=40, poor=85)

    def _score_recovery(self, features: dict) -> float:
        rate = features.get("hr_recovery_rate", 20)
        return self._normalize(rate, good=55, poor=8)

    def _score_hrv(self, features: dict) -> float:
        hrv = features.get("hrv_avg", 45)
        return self._normalize(hrv, good=90, poor=15)

    def _score_fatigue(self, features: dict) -> float:
        fatigue = features.get("fatigue_index", 30)
        # Inverted: lower fatigue = higher score
        return self._normalize(fatigue, good=5, poor=80)

    def _score_efficiency(self, features: dict) -> float:
        # Efficiency = fraction of time in aerobic zones (Z1+Z2)
        z1 = features.get("zone1_pct", 40)
        z2 = features.get("zone2_pct", 30)
        aerobic_pct = z1 + z2
        return self._normalize(aerobic_pct, good=85, poor=20)

    def _get_tier(self, ces: float) -> tuple:
        for threshold, label, emoji in CES_TIERS:
            if ces >= threshold:
                return label, emoji
        return "Beginner", "🌱"

    def _interpret(self, ces: float, components: dict) -> str:
        """Generate a human-readable interpretation of the CES."""
        insights = []

        if components["resting_hr_score"] < 40:
            insights.append("resting heart rate is elevated")
        if components["hrv_score"] < 40:
            insights.append("HRV is below optimal (focus on sleep & recovery)")
        if components["fatigue_score"] < 40:
            insights.append("accumulated fatigue is high (consider a rest day)")
        if components["recovery_score"] > 70:
            insights.append("excellent cardiac recovery speed")
        if components["efficiency_score"] > 70:
            insights.append("good aerobic base development")

        if not insights:
            return "Balanced cardiovascular profile. Maintain current training rhythm."

        return "Key observations: " + "; ".join(insights) + "."
