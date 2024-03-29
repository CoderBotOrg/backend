import pigpio
import threading
from time import sleep, time

from rotary_encoder.rotarydecoder import RotaryDecoder


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
        self._distance_per_tick = 0.06 #(mm)
        self._ticks = 0
        self._power = 0
        self._encoder_speed = 0
        self._is_moving = False

        # quadrature encoder variables
        self._start_timer = 0
        self._current_timer = 0
        self._ticks_threshold = 100
        self._ticks_counter = 0

        # other
        self._encoder_lock = threading.RLock()
        self._rotary_decoder = RotaryDecoder(pi, feedback_pin_A, feedback_pin_B, self.rotary_callback)

    # GETTERS
    # ticks
    def ticks(self):
        return self._ticks

    # distance
    def distance(self):
        #return self._distance
        return self._ticks * self._distance_per_tick

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
        # resetting distance and ticks before new movement
        self._distance = 0  # resetting distance travelled
        self._ticks = 0  # resetting ticks

        self._direction = 1 if power > 0 else -1  # setting direction according to speed
        self._power = abs(power) # setting current power

        if self._enable_pin is not None:
            self._pi.write(self._enable_pin, True)  # enabling motors

        # going forward
        if (self._direction == 1):
            self._pi.write(self._backward_pin, 0)
            self._pi.set_PWM_dutycycle(self._forward_pin, self._power)
        # going bacakward
        else:
            self._pi.write(self._forward_pin, 0)
            self._pi.set_PWM_dutycycle(self._backward_pin, self._power)

        self._is_moving = True

        # movement time elapse
        if (time_elapse > 0):
            sleep(time_elapse)
            self.stop()

    """ The stop function acquires the lock to operate on motor
        then writes a 0 on movement pins to stop the motor
        and releases the lock afterwards """

    def stop(self):
        # stopping motor
        self._pi.write(self._backward_pin, 0)
        self._pi.write(self._forward_pin, 0)

        # resetting wheel state
        self.reset_state()

    # stop auxiliary function, resets wheel state
    def reset_state(self):
        # returning state variables to consistent state
        # after stopping, values of distance and ticks remains until
        # next movement
        self._ticks = 0  # resetting ticks
        self._power = 0  # resetting PWM power
        self._encoder_speed = 0  # resetting encoder speed
        self._direction = 0  # resetting direction
        self._start_timer = 0
        self._current_timer = 0
        self._ticks_counter = 0
        self._is_moving = False  # resetting moving flag

    # adjust power for velocity control loop
    def adjust_power(self, power):
        self._power = power  # setting current power

        # adjusting power forward
        if (self._direction == 1):
            self._pi.set_PWM_dutycycle(self._forward_pin, abs(power))
        # adjusting power bacakward
        else:
            self._pi.set_PWM_dutycycle(self._backward_pin, abs(power))

    # CALLBACK
    """ The callback function rotary_callback is called on EITHER_EDGE by the
            rotary_decoder with a parameter value of 1 (1 new tick)
            - Gearbox ratio: 120:1 (1 wheel revolution = 120 motor revolution)
            - Encoder ratio: 16:1 encoder ticks for 1 motor revolution
            - 1 wheel revolution = 120 * 16 = 1920 ticks
            - R = 32.5mm        
            - 1 wheel revolution = 2πR = 2 * π * 32.5mm = 204.2mm
            - 3840 ticks = 204.2mm
            - 1 tick = 0.053mm
            - 1 tick : 0.053mm = x : 1000mm -> x = 18867 ticks approximately 
            So 0.053 is the ticks->distance(mm) conversion coefficient
            The callback function calculates current velocity by taking groups of 
            ticks_threshold ticks"""
    # callback function
    def rotary_callback(self, tick):
        self._encoder_lock.acquire()

        # taking groups of n ticks each
        if (self._ticks_counter == 0):
            self._start_timer = tick  # clock started
        elif (abs(self._ticks_counter) == self._ticks_threshold):
            self._current_timer = tick
            elapse = (self._current_timer - self._start_timer) / 1000000.0 # calculating time elapse
            # calculating current speed
            self._encoder_speed = self._ticks_threshold * self._distance_per_tick / elapse  # (mm/s)

        self._ticks += 1  # updating ticks

        if(abs(self._ticks_counter) < self._ticks_threshold):
            self._ticks_counter += 1
        else:
            self._start_timer = tick  # clock started
            self._ticks_counter = 0

        # updating ticks counter using module
        # 0, 1, 2, ... 8, 9, 10, 0, 1, 2, ...
        # not ideal, module on ticks counter not precise, may miss an interrupt
        #self._ticks_counter += 1 % (self._ticks_threshold + 1)

        self._encoder_lock.release() # releasing lock

    # callback cancelling
    def cancel_callback(self):
        self._rotary_decoder.cancel()
