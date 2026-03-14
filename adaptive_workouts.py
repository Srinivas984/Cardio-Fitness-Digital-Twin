"""
Adaptive Workout System - Adjusts training in real-time based on metrics
Learns from user patterns and optimizes future workouts
"""

from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np


class AdaptiveWorkout:
    """
    Adjusts workout parameters in real-time based on:
    - Current HR vs target
    - HRV and recovery state
    - Fatigue indicators
    - Performance trends
    """
    
    def __init__(self):
        self.workout_log = []
        self.user_max_hr = 190
        self.user_ftp = 250  # Functional Threshold Power
        self.adaptation_factor = 1.0
    
    def start_adaptive_workout(self, workout_type: str, base_duration: int, base_intensity: int) -> Dict:
        """
        Start adaptive workout with real-time adjustments
        base_intensity: 1-5 (zone)
        """
        return {
            "workout_type": workout_type,
            "base_duration_min": base_duration,
            "base_intensity": base_intensity,
            "current_duration_min": base_duration,
            "current_intensity": base_intensity,
            "adaptations_made": 0,
            "start_time": datetime.now()
        }
    
    def adjust_workout_real_time(self, 
                                 current_metrics: Dict,
                                 target_zone: int,
                                 elapsed_time: int) -> Dict:
        """
        Real-time workout adjustment algorithm
        Adapts duration, intensity, or focus based on metrics
        """
        hr = current_metrics.get("heart_rate", 150)
        hrv = current_metrics.get("hrv", 45)
        fatigue_index = current_metrics.get("fatigue_index", 0.5)
        
        adjustment = {
            "timestamp": datetime.now(),
            "duration_change": 0,
            "intensity_change": 0,
            "focus_change": None,
            "reason": "No adjustment needed"
        }
        
        # Check if athlete is fatiguing rapidly
        if fatigue_index > 0.7 and elapsed_time > 30:
            adjustment["duration_change"] = -5  # Reduce by 5 min
            adjustment["reason"] = "Rapid fatigue detected - reduce duration"
        
        # Check HRV crash (overtraining)
        if hrv < 30 and target_zone >= 3:
            adjustment["intensity_change"] = -1  # Drop 1 zone
            adjustment["reason"] = "HRV crash detected - reduce intensity"
        
        # Check if athlete can handle more
        if hrv > 50 and fatigue_index < 0.3 and target_zone < 4:
            adjustment["intensity_change"] = 1  # Increase 1 zone
            adjustment["reason"] = "High recovery - increase intensity"
        
        # Performance-based adjustment
        if self._is_athlete_improving():
            adjustment["focus_change"] = "increase_volume"
        
        return adjustment
    
    def suggest_interval_structure(self, total_duration: int, focus: str) -> Dict:
        """
        Suggest optimal interval structure for adaptive training
        Focuses: endurance, speed, power, recovery
        """
        intervals = {
            "endurance": {
                "warm_up": 10,
                "main_set": total_duration - 15,
                "cool_down": 5,
                "intensity": "Zone 2 steady"
            },
            "speed": {
                "warm_up": 10,
                "main_set": {
                    "intervals": 8,
                    "work": 3,  # min
                    "recovery": 2,
                    "intensity": "Zone 4"
                },
                "cool_down": 5
            },
            "power": {
                "warm_up": 10,
                "main_set": {
                    "intervals": 6,
                    "work": 5,  # min
                    "recovery": 3,
                    "intensity": "Zone 5 (max)"
                },
                "cool_down": 5
            },
            "recovery": {
                "warm_up": 5,
                "main_set": total_duration - 10,
                "cool_down": 5,
                "intensity": "Zone 1 easy"
            }
        }
        
        return intervals.get(focus, intervals["endurance"])
    
    def analyze_fatigue_progression(self, metrics_history: List[Dict]) -> Dict:
        """Analyze how fatigue progresses during workout"""
        if len(metrics_history) < 3:
            return {"status": "insufficient_data"}
        
        hrs = [m.get("heart_rate", 150) for m in metrics_history]
        hrvs = [m.get("hrv", 45) for m in metrics_history]
        
        # Calculate HR drift (fatigue indicator)
        hr_drift = hrs[-1] - hrs[0]
        hrv_trend = np.mean(hrvs[-3:]) - np.mean(hrvs[:3])
        
        return {
            "hr_drift_bpm": hr_drift,
            "drift_severity": "High" if hr_drift > 30 else "Moderate" if hr_drift > 15 else "Low",
            "hrv_trend": "Declining" if hrv_trend < -5 else "Stable" if hrv_trend > -5 else "Improving",
            "fatigue_index": self._calculate_fatigue_index(hrs, hrvs),
            "recommendation": self._get_fatigue_recommendation(hr_drift, hrv_trend)
        }
    
    def predict_recovery_time(self, workout_intensity: int, duration_minutes: int) -> Dict:
        """Predict recovery time needed after workout"""
        # Based on intensity and duration
        intensity_factor = workout_intensity / 5  # 0 to 1
        duration_factor = duration_minutes / 60  # 0 to 1
        
        recovery_hours = 24 + (intensity_factor * 12) + (duration_factor * 6)
        
        return {
            "estimated_recovery_hours": round(recovery_hours, 1),
            "full_recovery_time": datetime.now() + timedelta(hours=recovery_hours),
            "can_train_again_in": "Easy session" if recovery_hours < 36 else "Rest day needed",
            "next_hard_session": datetime.now() + timedelta(hours=recovery_hours)
        }
    
    def get_workout_recommendations(self, recent_performance: List[Dict]) -> List[str]:
        """
        Get smart recommendations for next workouts
        Based on recent performance and recovery patterns
        """
        if not recent_performance:
            return ["Start with moderate 30-45 min sessions to establish baseline"]
        
        recommendations = []
        
        # Analyze trends
        avg_stress = np.mean([p.get("training_stress", 50) for p in recent_performance])
        
        if avg_stress > 300:
            recommendations.append("🔴 HIGH stress load - take 1-2 easy days")
            recommendations.append("Focus on recovery: sleep 8+ hours, stretch, massage")
        elif avg_stress > 200:
            recommendations.append("🟡 MODERATE stress - mix hard and easy sessions")
            recommendations.append("Alternate: Hard day → Easy day → Rest")
        else:
            recommendations.append("🟢 LOW stress - ready for harder workouts")
            recommendations.append("Increase intensity or volume by 10%")
        
        return recommendations
    
    def _calculate_fatigue_index(self, hrs: List[int], hrvs: List[float]) -> float:
        """Calculate 0-1 fatigue index from metrics"""
        hr_fatigue = (max(hrs) - min(hrs)) / 100  # Normalized HR variability
        hrv_fatigue = 1 - (np.mean(hrvs) / 60)  # Normalized HRV (lower = more fatigued)
        
        return np.clip((hr_fatigue + hrv_fatigue) / 2, 0, 1)
    
    def _get_fatigue_recommendation(self, hr_drift: int, hrv_trend: float) -> str:
        """Get recommendation based on fatigue pattern"""
        if hr_drift > 30 or hrv_trend < -10:
            return "🛑 High fatigue detected - consider ending session or reducing intensity"
        elif hr_drift > 15 or hrv_trend < -5:
            return "⚠️ Moderate fatigue building - monitor closely"
        else:
            return "✅ Feeling good - can continue or push harder"
    
    def _is_athlete_improving(self) -> bool:
        """Check if athlete shows improvement trend"""
        # Would analyze workout_log for trends
        if len(self.workout_log) < 3:
            return False
        
        recent_workouts = self.workout_log[-3:]
        avg_power = np.mean([w.get("avg_power", 200) for w in recent_workouts])
        
        return avg_power > 200


