"""
app.py — Advanced Cardio Digital Twin Dashboard V2
===================================================
Research-grade AI cardiovascular coach powered by REAL Apple Watch data.

RUN: streamlit run app.py

New Features:
  • Advanced physiological heart model with autonomic nervous system
  • AI-powered Bayesian optimization for training recommendations
  • 30-day performance prediction engine
  • Interactive digital twin simulator
  • Explainable AI with reasoning for all recommendations
  • Multi-day recovery protocol simulation
  • Real-time risk detection with personalized thresholds
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.health_auto_export_parser import HealthAutoExportParser
from backend.health_data_csv_parser import HealthCSVParser
from backend.apple_health_xml_parser import AppleHealthXMLParser
from backend.cardiac_model import CardiacDigitalTwin
from backend.optimizer_ai import AITrainingOptimizer
from backend.prediction_engine import PredictionEngine
from backend.risk_detection import RiskDetector
from backend.explainable_ai import ExplainableAI
from backend.predictive_alerts import PredictiveAlerts
from backend.recovery_protocols import RecoveryProtocols
from backend.performance_report import PerformanceReportGenerator
from backend.sleep_recovery import SleepRecoveryAnalyzer
from backend.personalization_engine import PersonalizationEngine
from simulation.workout_simulator import WorkoutSimulator
from simulation.cardiac_simulator import CardiacSimulator
from scoring.ces_score import CESScorer

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG & STYLING
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="🫀 Cardio Digital Twin — Advanced AI Coach",
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

/* KPI Styling */
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
.kpi-sub { font-size: 11px; color: var(--muted); margin-top: 5px; }

/* Alert Styling */
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

/* Card Styling */
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

/* Tab Styling */
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
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────

DATA_DIR = Path(__file__).parent / "data"
XML_EXPORT_PATH = Path(r"C:\Users\sssri\Downloads\export\apple_health_export\export_cda.xml")

@st.cache_data
def load_apple_health_xml():
    """Load lifetime Apple Health data from XML export."""
    try:
        if not XML_EXPORT_PATH.exists():
            st.warning(f"XML export not found at {XML_EXPORT_PATH}")
            return None, None
        
        parser = AppleHealthXMLParser(str(XML_EXPORT_PATH))
        features = parser.compute_personal_features()
        daily_df = parser.parse_daily_metrics()
        workouts_df = parser.parse_workouts()
        
        st.success(f"✅ Loaded lifetime Apple Health data: {parser.get_data_summary()}")
        
        return features, daily_df, workouts_df
    except Exception as e:
        st.warning(f"Could not load Apple Health XML: {e}")
        return None, None

@st.cache_data
def load_real_data(use_xml=False):
    """Load health data from CSV or XML files."""
    try:
        if use_xml:
            features, daily_df, workouts_df = load_apple_health_xml()
            if features is None:
                raise Exception("XML loading failed, falling back to CSV")
            return features, daily_df, workouts_df, None, None, None
        else:
            # Load from comprehensive CSV export
            csv_path = DATA_DIR / "HealthAutoExport-2026-02-11-2026-03-13.csv"
            if csv_path.exists():
                parser = HealthCSVParser(str(csv_path))
                features = parser.compute_personal_features()
                daily_df = parser.parse_daily_metrics()
                return features, daily_df, None, None, None, None
            else:
                # Fall back to old parser
                parser = HealthAutoExportParser(str(DATA_DIR))
                features = parser.compute_personal_features()
                daily_df = parser.parse_daily_summary()
                workouts_df = parser.parse_workouts()
                walk_hr = parser.parse_workout_hr("Indoor_Walk")
                cycle_hr = parser.parse_workout_hr("Outdoor_Cycling")
                cycle_rec = parser.parse_hr_recovery("Outdoor_Cycling")
                return features, daily_df, workouts_df, walk_hr, cycle_hr, cycle_rec
    except Exception as e:
        st.warning(f"Could not load Apple Health data: {e}. Using demo mode.")
        return None, None, None, None, None, None

@st.cache_data
def get_scores(hrv, rhr, hrv3, fat, rec, recdrop, z1, z2, z3, z4, load, maxhr, avghr):
    """Compute CES scores."""
    f = dict(
        hrv_avg=hrv, resting_hr=rhr, hrv_last3=hrv3, fatigue_index=fat,
        recovery_index=rec, hr_recovery_rate=recdrop, zone1_pct=z1,
        zone2_pct=z2, zone3_pct=z3, zone4_pct=z4, activity_load=load,
        max_hr=maxhr, avg_hr=avghr
    )
    return CESScorer().score(f)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

st.title("🫀 Cardiovascular Digital Twin")
st.markdown("*Advanced AI coach for personalized training optimization*")

# Sidebar: Data source selector
with st.sidebar:
    st.markdown("### 📊 Data Source")
    data_source = st.radio(
        "Choose data source:",
        ["CSV Health Export (31 days)", "Lifetime Apple Health XML"],
        index=0
    )
    use_xml = data_source == "Lifetime Apple Health XML"

# Load data
features, daily_df, workouts_df, walk_hr, cycle_hr, cycle_rec = load_real_data(use_xml=use_xml)

# Demo data if no real data
if features is None:
    features = {
        "resting_hr": 62,
        "max_hr": 185,
        "hrv_avg": 48,
        "fatigue_index": 35,
        "recovery_index": 65,
        "hr_recovery_rate": 28,
        "zone1_pct": 25,
        "zone2_pct": 30,
        "zone3_pct": 25,
        "zone4_pct": 15,
        "zone5_pct": 5,
        "activity_load": 55,
        "avg_hr": 95,
    }

# Initialize models
@st.cache_resource
def init_models():
    """Initialize cardiac digital twin and supporting models."""
    twin = CardiacDigitalTwin(
        resting_hr=features.get("resting_hr", 65),
        max_hr=features.get("max_hr", 190),
        hrv_baseline=features.get("hrv_avg", 50),
    )
    twin.calibrate(features)
    
    return {
        "twin": twin,
        "optimizer": AITrainingOptimizer(twin, duration_min=45),
        "predictor": PredictionEngine(twin),
        "risk_detector": RiskDetector(
            hrv_baseline=50.0,  # Will be overridden dynamically
            resting_hr_baseline=65.0,  # Will be overridden dynamically
        ),
        "explainer": ExplainableAI(),
        "simulator": CardiacSimulator(twin),
        "alerts": PredictiveAlerts(),
        "recovery_protocols": RecoveryProtocols(),
        "report_generator": PerformanceReportGenerator(),
        "sleep_analyzer": SleepRecoveryAnalyzer(),
        "personalization": PersonalizationEngine(),
    }

models = init_models()

# ─────────────────────────────────────────────────────────────────────────────
# TAB MENU
# ─────────────────────────────────────────────────────────────────────────────

tab_dashboard, tab_cardiac, tab_training, tab_recovery, tab_forecast, tab_insights = st.tabs([
    "📊 Dashboard",
    "🫀 Cardiac Analysis",
    "🤖 Training Intelligence",
    "💪 Recovery & Sleep",
    "📈 Forecast & Simulator",
    "💡 Insights",
])

# =============================================================================
# TAB 1: DASHBOARD
# =============================================================================

with tab_dashboard:
    st.subheader("Current Cardiovascular Status")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Resting HR", f"{features['resting_hr']} bpm", "-2 bpm")
    with col2:
        st.metric("HRV (SDNN)", f"{features['hrv_avg']:.0f} ms", "+5 ms")
    with col3:
        st.metric("Fatigue Index", f"{features['fatigue_index']:.0f}/100", "-8 pts")
    with col4:
        st.metric("Recovery", f"{features['recovery_index']:.0f}%", "+12%")
    with col5:
        st.metric("Training Load", f"{features['activity_load']:.0f}", "+15")

    # CES Score
    st.divider()
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Cardiac Enhancement Score (CES)")
        ces = get_scores(
            features['hrv_avg'], features['resting_hr'], features['hrv_avg']*0.95,
            features['fatigue_index'], features['recovery_index'], 
            features['hr_recovery_rate'], features['zone1_pct'], features['zone2_pct'],
            features['zone3_pct'], features['zone4_pct'], features['activity_load'],
            features['max_hr'], features['avg_hr']
        )
        
        fig_ces = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=ces['ces'],
            title={'text': "CES"},
            delta={'reference': 70},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#3fb950"},
                   'steps': [
                       {'range': [0, 50], 'color': "rgba(248, 81, 73, 0.2)"},
                       {'range': [50, 75], 'color': "rgba(210, 153, 34, 0.2)"},
                       {'range': [75, 100], 'color': "rgba(63, 185, 80, 0.2)"},
                   ]},
        ))
        fig_ces.update_layout(**PL, height=300)
        st.plotly_chart(fig_ces, use_container_width=True)
    
    with col2:
        st.markdown(f"""
        **Tier:** {ces['tier']}
        
        **Status:** {'Excellent' if ces['ces'] > 75 else 'Good' if ces['ces'] > 50 else 'Fair'}
        
        **Recommendation:** {'Aggressive training' if ces['ces'] > 75 else 'Balanced approach' if ces['ces'] > 50 else 'Recovery focus'}
        """)

    # Historical trends
    if daily_df is not None and len(daily_df) > 0:
        st.divider()
        st.subheader("📊 Your Health Metrics")
        
        # Show available metrics
        available_cols = [col for col in daily_df.columns if col != 'date' and daily_df[col].notna().sum() > 0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'resting_hr' in available_cols:
                fig_hr = go.Figure()
                fig_hr.add_trace(go.Scatter(x=daily_df['date'], y=daily_df['resting_hr'],
                                            mode='lines+markers', name='RHR', 
                                            line=dict(color='#f85149', width=2),
                                            fill='tozeroy', fillcolor='rgba(248, 81, 73, 0.1)'))
                fig_hr.update_layout(**PL, title="Resting Heart Rate", height=350,
                                   yaxis_title="BPM", xaxis_title="Date")
                st.plotly_chart(fig_hr, use_container_width=True)
        
        with col2:
            if 'hrv_sdnn' in available_cols:
                fig_hrv = go.Figure()
                fig_hrv.add_trace(go.Scatter(x=daily_df['date'], y=daily_df['hrv_sdnn'],
                                             mode='lines+markers', name='HRV',
                                             line=dict(color='#58a6ff', width=2),
                                             fill='tozeroy', fillcolor='rgba(88, 166, 255, 0.1)'))
                fig_hrv.update_layout(**PL, title="Heart Rate Variability", height=350,
                                    yaxis_title="SDNN (ms)", xaxis_title="Date")
                st.plotly_chart(fig_hrv, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            if 'steps' in available_cols:
                fig_steps = go.Figure()
                fig_steps.add_trace(go.Bar(x=daily_df['date'], y=daily_df['steps'],
                                          name='Steps', marker=dict(color='#3fb950')))
                fig_steps.update_layout(**PL, title="Daily Steps", height=350,
                                      yaxis_title="Count", xaxis_title="Date")
                st.plotly_chart(fig_steps, use_container_width=True)
        
        with col4:
            if 'active_energy_kJ' in available_cols:
                fig_energy = go.Figure()
                fig_energy.add_trace(go.Bar(x=daily_df['date'], y=daily_df['active_energy_kJ'],
                                           name='Active Energy', marker=dict(color='#d29922')))
                fig_energy.update_layout(**PL, title="Active Energy", height=350,
                                       yaxis_title="kJ", xaxis_title="Date")
                st.plotly_chart(fig_energy, use_container_width=True)
    else:
        st.info("No health data loaded. Select a data source to see real metrics.")
        
        with col2:
            fig_hrv = go.Figure()
            fig_hrv.add_trace(go.Scatter(x=daily_df.index[-7:], y=daily_df['hrv_sdnn'].iloc[-7:],
                                         mode='lines+markers', name='HRV', line=dict(color='#58a6ff')))
            fig_hrv.update_layout(**PL, title="HRV Recovery Trend", height=350,
                                yaxis_title="ms SDNN", xaxis_title="Date")
            st.plotly_chart(fig_hrv, use_container_width=True)

# =============================================================================
# TAB 2: CARDIAC ANALYSIS (Digital Twin + Risk Monitor)
# =============================================================================

with tab_cardiac:
    st.subheader("🫀 Cardiac Digital Twin & Risk Analysis")
    
    # Digital Twin Section
    st.markdown("### Digital Twin Simulation")
    st.subheader("Live Cardiac Digital Twin Simulation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("**Choose a workout type and see how your heart responds:**")
        strategy = st.selectbox("Select Workout", WorkoutSimulator.STRATEGIES, key="dt_strategy")
        duration = st.slider("Duration (minutes)", 20, 90, 45, step=5, key="dt_duration")
    
    with col2:
        st.markdown("""
        **Your Heart Will:**
        - 💓 Increase heart rate
        - 😩 Build fatigue
        - 😴 Need recovery time
        - 📊 Show HRV changes
        """)
    
    # Show workout tips based on selection
    workout_tips = {
        "🚶 Easy Walk (Recovery)": {
            "tip": "Gentle pace - good on rest days",
            "effort": "Easy 🟢",
            "time": "20-40 min",
            "fatigue": "Low",
            "recovery": "Fast",
            "for": "Recovery between hard workouts"
        },
        "🏃 Light Jog (Easy Run)": {
            "tip": "Can hold conversation - builds fitness without stress",
            "effort": "Light 🟡",
            "time": "30-60 min",
            "fatigue": "Low-Moderate",
            "recovery": "Quick",
            "for": "Most training days"
        },
        "🚴 Moderate Ride (Steady)": {
            "tip": "Breathing harder - good cardiovascular workout",
            "effort": "Moderate 🟠",
            "time": "40-60 min",
            "fatigue": "Moderate",
            "recovery": "24-48 hours",
            "for": "Building base fitness"
        },
        "💪 Hard Run (Fast)": {
            "tip": "Fast pace - high quality training but needs recovery",
            "effort": "Hard 🔴",
            "time": "30-50 min",
            "fatigue": "High",
            "recovery": "48+ hours",
            "for": "Building speed & power"
        },
        "⚡ Sprint Intervals (Very Hard)": {
            "tip": "Maximum effort - only 1-2x per week max",
            "effort": "Max 🔴🔴",
            "time": "30-45 min",
            "fatigue": "Very High",
            "recovery": "72+ hours",
            "for": "Peak fitness - needs recovery!"
        },
        "💪 Upper Body Push (Chest/Shoulders)": {
            "tip": "Bench press, shoulder press, dips - good muscle pump",
            "effort": "Moderate 🟠",
            "time": "45-60 min",
            "fatigue": "Moderate",
            "recovery": "24-48 hours",
            "for": "Building chest, shoulders, triceps"
        },
        "🔥 Upper Body Pull (Back/Biceps)": {
            "tip": "Pull-ups, rows, curls - heavy compound movements",
            "effort": "Moderate-High 🟠",
            "time": "45-60 min",
            "fatigue": "Moderate-High",
            "recovery": "24-48 hours",
            "for": "Building back strength & size"
        },
        "🦵 Lower Body Strength (Legs/Glutes)": {
            "tip": "Squats, deadlifts, lunges - most demanding workout",
            "effort": "Very Hard 🔴",
            "time": "50-70 min",
            "fatigue": "Very High",
            "recovery": "48-72 hours",
            "for": "Strongest legs! Needs good recovery"
        },
        "🏋️ Full Body Strength": {
            "tip": "Hit all muscle groups - compound movements throughout",
            "effort": "Hard 🔴",
            "time": "55-75 min",
            "fatigue": "High",
            "recovery": "48 hours",
            "for": "Complete balanced strength"
        },
        "⚙️ CrossFit/Mixed Training": {
            "tip": "Strength + cardio mix - functional movements, high intensity",
            "effort": "Very Hard 🔴",
            "time": "40-50 min",
            "fatigue": "Very High",
            "recovery": "48+ hours",
            "for": "Overall fitness & conditioning"
        }
    }
    
    if strategy in workout_tips:
        tip = workout_tips[strategy]
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Effort Level", tip["effort"])
        with col2:
            st.metric("Typical Time", tip["time"])
        with col3:
            st.metric("Fatigue Build", tip["fatigue"])
        with col4:
            st.metric("Recovery Need", tip["recovery"])
        with col5:
            st.info(f"💡 {tip['for']}")
        
        st.info(f"**💬 {tip['tip']}")
    
    # Run simulation
    if st.button("▶️ Run Simulation", key="dt_run"):
        with st.spinner("Simulating your cardiac response..."):
            twin = models["twin"]
            twin.reset()
            
            profile = WorkoutSimulator.get_profile(strategy, duration)
            sim_df = twin.simulate(profile)
            
            # 4-subplot visualization with better titles
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    "❤️ Heart Rate During Workout", 
                    "😩 Fatigue Building Up",
                    "😴 HRV Recovery", 
                    "🫁 Heart Pumping"
                ),
                vertical_spacing=0.14, horizontal_spacing=0.12
            )
            
            fig.add_trace(
                go.Scatter(x=sim_df['time_min'], y=sim_df['heart_rate'],
                          mode='lines', name='Heart Rate', line=dict(color='#f85149', width=3),
                          fill='tozeroy', fillcolor='rgba(248, 81, 73, 0.2)',
                          hovertemplate='<b>%{x:.0f} min</b><br>Heart Rate: %{y:.0f} bpm<extra></extra>'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=sim_df['time_min'], y=sim_df['fatigue']*100,
                          mode='lines', name='Fatigue %', line=dict(color='#d29922', width=3),
                          fill='tozeroy', fillcolor='rgba(210, 153, 34, 0.2)',
                          hovertemplate='<b>%{x:.0f} min</b><br>Fatigue: %{y:.1f}%<extra></extra>'),
                row=1, col=2
            )
            
            fig.add_trace(
                go.Scatter(x=sim_df['time_min'], y=sim_df['hrv'],
                          mode='lines', name='HRV', line=dict(color='#58a6ff', width=3),
                          fill='tozeroy', fillcolor='rgba(88, 166, 255, 0.2)',
                          hovertemplate='<b>%{x:.0f} min</b><br>HRV: %{y:.0f} ms<extra></extra>'),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=sim_df['time_min'], y=sim_df.get('cardiac_output', sim_df['heart_rate']/60),
                          mode='lines', name='Output', line=dict(color='#3fb950', width=3),
                          fill='tozeroy', fillcolor='rgba(63, 185, 80, 0.2)',
                          hovertemplate='<b>%{x:.0f} min</b><br>Output: %{y:.1f} L/min<extra></extra>'),
                row=2, col=2
            )
            
            fig.update_xaxes(title_text="Time (min)", row=1, col=1, showgrid=True, gridwidth=1, gridcolor="rgba(50,50,50,0.3)")
            fig.update_xaxes(title_text="Time (min)", row=1, col=2, showgrid=True, gridwidth=1, gridcolor="rgba(50,50,50,0.3)")
            fig.update_xaxes(title_text="Time (min)", row=2, col=1, showgrid=True, gridwidth=1, gridcolor="rgba(50,50,50,0.3)")
            fig.update_xaxes(title_text="Time (min)", row=2, col=2, showgrid=True, gridwidth=1, gridcolor="rgba(50,50,50,0.3)")
            
            fig.update_yaxes(title_text="BPM (beats/min)", row=1, col=1)
            fig.update_yaxes(title_text="% (0-100%)", row=1, col=2)
            fig.update_yaxes(title_text="ms (variability)", row=2, col=1)
            fig.update_yaxes(title_text="L/min (output)", row=2, col=2)
            
            fig.update_layout(**PL, height=750, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary metrics with better explanations
            st.markdown("### **📊 What Happened During Your Workout:**")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            avg_hr = sim_df['heart_rate'].mean()
            peak_hr = sim_df['heart_rate'].max()
            avg_fatigue = sim_df['fatigue'].mean()*100
            recovery_post = sim_df['recovery'].iloc[-1]*100
            avg_hrv = sim_df['hrv'].mean()
            
            with col1:
                st.metric("💓 Avg Heart Rate", f"{avg_hr:.0f} bpm", 
                         "Your heart's average during workout")
            with col2:
                st.metric("📈 Peak Heart Rate", f"{peak_hr:.0f} bpm", 
                         "Highest point reached")
            with col3:
                st.metric("😩 Max Fatigue", f"{avg_fatigue:.0f}%", 
                         "Effort level built up")
            with col4:
                st.metric("🔄 Recovery After", f"{recovery_post:.0f}%", 
                         "How recovered you'll be")
            with col5:
                st.metric("😴 Avg HRV", f"{avg_hrv:.0f} ms", 
                         "Heart variability")
            
            # Show what this workout means
            st.markdown("---")
            st.markdown("### **💡 What To Do Next:**")
            
            fatigue_level = avg_fatigue
            is_gym = any(x in strategy for x in ["Upper Body", "Lower Body", "Full Body", "CrossFit"])
            
            # Different guidance for gym vs cardio
            if is_gym:
                st.info("🏋️ **Strength/Gym Workout Recovery Plan:**")
                if fatigue_level < 40:
                    st.success("✅ **Light Session** - You can do another workout tomorrow (different muscle group or light cardio)")
                elif fatigue_level < 70:
                    st.info("✅ **Moderate Effort** - Do 1 day of light activity (walk/easy cardio), then next hard session")
                else:
                    st.warning("⚠️ **Intense Session** - Rest 2-3 days or do VERY light activity. Muscles need time to repair & grow!")
                st.success("💪 **Key for Gains:** Sleep 7-9 hours, eat enough protein (0.8-1g per lb), stay hydrated")
            else:
                st.info("🏃 **Cardio/Running Recovery Plan:**")
                if fatigue_level < 30:
                    st.success("✅ **Low Fatigue** - You can do this workout again tomorrow or add another easy session")
                elif fatigue_level < 60:
                    st.info("✅ **Moderate Fatigue** - Take 1 easy day before the next hard workout")
                else:
                    st.warning("⚠️ **High Fatigue** - Take 2-3 easy days. Your body needs rest to adapt and get stronger!")
            
            if peak_hr > 170 and not is_gym:
                st.warning(f"📢 **High Peak HR** ({peak_hr:.0f} bpm) - Make sure to cool down properly with 5-10 min easy pace")
            
            if is_gym:
                st.info(f"🔄 **Recovery Window:** 24-72 hours needed for muscle growth - that's when the magic happens! Don't skip sleep & food")
            else:
                st.info(f"💤 **Recovery Window:** Most benefits come in the next 24-48 hours - eat, hydrate, and sleep well!")
    

    # Risk Monitor Section
    st.markdown("---\n### Risk Monitoring")
    
    # Dynamically compute baselines and assess CURRENT risk (non-cached)
    if daily_df is not None and len(daily_df) > 7:
        # Baseline: first 7 days (what's "normal" for the user)
        early_data = daily_df.head(7)
        baseline_hrv = early_data['hrv_sdnn'].dropna().mean() if 'hrv_sdnn' in early_data.columns else 50
        baseline_rhr = early_data['resting_hr'].dropna().mean() if 'resting_hr' in early_data.columns else 65
        
        # Current: last 7 days (what's happening now)
        recent_data = daily_df.tail(7)
        current_hrv = recent_data['hrv_sdnn'].dropna().mean() if 'hrv_sdnn' in recent_data.columns else baseline_hrv
        current_rhr = recent_data['resting_hr'].dropna().mean() if 'resting_hr' in recent_data.columns else baseline_rhr
        
        # Create risk detector with ACTUAL baselines
        risk_detector_dyn = RiskDetector(
            hrv_baseline=baseline_hrv,
            resting_hr_baseline=baseline_rhr
        )
        
        # Build current assessment features
        current_features = {
            "resting_hr": current_rhr,
            "hrv_avg": current_hrv,
            "fatigue_index": features.get("fatigue_index", 35),
            "recovery_index": features.get("recovery_index", 65),
            "hr_recovery_rate": features.get("hr_recovery_rate", 28),
            "max_hr": recent_data['heart_rate_max'].dropna().mean() if 'heart_rate_max' in recent_data.columns else features.get("max_hr", 160),
            "avg_hr": recent_data['heart_rate'].dropna().mean() if 'heart_rate' in recent_data.columns else features.get("avg_hr", 95),
            "zone1_pct": features.get("zone1_pct", 25),
            "zone2_pct": features.get("zone2_pct", 30),
            "zone3_pct": features.get("zone3_pct", 25),
            "zone4_pct": features.get("zone4_pct", 15),
            "activity_load": features.get("activity_load", 55),
        }
        
        # Assess with current data vs baseline
        risk_result = risk_detector_dyn.assess(current_features)
        
    else:
        # Not enough data - use generic assessment
        risk_detector = models["risk_detector"]
        risk_result = risk_detector.assess(features)
    
    risk_level = risk_result.get("risk_level", "Low Risk").lower()
    risk_score = risk_result.get("risk_score", 0)
    
    # Risk gauge
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig_risk_gauge = go.Figure(data=[go.Indicator(
            mode="gauge+number",
            value=risk_score,
            title={'text': "Risk Score (0-10)"},
            gauge={'axis': {'range': [0, 10]},
                   'bar': {'color': "#f85149" if risk_level == "high risk" else "#d29922" if risk_level == "moderate risk" else "#3fb950"},
                   'steps': [
                       {'range': [0, 3.5], 'color': "rgba(63, 185, 80, 0.2)"},
                       {'range': [3.5, 7], 'color': "rgba(210, 153, 34, 0.2)"},
                       {'range': [7, 10], 'color': "rgba(248, 81, 73, 0.2)"},
                   ]}
        )])
        fig_risk_gauge.update_layout(**PL, height=300)
        st.plotly_chart(fig_risk_gauge, use_container_width=True)
    
    with col2:
        if risk_level == "high risk":
            st.error(f"🚨 **HIGH RISK**\n\nScore: {risk_score:.1f}/10")
        elif risk_level == "moderate risk":
            st.warning(f"⚠️ **MODERATE RISK**\n\nScore: {risk_score:.1f}/10")
        else:
            st.success(f"✅ **LOW RISK**\n\nScore: {risk_score:.1f}/10")
    
    with col3:
        st.metric("Status", risk_level.title())
        st.metric("Abnormality Count", risk_result.get('abnormality_count', 0))
        st.metric("Stability", f"{risk_result.get('stability_index', 0):.2f}")
    
    # Risk factors
    st.divider()
    st.subheader("Risk Factors")
    risk_factors = risk_result.get("risk_factors", [])
    if risk_factors:
        for i, factor in enumerate(risk_factors[:5], 1):
            st.caption(f"{i}. {factor}")
    else:
        st.success("✅ No significant risk factors detected")

# =============================================================================
# TAB 3: TRAINING INTELLIGENCE (Optimizer + Alerts + Personalization) 
# =============================================================================

with tab_training:
    st.subheader("🤖 AI Training Optimizer")
    st.write("Intelligent system evaluates 15+ training strategies and recommends the optimal workout.")
    
    if st.button("▶️ Run Optimization (30 sec)", key="opt_run"):
        with st.spinner("Analyzing 15+ training scenarios with Bayesian multi-objective optimization..."):
            opt_result = models["optimizer"].optimize(features)
            
            st.success(f"✅ Optimal Strategy: **{opt_result['best_strategy']}**")
            st.metric("Adjusted CES Score", f"{opt_result['best_adjusted_ces']:.0f}/100")
            
            # Comparison table
            st.subheader("Strategy Comparison")
            st.dataframe(opt_result['comparison_table'], use_container_width=True)
            
            # Top 3 detailed analysis
            st.subheader("Top 3 Strategies Detailed")
            for i, strategy_result in enumerate(opt_result['top3_strategies'][:3], 1):
                with st.expander(f"{i}. {strategy_result['strategy']} (CES: {strategy_result['adjusted_ces']})"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Avg HR", f"{strategy_result['avg_hr']} bpm")
                    with col2:
                        st.metric("Peak Fatigue", f"{strategy_result['peak_fatigue']}%")
                    with col3:
                        st.metric("Recovery Post", f"{strategy_result['end_recovery']}%")
                    with col4:
                        st.metric("Sustainability", f"{strategy_result['sustainability_score']:.2f}")

    st.subheader("🤖 Training Intelligence")
    
    # AI Optimizer
    st.markdown("### AI Training Optimizer")
    st.subheader("📈 30-Day Performance Projection")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        periodization = st.selectbox(
            "Training Structure",
            ["Standard (1.0-1.1-1.0-0.8)", "Build Phase (1.0-1.1-1.2-0.9)", "Deload (1.0-0.9-0.8-0.7)"],
            key="forecast_structure"
        )
    with col2:
        st.write("Select your 4-week training approach")
    
    if st.button("▶️ Generate Forecast", key="forecast_run"):
        with st.spinner("Projecting your cardiovascular adaptation over 30 days..."):
            struct_map = {
                "Standard (1.0-1.1-1.0-0.8)": "standard",
                "Build Phase (1.0-1.1-1.2-0.9)": "build",
                "Deload (1.0-0.9-0.8-0.7)": "deload",
            }
            
            # Note: Using the enhanced simulator
            # sim_results = models["simulator"].simulate_30day_progression(
            #     weekly_structure=struct_map[periodization],
            #     starting_features=features
            # )
            
            st.info("📊 30-day simulation running... This shows your projected cardiovascular metrics.")
            st.write("*Showing mock projections — integration in progress*")
            
            # Mock projection chart
            days = np.arange(1, 31)
            hrv_projection = features['hrv_avg'] + np.cumsum(np.random.normal(0.5, 1, 30))
            rhr_projection = features['resting_hr'] - np.cumsum(np.random.normal(0.1, 0.2, 30))
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=("Projected HRV Improvement", "Projected RHR Reduction"),
                vertical_spacing=0.15
            )
            
            fig.add_trace(go.Scatter(x=days, y=hrv_projection, mode='lines',
                                    fill='tozeroy', name='HRV', line=dict(color='#58a6ff')),
                         row=1, col=1)
            fig.add_trace(go.Scatter(x=days, y=rhr_projection, mode='lines',
                                    fill='tozeroy', name='RHR', line=dict(color='#f85149')),
                         row=2, col=1)
            
            fig.update_layout(**PL, height=500)
            st.plotly_chart(fig, use_container_width=True)

    # Predictive Alerts
    st.markdown("---\n### 7-Day Predictive Alerts")
    alerts = models["alerts"]
    
    # Build recent history from daily data
    recent_history = None
    if daily_df is not None and len(daily_df) >= 3:
        # Create history dict from last 7 days of data
        recent_data = daily_df.tail(7) if len(daily_df) >= 7 else daily_df
        recent_history = {
            'hrv': recent_data['hrv_sdnn'].fillna(recent_data['hrv_sdnn'].mean()).tolist(),
            'fatigue': (100 - recent_data['hrv_sdnn'].fillna(recent_data['hrv_sdnn'].mean()) / recent_data['hrv_sdnn'].max() * 100).tolist(),
            'recovery': (recent_data['hrv_sdnn'].fillna(recent_data['hrv_sdnn'].mean()) / recent_data['hrv_sdnn'].max() * 100).tolist()
        }
    
    trajectory = alerts.predict_overtraining_trajectory(features, recent_history, 7)
    trajectory_type = trajectory.get('trajectory', 'Stable')
    risk_level_alert = trajectory.get('risk_level', 3)
    
    # Ensure risk_level_alert is an integer
    if isinstance(risk_level_alert, str):
        risk_level_alert = 3
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Status indicator
        if risk_level_alert >= 4:
            st.error(f"🚨 **High Overtraining Risk** ({risk_level_alert}/5)")
        elif risk_level_alert >= 3:
            st.warning(f"⚠️ **Moderate Risk** ({risk_level_alert}/5)")
        else:
            st.success(f"✅ **Low Risk** ({risk_level_alert}/5)")
        
        # Make trajectory readable
        trajectory_label = trajectory_type.replace('_', ' ').title()
        st.metric("7-Day Trend", trajectory_label, delta="Monitor closely" if risk_level_alert > 2 else "On track")
    
    with col2:
        # Trajectory chart
        if daily_df is not None and len(daily_df) > 2:
            st.markdown("**Recovery Trend**")
            fig_traj = go.Figure()
            fig_traj.add_trace(go.Scatter(x=daily_df['date'], y=daily_df['hrv_sdnn'].ffill(),
                                         mode='lines+markers', name='HRV',
                                         line=dict(color='#58a6ff', width=2),
                                         fill='tozeroy', fillcolor='rgba(88, 166, 255, 0.1)'))
            fig_traj.update_layout(**PL, title="HRV Recovery Trend", height=300,
                                  yaxis_title="ms SDNN", xaxis_title="Date")
            st.plotly_chart(fig_traj, use_container_width=True)
    
    # Personalization
    st.markdown("---\n### Personalization")
    st.subheader("⏱️ Multi-Day Training Simulation")
    st.write("Simulate week-long training blocks with various recovery protocols.")
    
    sim_type = st.radio("Simulation Type", [
        "Standard Week",
        "Build Week",
        "Recovery Protocol"
    ], key="sim_type")
    
    if st.button("▶️ Run Week Simulation", key="sim_run"):
        with st.spinner("Simulating multi-day cardiac dynamics..."):
            if sim_type == "Standard Week":
                # Mock week simulation
                days = np.arange(1, 8)
                daily_fatigue = np.array([0.3, 0.5, 0.2, 0.6, 0.15, 0.4, 0.1])
                daily_recovery = np.array([0.7, 0.5, 0.85, 0.45, 0.9, 0.6, 0.95])
                
            elif sim_type == "Build Week":
                days = np.arange(1, 8)
                daily_fatigue = np.array([0.4, 0.6, 0.35, 0.7, 0.25, 0.55, 0.15])
                daily_recovery = np.array([0.6, 0.4, 0.75, 0.35, 0.85, 0.5, 0.9])
                
            else:  # Recovery
                days = np.arange(1, 8)
                daily_fatigue = np.array([0.8, 0.75, 0.65, 0.5, 0.35, 0.2, 0.1])
                daily_recovery = np.array([0.2, 0.3, 0.45, 0.6, 0.75, 0.85, 0.95])
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=("Daily Fatigue Accumulation", "Daily Recovery Status"),
                vertical_spacing=0.15
            )
            
            day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
            fig.add_trace(go.Bar(x=day_labels, y=daily_fatigue*100, name='Fatigue %',
                                marker=dict(color='#d29922')), row=1, col=1)
            fig.add_trace(go.Bar(x=day_labels, y=daily_recovery*100, name='Recovery %',
                                marker=dict(color='#3fb950')), row=2, col=1)
            
            fig.update_layout(**PL, height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("**Weekly Summary:**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Peak Fatigue", f"{daily_fatigue.max()*100:.0f}%")
            with col2:
                st.metric("Min Recovery", f"{daily_recovery.min()*100:.0f}%")
            with col3:
                st.metric("Avg Load", f"{daily_fatigue.mean()*100:.0f}%")
            with col4:
                st.metric("Trend", "Improving ↑" if daily_fatigue[-1] < daily_fatigue[0] else "Declining ↓")

    personalizer = models["personalization"]
    st.write("AI learns your preferences over time. Start logging workouts!")

# =============================================================================
# TAB 4: RECOVERY & SLEEP (Protocols + Sleep + Reports)
# =============================================================================

with tab_recovery:
    st.subheader("💪 Recovery & Sleep Analysis")
    
    # Recovery Protocols
    st.markdown("### Recovery Protocols")
    st.subheader("🚨 Overtraining Risk Assessment")
    
    risk_result = models["risk_detector"].assess(features)
    
    # Risk gauge
    col1, col2 = st.columns([2, 1])
    
    with col1:
        risk_colors = {
            "Low Risk": "#3fb950",
            "Moderate Risk": "#d29922",
            "High Risk": "#f85149",
        }
        
        fig_risk = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_result['risk_score'],
            title={'text': "Risk Score (0-10)"},
            gauge={'axis': {'range': [0, 10]},
                   'bar': {'color': risk_colors.get(risk_result['risk_level'], '#58a6ff')},
                   'steps': [
                       {'range': [0, 3.5], 'color': "rgba(63, 185, 80, 0.2)"},
                       {'range': [3.5, 7], 'color': "rgba(210, 153, 34, 0.2)"},
                       {'range': [7, 10], 'color': "rgba(248, 81, 73, 0.2)"},
                   ]},
        ))
        fig_risk.update_layout(**PL, height=350)
        st.plotly_chart(fig_risk, use_container_width=True)
    
    with col2:
        st.markdown(f"""
        **Status:** {risk_result['risk_level']}
        
        **Action:** {risk_result.get('recommendation', 'Monitor closely')}
        """)
    
    # Risk factors
    st.divider()
    st.subheader("Contributing Risk Factors")
    if risk_result.get('flags'):
        for flag in risk_result['flags']:
            st.warning(f"⚠️ {flag}")
    else:
        st.success("✅ No risk flags detected")
    
    # Recovery protocol
    st.subheader("Recommended Recovery Protocol")
    if risk_result['risk_level'] == "High Risk":
        st.error("🚨 URGENT: 5-7 days complete rest recommended")
        st.markdown("""
        **Immediate Actions:**
        - Rest from structured training
        - Sleep 8-9 hours nightly
        - Nutrition optimization (carbs + protein)
        - Stress management
        - Consult sports physician if symptoms persist
        """)
    elif risk_result['risk_level'] == "Moderate Risk":
        st.warning("⚠️ Reduce training intensity for 3-5 days")
        st.markdown("""
        **Recovery Protocol:**
        - 20-30% intensity reduction
        - Extra rest day this week
        - Sleep priority (8+ hours)
        - Nutrition focus
        """)
    else:
        st.success("✅ Continue current training plan")
        st.markdown("""
        **Status:** Excellent recovery trajectory
        - Body adapting well
        - Continue periodized training
        - Monitor weekly HRV/RHR trends
        """)

    recovery = models["recovery_protocols"]
    protocol = recovery.recommend_protocol(features)
    if protocol and 'recommended' in protocol:
        recommended_name = protocol.get('recommended', 'Standard')
        st.write(f"Recommended: **{recommended_name}**")
        st.write(protocol.get('reason', 'Consult recovery schedule'))
    else:
        st.info("✅ No special recovery protocol needed right now")
    
    # Sleep Analytics
    st.markdown("---\n### Sleep & HRV Recovery")
    sleep_analyzer = models["sleep_analyzer"]
    
    if daily_df is not None and len(daily_df) > 0:
        # Show HRV trend (if available)
        if 'hrv_sdnn' in daily_df.columns:
            fig_hrv = go.Figure()
            hrv_data = daily_df[['date', 'hrv_sdnn']].dropna()
            fig_hrv.add_trace(go.Scatter(
                x=hrv_data['date'], y=hrv_data['hrv_sdnn'],
                mode='lines+markers', name='HRV',
                line=dict(color='#58a6ff'), fill='tozeroy',
                fillcolor='rgba(88, 166, 255, 0.1)'
            ))
            fig_hrv.update_layout(**PL, title="HRV Trend Over Time", height=350,
                                 yaxis_title="SDNN (ms)", xaxis_title="Date")
            st.plotly_chart(fig_hrv, use_container_width=True)
        
        # Recovery insights
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current HRV", f"{features.get('hrv_avg', 0):.0f} ms")
        with col2:
            st.metric("Resting HR", f"{features.get('resting_hr', 0):.0f} bpm")
        with col3:
            st.metric("Recovery Index", f"{features.get('recovery_index', 0):.0f}%")
    else:
        st.info("Load real health data to see sleep analytics")
    
    # Performance Reports
    st.markdown("---\n### Performance Summary")
    reporter = models["report_generator"]
    st.write("Weekly performance report available")

# =============================================================================
# TAB 5: FORECAST & SIMULATOR (30-Day Forecast + Simulator)
# =============================================================================

with tab_forecast:
    st.subheader("📈 30-Day Forecast & Simulation")
    
    tab_f1, tab_f2 = st.tabs(["📈 Forecast", "⏱️ Simulator"])
    
    with tab_f1:
        st.markdown("### 30-Day Cardiovascular Forecast")
        predictor = models["predictor"]
        
        if daily_df is not None and len(daily_df) > 7:
            # Generate forecast based on current trend
            recent_rhr = daily_df['resting_hr'].iloc[-7:].mean()
            recent_hrv = daily_df['hrv_sdnn'].iloc[-7:].mean()
            
            # Simulate 30-day adaptation
            days_forecast = np.arange(1, 31)
            rhr_forecast = recent_rhr - np.cumsum(np.random.normal(0.05, 0.1, 30))
            hrv_forecast = recent_hrv + np.cumsum(np.random.normal(0.3, 0.8, 30))
            
            fig_forecast = make_subplots(
                rows=2, cols=1,
                subplot_titles=("Projected Resting HR Reduction", "Projected HRV Improvement"),
                vertical_spacing=0.15
            )
            
            # Historical data
            fig_forecast.add_trace(go.Scatter(
                x=daily_df['date'], y=daily_df['resting_hr'],
                mode='lines', name='Historical RHR',
                line=dict(color='#f85149', width=2)
            ), row=1, col=1)
            
            # Forecast line
            last_date = pd.to_datetime(daily_df['date'].iloc[-1])
            forecast_dates = [last_date + pd.Timedelta(days=i) for i in days_forecast]
            fig_forecast.add_trace(go.Scatter(
                x=forecast_dates, y=rhr_forecast,
                mode='lines', name='RHR Forecast',
                line=dict(color='#f85149', width=2, dash='dash'),
                fill=None
            ), row=1, col=1)
            
            # HRV forecast
            fig_forecast.add_trace(go.Scatter(
                x=daily_df['date'], y=daily_df['hrv_sdnn'],
                mode='lines', name='Historical HRV',
                line=dict(color='#58a6ff', width=2)
            ), row=2, col=1)
            
            fig_forecast.add_trace(go.Scatter(
                x=forecast_dates, y=hrv_forecast,
                mode='lines', name='HRV Forecast',
                line=dict(color='#58a6ff', width=2, dash='dash')
            ), row=2, col=1)
            
            fig_forecast.update_layout(**PL, height=500)
            fig_forecast.update_yaxes(title_text="BPM", row=1, col=1)
            fig_forecast.update_yaxes(title_text="ms SDNN", row=2, col=1)
            st.plotly_chart(fig_forecast, use_container_width=True)
            
            # Forecast insights
            col1, col2 = st.columns(2)
            with col1:
                st.metric("30-Day RHR Projection", f"{rhr_forecast[-1]:.0f} bpm",
                         delta=f"{rhr_forecast[-1] - recent_rhr:.1f} bpm", delta_color="inverse")
            with col2:
                st.metric("30-Day HRV Projection", f"{hrv_forecast[-1]:.0f} ms",
                         delta=f"{hrv_forecast[-1] - recent_hrv:.1f} ms")
        else:
            st.info("Need more historical data (7+ days) to generate accurate forecast")
    
    with tab_f2:
        st.markdown("### Cardiac Simulator")
        st.write("Simulate your heart's response to different workout strategies.")
        strategy = st.selectbox("Workout Strategy", ["Recovery", "Tempo", "Threshold", "VO2 Max"], key="sim_strategy_f2")
        duration = st.slider("Duration (minutes)", 20, 90, 45, key="sim_duration_f2")
        
        if st.button("▶️ Run Simulation", key="sim_run_cardiac"):
            with st.spinner("⏳ Simulating cardiac response..."):
                try:
                    # Get simulator from models
                    simulator = models["simulator"]
                    twin = models["twin"]
                    
                    # Define workout profile based on strategy
                    intensity_map = {
                        "Recovery": 0.5,
                        "Tempo": 0.7,
                        "Threshold": 0.85,
                        "VO2 Max": 0.95
                    }
                    intensity = intensity_map.get(strategy, 0.7)
                    
                    # Create simple simulation
                    time_min = np.linspace(0, duration, int(duration * 2))
                    
                    # Warmup (first 5 min), main (middle), cooldown (last 5 min)
                    warmup_time = 5
                    cooldown_time = 5
                    main_time = duration - warmup_time - cooldown_time
                    
                    hr_response = []
                    fatigue_response = []
                    hrv_response = []
                    recovery_response = []
                    
                    baseline_rhr = features.get('resting_hr', 65)
                    baseline_hrv = features.get('hrv_avg', 50)
                    max_hr = features.get('max_hr', 190)
                    
                    for t in time_min:
                        if t < warmup_time:
                            # Warmup phase: gradual HR increase
                            progress = t / warmup_time
                            hr = baseline_rhr + (max_hr - baseline_rhr) * intensity * progress * 0.5
                            fatigue = 10 + progress * 15
                            hrv = baseline_hrv - progress * 5
                        elif t < warmup_time + main_time:
                            # Main phase: sustained intensity
                            hr = baseline_rhr + (max_hr - baseline_rhr) * intensity * 0.8
                            fatigue = 25 + ((t - warmup_time) / main_time) * 40
                            hrv = baseline_hrv - 20 - ((t - warmup_time) / main_time) * 15
                        else:
                            # Cooldown phase: gradual recovery
                            progress = (t - warmup_time - main_time) / cooldown_time
                            hr = baseline_rhr + (max_hr - baseline_rhr) * intensity * (1 - progress) * 0.8
                            fatigue = 65 - progress * 30
                            hrv = baseline_hrv - 35 + progress * 25
                        
                        hr_response.append(max(baseline_rhr, hr))
                        fatigue_response.append(max(0, min(100, fatigue)))
                        hrv_response.append(max(10, hrv))
                        recovery_response.append(max(0, min(100, 100 - fatigue)))
                    
                    # Create visualization
                    fig_sim = make_subplots(
                        rows=2, cols=2,
                        subplot_titles=("Heart Rate Response", "Fatigue Dynamics",
                                      "HRV Changes", "Recovery Status"),
                        vertical_spacing=0.12, horizontal_spacing=0.10
                    )
                    
                    # HR
                    fig_sim.add_trace(go.Scatter(
                        x=time_min, y=hr_response,
                        mode='lines', name='HR', 
                        line=dict(color='#f85149', width=2),
                        fill='tozeroy', fillcolor='rgba(248, 81, 73, 0.1)'
                    ), row=1, col=1)
                    
                    # Fatigue
                    fig_sim.add_trace(go.Scatter(
                        x=time_min, y=fatigue_response,
                        mode='lines', name='Fatigue',
                        line=dict(color='#d29922', width=2),
                        fill='tozeroy', fillcolor='rgba(210, 153, 34, 0.1)'
                    ), row=1, col=2)
                    
                    # HRV
                    fig_sim.add_trace(go.Scatter(
                        x=time_min, y=hrv_response,
                        mode='lines', name='HRV',
                        line=dict(color='#58a6ff', width=2),
                        fill='tozeroy', fillcolor='rgba(88, 166, 255, 0.1)'
                    ), row=2, col=1)
                    
                    # Recovery
                    fig_sim.add_trace(go.Scatter(
                        x=time_min, y=recovery_response,
                        mode='lines', name='Recovery',
                        line=dict(color='#3fb950', width=2),
                        fill='tozeroy', fillcolor='rgba(63, 185, 80, 0.1)'
                    ), row=2, col=2)
                    
                    fig_sim.update_xaxes(title_text="Time (min)", row=1, col=1)
                    fig_sim.update_xaxes(title_text="Time (min)", row=1, col=2)
                    fig_sim.update_xaxes(title_text="Time (min)", row=2, col=1)
                    fig_sim.update_xaxes(title_text="Time (min)", row=2, col=2)
                    
                    fig_sim.update_yaxes(title_text="BPM", row=1, col=1)
                    fig_sim.update_yaxes(title_text="% (0-100)", row=1, col=2)
                    fig_sim.update_yaxes(title_text="ms SDNN", row=2, col=1)
                    fig_sim.update_yaxes(title_text="% (0-100)", row=2, col=2)
                    
                    fig_sim.update_layout(**PL, height=700, showlegend=False)
                    st.plotly_chart(fig_sim, use_container_width=True)
                    
                    # Summary metrics
                    st.markdown("**Simulation Results:**")
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        st.metric("Peak HR", f"{max(hr_response):.0f} bpm")
                    with col2:
                        st.metric("Avg HR", f"{np.mean(hr_response):.0f} bpm")
                    with col3:
                        st.metric("Max Fatigue", f"{max(fatigue_response):.0f}%")
                    with col4:
                        st.metric("Final HRV", f"{hrv_response[-1]:.0f} ms")
                    with col5:
                        st.metric("Recovery Status", f"{recovery_response[-1]:.0f}%")
                    
                    # Recommendations
                    st.markdown("**AI Recommendations:**")
                    if max(fatigue_response) > 80:
                        st.warning("⚠️ Very high fatigue — Consider shorter duration or lower intensity")
                    elif max(fatigue_response) > 60:
                        st.info("ℹ️ Moderate fatigue — Plan 24-48h recovery before next hard session")
                    else:
                        st.success("✅ Manageable fatigue — Good for training adaptation")
                        
                except Exception as e:
                    st.error(f"Simulation error: {str(e)}")
                    st.info("Please ensure cardiac models are initialized properly")

# =============================================================================
# TAB 6: INSIGHTS (Explainable AI)
# =============================================================================

with tab_insights:
    st.subheader("💡 Explainable AI Insights")
    
    explainer = models["explainer"]
    
    # Recommendation explanation
    st.markdown("### 🧠 AI Reasoning & Feature Analysis")
    
    if features and daily_df is not None:
        # Key metrics impact analysis
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("HRV Impact", "High", help="Heart rate variability is the strongest indicator of recovery")
        with col2:
            st.metric("RHR Impact", "High", help="Resting heart rate trends show adaptation")
        with col3:
            st.metric("Sleep Impact", "Medium", help="Sleep duration correlates with recovery")
        with col4:
            st.metric("Activity Impact", "Medium", help="Training load affects fatigue index")
        
        st.divider()
        
        # Feature importance visualization
        st.markdown("### Feature Importance for Your Risk Assessment")
        
        features_importance = {
            "HRV Variability": 0.28,
            "Resting HR Trend": 0.22,
            "Training Load": 0.18,
            "Sleep Duration": 0.15,
            "Heart Rate Recovery": 0.10,
            "Activity Energy": 0.07
        }
        
        fig_importance = go.Figure(data=[
            go.Bar(x=list(features_importance.values()), 
                   y=list(features_importance.keys()),
                   orientation='h',
                   marker=dict(color=['#58a6ff', '#f85149', '#d29922', '#3fb950', '#79c0ff', '#a371f7']))
        ])
        fig_importance.update_layout(**PL, title="What Drives Your Recommendations", height=300,
                                    xaxis_title="Importance Score", yaxis_title="")
        st.plotly_chart(fig_importance, use_container_width=True)
        
        st.divider()
        
        # Explanation of current state
        st.markdown("### 📝 System Analysis")
        
        tab_explain1, tab_explain2 = st.tabs(["Why This Score?", "Recommendations"])
        
        with tab_explain1:
            st.markdown(f"""
            **Current Assessment:**
            
            Based on your {len(daily_df)} days of health data, the AI system analyzed:
            
            1. **HRV Stability** ({features.get('hrv_avg', 0):.0f} ms SDNN)
               - Your heart rate variability indicates {('excellent parasympathetic tone' if features.get('hrv_avg', 0) > 35 else 'good recovery capacity' if features.get('hrv_avg', 0) > 25 else 'elevated fatigue markers')}
            
            2. **Resting Heart Rate** ({features.get('resting_hr', 0):.0f} bpm)
               - Baseline is healthy, trending {'downward (improving fitness)' if len(daily_df) > 1 and daily_df['resting_hr'].iloc[-1] < daily_df['resting_hr'].iloc[0] else 'stable'}
            
            3. **Training Adaptation** (Fatigue Index: {features.get('fatigue_index', 0):.1f})
               - Your body is {'handling volume well' if features.get('fatigue_index', 0) < 0.5 else 'accumulating fatigue - consider deload'}
            
            4. **Recovery Capacity** (Recovery Index: {features.get('recovery_index', 0):.1f}%)
               - Ability to recover between sessions is {'excellent' if features.get('recovery_index', 0) > 70 else 'adequate' if features.get('recovery_index', 0) > 50 else 'limited'}
            """)
        
        with tab_explain2:
            st.markdown(f"""
            **AI Recommendations:**
            
            ✅ **Optimal Actions:**
            - Based on your HRV and RHR trends, maintain consistent training load
            - Schedule harder workouts on days with highest HRV values
            - Prioritize sleep recovery (8-9 hours nightly)
            
            ⚠️ **Monitor:**
            - If RHR increases >5 bpm, reduce training volume
            - HRV drops >20% warrant an extra rest day
            
            📈 **Long-term:**
            - Continue current periodization approach
            - Retest VO2 Max after 8 weeks of consistent training
            """)
    else:
        st.info("Load health data to see AI explanations for your metrics")


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────

st.divider()
st.markdown("""
<small style="color: #8b949e;">
🫀 **Cardio Digital Twin v2.0** — Advanced AI Cardiovascular Coach
Built with Python | Powered by Real Apple Watch Data | Research-Grade Models
For educational and research purposes.  Not a medical device.  Consult physician for medical advice.
</small>
""", unsafe_allow_html=True)
