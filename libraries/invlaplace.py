import numpy as np
from time import time


def getT2Spectrum(_t, _Z, _E, T2s, fixed_alpha=None, N_alpha=16, alpha_bounds=(-4,4)):
    if fixed_alpha is not None:
        alphas = [fixed_alpha]
    else:
        alphas = np.logspace(alpha_bounds[0], alpha_bounds[1], N_alpha)
    residuals = np.zeros(N_alpha)

    t, Z, E, weights = compress(_t, _Z, _E, 100)

    K = np.array([np.exp(-t / T2) for T2 in T2s]).transpose()
    Kw = (K.transpose() * weights).transpose()
    Zw = Z * weights

    S_i = []

    t_0 = time()
    for i, alpha in enumerate(alphas):
        S = brd(Kw, Zw, alpha)
        residuals[i] = np.linalg.norm(np.dot(K, S) - Z)
        S_i.append(S)

    t_1 = time()

    if len(alphas) > 1:
        # calculate curvature of residuals curve to find optimal alpha
        h = np.log10(alphas[1] / alphas[0])
        G_1 = np.gradient(np.log10(residuals), h)
        G_2 = np.gradient(G_1, h)
        k = G_2 / np.power(1 + G_1 * G_1, 3 / 2)
        alpha_index = np.argmax(k)
    else:
        alpha_index = 0
    S = S_i[alpha_index]

    # fit is np.dot(K, S)
    return S


def compress(time, real, imag, num):
    length = time.size
    time_com = np.zeros(num)
    real_com = np.zeros(num)
    imag_com = np.zeros(num)
    weights_com = np.zeros(num)

    # pick points exponentially along the time axis
    picking = [max(i, int(length**(i/(num-1)) - 1)) for i in range(num)]

    for i in range(num):
        if i == 0 or picking[i] == picking[i-1]+1:
            time_com[i] = time[i]
            real_com[i] = real[i]
            imag_com[i] = imag[i]
            weights_com[i] = 1
        else:
            time_com[i] = np.mean(time[picking[i - 1] + 1:picking[i] + 1])
            real_com[i] = np.mean(real[picking[i - 1] + 1:picking[i] + 1])
            imag_com[i] = np.mean(imag[picking[i - 1] + 1:picking[i] + 1])
            weights_com[i] = np.sqrt(picking[i] - picking[i - 1])
    return time_com, real_com, imag_com, weights_com


def brd(A: np.ndarray, b: np.ndarray, alpha) -> np.ndarray:
    m = A.shape[1]
    n = A.shape[0]
    I = np.eye(n, n)

    M = np.dot(A, A.transpose())
    c1 = np.dot(np.linalg.inv(M+alpha*I), b)
    ck = np.dot(c1.transpose(), A)
    M2 = np.zeros((n, n))
    f = np.zeros(m)
    for k in range(100):
        AA = np.empty((n, 0))
        for i in range(m):
            if ck[i]>1.0e-6:
                AA = np.hstack((AA, np.array([A[:,i]]).transpose()))
        M2 = np.dot(AA, AA.transpose())
        c2 = np.dot(np.linalg.inv(M2+alpha*I), b)
        l = np.max(np.abs(c2 - c1))
        if l<1.0e-4:
            #print('iterations: ', k+1)
            break

        ck = np.dot(c2.transpose(), A)
        c1 = c2

    for i in range(m):
        if ck[i]>1.0e-5:
            f[i] = ck[i]
        else:
            f[i] = 0

    return f


# P.D. Teal and C. Eccles,  Inverse Problems, 31(4):045010, April
# 2015. http://dx.doi.org/10.1088/0266-5611/31/4/045010
# https://github.com/paultnz/flint
# used under the GNU Affero General Public License v3.0
def flint(K1, K2, Z, alpha, S=None, fast=False):
    maxiter = 100000

    residuals = []

    if S is None:
        S = np.ones((K1.shape[1], K2.shape[1]))

    K1K1 = np.dot(K1.T, K1)
    K2K2 = np.dot(K2.T, K2)
    K1ZK2 = np.dot(np.dot(K1.T, Z), K2)

    # Lipschitz constant
    L = 2*(K1K1.trace()*K2K2.trace() + alpha)

    tZZ = np.dot(Z, Z.T).trace()  # used for calculating the residual

    Y = S
    tt = 1
    fac1 = (L - 2*alpha)/L
    fac2 = 2/L
    lastres = np.inf
    for i in range(maxiter):
        term2 = K1ZK2 - np.dot(K1K1, np.dot(Y, K2K2))
        Snew = np.clip(fac1*Y + fac2*term2, 0, None)

        ttnew = 0.5*(1 + np.sqrt(1 + 4*tt*tt))
        trat = (tt - 1)/ttnew
        Y = Snew + trat*(Snew-S)
        tt = ttnew
        S = Snew

        if i%500 == 0:
            # don't calculate the residual every iteration, as it is slow
            normS = alpha*np.linalg.norm(S)**2
            residual = tZZ - 2*np.dot(S.T, K1ZK2).trace() + np.dot(S.T, np.dot(K1K1, np.dot(S, K2K2))).trace() + normS
            residuals.append(residual)
            res_diff_ratio = np.abs(residual - lastres)/residual
            lastres = residual
            #print(i, tt, trat, L, residual, res_diff_ratio)
            if res_diff_ratio < 1e-5 or (fast and res_diff_ratio < 1e-1):
                return S, np.array(residuals)
    raise Exception('Max iterations reached')
