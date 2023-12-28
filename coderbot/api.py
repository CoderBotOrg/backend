"""
API methods implementation
This file contains every method called by the API defined in v2.yml
"""

import logging
import os
import subprocess
import urllib
from datetime import datetime

import connexion
import picamera
from flask import Response, request, send_file
from werkzeug.datastructures import Headers

from config import Config
from activity import Activities
from audio import Audio
from camera import Camera
from cnn.cnn_manager import CNNManager
from runtime_test import run_test
from musicPackages import MusicPackageManager
from program import Program, ProgramEngine
from motion import Motion
from cloud import CloudManager

from balena import Balena
from coderbot import CoderBot

BUTTON_PIN = 16

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

def get_status():
    """
    Expose CoderBot status:
    temperature, uptime, and internet connectivity status.
    (Cached method)
    """

    temp = "undefined"
    try:
        temp = os.popen("vcgencmd measure_temp").readline().replace("temp=", "")
    except Exception:
        pass

    uptime = 0
    try:
        uptime = subprocess.check_output(["uptime"]).decode('utf-8').replace('\n', '')
    except Exception:
        pass

    internet_status = False
    try:
        urllib.request.urlopen("https://coderCoderBot.get_instance().org") 
        internet_status = True
    except Exception:
        pass

    return {'internet_status': internet_status,
            'temp': temp,
            'uptime': uptime}

def get_info():
    """
    Expose informations about the CoderBot system.
    (Cached method)
    """
    device = {}
    serial = get_serial()

    try:
        device = Balena.get_instance().device()
        logging.info("device: %s", str(device))
    except Exception:
        pass

    return { 'release_commit': device.get("commit"),
             'coderbot_version': os.getenv("CODERBOT_VERSION"),
             'update_status': device.get("status"),
             'kernel': device.get("os_version"),
             'serial': serial }

prog = None
prog_engine = ProgramEngine.get_instance()

activities = Activities.get_instance()

## Robot control

def stop():
    CoderBot.get_instance().stop()
    return {}

def move(body):
    speed=body.get("speed")
    elapse=body.get("elapse")
    distance=body.get("distance")
    if (speed is None or speed == 0) or (elapse is not None and distance is not None):
        return None, 400
    CoderBot.get_instance().move(speed=speed, elapse=elapse, distance=distance)
    return {}

def turn(body):
    speed=body.get("speed")
    elapse=body.get("elapse")
    distance=body.get("distance")
    if (speed is None or speed == 0) or (elapse is not None and distance is not None):
        return None, 400
    CoderBot.get_instance().turn(speed=speed, elapse=elapse, distance=distance)
    return {}

def takePhoto():
    try:
        Camera.get_instance().photo_take()
        Audio.get_instance().say(settings.get("sound_shutter"))
        return {}
    except Exception as e:
        logging.warning("Error: %s", e)

def recVideo():
    try:
        Camera.get_instance().video_rec()
        Audio.get_instance().say(settings.get("sound_shutter"))
        return {}
    except Exception as e:
        logging.warning("Error: %s", e)

def stopVideo():
    try:
        Camera.get_instance().video_stop()
        Audio.get_instance().say(settings.get("sound_shutter"))
        return {}
    except Exception as e:
        logging.warning("Error: %s", e)

def speak(body):
    text = body.get("text", "")
    locale = body.get("locale", "")
    logging.debug("say: " + text + " in: " + locale)
    Audio.get_instance().say(text, locale)
    return {}

def reset():
    Balena.get_instance().purge()
    return {}

def halt():
    Audio.get_instance().say(what=settings.get("sound_stop"))
    Balena.get_instance().shutdown()
    return {}

def restart():
    Balena.get_instance().restart()

def reboot():
    Audio.get_instance().say(what=settings.get("sound_stop"))
    Balena.get_instance().reboot()
    return {}

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
        return Response(video_stream(Camera.get_instance()), headers=h, mimetype="multipart/x-mixed-replace; boundary=--BOUNDARYSTRING")
    except Exception:
        pass

def listPhotos():
    """
    Expose the list of taken photos
    """
    return Camera.get_instance().get_photo_list()

def getPhoto(name):
    mimetype = {'jpg': 'image/jpeg', 'mp4': 'video/mp4'}
    try:
        media_file = Camera.get_instance().get_photo_file(name)
        return send_file(media_file, mimetype=mimetype.get(name[:-3], 'image/jpeg'), max_age=0)
    except picamera.exc.PiCameraError as e:
        logging.error("Error: %s", str(e))
        return {"exception": str(e)}, 503
    except FileNotFoundError:
        return None, 404

def savePhoto(name, body):
    try:
        Camera.get_instance().update_photo({"name": name, "tag": body.get("tag")})
    except FileNotFoundError:
        return None, 404

