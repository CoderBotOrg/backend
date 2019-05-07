#!/usr/bin/env python

import pigpio

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

      # setting up GPIO
      self._pi.set_mode(feedback_pin_A, pigpio.INPUT)
      self._pi.set_mode(feedback_pin_B, pigpio.INPUT)
      self._pi.set_pull_up_down(feedback_pin_A, pigpio.PUD_UP)
      self._pi.set_pull_up_down(feedback_pin_B, pigpio.PUD_UP)

      # callback function on EITHER_EDGE for each pin
      self._callback_triggerA = self._pi.callback(feedback_pin_A, pigpio.EITHER_EDGE, self._pulse)
      self._callback_triggerB = self._pi.callback(feedback_pin_B, pigpio.EITHER_EDGE, self._pulse)

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
      # interrupt comes from pin A
      if (gpio == self._feedback_pin_A):
         self._levelA = level   # set level of squared wave (0, 1) on A
      # interrupt comes from pin B
      else:
         self._levelB = level   # set level of squared wave (0, 1) on B

      if (gpio != self._lastGpio): # debounce
         self._lastGpio = gpio

         # backward (A leading B)
         if (gpio == self._feedback_pin_A and level == 1):
            if (self._levelB == 0):
               self._callback(-1)   # A leading B, moving forward
               self._direction = -1 # backward
         elif (gpio == self._feedback_pin_A and level == 0):
            if (self._levelB == 1):
               self._callback(-1)   # A leading B, moving forward
               self._direction = -1 # backward

         # forward (B leading A)
         elif (gpio == self._feedback_pin_B and level == 1):
            if (self._levelA == 0):
               self._callback(1)   # B leading A, moving forward
               self._direction = 1 # forward
         elif (gpio == self._feedback_pin_B and level == 0):
            if (self._levelA == 1):
               self._callback(1)   # A leading B, moving forward
               self._direction = 1 # forward

   def cancel(self):

      """
      Cancel the rotary encoder decoder callbacks.
      """
      self._callback_triggerA.cancel()
      self._callback_triggerB.cancel()


