import coderbot
import signal_reader

from flask import Flask, render_template, request

bot = coderbot.CoderBot.get_instance()
reader = signal_reader.SignalReader.get_instance()

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
        reder.start()
        pass
    elif cmd == "signal_off":
        reader.stop()
        pass    
    return "ok"

def run_server():
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
