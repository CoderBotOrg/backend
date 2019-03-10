import pigpio
import threading
from time import sleep

from rotarydecoder import RotaryDecoder


class MotorEncoder:
    """ Class that handles rotary decoder motors modelisation

        The support class RotaryDecoder decodes mechanical rotary encoder
        pulses. See the file for more.

        Every movement method must acquire lock in order not to have
        concurrency problems on GPIO READ/WRITE """

    # default constructor
    def __init__(self, pigpio, enable_pin, forward_pin, backward_pin, encoder_feedback_pin):
        # setting pin variables
        self._pigpio = pigpio
        self._enable_pin = enable_pin
        self._forward_pin = forward_pin
        self._backward_pin = backward_pin
        self._encoder_feedback_pin = encoder_feedback_pin

        # setting movement variables
        self._direction = 0
        self._distance = 0
        self._ticks = 0
        self._power = 0
        self._encoder_speed = 0
        self._is_moving = False

        # other
        self._motor_lock = threading.RLock()
        self._rotary_decoder = RotaryDecoder(pigpio, encoder_feedback_pin, self.rotary_callback)

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
        self._direction = 1 if power > 0 else -1  # setting direction according to speed
        self._power = power
        self.stop()  # stopping motor to initialize new movement

        # going forward
        if (self._direction):
            self._pigpio.set_PWM_dutycycle(self._forward_pin, abs(power))
        # going bacakward
        else:
            self._pigpio.set_PWM_dutycycle(self._backward_pin, abs(power))

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
        self._pigpio.write(self._backward_pin, 0)
        self._pigpio.write(self._forward_pin, 0)

        # returning state variables to consistent state
        self._distance = 0       # resetting distance travelled
        self._ticks = 0          # resetting ticks
        self._power = 0          # resetting PWM power
        self._encoder_speed = 0  # resetting encoder speed
        self._direction = 0      # resetting direction
        self._is_moving = False  # resetting moving flag

        # releasing lock
        self._motor_lock.release()

    # CALLBACKS
    """ The callback function rotary_callback is called on FALLING_EDGE by the
        rotary_decoder with a parameter value of 1 (1 new tick)
        - Gearbox ratio: 120:1 (1 wheel revolution = 120 motor revolution)
        - Encoder ratio: 8:1 encoder ticks for 1 motor revolution
        - 1 wheel revolution = 128 * 8 = 960 ticks
        - R = 30mm
        - 1 wheel revolution = 2πR = 2 * π * 30mm = 188.5mm
        - 960 ticks = 188.5mm
        - 1 tick = 0.196mm
        - 1 tick : 0.196mm = x(ticks) : y(mm) """

    # callback function
    def rotary_callback(self, tick):
        self._motor_lock.acquire()
        self._ticks += tick  # updating ticks
        # self._encoder_speed = ?    # encoder speed (mm/s)
        self._distance = self._ticks * 0.196  # (mm) travelled

    # callback cancelling
    def cancel_callback(self):
        self._rotary_decoder.cancel()
