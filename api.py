"""
API methods implementation
This file contains every method called by the API defined in v2.yml
"""

import os
import subprocess
import json
import connexion
from tinydb import TinyDB, Query
from tinydb.operations import delete
from cachetools import cached, TTLCache
from coderbot import CoderBot
from program import ProgramEngine
from config import Config

bot_config = Config.get()
bot = CoderBot.get_instance(
    servo=(bot_config.get("move_motor_mode") == "servo"),
    motor_trim_factor=float(bot_config.get("move_motor_trim", 1.0)),
)

def get_serial():
    """
    Extract serial from cpuinfo file
    """
    cpuserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
        f.close()
    except Exception:
        cpuserial = "ERROR000000000"

    return cpuserial

@cached(cache=TTLCache(maxsize=1, ttl=10))
def get_status():
    """
    Expose CoderBot status:
    temperature, uptime, and internet connectivity status.
    (Cached method)
    """
    try:
        temp = os.popen("vcgencmd measure_temp").readline().replace("temp=", "")
    except Exception:
        temp = "undefined"

    uptime = subprocess.check_output(["uptime"]).decode('utf-8').replace('\n', '')
    internet_status = subprocess.check_output(["./utils/check_conn.sh"]).decode('utf-8').replace('\n', '')
    return {'internet_status': internet_status,
            'temp': temp,
            'uptime': uptime}

@cached(cache=TTLCache(maxsize=1, ttl=60))
def get_info():
    """
    Expose informations about the CoderBot system.
    (Cached method)
    """
    try:
        # manifest.json is generated while building/copying the backend
        with open('manifest.json', 'r') as f:
            metadata = json.load(f)
        backend_commit = metadata["backendCommit"][0:7]
    except Exception:
        backend_commit = "undefined"

    try:
        coderbot_version = subprocess.check_output(["cat", "/etc/coderbot/version"]).decode('utf-8').replace('\n', '')
    except Exception:
        coderbot_version = 'undefined'
    try:
        kernel = subprocess.check_output(["uname", "-r"]).decode('utf-8').replace('\n', '')
    except Exception:
        kernel = 'undefined'
    try:
        update_status = subprocess.check_output(["cat", "/etc/coderbot/update_status"]).decode('utf-8').replace('\n', '')
    except Exception:
        update_status = 'undefined'

    serial = get_serial()
    return {'backend_commit': backend_commit,
            'coderbot_version': coderbot_version,
            'update_status': update_status,
            'kernel': kernel,
            'serial': serial}

prog = None
prog_engine = ProgramEngine.get_instance()

# Programs and Activities databases
activities = TinyDB("data/activities.json")

## Robot control

def stop():
    bot.stop()
    return 200

def move(data):
    bot.move(speed=data["speed"], elapse=data["elapse"])
    return 200

def turn(data):
    bot.turn(speed=data["speed"], elapse=data["elapse"])
    return 200

def exec(data):
    program = prog_engine.create(data["name"], data["code"])
    return json.dumps(program.execute())

## System

def status():
    sts = get_status()

    return {
        "status": "ok",
        "internetConnectivity": sts["internet_status"],
        "temp": sts["temp"],
        "uptime": sts["uptime"],
    }

def info():
    inf = get_info()
    return {
        "model": 1,
        "version": inf["coderbot_version"],
        "backend commit build": inf["backend_commit"],
        "kernel" : inf["kernel"],
        "update status": inf["update_status"],
        "serial": inf["serial"]
    }

def restoreSettings():
    with open("data/defaults/config.json") as f:
        Config.write(json.loads(f.read()))
    Config.get()
    return "ok"

def updateFromPackage():
    os.system('sudo bash /home/pi/clean-update.sh')
    file_to_upload = connexion.request.files['file_to_upload']
    file_to_upload.save(os.path.join('/home/pi/', 'update.tar'))
    os.system('sudo reboot')
    return 200



## Programs

def saveProgram(data, overwrite):
    existing_program = prog_engine.load(data["name"])
    if existing_program and not overwrite:
        return "askOverwrite"
    elif existing_program and existing_program["default"] == True:
        return "defaultOverwrite"
    program = Program(name=data["name"], code=data["code"], dom_code=data["dom_code"])
    prog_engine.save(program)
    return 200

def loadProgram(name):
    existing_program = prog_engine.load(name)
    return existing_program.as_dict(), 200

def deleteProgram(data):
    prog_engine.delete(data["name"])

def listPrograms():
    return prog_engine.prog_list()


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

def resetDefaultPrograms():
    """
    Delete everything but the default programs
    """
    programs.purge()
    for filename in os.listdir("data/defaults/programs/"):
        if filename.endswith(".json"):
            with open("data/defaults/programs/" + filename) as p:
                q = p.read()
                programs.insert(json.loads(q))
