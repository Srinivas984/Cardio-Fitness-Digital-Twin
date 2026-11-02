import numpy as np


def detect_overtraining(hr_data):

    variability = np.std(hr_data)

    if variability > 25:
        return "High"

    elif variability > 15:
        return "Moderate"

    else:
        return "Low"