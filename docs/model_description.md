# Model Description

## Cardio-Fitness Digital Twin — Model Documentation

---

## 1. Cardiac Digital Twin Model

### Overview
The cardiac twin simulates heart rate dynamics as a discrete-time physiological system.

### Core Equation
```
HR(t+1) = HR(t) + activity_effect(t) - recovery_effect(t) + fatigue_effect(t) + noise(t)
```

### State Variables
| Variable | Range | Description |
|----------|-------|-------------|
| heart_rate | 30–220 bpm | Current cardiac output proxy |
| fatigue | 0–1 | Accumulated training stress |
| recovery | 0–1 | Current autonomic recovery level |
| activity_level | 0–1 | Normalized exercise intensity |
| hrv | 5–200 ms | Heart Rate Variability (SDNN) |

### Parameters (user-calibrated)
- `resting_hr`: Personal resting heart rate
- `max_hr`: Observed or formula-based max HR (220 - age)
- `hrv_baseline`: Baseline HRV from rest periods
- `fatigue_sensitivity`: How quickly fatigue builds (calibrated from fatigue_index)
- `recovery_rate`: How quickly recovery occurs (calibrated from HRV)

---

## 2. Fatigue Model (Banister Impulse-Response)

### Equation
```
Fatigue(t) = Fatigue(t-1) × exp(-1/τ_fatigue) + Load(t) × sensitivity
```

### Parameters
- `τ_fatigue = 15 days`: Physiological fatigue decay constant
- `sensitivity`: Individual response to training load

---

## 3. Cardiac Enhancement Score (CES)

### Formula
```
CES = 0.20 × RHR_score
    + 0.25 × HR_recovery_score
    + 0.25 × HRV_score
    + 0.15 × Fatigue_score
    + 0.15 × Efficiency_score
```

### Component Calculations
Each component is linearly normalized between elite (100) and poor (0) benchmarks:

| Component | Elite | Poor |
|-----------|-------|------|
| Resting HR | 40 bpm | 85 bpm |
| HR Recovery | 55 bpm/min | 8 bpm/min |
| HRV (SDNN) | 90 ms | 15 ms |
| Fatigue Index | 5/100 | 80/100 |
| Aerobic Efficiency | 85% | 20% |

### CES Tiers
| Score | Tier |
|-------|------|
| 80–100 | Elite Performer |
| 65–79 | Advanced Fitness |
| 50–64 | Good Baseline |
| 35–49 | Developing |
| 0–34 | Beginner |

---

## 4. 30-Day Prediction Model

### Adaptation Curve
```
CES_gain(t) = adaptation_rate × (1 - CES(t)/100) × 100 - fatigue_penalty
```

The sigmoid-like saturation term `(1 - CES/100)` models diminishing returns as fitness improves.

### Strategy-Specific Rates
| Strategy | Daily Adaptation Rate |
|----------|-----------------------|
| HIIT | 1.8% |
| Tempo Run | 1.5% |
| Steady Cardio | 1.2% |
| Strength Circuit | 1.0% |
| Recovery Day | 0.4% |

---

## 5. Overtraining Risk Detection

### Risk Score Components (0–10 scale)
| Marker | Threshold | Points |
|--------|-----------|--------|
| Resting HR elevation ≥8 bpm | Severe | +2.5 |
| Resting HR elevation ≥4 bpm | Mild | +1.0 |
| HRV < 65% of baseline | Critical | +2.5 |
| HRV < 80% of baseline | Warning | +1.5 |
| Fatigue index ≥70 | Severe | +3.0 |
| Fatigue index ≥50 | Moderate | +1.5 |
| Recovery index < 30 | Poor | +1.5 |
| HR recovery rate < 12 bpm/min | Slow | +1.0 |

### Risk Levels
| Score | Level |
|-------|-------|
| ≥ 6 | High Risk |
| 3–5.9 | Moderate Risk |
| < 3 | Low Risk |

---

## References
- Banister EW et al. (1975). A systems model of training for athletic performance.
- Plews DJ et al. (2013). Heart rate variability in elite triathletes.
- Foster C et al. (1998). Monitoring training in athletes with reference to overtraining syndrome.
