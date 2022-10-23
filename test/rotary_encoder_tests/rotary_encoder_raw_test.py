PIN_ENCODER_LEFT_A = 14 
PIN_ENCODER_LEFT_B = 15
PIN_ENCODER_RIGHT_A = 24
PIN_ENCODER_RIGHT_B = 25

from time import sleep
import pigpio

pi = pigpio.pi()

print("connected")

pi.set_mode(PIN_ENCODER_LEFT_A, pigpio.INPUT)
pi.set_mode(PIN_ENCODER_LEFT_B, pigpio.INPUT)
pi.set_mode(PIN_ENCODER_RIGHT_A, pigpio.INPUT)
pi.set_mode(PIN_ENCODER_RIGHT_B, pigpio.INPUT)

pi.set_pull_up_down(PIN_ENCODER_LEFT_A, pigpio.PUD_UP)
pi.set_pull_up_down(PIN_ENCODER_LEFT_B, pigpio.PUD_UP)
pi.set_pull_up_down(PIN_ENCODER_RIGHT_A, pigpio.PUD_UP)
pi.set_pull_up_down(PIN_ENCODER_RIGHT_B, pigpio.PUD_UP)


while(True):
	print("LEFT: A: %d, B: %d" % (pi.read(PIN_ENCODER_LEFT_A), pi.read(PIN_ENCODER_LEFT_B)))
	print("RIGHT: A: %d, B: %d" % (pi.read(PIN_ENCODER_RIGHT_A), pi.read(PIN_ENCODER_RIGHT_B)))
	sleep(.05)
