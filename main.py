import signal_reader
import coderbot

from flask import Flask, render_template, request

signal = signal_reader.SignalReader()
bot = coderbot.CoderBot()

app = Flask(__name__,static_url_path="")

@app.route("/")
def home():
    return render_template('control.html')

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
        signal.start()
    elif cmd == "signal_off":
        signal.stop()    
    return "ok"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
