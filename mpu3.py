import sys, os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lsm9ds1_rjg import Driver, I2CTransport, SPITransport


class SimpleExample:
    """This example shows how to poll the sensor for new data.
    It queries the sensor to discover when the accelerometer/gyro
    has new data and then reads all the sensors."""
    def __init__(self):
        #self.driver = self._create_spi_driver()
        self.driver = self._create_i2c_driver()
        self.driver.configure()

    @staticmethod
    def _create_i2c_driver() -> Driver:
        return Driver(
            I2CTransport(1, I2CTransport.I2C_AG_ADDRESS),
            I2CTransport(1, I2CTransport.I2C_MAG_ADDRESS))

    @staticmethod
    def _create_spi_driver() -> Driver:
        return Driver(
            SPITransport(0, False),
            SPITransport(1, True))

    def main(self):
        try:
            count = 0
            while True:
                ag_data_ready = self.driver.read_ag_status().accelerometer_data_available
                if ag_data_ready:
                    self.read_ag()
                    self.read_magnetometer()
                    count += 1
                else:
                    time.sleep(0.1)
        finally:
            self.driver.close()

    def read_ag(self):
        temp, acc, gyro = self.driver.read_ag_data()
        print('Temp:{} Acc:{} Gryo:{}'.format(temp, acc, gyro), end = '')

    def read_magnetometer(self):
        mag = self.driver.read_magnetometer()
        print('Mag {}'.format(mag))


if __name__ == '__main__':
    SimpleExample().main()
