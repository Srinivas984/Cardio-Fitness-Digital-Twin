import numpy as np


def compute_ces(hr_data):

    avg_hr = np.mean(hr_data)
    peak_hr = max(hr_data)

    efficiency = peak_hr / avg_hr

    ces = 50 + efficiency * 20

    ces = min(100, round(ces, 2))

    return ces