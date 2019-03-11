import pigpio
import threading
from time import sleep

from motorencoder import MotorEncoder

class WheelsAxel:
    """ Class that handles both motor encoders, left and right

        This class works like a wheels axle, coordinating left and right
        wheels at the same time

        It also tries to handle the inconsistent tension on wheels
        that makes one wheel go slower than the other """

    def __init__(self, pi, enable_pin,
                 left_forward_pin, left_backward_pin, left_encoder_feedback_pin,
                 right_forward_pin, right_backward_pin, right_encoder_feedback_pin):

        # state variables
        self._is_moving = False

        # left motor
        self._left_motor = MotorEncoder(pi,
                                        enable_pin,
                                        left_forward_pin,
                                        left_backward_pin,
                                        left_encoder_feedback_pin)
        # right motor
        self._right_motor = MotorEncoder(pi,
                                         enable_pin,
                                         right_forward_pin,
                                         right_backward_pin,
                                         right_encoder_feedback_pin)

        # other
        self._wheelsAxle_lock = threading.Condition() # race condition lock

    # STATE GETTERS
    """ Distance and speed are calculated by a mean of the feedback
        from the two motors """
    # distance
    def distance(self):
        l_dist = self._left_motor.distance()
        r_dist = self._right_motor.distance()
        return (l_dist + r_dist) / 2

    #speed
    def speed(self):
        l_speed = self._left_motor.speed()
        r_speed = self._right_motor.speed()
        return (l_speed + r_speed) / 2

    # MOVEMENT
    def control(self, power_left = 100, power_right = 100, time_elapse = 0):

        self._left_motor.control(power_left, time_elapse)
        self._right_motor.control(power_right, time_elapse)
        self._is_moving = True

        if(time_elapse > 0):
            sleep(time_elapse)
            self.stop()

    """ The stop function calls the two stop functions of the two
        correspondent motors """
    def stop(self):
        self._left_motor.stop()
        self._right_motor.stop()
        self._is_moving = False

    # CALLBACK


    def cancel_callback(self):
        self._right_motor.cancel_callback()
        self._left_motor.cancel_callback()
