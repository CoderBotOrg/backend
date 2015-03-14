import time
import copy
import os
import math
from PIL import Image as PILImage
from StringIO import StringIO
from threading import Thread, Lock

from viz import camera, streamer, image, blob
import config

CAMERA_REFRESH_INTERVAL=0.1
MAX_IMAGE_AGE = 0.0
PHOTO_PATH = "./photos"
PHOTO_PREFIX = "DSC"
VIDEO_PREFIX = "VID"
PHOTO_THUMB_SUFFIX = "_thumb"
PHOTO_THUMB_SIZE = (240,180)
VIDEO_ELAPSE_MAX = 900

class Camera(Thread):

  _instance = None
  _img_template = image.Image.load("coderdojo-logo.png")
  _warp_corners_1 = [(0, -120), (640, -120), (380, 480), (260, 480)]
  _warp_corners_2 = [(0, -60), (320, -60), (190, 240), (130, 240)]
  _warp_corners_4 = [(0, -30), (160, -30), (95, 120), (65, 120)]
  stream_port = 9080

  @classmethod
  def get_instance(cls):
    if cls._instance is None:
      cls._instance = Camera()
      cls._instance.start()
    return cls._instance

  def __init__(self):
    print "starting camera"
    cam_props = {"width":640, "height":480, "exposure_mode": config.Config.get().get("camera_exposure_mode")}
    self._camera = camera.Camera(props=cam_props)
    self._streamer = streamer.JpegStreamer("0.0.0.0:"+str(self.stream_port), st=0.1)
    #self._cam_off_img.save(self._streamer)
    self.recording = False
    self.video_start_time = time.time() + 8640000
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
        #print "run.1"
        self._image_lock.acquire()
        self._camera.grab_one()
        self._image_lock.release()
        #print "run.2: " + str(time.time()-ts)
        #self.save_image(image.Image(self._camera.get_image_bgr()).open().binarize().to_jpeg())
        self.save_image(self._camera.get_image_jpeg())
        #print "run.3: " + str(time.time()-ts)
      else:
        time.sleep(CAMERA_REFRESH_INTERVAL - (time.time() - self._image_time))

      if self.recording and time.time() - self.video_start_time > VIDEO_ELAPSE_MAX:
        self.video_stop()

    self._camera.grab_stop()

  def get_image(self, maxage = MAX_IMAGE_AGE):
    return image.Image(self._camera.get_image_bgr())

  def save_image(self, image_jpeg):
    self._streamer.set_image(image_jpeg)
    self._image_time=time.time()

  def set_text(self, text):
    self._camera.set_overlay_text(str(text))

  def get_next_photo_index(self):
    last_photo_index = 0
    for p in self._photos:
      try:
        index = int(p[len(PHOTO_PREFIX):-len(self._camera.PHOTO_FILE_EXT)])
        if index > last_photo_index:
          last_photo_index = index
      except:
        pass
    return last_photo_index + 1

  def photo_take(self):
    photo_index = self.get_next_photo_index()
    filename = PHOTO_PREFIX + str(photo_index) + self._camera.PHOTO_FILE_EXT;
    filename_thumb = PHOTO_PREFIX + str(photo_index) + PHOTO_THUMB_SUFFIX + self._camera.PHOTO_FILE_EXT;
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

  def video_rec(self, video_name=None):
    if self.is_recording():
      return
    self.recording = True

    if video_name is None:
      video_index = self.get_next_photo_index()
      filename = VIDEO_PREFIX + str(video_index) + self._camera.VIDEO_FILE_EXT;
      filename_thumb = VIDEO_PREFIX + str(video_index) + PHOTO_THUMB_SUFFIX + self._camera.PHOTO_FILE_EXT;
    else:
      filename = VIDEO_PREFIX + video_name + self._camera.VIDEO_FILE_EXT;
      filename_thumb = VIDEO_PREFIX + video_name + PHOTO_THUMB_SUFFIX + self._camera.PHOTO_FILE_EXT;
      try:
        os.remove(PHOTO_PATH + "/" + filename)
      except:
        pass

    oft = open(PHOTO_PATH +  "/" + filename_thumb, "w")
    im_str = self._camera.get_image_jpeg()
    im_pil = PILImage.open(StringIO(im_str)) 
    im_pil.resize(PHOTO_THUMB_SIZE).save(oft)
    self._photos.append(filename)
    self._camera.video_rec(PHOTO_PATH + "/" + filename)
    self.video_start_time = time.time()

  def video_stop(self):
    if self.recording:
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
    img = self.get_image(0).binarize()
    #img.drawRectangle(0,200,640,40)
    #img.drawRectangle(240,200,160,40, color=(0,0,255))
    slices = [0,0,0]
    blobs = [0,0,0]
    slices[0] = img.crop(0, 100, 160, 120)
    slices[1] = img.crop(0, 80, 160, 100)
    slices[2] = img.crop(0, 60, 160, 80)
    coords = [50, 50, 50]
    for idx, slice in enumerate(slices):
      blobs[idx] = slice.find_blobs(minsize=80, maxsize=1600)
      #print "blobs: " + str(blobs[idx])
      if len(blobs[idx]):
        coords[idx] = (blobs[idx][0].center[0] * 100) / 160
	print "line coord: " + str(idx) + " " +  str(coords[idx])+ " area: " + str(blobs[idx][0].area())
    
    self._image_lock.release()
    return coords[0]

  def find_signal(self):
    #print "signal"
    angle = None
    ts = time.time()
    self._image_lock.acquire()
    img = self.get_image(0)
    signals = img.find_template(self._img_template)
     
    print "signal: " + str(time.time() - ts)
    if len(signals):
      angle = signals[0].angle

    self._image_lock.release()

    return angle

  def find_face(self):
    faceX = None
    self._image_lock.acquire()
    img = self.get_image(0)
    ts = time.time()
    faces = img.grayscale().find_faces()
    print "face.detect: " + str(time.time() - ts)
    self._image_lock.release()
    print faces
    if len(faces):
      # Get the largest face, face is a rectangle 
      bigFace = faces[0]
      center = bigFace[0]+(bigFace[2]/2)
      faceX = (center * 100) / 160

    return faceX

  def path_ahead(self):
    #print "path ahead"
    ts = time.time()
    self._image_lock.acquire()
    img = self.get_image(0)
    #print "path_ahead.get_image: " + str(time.time() - ts)
    #img.crop(0, 100, 160, 120)

    #control_color = control.meanColor()
    #color_distance = cropped.dilate().color_distance(control_color)

    #control_hue = control.getNumpy().mean()
    #hue_distance = cropped.dilate().hueDistance(control_hue)

    #print "path_ahead.crop: " + str(time.time() - ts)
    #control_hue = control_hue - 20 if control_hue > 127 else control_hue + 20
    #binarized = cropped.dilate().binarize(control_hue)
    #binarized = cropped.dilate().binarize().invert()
    #control_hue = control_hue - 10
    #binarized = color_distance.binarize(control_hue).invert()
    #print "path_ahead.binarize: " + str(time.time() - ts)
    blobs = img.binarize().find_blobs(minsize=100, maxsize=8000)
    #print "path_ahead.blobs: " + str(time.time() - ts)
    coordY = 60
    if len(blobs):
      obstacle = blob.Blob.sort_distance((80,120), blobs)[0]
      #for b in blobs:
      #  print "blobs.bottom: " + str(b.bottom) + " area: " + str(b.area())

      print "obstacle:" + str(obstacle.bottom) 
      #print "path_ahead.sortdistnace: " + str(time.time() - ts)
      #dw_x = 260 + obstacle.coordinates()[0] - (obstacle.width()/2)
      #dw_y = 160 + obstacle.coordinates()[1] - (obstacle.height()/2) 
      #img.drawRectangle(dw_x, dw_y, obstacle.width(), obstacle.height(), color=(255,0,0))
      x, y = img.transform((obstacle.center[0], obstacle.bottom))
      coordY = 60 - ((y * 48) / 100) 
      print "coordY: " + str(coordY)
      #print obstacle.coordinates()[1]+(obstacle.height()/2)
      #ar_layer.centeredRectangle(obstacle.coordinates(), (obstacle.width(), obstacle.height()))
      #warped.addDrawingLayer(ar_layer)
      #warped.applyLayers()
      #self.save_image(warped.warp(self._unwarp_corners), expire=10)

    #img.drawText("path ahead clear for " + str(coordY) + " cm", 0, 0, fontsize=32 )
    #print "path_ahead.drawtext: " + str(time.time() - ts)
    #self.save_image(img)
    #print "path_ahead.save_image: " + str(time.time() - ts)
    self._image_lock.release()
    #print "path_ahead: " + str(time.time() - ts)
    return coordY

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
      obj = objects[-1]
      bottom = obj.bottom
      print "bottom: ", obj.center[0], obj.bottom
      coords = bw.transform([(obj.center[0], obj.bottom)])
      print "coordinates: ", coords
      x = coords[0][0]
      y = coords[0][1]
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
    
  def sleep(self, elapse):
    print "sleep"
    time.sleep(elapse)

