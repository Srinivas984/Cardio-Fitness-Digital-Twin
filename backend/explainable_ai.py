"""
explainable_ai.py
-----------------
Explainable AI system for cardiovascular digital twin.

Generates human-readable explanations for personalized recommendations.
Analyzes feature impact and provides reasoning for optimal training strategies.

Explainability methods:
  - Feature contribution analysis
  - Training recommendation reasoning
  - Risk factor explanation
  - Recovery protocol justification
  - Comparative strategy analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class ExplainableAI:
    """Generate interpretable explanations for AI recommendations."""

    def __init__(self):
        self.feature_importance = {}
        self.threshold_alerts = {}

    def explain_training_recommendation(
        self,
        recommended_strategy: str,
        current_features: dict,
        baseline_features: dict,
        all_strategy_scores: dict,
    ) -> Dict[str, str]:
        """
        Generate comprehensive explanation for training recommendation.

        Args:
            recommended_strategy: Name of recommended strategy (e.g., "Low-Intensity Aerobic")
            current_features: User's current physiological features
            baseline_features: User's personal baseline
            all_strategy_scores: Scores for all evaluated strategies

        Returns:
            Dict with explanation components
        """
        explanation = {
            "recommendation": recommended_strategy,
            "primary_reasons": [],
            "supporting_metrics": [],
            "risk_considerations": [],
            "expected_benefits": [],
        }

        # --- Analyze current physiological state ---
        hrv = current_features.get("hrv_avg", 50)
        hrv_baseline = baseline_features.get("hrv_avg", 50)
        resting_hr = current_features.get("resting_hr", 65)
        resting_hr_baseline = baseline_features.get("resting_hr", 65)
        fatigue = current_features.get("fatigue_index", 30)

        # HRV Analysis
        hrv_ratio = hrv / hrv_baseline if hrv_baseline > 0 else 1.0
        if hrv_ratio < 0.70:
            explanation["primary_reasons"].append(
                "HRV significantly suppressed (autonomic nervous system fatigued)"
            )
            explanation["supporting_metrics"].append(
                f"HRV at {hrv:.0f} ms, {(1-hrv_ratio)*100:.0f}% below personal baseline"
            )
            recommendation_type = "recovery"
        elif hrv_ratio < 0.85:
            explanation["primary_reasons"].append(
                "HRV moderately reduced (subclinical autonomic stress)"
            )
            explanation["supporting_metrics"].append(
                f"HRV recovering ({(1-hrv_ratio)*100:.0f}% below baseline)"
            )
            recommendation_type = "moderate"
        else:
            explanation["primary_reasons"].append("HRV at healthy levels (good autonomic recovery)")
            recommendation_type = "performance"

        # Resting HR Analysis
        hr_elevation = resting_hr - resting_hr_baseline
        if hr_elevation >= 8:
            explanation["primary_reasons"].append(
                "Resting HR significantly elevated above baseline"
            )
            explanation["supporting_metrics"].append(
                f"RHR +{hr_elevation:.0f} bpm vs baseline (overtraining indicator)"
            )
        elif hr_elevation >= 3:
            explanation["supporting_metrics"].append(
                f"RHR slightly elevated (+{hr_elevation:.0f} bpm) – recovery recommended"
            )

        # Fatigue Analysis
        if fatigue >= 70:
            explanation["primary_reasons"].append("High fatigue accumulation detected")
            explanation["supporting_metrics"].append(
                f"Fatigue index: {fatigue:.0f}/100 (recovery is priority)"
            )
            explanation["risk_considerations"].append(
                "Risk: Continued training could trigger overtraining syndrome"
            )
        elif fatigue >= 50:
            explanation["supporting_metrics"].append(
                f"Fatigue index: {fatigue:.0f}/100 (moderate accumulated stress)"
            )
            explanation["risk_considerations"].append(
                "Caution: Avoid high-intensity work, focus on recovery"
            )

        # --- Strategy comparison ---
        if all_strategy_scores:
            best_strategy = recommended_strategy
            best_score = all_strategy_scores.get(best_strategy, {}).get("adjusted_ces", 0)

            # Find second-best for comparison
            other_scores = {
                k: v.get("adjusted_ces", 0)
                for k, v in all_strategy_scores.items()
                if k != best_strategy
            }
            if other_scores:
                second_best = max(other_scores, key=other_scores.get)
                second_score = other_scores[second_best]

                explanation["supporting_metrics"].append(
                    f"{best_strategy} scores +{best_score - second_score:.0f} points vs {second_best}"
                )

        # --- Expected benefits ---
        if "recovery" in recommendation_type.lower() or "Low" in recommended_strategy:
            explanation["expected_benefits"].extend([
                "Promotes parasympathetic nervous system recovery",
                "Allows accumtulated fatigue to decay",
                "Improves HRV rebound within 24-48 hours",
                "Reduces overtraining risk",
            ])
        elif "moderate" in recommendation_type.lower():
            explanation["expected_benefits"].extend([
                "Maintains cardiovascular fitness",
                "Allows cautious training while body recovers",
                "Supports gradual fatigue clearance",
                "Low risk of additional stress",
            ])
        else:  # Performance
            explanation["expected_benefits"].extend([
                "Excellent opportunity for performance gains",
                "High readiness for challenging work",
                "Supports aerobic capacity development",
                "Low injury/illness risk with good recovery",
            ])

        # --- Recovery recommendations ---
        if hr_elevation >= 8 or hrv_ratio < 0.70:
            explanation["risk_considerations"].append(
                "RECOMMENDED RECOVERY PROTOCOL: 7-10 days easy activity, prioritize sleep (8+ hours), "
                "nutrition optimization (carbs + protein), massage/stretching"
            )

        return explanation

    def explain_overtraining_risk(self, features: dict, risk_level: str, risk_score: float) -> dict:
        """
        Generate explanation for overtraining risk assessment.

        Args:
            features: Current physiological features
            risk_level: "Low Risk", "Moderate Risk", or "High Risk"
            risk_score: Risk score 0-10

        Returns:
            Dictionary with detailed risk explanation
        """
        explanation = {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "contributing_factors": [],
            "protective_factors": [],
            "immediate_actions": [],
        }

        hrv = features.get("hrv_avg", 50)
        hrv_baseline = features.get("hrv_avg", 50)
        resting_hr = features.get("resting_hr", 65)
        resting_hr_baseline = features.get("resting_hr", 65)
        fatigue = features.get("fatigue_index", 30)
        recovery = features.get("recovery_index", 60)

        # Contributing factors
        if hrv < hrv_baseline * 0.70:
            explanation["contributing_factors"].append(
                f"HRV suppression: {hrv:.0f} ms ({(1-hrv/hrv_baseline)*100:.0f}% below baseline)"
            )

        if resting_hr - resting_hr_baseline >= 5:
            explanation["contributing_factors"].append(
                f"Elevated resting HR: +{resting_hr - resting_hr_baseline:.0f} bpm (autonomic stress)"
            )

        if fatigue >= 60:
            explanation["contributing_factors"].append(
                f"High fatigue accumulation: {fatigue:.0f}/100 (training load not balanced by recovery)"
            )

        if recovery < 50:
            explanation["contributing_factors"].append(
                f"Poor recovery status: {recovery:.0f}/100 (inadequate sleep or nutrition)"
            )

        # Protective factors
        if hrv >= hrv_baseline * 0.90:
            explanation["protective_factors"].append(
                "Excellent HRV: parasympathetic nervous system functioning well"
            )

        if resting_hr <= resting_hr_baseline + 2:
            explanation["protective_factors"].append(
                "Stable resting HR: no sign of autonomic stress"
            )

        if fatigue <= 40:
            explanation["protective_factors"].append(
                "Low fatigue: training load is manageable"
            )

        if recovery >= 70:
            explanation["protective_factors"].append(
                "Strong recovery status: good sleep and nutrition support"
            )

        # Immediate actions
        if risk_level == "High Risk":
            explanation["immediate_actions"] = [
                "✓ Reduce training volume by 50-70% immediately",
                "✓ Shift all sessions to Zone 1-2 intensity (conversational pace)",
                "✓ Prioritize sleep: target 8.5-9 hours nightly",
                "✓ Increase carbohydrate intake (5-7 g/kg body weight daily)",
                "✓ Consider rest day (complete rest, not easy activity)",
                "✓ If symptoms persist beyond 7 days, consult sports physician",
            ]
        elif risk_level == "Moderate Risk":
            explanation["immediate_actions"] = [
                "✓ Reduce intensity by 20-30% for next 3-5 days",
                "✓ Eliminate all high-intensity intervals (Zones 4-5)",
                "✓ Increase sleep target by 1 hour",
                "✓ Add extra rest day this week",
                "✓ Monitor HRV and RHR daily for recovery trends",
                "✓ Focus on nutrition (especially carbs + protein post-workout)",
            ]
        else:  # Low Risk
            explanation["immediate_actions"] = [
                "✓ Continue current training plan",
                "✓ Maintain sleep schedule (7-9 hours nightly)",
                "✓ Consider 1 additional rest day per week for sustained progress",
                "✓ Monitor HRV weekly; avoid sudden training jumps above +10%",
            ]

        return explanation

    def feature_contribution_analysis(
        self, current_features: dict, baseline_features: dict
    ) -> Dict[str, float]:
        """
        Analyze which features contribute most to current physiology status.

        Returns:
            Dict mapping feature names to contribution scores (-100 to +100)
        """
        contributions = {}

        # HRV contribution
        hrv_current = current_features.get("hrv_avg", 50)
        hrv_baseline = baseline_features.get("hrv_avg", 50)
        hrv_change_pct = ((hrv_current - hrv_baseline) / hrv_baseline * 100) if hrv_baseline > 0 else 0
        contributions["HRV_recovery"] = hrv_change_pct  # Positive = better

        # Resting HR contribution
        rhr_current = current_features.get("resting_hr", 65)
        rhr_baseline = baseline_features.get("resting_hr", 65)
        rhr_contribution = ((rhr_baseline - rhr_current) / rhr_baseline * 100) if rhr_baseline > 0 else 0
        contributions["Resting_HR"] = rhr_contribution  # Positive = better (lower is better)

        # Fatigue contribution
        fatigue_current = current_features.get("fatigue_index", 30)
        contributions["Fatigue_status"] = -fatigue_current / 100 * 100  # Negative = more fatigued

        # Recovery index contribution
        recovery_current = current_features.get("recovery_index", 60)
        contributions["Recovery_capacity"] = (recovery_current - 50) / 50 * 100  # 50 is neutral

        # Activity load contribution
        load_current = current_features.get("activity_load", 50)
        contributions["Training_load"] = (load_current - 50) / 100 * 100  # Scale to -100 to +100

        return contributions

    def compare_strategies(
        self,
        strategy_scores: dict,
        current_features: dict,
    ) -> Dict[str, Dict]:
        """
        Generate comparison analysis for multiple training strategies.

        Args:
            strategy_scores: Dict of {strategy_name: metrics_dict}
            current_features: Current physiological state

        Returns:
            Dict with comparative analysis for each strategy
        """
        comparison = {}

        for strategy_name, metrics in strategy_scores.items():
            analysis = {
                "name": strategy_name,
                "score": metrics.get("adjusted_ces", 0),
                "avg_hr": metrics.get("avg_hr", 0),
                "fatigue_buildup": metrics.get("avg_fatigue", 0),
                "recovery_post_session": metrics.get("end_recovery", 0),
                "physiological_impact": "",
                "recommendation_context": "",
            }

            # Categorize impact
            if metrics.get("avg_fatigue", 0) > 0.6:
                analysis["physiological_impact"] = "High stress (severe fatigue)"
                analysis["recommendation_context"] = "Use only in high-recovery weeks"
            elif metrics.get("avg_fatigue", 0) > 0.4:
                analysis["physiological_impact"] = "Moderate stress"
                analysis["recommendation_context"] = "Suitable with proper recovery following"
            else:
                analysis["physiological_impact"] = "Low stress (builds adaptation)"
                analysis["recommendation_context"] = "Safe option for most recovery days"

            comparison[strategy_name] = analysis

        return comparison

    def generate_weekly_summary(self, daily_features_list: List[dict]) -> dict:
        """
        Generate summary explanation of weekly trends.

        Args:
            daily_features_list: List of daily feature dicts

        Returns:
            Summary with trends and recommendations
        """
        if not daily_features_list:
            return {}

        df = pd.DataFrame(daily_features_list)

        # Calculate trends
        hrv_trend = df["hrv_avg"].iloc[-1] - df["hrv_avg"].iloc[0] if len(df) > 0 else 0
        rhr_trend = df["resting_hr"].iloc[-1] - df["resting_hr"].iloc[0] if len(df) > 0 else 0
        fatigue_trend = df["fatigue_index"].iloc[-1] - df["fatigue_index"].iloc[0] if len(df) > 0 else 0

        summary = {
            "period_days": len(df),
            "hrv_trend": {
                "direction": "↑ Improving" if hrv_trend > 5 else "↓ Declining" if hrv_trend < -5 else "→ Stable",
                "magnitude": abs(hrv_trend),
            },
            "rhr_trend": {
                "direction": "↓ Improving" if rhr_trend < -2 else "↑ Declining" if rhr_trend > 2 else "→ Stable",
                "magnitude": abs(rhr_trend),
            },
            "fatigue_trend": {
                "direction": "↓ Improving" if fatigue_trend < -5 else "↑ Deteriorating" if fatigue_trend > 5 else "→ Stable",
                "magnitude": abs(fatigue_trend),
            },
            "overall_assessment": "",
            "recommendations": [],
        }

        # Overall assessment
        positive_trends = sum([
            1 for d in [hrv_trend > 5, rhr_trend < -2, fatigue_trend < -5] if d
        ])

        if positive_trends >= 2:
            summary["overall_assessment"] = "Excellent week: Adaptation progressing well"
            summary["recommendations"].append("Maintain current training plan")
            summary["recommendations"].append("Consider modest volume increase (5-10%) next week")
        elif positive_trends == 1:
            summary["overall_assessment"] = "Good week: Some positive adaptation"
            summary["recommendations"].append("Continue current load; monitor trends")
        else:
            summary["overall_assessment"] = "Concerning week: Limited recovery"
            summary["recommendations"].append("Reduce volume or intensity next week")
            summary["recommendations"].append("Prioritize sleep and nutrition")

        return summary
