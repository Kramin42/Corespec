#!/usr/bin/env python3.6

import asyncio
import hardware.system as system

print('driver loaded')

system.write_elf('./programs/CPMG/CPMG_DMA.elf')

#loop = asyncio.get_event_loop()
#loop.run_until_complete(system.wait_for_scan(1))
#loop.close()

