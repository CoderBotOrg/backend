import pigpio
import threading

from rotarydecoder import RotaryDecoder


class MotorEncoder:
    """ Class that handles rotary decoder motors modelisation

        The support class RotaryDecoder decodes mechanical rotary encoder
        pulses. See the file for more.

        Every movement method must acquire lock in order not to have
        concurrency problems on GPIO READ/WRITE """

    # default constructor
    def __init__(self, pi, enable_pin, forward_pin, backward_pin, encoder_feedback_pin):
        # setting pin variables
        self._pi = pi
        self._enable_pin = enable_pin
        self._forward_pin = forward_pin
        self._backward_pin = backward_pin
        self._encoder_feedback_pin = encoder_feedback_pin

        # setting movement variables
        self._direction = 0
        self._distance = 0
        self._ticks = 0
        self._PWM_value = 0
        self._encoder_speed = 0
        self._is_moving = False

        # other
        self._callback = self._pi.callback()
        self._motor_lock = threading.RLock()
        self._rotary_decoder = RotaryDecoder(pi, encoder_feedback_pin, callback)

    # GETTERS
    # ticks
    def ticks(self):
        return self._ticks

    # distance
    def distance(self):
        return self._distance

    # direction
    def direction(self):
        return self._direction

    # speed
    def speed(self):
        return self._encoder_speed

    # is_moving
    def is_moving(self):
        return self._is_moving

    # MOVEMENT
    """ The stop function acquires the lock to operate on motor
        then writes a 0 on movement pins to stop the motor
        and releases the lock afterwards """
    def control(self, speed = 100.0):
        self._motor_lock.acquire()  # acquiring lock
        self._distance = 0  #resetting distance everytime motor is used
        self._direction = 1 if speed > 0 else -1    # setting direction according to speed

        if(self._direction):
            self.stop()
            self._pigpio.set_PWM_dutycycle()
        else
            self.stop()
            self._pigpio.set_PWM_dutycycle()



    """ The stop function acquires the lock to operate on motor
        then writes a 0 on movement pins to stop the motor
        and releases the lock afterwards """
    def stop(self):
        self._motor_lock.acquire()
        self._pi.write(self._backward_pin, 0)
        self._pi.write(self._forward_pin, 0)
        self._is_moving = False
        self._motor_lock.release()

    # OTHER
    # callback cancelling
    def cancel_callback(self):
        self._rotary_decoder.cancel()
