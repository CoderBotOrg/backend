import lsm9ds1
import time

class AccelGyroMag:
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
        mc = lsm9ds1.MagCalibration(xmin=0.03234, xmax=0.25718,
                                    ymin=0.036120000000000006, ymax=0.19138000000000002,
                                    heading_offset=-130.29698965718163)
        self.driver.configure(mc)


    GYRO_THRESHOLD = 1.5

    def read_ag(self):
        temp, acc, gyro = self.driver.read_values()
        print("Temp: %.1f °f" % temp)
        print("Gyro Roll: %.4f, Pitch: %.4f, Yaw: %.4f" % (gyro[AccelGyroMag.ROLL_IND],
                                                           gyro[AccelGyroMag.PITCH_IND],
                                                           gyro[AccelGyroMag.YAW_IND]))
        print("X: %.4f, Y: %.4f, Z: %.4f" % (acc[AccelGyroMag.X_IND],
                                             acc[AccelGyroMag.Y_IND],
                                             acc[AccelGyroMag.Z_IND]))

    def read_magnetometer(self):
        hdg = self.driver.mag_heading()
        print("Heading: " + str(hdg))


    def get_gyro(self):
        temp, acc, gyro = self.driver.read_values()
        return (gyro[AccelGyroMag.ROLL_IND],
                gyro[AccelGyroMag.PITCH_IND],
                gyro[AccelGyroMag.YAW_IND])

    def get_acc(self):
        temp, acc, gyro = self.driver.read_values()
        return (acc[AccelGyroMag.X_IND],
                acc[AccelGyroMag.Y_IND],
                acc[AccelGyroMag.Z_IND])

    def get_hdg(self):
        hdg = self.driver.mag_heading()
        return hdg

    def get_temp(self):
        temp, acc, gyro = self.driver.read_values()
        return temp
