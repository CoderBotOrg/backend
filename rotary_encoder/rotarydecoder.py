#!/usr/bin/env python

import pigpio

class RotaryDecoder:

   """ Class to decode mechanical rotary encoder pulses """

   def __init__(self, pi, encoder_feedback_pin, callback):

      self.pi = pi
      self.encoder_feedback_pin = encoder_feedback_pin   # encoder feedback pin
      self.callback = callback   # callback function on event
      self.value = 0             # value of encoder feedback

      # setting up GPIO
      self.pi.set_mode(encoder_feedback_pin, pigpio.INPUT)
      self.pi.set_pull_up_down(encoder_feedback_pin, pigpio.PUD_UP)

      # callback function on EITHER_EDGE
      self.callback_trigger = self.pi.callback(encoder_feedback_pin, pigpio.EITHER_EDGE, self._pulse)

   # pulse is the callback function on EITHER_EDGE
   # it returns a 1 if the feedback square wave is on a falling edge
   def _pulse(self, level):
      self.levB = level;

      if self.levB == 1:
          self.callback(1)


   def cancel(self):

      """
      Cancel the rotary encoder decoder.
      """

      self.callback_trigger.cancel()


