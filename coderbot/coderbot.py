############################################################################
#    CoderBot, a didactical programmable robot.
#    Copyright (C) 2014, 2015 Roberto Previtera <info@coderbot.org>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
############################################################################

import os
import sys
import time
import logging
import pigpio
import sonar
import hw.mpu
from rotary_encoder.wheelsaxel import WheelsAxel

# GPIO
class GPIO_CODERBOT_V_4():
    # motors
    PIN_MOTOR_ENABLE = 22
    PIN_LEFT_FORWARD = 25
    PIN_LEFT_BACKWARD = 24
    PIN_RIGHT_FORWARD = 4
    PIN_RIGHT_BACKWARD = 17

    PIN_PUSHBUTTON = 11
    # servo
    PIN_SERVO_1 = 9
    PIN_SERVO_2 = 10
    # sonar
    PIN_SONAR_1_TRIGGER = 18
    PIN_SONAR_1_ECHO = 7
    PIN_SONAR_2_TRIGGER = 18
    PIN_SONAR_2_ECHO = 8
    PIN_SONAR_3_TRIGGER = 18
    PIN_SONAR_3_ECHO = 23
    PIN_SONAR_4_TRIGGER = 18
    PIN_SONAR_4_ECHO = 13

    # encoder
    PIN_ENCODER_LEFT_A = 14
    PIN_ENCODER_LEFT_B = 6
    PIN_ENCODER_RIGHT_A = 15
    PIN_ENCODER_RIGHT_B = 12

    HAS_ENCODER = False

class GPIO_CODERBOT_V_5():
    # motors
    PIN_MOTOR_ENABLE = None #22
    PIN_LEFT_FORWARD = 17 #25
    PIN_LEFT_BACKWARD = 18 # 24
    PIN_RIGHT_FORWARD = 22 # 4
    PIN_RIGHT_BACKWARD = 23 #17

    PIN_PUSHBUTTON = 16 #11
    # servo
    PIN_SERVO_1 = 19 #9
    PIN_SERVO_2 = 26 #10
    # sonar
    PIN_SONAR_1_TRIGGER = 5 #18
    PIN_SONAR_1_ECHO = 27 #7
    PIN_SONAR_2_TRIGGER = 5 #18
    PIN_SONAR_2_ECHO = 6 #8
    PIN_SONAR_3_TRIGGER = 5 #18
    PIN_SONAR_3_ECHO = 12 #23
    PIN_SONAR_4_TRIGGER = 5 #18
    PIN_SONAR_4_ECHO = 13 #23

    # encoder
    PIN_ENCODER_LEFT_A = 14
    PIN_ENCODER_LEFT_B = 15 #6
    PIN_ENCODER_RIGHT_A = 24 #15
    PIN_ENCODER_RIGHT_B = 25 #12

    HAS_ENCODER = True

# PWM
PWM_FREQUENCY = 100 #Hz
PWM_RANGE = 100 #0-100

HW_VERSIONS = {
  "4": GPIO_CODERBOT_V_4(),
  "5": GPIO_CODERBOT_V_5()
}

