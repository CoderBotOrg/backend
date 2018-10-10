"""
"""

from flask import jsonify
import json
from coderbot import CoderBot
from program import ProgramEngine, Program
from config import Config
import connexion
import time
bot_config = Config.get()
bot = CoderBot.get_instance(servo=(bot_config.get("move_motor_mode") == "servo"),
									 motor_trim_factor=float(bot_config.get('move_motor_trim', 1.0)))

prog = None
prog_engine = ProgramEngine.get_instance()

def stop():
	bot.stop()
	return "ok"

def move(data):
	print(data)
	bot.move(speed=data['speed'], elapse=data['elapse'])
	return "ok"

def turn(data):
	print(data)
	bot.turn(speed=data['speed'], elapse=data['elapse'])
	return "ok"

def status():
	return "ok"

def list(data):
	return json.dumps(prog_engine.prog_list())

def exec(data):
	prog = prog_engine.create(data["name"], data["code"])
	return json.dumps(prog.execute())

def save(data):
	prog = Program(data["name"], data["code"], data["dom_code"])
	prog_engine.save(prog)
	return "ok"

def load(data):
    prog = prog_engine.load(data["id"])
    return jsonify(prog.as_json())

