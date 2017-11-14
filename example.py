import asyncio
import hardware.system as system

print('hardware loaded')

loop = asyncio.get_event_loop()
loop.run_until_complete(system.wait_for_scan(1))
loop.close()
