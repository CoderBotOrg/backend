import time
from SimpleCV import Camera, Image, Color, JpegStreamer
import coderbot

class LogoHandler():

  @classmethod
  def get_name(cls):
    return "Logo"
      
  def __init__(self, logo_file_name, bot):
    self.bot = bot
    self.template_logo = Image(logo_file_name)
    
  def handle(self, img, streamer):        
    logos = img.findTemplateOnce(self.template_logo, method="CCOEFF")
    if logos:
      logo = logos.sortArea()[-1]
      print "found logo at: " + str(logo.coordinates())
      x, y = logo.coordinates()
      if x < ((img.width/2) - (img.width / 5)):
        print "left"
      if x > ((img.width/2) + (img.width / 5)):
        print "right"
      if y < ((img.height/2) - (img.height / 5)):
        print "forward"
      if y > ((img.height/2) + (img.height / 5)):
        print "backward"
        
      logo.draw()

    img.save(streamer)
    
