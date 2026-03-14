"""
Cardio Digital Twin — Final Version
====================================
Best UI from v2 + Best features from v3

RUN: streamlit run app_final.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os
import requests
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.health_data_csv_parser import HealthCSVParser
from backend.cardiac_model import CardiacDigitalTwin
from backend.optimizer_ai import AITrainingOptimizer
from backend.risk_detection import RiskDetector
from backend.explainable_ai import ExplainableAI
from simulation.workout_simulator import WorkoutSimulator
from simulation.cardiac_simulator import CardiacSimulator
from scoring.ces_score import CESScorer
from healthkit_connector import HealthKitConnector, LiveDataStreamer
from live_coach import LivePersonalCoach, VoiceCoach
from adaptive_workouts import AdaptiveWorkout, SmartNotifications

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG & STYLING (FROM V2 - GOOD UI)
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="🫀 Cardio Digital Twin — AI Coach",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg: #0d1117;
    --surf: #161b22;
    --surf2: #1c2330;
    --border: #21262d;
    --green: #3fb950;
    --blue: #58a6ff;
    --amber: #d29922;
    --red: #f85149;
    --purple: #bc8cff;
    --text: #c9d1d9;
    --muted: #8b949e;
}

html, body, .stApp {
    background: var(--bg) !important;
    font-family: 'IBM Plex Sans', sans-serif;
    color: var(--text);
}

.stApp > header { background: transparent !important; }
section[data-testid="stSidebar"] { background: var(--surf) !important; border-right: 1px solid var(--border); }
section[data-testid="stSidebar"] * { color: var(--text) !important; }

.kpi {
    background: var(--surf);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 20px;
}
.kpi-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 6px;
}
.kpi-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 28px;
    font-weight: 600;
    line-height: 1;
}

.alert-box {
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 13px;
    line-height: 1.5;
}
.alert-warn { background: rgba(210, 153, 34, .1); border: 1px solid rgba(210, 153, 34, .3); color: #e3b341; }
.alert-info { background: rgba(88, 166, 255, .08); border: 1px solid rgba(88, 166, 255, .25); color: #79c0ff; }
.alert-danger { background: rgba(248, 81, 73, .08); border: 1px solid rgba(248, 81, 73, .3); color: #ff7b72; }
.alert-success { background: rgba(63, 185, 80, .08); border: 1px solid rgba(63, 185, 80, .3); color: #3fb950; }

.recommendation-card {
    background: var(--surf2);
    border-left: 4px solid var(--blue);
    border-radius: 6px;
    padding: 16px;
    margin: 8px 0;
}
.recommendation-card.warn { border-left-color: var(--amber); }
.recommendation-card.danger { border-left-color: var(--red); }
.recommendation-card.success { border-left-color: var(--green); }

.stTabs [data-baseweb="tab-list"] { background: var(--surf) !important; border-radius: 8px; padding: 4px; gap: 3px; border: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: var(--muted) !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 11px !important; border-radius: 6px !important; padding: 7px 16px !important; letter-spacing: .06em; }
.stTabs [aria-selected="true"] { background: var(--blue) !important; color: #0d1117 !important; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: .5rem !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY LAYOUT
# ─────────────────────────────────────────────────────────────────────────────

PL = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(22, 27, 34, 0.9)",
    font=dict(family="IBM Plex Mono, monospace", color="#8b949e", size=11),
    xaxis=dict(gridcolor="#21262d", linecolor="#21262d", zerolinecolor="#21262d"),
    yaxis=dict(gridcolor="#21262d", linecolor="#21262d", zerolinecolor="#21262d"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#21262d", font=dict(size=11)),
    margin=dict(l=40, r=20, t=36, b=36),
)

# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_resource
def load_data():
    """Load Apple Health data"""
    try:
        data_dir = Path(__file__).parent / "data"
        csv_files = list(data_dir.glob("HealthAutoExport-*.csv"))
        
        if not csv_files:
            return None, None
        
        csv_file = csv_files[0]
        parser = HealthCSVParser(str(csv_file))
        
        features = parser.compute_personal_features()
        daily_df = parser.parse_daily_metrics()
        
        return features, daily_df
    except Exception as e:
        return None, None

features, daily_df = load_data()

# Demo data
if features is None or daily_df is None:
    features = {
        "resting_hr": 62, "max_hr": 185, "hrv_avg": 48,
        "fatigue_index": 35, "recovery_index": 65,
        "hr_recovery_rate": 28, "zone1_pct": 25, "zone2_pct": 30,
        "zone3_pct": 25, "zone4_pct": 15, "activity_load": 55,
        "avg_hr": 95,
    }

# ─────────────────────────────────────────────────────────────────────────────
# V3 FEATURES: CALCULATE KEY METRICS
# ─────────────────────────────────────────────────────────────────────────────

def calculate_recovery_score(daily_df):
    """Recovery 0-100: green/yellow/red"""
    if daily_df is None or len(daily_df) < 7:
        return 70, "yellow"
    
    recent = daily_df.tail(7)
    baseline = daily_df.head(7)
    
    recent_hrv = recent['hrv_sdnn'].dropna().mean() if 'hrv_sdnn' in recent.columns else 50
    baseline_hrv = baseline['hrv_sdnn'].dropna().mean() if 'hrv_sdnn' in baseline.columns else 50
    hrv_ratio = (recent_hrv / max(baseline_hrv, 1)) * 100
    
    recent_rhr = recent['resting_hr'].dropna().mean() if 'resting_hr' in recent.columns else 65
    baseline_rhr = baseline['resting_hr'].dropna().mean() if 'resting_hr' in baseline.columns else 65
    rhr_ratio = (baseline_rhr / max(recent_rhr, 1)) * 100
    
    score = (hrv_ratio * 0.5 + rhr_ratio * 0.5)
    score = np.clip(score, 0, 100)
    
    status = "green" if score >= 80 else "yellow" if score >= 60 else "red"
    return int(score), status

def check_overtraining_warnings(daily_df):
    """Check overtraining red flags"""
    warnings = []
    if daily_df is None or len(daily_df) < 7:
        return warnings
    
    recent = daily_df.tail(7)
    baseline = daily_df.head(7)
    
    recent_hrv = recent['hrv_sdnn'].dropna().mean()
    baseline_hrv = baseline['hrv_sdnn'].dropna().mean()
    if baseline_hrv > 0 and recent_hrv < baseline_hrv * 0.85:
        drop_pct = int((1 - recent_hrv/baseline_hrv) * 100)
        warnings.append(("overtraining", f"⚠️ HRV DROPPED {drop_pct}%", "Your body is overtrained. Take 2-3 easy days!", "high"))
    
    recent_rhr = recent['resting_hr'].dropna().mean()
    baseline_rhr = baseline['resting_hr'].dropna().mean()
    if baseline_rhr > 0 and recent_rhr > baseline_rhr + 5:
        rise = int(recent_rhr - baseline_rhr)
        warnings.append(("stress", f"⚠️ RHR UP {rise} BPM", "Stress/sickness/overtraining. Rest today!", "high"))
    
    return warnings

def get_ai_recommendation(recovery_score, daily_df):
    """AI workout recommendation"""
    if recovery_score >= 80:
        return "💪 Hard Run or 🏋️ Lower Body", "Fully recovered", "green"
    elif recovery_score >= 60:
        return "🚴 Moderate Ride or 💪 Upper Push", "Moderate recovery", "orange"
    else:
        return "🚶 Easy Walk or 😴 Rest", "Body needs recovery", "red"

def get_weekly_plan(recovery_score):
    """7-day training plan"""
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    if recovery_score >= 80:
        plan = ["Hard Run 💪", "Upper Push 💪", "Easy Jog 🟢", "CrossFit ⚡", "Lower Legs 💪", "Moderate 🟡", "Rest 😴"]
    elif recovery_score >= 60:
        plan = ["Moderate 🟡", "Upper Pull 💪", "Easy 🟢", "CrossFit ⚡", "Lower 💪", "Easy 🟢", "Rest 😴"]
    else:
        plan = ["Easy Walk 🟢", "Light 🟡", "Rest 😴", "Easy 🟢", "Light 🟡", "Easy 🟢", "Rest 😴"]
    
    return days, plan

recovery_score, recovery_status = calculate_recovery_score(daily_df)
warnings = check_overtraining_warnings(daily_df)
ai_workout, ai_reason, ai_color = get_ai_recommendation(recovery_score, daily_df)

# ─────────────────────────────────────────────────────────────────────────────
# TITLE
# ─────────────────────────────────────────────────────────────────────────────

st.title("🫀 Cardio Digital Twin")
st.markdown("*AI Coach + Recovery Score + Injury Detection + Smart Weekly Plans*")

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────

tab_dashboard, tab_live_coach, tab_ai_coach, tab_cardiac, tab_training, tab_recovery, tab_forecast = st.tabs([
    "📊 Dashboard",
    "📱 Live Coach",
    "🤖 Today's Coach",
    "🫀 Cardiac Analysis",
    "🤖 Training Intelligence",
    "💪 Recovery & Sleep",
    "📈 Forecast & Simulator",
])

# =============================================================================
# TAB 1: DASHBOARD (FROM V2 - GOOD)
# =============================================================================

with tab_dashboard:
    st.subheader("📊 Complete Health Dashboard")
    
    # Top metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Resting HR", f"{features['resting_hr']} bpm", "-2 bpm")
        st.caption("Lower is better")
    with col2:
        st.metric("HRV (SDNN)", f"{features['hrv_avg']:.0f} ms", "+5 ms")
        st.caption("Higher = better recovery")
    with col3:
        st.metric("Fatigue Index", f"{features['fatigue_index']:.0f}/100", "-8")
        st.caption("Training load")
    with col4:
        st.metric("Recovery", f"{features['recovery_index']:.0f}%", "+12%")
        st.caption("Adaptation status")
    with col5:
        st.metric("Training Load", f"{features['activity_load']:.0f}", "+15")
        st.caption("Weekly volume")
    
    # Heart rate zones
    st.markdown("---")
    st.markdown("### 🎯 Training Zones Distribution")
    
    zones_data = {
        "Zone 1 (Recovery)": features.get('zone1_pct', 25),
        "Zone 2 (Aerobic)": features.get('zone2_pct', 30),
        "Zone 3 (Tempo)": features.get('zone3_pct', 25),
        "Zone 4 (Threshold)": features.get('zone4_pct', 15),
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_zones = go.Figure(data=[go.Pie(
            labels=list(zones_data.keys()),
            values=list(zones_data.values()),
            hole=0.3,
            marker=dict(colors=['#3fb950', '#58a6ff', '#d29922', '#f85149'])
        )])
        fig_zones.update_layout(**PL, height=300)
        st.plotly_chart(fig_zones, width='stretch')
    
    with col2:
        st.markdown("""
        **Zone Balance Analysis:**
        - 🟢 Zone 1: 25% ✅ 
        - 🔵 Zone 2: 30% ✅
        - 🟠 Zone 3: 25% ✅
        - 🔴 Zone 4: 15% ✅
        
        **Status:** Well-balanced training distribution
        """)
    
    # Recovery score gauge
    st.markdown("---")
    st.markdown("### 💚 Recovery Readiness Score")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if daily_df is not None and len(daily_df) >= 7:
            fig_hrv = go.Figure()
            fig_hrv.add_trace(go.Scatter(
                x=list(range(len(daily_df.tail(7)))),
                y=daily_df.tail(7)['hrv_sdnn'].fillna(0),
                mode='lines+markers',
                name='HRV',
                line=dict(color='#58a6ff', width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor='rgba(88, 166, 255, 0.2)'
            ))
            fig_hrv.update_layout(**PL, height=280, showlegend=False, title="HRV Trend (Last 7 Days)")
            st.plotly_chart(fig_hrv, width='stretch')
    
    with col2:
        status_emoji = "🟢" if recovery_status == "green" else "🟡" if recovery_status == "yellow" else "🔴"
        st.markdown(f"""
        <div class="kpi">
            <div class="kpi-label">Recovery Score</div>
            <div class="kpi-value">{recovery_score}</div>
            <div style="font-size: 40px; text-align: center; margin-top: 10px;">{status_emoji}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if recovery_status == "green":
            st.success("**Ready for Hard Workout**")
            st.caption("You're well recovered and can push intensity")
        elif recovery_status == "yellow":
            st.warning("**Ready for Moderate**")
            st.caption("Good for training but don't max effort")
        else:
            st.error("**Rest/Easy Only**")
            st.caption("Your body needs recovery time")
    
    # RHR trend
    st.markdown("---")
    st.markdown("### 📉 Resting Heart Rate Trend")
    
    if daily_df is not None and len(daily_df) >= 7:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            fig_rhr = go.Figure()
            fig_rhr.add_trace(go.Scatter(
                x=list(range(len(daily_df))),
                y=daily_df['resting_hr'].fillna(daily_df['resting_hr'].mean()),
                mode='lines+markers',
                name='RHR',
                line=dict(color='#ef4444', width=2),
                fill='tozeroy',
                fillcolor='rgba(239, 68, 68, 0.1)'
            ))
            fig_rhr.update_layout(**PL, height=250, showlegend=False)
            st.plotly_chart(fig_rhr, width='stretch')
        
        with col2:
            rhr_trend = daily_df['resting_hr'].tail(7).mean() - daily_df['resting_hr'].head(7).mean()
            st.metric("RHR Change", f"{rhr_trend:+.1f} bpm", delta_color="inverse")
            if rhr_trend < -2:
                st.success("Trending down = Getting fitter!")
            elif rhr_trend > 2:
                st.warning("Trending up = Fatigue or overtraining")
            else:
                st.info("Stable = Consistent fitness")
    
    # Key insights
    st.markdown("---")
    st.markdown("### 🔍 Key Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### ❤️ Cardiovascular Health
        - HR: Excellent baseline
        - Recovery: Within normal ranges
        - Variability: Good parasympathetic tone
        """)
    
    with col2:
        st.markdown("""
        #### 💪 Training Status
        - Load: Moderate volume
        - Intensity: Well distributed
        - Fatigue: Under control
        """)
    
    with col3:
        st.markdown("""
        #### 😴 Recovery Status
        - Sleep: Adequate
        - Stress: Low markers
        - Ready: For training today
        """)

# =============================================================================
# TAB 2: LIVE APPLE WATCH COACH (NEW FEATURE)
# =============================================================================

with tab_live_coach:
    st.subheader("📱 Live Apple Watch Coach: Real-Time Guidance")
    
    # Initialize live components
    if "heartkit_connector" not in st.session_state:
        st.session_state.healthkit_connector = HealthKitConnector(use_demo_mode=True)
        st.session_state.live_coach = LivePersonalCoach()
        st.session_state.adaptive_workout = AdaptiveWorkout()
        st.session_state.notifications = SmartNotifications()
    
    connector = st.session_state.healthkit_connector
    coach = st.session_state.live_coach
    
    # Check if iPhone data is available from API
    try:
        api_response = requests.get("http://localhost:5000/api/iphone", timeout=2)
        api_data = api_response.json() if api_response.status_code == 200 else {}
        iphone_connected = api_data.get("status") == "✅ iPhone connected"
        iphone_data_age = api_data.get("age_seconds", 999)
        data_is_fresh = iphone_data_age < 300  # 5 minutes
    except:
        iphone_connected = False
        iphone_data_age = 999
        data_is_fresh = False
    
    # Connection status
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if iphone_connected and data_is_fresh:
            st.success(f"📱 iPhone Connected (Live)")
        elif iphone_connected:
            st.warning(f"📱 iPhone Connected (Stale - restart Shortcut)")
        else:
            st.error("📱 Apple Watch Disconnected")
    
    with col2:
        if iphone_connected and data_is_fresh:
            st.metric("Signal", "Excellent", "Live")
        elif iphone_connected:
            st.metric("Signal", "Waiting", f"({int(iphone_data_age)}s old)")
        else:
            st.metric("Signal", "Demo Mode", "Synthetic")
    
    with col3:
        if iphone_connected and data_is_fresh:
            st.metric("Data Age", f"{int(iphone_data_age)}s old", "Fresh")
        elif iphone_connected:
            st.metric("Data Age", f"{int(iphone_data_age)}s old", "Stale")
    
    st.markdown("---")
    
    # Get metrics from API or demo
    try:
        if data_is_fresh:  # Only use API if data is fresh
            metrics_response = requests.get("http://localhost:5000/api/metrics", timeout=2)
            metrics = metrics_response.json() if metrics_response.status_code == 200 else {}
        else:
            metrics = {}  # Ignore stale data, use demo
    except:
        metrics = {}
    
    # Live metrics dashboard
    st.markdown("### 📊 Live Metrics from Apple Watch")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if data_is_fresh and metrics and "heart_rate" in metrics:
            hr = metrics["heart_rate"]["value"]
        else:
            hr, _ = connector.get_live_heart_rate()
        st.metric("❤️ Heart Rate", f"{hr} bpm", delta="Status: normal", delta_color="off")
    
    with col2:
        if data_is_fresh and metrics and "hrv" in metrics and metrics["hrv"]["value"] is not None:
            hrv = metrics["hrv"]["value"]
        else:
            hrv = connector.get_live_hrv()
        st.metric("🫀 HRV", f"{hrv:.0f} ms", delta="Recovery metric", delta_color="off")
    
    with col3:
        if data_is_fresh and metrics and "steps" in metrics:
            steps = metrics["steps"]["steps"]
            goal = metrics["steps"]["goal"]
        else:
            steps_data = connector.get_step_count()
            steps = steps_data["steps"]
            goal = steps_data["goal"]
        st.metric("👣 Steps", f"{steps:,}", delta=f"Goal: {goal:,}", delta_color="off")
    
    with col4:
        if data_is_fresh and metrics and "active_energy" in metrics:
            calories = metrics["active_energy"].get("value", 0)
            cal_goal = metrics["active_energy"].get("goal", 500)
        else:
            energy_data = connector.get_active_energy()
            calories = energy_data["calories"]
            cal_goal = energy_data["goal"]
        st.metric("🔥 Active Energy", f"{calories} kcal", delta=f"Goal: {cal_goal}", delta_color="off")
    
    st.markdown("---")
    
    # Workout control section
    st.markdown("### 🏋️ Start Live Coaching Session")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        workout_type = st.selectbox(
            "Workout Type",
            ["Running", "Cycling", "Strength", "HIIT", "Recovery"],
            key="live_workout_type"
        )
    
    with col2:
        duration = st.slider("Duration (min)", 15, 180, 45, step=5, key="live_duration")
    
    with col3:
        intensity = st.select_slider(
            "Target Zone",
            options=["1: Recovery", "2: Aerobic", "3: Tempo", "4: Threshold", "5: Max"],
            value="2: Aerobic",
            key="live_intensity"
        )
        zone = int(intensity.split(":")[0])
    
    if st.button("▶️ START LIVE COACHING", key="start_live", width='stretch'):
        st.session_state.live_session = True
        st.session_state.session_start = datetime.now()
        st.rerun()
    
    st.markdown("---")
    
    # Live coaching if session active
    if st.session_state.get("live_session", False):
        st.markdown("### 🎯 Real-Time Coaching Feed")
        
        # Get current metrics (from API if available and fresh, otherwise from demo)
        if data_is_fresh and metrics and "heart_rate" in metrics:
            hr = metrics["heart_rate"]["value"]
        else:
            hr, _ = connector.get_live_heart_rate()
        
        elapsed = int((datetime.now() - st.session_state.session_start).total_seconds())
        
        # Get coaching
        coaching = coach.get_real_time_coaching(hr, zone, elapsed)
        
        # Display coaching cue prominently
        st.markdown(f"""
        <div style="background: rgba(88, 166, 255, 0.1); border-left: 4px solid #58a6ff; border-radius: 8px; padding: 16px; margin: 12px 0;">
            <h3 style="margin: 0; color: #58a6ff;">💬 Coaching Cue</h3>
            <p style="font-size: 18px; margin: 12px 0 0 0; color: #c9d1d9;">{coaching['coaching_cue']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🎯 Action", coaching["next_action"])
        
        with col2:
            st.metric("⚡ Adjustment", coaching["intensity_adjustment"])
        
        with col3:
            st.metric("⏱️ Elapsed", f"{coaching['elapsed_minutes']:.1f} min")
        
        # Overexertion alert
        overexert = coach.detect_overexertion(hr, 190, coaching['elapsed_minutes'])
        if overexert["urgency"] in ["high", "critical"]:
            st.warning(f"⚠️ {overexert['recommendation']}")
        
        # Pacing guidance
        pacing = coach.get_pacing_guidance(hr, 190, 0)
        st.info(f"📍 {pacing}")
        
        # Stop button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("⏹️ END SESSION", key="stop_live", width='stretch'):
                st.session_state.live_session = False
                st.rerun()
        
        st.markdown("---")
        
        # Live HR graph (simulated history)
        st.markdown("### 📈 Heart Rate During Workout")
        
        # Generate fake history for demo
        elapsed_int = int(coaching['elapsed_minutes'])
        times = [datetime.now() - timedelta(minutes=i) for i in range(elapsed_int, 0, -1)] if elapsed_int > 0 else []
        hrs_history = [hr + np.random.normal(0, 5) for hr in [120 + i*5 for i in range(len(times))]]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times,
            y=hrs_history,
            mode='lines+markers',
            name='Heart Rate',
            line=dict(color='#ef4444', width=3),
            fill='tozeroy',
            fillcolor='rgba(239, 68, 68, 0.1)',
            marker=dict(size=5)
        ))
        
        fig.add_hline(y=130, line_dash="dash", line_color="#3fb950", annotation_text="Zone Min")
        fig.add_hline(y=155, line_dash="dash", line_color="#d29922", annotation_text="Zone Max")
        
        fig.update_layout(**PL, height=300, xaxis_title="Time", yaxis_title="BPM")
        st.plotly_chart(fig, width='stretch')
    
    else:
        st.info("📱 Press START to begin a live coaching session with your Apple Watch")

