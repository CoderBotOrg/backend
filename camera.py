import time
from threading import Thread

import SimpleCV

class Camera(Thread):

  _instance = None
  _cam_off_img = SimpleCV.Image("coderdojo-logo.png")

  @classmethod
  def get_instance(cls):
    if not cls._instance:
      cls._instance = Camera()
      cls._instance.start()
    return cls._instance

  def __init__(self):
    print "starting camera"
    self._camera = SimpleCV.Camera()
    self._streamer = SimpleCV.JpegStreamer("0.0.0.0:8090", st=0.5)
    self._cam_off_img.save(self._streamer)
    super(Camera, self).__init__()

  def run(self):
    self._image = self._camera.getImage()
    self._image.save(self._streamer)
    
  def calibrate(self):
    img = self._camera.getImage()
    self._background = img.hueHistogram()[-1]
        
  def find_line(self):
    img = self._image
    lines = img.findLines(threshold=20, minlinelength=50, maxlinegap=20)
    if lines:
      return lines[-1]
    
  def find_signal(self):
    img = self._image
    signals = img.findBlobs(minsize=500)
    if signal:
      return signal[-1]

  def path_ahead(self):
    img = self._image
    obstacles = img.findBlobs(minsize=500)
    for o in obstacles:
      if o.below(240):
        return False
    return True
    
