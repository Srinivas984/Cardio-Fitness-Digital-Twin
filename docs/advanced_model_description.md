# Advanced Cardio Digital Twin System Architecture v2.0

## Executive Summary

The Cardio Digital Twin is a research-grade AI cardiovascular coach that transforms wearable health data into actionable insights. It combines advanced physiological modeling, machine learning optimization, and explainable AI to provide personalized training recommendations and predict long-term cardiovascular outcomes.

**Key Innovation:** Bayesian multi-objective optimization + physiologically-grounded digital twin = scientifically-sound AI coaching.

---

## System Components

### 1. Core Physiological Model (`cardiac_model.py`)

**Purpose:** Simulate the human cardiovascular system with physiological accuracy.

**State Variables:**
- `heart_rate`: Current HR (bpm) — dynamic response to activity
- `fatigue`: Accumulated fatigue (0–1) — non-linear buildup from training
- `recovery`: Parasympathetic recovery status (0–1) — ANS tone/vagal function
- `hrv`: Heart Rate Variability (ms SDNN) — inversely related to fatigue/stress
- `parasympathetic`: Autonomic nervous system parasympathetic tone (0–1)
- `cardiac_output`: Stroke volume × HR (L/min) — reduced by fatigue
- `training_load`: Cumulative Training Impulse (TRIMP) — long-term load tracking

**Physics & Equations:**

```
HR(t) = HR(t-1) + activity_effect - recovery_effect - fatigue_effect

activity_effect = lag_constant × (target_HR - current_HR) × dt
where target_HR = RHR + intensity × (MaxHR - RHR)
and lag_constant = 0.15 × (1 + 0.3 × fatigue)  [HR response slower when fatigued]

Fatigue dynamics (Banister-like):
dF/dt = intensity^1.5 × sensitivity - recovery_rate × (1 - intensity) × recovery

HRV suppression:
HRV(t) = HRV_baseline × (1 - activity × 0.4) × (1 - fatigue × 0.5) 
       × (1 + parasympathetic × 0.2) + white_noise

Parasympathetic recovery:
dP/dt = recovery_rate × (1 - activity) × 0.5 - activity × 0.05
[Improves at rest, suppressed during exercise]

Cardiac Output:
Q = HR × SV
where SV = baseline_SV × (1 - fatigue × 0.2)
[Fatigue reduces stroke volume]

Training Impulse (TRIMP):
TRIMP = duration × intensity × age_factor × exp(1.92 × intensity)
[Exponential scaling for high-intensity work]
```

**Key Features:**
- Physiologically-grounded ODEs (not black-box neural nets)
- HR drift simulation (cardiac efficiency loss)
- Parasympathetic dynamics (autonomic nervous system)
- Fatigue-dependent recovery rates
- Personalized calibration from user baseline

**Calibration:**
Uses real user data (apple Health) to personalize:
- Resting HR baseline
- Max HR (220-age correction)
- HRV baseline (personalized SDNN)
- Fatigue sensitivity (based on fatigue_index)
- Recovery rate (based on HRV and recovery_index)
- VO2max estimation

---

### 2. AI Training Optimizer (`optimizer_ai.py`)

**Purpose:** Intelligent selection of optimal training strategy using Bayesian multi-objective optimization.

**Algorithm:**

1. **Strategy Evaluation** (15+ predefined strategies):
   - Rest Recovery
   - Low-Intensity Aerobic (Z1-Z2)
   - Moderate Aerobic (Z2-Z3)
   - Threshold Work (Z3-Z4)
   - VO2max HIIT
   - Sprint Intervals
   - And 9+ more...

2. **Simulation & Scoring:**
   For each strategy:
   ```
   simulation = digital_twin.simulate(activity_profile)
   
   raw_CES = CES_scorer.score(simulation_features)
   
   risk_penalty = weighted_risk(fatigue, HRV_suppression, recovery)
   
   sustainability_score = f(fatigue_zone, recovery, HRV_preservation)
   
   adjusted_CES = raw_CES - risk_penalty × sustainability_score
   ```

3. **Risk Adjustment:**
   ```
   risk_penalty = 0
   if peak_fatigue > 0.8: penalty += 15
   elif peak_fatigue > 0.6: penalty += 8
   if parasympathetic < 0.5: penalty += 10
   if recovery < 0.3: penalty += 8
   ```

4. **Sustainability Multiplier:**
   ```
   Assesses if workout can be repeated without overtraining:
   - Ideal fatigue zone: 0.2–0.5
   - Recovery preservation
   - HRV protection
   ```

