# Author: Cameron Dykstra
# Email: dykstra.cameron@gmail.com

import os
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
        self.dir = os.path.join(programs_dir, name)
        with open(os.path.join(self.dir, 'config.yaml'), 'r') as f:
            self.config = yaml.load(f.read())
        self.par = {}
        self.data = np.array([])

    def set_par(self, name: str, value):
        # TODO: check/cast type with config['parameters'][name]['dtype']
        self.par[name] = value

    def load_par(self, filename: str):
        new_par = {}
        with open(filename, 'r') as f:
            new_par = yaml.load(f.read())
        for name, value in new_par.items():
            self.set_par(name, value)

    def save_par(self, filename: str):
        with open(filename, 'w') as f:
            f.write(yaml.dump(self.par, default_flow_style=False))

    async def run(self):
        system.stop()
        system.write_elf(os.path.join(self.dir, self.config['executable']))
        par_def = self.config['parameters']
        for par_name in par_def:
            system.write_par(
                par_def[par_name]['offset'],
                self.par[par_name],
                par_def[par_name]['dtype'])
        system.run()
        # write run action
        system.write_par(
            self.config['action']['offset'],
            self.config['action']['values']['run'])
        # wait until status finished
        await system.wait_for_progress(
            self.config['status']['offset'],
            self.config['status']['values']['finished'])
        # return the data
        if self.config['output']['type'] == 'FIFO':
            self.data = system.read_fifo(
                self.config['output']['offset'],
                self.config['output']['length'],
                self.config['output']['dtype'])
        elif self.config['output']['type'] == 'DMA':
            pass
