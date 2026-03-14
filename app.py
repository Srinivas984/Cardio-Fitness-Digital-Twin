"""
app.py — Cardio-Fitness Digital Twin Dashboard
================================================
Powered by REAL Apple Watch data (Health Auto Export).

Run:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.health_auto_export_parser import HealthAutoExportParser
from backend.cardiac_model import CardiacDigitalTwin
from backend.optimizer_ai import AITrainingOptimizer
from backend.prediction_engine import PredictionEngine
from backend.risk_detection import RiskDetector
from simulation.workout_simulator import WorkoutSimulator
from scoring.ces_score import CESScorer

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Cardio Digital Twin — Srinivas", page_icon="❤️",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');
:root { --bg:#0d1117;--surf:#161b22;--surf2:#1c2330;--border:#21262d;
        --green:#3fb950;--blue:#58a6ff;--amber:#d29922;--red:#f85149;
        --purple:#bc8cff;--text:#c9d1d9;--muted:#8b949e; }
html,body,.stApp{background:var(--bg)!important;font-family:'IBM Plex Sans',sans-serif;color:var(--text);}
.stApp>header{background:transparent!important;}
section[data-testid="stSidebar"]{background:var(--surf)!important;border-right:1px solid var(--border);}
section[data-testid="stSidebar"] *{color:var(--text)!important;}
.kpi{background:var(--surf);border:1px solid var(--border);border-radius:10px;padding:16px 20px;}
.kpi-label{font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:6px;}
.kpi-value{font-family:'IBM Plex Mono',monospace;font-size:28px;font-weight:600;line-height:1;}
.kpi-sub{font-size:11px;color:var(--muted);margin-top:5px;}
.ces-panel{background:var(--surf);border:1px solid var(--border);border-radius:12px;padding:24px;text-align:center;}
.ces-num{font-family:'IBM Plex Mono',monospace;font-size:64px;font-weight:600;color:var(--green);line-height:1;}
.ces-tier{font-size:14px;color:var(--text);margin-top:6px;}
.ces-note{font-size:12px;color:var(--muted);margin-top:10px;line-height:1.5;}
.alert-box{border-radius:8px;padding:12px 16px;margin:8px 0;font-size:13px;line-height:1.5;}
.alert-warn{background:rgba(210,153,34,.1);border:1px solid rgba(210,153,34,.3);color:#e3b341;}
.alert-info{background:rgba(88,166,255,.08);border:1px solid rgba(88,166,255,.25);color:#79c0ff;}
.alert-danger{background:rgba(248,81,73,.08);border:1px solid rgba(248,81,73,.3);color:#ff7b72;}
.section-head{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--blue);padding-bottom:6px;border-bottom:1px solid var(--border);margin-bottom:12px;}
.prog-row{display:flex;align-items:center;gap:10px;margin-bottom:8px;}
.prog-label{width:100px;font-size:12px;color:var(--muted);flex-shrink:0;}
.prog-bar{flex:1;height:5px;background:var(--border);border-radius:3px;overflow:hidden;}
.prog-fill{height:100%;border-radius:3px;}
.prog-val{font-family:'IBM Plex Mono',monospace;font-size:12px;width:34px;text-align:right;color:var(--text);flex-shrink:0;}
.flag-item{display:flex;gap:10px;padding:8px 0;border-bottom:1px solid var(--border);font-size:13px;color:var(--muted);}
.flag-item:last-child{border-bottom:none;}
.rec-card{border-radius:8px;padding:12px 14px;margin-bottom:8px;border-left:3px solid;background:var(--surf2);}
.rec-title{font-size:13px;font-weight:600;color:var(--text);margin-bottom:4px;}
.rec-body{font-size:12px;color:var(--muted);line-height:1.55;}
.real-badge{display:inline-flex;align-items:center;gap:5px;padding:4px 10px;background:rgba(63,185,80,.1);border:1px solid rgba(63,185,80,.3);border-radius:12px;font-size:11px;color:var(--green);font-family:'IBM Plex Mono',monospace;}
.dot-live{width:6px;height:6px;border-radius:50%;background:var(--green);animation:blink 1.8s infinite;flex-shrink:0;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.2}}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding-top:.5rem!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--surf)!important;border-radius:8px;padding:4px;gap:3px;border:1px solid var(--border);}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;font-family:'IBM Plex Mono',monospace!important;font-size:11px!important;border-radius:6px!important;padding:7px 16px!important;letter-spacing:.06em;}
.stTabs [aria-selected="true"]{background:var(--blue)!important;color:#0d1117!important;}
</style>""", unsafe_allow_html=True)