5. **Output:**
   - Best strategy with confidence score
   - Ranking of all 15+ strategies
   - Comparison table (HR zones, fatigue, recovery)
   - Full simulation traces for analysis

**Bayesian Optimization** (advanced mode):
Uses differential evolution to optimize:
- Intensity (0.3–0.95)
- Duration (20–90 min)
- Interval structure (0–1 ratio)

Maximizes objective function:
```
score = CES_estimate - risk_penalty
subject to: intensity, duration, interval_ratio bounds
```

---

### 3. Explainable AI (`explainable_ai.py`)

**Purpose:** Generate human-readable explanations for all AI recommendations.

**Methods:**

1. **Training Recommendation Reasoning:**
   ```
   explain_training_recommendation()
   
   Returns:
   - Primary reasons (HRV analysis, fatigue status, recovery state)
   - Supporting metrics (deltas from baseline)
   - Risk considerations
   - Expected benefits
   ```

   Example output:
   ```
   Recommended Strategy: Low-Intensity Aerobic
   
   PRIMARY REASONS:
   - HRV significantly suppressed (autonomic nervous system fatigued)
   - High fatigue accumulation detected
   
   SUPPORTING METRICS:
   - HRV at 35 ms, 30% below personal baseline
   - Fatigue index: 70/100 (recovery is priority)
   
   EXPECTED BENEFITS:
   - Promotes parasympathetic nervous system recovery
   - Allows accumulated fatigue to decay
   - Improves HRV rebound within 24-48 hours
   ```

2. **Overtraining Risk Explanation:**
   ```
   explain_overtraining_risk()
   
   Identifies:
   - Contributing factors (HRV drop, RHR elevation, etc.)
   - Protective factors (good sleep, stable metrics)
   - Immediate action items
   ```

3. **Feature Contribution Analysis:**
   ```
   feature_contribution_analysis()
   
   Scores each metric's contribution:
   - HRV_recovery: +15 points (improving autonomic function)
   - Resting_HR: -8 points (elevated resting HR is negative)
   - Fatigue_status: -20 points (high fatigue)
   - Recovery_capacity: +10 points (good recovery)
   ```

4. **Strategy Comparison:**
   ```
   compare_strategies()
   
   For each strategy:
   - Physiological impact (low/moderate/high stress)
   - Recommendation context (when to use it)
   - Acute vs. chronic effects
   ```

5. **Weekly Summary:**
   ```
   generate_weekly_summary()
   
   Analyzes trends:
   - HRV direction (improving ↑ / stable → / declining ↓)
   - RHR trend (adaptation signal)
   - Fatigue trend (load balance)
   - Overall assessment + recommendations
   ```

---

### 4. Digital Twin Simulator (`cardiac_simulator.py`)

**Purpose:** Multi-day and scenario-based simulations for planning and prediction.

**Capabilities:**

1. **Training Week Simulation:**
   ```python
   simulate_training_week(
       workout_schedule=[
           {"day": 1, "activity_profile": [0.6]*45, "duration_min": 45},
           ...
       ],
       sleep_hours_per_night=8.0,
       nutrition_quality=1.0  # multiplier on recovery rate
   )
   ```
   
   Outputs:
   - Minute-by-minute HR, HRV, fatigue, recovery
   - Tracks sleep recovery periods
   - Shows overnight parasympathetic rebound

2. **30-Day Progression Simulation:**
   ```python
   simulate_30day_progression(
       weekly_structure="standard",  # periodization pattern
       starting_features={...}
   )
   ```
   
   Models:
   - 4-week training cycle with variable loads
   - Adaptive recovery from day to day
   - Cumulative fatigue and adaptation effects
   
   Returns:
   - Daily summaries (HR, HRV, fatigue trends)
   - Weekly summaries
   - 30-day projections for HRV, RHR, fitness gain

3. **Recovery Protocol Simulation:**
   ```python
   simulate_recovery_protocol(
       duration_days=7,
       protocol_type="standard"  # "aggressive", "gentle", "standard"
   )
   ```
   
   Shows:
   - HRV rebound timeline
   - Fatigue clearance curve
   - Expected recovery trajectory

4. **What-If Scenario Analysis:**
   ```python
   what_if_scenario(
       scenario_name="Sleep Boost",
       intervention="more_sleep",  # or "reduce_volume", "extra_day_off"
       duration_days=7
   )
   ```
   
   Compares outcomes of different interventions

---

### 5. Risk Detection Engine (`risk_detection.py`)

