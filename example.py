#!/usr/bin/env python3.6

import asyncio

import hardware.system as system
import logging
from program import list_programs, Program

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

async def main():
    print('available programs:', ', '.join(list_programs()))

    CPMG = Program('CPMG')
    CPMG.load_par('CPMG_par.yaml')

    outof = CPMG.get_config('progress.limit')+1

    await CPMG.run(progress_handler=lambda p: print('progress:', p, '/', outof))

    data = CPMG.data

    print('data size:', data.size)
    print('data:', data)

if __name__=='__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_until_complete(main())
    loop.run_until_complete(main())
    loop.close()
