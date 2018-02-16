# Author: Cameron Dykstra
# Email: dykstra.cameron@gmail.com

import os
import asyncio
import yaml
import numpy as np
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
        for prog_name in self._config['programs']:
            self.programs[prog_name] = Program(prog_name)
        self.exports = {f.replace('export_',''): getattr(self, f)
                        for f in dir(self) if callable(getattr(self, f))
                        and f.startswith('export_')}
        self.plots = {f.replace('plot_',''): getattr(self, f)
                      for f in dir(self) if callable(getattr(self, f))
                      and f.startswith('plot_')}
    
    # must be overridden
    # progress_handler takes arguments (progress, limit)
    async def run(self, progress_handler=None):
        pass
    
    # may be overridden to add/remove parameters
    # exposed to the user
    def get_metadata(self):
        merged_pars = {}
        for prog_name, prog in self.programs.items():
            for par_name, par in prog.config_get('parameters').items():
                merged_pars[par_name] = par
        return {'name': self.name,
                'description': self._config['description'],
                'parameters': merged_pars,
                'exports': list(self.exports.keys()),
                'plots': list(self.plots.keys())}
    
    # may be overridden in conjunction with get_metadata() 
    def set_parameters(self, parameters):
        for prog_name, prog in self.programs.items():
            for name, value in parameters.items():
                if name in prog.config_get('parameters'):
                    prog.set_par(name, value)

