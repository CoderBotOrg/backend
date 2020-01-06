import lsm9ds1
import time

class AccelGyro:
    X_IND = 0
    Y_IND = 1
    Z_IND = 2

    PITCH_IND = 0
    ROLL_IND = 1
    YAW_IND = 2

    """This example shows how to poll the sensor for new data.
    It queries the sensor to discover when the accelerometer/gyro
    has new data and then reads all the sensors."""
    def __init__(self):
        self.driver = lsm9ds1.make_i2c(1)
        mc = lsm9ds1.MagCalibration(xmin=-0.3612, xmax=-0.17836000000000002,
                                    ymin=-0.08750000000000001, ymax=0.07826000000000001,
                                    heading_offset=95.3491645593403)
        self.driver.configure(mc)


    GYRO_THRESHOLD = 1.5

    def read_ag(self):
        temp, acc, gyro = self.driver.read_values()
        print("Temp: %.1f °f" % temp)
        print("Gyro Roll: %.4f, Pitch: %.4f, Yaw: %.4f" % (gyro[SimpleExample.ROLL_IND],
                                                           gyro[SimpleExample.PITCH_IND],
                                                           gyro[SimpleExample.YAW_IND]))
        print("X: %.4f, Y: %.4f, Z: %.4f" % (acc[SimpleExample.X_IND],
                                             acc[SimpleExample.Y_IND],
                                             acc[SimpleExample.Z_IND]))

    def read_magnetometer(self):
        hdg = self.driver.mag_heading()
        print("Heading: %.2f" % hdg)


    def get_gyro(self):
        temp, acc, gyro = self.driver.read_values()
        return (gyro[SimpleExample.ROLL_IND],
                gyro[SimpleExample.PITCH_IND],
                gyro[SimpleExample.YAW_IND])

    def get_acc(self):
        temp, acc, gyro = self.driver.read_values()
        return (gyro[SimpleExample.X_IND],
                gyro[SimpleExample.Y_IND],
                gyro[SimpleExample.Z_IND])

    def get_hdg(self):
        hdg = self.driver.mag_heading()

    def get_temp(self):
        temp, acc, gyro = self.driver.read_values()
        return temp
