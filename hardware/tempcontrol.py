import os
import asyncio
import serial_asyncio
import logging
from time import time
from struct import pack, unpack
from libraries.gaspvt import record_pressure, record_temperature

import yaml

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEFAULT_PORT = '/dev/ttyPS1'
DEFAULT_BAUD = 115200
CMD_SIZE = 4
DATA_SIZE = 4
PACKET_SIZE = CMD_SIZE + DATA_SIZE

PAR_FILE = 'tempcontrol.yaml'

AMP_COOLDOWN_TIME = 20 # seconds

dir_path = os.path.dirname(os.path.realpath(__file__))

handler = None
write = None

mcs_ready = False

amp_enabled = False

parameters = {
    'setpoint': 30.0,
    'P': 0.5,
    'I': 0.001,
    'PT_Cal_A': 7.5,
    'PT_Cal_B': -50,
    'PP_Cal_A': 1.25,
    'PP_Cal_B': -5
}

try:
    with open(os.path.join(dir_path, PAR_FILE), 'r') as f:
        parameters.update(yaml.load(f.read()))
except Exception as e:
    logger.exception(e)

# average temperature readings so we dont spam too much
TEMP_AVERAGING = 10
TEMP_PERIOD = 1 # seconds
temp_sum = 0
temp_count = 0
temp_time = 0

start_time = time()

ERRTMPR_reported = False

def handler_raw(cmd):
    global parameters, amp_enabled, mcs_ready, temp_sum, temp_count, temp_time, start_time, ERRTMPR_reported
    #logger.debug(cmd)
    data = {'name': None, 'value': None}
    if (cmd[0:CMD_SIZE]==b'$TMP' or cmd[0:CMD_SIZE]==b'$ERR') and not mcs_ready:
        mcs_ready = True
        set_parameters(**parameters)  # set initial parameters
        asyncio.ensure_future(amp_on_delayed())
    if cmd[0:CMD_SIZE]==b'$TMP':
        ERRTMPR_reported = False
        temp_sum += unpack('>f', cmd[CMD_SIZE:PACKET_SIZE])[0]
        temp_count += 1
        temp_time += TEMP_PERIOD
        if temp_count == TEMP_AVERAGING:
            data['name'] = 'temperature'
            data['value'] = temp_sum/TEMP_AVERAGING
            data['time'] = temp_time
            temp_sum = 0
            temp_count = 0
            logger.debug('temperature: %.3f' % data['value'])
    if cmd[0:CMD_SIZE] == b'$IIA':
        data['name'] = 'pipe-pressure'
        current = unpack('>f', cmd[CMD_SIZE:PACKET_SIZE])[0]
        # logger.debug('current A: %f' % current)
        pressure = (parameters['PP_Cal_A']*current + parameters['PP_Cal_B'])  # in MPa
        record_pressure(pressure)
        data['value'] = pressure*1000000  # MPa -> Pa
        data['time'] = int(time() - start_time)
    if cmd[0:CMD_SIZE] == b'$IIB':
        data['name'] = 'pipe-temperature'
        current = unpack('>f', cmd[CMD_SIZE:PACKET_SIZE])[0]
        # logger.debug('current B: %f' % current)
        temperature = parameters['PT_Cal_A']*current + parameters['PT_Cal_B']  # in degrees Centigrade
        record_temperature(temperature + 273.15)  # record in Kelvin
        data['value'] = temperature
        data['time'] = int(time() - start_time)
    if cmd[0:CMD_SIZE] == b'$IIC':
        current = unpack('>f', cmd[CMD_SIZE:PACKET_SIZE])[0]
        # logger.debug('current C: %f' % current)
    if cmd[0:CMD_SIZE] == b'$IID':
        current = unpack('>f', cmd[CMD_SIZE:PACKET_SIZE])[0]
        # logger.debug('current D: %f' % current)
    if cmd[0:CMD_SIZE]==b'$TSP': # setpoint
        data['name'] = 'setpoint'
        data['value'] = unpack('>f', cmd[CMD_SIZE:PACKET_SIZE])[0]
        setpoint = data['value']
        logger.info('new setpoint: %.3f' % data['value'])
    if cmd[0:CMD_SIZE]==b'$TCP': # P
        data['name'] = 'P'
        data['value'] = unpack('>f', cmd[CMD_SIZE:PACKET_SIZE])[0]
        P = data['value']
        logger.info('new constant P: %.3f' % data['value'])
    if cmd[0:CMD_SIZE]==b'$TCI': # I
        data['name'] = 'I'
        data['value'] = unpack('>f', cmd[CMD_SIZE:PACKET_SIZE])[0]
        I = data['value']
        logger.info('new constant I: %.5f' % data['value'])
    if cmd[0:CMD_SIZE]==b'$AMP':
        if cmd[CMD_SIZE:PACKET_SIZE]==b'ON##':
            amp_enabled = True
            data['name'] = 'amp-power'
            data['value'] = True
            logger.info('amp power on')
        if cmd[CMD_SIZE:PACKET_SIZE]==b'OFF#':
            amp_enabled = False
            data['name'] = 'amp-power'
            data['value'] = False
            logger.info('amp power off')
    if cmd[0:CMD_SIZE] == b'$ERR':
        if cmd[CMD_SIZE:PACKET_SIZE]==b'TMPR' and not ERRTMPR_reported:
            ERRTMPR_reported = True
            data['name'] = 'error'
            data['value'] = 'Invalid temperature reading, check cable'
    if handler is not None and data['name'] is not None:
        handler(data)

