import os
import json

from coderbot import CoderBot
from camera import Camera
from program import ProgramEngine, Program

from flask import Flask, render_template, request
#from flask_sockets import Sockets

bot = CoderBot.get_instance()
cam = Camera.get_instance()

app = Flask(__name__,static_url_path="")
app.debug = True
#sockets = Sockets(app)

app.prog_engine = ProgramEngine.get_instance()

@app.route("/")
def handle_home():
    return render_template('control.html', host=request.host[:request.host.find(':')])

@app.route("/program")
def handle_program():
    return render_template('program.html', host=request.host[:request.host.find(':')])

@app.route("/bot", methods=["GET"])
def handle_bot():
    cmd = request.args.get('cmd')
    param = request.args.get('param')

    if cmd == "forward":
        bot.forward(elapse=float(param))
    elif cmd == "left":
        bot.left(elapse=float(param))
    elif cmd == "right":
        bot.right(elapse=float(param))
    elif cmd == "backward":
        bot.backward(elapse=float(param))
    elif cmd == "stop":
        bot.stop()
    elif cmd == "set_handler":
        print "param: " + str(param)
        try:
          handler = int(param) if int(param) >= 0 else None
          cam_h.set_active_handler(handler)      
        except e:
          print e 

    elif cmd == "say":
        print "say: " + str(param)
	bot.say(param)

    return "ok"

   
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

"""
@sockets.route('/bot_ws')
def bot_ws(ws):
  while True:
    m = ws.receive()
    print m
    if m == "forward":
      bot.forward()
    if m == "backward":
      bot.backward()
    if m == "left":
      bot.left()
    if m == "right":
      bot.right()
    elif m == "stop":
      bot.stop()

cam_h = camera.CameraHandler.get_instance()

def init():
  cam_h.add_handler(camera.SimpleHandler())
  cam_h.add_handler(signal.SignalHandler(coderbot.CoderBot.get_instance()))
  cam_h.add_handler(logo.LogoHandler("coderdojo-logo.png", coderbot.CoderBot.get_instance()))
  cam_h.set_active_handler(None)
  cam_h.start()

init()
"""

def run_server():
  app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)
