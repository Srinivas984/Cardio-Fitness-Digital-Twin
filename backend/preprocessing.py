"""
preprocessing.py
----------------
Cleans and normalizes raw wearable data.

Steps:
  1. Remove physiologically impossible HR values
  2. Impute missing HRV with rolling median
  3. Parse and validate timestamps
  4. Normalize step counts
  5. Add activity classification column
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Physiological bounds
HR_MIN, HR_MAX = 30, 220        # bpm
HRV_MIN, HRV_MAX = 5, 200      # ms (SDNN)
STEPS_MIN = 0


class Preprocessor:
    """Cleans raw cardiovascular data for downstream modeling."""

    def __init__(self, hr_min=HR_MIN, hr_max=HR_MAX):
        self.hr_min = hr_min
        self.hr_max = hr_max

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """Full preprocessing pipeline."""
        df = df.copy()
        df = self._validate_timestamps(df)
        df = self._clean_heart_rate(df)
        df = self._impute_hrv(df)
        df = self._clean_steps(df)
        df = self._add_activity_label(df)
        df = self._normalize_features(df)
        logger.info(f"Preprocessing complete. {len(df)} records retained.")
        return df

    def _validate_timestamps(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert timestamp column and drop rows with invalid dates."""
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        invalid = df["timestamp"].isna().sum()
        if invalid > 0:
            logger.warning(f"Dropped {invalid} rows with invalid timestamps.")
        df.dropna(subset=["timestamp"], inplace=True)
        df.sort_values("timestamp", inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df

    def _clean_heart_rate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove HR values outside physiological range."""
        before = len(df)
        mask = df["heart_rate"].between(self.hr_min, self.hr_max)
        df = df[mask | df["heart_rate"].isna()].copy()
        dropped = before - len(df)
        if dropped > 0:
            logger.warning(f"Removed {dropped} rows with invalid HR values.")
        # Interpolate short gaps in HR
        df["heart_rate"] = df["heart_rate"].interpolate(method="linear", limit=3)
        return df

    def _impute_hrv(self, df: pd.DataFrame) -> pd.DataFrame:
        """Impute missing HRV values using rolling median (window=5)."""
        if "hrv_sdnn" in df.columns:
            missing = df["hrv_sdnn"].isna().sum()
            df["hrv_sdnn"] = df["hrv_sdnn"].clip(lower=HRV_MIN, upper=HRV_MAX)
            # Rolling imputation
            rolling_median = df["hrv_sdnn"].rolling(window=5, min_periods=1).median()
            df["hrv_sdnn"] = df["hrv_sdnn"].fillna(rolling_median)
            if missing > 0:
                logger.info(f"Imputed {missing} missing HRV values.")
        return df

    def _clean_steps(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure steps are non-negative integers."""
        if "steps" in df.columns:
            df["steps"] = df["steps"].clip(lower=STEPS_MIN).fillna(0).astype(int)
        return df

    def _add_activity_label(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Classify intensity based on heart rate zones:
          - Rest:      HR < 60% max (~< 100)
          - Moderate:  100 <= HR < 140
          - Vigorous:  HR >= 140
        """
        if "activity_type" not in df.columns:
            conditions = [
                df["heart_rate"] < 100,
                (df["heart_rate"] >= 100) & (df["heart_rate"] < 140),
                df["heart_rate"] >= 140,
            ]
            choices = ["rest", "moderate", "vigorous"]
            df["activity_type"] = np.select(conditions, choices, default="rest")
        return df

    def _normalize_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add normalized versions of numeric columns (0–1 range)."""
        for col in ["heart_rate", "hrv_sdnn", "steps"]:
            if col in df.columns:
                col_min = df[col].min()
                col_max = df[col].max()
                rng = col_max - col_min
                df[f"{col}_norm"] = (df[col] - col_min) / rng if rng > 0 else 0.5
        return df
