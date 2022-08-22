"""
API methods implementation
This file contains every method called by the API defined in v2.yml
"""

import os
import subprocess
import json
import logging
from werkzeug.datastructures import Headers
from flask import (request,
                   send_file,
                   Response,
                   jsonify)
from cachetools import cached, TTLCache
from coderbot import CoderBot
from program import ProgramEngine, Program
from config import Config
from activity import Activities
from camera import Camera
from cnn_manager import CNNManager
from musicPackages import MusicPackageManager
from audio import Audio
from event import EventManager
from audioControls import AudioCtrl
from coderbotTestUnit import run_test as runCoderbotTestUnit

BUTTON_PIN = 16

bot_config = Config.get()
bot = CoderBot.get_instance(
    motor_trim_factor=float(bot_config.get("move_motor_trim", 1.0)),
    hw_version=bot_config.get("hw_version")
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

def move(body):
    try:
        bot.move(speed=body["speed"], elapse=body["elapse"], distance=body["distance"])
    except Exception as e:
        bot.move(speed=body["speed"], elapse=body["elapse"], distance=0)
    return 200

def turn(data):
    try:
        bot.turn(speed=data["speed"], elapse=data["elapse"])
    except Exception as e:
        bot.turn(speed=data["speed"], elapse=-1)
    return 200

def takePhoto():
    try:
        cam.photo_take()
        audio.say(app.bot_config.get("sound_shutter"))
    except Exception:
        logging.warning("Camera not present")

def recVideo():
    try:
        cam.video_rec()
        audio.say(app.bot_config.get("sound_shutter"))
    except Exception:
        logging.warning("Camera not present")

def stopVideo():
    try:
        cam.video_stop()
        audio.say(app.bot_config.get("sound_shutter"))
    except Exception:
        logging.warning("Camera not present")

def speak():
    logging.info("say: " + str(param1) + " in: " + str(get_locale()))
    audio.say(param1, get_locale())

def halt():
    logging.info("shutting down")
    audio.say(app.bot_config.get("sound_stop"))
    bot.halt()

def restart():
    logging.info("restarting bot")
    bot.restart()

def reboot():
    logging.info("rebooting")
    bot.reboot()

def video_stream(a_cam):
    while True:
        frame = a_cam.get_image_jpeg()
        yield ("--BOUNDARYSTRING\r\n" +
               "Content-type: image/jpeg\r\n" +
               "Content-Length: " + str(len(frame)) + "\r\n\r\n")
        yield frame
        yield "\r\n"

def streamVideo():
    try:
        cam = Camera.get_instance()
        h = Headers()
        h.add('Age', 0)
        h.add('Cache-Control', 'no-cache, private')
        h.add('Pragma', 'no-cache')
        return Response(video_stream(cam), headers=h, mimetype="multipart/x-mixed-replace; boundary=--BOUNDARYSTRING")
    except Exception:
        pass

def listPhotos():
    """
    Expose the list of taken photos
    """
    cam = Camera.get_instance()
    return json.dumps(cam.get_photo_list())

def getPhoto(filename):
    cam = Camera.get_instance()
    mimetype = {'jpg': 'image/jpeg', 'mp4': 'video/mp4'}
    try:
        media_file = cam.get_photo_file(filename)
        return send_file(media_file, mimetype=mimetype.get(filename[:-3], 'image/jpeg'), cache_timeout=0)
    except picamera.exc.PiCameraError as e:
        logging.error("Error: %s", str(e))

def takePhoto():
    cam = Camera.get_instance()
    try:
        cam.photo_take()
    except picamera.exc.PiCameraError as e:
        logging.error("Error: %s", str(e))

def savePhoto(filename):
    cam = Camera.get_instance()
    data = request.get_data(as_text=True)
    data = json.loads(data)
    cam.update_photo({"name": filename, "tag": data["tag"]})
    return jsonify({"res":"ok"})

def deletePhoto(filename):
    cam = Camera.get_instance()
    logging.debug("photo delete")
    cam.delete_photo(filename)
    return "ok"

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

def loadSettings():
    return Config.get()

def saveSettings():
    Config.write()

def saveWifiSettings(data):
    """
    Passes the received Wi-Fi configuration to the wifi.py script, applying it.
    Then reboots
    """
    mode = data.get("wifi_mode")
    ssid = data.get("wifi_ssid")
    psk = data.get("wifi_psk")

    logging.info("mode " + mode +" ssid: " + ssid + " psk: " + psk)
    client_params = " --ssid \"" + ssid + "\" --pwd \"" + psk + "\"" if ssid != "" and psk != "" else ""
    logging.info(client_params)
    os.system("sudo ./wifi.py updatecfg --mode " + mode + client_params)
    os.system("sudo reboot")
    if mode == "ap":
        return "http://coder.bot"
    return "http://coderbot.local"

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

def addMusicPackage():
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

def saveAsNewProgram(data):
    overwrite = data["overwrite"]
    existing_program = prog_engine.load(data["name"])
    if existing_program and not overwrite:
        return "askOverwrite"
    elif existing_program and existing_program.is_default() == True:
        return "defaultOverwrite"
    program = Program(name=data["name"], code=data["code"], dom_code=data["dom_code"])
    prog_engine.save(program)
    return 200

def saveProgram(name, data):
    overwrite = data["overwrite"]
    existing_program = prog_engine.load(name)
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

def deleteProgram(name):
    prog_engine.delete(name)

def listPrograms():
    return prog_engine.prog_list()

def runProgram(name):
    """
    Execute the given program
    """
    logging.debug("program_exec")
    name = request.form.get('name')
    code = request.form.get('code')
    prog = app.prog_engine.create(name, code)
    return json.dumps(prog.execute())

def stopProgram(name):
    """
    Stop the program execution
    """
    logging.debug("program_end")
    prog = app.prog_engine.get_current_program()
    if prog:
        prog.end()
    return "ok"

def statusProgram():
    """
    Expose the program status
    """
    logging.debug("program_status")
    prog = app.prog_engine.get_current_program()
    if prog is None:
        prog = Program("")
    return json.dumps({'name': prog.name, "running": prog.is_running(), "log": app.prog_engine.get_log()})


## Activities

def saveActivity(name, body):
    activity = body["activity"]
    activities.save(activity)

def saveAsNewActivity(body):
    activity = body["activity"]
    activities.save(activity["name"], activity)

def loadActivity(name=None, default=None):
    return activities.load(name, default)

def deleteActivity(name):
    activities.delete(name), 200

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

## Test
def testCoderbot(body):
    # taking first JSON key value (varargin)
    tests_state = runCoderbotTestUnit(body[list(data.keys())[0]])
    return tests_state

def listCNNModels():
    cnn = CNNManager.get_instance()
    return json.dumps(cnn.get_models())

def trainCNNModel():
    cam = Camera.get_instance()
    cnn = CNNManager.get_instance()
    logging.info("cnn_models_new")
    data = json.loads(request.get_data(as_text=True))
    cnn.train_new_model(model_name=data["model_name"],
                        architecture=data["architecture"],
                        image_tags=data["image_tags"],
                        photos_meta=cam.get_photo_list(),
                        training_steps=data["training_steps"],
                        learning_rate=data["learning_rate"])

    return json.dumps({"name": data["model_name"], "status": 0})

def getCNNModel(model_name):
    cnn = CNNManager.get_instance()
    model_status = cnn.get_models().get(model_name)

    return json.dumps(model_status)

def deleteCNNModel(model_name):
    cnn = CNNManager.get_instance()
    model_status = cnn.delete_model(model_name=model_name)

    return json.dumps(model_status)
