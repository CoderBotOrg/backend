import coderbot
import time

bot = coderbot.CoderBot.get_instance()

#print "bot.move(100, -1, 1000, 1000)"
#bot.move(100, -1, 1000, 1000)

#print "bot.move(100, -1, -1, -1)"
#bot.move(100, 1, -1000, -1000)
"""
bot.move(100, 0.5, -1)
time.sleep(1.0)
bot.move(-100, 0.5, -1)
time.sleep(1.0)
bot.move(100, -1, 500)
time.sleep(1.0)
bot.move(-100, -1, 500)
time.sleep(1.0)

bot.turn(100, 0.5, 500)
time.sleep(1.0)
bot.turn(-100, 0.5, 500)
time.sleep(1.0)
"""
bot.turn(80, -1, 450)
time.sleep(1.0)
bot.turn(-80, -1, 450)

bot.stop()
