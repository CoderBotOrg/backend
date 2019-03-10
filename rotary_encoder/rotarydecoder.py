#!/usr/bin/env python

import pigpio

class RotaryDecoder:

   """ Class to decode mechanical rotary encoder pulses """

   def __init__(self, pigpio, encoder_feedback_pin, callback):

      self._pigpio = pigpio
      self._encoder_feedback_pin = encoder_feedback_pin   # encoder feedback pin
      self._callback = callback   # callback function on event
      self._value = 0             # value of encoder feedback

      # setting up GPIO
      self._pigpio.set_mode(encoder_feedback_pin, pigpio.INPUT)
      self._pigpio.set_pull_up_down(encoder_feedback_pin, pigpio.PUD_UP)

      # callback function on EITHER_EDGE
      self._callback_trigger = self._pigpio.callback(encoder_feedback_pin, pigpio.EITHER_EDGE, self._pulse)

   """ pulse is the callback function on EITHER_EDGE
       it returns a 1 if the feedback square wave is on a falling edge 
       It simply returns a 1 on FALLING EDGE, i've detached this class in order
       to make it easier in case of extension with PIN A attached too """
   def _pulse(self, level):
      self.levB = level;

      # RAISING EDGE
      if self.levB == 1:
          self.callback(1)


   def cancel(self):

      """
      Cancel the rotary encoder decoder.
      """

      self.callback_trigger.cancel()


