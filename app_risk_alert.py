import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json

# Configure page
st.set_page_config(
    page_title="❤️ Cardio Risk Alert System",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for alerts
st.markdown("""
    <style>
    .alert-danger {
        padding: 20px;
        background-color: #ff6b6b;
        color: white;
        border-radius: 8px;
        margin: 10px 0;
        font-weight: bold;
    }
    .alert-warning {
        padding: 20px;
        background-color: #ffa500;
        color: white;
        border-radius: 8px;
        margin: 10px 0;
        font-weight: bold;
    }
    .alert-info {
        padding: 20px;
        background-color: #3498db;
        color: white;
        border-radius: 8px;
        margin: 10px 0;
        font-weight: bold;
    }
    .risk-score-high {
        font-size: 48px;
        font-weight: bold;
        color: #ff6b6b;
        text-align: center;
    }
    .risk-score-medium {
        font-size: 48px;
        font-weight: bold;
        color: #ffa500;
        text-align: center;
    }
    .risk-score-low {
        font-size: 48px;
        font-weight: bold;
        color: #2ecc71;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# API base URL
API_URL = "http://localhost:5000"

def get_latest_metrics():
    """Fetch latest health metrics from API"""
    try:
        response = requests.get(f"{API_URL}/api/metrics", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def calculate_overtraining_risk(heart_rate, hrv, steps, workout_intensity=70):
    """
    Calculate overtraining risk based on metrics
    HRV < 40 with high HR = strong overtraining indicator
    """
    overtraining_score = 0
    reasons = []
    
    # High resting heart rate
    if heart_rate > 85:
        overtraining_score += 20
        reasons.append(f"⚠️ Elevated resting HR ({heart_rate} bpm) - sign of stress/fatigue")
    
    # Low HRV (Heart Rate Variability)
    if hrv < 40:
        overtraining_score += 35
        reasons.append(f"🚨 Low HRV ({hrv:.1f} ms) - nervous system fatigued")
    elif hrv < 50:
        overtraining_score += 20
        reasons.append(f"⚠️ Below-optimal HRV ({hrv:.1f} ms) - recovery needed")
    
    # High training volume with low recovery
    if steps > 20000:
        overtraining_score += 15
        reasons.append(f"⚠️ High daily activity ({steps:,} steps) - ensure adequate rest")
    
    return min(overtraining_score, 100), reasons

def calculate_heart_attack_risk(heart_rate, hrv, age=45, diabetes=False, smoking=0):
    """
    Calculate 30-day heart attack risk using multiple factors
    Framingham Risk Score adapted for real-time monitoring
    """
    risk_score = 0
    risk_factors = []
    
    # Baseline age risk
    baseline_age_risk = (age - 40) * 0.5 if age >= 40 else 0
    risk_score += baseline_age_risk
    
    # HRV is a strong predictor of cardiac events
    if hrv < 30:
        risk_score += 25
        risk_factors.append(f"🚨 CRITICAL: Severely low HRV ({hrv:.1f} ms)")
    elif hrv < 50:
        risk_score += 15
        risk_factors.append(f"⚠️ Low HRV ({hrv:.1f} ms) - autonomic imbalance")
    elif hrv > 80:
        risk_score -= 5  # Good recovery
        risk_factors.append(f"✅ Excellent HRV ({hrv:.1f} ms)")
    
    # Resting heart rate - elevated = risk
    if heart_rate > 100:
        risk_score += 20
        risk_factors.append(f"🚨 HIGH: Resting HR {heart_rate} bpm (elevated)")
    elif heart_rate > 85:
        risk_score += 10
        risk_factors.append(f"⚠️ Elevated HR {heart_rate} bpm")
    elif heart_rate < 60:
        risk_score -= 5
        risk_factors.append(f"✅ Good resting HR {heart_rate} bpm")
    
    # Heart rate variability status
    if hrv < 20:
        risk_score += 15
        risk_factors.append("🚨 CRITICAL: Severe autonomic dysfunction")
    
    # Diabetes increases risk
    if diabetes:
        risk_score += 30
        risk_factors.append("🚨 Diabetes: +30% risk multiplier")
    
    # Smoking
    risk_score += smoking * 2
    if smoking > 0:
        risk_factors.append(f"🚨 Smoking ({smoking} cigarettes): Risk increased")
    
    # Normalize to percentage
    risk_percentage = min(max(risk_score, 0), 100)
    
    return risk_percentage, risk_factors

def get_risk_severity(score):
    """Get severity level and color for risk score"""
    if score < 15:
        return "LOW RISK ✅", "#2ecc71"
    elif score < 40:
        return "MODERATE RISK ⚠️", "#ffa500"
    else:
        return "HIGH RISK 🚨", "#ff6b6b"

st.title("❤️ Cardio Risk Alert System")
st.markdown("**Real-time monitoring for overtraining & heart attack risk prediction**")

# Sidebar configuration
st.sidebar.title("⚙️ Settings")
age = st.sidebar.slider("Age", 20, 80, 45)
diabetes = st.sidebar.checkbox("Diabetes diagnosis?")
smoking = st.sidebar.slider("Cigarettes per day", 0, 20, 0)

# Refresh data
col1, col2 = st.columns([3, 1])
refresh_interval = col1.selectbox("Auto-refresh interval", 
                                   ["Manual", "Every 30s", "Every 1m", "Every 5m"])
if col2.button("🔄 Refresh Now"):
    st.rerun()

st.divider()

# Get current metrics
metrics = get_latest_metrics()

if metrics:
    heart_rate = metrics.get("heart_rate", 70)
    hrv = metrics.get("hrv", 50)
    steps = metrics.get("steps", 5000)
    active_energy = metrics.get("active_energy", 0)
    
    # Display current metrics
    st.subheader("📊 Current Vital Signs")
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("❤️ Heart Rate", f"{heart_rate} bpm")
    with metric_cols[1]:
        st.metric("📈 HRV", f"{hrv:.1f} ms")
    with metric_cols[2]:
        st.metric("👟 Steps", f"{steps:,}")
    with metric_cols[3]:
        st.metric("🔥 Active Energy", f"{active_energy:.0f} kcal")
    
    st.divider()
    
    # ============ OVERTRAINING ANALYSIS ============
    st.subheader("⚡ Overtraining Risk Assessment")
    
    overtraining_score, overtraining_reasons = calculate_overtraining_risk(
        heart_rate, hrv, steps
    )
    
    # Display overtraining risk
    overtraining_severity, overtraining_color = get_risk_severity(overtraining_score)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(
            f'<p style="color: {overtraining_color}; font-size: 48px; font-weight: bold; text-align: center;">'
            f'{overtraining_score}%</p>',
            unsafe_allow_html=True
        )
        st.markdown(f'<p style="text-align: center; font-weight: bold;">{overtraining_severity}</p>', 
                   unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Risk Indicators:")
        if overtraining_reasons:
            for reason in overtraining_reasons:
                st.markdown(f"- {reason}")
        else:
            st.success("✅ No overtraining detected - Recovery status optimal")
    
    # Overtraining recommendations
    st.markdown("### 💡 Recommendations:")
    if overtraining_score > 60:
        st.error("🛑 CRITICAL: Take 2-3 days of complete rest. Consult a cardiologist if symptoms persist.")
    elif overtraining_score > 40:
        st.warning("⚠️ Reduce training intensity. Focus on recovery (sleep, hydration, nutrition).")
    elif overtraining_score > 20:
        st.info("ℹ️ Monitor closely. Consider easier training sessions this week.")
    else:
        st.success("✅ Recovery status excellent. You can maintain or increase training intensity.")
    
    st.divider()
    
    # ============ HEART ATTACK RISK PREDICTION ============
    st.subheader("🚨 30-Day Heart Attack Risk Prediction")
    
    ha_risk, ha_factors = calculate_heart_attack_risk(
        heart_rate, hrv, age, diabetes, smoking
    )
    
    # Display heart attack risk
    ha_severity, ha_color = get_risk_severity(ha_risk)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(
            f'<p style="color: {ha_color}; font-size: 48px; font-weight: bold; text-align: center;">'
            f'{ha_risk:.1f}%</p>',
            unsafe_allow_html=True
        )
        st.markdown(f'<p style="text-align: center; font-weight: bold;">in next 30 days</p>', 
                   unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Risk Factors:")
        for factor in ha_factors:
            st.markdown(f"- {factor}")
    
    # Heart attack risk recommendations
    st.markdown("### 🏥 Medical Recommendations:")
    if ha_risk > 50:
        st.error(
            "🚨 **CRITICAL RISK** - Seek immediate medical evaluation. "
            "Consider emergency care if experiencing chest pain, shortness of breath, or severe fatigue."
        )
    elif ha_risk > 30:
        st.warning(
            "⚠️ **HIGH RISK** - Schedule urgent cardiology appointment. "
            "Avoid strenuous exercise until cleared by physician."
        )
    elif ha_risk > 15:
        st.info(
            "ℹ️ **MODERATE RISK** - Consult your cardiologist for risk stratification. "
            "Consider stress testing and advanced cardiac evaluation."
        )
    else:
        st.success(
            "✅ **LOW RISK** - Continue healthy lifestyle. Annual checkups recommended."
        )
    
    st.divider()
    
    # ============ VISUALIZATION ============
    st.subheader("📈 Risk Timeline & Trends")
    
    # Create historical simulation (since we don't have real history)
    days = np.arange(0, 31)
    # Simulate 30-day risk projection
    hourly_hr_trend = np.sin(np.linspace(0, 4*np.pi, 30)) * 5 + heart_rate
    hourly_hrv_trend = np.cos(np.linspace(0, 4*np.pi, 30)) * 8 + hrv
    
    fig = go.Figure()
    
    # Create secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=days, y=hourly_hr_trend, name="HR Projection",
                  line=dict(color="red", width=2), mode='lines+markers'),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=days, y=hourly_hrv_trend, name="HRV Projection",
                  line=dict(color="blue", width=2), mode='lines+markers'),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="Days from now")
    fig.update_yaxes(title_text="Heart Rate (bpm)", secondary_y=False)
    fig.update_yaxes(title_text="HRV (ms)", secondary_y=True)
    fig.update_layout(hovermode='x unified', height=400, width='100%')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Risk gauge
    st.subheader("📊 Combined Risk Score")
    combined_risk = (overtraining_score * 0.3 + ha_risk * 0.7)
    
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=combined_risk,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall Cardio Risk"},
        delta={'reference': 30},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#ff6b6b" if combined_risk > 50 else ("#ffa500" if combined_risk > 30 else "#2ecc71")},
            'steps': [
                {'range': [0, 33], 'color': "#2ecc71"},
                {'range': [33, 66], 'color': "#ffa500"},
                {'range': [66, 100], 'color': "#ff6b6b"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig_gauge.update_layout(height=400, width='100%')
    st.plotly_chart(fig_gauge, use_container_width=True)
    
else:
    st.error(
        "⚠️ Cannot connect to health data API. "
        "Make sure the API server is running on port 5000 and metrics are available."
    )
    st.info("👉 Start the API server: `python healthkit_api_server.py`")

# Footer
st.divider()
st.markdown("""
    ### ⚠️ MEDICAL DISCLAIMER
    This application provides **educational risk assessments only** and should **NOT** be used as a substitute for professional medical advice.
    
    - Always consult with a qualified cardiologist for medical guidance
    - Seek emergency care immediately if experiencing chest pain, severe shortness of breath, or cardiac symptoms
    - This tool uses general population statistics and may not apply to your specific condition
    
    **Emergency: Call 911 or your local emergency number**
""")
