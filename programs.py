# Author: Cameron Dykstra
# Email: dykstra.cameron@gmail.com

import os
import re
import ast
import operator as op
import asyncio
import logging
import yaml
import numpy as np

from hardware import system

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

dir_path = os.path.dirname(os.path.realpath(__file__))
programs_dir = os.path.join(dir_path, 'programs')

def list_programs():
    return os.listdir(programs_dir)

class Program:
    def __init__(self, name: str):
        self._dir = os.path.join(programs_dir, name)
        with open(os.path.join(self._dir, 'config.yaml'), 'r') as f:
            self._config = yaml.load(f.read())
        self.par = {}
        self._data_ready = False

    def set_par(self, name: str, value):
        # TODO: check/cast type with config['parameters'][name]['dtype']
        self.par[name] = value
        self._data_ready = False # any parameter change requires re-running

    def load_par(self, filename: str):
        new_par = {}
        with open(filename, 'r') as f:
            new_par = yaml.load(f.read())
        for name, value in new_par.items():
            self.set_par(name, value)

    def save_par(self, filename: str):
        with open(filename, 'w') as f:
            f.write(yaml.dump(self.par, default_flow_style=False))

    def get_config(self, key):
        result =  self._config
        for k in key.split('.'):
            result = result[k]
        if type(result)==str:
            m = re.search('^\$\{(.*)\}$', result)
            if m is not None:
                pieces = re.split('\{([^{}]*)\}',m.group(1))
                # now replace odd numbered pieces with appropriate parameter values
                for i in range(1,len(pieces),2):
                    pieces[i] = str(self.par[pieces[i]])
                result = safe_eval(''.join(pieces))
        return result

    async def ensure_finished(self, progress_handler=None):
        # progress_handler should return quickly:
        # no heavy processing or blocking IO
        prev_progress = 0
        while self.status!=self.get_config('status.values.finished'):
            cur_progress = self.progress
            if progress_handler is not None and cur_progress!=prev_progress:
                progress_handler(cur_progress)
                prev_progress = cur_progress
            await asyncio.sleep(0.1)

    async def run(self, progress_handler=None):
        system.stop()
        self._data_ready = False

        logger.debug('run: writing ELF')
        system.write_elf(os.path.join(self._dir, self.get_config('executable')))

        logger.debug('run: writing parameters')
        par_def = self.get_config('parameters')
        for par_name in par_def:
            system.write_par(
                par_def[par_name]['offset'],
                self.par[par_name],
                par_def[par_name]['dtype'])

        logger.debug('run: running')
        # reset progress
        system.write_par(self.get_config('progress.offset'), 0)
        # set run action
        system.write_par(
            self.get_config('action.offset'),
            self.get_config('action.values.run'))
        system.run()

        # wait until status finished
        logger.debug('run: waiting until finished')
        await self.ensure_finished(progress_handler=progress_handler)
        self._data_ready = True
        logger.debug('run: finished')

    @property
    def data(self):
        if not self._data_ready:
            raise Exception('Data is not ready to be read!')

        # read the data
        logger.debug('reading data')
        if self.get_config('output.type') == 'FIFO':
            data = system.read_fifo(
                self.get_config('output.offset'),
                self.get_config('output.length'),
                self.get_config('output.dtype'))
        elif self.get_config('output.type') == 'DMA':
            data = system.read_dma(
                self.get_config('output.offset'),
                self.get_config('output.length'),
                self.get_config('output.dtype'))
        return data # don't let them change our data!

    @property
    def status(self):
        return system.read_par(self.get_config('status.offset'))

    @property
    def progress(self):
        return system.read_par(self.get_config('progress.offset'))

# safe evaluation for computed properties
# supported operators
safe_eval_ops = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
    ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
    ast.USub: op.neg}

def safe_eval(expr):
    """
    >>> eval_expr('2^6')
    4
    >>> eval_expr('2**6')
    64
    >>> eval_expr('1 + 2*3**(4^5) / (6 + -7)')
    -5.0
    """
    return eval_(ast.parse(expr, mode='eval').body)

def eval_(node):
    if isinstance(node, ast.Num): # <number>
        return node.n
    elif isinstance(node, ast.BinOp): # <left> <operator> <right>
        return safe_eval_ops[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
        return safe_eval_ops[type(node.op)](eval_(node.operand))
    else:
        raise TypeError(node)
