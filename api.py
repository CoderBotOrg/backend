"""
"""

from flask import jsonify
import json
from coderbot import CoderBot
from config import Config
bot_config = Config.get()
bot = CoderBot.get_instance(servo=(bot_config.get("move_motor_mode") == "servo"),
									 motor_trim_factor=float(bot_config.get('move_motor_trim', 1.0)))

def stop():
	bot.stop()
	return "ok"

def test():
	print(json.dumps(request.args))
	return "ok"