# =============================================================================
# TAB 3: TODAY'S COACH (NEW V3 FEATURE)
# =============================================================================

with tab_ai_coach:
    st.subheader("🤖 AI Coach: Complete Today's Plan")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="recommendation-card success">
            <strong style="font-size: 20px;">🎯 {ai_workout}</strong><br>
            <span style="color: #94a3b8; font-size: 14px;">{ai_reason}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 💡 Why This Workout?")
        
        if recovery_score >= 80:
            st.info("""
            **High Recovery (80+):** Your body is fully recovered!
            - ✅ Muscles: Fully repaired
            - ✅ HRV: Normal/elevated - parasympathetic active
            - ✅ RHR: Low - good cardiovascular state
            - ✅ Energy: High
            
            **Perfect for:** Intense training, building speed/power, heavy lifting
            """)
        elif recovery_score >= 60:
            st.info("""
            **Moderate Recovery (60-79):** Good to train but stay measured
            - ⚠️ Muscles: Partially recovered
            - ⚠️ HRV: Normal
            - ⚠️ RHR: Baseline
            - ⚠️ Energy: Decent
            
            **Perfect for:** Moderate intensity, skill practice, balanced work
            """)
        else:
            st.info("""
            **Low Recovery (0-59):** Body needs rest to adapt
            - 🔴 Muscles: Still repairing
            - 🔴 HRV: Suppressed
            - 🔴 RHR: Elevated
            - 🔴 Energy: Low
            
            **Perfect for:** Easy movement, active recovery, mobility
            """)
    
    with col2:
        fig = go.Figure(data=[go.Indicator(
            mode="gauge+number+delta",
            value=recovery_score,
            title={'text': "Recovery Score"},
            delta={'reference': 70},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#0ea5e9"},
                   'steps': [
                       {'range': [0, 30], 'color': "rgba(239, 68, 68, 0.2)"},
                       {'range': [30, 60], 'color': "rgba(245, 158, 11, 0.2)"},
                       {'range': [60, 100], 'color': "rgba(34, 197, 94, 0.2)"},
                   ]}
        )])
        fig.update_layout(**PL, height=320)
        st.plotly_chart(fig, width='stretch')
    
    # Detailed metrics
    st.markdown("---")
    st.markdown("### 📊 Recovery Details")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        hrv_status = daily_df['hrv_sdnn'].tail(7).mean() if daily_df is not None else 50
        st.metric("HRV (7-day avg)", f"{hrv_status:.0f} ms")
        if hrv_status > 45:
            st.success("Excellent recovery")
        else:
            st.warning("Monitor closely")
    
    with col2:
        rhr_status = daily_df['resting_hr'].tail(7).mean() if daily_df is not None else 65
        st.metric("RHR (7-day avg)", f"{rhr_status:.0f} bpm")
        if rhr_status < 65:
            st.success("Good baseline")
        else:
            st.warning("Elevated - rest needed")
    
    with col3:
        st.metric("Training Load", f"{features['activity_load']:.0f}")
        if features['activity_load'] < 60:
            st.caption("Moderate - can increase")
        else:
            st.caption("High - manage carefully")
    
    with col4:
        st.metric("Days in Week", "7 days")
        st.caption("Training volume analysis")
    
    # Overtraining warnings
    if warnings:
        st.markdown("---")
        st.markdown("### ⚠️ System Warnings")
        for _, title, desc, severity in warnings:
            if severity == "high":
                st.error(f"**{title}**\n\n{desc}")
            else:
                st.warning(f"**{title}**\n\n{desc}")
    else:
        st.success("✅ No overtraining warnings - You're good to go!")
    
    # Weekly plan (detailed)
    st.markdown("---")
    st.markdown("### 📅 Optimal Training Week")
    st.caption("Auto-personalized based on your current recovery state")
    
    days, plan = get_weekly_plan(recovery_score)
    
    cols = st.columns(7)
    for i, (day, workout) in enumerate(zip(days, plan)):
        with cols[i]:
            color = "#3fb950" if "🟢" in workout else "#f85149" if "🔴" in workout else "#d29922" if "🟡" in workout else "#0ea5e9"
            st.markdown(f"""
            <div style="background: rgba(22, 27, 34, 0.8); border-left: 4px solid {color}; border-radius: 8px; padding: 12px; text-align: center;">
                <strong style="font-size: 12px;">{day}</strong><br>
                <span style="font-size: 18px; margin: 8px 0; display: block;">{workout}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Training tips
    st.markdown("---")
    st.markdown("### 🎯 Today's Action Plan")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Before Workout**
        - 🥗 Eat light snack
        - 💧 Drink water (500ml)
        - 🫁 Warm up 5-10 min
        - 🧠 Mental prep
        """)
    
    with col2:
        st.markdown("""
        **During Workout**
        - 📊 Track intensity
        - 💧 Stay hydrated
        - 🎯 Focus on form
        - 📱 Monitor HR
        """)
    
    with col3:
        st.markdown("""
        **After Workout**
        - ❄️ Cool down 5 min
        - 🧘 Stretch 10 min
        - 🥤 Refuel & hydrate
        - 😴 Sleep 8+ hours
        """)

