import signal
import sys
import time
import SimpleCV

import coderbot

def main():
  _warp_region = [(0, 0), (640, 0), (380, 480), (260, 480)]
  c = SimpleCV.Camera()
  s = SimpleCV.JpegStreamer("0.0.0.0:8090")
  bot = coderbot.CoderBot()

  frame = 0
  while True:
    i = c.getImage()
    i = i.warp(_warp_region)
    i.drawRectangle(0,120,640,360, color=(255,255,255))
    i.drawRectangle(260,160,120,320, color=(0,0,255))
    cropped = i.crop(260, 160, 120, 320)
    control = cropped.crop(0, 280, 160, 40)
    #control_color = control.meanColor()
    control_hue = control.getNumpy().mean()
    control_hue = control_hue - 20 if control_hue > 127 else control_hue + 20
    binary = cropped.dilate().binarize(control_hue)    
    blobs = binary.findBlobs(minsize=1000, maxsize=38000)
    if blobs and len(blobs):
      blobs.draw()
      obstacle = blobs.sortDistance(point=(60,320))[0]
      i.drawRectangle(obstacle.coordinates()[0]-20+260, obstacle.coordinates()[1]-20+160, 40, 40, color=(255,0,0))
      coordY = obstacle.coordinates()[1] + (obstacle.height()/2)
      print coordY

    cropped.save(s)

def signal_handler(signal, frame):
  print('quit!')
  sys.exit(0)

if __name__ == "__main__":
  signal.signal(signal.SIGINT, signal_handler)
  print('Press Ctrl+C to quit!')
  main()



