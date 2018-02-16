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
import time

from experiment import list_experiments, load_experiment

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEFAULT_PARAMETER_FILE = 'default_par.yaml'

dir_path = os.path.dirname(os.path.realpath(__file__))

experiments = {}


#
# queries
#

async def experiment_metadata():
    return [exp.get_metadata() for k,exp in experiments.items()]


async def default_parameters():
    with open(os.path.join(dir_path, DEFAULT_PARAMETER_FILE), 'r') as f:
        return yaml.load(f.read())

async def export(experiment_name, export_name):
    return experiments[experiment_name].exports[export_name]()

async def plot(experiment_name, plot_name):
    return experiments[experiment_name].plots[plot_name]()

async def export_csv(experiment_name, export_name):
    data = experiments[experiment_name].exports[export_name]()
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
            else:
                if rownum < len(v):
                    done = False
                    row.append(str(v[rownum]))
                else:
                    row.append('')
        rownum += 1
    return csv

#
# commands
#

async def run(ws, experiment_name):
    experiment = experiments[experiment_name]
    def progress_handler(progress, limit=0):
        # fire and forget
        asyncio.ensure_future(ws.send(json.dumps({
            'type': 'progress',
            'finished': False,
            'progress': progress,
            'max': limit
        })))
    await experiment.run(progress_handler=progress_handler)
    await ws.send(json.dumps({'type': 'progress', 'finished': True}))
    await ws.send(json.dumps({'type': 'message', 'message': '%s experiment finished.' % experiment_name}))


async def set_parameters(ws, experiment_name, parameters):
    experiments[experiment_name].set_parameters(parameters)
    #await ws.send(json.dumps({'type': 'message', 'message': '%s parameters set.' % program_name}))


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
            await websocket.send(json.dumps({'type': 'error', 'message': str(e)}))
            logger.exception(e)
    logger.debug('handled request in %s seconds' % (time.time() - t_i))

async def consumer_handler(websocket, path):
    async for message in websocket:
        await consumer(websocket, message)

# web server
class Handler(web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path:
            url_path = 'client.html'
        return url_path

app = web.Application([
    ('/(.*)', Handler, {'path': '../microspec-client'})
])

if __name__=='__main__':
    for name in list_experiments():
        try:
            experiments[name] = load_experiment(name)
        except Exception as e:
            logger.exception(e)
    logger.debug('launching websocket server')
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(consumer_handler, '0.0.0.0', 8765))
    logger.debug('launching webserver')
    AsyncIOMainLoop().install()
    app.listen(80)
    asyncio.get_event_loop().run_forever()
