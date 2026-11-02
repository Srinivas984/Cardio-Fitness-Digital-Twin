import numpy as np


def digital_twin_heart(strategy, resting_hr, hrv):

    time_steps = 60

    hr = resting_hr
    hr_series = []

    fatigue = 0

    for t in range(time_steps):

        # Training load based on strategy
        if strategy == "HIIT":
            load = np.random.uniform(12, 18)

        elif strategy == "Steady Cardio":
            load = np.random.uniform(6, 10)

        else:
            load = np.random.uniform(2, 5)

        # HRV improves recovery
        recovery = hrv * 0.05

        # Fatigue accumulation
        fatigue += load * 0.1

        fatigue_effect = fatigue * 0.05

        hr = hr + load - recovery - fatigue_effect

        hr = max(hr, resting_hr)

        hr_series.append(hr)

    return hr_series