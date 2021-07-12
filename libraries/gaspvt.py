
# module-level vars with getters/setters
g_pressure = 0.101  # MPa, set default in case there is no sensor
g_temperature = 293  # K, set default in case there is no sensor


def record_pressure(pressure):
    global g_pressure
    g_pressure = pressure


def record_temperature(temperature):
    global g_temperature
    g_temperature = temperature


def get_pressure():
    global g_pressure
    return g_pressure


def get_temperature():
    global g_temperature
    return g_temperature


def pseudo_critical_para(type, dense_g_r):
    if type == 1:
        if dense_g_r >= 0.7:
            Pc = 4.8815 - 0.3861 * dense_g_r
            Tc = 92.2222 + 176.6667 * dense_g_r
        else:
            Pc = 4.7780 - 0.2482 * dense_g_r
            Tc = 92.2222 + 176.6667 * dense_g_r
    elif dense_g_r >= 0.7:
        Pc = 5.1021 - 0.6895 * dense_g_r
        Tc = 132.2222 + 116.6667 * dense_g_r
    else:
        Pc = 4.7780 - 0.2482 * dense_g_r
        Tc = 106.1111 + 152.2222 * dense_g_r
    return Pc, Tc

def Z_cal(P, T, Pc, Tc):
    Pr = P / Pc
    Tr = T / Tc
    if Pr >= 0.00002 and Pr <= 1.2:
        if Tr >= 1.05 and Tr <= 1.2:
            A = 1.6643
            B = -2.2114
            C = -0.3647
            D = 1.4385
        elif Tr > 1.2 and Tr <= 1.4:
            A = 0.5222
            B = -0.8511
            C = -0.0364
            D = 1.049
        elif Tr > 1.4 and Tr <= 2:
            A = 0.1392
            B = -0.2988
            C = 0.0007
            D = 0.9969
        elif Tr > 2 and Tr <= 3:
            A = 0.0295
            B = -0.0825
            C = 0.0009
            D = 0.9967
    elif Pr > 1.2 and Pr <= 2.8:
        if Tr >= 1.05 and Tr <= 1.2:
            A = -1.357
            B = 1.4942
            C = 4.6315
            D = -4.7006
        elif Tr > 1.2 and Tr <= 1.4:
            A = 0.1717
            B = -0.3232
            C = 0.5869
            D = 0.1229
        elif Tr > 1.4 and Tr <= 2:
            A = 0.0984
            B = -0.2053
            C = 0.0621
            D = 0.858
        elif Tr > 2 and Tr <= 3:
            A = 0.0211
            B = -0.0527
            C = 0.0127
            D = 0.9549
    elif Pr > 2.8 and Pr <= 5.4:
        if Tr >= 1.05 and Tr <= 1.2:
            A = -0.3278
            B = 0.4752
            C = 1.8223
            D = -1.9036
        elif Tr > 1.2 and Tr <= 1.4:
            A = -0.2521
            B = 0.3871
            C = 1.6087
            D = -1.6635
        elif Tr > 1.4 and Tr <= 2:
            A = -0.0284
            B = 0.0625
            C = 0.4714
            D = -0.0011
        elif Tr > 2 and Tr <= 3:
            A = 0.0041
            B = 0.0039
            C = 0.0607
            D = 0.7927

    if 0.00002 < Pr < 5.4 and 1.05 < Tr < 3.0:
        Z_imperfect = Pr * (A*Tr + B) + C*Tr + D
    elif 5.4 < Pr < 15 and 1.05 < Tr < 3.0:
        Z_imperfect = Pr*((3.66*Tr + 0.711)**(-1.4667)) - 1.637/(0.319*Tr + 0.522) + 2.071
    else:
        raise Exception('Pr or Tr out of bounds, Pr: %.2f, Tr: %.2f' % (Pr, Tr))
    return Z_imperfect


def volume_cal(V1, Z1, Z2, P1, P2, T1, T2):
    V2 = V1 * (Z2 / Z1) * (T2 / T1) * (P1 / P2)
    return V2


def gas_volume_conversion(type, dens_g_r, P1, P2, T1, T2, V1):
    Pc, Tc = pseudo_critical_para(type, dens_g_r)
    Z1 = Z_cal(P1, T1, Pc, Tc)
    Z2 = Z_cal(P2, T2, Pc, Tc)
    V2 = volume_cal(V1, Z1, Z2, P1, P2, T1, T2)
    return V2
