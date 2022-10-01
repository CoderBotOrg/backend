"""
API methods implementation
This file contains every method called by the API defined in v2.yml
"""

import os
import subprocess
import logging
import connexion
from werkzeug.datastructures import Headers
from flask import (request,
                   send_file,
                   Response)
import connexion
import picamera
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
from coderbotTestUnit import run_test as runCoderbotTestUnit
import pigpio

BUTTON_PIN = 16

config = Config.read()
bot = CoderBot.get_instance(
    motor_trim_factor=float(config.get("move_motor_trim", 1.0)),
    hw_version=config.get("hw_version")
)
audio_device = Audio.get_instance()
cam = Camera.get_instance()

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
    speed=body.get("speed")
    elapse=body.get("elapse")
    distance=body.get("distance")
    if (speed is None or speed == 0) or (elapse is not None and distance is not None):
        return 400
    bot.move(speed=speed, elapse=elapse, distance=distance)
    return 200

def turn(body):
    speed=body.get("speed")
    elapse=body.get("elapse")
    if speed is None or speed == 0:
        return 400
    bot.turn(speed=speed, elapse=elapse)
    return 200

def takePhoto():
    try:
        cam.photo_take()
        Audio.say(config.get("sound_shutter"))
    except Exception as e:
        logging.warning("Error: %s", e)

def recVideo():
    try:
        cam.video_rec()
        audio_device.say(config.get("sound_shutter"))
    except Exception as e:
        logging.warning("Error: %s", e)

def stopVideo():
    try:
        cam.video_stop()
        audio_device.say(config.get("sound_shutter"))
    except Exception as e:
        logging.warning("Error: %s", e)

def speak(body):
    text = body.get("text", "")
    locale = body.get("locale", "")
    logging.info("say: " + text + " in: " + locale)
    audio_device.say(text, locale)

def halt():
    logging.info("shutting down")
    audio_device.say(what=config.get("sound_stop"))
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
    return cam.get_photo_list()

def getPhoto(name):
    mimetype = {'jpg': 'image/jpeg', 'mp4': 'video/mp4'}
    try:
        media_file = cam.get_photo_file(name)
        return send_file(media_file, mimetype=mimetype.get(name[:-3], 'image/jpeg'), max_age=0)
    except picamera.exc.PiCameraError as e:
        logging.error("Error: %s", str(e))
        return 503
    except FileNotFoundError:
        return 404

def takePhoto():
    try:
        cam.photo_take()
    except picamera.exc.PiCameraError as e:
        logging.error("Error: %s", str(e))

def savePhoto(name, body):
    try:
        cam.update_photo({"name": name, "tag": body.get("tag")})
    except FileNotFoundError:
        return 404

def deletePhoto(name):
    logging.debug("photo delete")
    try:
        cam.delete_photo(name)
    except FileNotFoundError:
        return 404

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
    Config.restore()

def loadSettings():
    return Config.get()

def saveSettings(body):
    Config.write(body)

def saveWifiSettings(body):
    """
    Passes the received Wi-Fi configuration to the wifi.py script, applying it.
    Then reboots
    """
    mode = body.get("wifi_mode", "")
    ssid = body.get("wifi_ssid", "")
    psk = body.get("wifi_psk", "")

    logging.info("mode " + mode +" ssid: " + ssid + " psk: " + psk)
    client_params = " --ssid \"" + ssid + "\" --pwd \"" + psk + "\"" if ssid != "" and psk != "" else ""
    logging.info("sudo ./wifi.py updatecfg --mode " + mode + client_params)
    os.system("sudo ./wifi.py updatecfg --mode " + mode + client_params)
    os.system("sudo reboot")
    if mode == "ap":
        return {"base_url": "http://coder.bot"}
    return {"base_url": "http://coderbot.local"}

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
    return response

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

def deleteMusicPackage(name):
    """
    Delete a musical package an save the list of available packages on disk
    also delete package sounds and directory
    """
    musicPkg = MusicPackageManager.get_instance()
    musicPkg.deletePackage(name)
    return 200 

## Programs

def saveAsNewProgram(body):
    overwrite = body.get("overwrite")
    existing_program = prog_engine.load(body.get("name"))
    if existing_program and not overwrite:
        return "askOverwrite"
    elif existing_program and existing_program.is_default() == True:
        return "defaultOverwrite"
    program = Program(name=body.get("name"), code=body.get("code"), dom_code=body.get("dom_code"))
    prog_engine.save(program)
    return 200

def saveProgram(name, body):
    overwrite = body.get("overwrite")
    existing_program = prog_engine.load(name)
    if existing_program and not overwrite:
        return "askOverwrite"
    elif existing_program and existing_program.is_default() == True:
        return "defaultOverwrite"
    program = Program(name=body.get("name"), code=body.get("code"), dom_code=body.get("dom_code"))
    prog_engine.save(program)
    return 200

def loadProgram(name):
    existing_program = prog_engine.load(name)
    if existing_program:
        return existing_program.as_dict(), 200
    else:
        return 404

def deleteProgram(name):
    prog_engine.delete(name)

def listPrograms():
    return prog_engine.prog_list()

def runProgram(name, body):
    """
    Execute the given program
    """
    logging.debug("program_exec")
    code = body.get('code')
    prog = prog_engine.create(name, code)
    return prog.execute()

def stopProgram(name):
    """
    Stop the program execution
    """
    logging.debug("program_end")
    prog = prog_engine.get_current_program()
    if prog:
        prog.stop()
    return "ok"

def statusProgram(name):
    """
    Expose the program status
    """
    logging.debug("program_status")
    prog = prog_engine.get_current_program()
    if prog is None:
        prog = Program("")
    return {'name': prog.name, "running": prog.is_running(), "log": prog_engine.get_log()}


## Activities

def saveActivity(name, body):
    activity = body
    activities.save(activity.get("name"), activity)

def saveAsNewActivity(body):
    activity = body
    activities.save(activity.get("name"), activity)

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
    if len(body.keys()) > 0:
        tests_state = runCoderbotTestUnit(body[list(body.keys())[0]])
        return tests_state
    else:
        return 404

def listCNNModels():
    cnn = CNNManager.get_instance()
    return cnn.get_models()

def trainCNNModel(body):
    cam = Camera.get_instance()
    cnn = CNNManager.get_instance()
    logging.info("cnn_models_new")
    cnn.train_new_model(model_name=body.get("model_name"),
                        architecture=body.get("architecture"),
                        image_tags=body.get("image_tags"),
                        photos_meta=cam.get_photo_list(),
                        training_steps=body.get("training_steps"),
                        learning_rate=body.get("learning_rate"))

    return {"name": body.get("model_name"), "status": 0}

def getCNNModel(name):
    cnn = CNNManager.get_instance()
    model_status = cnn.get_models().get(name)

    return model_status

def deleteCNNModel(name):
    cnn = CNNManager.get_instance()
    model_status = cnn.delete_model(model_name=name)

    return model_status