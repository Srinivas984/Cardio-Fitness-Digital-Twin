"""
cardiac_simulator.py
--------------------
Advanced Digital Twin Cardiac Simulator.

Handles multi-day, multi-week, and scenario-based simulations
with support for time-series visualization and animation.

Features:
  - Multi-day simulation with workout sequences
  - Recovery protocol simulation
  - 30-day projection with fatigue dynamics
  - What-if scenario analysis
  - Adaptation curves (HR reduction, fitness gain)
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CardiacSimulator:
    """Advanced simulator for multi-day cardiac digital twin scenarios."""

    def __init__(self, cardiac_twin):
        """
        Initialize simulator with a CardiacDigitalTwin instance.

        Args:
            cardiac_twin: CardiacDigitalTwin object
        """
        self.twin = cardiac_twin
        self.simulation_log = []

    def simulate_training_week(
        self,
        workout_schedule: List[Dict],
        sleep_hours_per_night: float = 8.0,
        nutrition_quality: float = 1.0,  # 0.5=poor, 1.0=adequate, 1.5=optimal
    ) -> pd.DataFrame:
        """
        Simulate a full training week with workouts and recovery.

        Args:
            workout_schedule: List of dicts with 'day', 'activity_profile', 'duration_min'
            sleep_hours_per_night: Sleep duration per night (affects recovery)
            nutrition_quality: Nutrition quality multiplier (affects recovery rate)

        Returns:
            DataFrame with minute-by-minute simulation
        """
        self.twin.reset()

        # Adjust recovery rate based on sleep and nutrition
        base_recovery_rate = self.twin.recovery_rate
        sleep_factor = sleep_hours_per_night / 8.0  # Normalized to 8 hours
        adjusted_recovery_rate = base_recovery_rate * sleep_factor * nutrition_quality
        original_recovery_rate = self.twin.recovery_rate
        self.twin.recovery_rate = adjusted_recovery_rate

        records = []
        day_counter = 1
        elapsed_minutes = 0

        for workout_config in workout_schedule:
            workday = workout_config.get("day", day_counter)
            activity_profile = workout_config.get("activity_profile", [0.0] * 45)
            duration = len(activity_profile)

            # Simulate the workout
            for minute, activity_level in enumerate(activity_profile):
                state = self.twin.step(activity_level, dt=1.0)
                records.append({
                    "day": workday,
                    "time_hour": minute / 60,
                    "elapsed_min": elapsed_minutes,
                    "heart_rate": state.heart_rate,
                    "fatigue": state.fatigue,
                    "recovery": state.recovery,
                    "activity": activity_level,
                    "hrv": state.hrv,
                    "parasympathetic": state.parasympathetic,
                    "cardiac_output": state.cardiac_output,
                    "training_load": state.training_load,
                    "phase": "workout",
                })
                elapsed_minutes += 1

            # Overnight recovery (sleep simulation)
            sleep_minutes = int(sleep_hours_per_night * 60)
            for minute in range(sleep_minutes):
                state = self.twin.step(0.0, dt=1.0)  # No activity during sleep
                records.append({
                    "day": workday,
                    "time_hour": (duration + minute) / 60,
                    "elapsed_min": elapsed_minutes,
                    "heart_rate": state.heart_rate,
                    "fatigue": state.fatigue,
                    "recovery": state.recovery,
                    "activity": 0.0,
                    "hrv": state.hrv,
                    "parasympathetic": state.parasympathetic,
                    "cardiac_output": state.cardiac_output,
                    "training_load": state.training_load,
                    "phase": "sleep",
                })
                elapsed_minutes += 1

            # Rest of the day
            remaining_minutes = int((24 - sleep_hours_per_night) * 60 - duration)
            for minute in range(remaining_minutes):
                state = self.twin.step(0.0, dt=1.0)
                records.append({
                    "day": workday,
                    "time_hour": (duration + sleep_minutes + minute) / 60,
                    "elapsed_min": elapsed_minutes,
                    "heart_rate": state.heart_rate,
                    "fatigue": state.fatigue,
                    "recovery": state.recovery,
                    "activity": 0.0,
                    "hrv": state.hrv,
                    "parasympathetic": state.parasympathetic,
                    "cardiac_output": state.cardiac_output,
                    "training_load": state.training_load,
                    "phase": "rest",
                })
                elapsed_minutes += 1

            day_counter += 1

        # Restore original recovery rate
        self.twin.recovery_rate = original_recovery_rate

        return pd.DataFrame(records)

    def simulate_30day_progression(
        self,
        weekly_structure: str = "standard",  # "standard", "build", "deload"
        starting_features: dict = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        Simulate 30-day training cycle with modulated training load.

        Args:
            weekly_structure: Pattern for training loads across weeks
            starting_features: Initial user features for calibration

        Returns:
            Dict with 'daily_summary', 'weekly_summary', 'projections'
        """
        if starting_features:
            self.twin.calibrate(starting_features)

        self.twin.reset()

        daily_records = []
        week_number = 1
        day_counter = 1

        # Define 4-week training structure
        if weekly_structure == "standard":
            weekly_loads = [1.0, 1.1, 1.0, 0.8]  # Standard periodization
        elif weekly_structure == "build":
            weekly_loads = [1.0, 1.1, 1.2, 0.9]  # Progressive build
        else:  # "deload"
            weekly_loads = [1.0, 0.9, 0.8, 0.7]  # Recovery focus

        for week in range(4):
            load_multiplier = weekly_loads[week]

            for day_in_week in range(7):
                # Generate varied workout structure
                if day_in_week in [0, 2, 4]:  # Mon, Wed, Fri
                    # Main workout day
                    intensity = 0.6 * load_multiplier
                    duration = 45
                else:  # Light days
                    intensity = 0.4 * load_multiplier
                    duration = 30 if day_in_week in [1, 3] else 20

                # Simulate day
                day_start_state = self.twin.get_current_state_dict()
                activity_profile = [intensity] * duration + [0.0] * (1440 - duration)  # Full day minutes

                for minute, activity in enumerate(activity_profile):
                    state = self.twin.step(activity, dt=1.0)
                    if minute % 15 == 0:  # Log every 15 minutes to reduce data
                        daily_records.append({
                            "day": day_counter,
                            "week": week + 1,
                            "day_of_week": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][day_in_week],
                            "time_hour": minute / 60,
                            "heart_rate": state.heart_rate,
                            "fatigue": state.fatigue,
                            "recovery": state.recovery,
                            "hrv": state.hrv,
                            "training_load": state.training_load,
                            "cardiac_output": state.cardiac_output,
                        })

                day_counter += 1

        daily_df = pd.DataFrame(daily_records)

        # Generate daily summary
        daily_summary = daily_df.groupby("day").agg({
            "heart_rate": ["mean", "min", "max"],
            "hrv": "mean",
            "fatigue": "mean",
            "recovery": "mean",
            "training_load": "max",
            "cardiac_output": "mean",
        }).round(2)

        # Generate weekly summary
        weekly_summary = daily_df.groupby("week").agg({
            "heart_rate": "mean",
            "hrv": "mean",
            "fatigue": "max",
            "recovery": "min",
            "training_load": "sum",
        }).round(2)

        # Generate projections
        projections = self._generate_projections(daily_df)

        return {
            "daily_detail": daily_df,
            "daily_summary": daily_summary,
            "weekly_summary": weekly_summary,
            "projections": projections,
        }

    def simulate_recovery_protocol(
        self,
        duration_days: int = 7,
        protocol_type: str = "standard",  # "standard", "aggressive", "gentle"
    ) -> Dict[str, pd.DataFrame]:
        """
        Simulate recovery from overtraining.

        Args:
            duration_days: How many days for recovery simulation
            protocol_type: Recovery intensity level

        Returns:
            Dict with recovery simulation and expected outcomes
        """
        self.twin.reset()

        # Define protocol intensity profiles
        if protocol_type == "aggressive":
            # Active recovery with some low-intensity work
            daily_intensity = [0.2, 0.1, 0.15, 0.1, 0.25, 0.1, 0.0]
        elif protocol_type == "gentle":
            # Minimal activity, maximum rest
            daily_intensity = [0.05] * duration_days
        else:  # "standard"
            daily_intensity = [0.1, 0.15, 0.1, 0.05, 0.1, 0.0, 0.1]

        records = []
        for day_idx in range(duration_days):
            intensity = daily_intensity[day_idx % len(daily_intensity)]

            # Simulate 45-min activity, then rest
            for minute in range(int(45 * 60)):
                state = self.twin.step(intensity / 100.0, dt=1.0)
                if minute % 30 == 0:
                    records.append({
                        "day": day_idx + 1,
                        "time_hour": minute / 60,
                        "heart_rate": state.heart_rate,
                        "hrv": state.hrv,
                        "fatigue": state.fatigue,
                        "recovery": state.recovery,
                        "parasympathetic": state.parasympathetic,
                    })

            # Rest of day
            for minute in range(int(45 * 60), int(24 * 60)):
                state = self.twin.step(0.0, dt=1.0)
                if minute % 120 == 0:
                    records.append({
                        "day": day_idx + 1,
                        "time_hour": minute / 60,
                        "heart_rate": state.heart_rate,
                        "hrv": state.hrv,
                        "fatigue": state.fatigue,
                        "recovery": state.recovery,
                        "parasympathetic": state.parasympathetic,
                    })

        df = pd.DataFrame(records)

        # Calculate metrics
        hrv_rebound = df.groupby("day")["hrv"].mean().iloc[-1] - df.groupby("day")["hrv"].mean().iloc[0]
        fatigue_reduction = df.groupby("day")["fatigue"].mean().iloc[0] - df.groupby("day")["fatigue"].mean().iloc[-1]

        summary = {
            "protocol_type": protocol_type,
            "expected_hrv_improvement": f"+{hrv_rebound:.1f} ms",
            "fatigue_reduction": f"-{fatigue_reduction*100:.0f} points",
            "recovery_days_needed": len(set(df["day"])),
        }

        return {
            "simulation": df,
            "summary": summary,
        }

    def what_if_scenario(
        self,
        current_state_dict: dict,
        scenario_name: str,
        intervention: str,
        duration_days: int = 7,
    ) -> pd.DataFrame:
        """
        Run what-if scenario for a potential intervention.

        Args:
            current_state_dict: Current state of cardiac twin
            scenario_name: Name of scenario
            intervention: Type of intervention ("more_sleep", "reduce_volume", "extra_day_off", etc.)
            duration_days: How long to simulate

        Returns:
            DataFrame with scenario projection
        """
        # Modify parameters based on intervention
        if intervention == "more_sleep":
            sleep_multiplier = 1.2
            recovery_multiplier = 1.3
        elif intervention == "reduce_volume":
            intensity_multiplier = 0.7
            recovery_multiplier = 1.0
        elif intervention == "extra_day_off":
            intensity_multiplier = 0.8
            recovery_multiplier = 1.2
        elif intervention == "nutrition_boost":
            recovery_multiplier = 1.4
            intensity_multiplier = 1.0
        else:
            recovery_multiplier = 1.0
            intensity_multiplier = 1.0

        records = []
        for day in range(duration_days):
            for minute in range(int(24 * 60)):
                # Standard weekly pattern
                hour = minute // 60
                if hour < 8 or hour > 22:
                    activity = 0.0  # Sleep
                elif (day % 7) in [0, 2, 4]:  # Workout days
                    activity = 0.6 * intensity_multiplier
                else:
                    activity = 0.2 * intensity_multiplier if hour in [7, 17] else 0.0

                state = self.twin.step(activity, dt=1.0)

                if minute % 60 == 0:
                    records.append({
                        "day": day + 1,
                        "time_hour": minute / 60,
                        "HR": state.heart_rate,
                        "HRV": state.hrv,
                        "Fatigue": state.fatigue,
                        "Recovery": state.recovery,
                    })

        return pd.DataFrame(records)

    def _generate_projections(self, daily_df: pd.DataFrame) -> dict:
        """
        Generate forward projections from observed trends.

        Returns:
            Dict with projected metrics
        """
        # Calculate recent trends (last week)
        recent = daily_df[daily_df["day"] > daily_df["day"].max() - 7]

        if len(recent) == 0:
            return {}

        hrv_trend = recent.groupby("day")["hrv"].mean()
        fatigue_trend = recent.groupby("day")["fatigue"].mean()
        recovery_trend = recent.groupby("day")["recovery"].mean()

        # Linear projection
        hrv_slope = (hrv_trend.iloc[-1] - hrv_trend.iloc[0]) / len(hrv_trend)
        fatigue_slope = (fatigue_trend.iloc[-1] - fatigue_trend.iloc[0]) / len(fatigue_trend)

        projections = {
            "hrv_30day_projection": hrv_trend.iloc[-1] + hrv_slope * 21,
            "fatigue_30day_projection": max(0, fatigue_trend.iloc[-1] + fatigue_slope * 21),
            "hrv_trajectory": "improving" if hrv_slope > 1 else "stable" if hrv_slope > -1 else "declining",
            "fit_gain_potential": "high" if recovery_trend.iloc[-1] > 0.8 else "medium",
        }

        return projections
