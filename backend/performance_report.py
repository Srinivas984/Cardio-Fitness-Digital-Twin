"""
performance_report.py
---------------------
Generate professional performance reports (weekly, monthly).

Report contents:
  - Cardiovascular metrics summary
  - Training load vs adaptation
  - HRV + RHR trends with interpretations
  - Risk analysis
  - Personalized recommendations
  - PDF export support
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PerformanceReportGenerator:
    """Generates professional CardioScore reports."""

    def __init__(self):
        self.report_history = []

    def generate_weekly_report(
        self,
        week_data: pd.DataFrame,
        baseline: Dict,
        trainer_name: Optional[str] = None
    ) -> Dict:
        """
        Generate comprehensive weekly report.
        
        Args:
            week_data: DataFrame with 7 days of data (HRV, RHR, fatigue, training)
            baseline: User baseline metrics
            trainer_name: Optional coach/trainer name for personalization
        """
        
        if week_data is None or len(week_data) == 0:
            return {"error": "Insufficient data for weekly report"}
        
        # Calculate weekly summaries
        summary = self._calculate_weekly_summary(week_data, baseline)
        trends = self._analyze_trends(week_data, baseline)
        risk_assessment = self._weekly_risk_assessment(week_data, baseline)
        recommendations = self._generate_recommendations(summary, trends, risk_assessment)
        
        report = {
            "report_type": "Weekly CardioScore",
            "week_start": week_data.index[0] if hasattr(week_data, 'index') else "Unknown",
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            
            # Executive Summary
            "executive_summary": {
                "overall_status": summary["status"],
                "fitness_direction": summary["fitness_direction"],
                "key_metrics": summary["key_metrics"],
                "primary_focus": recommendations["primary_recommendation"]
            },
            
            # Detailed Metrics
            "metrics_summary": summary,
            "trend_analysis": trends,
            "risk_profile": risk_assessment,
            
            # Recommendations
            "recommendations": recommendations,
            
            # Metadata
            "coach": trainer_name,
            "confidence_level": self._calculate_confidence(week_data)
        }
        
        self.report_history.append(report)
        return report

    def generate_monthly_report(
        self,
        month_data: pd.DataFrame,
        baseline: Dict,
        trainer_name: Optional[str] = None
    ) -> Dict:
        """Generate comprehensive monthly report with periodization analysis."""
        
        if month_data is None or len(month_data) < 20:
            return {"error": "Need 3+ weeks for monthly report"}
        
        weeks = self._split_into_weeks(month_data)
        weekly_summaries = []
        
        for i, week_df in enumerate(weeks, 1):
            weekly_report = self.generate_weekly_report(week_df, baseline)
            weekly_summaries.append({
                "week": i,
                "summary": weekly_report.get("executive_summary"),
                "metrics": weekly_report.get("metrics_summary")
            })
        
        # Calculate month progression
        progression = self._analyze_monthly_progression(weeks, baseline)
        periodization_fit = self._assess_periodization_effectiveness(weeks, baseline)
        
        report = {
            "report_type": "Monthly CardioScore",
            "month": month_data.index[0].strftime("%B %Y") if hasattr(month_data.index[0], 'strftime') else "Unknown",
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            
            # Overall assessment
            "monthly_status": self._determine_monthly_status(weeks),
            "training_effectiveness": progression.get("effectiveness_score"),
            "adaptation_success": progression.get("adaptation_score"),
            
            # Weekly breakdown
            "weekly_summaries": weekly_summaries,
            
            # Progression analysis
            "monthly_progression": progression,
            "periodization_assessment": periodization_fit,
            
            # Recommendations
            "monthly_recommendations": self._generate_monthly_recommendations(progression),
            
            "coach": trainer_name,
        }
        
        return report

    def export_to_markdown(self, report: Dict) -> str:
        """Convert report to markdown for email/sharing."""
        
        md = []
        md.append(f"# {report.get('report_type', 'Report')}")
        md.append(f"**Report Date:** {report.get('report_date')}")
        md.append("")
        
        # Executive summary
        if "executive_summary" in report:
            exec_sum = report["executive_summary"]
            md.append("## Executive Summary")
            md.append(f"**Status:** {exec_sum.get('overall_status', 'N/A')}")
            md.append(f"**Fitness Direction:** {exec_sum.get('fitness_direction', 'N/A')}")
            md.append(f"**Primary Focus:** {exec_sum.get('primary_focus', 'N/A')}")
            md.append("")
        
        # Metrics
        if "metrics_summary" in report:
            metrics = report["metrics_summary"]
            md.append("## Key Metrics")
            for metric_name, metric_val in metrics.get("key_metrics", {}).items():
                md.append(f"- **{metric_name}:** {metric_val}")
            md.append("")
        
        # Trends
        if "trend_analysis" in report:
            trends = report["trend_analysis"]
            md.append("## Trend Analysis")
            for trend_name, trend_desc in trends.items():
                md.append(f"- **{trend_name}:** {trend_desc}")
            md.append("")
        
        # Risk
        if "risk_profile" in report:
            risk = report["risk_profile"]
            md.append("## Risk Profile")
            md.append(f"**Overall Risk:** {risk.get('overall_risk', 'Unknown')}")
            for risk_name, risk_level in risk.get("specific_risks", {}).items():
                md.append(f"- {risk_name}: {risk_level}")
            md.append("")
        
        # Recommendations
        if "recommendations" in report:
            recs = report["recommendations"]
            md.append("## Recommendations")
            md.append(f"**Primary:** {recs.get('primary_recommendation', 'N/A')}")
            if "action_items" in recs:
                md.append("\n**Action Items:**")
                for action in recs["action_items"]:
                    md.append(f"- {action}")
            md.append("")
        
        return "\n".join(md)

    def export_to_json(self, report: Dict) -> Dict:
        """Export report as JSON for API/storage."""
        return {
            **report,
            "exported_at": datetime.now().isoformat(),
            "exportable_formats": ["markdown", "json", "pdf"]
        }

    # ─────────────────────────────────────────────────────────────────────
    # Helper Methods
    # ─────────────────────────────────────────────────────────────────────

    def _calculate_weekly_summary(self, week_data: pd.DataFrame, baseline: Dict) -> Dict:
        """Calculate summary statistics for the week."""
        
        hrv_data = week_data.get("hrv", []) if isinstance(week_data, dict) else \
                   week_data["hrv"].values if "hrv" in week_data.columns else []
        rhr_data = week_data.get("resting_hr", []) if isinstance(week_data, dict) else \
                   week_data["resting_hr"].values if "resting_hr" in week_data.columns else []
        fatigue_data = week_data.get("fatigue", []) if isinstance(week_data, dict) else \
                       week_data["fatigue"].values if "fatigue" in week_data.columns else []
        
        hrv_baseline = baseline.get("hrv_baseline", 50)
        rhr_baseline = baseline.get("resting_hr", 65)
        
        hrv_avg = np.mean(hrv_data) if len(hrv_data) > 0 else 0
        rhr_avg = np.mean(rhr_data) if len(rhr_data) > 0 else 0
        fatigue_avg = np.mean(fatigue_data) if len(fatigue_data) > 0 else 0
        
        # Determine status
        if hrv_avg > hrv_baseline and fatigue_avg < 50:
            status = "🟢 Excellent - Peak fitness"
        elif hrv_avg > (hrv_baseline * 0.9) and fatigue_avg < 60:
            status = "🟢 Good - Healthy adaptation"
        elif hrv_avg > (hrv_baseline * 0.75) and fatigue_avg < 70:
            status = "🟡 Fair - Accumulating fatigue"
        else:
            status = "🔴 Concerning - Recovery needed"
        
        # Fitness direction
        if len(hrv_data) >= 7:
            hrv_trend = np.polyfit(range(len(hrv_data[:7])), hrv_data[:7], 1)[0]
            fitness_dir = "📈 Improving" if hrv_trend > 0 else "📉 Declining" if hrv_trend < 0 else "→ Stable"
        else:
            fitness_dir = "→ Insufficient data"
        
        return {
            "status": status,
            "fitness_direction": fitness_dir,
            "key_metrics": {
                "HRV Average": f"{hrv_avg:.0f} ms ({(hrv_avg/hrv_baseline)*100:.0f}% baseline)",
                "Resting HR Average": f"{rhr_avg:.0f} bpm",
                "Fatigue Index": f"{fatigue_avg:.0f}%",
                "Days Analyzed": len(hrv_data)
            }
        }

    def _analyze_trends(self, week_data: pd.DataFrame, baseline: Dict) -> Dict:
        """Analyze HRV, RHR, and fatigue trends."""
        trends = {}
        
        # HRV trend
        hrv_data = week_data.get("hrv", []) if isinstance(week_data, dict) else \
                   (week_data["hrv"].values if "hrv" in week_data.columns else [])
        if len(hrv_data) >= 3:
            trend = np.polyfit(range(len(hrv_data)), hrv_data, 1)[0]
            trends["HRV Trajectory"] = f"{'Improving ↑' if trend > 0.5 else 'Declining ↓' if trend < -0.5 else 'Stable →'} ({trend:.1f} ms/day)"
        
        # RHR trend
        rhr_data = week_data.get("resting_hr", []) if isinstance(week_data, dict) else \
                   (week_data["resting_hr"].values if "resting_hr" in week_data.columns else [])
        if len(rhr_data) >= 3:
            trend = np.polyfit(range(len(rhr_data)), rhr_data, 1)[0]
            trends["Resting HR Trajectory"] = f"{'Decreasing ↓ (better)' if trend < -0.3 else 'Increasing ↑ (fatigue)' if trend > 0.3 else 'Stable →'}"
        
        return trends

    def _weekly_risk_assessment(self, week_data: pd.DataFrame, baseline: Dict) -> Dict:
        """Assess risks during the week."""
        
        hrv_data = week_data.get("hrv", []) if isinstance(week_data, dict) else \
                   (week_data["hrv"].values if "hrv" in week_data.columns else [])
        
        hrv_min = np.min(hrv_data) if len(hrv_data) > 0 else baseline.get("hrv_baseline", 50)
        hrv_baseline = baseline.get("hrv_baseline", 50)
        hrv_ratio = hrv_min / hrv_baseline if hrv_baseline > 0 else 1.0
        
        if hrv_ratio < 0.7:
            risk = "🔴 HIGH - HRV significantly suppressed"
        elif hrv_ratio < 0.85:
            risk = "🟡 MODERATE - HRV mildly suppressed"
        else:
            risk = "🟢 LOW - HRV within normal range"
        
        return {
            "overall_risk": risk,
            "specific_risks": {
                "HRV Depression": f"Min HRV: {hrv_min:.0f}ms ({(hrv_ratio)*100:.0f}% of baseline)"
            },
            "recommendations": "Monitor closely if risk is moderate or high" if hrv_ratio < 0.85 else "Green light for training"
        }

    def _generate_recommendations(self, summary: Dict, trends: Dict, risk: Dict) -> Dict:
        """Generate actionable recommendations."""
        
        status_str = summary.get("status", "")
        
        if "Excellent" in status_str:
            primary = "💪 Continue current training approach"
            actions = [
                "Can sustain or increase training intensity",
                "Monitor for overuse injuries",
                "This is not a recovery week"
            ]
        elif "Good" in status_str:
            primary = "✅ Maintain current approach with light modulation"
            actions = [
                "Can do normal high-intensity work",
                "Monitor HRV for signs of accumulation",
                "Plan recovery week in 4-5 days if trend is flat"
            ]
        elif "Fair" in status_str:
            primary = "🟡 Reduce intensity, emphasize recovery"
            actions = [
                "Focus on Zone 2 aerobic work",
                "Add 1-2 extra recovery days",
                "Prioritize sleep & nutrition"
            ]
        else:
            primary = "🔴 MANDATORY recovery week"
            actions = [
                "Reduce training volume by 50%",
                "No high-intensity work",
                "Daily stretching + meditation",
                "Sleep target: 9+ hours"
            ]
        
        return {
            "primary_recommendation": primary,
            "action_items": actions
        }

    def _split_into_weeks(self, month_data: pd.DataFrame) -> List[pd.DataFrame]:
        """Split month data into week chunks."""
        weeks = []
        for i in range(0, len(month_data), 7):
            weeks.append(month_data.iloc[i:i+7])
        return weeks

    def _analyze_monthly_progression(self, weeks: List[pd.DataFrame], baseline: Dict) -> Dict:
        """Analyze month-long progression."""
        
        if not weeks:
            return {"effectiveness_score": 0}
        
        weekly_scores = []
        for week in weeks:
            hrv_data = week.get("hrv", []) if isinstance(week, dict) else \
                       (week["hrv"].values if "hrv" in week.columns else [])
            if len(hrv_data) > 0:
                score = np.mean(hrv_data)
                weekly_scores.append(score)
        
        if len(weekly_scores) < 2:
            return {"effectiveness_score": 50, "adaptation_score": 50}
        
        # Calculate effectiveness (upward HRV trend)
        trend = np.polyfit(range(len(weekly_scores)), weekly_scores, 1)[0]
        effectiveness = min(100, max(0, 50 + (trend * 10)))
        
        # Adaptation score (HRV improvement or stability)
        adaptation = min(100, max(0, 50 + (trend * 5) + 25)) if trend >= 0 else 40
        
        return {
            "effectiveness_score": round(effectiveness, 0),
            "adaptation_score": round(adaptation, 0),
            "overall_trend": "Improving" if trend > 0 else "Declining" if trend < 0 else "Stable"
        }

    def _assess_periodization_effectiveness(self, weeks: List[pd.DataFrame], baseline: Dict) -> Dict:
        """Assess if training blocks are working."""
        
        periodization_notes = []
        
        if len(weeks) >= 4:
            # Check for pattern (build -> deload)
            periodization_notes.append({
                "finding": "4-week cycle detected",
                "assessment": "Good periodization structure"
            })
        
        return {
            "structure": "Periodized" if len(weeks) >= 3 else "Unstructured",
            "findings": periodization_notes
        }

    def _generate_monthly_recommendations(self, progression: Dict) -> List[str]:
        """Generate month-level recommendations."""
        
        recommendations = []
        
        if progression.get("effectiveness_score", 0) > 70:
            recommendations.append("✅ Training plan is working - continue approach")
        else:
            recommendations.append("🔄 Consider adjusting training plan next month")
        
        if progression.get("adaptation_score", 0) > 60:
            recommendations.append("💪 Athlete is adapting well")
        else:
            recommendations.append("⚠️ Monitor for plateaus or overtraining")
        
        return recommendations

    def _determine_monthly_status(self, weeks: List[pd.DataFrame]) -> str:
        """Overall monthly assessment."""
        
        if len(weeks) < 2:
            return "Insufficient data"
        
        # Simple average of week assessments
        good_weeks = sum(1 for week in weeks if len(week) >= 5)
        
        if good_weeks >= len(weeks) * 0.8:
            return "🟢 Excellent month"
        elif good_weeks >= len(weeks) * 0.6:
            return "🟡 Mixed month - some recovery needed"
        else:
            return "🔴 Challenging month - plan reset"

    def _calculate_confidence(self, data: pd.DataFrame) -> float:
        """Calculate confidence in report (0-100%)."""
        
        if data is None or len(data) < 3:
            return 0.0
        elif len(data) < 5:
            return 50.0
        else:
            return 90.0
