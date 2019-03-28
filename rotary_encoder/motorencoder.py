import pigpio
import threading
from time import sleep, time

from rotarydecoder import RotaryDecoder


class MotorEncoder:
    """ Class that handles rotary decoder motors modelisation

        The support class RotaryDecoder decodes mechanical rotary encoder
        pulses. See the file for more.

        Every movement method must acquire lock in order not to have
        concurrency problems on GPIO READ/WRITE """

    # default constructor
    def __init__(self, pi, enable_pin, forward_pin, backward_pin, feedback_pin_A, feedback_pin_B):
        # setting pin variables
        self._pi = pi
        self._enable_pin = enable_pin
        self._forward_pin = forward_pin
        self._backward_pin = backward_pin
        self._feedback_pin_A = feedback_pin_A
        self._feedback_pin_B = feedback_pin_B

        # setting movement variables
        self._direction = 0
        self._distance = 0
        self._ticks = 0
        self._power = 0
        self._encoder_speed = 0
        self._is_moving = False

        # other
        self._motor_lock = threading.RLock()
        self._rotary_decoder = RotaryDecoder(pi, feedback_pin_A, feedback_pin_B, self.rotary_callback)

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
        and releases the lock afterwards 
        Motor speed on range 0 - 100 already set on PWM_set_range(100)
        if a time_elapse parameter value is provided, motion is locked
        for a certain amount of time """

    def control(self, power=100.0, time_elapse=0):
        self._motor_lock.acquire()  # acquiring lock

        #self.stop()  # stopping motor to initialize new movement

        self._direction = 1 if power > 0 else -1  # setting direction according to speed
        self._power = power # setting current power

        self._pi.write(self._enable_pin, True)  # enabling motors

        # going forward
        if (self._direction == 1):
            self._pi.set_PWM_dutycycle(self._forward_pin, abs(power))
        # going bacakward
        else:
            self._pi.set_PWM_dutycycle(self._backward_pin, abs(power))

        self._is_moving = True

        # releasing lock on motor
        self._motor_lock.release()

        # movement time elapse
        if (time_elapse > 0):
            sleep(time_elapse)
            self.stop()

    """ The stop function acquires the lock to operate on motor
        then writes a 0 on movement pins to stop the motor
        and releases the lock afterwards """

    def stop(self):
        self._motor_lock.acquire()

        # stopping motor
        self._pi.write(self._backward_pin, 0)
        self._pi.write(self._forward_pin, 0)

        # returning state variables to consistent state
        self._distance = 0       # resetting distance travelled
        self._ticks = 0          # resetting ticks
        self._power = 0          # resetting PWM power
        self._encoder_speed = 0  # resetting encoder speed
        self._direction = 0      # resetting direction
        self._is_moving = False  # resetting moving flag

        # releasing lock
        self._motor_lock.release()

    # CALLBACK
    """ The callback function rotary_callback is called on FALLING_EDGE by the
        rotary_decoder with a parameter value of 1 (1 new tick)
        
        - Gearbox ratio: 120:1 (1 wheel revolution = 120 motor revolution)
        - Encoder ratio: 16:1 encoder ticks for 1 motor revolution
        - 1 wheel revolution = 120 * 16 = 1920 ticks
        - R = 30mm
        - 1 wheel revolution = 2πR = 2 * π * 30mm = 188.5mm
        - 1920 ticks = 188.5mm
        - 1 tick = 0.0981mm
        - 1 tick : 0.0981mm = x : 1000mm -> x = 10193 ticks approximately """

    # callback function
    def rotary_callback(self, tick):
        self._motor_lock.acquire()
        self._ticks += tick  # updating ticks
        self._distance = self._ticks * 0.0981  # (mm) travelled
        #self._encoder_speed = (mm/s)
        self._motor_lock.release()

    # callback cancelling
    def cancel_callback(self):
        self._rotary_decoder.cancel()