**Purpose:** Identify overtraining risk with multi-marker threshold system.

**Risk Scoring (0–10 scale):**

| Marker | Low Risk | Moderate | High Risk |
|--------|----------|----------|-----------|
| HRV Ratio | >0.85 | 0.70–0.85 | <0.70 |
| RHR Elevation | <3 bpm | 3–8 bpm | >8 bpm |
| Fatigue Index | <40 | 40–60 | >60 |
| Recovery Index | >70% | 50–70% | <50% |

```
risk_score = 0
if HRV_ratio < 0.65: risk_score += 2.5
if RHR_elevation >= 8: risk_score += 2.5
if fatigue >= 70: risk_score += 3.0
if recovery < 50: risk_score += 2.0
```

**Output Categories:**
- **Low Risk** (0–3): Continue training, monitor trends
- **Moderate Risk** (3–7): Reduce intensity 20–30%, add rest day
- **High Risk** (7–10): 5–7 days complete rest, consult physician

**Recovery Recommendations:**
Each risk level includes specific protocols:
- Sleep duration targets
- Nutrition adjustments
- Training intensity caps
- Timeline for reassessment

---

### 6. Cardiac Enhancement Score (CES) (`ces_score.py`)

**Purpose:** Composite cardiovascular health metric.

**Components:**

```
CES = weight_HRV × HRV_score 
    + weight_RHR × RHR_score
    + weight_HRavg × HRavg_score
    + weight_recovery × recovery_score
    + weight_fatigue × fatigue_score
    + weight_zone_dist × zone_distribution_score

Typical weights: HRV(0.3), RHR(0.2), HRavg(0.15), Recovery(0.15), Fatigue(0.1), Zones(0.1)
```

**Scoring Functions:**

- **HRV Score:** Higher HRV (better ANS function) = higher score (0–100)
- **RHR Score:** Lower RHR (better fitness) = higher score (0–100)
- **Average HR:** Lower sustained HR (better efficiency) = higher score
- **Recovery Index:** Faster heart rate recovery = higher score
- **Fatigue Index:** Lower fatigue (less accumulated stress) = higher score
- **Zone Distribution:** Spending time in Z2 (aerobic) vs. excessive high-intensity

**Tier System:**
- **Excellent** (>75): Ready for challenging training
- **Good** (50–75): Balanced approach
- **Fair** (<50): Recovery/easier training recommended

---

## Data Pipeline

### Input Sources
1. **Apple Health Export** (CSV/XML):
   - Heart rate time series
   - Heart rate variability (SDNN)
   - Resting heart rate
   - Workout data (duration, type, calories)
   - Steps, active energy

2. **Manual User Input**:
   - Sleep hours
   - Nutrition quality
   - Stress levels
   - Illness/injury flags

### Feature Engineering
1. **Daily Aggregation:**
   - Resting HR (minimum HR during sleep)
   - Daily HRV (from morning measurements)
   - Training load (TRIMP calculation)
   - Recovery index (sleep + HRV + RHR)

2. **Trend Calculation:**
   - 7-day moving averages
   - Week-over-week changes
   - Baseline comparison

3. **Distribution Analysis:**
   - HR zone percentages
   - Intensity distribution
   - Training load balance

### Output
Clean, normalized feature vector with:
```python
{
    "resting_hr": 62.0,
    "hrv_avg": 48.0,
    "max_hr": 185,
    "fatigue_index": 35,
    "recovery_index": 65,
    "zone1_pct": 25,
    # ... etc
}
```

---

## Dashboard Overview

### Tab 1: Dashboard
- Current CES score with gauge
- Key metrics (RHR, HRV, Fatigue, Recovery, Training Load)
- 7-day trend charts
- Status indicator

### Tab 2: Digital Twin
- Real-time workout simulation
- 4-subplot visualization (HR, Fatigue, HRV, Cardiac Output)
- Strategy selector
- Live metrics

### Tab 3: AI Optimizer
- Runs 15+ strategy evaluations
- Bayesian optimization option
- Strategy comparison table
- Risk-adjusted recommendations

### Tab 4: 30-Day Forecast
- Projected HRV improvement
- Projected RHR reduction
- Periodization selector
- Weekly structure analysis

### Tab 5: Simulator
- Multi-day training simulation
- Recovery protocol analysis
- What-if scenarios
- Cumulative effect visualization

### Tab 6: Risk Monitor
- Overtraining risk gauge (0–10)
- Contributing factors
- Protective factors
- Recovery protocol

