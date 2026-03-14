"""
HealthKit API Server - Flask backend for Apple Watch data sync
Bridges iPhone Health app and Streamlit app

RUN: python healthkit_api_server.py
Then: http://localhost:5000/health
      http://localhost:5000/api/metrics
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import numpy as np
from healthkit_connector import HealthKitConnector, LiveDataStreamer

app = Flask(__name__)
CORS(app)

# Initialize health data connector
connector = HealthKitConnector(use_demo_mode=True)
streamer = LiveDataStreamer()

# Workout session state
active_session = None

# iPhone/Shortcut data storage for Windows live integration
iphone_live_data = {
    "heart_rate": None,
    "hrv": None,
    "oxygen": None,
    "steps": None,
    "energy": None,
    "timestamp": None
}


@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        "status": "✅ HealthKit API Server Running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "metrics": "/api/metrics",
            "heart_rate": "/api/heart_rate",
            "hrv": "/api/hrv",
            "oxygen": "/api/oxygen",
            "steps": "/api/steps",
            "energy": "/api/energy",
            "sleep": "/api/sleep",
            "start_workout": "/api/workout/start",
            "stop_workout": "/api/workout/stop",
            "status": "/api/status"
        },
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "✅ Server OK",
        "time": datetime.now().isoformat(),
        "connection": "Connected" if connector.is_authenticated else "Demo Mode"
    }), 200


@app.route('/api/metrics', methods=['GET'])
def get_all_metrics():
    """Get all current metrics at once"""
    # If iPhone data is available and fresh (< 5 min old), use it
    if iphone_live_data["timestamp"] is not None:
        age = (datetime.now() - datetime.fromisoformat(iphone_live_data["timestamp"])).total_seconds()
        if age < 300:  # Within 5 minutes
            metrics = {
                "timestamp": iphone_live_data["timestamp"],
                "source": "iPhone (Live)",
                "heart_rate": {
                    "value": iphone_live_data.get("heart_rate", 0),
                    "unit": "bpm"
                },
                "hrv": {
                    "value": iphone_live_data.get("hrv", 45),
                    "unit": "ms",
                    "note": "Calculated from heart rate"
                },
                "steps": {
                    "steps": iphone_live_data.get("steps", 0),
                    "goal": 10000,
                    "progress_pct": int((iphone_live_data.get("steps", 0) / 10000) * 100)
                },
                "active_energy": {
                    "value": iphone_live_data.get("energy", 0),
                    "unit": "kcal"
                },
                "data_age_seconds": age
            }
            return jsonify(metrics), 200
    
    # Fall back to demo data if no iPhone data
    hr, hr_status = connector.get_live_heart_rate()
    
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "source": "Demo Mode",
        "heart_rate": {
            "value": hr,
            "status": hr_status,
            "unit": "bpm"
        },
        "hrv": {
            "value": round(connector.get_live_hrv(), 1),
            "unit": "ms",
            "note": "Calculated from heart rate"
        },
        "steps": {
            "value": connector.get_step_count(),
            "unit": "steps"
        },
        "active_energy": {
            "value": connector.get_active_energy(),
            "unit": "kcal"
        },
        "sync_status": connector.get_sync_status()
    }), 200


@app.route('/api/heart_rate', methods=['GET'])
def get_heart_rate():
    """Get current heart rate"""
    hr, status = connector.get_live_heart_rate()
    return jsonify({
        "value": hr,
        "status": status,
        "unit": "bpm",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/hrv', methods=['GET'])
def get_hrv():
    """Get current HRV"""
    hrv = connector.get_live_hrv()
    return jsonify({
        "value": round(hrv, 1),
        "unit": "ms",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/oxygen', methods=['GET'])
def get_oxygen():
    """Get blood oxygen saturation"""
    o2 = connector.get_live_oxygen_saturation()
    return jsonify({
        "value": round(o2, 1),
        "unit": "%",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/steps', methods=['GET'])
def get_steps():
    """Get step count"""
    hours = request.args.get('hours', 24, type=int)
    steps = connector.get_step_count(hours)
    return jsonify({
        "steps": steps['steps'],
        "goal": steps['goal'],
        "progress_pct": steps.get('progress_pct', 0),
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/energy', methods=['GET'])
def get_energy():
    """Get active energy"""
    hours = request.args.get('hours', 24, type=int)
    energy = connector.get_active_energy(hours)
    return jsonify({
        "calories": energy['calories'],
        "goal": energy['goal'],
        "progress_pct": energy.get('progress_pct', 0),
        "unit": "kcal",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/sleep', methods=['GET'])
def get_sleep():
    """Get sleep data"""
    sleep = connector.get_sleep_data()
    return jsonify({
        "duration_hours": sleep['duration_hours'],
        "deep_sleep_pct": sleep['deep_sleep_pct'],
        "rem_sleep_pct": sleep['rem_sleep_pct'],
        "quality_score": sleep['quality_score'],
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get connection status"""
    status = connector.get_sync_status()
    return jsonify({
        "is_connected": status['is_connected'],
        "watch_name": status['watch_name'],
        "signal_strength": status['signal_strength'],
        "last_sync": status['last_sync'].isoformat() if status['last_sync'] else None,
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/workout/start', methods=['POST'])
def start_workout():
    """Start a workout session"""
    global active_session
    
    data = request.get_json()
    workout_type = data.get('type', 'Running')
    duration = data.get('duration', 30)
    zone = data.get('zone', 2)
    
    streamer.start_stream()
    active_session = {
        "id": datetime.now().timestamp(),
        "type": workout_type,
        "duration_min": duration,
        "zone": zone,
        "start_time": datetime.now(),
        "status": "active"
    }
    
    return jsonify({
        "status": "✅ Workout started",
        "session": active_session,
        "message": f"Started {workout_type} session - {duration} min in Zone {zone}"
    }), 200


@app.route('/api/workout/stop', methods=['POST'])
def stop_workout():
    """Stop workout session"""
    global active_session
    
    if not active_session:
        return jsonify({"status": "❌ No active session"}), 400
    
    streamer.stop_stream()
    active_session["status"] = "completed"
    active_session["end_time"] = datetime.now()
    
    return jsonify({
        "status": "✅ Workout completed",
        "session": active_session
    }), 200


@app.route('/api/workout/stream', methods=['GET'])
def stream_workout():
    """Get workout stream data"""
    if not active_session:
        return jsonify({"status": "❌ No active session"}), 400
    
    metrics = streamer.get_latest_metrics()
    
    return jsonify({
        "session": active_session,
        "metrics": {
            "heart_rate": metrics['heart_rate'],
            "hrv": metrics['hrv'],
            "oxygen_saturation": metrics['oxygen_saturation'],
            "timestamp": metrics['timestamp'].isoformat()
        }
    }), 200


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get historical data"""
    minutes = request.args.get('minutes', 10, type=int)
    
    if not active_session or minutes > 60:
        return jsonify({
            "error": "Invalid request",
            "max_history_minutes": 60
        }), 400
    
    history_df = streamer.get_stream_history(minutes)
    
    return jsonify({
        "data_points": len(history_df),
        "minutes": minutes,
        "metrics": history_df.to_dict('records')
    }), 200


@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint - returns sample data"""
    return jsonify({
        "status": "✅ API Working",
        "sample_metrics": {
            "heart_rate": 120,
            "hrv": 42.5,
            "oxygen": 97.8,
            "steps": 5234,
            "calories": 245
        },
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/upload', methods=['POST'])
def upload_iphone_data():
    """Receive live data from iPhone Shortcut (Windows live integration)"""
    global iphone_live_data
    
    try:
        data = request.get_json()
        
        # Validate required fields: heart_rate and steps
        if "heart_rate" not in data or data["heart_rate"] is None:
            return jsonify({
                "status": "⚠️ Missing heart_rate",
                "error": "heart_rate is required"
            }), 400
        
        if "steps" not in data or data["steps"] is None:
            return jsonify({
                "status": "⚠️ Missing steps",
                "error": "steps is required"
            }), 400
        
        if "active_energy" not in data or data["active_energy"] is None:
            return jsonify({
                "status": "⚠️ Missing active_energy",
                "error": "active_energy is required"
            }), 400
        
        # Validate data ranges
        errors = []
        
        # Heart rate validation (required)
        hr = data.get("heart_rate")
        if not isinstance(hr, (int, float)) or not (30 <= hr <= 220):
            errors.append(f"Heart rate {hr} invalid (must be 30-220 bpm)")
        
        # Steps validation (required)
        steps = data.get("steps")
        if not isinstance(steps, (int, float)) or not (0 <= steps <= 100000):
            errors.append(f"Steps {steps} invalid (must be 0-100,000)")
        
        # Active energy validation (required)
        energy = data.get("active_energy")
        if not isinstance(energy, (int, float)) or not (0 <= energy <= 5000):
            errors.append(f"Active energy {energy} invalid (must be 0-5000 kcal)")
        
        if errors:
            return jsonify({
                "status": "⚠️ Data validation failed",
                "errors": errors
            }), 400
        
        # Only update if we have valid heart rate
        if data.get("heart_rate", 0) > 0 and data.get("steps", 0) >= 0 and data.get("active_energy", 0) >= 0:
            # Calculate HRV as average based on heart rate (not from watch)
            # Lower HR → higher HRV (better recovery)
            # Higher HR → lower HRV (under stress)
            base_hrv = 50
            hr_adjustment = max(0, (220 - hr) / 2)  # Inversely proportional to HR
            calculated_hrv = base_hrv + hr_adjustment + np.random.normal(0, 3)  # Add slight variation
            
            # Update our live data storage with iPhone data
            iphone_live_data.update({
                "heart_rate": data.get("heart_rate"),
                "hrv": round(max(5, calculated_hrv), 1),  # Ensure minimum 5ms
                "oxygen": None,  # Not used
                "steps": data.get("steps"),
                "energy": data.get("active_energy"),  # Active calories from watch
                "timestamp": datetime.now().isoformat()
            })
            
            return jsonify({
                "status": "✅ Data received",
                "message": "Heart rate, steps, and active energy updated",
                "metrics": {
                    "heart_rate": iphone_live_data["heart_rate"],
                    "steps": iphone_live_data["steps"],
                    "active_energy": iphone_live_data["energy"],
                    "hrv": iphone_live_data["hrv"],
                    "hrv_note": "Calculated from heart rate (recovery indicator)"
                },
                "timestamp": iphone_live_data["timestamp"]
            }), 200
        else:
            return jsonify({
                "status": "⚠️ Invalid data",
                "error": "Heart rate, steps, and active energy must be valid"
            }), 400
        
    except Exception as e:
        return jsonify({
            "status": "❌ Error",
            "error": str(e)
        }), 400


@app.route('/api/iphone', methods=['GET'])
def get_iphone_data():
    """Get latest iPhone data (for Windows users)"""
    if iphone_live_data["timestamp"] is None:
        return jsonify({
            "status": "⏳ Waiting for iPhone data",
            "message": "Set up iOS Shortcut to send data",
            "instruction": "POST to /api/upload with: heart_rate, hrv (optional), oxygen (optional), steps, energy"
        }), 200
    
    return jsonify({
        "status": "✅ iPhone connected",
        "data": iphone_live_data,
        "age_seconds": (datetime.now() - datetime.fromisoformat(iphone_live_data["timestamp"])).total_seconds(),
        "note": "Oxygen is optional (not all Apple Watch models support it)"
    }), 200


# ============ RISK ANALYSIS ENDPOINTS ============

@app.route('/api/risk/overtraining', methods=['POST'])
def calculate_overtraining_risk():
    """Calculate overtraining risk based on metrics"""
    try:
        data = request.json
        heart_rate = data.get("heart_rate", 70)
        hrv = data.get("hrv", 50)
        steps = data.get("steps", 5000)
        
        overtraining_score = 0
        reasons = []
        
        # High resting heart rate
        if heart_rate > 85:
            overtraining_score += 20
            reasons.append(f"Elevated resting HR ({heart_rate} bpm) - sign of stress/fatigue")
        
        # Low HRV (Heart Rate Variability)
        if hrv < 40:
            overtraining_score += 35
            reasons.append(f"Low HRV ({hrv:.1f} ms) - nervous system fatigued")
        elif hrv < 50:
            overtraining_score += 20
            reasons.append(f"Below-optimal HRV ({hrv:.1f} ms) - recovery needed")
        
        # High training volume
        if steps > 20000:
            overtraining_score += 15
            reasons.append(f"High daily activity ({steps:,} steps) - ensure adequate rest")
        
        return jsonify({
            "overtraining_risk": min(overtraining_score, 100),
            "severity": "HIGH" if overtraining_score > 60 else ("MODERATE" if overtraining_score > 40 else "LOW"),
            "reasons": reasons,
            "recommendation": (
                "CRITICAL: Take 2-3 days complete rest" if overtraining_score > 60 
                else ("Reduce intensity, focus on recovery" if overtraining_score > 40 
                      else ("Monitor closely" if overtraining_score > 20 
                            else "Excellent recovery status"))
            )
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/risk/heart-attack', methods=['POST'])
def calculate_heart_attack_risk():
    """Calculate 30-day heart attack risk"""
    try:
        data = request.json
        heart_rate = data.get("heart_rate", 70)
        hrv = data.get("hrv", 50)
        age = data.get("age", 45)
        diabetes = data.get("diabetes", False)
        smoking = data.get("smoking", 0)
        
        risk_score = 0
        risk_factors = []
        
        # Baseline age risk
        baseline_age_risk = (age - 40) * 0.5 if age >= 40 else 0
        risk_score += baseline_age_risk
        
        # HRV is strong predictor
        if hrv < 30:
            risk_score += 25
            risk_factors.append(f"CRITICAL: Severely low HRV ({hrv:.1f} ms)")
        elif hrv < 50:
            risk_score += 15
            risk_factors.append(f"Low HRV ({hrv:.1f} ms) - autonomic imbalance")
        elif hrv > 80:
            risk_score -= 5
            risk_factors.append(f"Excellent HRV ({hrv:.1f} ms)")
        
        # Resting heart rate
        if heart_rate > 100:
            risk_score += 20
            risk_factors.append(f"HIGH: Resting HR {heart_rate} bpm (elevated)")
        elif heart_rate > 85:
            risk_score += 10
            risk_factors.append(f"Elevated HR {heart_rate} bpm")
        elif heart_rate < 60:
            risk_score -= 5
            risk_factors.append(f"Good resting HR {heart_rate} bpm")
        
        # Diabetes
        if diabetes:
            risk_score += 30
            risk_factors.append("Diabetes: +30% risk multiplier")
        
        # Smoking
        risk_score += smoking * 2
        if smoking > 0:
            risk_factors.append(f"Smoking ({smoking} cigarettes): Risk increased")
        
        risk_percentage = min(max(risk_score, 0), 100)
        
        return jsonify({
            "30day_heart_attack_risk": risk_percentage,
            "severity": "HIGH" if risk_percentage > 40 else ("MODERATE" if risk_percentage > 15 else "LOW"),
            "risk_factors": risk_factors,
            "recommendation": (
                "CRITICAL: Seek immediate medical evaluation" if risk_percentage > 50
                else ("HIGH RISK: Schedule urgent cardiology appointment" if risk_percentage > 30
                      else ("MODERATE: Consult cardiologist for risk stratification" if risk_percentage > 15
                            else "LOW: Continue healthy lifestyle"))
            )
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/risk/combined', methods=['GET'])
def get_combined_risk():
    """Get combined overtraining + heart attack risk"""
    try:
        if not iphone_live_data["timestamp"]:
            return jsonify({"error": "No metrics available"}), 400
        
        hr = iphone_live_data.get("heart_rate", 70)
        hrv = iphone_live_data.get("hrv", 50)
        steps = iphone_live_data.get("steps", 5000)
        
        # Calculate both risks
        overtraining = 0
        if hr > 85:
            overtraining += 20
        if hrv < 40:
            overtraining += 35
        elif hrv < 50:
            overtraining += 20
        if steps > 20000:
            overtraining += 15
        
        ha_risk = 0
        if hrv < 30:
            ha_risk += 25
        elif hrv < 50:
            ha_risk += 15
        elif hrv > 80:
            ha_risk -= 5
        
        if hr > 100:
            ha_risk += 20
        elif hr > 85:
            ha_risk += 10
        
        combined = (overtraining * 0.3 + ha_risk * 0.7)
        
        return jsonify({
            "overtraining_risk": min(overtraining, 100),
            "heart_attack_risk": min(ha_risk, 100),
            "combined_risk_score": min(max(combined, 0), 100),
            "overall_severity": "CRITICAL" if combined > 60 else ("HIGH" if combined > 40 else ("MODERATE" if combined > 20 else "LOW"))
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "message": "Check /health for available endpoints"
    }), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({
        "error": "Server error",
        "message": str(error)
    }), 500


if __name__ == '__main__':
    import sys
    
    print("\n" + "="*60)
    print("🍎 HEALTHKIT API SERVER")
    print("="*60 + "\n")
    
    print("✅ Starting server...\n")
    print("📍 Endpoints available at:\n")
    print("   💚 Health check:     http://localhost:5000/health")
    print("   📊 All metrics:      http://localhost:5000/api/metrics")
    print("   ❤️  Heart rate:       http://localhost:5000/api/heart_rate")
    print("   🫀 HRV:              http://localhost:5000/api/hrv")
    print("   🫁 Oxygen:           http://localhost:5000/api/oxygen")
    print("   👣 Steps:            http://localhost:5000/api/steps")
    print("   🔥 Energy:           http://localhost:5000/api/energy")
    print("   😴 Sleep:            http://localhost:5000/api/sleep")
    print("   🆙 Status:           http://localhost:5000/api/status")
    print("\n   🏋️  Start workout:    POST /api/workout/start")
    print("   🛑 Stop workout:     POST /api/workout/stop")
    print("   📈 Workout stream:   GET /api/workout/stream")
    print("\n" + "="*60)
    print("🔗 Server running at: http://localhost:5000")
    print("="*60 + "\n")
    
    print("💡 Open http://localhost:5000/health to test\n")
    print("Press CTRL+C to stop\n\n")
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Prevent double startup
        )
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped\n")
        sys.exit(0)
