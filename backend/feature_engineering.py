import pandas as pd

def extract_features(df):

    heart_rate = df[df["type"].str.contains("HeartRate")]
    resting_hr = df[df["type"].str.contains("RestingHeartRate")]
    hrv = df[df["type"].str.contains("HeartRateVariability")]

    features = {
        "avg_heart_rate": float(heart_rate["value"].mean()),
        "resting_hr": float(resting_hr["value"].mean()),
        "hrv": float(hrv["value"].mean())
    }

    return features