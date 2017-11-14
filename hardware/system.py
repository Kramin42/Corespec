# Driver for Microspec FPGA
# Author: Cameron Dykstra
# Email: dykstra.cameron@gmail.com

import asyncio
import os 
import logging

from pynq import Overlay

dir_path = os.path.dirname(os.path.realpath(__file__))
ol = Overlay(os.path.join(dir_path, 'system.bit'))

reset = ol.microblaze_ppu.pp_reset
mem_i = ol.microblaze_ppu.microblaze_0_local_memory.axi_bram_ctrl_i
mem_d = ol.microblaze_ppu.microblaze_0_local_memory.axi_bram_ctrl_d
mem_p = ol.microblaze_ppu.microblaze_0_local_memory.axi_bram_ctrl_p

mailbox = ol.microblaze_ppu.microblaze_core.mailbox

def stop():
    reset.write(0x0, 0)
    if reset.read(0x8)!=1:
        logging.error('stop command failed!')

def run():
    reset.write(0x0, 1)
    if reset.read(0x8)!=0:
        logging.error('run command failed!')

def status():
    return mem_p.read(0x4)

async def wait_for_scan(n):
    i = mem_p.read(0x1c)
    while i<n:
        await asyncio.sleep(1)
        i = mem_p.read(0x1c)
    return i
