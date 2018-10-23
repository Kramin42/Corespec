# Author: Cameron Dykstra
# Email: dykstra.cameron@gmail.com

import os
import yaml
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

DEFAULT_PAR_FILE = 'default_par.yaml'

dir_path = os.path.dirname(os.path.realpath(__file__))
workspaces_dir = os.path.join(dir_path, 'workspaces')

try:
    os.listdir(workspaces_dir)
except:
    os.makedirs(workspaces_dir)

if not os.listdir(workspaces_dir):
    os.makedirs(os.path.join(workspaces_dir, 'default'))


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

    def list_par_sets(self, exp_name):
        os.makedirs(os.path.join(self._par_dir, exp_name), exist_ok=True)
        return [s[:-5] for s in os.listdir(os.path.join(self._par_dir, exp_name)) if s.endswith('.yaml')] # [:-5] removes the '.yaml' part

    def load_par_set(self, exp_name, par_set_name):
        with open(os.path.join(self._par_dir, exp_name, par_set_name+'.yaml'), 'r') as f:
            return yaml.load(f.read())

    def save_par_set(self, exp_name, par_set_name, parameters):
        os.makedirs(os.path.join(self._par_dir, exp_name), exist_ok=True)
        with open(os.path.join(self._par_dir, exp_name, par_set_name+'.yaml'), 'w') as f:
            yaml.dump(parameters, f, default_flow_style=False)

    def save_default_pars(self, experiment_name, parameters, par_def):
        default_pars = self.load_default_pars()
        if experiment_name not in default_pars:
            default_pars[experiment_name] = {}
        if 'shared' not in default_pars:
            default_pars['shared'] = {}
        for name, value in parameters.items():
            if name in par_def:
                if 'shared' in par_def[name] and par_def[name]['shared']:
                    default_pars['shared'][name] = value
                else:
                    default_pars[experiment_name][name] = value
        with open(os.path.join(self._par_dir, DEFAULT_PAR_FILE), 'w') as f:
            yaml.dump(default_pars, f, default_flow_style=False)

    def load_default_pars(self):
        try:
            with open(os.path.join(self._par_dir, DEFAULT_PAR_FILE), 'r') as f:
                default_pars = yaml.load(f.read())
                if default_pars is not None:
                    return default_pars
        except Exception as e:
            logger.exception(e)
        return {}

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