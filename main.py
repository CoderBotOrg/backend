############################################################################
#    CoderBot, a didactical programmable robot.
#    Copyright (C) 2014, 2015 Roberto Previtera <info@coderbot.org>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
############################################################################

import os
import json
import logging
import time
import logging.handlers
import subprocess
import picamera

from coderbot import CoderBot, PIN_PUSHBUTTON
from camera import Camera
from motion import Motion
from audio import Audio
from program import ProgramEngine, Program
from config import Config

from flask import Flask, render_template, request, send_file, redirect, Response
from flask.ext.babel import Babel
#from flask_sockets import Sockets

logger = logging.getLogger()
logger.setLevel(logging.INFO)
 
# add a rotating handler
handler = logging.handlers.RotatingFileHandler('logs/coderbot.log', maxBytes=1000000, backupCount=5)
logger.addHandler(handler)

bot = None
cam = None
motion = None
audio = None

app = Flask(__name__,static_url_path="")
#app.config.from_pyfile('coderbot.cfg')
babel = Babel(app)
app.debug = False
#sockets = Sockets(app)

app.prog_engine = ProgramEngine.get_instance()
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

@app.route("/")
def handle_home():
    stream_port = cam.stream_port if cam else "" 
    return render_template('main.html', host=request.host[:request.host.find(':')], stream_port=stream_port, locale = get_locale(), config=app.bot_config, program_level=app.bot_config.get("prog_level", "std"), cam=cam!=None)

@app.route("/config", methods=["POST"])
def handle_config():
    Config.write(request.form)
    app.bot_config = Config.get()
    return "ok";

@app.route("/wifi", methods=["POST"])
def handle_wifi():
    mode = request.form.get("wifi_mode")
    ssid = request.form.get("wifi_ssid")
    psk = request.form.get("wifi_psk")
    logging.info( "mode ", mode, " ssid: ", ssid, " psk: ", psk)
    client_params = " \"" + ssid + "\" \"" + psk + "\"" if ssid != "" and psk != "" else ""
    logging.info(client_params)
    os.system("sudo python wifi.py updatecfg " + mode + client_params)
    if mode == "ap":
      return "http://coder.bot:8080";
    else:
      return "http://coderbotsrv.appspot.com/"

@app.route("/update", methods=["GET"])
def handle_update():
   logging.info("updating system.start")
   return Response(execute("./scripts/update_coderbot.sh"), mimetype='text/plain')

@app.route("/bot", methods=["GET"])
def handle_bot():
    cmd = request.args.get('cmd')
    param1 = request.args.get('param1')
    param2 = request.args.get('param2')

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
    logging.info( "bot_status" )
    return json.dumps({'status': 'ok'}) 

def video_stream(cam):
    refresh_timeout = float(app.bot_config.get("camera_refresh_timeout", "0.1")) 
    while not app.shutdown_requested:
        last_refresh_time = time.time()
        frame = cam.get_image_jpeg()
        yield ("--BOUNDARYSTRING\r\n" +
               "Content-type: image/jpeg\r\n" +
               "Content-Length: " + str(len(frame)) + "\r\n\r\n" +
               frame + "\r\n")
        now = time.time()
        if now - last_refresh_time < refresh_timeout:
            time.sleep(refresh_timeout - (now - last_refresh_time))

@app.route("/video")
def handle_video():
    return """
<html>
<head>
<style type=text/css>
    body { background-image: url(/video/stream); background-repeat:no-repeat; background-position:center top; background-attachment:fixed; height:100% }
</style>
</head>
<body>
&nbsp;
</body>
</html>
"""

@app.route("/video/stream")
def handle_video_stream():
    try:
        return Response(video_stream(cam), mimetype="multipart/x-mixed-replace; boundary=--BOUNDARYSTRING")
    except: pass

@app.route("/photos", methods=["GET"])
def handle_photos():
    logging.info("photos")
    return json.dumps(cam.get_photo_list())

@app.route("/photos/<filename>", methods=["GET"])
def handle_photo(filename):
    logging.info("photo")
    mimetype = {'jpeg': 'image/jpeg', 'h264': 'video/mp4'}
    video = None
    try:
      video = cam.get_photo_file(filename)
    except picamera.exc.PiCameraError:
      pass

    return send_file(video, mimetype.get(filename[:-3],'image'), cache_timeout=0)

@app.route("/photos/<filename>", methods=["POST"])
def handle_photo_cmd(filename):
    logging.debug("photo delete")
    cam.delete_photo(filename)
    return "ok"

@app.route("/photos/<filename>/thumb", methods=["GET"])
def handle_photo_thumb(filename):
    logging.debug("photo_thumb")
    return send_file(cam.get_photo_thumb_file(filename))
   
@app.route("/program/list", methods=["GET"])
def handle_program_list():
    logging.debug("program_list")
    return json.dumps(app.prog_engine.list())

@app.route("/program/load", methods=["GET"])
def handle_program_load():
    logging.debug("program_load")
    name = request.args.get('name')
    app.prog = app.prog_engine.load(name)
    return app.prog.dom_code

@app.route("/program/save", methods=["POST"])
def handle_program_save():
    logging.debug("program_save")
    name = request.form.get('name')
    dom_code = request.form.get('dom_code')
    code = request.form.get('code')
    prog = Program(name, dom_code = dom_code, code = code)
    app.prog_engine.save(prog)
    return "ok"

@app.route("/program/delete", methods=["POST"])
def handle_program_delete():
    logging.debug("program_delete")
    name = request.form.get('name')
    app.prog_engine.delete(name)
    return "ok"

@app.route("/program/exec", methods=["POST"])
def handle_program_exec():
    logging.debug("program_exec")
    name = request.form.get('name')
    code = request.form.get('code')
    app.prog = app.prog_engine.create(name, code)
    return json.dumps(app.prog.execute())

@app.route("/program/end", methods=["POST"])
def handle_program_end():
    logging.debug("program_end")
    if app.prog:
        app.prog.end()
    app.prog = None  
    return "ok"

@app.route("/program/status", methods=["GET"])
def handle_program_status():
    logging.debug("program_status")
    prog = Program("")
    if app.prog:
      prog = app.prog
    return json.dumps({'name': prog.name, "running": prog.is_running()}) 

@app.route("/tutorial")
def handle_tutorial():
    return redirect("/blockly-tutorial/apps/index.html", code=302)

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

def run_server():
  global bot
  global cam
  global motion
  global audio
  try:
    try:
      app.bot_config = Config.read()
      bot = CoderBot.get_instance(servo=(app.bot_config.get("move_motor_mode")=="servo"), motor_trim_factor=float(app.bot_config.get('move_motor_trim', 1.0)))
      audio = Audio.get_instance()
      audio.say(app.bot_config.get("sound_start"))
      try:
	cam = Camera.get_instance()
        #motion = Motion.get_instance()
      except picamera.exc.PiCameraError:
        logging.error("Camera not present")
      
      if app.bot_config.get('load_at_start') and len(app.bot_config.get('load_at_start')):
        app.prog = app.prog_engine.load(app.bot_config.get('load_at_start'))
        app.prog.execute()
    except ValueError as e:
      app.bot_config = {}
      logging.error(e)

    bot.set_callback(PIN_PUSHBUTTON, button_pushed, 100)
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False, threaded=True)
  finally:
    if cam:
      cam.exit()
    if bot:
      bot.exit()
    app.shutdown_requested = True
