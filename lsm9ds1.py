import os
import time
import math
import json
import spidev
import threading

from smbus2 import SMBusWrapper

MAX_INVALID_MAG = 99.0

#
# Hardware Constants
#
# from LSM9DS1_Datasheet.pdf
class Register:
    """Register constants"""
    WHO_AM_I = 0x0F
    CTRL_REG1_G = 0x10
    CTRL_REG2_G = 0x11
    CTRL_REG3_G = 0x12
    OUT_TEMP_L = 0x15
    STATUS_REG = 0x17
    OUT_X_G = 0x18
    CTRL_REG4 = 0x1E
    CTRL_REG5_XL = 0x1F
    CTRL_REG6_XL = 0x20
    CTRL_REG7_XL = 0x21
    CTRL_REG8 = 0x22
    CTRL_REG9 = 0x23
    CTRL_REG10 = 0x24
    OUT_X_XL = 0x28
    REFERENCE_G = 0x0B
    INT1_CTRL = 0x0C
    INT2_CTRL = 0x0D
    WHO_AM_I_M = 0x0F
    CTRL_REG1_M = 0x20
    CTRL_REG2_M = 0x21
    CTRL_REG3_M = 0x22
    CTRL_REG4_M = 0x23
    CTRL_REG5_M = 0x24
    STATUS_REG_M = 0x27
    OUT_X_L_M = 0x28


class MagCalibration:
    def __init__(self, xmin=MAX_INVALID_MAG, xmax=-MAX_INVALID_MAG, ymin=MAX_INVALID_MAG, ymax=-MAX_INVALID_MAG,
                 heading_offset=0.0):
        self.xmax = xmax
        self.xmin = xmin
        self.ymax = ymax
        self.ymin = ymin
        self.heading_offset = heading_offset

    def to_json(self):
        obj = self.to_dict()
        return json.dumps(obj)

    def to_dict(self):
        obj = {"xmin": self.xmin, "xmax": self.xmax, "ymin": self.ymin, "ymax": self.ymax,
               "heading_offset": self.heading_offset}
        return obj

    @staticmethod
    def from_dict(obj):
        return MagCalibration(xmin=obj['xmin'], xmax=obj['xmax'], ymin=obj['ymin'], ymax=obj['ymax'],
                              heading_offset=obj['heading_offset'])


#
# Status Classes
#
class AGStatus:
    def __init__(self, status):
        self.status = status

    @property
    def accelerometer_interrupt(self):
        return (self.status & 0x40) != 0

    @property
    def gyroscope_interrupt(self):
        return (self.status & 0x20) != 0

    @property
    def inactivity_interrupt(self):
        return (self.status & 0x10) != 0

    @property
    def boot_status(self):
        return (self.status & 0x08) != 0

    @property
    def temperature_data_available(self):
        return (self.status & 0x04) != 0

    @property
    def gyroscope_data_available(self):
        return (self.status & 0x02) != 0

    @property
    def accelerometer_data_available(self):
        return (self.status & 0x01) != 0


class MagnetometerStatus:
    def __init__(self, status):
        self.status = status

    @property
    def overrun(self):
        """data overrun on all axes"""
        return (self.status & 0x80) != 0

    @property
    def z_overrun(self):
        """Z axis data overrun"""
        return (self.status & 0x40) != 0

    @property
    def y_overrun(self):
        """Y axis data overrun"""
        return (self.status & 0x20) != 0

    @property
    def x_overrun(self):
        """X axis data overrun"""
        return (self.status & 0x10) != 0

    @property
    def data_available(self):
        """There's new data available for all axes."""
        return (self.status & 0x08) != 0

    @property
    def z_axis_data_available(self):
        return (self.status & 0x04) != 0

    @property
    def y_axis_data_available(self):
        return (self.status & 0x02) != 0

    @property
    def x_axis_data_available(self):
        return (self.status & 0x01) != 0

