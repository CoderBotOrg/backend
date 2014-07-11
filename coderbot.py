import os
import time
import pigpio

PIN_MOTOR_ENABLE = 22
PIN_LEFT_FORWARD = 25
PIN_LEFT_BACKWARD = 24
PIN_RIGHT_FORWARD = 4
PIN_RIGHT_BACKWARD = 17
PIN_PUSHBUTTON = 18

PWM_FREQUENCY = 100 #Hz
PWM_RANGE = 100 #0-100

def coderbot_callback(gpio, level, tick):
  return CoderBot.get_instance().callback(gpio, level, tick)

class CoderBot:
  _pin_out = [PIN_MOTOR_ENABLE, PIN_LEFT_FORWARD, PIN_RIGHT_FORWARD, PIN_LEFT_BACKWARD, PIN_RIGHT_BACKWARD]

  def __init__(self):
    self.pi = pigpio.pi('localhost')
    self.pi.set_mode(PIN_PUSHBUTTON, pigpio.INPUT)
    self._cb = dict()
    self._cb_last_tick = dict()
    self._cb_elapse = dict()    
    cb1 = self.pi.callback(PIN_PUSHBUTTON, pigpio.EITHER_EDGE, coderbot_callback)
    for pin in self._pin_out:
      self.pi.set_PWM_frequency(pin, PWM_FREQUENCY)
      self.pi.set_PWM_range(pin, PWM_RANGE)

    self.stop()
    self._is_moving = False
 
  the_bot = None

  @classmethod
  def get_instance(cls):
    if not cls.the_bot:
      cls.the_bot = CoderBot()
    return cls.the_bot

  def forward(self, speed=100, elapse=-1):
    self.motor_control(speed_left=speed, speed_right=speed, elapse=elapse)

  def backward(self, speed=100, elapse=-1):
    self.motor_control(speed_left=-speed, speed_right=-speed, elapse=elapse)

  def left(self, speed=100, elapse=-1):
    self.motor_control(speed_left=-speed, speed_right=speed, elapse=elapse)

  def right(self, speed=100, elapse=-1):
    self.motor_control(speed_left=speed, speed_right= -speed, elapse=elapse)

  def motor_control(self, speed_left=100, speed_right=100, elapse=-1):
    self._is_moving = True

    if speed_left < 0:
      speed_left = abs(speed_left)
      self.pi.write(PIN_LEFT_FORWARD, 0)
      self.pi.set_PWM_dutycycle(PIN_LEFT_BACKWARD, speed_left)
    else:
      self.pi.write(PIN_LEFT_BACKWARD, 0)
      self.pi.set_PWM_dutycycle(PIN_LEFT_FORWARD, speed_left)

    if speed_right < 0:
      speed_right = abs(speed_right)
      self.pi.write(PIN_RIGHT_FORWARD, 0)
      self.pi.set_PWM_dutycycle(PIN_RIGHT_BACKWARD, speed_right)
    else:
      self.pi.write(PIN_RIGHT_BACKWARD, 0)
      self.pi.set_PWM_dutycycle(PIN_RIGHT_FORWARD, speed_right)

    self.pi.write(PIN_MOTOR_ENABLE, 1)
    if elapse > 0:
      time.sleep(elapse)
      self.stop()

  def servo_control(self, speed_left=100, speed_right=100, elapse=-1):
    self._is_moving = True
    speed_left = ((speed_left + 100) * 50 / 200) + 50
    speed_right = ((speed_right + 100) * 50 / 200) + 50

    self.pi.write(PIN_MOTOR_ENABLE, 1)
    self.pi.write(PIN_RIGHT_BACKWARD, 0)
    self.pi.write(PIN_LEFT_BACKWARD, 0)
    self.pi.set_PWM_range(PIN_LEFT_FORWARD, 1000)
    self.pi.set_PWM_range(PIN_RIGHT_FORWARD, 1000)
    self.pi.set_PWM_frequency(PIN_LEFT_FORWARD, 50)
    self.pi.set_PWM_frequency(PIN_RIGHT_FORWARD, 50)
    self.pi.set_PWM_dutycycle(PIN_LEFT_FORWARD, speed_left)
    self.pi.set_PWM_dutycycle(PIN_RIGHT_FORWARD, speed_right)
    if elapse > 0:
      time.sleep(elapse)
      self.stop()


  def stop(self):
    for pin in self._pin_out:
      self.pi.write(pin, 0)
    self._is_moving = False

  def is_moving(self):
    return self._is_moving

  def say(self, what):
    if what and "$" in what:
      os.system ('omxplayer sounds/' + what[1:])
    elif what and len(what):
      os.system ('espeak -vit -p 90 -a 200 -s 150 -g 10 "' + what + '" 2>>/dev/null')

  def set_callback(self, gpio, callback, elapse):
    self._cb_elapse[gpio] = elapse * 1000
    self._cb[gpio] = callback
    self._cb_last_tick[gpio] = 0

  def callback(self, gpio, level, tick):
    cb = self._cb.get(gpio)
    if cb:
      elapse = self._cb_elapse.get(gpio)
      if level == 0:
        self._cb_last_tick[gpio] = tick
      elif tick - self._cb_last_tick[gpio] > elapse: 
        self._cb_last_tick[gpio] = tick
        print "pushed: ", level, tick
        cb()

  def halt(self):
    os.system ('sudo halt')


  