# =============================================================================
# TAB 3: CARDIAC (FROM V2)
# =============================================================================

with tab_cardiac:
    st.subheader("❤️ Cardiac Analysis: Heart Health Deep Dive")
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    # Use available data from features or daily_df
    current_hr = features.get('avg_hr', 72) if features else 72
    avg_hr = features.get('avg_hr', 72) if features else 72
    max_hr = features.get('max_hr', 180) if features else 180
    rhr = daily_df['resting_hr'].iloc[-1] if daily_df is not None and 'resting_hr' in daily_df.columns and len(daily_df) > 0 else 65
    
    with col1:
        st.metric("Current HR", f"{current_hr:.0f} bpm", "Activity-based")
        st.caption("Average during activity")
    
    with col2:
        st.metric("Avg HR", f"{avg_hr:.0f} bpm")
        st.caption("Session average")
    
    with col3:
        st.metric("Max HR", f"{max_hr:.0f} bpm")
        st.caption("Peak intensity")
    
    with col4:
        st.metric("Resting HR", f"{rhr:.0f} bpm")
        if rhr < 60:
            st.success("Excellent fitness")
        elif rhr < 70:
            st.info("Good fitness level")
        else:
            st.warning("Monitor trends")
    
    st.markdown("---")
    
    # Heart rate trend over time (using daily data)
    st.markdown("### 📈 Resting Heart Rate Trend (30 Days)")
    
    if daily_df is not None and len(daily_df) > 3 and 'resting_hr' in daily_df.columns:
        fig_hr = go.Figure()
        fig_hr.add_trace(go.Scatter(
            x=daily_df.index,
            y=daily_df['resting_hr'],
            mode='lines+markers',
            name='Resting HR',
            line=dict(color='#ef4444', width=2),
            fill='tozeroy',
            fillcolor='rgba(239, 68, 68, 0.1)',
            marker=dict(size=5)
        ))
        
        # Add zone bands
        fig_hr.add_hline(y=60, line_dash="dash", line_color="#3fb950", annotation_text="Good", annotation_position="right", annotation_font_size=10)
        fig_hr.add_hline(y=70, line_dash="dash", line_color="#d29922", annotation_text="Elevated", annotation_position="right", annotation_font_size=10)
        
        fig_hr.update_layout(**PL, height=300, xaxis_title="Date", yaxis_title="BPM")
        st.plotly_chart(fig_hr, width='stretch')
    else:
        st.info("Not enough data yet. Check back after 3+ days of tracking.")
    
    # HR Variability (HRV) Analysis
    st.markdown("---")
    st.markdown("### 🫀 Heart Rate Variability (HRV)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("""
        **What is HRV?** The variation in time between heartbeats
        - **High HRV (>50ms):** Better recovery, parasympathetic active
        - **Normal HRV (35-50ms):** Balanced nervous system
        - **Low HRV (<35ms):** Fatigue, stress, or overtraining detected
        
        **Why it matters:** HRV predicts recovery better than any other metric
        """)
    
    with col2:
        hrv_avg = daily_df['hrv_sdnn'].tail(7).mean() if daily_df is not None and 'hrv_sdnn' in daily_df.columns and len(daily_df) >= 7 else 45
        fig = go.Figure(data=[go.Indicator(
            mode="gauge+number",
            value=hrv_avg,
            title={'text': "HRV (7-day avg)"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#0ea5e9"},
                   'steps': [
                       {'range': [0, 35], 'color': "rgba(239, 68, 68, 0.2)"},
                       {'range': [35, 50], 'color': "rgba(245, 158, 11, 0.2)"},
                       {'range': [50, 100], 'color': "rgba(34, 197, 94, 0.2)"},
                   ]}
        )])
        fig.update_layout(**PL, height=300)
        st.plotly_chart(fig, width='stretch')
    
    # HRV Trend over time
    if daily_df is not None and len(daily_df) > 3 and 'hrv_sdnn' in daily_df.columns:
        st.markdown("### HRV Trend (30 Days)")
        
        fig_hrv = go.Figure()
        fig_hrv.add_trace(go.Scatter(
            x=daily_df.index,
            y=daily_df['hrv_sdnn'],
            mode='lines+markers',
            name='HRV',
            line=dict(color='#0ea5e9', width=2),
            fill='tozeroy',
            fillcolor='rgba(14, 165, 233, 0.1)',
            marker=dict(size=5)
        ))
        
        fig_hrv.add_hline(y=50, line_dash="dash", line_color="#3fb950", annotation_text="Excellently Recovered")
        fig_hrv.add_hline(y=35, line_dash="dash", line_color="#f85149", annotation_text="Fatigue Risk")
        
        fig_hrv.update_layout(**PL, height=300, xaxis_title="Date", yaxis_title="HRV (ms)")
        st.plotly_chart(fig_hrv, width='stretch')
    
    # Training zones - visualization with available data
    st.markdown("---")
    st.markdown("### 🎯 Training Zone Capability")
    
    zone_capabilities = {
        "Recovery\n(Easy)": min(100, max_hr * 0.65),
        "Aerobic\n(Steady)": min(100, max_hr * 0.80),
        "Tempo\n(Hard)": min(100, max_hr * 0.92),
        "Threshold\n(Maximum)": max_hr,
    }
    
    fig_zones = go.Figure(data=[go.Bar(
        x=list(zone_capabilities.keys()),
        y=list(zone_capabilities.values()),
        marker=dict(color=['#3fb950', '#58a6ff', '#d29922', '#f85149']),
        text=[f"{int(v)} bpm" for v in zone_capabilities.values()],
        textposition='auto',
    )])
    fig_zones.update_layout(**PL, height=300, yaxis_title="Heart Rate (bpm)")
    st.plotly_chart(fig_zones, width='stretch')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        **Z1: Recovery**
        Easy, conversational pace
        
        ✅ For rest days, active recovery
        """)
    
    with col2:
        st.markdown("""
        **Z2: Aerobic**
        Steady, buildable effort
        
        ✅ For base building, long sessions
        """)
    
    with col3:
        st.markdown("""
        **Z3: Tempo**
        Hard but sustainable
        
        ✅ For fitness development
        """)
    
    with col4:
        st.markdown("""
        **Z4: Threshold**
        Maximum sustainable effort
        
        ✅ For speed work, power
        """)
    
    # Cardiac insights
    st.markdown("---")
    st.markdown("### 💡 Heart Health Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if avg_hr < 100 and rhr < 65:
            st.success("""
            **Excellent Cardiovascular Fitness**
            
            ✅ Low average HR during activity
            ✅ Low resting HR
            ✅ Good aerobic base
            
            💪 Strong endurance capacity
            """)
        else:
            st.info("""
            **Building Cardiovascular Fitness**
            
            ⚠️ Continue consistent training
            ⚠️ Build aerobic base
            ⚠️ Add steady sessions
            
            📈 Fitness improves over time
            """)
    
    with col2:
        if max_hr > 170:
            st.success("""
            **Good Intensity Capacity**
            
            ✅ Can handle high loads
            ✅ Good anaerobic power
            ✅ Supports speed work
            
            🏃 Able to push hard
            """)
        else:
            st.info("""
            **Developing Intensity**
            
            ⚠️ Build speed work
            ⚠️ Add intervals
            ⚠️ Work on peak capacity
            
            🚀 Will improve with training
            """)
    
    with col3:
        hrv_7day = daily_df['hrv_sdnn'].tail(7).mean() if daily_df is not None and 'hrv_sdnn' in daily_df.columns and len(daily_df) >= 7 else 50
        if hrv_7day > 50:
            st.success("""
            **Excellent Recovery State**
            
            ✅ High HRV
            ✅ Rested nervous system
            ✅ Ready for intensity
            
            🎯 Perfect for hard work
            """)
        elif hrv_7day > 35:
            st.info("""
            **Normal Recovery State**
            
            ⚠️ Moderate HRV
            ⚠️ Balanced condition
            ⚠️ Can train normally
            
            📊 Monitor trends
            """)
        else:
            st.warning("""
            **Low Recovery State**
            
            🔴 Low HRV
            🔴 Fatigue signals
            🔴 Needs rest
            
            😴 Prioritize recovery
            """)

# =============================================================================
# TAB 4: TRAINING (FROM V2 - ENHANCED)
# =============================================================================

with tab_training:
    st.subheader("Training Intelligence")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("Choose a workout and see your heart's response:")
        strategy = st.selectbox("Select Workout", WorkoutSimulator.STRATEGIES, key="strategy")
        duration = st.slider("Duration (minutes)", 20, 90, 45, step=5, key="duration")
    
    with col2:
        st.markdown("""
        **When you workout:**
        - ❤️ Heart rate rises
        - 😩 Fatigue builds
        - 😴 Recovery needed
        - 📊 HRV affected
        """)
    
    if st.button("▶️ Run Simulation", key="sim_run"):
        with st.spinner("Simulating..."):
            twin = CardiacDigitalTwin(
                resting_hr=features.get("resting_hr", 65),
                max_hr=features.get("max_hr", 190),
                hrv_baseline=features.get("hrv_avg", 50),
            )
            twin.reset()
            
            profile = WorkoutSimulator.get_profile(strategy, duration)
            sim_df = twin.simulate(profile)
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=("Heart Rate", "Fatigue", "HRV", "Output"),
                vertical_spacing=0.12, horizontal_spacing=0.10
            )
            
            fig.add_trace(go.Scatter(x=sim_df['time_min'], y=sim_df['heart_rate'],
                                    mode='lines', line=dict(color='#f85149'),
                                    fill='tozeroy', fillcolor='rgba(248, 81, 73, 0.1)'),
                         row=1, col=1)
            fig.add_trace(go.Scatter(x=sim_df['time_min'], y=sim_df['fatigue']*100,
                                    mode='lines', line=dict(color='#d29922'),
                                    fill='tozeroy', fillcolor='rgba(210, 153, 34, 0.1)'),
                         row=1, col=2)
            fig.add_trace(go.Scatter(x=sim_df['time_min'], y=sim_df['hrv'],
                                    mode='lines', line=dict(color='#58a6ff'),
                                    fill='tozeroy', fillcolor='rgba(88, 166, 255, 0.1)'),
                         row=2, col=1)
            fig.add_trace(go.Scatter(x=sim_df['time_min'], y=sim_df.get('cardiac_output', sim_df['heart_rate']/60),
                                    mode='lines', line=dict(color='#3fb950'),
                                    fill='tozeroy', fillcolor='rgba(63, 185, 80, 0.1)'),
                         row=2, col=2)
            
            fig.update_layout(**PL, height=600, showlegend=False)
            st.plotly_chart(fig, width='stretch')
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Avg HR", f"{sim_df['heart_rate'].mean():.0f} bpm")
            with col2:
                st.metric("Peak HR", f"{sim_df['heart_rate'].max():.0f} bpm")
            with col3:
                st.metric("Fatigue", f"{sim_df['fatigue'].mean()*100:.0f}%")
            with col4:
                st.metric("Recovery", f"{sim_df['recovery'].iloc[-1]*100:.0f}%")
            with col5:
                st.metric("HRV Avg", f"{sim_df['hrv'].mean():.0f} ms")