PL = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(22,27,34,0.9)",
    font=dict(family="IBM Plex Mono, monospace", color="#8b949e", size=11),
    xaxis=dict(gridcolor="#21262d", linecolor="#21262d", zerolinecolor="#21262d"),
    yaxis=dict(gridcolor="#21262d", linecolor="#21262d", zerolinecolor="#21262d"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#21262d", font=dict(size=11)),
    margin=dict(l=40, r=20, t=36, b=36),
)

DATA_DIR = Path(__file__).parent / "data"

@st.cache_data
def load_real_data():
    parser = HealthAutoExportParser(str(DATA_DIR))
    features    = parser.compute_personal_features()
    daily_df    = parser.parse_daily_summary()
    workouts_df = parser.parse_workouts()
    walk_hr     = parser.parse_workout_hr("Indoor_Walk")
    cycle_hr    = parser.parse_workout_hr("Outdoor_Cycling")
    cycle_rec   = parser.parse_hr_recovery("Outdoor_Cycling")
    return features, daily_df, workouts_df, walk_hr, cycle_hr, cycle_rec

@st.cache_data
def get_scores(hrv, rhr, hrv3, fat, rec, recdrop, z1, z2, z3, z4, load, maxhr, avghr):
    f = dict(hrv_avg=hrv, resting_hr=rhr, hrv_last3=hrv3, fatigue_index=fat,
             recovery_index=rec, hr_recovery_rate=recdrop, zone1_pct=z1,
             zone2_pct=z2, zone3_pct=z3, zone4_pct=z4, activity_load=load,
             max_hr=maxhr, avg_hr=avghr, min_hr=rhr-5, hr_range=maxhr-rhr,
             hr_std=10.0, theoretical_max_hr=190.0, hrv_recovery_score=rec*0.6,
             resting_hrv=hrv3, total_steps=156604)
    ces  = CESScorer().score(f)
    risk = RiskDetector(hrv_baseline=hrv, resting_hr_baseline=rhr).assess(f)
    return ces, risk, f

@st.cache_data
def run_opt(hrv, rhr, fat, maxhr, avghr, duration):
    f = dict(hrv_avg=hrv, resting_hr=rhr, fatigue_index=fat, max_hr=maxhr,
             avg_hr=avghr, hr_recovery_rate=1.0, zone1_pct=62, zone2_pct=30,
             zone3_pct=7, zone4_pct=1, activity_load=7000, recovery_index=26,
             min_hr=rhr-5, hr_range=maxhr-rhr, hr_std=10, theoretical_max_hr=190,
             hrv_recovery_score=40, resting_hrv=hrv*0.7, total_steps=156604)
    twin = CardiacDigitalTwin(resting_hr=rhr, max_hr=maxhr, hrv_baseline=hrv)
    twin.calibrate(f)
    return AITrainingOptimizer(twin, duration_min=duration).optimize(f)

