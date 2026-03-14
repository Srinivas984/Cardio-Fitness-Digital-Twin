"""
Comprehensive feature test for Cardio Digital Twin
Tests all major components to identify broken features
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_endpoints():
    """Test API server endpoints"""
    import urllib.request
    import json
    
    print("\n" + "="*60)
    print("TESTING API ENDPOINTS")
    print("="*60)
    
    endpoints = [
        ("GET", "http://localhost:5000/api/test", None),
        ("GET", "http://localhost:5000/api/metrics", None),
        ("GET", "http://localhost:5000/api/iphone", None),
        ("GET", "http://localhost:5000/api/heart_rate", None),
        ("GET", "http://localhost:5000/api/steps", None),
        ("GET", "http://localhost:5000/api/energy", None),
        ("GET", "http://localhost:5000/api/hrv", None),
        ("GET", "http://localhost:5000/api/status", None),
    ]
    
    for method, url, body in endpoints:
        try:
            response = urllib.request.urlopen(url, timeout=2)
            data = json.loads(response.read().decode())
            print(f"✅ {method:4} {url.split('/')[-1]:20} - Status: {response.status}")
        except Exception as e:
            print(f"❌ {method:4} {url.split('/')[-1]:20} - Error: {str(e)[:50]}")

def test_data_upload():
    """Test data upload to API"""
    import urllib.request
    import json
    
    print("\n" + "="*60)
    print("TESTING DATA UPLOAD")
    print("="*60)
    
    data = {"heart_rate": 75, "steps": 5000, "active_energy": 250}
    
    try:
        request = urllib.request.Request(
            'http://localhost:5000/api/upload',
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        response = urllib.request.urlopen(request, timeout=2)
        result = json.loads(response.read().decode())
        
        if result.get('status') == '✅ Data received':
            print(f"✅ Data upload successful")
            print(f"   Heart Rate: {result['metrics'].get('heart_rate')} bpm")
            print(f"   Steps: {result['metrics'].get('steps')}")
            print(f"   Active Energy: {result['metrics'].get('active_energy')} kcal")
            print(f"   HRV (calculated): {result['metrics'].get('hrv')} ms")
            return True
        else:
            print(f"❌ Upload response unexpected: {result.get('status')}")
            return False
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def test_healthkit_connector():
    """Test HealthKit connector functionality"""
    from healthkit_connector import HealthKitConnector
    
    print("\n" + "="*60)
    print("TESTING HEALTHKIT CONNECTOR")
    print("="*60)
    
    try:
        connector = HealthKitConnector(use_demo_mode=True)
        print("✅ HealthKitConnector initialized")
        
        # Test methods
        hr, status = connector.get_live_heart_rate()
        print(f"✅ get_live_heart_rate: {hr} bpm ({status})")
        
        hrv = connector.get_live_hrv()
        print(f"✅ get_live_hrv: {hrv:.1f} ms")
        
        o2 = connector.get_live_oxygen_saturation()
        print(f"✅ get_live_oxygen_saturation: {o2:.1f}%")
        
        steps = connector.get_step_count()
        print(f"✅ get_step_count: {steps['steps']} steps (goal: {steps['goal']})")
        
        energy = connector.get_active_energy()
        print(f"✅ get_active_energy: {energy['calories']} kcal (goal: {energy['goal']})")
        
        return True
    except Exception as e:
        print(f"❌ HealthKitConnector error: {e}")
        return False

def test_live_coach():
    """Test Live Coach functionality"""
    from live_coach import LivePersonalCoach, VoiceCoach
    
    print("\n" + "="*60)
    print("TESTING LIVE COACH")
    print("="*60)
    
    try:
        coach = LivePersonalCoach()
        print("✅ LivePersonalCoach initialized")
        
        # Start session
        result = coach.start_session("Running", 45, target_hr_zone=2)
        print(f"✅ start_session: {result['status']}")
        
        # Get coaching
        coaching = coach.get_real_time_coaching(current_hr=150, target_zone=2, elapsed_seconds=300)
        print(f"✅ get_real_time_coaching: {coaching.get('coaching_cue', 'N/A')[:50]}...")
        
        voice = VoiceCoach()
        print("✅ VoiceCoach initialized")
        
        return True
    except Exception as e:
        print(f"❌ LiveCoach error: {e}")
        return False

def test_adaptive_workouts():
    """Test adaptive workout functionality"""
    from adaptive_workouts import AdaptiveWorkout, SmartNotifications
    
    print("\n" + "="*60)
    print("TESTING ADAPTIVE WORKOUTS")
    print("="*60)
    
    try:
        workout = AdaptiveWorkout()
        print("✅ AdaptiveWorkout initialized")
        
        # Start workout
        result = workout.start_adaptive_workout("Running", 45, 2)
        print(f"✅ start_adaptive_workout: {result['workout_type']}")
        
        # Adjust workout
        metrics = {"heart_rate": 155, "hrv": 35}
        adjustment = workout.adjust_workout_real_time(metrics, 2, 300)
        print(f"✅ adjust_workout_real_time: {adjustment.get('adjustment_type', 'none')}")
        
        notifier = SmartNotifications()
        print("✅ SmartNotifications initialized")
        
        return True
    except Exception as e:
        print(f"❌ AdaptiveWorkout error: {e}")
        return False

def test_backend_modules():
    """Test backend analysis modules"""
    from backend.cardiac_model import CardiacDigitalTwin
    from backend.optimizer_ai import AITrainingOptimizer
    from backend.risk_detection import RiskDetector
    from backend.explainable_ai import ExplainableAI
    
    print("\n" + "="*60)
    print("TESTING BACKEND MODULES")
    print("="*60)
    
    try:
        twin = CardiacDigitalTwin()
        print("✅ CardiacDigitalTwin initialized")
        
        optimizer = AITrainingOptimizer()
        print("✅ AITrainingOptimizer initialized")
        
        detector = RiskDetector()
        print("✅ RiskDetector initialized")
        
        explainer = ExplainableAI()
        print("✅ ExplainableAI initialized")
        
        return True
    except Exception as e:
        print(f"❌ Backend module error: {e}")
        return False

def test_simulation_modules():
    """Test simulation modules"""
    from simulation.workout_simulator import WorkoutSimulator
    from simulation.cardiac_simulator import CardiacSimulator
    
    print("\n" + "="*60)
    print("TESTING SIMULATION MODULES")
    print("="*60)
    
    try:
        workout_sim = WorkoutSimulator()
        print("✅ WorkoutSimulator initialized")
        
        cardiac_sim = CardiacSimulator()
        print("✅ CardiacSimulator initialized")
        
        return True
    except Exception as e:
        print(f"❌ Simulation module error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "🔍 CARDIO DIGITAL TWIN - COMPREHENSIVE FEATURE TEST")
    print("=" * 60)
    
    results = {}
    
    results['API Endpoints'] = test_api_endpoints()
    results['Data Upload'] = test_data_upload()
    results['HealthKit Connector'] = test_healthkit_connector()
    results['Live Coach'] = test_live_coach()
    results['Adaptive Workouts'] = test_adaptive_workouts()
    results['Backend Modules'] = test_backend_modules()
    results['Simulation Modules'] = test_simulation_modules()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, result in results.items():
        status = "✅ PASS" if result else "⚠️ CHECK"
        print(f"{status:10} {test_name}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} feature groups working")

if __name__ == "__main__":
    main()
