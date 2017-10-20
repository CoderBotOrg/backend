############################################################################
#    CoderBot, a didactical programmable robot.
#    Copyright (C) 2014, 2017 Roberto Previtera <info@coderbot.org>
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
"""
The Camera module implements the Camera class, which is the abstraction
from the lower lever PiCamera (RPI specific)
"""
import picamera
import picamera.array
import io
import os
import time
import copy
import logging
import numpy as np
from threading import Condition

class Camera(object):

    FFMPEG_CMD = 'MP4Box'
    PHOTO_FILE_EXT = ".jpg"
    VIDEO_FILE_EXT = ".mp4"
    VIDEO_FILE_EXT_H264 = '.h264'

    class StreamingOutputMJPEG(object):
        def __init__(self):
            self.frame = None
            self.buffer = io.BytesIO()
            self.condition = Condition()

        def write(self, buf):
            if buf.startswith(b'\xff\xd8'):
                # New frame, copy the existing buffer's content and notify all
                # clients it's available
                self.buffer.truncate()
                with self.condition:
                    self.frame = self.buffer.getvalue()
                    self.condition.notify_all()
                self.buffer.seek(0)
            return self.buffer.write(buf)

    class StreamingOutputBGR(object):
        def __init__(self, resolution):
            self.frame = None
            self.condition = Condition()
            self.resolution = resolution
            self.count = 0

        def write(self, buf):
            with self.condition:
                frame = np.frombuffer(buf, dtype=np.uint8)
                self.frame = frame.reshape(self.resolution[1], self.resolution[0], 4)
                self.frame = np.delete(self.frame, 3, 2)
                self.condition.notify_all()
            return len(buf)

    def __init__(self, props):
        logging.info("camera init")
        self.camera = picamera.PiCamera()
        self.camera.resolution = (props.get('width', 640), props.get('height', 512))
        self.out_rgb_resolution = (self.camera.resolution[0] / int(props.get('cv_image_factor', 4)), self.camera.resolution[1] / int(props.get('cv_image_factor', 4)))
        self.camera.framerate = float(props.get('framerate', 20))
        self.camera.exposure_mode = props.get('exposure_mode', "auto")
        self.output_mjpeg = self.StreamingOutputMJPEG()
        self.output_bgr = self.StreamingOutputBGR(self.out_rgb_resolution)
        self.h264_encoder = None
        self.recording = None
        self.video_filename = None
        self._jpeg_quality = props.get('jpeg_quality', 20)
        self._jpeg_bitrate = props.get('jpeg_bitrate', 5000000)

    def video_rec(self, filename):
        self.video_filename = filename[:filename.rfind(".")]
        self.camera.start_recording(self.video_filename + self.VIDEO_FILE_EXT_H264, format="h264", quality=23, splitter_port=2)

    def video_stop(self):
        logging.debug("video_stop")
        self.camera.stop_recording(2)

        # pack in mp4 container
        params = " -fps " + str(self.camera.framerate) + " -add "  + self.video_filename + self.VIDEO_FILE_EXT_H264 + "  " + self.video_filename + self.VIDEO_FILE_EXT
        os.system(self.FFMPEG_CMD + params)
        # remove h264 file
        os.remove(self.video_filename + self.VIDEO_FILE_EXT_H264)

    def grab_start(self):
        logging.debug("grab_start")
        self.camera.start_recording(self.output_mjpeg, format="mjpeg", splitter_port=0, bitrate=self._jpeg_bitrate)
        self.camera.start_recording(self.output_bgr, format="bgra", splitter_port=1, resize=self.out_rgb_resolution)

    def grab_stop(self):
        logging.debug("grab_stop")

        self.camera.stop_recording(0)
        self.camera.stop_recording(1)

    def get_image_jpeg(self):
        with self.output_mjpeg.condition:
            self.output_mjpeg.condition.wait()
            return self.output_mjpeg.frame

    def get_image_bgr(self):
        with self.output_bgr.condition:
            self.output_bgr.condition.wait()
            return self.output_bgr.frame

    def set_overlay_text(self, text):
        try:
            self.camera.annotate_text = text
        except picamera.PiCameraValueError:
            logging.info("PiCameraValueError")

    def close(self):
        self.camera.close()
