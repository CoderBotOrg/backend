import unittest
import test.pigpio_mock
import hw.mpu
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

sh = logging.StreamHandler()
# add a rotating handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)

logger.addHandler(sh)

class MPUTestCase(unittest.TestCase):
    def setUp(self):
        self.mpu = mpu.AccelGyroMag()

    def test_gyro(self):
        gyro = self.mpu.get_gyro()
        self.assertTrue(gyro is not None)

    def test_acc(self):
        acc = self.mpu.get_acc()
        self.assertTrue(acc is not None)

    def test_mag(self):
        hdg = self.mpu.get_hdg()
        self.assertTrue(hdg is not None)

    def test_temp(self):
        temp = self.mpu.get_temp()
        self.assertTrue(temp is not None)

