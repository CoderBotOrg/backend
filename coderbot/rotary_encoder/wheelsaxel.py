import pigpio
import threading
from time import sleep, time
import logging

from rotary_encoder.motorencoder import MotorEncoder

class WheelsAxel:
    """ Class that handles both motor encoders, left and right

        This class works like a wheels axle, coordinating left and right
        wheels at the same time

        It also tries to handle the inconsistent tension on wheels
        that makes one wheel go slower than the other """

    # Maximum integral error accumulation (prevents windup)
    MAX_INTEGRAL = 5.0

    # Cross-coupling gain for straight-line correction.
    # Penalizes speed difference between wheels to keep the robot straight.
    PID_KP_DIFF = 0.3

    # Maximum power headroom factor.
    # PID can increase power up to this factor above the requested power.
    POWER_HEADROOM = 1.3

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
        if l_dir == r_dir:
            return l_dir
        else:
            return 0

    # MOVEMENT
    """ Movement wrapper method
        if time is specified and distance is not, control_time is called
        if distance is specified and time is not, control_distance is called
        if both distance and time are specified, control_velocity is called """
    def control(self, power_left=100, power_right=100, time_elapse=None, target_distance=None):
        if time_elapse is not None and target_distance is None:  # time
            self.control_time(power_left, power_right, time_elapse)
        elif time_elapse is None and target_distance is not None:  # distance
            self.control_distance(power_left, power_right, target_distance)
        else:  # velocity
            self.control_velocity(time_elapse, target_distance)

    """ Motor time control allows the motors
        to run for a certain amount of time """
    def control_time(self, power_left=100, power_right=100, time_elapse=-1):
        if time_elapse > 0:
            return self.control_time_encoder(power_left, power_right, time_elapse)

        # applying tension to motors (open-loop, no PID — used for
        # continuous/manual control with time_elapse=-1)
        self._left_motor.control(power_left, -1)
        self._right_motor.control(power_right, -1)
        self._is_moving = True

    """ Motor time control allows the motors
        to run for a certain amount of time with PID """
    def control_time_encoder(self, power_left=100, power_right=100, time_elapse=-1):
        time_init = time()
        condition = lambda: time() - time_init < time_elapse
        self._pid_loop(power_left, power_right, condition, "elapse", time_elapse)

    """ Motor distance control allows the motors
            to run for a certain amount of distance (mm) """
    def control_distance(self, power_left=100, power_right=100, target_distance=0):
        condition = lambda: abs(self.distance()) < abs(target_distance)
        self._pid_loop(power_left, power_right, condition, "dist", target_distance)

    def _pid_loop(self, power_left, power_right, continue_condition, label, target_value):
        """Shared PID control loop used by both time and distance control modes.

        Features:
        - Per-wheel PID speed regulation (proportional + integral + derivative)
        - Cross-coupling term that penalizes speed difference between wheels
          for straight-line driving correction
        - Integral windup protection (clamped accumulation)
        - Power headroom: PID can increase power above requested level
          to compensate for friction/load

        Args:
            power_left: power for left motor (-100 to 100)
            power_right: power for right motor (-100 to 100)
            continue_condition: callable returning True while loop should run
            label: label for logging ("elapse" or "dist")
            target_value: target value for logging
        """
        # Guard against zero power (would cause ZeroDivisionError)
        if power_left == 0 or power_right == 0:
            logging.warning("_pid_loop called with zero power, skipping")
            return

        self._is_moving = True

        # get desired direction from power, then normalize on power > 0
        left_direction = power_left / abs(power_left)
        right_direction = power_right / abs(power_right)
        power_left = abs(power_left)
        power_right = abs(power_right)

        # applying tension to motors
        self._left_motor.control(power_left * left_direction)
        self._right_motor.control(power_right * right_direction)

        # PID target speeds (proportional to requested power)
        target_speed_left = (self.pid_max_speed / 100) * power_left   # mm/s
        target_speed_right = (self.pid_max_speed / 100) * power_right  # mm/s

        # Determine if this is straight-line mode (same target for both wheels)
        straight_line = (target_speed_left == target_speed_right)

        # PID state variables
        left_derivative_error = 0.0
        right_derivative_error = 0.0
        left_integral_error = 0.0
        right_integral_error = 0.0
        left_prev_error = 0.0
        right_prev_error = 0.0

        # Power limits: allow PID to increase power above requested
        max_power_left = min(100, power_left * self.POWER_HEADROOM)
        max_power_right = min(100, power_right * self.POWER_HEADROOM)

        logging.info("moving? %s distance: %s target %s: %s",
                     self._is_moving, self.distance(), label, target_value)

        while continue_condition() and self._is_moving:
            left_speed = self._left_motor.speed()
            right_speed = self._right_motor.speed()

            logging.debug("speed.left: %s speed.right: %s", left_speed, right_speed)

            if left_speed > 10 and right_speed > 10:
                # --- Per-wheel PID error (relative) ---
                left_error = (target_speed_left - left_speed) / target_speed_left
                right_error = (target_speed_right - right_speed) / target_speed_right

                # --- Per-wheel PID correction ---
                left_correction = (
                    left_error * self.pid_kp +
                    left_derivative_error * self.pid_kd +
                    left_integral_error * self.pid_ki
                )
                right_correction = (
                    right_error * self.pid_kp +
                    right_derivative_error * self.pid_kd +
                    right_integral_error * self.pid_ki
                )

                # --- Cross-coupling for straight-line correction ---
                # If both wheels should go the same speed, penalize
                # any difference between them
                if straight_line and target_speed_left > 0:
                    speed_diff_error = (left_speed - right_speed) / target_speed_left
                    left_correction -= speed_diff_error * self.PID_KP_DIFF
                    right_correction += speed_diff_error * self.PID_KP_DIFF

                # --- Apply corrections to power ---
                corrected_power_left = power_left + (left_correction * power_left)
                corrected_power_right = power_right + (right_correction * power_right)

                # Clamp to [0, max_power] — allows PID to INCREASE power
                power_left_norm = max(min(corrected_power_left, max_power_left), 0)
                power_right_norm = max(min(corrected_power_right, max_power_right), 0)

                logging.debug(
                    "ls:%d rs:%d le:%.3f re:%.3f ld:%.3f rd:%.3f "
                    "li:%.3f ri:%.3f lc:%.3f rc:%.3f lp:%d rp:%d",
                    int(left_speed), int(right_speed),
                    left_error, right_error,
                    left_derivative_error, right_derivative_error,
                    left_integral_error, right_integral_error,
                    left_correction, right_correction,
                    int(power_left_norm), int(power_right_norm))

                # adjusting power on each motor
                self._left_motor.adjust_power(power_left_norm * left_direction)
                self._right_motor.adjust_power(power_right_norm * right_direction)

                # --- Update derivative term ---
                left_derivative_error = (left_error - left_prev_error) / self.pid_sample_time
                right_derivative_error = (right_error - right_prev_error) / self.pid_sample_time

                # --- Update integral term with windup protection ---
                left_integral_error += left_error * self.pid_sample_time
                right_integral_error += right_error * self.pid_sample_time
                left_integral_error = max(-self.MAX_INTEGRAL,
                                          min(self.MAX_INTEGRAL, left_integral_error))
                right_integral_error = max(-self.MAX_INTEGRAL,
                                           min(self.MAX_INTEGRAL, right_integral_error))

                left_prev_error = left_error
                right_prev_error = right_error

            # checking each SAMPLETIME seconds
            sleep(self.pid_sample_time)

        logging.info("control.stop, target %s: %s actual distance: %s l ticks: %s r ticks: %s",
                     label, target_value, self.distance(),
                     self._left_motor.ticks(), self._right_motor.ticks())
        # robot arrived
        self.stop()

    """ Motor speed control to travel given distance
        in given time adjusting power on motors
        NOT very intuitive, idea has been postponed"""
    def control_velocity(self, time_elapse=0, target_distance=0):
        pass

    """ The stop function calls the two stop functions of the two
        correspondent motors. """
    def stop(self):
        # stopping left and right motors
        self._left_motor.stop()
        self._right_motor.stop()

        # updating state
        logging.info("stopping")
        self._is_moving = False

    # CALLBACK
    def cancel_callback(self):
        self._right_motor.cancel_callback()
        self._left_motor.cancel_callback()
