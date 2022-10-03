import time

from hw import lsm9ds1

class SimpleExample:
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

    def main(self):
        try:
            count = 0
            while True:
                ag_data_ready = self.driver.read_ag_status().accelerometer_data_available
                if ag_data_ready:
                    self.read_ag()
                    print("")
                    #self.read_magnetometer()
                    count += 1
                time.sleep(0.05)
        finally:
            self.driver.close()

    def read_ag(self):
        temp, acc, gyro = self.driver.read_values()
        #print("Temp: %.1f °f" % temp, end='')
        #print("Gyro Roll: %.4f, Pitch: %.4f, Yaw: %.4f" % (gyro[SimpleExample.ROLL_IND],
        #                                                   gyro[SimpleExample.PITCH_IND],
        #                                                   gyro[SimpleExample.YAW_IND]), end='')
        print("X: %.4f, Y: %.4f, Z: %.4f" % (acc[SimpleExample.X_IND],
                                             acc[SimpleExample.Y_IND],
                                             acc[SimpleExample.Z_IND]), end='')

    def read_magnetometer(self):
        hdg = self.driver.mag_heading()
        print("headind: %f ", hdg, end='')
        mag = self.driver.read_magnetometer()
        print('Mag {}'.format(mag))


if __name__ == '__main__':
    SimpleExample().main()
