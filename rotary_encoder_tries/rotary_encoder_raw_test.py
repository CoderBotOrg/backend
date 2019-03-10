PIN_ENCODER_LEFT = 15
PIN_ENCODER_RIGHT = 14

import time
import pigpio

#pi = pigpio.pi('coderbot.local')
pi = pigpio.pi()

print("connected")

pi.set_mode(PIN_ENCODER_LEFT, pigpio.INPUT)
pi.set_mode(PIN_ENCODER_RIGHT, pigpio.INPUT)

pi.set_pull_up_down(PIN_ENCODER_LEFT, pigpio.PUD_UP)
pi.set_pull_up_down(PIN_ENCODER_RIGHT, pigpio.PUD_UP)


while(True):
	print("[ LEFT: " + str(pi.read(PIN_ENCODER_LEFT)) + ", RIGHT: " + str(pi.read(PIN_ENCODER_RIGHT)) + " ]")