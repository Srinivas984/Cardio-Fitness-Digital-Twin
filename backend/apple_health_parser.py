"""
apple_health_parser.py
----------------------
Parses Apple Health export.xml files and extracts relevant cardiovascular
metrics: Heart Rate, HRV (SDNN), and Step Count.

Usage:
    parser = AppleHealthParser("path/to/export.xml")
    df = parser.parse()
"""

import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppleHealthParser:
    """Parses Apple Health XML exports into structured DataFrames."""

    # Apple Health record type identifiers
    RECORD_TYPES = {
        "heart_rate": "HKQuantityTypeIdentifierHeartRate",
        "hrv": "HKQuantityTypeIdentifierHeartRateVariabilitySDNN",
        "steps": "HKQuantityTypeIdentifierStepCount",
    }

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.tree = None
        self.root = None

    def load(self):
        """Load and parse the XML file."""
        try:
            logger.info(f"Loading Apple Health export from: {self.filepath}")
            self.tree = ET.parse(self.filepath)
            self.root = self.tree.getroot()
            logger.info("XML loaded successfully.")
        except FileNotFoundError:
            raise FileNotFoundError(f"Export file not found: {self.filepath}")
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML: {e}")

    def _extract_records(self, record_type: str) -> list:
        """Extract records of a specific type from the XML tree."""
        records = []
        for record in self.root.findall("Record"):
            if record.attrib.get("type") == record_type:
                try:
                    records.append({
                        "timestamp": pd.to_datetime(record.attrib["startDate"]),
                        "value": float(record.attrib["value"]),
                    })
                except (KeyError, ValueError):
                    continue  # Skip malformed records
        return records

    def _extract_heart_rate(self) -> pd.DataFrame:
        records = self._extract_records(self.RECORD_TYPES["heart_rate"])
        if not records:
            return pd.DataFrame(columns=["timestamp", "heart_rate"])
        df = pd.DataFrame(records)
        df.rename(columns={"value": "heart_rate"}, inplace=True)
        return df

    def _extract_hrv(self) -> pd.DataFrame:
        records = self._extract_records(self.RECORD_TYPES["hrv"])
        if not records:
            return pd.DataFrame(columns=["timestamp", "hrv_sdnn"])
        df = pd.DataFrame(records)
        df.rename(columns={"value": "hrv_sdnn"}, inplace=True)
        return df

    def _extract_steps(self) -> pd.DataFrame:
        records = self._extract_records(self.RECORD_TYPES["steps"])
        if not records:
            return pd.DataFrame(columns=["timestamp", "steps"])
        df = pd.DataFrame(records)
        df.rename(columns={"value": "steps"}, inplace=True)
        return df

    def parse(self) -> pd.DataFrame:
        """
        Full parse pipeline: load XML, extract metrics, merge into one DataFrame.
        Returns a unified DataFrame sorted by timestamp.
        """
        self.load()

        hr_df = self._extract_heart_rate()
        hrv_df = self._extract_hrv()
        steps_df = self._extract_steps()

        # Round timestamps to the nearest hour for alignment
        for df in [hr_df, hrv_df, steps_df]:
            if not df.empty:
                df["timestamp"] = df["timestamp"].dt.round("h")

        # Aggregate by hour
        if not hr_df.empty:
            hr_df = hr_df.groupby("timestamp")["heart_rate"].mean().reset_index()
        if not hrv_df.empty:
            hrv_df = hrv_df.groupby("timestamp")["hrv_sdnn"].mean().reset_index()
        if not steps_df.empty:
            steps_df = steps_df.groupby("timestamp")["steps"].sum().reset_index()

        # Merge all metrics
        merged = hr_df
        if not hrv_df.empty:
            merged = pd.merge(merged, hrv_df, on="timestamp", how="outer")
        if not steps_df.empty:
            merged = pd.merge(merged, steps_df, on="timestamp", how="outer")

        merged.sort_values("timestamp", inplace=True)
        merged.reset_index(drop=True, inplace=True)

        logger.info(f"Parsed {len(merged)} records from Apple Health export.")
        return merged
