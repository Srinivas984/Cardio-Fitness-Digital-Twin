# Apple Watch Integration Guide

## Overview
The Cardio Digital Twin app can now integrate with your Apple Watch to stream real-time health data (heart rate, HRV, oxygen, steps, calories, sleep) directly into the coaching system.

---

## Prerequisites

### 1. **Apple Watch Requirements**
- ✅ Apple Watch Series 3 or newer
- ✅ Running watchOS 8.0 or later
- ✅ Bluetooth enabled
- ✅ iPhone with iOS 15+

### 2. **iPhone Setup**
- ✅ Health app installed (comes with iOS)
- ✅ Allow app permissions for health data
- ✅ iCloud account signed in
- ✅ WiFi or cellular connection

### 3. **Computer Running the App**
- ✅ macOS 11+, Windows 10+, or Linux
- ✅ Python 3.8+
- ✅ Streamlit installed
- ✅ Same network as iPhone (for local sync)

---

## Setting Up HealthKit Integration

### **Step 1: Enable Health Data Collection (iPhone)**

1. Open **Health app** on iPhone
2. Go to **Devices** → Your Apple Watch
3. Make sure **Health Sharing** is ON
4. Enable these data types:
   - ✅ Heart Rate
   - ✅ Resting Heart Rate
   - ✅ Heart Rate Variability (HRV)
   - ✅ Blood Oxygen
   - ✅ Steps
   - ✅ Active Energy
   - ✅ Sleep
   - ✅ Workouts

### **Step 2: Configure Health App Privacy**

1. **Health** → **Authorization** (or **Apps** → [App Name])
2. Grant permissions for:
   - Heart Rate (Read & Write)
   - Calories (Read & Write)  
   - Sleep (Read)
   - Workouts (Read & Write)

### **Step 3: Install Companion App (macOS/Windows)**

```bash
# Clone or download the Cardio Digital Twin repository
cd cardio_digital_twin

# Install required Python packages
pip install -r requirements.txt
```

Required packages:
```
streamlit>=1.32.0
plotly>=5.18.0
pandas>=2.0.0
numpy>=1.24.0
# For HealthKit integration:
healthkit-python>=0.1.0  # (if using macOS)
# For Windows/Linux: Use REST API or local sync
```

---

## Enabling Real Data (Not Demo Mode)

### **Option A: macOS with Native HealthKit API**

1. **Edit** `healthkit_connector.py`:

```python
# Change this:
connector = HealthKitConnector(use_demo_mode=True)

# To this:
connector = HealthKitConnector(use_demo_mode=False)
```

2. **Install HealthKit library**:
```bash
pip install healthkit
```

3. **Configure HealthKit authentication**:
```python
# In healthkit_connector.py, uncomment:
def _initialize_healthkit(self):
    from healthkit import HealthKit
    self.hk = HealthKit()
    self.is_authenticated = self.hk.authenticate()
```

### **Option B: Windows/Linux with HealthKit Cloud Sync**

Since HealthKit is Apple-only, use cloud sync:

1. **Set up iCloud integration**:
   - Enable **iCloud Health Backup** on iPhone
   - Sign in with same Apple ID on computer

2. **Install iCloud library**:
```bash
pip install pyicloud
```

3. **Authenticate**:
```python
from pyicloud import PyiCloudService

# In healthkit_connector.py:
user_id = "your_apple_id@icloud.com"
password = "your_app_specific_password"  # Generate in iCloud settings
icloud = PyiCloudService(user_id, password)
```

### **Option C: REST API Integration (Recommended for Hackathons)**

Use a REST API server to bridge iPhone and app:

1. **Install server package**:
```bash
pip install flask flask-cors
```

2. **Start local server** (before running Streamlit):
```bash
python healthkit_api_server.py
# Server runs at http://localhost:5000
```

3. **Connect app to server**:
```python
# In healthkit_connector.py:
HEALTHKIT_API_URL = "http://localhost:5000/api"
```

---

## Running the App with Real Apple Watch Data

### **Step 1: Start Backend Server (if using Option C)**

```bash
# Terminal 1
cd cardio_digital_twin
python healthkit_api_server.py
# Runs at http://localhost:5000
```

### **Step 2: Start Streamlit App**

```bash
# Terminal 2
cd cardio_digital_twin
streamlit run app_final.py
# Opens at http://localhost:8506
```

### **Step 3: Go to "Live Coach" Tab**

