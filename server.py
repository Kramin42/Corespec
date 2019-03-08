#!/usr/bin/env python3.6

import os
import logging
import tornado.web as web
from tornado.platform.asyncio import AsyncIOMainLoop
import asyncio
import websockets
import json
import yaml
import numpy as np
import scipy.io as sio
from base64 import b64encode, b64decode
import time
import tempfile

from experiment import list_experiments, load_experiment
from workspace import list_workspaces, Workspace
from hardware import tempcontrol
from util import *
from config import CONFIG

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

DEFAULT_PARAMETER_FILE = 'default_par.yaml'
DEFAULT_LANGUAGE_FILE = 'lang.yaml'

dir_path = os.path.dirname(os.path.realpath(__file__))

experiments = {}
workspace = None

#
# queries
#

async def load_language(lang_name):
    with open(os.path.join(dir_path, DEFAULT_LANGUAGE_FILE), 'r') as f:
        langs = yaml.load(f.read())
    return langs[lang_name]

async def experiment_metadata():
    return [exp.get_metadata() for k,exp in experiments.items()]

async def workspace_metadata():
    return list_workspaces()

async def default_parameters():
    return workspace.load_default_pars()

async def load_parameter_set(experiment_name, par_set_name):
    return workspace.load_par_set(experiment_name, par_set_name)

async def list_parameter_sets(experiment_name):
    return workspace.list_par_sets(experiment_name)

async def export(experiment_name, export_name):
    return encode_data(experiments[experiment_name].exports[export_name]())

async def plot(experiment_name, plot_name):
    return encode_data(experiments[experiment_name].get_plot(plot_name))

async def export_csv(experiment_name, export_name):
    # TODO: fix to convert nparray
    data = experiments[experiment_name].get_export(export_name)
    csv = ''
    row = data.keys()
    rownum = 0
    done = False
    while not done:
        csv += ','.join(row) + '\n'
        done = True
        row = []
        for k, v in data.items():
            if type(v) is str:
                if rownum==0:
                    row.append(v)
                else:
                    row.append('')
            elif type(v) is float or type(v) is int:
                if rownum==0:
                    row.append(str(v))
                else:
                    row.append('')
            else:
                if rownum < len(v):
                    done = False
                    row.append(str(v[rownum]))
                else:
                    row.append('')
        rownum += 1
    return csv

async def export_matlab(experiment_name, export_name):
    # TODO: fix to convert nparray
    data = experiments[experiment_name].get_export(export_name)
    f = tempfile.NamedTemporaryFile(delete=False)
    logger.debug('creating temp file %s' % f.name)
    try:
        sio.savemat(f.name, data, appendmat=False)
        buf = f.read()
        return b64encode(buf).decode('utf-8')
    finally:
        f.close()
        os.remove(f.name)

async def get_tempcontrol():
    return tempcontrol.get_parameters()

#
# commands
#

async def run(ws, experiment_name):
    experiment = experiments[experiment_name]
    def progress_handler(progress, limit=0):
        # fire and forget
        asyncio.ensure_future(ws.send(json.dumps({
            'type': 'progress',
            'experiment': experiment_name,
            'finished': False,
            'progress': int(progress),
            'max': int(limit)
        })))
    def message_handler(message, type='message'):
        asyncio.ensure_future(ws.send(json.dumps({'type': type, 'message': message})))
    await experiment.run(progress_handler=progress_handler, message_handler=message_handler)
    #if experiment.name in ['FID', 'CPMG']:
    #    experiment.save(workspace.new_data_dir(experiment.name))
    await ws.send(json.dumps({'type': 'progress', 'experiment': experiment_name, 'finished': True}))
    await ws.send(json.dumps({'type': 'message', 'message': '%s experiment finished.' % experiment_name}))

async def abort(ws, experiment_name):
    experiments[experiment_name].abort()

async def set_parameters(ws, experiment_name, parameters):
    experiments[experiment_name].set_parameters(parameters)
    # save parameters to workspace default par file
    workspace.save_default_pars(experiment_name, parameters, experiments[experiment_name].par_def)
    #await ws.send(json.dumps({'type': 'message', 'message': '%s parameters set.' % program_name}))

async def save_parameter_set(ws, experiment_name, par_set_name, parameters):
    workspace.save_par_set(experiment_name, par_set_name, parameters)
    await ws.send(json.dumps({'type': 'message', 'message': 'Saved parameter set %s.' % par_set_name}))

async def set_workspace(ws, workspace_name):
    global workspace
    workspace = Workspace(workspace_name)
    await ws.send(json.dumps({'type': 'message', 'message': 'Switched to workspace %s.' % workspace.name}))

async def set_amp(ws, on):
    if on:
        tempcontrol.amp_on()
    else:
        tempcontrol.amp_off()

async def set_tempcontrol(ws, **parameters):
    tempcontrol.set_parameters(**parameters)

#
# temperature control message handler
#

def tempcontrol_handler(data):
    broadcast(json.dumps({
        'type': 'tempcontrol',
        'data': data
    }))

#
# websocket server
#

async def consumer(websocket, message):
    data = json.loads(message)
    logger.debug(data)
    t_i = time.time()
    if data['type'] == 'query':
        try:
            result = await globals()[data['query']](**data['args'])
            logger.debug('generated result in %s seconds' % (time.time() - t_i))
            await websocket.send(json.dumps({
                'type': 'result',
                'ref': data['ref'],
                'result': result
            }))
        except Exception as e:
            await websocket.send(json.dumps({'type': 'error', 'ref': data['ref'], 'message': str(e), 'silent': True}))
            logger.exception(e)
    elif data['type'] == 'command':
        try:
            await globals()[data['command']](websocket, **data['args'])
            logger.debug('executed command in %s seconds' % (time.time() - t_i))
            await websocket.send(json.dumps({
                'type': 'finished',
                'ref': data['ref'],
            }))
        except Exception as e:
            await websocket.send(json.dumps({'type': 'error', 'ref': data['ref'], 'message': str(e), 'silent': False}))
            logger.exception(e)
    logger.debug('handled request in %s seconds' % (time.time() - t_i))

connected = set()
async def consumer_handler(websocket, path):
    connected.add(websocket)
    try:
        async for message in websocket:
            asyncio.ensure_future(consumer(websocket, message))
    finally:
        connected.remove(websocket)

def broadcast(msg):
    for ws in connected:
        asyncio.ensure_future(ws.send(msg))

# web server
class Handler(web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path:
            url_path = 'app.html'
        if url_path == 'flowmeter':
            url_path = 'flowmeter.html'
        return url_path

from admin import AdminHandler

app = web.Application([
    ('/admin', AdminHandler),
    ('/(.*)', Handler, {'path': os.path.join(dir_path, 'client')})
])

if __name__=='__main__':
    for name in list_experiments():
        try:
            experiments[name] = load_experiment(name)
        except Exception as e:
            logger.exception(e)
    for name in list_workspaces():
        if name == 'default':
            workspace = Workspace(name)
    logger.debug('launching websocket server')
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(consumer_handler, '0.0.0.0', 8765))
    logger.debug('launching webserver')
    AsyncIOMainLoop().install()
    app.listen(CONFIG['port'])
    loop = asyncio.get_event_loop()
    tempcontrol.init(loop, tempcontrol_handler)
    loop.run_forever()
    loop.close()
