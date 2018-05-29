import asyncio
import serial_asyncio
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEFAULT_PORT = '/dev/ttyPS1'
DEFAULT_BAUD = 115200

handler = None
write = None

def amp_on():
    write(b'$AMPON##')

def amp_off():
    write(b'$AMPOFF#')

class TempControl(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        self.acc = b''
        logger.debug('port opened', transport)
        transport.serial.rts = False  # You can manipulate Serial object via transport
        global write
        write = transport.write
        #transport.write(b'Hello, World!\n')  # Write serial data via transport

    def data_received(self, data):
        logger.debug('data received:', repr(data))
        self.acc+=data
        while b'$' in self.acc:
            acc_split = self.acc.split(b'$')
            cmd = b'$'+acc_split[1][:7]
            logger.debug(cmd)
            self.acc = acc_split[1][7:]+acc_split[2:].join(b'$')
            pass

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
