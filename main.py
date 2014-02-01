from flask import Flask, render_template

import coderbot
app = Flask(__name__,static_url_path="")
bot = coderbot.CoderBot()

@app.route("/")
def home():
    return render_template('control.html')

@app.route("/bot")
def bot():
    cmd = self.request.get('cmd')
    param = self.request.get('param')
    if cmd == "forward":
        bot.forward(float(param))
    elif cmd == "left":
        bot.left(float(param))
    elif cmd == "right":
        bot.right(float(param))
    elif cmd == "left":
        bot.backward(float(param))
    return

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
