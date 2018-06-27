import os 
import logging
import numpy as np
from time import sleep, time

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

status = 0
run_time = time()

def stop() -> None:
    logger.debug('stopping')


def run() -> None:
    global run_time
    run_time = time()


def write_elf(path: str) -> None:
    pass


def write_par(
        offset: int,
        value,
        dtype=np.dtype(np.int32)) -> None:
    logger.debug('writing %s at 0x%X', value, offset)

def read_par(offset: int, dtype=np.dtype(np.int32)):
    if offset==4:
        if time()-run_time > 1:
            return 10
        else:
            return 2
    return 0

def read_dma(
        offset: int,
        length: int,
        dtype=np.dtype(np.int32)) -> np.ndarray:
    data = None
    return data


def read_fifo(
        offset: int,
        length: int,
        dtype=np.dtype(np.int32)) -> np.ndarray:
    #data = np.random.randcompl(-1000000, 1000000, size=length, dtype=dtype)
    data = np.zeros(int(length/2), dtype=np.complex64)
    x = np.linspace(0,data.size,data.size,endpoint=False)
    for i in range(10):
        data += 100*np.exp(1j*np.random.random_sample()*10*x)*np.exp(-np.random.random_sample()*0.05*x)
    data += 1000 * np.exp(1j*0.0*x) * np.exp(-0.005 * x)
    data += (1j*np.random.sample(data.size)+np.random.sample(data.size)-0.5j-0.5)*100
    return data.view(np.float32).astype(np.int32)
