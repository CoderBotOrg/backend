import time
import SimpleCV

import coderbot

def main():
  c = SimpleCV.Camera()
  s = SimpleCV.JpegStreamer("0.0.0.0:8090")
  bot = coderbot.CoderBot()

  frame = 0
  while True:
    i = c.getImage()
    i.drawRectangle(0,200,640,40)
    i.drawRectangle(240,200,160,40, color=(0,0,255))
    cropped = i.crop(0, 200, 640, 40)
    blobs = cropped.findBlobs(minsize=800, maxsize=4000)
    if blobs and len(blobs):
      line = blobs[-1]
      i.drawRectangle(line.minRect()[0][0], 200, line.width(), line.height(), color=(0,255,0))
      coordX = line.coordinates()[0]
      if coordX > 400:
        print "going right"
        bot.right(0.04)
      elif coordX < 240:
        print "going left"
        bot.left(0.04)
      else:
        print "going straight"
        bot.forward(0.2)
    else:
      bot.backward(0.1)

    frame += 1
    if frame % 4 == 0: 
      i.save(s)
    time.sleep(0.05)


if __name__ == "__main__":
  main()
