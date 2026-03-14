# ⚡ Simple Apple Watch Shortcut Setup

## Get Heart Rate, Steps + Active Energy

On your **iPhone**, in the **Shortcuts** app:

### Step 1: Create New Shortcut
- Tap **"+"** button
- Search for: **"Get health samples"**

### Step 2: Add 3 Health Samples

Add exactly these 3 actions (search for **"Get health samples"** for each):

| # | Action | Setting |
|---|--------|----------|
| 1️⃣ | **Heart Rate** | Quantity → Heart Rate → Most Recent |
| 2️⃣ | **Steps** | Quantity → Step Count → Today |
| 3️⃣ | **Active Energy** | Quantity → Active Energy → Today |

That's it! Don't add anything else.

### Step 3: Post to API

Add: **"Post"** action

```
URL: http://192.168.64.217:5000/api/upload

Method: Post

Headers:
  Content-Type: application/json

Body (Raw JSON):
{
  "heart_rate": [Heart Rate result],
  "steps": [Steps result],
  "active_energy": [Active Energy result]
}
```

### Step 4: Auto-Run Every Minute

1. Go to **Automation** tab
2. Tap **"+"** → **"Create Personal Automation"**
3. Select **"Time of Day"**
4. Set: **Every 1 Minute**
5. Add action: **"Run Shortcut"** → Select your shortcut
6. **Turn OFF:** "Ask Before Running"
7. **Turn OFF:** "Notify When Run"
8. Tap **"Done"**

---

## ✅ Verify It Works

1. Your Shortcut should auto-run every 1 minute
2. Open Windows app at `http://localhost:8508`
3. Go to **📱 Live Coach** tab
4. You should see **"iPhone Connected (Live)"** ✅
5. Heart rate and steps will update live
6. **HRV is automatically calculated** from your heart rate

---

## 📊 Valid Data Ranges

| Metric | Min | Max |
|--------|-----|-----|
| **Heart Rate** | 30 | 220 |
| **Steps** | 0 | 100,000 || **Active Energy** | 0 | 5,000 |
**That's all you need!**

---

## 🚨 Troubleshooting

### "Missing heart_rate" or "Missing steps"
→ Your Shortcut didn't send one of the values
→ Make sure you added BOTH health samples

### "Apple Watch Disconnected"
→ Automation stopped
→ Open Shortcuts and manually tap ▶️ to run it

### Still not working?
1. Keep Shortcuts app in background (don't close it)
2. Check WiFi is connected
3. Try running Shortcut manually once with ▶️ button
4. Wait 60 seconds for automation to trigger

---

**Your Windows IP: `192.168.64.217:5000`**
