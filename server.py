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

from program import Program, list_programs

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEFAULT_PARAMETER_FILE = 'default_par.yaml'

dir_path = os.path.dirname(os.path.realpath(__file__))

programs = {}


#
# queries
#

async def program_metadata():
    return [{
        'name': p.name,
        'description': p.config_get('description'),
        'parameters': p.config_get('parameters')
    } for k,p in programs.items()]


async def default_parameters():
    with open(os.path.join(dir_path, DEFAULT_PARAMETER_FILE), 'r') as f:
        return yaml.load(f.read())


async def raw_data(program_name):
    return programs[program_name].data.tolist()


async def real_imag_data(program_name):
    data = programs[program_name].data
    par = programs[program_name].par
    # deinterleave
    data = data.astype(np.float32).view(np.complex64)
    # phase
    if 'phaseRx' in par:
        data = data*np.exp(1j*np.pi*par['phaseRx']/180)
    return {'real': data.real.tolist(), 'imag': data.imag.tolist(), 'unit': 'μV'}


async def cpmg_int_data(program_name):
    data = programs[program_name].data
    par = programs[program_name].par
    # deinterleave
    data = data.astype(np.float32).view(np.complex64)
    # phase
    if 'phaseRx' in par:
        data = data*np.exp(1j*np.pi*par['phaseRx']/180)

    # number of samples per echo
    samples = par['samples']
    echoes = par['loops']
    echo_time = (par['T180']+par['T2']+par['T3'])/1000000000.0

    x = np.linspace(0, echoes*echo_time, echoes)
    y = np.zeros(echoes, dtype=np.complex64)
    for i in range(echoes):
        y[i] = np.sum(data[i*samples:(i+1)*samples])
    return {
        'x': x.tolist(),
        'y_real': y.real.tolist(),
        'y_imag': y.imag.tolist(),
        'x_unit': 's'}


async def cpmg_echo_data(program_name):
    data = programs[program_name].data
    par = programs[program_name].par
    # deinterleave
    data = data.astype(np.float32).view(np.complex64)
    # phase
    if 'phaseRx' in par:
        data = data*np.exp(1j*np.pi*par['phaseRx']/180)

    samples = par['samples']
    echoes = par['loops']
    echo_time = (par['T180']+par['T2']+par['T3'])/1000000000.0
    x = np.linspace(0, echo_time, samples)
    y = np.zeros(samples, dtype=np.complex64)
    for i in range(len(data)):
        y[i%samples] += data[i]
    y /= echoes
    return {
        'x': x.tolist(),
        'y_real': y.real.tolist(),
        'y_imag': y.imag.tolist(),
        'x_unit': 's',
        'y_unit': 'μV'}


async def wobble_data(program_name):
    data = programs[program_name].data
    par = programs[program_name].par

    width = par['bandwidth']
    center = par['freqTx']
    samples = par['samples']

    y = data.astype(np.float32)
    y = np.mean(y.reshape(-1, samples), axis=1)
    x = np.linspace(center-width/2, center+width/2, len(y))
    return {
        'x': x.tolist(),
        'y': y.tolist(),
        'x_unit': 'MHz'}


async def noise_data(program_name):
    data = programs[program_name].data

    y = data.astype(np.float32).view(np.complex64)
    x = np.linspace(0, 0.5*len(y), len(y), endpoint=False)
    return {
        'x': x.tolist(),
        'y': y.real.tolist(),
        'rms': np.sqrt(np.mean(np.abs(y)**2)).item(),
        'y_unit': 'μV',
        'x_unit': 'μs'}


#
# commands
#

async def run(ws, program_name):
    program = programs[program_name]
    def progress_handler(progress):
        # fire and forget
        asyncio.ensure_future(ws.send(json.dumps({
            'type': 'progress',
            'finished': False,
            'progress': float(progress),
            'max': float(program.config_get('progress.limit')+1)})))
    await program.run(progress_handler=progress_handler)
    await ws.send(json.dumps({'type': 'progress', 'finished': True}))
    #await ws.send(json.dumps({'type': 'message', 'message': 'Program %s finished.' % name}))


async def set_parameters(ws, program_name, parameters):
    program = programs[program_name]
    for name, value in parameters.items():
        program.set_par(name, value)
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
    ('/(.*)', Handler, {'path': '/home/root/microspec-client'})
])

if __name__=='__main__':
    for name in list_programs():
        try:
            programs[name] = Program(name)
        except Exception as e:
            logger.exception(e)
    logger.debug('launching websocket server')
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(consumer_handler, '0.0.0.0', 8765))
    logger.debug('launching webserver')
    AsyncIOMainLoop().install()
    app.listen(80)
    asyncio.get_event_loop().run_forever()
