"""
Live AI Personal Coach - Real-time coaching engine
Provides adaptive guidance, smart notifications, and workout adjustments
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import numpy as np


class LivePersonalCoach:
    """
    Real-time AI coach that adapts to live metrics
    Provides coaching cues, pacing guidance, recovery tips
    """
    
    def __init__(self):
        self.session_start_time = None
        self.target_zones = {}
        self.coaching_history = []
        self.alert_threshold = 0.85  # 85% max HR
    
    def start_session(self, workout_type: str, duration_minutes: int, target_hr_zone: int = 2):
        """Start coaching session"""
        self.session_start_time = datetime.now()
        self.target_zones = self._calculate_zones(target_hr_zone)
        self.coaching_history = []
        
        return {
            "status": "Session started",
            "workout_type": workout_type,
            "duration_min": duration_minutes,
            "target_zone": target_hr_zone,
            "zones": self.target_zones
        }
    
    def get_real_time_coaching(self, current_hr: int, target_zone: int, elapsed_seconds: int) -> Dict:
        """
        Provide real-time coaching based on current metrics
        Returns coaching cue, intensity adjustment, next action
        """
        zone_info = self._get_zone_info(current_hr, target_zone)
        coaching_cue = self._generate_coaching_cue(current_hr, target_zone, zone_info)
        intensity_adjustment = self._calculate_intensity_adjustment(current_hr, target_zone)
        
        elapsed_minutes = elapsed_seconds / 60
        
        coaching = {
            "timestamp": datetime.now(),
            "current_hr": current_hr,
            "target_zone": target_zone,
            "zone_info": zone_info,
            "coaching_cue": coaching_cue,
            "intensity_adjustment": intensity_adjustment,
            "elapsed_minutes": round(elapsed_minutes, 1),
            "next_action": self._get_next_action(current_hr, target_zone, elapsed_minutes),
            "urgency": "high" if abs(current_hr - zone_info["target"]) > 20 else "low"
        }
        
        self.coaching_history.append(coaching)
        return coaching
    
    def get_pacing_guidance(self, current_hr: int, max_hr: int, pace: float) -> str:
        """Get pacing guidance (slower, maintain, push, recover)"""
        target_hr = max_hr * 0.75  # Zone 2 baseline
        
        if current_hr < target_hr - 20:
            return "🔼 PUSH - Pick up the pace, you're below target"
        elif current_hr < target_hr - 10:
            return "↗️ ACCELERATE - Gradually increase intensity"
        elif current_hr > target_hr + 20:
            return "🔽 EASE - Back off pace, getting too hot"
        elif current_hr > target_hr + 10:
            return "↘️ DECELERATE - Slightly reduce intensity"
        else:
            return "✅ PERFECT PACE - Hold steady, great work!"
    
    def get_recovery_cues(self, current_hr: int, target_zone: int) -> List[str]:
        """Get recovery-focused coaching cues"""
        cues = []
        
        if target_zone == 1:  # Easy zone
            if current_hr > 120:
                cues.append("💨 Breathe deeper - slow your breathing")
                cues.append("🚶 Ease into recovery pace")
        
        cues.append("💧 Stay hydrated - sip water regularly")
        cues.append("🧠 Mental focus - you're building aerobic base")
        
        return cues
    
    def detect_overexertion(self, current_hr: int, max_hr: int, duration_minutes: float) -> Dict:
        """Detect if athlete is overexerting and provide guidance"""
        hr_percentage = (current_hr / max_hr) * 100
        
        alert = {
            "is_overexerting": hr_percentage > 85,
            "hr_percentage": round(hr_percentage, 1),
            "recommendation": "",
            "urgency": "normal"
        }
        
        if hr_percentage > 95:
            alert["recommendation"] = "⚠️ CRITICAL: Reduce intensity immediately - avoid injury!"
            alert["urgency"] = "critical"
        elif hr_percentage > 90:
            alert["recommendation"] = "⚠️ HIGH INTENSITY: Consider backing off soon"
            alert["urgency"] = "high"
        elif hr_percentage > 85:
            alert["recommendation"] = "ℹ️ NEAR LIMIT: Monitor closely"
            alert["urgency"] = "medium"
        else:
            alert["recommendation"] = "✅ Within safe limits"
            alert["urgency"] = "normal"
        
        return alert
    
    def suggest_break(self, duration_minutes: float, avg_hr: int, max_hr: int) -> Dict:
        """Suggest break/recovery window"""
        hr_percentage = (avg_hr / max_hr) * 100
        
        return {
            "should_take_break": duration_minutes > 45 and hr_percentage > 70,
            "reason": "Recovery window recommended" if duration_minutes > 45 else "Keep going",
            "suggested_break_duration_min": 2,
            "next_recovery_window": "5 minutes"
        }
    
    def get_session_summary(self, metrics: Dict) -> Dict:
        """Get end-of-session summary"""
        if not self.coaching_history:
            return {"error": "No coaching data collected"}
        
        hrs = [c["current_hr"] for c in self.coaching_history if "current_hr" in c]
        
        return {
            "session_duration_min": metrics.get("duration", 0),
            "avg_hr": round(np.mean(hrs)) if hrs else 0,
            "max_hr": max(hrs) if hrs else 0,
            "min_hr": min(hrs) if hrs else 0,
            "calories_burned": metrics.get("calories", 0),
            "training_effect": "✅ Good workout" if metrics.get("calories", 0) > 200 else "⚠️ Keep intensity",
            "recovery_time_hours": 24,
            "notes": "Great effort! Remember to hydrate and eat within 30 min"
        }
    
    def _calculate_zones(self, zone: int) -> Dict:
        """Calculate HR zones"""
        max_hr = 190
        return {
            1: {"min": 0, "max": int(max_hr * 0.60), "name": "Recovery"},
            2: {"min": int(max_hr * 0.60), "max": int(max_hr * 0.75), "name": "Aerobic"},
            3: {"min": int(max_hr * 0.75), "max": int(max_hr * 0.85), "name": "Tempo"},
            4: {"min": int(max_hr * 0.85), "max": int(max_hr * 0.95), "name": "Threshold"},
            5: {"min": int(max_hr * 0.95), "max": max_hr, "name": "Maximum"},
        }
    
    def _get_zone_info(self, current_hr: int, target_zone: int) -> Dict:
        """Get info about current zone"""
        zones = self._calculate_zones(1)  # Get all zones
        zone = zones[target_zone]
        
        return {
            "name": zone["name"],
            "target": (zone["min"] + zone["max"]) // 2,
            "min": zone["min"],
            "max": zone["max"],
            "current_offset": current_hr - ((zone["min"] + zone["max"]) // 2)
        }
    
    def _generate_coaching_cue(self, current_hr: int, target_zone: int, zone_info: Dict) -> str:
        """Generate smart coaching cue based on metrics"""
        offset = zone_info["current_offset"]
        zone_name = zone_info["name"]
        
        cues = {
            1: {  # Recovery
                "positive": "Perfect recovery pace! 🧘 Focus on breathing and relaxation",
                "slow": "You can go a bit faster if you want 🚶",
                "fast": "Ease back - stay in easy zone 💚"
            },
            2: {  # Aerobic
                "positive": "Great aerobic pace! 💪 Hold this effort",
                "slow": "Pick up pace a little bit 📈",
                "fast": "Slight reduction - stay comfortable 🎯"
            },
            3: {  # Tempo
                "positive": "Strong effort! 🔥 Stay focused and steady",
                "slow": "Increase intensity - push harder! ⚡",
                "fast": "Back off a bit - unsustainable 🛑"
            },
            4: {  # Threshold
                "positive": "Max effort! 💥 Give it your all!",
                "slow": "Push harder if you can 🚀",
                "fast": "Careful - near limit 🔴"
            },
            5: {  # Max
                "positive": "MAXIMUM EFFORT! 🔥🔥🔥",
                "slow": "PUSH HARD! 💪",
                "fast": "DANGER - REDUCE NOW! 🛑"
            }
        }
        
        if offset > 10:
            return cues[target_zone]["fast"]
        elif offset < -10:
            return cues[target_zone]["slow"]
        else:
            return cues[target_zone]["positive"]
    
    def _calculate_intensity_adjustment(self, current_hr: int, target_zone: int) -> str:
        """Recommend intensity adjustment"""
        zones = self._calculate_zones(target_zone)
        zone = zones[target_zone]
        target_hr = (zone["min"] + zone["max"]) // 2
        
        diff = current_hr - target_hr
        
        if diff > 20:
            return "Decrease by 5-10%"
        elif diff > 10:
            return "Decrease slightly"
        elif diff < -20:
            return "Increase by 5-10%"
        elif diff < -10:
            return "Increase slightly"
        else:
            return "Maintain"
    
    def _get_next_action(self, current_hr: int, target_zone: int, elapsed_minutes: float) -> str:
        """Suggest next action"""
        if elapsed_minutes < 5:
            return "Warm up more - ease into target zone"
        elif elapsed_minutes > 45 and current_hr > 150:
            return "Consider taking a 1-2 min recovery break"
        elif elapsed_minutes > 90:
            return "Cool down phase starting - gradually reduce intensity"
        else:
            return "Maintain current pace - you're doing great!"


class VoiceCoach:
    """Text-to-speech coaching messages for Apple Watch"""
    
    @staticmethod
    def generate_voice_message(coaching_cue: str) -> str:
        """Convert coaching cue to voice message"""
        # Remove emojis for voice
        message = coaching_cue
        for emoji in ["🔼", "↗️", "🔽", "↘️", "✅", "💨", "🚶", "💧", "🧠", 
                      "⚠️", "ℹ️", "🧘", "💪", "📈", "💚", "🎯", "🔥", "⚡", "🛑", 
                      "💥", "🚀", "🔴", "🔥🔥🔥"]:
            message = message.replace(emoji, "")
        
        return message.strip()
