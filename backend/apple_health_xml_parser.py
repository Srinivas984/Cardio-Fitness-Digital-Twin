"""
apple_health_xml_parser.py
--------------------------
Parses Apple Health XML exports in HL7 CDA (Clinical Document Architecture) format.

The CDA is a medical-standard document format containing health observations.
Each observation embeds its data in <text> child elements with:
  - type: the health metric type (HRV, RestingHeartRate, etc.)
  - value: the numerical value
  - startDate/endDate: timestamps in ISO 8601 CDA format (yyyyMMddhhmmss+tzoffset)

Supports:
  - Heart Rate Variability (HRV)
  - Resting Heart Rate
  - Heart Rate measurements
  - Sleep records
  - Workouts
  - Steps and Activity Energy
  - VO2 Max and other metrics
"""

import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
import io

logger = logging.getLogger(__name__)


class AppleHealthXMLParser:
    """
    Parses Apple Health CDA (Clinical Document Architecture) XML exports.
    
    File structure:
    <ClinicalDocument>
      <entry>
        <organizer>
          <component>
            <observation>
              <text>
                <type>HKQuantityTypeIdentifier...</type>
                <value>42.5</value>
                <startDate>20250305...</startDate>
                ...
              </text>
            </observation>
          </component>
        </organizer>
      </entry>
    </ClinicalDocument>
    """

    def __init__(self, xml_file_path: str):
        self.xml_file = Path(xml_file_path)
        self.tree = None
        self.root = None
        self._load_xml()

    def _load_xml(self):
        """Load and parse CDA XML file with streaming to handle large multi-document files.
        
        The export file is 231 MB+ and contains multiple concatenated ClinicalDocument
        elements. We stream-read to extract just the first complete document.
        """
        try:
            logger.info("Streaming Apple Health CDA XML export (231 MB+)...")
            
            content_lines = []
            in_first_doc = False
            total_lines = 0
            found_closing = False
            
            # Stream-read the file line by line
            with open(self.xml_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    total_lines += 1
                    
                    # Detect start of first ClinicalDocument opening tag
                    if '<ClinicalDocument' in line and not in_first_doc and '>' in line:
                        in_first_doc = True
                    
                    if in_first_doc:
                        content_lines.append(line)
                        
                        # Break when we find the closing tag
                        if '</ClinicalDocument>' in line and in_first_doc:
                            found_closing = True
                            break
                    
                    # Progress indicator
                    if total_lines % 100000 == 0:
                        logger.info(f"  Scanning... {total_lines//1000}k lines")
            
            if not content_lines or not found_closing:
                raise ValueError("Could not extract first ClinicalDocument from file")
            
            content = ''.join(content_lines)
            logger.info(f"✅ Extracted document: {len(content_lines)} lines, {len(content)//1000}kB")
            
            # Parse the extracted document
            self.tree = ET.parse(io.StringIO(content))
            self.root = self.tree.getroot()
            
            # Define namespaces
            self.ns = {'cda': 'urn:hl7-org:v3'}
            
            logger.info(f"✅ Success fully parsed ClinicalDocument")
            
        except Exception as e:
            logger.error(f"❌ Failed to load XML: {e}")
            raise

    def _extract_observation_data(self, observation_elem) -> dict:
        """
        Extract health data from <observation> element.
        
        Data is embedded in nested <text> element with child tags for:
          - type: health metric type code
          - value: numerical value
          - startDate/endDate: timestamps
          - unit: measurement unit
          - sourceName: source app
          ... other metadata
        """
        data = {}
        
        # Find <text> element(s) within observation
        text_elems = observation_elem.findall('.//text') + observation_elem.findall('.//cda:text', self.ns)
        
        for text_elem in text_elems:
            # Each child of <text> is a data field
            for child in text_elem:
                tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                value = child.text if child.text else ''
                
                if value:
                    data[tag_name] = value
        
        # Also extract effectiveTime (timestamp)
        eff_time_elems = observation_elem.findall('.//effectiveTime') + observation_elem.findall('.//cda:effectiveTime', self.ns)
        
        for eff_time in eff_time_elems:
            # CDA uses <low> and <high> for time ranges
            low = eff_time.find('low')
            if low is None:
                low = eff_time.find('{urn:hl7-org:v3}low')
            
            if low is not None and low.get('value'):
                data['startDate'] = low.get('value')
            
            high = eff_time.find('high')
            if high is None:
                high = eff_time.find('{urn:hl7-org:v3}high')
            
            if high is not None and high.get('value'):
                data['endDate'] = high.get('value')
            
            # Single timestamp
            if (low is None and high is None) and eff_time.get('value'):
                data['startDate'] = eff_time.get('value')
        
        return data

    def parse_daily_metrics(self) -> pd.DataFrame:
        """
        Extract daily aggregated metrics (HRV, RHR, HR stats, etc.).
        
        In CDA XML, health data structure is:
        <observation>
            <text>
                <type>HKQuantityTypeIdentifier...</type>
                <value>42.5</value>
                <unit>ms</unit>
                <sourceName>...</sourceName>
            </text>
            <effectiveTime>
                <low value="20250305065312+0530"/>
                <high value="20250305065312+0530"/>  
            </effectiveTime>
        </observation>
        
        Returns: DataFrame with columns [date, hrv_sdnn, resting_hr, heart_rate, steps, active_energy_kJ, vo2_max]
        """
        records = []
        
        # Debug: Check if root is set
        if self.root is None:
            logger.error("❌ XML root not loaded!")
            logger.warning("⚠️ No health metrics parsed from text elements")
            return pd.DataFrame()
        
        logger.info(f"📍 Root element: {self.root.tag}")
        
        ns = {'cda': 'urn:hl7-org:v3'}
        
        # Find observation elements (not text elements directly)
        observations = self.root.findall('.//cda:observation', ns)
        logger.info(f"🔍 Found {len(observations)} observation elements")
        
        for i, observation in enumerate(observations):
            # Get timestamp from effectiveTime
            effective_time = observation.find('.//cda:effectiveTime', ns)
            
            timestamp = None
            if effective_time is not None:
                # Try to get from <low> element
                low = effective_time.find('cda:low', ns)
                if low is None:
                    low = effective_time.find('low')
                
                if low is not None and low.get('value'):
                    timestamp = low.get('value')
            
            if not timestamp:
                if i == 0:
                    logger.debug(f"[0] Skipping observation, no timestamp found")
                continue
            
            # Get data from nested text element
            text_elem = observation.find('.//cda:text', ns)
            if text_elem is None:
                text_elem = observation.find('.//text')
            
            if text_elem is None:
                continue
            
            # Extract data from text element children
            data = {}
            for child in text_elem:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                value = child.text if child.text else ''
                
                if value and value.strip():
                    data[tag] = value.strip()
            
            # Debug first observation
            if i == 0:
                logger.info(f"[0] Extracted data: {data}")
            
            # Require at least type and value
            if not data.get('type') or not data.get('value'):
                if i == 0:
                    logger.info(f"[0] Missing type or value. Type={data.get('type')}, Value={data.get('value')}")
                continue
            
            try:
                record_type = data.get('type', '')
                value_num = float(data.get('value', ''))
                
                # Parse timestamp
                dt = self._parse_iso_datetime(timestamp)
                if not dt:
                    if i == 0:
                        logger.info(f"[0] Could not parse timestamp: {timestamp}")
                    continue
                
                date = dt.date()
                
                if i == 0:
                    logger.info(f"[0] Parsed: type={record_type}, value={value_num}, date={date}")
                
                # Map Apple Health type identifiers to metric categories  
                metric_name = None
                if 'HRV' in record_type or 'Variability' in record_type:
                    metric_name = 'hrv_sdnn'
                
                elif 'RestingHeartRate' in record_type or 'Resting' in record_type:
                    metric_name = 'resting_hr'
                
                elif 'HeartRate' in record_type or 'Heart Rate' in data.get('sourceName', ''):
                    metric_name = 'heart_rate'
                
                elif 'StepCount' in record_type or 'Steps' in record_type:
                    metric_name = 'steps'
                
                elif 'ActiveEnergy' in record_type or 'Active Energy' in record_type:
                    metric_name = 'active_energy_kJ'
                
                elif 'VO2Max' in record_type:
                    metric_name = 'vo2_max'
                
                elif 'DietaryWater' in record_type or 'Water' in record_type:
                    metric_name = 'water_intake_mL'
                
                if metric_name:
                    records.append({'date': date, 'metric': metric_name, 'value': value_num})
                elif i == 0:
                    logger.info(f"[0] Type '{record_type}' did not match any metric category")
            
            except (ValueError, TypeError) as e:
                if i == 0:
                    logger.info(f"[0] Error parsing: {e}")
                continue
        
        if not records:
            logger.warning("⚠️ No health metrics parsed from observation elements")
            return pd.DataFrame()
        
        logger.info(f"📊 Parsed {len(records)} health records")
        
        # Convert to DataFrame
        df = pd.DataFrame(records)
        
        # Pivot and aggregate (mean for multiple readings per day)
        df_pivot = df.pivot_table(
            index='date',
            columns='metric',
            values='value',
            aggfunc='mean'
        )
        
        df_pivot = df_pivot.reset_index()
        df_pivot.columns.name = None
        df_pivot = df_pivot.sort_values('date').reset_index(drop=True)
        
        logger.info(f"✅ Computed daily metrics for {len(df_pivot)} days")
        return df_pivot

    def _parse_iso_datetime(self, iso_string: str) -> datetime:
        """
        Parse ISO 8601 CDA datetime format.
        
        CDA format: yyyyMMddhhmmss±hhmm (e.g., 20250305144829+0530)
        """
        try:
            # Remove timezone offset
            base_dt = iso_string[:14]  # yyyyMMddhhmmss
            
            if len(base_dt) == 14:
                return datetime.strptime(base_dt, '%Y%m%d%H%M%S')
            elif len(iso_string) == 8:
                return datetime.strptime(iso_string, '%Y%m%d')
            else:
                # Try fromisoformat as fallback
                clean = iso_string.replace('Z', '+00:00').split('+')[0].split('-')[0]
                return datetime.fromisoformat(clean)
        except Exception as e:
            logger.debug(f"Could not parse datetime {iso_string}: {e}")
            return None

    def parse_workouts(self) -> pd.DataFrame:
        """
        Extract workout records from text elements.
        Returns: DataFrame [start_time, end_time, workout_type, duration_min, active_energy_kJ, distance_km]
        """
        workouts = []
        
        # Find all text elements with namespace support
        ns = {'cda': 'urn:hl7-org:v3'}
        text_elems = self.root.findall('.//cda:text', ns)
        
        for text_elem in text_elems:
            data = {}
            for child in text_elem:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                if child.text:
                    data[tag] = child.text.strip()
            
            record_type = data.get('type', '')
            if 'Workout' not in record_type:
                continue
            
            try:
                start_str = data.get('startDate')
                end_str = data.get('endDate')
                
                start_dt = self._parse_iso_datetime(start_str) if start_str else None
                end_dt = self._parse_iso_datetime(end_str) if end_str else None
                
                if not start_dt or not end_dt:
                    continue
                
                duration_min = (end_dt - start_dt).total_seconds() / 60
                
                workouts.append({
                    'start_time': start_dt,
                    'end_time': end_dt,
                    'workout_type': data.get('workoutActivityType', 'Unknown'),
                    'duration_min': duration_min,
                    'active_energy_kJ': float(data.get('energy', 0)),
                    'distance_km': float(data.get('distance', 0)) / 1000 if data.get('distance') else 0
                })
            
            except (ValueError, TypeError):
                continue
        
        if not workouts:
            logger.warning("⚠️ No workouts found")
            return pd.DataFrame()
        
        df = pd.DataFrame(workouts)
        logger.info(f"✅ Parsed {len(df)} workouts")
        return df

    def parse_sleep(self) -> pd.DataFrame:
        """
        Extract sleep records from text elements.
        Returns: DataFrame [start, end, date, duration_hours]
        """
        sleep_records = []
        
        # Find all text elements with namespace support
        ns = {'cda': 'urn:hl7-org:v3'}
        text_elems = self.root.findall('.//cda:text', ns)
        
        for text_elem in text_elems:
            data = {}
            for child in text_elem:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                if child.text:
                    data[tag] = child.text.strip()
            
            record_type = data.get('type', '')
            if 'SleepAnalysis' not in record_type and 'sleep' not in record_type.lower():
                continue
            
            try:
                start_str = data.get('startDate')
                end_str = data.get('endDate')
                
                start_dt = self._parse_iso_datetime(start_str) if start_str else None
                end_dt = self._parse_iso_datetime(end_str) if end_str else None
                
                if not start_dt or not end_dt:
                    continue
                
                duration_hours = (end_dt - start_dt).total_seconds() / 3600
                
                sleep_records.append({
                    'start': start_dt,
                    'end': end_dt,
                    'date': start_dt.date(),
                    'duration_hours': duration_hours
                })
            
            except (ValueError, TypeError):
                continue
        
        if not sleep_records:
            logger.warning("⚠️ No sleep records found")
            return pd.DataFrame()
        
        df = pd.DataFrame(sleep_records)
        logger.info(f"✅ Parsed {len(df)} sleep records")
        return df

    def compute_personal_features(self) -> dict:
        """
        Compute current personal baseline features from available data.
        
        Returns: Dictionary with keys for CardiacDigitalTwin initialization:
          - resting_hr, max_hr, hrv_avg, hrv_baseline
          - fatigue_index, recovery_index, hr_recovery_rate
          - zone1_pct...zone5_pct (HR zone distribution)
          - activity_load, avg_hr
        """
        daily_df = self.parse_daily_metrics()
        
        if daily_df.empty:
            logger.warning("⚠️ No daily metrics for feature computation—using defaults")
            return self._default_features()
        
        # Latest and baseline
        latest = daily_df.iloc[-1]
        baseline = daily_df.iloc[0]
        
        # Recent 7-day average
        recent_data = daily_df.iloc[-7:] if len(daily_df) >= 7 else daily_df
        
        # Extract baselines
        resting_hr = float(latest.get('resting_hr', 62)) if pd.notna(latest.get('resting_hr')) else 62
        hrv_avg = float(recent_data['hrv_sdnn'].mean()) if 'hrv_sdnn' in recent_data.columns else 50
        hr_avg = float(recent_data['heart_rate'].mean()) if 'heart_rate' in recent_data.columns else 95
        
        max_hr = 185  # Standard estimate for adults
        
        # HR zone distribution (estimate)
        zone_pcts = {'zone1_pct': 25, 'zone2_pct': 30, 'zone3_pct': 25, 'zone4_pct': 15, 'zone5_pct': 5}
        
        return {
            "resting_hr": float(resting_hr),
            "max_hr": float(max_hr),
            "hrv_avg": float(hrv_avg),
            "hrv_baseline": float(hrv_avg),
            "fatigue_index": 30,
            "recovery_index": 70,
            "hr_recovery_rate": 25,
            **zone_pcts,
            "activity_load": 50,
            "avg_hr": float(hr_avg),
        }

    def _default_features(self) -> dict:
        """Return default baseline features if no data available."""
        return {
            "resting_hr": 62,
            "max_hr": 185,
            "hrv_avg": 50,
            "hrv_baseline": 50,
            "fatigue_index": 30,
            "recovery_index": 70,
            "hr_recovery_rate": 25,
            "zone1_pct": 25,
            "zone2_pct": 30,
            "zone3_pct": 25,
            "zone4_pct": 15,
            "zone5_pct": 5,
            "activity_load": 50,
            "avg_hr": 95,
        }

    def get_data_summary(self) -> dict:
        """
        Get summary of available data in the export.
        
        Returns: Dict with counts and date ranges for all data types.
        """
        daily = self.parse_daily_metrics()
        workouts = self.parse_workouts()
        sleep = self.parse_sleep()
        
        summary = {
            "daily_records": len(daily),
            "date_range": f"{daily['date'].min()} to {daily['date'].max()}" if len(daily) > 0 else "No data",
            "workouts_count": len(workouts),
            "sleep_records": len(sleep),
            "has_hrv": "hrv_sdnn" in daily.columns if len(daily) > 0 else False,
            "has_resting_hr": "resting_hr" in daily.columns if len(daily) > 0 else False,
            "has_heart_rate": "heart_rate" in daily.columns if len(daily) > 0 else False,
        }
        
        logger.info(f"📊 Data Summary: {summary}")
        return summary
