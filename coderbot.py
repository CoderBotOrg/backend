import time
import pigpio

PIN_MOTOR_ENABLE = 22
PIN_LEFT_FORWARD = 25
PIN_LEFT_BACKWARD = 24
PIN_RIGHT_FORWARD = 4
PIN_RIGHT_BACKWARD = 17

class CoderBot:
  def __init__(self):
    pigpio.start()
    pigpio.write(PIN_MOTOR_ENABLE, 0)
    pigpio.write(PIN_LEFT_FORWARD, 0)
    pigpio.write(PIN_RIGHT_FORWARD, 0)
    pigpio.write(PIN_LEFT_BACKWARD, 0)
    pigpio.write(PIN_RIGHT_BACKWARD, 0)

  the_bot = None

  @classmethod
  def get_instance(cls):
    if not cls.the_bot:
      cls.the_bot = CoderBot()
    return cls.the_bot
    
  def forward(self, seconds):
    pigpio.write(PIN_MOTOR_ENABLE, 1)
    pigpio.write(PIN_LEFT_FORWARD, 1)
    pigpio.write(PIN_RIGHT_FORWARD, 1)
    time.sleep(seconds)
    pigpio.write(PIN_MOTOR_ENABLE, 0)
    pigpio.write(PIN_LEFT_FORWARD, 0)
    pigpio.write(PIN_RIGHT_FORWARD, 0)

  def backward(self, seconds):
    pigpio.write(PIN_MOTOR_ENABLE, 1)
    pigpio.write(PIN_LEFT_BACKWARD, 1)
    pigpio.write(PIN_RIGHT_BACKWARD, 1)
    time.sleep(seconds)
    pigpio.write(PIN_MOTOR_ENABLE, 0)
    pigpio.write(PIN_LEFT_BACKWARD, 0)
    pigpio.write(PIN_RIGHT_BACKWARD, 0)
    
  def left(self, seconds):
    pigpio.write(PIN_MOTOR_ENABLE, 1)
    pigpio.write(PIN_LEFT_BACKWARD, 1)
    pigpio.write(PIN_RIGHT_FORWARD, 1)
    time.sleep(seconds)
    pigpio.write(PIN_MOTOR_ENABLE, 0)
    pigpio.write(PIN_LEFT_BACKWARD, 0)
    pigpio.write(PIN_RIGHT_FORWARD, 0)

  def right(self, seconds):
    pigpio.write(PIN_MOTOR_ENABLE, 1)
    pigpio.write(PIN_LEFT_FORWARD, 1)
    pigpio.write(PIN_RIGHT_BACKWARD, 1)
    time.sleep(seconds)
    pigpio.write(PIN_MOTOR_ENABLE, 0)
    pigpio.write(PIN_LEFT_FORWARD, 0)
    pigpio.write(PIN_RIGHT_BACKWARD, 0) 
