from coderbot import CoderBot
import sys

DISTANCE = float(sys.argv[1])

c = CoderBot()
c.move(speed=70, distance=DISTANCE)
