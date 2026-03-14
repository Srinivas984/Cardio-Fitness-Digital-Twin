"""
cardiac_model.py
----------------
Advanced Digital Twin Cardiovascular Model V2.

Simulates heart rate dynamics as a physiological system using improved
system dynamics with:

    HR_t = basal_HR + activity_effect - recovery_effect - fatigue_effect
    HRV_t = HRV_baseline * recovery_modulation - fatigue_suppression
    fatigue_t = fatigue_decay + training_impulse

State variables:
  - heart_rate:     current HR (bpm)
  - fatigue:        accumulated training fatigue (0–1)
  - recovery:       autonomic nervous system recovery (0–1)
  - activity_level: current activity intensity (0–1)
  - hrv:            heart rate variability (ms)
  - training_load:  cumulative training stress

Enhanced features:
  - HRV suppression during high fatigue
  - Parasympathetic recovery dynamics
  - Non-linear fatigue accumulation curves
  - HR drift (cardiac efficiency loss)
  - Personalized adaptation parameters

The model runs as discrete-time simulation. Each timestep = 1 minute.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
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
    parasympathetic: float = 0.8  # ANS parasympathetic tone (0-1)
    cardiac_output: float = 5.0   # Liters/minute
    training_load: float = 0.0    # Cumulative Training Stress Score


class CardiacDigitalTwin:
    """
    Physiological digital twin of the human cardiovascular system.

    Enhanced with:
      - HRV dynamics and parasympathetic tone
      - Cardiac output estimation
      - Training load (TRIMP) tracking
      - Improved fatigue-recovery modeling
      - HR drift and cardiac efficiency
      - Personalized adaptation curves

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
        vo2_max: float = 50.0,  # mL/kg/min
        training_responsiveness: float = 1.0,  # 0.5=low, 1.0=avg, 1.5=high
    ):
        self.resting_hr = resting_hr
        self.max_hr = max_hr
        self.hrv_baseline = hrv_baseline
        self.fatigue_sensitivity = fatigue_sensitivity
        self.recovery_rate = recovery_rate
        self.age = age
        self.vo2_max = vo2_max
        self.training_responsiveness = training_responsiveness

        # Autonomic nervous system parameters
        self.parasympathetic_tau = 12.0  # Hours for parasympathetic recovery
        
        # HR drift parameters (cardiac efficiency loss with fatigue)
        self.hr_drift_factor = 0.02
        
        # Initial state
        self.state = CardiacState(
            heart_rate=resting_hr,
            fatigue=0.1,
            recovery=0.9,
            activity_level=0.0,
            hrv=hrv_baseline,
            parasympathetic=0.9,
            cardiac_output=self._estimate_cardiac_output(resting_hr),
            training_load=0.0,
        )
        
        # History tracking for multi-day simulations
        self.history = []

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
        
        # Estimate VO2max from max HR if available
        if "max_hr" in features:
            # Rough estimation using standard formula
            age_factor = max(1 - (self.age - 25) * 0.005, 0.6)
            self.vo2_max = (features.get("max_hr", 190) - 60) * 0.8 * age_factor
        
        # Assess training responsiveness from recovery metrics
        recovery_idx = features.get("recovery_index", 60)
        if recovery_idx > 70:
            self.training_responsiveness = 1.3
        elif recovery_idx < 50:
            self.training_responsiveness = 0.8

        self.state = CardiacState(
            heart_rate=self.resting_hr,
            fatigue=fatigue_idx * 0.3,
            recovery=hrv_norm * 0.9,
            activity_level=0.0,
            hrv=self.hrv_baseline,
            parasympathetic=hrv_norm * 0.95,
            cardiac_output=self._estimate_cardiac_output(self.resting_hr),
            training_load=0.0,
        )
        
        self.history = []
        logger.info("Digital twin calibrated to user physiology.")

    def _estimate_cardiac_output(self, hr: float, stroke_volume: float = 80.0) -> float:
        """
        Estimate cardiac output (Q) = HR × SV
        Stroke volume varies with fitness and fatigue.
        """
        return (hr * stroke_volume) / 1000  # liters/minute

    def _calculate_training_impulse(self, hr_ratio: float, duration_min: float) -> float:
        """
        Calculate Training Impulse (TRIMP) score for this activity.
        TRIMP = duration × intensity_factor × heart_rate_reserve_ratio
        
        Args:
            hr_ratio: (HR - RHR) / (MaxHR - RHR)
            duration_min: Duration of activity in minutes
        
        Returns:
            TRIMP score
        """
        # Normalize for age using standard sports science formula
        age_factor = np.exp(0.006 * (self.age - 25))
        
        # Exponential scaling based on intensity
        intensity_scale = 0.64 * np.exp(1.92 * hr_ratio) if hr_ratio > 0 else 0
        
        trimp = duration_min * hr_ratio * intensity_scale * age_factor
        return trimp

    def step(self, activity_level: float, dt: float = 1.0) -> CardiacState:
        """
        Advance the simulation by one timestep with improved physiological model.

        Args:
            activity_level: Normalized exercise intensity (0=rest, 1=max effort)
            dt: Timestep in minutes (default 1 min)

        Returns:
            Updated CardiacState
        """
        s = self.state

        # --- 1. Heart Rate Response with HR Drift ---
        # Target HR based on intensity
        target_hr = self.resting_hr + activity_level * (self.max_hr - self.resting_hr)
        
        # HR lag: cardiovascular response delay (5-15 seconds typically)
        hr_lag = 0.15 * (1 + 0.3 * s.fatigue)  # Fatigued heart responds slower
        hr_change = hr_lag * (target_hr - s.heart_rate) * dt
        new_hr = s.heart_rate + hr_change
        
        # HR drift during sustained exercise: cardiac efficiency loss
        hr_drift = (s.fatigue * activity_level * self.hr_drift_factor * dt) if activity_level > 0.5 else 0
        new_hr = new_hr + hr_drift

        # --- 2. Fatigue Accumulation (Banister-like model) ---
        # Fatigue builds nonlinearly with intensity
        fatigue_impulse = activity_level ** 1.5 * self.fatigue_sensitivity * dt
        fatigue_decay = self.recovery_rate * (1 - activity_level) * (1 + s.recovery) * dt
        new_fatigue = np.clip(s.fatigue + fatigue_impulse - fatigue_decay, 0, 1.0)

        # --- 3. Parasympathetic Recovery (vagal tone) ---
        # Rest improves parasympathetic tone, exercise suppresses it
        para_gain = self.recovery_rate * (1 - activity_level) * 0.5 * dt
        para_loss = activity_level * 0.05 * dt
        new_parasympathetic = np.clip(s.parasympathetic + para_gain - para_loss, 0.3, 1.0)

        # --- 4. Recovery Index (depends on parasympathetic + inverse fatigue) ---
        recovery_gain = self.recovery_rate * (1 - activity_level) * new_parasympathetic * 0.3 * dt
        recovery_loss = 0.02 * activity_level * dt
        new_recovery = np.clip(s.recovery + recovery_gain - recovery_loss, 0, 1.0)

        # --- 5. Fatigue Effect on Resting HR (elevated RHR indicator) ---
        fatigue_hr_effect = new_fatigue * 10 * (1 - new_recovery)  # up to +10 bpm
        new_hr = np.clip(new_hr + fatigue_hr_effect, self.resting_hr - 5, self.max_hr)

        # --- 6. HRV Dynamics (suppressed by fatigue and high heart rate) ---
        # HRV baseline modulated by activity and fatigue
        hrv_activity_effect = 0.4 * activity_level  # Activity reduces HRV
        hrv_fatigue_effect = 0.5 * new_fatigue     # Fatigue reduces HRV
        hrv_recovery_effect = 0.2 * new_parasympathetic  # Recovery increases HRV
        
        hrv_multiplier = 1.0 - hrv_activity_effect - hrv_fatigue_effect + hrv_recovery_effect
        hrv_noise = np.random.normal(0, 2)  # Physiological variability
        new_hrv = np.clip(
            self.hrv_baseline * max(hrv_multiplier, 0.1) + hrv_noise,
            5, self.hrv_baseline * 1.5
        )

        # --- 7. Cardiac Output (depends on HR and stroke volume) ---
        # Stroke volume reduced by fatigue
        sv_reduction = 1.0 - (0.2 * new_fatigue)
        new_cardiac_output = self._estimate_cardiac_output(new_hr, stroke_volume=80 * sv_reduction)

        # --- 8. Training Load (cumulative TRIMP) ---
        hr_reserve_ratio = (new_hr - self.resting_hr) / max(self.max_hr - self.resting_hr, 1)
        trimp_increment = self._calculate_training_impulse(hr_reserve_ratio, dt)
        new_training_load = s.training_load + trimp_increment

        self.state = CardiacState(
            time=s.time + dt,
            heart_rate=round(new_hr, 1),
            fatigue=round(new_fatigue, 4),
            recovery=round(new_recovery, 4),
            activity_level=activity_level,
            hrv=round(new_hrv, 1),
            parasympathetic=round(new_parasympathetic, 4),
            cardiac_output=round(new_cardiac_output, 2),
            training_load=round(new_training_load, 2),
        )
        return self.state

    def simulate(self, activity_profile: List[float], dt: float = 1.0) -> pd.DataFrame:
        """
        Run a full simulation over an activity profile.

        Args:
            activity_profile: List of activity levels [0,1] for each timestep
            dt: Timestep duration in minutes

        Returns:
            DataFrame with one row per timestep, includes all state variables
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
                "parasympathetic": state.parasympathetic,
                "cardiac_output": state.cardiac_output,
                "training_load": state.training_load,
            })
        
        df = pd.DataFrame(records)
        self.history.append(df.copy())
        return df

    def simulate_multiday(
        self, 
        daily_profiles: List[List[float]], 
        recovery_nights: int = 10,
        dt: float = 1.0
    ) -> pd.DataFrame:
        """
        Simulate multiple days with overnight recovery periods.

        Args:
            daily_profiles: List of activity profiles, one per day
            recovery_nights: Hours of rest each night
            dt: Timestep in minutes

        Returns:
            DataFrame with all days concatenated, with day markers
        """
        records = []
        day_counter = 1
        
        for profile in daily_profiles:
            # Simulate the day
            sim_df = self.simulate(profile, dt)
            sim_df['day'] = day_counter
            sim_df['time_hour'] = sim_df['time_min'] / 60
            records.append(sim_df)
            
            # Overnight recovery (no activity)
            overnight_steps = int(recovery_nights * 60 / dt)
            recovery_profile = [0.0] * overnight_steps
            
            # Simulate recovery night
            recovery_df = pd.DataFrame()
            for step in recovery_profile:
                state = self.step(step, dt)
                recovery_df = pd.concat([recovery_df, pd.DataFrame([{
                    "time_min": state.time,
                    "heart_rate": state.heart_rate,
                    "fatigue": state.fatigue,
                    "recovery": state.recovery,
                    "activity_level": state.activity_level,
                    "hrv": state.hrv,
                    "parasympathetic": state.parasympathetic,
                    "cardiac_output": state.cardiac_output,
                    "training_load": state.training_load,
                }])], ignore_index=True)
            
            recovery_df['day'] = day_counter
            recovery_df['time_hour'] = recovery_df['time_min'] / 60
            day_counter += 1
        
        return pd.concat(records, ignore_index=True)

    def reset(self):
        """Reset to baseline state."""
        self.state = CardiacState(
            heart_rate=self.resting_hr,
            fatigue=0.1,
            recovery=0.9,
            hrv=self.hrv_baseline,
            parasympathetic=0.9,
            cardiac_output=self._estimate_cardiac_output(self.resting_hr),
            training_load=0.0,
        )
        self.history = []

    def get_current_state_dict(self) -> dict:
        """Get current state as dictionary for easy access."""
        s = self.state
        return {
            "heart_rate": s.heart_rate,
            "fatigue": s.fatigue,
            "recovery": s.recovery,
            "activity_level": s.activity_level,
            "hrv": s.hrv,
            "parasympathetic": s.parasympathetic,
            "cardiac_output": s.cardiac_output,
            "training_load": s.training_load,
            "time": s.time,
        }
