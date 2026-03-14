# ⚡ Quick Reference: Cardio Risk Monitoring

## 🚀 Start Everything in 30 Seconds

**PowerShell:**
```powershell
.\RUN_ALL.ps1
```

**Then open:**
- Main Dashboard: http://localhost:8508
- Risk Alert: http://localhost:8509

---

## 📊 Dashboard Quick Reference

### Main Dashboard (Port 8508)
| Tab | Use Case |
|-----|----------|
| 📱 Live Coach | Real-time metrics from Apple Watch |
| 🎯 Adaptive Workouts | Personalized training plans |
| 💪 Smart Coaching | AI-powered guidance |
| 📈 Trends & Analytics | 30-day performance review |
| 🏥 Cardiac Health | Heart condition analysis |
| ⚡ Risk Detection | Arrhythmia/AFib detection |
| 🎨 Settings | Profile & preferences |

### Risk Alert System (Port 8509)
| Section | Metric |
|---------|--------|
| 📊 Vital Signs | HR, HRV, Steps, Calories |
| ⚡ Overtraining | Recovery status & fatigue |
| 🚨 Heart Attack Risk | 30-day cardiac event probability |
| 📈 Trends | 30-day risk projection |
| 💡 Recommendations | Medical action items |

---

## 🟢 Healthy Ranges

```
✅ Good Status:
   HR: 60-80 bpm
   HRV: 60-100 ms
   Steps: 8,000-15,000
   Energy: 100-500 kcal

⚠️ Caution Zone:
   HR: 80-100 bpm
   HRV: 40-60 ms
   Steps: 15,000-20,000
   Energy: 500-800 kcal

🔴 Concerning:
   HR: >100 bpm
   HRV: <40 ms
   Steps: >20,000
   Energy: >800 kcal
```

---

## 📱 iPhone Shortcut Data

Send this every minute:
```json
{
  "heart_rate": 72,
  "steps": 2500,
  "active_energy": 150
}
```

**Endpoint:** `POST http://<LAPTOP_IP>:5000/api/upload`

---

## 🚨 When to Seek Medical Care

### Immediate (Call 911):
- Chest pain or pressure
- Severe shortness of breath
- Heart Attack Risk > 70% + symptoms
- Loss of consciousness

### Urgent (Go to ER):
- Heart Attack Risk > 60%
- Overtraining Risk 100% with symptoms
- HR consistently > 120 bpm at rest
- Severe dizziness or syncope

### Routine (Book Appointment):
- Heart Attack Risk 30-40%
- Overtraining Risk 40-60%
- Persistent elevated HR (80-100)
- Low HRV (<50ms) for >1 week

---

## 💡 Quick Tips

1. **Check Daily** - Risk changes with stress, sleep, training
2. **Monitor Trends** - Single reading less important than patterns
3. **HRV is Key** - Best predictor of cardiac health
4. **Rest Matters** - 8+ hours sleep improves HRV greatly
5. **Stress Management** - Meditation/yoga reduces HR & improves HRV

---

## 🔄 Typical Health Metrics Flow

```
Time    HR    HRV    Risk    Status
08:00   58    75     5%      ✅ Excellent
09:00   72    68     8%      ✅ Good
12:00   85    52     25%     ⚠️ Monitor
16:00   92    38     50%     🔴 High
20:00   65    70     12%     ✅ Recovered
```

---

## 📡 API Testing

```powershell
# Test API Server
curl http://localhost:5000/api/metrics

# Send test data
$data = @{
    heart_rate = 72
    steps = 5000
    active_energy = 150
} | ConvertTo-Json

curl -X POST http://localhost:5000/api/upload `
     -ContentType "application/json" `
     -Body $data

# Check combined risk
curl http://localhost:5000/api/risk/combined
```

---

## 🐛 Troubleshooting

### Apps won't start
```powershell
# Kill old processes
Get-Process python* | Stop-Process -Force
# Then run: .\RUN_ALL.ps1
```

### Port already in use
```powershell
# Find what's using port (example: 8509)
netstat -ano | findstr :8509
# Kill process: taskkill /PID <PID> /F
```

### No data from iPhone
1. Check iPhone Shortcut is running
2. Verify laptop IP in Shortcut URL
3. Check both on same WiFi
4. Test: `curl http://localhost:5000/api/metrics`

### Risk scores seem high
- May indicate actual health concern
- Seek medical evaluation if consistent
- Check age/comorbidity settings in Risk Alert sidebar

---

## 📚 Files Overview

```
.
├── app_final.py              # Main 7-tab dashboard (8508)
├── app_risk_alert.py         # Risk alert system (8509)
├── healthkit_api_server.py   # Backend API (5000)
├── RUN_ALL.ps1               # Start all services
├── RUN_ALL.bat               # Windows batch launcher
├── QUICK_SHORTCUT.md         # iPhone setup guide
├── RISK_ALERT_README.md      # Detailed risk docs
└── data/                      # Health data files
```

---

## ⚡ Performance Tips

- Use high-quality WiFi for iPhone Shortcut
- Minimal background apps for accurate metrics
- Wear Apple Watch snugly for better sensors
- Sync every 1-5 minutes for fresh data
- View dashboards on same network for best responsiveness

---

**Last Updated:** March 14, 2026
**Version:** 1.0.0
**Status:** ✅ Ready for Deployment
