import pigpio
import threading
from time import sleep

from rotary_encoder.motorencoder import MotorEncoder

class WheelsAxel:
    """ Class that handles both motor encoders, left and right

        This class works like a wheels axle, coordinating left and right
        wheels at the same time

        It also tries to handle the inconsistent tension on wheels
        that makes one wheel go slower than the other """

    def __init__(self, pi, enable_pin,
                 left_forward_pin, left_backward_pin, left_encoder_feedback_pin_A, left_encoder_feedback_pin_B,
                 right_forward_pin, right_backward_pin, right_encoder_feedback_pin_A, right_encoder_feedback_pin_B):

        # state variables
        self._is_moving = False

        # left motor
        self._left_motor = MotorEncoder(pi,
                                        enable_pin,
                                        left_forward_pin,
                                        left_backward_pin,
                                        left_encoder_feedback_pin_A,
                                        left_encoder_feedback_pin_B)
        # right motor
        self._right_motor = MotorEncoder(pi,
                                         enable_pin,
                                         right_backward_pin,
                                         right_forward_pin,
                                         right_encoder_feedback_pin_A,
                                         right_encoder_feedback_pin_B)

        # other
        self._wheelsAxle_lock = threading.Condition() # race condition lock

    # STATE GETTERS
    """ Distance and speed are calculated by a mean of the feedback
        from the two motors """
    # distance
    def distance(self):
        l_dist = self._left_motor.distance()
        r_dist = self._right_motor.distance()
        return (l_dist + r_dist) * 0.5

    #speed
    def speed(self):
        l_speed = self._left_motor.speed()
        r_speed = self._right_motor.speed()
        return (l_speed + r_speed) * 0.5

    #direction
    def direction(self):
        l_dir = self._left_motor.direction()
        r_dir = self._right_motor.direction()
        if(l_dir == r_dir):
            return l_dir
        else:
            return 0

    # MOVEMENT
    """ Movement wrapper method 
        if time is specified and distance is not, control_time is called
        if distance is specified and time is not, control_distance is called
        if both distance and time are specified, control_velocity is called """
    def control(self, power_left=100, power_right=100, time_elapse=0, target_distance=0):
        if(time_elapse != 0 and target_distance == 0): # time
            self.control_time(power_left, power_right, time_elapse)
        elif(time_elapse == 0 and target_distance != 0): # distance
            self.control_distance(power_left, power_right, target_distance)
        else: # velocity
            self.control_velocity(time_elapse, target_distance)

    """ Motor time control allows the motors
        to run for a certain amount of time """
    def control_time(self, power_left=100, power_right=100, time_elapse=0):
        self._wheelsAxle_lock.acquire() # wheelsAxle lock acquire

        # applying tension to motors
        self._left_motor.control(power_left)
        self._right_motor.control(power_right)
        self._is_moving = True

        # moving for desired time
        if time_elapse > 0:
            sleep(max(time_elapse, 0))
            self.stop()

    """ Motor distance control allows the motors
            to run for a certain amount of distance (mm) """
    def control_distance(self, power_left=100, power_right=100, target_distance=0):
        self._wheelsAxle_lock.acquire() # wheelsAxle lock acquire
        self._is_moving = True

        # applying tension to motors
        self._left_motor.control(power_left)
        self._right_motor.control(power_right)

        # moving for certaing amount of distance
        # threshold value avoid to stop it after
        while(abs(self.distance()) < target_distance):
            pass # busy waiting

        # robot arrived
        self.stop()

    """ Motor speed control to travel given distance
        in given time adjusting power on motors 
        NOT very intuitive, idea has been postponed"""
    def control_velocity(self, time_elapse=0, target_distance=0):
        pass

    """ The stop function calls the two stop functions of the two
        correspondent motors. 
        Locks are automatically obtained """
    def stop(self):
        # stopping left and right motors
        self._left_motor.stop()
        self._right_motor.stop()

        # trying to fix distance different than zero after
        # wheels has stopped by re-resetting state after 0.5s
        sleep(0.5)
        self._left_motor.reset_state()
        self._right_motor.reset_state()

        # updating state
        self._is_moving = False
        # restoring callback
        try:
            self._wheelsAxle_lock.release()
        except RuntimeError:
            pass

    # CALLBACK
    def cancel_callback(self):
        self._right_motor.cancel_callback()
        self._left_motor.cancel_callback()
