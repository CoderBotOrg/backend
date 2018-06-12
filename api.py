import os
import json
import logging
import logging.handlers
import subprocess
import picamera

from coderbot import CoderBot, PIN_PUSHBUTTON
from camera import Camera
from motion import Motion
from audio import Audio
from program import ProgramEngine, Program
from config import Config
from cnn_manager import CNNManager
from event import EventManager
from conversation import Conversation

from flask import Flask, render_template, request, send_file, Response, jsonify, Blueprint
from flask_babel import Babel
from flask_cors import CORS
from werkzeug.datastructures import Headers
import connexion

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

#app = Flask(__name__, static_url_path="")
app = connexion.App(__name__, static_url_path="", specification_dir='./')
app.add_api('swagger.yml')

CORS(app.app)
babel = Babel(app.app)
app.app.debug = False
app.app.prog_engine = ProgramEngine.get_instance()
app.app.prog = None
app.app.shutdown_requested = False


#@app.route("/v2/stop", methods=["GET"])
def stop():
    return jsonify('ok')

def button_pushed():
    if app.app.bot_config.get('button_func') == "startstop":
        if app.app.prog and app.app.prog.is_running():
            app.app.prog.end()
        elif app.app.prog and not app.app.prog.is_running():
            app.app.prog.execute()

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
            app.app.bot_config = Config.read()
            bot = CoderBot.get_instance(servo=(app.app.bot_config.get("move_motor_mode") == "servo"),
                                        motor_trim_factor=float(app.app.bot_config.get('move_motor_trim', 1.0)))
            audio = Audio.get_instance()
            audio.say(app.app.bot_config.get("sound_start"))
            try:
                cam = Camera.get_instance()
                motion = Motion.get_instance()
            except picamera.exc.PiCameraError:
                logging.error("Camera not present")

            cnn = CNNManager.get_instance()
            event = EventManager.get_instance("coderbot")
            conv = Conversation.get_instance()

            if app.app.bot_config.get('load_at_start') and len(app.app.bot_config.get('load_at_start')):
                app.app.prog = app.app.prog_engine.load(app.app.bot_config.get('load_at_start'))
                app.app.prog.execute()
        except ValueError as e:
            app.app.bot_config = {}
            logging.error(e)

        bot.set_callback(PIN_PUSHBUTTON, button_pushed, 100)
        app.run(host="0.0.0.0", port=8081, debug=True, use_reloader=True, threaded=True)
    finally:
        if cam:
            cam.exit()
        if bot:
            bot.exit()
        app.app.shutdown_requested = True

run_server()