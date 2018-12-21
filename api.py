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
import subprocess
from cachetools import cached, TTLCache

bot_config = Config.get()
bot = CoderBot.get_instance(
    servo=(bot_config.get("move_motor_mode") == "servo"),
    motor_trim_factor=float(bot_config.get("move_motor_trim", 1.0)),
)

def get_serial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"

  return cpuserial

@cached(cache=TTLCache(maxsize=1, ttl=10))
def get_status():
    try:
        temp = os.popen("vcgencmd measure_temp").readline().replace("temp=","")
    except:
        temp = "undefined"
    
    uptime = subprocess.check_output(["uptime"]).decode('utf-8').replace('\n', '')
    internet_status = subprocess.check_output(["./scripts/check_conn.sh"]).decode('utf-8').replace('\n', '')
    return {'internet_status': internet_status,
            'temp': temp,
            'uptime': uptime}

@cached(cache=TTLCache(maxsize=1, ttl=60))
def get_info():
    # [:-2] strips out '\n' (cat)
    try:
        backend_commit = subprocess.check_output(["git", "rev-parse", "HEAD"])[0:7].decode('utf-8')
    except:
        backend_commit = 'undefined'
    try:
        coderbot_version = subprocess.check_output(["cat", "/etc/coderbot/version"]).decode('utf-8').replace('\n', '')
    except:
        coderbot_version  = 'undefined'
    try:
        kernel = subprocess.check_output(["uname", "-r"]).decode('utf-8').replace('\n', '')
    except:
        kernel = 'undefined'
    try:
        update_status = subprocess.check_output(["cat", "/etc/coderbot/update_status"]).decode('utf-8').replace('\n', '')
    except:
        update_status = 'undefined'

    serial = get_serial();
    return {'backend_commit':backend_commit,
            'coderbot_version':coderbot_version,
            'update_status': update_status,
            'kernel':kernel,
            'serial':serial}

prog = None
prog_engine = ProgramEngine.get_instance()

programs = TinyDB("data/programs.json")
activities = TinyDB("data/activities.json")

query = Query()

def stop():
    bot.stop()
    return 200


def move(data):
    print(data)
    bot.move(speed=data["speed"], elapse=data["elapse"])
    return 200


def turn(data):
    print(data)
    bot.turn(speed=data["speed"], elapse=data["elapse"])
    return 200

def status():
    status = get_status()

    return {
        "status": "ok",
        "internetConnectivity": status["internet_status"],
        "temp": status["temp"],
        "uptime": status["uptime"],
    }

def info():
    info = get_info()
    return {
        "model": 1,
        "version": info["coderbot_version"],
        "backend commit build": info["backend_commit"],
        "kernel" : info["kernel"],
        "update status": info["update_status"],
        "serial": info["serial"]
    }


def exec(data):
    prog = prog_engine.create(data["name"], data["code"])
    return json.dumps(prog.execute())


def restoreSettings():
    with open("data/defaults/config.json") as f:
        Config.write(json.loads(f.read()))
    bot_config = Config.get()
    return "ok"


## Programs


def saveProgram(data, overwrite):
    print(overwrite)
    if programs.search(query.name == data["name"]) == []:
        programs.insert(data)
        return 200
    else:
        # Disallow overwriting a default program
        if programs.search((query.name == data["name"]) & (query.default == "True")):
            return "defaultOverwrite"
        # Overwrite existing program with the same name
        else:
            if (overwrite == "1"):
                programs.update(data, query.name == data["name"])
                return 200
            else:
                return "askOverwrite"


def loadProgram(name):
    return programs.search(query.name == name)[0], 200


def deleteProgram(data):
    programs.remove(query.name == data["name"])


def listPrograms():
    return programs.all()


## Activities

def saveActivity(data):
    data = data["activity"]
    if activities.search(query.name == data["name"]) == []:
        activities.insert(data)
        return 200
    else:
        activities.update(data, query.name == data["name"])
        return 200


def loadActivity(name):
    return activities.search(query.name == name)[0], 200


def deleteActivity(data):
    activities.remove(query.name == data["name"])


def listActivities():
    return activities.all()

# Delete everything but the defaults programs
def resetDefaultPrograms():
    programs.purge()
    for filename in os.listdir("data/defaults/programs/"):
        if filename.endswith(".json"):
            with open("data/defaults/programs/" + filename) as p:
                q = p.read()
                programs.insert(json.loads(q))

def updateFromPackage():
    os.system('sudo bash /home/pi/clean-update.sh')
    file_to_upload = connexion.request.files['file_to_upload']
    file_to_upload.save(os.path.join('/home/pi/', 'update.tar'))
    os.system('sudo coderbot_update /home/pi/update.tar && sudo reboot')
    return 200
