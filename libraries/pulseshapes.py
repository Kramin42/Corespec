
import numpy as np
from scipy import signal

# TODO: load gradient calibration from config
#GAMMA_G_MAX = 6.5e3  # Hz/mm, roughly (6e3 for Z grad, 7e3 for X/Y grad)
GAMMA = 42.5775e6 # Hz/T
G_MAX = 0.15  # T/m
RF_SPACING_MIN = 8e-6

def calc_soft_pulse(pulse_width, slice_width, flip_angle=90, gradient=G_MAX, N_max=256):

    if slice_width == 0:
        return 1, pulse_width, np.array([1.0])

    N = int(pulse_width/RF_SPACING_MIN)
    if N > N_max:
        N = N_max
    spacing = pulse_width/N

    # SLR method see http://ee-classes.usc.edu/ee591/library/Pauly-SLR.pdf
    a = [5.309e-3, 7.114e-2, -4.761e-1, -2.66e-3, -5.941e-1, -4.278e-1]
    delta_1_eff = 0.01
    delta_2_eff = 0.01

    # for 90 pulse
    if flip_angle == 90:
        delta_1 = np.sqrt(delta_1_eff / 2)
        delta_2 = delta_2_eff / np.sqrt(2)
    elif flip_angle == 180:
        delta_1 = delta_1_eff/8
        delta_2 = np.sqrt(delta_2_eff/2)
    else:
        delta_1 = delta_1_eff
        delta_2 = delta_2_eff
    # for spin echo
    # delta_1 = delta_1_eff/4
    # delta_2 = np.sqrt(delta_2_eff)

    gamma_G = GAMMA*gradient
    B = gamma_G * slice_width
    TB = pulse_width * B
    L_1 = np.log10(delta_1)
    L_2 = np.log10(delta_2)
    D_inf = (a[0] * L_1 * L_1 + a[1] * L_1 + a[2]) * L_2 + (a[3] * L_1 * L_1 + a[4] * L_1 + a[5])
    W = D_inf / TB
    BW = B * W
    F_sample = N / pulse_width
    F_pass = ((B - BW) / 2) / F_sample
    F_stop = ((B + BW) / 2) / F_sample

    if F_pass < 0:
        raise Exception("Slice Width*Pulse Width product too small (%f < %f)." % (pulse_width*slice_width, D_inf/gamma_G))

    points = signal.remez(N, [0, F_pass, F_stop, 0.5], [1, 0], [1 / delta_1, 1 / delta_2])
    points *= 1 / np.max(points)

    return N, spacing, points
