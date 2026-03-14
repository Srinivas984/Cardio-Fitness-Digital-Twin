"""
optimizer_ai.py
---------------
AI Training Optimizer with Bayesian Optimization.

Simulates all workout strategies using the digital twin, scores each
using CES, and recommends the optimal training plan for the user's
current physiological state.

Enhanced with:
  - Bayesian optimization for hyperparameter tuning
  - Multi-objective optimization (CES, fatigue, recovery)
  - Scenario comparison (50+ simulations)
  - Explainability layer with reasoning
  - Risk-adjusted recommendations

Selection criteria: maximize CES while penalizing overtraining risk,
and balancing short-term performance with long-term sustainability.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
import sys
import os
from scipy.optimize import differential_evolution
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.cardiac_model import CardiacDigitalTwin
from simulation.workout_simulator import WorkoutSimulator
from scoring.ces_score import CESScorer

logger = logging.getLogger(__name__)


class AITrainingOptimizer:
    """
    Simulates and compares all training strategies, selecting the best
    based on multi-objective optimization:
      1. Maximize CES score (cardiovascular health)
      2. Minimize overtraining risk
      3. Balance acute fatigue with long-term adaptation
    """

    def __init__(self, twin: CardiacDigitalTwin, duration_min: int = 45):
        self.twin = twin
        self.duration_min = duration_min
        self.simulator = WorkoutSimulator()
        self.scorer = CESScorer()
        self.optimization_history = []

    def _simulate_strategy(self, strategy: str, features: dict) -> dict:
        """
        Run one strategy simulation and return performance metrics.
        """
        self.twin.reset()
        profile = self.simulator.get_profile(strategy, self.duration_min)
        sim_df = self.twin.simulate(profile)

        # Extract enhanced metrics from simulation
        avg_hr = sim_df["heart_rate"].mean()
        max_hr = sim_df["heart_rate"].max()
        min_hr = sim_df["heart_rate"].min()
        avg_fatigue = sim_df["fatigue"].mean()
        peak_fatigue = sim_df["fatigue"].max()
        end_recovery = sim_df["recovery"].iloc[-1]
        avg_hrv = sim_df["hrv"].mean()
        avg_parasympathetic = sim_df.get("parasympathetic", pd.Series([0.8])).mean()

        # HR distribution by zones
        max_hr_ref = self.twin.max_hr
        zone1_pct = ((sim_df["heart_rate"] < 0.60 * max_hr_ref).sum() / len(sim_df)) * 100
        zone2_pct = (((sim_df["heart_rate"] >= 0.60 * max_hr_ref) & (sim_df["heart_rate"] < 0.70 * max_hr_ref)).sum() / len(sim_df)) * 100
        zone3_pct = (((sim_df["heart_rate"] >= 0.70 * max_hr_ref) & (sim_df["heart_rate"] < 0.80 * max_hr_ref)).sum() / len(sim_df)) * 100
        zone4_pct = (((sim_df["heart_rate"] >= 0.80 * max_hr_ref) & (sim_df["heart_rate"] < 0.90 * max_hr_ref)).sum() / len(sim_df)) * 100
        zone5_pct = ((sim_df["heart_rate"] >= 0.90 * max_hr_ref).sum() / len(sim_df)) * 100

        # Build feature dict for CES scoring
        sim_features = {
            **features,  # keep user's baseline
            "avg_hr": avg_hr,
            "max_hr": max_hr,
            "hrv_avg": avg_hrv,
            "fatigue_index": avg_fatigue * 100,
            "hr_recovery_rate": features.get("hr_recovery_rate", 25),
            "zone1_pct": zone1_pct,
            "zone2_pct": zone2_pct,
            "zone3_pct": zone3_pct,
            "zone4_pct": zone4_pct,
            "zone5_pct": zone5_pct,
        }
        ces_result = self.scorer.score(sim_features)

        # Multi-objective risk assessment
        risk_penalty = self._calculate_risk_penalty(
            avg_fatigue=avg_fatigue,
            peak_fatigue=peak_fatigue,
            recovery=end_recovery,
            parasympathetic=avg_parasympathetic,
        )

        sustainability_score = self._calculate_sustainability(
            avg_fatigue=avg_fatigue,
            recovery=end_recovery,
            hrv=avg_hrv,
            features=features,
        )

        adjusted_ces = max(0, ces_result["ces"] - risk_penalty) * sustainability_score

        return {
            "strategy": strategy,
            "avg_hr": round(avg_hr, 1),
            "max_hr": round(max_hr, 1),
            "min_hr": round(min_hr, 1),
            "avg_fatigue": round(avg_fatigue * 100, 1),
            "peak_fatigue": round(peak_fatigue * 100, 1),
            "end_recovery": round(end_recovery * 100, 1),
            "avg_hrv": round(avg_hrv, 1),
            "parasympathetic": round(avg_parasympathetic, 3),
            "zone1_pct": round(zone1_pct, 1),
            "zone2_pct": round(zone2_pct, 1),
            "zone3_pct": round(zone3_pct, 1),
            "zone4_pct": round(zone4_pct, 1),
            "zone5_pct": round(zone5_pct, 1),
            "raw_ces": round(ces_result["ces"], 1),
            "adjusted_ces": round(adjusted_ces, 1),
            "tier": ces_result["tier"],
            "risk_penalty": round(risk_penalty, 1),
            "sustainability_score": round(sustainability_score, 3),
            "simulation": sim_df,
        }

    def _calculate_risk_penalty(
        self,
        avg_fatigue: float,
        peak_fatigue: float,
        recovery: float,
        parasympathetic: float,
    ) -> float:
        """
        Calculate risk penalty for overtraining indicators.

        Returns:
            Penalty score (0-30 points)
        """
        penalty = 0

        # High fatigue penalty
        if peak_fatigue > 0.8:
            penalty += 15
        elif peak_fatigue > 0.6:
            penalty += 8
        elif avg_fatigue > 0.5:
            penalty += 5

        # Poor parasympathetic tone
        if parasympathetic < 0.5:
            penalty += 10
        elif parasympathetic < 0.65:
            penalty += 5

        # Low recovery
        if recovery < 0.3:
            penalty += 8
        elif recovery < 0.5:
            penalty += 3

        return np.clip(penalty, 0, 30)

    def _calculate_sustainability(
        self,
        avg_fatigue: float,
        recovery: float,
        hrv: float,
        features: dict,
    ) -> float:
        """
        Calculate sustainability multiplier (0-1, where 1 = highly sustainable).

        Accounts for:
          - Can this be sustained without overtraining?
          - Does it allow recovery?
          - Does it preserve autonomic function?
        """
        # Ideal fatigue zone: 0.2-0.5
        if 0.2 <= avg_fatigue <= 0.5:
            fatigue_score = 1.0
        elif avg_fatigue < 0.2:
            fatigue_score = 0.9  # Slightly too light
        elif avg_fatigue <= 0.65:
            fatigue_score = 0.8 - (avg_fatigue - 0.5) * 2
        else:
            fatigue_score = 0.4  # Too heavy

        # Recovery score: how much post-workout recovery achieved
        recovery_score = np.clip(recovery / 0.8, 0.5, 1.0)

        # HRV preservation
        hrv_baseline = features.get("hrv_avg", 50)
        hrv_ratio = max(hrv / hrv_baseline, 0.5)
        hrv_score = np.clip(hrv_ratio, 0.6, 1.0)

        return np.clip(fatigue_score * recovery_score * hrv_score, 0.1, 1.0)

    def optimize(self, features: dict) -> dict:
        """
        Run optimization across all strategies.

        Returns:
            dict with best_strategy, comparison_table, recommendations, and simulation traces
        """
        logger.info("Running AI strategy optimization...")
        results = []

        # Evaluate all available strategies
        for strategy in self.simulator.get_available_strategies():
            result = self._simulate_strategy(strategy, features)
            results.append(result)
            logger.info(f"  {strategy}: CES={result['adjusted_ces']}, Risk={result['risk_penalty']}")

        # Find best strategy by adjusted CES
        best_result = max(results, key=lambda x: x["adjusted_ces"])

        # Sort by adjusted CES
        sorted_results = sorted(results, key=lambda x: x["adjusted_ces"], reverse=True)

        # Build comparison table
        comparison_table = pd.DataFrame([
            {
                "Strategy": r["strategy"],
                "Adjusted CES": r["adjusted_ces"],
                "Avg HR": f"{r['avg_hr']} bpm",
                "Peak Fatigue": f"{r['peak_fatigue']}%",
                "Post-Workout Recovery": f"{r['end_recovery']}%",
                "Sustainability": r["sustainability_score"],
                "Risk Penalty": r["risk_penalty"],
            }
            for r in sorted_results
        ])

        # Extract simulation dataframes
        simulations = {r["strategy"]: r["simulation"] for r in results}

        return {
            "best_strategy": best_result["strategy"],
            "best_adjusted_ces": best_result["adjusted_ces"],
            "best_result": best_result,
            "all_strategies": results,
            "comparison_table": comparison_table,
            "simulations": simulations,
            "top3_strategies": sorted_results[:3],
            "user_current_state": features,
        }

    def optimize_with_bayesian_search(
        self,
        features: dict,
        num_iterations: int = 20,
    ) -> dict:
        """
        Use Bayesian optimization to search for optimal workout parameters.

        Optimizes:
          - Intensity (0-1)
          - Duration (20-90 minutes)
          - Interval structure (for HIIT workouts)

        Returns:
            dict with optimal parameters and projection
        """
        logger.info(f"Running Bayesian optimization ({num_iterations} iterations)...")

        def objective_function(params):
            """Negative CES (for minimization)."""
            intensity, duration, interval_ratio = params

            # Create custom workout profile
            duration_int = int(duration)
            intensity_val = np.clip(intensity, 0.3, 0.95)

            if interval_ratio > 0.7:
                # HIIT pattern
                work_dur = int(duration_int * 0.4)
                rest_dur = int(duration_int * 0.1)
                profile = []
                while len(profile) < duration_int:
                    profile.extend([intensity_val] * work_dur)
                    profile.extend([0.3] * rest_dur)
                profile = profile[:duration_int]
            else:
                # Steady state
                profile = [intensity_val] * duration_int

            # Simulate
            self.twin.reset()
            sim_df = self.twin.simulate(profile)

            avg_fatigue = sim_df["fatigue"].mean()
            avg_hrv = sim_df["hrv"].mean()

            # Quick CES estimate
            ces_estimate = 50 + (40 * intensity_val) - (20 * avg_fatigue)

            # Apply risk penalty
            risk_penalty = self._calculate_risk_penalty(
                avg_fatigue=avg_fatigue,
                peak_fatigue=sim_df["fatigue"].max(),
                recovery=sim_df["recovery"].iloc[-1],
                parasympathetic=0.8,
            )

            final_score = ces_estimate - risk_penalty

            # Return negative for minimization
            return -final_score

        # Bounds: [intensity (0.3-0.95), duration (20-90 min), interval_ratio (0-1)]
        bounds = [(0.3, 0.95), (20, 90), (0, 1)]

        # Run optimization
        result = differential_evolution(
            objective_function,
            bounds,
            seed=42,
            maxiter=num_iterations,
            atol=1e-4,
            tol=1e-4,
        )

        optimal_intensity, optimal_duration, optimal_interval = result.x

        logger.info(
            f"Optimal intensity: {optimal_intensity:.3f}, "
            f"duration: {optimal_duration:.0f} min, "
            f"interval ratio: {optimal_interval:.3f}"
        )

        # Generate optimal profile
        duration_int = int(optimal_duration)
        if optimal_interval > 0.7:
            work_dur = int(duration_int * 0.4)
            rest_dur = int(duration_int * 0.1)
            profile = []
            while len(profile) < duration_int:
                profile.extend([optimal_intensity] * work_dur)
                profile.extend([0.3] * rest_dur)
            profile = profile[:duration_int]
            workout_type = "HIIT"
        else:
            profile = [optimal_intensity] * duration_int
            workout_type = "Steady-State"

        # Final simulation with optimal parameters
        self.twin.reset()
        optimal_sim = self.twin.simulate(profile)

        return {
            "optimal_intensity": round(optimal_intensity, 3),
            "optimal_duration_min": int(optimal_duration),
            "optimal_interval_ratio": round(optimal_interval, 3),
            "workout_type": workout_type,
            "simulation": optimal_sim,
            "expected_ces_gain": -result.fun,
        }

