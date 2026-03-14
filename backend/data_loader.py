"""
data_loader.py
--------------
Unified data loading interface. Supports:
  - Apple Health XML exports (via AppleHealthParser)
  - CSV files (for demo/simulation data)
  - In-memory simulated data generation

Returns a standardized pandas DataFrame for the pipeline.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Expected columns in the standardized schema
REQUIRED_COLUMNS = ["timestamp", "heart_rate", "hrv_sdnn", "steps"]


class DataLoader:
    """Loads cardiovascular data from multiple sources."""

    def __init__(self, source: str = "sample"):
        """
        Args:
            source: 'sample' | 'csv:<path>' | 'xml:<path>'
        """
        self.source = source

    def load(self) -> pd.DataFrame:
        """Dispatch to the appropriate loader based on source."""
        if self.source == "sample":
            return self._load_sample()
        elif self.source.startswith("csv:"):
            path = self.source[4:]
            return self._load_csv(path)
        elif self.source.startswith("xml:"):
            path = self.source[4:]
            return self._load_xml(path)
        else:
            raise ValueError(f"Unknown source format: {self.source}")

    def _load_csv(self, path: str) -> pd.DataFrame:
        """Load from a CSV file."""
        logger.info(f"Loading CSV from: {path}")
        df = pd.read_csv(path, parse_dates=["timestamp"])
        df = self._validate_and_fill(df)
        return df

    def _load_xml(self, path: str) -> pd.DataFrame:
        """Load from Apple Health XML export (lifetime data)."""
        from backend.apple_health_xml_parser import AppleHealthXMLParser
        parser = AppleHealthXMLParser(path)
        daily_df = parser.parse_daily_metrics()
        
        if daily_df.empty:
            logger.warning("No daily metrics parsed from XML")
            return self._load_sample()  # Fallback to sample
        
        # Rename columns to match expected schema
        df = daily_df.copy()
        df.rename(columns={
            'date': 'timestamp',
            'hrv_sdnn': 'hrv_sdnn',
            'resting_hr': 'resting_hr',
            'heart_rate_avg': 'heart_rate',
        }, inplace=True)
        
        # Use datetime instead of just date
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        df = self._validate_and_fill(df)
        logger.info(f"Loaded {len(df)} records from Apple Health XML")
        return df

    def _load_sample(self) -> pd.DataFrame:
        """Load the bundled sample CSV dataset."""
        sample_path = Path(__file__).parent.parent / "data" / "sample_health_data.csv"
        return self._load_csv(str(sample_path))

    def _validate_and_fill(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure required columns exist; fill missing ones with NaN."""
        for col in REQUIRED_COLUMNS:
            if col not in df.columns:
                logger.warning(f"Column '{col}' missing — filling with NaN.")
                df[col] = np.nan
        df.sort_values("timestamp", inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df
