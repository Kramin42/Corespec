import asyncio
import serial_asyncio
import logging
from struct import pack, unpack

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEFAULT_PORT = '/dev/ttyPS1'
DEFAULT_BAUD = 115200
CMD_SIZE = 4
DATA_SIZE = 4
PACKET_SIZE = CMD_SIZE + DATA_SIZE

handler = None
write = None

def handler_raw(cmd):
    logger.debug(cmd)
    if cmd[0:CMD_SIZE]==b'$TMP':
        temp = unpack('>f', cmd[CMD_SIZE:PACKET_SIZE])[0]
        logger.info('temperature: %.3f' % temp)
    if cmd[0:CMD_SIZE]==b'$AMP':
        if cmd[CMD_SIZE:PACKET_SIZE]==b'ON##':
            logger.debug('amp power on')
        if cmd[CMD_SIZE:PACKET_SIZE]==b'OFF#':
            logger.debug('amp power off')

def amp_on():
    write(b'$AMPON##')

def amp_off():
    write(b'$AMPOFF#')

class TempControl(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        self.acc = b''
        logger.debug('port opened')
        transport.serial.rts = False  # You can manipulate Serial object via transport
        global write
        write = transport.write
        #transport.write(b'Hello, World!\n')  # Write serial data via transport

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
    coro = serial_asyncio.create_serial_connection(event_loop, TempControl, DEFAULT_PORT, baudrate=DEFAULT_BAUD)
    asyncio.ensure_future(coro)
    handler = response_handler
