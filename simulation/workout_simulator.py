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

    STRATEGIES = ["HIIT", "Steady Cardio", "Recovery Day", "Tempo Run", "Strength Circuit"]

    @staticmethod
    def hiit(duration_min: int = 45) -> List[float]:
        """
        High-Intensity Interval Training:
          - 5 min warm-up (40% effort)
          - Alternating: 30s hard (90%) / 90s easy (35%) × 15 rounds
          - 5 min cool-down (30%)
        """
        profile = []

        # Warm-up
        profile += [0.4 + 0.01 * i for i in range(5)]

        # Intervals (30s hard = 0.5 min, 90s easy = 1.5 min → round to 1-min steps)
        rounds = (duration_min - 10) // 2  # ~2 min per interval pair
        for _ in range(rounds):
            profile.append(0.92)   # 1 min hard
            profile.append(0.35)   # 1 min easy

        # Cool-down
        profile += [max(0.3, 0.5 - 0.04 * i) for i in range(5)]

        return profile[:duration_min]

    @staticmethod
    def steady_cardio(duration_min: int = 45, intensity: float = 0.65) -> List[float]:
        """
        Steady Zone 2 Cardio:
          - 5 min ramp up
          - Sustained at target intensity ± slight variation
          - 5 min cool-down
        """
        profile = []

        # Ramp up
        for i in range(5):
            profile.append(0.3 + (intensity - 0.3) * (i / 5))

        # Sustained phase with mild variability
        sustained_duration = duration_min - 10
        noise = np.random.normal(0, 0.02, sustained_duration)
        sustained = np.clip(intensity + noise, 0.55, 0.80)
        profile += list(sustained)

        # Cool-down
        for i in range(5):
            profile.append(max(0.2, intensity - 0.07 * i))

        return profile[:duration_min]

    @staticmethod
    def recovery_day(duration_min: int = 30) -> List[float]:
        """
        Active Recovery:
          - Light walking / gentle movement
          - Target < 50% max HR
        """
        noise = np.random.normal(0, 0.02, duration_min)
        profile = np.clip(0.3 + noise, 0.2, 0.42)
        return list(profile)

    @staticmethod
    def tempo_run(duration_min: int = 40) -> List[float]:
        """
        Threshold / Tempo Run:
          - 8 min warm-up
          - 25 min at lactate threshold (~75–80%)
          - 7 min cool-down
        """
        profile = []
        # Warm-up
        for i in range(8):
            profile.append(0.40 + 0.04 * i)
        # Tempo pace
        noise = np.random.normal(0, 0.015, 25)
        tempo = np.clip(0.78 + noise, 0.72, 0.85)
        profile += list(tempo)
        # Cool-down
        for i in range(7):
            profile.append(max(0.25, 0.78 - 0.07 * i))
        return profile[:duration_min]

    @staticmethod
    def strength_circuit(duration_min: int = 50) -> List[float]:
        """
        Strength & Circuit Training:
          - Alternating moderate effort bursts with short rest
        """
        profile = []
        for i in range(duration_min):
            cycle = i % 4  # 4-minute cycle
            if cycle < 2:  # 2 min work
                profile.append(np.random.uniform(0.65, 0.80))
            else:           # 2 min rest
                profile.append(np.random.uniform(0.20, 0.35))
        return profile

    def get_profile(self, strategy: str, duration_min: int = 45) -> List[float]:
        """
        Retrieve the activity profile for a named strategy.

        Args:
            strategy: One of STRATEGIES
            duration_min: Desired duration in minutes

        Returns:
            List of normalized activity levels (0–1)
        """
        dispatch = {
            "HIIT": self.hiit,
            "Steady Cardio": self.steady_cardio,
            "Recovery Day": self.recovery_day,
            "Tempo Run": self.tempo_run,
            "Strength Circuit": self.strength_circuit,
        }
        if strategy not in dispatch:
            raise ValueError(f"Unknown strategy: {strategy}. Choose from: {self.STRATEGIES}")
        return dispatch[strategy](duration_min)

    def all_profiles(self, duration_min: int = 45) -> Dict[str, List[float]]:
        """Return activity profiles for all strategies."""
        return {s: self.get_profile(s, duration_min) for s in self.STRATEGIES}
