from time import sleep
from motorencoder import MotorEncoder
import pigpio

pi = pigpio.pi()

m = MotorEncoder(pi, 22, 25, 24, 14, 16)

while(True):
	print("Speed: %d" % (m._encoder_speed))
	print("Distance: %d" % (m._distance))
	#print("Start timer: %d" % (c._twin_motors_enc._left_motor._start_timer))
	#print("Current timer: %d" % (c._twin_motors_enc._left_motor._current_timer))
	#print("Elapse: %d" % (c._twin_motors_enc._left_motor._current_timer - c._twin_motors_enc._left_motor._start_timer))
	print("")
	sleep(0.05)