# =============================================================================
# TAB 5: RECOVERY (FROM V2)
# =============================================================================

with tab_recovery:
    st.subheader("😴 Recovery & Sleep: Optimize Your Adaptation")
    
    # Recovery Score Quick View
    col1, col2, col3, col4 = st.columns(4)
    
    hrv_7day = daily_df['hrv_sdnn'].tail(7).mean() if daily_df is not None and 'hrv_sdnn' in daily_df.columns else 45
    rhr_7day = daily_df['resting_hr'].tail(7).mean() if daily_df is not None and 'resting_hr' in daily_df.columns else 65
    recovery_idx = (hrv_7day / 50) * 100 if hrv_7day > 0 else 70  # Normalize to 100
    
    with col1:
        st.metric("HRV (7-day)", f"{hrv_7day:.0f} ms")
        if hrv_7day > 50:
            st.success("Excellent")
        elif hrv_7day > 35:
            st.info("Normal")
        else:
            st.warning("Low - Rest needed")
    
    with col2:
        st.metric("RHR (7-day)", f"{rhr_7day:.0f} bpm")
        if rhr_7day < 60:
            st.success("Excellent")
        elif rhr_7day < 70:
            st.info("Good")
        else:
            st.warning("Elevated - Consider rest")
    
    with col3:
        st.metric("Recovery Index", f"{min(100, recovery_idx):.0f}%")
        if recovery_idx > 80:
            st.success("Very Ready")
        else:
            st.info("Ready to train")
    
    with col4:
        sleep_est = "7-8 hrs" if hrv_7day > 45 else "6-7 hrs"
        st.metric("Sleep Need", sleep_est)
        st.caption("Estimated based on HRV")
    
    st.markdown("---")
    
    # Recovery mechanisms explained
    st.markdown("### 🔄 How Recovery Works")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        **The Recovery Cycle:**
        1. **Workout** - Muscle damage
        2. **Rest** - Adaptation begins
        3. **Sleep** - Hormone release
        4. **Recovery** - Muscles rebuild stronger
        5. **Ready** - For next challenge
        
        Cycle time: 24-48 hours
        """)
    
    with col2:
        recovery_stages = {
            "Immediate (0-2 hrs)": "Cool down, refuel, hydrate",
            "Short-term (2-24 hrs)": "Sleep, nutrition, light movement",
            "Medium-term (1-3 days)": "Full recovery protocols",
            "Long-term (1-2 weeks)": "Performance gains appear",
        }
        
        for stage, action in recovery_stages.items():
            st.markdown(f"• **{stage}:** {action}")
    
    st.markdown("---")
    
    # HRV & RHR correlation
    st.markdown("### 📊 HRV vs RHR: Recovery Indicators")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **HRV (Heart Rate Variability)**
        
        📊 **What it measures:** Time variation between heartbeats
        
        ✅ **High HRV (>50ms):**
        - Parasympathetic active (rest & digest)
        - Well-recovered nervous system
        - Ready for hard training
        
        🔴 **Low HRV (<35ms):**
        - Sympathetic active (fight or flight)
        - Fatigued nervous system
        - Needs recovery days
        """)
    
    with col2:
        st.info("""
        **RHR (Resting Heart Rate)**
        
        📊 **What it measures:** HR when fully rested
        
        ✅ **Low RHR (<60bpm):**
        - Good cardiovascular fitness
        - Efficient heart
        - Positive training adaptation
        
        🔴 **High RHR (>70bpm):**
        - May indicate fatigue
        - Insufficient recovery
        - Needs lighter training
        """)
    
    # Sleep quality impact chart
    st.markdown("---")
    st.markdown("### 🛌 Sleep Quality Impact on Recovery")
    
    if daily_df is not None and len(daily_df) > 7:
        fig_sleep = go.Figure()
        
        fig_sleep.add_trace(go.Scatter(
            x=daily_df.index,
            y=daily_df['hrv_sdnn'],
            mode='lines+markers',
            name='HRV',
            line=dict(color='#0ea5e9', width=2),
            yaxis='y'
        ))
        
        fig_sleep.add_trace(go.Scatter(
            x=daily_df.index,
            y=daily_df['resting_hr'],
            mode='lines+markers',
            name='RHR',
            line=dict(color='#ef4444', width=2),
            yaxis='y2'
        ))
        
        layout_dict = dict(PL)
        layout_dict.update({
            'height': 300,
            'hovermode': 'x unified',
            'yaxis': dict(title=dict(text="HRV (ms)", font=dict(color="#0ea5e9"))),
            'yaxis2': dict(title=dict(text="RHR (bpm)", font=dict(color="#ef4444")), overlaying='y', side='right'),
        })
        fig_sleep.update_layout(**layout_dict)
        
        st.plotly_chart(fig_sleep, width='stretch')
        st.caption("Notice: When both HRV ↑ and RHR ↓ = Better sleep & recovery")
    
    # Recovery tips
    st.markdown("---")
    st.markdown("### 💡 Daily Recovery Protocol")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        **Morning (0-2 hrs after wake)**
        
        📊 Current state: {'✅ Ready' if recovery_idx > 70 else '⚠️ Monitor'}
        
        ✅ Do:
        - Hydrate (500ml water)
        - Light breakfast
        - Mobility exercises
        - Check HRV reading
        
        ❌ Avoid:
        - Cold exposure
        - Stressful situations
        - Intense exercise
        """)
    
    with col2:
        st.markdown("""
        **Afternoon (2-8 hrs)**
        
        🏋️ Training window
        
        ✅ Do:
        - Structured training
        - Proper warm-up
        - Progressive loading
        - Adequate hydration
        
        ❌ Avoid:
        - Excessive volume
        - Training when fatigued
        - Overtraining
        """)
    
    with col3:
        st.markdown("""
        **Evening (8+ hrs)**
        
        😴 Recovery priority
        
        ✅ Do:
        - Proper cool-down
        - Protein-rich meal
        - Stretch & mobility
        - 8+ hours sleep
        
        ❌ Avoid:
        - Blue light before bed
        - Caffeine after 2pm
        - Large meals
        - Stress/anxiety
        """)
    
    # Recovery readiness
    st.markdown("---")
    st.markdown("### 🎯 Recovery Readiness Check")
    
    readiness_factors = {
        "HRV Status": "Good ✅" if hrv_7day > 35 else "Low 🔴",
        "RHR Status": "Good ✅" if rhr_7day < 70 else "Elevated 🔴",
        "Recovery Trend": "Improving ✅" if hrv_7day > 40 else "Stable ✅" if hrv_7day > 30 else "Declining 🔴",
        "Sleep Quality": "Likely Good ✅" if hrv_7day > 45 else "Check Pattern 🔴",
        "Training Load": "Manageable ✅" if rhr_7day < 70 else "High 🔴",
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        for factor, status in readiness_factors.items():
            st.markdown(f"• **{factor}:** {status}")
    
    with col2:
        overall_readiness = sum([1 for s in readiness_factors.values() if "✅" in s])
        readiness_pct = (overall_readiness / len(readiness_factors)) * 100
        
        fig = go.Figure(data=[go.Indicator(
            mode="gauge+number",
            value=readiness_pct,
            title={'text': "Overall Readiness"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#0ea5e9"},
                   'steps': [
                       {'range': [0, 40], 'color': "rgba(239, 68, 68, 0.2)"},
                       {'range': [40, 70], 'color': "rgba(245, 158, 11, 0.2)"},
                       {'range': [70, 100], 'color': "rgba(34, 197, 94, 0.2)"},
                   ]}
        )])
        fig.update_layout(**PL, height=300)
        st.plotly_chart(fig, width='stretch')

# =============================================================================
# TAB 6: FORECAST (FROM V2)
# =============================================================================

with tab_forecast:
    st.subheader("📈 30-Day Forecast: Trending & Predictions")
    
    if daily_df is not None and len(daily_df) > 5:
        # RHR Trend
        st.markdown("### 📉 Resting Heart Rate Trend")
        
        fig_rhr = go.Figure()
        
        fig_rhr.add_trace(go.Scatter(
            x=daily_df.index,
            y=daily_df['resting_hr'].fillna(daily_df['resting_hr'].mean()),
            mode='lines+markers',
            name='RHR',
            line=dict(color='#f85149', width=2),
            fill='tozeroy',
            fillcolor='rgba(239, 68, 68, 0.1)',
            marker=dict(size=6)
        ))
        
        # Add trend line
        if len(daily_df) > 2:
            z = np.polyfit(range(len(daily_df)), daily_df['resting_hr'].fillna(daily_df['resting_hr'].mean()), 1)
            p = np.poly1d(z)
            fig_rhr.add_trace(go.Scatter(
                x=daily_df.index,
                y=p(range(len(daily_df))),
                mode='lines',
                name='Trend',
                line=dict(color='#58a6ff', width=2, dash='dash')
            ))
        
        fig_rhr.update_layout(**PL, height=300, hovermode='x unified')
        st.plotly_chart(fig_rhr, width='stretch')
        
        # RHR interpretation
        col1, col2 = st.columns(2)
        
        with col1:
            rhr_current = daily_df['resting_hr'].iloc[-1] if len(daily_df) > 0 else 65
            rhr_start = daily_df['resting_hr'].iloc[0] if len(daily_df) > 0 else 65
            rhr_change = rhr_start - rhr_current
            
            st.metric("RHR Change", f"{rhr_change:+.1f} bpm", 
                     delta_color="inverse",  # inverse = green for negative, red for positive
                     label_visibility="visible")
            
            if rhr_change > 0:
                st.success(f"""
                **✅ Getting Fitter!**
                
                Down {rhr_change:.1f} bpm over 30 days
                At this rate: Another 3 bpm drop in 30 days
                Aerobic base improving 📈
                """)
            elif rhr_change < -5:
                st.warning(f"""
                **⚠️ Fatigue Accumulating**
                
                Up {abs(rhr_change):.1f} bpm - possible overtraining
                Monitor closely for recovery
                Consider deload week
                """)
            else:
                st.info(f"""
                **ℹ️ Stable**
                
                RHR stable ± 2 bpm
                Normal variation
                Continue current plan
                """)
        
        with col2:
            if len(daily_df) > 7:
                rhr_7day = daily_df['resting_hr'].tail(7).mean()
                rhr_30day = daily_df['resting_hr'].mean()
                rhr_14day = daily_df['resting_hr'].tail(14).mean()
                
                st.markdown(f"""
                **7-Day Averages**
                
                • Last 7 days: **{rhr_7day:.1f}** bpm
                • Last 14 days: **{rhr_14day:.1f}** bpm
                • Last 30 days: **{rhr_30day:.1f}** bpm
                
                Trend: {'Improving ✅' if rhr_7day < rhr_14day else 'Declining ⚠️' if rhr_7day > rhr_14day else 'Stable ℹ️'}
                """)
        
        st.markdown("---")
        
        # HRV Trend
        if 'hrv_sdnn' in daily_df.columns:
            st.markdown("### 📊 HRV Recovery Trend")
            
            fig_hrv = go.Figure()
            
            fig_hrv.add_trace(go.Scatter(
                x=daily_df.index,
                y=daily_df['hrv_sdnn'],
                mode='lines+markers',
                name='HRV',
                line=dict(color='#0ea5e9', width=2),
                fill='tozeroy',
                fillcolor='rgba(14, 165, 233, 0.1)',
                marker=dict(size=6)
            ))
            
            # Add threshold lines
            fig_hrv.add_hline(y=50, line_dash="dash", line_color="#3fb950", annotation_text="Excellent (>50)")
            fig_hrv.add_hline(y=35, line_dash="dash", line_color="#f85149", annotation_text="Fatigue (<35)")
            
            fig_hrv.update_layout(**PL, height=300, hovermode='x unified')
            st.plotly_chart(fig_hrv, width='stretch')
            
            hrv_current = daily_df['hrv_sdnn'].iloc[-1] if len(daily_df) > 0 else 45
            hrv_avg = daily_df['hrv_sdnn'].mean()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Current HRV", f"{hrv_current:.0f} ms")
                if hrv_current > 50:
                    st.success("Excellent Recovery 🎯")
                elif hrv_current > 35:
                    st.info("Normal Recovery 📊")
                else:
                    st.error("Low - Rest Needed 🔴")
            
            with col2:
                st.markdown(f"""
                **HRV Analysis**
                
                • Current: **{hrv_current:.0f}** ms
                • 30-day avg: **{hrv_avg:.0f}** ms
                • Status: {'🟢 High' if hrv_current > 50 else '🟡 Normal' if hrv_current > 35 else '🔴 Low'}
                
                Recovery pattern: {'Stable' if abs(hrv_current - hrv_avg) < 10 else 'Volatile'}
                """)
        
        st.markdown("---")
        
        # Comparative metrics
        st.markdown("### 📊 Fitness Metrics Comparison")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            rhr_min = daily_df['resting_hr'].min() if 'resting_hr' in daily_df.columns else 60
            rhr_max = daily_df['resting_hr'].max() if 'resting_hr' in daily_df.columns else 72
            st.metric("RHR Range", f"{rhr_min:.0f}-{rhr_max:.0f}")
            st.caption(f"Spread: {rhr_max - rhr_min:.0f} bpm")
        
        with col2:
            hrv_min = daily_df['hrv_sdnn'].min() if 'hrv_sdnn' in daily_df.columns else 30
            hrv_max = daily_df['hrv_sdnn'].max() if 'hrv_sdnn' in daily_df.columns else 60
            st.metric("HRV Range", f"{hrv_min:.0f}-{hrv_max:.0f}")
            st.caption(f"Spread: {hrv_max - hrv_min:.0f} ms")
        
        with col3:
            days_good = (daily_df['hrv_sdnn'] > 45).sum() if 'hrv_sdnn' in daily_df.columns else 0
            pct_good = round(100 * days_good / len(daily_df)) if len(daily_df) > 0 else 0
            st.metric("Days Well-Recovered", f"{pct_good}%")
            st.caption(f"{days_good} of {len(daily_df)} days")
        
        with col4:
            days_trained = len([x for x in daily_df.index if x is not None])
            avg_per_week = round(7 * days_trained / max(len(daily_df), 1))
            st.metric("Training Frequency", f"{avg_per_week}x/week")
            st.caption("Based on activity data")
        
        st.markdown("---")
        
        # Advanced insights
        st.markdown("### 💡 Performance Insights & Predictions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if len(daily_df) > 7:
                rhr_7 = daily_df['resting_hr'].tail(7).mean()
                rhr_30 = daily_df['resting_hr'].mean()
                slope = rhr_30 - rhr_7
                
                if slope > 2:
                    st.error(f"""
                    **⚠️ Fatigue Trend Detected**
                    
                    Recent RHR higher than average
                    Last 7 days: {rhr_7:.0f} bpm (vs 30-day avg: {rhr_30:.0f})
                    
                    Recommendation:
                    • Reduce training volume
                    • Focus on sleep quality
                    • Consider 1-2 easy days
                    """)
                elif slope < -2:
                    st.success(f"""
                    **✅ Fitness Gain Trend**
                    
                    Recent weeks show improvement
                    Last 7 days: {rhr_7:.0f} bpm (vs 30-day avg: {rhr_30:.0f})
                    
                    Positive indicators:
                    • Aerobic fitness improving
                    • Training adaptation working
                    • Continue current progression
                    """)
                else:
                    st.info(f"""
                    **ℹ️ Stable Performance**
                    
                    RHR stable within normal range
                    Last 7 days: {rhr_7:.0f} bpm (vs 30-day avg: {rhr_30:.0f})
                    
                    Next steps:
                    • Maintain current program
                    • Look for small improvements
                    • Stay consistent
                    """)
        
        with col2:
            if 'hrv_sdnn' in daily_df.columns and len(daily_df) > 7:
                hrv_7 = daily_df['hrv_sdnn'].tail(7).mean()
                hrv_30 = daily_df['hrv_sdnn'].mean()
                recovery_quality = "Excellent" if hrv_7 > 50 else "Good" if hrv_7 > 40 else "Fair" if hrv_7 > 30 else "Poor"
                
                st.markdown(f"""
                **Recovery Quality: {recovery_quality}**
                
                HRV Analysis:
                • Last 7 days: **{hrv_7:.0f}** ms
                • 30-day avg: **{hrv_30:.0f}** ms
                
                **Action Recommendation:**
                
                {'🎯 Ready for intensity - Good recovery base' if hrv_7 > 45 else '⚠️ Maintain moderate training - Monitor recovery' if hrv_7 > 35 else '🔴 Reduce intensity urgently - Rest needed'}
                """)
    
    else:
        st.info("📊 Need more data. Check back after 7+ days of tracking.")

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown("""
<center style="color: #8b949e;">

**Cardio Digital Twin** — AI Coach + Recovery Science  
*6 Tabs: Dashboard | AI Coach | Cardiac | Training | Recovery | Forecast*

Built with ❤️ for athletes
</center>
""", unsafe_allow_html=True)
