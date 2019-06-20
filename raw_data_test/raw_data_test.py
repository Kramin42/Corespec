#!/usr/bin/env python3.6

samples = 64000

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
print('data:', data)

for i in range(16):
    mask = (i+1)**2
    count = np.sum(np.bitwise_and(data, mask)/mask)
    print('bit %i count: %d' % (i, count))

np.save('data', data)
