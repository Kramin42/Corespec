# program proxy via websocket

import numpy as np
from base64 import b64decode
import json
import yaml
import asyncio
import websocket
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEVICE_SERVER_URI = 'ws://localhost:9876'

class Program:
    def __init__(self, name: str):
        self.name = name
        self.ws_uri = DEVICE_SERVER_URI
        self.ws = websocket.create_connection(self.ws_uri)
        self.par = {}
        self._data = None

    def _ws_send(self, obj):
        sent = False
        for i in range(10):
            try:
                self.ws.send(json.dumps(obj))
            except ConnectionResetError as e:
                self.ws = websocket.create_connection(self.ws_uri)
            else:
                sent = True
                break
        if not sent:
            raise Exception('Could not connect to device')

    def _ws_recv(self):
        reply = json.loads(self.ws.recv())
        return reply

    def set_par(self, name: str, value):
        self.par[name] = value

    def load_par(self, filename: str):
        with open(filename, 'r') as f:
            new_par = yaml.load(f.read())
        for name, value in new_par.items():
            self.set_par(name, value)

    def save_par(self, filename: str):
        with open(filename, 'w') as f:
            f.write(yaml.dump(self.par, default_flow_style=False))

    def config_get(self, key):
        self._ws_send({
            'type': 'query',
            'query': 'config_get',
            'ref': 'x',
            'args': {
                'program_name': self.name,
                'key': key
            }
        })
        reply = self._ws_recv()
        if reply['type'] == 'error':
            raise Exception(reply['message'])
        return reply['result']

    def _run_sync(self, progress_handler=None):
        self._ws_send({
            'type': 'command',
            'command': 'set_parameters',
            'ref': 'x',
            'args': {
                'program_name': self.name,
                'parameters': self.par
            }
        })
        reply = self._ws_recv()
        if reply['type'] == 'error':
            raise Exception(reply['message'])
        if reply['type'] != 'finished':
            raise Exception('Unable to set parameters on device')
        self._ws_send({
            'type': 'command',
            'command': 'run',
            'ref': 'x',
            'args': {
                'program_name': self.name
            }
        })
        type = None
        while type != 'finished':
            reply = self._ws_recv()
            type = reply['type']
            if type == 'error':
                raise Exception(reply['message'])
            if type == 'progress':
                if progress_handler is not None:
                    progress_handler(reply['progress'], reply['limit'])

    async def run(self, progress_handler=None):
        await asyncio.get_event_loop().run_in_executor(None, lambda: self._run_sync(progress_handler=progress_handler))

    @property
    def data(self):
        self._ws_send({
            'type': 'query',
            'query': 'data',
            'ref': 'x',
            'args': {
                'program_name': self.name,
            }
        })
        reply = self._ws_recv()
        if reply['type'] == 'error':
            raise Exception(reply['message'])
        return np.fromstring(b64decode(reply['result']['bytes']), dtype=reply['result']['dtype'])
