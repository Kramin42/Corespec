
import os
import asyncio
import yaml
import numpy as np
import logging
import importlib
from abc import ABC, abstractmethod

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

class BaseExperiment(ABC):
    def __init__(self, name: str):
        self.name = name
        self._dir = os.path.join(experiments_dir, name)
        with open(os.path.join(self._dir, 'config.yaml'), 'r') as f:
            self._config = yaml.load(f.read())
        self.programs = {}
        for prog_name in self._config['programs']:
            self.programs[prog_name] = Program(prog_name)
        super().__init__()

    @abstractmethod
    def run(self):
        pass
