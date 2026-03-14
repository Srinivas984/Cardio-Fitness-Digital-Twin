"""
predictive_alerts.py
--------------------
Proactive alert system that predicts future cardio states and warnings.

Capabilities:
  - Overtraining trajectory prediction (next 3-7 days)
  - Optimal recovery windows
  - Safe training activity levels
  - Risk escalation alerts
  - Golden hour recommendations

Uses: Existing digital twin to forward-project HRV, fatigue, recovery.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PredictiveAlerts:
    """
    Forecasts future cardio state and generates proactive alerts.
    """

    def __init__(self):
        self.alert_history = []
        self.thresholds = {
            "hrv_drop_severe": 0.35,  # 35% below baseline = severe alert
            "hrv_drop_moderate": 0.25,  # 25% = moderate
            "fatigue_high": 0.75,  # >75% = risk
            "recovery_low": 0.30,  # <30% = needs recovery
        }

    def predict_overtraining_trajectory(
        self, 
        current_state: dict,
        recent_history: pd.DataFrame,
        days_ahead: int = 7
    ) -> Dict:
        """
        Predict if user is on trajectory toward overtraining.
        
        Args:
            current_state: Current HRV, fatigue, recovery, training load
            recent_history: Last 7 days of data
            days_ahead: How many days to forecast
            
        Returns:
            Dict with trajectory, risk level, inflection point
        """
        
        # Extract trends from historical data
        if recent_history is None or len(recent_history) < 3:
            return {
                "trajectory": "insufficient_data",
                "risk_level": "unknown",
                "days_until_concern": None,
                "recommendation": "Need 3+ days of data for predictions"
            }
        
        hrv_trend = self._extract_trend(recent_history.get("hrv", []))
        fatigue_trend = self._extract_trend(recent_history.get("fatigue", []))
        recovery_trend = self._extract_trend(recent_history.get("recovery", []))
        
        # Project forward
        projected_hrv = current_state.get("hrv_avg", 50) + (hrv_trend * days_ahead)
        projected_fatigue = current_state.get("fatigue_index", 30) + (fatigue_trend * days_ahead)
        projected_recovery = current_state.get("recovery_index", 70) + (recovery_trend * days_ahead)
        
        # Determine risk trajectory
        if projected_fatigue > 85 or projected_recovery < 15:
            trajectory = "severe_overtraining"
            risk_level = 5
        elif projected_fatigue > 75 or projected_recovery < 25:
            trajectory = "mild_overtraining"
            risk_level = 4
        elif projected_fatigue > 60:
            trajectory = "accumulating_fatigue"
            risk_level = 3
        elif projected_hrv < (current_state.get("hrv_baseline", 50) * 0.7):
            trajectory = "hrv_suppression"
            risk_level = 3
        else:
            trajectory = "healthy_adaptation"
            risk_level = 1
        
        # Find inflection point (when risk becomes moderate)
        days_until_concern = None
        if risk_level >= 3:
            for day in range(1, days_ahead + 1):
                day_fatigue = current_state.get("fatigue_index", 30) + (fatigue_trend * day)
                day_recovery = current_state.get("recovery_index", 70) + (recovery_trend * day)
                if day_fatigue > 75 or day_recovery < 25:
                    days_until_concern = day
                    break
        
        return {
            "trajectory": trajectory,
            "risk_level": risk_level,
            "days_until_concern": days_until_concern,
            "projected_hrv_7day": round(projected_hrv, 1),
            "projected_fatigue_7day": round(projected_fatigue, 1),
            "projected_recovery_7day": round(projected_recovery, 1),
            "hrv_trend_direction": "declining" if hrv_trend < 0 else "improving" if hrv_trend > 0 else "stable",
            "fatigue_trend_direction": "accumulating" if fatigue_trend > 0 else "reducing" if fatigue_trend < 0 else "stable",
        }

    def find_recovery_windows(
        self,
        current_state: dict,
        forecast_days: int = 7
    ) -> List[Dict]:
        """
        Identify optimal recovery windows in next N days.
        
        Args:
            current_state: Current physiological state
            forecast_days: Days to analyze
            
        Returns:
            List of recovery windows with descriptions
        """
        hrv = current_state.get("hrv_avg", 50)
        hrv_baseline = current_state.get("hrv_baseline", 50)
        fatigue = current_state.get("fatigue_index", 30)
        recovery = current_state.get("recovery_index", 70)
        
        windows = []
        
        # Immediate recovery window (next 24 hours)
        if fatigue > 60 or recovery < 40:
            windows.append({
                "window": "Next 24 hours",
                "priority": "HIGH",
                "action": "Active recovery or complete rest",
                "reason": "Elevated fatigue + reduced recovery capacity",
                "duration_hours": 24,
                "expected_benefit": "HRV rebound by 5-10% with parasympathetic activation"
            })
        
        # 48-72 hour window
        if hrv < (hrv_baseline * 0.85):
            windows.append({
                "window": "Within 48-72 hours",
                "priority": "MEDIUM",
                "action": "Easy aerobic work only (Zone 1-2)",
                "reason": f"HRV at {hrv:.0f}ms ({(hrv/hrv_baseline)*100:.0f}% of baseline)",
                "duration_hours": 72,
                "expected_benefit": "Allow parasympathetic recovery + light cardio adaptation"
            })
        
        # Build phase (low fatigue, good recovery)
        if fatigue < 50 and recovery > 60:
            windows.append({
                "window": "Days 2-4 (Optimal Training Window)",
                "priority": "HIGH",
                "action": "Threshold or VO2max work + strength",
                "reason": "Low fatigue + high recovery = capacity for intense training",
                "duration_hours": 72,
                "expected_benefit": "Maximum fitness adaptation with minimal risk"
            })
        
        return windows

    def generate_safe_activity_levels(
        self,
        current_state: dict
    ) -> Dict:
        """
        Recommend safe activity intensities for today/tomorrow.
        
        Returns:
            Dict with approved zone recommendations
        """
        fatigue = current_state.get("fatigue_index", 30)
        recovery = current_state.get("recovery_index", 70)
        hrv_ratio = current_state.get("hrv_avg", 50) / current_state.get("hrv_baseline", 50)
        
        recommended_zones = []
        prohibited_zones = []
        
        # Zone 1-2 (Recovery/Easy)
        if True:  # Always safe
            recommended_zones.append({
                "zone": "Zone 1-2 (Recovery Aerobic)",
                "hr_range": "50-70% max HR",
                "duration": "Up to 90 minutes",
                "safety": "SAFE",
                "why": "Always beneficial for recovery"
            })
        
        # Zone 3 (Steady)
        if recovery > 50 and fatigue < 60:
            recommended_zones.append({
                "zone": "Zone 3 (Steady)",
                "hr_range": "70-80% max HR",
                "duration": "Up to 60 minutes",
                "safety": "ACCEPTABLE",
                "why": "Sustainable with current recovery state"
            })
        else:
            prohibited_zones.append({
                "zone": "Zone 3 (Steady)",
                "reason": "Reduced recovery capacity or elevated fatigue",
                "recommended_wait": "24-48 hours"
            })
        
        # Zone 4 (Threshold)
        if recovery > 65 and fatigue < 50 and hrv_ratio > 0.90:
            recommended_zones.append({
                "zone": "Zone 4 (Threshold)",
                "hr_range": "80-90% max HR",
                "duration": "20-40 minutes",
                "safety": "OK",
                "why": "Good recovery state supports threshold work"
            })
        else:
            prohibited_zones.append({
                "zone": "Zone 4 (Threshold)",
                "reason": f"HRV compromised ({hrv_ratio*100:.0f}% baseline), recovery insufficient",
                "recommended_wait": "2-3 days"
            })
        
        # Zone 5 (VO2max/Sprint)
        if recovery > 75 and fatigue < 40 and hrv_ratio > 0.95:
            recommended_zones.append({
                "zone": "Zone 5 (VO2max/Sprint)",
                "hr_range": "90-100% max HR",
                "duration": "Intervals only (5-8 min total)",
                "safety": "RISKY_BUT_POSSIBLE",
                "why": "Excellent recovery state, but limit duration to prevent fatigue spike"
            })
        else:
            prohibited_zones.append({
                "zone": "Zone 5 (VO2max/Sprint)",
                "reason": "Insufficient recovery capacity. Risk of HRV further suppression.",
                "recommended_wait": "3-5 days"
            })
        
        return {
            "current_fatigue_level": fatigue,
            "current_recovery_level": recovery,
            "hrv_ratio_vs_baseline": round(hrv_ratio * 100, 1),
            "recommended_zones": recommended_zones,
            "prohibited_zones": prohibited_zones,
            "overall_recommendation": self._activity_rating(fatigue, recovery, hrv_ratio),
        }

    def risk_escalation_forecast(
        self,
        current_state: dict,
        recent_history: Optional[pd.DataFrame] = None
    ) -> Dict:
        """
        Predict if risk is escalating (next 3-7 days).
        
        Returns:
            Alert with escalation trajectory
        """
        fatigue = current_state.get("fatigue_index", 30)
        hrv = current_state.get("hrv_avg", 50)
        hrv_baseline = current_state.get("hrv_baseline", 50)
        recovery = current_state.get("recovery_index", 70)
        
        escalation_signals = []
        
        # Signal 1: HRV depression + fatigue rise
        if (hrv < hrv_baseline * 0.85) and (fatigue > 60):
            escalation_signals.append({
                "signal": "HRV depression + Fatigue accumulation",
                "severity": "HIGH",
                "days_until_critical": 2,
                "action": "URGENT: Reduce training volume immediately"
            })
        
        # Signal 2: Recovery collapsing
        if recovery < 30 and fatigue > 75:
            escalation_signals.append({
                "signal": "Recovery capacity collapsed",
                "severity": "HIGH",
                "days_until_critical": 1,
                "action": "MANDATORY: REST DAY required"
            })
        
        # Signal 3: Chronic HRV suppression
        if hrv < hrv_baseline * 0.75:
            escalation_signals.append({
                "signal": "Chronic HRV suppression (>25% below baseline)",
                "severity": "MEDIUM",
                "days_until_critical": 3,
                "action": "Reduce intensity + add 1-2 extra recovery days"
            })
        
        # Signal 4: Linear fatigue rise (bad trend)
        if recent_history is not None and len(recent_history) >= 5:
            fatigue_trend = self._extract_trend(recent_history.get("fatigue", []))
            if fatigue_trend > 5:  # Fatigue rising 5+ points/day
                escalation_signals.append({
                    "signal": "Fatigue accumulating faster than recovery",
                    "severity": "MEDIUM",
                    "days_until_critical": 4,
                    "action": "Reduce weekly training frequency"
                })
        
        if not escalation_signals:
            escalation_signals.append({
                "signal": "None detected",
                "severity": "LOW",
                "days_until_critical": 7,
                "action": "Continue current approach, monitor HRV"
            })
        
        return {
            "escalation_alerts": escalation_signals,
            "overall_risk_trajectory": "escalating" if escalation_signals[0]["severity"] in ["HIGH", "MEDIUM"] else "stable",
            "recommended_actions": [a["action"] for a in escalation_signals[:2]]
        }

    def golden_hour_recommendation(
        self,
        current_state: dict
    ) -> Dict:
        """
        Find the absolute best time in next 7 days for peak performance.
        (Based on projected fatigue/recovery curves)
        
        Returns:
            "Golden hour" window with reasoning
        """
        fatigue = current_state.get("fatigue_index", 30)
        recovery = current_state.get("recovery_index", 70)
        
        # Simple heuristic: recovery > 70 and fatigue < 50
        score = (recovery * 0.6) - (fatigue * 0.4)
        
        if score > 60:
            timing = "RIGHT NOW"
            window_duration = "Next 24 hours"
            reason = "Peak recovery state - optimal for high-intensity work"
        elif recovery > 65:
            timing = "Next 24-48 hours"
            window_duration = "36-48 hours"
            reason = "Good recovery window before fatigue accumulates"
        elif recovery > 55:
            timing = "Next 2-3 days"
            window_duration = "48-72 hours"
            reason = "Recovery sufficient for moderate-high intensity"
        else:
            timing = "Wait 3-5 days"
            window_duration = "After recovery accumulates"
            reason = "Current state suboptimal; allow recovery first"
        
        return {
            "golden_hour": timing,
            "window_duration": window_duration,
            "reason": reason,
            "expected_performance": "Maximum fitness benefit + minimal overtraining risk",
            "suggested_workout": self._suggest_workout_type(current_state),
            "estimated_ces_gain": round(score / 100 * 10, 1) if score > 0 else 0,
        }

    # ─────────────────────────────────────────────────────────────────────
    # Helper Methods
    # ─────────────────────────────────────────────────────────────────────

    def _extract_trend(self, series: List[float]) -> float:
        """Extract trend (slope) from time series."""
        if len(series) < 2:
            return 0.0
        series = np.array(series[-7:])  # Last 7 points
        if len(series) < 2:
            return 0.0
        x = np.arange(len(series))
        try:
            coeffs = np.polyfit(x, series, 1)
            return float(coeffs[0])
        except:
            return 0.0

    def _activity_rating(self, fatigue: float, recovery: float, hrv_ratio: float) -> str:
        """Rate current activity readiness."""
        if recovery > 75 and fatigue < 40 and hrv_ratio > 0.95:
            return "🟢 EXCELLENT: Peak performance window - can do any intensity"
        elif recovery > 65 and fatigue < 50 and hrv_ratio > 0.90:
            return "🟢 GOOD: Can do moderate-high intensity work"
        elif recovery > 50 and fatigue < 60:
            return "🟡 FAIR: Easy to moderate intensity only"
        elif recovery > 30 and fatigue < 75:
            return "🟡 CAUTION: Easy recovery work or rest recommended"
        else:
            return "🔴 WARNING: Rest day strongly recommended"

    def _suggest_workout_type(self, current_state: dict) -> str:
        """Suggest workout type based on current state."""
        recovery = current_state.get("recovery_index", 70)
        fatigue = current_state.get("fatigue_index", 30)
        
        if recovery > 70 and fatigue < 40:
            return "VO2max intervals or threshold work"
        elif recovery > 60 and fatigue < 50:
            return "Steady-state aerobic (Zone 3)"
        elif recovery > 50:
            return "Easy recovery run or cross-training"
        else:
            return "Complete rest or 20-min easy walk"
