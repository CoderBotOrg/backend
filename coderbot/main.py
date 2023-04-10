"""
This module provides the http web server exposing the
CoderBot REST API and static resources
"""
import os
import logging
import logging.handlers
import picamera
import connexion

from flask_cors import CORS

from camera import Camera
from motion import Motion
from audio import Audio
from program import ProgramEngine
from config import Config
from cnn.cnn_manager import CNNManager
from event import EventManager
from coderbot import CoderBot
from cloud import CloudManager

# Logging configuration
logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))
# sh = logging.StreamHandler()
# formatter = logging.Formatter('%(message)s')
# sh.setFormatter(formatter)
# logger.addHandler(sh)

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

# Finally, get the server running
def run_server():
    bot = None
    cam = None
    try:
        try:
            app.bot_config = Config.read()

            bot = CoderBot.get_instance()

            try:
                audio_device = Audio.get_instance()
                audio_device.set_volume(int(app.bot_config.get('audio_volume_level')), 100)
                audio_device.say(app.bot_config.get("sound_start"))
            except Exception:
                logging.warning("Audio not present")

            try:
                cam = Camera.get_instance()
                Motion.get_instance()
            except picamera.exc.PiCameraError:
                logging.warning("Camera not present")

            CNNManager.get_instance()
            EventManager.get_instance("coderbot")

            if app.bot_config.get('load_at_start') and app.bot_config.get('load_at_start'):
                prog = app.prog_engine.load(app.bot_config.get('load_at_start'))
                prog.execute()

            CloudManager.get_instance()
            
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
