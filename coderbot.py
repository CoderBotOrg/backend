import os
import time
import pigpio

PIN_MOTOR_ENABLE = 22
PIN_LEFT_FORWARD = 25
PIN_LEFT_BACKWARD = 24
PIN_RIGHT_FORWARD = 4
PIN_RIGHT_BACKWARD = 17
PIN_PUSHBUTTON = 18

def pushed_button(gpio, level, tick):
  return CoderBot.get_instance().pushed_button(level, tick)

class CoderBot:
  def __init__(self):
    pigpio.start('localhost')
    pigpio.set_mode(PIN_PUSHBUTTON, pigpio.INPUT)
    self._cb_pushbutton = None
    self._cb_last_tick = 0
    self._elapse_pushbutton = 0    
    cb1 = pigpio.callback(PIN_PUSHBUTTON, pigpio.RISING_EDGE, pushed_button)
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

  def set_pushed_button_callback(callback, elapse):
    self._elapse_pushbutton = elapse
    self._cb_pushbutton = callback

  def pushed_button(self, level, tick):
    if tick - self._cb_last_tick > 10000: 
      self._cb_last_tick = tick
      print "pushed: ", level, tick
      if self._cb_pushbutton:
        self._cb_pushbutton(self, level, tick)

  def halt(self):
    os.system ('sudo halt')


  