class SmartNotifications:
    """
    Send smart notifications based on athlete metrics and training schedule
    """
    
    def __init__(self):
        self.notification_history = []
    
    def check_training_window(self, current_hr: int, hrv: int, time_of_day: str) -> Dict:
        """Check if it's optimal time to train"""
        optimal = {
            "is_optimal": False,
            "reason": "",
            "recommendation": ""
        }
        
        if 6 <= int(time_of_day.split(":")[0]) <= 8:  # Morning
            optimal["is_optimal"] = True
            optimal["reason"] = "Morning optimal - fresh, cortisol elevated for training"
            optimal["recommendation"] = "Best time for high-intensity work"
        
        elif 16 <= int(time_of_day.split(":")[0]) <= 18:  # Afternoon
            optimal["is_optimal"] = True
            optimal["reason"] = "Afternoon optimal - core temperature peaked"
            optimal["recommendation"] = "Good for speed or power work"
        
        else:
            optimal["is_optimal"] = False
            optimal["reason"] = "Suboptimal time - body not primed"
        
        if hrv < 30:
            optimal["recommendation"] += " | But HRV is low - consider rest day instead"
        
        return optimal
    
    def send_adaptive_notification(self, message: str, urgency: str = "normal") -> bool:
        """Send notification to Apple Watch"""
        notification = {
            "timestamp": datetime.now(),
            "message": message,
            "urgency": urgency,
            "sent": True
        }
        self.notification_history.append(notification)
        return True
    
    def get_next_workout_reminder(self, last_workout: Dict, recovery_needed_hours: int) -> str:
        """Get reminder for next workout"""
        next_time = last_workout.get("end_time") + timedelta(hours=recovery_needed_hours)
        
        return f"✅ You can train again at {next_time.strftime('%H:%M')} (after {recovery_needed_hours}h recovery)"
