# Author: Cameron Dykstra
# Email: dykstra.cameron@gmail.com

import os
import shutil
import re
import ast
import operator as op
import asyncio
import logging
import yaml
import numpy as np

from config import CONFIG

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

dir_path = os.path.dirname(os.path.realpath(__file__))
programs_dir = os.path.join(dir_path, 'programs')

if CONFIG['dummy_hardware']:
    from dummy import system
else:
    from hardware import system

def list_programs():
    return os.listdir(programs_dir)

class Program:
    def __init__(self, name: str):
        self.name = name
        self._dir = os.path.join(programs_dir, name)
        with open(os.path.join(self._dir, 'config.yaml'), 'r') as f:
            self._config = yaml.load(f.read())
        self.par = {}
        self.par_deps = {}
        self._data_ready = False
        self._data = None
        self._aborted = False

    def set_par(self, name: str, value):
        # TODO: check/cast type with config['parameters'][name]['dtype']
        self.par[name] = value
        self._data_ready = False # any parameter change requires re-running

    def load_par(self, filename: str):
        with open(filename, 'r') as f:
            new_par = yaml.load(f.read())
        for name, value in new_par.items():
            self.set_par(name, value)

    def save_par(self, filename: str):
        with open(filename, 'w') as f:
            f.write(yaml.dump(self.par, default_flow_style=False))

    def config_get(self, key):
        result = self._config
        for k in key.split('.'):
            result = result[k]
        if type(result)==str:
            m = re.search('^\$\{(.*)\}$', result)
            if m is not None:
                pieces = re.split('\{([^{}]*)\}',m.group(1))
                # now replace odd numbered pieces with appropriate parameter values
                deps = []
                for i in range(1,len(pieces),2):
                    deps.append(pieces[i])
                    pieces[i] = str(self.get_scaled_par(pieces[i]))
                self.par_deps[key] = deps # update dependency tracking
                logger.debug('setting %s deps to %s' % (key, ','.join(deps)))
                result = safe_eval(''.join(pieces))
        return result

    # TODO: possibly this should be the only way to read the parameter values
    def get_scaled_par(self, par_name):
        par_def = self.config_get('parameters.'+par_name)
        value = self.par[par_name]
        if 'scaling' in par_def:
            value *= par_def['scaling']
        return value

    def expand_par_deps(self, key):
        deps = self.par_deps[key]
        done = False
        while not done:
            logger.debug(deps)
            done = True
            new_deps = []
            for par_name in deps:
                if 'derived_parameters.'+par_name+'.value' in self.par_deps:
                    new_deps+=self.par_deps['derived_parameters.'+par_name+'.value']
                    done = False
                else:
                    new_deps.append(par_name)
            deps = new_deps
        return deps

    async def ensure_finished(self, progress_handler=None):
        # progress_handler should return quickly:
        # no heavy processing or blocking IO
        prev_progress = 0
        while self.status!=self.config_get('status.values.finished'):
            if self._aborted:
                raise Exception('Aborted')
            if self.has_progress:
                cur_progress = self.progress
                if progress_handler is not None and cur_progress!=prev_progress:
                    progress_handler(cur_progress, self.config_get('progress.limit')+1)
                    prev_progress = cur_progress
            await asyncio.sleep(0.1)

    async def run(self, progress_handler=None, warning_handler=None):
        system.stop()
        self._aborted = False
        self._data_ready = False

        logger.debug('run: writing ELF')
        system.write_elf(os.path.join(self._dir, self.config_get('executable')))

        logger.debug('run: writing user parameters')
        try:
            par_def = self.config_get('parameters')
        except KeyError as e:
            logger.warning(e)
            par_def = None
        if par_def is not None:
            for par_name in par_def:
                if 'min' in self.config_get('parameters.'+par_name):
                    min = self.config_get('parameters.'+par_name+'.min')
                    if self.par[par_name] < min:
                        raise Exception('Parameter too small: %s=%s < %s' % (par_name, self.par[par_name], min))
                if 'max' in self.config_get('parameters.'+par_name):
                    max = self.config_get('parameters.'+par_name+'.max')
                    if self.par[par_name] > max:
                        raise Exception('Parameter too large: %s=%s > %s' % (par_name, self.par[par_name], max))
                if 'offset' in par_def[par_name]:
                    system.write_par(
                        par_def[par_name]['offset'],
                        self.get_scaled_par(par_name),
                        par_def[par_name]['dtype'])

        logger.debug('run: writing derived parameters')
        try:
            der_par_def = self.config_get('derived_parameters')
        except KeyError as e:
            logger.warning(e)
            der_par_def = None
        if der_par_def is not None:
            for par_name in der_par_def:
                self.par[par_name] = self.config_get('derived_parameters.'+par_name+'.value')
                if 'min' in self.config_get('derived_parameters.'+par_name):
                    min = self.config_get('derived_parameters.'+par_name+'.min')
                    if self.par[par_name] < min:
                        raise Exception('Derived parameter too small: %s=%s < %s, derived from: %s' %
                                        (par_name, self.par[par_name], min,
                                         ', '.join(self.expand_par_deps('derived_parameters.' + par_name + '.value'))))
                if 'max' in self.config_get('derived_parameters.'+par_name):
                    max = self.config_get('derived_parameters.'+par_name+'.max')
                    if self.par[par_name] > max:
                        raise Exception('Derived parameter too large: %s=%s > %s, derived from: %s' %
                                        (par_name, self.par[par_name], max,
                                         ', '.join(self.expand_par_deps('derived_parameters.' + par_name + '.value'))))
                if 'offset' in self.config_get('derived_parameters.'+par_name):
                    system.write_par(
                        self.config_get('derived_parameters.'+par_name+'.offset'),
                        self.par[par_name],
                        self.config_get('derived_parameters.'+par_name+'.dtype'))
        
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
        logger.debug('run: reading data')
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
        try:
            self._data = self._data*self.config_get('output.scale_factor')
        except KeyError as e: # no scale factor set in config
            logger.warning(e)
        self._data_ready = True
        if warning_handler:
            try:
                adc_overflow_count = system.read_par(self.config_get('adc_overflow_count.offset'))
                # TODO: test adc overflow count
                #if adc_overflow_count>0:
                #    warning_handler('ADC overflow detected! (count: %i)' % adc_overflow_count)
            except Exception as e: # errors here are not important
                logger.debug('Error during warning check: %s' % str(e))
        logger.debug('run: finished')
        system.stop()

    def abort(self):
        logger.debug('aborting run...')
        system.stop()
        # trigger ensure_finished to exit
        self._aborted = True

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
