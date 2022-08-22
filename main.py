"""
This module provides the http web server exposing the
CoderBot REST API and static resources
"""
import os
import logging
import logging.handlers
import subprocess
import picamera
import connexion

from flask import (send_from_directory, redirect)

from flask_cors import CORS

from coderbot import CoderBot
from camera import Camera
from motion import Motion
from audio import Audio
from program import ProgramEngine, Program
from config import Config
from cnn_manager import CNNManager
from event import EventManager
from audioControls import AudioCtrl

# Logging configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
fh = logging.handlers.RotatingFileHandler('./logs/coderbot.log', maxBytes=1000000, backupCount=5)
formatter = logging.Formatter('%(message)s')
sh.setFormatter(formatter)
fh.setFormatter(formatter)
#logger.addHandler(sh)
logger.addHandler(fh)

## (Connexion) Flask app configuration

# Serve a custom version of the swagger ui (Jinja2 templates) based on the default one
#  from the folder 'swagger-ui'. Clone the 'swagger-ui' repository inside the backend folder
options = {"swagger_ui": False}
connexionApp = connexion.App(__name__, options=options)

# Connexion wraps FlaskApp, so app becomes connexionApp.app
app = connexionApp.app
# Access-Control-Allow-Origin
CORS(app)
app.debug = False
app.prog_engine = ProgramEngine.get_instance()

## New API and web application

# API v1 is defined in v1.yml and its methods are in api.py
connexionApp.add_api('v1.yml')

@app.route('/vue/<path:filename>')
def serve_vue_app(filename):
    """
    Serve (a build of) the new Vue application
    "dist" is the output of `npm run build` from the 'vue-app' repository
    """
    return send_from_directory('dist', filename)

@app.route('/docs/')
def redirect_docs_app():
    return redirect('/docs/index.html', code=302)

@app.route('/docs/<path:subpath>')
def serve_docs_app(subpath):
    """
    Serve (a build of) the documentation
    'cb_docs' is the output of `npx vuepress build pages/`
    from the 'docs' repository
    """
    if (subpath[-1] == '/'):
        subpath = subpath + 'index.html'
    return send_from_directory('cb_docs', subpath)

@app.route('/')
def redirect_vue_app():
    return redirect('/vue/index.html', code=302)


def button_pushed():
    if app.bot_config.get('button_func') == "startstop":
        prog = app.prog_engine.get_current_prog()
        if prog and prog.is_running():
            prog.end()
        elif prog and not prog.is_running():
            prog.execute()

def remove_doreset_file():
    try:
        os.remove("/home/pi/doreset")
    except OSError:
        pass

def align_wifi_config():
    if app.bot_config["wifi_ssid"] == "coderbot_CHANGEMEATFIRSTRUN":
        out = os.popen("sudo ./wifi.py getcfg --ssid").read()
        if "coderbot_" in out:
            app.bot_config["wifi_ssid"] = out.split()[0]
            Config.write(app.bot_config)
            app.bot_config = Config.get()

# Finally, get the server running
def run_server():
    bot = None
    cam = None
    try:
        try:
            app.bot_config = Config.read()
            align_wifi_config()
            bot = CoderBot.get_instance(motor_trim_factor=float(app.bot_config.get('move_motor_trim', 1.0)),
                                        hw_version=app.bot_config.get('hardware_version'))
            audio = Audio.get_instance()
            audio.say(app.bot_config.get("sound_start"))

            try:
                audioCtrl = AudioCtrl.get_instance()
                audioCtrl.setVolume(int(app.bot_config.get('audio_volume_level')))
            except Exception as e:
                logging.warning("error initialising AudioCtrl: %s", str(e))

            try:
                cam = Camera.get_instance()
                Motion.get_instance()
            except picamera.exc.PiCameraError:
                logging.error("Camera not present")

            CNNManager.get_instance()
            EventManager.get_instance("coderbot")

            if app.bot_config.get('load_at_start') and app.bot_config.get('load_at_start'):
                prog = app.prog_engine.load(app.bot_config.get('load_at_start'))
                prog.execute()
        except ValueError as e:
            app.bot_config = {}
            logging.error(e)

        bot.set_callback(bot.GPIOS.PIN_PUSHBUTTON, button_pushed, 100)

        remove_doreset_file()

        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False, threaded=True)
    finally:
        if cam:
            cam.exit()
        if bot:
            bot.exit()

if __name__ == "__main__":
    run_server()
