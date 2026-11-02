"""
optimizer_ai.py
---------------
AI Training Optimizer.

Simulates all workout strategies using the digital twin, scores each
using CES, and recommends the optimal training plan for the user's
current physiological state.

Selection criteria: maximize CES while penalizing overtraining risk.
"""

import numpy as np
import pandas as pd
from typing import Dict, List
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.cardiac_model import CardiacDigitalTwin
from simulation.workout_simulator import WorkoutSimulator
from scoring.ces_score import CESScorer

logger = logging.getLogger(__name__)


class AITrainingOptimizer:
    """
    Simulates and compares all training strategies, selecting the best
    based on cardiac response and CES optimization.
    """

    def __init__(self, twin: CardiacDigitalTwin, duration_min: int = 45):
        self.twin = twin
        self.duration_min = duration_min
        self.simulator = WorkoutSimulator()
        self.scorer = CESScorer()

    def _simulate_strategy(self, strategy: str, features: dict) -> dict:
        """
        Run one strategy simulation and return performance metrics.
        """
        self.twin.reset()
        profile = self.simulator.get_profile(strategy, self.duration_min)
        sim_df = self.twin.simulate(profile)

        # Extract metrics from simulation
        avg_hr = sim_df["heart_rate"].mean()
        max_hr = sim_df["heart_rate"].max()
        avg_fatigue = sim_df["fatigue"].mean()
        end_recovery = sim_df["recovery"].iloc[-1]
        avg_hrv = sim_df["hrv"].mean()

        # Build feature-like dict for CES scoring
        sim_features = {
            **features,  # keep user's baseline
            "avg_hr": avg_hr,
            "max_hr": max_hr,
            "hrv_avg": avg_hrv,
            "fatigue_index": avg_fatigue * 100,
            "hr_recovery_rate": features.get("hr_recovery_rate", 25),
            "zone1_pct": ((sim_df["heart_rate"] < 0.6 * self.twin.max_hr).sum() / len(sim_df)) * 100,
            "zone2_pct": (((sim_df["heart_rate"] >= 0.6 * self.twin.max_hr) & (sim_df["heart_rate"] < 0.7 * self.twin.max_hr)).sum() / len(sim_df)) * 100,
        }
        ces_result = self.scorer.score(sim_features)

        # Overtraining risk penalty
        risk_penalty = 0
        if avg_fatigue > 0.6:
            risk_penalty = 10
        elif avg_fatigue > 0.4:
            risk_penalty = 5

        adjusted_ces = max(0, ces_result["ces"] - risk_penalty)

        return {
            "strategy": strategy,
            "avg_hr": round(avg_hr, 1),
            "max_hr": round(max_hr, 1),
            "avg_fatigue": round(avg_fatigue * 100, 1),
            "end_recovery": round(end_recovery * 100, 1),
            "avg_hrv": round(avg_hrv, 1),
            "raw_ces": ces_result["ces"],
            "adjusted_ces": round(adjusted_ces, 1),
            "tier": ces_result["tier"],
            "risk_penalty": risk_penalty,
            "simulation": sim_df,
        }

    def optimize(self, features: dict) -> dict:
        """
        Run optimization across all strategies.

        Returns:
            dict with best_strategy, comparison_table, and simulation traces
        """
        logger.info("Running AI strategy optimization...")
        results = []
        simulations = {}

        for strategy in WorkoutSimulator.STRATEGIES:
            result = self._simulate_strategy(strategy, features)
            simulations[strategy] = result.pop("simulation")
            results.append(result)

        comparison_df = pd.DataFrame(results).sort_values("adjusted_ces", ascending=False)

        best = comparison_df.iloc[0]
        best_strategy = best["strategy"]

        logger.info(f"Optimal strategy: {best_strategy} (CES: {best['adjusted_ces']})")

        return {
            "best_strategy": best_strategy,
            "best_ces": best["adjusted_ces"],
            "comparison_table": comparison_df,
            "simulations": simulations,
            "recommendation": self._build_recommendation(best, features),
        }

    def _build_recommendation(self, best: pd.Series, features: dict) -> str:
        """Generate natural-language training recommendation."""
        fatigue = features.get("fatigue_index", 30)
        hrv = features.get("hrv_avg", 50)

        lines = [
            f"**Recommended Strategy: {best['strategy']}**",
            f"Predicted CES: {best['adjusted_ces']:.0f}/100",
            "",
        ]

        if fatigue > 60:
            lines.append("⚠️ High fatigue detected — prioritize recovery between sessions.")
        elif fatigue > 40:
            lines.append("⚡ Moderate fatigue — avoid back-to-back high-intensity days.")

        if hrv < 30:
            lines.append("💤 Low HRV — sleep quality and stress management should be prioritized.")
        elif hrv > 60:
            lines.append("✅ Excellent HRV — your nervous system is well-recovered.")

        lines.append(f"\n📊 Average HR during session: {best['avg_hr']} bpm")
        lines.append(f"🔥 Peak HR: {best['max_hr']} bpm")
        lines.append(f"💪 Recovery level post-session: {best['end_recovery']}%")

        return "\n".join(lines)
