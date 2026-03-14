# 🚨 Cardio Risk Alert System

## Overview

The **Cardio Risk Alert System** is a specialized dashboard that monitors two critical cardiac health metrics:

1. **⚡ Overtraining Risk** - Detects if your body is being overexerted with insufficient recovery
2. **🏥 30-Day Heart Attack Risk Prediction** - Estimates cardiac event risk using real-time metrics

This app runs **alongside** the main Cardio Coach dashboard for comprehensive health monitoring.

---

## 🎯 Features

### Overtraining Detection
- **Real-time HRV monitoring** - Heart Rate Variability is the key indicator of recovery status
- **Resting HR analysis** - Elevated resting heart rate signals fatigue
- **Training volume assessment** - Tracks step count and activity levels
- **Adaptive recommendations** - Provides actionable recovery guidance

**How it works:**
- HRV < 40 ms = High overtraining risk
- HR > 85 bpm = Stress/fatigue indicator
- Steps > 20,000 = High training volume requiring rest

### Heart Attack Risk Prediction (30-day)
- **Cardiac risk scoring** - Uses Framingham-adapted model
- **Multi-factor analysis** - Age, HRV, resting heart rate, diabetes, smoking
- **Risk stratification** - LOW / MODERATE / HIGH / CRITICAL
- **Medical recommendations** - Evidence-based guidance

**Risk Factors:**
- HRV < 30 ms = Critical autonomic dysfunction
- HR > 100 bpm = Elevated cardiac stress
- Age + comorbidities = Baseline risk increase
- Diabetes = +30% risk multiplier
- Smoking = +2% per cigarette/day

---

## 📊 Dashboard Layout

### Home Tab
```
📊 Current Vital Signs
├── ❤️ Heart Rate (bpm)
├── 📈 HRV (ms)
├── 👟 Steps
└── 🔥 Active Energy (kcal)

⚡ Overtraining Risk Assessment
├── Risk Score (0-100%)
├── Severity Level
├── Risk Indicators
└── Recovery Recommendations

🚨 30-Day Heart Attack Risk Prediction
├── Risk Score (%)
├── Risk Factors
├── Medical Recommendations
└── Timeline Projection

📈 Risk Trends & Visualization
└── 30-day projection charts
```

### Settings
- Age (20-80)
- Diabetes status
- Smoking frequency
- Auto-refresh interval

---

## 🚀 Running the Apps

### Option 1: Quick Start (All in one)
```powershell
# Run the PowerShell script
.\RUN_ALL.ps1
```

This starts:
- ✅ API Server (port 5000)
- ✅ Main Dashboard (port 8508)
- ✅ Risk Alert System (port 8509)

### Option 2: Manual Start

**Terminal 1 - API Server:**
```powershell
python healthkit_api_server.py
# Running on http://localhost:5000
```

**Terminal 2 - Main Dashboard:**
```powershell
streamlit run app_final.py
# Running on http://localhost:8508
```

**Terminal 3 - Risk Alert System:**
```powershell
streamlit run app_risk_alert.py --server.port=8509
# Running on http://localhost:8509
```

### Option 3: Batch File (Windows)
```powershell
RUN_ALL.bat
```

---

## 🌐 Access Points

| Dashboard | URL | Purpose |
|-----------|-----|---------|
| **Main Costco Coach** | http://localhost:8508 | 7-tab AI health coaching |
| **Risk Alert System** | http://localhost:8509 | Cardio health monitoring |
| **API Server** | http://localhost:5000 | Backend health data |

---

## 📱 Data Flow

```
Apple Watch
    ↓
iPhone Health App
    ↓
iOS Shortcut
    ↓
POST /api/upload (http://localhost:5000)
    ↓
healthkit_api_server.py
    ↓
app_final.py (8508) + app_risk_alert.py (8509)
```

---

## 🔴 Alert Thresholds

### Overtraining Risk
| Score | Level | Action |
|-------|-------|--------|
| 0-20% | ✅ LOW | Continue training normally |
| 20-40% | ⚠️ MODERATE | Monitor closely, easier sessions |
| 40-60% | 🔴 HIGH | Reduce intensity, focus on recovery |
| 60-100% | 🚨 CRITICAL | 2-3 days complete rest, consult doctor |

