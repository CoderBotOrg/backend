import coderbot
import camera_handler

from flask import Flask, render_template, request

bot = coderbot.CoderBot.get_instance()
camera_handler = camera_handler.CameraReader.get_instance()

app = Flask(__name__,static_url_path="")

@app.route("/")
def home():
    return render_template('control.html', host=request.host[:request.host.find(':')])

@app.route("/blockly")
def blockly():
    return render_template('blockly.html')

@app.route("/bot")
def handle_bot():
    cmd = request.args.get('cmd')
    param = request.args.get('param')
    if cmd == "forward":
        bot.forward(float(param))
    elif cmd == "left":
        bot.left(float(param))
    elif cmd == "right":
        bot.right(float(param))
    elif cmd == "backward":
        bot.backward(float(param))
    elif cmd == "signal_on":
        camera_handler.set_active_handler(1)
        pass
    elif cmd == "signal_off":
        camera_handler.set_active_handler(None)
        pass    
    return "ok"

def run_server():
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
