"""
This is mudule main, which provides the http web server that expose the
CoderBot REST API and static resources (html, js, css, jpg).
"""
import os
import errno
import json
import logging
import logging.handlers
import picamera

from coderbot import CoderBot
from camera import Camera
from motion import Motion
from audio import Audio
from program import Program
from config import Config
from event import EventManager
from conversation import Conversation

from flask import Flask, render_template, request, send_file, Response, jsonify
from flask_babel import Babel
from werkzeug.datastructures import Headers
from flask_cors import CORS

#from flask_sockets import Sockets


from pathlib import Path
import signal


# Status File
def read_statusFile(temp_files_dict):
    tmp_folder_path = temp_files_dict["tmp_folder_path"]
    status_fileName = temp_files_dict["status_fileName"]

    # Load the status file
    with open(tmp_folder_path + status_fileName, "r") as fh:
        try:
            data_coderbotStatus = json.loads(fh.read())
        except Exception as e:
            print("####### JSON ERROR: "+str(e))
            print("####### FILE: "+str(fh.read()))
            print("####### PATH: "+ tmp_folder_path + status_fileName)
            data_coderbotStatus = None
    return data_coderbotStatus

def write_statusFile(data_coderbotStatus, temp_files_dict):
    tmp_folder_path = temp_files_dict["tmp_folder_path"]
    status_fileName = temp_files_dict["status_fileName"]

    # Create the file and if already exists overwites it
    with open(tmp_folder_path + status_fileName + ".tmp", "w") as fh:
        fh.write(json.dumps(data_coderbotStatus))
        os.rename(tmp_folder_path + status_fileName + ".tmp", tmp_folder_path + status_fileName)

def write_prog_gen_commands(command, mode, temp_files_dict):
    tmp_folder_path = temp_files_dict["tmp_folder_path"]
    status_fileName = temp_files_dict["status_fileName"]
    prog_gen_commands_fileName = temp_files_dict["prog_gen_commands_fileName"]

    data_prog_gen_commands = {}
    data_prog_gen_commands["command"] = command
    data_prog_gen_commands["argument"] = mode
    # Create the file and if already exists overwites it
    with open(tmp_folder_path + prog_gen_commands_fileName + ".tmp", "w") as fh:
        fh.write(json.dumps(data_prog_gen_commands))
        os.rename(tmp_folder_path + prog_gen_commands_fileName + ".tmp", tmp_folder_path + prog_gen_commands_fileName)

