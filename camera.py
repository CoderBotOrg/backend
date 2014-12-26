import time
import copy
import os
import math
from PIL import Image as PILImage
from StringIO import StringIO
from threading import Thread, Lock

from viz import camera, streamer, image, blob

CAMERA_REFRESH_INTERVAL=0.1
MAX_IMAGE_AGE = 0.0
PHOTO_PATH = "./photos"
PHOTO_PREFIX = "DSC"
VIDEO_PREFIX = "VID"
PHOTO_THUMB_SUFFIX = "_thumb"
PHOTO_THUMB_SIZE = (240,180)

class Camera(Thread):

  _instance = None
  _cam_props = {"width":640, "height":480}
  #_cam_off_img = SimpleCV.Image("coderdojo-logo.png")
  _warp_corners_1 = [(0, -120), (640, -120), (380, 480), (260, 480)]
  _warp_corners_2 = [(0, -60), (320, -60), (190, 240), (130, 240)]
  _warp_corners_4 = [(0, -30), (160, -30), (95, 120), (65, 120)]
  stream_port = 8090

  @classmethod
  def get_instance(cls):
    if not cls._instance:
      cls._instance = Camera()
      cls._instance.start()
    return cls._instance

  def __init__(self):
    print "starting camera"
    self._camera = camera.Camera(props=self._cam_props)
    self._streamer = streamer.JpegStreamer("0.0.0.0:"+str(self.stream_port), st=0.1)
    #self._cam_off_img.save(self._streamer)
    self.recording = False
    self._run = True
    self._image_time = 0
    self._image_lock = Lock()

    self._photos = []
   
    for dirname, dirnames, filenames,  in os.walk(PHOTO_PATH):
      for filename in filenames:
        if (PHOTO_PREFIX in filename or VIDEO_PREFIX in filename) and PHOTO_THUMB_SUFFIX not in filename:
          self._photos.append(filename)
   
    super(Camera, self).__init__()

  def run(self):
    self._camera.grab_start()
    while self._run:
      if time.time() - self._image_time > CAMERA_REFRESH_INTERVAL:
        ts = time.time()
        print "run.1"
        self._image_lock.acquire()
        self._camera.grab_one()
        #print "run.2: " + str(time.time()-ts)
        #self.save_image(image.Image(self._camera.get_image_bgr()).filter_color((140, 53, 44)).to_jpeg())
        self.save_image(self._camera.get_image_jpeg())
        #print "run.3: " + str(time.time()-ts)
        self._image_lock.release()
      else:
        time.sleep(time.time() - self._image_time)

    self._camera.grab_stop()

  def get_image(self, maxage = MAX_IMAGE_AGE):
    return image.Image(self._camera.get_image_bgr())

  def save_image(self, image_jpeg):
    self._streamer.set_image(image_jpeg)
    self._image_time=time.time()

  def take_photo(self):
    last_photo_index = 0
    if len(self._photos):
      last_photo_index = int(self._photos[-1][len(PHOTO_PREFIX):-len(self._camera.PHOTO_FILE_EXT)])
    filename = PHOTO_PREFIX + str(last_photo_index+1) + self._camera.PHOTO_FILE_EXT;
    filename_thumb = PHOTO_PREFIX + str(last_photo_index+1) + PHOTO_THUMB_SUFFIX + self._camera.PHOTO_FILE_EXT;
    of = open(PHOTO_PATH + "/" + filename, "w+")
    oft = open(PHOTO_PATH + "/" + filename_thumb, "w+")
    im_str = self._camera.get_image_jpeg()
    of.write(im_str)
    # thumb
    im_pil = PILImage.open(StringIO(im_str)) 
    im_pil.resize(PHOTO_THUMB_SIZE).save(oft)
    self._photos.append(filename)

  def is_recording(self):
    return self.recording

  def video_rec(self):
    if self.is_recording():
      return
    self.recording = True

    last_photo_index = 0
    if len(self._photos):
      last_photo_index = int(self._photos[-1][len(PHOTO_PREFIX):-len(self._camera.PHOTO_FILE_EXT)])
    filename = VIDEO_PREFIX + str(last_photo_index+1) + self._camera.VIDEO_FILE_EXT;
    filename_thumb = VIDEO_PREFIX + str(last_photo_index+1) + PHOTO_THUMB_SUFFIX + self._camera.PHOTO_FILE_EXT;
    oft = open(PHOTO_PATH +  "/" + filename_thumb, "w")
    im_str = self._camera.get_image_jpeg()
    im_pil = PILImage.open(StringIO(im_str)) 
    im_pil.resize(PHOTO_THUMB_SIZE).save(oft)
    self._photos.append(filename)
    self._camera.video_rec(PHOTO_PATH + "/" + filename)

  def video_stop(self):
    self._camera.video_stop()
    self.recording = False
    
  def get_photo_list(self):
    return self._photos

  def get_photo_file(self, filename):
    return open(PHOTO_PATH + "/" + filename)

  def get_photo_thumb_file(self, filename):
    return open(PHOTO_PATH + "/" + filename[:-len(PHOTO_FILE_EXT)] + PHOTO_THUMB_SUFFIX + PHOTO_FILE_EXT)

  def delete_photo(self, filename):
    print filename
    os.remove(PHOTO_PATH + "/" + filename)
    os.remove(PHOTO_PATH + "/" + filename[:filename.rfind(".")] + PHOTO_THUMB_SUFFIX + self._camera.PHOTO_FILE_EXT)
    self._photos.remove(filename)

  def exit(self):
    self._run = False
    self.join()

  def calibrate(self):
    img = self._camera.getImage()
    self._background = img.hueHistogram()[-1]
        
  def find_line(self):
    self._image_lock.acquire()
    img = self.get_image(0)
    #img.drawRectangle(0,200,640,40)
    #img.drawRectangle(240,200,160,40, color=(0,0,255))
    cropped = img.crop(0, 200, 640, 40)
    blobs = cropped.find_blobs(minsize=800, maxsize=4000)
    coordX = 50
    if blobs and len(blobs):
      line = blobs[-1]
      #img.drawRectangle(line.minRect()[0][0], 200, line.width(), line.height(), color=(0,255,0))
      coordX = (line.center[0] * 100) / cropped.width
    
    self._image_lock.release()
    return coordX

  def find_signal(self):
    #print "signal"
    angle = None
    ts = time.time()
    self._image_lock.acquire()
    img = self.get_image(0)
    #print "signal.get_image: " + str(time.time() - ts)
    warped = img.resize(320).warp(self._warp_corners_2).resize(640)
    #print "signal.warp: " + str(time.time() - ts)
    cropped = warped.crop(260, 160, 120, 320)

    binarized = cropped.binarize()

    blobs = binarized.find_blobs(minsize=3000, maxsize=4000)
    #print blobs
    print "signal.blobs: " + str(time.time() - ts)
    signal = binarized
    coordY = 60
    if blobs and len(blobs):
      blobs.draw()
      signals = blobs.filter([b.isSquare() for b in blobs]) 
      #print signals
      if signals:
        signal = signals.sortDistance((320, 480))[0].crop().crop(8,8,46,46)
        #print "found signal: " + str(signal)
        lines = signal.findLines(threshold=10, minlinelength=10, maxlinegap=2, cannyth1=50, cannyth2=100)
        #print "lines: " + str(lines)
        if lines and len(lines):
          lines = lines.sortLength()
        
          #center_line = lines[-1]
          #center_line.draw()

          #print "center_line: " + str(center_line.length())

          angle = center_line.angle()
          #print "angle raw: " + str(angle)
          if angle < 0.0:
            angle = angle + 360
          if (((angle < 45.0 or angle > 315.0) and (center_line.coordinates()[0] < (signal.width / 2))) or
             ((angle > 45.0 and angle < 135.0)  and (center_line.coordinates()[1] > (signal.height / 2))) or
             ((angle > 135.0 and angle < 225.0) and (center_line.coordinates()[0] > (signal.width / 2))) or
             ((angle > 225.0 and angle < 315.0)  and (center_line.coordinates()[1] < (signal.height / 2)))):
            angle = angle + 180
          if angle > 360.0:
            angle = angle - 360
          
          img.drawText("signal found pointing at " + str(angle), 0, 0, fontsize=32 )
          #print "angle final: " + str(angle)
        else:
          angle = -1
          img.drawText("stop signal found", 0, 0, fontsize=32 )

    self.save_image(img)
    self._image_lock.release()
    #print "signal: " + str(time.time() - ts)
    return angle

  def find_face(self):
    print "face"
    faceX = None
    ts = time.time()
    self._image_lock.acquire()
    img = self.get_image(0)
    faces = img.find_faces()
    if faces is not None and len(faces):
      # Get the largest face 
      bigFace = faces[-1]
      # Draw a green box around the face 
      #bigFace.draw()
      faceX = (bigFace.center[0] * 100) / 80

    self.save_image(img)
    self._image_lock.release()
    print "face: " + str(time.time() - ts)
    return faceX

  def path_ahead(self):
    print "path ahead"
    ts = time.time()
    self._image_lock.acquire()
    img = self.get_image(0)
    print "path_ahead.get_image: " + str(time.time() - ts)
    img.crop(0, 100, 160, 120)

    control_color = control.meanColor()
    color_distance = cropped.dilate().color_distance(control_color)

    control_hue = control.getNumpy().mean()
    #hue_distance = cropped.dilate().hueDistance(control_hue)

    print "path_ahead.crop: " + str(time.time() - ts)
    #control_hue = control_hue - 20 if control_hue > 127 else control_hue + 20
    #binarized = cropped.dilate().binarize(control_hue)
    #binarized = cropped.dilate().binarize().invert()
    control_hue = control_hue - 10
    binarized = color_distance.binarize(control_hue).invert()
    print "path_ahead.binarize: " + str(time.time() - ts)
    blobs = binarized.findBlobs(minsize=1000, maxsize=(cropped.width*cropped.height)-2000)
    print "path_ahead.blobs: " + str(time.time() - ts)
    coordY = 60
    if blobs and len(blobs):
      print blobs
      obstacle = blobs.sortDistance(point=(60,480))[0]
      print "path_ahead.sortdistnace: " + str(time.time() - ts)
      #dw_x = 260 + obstacle.coordinates()[0] - (obstacle.width()/2)
      #dw_y = 160 + obstacle.coordinates()[1] - (obstacle.height()/2) 
      #img.drawRectangle(dw_x, dw_y, obstacle.width(), obstacle.height(), color=(255,0,0))
      coordY = 60 - (((obstacle.center()[1]+(obstacle.height()/2)) * 48) / cropped.height) 
      #print obstacle.coordinates()[1]+(obstacle.height()/2)
      #ar_layer.centeredRectangle(obstacle.coordinates(), (obstacle.width(), obstacle.height()))
      #warped.addDrawingLayer(ar_layer)
      #warped.applyLayers()
      #self.save_image(warped.warp(self._unwarp_corners), expire=10)

    img.drawText("path ahead clear for " + str(coordY) + " cm", 0, 0, fontsize=32 )
    print "path_ahead.drawtext: " + str(time.time() - ts)
    self.save_image(img)
    print "path_ahead.save_image: " + str(time.time() - ts)
    self._image_lock.release()
    print "path_ahead: " + str(time.time() - ts)
    return coordY

  def find_code(self):
    #print "code"
    code_data = None
    ts = time.time()
    self._image_lock.acquire()
    img = self.get_image(0)
    #print "signal.get_image: " + str(time.time() - ts)
    warped = img.resize(320).warp(self._warp_corners_2).resize(640)
    #print "code.warp: " + str(time.time() - ts)
    cropped = warped.crop(260, 160, 120, 320)

    barcode = cropped.findBarcode()
    if barcode:
      code_data = barcode.data
      img.drawText("code found: " + data, 0, 0, fontsize=32 )
    self.save_image(img)
    self._image_lock.release()
    #print "code: " + str(time.time() - ts)
    return code_data
    
  def find_color(self, s_color):
    print s_color
    color = (int(s_color[1:3],16), int(s_color[3:5],16), int(s_color[5:7],16))
    code_data = None
    ts = time.time()
    self._image_lock.acquire()
    img = self.get_image(0)
    #print "signal.get_image: " + str(time.time() - ts)
    #warped = img.colorDistance(color).resize(160).warp(self._warp_corners_4).binarize(80)
    #print "oject.warp: " + str(time.time() - ts)
    #objects = warped.findBlobs(minsize=200, maxsize=4000)
    bw = img.filter_color(color)
    objects = bw.find_blobs(minsize=50, maxsize=1000)
    print objects
    dist = -1
    angle = 180

    if objects and len(objects):
      object = objects[-1]
      bottom = object.bottom
      print "bottom: ", object.center[0], object.bottom
      x, y = bw.transform(object.center[0], object.bottom)
      print "coordinates: ", x, y
      #print "height: " + str(object.height())
      dist = math.sqrt(math.pow(12 + (68 * (120 - y) / 100),2) + (math.pow((x-80)*60/160,2)))
      angle = math.atan2(x - 80, 120 - y) * 180 / math.pi
      print "object found, dist: " + str(dist) + " angle: " + str(angle)
      #img.drawText("object found, dist: " + str(dist) + " angle: " + str(angle), 0, 0, fontsize=32 )
    #self.save_image(self._camera.get_image_jpeg())
    #self.save_image(img.to_jpeg())
    self._image_lock.release()
    #print "object: " + str(time.time() - ts)
    return [dist, angle]
    
  def find_logo(self):
    #print "logo"
    logo_y = None
    ts = time.time()
    self._image_lock.acquire()
    img = self.get_image(0)
    #print "logo.get_image: " + str(time.time() - ts)
    warped = img.resize(320).warp(self._warp_corners_2).resize(640)
    #print "logo.warp: " + str(time.time() - ts)
    cropped = warped.crop(260, 160, 120, 320)

    logo = img.findKeypointMatch(self._cam_off_img)
    if logo:
      #logo = logos[-1]
      x, y = logo.coordinates()
      print "found logo at: " + str(x) + " " + str(y)
      logo_y = 60 - ((y * 48) / cropped.height) 
      img.drawText("logo found at: " + str(logo.coordinates()), 0, 0, fontsize=32 )
    self.save_image(img)
    self._image_lock.release()
    #print "code: " + str(time.time() - ts)
    return logo_y 
    
  def sleep(self, elapse):
    print "sleep"
    time.sleep(elapse)

