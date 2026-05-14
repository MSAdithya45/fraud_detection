import numpy as np


def calculate_psi(expected, actual, bins):

    expected_counts, _ = np.histogram(expected, bins=bins)
    actual_counts, _ = np.histogram(actual, bins=bins)

    expected_perc = expected_counts / len(expected)
    actual_perc = actual_counts / len(actual)

    psi_values = []

    for e, a in zip(expected_perc, actual_perc):

        if e == 0:
            e = 0.0001

        if a == 0:
            a = 0.0001

        psi = (a - e) * np.log(a / e)

        psi_values.append(psi)

    return np.sum(psi_values)