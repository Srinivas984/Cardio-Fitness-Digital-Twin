"""
Mobile Health Input Dashboard
Access from iPhone to quickly input Apple Watch metrics
Sends data directly to Windows app in real-time
"""

from flask import Flask, render_template_string, request, jsonify
import requests
import json

app = Flask(__name__)

# HTML form for iPhone
MOBILE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apple Watch Metrics Input</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            color: #fff;
            padding: 16px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        
        h1 {
            text-align: center;
            margin-bottom: 8px;
            font-size: 24px;
            color: #ff3b30;
        }
        
        .subtitle {
            text-align: center;
            color: #999;
            margin-bottom: 24px;
            font-size: 14px;
        }
        
        .input-group {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
        }
        
        label {
            display: block;
            font-size: 14px;
            margin-bottom: 8px;
            color: #aaa;
            font-weight: 500;
        }
        
        input[type="number"] {
            width: 100%;
            padding: 12px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.05);
            color: #fff;
            font-size: 16px;
            font-weight: bold;
        }
        
        input[type="number"]:focus {
            outline: none;
            border-color: #ff3b30;
            background: rgba(255, 255, 255, 0.08);
        }
        
        .input-unit {
            display: inline-block;
            margin-left: 8px;
            color: #999;
            font-size: 14px;
        }
        
        button {
            width: 100%;
            padding: 14px;
            background: #ff3b30;
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 16px;
            font-weight: bold;
            margin-top: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        button:active {
            background: #e63027;
        }
        
        .status {
            text-align: center;
            margin-top: 12px;
            padding: 12px;
            border-radius: 8px;
            font-size: 14px;
            display: none;
        }
        
        .status.success {
            background: rgba(52, 211, 153, 0.2);
            color: #34d399;
            display: block;
        }
        
        .status.error {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            display: block;
        }
        
        .info {
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 16px;
            font-size: 13px;
            line-height: 1.6;
            color: #93c5fd;
        }
        
        .hr-zone {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-top: 8px;
            font-size: 12px;
        }
        
        .zone-badge {
            background: rgba(255, 255, 255, 0.1);
            padding: 6px;
            border-radius: 6px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>❤️ Apple Watch Metrics</h1>
        <p class="subtitle">Quick entry from your iPhone</p>
        
        <div class="info">
            📱 Open this on your iPhone and enter your Apple Watch metrics.
            They'll appear live in your Cardio Digital Twin dashboard on Windows!
        </div>
        
        <form id="metricsForm">
            <div class="input-group">
                <label>Heart Rate <span class="input-unit">bpm</span></label>
                <input type="number" id="heart_rate" name="heart_rate" min="40" max="200" placeholder="e.g. 85" required>
                <div class="hr-zone">
                    <div class="zone-badge">Zone 1: 100-120</div>
                    <div class="zone-badge">Zone 2: 120-140</div>
                    <div class="zone-badge">Zone 3: 140-160</div>
                    <div class="zone-badge">Zone 4: 160-180</div>
                </div>
            </div>
            
            <div class="input-group">
                <label>HRV (Heart Rate Variability) <span class="input-unit">ms</span></label>
                <input type="number" id="hrv" name="hrv" min="0" max="200" step="0.1" placeholder="e.g. 42.5">
            </div>
            
            <div class="input-group">
                <label>Blood Oxygen (SpO₂) <span class="input-unit">%</span></label>
                <input type="number" id="oxygen" name="oxygen" min="80" max="100" step="0.1" placeholder="e.g. 97.8">
            </div>
            
            <div class="input-group">
                <label>Steps <span class="input-unit">count</span></label>
                <input type="number" id="steps" name="steps" min="0" max="50000" placeholder="e.g. 8234">
            </div>
            
            <div class="input-group">
                <label>Active Energy <span class="input-unit">kcal</span></label>
                <input type="number" id="energy" name="energy" min="0" max="2000" step="1" placeholder="e.g. 345">
            </div>
            
            <button type="submit">✅ Send to Windows App</button>
            
            <div id="status" class="status"></div>
        </form>
    </div>
    
    <script>
        document.getElementById('metricsForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const statusDiv = document.getElementById('status');
            const data = {
                heart_rate: parseInt(document.getElementById('heart_rate').value),
                hrv: parseFloat(document.getElementById('hrv').value) || null,
                oxygen: parseFloat(document.getElementById('oxygen').value) || null,
                steps: parseInt(document.getElementById('steps').value) || null,
                energy: parseInt(document.getElementById('energy').value) || null
            };
            
            try {
                const response = await fetch('/api/submit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                statusDiv.className = 'status success';
                statusDiv.textContent = '✅ Data sent! Check your Windows app';
                
                // Reset form
                document.getElementById('metricsForm').reset();
                
                // Hide message after 2 seconds
                setTimeout(() => {
                    statusDiv.className = 'status';
                }, 2000);
                
            } catch (error) {
                statusDiv.className = 'status error';
                statusDiv.textContent = '❌ Error sending data: ' + error.message;
            }
        });
    </script>
</body>
</html>
"""


@app.route('/', methods=['GET'])
def index():
    """Serve mobile input form"""
    return render_template_string(MOBILE_HTML)


@app.route('/api/submit', methods=['POST'])
def submit_metrics():
    """Receive metrics from iPhone and forward to main API"""
    try:
        data = request.get_json()
        
        # Send to main API server
        api_response = requests.post(
            'http://localhost:5000/api/upload',
            json=data,
            timeout=2
        )
        
        return jsonify({
            "status": "✅ Metrics received",
            "data": data,
            "message": "Data sent to Cardio Digital Twin"
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "❌ Error",
            "error": str(e)
        }), 400


@app.route('/api/status', methods=['GET'])
def status():
    """Check connection status"""
    try:
        response = requests.get('http://localhost:5000/api/iphone', timeout=2)
        is_connected = response.json().get('status') == '✅ iPhone connected'
        return jsonify({
            "mobile_form": "✅ Running on port 5001",
            "main_api": "✅ Connected" if is_connected else "⏳ Waiting for data",
            "instructions": "Open http://your-windows-ip:5001 on your iPhone"
        }), 200
    except:
        return jsonify({
            "mobile_form": "✅ Running on port 5001",
            "main_api": "❌ Main API not responding"
        }), 200


if __name__ == '__main__':
    print("\n" + "="*60)
    print("📱 MOBILE HEALTH INPUT DASHBOARD")
    print("="*60 + "\n")
    print("✅ Open on iPhone: http://192.168.64.217:5001\n")
    print("📊 Data will appear live in Cardio Digital Twin!\n")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=False)