### Heart Attack Risk (30-day)
| Score | Level | Action |
|-------|-------|--------|
| 0-15% | ✅ LOW RISK | Continue healthy lifestyle |
| 15-40% | ⚠️ MODERATE | Consult cardiologist for evaluation |
| 40-60% | 🔴 HIGH RISK | Urgent cardiology appointment needed |
| 60-100% | 🚨 CRITICAL RISK | Seek immediate medical evaluation |

---

## 💡 Example Scenarios

### Scenario 1: Overtraining
```
✗ HRV: 35 ms (LOW)
✗ Heart Rate: 92 bpm (ELEVATED)
✓ Steps: 15,000 (normal)

Overtraining Risk: 55% (HIGH)
Recommendation: Reduce intensity, focus on recovery
```

### Scenario 2: Normal Recovery
```
✓ HRV: 65 ms (GOOD)
✓ Heart Rate: 62 bpm (OPTIMAL)
✓ Steps: 8,000 (light activity)

Overtraining Risk: 5% (LOW)
Recommendation: Excellent recovery status
```

### Scenario 3: Cardiac Risk
```
✗ HRV: 28 ms (CRITICAL)
✗ Heart Rate: 105 bpm (ELEVATED)
✓ Smoking: 0 cigarettes
✗ Age: 55 years

30-Day Heart Attack Risk: 52%
Recommendation: SEEK IMMEDIATE MEDICAL EVALUATION
```

---

## 📡 API Endpoints for Risk Analysis

### Calculate Overtraining Risk
```bash
POST /api/risk/overtraining
Content-Type: application/json

{
  "heart_rate": 85,
  "hrv": 45,
  "steps": 18000
}

Response:
{
  "overtraining_risk": 55,
  "severity": "MODERATE",
  "reasons": [
    "Low HRV (45 ms) - recovery needed"
  ],
  "recommendation": "Reduce intensity, focus on recovery"
}
```

### Calculate Heart Attack Risk
```bash
POST /api/risk/heart-attack
Content-Type: application/json

{
  "heart_rate": 80,
  "hrv": 50,
  "age": 45,
  "diabetes": false,
  "smoking": 0
}

Response:
{
  "30day_heart_attack_risk": 18.5,
  "severity": "MODERATE",
  "risk_factors": [
    "Low HRV (50 ms) - autonomic imbalance"
  ],
  "recommendation": "Consult cardiologist for risk stratification"
}
```

### Get Combined Risk
```bash
GET /api/risk/combined

Response:
{
  "overtraining_risk": 45,
  "heart_attack_risk": 25,
  "combined_risk_score": 30.5,
  "overall_severity": "MODERATE"
}
```

---

## ⚠️ Medical Disclaimer

This application provides **educational risk assessments only** and should **NOT** be used as a substitute for professional medical advice.

- Always consult with a qualified cardiologist
- Seek emergency care for chest pain, severe shortness of breath, or cardiac symptoms
- This tool uses general population statistics
- Individual risk may differ significantly from predictions

**Emergency: Call 911 or your local emergency number immediately**

---

## 🔧 Technical Stack

- **Frontend:** Streamlit 1.32+
- **Backend:** Flask 3.1.3 with CORS
- **Data Source:** Apple Watch (via iPhone Shortcut)
- **Real-time Metrics:** Heart Rate, HRV, Steps, Active Energy
- **Analysis:** Frameingham Risk Score (adapted)
- **Visualization:** Plotly interactive charts

---

## 📝 Setup Checklist

- [ ] Clone project from GitHub
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create iOS Shortcut for health data (see QUICK_SHORTCUT.md)
- [ ] Start API server: `python healthkit_api_server.py`
- [ ] Start main dashboard: `streamlit run app_final.py`
- [ ] Start risk alert: `streamlit run app_risk_alert.py --server.port=8509`
- [ ] Open in browser: http://localhost:8508 and http://localhost:8509
- [ ] Send first test data from iPhone Shortcut
- [ ] Monitor alerts and recommendations

---

## 🤝 Integration with Main Dashboard

Both apps work **independently** but share the same data source:

- **app_final.py (8508):** Full 7-tab coaching dashboard
- **app_risk_alert.py (8509):** Focused risk monitoring

They can run simultaneously and access the same health metrics from the API server.

---

## 📧 Support

For issues or questions:
1. Check that API server is running (`http://localhost:5000`)
2. Verify metrics are being received from iPhone
3. Review error logs in terminal
4. Check GitHub repository for updates

---

**Version:** 1.0.0  
**Last Updated:** March 14, 2026  
**Status:** ✅ Production Ready
