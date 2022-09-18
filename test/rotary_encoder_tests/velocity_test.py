from time import sleep
from coderbot import CoderBot

c = CoderBot.get_instance()

while(True):
	print("Speed: %d" % (c._twin_motors_enc._left_motor._encoder_speed))
	print("Distance: %d" % (c._twin_motors_enc._left_motor._distance))
	print("Start timer: %d" % (c._twin_motors_enc._left_motor._start_timer))
	print("Current timer: %d" % (c._twin_motors_enc._left_motor._current_timer))
	print("Elapse: %d" % (c._twin_motors_enc._left_motor._current_timer - c._twin_motors_enc._left_motor._start_timer))
	print("")
	sleep(0.3)


