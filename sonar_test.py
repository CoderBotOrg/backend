from coderbot import CoderBot
import time

bot = CoderBot.get_instance()

for x in range(1,100):
  a = bot.get_sonar_distance(0)
  time.sleep(0.003)
  b = bot.get_sonar_distance(1)
  print "sonar_1: " + str(a) + " sonar_2: " + str(b)
  time.sleep(0.1)

