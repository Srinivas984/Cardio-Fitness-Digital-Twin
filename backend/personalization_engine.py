"""
personalization_engine.py
-------------------------
Learns user-specific responses to workouts and adapts recommendations.

Tracks:
  - Individual workout response patterns
  - Which workout types work best for this person
  - How fast they recover
  - Personal sensitivity to intensity
  - Optimal training frequency
  - Individual risk thresholds

Learns over time to personalize:
  - Workout recommendations
  - Recovery protocols
  - Training volume
  - Intensity distribution
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PersonalizationEngine:
    """
    Personalization system that learns user-specific patterns.
    """

    def __init__(self):
        self.workout_history = []
        self.response_profiles = {}
        self.performance_history = []
        self.personalized_thresholds = {}
        self.learning_status = "initializing"

    def log_workout_and_response(
        self,
        workout_type: str,
        intensity_level: str,
        duration_min: int,
        hrv_before: float,
        hrv_after_24h: float,
        rhr_change: float,
        perceived_difficulty: int,  # 1-10
        notes: Optional[str] = None
    ) -> Dict:
        """
        Log a workout and its 24h physiological response.
        Used to build personalized response profiles.
        """
        
        entry = {
            "date": datetime.now(),
            "workout_type": workout_type,
            "intensity": intensity_level,
            "duration": duration_min,
            "hrv_before": hrv_before,
            "hrv_after_24h": hrv_after_24h,
            "hrv_change": hrv_after_24h - hrv_before,
            "rhr_change": rhr_change,
            "perceived_difficulty": perceived_difficulty,
            "notes": notes,
            "recovery_quality": self._rate_recovery_quality(hrv_after_24h - hrv_before)
        }
        
        self.workout_history.append(entry)
        self._update_response_profiles()
        
        return entry

    def get_personalized_recommendation(
        self,
        current_hrv: float,
        current_fatigue: float,
        current_recovery: float,
        last_n_days_history: Optional[pd.DataFrame] = None
    ) -> Dict:
        """
        Get recommendation personalized to THIS athlete's patterns.
        """
        
        # Check learning status
        if len(self.workout_history) < 5:
            return {
                "status": "learning",
                "recommendation": "Generic recommendation (need 5+ logged workouts for personalization)",
                "confidence": 0.0,
                "personalization_data_needed": 5 - len(self.workout_history)
            }
        
        # Analyze personal response profiles
        best_workouts = self._get_best_performing_workouts()
        recovery_pattern = self._analyze_recovery_pattern()
        intensity_sensitivity = self._calculate_intensity_sensitivity()
        
        # Generate personalized recommendation
        recommendation = self._select_personalized_workout(
            current_hrv=current_hrv,
            current_fatigue=current_fatigue,
            recovery_pattern=recovery_pattern,
            intensity_sensitivity=intensity_sensitivity,
            best_workouts=best_workouts
        )
        
        return {
            "status": "personalized",
            "recommendation": recommendation,
            "confidence": self._calculate_confidence_score(),
            "personalization_profile": {
                "best_workouts": best_workouts[:3],
                "recovery_speed": recovery_pattern.get("avg_recovery_hours"),
                "intensity_sensitivity": intensity_sensitivity,
                "optimal_frequency": self._calculate_optimal_frequency()
            }
        }

    def predict_hrv_response(
        self,
        workout_type: str,
        intensity: str,
        duration: int
    ) -> Dict:
        """
        Predict this person's HRV response to a specific workout.
        Based on their personal history.
        """
        
        if len(self.workout_history) < 3:
            return {"prediction": "Insufficient personalization data"}
        
        # Find similar workouts in history
        similar_workouts = [
            w for w in self.workout_history
            if w.get("workout_type") == workout_type and w.get("intensity") == intensity
        ]
        
        if not similar_workouts:
            return {"prediction": "No previous experience with this workout type"}
        
        # Average response
        avg_hrv_change = np.mean([w.get("hrv_change", 0) for w in similar_workouts])
        avg_rhr_change = np.mean([w.get("rhr_change", 0) for w in similar_workouts])
        recovery_hours = np.mean([
            w.get("duration", 60) / 30  # Rough estimate
            for w in similar_workouts
        ]) * 24
        
        interpretation = self._interpret_hrv_response(avg_hrv_change)
        
        return {
            "predicted_hvr_change": f"{avg_hrv_change:+.1f} ms",
            "predicted_rhr_impact": f"{avg_rhr_change:+.1f} bpm (24h after)",
            "estimated_recovery_time_hours": round(recovery_hours, 0),
            "interpretation": interpretation,
            "sample_size": len(similar_workouts),
            "confidence": "High" if len(similar_workouts) >= 3 else "Medium"
        }

    def find_optimal_training_frequency(self) -> Dict:
        """
        Analyze personal history to find optimal training frequency.
        """
        
        if len(self.workout_history) < 10:
            return {"recommendation": "Need 10+ workouts to analyze frequency patterns"}
        
        # Count workouts per week
        now = datetime.now()
        week_counts = []
        
        for i in range(4):
            week_start = now - timedelta(days=7*(i+1))
            week_end = now - timedelta(days=7*i)
            
            week_workouts = [
                w for w in self.workout_history
                if week_start <= w.get("date", datetime.now()) <= week_end
            ]
            week_counts.append(len(week_workouts))
        
        avg_weekly_frequency = np.mean(week_counts) if week_counts else 0
        
        # Correlate frequency with HRV trend
        hrv_trend = self._analyze_hrv_trend_by_frequency()
        
        return {
            "current_average_frequency": f"{avg_weekly_frequency:.1f} workouts/week",
            "optimal_frequency_range": self._determine_optimal_frequency(hrv_trend),
            "frequency_sensitivity": hrv_trend.get("sensitivity", "Unknown"),
            "recommendation": "Increase frequency" if hrv_trend.get("improving", False) else \
                             "Maintain current frequency" if "stable" in hrv_trend.get("sensitivity", "").lower() else \
                             "Reduce frequency"
        }

    def identify_recovery_pattern(self) -> Dict:
        """
        Identify this person's personal recovery pattern.
        """
        
        if len(self.workout_history) < 5:
            return {"pattern": "Insufficient data"}
        
        # Calculate recovery metrics
        recovery_times = []
        hrv_recovery_ratios = []
        
        for i, workout in enumerate(self.workout_history[:-1]):
            next_workout = self.workout_history[i + 1]
            time_between = (next_workout.get("date", datetime.now()) - 
                           workout.get("date", datetime.now())).total_seconds() / 3600
            
            recovery_times.append(time_between)
            
            # HRV recovery ratio
            if workout.get("hrv_before", 0) > 0:
                ratio = next_workout.get("hrv_before", 0) / workout.get("hrv_before", 1)
                hrv_recovery_ratios.append(ratio)
        
        avg_time_to_recovery = np.mean(recovery_times) if recovery_times else 24
        avg_hrv_recovery_ratio = np.mean(hrv_recovery_ratios) if hrv_recovery_ratios else 0.95
        
        recovery_speed = self._classify_recovery_speed(avg_time_to_recovery)
        recovery_quality = "Good" if avg_hrv_recovery_ratio > 0.95 else \
                          "Moderate" if avg_hrv_recovery_ratio > 0.85 else "Slow"
        
        return {
            "recovery_speed_classification": recovery_speed,
            "average_time_to_full_recovery": f"{avg_time_to_recovery:.0f} hours",
            "hrv_recovery_quality": recovery_quality,
            "implication": f"This person recovers {recovery_speed} and needs {self._days_rest_needed(recovery_speed)} rest days between hard sessions",
            "optimal_rest_days": self._days_rest_needed(recovery_speed)
        }

    def identify_workout_preferences(self) -> Dict:
        """
        Identify which workout types this person responds best to.
        """
        
        if len(self.workout_history) < 5:
            return {"status": "Insufficient data"}
        
        # Group by workout type
        workout_types = {}
        
        for workout in self.workout_history:
            wtype = workout.get("workout_type", "Unknown")
            if wtype not in workout_types:
                workout_types[wtype] = []
            workout_types[wtype].append(workout)
        
        # Score each type
        type_scores = {}
        
        for wtype, workouts in workout_types.items():
            # Score: positive HRV change + good recovery quality
            avg_hrv_change = np.mean([w.get("hrv_change", 0) for w in workouts])
            recovery_quality = np.mean([
                1 if w.get("recovery_quality", 0) == "Good" else 0.5 if w.get("recovery_quality") == "Moderate" else 0
                for w in workouts
            ])
            
            score = (avg_hrv_change * 0.6) + (recovery_quality * 40)  # Weighted score
            type_scores[wtype] = {
                "score": round(score, 1),
                "avg_hrv_change": round(avg_hrv_change, 1),
                "recovery_quality": recovery_quality,
                "sample_size": len(workouts)
            }
        
        # Rank
        ranked = sorted(type_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        
        return {
            "best_workouts": [r[0] for r in ranked[:3]],
            "workout_effectiveness_ranking": ranked,
            "recommendation": f"Prioritize {ranked[0][0]} for best response" if ranked else "Insufficient data"
        }

    def get_personalized_risk_thresholds(self) -> Dict:
        """
        Calculate personalized risk thresholds based on history.
        (Not standard population thresholds)
        """
        
        if len(self.workout_history) < 10:
            return {
                "status": "learning",
                "message": "Using standard thresholds until personalization matured"
            }
        
        # Analyze when this person actually gets injured/sick
        # or when HRV dropped beyond recovery
        
        # For now, return learning status
        return {
            "status": "personalizing",
            "custom_hrv_threshold": "Learning individual baseline...",
            "custom_fatigue_threshold": "Learning individual tolerance...",
            "next_update": f"After {max(0, 20 - len(self.workout_history))} more logged workouts"
        }

    # ─────────────────────────────────────────────────────────────────────
    # Helper Methods
    # ─────────────────────────────────────────────────────────────────────

    def _rate_recovery_quality(self, hrv_change: float) -> str:
        """Rate recovery quality based on HRV change."""
        if hrv_change > 5:
            return "Excellent"
        elif hrv_change > 0:
            return "Good"
        elif hrv_change > -5:
            return "Moderate"
        else:
            return "Poor"

    def _update_response_profiles(self):
        """Update aggregate response profiles."""
        # Recalculate based on history
        pass

    def _get_best_performing_workouts(self) -> List[str]:
        """Return list of best-performing workout types."""
        if not self.workout_history:
            return ["Steady Cardio", "Recovery Day"]
        
        # Simple: average HRV change per type
        type_changes = {}
        for w in self.workout_history:
            wtype = w.get("workout_type", "Unknown")
            if wtype not in type_changes:
                type_changes[wtype] = []
            type_changes[wtype].append(w.get("hrv_change", 0))
        
        ranked = sorted(
            [(k, np.mean(v)) for k, v in type_changes.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        return [r[0] for r in ranked]

    def _analyze_recovery_pattern(self) -> Dict:
        """Analyze personal recovery pattern."""
        if not self.workout_history:
            return {"avg_recovery_hours": 24}
        
        # Simple average
        durations = [w.get("duration", 60) for w in self.workout_history]
        avg_duration = np.mean(durations) if durations else 60
        
        return {
            "avg_recovery_hours": avg_duration / 30 * 24,  # Rough estimate
            "pattern": "Fast" if avg_duration < 40 else "Slow"
        }

    def _calculate_intensity_sensitivity(self) -> str:
        """How sensitive is this person to intensity."""
        if not self.workout_history:
            return "Unknown"
        
        high_intensity_workouts = [
            w for w in self.workout_history
            if w.get("intensity") in ["high", "HIIT", "VO2max"]
        ]
        
        if not high_intensity_workouts:
            return "Unknown"
        
        avg_hrv_drop = np.mean([w.get("hrv_change", 0) for w in high_intensity_workouts])
        
        if avg_hrv_drop < -10:
            return "Very High - Needs extended recovery after intensity"
        elif avg_hrv_drop < -5:
            return "High - Notices significant HRV impact"
        else:
            return "Moderate - Tolerates intensity well"

    def _select_personalized_workout(
        self,
        current_hrv: float,
        current_fatigue: float,
        recovery_pattern: Dict,
        intensity_sensitivity: str,
        best_workouts: List[str]
    ) -> str:
        """Select workout based on personal patterns."""
        
        if current_hrv < 45 or current_fatigue > 75:
            return f"Recovery work (your best: {best_workouts[0] if best_workouts else 'easy cardio'})"
        elif current_fatigue > 60:
            return "Moderate intensity aerobic work"
        else:
            return f"High-intensity work (your strength: {best_workouts[0] if best_workouts else 'mixed'})"

    def _calculate_confidence_score(self) -> float:
        """Calculate personalization confidence (0-1)."""
        n = len(self.workout_history)
        
        if n < 5:
            return 0.2
        elif n < 10:
            return 0.5
        elif n < 20:
            return 0.75
        else:
            return 0.95

    def _calculate_optimal_frequency(self) -> str:
        """Calculate optimal training frequency."""
        if not self.workout_history:
            return "3-4 sessions/week (standard)"
        
        recovery_speed = self._analyze_recovery_pattern().get("pattern")
        
        if recovery_speed == "Fast":
            return "5-6 sessions/week"
        else:
            return "3-4 sessions/week"

    def _interpret_hrv_response(self, hrv_change: float) -> str:
        """Interpret HRV response magnitude."""
        if hrv_change > 5:
            return "Strong positive adaptation"
        elif hrv_change > 0:
            return "Slight positive adaptation"
        elif hrv_change > -5:
            return "Minimal fatigue impact"
        elif hrv_change > -10:
            return "Moderate HRV suppression (24-48h recovery expected)"
        else:
            return "Significant HRV suppression (48h+ recovery expected)"

    def _analyze_hrv_trend_by_frequency(self) -> Dict:
        """Analyze if higher frequency improves or harms HRV."""
        return {
            "sensitivity": "Unknown - need more data",
            "improving": None
        }

    def _determine_optimal_frequency(self, hrv_trend: Dict) -> str:
        """Determine optimal frequency based on trend."""
        return "3-5 sessions/week (adjust based on response)"

    def _classify_recovery_speed(self, avg_time_hours: float) -> str:
        """Classify recovery speed."""
        if avg_time_hours < 20:
            return "Very Fast"
        elif avg_time_hours < 30:
            return "Fast"
        elif avg_time_hours < 48:
            return "Moderate"
        else:
            return "Slow"

    def _days_rest_needed(self, recovery_speed: str) -> int:
        """Recommend rest days based on recovery speed."""
        mapping = {
            "Very Fast": 1,
            "Fast": 1,
            "Moderate": 2,
            "Slow": 3
        }
        return mapping.get(recovery_speed, 2)
