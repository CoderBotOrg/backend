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
import time
import threading
import logging
import pigpio
import sonar
import mpu

PIN_MOTOR_ENABLE = 22
PIN_LEFT_FORWARD = 25
PIN_LEFT_BACKWARD = 24
PIN_RIGHT_FORWARD = 4
PIN_RIGHT_BACKWARD = 17
PIN_PUSHBUTTON = 11
PIN_SERVO_3 = 9
PIN_SERVO_4 = 10
PIN_SONAR_1_TRIGGER = 18
PIN_SONAR_1_ECHO = 7
PIN_SONAR_2_TRIGGER = 18
PIN_SONAR_2_ECHO = 8
PIN_SONAR_3_TRIGGER = 18
PIN_SONAR_3_ECHO = 23
PIN_ENCODER_LEFT = 15
PIN_ENCODER_RIGHT = 14

PWM_FREQUENCY = 100 #Hz
PWM_RANGE = 100 #0-100

class CoderBot(object):

    # pylint: disable=too-many-instance-attributes

    _pin_out = [PIN_MOTOR_ENABLE, PIN_LEFT_FORWARD, PIN_RIGHT_FORWARD, PIN_LEFT_BACKWARD, PIN_RIGHT_BACKWARD, PIN_SERVO_3, PIN_SERVO_4]

    def __init__(self, servo=False, motor_trim_factor=1.0, encoder=False):
        self.pi = pigpio.pi('localhost')
        self.pi.set_mode(PIN_PUSHBUTTON, pigpio.INPUT)
        self._cb = dict()
        self._cb_last_tick = dict()
        self._cb_elapse = dict()
        self._servo = servo
        self._encoder = encoder
        self._motor_trim_factor = motor_trim_factor
        if self._servo:
            self.motor_control = self._servo_motor
        elif self._encoder:
            self._twin_motors_enc = self.TwinMotorsEncoder(
                self.pi,
                pin_enable=PIN_MOTOR_ENABLE,
                pin_forward_left=PIN_LEFT_FORWARD,
                pin_backward_left=PIN_LEFT_BACKWARD,
                pin_encoder_left=PIN_ENCODER_LEFT,
                pin_forward_right=PIN_RIGHT_FORWARD,
                pin_backward_right=PIN_RIGHT_BACKWARD,
                pin_encoder_right=PIN_ENCODER_RIGHT)
            self.motor_control = self._dc_enc_motor
        else:
            self.motor_control = self._dc_motor

        self._cb1 = self.pi.callback(PIN_PUSHBUTTON, pigpio.EITHER_EDGE, self._cb_button)

        for pin in self._pin_out:
            self.pi.set_PWM_frequency(pin, PWM_FREQUENCY)
            self.pi.set_PWM_range(pin, PWM_RANGE)

        self.sonar = [sonar.Sonar(self.pi, PIN_SONAR_1_TRIGGER, PIN_SONAR_1_ECHO),
                      sonar.Sonar(self.pi, PIN_SONAR_2_TRIGGER, PIN_SONAR_2_ECHO),
                      sonar.Sonar(self.pi, PIN_SONAR_3_TRIGGER, PIN_SONAR_3_ECHO)]

        try:
            self._ag = mpu.AccelGyro()
        except IOError:
            logging.info("MPU not available")

        self.stop()
        self._is_moving = False

    the_bot = None

    def exit(self):
        self._cb1.cancel()
        if self._encoder:
            self._twin_motors_enc.exit()
        for s in self.sonar:
            s.cancel()

    @classmethod
    def get_instance(cls, servo=False, motor_trim_factor=1.0):
        if not cls.the_bot:
            cls.the_bot = CoderBot(servo, motor_trim_factor)
        return cls.the_bot

    def move(self, speed=100, elapse=-1, steps=-1):
        speed_left = min(100, max(-100, speed * self._motor_trim_factor))
        speed_right = min(100, max(-100, speed / self._motor_trim_factor))
        self.motor_control(speed_left=speed_left, speed_right=speed_right, elapse=elapse, steps_left=steps, steps_right=steps)

    def turn(self, speed=100, elapse=-1, steps=-1):
        speed_left = min(100, max(-100, speed * self._motor_trim_factor))
        speed_right = -min(100, max(-100, speed / self._motor_trim_factor))
        self.motor_control(speed_left=speed_left, speed_right=speed_right, elapse=elapse, steps_left=steps, steps_right=steps)

    def turn_angle(self, speed=100, angle=0):
        z = self._ag.get_gyro_data()['z']
        self.turn(speed, elapse=-1)
        while abs(z - self._ag.get_gyro_data()['z']) < angle:
            time.sleep(0.05)
            logging.info(self._ag.get_gyro_data()['z'])
        self.stop()

    def forward(self, speed=100, elapse=-1):
        self.move(speed=speed, elapse=elapse)

    def backward(self, speed=100, elapse=-1):
        self.move(speed=-speed, elapse=elapse)

    def left(self, speed=100, elapse=-1):
        self.turn(speed=-speed, elapse=elapse)

    def right(self, speed=100, elapse=-1):
        self.turn(speed=speed, elapse=elapse)

    def servo3(self, angle):
        self._servo_control(PIN_SERVO_3, angle)

    def servo4(self, angle):
        self._servo_control(PIN_SERVO_4, angle)

    def get_sonar_distance(self, sonar_id=0):
        return self.sonar[sonar_id].get_distance()

    def _dc_enc_motor(self, speed_left=100, speed_right=100, elapse=-1, steps_left=-1, steps_right=-1):
        self._twin_motors_enc.control(power_left=speed_left, power_right=speed_right,
                                      elapse=elapse, speed_left=speed_left, speed_right=speed_right,
                                      steps_left=steps_left, steps_right=steps_right)

    def _dc_motor(self, speed_left=100, speed_right=100, elapse=-1, steps_left=-1, steps_right=-1):

        # pylint: disable=too-many-instance-attributes

        self._encoder_cur_left = 0
        self._encoder_cur_right = 0
        self._encoder_target_left = steps_left
        self._encoder_target_right = steps_right
        self._encoder_dir_left = (speed_left > 0) - (speed_left < 0)
        self._encoder_dir_right = (speed_right > 0) - (speed_right < 0)
        self._encoder_last_tick_time_left = 0
        self._encoder_last_tick_time_right = 0
        self._encoder_motor_stopping_left = False
        self._encoder_motor_stopping_right = False
        self._encoder_motor_stopped_left = False
        self._encoder_motor_stopped_right = False

        self._is_moving = True
        if speed_left < 0:
            speed_left = abs(speed_left)
            self.pi.write(PIN_LEFT_FORWARD, 0)
            self.pi.set_PWM_dutycycle(PIN_LEFT_BACKWARD, speed_left)
        else:
            self.pi.write(PIN_LEFT_BACKWARD, 0)
            self.pi.set_PWM_dutycycle(PIN_LEFT_FORWARD, speed_left)

        if speed_right < 0:
            speed_right = abs(speed_right)
            self.pi.write(PIN_RIGHT_FORWARD, 0)
            self.pi.set_PWM_dutycycle(PIN_RIGHT_BACKWARD, speed_right)
        else:
            self.pi.write(PIN_RIGHT_BACKWARD, 0)
            self.pi.set_PWM_dutycycle(PIN_RIGHT_FORWARD, speed_right)

        self.pi.write(PIN_MOTOR_ENABLE, 1)
        if elapse > 0:
            time.sleep(elapse)
            self.stop()

    def _servo_motor(self, speed_left=100, speed_right=100, elapse=-1, steps_left=-1, steps_right=-1):
        self._is_moving = True
        speed_left = -speed_left

        steps_left
        steps_right

        self.pi.write(PIN_MOTOR_ENABLE, 1)
        self.pi.write(PIN_RIGHT_BACKWARD, 0)
        self.pi.write(PIN_LEFT_BACKWARD, 0)

        self._servo_motor_control(PIN_LEFT_FORWARD, speed_left)
        self._servo_motor_control(PIN_RIGHT_FORWARD, speed_right)
        if elapse > 0:
            time.sleep(elapse)
            self.stop()


    def _servo_motor_control(self, pin, speed):
        self._is_moving = True
        speed = ((speed + 100) * 50 / 200) + 52

        self.pi.set_PWM_range(pin, 1000)
        self.pi.set_PWM_frequency(pin, 50)
        self.pi.set_PWM_dutycycle(pin, speed)

    def _servo_control(self, pin, angle):
        duty = ((angle + 90) * 100 / 180) + 25

        self.pi.set_PWM_range(pin, 1000)
        self.pi.set_PWM_frequency(pin, 50)
        self.pi.set_PWM_dutycycle(pin, duty)

    def stop(self):
        if self._encoder:
            self._twin_motors_enc.stop()
        else:
            for pin in self._pin_out:
                self.pi.write(pin, 0)
        self._is_moving = False

    def is_moving(self):
        return self._is_moving

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

    class MotorEncoder(object):
        def __init__(self, parent, _pigpio, pin_enable, pin_forward, pin_backward, pin_encoder):
            self._parent = parent
            self._pigpio = _pigpio
            self._pin_enable = pin_enable
            self._pin_forward = pin_forward
            self._pin_backward = pin_backward
            self._pin_encoder = pin_encoder
            self._direction = False
            self._pin_duty = 0
            self._pin_reverse = 0
            self._power = 0.0
            self._power_actual = 0.0
            self._encoder_dist = 0
            self._encoder_speed = 0.0
            self._encoder_last_tick = 0
            self._encoder_dist_target = 0
            self._encoder_speed_target = 0.0
            self._encoder_k_s_1 = 20
            self._encoder_k_v_1 = 80
            self._motor_stopping = False
            self._motor_running = False
            self._motor_stop_fast = True
            self._pigpio.set_mode(self._pin_encoder, pigpio.INPUT)
            self._cb = self._pigpio.callback(self._pin_encoder, pigpio.RISING_EDGE, self._cb_encoder)
            self._motor_lock = threading.RLock()

        def exit(self):
            self._cb.cancel()

        def _cb_encoder(self, gpio, level, tick):
            self._motor_lock.acquire()
            self._encoder_dist += 1
            delta_ticks = tick - self._encoder_last_tick if tick > self._encoder_last_tick else tick - self._encoder_last_tick + 4294967295
            self._encoder_last_tick = tick
            self._encoder_speed = 1000000.0 / delta_ticks #convert speed in steps per second
            #print "pin: " + str(self._pin_forward) + " dist: " + str(self._encoder_dist) + " target: " + str(self._encoder_dist_target)
            if self._encoder_dist_target >= 0 and self._motor_stop_fast:
                #delta_s is the delta (in steps)before the target  to reverse the motor in order to arrive at target
                delta_s = max(min(self._encoder_speed / self._encoder_k_s_1, 100), 0)
                #print "pin: " + str(self._pin_forward) + " dist: " + str(self._encoder_dist) + " target: " + str(self._encoder_dist_target) + " delta_s: " + str(delta_s)
                if (self._encoder_dist >= self._encoder_dist_target - delta_s and
                        not self._motor_stopping and self._motor_running):
                    self._motor_stopping = True
                    self._pigpio.write(self._pin_duty, 0)
                    self._pigpio.set_PWM_dutycycle(self._pin_reverse, self._power)
                elif (self._motor_running and
                      ((self._motor_stopping and
                        self._encoder_speed < self._encoder_k_v_1) or
                       (self._motor_stopping and
                        self._encoder_dist >= self._encoder_dist_target))):
                    self.stop()
                    logging.info("dist: " + str(self._encoder_dist) + " speed: " + str(self._encoder_speed))
            if self._encoder_dist_target >= 0 and not self._motor_stop_fast:
                if self._encoder_dist >= self._encoder_dist_target:
                    self.stop()
            self._parent._cb_encoder(self, gpio, level, tick)
            self._motor_lock.release()
            if not self._motor_running:
                self._parent._check_complete()

        def control(self, power=100.0, elapse=-1, speed=100.0, steps=-1):
            self._motor_lock.acquire()
            self._direction = speed > 0
            self._encoder_dist_target = steps
            self._motor_stopping = False
            self._motor_running = True
            self._encoder_dist = 0
            self._encoder_speed_target = abs(speed)
            self._power = abs(power) #TODO: initial power must be a function of desired speed
            self._power_actual = abs(power) #TODO: initial power must be a function of desired speed
            self._pin_duty = self._pin_forward if self._direction else self._pin_backward
            self._pin_reverse = self._pin_backward if self._direction else self._pin_forward
            self._pigpio.write(self._pin_reverse, 0)
            self._pigpio.set_PWM_dutycycle(self._pin_duty, self._power)
            self._pigpio.write(self._pin_enable, True)
            self._motor_lock.release()
            if elapse > 0:
                time.sleep(elapse)
                self.stop()

        def stop(self):
            self._motor_lock.acquire()
            self._motor_stopping = False
            self._motor_running = False
            self._pigpio.write(self._pin_forward, 0)
            self._pigpio.write(self._pin_backward, 0)
            self._motor_lock.release()

        def distance(self):
            return self._encoder_dist

        def speed(self):
            return self._encoder_speed

        def stopping(self):
            return self._motor_stopping

        def running(self):
            return self._motor_running

        def adjust_power(self, power_delta):
            self._power_actual = min(max(self._power + power_delta, 0), 100)
            self._pigpio.set_PWM_dutycycle(self._pin_duty, self._power_actual)

    class TwinMotorsEncoder(object):
        def __init__(self, apigpio, pin_enable, pin_forward_left, pin_backward_left, pin_encoder_left, pin_forward_right, pin_backward_right, pin_encoder_right):
            self._straight = False
            self._running = False
            self._encoder_sem = threading.Condition()
            self._motor_left = CoderBot.MotorEncoder(self, apigpio, pin_enable, pin_forward_left, pin_backward_left, pin_encoder_left)
            self._motor_right = CoderBot.MotorEncoder(self, apigpio, pin_enable, pin_forward_right, pin_backward_right, pin_encoder_right)

        def exit(self):
            self._motor_left.exit()
            self._motor_right.exit()

        def control(self, power_left=100.0, power_right=100.0, elapse=-1, speed_left=-1, speed_right=-1, steps_left=-1, steps_right=-1):
            self._straight = power_left == power_right and speed_left == speed_right and steps_left == steps_right

            if steps_left >= 0 or steps_right >= 0:
                self._encoder_sem.acquire()

            self._motor_left.control(power=power_left, elapse=-1, speed=speed_left, steps=steps_left)
            self._motor_right.control(power=power_right, elapse=-1, speed=speed_right, steps=steps_right)
            self._running = True

            if elapse > 0:
                time.sleep(elapse)
                self.stop()

            if steps_left >= 0 or steps_right >= 0:
                self._encoder_sem.wait()
                self._encoder_sem.release()
                self.stop()

        def stop(self):
            self._motor_left.stop()
            self._motor_right.stop()
            self._running = False

        def distance(self):
            return (self._motor_left.distance() + self._motor_right.distance()) / 2

        def speed(self):
            return (self._motor_left.speed() + self._motor_right.speed()) / 2

        def _cb_encoder(self, motor, gpio, level, tick):
            if (self._straight and self._running and not self._motor_left.stopping() and not self._motor_right.stopping() and
                    abs(self._motor_left.distance() - self._motor_right.distance()) > 2):
                distance_delta = self._motor_left.distance() - self._motor_right.distance()
                speed_delta = self._motor_left.speed() - self._motor_right.speed()
                power_delta = (distance_delta / 2.0) + (speed_delta / 10.0)
                #print "power_delta: " + str(power_delta) + " distance_delta: " + str(distance_delta) + " speed_delta: " + str(speed_delta)
                if self._motor_left == motor:
                    self._motor_left.adjust_power(-power_delta)
                if self._motor_right == motor:
                    self._motor_right.adjust_power(power_delta)

        def _check_complete(self):
            if self._motor_left.running() is False and self._motor_right.running() is False:
                self._encoder_sem.acquire()
                self._encoder_sem.notify()
                self._encoder_sem.release()

    def halt(self):
        os.system('sudo halt')

    def restart(self):
        os.system('sudo /etc/init.d/coderbot restart')

    def reboot(self):
        os.system('sudo reboot')
