import pigpio
import threading
from time import sleep
import logging

from rotary_encoder.motorencoder import MotorEncoder

class WheelsAxel:
    """ Class that handles both motor encoders, left and right

        This class works like a wheels axle, coordinating left and right
        wheels at the same time

        It also tries to handle the inconsistent tension on wheels
        that makes one wheel go slower than the other """

    def __init__(self, pi, enable_pin,
                 left_forward_pin, left_backward_pin, left_encoder_feedback_pin_A, left_encoder_feedback_pin_B,
                 right_forward_pin, right_backward_pin, right_encoder_feedback_pin_A, right_encoder_feedback_pin_B,
                 pid_params):

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

        self.pid_kp = pid_params[0]
        self.pid_kd = pid_params[1]
        self.pid_ki = pid_params[2]
        self.pid_max_speed = pid_params[3]
        self.pid_sample_time = pid_params[4]

        # other
        #self._wheelsAxle_lock = threading.RLock() # race condition lock

    # STATE GETTERS
    """ Distance and speed are calculated by a mean of the feedback
        from the two motors """

    def is_moving(self):
        return self._left_motor.is_moving() or self._right_motor.is_moving()
    
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
    def control(self, power_left=100, power_right=100, time_elapse=None, target_distance=None):
        if(time_elapse is not None and target_distance is None): # time
            self.control_time(power_left, power_right, time_elapse)
        elif(time_elapse is None and target_distance is not None): # distance
            self.control_distance(power_left, power_right, target_distance)
        else: # velocity
            self.control_velocity(time_elapse, target_distance)

    """ Motor time control allows the motors
        to run for a certain amount of time """
    def control_time(self, power_left=100, power_right=100, time_elapse=-1):
        #self._wheelsAxle_lock.acquire() # wheelsAxle lock acquire

        # applying tension to motors
        self._left_motor.control(power_left, -1)
        self._right_motor.control(power_right, -1)
        self._is_moving = True

        # moving for desired time
        # fixed for direct control that uses time_elapse -1 and stops manually
        if(time_elapse > 0):
            sleep(time_elapse)
            self.stop()

    """ Motor distance control allows the motors
            to run for a certain amount of distance (mm) """
    def control_distance(self, power_left=100, power_right=100, target_distance=0):
        #self._wheelsAxle_lock.acquire() # wheelsAxle lock acquire
        self._is_moving = True

        # get desired direction from power, then normalize on power > 0 
        left_direction = power_left/abs(power_left)
        right_direction = power_right/abs(power_right)
        power_left = abs(power_left)
        power_right = abs(power_right)

        self._left_motor.reset_state()
        self._right_motor.reset_state()

        # applying tension to motors
        self._left_motor.control(power_left * left_direction)
        self._right_motor.control(power_right * right_direction)

        #PID parameters
        # assuming that power_right is equal to power_left and that coderbot
        # moves at 11.5mm/s at full PWM duty cycle
        
        target_speed_left = (self.pid_max_speed / 100) * power_left #velocity [mm/s]
        target_speed_right = (self.pid_max_speed / 100) * power_right  # velocity [mm/s]

        # SOFT RESPONSE
        # KP = 0.04  #proportional coefficient
        # KD = 0.02  # derivative coefficient
        # KI = 0.005 # integral coefficient

        # MEDIUM RESPONSE
        # KP = 0.9  # proportional coefficient
        # KD = 0.1  # derivative coefficient
        # KI = 0.05 # integral coefficient

        # STRONG RESPONSE
        # KP = 0.9   # proportional coefficient
        # KD = 0.05  # derivative coefficient
        # KI = 0.03  # integral coefficient

        left_derivative_error = 0
        right_derivative_error = 0
        left_integral_error = 0
        right_integral_error = 0
        left_prev_error = 0
        right_prev_error = 0
        # moving for certaing amount of distance
        logging.info("moving? " + str(self._is_moving) + " distance: " + str(self.distance()) + " target: " + str(target_distance))
        while(abs(self.distance()) < abs(target_distance) and self._is_moving == True):
            # PI controller
            logging.debug("speed.left: " + str(self._left_motor.speed()) + " speed.right: " + str(self._right_motor.speed()))
            if(abs(self._left_motor.speed()) > 10 and abs(self._right_motor.speed()) > 10):
                # relative error
                left_error = float(target_speed_left - self._left_motor.speed()) / target_speed_left
                right_error = float(target_speed_right - self._right_motor.speed()) / target_speed_right

                left_correction = (left_error * self.pid_kp) + (left_derivative_error * self.pid_kd) + (left_integral_error * self.pid_ki)
                right_correction = (right_error * self.pid_kp) + (right_derivative_error * self.pid_kd) + (right_integral_error * self.pid_ki)

                corrected_power_left = power_left + (left_correction * power_left)
                corrected_power_right  = power_right + (right_correction * power_right)

                #print("LEFT correction: %f" % (left_error * KP + left_derivative_error * KD + left_integral_error * KI))
                #print("RIGHT correction: %f" % (right_error * KP + right_derivative_error * KD + right_integral_error * KI))

                # conrispondent new power
                power_left_norm = max(min(corrected_power_left, power_left), 0)
                power_right_norm =  max(min(corrected_power_right, power_right), 0)

                logging.debug("ls:" + str(int(self._left_motor.speed())) + " rs: " + str(int(self._right_motor.speed())) + 
                              " le:" + str(left_error) + " re: " + str(right_error) + 
                              " ld:" + str(left_derivative_error) + " rd: " + str(right_derivative_error) + 
                              " li:" + str(left_integral_error) + " ri: " + str(right_integral_error) + 
                              " lc: " + str(int(left_correction)) + " rc: " + str(int(right_correction)) + 
                              " lp: " + str(int(power_left_norm)) + " rp: " + str(int(power_right_norm)))
 
                # adjusting power on each motors
                self._left_motor.adjust_power(power_left_norm * left_direction )
                self._right_motor.adjust_power(power_right_norm * right_direction)

                left_derivative_error = (left_error - left_prev_error) / self.pid_sample_time
                right_derivative_error = (right_error - right_prev_error) / self.pid_sample_time
                left_integral_error += (left_error * self.pid_sample_time)
                right_integral_error += (right_error * self.pid_sample_time)

                left_prev_error = left_error
                right_prev_error = right_error

            # checking each SAMPLETIME seconds
            sleep(self.pid_sample_time)

        logging.info("control_distance.stop, target dist: " + str(target_distance) + 
            " actual distance: " + str(self.distance()) + 
            " l ticks: " + str(self._left_motor.ticks()) + 
            " r ticks: " + str(self._right_motor.ticks()))
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

        #self._left_motor.reset_state()
        #self._right_motor.reset_state()

        # updating state
        logging.info("stopping")
        self._is_moving = False

    # CALLBACK
    def cancel_callback(self):
        self._right_motor.cancel_callback()
        self._left_motor.cancel_callback()
