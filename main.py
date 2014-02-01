from flask import Flask, render_template, request

import coderbot
app = Flask(__name__,static_url_path="")
bot = coderbot.CoderBot()

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
    return "ok"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
