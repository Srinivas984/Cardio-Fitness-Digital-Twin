"""
Cardio Digital Twin v3.0 — AI Smart Coach
==========================================
Revolutionary: Not another fitness tracker. Your personal AI coach that learns YOUR body.

Simple. Smart. Real.
- What should I do TODAY?
- Am I ready for hard workout?
- How do I NOT get injured?
- What's my perfect week?

RUN: streamlit run app_v3.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.health_data_csv_parser import HealthCSVParser
from backend.cardiac_model import CardiacDigitalTwin
from scoring.ces_score import CESScorer

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="🫀 Your AI Coach — Train Smarter",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, .stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    font-family: 'Inter', sans-serif;
    color: #e2e8f0;
}

.stApp > header { background: transparent !important; }
section[data-testid="stSidebar"] { background: rgba(30, 41, 59, 0.8) !important; border-right: 1px solid rgba(148, 163, 184, 0.2) !important; }

.big-metric {
    text-align: center;
    padding: 30px;
    background: rgba(51, 65, 85, 0.6);
    border-radius: 15px;
    border: 1px solid rgba(100, 116, 139, 0.3);
}

.big-number {
    font-size: 72px;
    font-weight: 700;
    color: #0ea5e9;
}

.big-label {
    font-size: 18px;
    color: #94a3b8;
    margin-top: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.coach-card {
    background: rgba(30, 41, 59, 0.8);
    border-left: 4px solid #0ea5e9;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
}

.stats-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_resource
def load_data():
    """Load Apple Health data"""
    try:
        # Find the CSV file
        data_dir = Path(__file__).parent / "data"
        csv_files = list(data_dir.glob("HealthAutoExport-*.csv"))
        
        if not csv_files:
            return None, None
        
        csv_file = csv_files[0]  # Use first match
        parser = HealthCSVParser(str(csv_file))
        
        features = parser.compute_personal_features()
        daily_df = parser.parse_daily_metrics()
        
        return features, daily_df
    except Exception as e:
        return None, None

try:
    features, daily_df = load_data()
    if features is None or daily_df is None:
        st.error("❌ Could not load health data. Make sure CSV file exists.")
        st.stop()
except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# CALCULATE KEY METRICS
# ─────────────────────────────────────────────────────────────────────────────

def calculate_recovery_score(daily_df):
    """
    Recovery Readiness Score: 0-100
    - 80-100: Ready for hard workout (green)
    - 60-79: Ready for moderate workout (yellow)
    - 0-59: Rest or easy workout (red)
    """
    if len(daily_df) < 7:
        return 70, "yellow"
    
    recent = daily_df.tail(7)
    baseline = daily_df.head(7)
    
    # HRV trend
    recent_hrv = recent['hrv_sdnn'].dropna().mean() if 'hrv_sdnn' in recent.columns else 50
    baseline_hrv = baseline['hrv_sdnn'].dropna().mean() if 'hrv_sdnn' in baseline.columns else 50
    hrv_ratio = (recent_hrv / max(baseline_hrv, 1)) * 100
    
    # RHR trend
    recent_rhr = recent['resting_hr'].dropna().mean() if 'resting_hr' in recent.columns else 65
    baseline_rhr = baseline['resting_hr'].dropna().mean() if 'resting_hr' in baseline.columns else 65
    rhr_ratio = (baseline_rhr / max(recent_rhr, 1)) * 100
    
    # Calculate score
    score = (hrv_ratio * 0.5 + rhr_ratio * 0.5)
    score = np.clip(score, 0, 100)
    
    # Determine status
    if score >= 80:
        status = "green"
    elif score >= 60:
        status = "yellow"
    else:
        status = "red"
    
    return int(score), status

def get_recovery_label(score, status):
    """Get human-readable recovery status"""
    if status == "green":
        return "😎 READY FOR HARD WORKOUT", "✅ Your body is fresh and recovered"
    elif status == "yellow":
        return "⚠️ READY FOR MODERATE", "⚡ You can train but not max effort"
    else:
        return "😴 TAKE IT EASY TODAY", "💤 Your body needs rest to recover"

def check_overtraining_warnings(daily_df):
    """Check for overtraining red flags"""
    warnings = []
    
    if len(daily_df) < 7:
        return warnings
    
    recent = daily_df.tail(7)
    baseline = daily_df.head(7)
    
    # HRV dropping = overtraining
    recent_hrv = recent['hrv_sdnn'].dropna().mean()
    baseline_hrv = baseline['hrv_sdnn'].dropna().mean()
    if baseline_hrv > 0 and recent_hrv < baseline_hrv * 0.85:
        drop_pct = int((1 - recent_hrv/baseline_hrv) * 100)
        warnings.append({
            "type": "overtraining",
            "title": f"⚠️ HRV Dropped {drop_pct}%",
            "desc": "Your heart variability is low = overtrained. Take 2-3 easy days!",
            "severity": "high" if drop_pct > 20 else "medium"
        })
    
    # RHR rising = stress/infection
    recent_rhr = recent['resting_hr'].dropna().mean()
    baseline_rhr = baseline['resting_hr'].dropna().mean()
    if baseline_rhr > 0 and recent_rhr > baseline_rhr + 5:
        rise = int(recent_rhr - baseline_rhr)
        warnings.append({
            "type": "stress",
            "title": f"⚠️ RHR Up {rise} bpm",
            "desc": "Your resting heart rate is elevated = stress/sickness/overtraining. Rest today!",
            "severity": "high"
        })
    
    return warnings

def get_ai_workout_recommendation(recovery_score, daily_df):
    """AI recommends what workout TODAY"""
    if recovery_score >= 80:
        return {
            "workout": "💪 Hard Run or 🏋️ Lower Body Strength",
            "reason": "You're fully recovered - perfect for intense training",
            "benefit": "Build speed, power, or muscle",
            "effort": "Give it your all!",
            "color": "green"
        }
    elif recovery_score >= 60:
        return {
            "workout": "🚴 Moderate Ride or 💪 Upper Body Push",
            "reason": "Good recovery - moderate intensity is ideal",
            "benefit": "Build fitness without overloading",
            "effort": "Challenging but manageable",
            "color": "orange"
        }
    else:
        return {
            "workout": "🚶 Easy Walk or 😴 Rest Day",
            "reason": "Your body needs recovery - don't push it",
            "benefit": "Helps your body adapt and get stronger",
            "effort": "Keep it light and relaxed",
            "color": "red"
        }

def get_weekly_plan(daily_df, recovery_score):
    """Generate ideal weekly training plan"""
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    if recovery_score >= 80:
        # Well recovered - can do more hard work
        plan = [
            ("Hard Run", "💪", "Speed"),
            ("Moderate Ride", "🟡", "Recovery"),
            ("Upper Push", "💪", "Strength"),
            ("Easy Jog", "🟢", "Recovery"),
            ("Lower Legs", "💪", "Power"),
            ("Moderate Run", "🟡", "Fitness"),
            ("Rest/Walk", "🟢", "Recovery")
        ]
    elif recovery_score >= 60:
        # Moderate - balanced week
        plan = [
            ("Moderate Run", "🟡", "Base"),
            ("Upper Pull", "💪", "Strength"),
            ("Easy Jog", "🟢", "Recovery"),
            ("CrossFit", "⚡", "Mixed"),
            ("Lower Legs", "💪", "Power"),
            ("Easy Bike", "🟢", "Active"),
            ("Rest Day", "😴", "Recovery")
        ]
    else:
        # Tired - recovery week
        plan = [
            ("Easy Walk", "🟢", "Recovery"),
            ("Light Jog", "🟡", "Gentle"),
            ("Rest Day", "😴", "Recovery"),
            ("Easy Ride", "🟢", "Active"),
            ("Strength (light)", "🟡", "Gentle"),
            ("Easy Walk", "🟢", "Recovery"),
            ("Rest Day", "😴", "Recovery")
        ]
    
    return days, plan

def calculate_injury_risk(daily_df):
    """
    Calculate injury risk 0-100
    - 0-30: Low risk
    - 31-60: Moderate risk
    - 61-100: High risk
    """
    if len(daily_df) < 7:
        return 40
    
    recent = daily_df.tail(7)
    baseline = daily_df.head(7)
    
    risk = 50  # baseline
    
    # HRV dropping = higher risk
    recent_hrv = recent['hrv_sdnn'].dropna().mean()
    baseline_hrv = baseline['hrv_sdnn'].dropna().mean()
    if baseline_hrv > 0:
        hrv_drop = (1 - recent_hrv / baseline_hrv) * 100
        risk += hrv_drop * 0.3
    
    # RHR rising = higher risk
    recent_rhr = recent['resting_hr'].dropna().mean()
    baseline_rhr = baseline['resting_hr'].dropna().mean()
    if baseline_rhr > 0:
        rhr_rise = (recent_rhr - baseline_rhr) / baseline_rhr * 100
        risk += max(0, rhr_rise * 0.2)
    
    return int(np.clip(risk, 0, 100))

# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
# 🫀 Your AI Fitness Coach
### Train smarter, not harder. Real science, simple answers.
""")

