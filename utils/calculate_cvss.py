def calculate_cvss(likelihood, impact):
    likelihood_map = {"Low": 0.3, "Moderate": 0.6, "High": 0.9}
    impact_map = {"Low": 0.3, "Moderate": 0.6, "High": 0.9}
    score = likelihood_map[likelihood] * impact_map[impact] * 10
    return round(score, 1), classify(score)

def classify(score):
    if score >= 9:
        return "Critical"
    elif score >= 7:
        return "High"
    elif score >= 4:
        return "Medium"
    else:
        return "Low"