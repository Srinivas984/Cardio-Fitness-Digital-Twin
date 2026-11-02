"""
cardiac_model.py
----------------
Digital Twin Cardiovascular Model.

Simulates heart rate dynamics as a physiological system using:

    HR_next = HR + activity_effect - recovery_effect - fatigue_effect

State variables:
  - heart_rate:     current HR (bpm)
  - fatigue:        accumulated fatigue (0–1)
  - recovery:       current recovery level (0–1)
  - activity_level: current activity intensity (0–1)

The model runs as a discrete-time simulation. Each timestep = 1 minute.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class CardiacState:
    """Snapshot of the cardiovascular system at one timestep."""
    time: float = 0.0
    heart_rate: float = 65.0
    fatigue: float = 0.1
    recovery: float = 0.8
    activity_level: float = 0.0
    hrv: float = 50.0


class CardiacDigitalTwin:
    """
    Physiological digital twin of the human cardiovascular system.

    Parameters are calibrated to match typical adult physiology
    and can be adjusted per-user based on their wearable data.
    """

    def __init__(
        self,
        resting_hr: float = 65.0,
        max_hr: float = 190.0,
        hrv_baseline: float = 50.0,
        fatigue_sensitivity: float = 0.08,
        recovery_rate: float = 0.05,
        age: int = 30,
    ):
        self.resting_hr = resting_hr
        self.max_hr = max_hr
        self.hrv_baseline = hrv_baseline
        self.fatigue_sensitivity = fatigue_sensitivity
        self.recovery_rate = recovery_rate
        self.age = age

        # Initial state
        self.state = CardiacState(
            heart_rate=resting_hr,
            fatigue=0.1,
            recovery=0.9,
            activity_level=0.0,
            hrv=hrv_baseline,
        )

    def calibrate(self, features: dict):
        """
        Calibrate the twin using real wearable features.
        Adjusts baseline parameters to match the user's physiology.
        """
        self.resting_hr = features.get("resting_hr", self.resting_hr)
        self.max_hr = features.get("max_hr", self.max_hr)
        self.hrv_baseline = features.get("hrv_avg", self.hrv_baseline)

        # Calibrate fatigue sensitivity based on fatigue index
        fatigue_idx = features.get("fatigue_index", 30) / 100
        self.fatigue_sensitivity = 0.05 + fatigue_idx * 0.08

        # Calibrate recovery rate based on HRV
        hrv_norm = min(features.get("hrv_avg", 50) / 100, 1.0)
        self.recovery_rate = 0.03 + hrv_norm * 0.05

        self.state = CardiacState(
            heart_rate=self.resting_hr,
            fatigue=fatigue_idx * 0.3,
            recovery=hrv_norm * 0.9,
            activity_level=0.0,
            hrv=self.hrv_baseline,
        )
        logger.info("Digital twin calibrated to user physiology.")

    def step(self, activity_level: float, dt: float = 1.0) -> CardiacState:
        """
        Advance the simulation by one timestep.

        Args:
            activity_level: Normalized exercise intensity (0=rest, 1=max effort)
            dt: Timestep in minutes (default 1 min)

        Returns:
            Updated CardiacState
        """
        s = self.state

        # --- Activity effect: HR rises with exercise ---
        target_hr = self.resting_hr + activity_level * (self.max_hr - self.resting_hr)
        hr_lag = 0.15  # How quickly HR approaches target (physiological lag)
        new_hr = s.heart_rate + hr_lag * (target_hr - s.heart_rate) * dt

        # --- Fatigue accumulation: builds with high-intensity work ---
        fatigue_gain = self.fatigue_sensitivity * activity_level * dt
        fatigue_loss = self.recovery_rate * (1 - activity_level) * dt
        new_fatigue = np.clip(s.fatigue + fatigue_gain - fatigue_loss, 0, 1)

        # --- Recovery: improves at rest, hindered by fatigue ---
        recovery_gain = self.recovery_rate * (1 - activity_level) * (1 - s.fatigue) * dt
        recovery_loss = 0.02 * activity_level * dt
        new_recovery = np.clip(s.recovery + recovery_gain - recovery_loss, 0, 1)

        # --- Fatigue effect on HR: fatigued heart beats faster at rest ---
        fatigue_hr_effect = new_fatigue * 10  # up to +10 bpm when fully fatigued
        new_hr = np.clip(new_hr + fatigue_hr_effect, self.resting_hr - 5, self.max_hr)

        # --- HRV: inversely related to HR and fatigue ---
        hrv_noise = np.random.normal(0, 2)  # physiological variability
        new_hrv = np.clip(
            self.hrv_baseline * (1 - 0.4 * activity_level) * (1 - 0.3 * new_fatigue) + hrv_noise,
            5, 200
        )

        self.state = CardiacState(
            time=s.time + dt,
            heart_rate=round(new_hr, 1),
            fatigue=round(new_fatigue, 4),
            recovery=round(new_recovery, 4),
            activity_level=activity_level,
            hrv=round(new_hrv, 1),
        )
        return self.state

    def simulate(self, activity_profile: List[float], dt: float = 1.0) -> pd.DataFrame:
        """
        Run a full simulation over an activity profile.

        Args:
            activity_profile: List of activity levels [0,1] for each timestep
            dt: Timestep duration in minutes

        Returns:
            DataFrame with one row per timestep
        """
        records = []
        for activity in activity_profile:
            state = self.step(activity, dt)
            records.append({
                "time_min": state.time,
                "heart_rate": state.heart_rate,
                "fatigue": state.fatigue,
                "recovery": state.recovery,
                "activity_level": state.activity_level,
                "hrv": state.hrv,
            })
        return pd.DataFrame(records)

    def reset(self):
        """Reset to baseline state."""
        self.state = CardiacState(
            heart_rate=self.resting_hr,
            fatigue=0.1,
            recovery=0.9,
            hrv=self.hrv_baseline,
        )
