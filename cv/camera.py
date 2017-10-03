############################################################################
#    CoderBot, a didactical programmable robot.
#    Copyright (C) 2014, 2015 Roberto Previtera <info@coderbot.org>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
############################################################################

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
    self.camera.resolution = (props.get('width', 640), props.get('height', 512))
    self.out_rgb_resolution = (self.camera.resolution[0] / int(props.get('cv_image_factor', 4)), self.camera.resolution[1] / int(props.get('cv_image_factor', 4)))
    self.camera.framerate = 30
    self.camera.exposure_mode = props.get('exposure_mode')
    self.out_jpeg = io.BytesIO()
    self.out_rgb = picamera.array.PiRGBArray(self.camera, size=self.out_rgb_resolution)
    self.h264_encoder = None
    self.recording = None
    self.video_filename = None
    self._jpeg_quality = props.get('jpeg_quality', 20)

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
    os.system(self.FFMPEG_CMD + params)
    # remove h264 file
    os.remove(self.video_filename + self.VIDEO_FILE_EXT_H264)

  def grab(self):
    ts = time.time()
    camera_port_0, output_port_0 = self.camera._get_ports(True, 0)
    self.jpeg_encoder = self.camera._get_image_encoder(camera_port_0, output_port_0, 'jpeg', None, quality=self._jpeg_quality)
    camera_port_1, output_port_1 = self.camera._get_ports(True, 1)
    self.rgb_encoder = self.camera._get_image_encoder(camera_port_1, output_port_1, 'bgr', self.out_rgb_resolution)
    #print "g.1: " + str(ts - time.time())
    #ts = time.time()

    with self.camera._encoders_lock:
      self.camera._encoders[0] = self.jpeg_encoder
      self.camera._encoders[1] = self.rgb_encoder

    self.out_jpeg.seek(0)
    self.out_rgb.seek(0)

    self.jpeg_encoder.start(self.out_jpeg)
    self.rgb_encoder.start(self.out_rgb)

    if not self.jpeg_encoder.wait(10):
      raise picamera.PiCameraError('Timed out')
    if not self.rgb_encoder.wait(10):
      raise picamera.PiCameraError('Timed out')

    with self.camera._encoders_lock:
      del self.camera._encoders[0]
      del self.camera._encoders[1]
    self.jpeg_encoder.close()
    self.rgb_encoder.close()

  def grab_start(self):
    logging.debug("grab_start")

    #ts = time.time()
    camera_port_0, output_port_0 = self.camera._get_ports(True, 0)
    self.jpeg_encoder = self.camera._get_image_encoder(camera_port_0, output_port_0, 'jpeg', None, quality=self._jpeg_quality)
    camera_port_1, output_port_1 = self.camera._get_ports(True, 1)
    self.rgb_encoder = self.camera._get_image_encoder(camera_port_1, output_port_1, 'bgr', self.out_rgb_resolution)

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
    try:
      self.camera.annotate_text = text
    except picamera.PiCameraValueError:
      logging.info("PiCameraValueError")
    
  def close(self):
    self.camera.close()
