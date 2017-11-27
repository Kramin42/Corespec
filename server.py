#!/usr/bin/env python3.6

import logging
import asyncio
import websockets
import json
import yaml
import numpy as np

from programs import Program, list_programs

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEFAULT_PARAMETER_FILE = 'default_par.yaml'

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
    with open(DEFAULT_PARAMETER_FILE, 'r') as f:
        return yaml.load(f.read())


async def raw_data(program_name):
    return programs[program_name].data.tolist()


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
    await ws.send(json.dumps({'type': 'message', 'message': 'Program %s finished.' % name}))


async def set_parameters(ws, program_name, parameters):
    program = programs[program_name]
    for name, value in parameters.items():
        program.set_par(name, value)
    await ws.send(json.dumps({'type': 'message', 'message': '%s parameters set.' % program_name}))


#
# websocket server
#

async def consumer(websocket, message):
    data = json.loads(message)
    logger.debug(data)
    if data['type'] == 'query':
        try:
            result = await globals()[data['query']](**data['args'])
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
        except Exception as e:
            logger.exception(e)

async def consumer_handler(websocket, path):
    async for message in websocket:
        await consumer(websocket, message)

if __name__=='__main__':
    for name in list_programs():
        try:
            programs[name] = Program(name)
        except Exception as e:
            logger.exception(e)

    asyncio.get_event_loop().run_until_complete(
        websockets.serve(consumer_handler, '0.0.0.0', 8765))
    asyncio.get_event_loop().run_forever()
