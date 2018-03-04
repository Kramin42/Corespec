# Author: Cameron Dykstra
# Email: dykstra.cameron@gmail.com

import os
import yaml
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

dir_path = os.path.dirname(os.path.realpath(__file__))
workspaces_dir = os.path.join(dir_path, 'workspaces')


def list_workspaces():
    workspaces = os.listdir(workspaces_dir)
    for workspace in workspaces:
        # ensure directory structure
        os.makedirs(os.path.join(workspaces_dir, workspace, 'parameters'), exist_ok=True)
        os.makedirs(os.path.join(workspaces_dir, workspace, 'data'), exist_ok=True)
    return workspaces


class Workspace:
    def __init__(self, name):
        self.name = name
        self._dir = os.path.join(workspaces_dir, name)
        self._par_dir = os.path.join(self._dir, 'parameters')
        self._data_dir = os.path.join(self._dir, 'data')

    def list_par_sets(self):
        return [s[:-5] for s in os.listdir(self._par_dir) if s.endswith('.yaml')] # [:-5] removes the '.yaml' part

    def load_par_set(self, name):
        with open(os.path.join(self._par_dir, name+'.yaml'), 'r') as f:
            return yaml.load(f.read())

    def save_par_set(self, name, parameters):
        with open(os.path.join(self._par_dir, name+'.yaml'), 'w') as f:
            yaml.dump(parameters, f, default_flow_style=False)

    def new_data_dir(self, prefix):
        basedirname = prefix + '_' + datetime.now().strftime('%Y-%m-%d@%H-%M-%S')
        dirname = basedirname
        counter = 0
        done = False
        while not done:
            try:
                os.mkdir(os.path.join(self._data_dir, dirname))
                done = True
            except FileExistsError:  # in case we are called twice within a second
                counter += 1
                dirname = basedirname + '_' + str(counter)
                done = False
        return os.path.join(self._data_dir, dirname)