1. Click **📱 Live Coach** (2nd tab)
2. Check **Apple Watch Connection Status**
3. You should see:
   - ✅ "Apple Watch Series X Connected"
   - 📊 Live metrics (HR, HRV, O₂, steps, calories)
   - 🟢 "Signal: Excellent"
   - ⏰ "Last Sync: Just now"

### **Step 4: Start a Live Coaching Session**

1. Select **Workout Type** (Running, Cycling, Strength, HIIT, Recovery)
2. Set **Duration** (15-180 min)
3. Choose **Target Zone** (Recovery to Max)
4. Click **▶️ START LIVE COACHING**

Watch the real-time coaching cues appear on your screen!

---

## Testing with Demo Data

If you don't have Apple Watch yet, the app runs perfectly in **demo mode**:

```bash
streamlit run app_final.py
# Already configured to use realistic synthetic data
```

The demo generates:
- ✅ Realistic HR patterns (varies by time of day)
- ✅ Recovery-based HRV (higher in morning, lower at night)
- ✅ Activity-realistic step counts
- ✅ Sleep data with quality scores
- ✅ Live workout simulation

**Use demo mode to:**
- Test coaching features
- Demo at hackathons
- Verify UI/UX
- Prepare for real data

---

## Troubleshooting

### **Problem: "Apple Watch Disconnected"**

**Solutions:**
1. Check iPhone is on same WiFi as computer
2. Verify Health app has app permissions enabled
3. Check Bluetooth is on
4. Restart iPhone Health app
5. Check Health data is recent (< 5 minutes old)

### **Problem: "No data showing"**

**Solutions:**
1. Ensure Apple Watch is actively syncing
2. Go for a 5-minute walk to generate fresh data
3. Check timestamp in Health app
4. Restart Streamlit app

### **Problem: "Authentication failed"**

**Solutions:**
1. Verify Apple ID credentials
2. Check app-specific password (not regular password)
3. Enable "Allow Less Secure Apps" if needed
4. Regenerate authentication token

### **Problem: "Demo mode working but real data won't sync"**

**Solutions:**
1. Start with Option C (REST API) - most reliable
2. Verify server is running: `curl http://localhost:5000/health`
3. Check firewall allows localhost:5000
4. View server logs for error details

---

## Real-Time Coaching Features (Active with Real Data)

Once connected, you get:

### 📊 **Live Metrics Dashboard**
- Heart Rate (bpm) - real-time
- HRV (ms) - recovery indicator
- Blood Oxygen (%)
- Steps today
- Active Energy burned

### 🎯 **Real-Time Coaching Cues**
- "🔼 PUSH - Pick up pace"
- "✅ PERFECT PACE - Hold steady"
- "🔽 EASE - Back off intensity"
- Personalized based on YOUR metrics

### ⚡ **Adaptive Intensity Adjustments**
- Suggest "Increase by 5-10%"
- Recommend "Maintain current effort"
- Alert "Decrease immediately"

### ⚠️ **Safety Alerts**
- 🔴 CRITICAL: Reduce immediately
- 🟡 HIGH: Monitor closely
- ℹ️ MEDIUM: Consider backing off

### 📈 **Live Performance Graphs**
- Heart Rate during workout
- Training zone distribution
- Pace/power over time
- Calories burned

---

## Advanced: Building Custom Apple Watch App

To send notifications directly to Apple Watch:

```python
# In live_coach.py - already implemented!
connector.send_notification(
    title="Push!",
    message="Pick up pace 🔼",
    urgency="high"
)
```

This sends to Apple Watch via:
1. iPhone Health app notification
2. Apple Watch native notification
3. Voice guidance (text-to-speech)

---

## Demo Scenario (For Hackathon)

If you don't have real data ready:

1. **Open app** → Already in demo mode
2. **Go to "📱 Live Coach"** tab
3. **Click "START LIVE COACHING"**
4. Watch realistic metrics stream in real-time
5. See coaching cues adapt to "athlete" performance
6. Demo entire 30-minute "workout" in ~2 minutes

Perfect for showing judges the system in action! ✅

---

## Next Steps

1. ✅ **Immediate**: Test with demo data
2. 🔄 **Today**: Set up HealthKit on your iPhone
3. 📱 **Tomorrow**: Enable real Apple Watch sync
4. 🚀 **Hackathon**: Impress with live data!

Questions? Check the code in:
- `healthkit_connector.py` - Data connection
- `live_coach.py` - Coaching logic
- `adaptive_workouts.py` - Adaptive algorithms

Good luck! 🏃‍♂️⚽🚴‍♀️
