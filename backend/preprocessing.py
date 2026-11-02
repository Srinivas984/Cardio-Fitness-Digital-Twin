import pandas as pd

def preprocess_health_data(df):

    # convert date column to datetime
    df["date"] = pd.to_datetime(df["date"])

    # convert values to numeric
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # remove invalid rows
    df = df.dropna()

    return df