class I2CTransport():
    I2C_AG_ADDRESS = 0x6B
    I2C_MAG_ADDRESS = 0x1E

    def __init__(self, port, i2c_address, data_ready_pin=None):
        super().__init__()
        self.port = port
        self.i2c_device = i2c_address
        self.data_ready_interrupt = None

    def write_byte(self, address, value):
        with SMBusWrapper(self.port) as bus:
            bus.write_byte_data(self.i2c_device, address, value)

    def read_byte(self, address):
        with SMBusWrapper(self.port) as bus:
            bus.write_byte(self.i2c_device, address)
            return bus.read_byte(self.i2c_device)

    def read_bytes(self, address, length):
        with SMBusWrapper(self.port) as bus:
            bus.write_byte(self.i2c_device, address)
            result = bus.read_i2c_block_data(self.i2c_device, address, length)
            return result

#
# Main Interface: lsm9ds1
#
def make_i2c(i2cbus_no):
    return lsm9ds1(
        I2CTransport(i2cbus_no, I2CTransport.I2C_AG_ADDRESS),
        I2CTransport(i2cbus_no, I2CTransport.I2C_MAG_ADDRESS))


class lsm9ds1:
    AG_ID = 0b01101000
    MAG_ID = 0b00111101

    # from LSM9DS1_Datasheet.pdf
    ACC_SENSOR_SCALE = 0.061 / 1000.0
    GAUSS_SENSOR_SCALE = 0.14 / 1000.0
    DPS_SENSOR_SCALE = 8.75 / 1000.0
    TEMP_SENSOR_SCALE = 59.5 / 1000.0
    TEMPC_0 = 25
    YMAG_IND = 1
    XMAG_IND = 0

    def __init__(self, ag_protocol, magnetometer_protocol, high_priority=False):
        self.ag = ag_protocol
        self.mag = magnetometer_protocol
        self.mag_calibration = None
        # Needs to be a high priority process or it'll drop samples
        # when other processes are under heavy load.
        if high_priority:
            priority = os.sched_get_priority_max(os.SCHED_FIFO)
            param = os.sched_param(priority)
            os.sched_setscheduler(0, os.SCHED_FIFO, param)

    def set_mag_calibration(self, mag_calibration):
        self.mag_calibration = mag_calibration

    def configure(self, mag_calibration=None):
        """Resets the device and configures it. Optionally pass in the mag calibration info"""

        self.set_mag_calibration(mag_calibration)

        ###################################################
        #   - Bit 0 - SW_RESET - software reset for accelerometer and gyro - default 0
        #   - Bit 2 - IF_ADD_INC - automatic register increment for multibyte access - default 1
        #   - Bit 6 - BDU - Block data update . Ensures high and low bytes come from
        #             the same sample. Not necessary if waiting for data ready - default 0
        self.ag.write_byte(Register.CTRL_REG8, 0x05)
        # 0x08 - reboot magnetometer, +/- 4 Gauss full scale - fixes occasional magnetometer hang
        # 0x04 - soft reset magnetometer, +/- 4 Gauss full scale
        self.mag.write_byte(Register.CTRL_REG2_M, 0x08)
        time.sleep(0.01)    # Wait for reset
        ###################################################
        # Confirm that we're connected to the device
        if self.ag.read_byte(Register.WHO_AM_I) != lsm9ds1.AG_ID:
            raise RuntimeError('Could not find LSM9DS1 Acceleromter/Gyro. Check wiring and port numbers.')
        if self.mag.read_byte(Register.WHO_AM_I_M) != lsm9ds1.MAG_ID:
            raise RuntimeError('Could not find LSM9DS1 Magnetometer. Check wiring and port numbers.')
        ###################################################
        # Set up output data rate for Accelerometer and Gyro if using both
        # Use CTRL_REG2_G and CTRL_REG3_G to control the optional additional filters
        # 0x6A - 500 dps, 119 Hz ODR, 38Hz cut off (31 Hz Cut off if HP filter is enabled)
        # 0x8A - 500 dps, 238 Hz ODR, 76Hz cut off (63 Hz Cut off if HP filter is enabled)
        # 0xAA - 500 dps, 476 Hz ODR, 100Hz cut off (57 Hz Cut off if HP filter is enabled)
        # 0x00 - disabled
        self.ag.write_byte(Register.CTRL_REG1_G, 0x8A)
        # 0x03 - Enable LPF2 - Frequency set by REG1 (2nd Low Pass Filter)
        # self.ag.write_byte(Register.CTRL_REG2_G, 0x03)
        # 0x45   - Enable High Pass Filter at (0.2 Hz @ 119 ODR) or (0.5 Hz @ 238 ODR)
        # self.ag.write_byte(Register.CTRL_REG3_G, 0x45)
        ###################################################
        # Set up Accelerometer
        # 0xC0 - Set to +- 2G, 119 Hz ODR, 50 Hz BW (Frequency is ignored if Gryo is enabled)
        # 0x87 - Set to +- 2G, 238 Hz ODR, 50 Hz BW (Frequency is ignored if Gryo is enabled)
        self.ag.write_byte(Register.CTRL_REG6_XL, 0x87)
        # 0x01 INT1_A/G pin set by accelerometer data ready
        self.ag.write_byte(Register.INT1_CTRL, 0x01)
        ###################################################
        # Set up magnetometer
        # MSB enables temperature compensation
        # 0x98 - 40 Hz ODR, Enable Temp Comp
        # 0x9C - 80 Hz ODR, Enable Temp Comp
        # 0x18 - 40 Hz ODR, Disable Temp Comp
        # 0x1C - 80 Hz ODR, Enable Temp Comp
        # 0xE2 - 155 Hz ODR, Enable Temp Comp, x and y ultra high performance
        # 0xC2 - 300 Hz ODR, Enable Temp Comp, x and y high performance
        # 0xA2 - 560 Hz ODR, Enable Temp Comp, x and y medium performance
        # 0x82 - 1000 Hz ODR, Enable Temp Comp, x and y low performance
        self.mag.write_byte(Register.CTRL_REG1_M, 0xC2)
        # 0x00 - Magnetometer continuous operation - I2C enabled
        # 0x80 - Magnetometer continuous operation - I2C disabled
        self.mag.write_byte(Register.CTRL_REG3_M, 0x00)
        # 0x08 - z axi high performance mode - doesn't seem to do anything
        self.mag.write_byte(Register.CTRL_REG4_M, 0x08)
        # Enable BDU (block data update) to ensure high and low bytes come from the same sample
        self.mag.write_byte(Register.CTRL_REG5_M, 0x40)

    def close(self):
        """Closes the I2C/SPI connection. This must be called on shutdown."""
        self.ag.close()
        self.mag.close()

    #
    # Simplified scaled interface
    #
    def mag_heading(self):
        """Returns the heading in 360°"""
        values = self.mag_values()
        y = values[lsm9ds1.YMAG_IND]
        x = values[lsm9ds1.XMAG_IND]
        if self.mag_calibration is not None:
            mc = self.mag_calibration
            # scale these samples between -1:1
            if mc.xmax != mc.xmin:
                x = ((x - mc.xmin) / (mc.xmax - mc.xmin)) * 2 - 1
            if mc.ymax != mc.ymin:
                y = ((y - mc.ymin) / (mc.ymax - mc.ymin)) * 2 - 1
        heading = math.atan2(y, x)
        heading = (heading / (2 * math.pi)) * 360.0
        if self.mag_calibration is not None:
            heading = (heading + self.mag_calibration.heading_offset) % 360.0
        return heading

    def read_values(self):
        """Returns scaled values of temp, accel, gyro"""
        temp, acc, gyro = self.read_ag_data()
        tempc = lsm9ds1.TEMPC_0 + temp * lsm9ds1.TEMP_SENSOR_SCALE
        tempf = (tempc * 9/5) + 32
        acc = [c * lsm9ds1.ACC_SENSOR_SCALE for c in acc]
        gyro = [g * lsm9ds1.DPS_SENSOR_SCALE for g in gyro]
        return tempf, acc, gyro

    #
    # Raw interface
    #
    def ag_data_ready(self, timeout_millis):
        return self.ag.data_ready(timeout_millis)

    def read_ag_status(self):
        """Returns the status byte for the accelerometer and gyroscope."""
        data = self.ag.read_byte(Register.STATUS_REG)
        return AGStatus(data)

    def read_ag_data(self):
        """Returns the current temperature, acceleration and angular velocity
        values in one go. This is faster than fetching them independently.
        These values can be invalid unless they're read when the data is ready."""
        data = self.ag.read_bytes(Register.OUT_TEMP_L, 14)
        temp = lsm9ds1.to_int16(data[0:2])
        gyro = lsm9ds1.to_vector_left_to_right_hand_rule(data[2:8])
        acc = lsm9ds1.to_vector_left_to_right_hand_rule(data[8:14])
        return temp, acc, gyro

    def read_temperature(self):
        """Reads the temperature. See also read_ag_data()"""
        data = self.ag.read_bytes(Register.OUT_TEMP_L, 2)
        return lsm9ds1.to_int16(data)

    def read_acceleration(self):
        """Reads the accelerations. See also read_ag_data()"""
        data = self.ag.read_bytes(Register.OUT_X_XL, 6)
        return lsm9ds1.to_vector_left_to_right_hand_rule(data)

    def read_gyroscope(self):
        """Reads the angular velocities. See also read_ag_data()"""
        data = self.ag.read_bytes(Register.OUT_X_G, 6)
        return lsm9ds1.to_vector_left_to_right_hand_rule(data)

    def magnetometer_data_ready(self, timout_millis: int) -> bool:
        return self.mag.data_ready(timout_millis)

    def read_magnetometer_status(self):
        """Returns the status byte for the magnetometer"""
        data = self.mag.read_byte(Register.STATUS_REG_M)
        return MagnetometerStatus(data)

    def mag_values(self):
        mag = self.read_magnetometer()
        mag = [m * lsm9ds1.GAUSS_SENSOR_SCALE for m in mag]
        return mag

    def read_magnetometer(self):
        """Reads the magnetometer field strengths"""
        data = self.mag.read_bytes(Register.OUT_X_L_M, 6)
        return lsm9ds1.to_vector(data)

    @staticmethod
    def to_vector(data):
        return [lsm9ds1.to_int16(data[0:2]), lsm9ds1.to_int16(data[2:4]), lsm9ds1.to_int16(data[4:6])]

    @staticmethod
    def to_vector_left_to_right_hand_rule(data):
        """Like to_vector except it converts from the left to the right hand rule
        by negating the x-axis."""
        return [-lsm9ds1.to_int16(data[0:2]), lsm9ds1.to_int16(data[2:4]), lsm9ds1.to_int16(data[4:6])]

    @staticmethod
    def to_int16(data):
        """
        Converts little endian bytes into a signed 16-bit integer
        :param data: 16bit int in little endian, two's complement form
        :return: an integer
        """
        return int.from_bytes(data, byteorder='little', signed=True)


