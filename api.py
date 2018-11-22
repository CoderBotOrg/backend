"""
"""

from flask import jsonify
import json
from coderbot import CoderBot
from program import ProgramEngine, Program
from config import Config
import connexion
import time
import sqlite3
from tinydb import TinyDB, Query
from tinydb.operations import delete
import os

bot_config = Config.get()
bot = CoderBot.get_instance(
    servo=(bot_config.get("move_motor_mode") == "servo"),
    motor_trim_factor=float(bot_config.get("move_motor_trim", 1.0)),
)

prog = None
prog_engine = ProgramEngine.get_instance()


def stop():
    bot.stop()
    return "ok"


def move(data):
    print(data)
    bot.move(speed=data["speed"], elapse=data["elapse"])
    return 200


def turn(data):
    print(data)
    bot.turn(speed=data["speed"], elapse=data["elapse"])
    return 200


def status():
    return {
        "status": "ok", "internetConnectivity": True, "temp": "40", "uptime": "5h", "status": "ok", "internetConnectivity": True, "temp": "40", "uptime": "5h"}


# Hardware and software information
def info():
    return {
        "model": 1,
        "serial": 2,
        "cbVersion": 3,
        "backendVersion": 4,
        "vueVersion": 5,
        "kernel": 6,
    }

def exec(data):
    prog = prog_engine.create(data["name"], data["code"])
    return json.dumps(prog.execute())

def editSettings(data):
    return "ok"

def restoreSettings():
    with open('defaultConfig.json') as f:
        Config.write(json.loads(f.read()))
    bot_config = Config.get()
    return "ok"


programs = TinyDB("programs.json")
query = Query()

def save(data):
    if(programs.search(query.name == data["name"]) == []):
        programs.insert(data)
    else:
        if(programs.search((query.name == data["name"]) & (query.default == "True"))):
            return "defaultOverwrite"
        else:
            programs.update(data, query.name == data["name"])

def load(name):
    return programs.search(query.name == name)[0]

def delete(data):
    programs.remove(query.name == data["name"])

def list():
    return programs.all()

def resetDefaultPrograms():
    programs.purge()
    for filename in os.listdir("data"):
        if filename.endswith(".data"):
            with open("data/" + filename) as p:
                q = p.read()
                programs.insert(json.loads(q))
resetDefaultPrograms()
#return programs.search(query.default == "True")


settings = TinyDB("settings.json")
settings.insert({"yessa": "okiz"})