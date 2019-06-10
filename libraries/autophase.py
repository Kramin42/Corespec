import numpy as np
import scipy.optimize as opt

def get_autophase(y, t0=0, dwelltime=1):
    # returns phase to be applied
    PADTO = 10000
    if len(y) < PADTO:
        y_pad = np.concatenate((y, np.zeros(PADTO - len(y), dtype=np.complex)))
    else:
        y_pad = y
    fft_y = np.fft.fftshift(np.fft.fft(y_pad))
    if t0 != 0:
        fft_f = np.fft.fftshift(np.fft.fftfreq(len(fft_y), dwelltime))
        fft_y *= np.exp(1j * 2 * np.pi * -t0 * fft_f)  # correct for time shift

    def minf(phi):
        fft_y_phased = fft_y * np.exp(1j * phi[0])
        return (fft_y_phased.imag ** 2).sum() - (fft_y_phased.real ** 2).sum()

    res = opt.minimize(minf, np.array([0]), method='nelder-mead')

    phi = res['x'][0]
    fft_y_phased = fft_y * np.exp(1j*phi)
    if fft_y_phased.sum() < 0:
        phi += np.pi
    return phi
