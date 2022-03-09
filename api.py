"""
API methods implementation
This file contains every method called by the API defined in v2.yml
"""

import os
import subprocess
import json
import logging
import connexion
import pigpio
from cachetools import cached, TTLCache
from coderbot import CoderBot
from program import ProgramEngine, Program
from config import Config
from activity import Activities
from coderbotTestUnit import run_test as runCoderbotTestUnit
from cnn_manager import CNNManager
from musicPackages import MusicPackageManager

BUTTON_PIN = 16

bot_config = Config.get()
bot = CoderBot.get_instance(
    motor_trim_factor=float(bot_config.get("move_motor_trim", 1.0)),
    encoder=bool(bot_config.get("encoder"))
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
    try:
        encoder = bool(Config.read().get('encoder'))
        if(encoder):
            motors = 'DC encoder motors'
        else:
            motors = 'DC motors'
    except Exception:
        motors = 'undefined'

    serial = get_serial()

    return {'backend_commit': backend_commit,
            'coderbot_version': coderbot_version,
            'update_status': update_status,
            'kernel': kernel,
            'serial': serial,
            'motors': motors}

prog = None
prog_engine = ProgramEngine.get_instance()

activities = Activities.get_instance()

## Robot control

def stop():
    bot.stop()
    return 200

def move(data):
    try:
        bot.move(speed=data["speed"], elapse=data["elapse"], distance=data["distance"])
    except Exception as e:
        bot.move(speed=data["speed"], elapse=data["elapse"], distance=0)
    return 200

def turn(data):
    try:
        bot.turn(speed=data["speed"], elapse=data["elapse"])
    except Exception as e:
        bot.turn(speed=data["speed"], elapse=-1)
    return 200

def exec(data):
    program = prog_engine.create(data["name"], data["code"])
    options = data["options"]
    return json.dumps(program.execute(options))

## System

def status():
    sts = get_status()
    # getting reset log file
    try:
        with open('/home/pi/coderbot/logs/reset_trigger_service.log', 'r') as log_file:
            data = [x for x in log_file.read().split('\n') if x]
    except Exception: # direct control case
        data = [] # if file doesn't exist, no restore as ever been performed. return empty data


    return {
        "status": "ok",
        "internetConnectivity": sts["internet_status"],
        "temp": sts["temp"],
        "uptime": sts["uptime"],
        "log": data
    }

def info():
    inf = get_info()
    return {
        "model": 1,
        "version": inf["coderbot_version"],
        "backend commit build": inf["backend_commit"],
        "kernel" : inf["kernel"],
        "update status": inf["update_status"],
        "serial": inf["serial"],
        "motors": inf["motors"]
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

def listMusicPackages():
    """
    list available music packages
    """
    musicPkg = MusicPackageManager.get_instance()
    response = musicPkg.listPackages()
    return json.dumps(response)

def updateMusicPackages():
    """
    Add a musical package an save the list of available packages on disk
    also add sounds and directory
    """
    """zipName = request.args.get("zipname")
    """
    file_to_upload = connexion.request.files['file_to_upload']
    print("adding " +str(file_to_upload))
    print("adding " + file_to_upload.filename)
    file_to_upload.save(os.path.join('./updatePackages/', file_to_upload.filename))
    musicPkg = MusicPackageManager.get_instance()
    response = musicPkg.addPackage(file_to_upload.filename)
    if response == 1:
        return 200
    elif response == 2:
        return 400
    elif response == 3:
        return 400

def deleteMusicPackage(package_data):
    """
    Delete a musical package an save the list of available packages on disk
    also delete package sounds and directory
    """
    musicPkg = MusicPackageManager.get_instance()
    musicPkg.deletePackage(package_data['package_name'])
    return 200 

## Programs

def saveProgram(data, overwrite):
    existing_program = prog_engine.load(data["name"])
    if existing_program and not overwrite:
        return "askOverwrite"
    elif existing_program and existing_program.is_default() == True:
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
    activity = data["activity"]
    activities.save(activity)

def loadActivity(name=None, default=None):
    return activities.load(name, default)

def deleteActivity(data):
    activities.delete(data), 200

def listActivities():
    return activities.list()

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

## Reset
def reset():
    pi = pigpio.pi('localhost')
    #simulating FALLING EDGE
    # it triggers the reset by using the service altready running on the system that detects a button press (3 sec).
    pi.write(BUTTON_PIN, 1)
    pi.write(BUTTON_PIN, 0)

    return {
        "status": "ok"
    }

## Test
def testCoderbot(data):
    # taking first JSON key value (varargin)
    tests_state = runCoderbotTestUnit(data[list(data.keys())[0]])
    return tests_state

def list_cnn_models():
    cnn = CNNManager.get_instance()
    logging.info("cnn_models_list")
    return json.dumps(cnn.get_models())

