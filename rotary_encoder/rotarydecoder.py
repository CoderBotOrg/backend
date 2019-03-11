#!/usr/bin/env python

import pigpio

class RotaryDecoder:

   """ Class to decode mechanical rotary encoder pulses """

   def __init__(self, pi, encoder_feedback_pin, callback):

      self._pi = pi
      self._encoder_feedback_pin = encoder_feedback_pin   # encoder feedback pin
      self._callback = callback   # callback function on event
      self._value = 0             # value of encoder feedback

      # setting up GPIO
      self._pi.set_mode(encoder_feedback_pin, pigpio.INPUT)
      self._pi.set_pull_up_down(encoder_feedback_pin, pigpio.PUD_UP)

      # callback function on EITHER_EDGE
      self._callback_trigger = self._pi.callback(encoder_feedback_pin, pigpio.EITHER_EDGE, self._pulse)

   """ pulse is the callback function on EITHER_EDGE
       it returns a 1 if the feedback square wave is on a falling edge 
       It simply returns a 1 on FALLING EDGE, i've detached this class in order
       to make it easier in case of extension with PIN A attached too """
   def _pulse(self, pi, level, tick):
      self._value = level

      # RAISING EDGE
      if self._value == 1:
          self._callback(1)


   def cancel(self):

      """
      Cancel the rotary encoder decoder.
      """

      self._callback_trigger.cancel()


