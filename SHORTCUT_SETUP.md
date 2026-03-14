# Apple Watch Shortcut Integration Guide

## ✅ What You'll Get
- **Live Apple Watch data** on your Windows app
- **Automatic updates** every 30-60 seconds
- **Accurate metrics** validated and displayed instantly
- Works on any iPhone with Apple Watch

---

## 📱 iOS Shortcut Setup (Step-by-Step)

### Part 1: Create the Shortcut

1. **Open Shortcuts app** on iPhone
2. Tap **"+"** to create new shortcut
3. Search for and add these actions IN ORDER:

#### Action 1: Get Heart Rate
```
Search: "Get health samples"
Set: Heart Rate
  └─ Category: Quantity
  └─ Quantity: Heart Rate
  └─ Sample Type: Most Recent
```
- Name the result: **"Get HR"**
- Add action: **"Extract values"** 
- Select: **"Value"**

#### Action 2: Get HRV  
```
Search: "Get health samples"
Set: Heart Rate Variability
  └─ Category: Quantity
  └─ Quantity: Heart Rate Variability
  └─ Sample Type: Most Recent
```
- Name the result: **"Get HRV"**

#### Action 3: Get Blood Oxygen (Optional - if your Watch supports it)
```
Search: "Get health samples"
Set: Blood Oxygen
  └─ Category: Quantity
  └─ Quantity: Blood Oxygen
  └─ Sample Type: Most Recent
```
- Name the result: **"Get O2"**

#### Action 4: Get Steps
```
Search: "Get health samples"
Set: Step Count
  └─ Category: Quantity
  └─ Quantity: Step Count
  └─ Sample Type: Today
```
- Name the result: **"Get Steps"**

#### Action 5: Get Active Energy
```
Search: "Get health samples"
Set: Active Energy Burned
  └─ Category: Quantity
  └─ Quantity: Active Energy Burned
  └─ Sample Type: Today
```
- Name the result: **"Get Energy"**

#### Action 6: Send Data to API
```
Search: "Post"
URL: http://192.168.64.217:5000/api/upload
Method: Post
Headers:
  - Key: Content-Type
  - Value: application/json

Request Body (JSON):
{
  "heart_rate": [Get HR converted to number],
  "hrv": [Get HRV converted to number],
  "oxygen": [Get O2 converted to number],
  "steps": [Get Steps converted to number],
  "energy": [Get Energy converted to number]
}
```

### Part 2: Set Up Automation

1. **Go to Automation** tab (in Shortcuts)
2. Tap **"+"** → **"Create Personal Automation"**
3. Select: **"Time of Day"**
4. Configure:
   - Start: **any time**
   - Repeats: **Every 1 Minute** ⭐ (as frequent as possible)
5. Tap: **"Next"**
6. Add action: **"Run Shortcut"** → Select your Shortcut name
7. Turn OFF: **"Ask Before Running"** ⭐
8. Turn OFF: **"Notify When Run"**
9. Tap: **"Done"**

### Part 3: Verify It Works

1. Your Shortcut should now run **automatically every minute**
2. Check your Windows app at `http://localhost:8508`
3. Go to **📱 Live Coach** tab
4. You should see: **"iPhone Connected (Live)"** ✅
5. Metrics should update every ~60 seconds

---

## 🔧 Troubleshooting

### "Apple Watch Disconnected"
- Check iPhone Bluetooth is ON
- Disable airplane mode
- Verify Health app permission in Settings → Privacy → Health → Your App

### Data shows 0s
- Check Shortcut automation is enabled
- Verify time automation is set to repeat (not just once)
- Run shortcut manually once to test

### Data validation errors
Check values are in valid ranges:
- **Heart Rate:** 30-220 bpm
- **HRV:** 0-300 ms
- **Blood Oxygen:** 70-100%
- **Steps:** 0-100,000
- **Active Energy:** 0-5,000 kcal

### "Stale data" warning
- Shortcut stopped running
- iPhone is locked or in low power mode
- Check if privacy permissions changed

---

## 📊 Valid Data Ranges

| Metric | Min | Max | Note |
|--------|-----|-----|------|
| Heart Rate | 30 bpm | 220 bpm | Must have |
| HRV | 0 ms | 300 ms | Optional |
| Blood Oxygen | 70% | 100% | Optional |
| Steps | 0 | 100,000 | Optional |
| Active Energy | 0 kcal | 5,000 kcal | Optional |

---

## 🚀 Tips for Best Results

✅ **Keep iOS Shortcuts app open** - automation runs better in foreground  
✅ **Enable WiFi** for reliable data sync  
✅ **Set repeating automation to 1 minute** - most frequent allowed  
✅ **Turn off battery saver** - it interferes with automations  
✅ **Grant Health app permission** - essential for reading data  

---

## 📱 Your Windows IP: `192.168.64.217:5000`

Use this URL in your Shortcut's Post request. If your Windows IP changes, update the Shortcut POST URL.

---

**All set?** Your Apple Watch data will now stream live to your Cardio Digital Twin! 🎯
