#!/usr/bin/env python3.6

import asyncio

import hardware.system as system
from programs import Program

print('driver loaded')

CPMG = Program('CPMG')
CPMG.load_par('CPMG_par.yaml')

loop = asyncio.get_event_loop()
loop.run_until_complete(CPMG.run())
loop.close()

print(CPMG.data)
