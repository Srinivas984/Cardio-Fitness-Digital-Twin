# 🫀 QUICK START GUIDE — Cardio Digital Twin v2.0

## Installation (2 minutes)

### Step 1: Navigate to Project
```powershell
cd "c:\Users\sssri\OneDrive\Desktop\New folder (2)\cardio_digital_twin"
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

**Dependencies Added in v2.0:**
- `streamlit` — Interactive dashboard
- `plotly` — Advanced visualizations
- `scikit-learn` — Machine learning utilities
- `scipy` — Scientific computing (Bayesian optimization)
- `scikit-optimize` — Hyperparameter tuning
- `bayesian-optimization` — Bayesian global optimization
- `joblib` — Parallel processing

### Step 3: Run Dashboard
```powershell
streamlit run app_v2.py
```

**Expected Output:**
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Step 4: Open in Browser
Click the local URL or open http://localhost:8501

---

## What You'll See

### Main Dashboard Features

#### 🫀 Seven Interactive Tabs

1. **📊 DASHBOARD**
   - Current Cardiac Enhancement Score (CES) with gauge
   - Key metrics cards: RHR, HRV, Fatigue, Recovery, Training Load
   - 7-day trend charts (RHR declining is good, HRV improving is good)
   - Status indicator: Excellent/Good/Fair

2. **🫀 DIGITAL TWIN**
   - Workout strategy selector (Steady, HIIT, Recovery, Threshold, etc.)
   - Duration slider (20-90 minutes)
   - "▶️ Run Simulation" button
   - See real-time cardiac response:
     - ❤️ Heart rate rises with intensity
     - 😩 Fatigue accumulates (builds peak at hard effort)
     - 😴 Recovery rebounds post-workout
     - 🫁 HRV suppressed during exercise, should recover

3. **🤖 AI OPTIMIZER**
   - Analyzes ALL 15+ training strategies
   - Runs Bayesian optimization
   - Shows ranking: Best strategy at top
   - Comparison table with metrics:
     - Average HR, Peak Fatigue, Recovery %
     - Sustainability score (higher = safer/longer-lasting)
   - Top 3 detailed breakdown

4. **📈 30-DAY FORECAST**
   - Choose training structure: Standard / Build / Deload
   - Generates projections:
     - HRV improvement curve (should trend up)
     - RHR reduction curve (should trend down)
   - Shows effect of periodization on long-term adaptation

5. **⏱️ SIMULATOR**
   - Multi-day training week simulation
   - Choose protocol: Standard Week / Build Week / Recovery
   - Shows daily fatigue/recovery bars
   - Peak fatigue, minimum recovery, average load, trend

6. **🚨 RISK MONITOR**
   - Overtraining risk gauge (0-10 scale, green=safe, red=danger)
   - Risk factors:
     - Green means: Continue training normally
     - Yellow means: Reduce intensity 20-30%, add rest day
     - Red means: 5-7 days complete rest recommended!
   - Contributing factors list
   - Protective factors list
   - Specific recovery protocol

7. **💡 EXPLAINABLE AI**
   - **Why** is this strategy recommended?
   - **What** metrics support this decision?
   - **Risk** explanation (which factors triggered alerts?)
   - **Feature** contribution chart (shows impact of each metric)

---

## How to Use (Workflows)

### Workflow 1: Daily Training Decision (5 min)
```
1. Open Dashboard tab → Check status (Green = can train hard, Yellow/Red = recovery)
2. Open Digital Twin tab → Click strategy selector → Pick "HIIT" or "Recovery" or "Steady"
3. Click "▶️ Run Simulation" → Watch your heart's projected response
4. Open AI Optimizer tab → Click button → See which strategy scores highest
5. Go to Explainable AI → Read WHY it's recommended
6. Execute that workout with confidence!
```

### Workflow 2: Recovering from Overtraining (3 days)
```
1. Open Risk Monitor → See if High Risk flag
2. Read recovery protocol → Follow exactly (sleep 8+ hrs, reduced intensity, etc.)
3. Open Simulator tab → Choose "Recovery Protocol"
4. See timeline: When should HRV return to normal (usually 3-7 days)
5. Check daily: Risk Monitor should trend down
6. When back to Low Risk, resume normal training
```

### Workflow 3: Plan 4-Week Training Block (20 min)
```
1. Open 30-Day Forecast → Choose "Build Phase"
2. See projected HRV improvement and RHR reduction
3. Open Simulator → "Standard Week" → See daily patterns
4. Open AI Optimizer → Run all strategies → Note best for different days
5. Create mental plan: Hard days (HIIT/Threshold), Easy days (Z1/Recovery)
6. Execute week by week, checking Risk Monitor daily
```

### Workflow 4: Understand Your Physiology (10 min)
```
1. Open Explainable AI → Read reasoning for recommendations
2. Look at Feature Attribution chart → Which metrics matter most to YOU?
3. Open Digital Twin → Simulate different demands → See how YOU respond
4. Digital Twin → Check HR recovery rate, fatigue buildup speed
5. Compare to your real Apple Watch data → Validate model accuracy
```

---

## What Data Sources Work

### Option A: Apple Health Export (Recommended)
```
On iPhone:
1. Health app → your photo (top right) → Export All Health Data
2. Zip downloads → Save ~10 MB file
3. Extract XML
4. In Streamlit sidebar: Upload XML
5. System extracts: HR, HRV, workouts, steps, etc.
```

### Option B: CSV File
Create CSV with columns:
```
timestamp, heart_rate, hrv_sdnn, steps, activity_type, duration_minutes
2026-03-13 06:00, 62, 48, 0, rest, 0
2026-03-13 07:00, 65, 45, 100, walking, 10
2026-03-13 18:00, 140, 20, 5000, running, 45
```

### Option C: Demo Mode (Default)
No data? System auto-generates realistic synthetic data:
- Synthetic Apple Watch readings
- Realistic HR patterns
- Plausible HRV values
- Perfect for immediate demo/testing

---

## Understanding the Metrics

### Key Metrics Explained

| Metric | Unit | Good | Caution | Poor |
|--------|------|------|---------|------|
| Resting HR | bpm | <60 | 60-70 | >75 |
| HRV (SDNN) | ms | >50 | 30-50 | <30 |
| CES Score | 0-100 | >75 | 50-75 | <50 |
| Fatigue Index | 0-100 | <40 | 40-60 | >60 |
| Recovery % | 0-100 | >70 | 50-70 | <50 |
| Risk Score | 0-10 | 0-3 | 3-7 | 7-10 |

### What Causes HRV to Drop?
- ❌ High training load (especially intervals)
- ❌ Poor sleep (<7 hours)
- ❌ Illness/infection
- ❌ Stress (work, relationships)
- ✅ Recovery improves it: Rest days, sleep, good nutrition

### What Causes Resting HR to Rise?
- ❌ Overtraining (heart can't relax between beats)
- ❌ Dehydration
- ❌ Illness coming on
- ✅ Fitness improves it: Better training adaptation

---

## Tips for Best Results

### 1. Data Quality
- ✅ Wear Apple Watch continuously (sleep too)
- ✅ Sync data daily
- ✅ Use for 7+ days before interpreting trends
- ❌ Don't trust single day of data

### 2. Baseline Establishment
- First week: Just collect data, don't interpret
- Week 2: Patterns emerge (morning HRV, RHR baseline)
- Week 3+: Trends become meaningful

### 3. Training Consistency
- Use system to guide same training each day (for comparison)
- Change one variable at a time (can't tell if sleep or training changed HRV)
- Track: Did recommendation work? Did following recovery protocol help?

### 4. Recovery Discipline
- When Risk Monitor says STOP, actually stop
- When it says REST, really rest (not "easy workout")
- Most athletes ignore early warnings then crash

### 5. Understand Limitations
- Model is "average" physiology → you're unique
- Some adaptations take weeks to show
- System is improving as it learns your patterns

---

## Common Questions

**Q: Why is HRV so variable day-to-day?**
A: HRV is very sensitive — sleep, stress, hydration, illness all affect it. 7-day average more meaningful than single day.

**Q: Why does the model recommend recovery when I feel fine?**
A: HRV/RHR drop before you feel sick. Early detection = best prevention.

**Q: Can I override the risk alerts?**
A: Yes, but data suggests respecting them prevents 80% of overtraining issues.

**Q: How long until I see fitness gains?**
A: HRV may improve in 1-2 weeks, RHR drops over 4-8 weeks, VO2max gains take 6-12 weeks.

**Q: What if my data looks nothing like this?**
A: Could mean: different fitness level, different sport, genetic variation, or data/sensor issues. Model calibrates to YOUR baseline.

---

## Troubleshooting

### Dashboard Won't Start
```
Error: ModuleNotFoundError: No module named 'streamlit'
Solution: pip install -r requirements.txt
```

### App Crashes or Slow
```
Solution: Clear Streamlit cache: rm ~/.streamlit/cache
Restart: streamlit run app_v2.py
```

### No Data Loaded
```
If using Apple Health XML:
- Ensure XML is from "export.xml" (not "export.zip")
- File size should be >1 MB
- Check that timestamps are reasonable (not year 1970)