# Initialize the status file
def initialize_coderbotStatus(temp_files_dict):
    tmp_folder_path = temp_files_dict["tmp_folder_path"]
    status_fileName = temp_files_dict["status_fileName"]
    # The try-except has been used in order to avoid race conditions between the evaulation
    # of the existence of the folder and its creation
    try:
        os.makedirs(tmp_folder_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    # Initial JSON
    default_status = {"ok":True, "prog_gen":{}, "prog_handler":{"mode": "stop"}}
    write_statusFile(default_status, temp_files_dict)



# Evaluates if the datas sent to the /bot endpoint are valid
def eval_endpoint_bot(data):

    ## This dictionary defines how the JSON received should be in order to be considered a legal request.
    ## The constraints defined are: the key names allowed and their respective values types.
    # The constraints not explicitly defined or not defined at all are:
    #  - "cmd" is the only key name allowed
    #  - the dictionary contained in "cmd" must conain only ONE of the keys listed
    #  - these listed keys contains an another dictionary that must contain EXACTLY all the keys listed
    model_apis = {"cmd":{"move":{"param1":"int", "param2":"float"}, "turn":{"param1":"int", "param2":"float"}, "move_motion":{"param2":"float"}, "turn_motion":{"param2":"float"}, "stop":{}, "take_photo":{}, "video_rec":{}, "video_stop":{}, "say":{"param1":"str"}, "halt":{}, "restart":{}, "reboot":{}}}

    ## Example JSONs client->server
    # {"cmd":{"move":{"param1":2, "param2":4.5}}}
    # {"cmd":{"move":{"param2":53.9}}}
    # {"cmd":{"stop":{}}}

    ## Example JSONs server->client
    # {"ok":false,"error_code":400,"description":"JSONDecodeError"}
    # {"ok":true,"description":""}

    # Loading JSON
    try:
        data = json.loads(data)
    except json.decoder.JSONDecodeError: # It's not a JSON
        return {"ok":False,"error_code":400,"description":"JSONDecodeError"}
    except: # Unknown error
        return {"ok":False,"error_code":500,"description":"UnexpectedError on loading the JSON"}

    # Check if there's exactly ONE key
    if not (len(data) == 1):
        return {"ok":False,"error_code":400,"description":"TooMuchParameters"}

    # Check if ALL keys are legal
    if not (set(data.keys()).issubset(model_apis.keys())):
        return {"ok":False,"error_code":400,"description":"IllegalParameter"}
    # Iterate all keys and their content (in this case only ONE)
    for key_1, value_1 in data.items():
        # Check if there's exactly ONE key contained in cmd dict
        if not (len(data[key_1]) == 1):
            return {"ok":False,"error_code":400,"description":"TooMuchParameters"}
        # Check if ALL (in this case ONE) the key(s) contained in cmd are legal
        if not (set(data[key_1].keys()).issubset(model_apis[key_1].keys())):
            return {"ok":False,"error_code":400,"description":"IllegalParameter"}
        # Iterate all key(s) (only ONE) and their content of the dict contained in cmd
        for key_2, value_2 in value_1.items():
            # Check if there's exactly ALL the keys (params) expected
            if not (set(data[key_1][key_2].keys()) == set(model_apis[key_1][key_2].keys())):
                return {"ok":False,"error_code":400,"description":"WrongParameters"}
            # Iterate all parameters and their content
            for key_3, value_3 in value_2.items():
                # Check if all the parameters contains the expected types
                type_expected = model_apis[key_1][key_2][key_3]
                if type_expected == "int":
                    is_correctType_flag = isinstance(value_3, int)
                elif type_expected == "float":
                    is_correctType_flag = isinstance(value_3, float)
                elif type_expected == "str":
                    is_correctType_flag = isinstance(value_3, str)
                else: # It's impossible to enter in this else, but I'll put i'll define this case anyway
                    is_correctType_flag = False
                if not is_correctType_flag:
                    return {"ok":False,"error_code":400,"description":"WrongType"}

    # If the execution arrives until here it means that the JSON passed the test and the evaluation is positive
    return {"ok":True,"description":""}


# Initialize the status file
temp_files_dict = {"tmp_folder_path": "tmp/", "status_fileName": "coderbotStatus_temp.json", "prog_gen_commands_fileName": "coderbotProg_gen_commands_temp.json"}
initialize_coderbotStatus(temp_files_dict)

logger = logging.getLogger()
logger.setLevel(logging.WARNING)

sh = logging.StreamHandler()
# add a rotating handler
fh = logging.handlers.RotatingFileHandler('./logs/coderbot.log', maxBytes=1000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
fh.setFormatter(formatter)

logger.addHandler(sh)
logger.addHandler(fh)

bot = None
cam = None
motion = None
audio = None
cnn = None
event = None
conv = None

app = Flask(__name__, static_url_path="")
#app.config.from_pyfile('coderbot.cfg')
babel = Babel(app)
CORS(app)
app.debug = False
#sockets = Sockets(app)

app.prog = None
app.shutdown_requested = False

@babel.localeselector
def get_locale():
    # otherwise try to guess the language from the user accept
    # header the browser transmits.
    loc = request.accept_languages.best_match(['it', 'en', 'fr', 'es'])
    if loc is None:
        loc = 'en'
    return loc

# Serve legacy web application templates
@app.route("/")
def handle_home():
    return render_template('main.html',
                           host=request.host[:request.host.find(':')],
                           locale=get_locale(),
                           config=app.bot_config,
                           program_level=app.bot_config.get("prog_level", "std"),
                           cam=cam != None,
                           cnn_model_names = json.dumps({}))

# TODO: Refactor the def below
# Execute Actions
def do_endpoint_bot(data):
   response = {"ok":True,"description":""}
   action = list(data["cmd"].keys())[0]
   if action == "move":
      bot.move(speed=data["cmd"][action]["param1"], elapse=data["cmd"][action]["param2"])
   elif action == "turn":
        bot.turn(speed=data["cmd"][action]["param1"], elapse=data["cmd"][action]["param2"])
   elif action == "move_motion":
        motion.move(dist=data["cmd"][action]["param2"])
   elif action == "turn_motion":
        motion.turn(angle=data["cmd"][action]["param2"])
   elif action == "stop":
      bot.stop()
      try:
         motion.stop()
      except:
         logging.warning("Camera not present")
         response = {"ok":False,"error_code":500,"description":"CameraNotPresent"}
   elif action == "take_photo":
      try:
         cam.photo_take()
         audio.say(app.bot_config.get("sound_shutter"))
      except:
         logging.warning("Camera not present")
         response = {"ok":False,"error_code":500,"description":"CameraNotPresent"}
   elif action == "video_rec":
      try:
         cam.video_rec()
         audio.say(app.bot_config.get("sound_shutter"))
      except:
         logging.warning("Camera not present")
         response = {"ok":False,"error_code":500,"description":"CameraNotPresent"}
   elif data["cmd"] == "video_stop":
      try:
         cam.video_stop()
         audio.say(app.bot_config.get("sound_shutter"))
      except:
         logging.warning("Camera not present")
         response = {"ok":False,"error_code":500,"description":"CameraNotPresent"}
   elif action == "say":
      logging.info("say: " + data["cmd"][action]["param1"] + " in: " + str(get_locale()))
      audio.say(data["cmd"][action]["param1"], get_locale())
   elif action == "halt":
      logging.info("shutting down")
      audio.say(app.bot_config.get("sound_stop"))
      bot.halt()
   elif action == "restart":
      logging.info("restarting bot")
      bot.restart()
   elif action == "reboot":
      logging.info("rebooting")
      bot.reboot()
   else:
      response = {"ok":False,"error_code":500,"description":"UnknownFrakingErrorBecauseThisDefNeedsToBeRefactorized"}
   return response

# Send actions to the bot
@app.route("/bot", methods=["POST"])
def controlBot():

    data = request.get_data().decode("utf-8")

    # Evaualte data received and if not legal returns an error response
    evaulation = eval_endpoint_bot(data)
    if not evaulation["ok"]:
        return json.dumps(evaulation), evaulation["error_code"]

    # Execute de validated data and return a positive or error response
    evaulation = do_endpoint_bot(json.loads(data))
    if evaulation["ok"]:
        return json.dumps(evaulation), 200
    else:
        return json.dumps(evaulation), evaulation["error_code"]


# Send actions to the bot (Legacy)
@app.route("/bot", methods=["GET"])
def handle_bot():
    cmd = request.args.get('cmd')
    param1 = request.args.get('param1')
    param2 = request.args.get('param2')
    ## Compatibility layer for the new internal API of the function "executeCommand"
    if not (param1 is None) and not (cmd == "say"):
        param1 = int(param1)
    if not (param2 is None):
        param2 = float(param2)
    data = {"cmd":{cmd:{"param1":param1, "param2":param2}}}
    ####
    do_endpoint_bot(data)
    return "OK"

@app.route("/bot/status", methods=["GET"])
def handle_bot_status():

    # Load the status file
    data_coderbotStatus = read_statusFile(temp_files_dict)

    # Check if the generated program is running
    if data_coderbotStatus["prog_gen"]:
        # Not guaranteed to get the currentBlockId, for example during the whole "loading" status and the early part of "running" status" it can be None
        currentBlockId = data_coderbotStatus["prog_gen"]["currentBlockId"]
        progStatus = data_coderbotStatus["prog_gen"]["status"]
    else:
        currentBlockId = None
        progStatus = "notRunning"
    # TODO: Change the APIs below
    # Proposed new API response: {'ok': True, "result":{'blockId': currentBlockId, 'progStatus': progStatus}}
    return json.dumps({'status': 'ok', 'blockId': currentBlockId, 'progStatus': progStatus})

def video_stream(a_cam):
    while not app.shutdown_requested:
        frame = a_cam.get_image_jpeg()
        yield ("--BOUNDARYSTRING\r\n" +
               "Content-type: image/jpeg\r\n" +
               "Content-Length: " + str(len(frame)) + "\r\n\r\n")
        yield frame
        yield "\r\n"

@app.route("/video/stream")
def handle_video_stream():
    try:
        h = Headers()
        h.add('Age', 0)
        h.add('Cache-Control', 'no-cache, private')
        h.add('Pragma', 'no-cache')
        return Response(video_stream(cam), headers=h, mimetype="multipart/x-mixed-replace; boundary=--BOUNDARYSTRING")
    except:
        pass



@app.route("/program/exec", methods=["POST"])
def handle_program_exec():
    logging.debug("program_exec")
    code = request.form.get('code')
    mode = request.form.get('mode')


    # Load the status file
    data_coderbotStatus = read_statusFile(temp_files_dict)

    # if read_statusFile(temp_files_dict) returns None type, a reboot is needed
    if data_coderbotStatus is None:
        return json.dumps({"ok":False, "error_code":"coderbotStatusJsonError"}), 500


    if data_coderbotStatus["prog_handler"]["mode"] != "stop":
        prog_gen_pid = int(data_coderbotStatus["prog_gen"]["pid"])
        try:
            os.kill(prog_gen_pid, 0)
        except OSError:
            prog_gen_is_up = False
        else:
            prog_gen_is_up = True
        if not prog_gen_is_up:
            data_coderbotStatus["prog_gen"] = {}
            data_coderbotStatus["prog_handler"]["mode"] = "stop"
            write_statusFile(data_coderbotStatus, temp_files_dict)

    if data_coderbotStatus["prog_handler"]["mode"] == "stop":
        data_coderbotStatus["prog_handler"]["mode"] = mode
        write_statusFile(data_coderbotStatus, temp_files_dict)
        evaulation = Program.run(code, mode, temp_files_dict)
    else: # data_coderbotStatus["prog_handler"]["mode"] == "stepByStep" or "fullExec"
        if mode == "stop":
            signal_to_program = signal.SIGTERM
        else: #else mode == "fullExec" or mode == stepByStep"
            write_prog_gen_commands("change_mode", mode, temp_files_dict)
            signal_to_program = signal.SIGUSR1

        try:
            os.kill(prog_gen_pid, signal_to_program)
        except Exception as err:
            # The process in reality was already terminated, probably because of some crash or the previous program unexpectedly terminated after the "data_coderbotStatus" dict
            # has been retrieved from the file (this last case is really unlikely to happen).
            print("######### error: "+str(err))

        evaulation = {"ok":True,"description":""}

    # Returns a positive or error response
    if evaulation["ok"]:
        return json.dumps(evaulation), 200
    else:
        return json.dumps(evaulation), evaulation["error_code"]


#def button_pushed():
#    if app.bot_config.get('button_func') == "startstop":
#        if app.prog and app.prog.is_running():
#            app.prog.end()
#        elif app.prog and not app.prog.is_running():
#            app.prog.execute()

def run_server():
    global bot
    global cam
    global motion
    global audio
    global cnn
    global conv
    global event
    try:
        try:
            app.bot_config = Config.read()
            bot = CoderBot.get_instance(servo=(app.bot_config.get("move_motor_mode") == "servo"),
                                        motor_trim_factor=float(app.bot_config.get('move_motor_trim', 1.0)))
            audio = Audio.get_instance()
            audio.say(app.bot_config.get("sound_start"))
            try:
                cam = Camera.get_instance()
                motion = Motion.get_instance()
            except picamera.exc.PiCameraError:
                logging.error("Camera not present")

            event = EventManager.get_instance("coderbot")
            conv = Conversation.get_instance()

        except ValueError as e:
            app.bot_config = {}
            logging.error(e)

        #bot.set_callback(PIN_PUSHBUTTON, button_pushed, 100)
        app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False, threaded=True)
    finally:
        if cam:
            cam.exit()
        if bot:
            bot.exit()
        app.shutdown_requested = True
