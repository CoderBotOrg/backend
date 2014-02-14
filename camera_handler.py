import time
from threading import Thread
from SimpleCV import Camera, Image, Color, JpegStreamer
import coderbot

class CameraHandler(Thread):

  def __init__(self):
    self.cam = Camera()
    self.streamer = JpegStreamer("0.0.0.0:8090")
    Thread.__init__(self)

  _the_reader = None
  
  @classmethod
  def get_instance(cls) {
    if not cls._cam_handler:
      cls._cam_handler = CameraHandler()
    return cls._cam_handler 
  }
  
  def start(self):
    self.finish = False
    print "CameraHandler starting"
    Thread.start(self)

  def stop(self):
    self.finish = True
    self.join()

  def run(self):
    print "run"
    while not self.finish:
      print "getting image"
      img = self.cam.getImage()
      if _active_handler_idx:
      	handler = self._handlers[_active_handler_idx]:
      	handler.handle(img, streamer)
      
  
  _handlers = []
  _active_handler_idx
  
  def add_handler(handler):
    _handler.add[handler]
  def set_active_handler(self, index):
    _active_handler_idx = index
    
    
class SimpleHandler():

  @classdef
  def get_name(cls):
    return "Simple"
    
  def handle(img, streamer):        
    img.save(streamer)
    
class SignalHandler():

  corners = [(160, 0), (480, 0), (460, 480), (180, 480)]

  @classdef
  def get_name(cls):
    return "Signal"
      
  def __init__(self, bot):
    self.bot = bot
    
  def handle(img, streamer):        
    lineAngle = None

    # Warp the picture to straighten the paper
    warped = img.warp(SignalReader.corners)
    
    # extract details
    img_bin = warped.binarize(100).invert()    
    
    #find objects
    blobs = img_bin.findBlobs(minsize=8000)
    
    if blobs and len(blobs):
      #found blobs, see if it's a signal
      circle = blobs.sortArea()[0]
      img_circle = circle.crop()
        #img_circle.show()
        lines = img_circle.findLines(threshold=40)
        #print lines
        if lines and len(lines):
          line = lines.sortLength()[-1]
          lineAngle = line.angle()
          #line.crop().show()
          print str(lineAngle) + " " + str(line.coordinates())
      
          if (line.x < (img_circle.width / 2)):
            if (line.y < (img_circle.height / 2)):
              lineAngle = lineAngle - 180
            else:
              lineAngle = lineAngle + 180
 
          print lineAngle   
      if lineAngle:
        if lineAngle > -30 and lineAngle < 30:
          print "turn right"
          self.bot.right(1.8)
        elif lineAngle < -60 and lineAngle > -120:
          print "go forward"
          self.bot.forward(2)
        elif lineAngle > 150 or lineAngle < -150:
          print "turn left"
          self.bot.left(1.8)
        elif lineAngle > 60 and lineAngle < 110:
          print "go backward"
          self.bot.backward(2)
      else:
        time.sleep(0.5)

    print "Signal Reader stopping"

class LogoHandler(BaseHandler):

  @classdef
  def get_name(cls):
    return "Logo"
      
  def __init__(self, logo_file_name, bot):
    self.bot = bot
    self.template_logo = Image(logo_file_name)
    
  def handle(img, streamer):        
    logos = img.findTemplate(self.template_logo)
    if logos:
      logo = logos.sortArea()[-1]
      print logo.coordinates()
      logo.draw()
    img.save(streamer)
    time.sleep(0.5)  
    