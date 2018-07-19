#!/usr/bin/env python3.6

import asyncio

import hardware.system as system
import logging
import time
from program import list_programs, Program

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.debug('mem I offset: 0x%x' % system.mem_i.mmio.base_addr)
logger.debug('mem I size: 0x%x' % system.mem_i.mmio.length)
logger.debug('mem D offset: 0x%x' % system.mem_d.mmio.base_addr)
logger.debug('mem D size: 0x%x' % system.mem_d.mmio.length)
logger.debug('mem P offset: 0x%x' % system.mem_p.mmio.base_addr)
logger.debug('mem P size: 0x%x' % system.mem_p.mmio.length)

async def main():
    print('available programs:', ', '.join(list_programs()))

    prog = Program('Noise_DMA')
    prog.load_par('example.par')

    await prog.run(progress_handler=lambda p, l: print('progress:', p, '@',time.time()))

    data = prog.data

    print('data size:', data.size)
    print('data:', data)

if __name__=='__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
