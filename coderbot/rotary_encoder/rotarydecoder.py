#!/usr/bin/env python

import pigpio
import threading

class RotaryDecoder:

    """ Class to decode mechanical rotary encoder pulses """

    def __init__(self, pi, feedback_pin_A, feedback_pin_B, callback):

        self._pi = pi
        self._feedback_pin_A = feedback_pin_A   # encoder feedback pin A
        self._feedback_pin_B = feedback_pin_B   # encoder feedback pin B
        self._callback = callback   # callback function on event
        self._direction = 0         # direction, forward = 1, backward = -1, steady = 0

        self._levelA = 0  # value of encoder feedback pin A
        self._levelB = 0  # value of encoder feedback pin B
      
        self._lock = threading.RLock()

        # setting up GPIO
        self._pi.set_mode(feedback_pin_A, pigpio.INPUT)
        self._pi.set_mode(feedback_pin_B, pigpio.INPUT)
        self._pi.set_pull_up_down(feedback_pin_A, pigpio.PUD_UP)
        self._pi.set_pull_up_down(feedback_pin_B, pigpio.PUD_UP)

        # callback function on EITHER_EDGE for each pin
        self._callback_triggerA = self._pi.callback(feedback_pin_A, pigpio.EITHER_EDGE, self._pulseA)
        self._callback_triggerB = self._pi.callback(feedback_pin_B, pigpio.EITHER_EDGE, self._pulseA)

        self._lastGpio = None

    """ pulse is the callback function on EITHER_EDGE
        We have two feedback input from pin A and B (two train waves)
        it returns a 1 if the square waves have A leading B because we're moving forward
        It returns a -1 if the square waves have B leading A because we're moving backwards
        In either case, A is staggered from B by (+-)pi/2 radiants
        Note: level = 0 falling edge
                      1 raising edge
                      2 from watchdog
       
                       +---------+         +---------+      0   
                       |         |         |         |
             B         |         |         |         |
                       |         |         |         |
             +---------+         +---------+         +----- 1   # B leading A
                 +---------+         +---------+            0   # forward
                 |         |         |         |
             A   |         |         |         |
                 |         |         |         |
             ----+         +---------+         +----------+ 1   
            
            
                 +---------+         +---------+            0
                 |         |         |         |
             A   |         |         |         |
                 |         |         |         |
             ----+         +---------+         +----------+ 1   # A leading B
                       +---------+         +---------+      0   # backward
                       |         |         |         |
             B         |         |         |         |
                       |         |         |         |
             +---------+         +---------+         +----- 1
    """
    def _pulse(self, gpio, level, tick):
        self._lock.acquire()
        # interrupt comes from pin A
        if (gpio == self._feedback_pin_A):
            self._levelA = level   # set level of squared wave (0, 1) on A
        # interrupt comes from pin B
        else:
            self._levelB = level   # set level of squared wave (0, 1) on B

        if (gpio != self._lastGpio): # debounce
            self._lastGpio = gpio

            # forward (A leading B)
            if (gpio == self._feedback_pin_A and 
                ((level == 1 and self._levelB == 0) or 
                (level == 0 and self._levelB == 1))):
                self._direction = 1 # forward
            # backward (B leading A)
            elif (gpio == self._feedback_pin_B and 
                ((level == 1 and self._levelA == 0) or
                (level == 0 and self._levelA == 1))):
                self._direction = -1 # forward
        
        direction = self._direction
        self._lock.release()
        self._callback(direction)

    def _pulseA(self, gpio, level, tick):
        self._callback(tick)

    def cancel(self):

        """
        Cancel the rotary encoder decoder callbacks.
        """
        self._callback_triggerA.cancel()
        self._callback_triggerB.cancel()


