class CPUTemperature:
    def __init__(self):
        pass

    @property
    def temperature(self):
        return 50.0

class BoardInfo:
    model = 'Raspberry Pi 3 Model B'
    revision = 'a02082'
    released = 'Q1 2016'
    manufacturer = 'Sony UK'
    soc = 'BCM2837'
    pcb_revision = '1.2'
    memory = '1GB'
    storage = 'MicroSD'
    usb = '4'
    usb3 = '0'
    ethernet = '1'
    eth_speed = '100M'
    wifi = 'b/g/n'
    bluetooth = '4.1'

class PinFactory:
    board_info = BoardInfo

class Device: 
    pin_factory = PinFactory



