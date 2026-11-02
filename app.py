import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

# Backend pipeline
from backend.data_loader import load_health_data
from backend.preprocessing import preprocess_health_data
from backend.feature_engineering import extract_features

# Simulation modules
from simulator import simulate
from ces_score import compute_ces
from optimizer import find_best_strategy
from prediction import predict_30_days
from risk_detection import detect_overtraining
from heart_animation import show_beating_heart


# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------
st.set_page_config(page_title="AI Cardio Digital Twin", layout="wide")

st.title("🫀 AI Cardio Digital Twin")
st.caption("Personalized Cardiac Performance Optimization using Digital Twin Simulation")


# ------------------------------------------------
# LOAD APPLE HEALTH DATA
# ------------------------------------------------
try:

    df = load_health_data()
    df = preprocess_health_data(df)
    features = extract_features(df)

    avg_heart_rate = round(features.get("avg_heart_rate", 0), 1)
    resting_hr_data = round(features.get("resting_hr", 0), 1)
    hrv = round(features.get("hrv", 0), 1)

except:
    avg_heart_rate = 75
    resting_hr_data = 65
    hrv = 50


# ------------------------------------------------
# SIDEBAR USER PROFILE
# ------------------------------------------------
st.sidebar.header("User Profile")

age = st.sidebar.slider("Age", 18, 70, 22)

rest_hr = st.sidebar.slider(
    "Resting Heart Rate",
    50,
    90,
    int(resting_hr_data)
)

fitness_level = st.sidebar.selectbox(
    "Fitness Level",
    ["Beginner", "Intermediate", "Athlete"]
)

strategy = st.sidebar.selectbox(
    "Training Strategy",
    ["HIIT", "Steady Cardio", "Recovery"]
)

st.sidebar.markdown("---")

st.sidebar.subheader("Wearable Data")

st.sidebar.metric("Avg Heart Rate", avg_heart_rate)
st.sidebar.metric("Resting HR", resting_hr_data)
st.sidebar.metric("HRV", hrv)


# ------------------------------------------------
# RUN HEART SIMULATION
# ------------------------------------------------
hr_data = simulate(strategy)

current_hr = hr_data[-1]

ces = compute_ces(hr_data)

avg_hr = round(sum(hr_data) / len(hr_data), 1)

peak_hr = round(max(hr_data), 1)


# ------------------------------------------------
# TABS
# ------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["Dashboard", "Digital Twin", "AI Optimizer", "Predictions"]
)


# ------------------------------------------------
# TAB 1 : DASHBOARD
# ------------------------------------------------
with tab1:

    st.header("Heart Simulation")

    col1, col2, col3 = st.columns(3)

    col1.metric("Cardiac Enhancement Score", ces)
    col2.metric("Average Heart Rate", avg_hr)
    col3.metric("Peak Heart Rate", peak_hr)

    st.subheader("Digital Twin Heart")

    show_beating_heart(current_hr)

    df_sim = pd.DataFrame({
        "Time": range(len(hr_data)),
        "Heart Rate": hr_data
    })

    fig = px.area(
        df_sim,
        x="Time",
        y="Heart Rate",
        title="Digital Twin Heart Simulation",
        line_shape="spline"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Training Insights")

    if ces > 80:
        st.success("Excellent cardiovascular improvement predicted")

    elif ces > 65:
        st.info("Moderate improvement expected")

    else:
        st.warning("Low improvement predicted — consider another strategy")

    st.subheader("Overtraining Risk Detection")

    risk = detect_overtraining(hr_data)

    if risk == "High":
        st.error("⚠ High overtraining risk detected")

    elif risk == "Moderate":
        st.warning("Moderate fatigue detected")

    else:
        st.success("Training load within safe limits")


# ------------------------------------------------
# TAB 2 : DIGITAL TWIN
# ------------------------------------------------
with tab2:

    st.header("Digital Twin Visualization")

    st.write(
        "The digital twin replicates the user's cardiovascular system "
        "and predicts how the heart responds to exercise."
    )

    col1, col2, col3 = st.columns(3)

    col1.subheader("User Data")
    col1.write("Heart rate, HRV, and activity collected from wearable devices.")

    col2.subheader("Digital Twin Model")
    col2.write("AI model simulates heart dynamics and fatigue accumulation.")

    col3.subheader("Simulation Engine")
    col3.write("Predicts physiological response to training strategies.")

    st.markdown("---")

    st.subheader("3D Anatomical Heart Model")

    show_beating_heart(current_hr)

    time = np.arange(0, 100)

    fatigue = np.sin(time / 10) + 2
    recovery = np.cos(time / 10) + 2

    df_states = pd.DataFrame({
        "Time": time,
        "Fatigue": fatigue,
        "Recovery": recovery
    })

    fig_states = px.line(
        df_states,
        x="Time",
        y=["Fatigue", "Recovery"],
        title="Exercise → Fatigue → Recovery Simulation"
    )

    st.plotly_chart(fig_states, use_container_width=True)


# ------------------------------------------------
# TAB 3 : AI OPTIMIZER
# ------------------------------------------------
with tab3:

    st.header("AI Training Optimizer")

    st.write(
        "The AI evaluates multiple workout strategies using the digital twin "
        "and recommends the optimal one."
    )

    if st.button("Generate Optimal Training Plan"):

        best_strategy, best_score, results = find_best_strategy()

        st.success(f"Recommended Strategy: {best_strategy}")

        st.write(f"Predicted CES: {best_score}")

        results_df = pd.DataFrame(
            list(results.items()),
            columns=["Strategy", "CES Score"]
        )

        fig2 = px.bar(
            results_df,
            x="Strategy",
            y="CES Score",
            title="Training Strategy Comparison"
        )

        st.plotly_chart(fig2, use_container_width=True)


# ------------------------------------------------
# TAB 4 : PREDICTIONS
# ------------------------------------------------
with tab4:

    st.header("30-Day Cardiac Performance Prediction")

    future_strategy = st.selectbox(
        "Select Strategy",
        ["HIIT", "Steady Cardio", "Recovery"]
    )

    if st.button("Predict 30 Day Improvement"):

        future_scores = predict_30_days(future_strategy)

        df_future = pd.DataFrame({
            "Day": range(1, 31),
            "Predicted CES": future_scores
        })

        fig3 = px.line(
            df_future,
            x="Day",
            y="Predicted CES",
            title="Predicted Cardiac Performance Over 30 Days"
        )

        st.plotly_chart(fig3, use_container_width=True)

        st.success(
            f"Predicted CES after 30 days: {round(future_scores[-1], 2)}"
        )


# ------------------------------------------------
# FOOTER
# ------------------------------------------------
st.markdown("---")

st.caption(
    "This platform creates a digital twin of the user's cardiovascular system "
    "and simulates training strategies to optimize cardiac performance."
)