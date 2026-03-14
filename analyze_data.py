import pandas as pd
import numpy as np

# Load the CSV
csv = pd.read_csv('data/HealthAutoExport-2026-02-11-2026-03-13.csv')

print('📊 DATA ANALYSIS')
print('=' * 70)
print(f'Total rows: {len(csv)} days')
print(f'Total columns: {len(csv.columns)}')
print(f'Date range: {csv.iloc[0]["Date/Time"]} to {csv.iloc[-1]["Date/Time"]}')

print('\n📈 COLUMN AVAILABILITY:')
print('=' * 70)
for col in csv.columns:
    non_null = csv[col].notna().sum()
    null_count = csv[col].isna().sum()
    pct = (non_null / len(csv)) * 100
    status = '✅' if pct > 80 else '⚠️' if pct > 30 else '❌'
    print(f'{status} {col}: {non_null}/{len(csv)} ({pct:.0f}%)')

print('\n⚠️ MISSING DATA SUMMARY:')
print('=' * 70)
missing = csv.isnull().sum()
missing_pct = (missing / len(csv)) * 100
critical_missing = missing[missing_pct > 50]
if len(critical_missing) > 0:
    print('Columns with >50% missing data:')
    for col, count in critical_missing.items():
        print(f'  ❌ {col}: {count} missing ({(count/len(csv))*100:.0f}%)')
else:
    print('✅ No critical missing data (>50%)')

print('\n🫀 KEY METRICS STATUS:')
print('=' * 70)
key_metrics = {
    'Heart Rate Variability (ms)': '📊 HRV',
    'Resting Heart Rate (count/min)': '❤️ Resting HR',
    'Heart Rate [Avg] (count/min)': '💓 Average HR',
    'Heart Rate [Min] (count/min)': '📉 Min HR',
    'Heart Rate [Max] (count/min)': '📈 Max HR',
    'Active Energy (kJ)': '⚡ Active Energy',
    'Step Count (count)': '👣 Steps',
    'VO2 Max (ml/(kg·min))': '🫁 VO2 Max',
    'Sleep Analysis [Total] (hr)': '😴 Sleep',
    'Blood Oxygen Saturation (%)': '🩸 Blood O2',
    'Respiratory Rate (count/min)': '🌬️ Resp Rate',
}

for col, label in key_metrics.items():
    if col in csv.columns:
        available = csv[col].notna().sum()
        pct = (available / len(csv)) * 100
        if available > 0:
            mean_val = csv[col].mean()
            print(f'✅ {label}: {available}/31 days ({pct:.0f}%) | Avg: {mean_val:.2f}')
        else:
            print(f'❌ {label}: 0 days (0%) - NO DATA')
    else:
        print(f'❌ {label}: NOT IN CSV')

print('\n📋 SAMPLE DATA (First 5 rows):')
print('=' * 70)
print(csv.head())