class CoderBot(object):

    # pylint: disable=too-many-instance-attributes

    def __init__(self, motor_trim_factor=1.0, hw_version="5"):
        try:
            self._mpu = mpu.AccelGyroMag()
            logging.info("MPU available")
        except:
            logging.info("MPU not available")

        self.GPIOS = HW_VERSIONS.get(hw_version, GPIO_CODERBOT_V_5())
        self._pin_out = [self.GPIOS.PIN_LEFT_FORWARD, self.GPIOS.PIN_RIGHT_FORWARD, self.GPIOS.PIN_LEFT_BACKWARD, self.GPIOS.PIN_RIGHT_BACKWARD, self.GPIOS.PIN_SERVO_1, self.GPIOS.PIN_SERVO_2]
        self.pi = pigpio.pi('localhost')
        self.pi.set_mode(self.GPIOS.PIN_PUSHBUTTON, pigpio.INPUT)
        self._cb = dict()
        self._cb_last_tick = dict()
        self._cb_elapse = dict()
        self._encoder = self.GPIOS.HAS_ENCODER
        self._motor_trim_factor = motor_trim_factor
        self._twin_motors_enc = WheelsAxel(
            self.pi,
            enable_pin=self.GPIOS.PIN_MOTOR_ENABLE,
            left_forward_pin=self.GPIOS.PIN_LEFT_FORWARD,
            left_backward_pin=self.GPIOS.PIN_LEFT_BACKWARD,
            left_encoder_feedback_pin_A=self.GPIOS.PIN_ENCODER_LEFT_A,
            left_encoder_feedback_pin_B=self.GPIOS.PIN_ENCODER_LEFT_B,
            right_forward_pin=self.GPIOS.PIN_RIGHT_FORWARD,
            right_backward_pin=self.GPIOS.PIN_RIGHT_BACKWARD,
            right_encoder_feedback_pin_A=self.GPIOS.PIN_ENCODER_RIGHT_A,
            right_encoder_feedback_pin_B=self.GPIOS.PIN_ENCODER_RIGHT_B)
        self.motor_control = self._dc_enc_motor

        self._cb1 = self.pi.callback(self.GPIOS.PIN_PUSHBUTTON, pigpio.EITHER_EDGE, self._cb_button)

        for pin in self._pin_out:
            self.pi.set_PWM_frequency(pin, PWM_FREQUENCY)
            self.pi.set_PWM_range(pin, PWM_RANGE)

        self.sonar = [sonar.Sonar(self.pi, self.GPIOS.PIN_SONAR_1_TRIGGER, self.GPIOS.PIN_SONAR_1_ECHO),
                      sonar.Sonar(self.pi, self.GPIOS.PIN_SONAR_2_TRIGGER, self.GPIOS.PIN_SONAR_2_ECHO),
                      sonar.Sonar(self.pi, self.GPIOS.PIN_SONAR_3_TRIGGER, self.GPIOS.PIN_SONAR_3_ECHO),
                      sonar.Sonar(self.pi, self.GPIOS.PIN_SONAR_4_TRIGGER, self.GPIOS.PIN_SONAR_4_ECHO)]
        self._servos = [self.GPIOS.PIN_SERVO_1, self.GPIOS.PIN_SERVO_2]

        self.stop()

    the_bot = None

    def exit(self):
        self._cb1.cancel()
        if self._encoder:
            self._twin_motors_enc.cancel_callback()
        for s in self.sonar:
            s.cancel()

    @classmethod
    def get_instance(cls, motor_trim_factor=1.0, hw_version="5", servo=False):
        if not cls.the_bot:
            cls.the_bot = CoderBot(motor_trim_factor=motor_trim_factor, hw_version=hw_version)
        return cls.the_bot

    def move(self, speed=100, elapse=None, distance=None):
        self._motor_trim_factor = 1.0
        speed_left = min(100, max(-100, speed * self._motor_trim_factor))
        speed_right = min(100, max(-100, speed / self._motor_trim_factor))
        self.motor_control(speed_left=speed_left, speed_right=speed_right, time_elapse=elapse, target_distance=distance)

    def turn(self, speed=100, elapse=-1):
        speed_left = min(100, max(-100, speed * self._motor_trim_factor))
        speed_right = -min(100, max(-100, speed / self._motor_trim_factor))
        self.motor_control(speed_left=speed_left, speed_right=speed_right, time_elapse=elapse)

    def turn_angle(self, speed=100, angle=0):
        z = self._mpu.get_gyro()[2]
        self.turn(speed, elapse=0)
        while abs(z - self._mpu.get_gyro()[2]) < angle:
            time.sleep(0.05)
            logging.info(self._mpu.get_gyro()[2])
        self.stop()

    def forward(self, speed=100, elapse=None, distance=None):
        self.move(speed=speed, elapse=elapse, distance=distance)

    def backward(self, speed=100, elapse=None, distance=None):
        self.move(speed=-speed, elapse=elapse, distance=distance)

    def left(self, speed=100, elapse=-1):
        self.turn(speed=-speed, elapse=elapse)

    def right(self, speed=100, elapse=-1):
        self.turn(speed=speed, elapse=elapse)

    def servo(self, servo, angle):
        self._servo_control(self._servos[servo], angle)

    def get_sonar_distance(self, sonar_id=0):
        return self.sonar[sonar_id].get_distance()

    def get_mpu_accel(self, axis=None):
        acc = self._mpu.get_acc()
        if axis is None:
            return acc
        else:
            return int(acc[axis]*100.0)/100.0

    def get_mpu_gyro(self, axis=None):
        gyro = self._mpu.get_gyro()
        if axis is None:
            return gyro
        else:
            return int(gyro[axis]*100.0)/200.0

    def get_mpu_heading(self):
        hdg = self._mpu.get_hdg()
        return int(hdg)

    def get_mpu_temp(self):
        temp = self._mpu.get_temp()
        return int(temp*100.0)/100.0

    def _servo_control(self, pin, angle):
        duty = ((angle + 90) * 100 / 180) + 25

        self.pi.set_PWM_range(pin, 1000)
        self.pi.set_PWM_frequency(pin, 50)
        self.pi.set_PWM_dutycycle(pin, duty)

    def _dc_enc_motor(self, speed_left=100, speed_right=100, time_elapse=None, target_distance=None):
        self._twin_motors_enc.control(power_left=speed_left,
                                      power_right=speed_right,
                                      time_elapse=time_elapse,
                                      target_distance=target_distance)

    def stop(self):
        self._twin_motors_enc.stop()

    def is_moving(self):
        return self._twin_motors_enc._is_moving

    # Distance travelled getter
    def distance(self):
        return self._twin_motors_enc.distance()

    # CoderBot velocity getter
    def speed(self):
        return self._twin_motors_enc.speed()

    # CoderBot direction getter
    def direction(self):
        return self._twin_motors_enc.speed()

    def set_callback(self, gpio, callback, elapse):
        self._cb_elapse[gpio] = elapse * 1000
        self._cb[gpio] = callback
        self._cb_last_tick[gpio] = 0

    def sleep(self, elapse):
        logging.debug("sleep: %s", str(elapse))
        time.sleep(elapse)

    def _cb_button(self, gpio, level, tick):
        cb = self._cb.get(gpio)
        if cb:
            elapse = self._cb_elapse.get(gpio)
            if level == 0:
                self._cb_last_tick[gpio] = tick
            elif tick - self._cb_last_tick[gpio] > elapse:
                self._cb_last_tick[gpio] = tick
                logging.info("pushed: %d, %d", level, tick)
                cb()

    def halt(self):
        os.system('sudo halt')

    def restart(self):
        sys.exit()

    def reboot(self):
        os.system('sudo reboot')