### Tab 7: Explainable AI
- Recommendation reasoning
- Risk explanation
- Feature attribution
- Weekly trend analysis

---

## Research Basis

### Physiological Models
- **Banister Impulse-Response:** Fatigue & performance modeling (Banister 1991)
- **Cardiac Dynamics:** Heart rate control physiology (Berntson et al. 2000)
- **Autonomic Nervous System:** HRV as vagal tone proxy (Task Force 1996)
- **Training Load:** TRIMP calculation (Lucia et al. 2003)

### Optimization Methods
- **Bayesian Optimization:** Hyperparameter tuning (Bergstra et al. 2011)
- **Multi-Objective Optimization:** Risk-adjusted recommendations
- **Explainable AI:** Feature attribution & SHAP-like analysis

### Sports Science
- **Overtraining Syndrome:** Multi-marker detection guidelines (Kreher & Schwartz 2012)
- **Heart Rate Training Zones:** Zone definitions (Karvonen et al. 1957)
- **Recovery Physiology:** Sleep, nutrition, autonomic rebound (Halson & Jeukendrup 2004)

---

## Key Innovations

### 1. Physiological Grounding
Unlike black-box AI, this system uses:
- Validated ODEs for HR dynamics
- Scientifically-understood fatigue models
- Well-established ANS physiology

### 2. Risk-Aware Optimization
Maximizes CES while:
- Penalizing overtraining risk
- Preserving long-term sustainability
- Respecting autonomic thresholds

### 3. Explainability
Every recommendation includes:
- Clear reasoning (HRV low → recovery needed)
- Magnitude of impact ("HRV 30% below baseline")
- Specific action items

### 4. Adaptivity
Continuous calibration:
- Model parameters adjust to user data
- Baselines update weekly
- Recovery curves personalized

---

## Performance Metrics

| Metric | Target | Method |
|--------|--------|--------|
| Recommendation Accuracy | >85% | Cross-validation on athlete data |
| Risk Detection Sensitivity | >90% | Overtraining syndrome cases |
| Adaptation Prediction | ±7 days | 30-day forecast RMSE |
| User Trust | >4/5 stars | Explainability & reasoning |

---

## Limitations & Future Work

### Current Limitations
- Single-user profiling (no population data)
- Assumes regular Apple Watch data
- No individual pathology modeling
- Sleep quality estimated from HRV proxy

### Future Enhancements
1. **Population Norming:**
   - Age, fitness level comparison groups
   - Personalized thresholds by demographic

2. **Advanced Inputs:**
   - Sleep stage data (Oura, Eight, etc.)
   - Core temperature (Apple Watch Series 8+)
   - Fine-grained GPS/altitude data
   - Nutrition tracking integration

3. **Pathology Modeling:**
   - Individual overtraining susceptibility
   - Inflammation response patterns
   - Recovery hormone simulation

4. **Reinforcement Learning:**
   - Learns user's unique adaptation curves
   - Contextual recommendations (stress, weather, etc.)
   - Long-term performance optimization

5. **Integration:**
   - Real-time alerts on Apple Watch
   - Coach communication system
   - Training plan auto-generation

---

## Hackathon Differentiators

✅ **Physiological Sophistication:** Research-grade cardiac modeling (not typical app)
✅ **AI Innovation:** Bayesian multi-objective optimization with explainability
✅ **Real Data:** Powered by actual Apple Watch health data
✅ **Actionable:** Specific, personalized recommendations with reasoning
✅ **Scalable:** Architecture ready for clinical research & athlete support
✅ **Open Science:** All methods documented & scientifically grounded

---

## References

- Banister, E. W. (1991). Modeling elite athletic performance. In: Modeling in Sport. Model. Mech. Exerc.
- Berntson, G. G., et al. (2000). Heart rate variability: origins, methods, interpretation. Psychophysiology.
- Task Force of the European Society of Cardiology (1996). Heart rate variability. Circulation.
- Lucia, A., et al. (2003). Frequency of the O2 deficit during supramaximal exercise. J Appl Physiol.
- Kreher, J. B., & Schwartz, J. B. (2012). Overtraining syndrome. The Journal of Sports Medicine.
- Karvonen, M. J., et al. (1957). The effects of training on heart rate. Ann Med Exp Biol Fenniae.
- Halson, S. L., & Jeukendrup, A. E. (2004). Does overtraining exist? Eur J Sport Sci.

---

**Version:** 2.0 (Advanced AI Coach)
**Last Updated:** March 2026
**Author:** Srinivas Digital Health Research
**Status:** Research-Grade Prototype
