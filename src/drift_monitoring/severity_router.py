def determine_severity(score):

    if score < 0.15:
        return "LOW"

    elif score < 0.30:
        return "MEDIUM"

    return "HIGH"