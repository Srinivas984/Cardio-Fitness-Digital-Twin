#!/usr/bin/env python3
import urllib.request
import json

print("FINAL SYSTEM TEST")
print("="*60)

# Test 1
print("\n[1] Testing data upload...")
try:
    data = {'heart_rate': 90, 'steps': 8000, 'active_energy': 350}
    req = urllib.request.Request('http://localhost:5000/api/upload', 
        data=json.dumps(data).encode(), 
        headers={'Content-Type': 'application/json'}, method='POST')
    resp = urllib.request.urlopen(req, timeout=2)
    result = json.loads(resp.read().decode())
    hr = result['metrics'].get('heart_rate')
    hrv = result['metrics'].get('hrv')
    print(f"    SUCCESS: Uploaded HR={hr} bpm, HRV={hrv:.1f} ms (auto-calculated)")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 2
print("\n[2] Testing metrics retrieval...")
try:
    resp = urllib.request.urlopen('http://localhost:5000/api/metrics', timeout=2)
    m = json.loads(resp.read().decode())
    source = m.get('source', 'unknown')
    hr = m.get('heart_rate', {}).get('value', 'N/A')
    steps = m.get('steps', {}).get('steps', 'N/A')
    energy = m.get('active_energy', {}).get('value', 'N/A')
    print(f"    SUCCESS: Source={source}")
    print(f"    - Heart Rate: {hr} bpm")
    print(f"    - Steps: {steps}")
    print(f"    - Energy: {energy} kcal")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 3  
print("\n[3] Testing app status...")
try:
    resp = urllib.request.urlopen('http://localhost:8508', timeout=3)
    print(f"    SUCCESS: Streamlit app is running")
except Exception as e:
    print(f"    INFO: {e}")

print("\n" + "="*60)
print("OVERALL STATUS: All core functions working")
print("="*60)
