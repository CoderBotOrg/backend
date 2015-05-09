import picamera
import picamera.array
import io
import os
import time
import copy
import logging

class Camera():

  FFMPEG_CMD = 'MP4Box'
  PHOTO_FILE_EXT = ".jpg"
  VIDEO_FILE_EXT = ".mp4"
  VIDEO_FILE_EXT_H264 = '.h264'

  def __init__(self, props):
    logging.info("camera init")
    self.camera = picamera.PiCamera()
    self.camera.resolution = (props.get('width', 640), props.get('height', 240))
    self.camera.framerate = 30
    self.camera.exposure_mode = props.get('exposure_mode')
    self.out_jpeg = io.BytesIO()
    self.out_rgb = picamera.array.PiRGBArray(self.camera, size=(160,120))
    self.h264_encoder = None
    self.recording = None
    self.video_filename = None

  def video_rec(self, filename):
    self.video_filename = filename[:filename.rfind(".")]

    camera_port_2, output_port_2 = self.camera._get_ports(True, 2)
    self.h264_encoder = self.camera._get_video_encoder(camera_port_2, output_port_2, 'h264', None)

    with self.camera._encoders_lock:
      self.camera._encoders[2] = self.h264_encoder

    logging.debug( self.video_filename + self.VIDEO_FILE_EXT_H264 )

    self.h264_encoder.start(self.video_filename + self.VIDEO_FILE_EXT_H264)

  def video_stop(self):
    logging.debug("video_stop")
    self.h264_encoder.stop()

    with self.camera._encoders_lock:
      del self.camera._encoders[2]

    self.h264_encoder.close()

    # pack in mp4 container
    params = " -fps 12 -add "  + self.video_filename + self.VIDEO_FILE_EXT_H264 + "  " + self.video_filename + self.VIDEO_FILE_EXT
    #avconv_params = " -r 30 -i "  + self.video_filename + self.VIDEO_FILE_EXT_H264 + " -vcodec copy  " + self.video_filename + self.VIDEO_FILE_EXT
    os.system(self.FFMPEG_CMD + params)
    # remove h264 file
    os.remove(self.video_filename + self.VIDEO_FILE_EXT_H264)

  def grab(self):
    ts = time.time()
    camera_port_0, output_port_0 = self.camera._get_ports(True, 0)
    self.jpeg_encoder = self.camera._get_image_encoder(camera_port_0, output_port_0, 'jpeg', None, quality=40)
    camera_port_1, output_port_1 = self.camera._get_ports(True, 1)
    self.rgb_encoder = self.camera._get_image_encoder(camera_port_1, output_port_1, 'bgr', (160, 120))
    #print "g.1: " + str(ts - time.time())
    #ts = time.time()

    with self.camera._encoders_lock:
      self.camera._encoders[0] = self.jpeg_encoder
      self.camera._encoders[1] = self.rgb_encoder

    #print "g.2: " + str(ts - time.time())
    #ts = time.time()

    self.out_jpeg.seek(0)
    self.out_rgb.seek(0)

    self.jpeg_encoder.start(self.out_jpeg)
    self.rgb_encoder.start(self.out_rgb)

    #print "g.3: " + str(ts - time.time())
    #ts = time.time()

    if not self.jpeg_encoder.wait(10):
      raise picamera.PiCameraError('Timed out')
    if not self.rgb_encoder.wait(10):
      raise picamera.PiCameraError('Timed out')

    #print "g.4: " + str(ts - time.time())
    #ts = time.time()

    with self.camera._encoders_lock:
      del self.camera._encoders[0]
      del self.camera._encoders[1]
    self.jpeg_encoder.close()
    self.rgb_encoder.close()

    #print "g.5: " + str(ts - time.time())

  def grab_start(self):
    logging.debug("grab_start")

    #ts = time.time()
    camera_port_0, output_port_0 = self.camera._get_ports(True, 0)
    self.jpeg_encoder = self.camera._get_image_encoder(camera_port_0, output_port_0, 'jpeg', None, quality=40)
    camera_port_1, output_port_1 = self.camera._get_ports(True, 1)
    self.rgb_encoder = self.camera._get_image_encoder(camera_port_1, output_port_1, 'bgr', (160, 120))

    with self.camera._encoders_lock:
      self.camera._encoders[0] = self.jpeg_encoder
      self.camera._encoders[1] = self.rgb_encoder

  def grab_one(self):
    self.out_jpeg.seek(0)
    self.out_rgb.seek(0)

    self.jpeg_encoder.start(self.out_jpeg)
    self.rgb_encoder.start(self.out_rgb)

    if not self.jpeg_encoder.wait(10):
      raise picamera.PiCameraError('Timed out')
    if not self.rgb_encoder.wait(10):
      raise picamera.PiCameraError('Timed out')

  def grab_stop(self):
    logging.debug("grab_stop")

    with self.camera._encoders_lock:
      del self.camera._encoders[0]
      del self.camera._encoders[1]

    self.jpeg_encoder.close()
    self.rgb_encoder.close()

  def get_image_jpeg(self):
    return self.out_jpeg.getvalue()

  def get_image_bgr(self):
    return self.out_rgb.array

  def grab_jpeg(self):
    ts = time.time()
    self.out_jpeg.seek(0)

    self.jpeg_encoder.start(self.out_jpeg)

    if not self.jpeg_encoder.wait(10):
      raise picamera.PiCameraError('Timed out')

    #print time.time() - ts

  def grab_bgr(self):
    ts = time.time()
    self.out_rgb.seek(0)

    self.rgb_encoder.start(self.out_rgb)

    if not self.rgb_encoder.wait(10):
      raise picamera.PiCameraError('Timed out')
   
    #print time.time() - ts

  def set_overlay_text(self, text):
    self.camera.annotate_text = text
    
  def close(self):
    self.camera.close()
