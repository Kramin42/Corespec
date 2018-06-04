import asyncio
import serial_asyncio
import logging
from struct import pack, unpack

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DEFAULT_PORT = '/dev/ttyPS1'
DEFAULT_BAUD = 115200
CMD_SIZE = 4
DATA_SIZE = 4
PACKET_SIZE = CMD_SIZE + DATA_SIZE

AMP_COOLDOWN_TIME = 2 # minutes

handler = None
write = None

mcs_ready = False

amp_enabled = False

setpoint = 30.0
P = 0.5
I = 0.001

# average temperature readings so we dont spam too much
TEMP_AVERAGING = 10
temp_sum = 0
temp_count = 0

def handler_raw(cmd):
    global setpoint, P, I, amp_enabled, mcs_ready, temp_sum, temp_count
    #logger.debug(cmd)
    data = {'name': None, 'value': None}
    if cmd[0:CMD_SIZE]==b'$TMP':
        if not mcs_ready:
            mcs_ready = True
            set_parameters(setpoint=setpoint, P=P, I=I)  # set initial parameters
            asyncio.ensure_future(amp_on_delayed())
        temp_sum += unpack('>f', cmd[CMD_SIZE:PACKET_SIZE])[0]
        temp_count += 1
        if temp_count == TEMP_AVERAGING:
            data['name'] = 'temperature'
            data['value'] = temp_sum/TEMP_AVERAGING
            temp_sum = 0
            temp_count = 0
            logger.debug('temperature: %.3f' % data['value'])
    if cmd[0:CMD_SIZE]==b'$TSP': # setpoint
        data['name'] = 'setpoint'
        data['value'] = unpack('>f', cmd[CMD_SIZE:PACKET_SIZE])[0]
        logger.info('new setpoint: %.3f' % data['value'])
    if cmd[0:CMD_SIZE]==b'$TCP': # P
        data['name'] = 'P'
        data['value'] = unpack('>f', cmd[CMD_SIZE:PACKET_SIZE])[0]
        logger.info('new constant P: %.3f' % data['value'])
    if cmd[0:CMD_SIZE]==b'$TCI': # I
        data['name'] = 'I'
        data['value'] = unpack('>f', cmd[CMD_SIZE:PACKET_SIZE])[0]
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
    if handler is not None and data['name'] is not None:
        handler(data)

def get_parameters():
    return {
        'setpoint': setpoint,
        'P': P,
        'I': I,
        'amp_on': amp_enabled,
    }

async def amp_on_delayed():
    await asyncio.sleep(60*AMP_COOLDOWN_TIME)
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

def set_parameters(setpoint=None, P=None, I=None):
    if not mcs_ready:
        raise Exception('Temperature control not ready')
    logger.debug('setting initial parameters %.2f %.3f %.5f' % (setpoint, P, I))
    if setpoint is not None:
        cmd = b'$TSP' + pack('>f', setpoint)
        write(cmd)
    if P is not None:
        cmd = b'$TCP' + pack('>f', P)
        write(cmd)
    if I is not None:
        cmd = b'$TCI' + pack('>f', I)
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
