import time
from threading import Thread

import SimpleCV

class Camera(Thread):

  _instance = None
  _cam_props = {"width":640, "height":480}
  _cam_off_img = SimpleCV.Image("coderdojo-logo.png")
  _warp_corners = [(0, 0), (640, 0), (380, 480), (260, 480)]


  @classmethod
  def get_instance(cls):
    if not cls._instance:
      cls._instance = Camera()
      cls._instance.start()
    return cls._instance

  def __init__(self):
    print "starting camera"
    self._camera = SimpleCV.Camera(prop_set=self._cam_props, threaded=False)
    self._streamer = SimpleCV.JpegStreamer("0.0.0.0:8090")
    self._cam_off_img.save(self._streamer)
    self._run = True
    super(Camera, self).__init__()

  def run(self):
    frame = 0
    while self._run:
      self._image = self._camera.getImage()
      #peaks = self._image.huePeaks()
      #hue = self._image.hueDistance(peaks[0][0])
      #mask = hue.binarize().invert()
      if not (frame % 10):
        self._image.save(self._streamer)
    
  def exit(self):
    self._run = False
    self.join()

  def calibrate(self):
    img = self._camera.getImage()
    self._background = img.hueHistogram()[-1]
        
  def find_line(self):
    img = self._image
    img.drawRectangle(0,200,640,40)
    img.drawRectangle(240,200,160,40, color=(0,0,255))
    cropped = img.crop(0, 200, 640, 40)
    blobs = cropped.findBlobs(minsize=800, maxsize=4000)
    coordX = 50
    if blobs and len(blobs):
      line = blobs[-1]
      img.drawRectangle(line.minRect()[0][0], 200, line.width(), line.height(), color=(0,255,0))
      coordX = (line.coordinates()[0] * 100) / cropped.width
    
    return coordX

    
  def find_signal(self):
    img = self._image
    signals = img.findBlobs(minsize=500)
    if signal:
      return signal[-1]

  def path_ahead(self):
    img = self._image
    warped = img.warp(self._warp_corners)
    cropped = warped.crop(260, 160, 120, 320)
    control = cropped.crop(0, 280, 160, 40)
    #control_color = control.meanColor()
    control_hue = control.getNumpy().mean()
    control_hue = control_hue - 20 if control_hue > 127 else control_hue + 20
    binarized = cropped.dilate().binarize(control_hue)
    blobs = binarized.findBlobs(minsize=1000, maxsize=(cropped.width*cropped.height)-2000)
    coordY = 60
    if blobs and len(blobs):
      print blobs
      obstacle = blobs.sortDistance(point=(60,320))[0]
      dw_x = 260 + obstacle.coordinates()[0] - (obstacle.width()/2)
      dw_y = 160 + obstacle.coordinates()[1] - (obstacle.height()/2) 
      img.drawRectangle(dw_x, dw_y, obstacle.width(), obstacle.height(), color=(255,0,0))
      coordY = 60 - (((obstacle.coordinates()[1]+(obstacle.height()/2)) * 48) / cropped.height) 
      print obstacle.coordinates()[1]+(obstacle.height()/2)
    
    return coordY
    
