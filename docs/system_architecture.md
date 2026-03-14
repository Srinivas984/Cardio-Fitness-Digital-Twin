# System Architecture

## Cardio-Fitness Digital Twin

```
Wearable Data (Apple Watch / CSV)
          │
          ▼
┌─────────────────────┐
│  apple_health_parser │  Parses XML or CSV health exports
│  data_loader.py      │  Unified loading interface
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  preprocessing.py    │  HR bounds validation, HRV imputation,
│                      │  timestamp normalization, activity labeling
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ feature_engineering  │  avg/max/min HR, HRV stats, fatigue index,
│                      │  recovery index, activity load, HR zones
└─────────┬───────────┘
          │
     ┌────┴────────────────────────────────────┐
     │                                         │
     ▼                                         ▼
┌──────────────┐                    ┌──────────────────┐
│ cardiac_model │                   │  ces_score.py     │
│ (Digital Twin)│                   │  (CES 0–100)      │
│               │                   └────────┬─────────┘
│ HR dynamics   │                            │
│ Fatigue       │                            │
│ Recovery      │                   ┌────────▼─────────┐
│ HRV           │                   │  risk_detection   │
└──────┬────────┘                   │  Low/Mod/High     │
       │                            └──────────────────┘
       ▼
┌──────────────────┐
│ workout_simulator │  Generates activity profiles per strategy
│                   │  HIIT / Steady Cardio / Recovery / Tempo / Circuit
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  optimizer_ai.py  │  Simulates all strategies, picks best CES
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ prediction_engine │  30-day CES trajectory simulation
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│   app.py          │  Streamlit dashboard with 5 tabs
│   (Dashboard)     │
└──────────────────┘
```

## Data Flow

1. Raw wearable data loaded → standardized DataFrame
2. Preprocessing cleans + validates physiological bounds
3. Feature engineering extracts 15+ biomarkers
4. Digital twin calibrated to user's physiology
5. Optimizer simulates 5 strategies × full workout duration
6. CES computed per strategy; best selected
7. 30-day forecast generated for best strategy
8. Risk assessment flags overtraining markers
9. All results rendered in interactive dashboard
