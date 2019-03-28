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
        return (l_dist + r_dist) / 2

    #speed
    def speed(self):
        l_speed = self._left_motor.speed()
        r_speed = self._right_motor.speed()
        return (l_speed + r_speed) / 2

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

        # moving for certaing amount of distance
        while(self.distance() < target_distance):
            sleep(0.05) # check if arrived every 50ms,
            print(str(self.distance()))
            target_distance = target_distance - self.distance() # updating target distance

        # robot arrived
        self.stop()

    """ Motor speed control to travel given distance
        in given time adjusting power on motors invididually """
    def control_velocity(self, time_elapse=0, target_distance=0):
        pass

    # old control distance, trying to adjust power
    # def control_distance(self, power_left = 100, power_right = 100, target_distance = 0):
    #     self._is_moving = True
    #     delta = 1
    #
    #     while(target_distance > 0):
    #
    #         self._left_motor.control(min(max(power_left * delta, power_left), 100))
    #         self._right_motor.control(min(max(power_right * delta, power_right), 100))
    #
    #         print("Target distance: " + str(target_distance))
    #         print("Power left: " + str(power_left * delta))
    #         print("Power right: " + str(power_right * delta))
    #
    #         sleep(.2)
    #
    #         try:
    #             delta = self._left_motor.ticks() / self._right_motor.ticks()
    #             target_distance = target_distance - self.distance()
    #         except:
    #             delta = 1
    #
    #         print("delta_ticks: " + str(delta))
    #         print("new target distance: " + str(target_distance))
    #         print("")
    #
    #     print("Stopping...")
    #     self.stop()

    """ The stop function calls the two stop functions of the two
        correspondent motors. 
        Locks are automatically obtained """
    def stop(self):
        self._left_motor.stop()
        self._right_motor.stop()

        self._is_moving = False
        self._wheelsAxle_lock.release()

    # CALLBACK
    def cancel_callback(self):
        self._right_motor.cancel_callback()
        self._left_motor.cancel_callback()
