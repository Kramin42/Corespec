# Driver for Microspec FPGA
# Author: Cameron Dykstra
# Email: dykstra.cameron@gmail.com

import os 
import logging
import numpy as np

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from pynq import Overlay
from elftools.elf.elffile import ELFFile

# constants
DMA_OFFSET = 0x30000000 # OS has 768M
DMA_SIZE   = 0x10000000 # 256M of DMA

dir_path = os.path.dirname(os.path.realpath(__file__))
ol = Overlay(os.path.join(dir_path, 'system.bit'))

reset = ol.microblaze_ppu.pp_reset
mem_i = ol.microblaze_ppu.microblaze_0_local_memory.axi_bram_ctrl_i
mem_d = ol.microblaze_ppu.microblaze_0_local_memory.axi_bram_ctrl_d
mem_p = ol.microblaze_ppu.microblaze_0_local_memory.axi_bram_ctrl_p
mailbox = ol.microblaze_ppu.microblaze_core.mailbox


def stop() -> None:
    reset.write(0x0, 0)
    if reset.read(0x8)!=1:
        logger.error('stop command failed!')


def run() -> None:
    reset.write(0x0, 1)
    if reset.read(0x8)!=0:
        logger.error('run command failed!')


def write_elf(path: str) -> None:
    with open(path, 'rb') as f:
        elffile = ELFFile(f)

        if elffile['e_machine'] != 189:
            logger.error('incompatible elf file, not for microblaze')

        for segment in elffile.iter_segments():
            offset = segment['p_vaddr']
            data = segment.data()
            logger.debug('writing 0x%X bytes at 0x%X', len(data), offset)
            # hack to write to the correct memory space
            if offset<mem_i.mmio.length:
                mem_i.write(offset, data)
            else:
                offset-=mem_i.mmio.length
                mem_d.write(offset, data)


def write_par(
        offset: int,
        value,
        dtype=np.dtype(np.int32)) -> None:
    value = np.array([value], dtype=dtype)[0] # must be a better way...
    # offset is a bytes offset since params could have varying size
    logger.debug('writing %s at 0x%X', value, offset)
    mem_p.write(offset, value.tobytes())

def read_par(offset: int, dtype=np.dtype(np.int32)):
    dtype = np.dtype(dtype)
    length = dtype.itemsize
    return np.frombuffer(mem_p.mmio.mem[offset:offset+length], dtype=dtype)[0]

def read_dma(
        offset: int,
        length: int,
        dtype=np.dtype(np.int32)) -> np.ndarray:
    # length is relative to the dtype size
    # offset is absolute
    dtype = np.dtype(dtype)
    length *= dtype.itemsize
    with open('/dev/mem', 'r+b') as f:
        mem = mmap(f.fileno(), DMA_SIZE, offset=DMA_OFFSET)
        data = np.frombuffer(mem[offset:offset+length], dtype=dtype)
    return data


def read_fifo(
        offset: int,
        length: int,
        dtype=np.dtype(np.int32)) -> np.ndarray:
    # length is relative to the dtype size
    # offset is absolute
    dtype = np.dtype(dtype)
    length *= dtype.itemsize
    data = np.frombuffer(mem_p.mmio.mem[offset:offset+length], dtype=dtype)
    return data
