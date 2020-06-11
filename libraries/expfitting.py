import numpy as np
from scipy.optimize import curve_fit

def single_exp(x, a, b):
    return a * np.exp(-b * x)


def multi_exp(x, *args):
    return np.sum([a * np.exp(-b * x) for a, b in zip(args[::2], args[1::2])], axis=0)


def fit_multi_exp(x, y, weights=None, N_exp=2, T2_min=10**-2, T2_max=10**2):
    sigma = None
    if weights is not None:
        sigma = 1 / weights
    spopt, spcov = curve_fit(single_exp, x, y, sigma=sigma, p0=[0, 1], bounds=([0, 1/T2_max], [np.inf, 1/T2_min]))
    mp0 = [0, spopt[1]] * N_exp
    mp0[0] = spopt[0]
    # set up initial guesses for decay parameter
    mp0[1::2] = [spopt[1] * (2 ** (i)) for i in range(N_exp)]
    mp0[1::2] = np.clip(mp0[1::2], 1 / T2_max, 1 / T2_min)
    mpopt, mpcov = curve_fit(multi_exp, x, y, sigma=sigma, p0=mp0, bounds=([0, 1/T2_max]*N_exp, [np.inf, 1/T2_min]*N_exp))
    y_fit = multi_exp(x, *mpopt)
    mstderr = np.sqrt(np.sum((y_fit - y) ** 2) / len(y))
    return mpopt, mstderr
