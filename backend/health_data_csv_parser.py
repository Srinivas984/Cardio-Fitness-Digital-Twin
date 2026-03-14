"""
health_data_csv_parser.py
-----------------------
Loads comprehensive health data from Apple Health CSV exports.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HealthCSVParser:
    """Load comprehensive health data from CSV export"""
    
    def __init__(self, csv_file_path: str):
        self.csv_file = Path(csv_file_path)
        self.df = None
        self._load_csv()
    
    def _load_csv(self):
        """Load and parse the health CSV"""
        try:
            logger.info(f"Loading health data from CSV: {self.csv_file.name}")
            
            self.df = pd.read_csv(self.csv_file)
            self.df['Date/Time'] = pd.to_datetime(self.df['Date/Time'])
            
            logger.info(f"✅ Loaded {len(self.df)} days of health history")
            
        except Exception as e:
            logger.error(f"❌ Failed to load CSV: {e}")
            raise
    
    def parse_daily_metrics(self) -> pd.DataFrame:
        """
        Extract daily metrics in standard format.
        
        Returns DataFrame with columns:
        - date: datetime.date
        - hrv_sdnn: Heart Rate Variability (ms)
        - resting_hr: Resting Heart Rate (bpm)
        - heart_rate: Average Heart Rate (bpm)
        - steps: Step count
        - active_energy_kJ: Active Energy (kJ)
        - vo2_max: VO2 Max (ml/kg/min)
        - heart_rate_min: Min HR during day
        - heart_rate_max: Max HR during day
        - respiratory_rate: Breaths per minute
        - blood_oxygen: Blood Oxygen Saturation (%)
        - distance_km: Walking + Running Distance
        """
        result = pd.DataFrame()
        result['date'] = self.df['Date/Time'].dt.date
        
        # Map CSV columns to standard metric names
        column_mapping = {
            'Heart Rate Variability (ms)': 'hrv_sdnn',
            'Resting Heart Rate (count/min)': 'resting_hr',
            'Heart Rate [Avg] (count/min)': 'heart_rate',
            'Step Count (count)': 'steps',
            'Active Energy (kJ)': 'active_energy_kJ',
            'VO2 Max (ml/(kg·min))': 'vo2_max',
            'Heart Rate [Min] (count/min)': 'heart_rate_min',
            'Heart Rate [Max] (count/min)': 'heart_rate_max',
            'Respiratory Rate (count/min)': 'respiratory_rate',
            'Blood Oxygen Saturation (%)': 'blood_oxygen',
            'Walking + Running Distance (km)': 'distance_km',
        }
        
        for csv_col, std_col in column_mapping.items():
            if csv_col in self.df.columns:
                result[std_col] = self.df[csv_col]
        
        logger.info(f"✅ Parsed daily metrics: {len(result)} days, {len(result.columns)-1} metrics")
        
        return result
    
    def parse_sleep(self) -> pd.DataFrame:
        """
        Extract sleep analysis metrics.
        
        Returns DataFrame with columns:
        - date: datetime.date
        - total_sleep_hr, asleep_hr, in_bed_hr, core_hr, deep_hr, rem_hr, awake_hr
        """
        result = pd.DataFrame()
        result['date'] = self.df['Date/Time'].dt.date
        
        sleep_mapping = {
            'Sleep Analysis [Total] (hr)': 'total_sleep_hr',
            'Sleep Analysis [Asleep] (hr)': 'asleep_hr',
            'Sleep Analysis [In Bed] (hr)': 'in_bed_hr',
            'Sleep Analysis [Core] (hr)': 'core_hr',
            'Sleep Analysis [Deep] (hr)': 'deep_hr',
            'Sleep Analysis [REM] (hr)': 'rem_hr',
            'Sleep Analysis [Awake] (hr)': 'awake_hr',
        }
        
        for csv_col, std_col in sleep_mapping.items():
            if csv_col in self.df.columns:
                result[std_col] = self.df[csv_col]
        
        return result
    
    def parse_workouts(self) -> pd.DataFrame:
        """No workouts in this CSV, but can be populated from Workouts file if available"""
        return pd.DataFrame()
    
    def compute_personal_features(self) -> dict:
        """
        Compute baseline personal health features from the data.
        
        Returns dict with keys expected by the app:
        - resting_hr: Latest resting heart rate
        - hrv_avg: Average HRV
        - max_hr: Latest max HR
        - avg_hr: Average heart rate
        - fatigue_index: Computed fatigue score (0-100)
        - recovery_index: Computed recovery score (0-100) 
        - hr_recovery_rate: HR recovery rate estimate
        - zone1_pct, zone2_pct, zone3_pct, zone4_pct: Training zone percentages
        - activity_load: Daily activity load estimate
        """
        daily = self.parse_daily_metrics()
        
        features = {}
        
        if not daily.empty:
            # Get latest/average values
            if 'resting_hr' in daily.columns:
                latest_rhr = daily['resting_hr'].dropna().iloc[-1] if len(daily['resting_hr'].dropna()) > 0 else 70
                features['resting_hr'] = float(latest_rhr)
            else:
                features['resting_hr'] = 70.0
            
            if 'hrv_sdnn' in daily.columns:
                hrv_values = daily['hrv_sdnn'].dropna()
                features['hrv_avg'] = float(hrv_values.mean()) if len(hrv_values) > 0 else 40
            else:
                features['hrv_avg'] = 40.0
            
            if 'heart_rate_max' in daily.columns:
                latest_max = daily['heart_rate_max'].dropna().iloc[-1] if len(daily['heart_rate_max'].dropna()) > 0 else 160
                features['max_hr'] = float(latest_max)
            else:
                features['max_hr'] = 160.0
            
            if 'heart_rate' in daily.columns:
                hr_values = daily['heart_rate'].dropna()
                features['avg_hr'] = float(hr_values.mean()) if len(hr_values) > 0 else 100
            else:
                features['avg_hr'] = 100.0
            
            # Compute derived metrics
            # Fatigue index: based on HRV trends (lower HRV = higher fatigue)
            hrv_avg = features['hrv_avg']
            features['fatigue_index'] = max(0, min(100, 100 - (hrv_avg / 50) * 100))  # 0-100
            
            # Recovery index: inverse of fatigue
            features['recovery_index'] = 100 - features['fatigue_index']
            
            # HR recovery rate estimate: assume 12-15 bpm per minute recovery
            features['hr_recovery_rate'] = np.random.uniform(12, 18)  # Demo value
            
            # Activity load: based on active energy
            if 'active_energy_kJ' in daily.columns:
                active_energy = daily['active_energy_kJ'].dropna().mean()
                features['activity_load'] = float(active_energy / 10)  # Normalize
            else:
                features['activity_load'] = 50.0
            
            # Training zones: estimate based on max HR and daily data
            # Simplified: assume distribution across zones
            features['zone1_pct'] = 25  # <60% max HR
            features['zone2_pct'] = 30  # 60-70% max HR
            features['zone3_pct'] = 25  # 70-85% max HR
            features['zone4_pct'] = 15  # >85% max HR
            
        else:
            # Default values if no data
            features = {
                'resting_hr': 70.0,
                'hrv_avg': 40.0,
                'max_hr': 160.0,
                'avg_hr': 100.0,
                'fatigue_index': 35.0,
                'recovery_index': 65.0,
                'hr_recovery_rate': 15.0,
                'activity_load': 50.0,
                'zone1_pct': 25,
                'zone2_pct': 30,
                'zone3_pct': 25,
                'zone4_pct': 15,
            }
        
        logger.info(f"✅ Personal features computed: RHR={features['resting_hr']:.0f}, HRV={features['hrv_avg']:.1f}, MaxHR={features['max_hr']:.0f}")
        
        return features
    
    def get_data_summary(self) -> dict:
        """Get summary of available data"""
        daily = self.parse_daily_metrics()
        
        return {
            'date_range': f"{daily['date'].min()} to {daily['date'].max()}" if not daily.empty else "No data",
            'total_days': len(daily),
            'metrics': [col for col in daily.columns if col != 'date'],
            'available_metrics': {col: daily[col].notna().sum() for col in daily.columns if col != 'date'},
        }
