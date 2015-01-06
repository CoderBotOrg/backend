from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import ThreadingMixIn, TCPServer
import threading
import time
import re
import socket
import numpy as np
import cv2
import colorsys
import camera as cam
import copy

_jpegstreamers = {}
class JpegStreamHandler(SimpleHTTPRequestHandler):
    """
    The JpegStreamHandler handles requests to the threaded HTTP server.
    Once initialized, any request to this port will receive a multipart/replace
    jpeg.
    """


    def do_GET(self):
        global _jpegstreamers


        if (self.path == "/" or not self.path):


            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("""
<html>
<head>
<style type=text/css>
    body { background-image: url(/stream); background-repeat:no-repeat; background-position:center top; background-attachment:fixed; height:100% }
</style>
</head>
<body>
&nbsp;
</body>
</html>
            """)
            return


        elif (self.path == "/stream"):
            self.send_response(200)
            self.send_header("Connection", "close")
            self.send_header("Max-Age", "0")
            self.send_header("Expires", "0")
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=--BOUNDARYSTRING")
            self.end_headers()
            (host, port) = self.server.socket.getsockname()[:2]


            count = 0
            timeout = 0.75
            lasttimeserved = 0
            while (1):
                if True: #(_jpegstreamers[port].refreshtime > lasttimeserved or time.time() - timeout > lasttimeserved):
                    try:
                        self.wfile.write("--BOUNDARYSTRING\r\n")
                        self.send_header("Content-type", "image/jpeg")
                        self.send_header("Content-Length", str(len(_jpegstreamers[port].jpgdata)))
                        self.end_headers()
                        _jpegstreamers[port]._lock.acquire()
                        self.wfile.write(_jpegstreamers[port].jpgdata)
                        _jpegstreamers[port]._lock.release()
                        self.wfile.write("\r\n")
                        lasttimeserved = time.time()
                    except socket.error, e:
			print "send_response socket.error: " + str(e)
                        return    
                    #except IOError, e:
			print "send_response generic IOError: " + str(e)
                        return
                    count = count + 1


                time.sleep(_jpegstreamers[port].sleeptime)




class JpegTCPServer(ThreadingMixIn, TCPServer):
    allow_reuse_address = True
    daemon_threads = True


#factory class for jpegtcpservers
class JpegStreamer():
    """
    The JpegStreamer class allows the user to stream a jpeg encoded file
    to a HTTP port.  Any updates to the jpg file will automatically be pushed
    to the browser via multipart/replace content type.
    To initialize:
    js = JpegStreamer()
    to update:
    img.save(js)
    to open a browser and display:
    import webbrowser
    webbrowser.open(js.url)
    Note 3 optional parameters on the constructor:
    - port (default 8080) which sets the TCP port you need to connect to
    - sleep time (default 0.1) how often to update.  Above 1 second seems to cause dropped connections in Google chrome
    Once initialized, the buffer and sleeptime can be modified and will function properly -- port will not.
    """
    server = ""
    host = ""
    port = ""
    sleeptime = ""
    framebuffer = ""
    counter = 0
    refreshtime = 0
    _lock = threading.Lock()

    def __init__(self, hostandport = 8080, st=0.1):
        global _jpegstreamers
        if (type(hostandport) == int):
            self.port = hostandport
            self.host = "localhost"
        elif (isinstance(hostandport, basestring) and re.search(":", hostandport)):
            (self.host, self.port) = hostandport.split(":")
            self.port = int(self.port)
        elif (type(hostandport) == tuple):
            (self.host, self.port) = hostandport

        self.jpgdata = []
        self.sleeptime = st
        self.server = JpegTCPServer((self.host, self.port), JpegStreamHandler)
        self.server_thread = threading.Thread(target = self.server.serve_forever)
        _jpegstreamers[self.port] = self

        self.server_thread.daemon = True
        self.server_thread.start()
        self.framebuffer = self #self referential, ugh.  but gives some bkcompat


    def url(self):
        """
        Returns the JpegStreams Webbrowser-appropriate URL, if not provided in the constructor, it defaults to "http://localhost:8080"
        """
        return "http://" + self.host + ":" + str(self.port) + "/"


    def streamUrl(self):
        """
        Returns the URL of the MJPEG stream. If host and port are not set in the constructor, defaults to "http://localhost:8080/stream/"
        """
        return self.url() + "stream"

    def set_image(self, image):
        _jpegstreamers[self.port]._lock.acquire()
        _jpegstreamers[self.port].jpgdata = copy.copy(image)
        _jpegstreamers[self.port]._lock.release()
 

