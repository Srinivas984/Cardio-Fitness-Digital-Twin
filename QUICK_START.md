# ⚡ QUICK START: Apple Watch Integration

## 🚀 Fastest Way (Demo Mode - Right Now)

```bash
# Just run it!
cd cardio_digital_twin
streamlit run app_final.py
```

Then:
1. Open http://localhost:8506
2. Click "📱 Live Coach" tab
3. Click "▶️ START LIVE COACHING"
4. Watch coaching cues appear in real-time!

✅ Works with realistic synthetic data - perfect for testing/demo!

---

## 📱 Two Ways to Use Real Apple Watch Data

### **Option A: macOS (Simplest)**
```bash
# 1. Make Apple Watch data available
python setup_healthkit.py
# Choose option "2: macOS HealthKit"

# 2. Run app
streamlit run app_final.py
```
✅ Direct connection, fastest, lowest latency

### **Option B: Any Computer + iPhone (Most Flexible)**
```bash
# Terminal 1 - Start server
python healthkit_api_server.py

# Terminal 2 - Start app  
streamlit run app_final.py
```
✅ Works on Windows, Mac, Linux - iPhone syncs via WiFi

---

## 📋 Setup Checklist

- [ ] Apple Watch Series 3+ with watchOS 8+
- [ ] iPhone with Health app (built-in)
- [ ] Both on same WiFi (if using Option B)
- [ ] Latest Python 3.8+
- [ ] `pip install -r requirements.txt`

---

## ❓ How It Works

```
Apple Watch
    ↓ (via iPhone)
Health App (iPhone)
    ↓ (via HealthKit/iCloud/WiFi)
Cardio Twin Server/API
    ↓
Streamlit Web App
    ↓
Live Coaching!
```

---

## 🎯 In the App

**📱 Live Coach Tab:**

1. **Watch Status**: Shows connection, signal, last sync
2. **Live Metrics**: 
   - ❤️ HR (real-time from Apple Watch)
   - 🫀 HRV (recovery indicator)
   - 🫁 O₂ Saturation
   - 👣 Steps
   - 🔥 Active Energy

3. **Coaching**:
   - Pick workout type
   - Set duration & zone
   - Press START
   - Get real-time coaching!

---

## 🆘 Troubleshooting

**"Apple Watch Disconnected"**
→ Check iPhone Health app has data, restart WiFi

**"No data showing"**
→ Go for 5-min walk, check timestamp is recent

**"Need to enable demo mode quickly?"**
→ Run: `streamlit run app_final.py` (already in demo!)

**"Want detailed setup?"**
→ Read: `APPLE_WATCH_SETUP.md`

**"Need interactive setup?"**
→ Run: `python setup_healthkit.py`

---

## 🏃‍♂️ Typical Workout Flow

1. Open app → **📱 Live Coach** tab
2. See live metrics update every second
3. Pick **Running** (or your activity)
4. Set **45 minutes**, **Zone 2** (aerobic)
5. Click **START**
6. Watch coaching cues:
   - "🔼 PUSH - Pick up pace"
   - "✅ PERFECT PACE"
   - "🔽 EASE - Back off"
7. Real-time HR graph updates
8. Session summary when done

---

## 💡 Demo vs Real Data Comparison

| Feature | Demo | Real |
|---------|------|------|
| HR updates | Every 30 sec | Every 5 sec |
| Data accuracy | Realistic patterns | Your actual metrics |
| Coaching | Adaptive patterns | Personalized to YOU |
| Setup time | 0 sec | 5-10 min |
| No watch needed | ✅ YES | ❌ Needs Apple Watch |

---

## 🎓 Understanding the Data

**Heart Rate (HR)**
- Normal resting: 60-100 bpm
- During exercise: varies by intensity
- When coaching says "PUSH" → increase intensity

**HRV (Heart Rate Variability)**
- High (>50ms) = Well recovered
- Normal (35-50ms) = OK to train
- Low (<35ms) = Needs rest

**Training Zones**
- Zone 1: Recovery (easy walking)
- Zone 2: Aerobic (conversational pace)
- Zone 3: Tempo (harder but sustainable)
- Zone 4: Threshold (near maximum effort)
- Zone 5: Maximum (all-out sprint)

---

## 🚀 Ready?

```bash
# Just run it!
streamlit run app_final.py
```

Then go to **📱 Live Coach** tab and start!

Questions? Check `APPLE_WATCH_SETUP.md` for details.

Happy coaching! 🏃‍♀️💪
