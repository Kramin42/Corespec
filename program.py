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
        self.name = name
        self._dir = os.path.join(programs_dir, name)
        with open(os.path.join(self._dir, 'config.yaml'), 'r') as f:
            self._config = yaml.load(f.read())
        self.par = {}
        self._data_ready = False
        self._data = None

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

    def config_get(self, key):
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
        while self.status!=self.config_get('status.values.finished'):
            if self.has_progress:
                cur_progress = self.progress
                if progress_handler is not None and cur_progress!=prev_progress:
                    progress_handler(cur_progress)
                    prev_progress = cur_progress
            await asyncio.sleep(0.1)

    async def run(self, progress_handler=None):
        system.stop()
        self._data_ready = False

        logger.debug('run: writing ELF')
        system.write_elf(os.path.join(self._dir, self.config_get('executable')))

        logger.debug('run: writing user parameters')
        par_def = self.config_get('parameters')
        for par_name in par_def:
            if 'offset' in par_def[par_name]:
                system.write_par(
                    par_def[par_name]['offset'],
                    self.par[par_name],
                    par_def[par_name]['dtype'])
        
        logger.debug('run: writing derived parameters')
        for par_name in config.get('derived_parameters'):
            self.par[par_name] = config.get('derived_parameters.'+par_name+'.value')
            if 'offset' in config.get('derived_parameters.'+par_name):
                system.write_par(
                    config.get('derived_parameters.'+par_name+'.offset'),
                    self.par[par_name],
                    config.get('derived_parameters.'+par_name+'.dtype'))

        logger.debug('run: running')
        # reset progress
        if self.has_progress:
            system.write_par(self.config_get('progress.offset'), 0)
        # set run action
        system.write_par(
            self.config_get('action.offset'),
            self.config_get('action.values.run'))
        system.run()

        # wait until status finished
        logger.debug('run: waiting until finished')
        await self.ensure_finished(progress_handler=progress_handler)
        # read the data
        logger.debug('reading data')
        if self.config_get('output.type') == 'FIFO':
            self._data = system.read_fifo(
                self.config_get('output.offset'),
                self.config_get('output.length'),
                self.config_get('output.dtype'))
        elif self.config_get('output.type') == 'DMA':
            self._data = system.read_dma(
                self.config_get('output.offset'),
                self.config_get('output.length'),
                self.config_get('output.dtype'))
        self._data = self._data*self.config_get('output.scale_factor')
        self._data_ready = True
        logger.debug('run: finished')

    @property
    def data(self):
        if not self._data_ready:
            raise Exception('Data is not ready to be read!')
        return np.copy(self._data) # don't let them change our data!

    @property
    def status(self):
        return system.read_par(self.config_get('status.offset'))

    @property
    def progress(self):
        return system.read_par(self.config_get('progress.offset'))

    @property
    def has_progress(self):
        return 'progress' in self._config

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