def deletePhoto(name):
    logging.debug("photo delete")
    try:
        Camera.get_instance().delete_photo(name)
    except FileNotFoundError:
        return None, 404

def restoreSettings():
    Config.restore()
    return restart()

def loadSettings():
    return Config.get()

def saveSettings(body):
    Config.write(body)
    return Config.write(body)

def updateFromPackage():
    os.system('sudo bash /home/pi/clean-update.sh')
    file_to_upload = connexion.request.files['file_to_upload']
    file_to_upload.save(os.path.join('/home/pi/', 'update.tar'))
    os.system('sudo reboot')
    return {}

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
    zipName = request.args.get("zipname")
    """
    try:
        file_to_upload = connexion.request.files['file_to_upload']
        logging.info("adding " + file_to_upload.filename)
        file_to_upload.save(os.path.join('/tmp/', file_to_upload.filename))
        music_pkg = MusicPackageManager.get_instance()
        music_pkg.addPackage(file_to_upload.filename)
        return "{}", 200
    except ValueError:
        return "{}", 409
    except Exception:
        return "{}", 400

def deleteMusicPackage(name):
    """
    Delete a musical package an save the list of available packages on disk
    also delete package sounds and directory
    """
    musicPkg = MusicPackageManager.get_instance()
    musicPkg.deletePackage(name)
    return {} 

## Programs

def saveNewProgram(body):
    overwrite = body.get("overwrite")
    name = body["name"]
    existing_program = prog_engine.load_by_name(name)
    logging.info("saving - name: %s, body: %s", name, str(existing_program))
    if existing_program is not None and not overwrite:
        return "askOverwrite"
    elif existing_program is not None and existing_program.is_stock() == True:
        return "defaultCannotOverwrite", 400
    program = Program(name=body.get("name"), code=body.get("code"), dom_code=body.get("dom_code"), modified=datetime.now(), status="active")
    program_db_entry = prog_engine.save(program)
    return program_db_entry

def saveProgram(id, body):
    overwrite = body.get("overwrite")
    name = body["name"]
    existing_program = prog_engine.load(id)
    logging.info("saving - id: %s - name: %s - existing: %s", id, name, str(existing_program is not None))
    if existing_program is not None and existing_program.is_stock() == True:
        return "defaultCannotOverwrite", 400
    program = Program(
        id=existing_program._id,
        name=existing_program._name, 
        code=body.get("code"), 
        dom_code=body.get("dom_code"), 
        modified=datetime.now(),
        status="active")
    prog_engine.save(program)
    return program.as_dict()

def loadProgram(id):
    existing_program = prog_engine.load(id)
    if existing_program:
        return existing_program.as_dict(), 200
    else:
        return None, 404

def deleteProgram(id):
    prog_engine.delete(id, logical=True)

def listPrograms():
    return prog_engine.prog_list(active_only=True)

def runProgram(id):
    """
    Execute the given program
    """
    logging.debug("program_exec")
    prog = prog_engine.load(id)
    if prog is not None:
        return prog.execute()
    else:
        return {}, 404

def stopProgram(id):
    """
    Stop the program execution
    """
    logging.debug("program_end")
    prog = prog_engine.get_current_program()
    if prog:
        prog.stop()
    return "ok"

def statusProgram(id):
    """
    Expose the program status
    """
    logging.debug("program_status")
    prog = prog_engine.get_current_program()
    if prog is None:
        prog = Program("")
    return {'name': prog.name, "running": prog.is_running(), "log": prog_engine.get_log()}


## Activities

def saveActivity(id, body):
    activity = body
    activity["id"] = id
    return activities.save(activity)

def saveAsNewActivity(body):
    activity = body
    return activities.save(activity)

def loadActivity(id=None, default=None):
    return activities.load(id, default)

def deleteActivity(id):
    activities.delete(id), 200

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

## Test
def testCoderbot(body):
    return run_test(body.get("tests", []))

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
                        photos_meta=Camera.get_instance().get_photo_list(),
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

def cloudSyncRequest():
    CloudManager.get_instance().sync()
    return {}

def cloudSyncStatus():
    return CloudManager.get_instance().sync_status()

def cloudRegistrationRequest(body):
    CloudManager.get_instance().register(body)
    return {}

def cloudRegistrationDelete():
    CloudManager.get_instance().unregister()
    return {}

def cloudRegistrationStatus():
    registration = Config.read().get("cloud").get('registration', {})
    return {
        "registered": CloudManager.get_instance().registration_status(),
        "name": registration.get('name', ""),
        "description": registration.get('description', ""),
        "org_id": registration.get('org_id', ""),
        "org_name": registration.get('org_name', ""),
        "org_description": registration.get('org_description', "")
    }
