import os
import json

from coderbot import CoderBot, PIN_PUSHBUTTON
from camera import Camera
from motion import Motion
from program import ProgramEngine, Program
from config import Config

from flask import Flask, render_template, request, send_file, redirect
from flask.ext.babel import Babel
#from flask_sockets import Sockets

bot = None
cam = None
motion = None

app = Flask(__name__,static_url_path="")
#app.config.from_pyfile('coderbot.cfg')
babel = Babel(app)
app.debug = True
#sockets = Sockets(app)

app.prog_engine = ProgramEngine.get_instance()
app.prog = None

@babel.localeselector
def get_locale():
    # otherwise try to guess the language from the user accept
    # header the browser transmits.
    loc = request.accept_languages.best_match(['it', 'en'])
    if loc is None:
      loc = 'it'
    return loc

@app.route("/")
def handle_home():
    return render_template('main.html', host=request.host[:request.host.find(':')], stream_port=cam.stream_port, locale = get_locale(), config=app.bot_config, program_level=app.bot_config.get("prog_level", "std"))

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
    print "mode ", mode, " ssid: ", ssid, " psk: ", psk
    client_params = " \"" + ssid + "\" \"" + psk + "\"" if ssid != "" and psk != "" else ""
    print client_params
    os.system("sudo python wifi.py updatecfg " + mode + client_params)
    if mode == "ap":
      return "http://coder.bot:8080";
    else:
      return "http://coderbotsrv.appspot.com/"

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
    elif cmd == "take_photo":
        cam.photo_take()
        bot.say(app.bot_config.get("sound_shutter"))
    elif cmd == "video_rec":
        cam.video_rec()
        bot.say(app.bot_config.get("sound_shutter"))
    elif cmd == "video_stop":
        cam.video_stop()
        bot.say(app.bot_config.get("sound_shutter"))

    elif cmd == "say":
        print "say: " + str(param1)
	bot.say(param1)

    elif cmd == "halt":
        print "shutting down"
        bot.say(app.bot_config.get("sound_stop"))
	bot.halt()

    return "ok"

@app.route("/bot/status", methods=["GET"])
def handle_bot_status():
    print "bot_status"
    return json.dumps({'status': 'ok'}) 

@app.route("/photos", methods=["GET"])
def handle_photos():
    print "photos"
    return json.dumps(cam.get_photo_list())

@app.route("/photos/<filename>", methods=["GET"])
def handle_photo(filename):
    print "photo"
    mimetype = {'jpeg': 'image/jpeg', 'h264': 'video/mp4'}
    video = None
    try:
      video = cam.get_photo_file(filename)
    except:
      pass

    return send_file(video, mimetype.get(filename[:-3],'image'), cache_timeout=0)

@app.route("/photos/<filename>", methods=["POST"])
def handle_photo_cmd(filename):
    print "photo delete"
    cam.delete_photo(filename)
    return "ok"

@app.route("/photos/<filename>/thumb", methods=["GET"])
def handle_photo_thumb(filename):
    print "photo_thumb"
    return send_file(cam.get_photo_thumb_file(filename))
   
@app.route("/program/list", methods=["GET"])
def handle_program_list():
    print "program_list"
    return json.dumps(app.prog_engine.list())

@app.route("/program/load", methods=["GET"])
def handle_program_load():
    print "program_load"
    name = request.args.get('name')
    app.prog = app.prog_engine.load(name)
    return app.prog.dom_code

@app.route("/program/save", methods=["POST"])
def handle_program_save():
    print "program_save"
    name = request.form.get('name')
    dom_code = request.form.get('dom_code')
    code = request.form.get('code')
    prog = Program(name, dom_code = dom_code, code = code)
    app.prog_engine.save(prog)
    return "ok"

@app.route("/program/delete", methods=["POST"])
def handle_program_delete():
    print "program_delete"
    name = request.form.get('name')
    app.prog_engine.delete(name)
    return "ok"

@app.route("/program/exec", methods=["POST"])
def handle_program_exec():
    print "program_exec"
    name = request.form.get('name')
    code = request.form.get('code')
    app.prog = app.prog_engine.create(name, code)
    return json.dumps(app.prog.execute())

@app.route("/program/end", methods=["POST"])
def handle_program_end():
    print "program_end"
    if app.prog:
        app.prog.end()
    app.prog = None  
    return "ok"

@app.route("/program/status", methods=["GET"])
def handle_program_status():
    print "program_status"
    prog = Program("")
    if app.prog:
      prog = app.prog
    return json.dumps({'name': prog.name, "running": prog.is_running()}) 

@app.route("/tutorial")
def handle_tutorial():
    return redirect("/blockly-tutorial/apps/index.html", code=302)

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
  try:
    app.bot_config = Config.read()
    bot = CoderBot.get_instance(servo=(app.bot_config.get("move_motor_mode")=="servo"))
    cam = Camera.get_instance()
    motion = Motion.get_instance()
  except ValueError as e:
    app.bot_config = {}
    print e
  if app.bot_config.get('load_at_start') and len(app.bot_config.get('load_at_start')):
    app.prog = app.prog_engine.load(app.bot_config.get('load_at_start'))

  bot.set_callback(PIN_PUSHBUTTON, button_pushed, 100)
  bot.say(app.bot_config.get("sound_start"))
  app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)
