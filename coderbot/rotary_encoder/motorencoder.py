import pigpio
import threading
import logging
from collections import deque
from time import sleep, time

from rotary_encoder.rotarydecoder import RotaryDecoder


class MotorEncoder:
    """ Class that handles rotary decoder motors modelisation

        The support class RotaryDecoder decodes mechanical rotary encoder
        pulses. See the file for more.

        Every movement method must acquire lock in order not to have
        concurrency problems on GPIO READ/WRITE """

    # Encoder geometry constants
    # Gearbox ratio: 120:1 (1 wheel revolution = 120 motor revolutions)
    # Encoder ratio: 16 ticks per motor revolution
    # 1 wheel revolution = 120 * 16 = 1920 ticks (single channel)
    # Both channels, EITHER_EDGE: 1920 * 2 = 3840 callbacks per revolution
    # R = 32.5mm → circumference = 2πR = 204.2mm
    # 3840 ticks = 204.2mm → 1 tick = 0.053mm
    DISTANCE_PER_TICK = 0.053  # mm per encoder callback

    # Speed calculation: sliding window size (ticks)
    # Smaller = more responsive but noisier; larger = smoother but laggier
    SPEED_WINDOW_SIZE = 20

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
        self._direction = 0           # commanded direction: 1=forward, -1=backward, 0=stopped
        self._encoder_direction = 0   # direction detected by quadrature encoder
        self._ticks = 0               # total ticks (unsigned, for speed/distance magnitude)
        self._signed_ticks = 0        # signed ticks (for directional distance)
        self._power = 0
        self._encoder_speed = 0.0
        self._is_moving = False

        # sliding window for speed calculation
        self._tick_history = deque(maxlen=self.SPEED_WINDOW_SIZE + 1)

        # other
        self._encoder_lock = threading.RLock()
        self._rotary_decoder = RotaryDecoder(pi, feedback_pin_A, feedback_pin_B, self.rotary_callback)

    # GETTERS
    # ticks
    def ticks(self):
        return self._ticks

    # distance (unsigned magnitude)
    def distance(self):
        return self._ticks * self.DISTANCE_PER_TICK

    # signed distance (positive=forward, negative=backward)
    def signed_distance(self):
        return self._signed_ticks * self.DISTANCE_PER_TICK

    # direction from encoder feedback
    def direction(self):
        return self._encoder_direction

    # speed (always positive, magnitude only)
    def speed(self):
        return self._encoder_speed

    # is_moving
    def is_moving(self):
        return self._is_moving

    # MOVEMENT
    """ The control function sets PWM to drive the motor at the given power.
        Motor speed on range 0 - 100 already set on PWM_set_range(100)
        if a time_elapse parameter value is provided, motion is locked
        for a certain amount of time """

    def control(self, power=100.0, time_elapse=0):
        # resetting ticks before new movement
        self._ticks = 0
        self._signed_ticks = 0

        self._direction = 1 if power > 0 else -1  # setting direction according to speed
        self._power = abs(power)  # setting current power

        if self._enable_pin is not None:
            self._pi.write(self._enable_pin, True)  # enabling motors

        # going forward
        if self._direction == 1:
            self._pi.write(self._backward_pin, 0)
            self._pi.set_PWM_dutycycle(self._forward_pin, self._power)
        # going backward
        else:
            self._pi.write(self._forward_pin, 0)
            self._pi.set_PWM_dutycycle(self._backward_pin, self._power)

        self._is_moving = True

        # movement time elapse
        if time_elapse > 0:
            sleep(time_elapse)
            self.stop()

    """ The stop function writes a 0 on movement pins to stop the motor """

    def stop(self):
        # stopping motor
        self._pi.write(self._backward_pin, 0)
        self._pi.write(self._forward_pin, 0)

        # resetting wheel state
        self.reset_state()

    # stop auxiliary function, resets wheel state
    def reset_state(self):
        # returning state variables to consistent state
        # after stopping, values of distance and ticks remain until
        # next movement
        self._ticks = 0
        self._signed_ticks = 0
        self._power = 0
        self._encoder_speed = 0.0
        self._direction = 0
        self._encoder_direction = 0
        self._tick_history.clear()
        self._is_moving = False

    # adjust power for velocity control loop
    def adjust_power(self, power):
        self._power = abs(power)  # setting current power

        # adjusting power forward
        if self._direction == 1:
            self._pi.set_PWM_dutycycle(self._forward_pin, self._power)
        # adjusting power backward
        else:
            self._pi.set_PWM_dutycycle(self._backward_pin, self._power)

    # CALLBACK
    """ The callback function rotary_callback is called on EITHER_EDGE by the
            rotary_decoder with direction (+1/-1) and tick (pigpio timestamp).

            Speed is calculated using a sliding window of recent ticks for
            responsive, continuous updates. Uses pigpio.tickDiff() to handle
            the 32-bit microsecond counter wraparound (~72 min). """

    def rotary_callback(self, direction, tick):
        with self._encoder_lock:
            # update direction from quadrature decoder
            self._encoder_direction = direction

            # update tick counts
            self._ticks += 1
            self._signed_ticks += direction

            # sliding window speed calculation
            self._tick_history.append(tick)

            if len(self._tick_history) >= self.SPEED_WINDOW_SIZE + 1:
                # we have enough ticks for a speed measurement
                oldest_tick = self._tick_history[0]
                elapsed_us = pigpio.tickDiff(oldest_tick, tick)
                if elapsed_us > 0:
                    self._encoder_speed = (
                        self.SPEED_WINDOW_SIZE * self.DISTANCE_PER_TICK
                        / (elapsed_us / 1000000.0)
                    )  # mm/s
            # else: not enough ticks yet, keep speed at last known value

    # callback cancelling
    def cancel_callback(self):
        self._rotary_decoder.cancel()