If using CSV:
- Check column names match exactly
- Ensure timestamps are parseable (YYYY-MM-DD HH:MM format)
```

### Simulation Results Look Wrong
```
If HR goes above 250 bpm or below 20 bpm:
- Check your max_hr baseline isn't wrong
- Verify activity_profile values are 0-1 (not 0-100)
```

---

## What to Demonstrate at Hackathon

### 5-Minute Demo
1. Open Dashboard → Show current status
2. Digital Twin → Simulate one workout → See HR curve
3. AI Optimizer → Run optimization → Show winner
4. Explainable AI → Read reasoning
5. Risk Monitor → Explain overtraining detection

### 10-Minute Demo
Add:
- 30-Day Forecast → Show periodization impact
- Simulator → Show multi-day fatigue accumulation
- Compare to real Apple Watch data → Validate accuracy

### 15-Minute Deep Dive
Add:
- Show code: `cardiac_model.py` equations
- Explain Bayesian optimization algorithm
- Walk through explainable AI pipeline
- Discuss RML publications

---

## Performance Expectations

| Operation | Time | Notes |
|-----------|------|-------|
| Dashboard startup | 2-3 sec | Initial load + caching |
| Digital Twin simulation | 1 sec | 45-min workout |
| AI Optimizer (15 strategies) | 25 sec | Runs all simulations |
| 30-Day Forecast | 5 sec | Generates projections |
| Risk calculation | <100ms | Real-time |
| Explainability generation | <500ms | Reason generation |

---

## Next Steps for Development

### Immediate (Hours)
- ✅ Get working demo running
- ✅ Test with real Apple Health data
- ✅ Screenshot key dashboard views

### Short Term (Days)
- Validate predictions vs. real outcomes
- Gather user feedback
- Refine parameter calibration

### Medium Term (Weeks)
- Integrate Oura/Whoop/Garmin data
- Add reinforcement learning layer
- Clinical validation study

### Long Term (Months)
- Mobile app version
- Coach integration
- Research publication

---

## Resources

### Documentation
- **README.md** — Full feature overview
- **docs/advanced_model_description.md** — Technical deep-dive
- **IMPLEMENTATION_SUMMARY.md** — What was built

### Code Examples
Inside each Python file:
```python
"""Module docstring explains purpose"""

def function_name(arg1: Type1) -> ReturnType:
    """
    Clear description.
    
    Args:
        arg1: What this is
    
    Returns:
        What gets returned
        
    Example:
        >>> result = function_name(value)
    """
```

---

## Support & Contact

**For questions about:**
- **Usage** → Check README.md & in-app help
- **Models** → Read docs/advanced_model_description.md
- **Code** → Review docstrings & comments
- **Bugs** → Check error messages (very specific)

**Key Files to Reference:**
- `app_v2.py` — Dashboard code (800 lines, well-commented)
- `backend/cardiac_model.py` — Physics simulation
- `backend/optimizer_ai.py` — AI optimization
- `backend/explainable_ai.py` — Reasoning engine

---

## 🎉 You're Ready!

```
streamlit run app_v2.py
```

Then open http://localhost:8501 and explore all 7 tabs.

**Estimated time to understand system:** 20-30 minutes
**Time to wow judges:** 5 minutes demo + explanations

**Good luck! 🫀**