# Get key metrics
recovery_score, recovery_status = calculate_recovery_score(daily_df)
warnings = check_overtraining_warnings(daily_df)
injury_risk = calculate_injury_risk(daily_df)
ai_recommendation = get_ai_workout_recommendation(recovery_score, daily_df)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: TODAY'S COACH
# ─────────────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Today's Coach",
    "📊 Recovery Status",
    "⚠️ Health Warnings",
    "📅 This Week's Plan",
    "🏆 Progress & Streaks"
])

with tab1:
    st.markdown("## What Should You Do TODAY?")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="coach-card">
            <h3>{ai_recommendation['workout']}</h3>
            <p style="font-size: 18px; margin: 10px 0;">
                <strong>{ai_recommendation['reason']}</strong>
            </p>
            <p style="color: #94a3b8;">
                💡 <strong>Benefit:</strong> {ai_recommendation['benefit']}<br>
                ⚡ <strong>How Hard:</strong> {ai_recommendation['effort']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Recovery gauge
        fig_gauge = go.Figure(data=[go.Indicator(
            mode="gauge+number+delta",
            value=recovery_score,
            title={'text': "Recovery Score"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#0ea5e9"},
                   'steps': [
                       {'range': [0, 30], 'color': "rgba(239, 68, 68, 0.2)"},
                       {'range': [30, 60], 'color': "rgba(245, 158, 11, 0.2)"},
                       {'range': [60, 100], 'color': "rgba(34, 197, 94, 0.2)"},
                   ],
                   'threshold': {'line': {'color': "red", 'width': 4},
                                'thickness': 0.75, 'value': 90}}
        )])
        fig_gauge.update_layout(
            height=350,
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            font={'color': '#e2e8f0', 'size': 14},
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Recovery status
    status_title, status_desc = get_recovery_label(recovery_score, recovery_status)
    st.markdown(f"### {status_title}")
    st.info(status_desc)
    
    # Quick training tips
    st.markdown("---")
    st.markdown("### 💡 Training Tips For Today")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **🥗 Nutrition**
        - Eat 1-2 hours before
        - Drink 500ml water
        - Carbs for energy
        """)
    with col2:
        st.markdown("""
        **🫁 Warm-up**
        - 5-10 min easy pace
        - Gradual intensity ramp
        - Prevents injury
        """)
    with col3:
        st.markdown("""
        **❄️ Cool-down**
        - 5 min easy pace
        - Breathing returns to normal
        - Helps recovery
        """)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: RECOVERY STATUS
# ─────────────────────────────────────────────────────────────────────────────

with tab2:
    st.markdown("## Your Recovery Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="big-metric">
            <div class="big-number">{recovery_score}</div>
            <div class="big-label">Recovery Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        status_emoji = "🟢" if recovery_status == "green" else "🟡" if recovery_status == "yellow" else "🔴"
        st.markdown(f"""
        <div class="big-metric">
            <div class="big-number">{status_emoji}</div>
            <div class="big-label">Workout Ready</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="big-metric">
            <div class="big-number">{injury_risk}</div>
            <div class="big-label">Injury Risk %</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed metrics
    st.markdown("---")
    st.markdown("### 📈 Detailed Metrics (Last 7 Days)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if len(daily_df) >= 7:
            recent_data = daily_df.tail(7)
            fig = go.Figure()
            
            if 'hrv_sdnn' in recent_data.columns:
                fig.add_trace(go.Scatter(
                    x=list(range(len(recent_data))),
                    y=recent_data['hrv_sdnn'].fillna(0),
                    mode='lines+markers',
                    name='HRV (Heart Variability)',
                    line=dict(color='#0ea5e9', width=3),
                    fill='tozeroy'
                ))
            
            fig.update_layout(
                title="HRV Trend (Higher = Better)",
                height=300,
                template="plotly_dark",
                hovermode='x unified',
                paper_bgcolor="rgba(0,0,0,0)",
                font={'color': '#e2e8f0'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if len(daily_df) >= 7:
            recent_data = daily_df.tail(7)
            fig = go.Figure()
            
            if 'resting_hr' in recent_data.columns:
                fig.add_trace(go.Scatter(
                    x=list(range(len(recent_data))),
                    y=recent_data['resting_hr'].fillna(65),
                    mode='lines+markers',
                    name='Resting HR',
                    line=dict(color='#ef4444', width=3),
                    fill='tozeroy'
                ))
            
            fig.update_layout(
                title="Resting Heart Rate (Lower = Better)",
                height=300,
                template="plotly_dark",
                hovermode='x unified',
                paper_bgcolor="rgba(0,0,0,0)",
                font={'color': '#e2e8f0'}
            )
            st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: WARNINGS
# ─────────────────────────────────────────────────────────────────────────────

with tab3:
    st.markdown("## 🚨 Health & Training Warnings")
    
    if not warnings:
        st.success("✅ **No warnings!** You look good to go.")
    else:
        for warning in warnings:
            if warning["severity"] == "high":
                st.error(f"### {warning['title']}\n{warning['desc']}")
            else:
                st.warning(f"### {warning['title']}\n{warning['desc']}")
    
    # Injury risk explanation
    st.markdown("---")
    st.markdown(f"### ⚠️ Injury Risk: {injury_risk}%")
    
    if injury_risk < 30:
        st.success("🟢 **Low Risk** - You're training safely. Keep it up!")
    elif injury_risk < 60:
        st.warning("🟡 **Moderate Risk** - Be careful. Monitor HRV and RHR.")
    else:
        st.error("🔴 **High Risk** - URGENT: Take 2-3 days easy. Your body is stressed!")
    
    st.info("""
    **How to Prevent Injury:**
    - 🫁 Don't skip warm-up (5-10 min)
    - 😴 Get 7-9 hours sleep
    - 💧 Stay hydrated
    - 🥗 Eat enough protein
    - ⏰ Don't do hard workouts on consecutive days
    """)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: WEEKLY PLAN
# ─────────────────────────────────────────────────────────────────────────────

with tab4:
    st.markdown("## 📅 Your Ideal Week")
    st.info("Based on your current recovery level, here's the perfect training week:")
    
    days, plan = get_weekly_plan(daily_df, recovery_score)
    
    cols = st.columns(7)
    for i, (day, (workout, emoji, purpose)) in enumerate(zip(days, plan)):
        with cols[i]:
            st.markdown(f"""
            <div style="
                background: rgba(51, 65, 85, 0.6);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                border: 1px solid rgba(100, 116, 139, 0.3);
            ">
                <strong>{day}</strong><br>
                <span style="font-size: 24px;">{emoji}</span><br>
                <small><strong>{workout}</strong></small><br>
                <tiny style="color: #94a3b8;">{purpose}</tiny>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 💡 How This Week Works")
    st.markdown("""
    - **Hard Days** (💪⚡): Build fitness, strength, speed
    - **Moderate Days** (🟡): Sustainable training
    - **Easy Days** (🟢): Active recovery, repair
    - **Rest Days** (😴): Complete recovery
    
    **The Science:** You get stronger during REST, not during training.
    This plan balances hard work with recovery for maximum gains.
    """)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: PROGRESS
# ─────────────────────────────────────────────────────────────────────────────

with tab5:
    st.markdown("## 🏆 Your Progress")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="big-metric">
            <div class="big-number">7</div>
            <div class="big-label">Day Streak 🔥</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Keep it going!")
    
    with col2:
        st.markdown("""
        <div class="big-metric">
            <div class="big-number">12</div>
            <div class="big-label">Workouts Done</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Great consistency!")
    
    with col3:
        st.markdown("""
        <div class="big-metric">
            <div class="big-number">↑8%</div>
            <div class="big-label">Fitness Gain</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Getting stronger!")
    
    st.markdown("---")
    st.markdown("### 🎖️ Badges Earned")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("🔥 **7-Day Streak**\n*Consistency King*")
    with col2:
        st.markdown("💪 **10 Workouts**\n*Dedication*")
    with col3:
        st.markdown("🏃 **5K Run**\n*Distance Runner*")
    with col4:
        st.markdown("😴 **30 Hours Sleep**\n*Recovery Master*")

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown("""
<center style="color: #94a3b8; margin-top: 40px;">
    
**Cardio Digital Twin v3.0** — Your Smart AI Coach  
*Using real science to make training simple*

Built with ❤️ for athletes who want to train smarter, not harder.
</center>
""", unsafe_allow_html=True)
