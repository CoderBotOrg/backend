#!/usr/bin/env python

import pigpio

class decoder:

   """Class to decode mechanical rotary encoder pulses."""

   def __init__(self, pi, gpioB, callback):

      self.pi = pi
      self.gpioB = gpioB
      self.callback = callback

      self.levB = 0

      self.lastGpio = None

      self.pi.set_mode(gpioB, pigpio.INPUT)

      self.pi.set_pull_up_down(gpioB, pigpio.PUD_UP)

      self.cbB = self.pi.callback(gpioB, pigpio.EITHER_EDGE, self._pulse)

   def _pulse(self, gpio, level, tick):
      self.levB = level;

      #if gpio != self.lastGpio: # debounce
      #   self.lastGpio = gpio
      if self.levB == 1:
          self.callback(1)


   def cancel(self):

      """
      Cancel the rotary encoder decoder.
      """

      self.cbB.cancel()


