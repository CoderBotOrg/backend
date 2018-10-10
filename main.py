"""
This module provides the http web server exposing the
CoderBot REST API and static resources
"""
import os
import json
import logging
import logging.handlers
import subprocess
import picamera
import connexion

from coderbot import CoderBot, PIN_PUSHBUTTON
from camera import Camera
from motion import Motion
from audio import Audio
from program import ProgramEngine, Program
from config import Config
from cnn_manager import CNNManager
from event import EventManager
from conversation import Conversation

from flask import (Flask, 
                    render_template, 
                    request, 
                    send_file, 
                    Response, 
                    jsonify,
                    send_from_directory)
from flask_babel import Babel
from flask_cors import CORS
from werkzeug.datastructures import Headers

# Logging configuration
logger = logging.getLogger()
logger.setLevel(logging.WARNING)
sh = logging.StreamHandler()
fh = logging.handlers.RotatingFileHandler('./logs/coderbot.log', maxBytes=1000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(sh)
logger.addHandler(fh)

# Initialisation
global bot
bot = None
cam = None
motion = None
audio = None
cnn = None
event = None
conv = None

# (Connexion) Flask app configuration
connexionApp = connexion.App(__name__, swagger_ui=True, swagger_path='swagger-ui/')
# We serve a custom version of the swagger ui (Jinja2 templates) based on the default one

# New API is defined in v2.yml and its methods are in api.py
connexionApp.add_api('v2.yml')


# Connexion wraps FlaskApp, so app becomes app
app = connexionApp.app
CORS(app) # Access-Control-Allow-Origin
babel = Babel(app)
app.debug = False
app.prog_engine = ProgramEngine.get_instance()
app.prog = None
app.shutdown_requested = False

## Legacy Routes

@babel.localeselector
def get_locale():
    # otherwise try to guess the language from the user accept
    # header the browser transmits.
    loc = request.accept_languages.best_match(['it', 'en', 'fr', 'es'])
    if loc is None:
        loc = 'en'
    return loc

"""
Workaround: serve the 'static' subfolders with 'send_from_directory'
(connexion wrapper ignores `static_url_path`)
"""

@app.route('/css/<path:filename>')
def render_static_assets0(filename):
    return send_from_directory('static/css', filename)

@app.route('/fonts/<path:filename>')
def render_static_assets1(filename):
    return send_from_directory('static/fonts', filename)

@app.route('/images/<path:filename>')
def render_static_assets2(filename):
    return send_from_directory('static/images', filename)

@app.route('/js/<path:filename>')
def render_static_assets3(filename):
    return send_from_directory('static/js', filename)

@app.route('/media/<path:filename>')
def render_static_assets4(filename):
    return send_from_directory('static/media', filename)

# Serve the new Vue application (build)
#  "dist" is the output of `npm run build` from the vue-app repository

@app.route('/vue/<path:filename>')
def render_static_assets5(filename):
    return send_from_directory('dist', filename)

# Serve web app application templates
@app.route("/")
def handle_home():
    return render_template('main.html',
                           host=request.host[:request.host.find(':')],
                           locale=get_locale(),
                           config=app.bot_config,
                           program_level=app.bot_config.get("prog_level", "std"),
                           cam=cam != None,
                           cnn_model_names = json.dumps({}))

# Overwrite configuration file on disk and reload it
@app.route("/config", methods=["POST"])
def handle_config():
    Config.write(request.form)
    app.bot_config = Config.get()
    return "ok"

# Expose configuration as JSON
@app.route("/config", methods=["GET"])
def returnConfig():
    return(jsonify(app.bot_config)) 

# Changes wi-fi configuration and reboot
@app.route("/wifi", methods=["POST"])
def handle_wifi():
    mode = request.form.get("wifi_mode")
    ssid = request.form.get("wifi_ssid")
    psk = request.form.get("wifi_psk")
    logging.info("mode " + mode +" ssid: " + ssid + " psk: " + psk)
    client_params = " \"" + ssid + "\" \"" + psk + "\"" if ssid != "" and psk != "" else ""
    logging.info(client_params)
    os.system("sudo python wifi.py updatecfg " + mode + client_params)
    os.system("sudo reboot")
    if mode == "ap":
        return "http://coder.bot:8080"
    else:
        return "http://coderbot.local:8080"

# Update the system
@app.route("/update", methods=["GET"])
def handle_update():
    logging.info("updating system.start")
    return Response(execute("./scripts/update_coderbot.sh"), mimetype='text/plain')

# Execute single command
@app.route("/bot", methods=["GET"])
def handle_bot():
    cmd = request.args.get('cmd')
    param1 = request.args.get('param1')
    param2 = request.args.get('param2')
    print('/bot',json.dumps(request.args))
    if cmd == "move":
        bot.move(speed=int(param1), elapse=float(param2))
    elif cmd == "turn":
        bot.turn(speed=int(param1), elapse=float(param2))
    elif cmd == "move_motion":
        motion.move(dist=float(param2))
    elif cmd == "turn_motion":
        motion.turn(angle=float(param2))
    elif cmd == "stop":
        bot.stop()
        try:
          motion.stop()
        except:
          logging.warning("Camera not present")
          pass
    elif cmd == "take_photo":
        try:
            cam.photo_take()
            audio.say(app.bot_config.get("sound_shutter"))
        except:
            logging.warning("Camera not present")
            pass
    elif cmd == "video_rec":
        try:
          cam.video_rec()
          audio.say(app.bot_config.get("sound_shutter"))
        except:
          logging.warning("Camera not present")
          pass
    elif cmd == "video_stop":
        try:
          cam.video_stop()
          audio.say(app.bot_config.get("sound_shutter"))
        except:
          logging.warning("Camera not present")
          pass
    elif cmd == "say":
        logging.info("say: " + str(param1) + " in: " + str(get_locale()))
        audio.say(param1, get_locale())

    elif cmd == "halt":
        logging.info("shutting down")
        audio.say(app.bot_config.get("sound_stop"))
        bot.halt()
    elif cmd == "restart":
        logging.info("restarting bot")
        bot.restart()
    elif cmd == "reboot":
        logging.info("rebooting")
        bot.reboot()
    return "ok"

@app.route("/bot/status", methods=["GET"])
def handle_bot_status():
    return json.dumps({'status': 'ok'})

def video_stream(a_cam):
    while not app.shutdown_requested:
        frame = a_cam.get_image_jpeg()
        yield ("--BOUNDARYSTRING\r\n" +
               "Content-type: image/jpeg\r\n" +
               "Content-Length: " + str(len(frame)) + "\r\n\r\n")
        yield frame
        yield "\r\n"

# Render cam stream
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

# Photos
@app.route("/photos", methods=["GET"])
def handle_photos():
    logging.info("photos")
    return json.dumps(cam.get_photo_list())

@app.route("/photos/<filename>", methods=["GET"])
def handle_photo_get(filename):
    logging.info("media filename: " + filename)
    mimetype = {'jpg': 'image/jpeg', 'mp4': 'video/mp4'}
    try:
        media_file = cam.get_photo_file(filename)
        return send_file(media_file, mimetype=mimetype.get(filename[:-3], 'image/jpeg'), cache_timeout=0)
    except picamera.exc.PiCameraError as e:
        logging.error("Error: " + str(e))

@app.route("/photos/<filename>", methods=["PUT"])
def handle_photo_put(filename):
    logging.info("photo update")
    data = request.get_data(as_text=True)
    data = json.loads(data)
    cam.update_photo({"name": filename, "tag":data["tag"]})
    return jsonify({"res":"ok"})

@app.route("/photos/<filename>", methods=["DELETE"])
def handle_photo_cmd(filename):
    logging.debug("photo delete")
    cam.delete_photo(filename)
    return "ok"

# Programs list
@app.route("/program/list", methods=["GET"])
def handle_program_list():
    logging.debug("program_list")
    return json.dumps(app.prog_engine.prog_list())

# Get saved program as JSON
@app.route("/program/load", methods=["GET"])
def handle_program_load():
    logging.debug("program_load")
    name = request.args.get('name')
    app.prog = app.prog_engine.load(name)
    return jsonify(app.prog.as_json())

# Save new program
@app.route("/program/save", methods=["POST"])
def handle_program_save():
    logging.debug("program_save")
    name = request.form.get('name')
    dom_code = request.form.get('dom_code')
    code = request.form.get('code')
    prog = Program(name, dom_code=dom_code, code=code)
    app.prog_engine.save(prog)
    return "ok"

# Delete saved program
@app.route("/program/delete", methods=["POST"])
def handle_program_delete():
    logging.debug("program_delete")
    name = request.form.get('name')
    app.prog_engine.delete(name)
    return "ok"

# Execute the given code
@app.route("/program/exec", methods=["POST"])
def handle_program_exec():
    logging.debug("program_exec")
    name = request.form.get('name')
    code = request.form.get('code')
    app.prog = app.prog_engine.create(name, code)
    return json.dumps(app.prog.execute())

# Stop the execution
@app.route("/program/end", methods=["POST"])
def handle_program_end():
    logging.debug("program_end")
    if app.prog:
        app.prog.end()
    app.prog = None
    return "ok"

# Program status
@app.route("/program/status", methods=["GET"])
def handle_program_status():
    logging.debug("program_status")
    prog = Program("")
    if app.prog:
        prog = app.prog
    return json.dumps({'name': prog.name, "running": prog.is_running(), "log": app.prog_engine.get_log()})

@app.route("/cnnmodels", methods=["GET"])
def handle_cnn_models_list():
    logging.info("cnn_models_list")
    return json.dumps(cnn.get_models())

@app.route("/cnnmodels", methods=["POST"])
def handle_cnn_models_new():
    logging.info("cnn_models_new")
    data = json.loads(request.get_data(as_text=True))
    cnn.train_new_model(model_name=data["model_name"],
                        architecture=data["architecture"],
                        image_tags=data["image_tags"],
                        photos_meta=cam.get_photo_list(),
                        training_steps=data["training_steps"],
                        learning_rate=data["learning_rate"])

    return json.dumps({"name": data["model_name"], "status": 0})

@app.route("/cnnmodels/<model_name>", methods=["GET"])
def handle_cnn_models_status(model_name):
    logging.info("cnn_models_status")
    model_status = cnn.get_models().get(model_name)

    return json.dumps(model_status)

@app.route("/cnnmodels/<model_name>", methods=["DELETE"])
def handle_cnn_models_delete(model_name):
    logging.info("cnn_models_delete")
    model_status = cnn.delete_model(model_name=model_name)

    return json.dumps(model_status)

# Spawn a sub-process and execute things there
def execute(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Poll process for new output until finished
    while True:
        nextline = process.stdout.readline()
        if nextline == '' and process.poll() != None:
            break
        logging.info(nextline)
        yield nextline

def button_pushed():
    if app.bot_config.get('button_func') == "startstop":
        if app.prog and app.prog.is_running():
            app.prog.end()
        elif app.prog and not app.prog.is_running():
            app.prog.execute()

# Finally, get the server running
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

            cnn = CNNManager.get_instance()
            event = EventManager.get_instance("coderbot")
            conv = Conversation.get_instance()

            if app.bot_config.get('load_at_start') and len(app.bot_config.get('load_at_start')):
                app.prog = app.prog_engine.load(app.bot_config.get('load_at_start'))
                app.prog.execute()
        except ValueError as e:
            app.bot_config = {}
            logging.error(e)

        bot.set_callback(PIN_PUSHBUTTON, button_pushed, 100)
        app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False, threaded=True)
    finally:
        if cam:
            cam.exit()
        if bot:
            bot.exit()
        app.shutdown_requested = True
