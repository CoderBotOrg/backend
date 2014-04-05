import os
import time
import pigpio

PIN_MOTOR_ENABLE = 22
PIN_LEFT_FORWARD = 25
PIN_LEFT_BACKWARD = 24
PIN_RIGHT_FORWARD = 4
PIN_RIGHT_BACKWARD = 17

class CoderBot:
  def __init__(self):
    pigpio.start('localhost')
    self.stop()

  the_bot = None

  @classmethod
  def get_instance(cls):
    if not cls.the_bot:
      cls.the_bot = CoderBot()
    return cls.the_bot
    
  def forward(self, seconds=-1):
    pigpio.write(PIN_MOTOR_ENABLE, 1)
    pigpio.write(PIN_LEFT_FORWARD, 1)
    pigpio.write(PIN_RIGHT_FORWARD, 1)
    if seconds > 0:
      time.sleep(seconds)
      self.stop()

  def backward(self, seconds=-1):
    pigpio.write(PIN_MOTOR_ENABLE, 1)
    pigpio.write(PIN_LEFT_BACKWARD, 1)
    pigpio.write(PIN_RIGHT_BACKWARD, 1)
    if seconds > 0:
      time.sleep(seconds)
      self.stop()     
    
  def left(self, seconds=-1):
    pigpio.write(PIN_MOTOR_ENABLE, 1)
    pigpio.write(PIN_LEFT_BACKWARD, 1)
    pigpio.write(PIN_RIGHT_FORWARD, 1)
    if seconds > 0:
      time.sleep(seconds)
      self.stop()    

  def right(self, seconds=-1):
    pigpio.write(PIN_MOTOR_ENABLE, 1)
    pigpio.write(PIN_LEFT_FORWARD, 1)
    pigpio.write(PIN_RIGHT_BACKWARD, 1)
    if seconds > 0:
      time.sleep(seconds)
      self.stop()

  def stop(self):
    pigpio.write(PIN_MOTOR_ENABLE, 0)
    pigpio.write(PIN_LEFT_FORWARD, 0)
    pigpio.write(PIN_LEFT_BACKWARD, 0)
    pigpio.write(PIN_RIGHT_FORWARD, 0)
    pigpio.write(PIN_RIGHT_BACKWARD, 0)

  def say(self, what):
    os.system ('espeak -vit -p 66 -a 200 -s 150 -g 10 "' + repr(what) + '" 2>>/dev/null')


  
