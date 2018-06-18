import os
import yaml
import shutil

dir_path = os.path.dirname(os.path.realpath(__file__))

CONFIG = {}
def load_global_config():
    global CONFIG
    with open(os.path.join(dir_path, 'config.yaml'), 'r') as f:
        CONFIG = yaml.load(f.read())

try:
    load_global_config()
except IOError:
    shutil.copyfile(os.path.join(dir_path, 'default_config.yaml'), os.path.join(dir_path, 'config.yaml'))
    load_global_config()
