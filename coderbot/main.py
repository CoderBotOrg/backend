"""
This module provides the http web server exposing the
CoderBot REST API and static resources
"""
import os
import logging
import logging.handlers
import picamera
import connexion

from connexion.options import SwaggerUIOptions
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware

from camera import Camera
from motion import Motion
from audio import Audio
from program import ProgramEngine
from config import Config
from cnn.cnn_manager import CNNManager
from event import EventManager
from coderbot import CoderBot

# Logging configuration
logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))

## (Connexion) Flask app configuration

# Serve a custom version of the swagger ui (Jinja2 templates) based on the default one
#  from the folder 'swagger-ui'. Clone the 'swagger-ui' repository inside the backend folder
swagger_ui_options = SwaggerUIOptions(swagger_ui=True)
app = connexion.App(__name__, swagger_ui_options=swagger_ui_options)
app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.prog_engine = ProgramEngine.get_instance()

## New API and web application

# API v1 is defined in v1.yml and its methods are in api.py
app.add_api('v1.yml')

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
            bot = CoderBot.get_instance(motor_trim_factor=float(app.bot_config.get('move_motor_trim', 1.0)),
                                        motor_max_power=int(app.bot_config.get('motor_max_power', 100)),
                                        motor_min_power=int(app.bot_config.get('motor_min_power', 0)),
                                        hw_version=app.bot_config.get('hardware_version'),
                                        pid_params=(float(app.bot_config.get('pid_kp', 1.0)),
                                            float(app.bot_config.get('pid_kd', 0.1)),
                                            float(app.bot_config.get('pid_ki', 0.01)),
                                            float(app.bot_config.get('pid_max_speed', 200)),
                                            float(app.bot_config.get('pid_sample_time', 0.01))),
                                        from_defaults=False)

            try:
                audio_device = Audio.get_instance()
                audio_device.set_volume(int(app.bot_config.get('audio_volume_level')), 100)
                audio_device.say(app.bot_config.get("sound_start"))
            except Exception:
                logging.warning("Audio not present")

            try:
                logging.info("starting camera")
                cam = Camera.get_instance()
                Motion.get_instance()
            except picamera.exc.PiCameraError:
                logging.warning("Camera not present")

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

        app.run(host="0.0.0.0", port=5000)
    finally:
        if cam:
            cam.exit()
        if bot:
            bot.exit()

if __name__ == "__main__":
    run_server()