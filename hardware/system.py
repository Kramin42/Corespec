# Driver for Microspec FPGA
# Author: Cameron Dykstra
# Email: dykstra.cameron@gmail.com

import os
import shutil
import logging
import numpy as np
import yaml
from mmap import mmap

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

dir_path = os.path.dirname(os.path.realpath(__file__))

def load_config(file_name):
    with open(os.path.join(dir_path, file_name), 'r') as f:
        return yaml.load(f.read())

CONFIG = load_config('default_config.yaml')

try:
    CONFIG.update(load_config('config.yaml'))
except IOError:
    shutil.copyfile(os.path.join(dir_path, 'default_config.yaml'), os.path.join(dir_path, 'config.yaml'))

from pynq import Overlay
from pynq.lib import AxiGPIO
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

zynq_gpio = AxiGPIO(ol.zynq_gpio).channel1

def set_flow_enabled(b):
    zynq_gpio.write(0 if b else 1, 0x1)  # 0 is the flowing state


def stop() -> None:
    reset.write(0x0, 0)
    logger.debug('reset read: %i' % reset.read(0x8))
    if reset.read(0x8)!=1:
        logger.error('stop command failed!')


def run() -> None:
    reset.write(0x0, 1)
    logger.debug('reset read: %i' % reset.read(0x8))
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
                logger.debug('writing to D mem at offset 0x%X' % offset)
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
        reloffset: int=0,
        dtype=np.dtype(np.int32)) -> np.ndarray:
    # length is relative to the dtype size
    # offset is absolute
    # skip is relative to the dtype size
    dtype = np.dtype(dtype)
    length *= dtype.itemsize
    offset += reloffset*dtype.itemsize
    with open('/dev/mem', 'r+b') as f:
        mem = mmap(f.fileno(), DMA_SIZE, offset=DMA_OFFSET)
        logger.debug('reading from %i to %i' % (offset, offset+length))
        data = np.frombuffer(mem[offset:offset+length], dtype=dtype)
    return data.astype(np.float32)


def read_fifo(
        offset: int,
        length: int,
        dtype=np.dtype(np.int32)) -> np.ndarray:
    # length is relative to the dtype size
    # offset is absolute
    dtype = np.dtype(dtype)
    length *= dtype.itemsize
    data = np.frombuffer(mem_p.mmio.mem[offset:offset+length], dtype=dtype)
    return data.astype(np.float32)


def calibrate(
        data: np.ndarray,
        decimation: int=None) -> np.ndarray:
    data = data * CONFIG['input_calibration']
    if decimation is not None:
        Bmax = CONFIG['DSP_CIC_N']*np.log2(decimation*CONFIG['DSP_CIC_M']) + CONFIG['DSP_CIC_B']
        # FIXME: the 0.745 factor here is for systems which were calibrated before this correction was implemented,
        # and should be eventually removed. Calibration was done at a decimation of 50.
        # Bmax = 4*np.log2(50*2)+16, 1/(2**(np.ceil(Bmax) - Bmax)) = 0.745
        data = 0.745 * data * (2**(np.ceil(Bmax) - Bmax))
    return data
