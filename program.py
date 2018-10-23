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
logger.setLevel(logging.ERROR)

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
        self._acc_data = None
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

    async def ensure_finished(self, progress_handler=None, message_handler=None):
        # progress_handler should return quickly:
        # no heavy processing or blocking IO
        prev_progress = -1
        rotbuf_scandelayed = False
        rotbuf_finished = True # use this to prevent early ending when using the rotary buffer
        rotbuf = 'rotbuf' in self.config_get('output') and self.config_get('output.rotbuf')
        if rotbuf:
            rotbuf_read_index = system.read_par(
                int(self.config_get('output.rotbuf_read_index_offset')), 'uint32')
            rotbuf_length = system.read_par(
                int(self.config_get('output.rotbuf_length_offset')), 'uint32')
            rotbuf_total = int(self.config_get('output.rotbuf_total'))
            block_skip = 0
            if 'block_skip' in self.config_get('output'):
                block_skip = int(self.config_get('output.block_skip'))
            block_count = int(self.config_get('output.block_count'))
            block_length = int(self.config_get('output.block_length'))
            rotbuf_counter = 0
            self._acc_data = np.zeros(
                block_count*(block_length+block_skip),
                dtype=np.float32)
            rotbuf_finished = False
        while self.status!=self.config_get('status.values.finished') or not rotbuf_finished:
            final_run_done = self.status==self.config_get('status.values.finished')
            if self._aborted:
                raise Exception('Aborted')
            if self.has_progress:
                cur_progress = self.progress
                if progress_handler is not None and cur_progress!=prev_progress:
                    progress_handler(cur_progress, self.config_get('progress.limit')+1)
                    prev_progress = cur_progress

            if rotbuf:
                rotbuf_write_index = system.read_par(
                    int(self.config_get('output.rotbuf_write_index_offset')), 'uint32')
                if not rotbuf_scandelayed and (rotbuf_write_index+1)%rotbuf_length == rotbuf_read_index:
                    rotbuf_scandelayed = True
                    message_handler('Warning: scans delayed by full memory buffer.', type='warning')
                if rotbuf_write_index!=rotbuf_read_index and not rotbuf_finished:
                    logger.debug('rotbuf_read_index: %i, rotbuf_write_index: %i, rotbuf_length: %i' % (rotbuf_read_index, rotbuf_write_index, rotbuf_length))
                    # calculate the length of continuous readable data
                    if rotbuf_write_index>rotbuf_read_index:
                        scans_to_read = rotbuf_write_index - rotbuf_read_index
                    else:
                        scans_to_read = rotbuf_length - rotbuf_read_index
                    self._acc_data += np.sum(
                        np.split(
                            system.read_dma(
                                offset=int(self.config_get('output.offset')),
                                reloffset=block_count*(block_skip+block_length)*rotbuf_read_index,
                                length=block_count*(block_length+block_skip)*scans_to_read,
                                dtype=self.config_get('output.dtype')),
                            scans_to_read),
                        axis=0)

                    # allow partial data to be retrieved
                    rotbuf_counter += scans_to_read
                    self._data = np.array(np.split(self._acc_data/rotbuf_counter, block_count))[:, block_skip:].flatten()
                    self._data = system.calibrate(self._data, self.get_scaled_par('dwell_time'))
                    if 'scale_factor' in self.config_get('output'):
                        self._data = self._data * self.config_get('output.scale_factor')
                    self._data_ready = True

                    rotbuf_read_index+=scans_to_read
                    rotbuf_read_index%=rotbuf_length
                    system.write_par(int(self.config_get('output.rotbuf_read_index_offset')), rotbuf_read_index, 'uint32')
                    rotbuf_finished = (rotbuf_counter == rotbuf_total)

            await asyncio.sleep(0.1)

    async def run(self, progress_handler=None, message_handler=None):
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

        rotbuf = 'rotbuf' in self.config_get('output') and self.config_get('output.rotbuf')

        if self.config_get('output.type') == 'DMA':
            # DMA rotating buffer
            if rotbuf:
                block_count = int(self.config_get('output.block_count'))
                block_length = int(self.config_get('output.block_length'))
                block_skip = 0
                if 'block_skip' in self.config_get('output'):
                    block_skip = int(self.config_get('output.block_skip'))
                dtype_size = np.dtype(self.config_get('output.dtype')).itemsize
                rotbuf_length = int(system.DMA_SIZE/((block_length+block_skip)*block_count*dtype_size))
                if rotbuf_length<3: # must be at least 2 for buffer to work
                    raise Exception('Number of samples per scan too large, cannot fit in memory')
                system.write_par(
                    int(self.config_get('output.rotbuf_length_offset')),
                    rotbuf_length,
                    'uint32')
                system.write_par(
                    int(self.config_get('output.rotbuf_read_index_offset')),
                    0,
                    'uint32')
                system.write_par(
                    int(self.config_get('output.rotbuf_write_index_offset')),
                    0,
                    'uint32')
        
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
        await self.ensure_finished(progress_handler=progress_handler, message_handler=message_handler)
        # read the data
        logger.debug('run: reading data')
        if self.config_get('output.type') == 'FIFO':
            self._data = system.read_fifo(
                offset=int(self.config_get('output.offset')),
                length=int(self.config_get('output.length')),
                dtype=self.config_get('output.dtype'))
        elif self.config_get('output.type') == 'DMA':
            cfg_output = self.config_get('output')
            if not rotbuf:
                # block method for (e.g.) skipping ignore_sample data
                if 'block_count' in cfg_output and 'block_length' in cfg_output:
                    block_count = int(self.config_get('output.block_count'))
                    block_length = int(self.config_get('output.block_length'))
                    self._data = np.empty(
                        block_count*block_length,
                        dtype=self.config_get('output.dtype'))
                    block_skip = 0
                    if 'block_skip' in cfg_output:
                        block_skip = int(self.config_get('output.block_skip'))
                    logger.debug('reading %i blocks, length %i, skip %i' % (block_count, block_length, block_skip))
                    tempdata = system.read_dma(
                        offset=int(self.config_get('output.offset')),
                        length=(block_skip+block_length)*block_count,
                        dtype=self.config_get('output.dtype'))
                    self._data = np.array(np.split(tempdata, block_count))[:,block_skip:].flatten()
                    #for i in range(block_count):
                    #    self._data[i*block_length:(i+1)*block_length] = \
                    #        tempdata[block_skip+i*(block_length+block_skip):(i+1)*(block_length+block_skip)]
                else:  # basic method
                    self._data = system.read_dma(
                        offset=int(self.config_get('output.offset')),
                        length=int(self.config_get('output.length')),
                        dtype=self.config_get('output.dtype'))

        if not rotbuf:
            self._data = system.calibrate(self._data, self.get_scaled_par('dwell_time'))
            if 'scale_factor' in self.config_get('output'):
                self._data = self._data*self.config_get('output.scale_factor')
            self._data_ready = True

        if message_handler:
            try:
                adc_overflow_count = system.read_par(self.config_get('adc_overflow_count.offset'))
                logger.debug('ADC overflow count: %i' % adc_overflow_count)
                # TODO: test adc overflow count
                if adc_overflow_count>0:
                    message_handler('ADC overflow detected! (count: %i)' % adc_overflow_count, type='warning')
            except Exception as e: # errors here are not important
                logger.debug('Error during warning check: %s' % str(e))
        logger.debug('run: finished')
        logger.debug('error: %i' % system.read_par(0x08))
        logger.debug('debug1: %i' % system.read_par(0x0c))
        logger.debug('debug2: %i' % system.read_par(0x10))
        logger.debug('status: %i' % self.status)
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
