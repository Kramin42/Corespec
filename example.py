#!/usr/bin/env python3.6

import asyncio

import hardware.system as system
import logging
import time
from program import list_programs, Program

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

async def main():
    print('available programs:', ', '.join(list_programs()))

    prog = Program('Wobble')
    prog.load_par('Wobble_par.yaml')

    await prog.run(progress_handler=lambda p, l: print('progress:', p, '@',time.time()))

    data = prog.data

    print('data size:', data.size)
    #print('data:', data)

if __name__=='__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