#
# Run me as an application to get calibration info:
#  python -m lsm9ds1.lsm9ds1
#
def poll_mag_calibration(imu, mc, evt, verbose=True):
    """
    Will poll the x, y mag gauss values in order to establish min, max
    """
    samples = 0
    while not evt.is_set():
        m = imu.mag_values()
        samples += 1
        x = m[lsm9ds1.XMAG_IND]
        y = m[lsm9ds1.YMAG_IND]
        if x < mc.xmin:
            mc.xmin = x
        if x > mc.xmax:
            mc.xmax = x
        if y < mc.ymin:
            mc.ymin = y
        if y > mc.ymax:
            mc.ymax = y

    if verbose:
        print("%d samples." % samples)


def run_interactive_calibration(i2cbus_no):
    mc = MagCalibration()
    evt = threading.Event()
    imu = make_i2c(i2cbus_no)
    calibration__thread = threading.Thread(target=poll_mag_calibration, args=[imu, mc, evt])
    calibration__thread.start()

    input("Rotate device for 2 revolutions at approximately 10 seconds per revolution press enter when done >")
    evt.set()
    calibration__thread.join()

    while True:
        current = input("What direction am I currently facing (in 360°) >")
        try:
            current = float(current)
            break
        except Exception:
            print("I need a floating point number for the heading")

    imu.set_mag_calibration(mc)
    observed = imu.mag_heading()

    mc.heading_offset = current - observed
    return mc


if __name__ == '__main__':
    mc = run_interactive_calibration(0)
    print(mc.to_json())
