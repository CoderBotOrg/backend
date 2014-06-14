import os
import json

from coderbot import CoderBot
from camera import Camera
from program import ProgramEngine, Program

from flask import Flask, render_template, request
from flask.ext.babel import Babel
#from flask_sockets import Sockets

CONFIG_FILE = "coderbot.cfg"

bot = CoderBot.get_instance()
cam = Camera.get_instance()

app = Flask(__name__,static_url_path="")
#app.config.from_pyfile('coderbot.cfg')
babel = Babel(app)
app.debug = True
#sockets = Sockets(app)

app.prog_engine = ProgramEngine.get_instance()

@babel.localeselector
def get_locale():
    # otherwise try to guess the language from the user accept
    # header the browser transmits.
    return request.accept_languages.best_match(['it', 'en'])

@app.route("/")
def handle_home():
    return render_template('main.html', host=request.host[:request.host.find(':')], stream_port=cam.stream_port, locale = get_locale(), config=app.bot_config, program_level=app.bot_config.get("prog_level", "std"))

@app.route("/config", methods=["POST"])
def handle_config():
    app.bot_config = request.form
    f = open(CONFIG_FILE, 'w')
    json.dump(app.bot_config, f)
    print str(app.bot_config)
    return "ok";

@app.route("/bot", methods=["GET"])
def handle_bot():
    cmd = request.args.get('cmd')
    param1 = request.args.get('param1')
    param2 = request.args.get('param2')

    if cmd == "forward":
        bot.forward(speed=int(param1), elapse=float(param2))
    elif cmd == "left":
        bot.left(speed=int(param1), elapse=float(param2))
    elif cmd == "right":
        bot.right(speed=int(param1), elapse=float(param2))
    elif cmd == "backward":
        bot.backward(speed=int(param1), elapse=float(param2))
    elif cmd == "stop":
        bot.stop()
    elif cmd == "set_handler":
        print "param: " + str(param1)
        try:
          handler = int(param1) if int(param1) >= 0 else None
          cam_h.set_active_handler(handler)      
        except e:
          print e 

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

   
@app.route("/program/list", methods=["GET"])
def handle_program_list():
    print "program_list"
    return json.dumps(app.prog_engine.list())

@app.route("/program/load", methods=["GET"])
def handle_program_load():
    print "program_load"
    name = request.args.get('name')
    return app.prog_engine.load(name).dom_code

@app.route("/program/save", methods=["POST"])
def handle_program_save():
    print "program_save"
    name = request.form.get('name')
    dom_code = request.form.get('dom_code')
    prog = Program(name, dom_code = dom_code)
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
    app.prog = Program(name, code)
    return json.dumps(app.prog.execute())

@app.route("/program/end", methods=["POST"])
def handle_program_end():
    print "program_end"
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

def run_server():
  f = open(CONFIG_FILE, 'r')
  try:
    app.bot_config = json.load(f)
  except ValueError as e:
    app.bot_config = {}
    print e

  bot.say(app.bot_config.get("sound_start"))
  app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)
