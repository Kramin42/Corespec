#!/usr/bin/env python3.6

RMS_0dbm_nominal = 7800
RMS_tol = 0.1
bit_count_tol = 0.1

samples = 256000

warning = False

import numpy as np
from hardware import system

system.stop()
system.write_elf('programs/Raw/RAW_DMA.elf')
system.write_par(0xc4, samples/2)
system.write_par(0x0, 1)
system.run()
while system.read_par(0x4)!=10:
    pass

data = system.read_dma(0, samples, "int16")
print('int16 range: -32767 to +32768')
print('data[:10]:', data[:10])

data_float = data.astype(float)

RMS = np.sqrt(np.mean(data_float*data_float))

print('data max:', data.max(), ', min:', data.min(), ', p-p:', data_float.max()-data_float.min())
print('data mean:', data_float.mean(), ', RMS:', RMS)

if RMS < RMS_0dbm_nominal*(1-RMS_tol) or RMS > RMS_0dbm_nominal*(1+RMS_tol):
    warning = True
    print("WARNING: check RMS level! Nominal %i for 0dBm input (223 mV rms)." % RMS_0dbm_nominal)

count_test_max = (1+bit_count_tol)*samples/2
count_test_min = (1-bit_count_tol)*samples/2
for i in range(16):
    mask = (i+1)**2
    count = np.sum(np.bitwise_and(data, mask)/mask)
    print('bit %i count: %d' % (i, count))
    if count == 0 or count == samples:
        warning = True
        print('WARNING: bad connection for bit %i!' % i)
    elif count < count_test_min or count > count_test_max:
        warning = True
        print('WARNING: possibly bad connection with bit %i' % i)

np.save('adc_raw_data', data)

if warning:
    print('CHECK WARNINGS')
else:
    print('ALL GOOD')
