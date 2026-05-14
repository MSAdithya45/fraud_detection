from scipy.stats import ks_2samp


def calculate_ks(expected, actual):

    statistic, p_value = ks_2samp(expected, actual)

    return {
        "ks_statistic": statistic,
        "p_value": p_value
    }