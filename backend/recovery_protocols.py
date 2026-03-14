"""
recovery_protocols.py
---------------------
Pre-built recovery programs for different scenarios.

Protocols:
  - Acute Recovery (Emergency, <24 hours)
  - Short Recovery Block (2-3 days)
  - Week Recovery (7 days)
  - Overtraining Reversal (10-14 days)
  - Off-Season (4+ weeks)

Each protocol specifies:
  - Daily activity recommendations
  - Sleep targets
  - Nutrition focus
  - Stress management
  - Expected HRV + fatigue trajectory
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RecoveryProtocols:
    """Pre-built recovery strategies for different scenarios."""

    def __init__(self):
        self.protocols = self._build_protocols()

    def _build_protocols(self) -> Dict:
        """Build library of recovery protocols."""
        return {
            "acute_emergency": {
                "name": "Acute Emergency Recovery (24 hours)",
                "description": "When HRV crashes or fatigue spikes acutely",
                "trigger": "HRV drop >30% or fatigue >80%",
                "duration_days": 1,
                "daily_plan": [
                    {
                        "day": 1,
                        "activity": "Complete rest or 15-20 min easy walk",
                        "intensity_zones": "Zone 1 only (walk)",
                        "duration_minutes": 20,
                        "sleep_target_hours": 9,
                        "nutrition": "Normal meals + extra carbs + electrolyte drink",
                        "stress_management": "Meditation (10 min), no high-stress tasks",
                        "expected_hrv_change": "+5 to +10 ms (rebound)",
                        "expected_fatigue_change": "-10 to -15 points"
                    }
                ],
                "benefits": [
                    "Rapid parasympathetic activation",
                    "Neurological recovery",
                    "Glycogen restoration"
                ],
                "success_markers": [
                    "HRV returns to within 10% of baseline",
                    "Fatigue drops below 60%",
                    "Sleep quality improves"
                ]
            },

            "short_recovery_block": {
                "name": "Short Recovery Block (2-3 days)",
                "description": "Light activity to promote aerobic adaptation without stress",
                "trigger": "Fatigue 60-75% or HRV 80-90% of baseline",
                "duration_days": 3,
                "daily_plan": [
                    {
                        "day": 1,
                        "activity": "Easy Zone 1-2 aerobic (walking, easy cycling)",
                        "intensity_zones": "Zone 1-2",
                        "duration_minutes": 30,
                        "sleep_target_hours": 8.5,
                        "nutrition": "Balanced carbs + protein, hydration focus",
                        "stress_management": "Light stretching, progressive relaxation",
                        "expected_hrv_change": "+3 to +5 ms",
                        "expected_fatigue_change": "-5 points"
                    },
                    {
                        "day": 2,
                        "activity": "Activity rest or 20-min Zone 1 walk",
                        "intensity_zones": "Zone 1 or complete rest",
                        "duration_minutes": 20,
                        "sleep_target_hours": 9,
                        "nutrition": "Anti-inflammatory foods (berries, omega-3s, turmeric)",
                        "stress_management": "Yoga or tai chi (20 min)",
                        "expected_hrv_change": "+5 to +8 ms",
                        "expected_fatigue_change": "-8 points"
                    },
                    {
                        "day": 3,
                        "activity": "Easy Zone 2 aerobic (45 min easy run/cycle)",
                        "intensity_zones": "Zone 2",
                        "duration_minutes": 45,
                        "sleep_target_hours": 8.5,
                        "nutrition": "Normal training diet + extra antioxidants",
                        "stress_management": "Meditation + breathing work",
                        "expected_hrv_change": "+8 to +12 ms (cumulative)",
                        "expected_fatigue_change": "-15 to -20 points (cumulative)"
                    }
                ],
                "benefits": [
                    "Light aerobic stimulus maintains fitness",
                    "Parasympathetic activation without fatigue spike",
                    "Mental recovery",
                    "Movement quality improvement"
                ],
                "success_markers": [
                    "HRV improves 10-15 points over 3 days",
                    "Fatigue drops below 55%",
                    "Resting HR stable or declining",
                    "Sleep quality improving"
                ]
            },

            "week_recovery": {
                "name": "Full Week Recovery Block (7 days)",
                "description": "Structured week focusing on parasympathetic recovery and light movement",
                "trigger": "Chronic HRV suppression or fatigue >70% for 3+ days",
                "duration_days": 7,
                "daily_plan": [
                    {
                        "day": 1,
                        "activity": "Complete rest + gentle mobility",
                        "intensity_zones": "None (rest)",
                        "duration_minutes": 10,
                        "sleep_target_hours": 9,
                        "nutrition": "Light meals, high carbs, good hydration",
                        "stress_management": "Sleep + meditation priority"
                    },
                    {
                        "day": 2,
                        "activity": "20-min Zone 1 walk",
                        "intensity_zones": "Zone 1",
                        "duration_minutes": 20,
                        "sleep_target_hours": 9
                    },
                    {
                        "day": 3,
                        "activity": "30-min Zone 2 easy pace",
                        "intensity_zones": "Zone 2",
                        "duration_minutes": 30,
                        "sleep_target_hours": 8.5
                    },
                    {
                        "day": 4,
                        "activity": "Complete rest day",
                        "intensity_zones": "None",
                        "duration_minutes": 0,
                        "sleep_target_hours": 9
                    },
                    {
                        "day": 5,
                        "activity": "45-min Zone 2 steady aerobic",
                        "intensity_zones": "Zone 2",
                        "duration_minutes": 45,
                        "sleep_target_hours": 8.5
                    },
                    {
                        "day": 6,
                        "activity": "20-min Zone 1 walk + 15-min strength (light)",
                        "intensity_zones": "Zone 1 + very light resistance",
                        "duration_minutes": 35,
                        "sleep_target_hours": 8.5
                    },
                    {
                        "day": 7,
                        "activity": "Complete rest or 20-min yoga",
                        "intensity_zones": "None / Zone 1",
                        "duration_minutes": 20,
                        "sleep_target_hours": 9
                    }
                ],
                "benefits": [
                    "Comprehensive physiological recovery",
                    "HRV normalization",
                    "CNS reset",
                    "Injury prevention via active recovery",
                    "Mental reset"
                ],
                "expected_outcomes": {
                    "hrv_improvement": "+15 to +25 ms",
                    "resting_hr_reduction": "-3 to -5 bpm",
                    "fatigue_reduction": "-30 to -40 points",
                    "sleep_quality_change": "Significant improvement"
                }
            },

            "overtraining_reversal": {
                "name": "Overtraining Reversal Protocol (10-14 days)",
                "description": "Intensive recovery for diagnosed overtraining (OTS)",
                "trigger": "Multiple OTS symptoms: chronic HRV depression, mood changes, performance plateau",
                "duration_days": 14,
                "daily_plan": [
                    {
                        "day": "1-3",
                        "activity": "Complete rest or gentle walking only",
                        "intensity_zones": "Zone 1 max (20 min)",
                        "nutrition": "Focus: Sleep + stress reduction + nutrition",
                        "special": "No structured exercise",
                        "expected_hrv_change": "+5 to +10 ms/day"
                    },
                    {
                        "day": "4-7",
                        "activity": "Very easy Zone 1-2 (20-30 min walks/easy cycling)",
                        "intensity_zones": "Zone 1-2",
                        "duration_minutes": 25,
                        "sleep_target_hours": 9,
                        "special": "Build slowly - NO intensity",
                        "expected_hrv_change": "+3 to +5 ms/day"
                    },
                    {
                        "day": "8-10",
                        "activity": "Easy Zone 2 work (30-45 min)",
                        "intensity_zones": "Zone 2",
                        "duration_minutes": 40,
                        "sleep_target_hours": 8.5,
                        "special": "First heart-rate stimulus, but very conservative",
                        "expected_hrv_change": "+2 to +3 ms/day"
                    },
                    {
                        "day": "11-14",
                        "activity": "Aerobic + very light strength (no intensity)",
                        "intensity_zones": "Zone 2 + light bodyweight",
                        "duration_minutes": 45,
                        "sleep_target_hours": 8,
                        "special": "Gradual return, test readiness for Zone 3",
                        "expected_hrv_change": "+1 to +2 ms/day (approaching baseline)"
                    }
                ],
                "critical_rules": [
                    "❌ NO high-intensity work for 10-14 days minimum",
                    "❌ NO racing or competitive efforts",
                    "✅ Daily sleep 8-9 hours",
                    "✅ Manage life stress (work, relationships)",
                    "✅ Daily HRV monitoring to confirm recovery"
                ],
                "expected_outcomes": {
                    "hrv_improvement": "+30 to +50 ms (back toward baseline)",
                    "fatigue_reduction": "-50 to -70 points",
                    "mood_improvement": "Noticeable within 5-7 days",
                    "performance_readiness": "Ready for normal training by day 14-21"
                },
                "warning_signs_to_abort": [
                    "HRV continues declining",
                    "New injuries or pains emerging",
                    "Persistent mood/sleep issues",
                    "Elevated resting HR"
                ]
            },

            "off_season_extended": {
                "name": "Extended Off-Season Recovery (4+ weeks)",
                "description": "Long-term recovery with mixed-sport approach and psychological reset",
                "trigger": "End of competitive season or chronic accumulation of fatigue",
                "duration_days": 28,
                "phase_1_buildup": "Days 1-7: Complete rest from primary sport",
                "phase_2_crosstraining": "Days 8-21: Mix of easy aerobic + cross-training + strength",
                "phase_3_foundation": "Days 22-28: Base-building for next season",
                "daily_plan": [
                    {
                        "week": 1,
                        "focus": "Mental + physical deload",
                        "activity": "Walking only, no structured exercise",
                        "sleep": 9,
                        "nutrition": "Stress-free eating, no restrictions"
                    },
                    {
                        "week": 2,
                        "focus": "Variety + enjoyment",
                        "activities": ["Hiking", "Swimming", "Cycling"],
                        "intensity_zones": "Zone 1-2",
                        "sleep": 8.5,
                        "strength": "None"
                    },
                    {
                        "week": 3,
                        "focus": "Base building + light strength",
                        "activities": ["Easy runs", "Cycling", "Swimming"],
                        "intensity_zones": "Zone 2 primary, touch Zone 3",
                        "sleep": 8,
                        "strength": "2x light bodyweight + mobility"
                    },
                    {
                        "week": 4,
                        "focus": "Foundation + sport-specific prep",
                        "activities": ["Structured easy runs", "Tempo touch", "Strength"],
                        "intensity_zones": "Zone 2-3",
                        "sleep": 8,
                        "strength": "3x moderate bodyweight + weights"
                    }
                ],
                "expected_transformation": {
                    "fitness_loss": "Minimal (5-10%)",
                    "motivation_gain": "High - psychological refresh",
                    "injury_prevention": "Soft tissue repair",
                    "baseline_hrv": "Return to personal best or higher"
                }
            }
        }

    def recommend_protocol(self, current_state: dict) -> Dict:
        """
        Auto-recommend recovery protocol based on current state.
        """
        fatigue = current_state.get("fatigue_index", 30)
        hrv_ratio = current_state.get("hrv_avg", 50) / current_state.get("hrv_baseline", 50)
        recovery = current_state.get("recovery_index", 70)
        
        # Decision tree
        if hrv_ratio < 0.70 or fatigue > 80:
            return {
                "recommended": "overtraining_reversal",
                "urgency": "CRITICAL",
                "reason": "Signs of overtraining syndrome detected",
                "immediate_action": "Start 14-day recovery protocol immediately"
            }
        elif fatigue > 75 or recovery < 20:
            return {
                "recommended": "acute_emergency",
                "urgency": "HIGH",
                "reason": "Acute fatigue spike or recovery collapse",
                "immediate_action": "Take tomorrow off as complete rest day"
            }
        elif fatigue > 60 or hrv_ratio < 0.85:
            return {
                "recommended": "short_recovery_block",
                "urgency": "MEDIUM",
                "reason": "Elevated fatigue and HRV suppression",
                "immediate_action": "Start 3-day recovery block tomorrow"
            }
        elif hrv_ratio < 0.90:
            return {
                "recommended": "week_recovery",
                "urgency": "MEDIUM-LOW",
                "reason": "Chronic HRV suppression indicates accumulated fatigue",
                "immediate_action": "Plan 7-day recovery week in next 3-5 days"
            }
        else:
            return {
                "recommended": None,
                "urgency": "NONE",
                "reason": "Current state is healthy - no recovery protocol needed",
                "immediate_action": "Continue normal training with standard recovery"
            }

    def get_protocol(self, protocol_name: str) -> Optional[Dict]:
        """Retrieve specific protocol."""
        return self.protocols.get(protocol_name)

    def list_all_protocols(self) -> List[str]:
        """List all available protocols."""
        return [
            {
                "id": k,
                "name": v.get("name", k),
                "duration": v.get("duration_days", "Unknown"),
                "trigger": v.get("trigger", "Unknown")
            }
            for k, v in self.protocols.items()
        ]

    def protocol_timeline(self, protocol_name: str) -> pd.DataFrame:
        """Convert protocol to DataFrame for visualization."""
        protocol = self.protocols.get(protocol_name)
        if not protocol:
            return pd.DataFrame()
        
        daily_plan = protocol.get("daily_plan", [])
        
        # Flatten for display
        rows = []
        for day_plan in daily_plan:
            rows.append({
                "Day": day_plan.get("day", "?"),
                "Activity": day_plan.get("activity", "Rest"),
                "Duration (min)": day_plan.get("duration_minutes", 0),
                "Intensity": day_plan.get("intensity_zones", "Rest"),
                "Sleep (hrs)": day_plan.get("sleep_target_hours", 8),
                "Expected Recovery": day_plan.get("expected_hrv_change", "N/A")
            })
        
        return pd.DataFrame(rows)
