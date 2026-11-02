from digital_twin import digital_twin_heart
from backend.data_loader import load_health_data
from backend.preprocessing import preprocess_health_data
from backend.feature_engineering import extract_features


def simulate(strategy):

    try:

        df = load_health_data()
        df = preprocess_health_data(df)
        features = extract_features(df)

        resting_hr = features["resting_hr"]
        hrv = features["hrv"]

    except:

        resting_hr = 65
        hrv = 50

    hr_series = digital_twin_heart(strategy, resting_hr, hrv)

    return hr_series