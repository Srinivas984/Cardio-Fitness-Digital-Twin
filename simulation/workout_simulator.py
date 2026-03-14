"""
workout_simulator.py
--------------------
Generates standardized activity profiles for different workout strategies.

Strategies:
  - HIIT: High-Intensity Interval Training
  - Steady Cardio: Zone 2 aerobic training
  - Recovery Day: Light movement + rest

Each strategy returns a normalized activity profile (0–1 per minute).
"""

import numpy as np
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class WorkoutSimulator:
    """Generates normalized activity profiles for training strategy simulation."""

    STRATEGIES = [
        "🚶 Easy Walk (Recovery)",
        "🏃 Light Jog (Easy Run)",
        "🚴 Moderate Ride (Steady)",
        "💪 Hard Run (Fast)",
        "⚡ Sprint Intervals (Very Hard)",
        "💪 Upper Body Push (Chest/Shoulders)",
        "🔥 Upper Body Pull (Back/Biceps)",
        "🦵 Lower Body Strength (Legs/Glutes)",
        "🏋️ Full Body Strength",
        "⚙️ CrossFit/Mixed Training",
    ]

    @staticmethod
    def easy_walk(duration_min: int = 30) -> List[float]:
        """
        Easy Walk / Recovery Walk (30-50% max HR):
        - Very light, can talk freely
        - Helps blood flow recovery
        - No fatigue buildup
        """
        noise = np.random.normal(0, 0.01, duration_min)
        profile = np.clip(0.35 + noise, 0.25, 0.45)
        return list(profile)

    @staticmethod
    def light_jog(duration_min: int = 35) -> List[float]:
        """
        Light Jog / Easy Run (55-70% max HR):
        - Can hold conversation
        - Burns fat, builds base
        - Minimal fatigue
        """
        profile = []
        # Warm-up (first 5 min)
        for i in range(5):
            profile.append(0.35 + (0.60 - 0.35) * (i / 5))
        # Sustained easy pace
        sustained_duration = duration_min - 10
        noise = np.random.normal(0, 0.015, sustained_duration)
        sustained = np.clip(0.60 + noise, 0.55, 0.70)
        profile += list(sustained)
        # Cool-down (last 5 min)
        for i in range(5):
            profile.append(max(0.30, 0.60 - 0.06 * i))
        return profile[:duration_min]

    @staticmethod
    def moderate_ride(duration_min: int = 45) -> List[float]:
        """
        Moderate Ride / Steady Cardio (65-75% max HR):
        - Breathing harder, can still talk in short sentences
        - Good training stimulus
        - Moderate fatigue
        """
        profile = []
        # Warm-up (first 5 min)
        for i in range(5):
            profile.append(0.40 + (0.68 - 0.40) * (i / 5))
        # Sustained moderate pace
        sustained_duration = duration_min - 10
        noise = np.random.normal(0, 0.018, sustained_duration)
        sustained = np.clip(0.68 + noise, 0.60, 0.78)
        profile += list(sustained)
        # Cool-down (last 5 min)
        for i in range(5):
            profile.append(max(0.30, 0.68 - 0.08 * i))
        return profile[:duration_min]

    @staticmethod
    def hard_run(duration_min: int = 40) -> List[float]:
        """
        Hard Run / Fast Steady (75-85% max HR):
        - Heavy breathing, difficult to hold conversation
        - Strong training stimulus, builds fitness
        - High fatigue accumulation
        """
        profile = []
        # Warm-up (6 min)
        for i in range(6):
            profile.append(0.40 + (0.75 - 0.40) * (i / 6))
        # Hard pace main set
        main_duration = duration_min - 11
        noise = np.random.normal(0, 0.015, main_duration)
        main = np.clip(0.80 + noise, 0.72, 0.88)
        profile += list(main)
        # Cool-down (5 min)
        for i in range(5):
            profile.append(max(0.30, 0.80 - 0.10 * i))
        return profile[:duration_min]

    @staticmethod
    def sprint_intervals(duration_min: int = 40) -> List[float]:
        """
        Sprint Intervals / High Intensity (85-95% max HR):
        - Maximum effort intervals with recovery
        - Very high fatigue, builds peak fitness
        - Requires good recovery (not daily!)
        """
        profile = []
        # Warm-up (5 min) - important!
        for i in range(5):
            profile.append(0.35 + (0.50 - 0.35) * (i / 5))
        
        # Main phase: alternating 2min hard / 1min easy × 5-6 rounds
        rounds = (duration_min - 10) // 3  # Each round ~3 min
        for _ in range(rounds):
            # 2 min hard efforts
            hard_duration = 2
            hard_intensity = np.random.uniform(0.88, 0.96, hard_duration)
            profile += list(hard_intensity)
            # 1 min recovery
            recovery = np.random.uniform(0.45, 0.55, 1)
            profile += list(recovery)
        
        # Cool-down (5 min)
        for i in range(5):
            profile.append(max(0.25, 0.50 - 0.05 * i))
        
        return profile[:duration_min]

    @staticmethod
    def upper_push(duration_min: int = 50) -> List[float]:
        """
        Upper Body Push (Chest/Shoulders/Triceps):
        - Bench press, incline press, shoulder press, dips, cable flyes
        - Mix of warm-up sets and heavy working sets
        - More recovery between sets than cardio
        """
        profile = []
        # Warm-up (5 min) - easy, get blood flowing
        for i in range(5):
            profile.append(0.30 + 0.04 * i)
        
        # Working sets: ~40 min of mixed intensity
        # Heavy weight, lower reps = intense but rest between
        for set_num in range(6):
            # Work set (4-5 min) - harder effort
            work_duration = 5
            work_intensity = np.random.uniform(0.68, 0.78, work_duration)
            profile += list(work_intensity)
            
            # Rest between sets (2-3 min) - lower heart rate
            rest_duration = 2
            rest_intensity = np.random.uniform(0.35, 0.45, rest_duration)
            profile += list(rest_intensity)
        
        # Cool-down (5 min)
        for i in range(5):
            profile.append(max(0.25, 0.45 - 0.04 * i))
        
        return profile[:duration_min]

    @staticmethod
    def upper_pull(duration_min: int = 50) -> List[float]:
        """
        Upper Body Pull (Back/Biceps):
        - Pull-ups, rows, lat pulldowns, face pulls, curls
        - Compound movements with heavy weight
        - Similar pattern to push - work set then rest
        """
        profile = []
        # Warm-up (5 min)
        for i in range(5):
            profile.append(0.30 + 0.04 * i)
        
        # Working sets: 40 min of mixed intensity
        for set_num in range(6):
            # Work set (4-5 min) - intense compound movement
            work_duration = 5
            work_intensity = np.random.uniform(0.70, 0.80, work_duration)
            profile += list(work_intensity)
            
            # Rest between sets (2-3 min)
            rest_duration = 2
            rest_intensity = np.random.uniform(0.35, 0.45, rest_duration)
            profile += list(rest_intensity)
        
        # Cool-down (5 min)
        for i in range(5):
            profile.append(max(0.25, 0.45 - 0.04 * i))
        
        return profile[:duration_min]

    @staticmethod
    def lower_legs(duration_min: int = 55) -> List[float]:
        """
        Lower Body Strength (Legs/Glutes):
        - Squats, deadlifts, lunges, leg press
        - Heavy compound movements = very high heart rate
        - Longest recovery between sets
        """
        profile = []
        # Extended warm-up (7 min) - legs need more prep
        for i in range(7):
            profile.append(0.30 + 0.035 * i)
        
        # Working sets: 43 min - heaviest lifts
        for set_num in range(5):
            # Work set (5-6 min) - very intense (squats/deadlifts)
            work_duration = 6
            work_intensity = np.random.uniform(0.75, 0.88, work_duration)
            profile += list(work_intensity)
            
            # Longer rest between leg sets (3-4 min) - demanding recovery
            rest_duration = 3
            rest_intensity = np.random.uniform(0.35, 0.45, rest_duration)
            profile += list(rest_intensity)
        
        # Cool-down (5 min) - walk it off
        for i in range(5):
            profile.append(max(0.25, 0.45 - 0.04 * i))
        
        return profile[:duration_min]

    @staticmethod
    def full_body_strength(duration_min: int = 60) -> List[float]:
        """
        Full Body Strength:
        - Compound movements hitting all muscle groups
        - Squat/deadlift variation + push + pull
        - High intensity, medium-high heart rate maintained
        """
        profile = []
        # Warm-up (7 min)
        for i in range(7):
            profile.append(0.30 + 0.035 * i)
        
        # Block 1: Lower (deadlifts/squats) - 12 min
        for _ in range(2):
            profile += list(np.random.uniform(0.75, 0.85, 5))  # work
            profile += list(np.random.uniform(0.35, 0.45, 1))  # rest
        
        # Block 2: Push (bench/press) - 10 min
        for _ in range(2):
            profile += list(np.random.uniform(0.70, 0.80, 5))  # work
            profile += list(np.random.uniform(0.35, 0.45, 1))  # rest
        
        # Block 3: Pull (rows/pullups) - 10 min
        for _ in range(2):
            profile += list(np.random.uniform(0.70, 0.80, 5))  # work
            profile += list(np.random.uniform(0.35, 0.45, 1))  # rest
        
        # Cool-down (7 min)
        for i in range(7):
            profile.append(max(0.25, 0.45 - 0.03 * i))
        
        return profile[:duration_min]

    @staticmethod
    def crossfit_mixed(duration_min: int = 45) -> List[float]:
        """
        CrossFit / Mixed Training:
        - Combination of strength + cardio
        - High intensity interval style with functional movements
        - AMRAPs, EMOMs, or strength + cardio circuits
        """
        profile = []
        # Warm-up (5 min)
        for i in range(5):
            profile.append(0.35 + 0.04 * i)
        
        # Main phase: 35 min of mixed intensity circuits
        # Circuit style: hard rounds alternating with active recovery
        num_rounds = 5  # 5 rounds of 5-min circuits
        for round_num in range(num_rounds):
            # AMRAP / circuit round (4 min hard)
            circuit_duration = 4
            circuit = np.random.uniform(0.80, 0.92, circuit_duration)
            profile += list(circuit)
            
            # Active recovery (1 min) - walk/catch breath
            recovery = np.random.uniform(0.40, 0.50, 1)
            profile += list(recovery)
        
        # Cool-down (5 min)
        for i in range(5):
            profile.append(max(0.25, 0.50 - 0.05 * i))
        
        return profile[:duration_min]

    @staticmethod
    def get_profile(strategy: str, duration_min: int = 45) -> List[float]:
        """
        Retrieve the activity profile for a named strategy.

        Args:
            strategy: One of STRATEGIES
            duration_min: Desired duration in minutes

        Returns:
            List of normalized activity levels (0–1)
        """
        dispatch = {
            "🚶 Easy Walk (Recovery)": WorkoutSimulator.easy_walk,
            "🏃 Light Jog (Easy Run)": WorkoutSimulator.light_jog,
            "🚴 Moderate Ride (Steady)": WorkoutSimulator.moderate_ride,
            "💪 Hard Run (Fast)": WorkoutSimulator.hard_run,
            "⚡ Sprint Intervals (Very Hard)": WorkoutSimulator.sprint_intervals,
            "💪 Upper Body Push (Chest/Shoulders)": WorkoutSimulator.upper_push,
            "🔥 Upper Body Pull (Back/Biceps)": WorkoutSimulator.upper_pull,
            "🦵 Lower Body Strength (Legs/Glutes)": WorkoutSimulator.lower_legs,
            "🏋️ Full Body Strength": WorkoutSimulator.full_body_strength,
            "⚙️ CrossFit/Mixed Training": WorkoutSimulator.crossfit_mixed,
        }
        if strategy not in dispatch:
            raise ValueError(f"Unknown strategy: {strategy}. Choose from: {WorkoutSimulator.STRATEGIES}")
        return dispatch[strategy](duration_min)

    @staticmethod
    def all_profiles(duration_min: int = 45) -> Dict[str, List[float]]:
        """Return activity profiles for all strategies."""
        return {s: WorkoutSimulator.get_profile(s, duration_min) for s in WorkoutSimulator.STRATEGIES}

    @staticmethod
    def get_available_strategies() -> List[str]:
        """Return list of available training strategies."""
        return WorkoutSimulator.STRATEGIES
