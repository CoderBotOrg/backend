import time
from threading import Thread
from SimpleCV import Camera, Image, Color, JpegStreamer
import coderbot

class CameraHandler(Thread):

  def __init__(self):
    print "starting camera"
    self.cam = Camera()
    self.streamer = JpegStreamer("0.0.0.0:8091")
    Thread.__init__(self)

  _cam_handler = None
  
  @classmethod
  def get_instance(cls): 
    if not cls._cam_handler:
      cls._cam_handler = CameraHandler()
    return cls._cam_handler 
  
  
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
      if self._active_handler_idx is not None:
      	handler = self._handlers[self._active_handler_idx]
      	handler.handle(img, self.streamer)
      else:
        time.sleep(0.5)
  
  _handlers = []
  _active_handler_idx = None
  
  @classmethod
  def add_handler(cls, handler):
    print "adding: " + handler.get_name()
    cls._handlers.append(handler)
  
  @classmethod
  def set_active_handler(cls, index):
    print index
    cls._active_handler_idx = index
    print "activating: " + (cls._handlers[cls._active_handler_idx].get_name() if index is not None else "None")
    
    
class SimpleHandler():

  @classmethod
  def get_name(cls):
    return "Simple"
    
  def handle(self, img, streamer):        
    print "streaming"
    img.save(streamer)
    
