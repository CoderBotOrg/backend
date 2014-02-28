import time
from SimpleCV import Camera, Image, Color, JpegStreamer
import coderbot

class SignalHandler():

  corners = [(160, 0), (480, 0), (380, 480), (260, 480)]

  @classmethod
  def get_name(cls):
    return "Signal"
      
  def __init__(self, bot):
    self.bot = bot
    
  def handle(self, img, streamer):        
    lineAngle = None

    # Warp the picture to straighten the paper
    warped = img.warp(self.corners)
    
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
        circle.draw()
        line.draw()
        if (line.x < (img_circle.width / 2)):
          if (line.y < (img_circle.height / 2)):
            lineAngle = lineAngle - 180
          else:
            lineAngle = lineAngle + 180
 
        print lineAngle

    warped.save(streamer)
   
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

