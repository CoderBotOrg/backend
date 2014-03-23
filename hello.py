from flask import Flask
from flask_sockets import Sockets

app = Flask(__name__)
sockets = Sockets(app)

@sockets.route('/echo')
def echo_socket(ws):
    while True:
        message = ws.receive()
	print(message)
        ws.send(message)

@app.route('/')
def hello():
    return """
<!DOCTYPE html>
<html>
  <head>
    <script type="text/javascript">
       var ws = new WebSocket("ws://192.168.0.129:8000/echo");
       ws.onopen = function() {
           ws.send("socket open");
       };
       ws.onclose = function(evt) {
           alert("socket closed");
       };
       ws.onmessage = function(evt) {
           document.getElementById("log").innerHTML += evt.data;
       }
    </script>
  </head>
  <body>
  <h1>Socket test</h1>
  <button onmousedown="ws.send('mousedown')" onmouseup="ws.send('mouseup');">push me</button>
  <div id="log"><div>
  </body>
</html>
"""

