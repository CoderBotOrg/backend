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


db = TinyDB("db.json")
query = Query()

def save(data):
    if(db.search(query.name == data["name"]) == []):
        db.insert(data)
    else:
        db.update(data, query.name == data["name"])

def load(name):
    return db.search(query.name == name)[0]

def delete(data):
    db.remove(query.name == data["name"])

def list():
    return db.all()

def resetDefaultPrograms():
    db.purge()
    for filename in os.listdir("data"):
        if filename.endswith(".data"):
            with open("data/" + filename) as p:
                q = p.read()
                db.insert(json.loads(q))