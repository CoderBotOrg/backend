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
                                         right_forward_pin,
                                         right_backward_pin,
                                         right_encoder_feedback_pin_B,
                                         right_encoder_feedback_pin_A)

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
        # fixed for direct control that uses time_elapse -1 and stops manually
        if(time_elapse > 0):
            sleep(time_elapse)
            self.stop()

    """ Motor distance control allows the motors
            to run for a certain amount of distance (mm) """
    def control_distance(self, power_left=100, power_right=100, target_distance=0):
        self._wheelsAxle_lock.acquire() # wheelsAxle lock acquire
        self._is_moving = True

        # applying tension to motors
        self._left_motor.control(power_left)
        self._right_motor.control(power_right)

        #PID parameters
        # assuming that power_right is equal to power_left and that coderbot
        # moves at 11.5mm/s at full PWM duty cycle
        TARGET = 0.95 * power_right #velocity [mm/s]
        KP = 0.02   #proportional coefficient
        KI = 0.005
        SAMPLETIME = 0.05
        left_speed = TARGET
        right_speed = left_speed
        integral_error = 0

        # moving for certaing amount of distance
        while(abs(self.distance()) < target_distance):
            # PI controller

            # relative error
            left_error = TARGET - self._left_motor.speed()
            right_error = TARGET - self._right_motor.speed()

            left_speed += (left_error * KP) - (integral_error * KI)
            right_speed += (right_error * KP) + (integral_error * KI)

            # conrispondent new power
            left_power = max(min(100 * left_speed / 95, 100), 0)
            right_power =  max(min(100 * right_speed / 95, 100), 0)

            print("Left SPEED: %f" % (self._left_motor.speed()))
            print("Right SPEED: %f" % (self._right_motor.speed()))
            print("Left POWER: %f" % (left_power))
            print("Right POWER: %f" % (right_power))

            # adjusting power on each motors
            self._left_motor.adjust_power(left_power)
            self._right_motor.adjust_power(right_power)


            integral_error += (left_speed - right_speed)

            # restoring factor
            left_speed = TARGET
            right_speed = TARGET

            # checking each SAMPLETIME seconds
            sleep(SAMPLETIME)

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
        sleep(0.1)
        self._left_motor.reset_state()
        self._right_motor.reset_state()

        # updating state
        self._is_moving = False
        # restoring callback
        try:
            self._wheelsAxle_lock.release()
        except Exception as e:
            pass

    # CALLBACK
    def cancel_callback(self):
        self._right_motor.cancel_callback()
        self._left_motor.cancel_callback()
