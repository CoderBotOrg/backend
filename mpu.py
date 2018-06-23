import MPU6050
import time

class AccelGyro:
    GYRO_THRESHOLD = 1.5

    def __init__(self):
        self.ag = MPU6050.MPU6050(0x68)
        self.ag.set_gyro_range(MPU6050.MPU6050.GYRO_RANGE_250DEG)
        self.gyro_abs = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.t = time.time()

    def get_gyro_data(self):
        gyro_data = self.ag.get_gyro_data()
        for k in gyro_data.keys():
            if abs(gyro_data[k]) > self.GYRO_THRESHOLD:
                self.gyro_abs[k] += gyro_data[k] * (time.time() - self.t)

        self.t = time.time()
        return self.gyro_abs
