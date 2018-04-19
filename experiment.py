# Author: Cameron Dykstra
# Email: dykstra.cameron@gmail.com

import os
import asyncio
import yaml
import numpy as np
import scipy.io as sio
import logging
import importlib

from program import Program, list_programs

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

dir_path = os.path.dirname(os.path.realpath(__file__))
experiments_dir = os.path.join(dir_path, 'experiments')

def list_experiments():
    return os.listdir(experiments_dir)

def load_experiment(name: str):
    module = importlib.import_module('experiments.%s' % name)
    return module.Experiment(name)

class BaseExperiment:
    def __init__(self, name: str):
        self.name = name
        self._dir = os.path.join(experiments_dir, name)
        with open(os.path.join(self._dir, 'config.yaml'), 'r') as f:
            self._config = yaml.load(f.read())
        self.programs = {}
        self.par = {}
        for prog_name in self._config['programs']:
            self.programs[prog_name] = Program(prog_name)
        self.par_def = {}
        for prog_name, prog in self.programs.items():
            for par_name, par in prog.config_get('parameters').items():
                self.par_def[par_name] = par
        self.exports = {f.replace('export_',''): getattr(self, f)
                        for f in dir(self) if callable(getattr(self, f))
                        and f.startswith('export_')}
        self.plots = {f.replace('plot_',''): getattr(self, f)
                      for f in dir(self) if callable(getattr(self, f))
                      and f.startswith('plot_')}
        self.override()
    
    # must be overridden
    # progress_handler takes arguments (progress, limit)
    async def run(self, progress_handler=None):
        pass

    # must be overridden, must return a numpy array
    def raw_data(self):
        pass

    # may be overridden to add/remove parameters exposed to the user
    # among other things, will be called at initialisation
    def override(self):
        pass

    def abort(self):
        logger.debug('aborting experiment...')
        for prog_name, prog in self.programs.items():
            prog.abort()

    def save(self, dir):
        sio.savemat(os.path.join(dir, 'raw_data.mat'), {'raw_data': self.raw_data()})
        with open(os.path.join(dir, 'par.yaml'), 'w') as f:
            yaml.dump(self.par, f, default_flow_style=False)
        with open(os.path.join(dir, 'config.yaml'), 'w') as f:
            yaml.dump({'experiment': self.name}, f, default_flow_style=False)

    def get_metadata(self):
        merged_pars = {}
        for prog_name, prog in self.programs.items():
            for par_name, par in prog.config_get('parameters').items():
                merged_pars[par_name] = par
        return {'name': self.name,
                'description': self._config['description'] if 'description' in self._config else '',
                'parameters': self.par_def,
                'exports': list(self.exports.keys()),
                'plots': list(self.plots.keys()),
                'defaults': self._config['defaults'] if 'defaults' in self._config else {}}

    def set_parameters(self, parameters):
        self.par.update(parameters)
        for prog_name, prog in self.programs.items():
            for name, value in self.par.items():
                if name in prog.config_get('parameters'):
                    prog.set_par(name, value)
