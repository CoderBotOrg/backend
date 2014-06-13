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
    self._is_moving = False

  the_bot = None

  @classmethod
  def get_instance(cls):
    if not cls.the_bot:
      cls.the_bot = CoderBot()
    return cls.the_bot

  def forward(self, speed=100, elapse=-1):
    self._is_moving = True
    speed = (255 * speed) / 100
    pigpio.write(PIN_RIGHT_FORWARD, 1)
    pigpio.write(PIN_LEFT_FORWARD, 1)
    pigpio.write(PIN_RIGHT_BACKWARD, 0)
    pigpio.write(PIN_LEFT_BACKWARD, 0)
    pigpio.set_PWM_frequency(PIN_MOTOR_ENABLE, 100)
    pigpio.set_PWM_dutycycle(PIN_MOTOR_ENABLE, speed)
    if elapse > 0:
      time.sleep(elapse)
      self.stop()

  def backward(self, speed=100, elapse=-1):
    self._is_moving = True
    speed = (255 * speed) / 100
    pigpio.write(PIN_RIGHT_FORWARD, 0)
    pigpio.write(PIN_LEFT_FORWARD, 0)
    pigpio.write(PIN_RIGHT_BACKWARD, 1)
    pigpio.write(PIN_LEFT_BACKWARD, 1)
    pigpio.set_PWM_frequency(PIN_MOTOR_ENABLE, 100)
    pigpio.set_PWM_dutycycle(PIN_MOTOR_ENABLE, speed)
    if elapse > 0:
      time.sleep(elapse)
      self.stop()

  def left(self, speed=100, elapse=-1):
    self._is_moving = True
    speed = (255 * speed) / 100
    pigpio.write(PIN_RIGHT_FORWARD, 1)
    pigpio.write(PIN_LEFT_FORWARD, 0)
    pigpio.write(PIN_RIGHT_BACKWARD, 0)
    pigpio.write(PIN_LEFT_BACKWARD, 1)
    pigpio.set_PWM_frequency(PIN_MOTOR_ENABLE, 100)
    pigpio.set_PWM_dutycycle(PIN_MOTOR_ENABLE, speed)
    if elapse > 0:
      time.sleep(elapse)
      self.stop()

  def right(self, speed=100, elapse=-1):
    self._is_moving = True
    speed = (255 * speed) / 100
    pigpio.write(PIN_RIGHT_FORWARD, 0)
    pigpio.write(PIN_LEFT_FORWARD, 1)
    pigpio.write(PIN_RIGHT_BACKWARD, 1)
    pigpio.write(PIN_LEFT_BACKWARD, 0)
    pigpio.set_PWM_frequency(PIN_MOTOR_ENABLE, 100)
    pigpio.set_PWM_dutycycle(PIN_MOTOR_ENABLE, speed)
    if elapse > 0:
      time.sleep(elapse)
      self.stop()

  def forward_old(self, seconds=-1):
    pigpio.write(PIN_LEFT_FORWARD, 1)
    pigpio.write(PIN_RIGHT_FORWARD, 1)
    pigpio.write(PIN_MOTOR_ENABLE, 1)
    if seconds > 0:
      time.sleep(seconds)
      self.stop()

  def backward_old(self, seconds=-1):
    pigpio.write(PIN_LEFT_BACKWARD, 1)
    pigpio.write(PIN_RIGHT_BACKWARD, 1)
    pigpio.write(PIN_MOTOR_ENABLE, 1)
    if seconds > 0:
      time.sleep(seconds)
      self.stop()     
    
  def left_old(self, seconds=-1):
    pigpio.write(PIN_LEFT_BACKWARD, 1)
    pigpio.write(PIN_RIGHT_FORWARD, 1)
    pigpio.write(PIN_MOTOR_ENABLE, 1)
    if seconds > 0:
      time.sleep(seconds)
      self.stop()    

  def right_old(self, seconds=-1):
    pigpio.write(PIN_LEFT_FORWARD, 1)
    pigpio.write(PIN_RIGHT_BACKWARD, 1)
    pigpio.write(PIN_MOTOR_ENABLE, 1)
    if seconds > 0:
      time.sleep(seconds)
      self.stop()

  def stop(self):
    pigpio.write(PIN_MOTOR_ENABLE, 0)
    pigpio.write(PIN_LEFT_FORWARD, 0)
    pigpio.write(PIN_LEFT_BACKWARD, 0)
    pigpio.write(PIN_RIGHT_FORWARD, 0)
    pigpio.write(PIN_RIGHT_BACKWARD, 0)
    self._is_moving = False

  def is_moving(self):
    return self._is_moving

  def say(self, what):
    if what and "$" in what:
      os.system ('omxplayer sounds/' + what[1:])
    elif what and len(what):
      os.system ('espeak -vit -p 90 -a 200 -s 150 -g 10 "' + what + '" 2>>/dev/null')

  def halt(self):
    os.system ('sudo halt')


  
