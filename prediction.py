from simulator import simulate
from ces_score import compute_ces

def predict_30_days(strategy):

    ces_progress = []

    base_score = 60

    for day in range(30):

        hr_data = simulate(strategy)

        ces = compute_ces(hr_data)

        # gradual improvement model
        improvement = ces * 0.05

        base_score += improvement

        if base_score > 100:
            base_score = 100

        ces_progress.append(base_score)

    return ces_progress