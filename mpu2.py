import time

from lsm9ds1 import lsm9ds1


class SimpleExample:
    X_IND = 1
    Y_IND = 2
    Z_IND = 0

    PITCH_IND = 1
    ROLL_IND = 0
    YAW_IND = 2

    """This example shows how to poll the sensor for new data.
    It queries the sensor to discover when the accelerometer/gyro
    has new data and then reads all the sensors."""
    def __init__(self):
        self.driver = lsm9ds1.make_i2c(0)
        mc = lsm9ds1.MagCalibration(xmin=-0.3612, xmax=-0.17836000000000002,
                                    ymin=-0.08750000000000001, ymax=0.07826000000000001,
                                    heading_offset=95.3491645593403)
        self.driver.configure(mc)

    def main(self):
        try:
            count = 0
            while True:
                ag_data_ready = self.driver.read_ag_status().accelerometer_data_available
                if ag_data_ready:
                    self.read_ag()
                    self.read_magnetometer()
                    count += 1
                time.sleep(0.05)
        finally:
            self.driver.close()

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


if __name__ == '__main__':
    SimpleExample().main()
