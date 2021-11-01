# RPi PINOUTS
# MOSI -> GPIO10
# MISO -> GPIO9
# SCK  -> GPIO11
# CE1  -> GPIO7
# CE1  -> GPIO8

# get the GPIO Library and SPI Library
import spidev
import time

BAUDRATE_MAX    = 250000
BAUDRATE        = 10000

START           = 0xff
CMD_RESET       = 0x00
CMD_SET_DATA    = 0x01
CMD_GET_DATA    = 0x02

ADDR_AI_FIRST   = 0x00
ADDR_AI_LAST    = 0x01
ADDR_DI_FIRST   = 0x02
ADDR_DI_LAST    = 0x05
ADDR_DO_FIRST   = 0x00
ADDR_DO_LAST    = 0x0a

class ATMega328():

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ATMega328()
        return cls._instance

    def __init__(self):
        #Initialze the SPI 
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)
        self.spi.max_speed_hz = BAUDRATE_MAX

    def close(self):
        self.spi.close()

    def digitalWrite(self, addr, value):
        resp = self.spi.xfer([START, CMD_SET_DATA, addr, value, 0], BAUDRATE)
 
    def digitalRead(self, addr):
        resp = self.spi.xfer([START, CMD_GET_DATA, addr, 0, 0], BAUDRATE)
        return resp[3]

    def analogRead(self, addr):
        resp = self.spi.xfer([START, CMD_GET_DATA, addr, 0, 0], BAUDRATE)
        return resp[3]

    def get_input(self, addr):
        if addr >= ADDR_AI_FIRST and addr <= ADDR_AI_LAST:
            return self.analogRead(addr)
        elif addr >= ADDR_DI_FIRST and addr <= ADDR_DI_LAST:
            return self.digitalRead(addr)

    def set_output(self, addr, value):
        if addr >= ADDR_DO_FIRST and addr <= ADDR_DO_LAST:
            self.digitalWrite(addr, value)
