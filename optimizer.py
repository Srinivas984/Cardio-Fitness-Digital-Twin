from simulator import simulate
from ces_score import compute_ces

def find_best_strategy():

    strategies = [
        "Recovery",
        "Steady Cardio",
        "HIIT"
    ]

    best_strategy = None
    best_score = -1

    results = {}

    for s in strategies:

        hr_data = simulate(s)

        ces = compute_ces(hr_data)

        results[s] = ces

        if ces > best_score:
            best_score = ces
            best_strategy = s

    return best_strategy, best_score, results