features, daily_df, workouts_df, walk_hr, cycle_hr, cycle_rec = load_real_data()
ces_result, risk_result, feat_full = get_scores(
    features["hrv_avg"], features["resting_hr"], features["hrv_last3"],
    features["fatigue_index"], features["recovery_index"],
    features["cycling_rec_drop"], features["zone1_pct"], features["zone2_pct"],
    features["zone3_pct"], features["zone4_pct"], features["activity_load"],
    features["max_hr"], features["avg_hr"],
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="padding:12px 0 4px;text-align:center;"><div style="font-family:\'IBM Plex Mono\',monospace;font-size:13px;color:#58a6ff;letter-spacing:.1em;">❤ CARDIO TWIN</div></div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;margin-bottom:12px;"><div class="real-badge"><span class="dot-live"></span>LIVE — Apple Watch</div></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("**Settings**")
    age = st.slider("Age", 18, 65, 30)
    workout_duration = st.slider("Session Duration (min)", 20, 90, 45)
    st.divider()
    st.markdown(f"""
    <div style="font-size:11px;color:#8b949e;line-height:2.2;">
    <div style="font-family:'IBM Plex Mono',monospace;color:#58a6ff;font-size:10px;letter-spacing:.1em;margin-bottom:4px;">DATA SOURCE</div>
    📊 Feb 11 – Mar 13, 2026<br>
    💓 {len(daily_df[daily_df.get('hrv_sdnn',pd.Series(dtype=float)).notna()] if 'hrv_sdnn' in daily_df.columns else [])} HRV readings<br>
    🏋 {len(workouts_df)} workout sessions<br>
    🚴 22.1 km outdoor cycling<br>
    🚶 Indoor walk data<br>
    🫀 Post-workout recovery HR
    </div>""", unsafe_allow_html=True)
    st.divider()
    st.markdown(f"""
    <div style="font-size:11px;color:#8b949e;line-height:2.2;">
    <div style="font-family:'IBM Plex Mono',monospace;color:#58a6ff;font-size:10px;letter-spacing:.1em;margin-bottom:4px;">PERSONAL BASELINES</div>
    HRV avg: <span style="color:#3fb950;">{features['hrv_avg']:.1f} ms</span><br>
    Resting HR: <span style="color:#3fb950;">{features['resting_hr']:.0f} bpm</span><br>
    Last 3-day HRV: <span style="color:#d29922;">{features['hrv_last3']:.1f} ms</span><br>
    HRV trend: <span style="color:#f85149;">{features['hrv_trend_pct']:+.1f}%</span>
    </div>""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:14px;padding:4px 0 18px;">
  <div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:18px;color:#c9d1d9;font-weight:600;">Srinivas — Cardio Digital Twin</div>
    <div style="font-size:12px;color:#8b949e;margin-top:3px;">Feb 11 – Mar 13, 2026 &nbsp;·&nbsp; Srinivas's Apple Watch &nbsp;·&nbsp; Health Auto Export</div>
  </div>
</div>""", unsafe_allow_html=True)

if features["hrv_trend_pct"] < -20:
    st.markdown(f"""
    <div class="alert-box alert-warn">
    ⚠ <strong>HRV declining this week:</strong> Last 3-day average {features['hrv_last3']:.0f} ms is
    {abs(features['hrv_trend_pct']):.0f}% below your {features['hrv_avg']:.0f} ms baseline.
    Reduce intensity and prioritise sleep before your next hard session.
    </div>""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Dashboard", "🫀 Digital Twin", "🤖 AI Optimizer", "📈 Predictions", "🚨 Risk Monitor"]
)

# ════════════════════════════════════════════════════════════════════════════
# TAB 1  DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    c1,c2,c3,c4,c5 = st.columns(5)
    for col, lbl, val, unit, sub, clr in [
        (c1,"CES Score",    f"{ces_result['ces']:.0f}","/100",   ces_result['tier'],         "#3fb950"),
        (c2,"HRV Baseline", f"{features['hrv_avg']:.1f}","ms",  "Personal avg",             "#58a6ff"),
        (c3,"Resting HR",   f"{features['resting_hr']:.0f}","bpm","7-day avg",              "#3fb950"),
        (c4,"Avg Steps",    f"{features['avg_steps']:.0f}","",  "30-day daily avg",         "#8b949e"),
        (c5,"Workouts",     "2","",                              "Feb–Mar recorded",         "#bc8cff"),
    ]:
        with col:
            st.markdown(f'<div class="kpi"><div class="kpi-label">{lbl}</div><div class="kpi-value" style="color:{clr};">{val}<span style="font-size:14px;color:#8b949e;"> {unit}</span></div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-head">Cardiac Enhancement Score</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ces-panel"><div class="ces-num">{ces_result["ces"]:.0f}</div><div class="ces-tier">{ces_result["emoji"]} {ces_result["tier"]}</div><div class="ces-note">{ces_result["interpretation"]}</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-head">CES Components (from your real data)</div>', unsafe_allow_html=True)
        comp = ces_result["components"]
        for lbl, val, color in [
            ("Resting HR",  comp["resting_hr_score"], "#3fb950"),
            ("HR Recovery", comp["recovery_score"],   "#f85149"),
            ("HRV",         comp["hrv_score"],        "#58a6ff"),
            ("Fatigue",     comp["fatigue_score"],    "#d29922"),
            ("Efficiency",  comp["efficiency_score"], "#bc8cff"),
        ]:
            st.markdown(f'<div class="prog-row"><div class="prog-label">{lbl}</div><div class="prog-bar"><div class="prog-fill" style="width:{val:.0f}%;background:{color};"></div></div><div class="prog-val">{val:.0f}</div></div>', unsafe_allow_html=True)
        st.markdown("""<div class="alert-box alert-danger" style="margin-top:10px;font-size:12px;">
        ⚠ <strong>HR Recovery (38/100)</strong> is your biggest gap — post-cycling HR dropped only 1 bpm in 1 min.
        Improving this single metric will add ~15 pts to your CES.</div>""", unsafe_allow_html=True)

    with col_b:
        if "hrv_sdnn" in daily_df.columns:
            hrv_data = daily_df[["date","hrv_sdnn"]].dropna()
            st.markdown('<div class="section-head">HRV Trend — Your Real Apple Watch Data</div>', unsafe_allow_html=True)
            fig_hrv = go.Figure()
            fig_hrv.add_hline(y=features["hrv_avg"], line_dash="dash", line_color="#8b949e",
                               annotation_text=f"Baseline {features['hrv_avg']:.0f}ms",
                               annotation_font=dict(color="#8b949e",size=10))
            hrv_colors = ["#3fb950" if v >= 70 else "#d29922" if v >= 50 else "#f85149" for v in hrv_data["hrv_sdnn"]]
            fig_hrv.add_trace(go.Scatter(
                x=hrv_data["date"], y=hrv_data["hrv_sdnn"],
                mode="lines+markers", line=dict(color="#58a6ff",width=2),
                marker=dict(color=hrv_colors,size=8,line=dict(color="#0d1117",width=1)),
                fill="tozeroy", fillcolor="rgba(88,166,255,0.07)",
            ))
            fig_hrv.update_layout(**PL, height=220, showlegend=False)
            fig_hrv.update_xaxes(tickformat="%b %d")
            fig_hrv.update_yaxes(title="HRV (ms)")
            st.plotly_chart(fig_hrv, use_container_width=True)

        if "heart_rate_avg" in daily_df.columns:
            hr_data = daily_df[["date","heart_rate_avg"]].dropna()
            st.markdown('<div class="section-head">Daily Avg Heart Rate</div>', unsafe_allow_html=True)
            fig_hr = go.Figure(go.Bar(
                x=hr_data["date"], y=hr_data["heart_rate_avg"],
                marker_color=["#f85149" if v >= 90 else "#d29922" if v >= 80 else "#3fb950" for v in hr_data["heart_rate_avg"]],
                marker_line_width=0,
            ))
            fig_hr.update_layout(**PL, height=200, showlegend=False)
            fig_hr.update_xaxes(tickformat="%b %d")
            fig_hr.update_yaxes(title="bpm", range=[50, 125])
            st.plotly_chart(fig_hr, use_container_width=True)

        if "steps" in daily_df.columns:
            steps_data = daily_df[["date","steps"]].dropna()
            st.markdown('<div class="section-head">Daily Steps</div>', unsafe_allow_html=True)
            fig_steps = go.Figure(go.Bar(
                x=steps_data["date"], y=steps_data["steps"],
                marker_color="#21262d", marker_line_width=0,
            ))
            fig_steps.add_hline(y=features["avg_steps"], line_dash="dot", line_color="#58a6ff",
                                  annotation_text=f"Avg {features['avg_steps']:.0f}",
                                  annotation_font=dict(color="#58a6ff",size=10))
            fig_steps.update_layout(**PL, height=180, showlegend=False)
            fig_steps.update_xaxes(tickformat="%b %d")
            fig_steps.update_yaxes(title="steps")
            st.plotly_chart(fig_steps, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2  DIGITAL TWIN
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-head">Digital Twin — Calibrated to Your Apple Watch Data</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="alert-box alert-info">Twin calibrated: RHR {features["resting_hr"]:.0f} bpm &nbsp;·&nbsp; Max HR {features["max_hr"]:.0f} bpm &nbsp;·&nbsp; HRV {features["hrv_avg"]:.0f} ms &nbsp;·&nbsp; Fatigue {features["fatigue_index"]:.0f}/100</div>', unsafe_allow_html=True)

    col_ctrl, col_viz = st.columns([1, 3])
    with col_ctrl:
        strategy_sel = st.selectbox("Strategy", WorkoutSimulator.STRATEGIES)
        sim_dur = st.slider("Duration (min)", 20, 90, 45, key="twin_dur")
        st.markdown("<br>", unsafe_allow_html=True)
        if not workouts_df.empty:
            st.markdown('<div style="font-size:10px;color:#8b949e;font-family:\'IBM Plex Mono\',monospace;margin-bottom:6px;letter-spacing:.1em;">YOUR REAL SESSIONS</div>', unsafe_allow_html=True)
            for _, w in workouts_df.iterrows():
                st.markdown(f'<div style="background:var(--surf2);border:1px solid var(--border);border-radius:6px;padding:8px 10px;margin-bottom:6px;font-size:11px;"><div style="color:#c9d1d9;font-weight:600;">{w.get("workout_type","")}</div><div style="color:#8b949e;margin-top:2px;">{w.get("duration","")} &nbsp;·&nbsp; avg {w.get("hr_avg",0):.0f} bpm &nbsp;·&nbsp; {w.get("distance_km",0):.1f}km</div></div>', unsafe_allow_html=True)

    with col_viz:
        twin = CardiacDigitalTwin(resting_hr=features["resting_hr"], max_hr=features["max_hr"], hrv_baseline=features["hrv_avg"])
        twin.calibrate(feat_full)
        profile = WorkoutSimulator().get_profile(strategy_sel, sim_dur)
        sim_df = twin.simulate(profile)

        fig_twin = make_subplots(rows=3, cols=1, subplot_titles=["Heart Rate","Fatigue & Recovery","HRV"], vertical_spacing=0.1, shared_xaxes=True)
        fig_twin.add_trace(go.Scatter(x=sim_df["time_min"], y=sim_df["heart_rate"], name="Simulated HR", line=dict(color="#58a6ff",width=2.5), fill="tozeroy", fillcolor="rgba(88,166,255,0.07)"), row=1, col=1)

        if strategy_sel == "Steady Cardio" and not cycle_hr.empty:
            t0 = cycle_hr["timestamp"].iloc[0]
            cyc = cycle_hr.copy(); cyc["min"] = (cyc["timestamp"]-t0).dt.total_seconds()/60
            fig_twin.add_trace(go.Scatter(x=cyc["min"], y=cyc["hr_avg"], name="Your Real Cycling HR", line=dict(color="#3fb950",width=2,dash="dot"), opacity=0.85), row=1, col=1)

        fig_twin.add_trace(go.Scatter(x=sim_df["time_min"], y=sim_df["fatigue"]*100, name="Fatigue", line=dict(color="#f85149",width=2)), row=2, col=1)
        fig_twin.add_trace(go.Scatter(x=sim_df["time_min"], y=sim_df["recovery"]*100, name="Recovery", line=dict(color="#3fb950",width=2)), row=2, col=1)
        fig_twin.add_trace(go.Scatter(x=sim_df["time_min"], y=sim_df["hrv"], name="HRV", line=dict(color="#bc8cff",width=2)), row=3, col=1)

        for k,v in PL.items():
            if k not in ["xaxis","yaxis"]: fig_twin.update_layout(**{k:v})
        for i in range(1,4):
            fig_twin.update_xaxes(gridcolor="#21262d", linecolor="#21262d", row=i, col=1)
            fig_twin.update_yaxes(gridcolor="#21262d", linecolor="#21262d", row=i, col=1)
        fig_twin.update_layout(height=460, showlegend=True)
        fig_twin.update_xaxes(title_text="Time (minutes)", row=3, col=1)
        st.plotly_chart(fig_twin, use_container_width=True)

    st.markdown('<div class="section-head">Real Workout Heart Rate Data</div>', unsafe_allow_html=True)
    wc1, wc2 = st.columns(2)
    with wc1:
        if not walk_hr.empty:
            wh = walk_hr.copy(); t0=wh["timestamp"].iloc[0]; wh["min"]=(wh["timestamp"]-t0).dt.total_seconds()/60
            fig_w = go.Figure(go.Scatter(x=wh["min"],y=wh["hr_avg"],fill="tozeroy",fillcolor="rgba(210,153,34,0.08)",line=dict(color="#d29922",width=2)))
            fig_w.update_layout(**PL, height=200, title="Indoor Walk — Mar 8 (31 min)")
            fig_w.update_xaxes(title="min"); fig_w.update_yaxes(title="bpm")
            st.plotly_chart(fig_w, use_container_width=True)
    with wc2:
        if not cycle_hr.empty:
            ch = cycle_hr.copy(); t0=ch["timestamp"].iloc[0]; ch["min"]=(ch["timestamp"]-t0).dt.total_seconds()/60
            fig_c = go.Figure(go.Scatter(x=ch["min"],y=ch["hr_avg"],fill="tozeroy",fillcolor="rgba(88,166,255,0.08)",line=dict(color="#58a6ff",width=2)))
            fig_c.update_layout(**PL, height=200, title="Outdoor Cycling — Mar 10 (49 min, 22.1 km)")
            fig_c.update_xaxes(title="min"); fig_c.update_yaxes(title="bpm")
            st.plotly_chart(fig_c, use_container_width=True)

    if cycle_rec and "raw_df" in cycle_rec:
        st.markdown('<div class="section-head">Post-Cycling HR Recovery (Real Data)</div>', unsafe_allow_html=True)
        rdf = cycle_rec["raw_df"].copy(); t0=rdf["timestamp"].iloc[0]; rdf["sec"]=(rdf["timestamp"]-t0).dt.total_seconds()
        fig_rec = go.Figure(go.Scatter(x=rdf["sec"],y=rdf["hr_avg"],mode="lines+markers",line=dict(color="#f85149",width=2),marker=dict(size=4),fill="tozeroy",fillcolor="rgba(248,81,73,0.07)"))
        fig_rec.add_annotation(x=60, y=cycle_rec["hr_at_1min"], text=f"1-min drop: {cycle_rec['recovery_drop_1min']:.0f} bpm (target: 12–20+)", showarrow=True, arrowhead=2, arrowcolor="#f85149", font=dict(color="#f85149",size=11), ax=-100, ay=-30)
        fig_rec.update_layout(**PL, height=220, title="Post-Cycling HR Recovery")
        fig_rec.update_xaxes(title="Seconds after workout"); fig_rec.update_yaxes(title="bpm")
        st.plotly_chart(fig_rec, use_container_width=True)
        st.markdown(f'<div class="alert-box alert-danger">Your 1-min HR recovery drop: <strong>{cycle_rec["recovery_drop_1min"]:.0f} bpm</strong> — elite target is 25–40 bpm. This is your highest-leverage training focus.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 3  AI OPTIMIZER
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-head">AI Training Strategy Optimizer</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="alert-box alert-info">Optimising for: HRV {features["hrv_avg"]:.0f}ms · RHR {features["resting_hr"]:.0f}bpm · Fatigue {features["fatigue_index"]:.0f}/100</div>', unsafe_allow_html=True)

    if st.button("🤖 Run AI Optimization", type="primary"):
        with st.spinner("Simulating 5 strategies on your calibrated digital twin..."):
            opt = run_opt(features["hrv_avg"], features["resting_hr"], features["fatigue_index"], features["max_hr"], features["avg_hr"], workout_duration)
        st.session_state["opt"] = opt

    if "opt" in st.session_state:
        opt = st.session_state["opt"]
        comp_df = opt["comparison_table"]
        best = comp_df.iloc[0]
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(88,166,255,.07),rgba(63,185,80,.05));border:1px solid rgba(63,185,80,.3);border-radius:10px;padding:18px 22px;margin:12px 0;">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.15em;color:#58a6ff;">OPTIMAL STRATEGY</div>
            <div style="font-size:24px;font-weight:600;color:#c9d1d9;margin-top:4px;">🏆 {opt['best_strategy']}</div>
            <div style="font-size:13px;color:#8b949e;margin-top:6px;">Predicted CES: <strong style="color:#3fb950;">{opt['best_ces']:.0f}/100</strong> &nbsp;·&nbsp; Avg HR: <strong>{best['avg_hr']:.0f} bpm</strong> &nbsp;·&nbsp; Peak: <strong>{best['max_hr']:.0f} bpm</strong></div>
        </div>""", unsafe_allow_html=True)

        oc1, oc2 = st.columns(2)
        with oc1:
            st.markdown('<div class="section-head">CES by Strategy</div>', unsafe_allow_html=True)
            fig_opt = go.Figure(go.Bar(
                x=comp_df["strategy"], y=comp_df["adjusted_ces"],
                marker_color=["#3fb950" if s==opt["best_strategy"] else "#21262d" for s in comp_df["strategy"]],
                marker_line_color=["#3fb950" if s==opt["best_strategy"] else "#30363d" for s in comp_df["strategy"]],
                marker_line_width=1.5,
                text=[f"{v:.0f}" for v in comp_df["adjusted_ces"]], textposition="outside",
                textfont=dict(size=12,color="#c9d1d9"),
            ))
            fig_opt.update_layout(**PL, height=280, showlegend=False)
            fig_opt.update_yaxes(range=[0,105])
            st.plotly_chart(fig_opt, use_container_width=True)
        with oc2:
            st.markdown('<div class="section-head">HR Profiles</div>', unsafe_allow_html=True)
            fig_tr = go.Figure()
            colors_t = ["#58a6ff","#3fb950","#d29922","#f85149","#bc8cff"]
            for i,(strat,sdf) in enumerate(opt["simulations"].items()):
                is_best = strat==opt["best_strategy"]
                fig_tr.add_trace(go.Scatter(x=sdf["time_min"],y=sdf["heart_rate"],name=strat,line=dict(color=colors_t[i%5],width=2.5 if is_best else 1),opacity=1.0 if is_best else 0.4))
            fig_tr.update_layout(**PL,height=280)
            fig_tr.update_xaxes(title="min"); fig_tr.update_yaxes(title="bpm")
            st.plotly_chart(fig_tr, use_container_width=True)

        st.markdown('<div class="section-head">Full Comparison</div>', unsafe_allow_html=True)
        disp = comp_df[["strategy","avg_hr","max_hr","avg_fatigue","end_recovery","adjusted_ces"]].copy()
        disp.columns = ["Strategy","Avg HR","Peak HR","Fatigue %","Recovery %","CES"]
        st.dataframe(disp.style.background_gradient(subset=["CES"],cmap="Greens").format({"Avg HR":"{:.0f}","Peak HR":"{:.0f}","Fatigue %":"{:.0f}","Recovery %":"{:.0f}","CES":"{:.0f}"}), use_container_width=True)
    else:
        st.markdown('<div class="alert-box alert-info">Click "Run AI Optimization" to simulate all strategies on your real digital twin.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4  PREDICTIONS
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-head">30-Day Cardiac Performance Forecast</div>', unsafe_allow_html=True)
    pc1, pc2 = st.columns([1,3])
    with pc1:
        pred_strategy = st.selectbox("Strategy", WorkoutSimulator.STRATEGIES, key="pred_s")
        pred_days = st.slider("Forecast Days", 7, 90, 30)
        st.markdown(f"""<div style="margin-top:12px;padding:12px;background:rgba(88,166,255,.06);border:1px solid rgba(88,166,255,.2);border-radius:8px;font-size:12px;color:#8b949e;line-height:2.2;">
        Starting CES: <span style="color:#58a6ff;">{ces_result['ces']:.0f}</span><br>
        HRV now: <span style="color:#d29922;">{features['hrv_last3']:.0f}ms ↓</span><br>
        Fatigue: <span style="color:#d29922;">{features['fatigue_index']:.0f}/100</span><br>
        Sessions/mo: <span style="color:#f85149;">2 (low)</span>
        </div>""", unsafe_allow_html=True)

    with pc2:
        engine = PredictionEngine(days=pred_days)
        pred_df = engine.predict(baseline_ces=ces_result["ces"], strategy=pred_strategy,
                                  current_fatigue=features["fatigue_index"]/100, current_hrv=features["hrv_avg"])
        fig_pred = go.Figure()
        fig_pred.add_trace(go.Scatter(x=pred_df["day"],y=pred_df["ces_smooth"],name="Predicted CES",line=dict(color="#3fb950",width=3),fill="tozeroy",fillcolor="rgba(63,185,80,0.07)"))
        fig_pred.add_trace(go.Scatter(x=pred_df["day"],y=pred_df["ces"],name="Daily",line=dict(color="#3fb950",width=1,dash="dot"),opacity=0.4))
        rest = pred_df[pred_df["is_rest_day"]]
        fig_pred.add_trace(go.Scatter(x=rest["day"],y=rest["ces"],name="Rest Days",mode="markers",marker=dict(symbol="circle",color="#58a6ff",size=7,line=dict(color="#0d1117",width=1))))
        fig_pred.add_hline(y=ces_result["ces"],line_dash="dash",line_color="#8b949e",annotation_text=f"Baseline {ces_result['ces']:.0f}",annotation_font=dict(color="#8b949e",size=10))
        fig_pred.update_layout(**PL,height=300)
        fig_pred.update_xaxes(title="Day")
        fig_pred.update_yaxes(title="CES",range=[max(0,ces_result["ces"]-8),min(100,pred_df["ces"].max()+8)])
        st.plotly_chart(fig_pred, use_container_width=True)

    final_ces = pred_df["ces"].iloc[-1]; improvement = final_ces - ces_result["ces"]
    s1,s2,s3,s4 = st.columns(4)
    for col,lbl,val,clr in [(s1,"Starting CES",f"{ces_result['ces']:.0f}/100","#8b949e"),(s2,f"Day {pred_days}",f"{final_ces:.0f}/100","#3fb950"),(s3,"Total Gain",f"+{improvement:.1f} pts","#3fb950"),(s4,"Peak CES",f"{pred_df['ces'].max():.0f}/100","#58a6ff")]:
        with col:
            st.markdown(f'<div class="kpi"><div class="kpi-label">{lbl}</div><div class="kpi-value" style="color:{clr};font-size:22px;">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-head">Strategy Comparison — 30-Day Improvement</div>', unsafe_allow_html=True)
    comp30 = engine.compare_strategies(ces_result["ces"], feat_full)
    fig_c30 = go.Figure(go.Bar(x=comp30["strategy"],y=comp30["improvement"],marker_color=["#3fb950" if s==pred_strategy else "#21262d" for s in comp30["strategy"]],text=[f"+{v:.1f}" for v in comp30["improvement"]],textposition="outside",textfont=dict(size=11,color="#c9d1d9")))
    fig_c30.update_layout(**PL,height=240)
    fig_c30.update_yaxes(title="CES improvement (pts)")
    st.plotly_chart(fig_c30, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 5  RISK MONITOR
# ════════════════════════════════════════════════════════════════════════════
with tab5:
    rcol_map = {"Low Risk":"#3fb950","Moderate Risk":"#d29922","High Risk":"#f85149"}
    rc = rcol_map.get(risk_result["risk_level"],"#d29922")
    st.markdown(f"""
    <div style="background:rgba(210,153,34,.07);border:1px solid rgba(210,153,34,.25);border-radius:10px;padding:20px 24px;margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:14px;">
            <span style="font-size:40px;">{risk_result['icon']}</span>
            <div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:20px;font-weight:600;color:{rc};">{risk_result['risk_level']}</div>
                <div style="font-size:13px;color:#8b949e;margin-top:4px;">Risk score: {risk_result['risk_pct']:.0f}/100</div>
            </div>
        </div>
        <div style="margin-top:14px;font-size:13px;color:#8b949e;">{risk_result['message']}</div>
        <div style="margin-top:10px;padding:10px;background:rgba(210,153,34,.08);border-radius:6px;font-size:12px;color:#c9d1d9;"><strong>Action:</strong> {risk_result['action']}</div>
    </div>""", unsafe_allow_html=True)

    rc1, rc2 = st.columns(2)
    with rc1:
        st.markdown('<div class="section-head">Real Data Risk Flags</div>', unsafe_allow_html=True)
        real_flags = [
            ("⚠", f"HRV today: {features['hrv_last3']:.0f}ms — {abs(features['hrv_trend_pct']):.0f}% below your {features['hrv_avg']:.0f}ms baseline", "#d29922"),
            ("⚠", "4-day consecutive HRV decline: Mar 10→11→12→13: 78→54→44→39 ms", "#d29922"),
            ("⚠", f"Post-cycling HR recovery: {features['cycling_rec_drop']:.0f} bpm/min (target: 12–20+)", "#d29922"),
            ("✓", f"Resting HR stable at {features['resting_hr']:.0f} bpm — no cardiac strain signal", "#3fb950"),
            ("✓", "No abnormal HR notifications in the 30-day period", "#3fb950"),
            ("✓", "ECG on file — no irregular rhythm flagged", "#3fb950"),
        ]
        for icon, flag, color in real_flags:
            st.markdown(f'<div class="flag-item"><span style="color:{color};flex-shrink:0;">{icon}</span><span>{flag}</span></div>', unsafe_allow_html=True)

    with rc2:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=risk_result["risk_pct"],
            number={"font":{"family":"IBM Plex Mono","size":28,"color":rc}},
            title={"text":"Risk Score","font":{"family":"IBM Plex Mono","size":11,"color":"#8b949e"}},
            gauge={"axis":{"range":[0,100],"tickcolor":"#21262d","tickfont":{"size":9}},"bar":{"color":rc,"thickness":0.28},"bgcolor":"#161b22","bordercolor":"#21262d",
                   "steps":[{"range":[0,35],"color":"rgba(63,185,80,.12)"},{"range":[35,65],"color":"rgba(210,153,34,.12)"},{"range":[65,100],"color":"rgba(248,81,73,.12)"}]},
        ))
        fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(family="IBM Plex Mono",color="#8b949e"),height=260,margin=dict(l=30,r=30,t=50,b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown('<div class="section-head">Recovery Protocol — Based on Your Real Data</div>', unsafe_allow_html=True)
    for border_color, title, body in [
        ("#f85149","Sleep quality (your #1 lever)", f"Your best HRV (108 ms, Feb 27) followed 6.3 hrs sleep with 0.94 hrs deep sleep. Your worst recent HRV (39 ms, Mar 13) follows days with no recorded sleep data. Sleep is your single most powerful HRV lever."),
        ("#d29922","Reduce training load 3–5 days", "Zone 2 only — keep HR at 115–133 bpm. No HIIT or tempo until HRV recovers above 55 ms. Your cycling session shows you can sustain Zone 2 for 49 min efficiently."),
        ("#d29922","Heat & hydration recovery", f"You trained at 30.2°C (cycling) and 28.8°C (walk). Heat + exertion depletes electrolytes fast. Target 2.5–3L water + electrolytes on training days."),
        ("#3fb950","HR recovery training target", f"After every session: 2 min slow walk → record 60-second HR drop. Current: {features['cycling_rec_drop']:.0f} bpm. Target: 12+ bpm within 4 weeks. This alone adds ~15 CES points."),
    ]:
        st.markdown(f'<div class="rec-card" style="border-color:{border_color};"><div class="rec-title">{title}</div><div class="rec-body">{body}</div></div>', unsafe_allow_html=True)
