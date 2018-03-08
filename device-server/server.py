#!/usr/bin/env python3.6

import os
import logging
import tornado.web as web
from tornado.platform.asyncio import AsyncIOMainLoop
import asyncio
import websockets
import json
import yaml
import time
from base64 import b64encode, b64decode

import program

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

dir_path = os.path.dirname(os.path.realpath(__file__))

programs = {name: program.Program(name) for name in program.list_programs()}

#
# queries
#

async def list_programs():
    return programs.keys()

async def config_get(program_name, key):
    return programs[program_name].config_get(key)

async def data(program_name):
    data = programs[program_name].data
    return {'bytes': b64encode(data.tobytes()).decode(), 'dtype': str(data.dtype)}

#
# commands
#

async def set_parameters(ws, program_name, parameters):
    for key, val in parameters.items():
        programs[program_name].set_par(key, val)

async def run(ws, program_name):
    def progress_handler(progress, limit=0):
        # fire and forget
        asyncio.ensure_future(ws.send(json.dumps({
            'type': 'progress',
            'progress': int(progress),
            'limit': int(limit)
        })))
    await programs[program_name].run(progress_handler=progress_handler)

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
            await websocket.send(json.dumps({'type': 'error', 'message': repr(e)}))
            logger.exception(e)
    logger.debug('handled request in %s seconds' % (time.time() - t_i))

async def consumer_handler(websocket, path):
    async for message in websocket:
        await consumer(websocket, message)


if __name__=='__main__':
    logger.debug('launching device websocket server')
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(consumer_handler, '0.0.0.0', 9876))
    AsyncIOMainLoop().install()
    asyncio.get_event_loop().run_forever()