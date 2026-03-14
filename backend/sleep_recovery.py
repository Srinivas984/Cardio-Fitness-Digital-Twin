"""
sleep_recovery.py
-----------------
Sleep analysis and its impact on cardiovascular recovery.

Analyzes:
  - Sleep quality correlation with HRV
  - Sleep debt accumulation
  - Optimal sleep windows for recovery
  - Sleep quality score
  - Recovery predictions based on sleep
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SleepRecoveryAnalyzer:
    """Analyzes sleep-recovery relationships."""

    def __init__(self):
        self.sleep_targets = {
            "standard": 8.0,
            "recovery": 9.0,
            "debt_repayment": 9.5,
            "minimum": 7.0
        }
        self.sleep_history = []

    def add_sleep_data(
        self,
        date: datetime,
        duration_hours: float,
        quality_score: float,  # 1-10 scale
        notes: Optional[str] = None
    ) -> Dict:
        """
        Log sleep data point.
        
        Args:
            date: Sleep date
            duration_hours: Hours slept
            quality_score: Subjective or wearable quality (1-10)
            notes: Optional notes (wakeups, stress, etc)
        """
        
        entry = {
            "date": date,
            "duration": duration_hours,
            "quality": quality_score,
            "notes": notes,
            "logged_at": datetime.now()
        }
        
        self.sleep_history.append(entry)
        return entry

    def analyze_sleep_hrv_correlation(
        self,
        sleep_data: List[Dict],
        hrv_data: pd.DataFrame
    ) -> Dict:
        """
        Analyze correlation between previous night's sleep and next-day HRV.
        
        Shows: Sleep quality → HRV response lag (usually 8-24 hours)
        """
        
        if not sleep_data or hrv_data is None or len(hrv_data) < 7:
            return {
                "correlation": "Insufficient data",
                "sample_size": len(sleep_data)
            }
        
        # Extract sleep quality scores
        sleep_quality = np.array([entry.get("quality", 5) for entry in sleep_data[-7:]])
        
        # Extract next-day HRV  (assuming HRV data is daily averages)
        try:
            hrv_values = hrv_data[-7:].values if hasattr(hrv_data, 'values') else hrv_data[-7:]
            hrv_values = np.array([float(x) if x else 0 for x in hrv_values])
        except:
            hrv_values = np.array([50] * len(sleep_quality))
        
        # Calculate correlation
        if len(sleep_quality) >= 5 and len(hrv_values) >= 5:
            correlation = np.corrcoef(sleep_quality, hrv_values)[0, 1]
        else:
            correlation = 0.0
        
        interpretation = self._interpret_sleep_hrv_correlation(correlation)
        
        return {
            "correlation_coefficient": round(correlation, 2),
            "interpretation": interpretation,
            "sample_size": len(sleep_quality),
            "implication": "Sleep quality significantly impacts next-day HRV" if abs(correlation) > 0.5 else \
                          "Sleep quality moderately impacts next-day HRV" if abs(correlation) > 0.3 else \
                          "Sleep quality has weak correlation with HRV (other factors dominant)"
        }

    def calculate_sleep_debt(
        self,
        sleep_history: List[Dict],
        target_hours: float = 8.0,
        lookback_days: int = 7
    ) -> Dict:
        """
        Calculate cumulative sleep debt.
        
        Args:
            sleep_history: List of daily sleep entries
            target_hours: Target sleep duration
            lookback_days: How many days to analyze
            
        Returns:
            Sleep debt in hours + implications
        """
        
        if not sleep_history:
            return {"debt_hours": 0, "status": "No data"}
        
        recent_sleep = sleep_history[-lookback_days:] if len(sleep_history) >= lookback_days else sleep_history
        
        total_sleep = sum(entry.get("duration", 8) for entry in recent_sleep)
        total_target = target_hours * len(recent_sleep)
        debt = max(0, total_target - total_sleep)
        
        # Risk assessment
        if debt == 0:
            status = "🟢 No sleep debt"
            impact = "Optimal recovery state"
        elif debt < 3:
            status = "🟡 Minor sleep debt"
            impact = "Slightly reduced recovery capacity, HRV may be 3-5% suppressed"
        elif debt < 7:
            status = "🟡 Moderate sleep debt"
            impact = "Noticeably reduced HRV + recovery, consider light training"
        else:
            status = "🔴 Severe sleep debt"
            impact = "Significantly compromised recovery, risk of illness/injury"
        
        # Repayment time
        repayment_days = debt / target_hours if target_hours > 0 else 0
        
        return {
            "total_debt_hours": round(debt, 1),
            "status": status,
            "impact_on_recovery": impact,
            "days_to_repay": round(repayment_days, 1),
            "repayment_strategy": self._get_debt_repayment_strategy(debt),
            "lookback_period": f"Last {len(recent_sleep)} days"
        }

    def predict_hrv_from_sleep(
        self,
        last_night_sleep_hours: float,
        last_night_sleep_quality: float,  # 1-10
        personal_baseline_hrv: float,
        sleep_sensitivity: float = 0.5  # How much sleep affects this person (0-1)
    ) -> Dict:
        """
        Predict today's HRV based on last night's sleep.
        
        Sleep quality and duration → HRV multiplier
        """
        
        # Base HRV from sleep
        sleep_quality_factor = last_night_sleep_quality / 10.0  # Normalize 0-1
        sleep_duration_factor = min(last_night_sleep_hours / 8.0, 1.2)  # Cap at 1.2x (oversleep doesn't help)
        
        sleep_benefit = (sleep_quality_factor * sleep_duration_factor) ** (1 + sleep_sensitivity)
        
        predicted_hrv = personal_baseline_hrv * (0.85 + (sleep_benefit * 0.25))  # HRV range: 85-110% baseline
        
        interpretation = f"Based on {last_night_sleep_hours}h sleep @ quality {last_night_sleep_quality}/10"
        
        if predicted_hrv > personal_baseline_hrv * 1.05:
            outlook = "🟢 Excellent HRV expected - ready for hard work"
        elif predicted_hrv > personal_baseline_hrv * 0.95:
            outlook = "🟢 Normal HRV expected - standard training safe"
        elif predicted_hrv > personal_baseline_hrv * 0.85:
            outlook = "🟡 Slightly suppressed HRV - easy/moderate work only"
        else:
            outlook = "🔴 Poor HRV expected - recovery focus"
        
        return {
            "predicted_hrv_ms": round(predicted_hrv, 0),
            "ratio_to_baseline": round(predicted_hrv / personal_baseline_hrv * 100, 0),
            "interpretation": interpretation,
            "activity_outlook": outlook,
            "confidence": "Moderate" if sleep_sensitivity > 0.3 else "Low"
        }

    def optimal_sleep_schedule(
        self,
        current_fatigue_level: float,  # 0-100
        training_intensity_level: str,  # "low", "moderate", "high"
        chronotype: str = "normal"  # "early_bird", "night_owl", "normal"
    ) -> Dict:
        """
        Recommend optimal sleep schedule based on training demands.
        """
        
        # Base target
        if training_intensity_level == "low":
            target_hours = 7.5
        elif training_intensity_level == "moderate":
            target_hours = 8.0
        else:  # high
            target_hours = 9.0
        
        # Adjust for fatigue
        if current_fatigue_level > 70:
            target_hours = min(9.5, target_hours + 1.0)
        
        # Chronotype adjustment (time not duration)
        bedtimes = {
            "early_bird": "21:00-22:00 (sleep 5:30-6:30)",
            "night_owl": "23:30-00:30 (sleep 7:30-8:30)",
            "normal": "22:00-23:00 (sleep 6:00-7:00)"
        }
        
        return {
            "target_sleep_duration": round(target_hours, 1),
            "recommended_bedtime": bedtimes.get(chronotype, bedtimes["normal"]),
            "wake_time": self._calculate_wake_time(target_hours),
            "rationale": f"{training_intensity_level} intensity training requires {target_hours}h sleep",
            "sleep_stages_focus": self._recommend_sleep_focus(training_intensity_level),
            "pre_sleep_routine": self._pre_sleep_recommendations(current_fatigue_level)
        }

    def sleep_quality_score(
        self,
        duration_hours: float,
        subjective_quality: Optional[float] = None,  # 1-10
        wakeups: int = 0,
        morning_hrv: Optional[float] = None,
        baseline_hrv: Optional[float] = None
    ) -> Dict:
        """
        Calculate comprehensive sleep quality score (0-100).
        """
        
        score = 0.0
        factors = {}
        
        # Duration component (0-40 points)
        if 7 <= duration_hours <= 9:
            duration_score = 40
            factors["duration"] = "Optimal (7-9h)"
        elif 6.5 <= duration_hours < 7 or 9 < duration_hours <= 9.5:
            duration_score = 30
            factors["duration"] = "Good (6.5-9.5h)"
        elif 6 <= duration_hours < 6.5 or 9.5 < duration_hours <= 10:
            duration_score = 20
            factors["duration"] = "Suboptimal"
        else:
            duration_score = 10
            factors["duration"] = "Poor"
        
        score += duration_score
        
        # Quality component (0-30 points)
        if subjective_quality is not None:
            quality_score = min(30, subjective_quality * 3)
            factors["quality"] = f"Subjective: {subjective_quality}/10"
            score += quality_score
        
        # Wakeup component (0-15 points)
        if wakeups == 0:
            wakeup_score = 15
        elif wakeups <= 1:
            wakeup_score = 10
        elif wakeups <= 2:
            wakeup_score = 5
        else:
            wakeup_score = 0
        
        factors["fragmentation"] = f"{wakeups} wakeups"
        score += wakeup_score
        
        # HRV recovery component (0-15 points)
        if morning_hrv is not None and baseline_hrv is not None and baseline_hrv > 0:
            hrv_ratio = morning_hrv / baseline_hrv
            if hrv_ratio > 1.0:
                hrv_score = 15
            elif hrv_ratio > 0.95:
                hrv_score = 12
            elif hrv_ratio > 0.85:
                hrv_score = 8
            else:
                hrv_score = 3
            
            factors["hrv_recovery"] = f"{(hrv_ratio*100):.0f}% of baseline"
            score += hrv_score
        
        return {
            "overall_score": round(score, 0),
            "grade": "A" if score >= 80 else "B" if score >= 70 else "C" if score >= 60 else "D" if score >= 50 else "F",
            "interpretation": f"Sleep quality {'excellent' if score >= 80 else 'good' if score >= 70 else 'fair' if score >= 60 else 'poor'}",
            "component_scores": factors,
            "next_night_recommendation": "Maintain current sleep habits" if score >= 70 else "Improve sleep environment and schedule"
        }

    # ─────────────────────────────────────────────────────────────────────
    # Helper Methods
    # ─────────────────────────────────────────────────────────────────────

    def _interpret_sleep_hrv_correlation(self, correlation: float) -> str:
        """Interpret sleep-HRV correlation strength."""
        if correlation > 0.7:
            return "Very Strong - Sleep is primary HRV driver"
        elif correlation > 0.5:
            return "Strong - Sleep significantly impacts HRV"
        elif correlation > 0.3:
            return "Moderate - Sleep important but not sole factor"
        elif correlation > 0:
            return "Weak - Sleep has minor HRV impact"
        else:
            return "Negative - Unusual pattern, monitor"

    def _get_debt_repayment_strategy(self, debt_hours: float) -> str:
        """Recommend sleep debt repayment approach."""
        
        if debt_hours < 3:
            return "Add 30 min per night for 3-5 nights"
        elif debt_hours < 7:
            return "Add 1 hour per night for 5-7 nights, or 2-hour weekend catch-up"
        else:
            return "URGENT: Add 1.5 hours per night until repaid, reduce training volume"

    def _calculate_wake_time(self, sleep_hours: float) -> str:
        """Calculate recommended wake time given sleep hours."""
        mins = int((sleep_hours % 1) * 60)
        hours_part = int(sleep_hours)
        
        return f"Sleep {hours_part}h {mins}min (e.g., sleep 22:00 → wake 6:{"00" if mins ==0 else mins})"

    def _recommend_sleep_focus(self, training_intensity: str) -> Dict:
        """Recommend which sleep stages to prioritize."""
        
        stages = {
            "low": {
                "light_sleep": "Maintain normal (30-40%)",
                "deep_sleep": "Standard (13-23%)",
                "rem_sleep": "Standard (20-25%)",
                "focus": "General recovery only"
            },
            "moderate": {
                "light_sleep": "Maintain (30-40%)",
                "deep_sleep": "Increase (15-25%)",
                "rem_sleep": "Standard (20-25%)",
                "focus": "Deepen sleep via cool room, consistency"
            },
            "high": {
                "light_sleep": "Reduce (25-35%)",
                "deep_sleep": "Maximize (18-27%)",
                "rem_sleep": "Optimize (20-30%)",
                "focus": "Prioritize deep sleep for muscle recovery + REM for cognitive recovery"
            }
        }
        
        return stages.get(training_intensity, stages["moderate"])

    def _pre_sleep_recommendations(self, fatigue_level: float) -> List[str]:
        """Recommend pre-sleep routine based on fatigue."""
        
        if fatigue_level > 70:
            return [
                "90 min before bed: Cool shower (65-68°F)",
                "60 min before: Light meal (carbs + protein)",
                "30 min before: Dim lights, meditation app",
                "Avoid: Screens, caffeine, intense discussion"
            ]
        else:
            return [
                "60 min before: Reduced blue light",
                "30 min before: Light stretching or yoga",
                "Standard routine: 7.5-8.5h target",
                "Consistency: Same bed/wake time daily"
            ]