def get_parameters():
    global parameters
    return parameters

async def amp_on_delayed():
    await asyncio.sleep(AMP_COOLDOWN_TIME)
    if not amp_enabled:
        asyncio.ensure_future(amp_on_delayed())  # schedule retry in case it fails for hardware reasons
        amp_on()

def amp_on():
    if not mcs_ready:
        raise Exception('Temperature control not ready')
    write(b'$AMPON##')

def amp_off():
    print('bye')
    if not mcs_ready:
        raise Exception('Temperature control not ready')
    write(b'$AMPOFF#')

def set_parameters(**pars):
    global parameters
    for key in pars: # ensure they are floats
        pars[key] = float(pars[key])
    parameters.update(pars)
    with open(os.path.join(dir_path, PAR_FILE), 'w') as f:
        yaml.dump(parameters, f, default_flow_style=False)
    if not mcs_ready:
        raise Exception('Temperature control not ready')
    logger.debug('setting tempcontrol parameters %.2f %.3f %.5f' % (pars['setpoint'], pars['P'], pars['I']))
    if pars['setpoint'] is not None:
        cmd = b'$TSP' + pack('>f', pars['setpoint'])
        write(cmd)
    if pars['P'] is not None:
        cmd = b'$TCP' + pack('>f', pars['P'])
        write(cmd)
    if pars['I'] is not None:
        cmd = b'$TCI' + pack('>f', pars['I'])
        write(cmd)

class TempControl(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        self.acc = b''
        logger.debug('port opened')
        transport.serial.rts = False  # You can manipulate Serial object via transport
        global write
        write = transport.write

    def data_received(self, data):
        #logger.debug('data received:'+repr(data))
        self.acc+=data
        while True:
            loc = self.acc.find(b'$')
            if loc < 0:
                break
            self.acc = self.acc[loc:]
            if len(self.acc) < PACKET_SIZE:
                break
            cmd = self.acc[:PACKET_SIZE]
            handler_raw(cmd)
            self.acc = self.acc[PACKET_SIZE:]

    def connection_lost(self, exc):
        logger.debug('port closed')
        self.transport.loop.stop()

    def pause_writing(self):
        logger.debug('pause writing')
        logger.debug(self.transport.get_write_buffer_size())

    def resume_writing(self):
        logger.debug(self.transport.get_write_buffer_size())
        logger.debug('resume writing')

def init(event_loop, response_handler=None):
    global handler
    logger.debug('starting temperature control')
    coro = serial_asyncio.create_serial_connection(event_loop, TempControl, DEFAULT_PORT, baudrate=DEFAULT_BAUD)
    asyncio.ensure_future(coro)
    handler = response_handler
