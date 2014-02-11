import time
from threading import Thread
from SimpleCV import Camera, Image, Color, JpegStreamer
import coderbot

class SignalReader(Thread):

  def __init__(self):
    self.cam = Camera()
    time.sleep(2)
    self.streamer = JpegStreamer("0.0.0.0:8090")
    self.bot = coderbot.CoderBot()
    Thread.__init__(self)

  corners = [(160, 0), (480, 0), (460, 480), (180, 480)]

  def start(self):
    self.finish = False
    print "SignalReader starting"
    Thread.start(self)

  def stop(self):
    self.finish = True

  def run(self):
    print "run"
    while not self.finish:
      print "getting image"
      img = self.cam.getImage()

      # Warp the picture to straighten the paper
      warped = img.warp(SignalReader.corners)
      print "saving to streamer"
      warped.save(self.streamer)
      img_bin = warped.binarize(100).invert()
      lineAngle = None
      blobs = img_bin.findBlobs(minsize=8000)
      if blobs and len(blobs):
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
          self.bot.right(2)
        elif lineAngle < -60 and lineAngle > -120:
          print "go forward"
          self.bot.forward(2)
        elif lineAngle > 150 or lineAngle < -150:
          print "turn left"
          self.bot.left(2)
        elif lineAngle > 60 and lineAngle < 110:
          print "go backward"
          self.bot.backward(2)
      else:
        time.sleep(0.5)

    print "Signal Reader stopping"


