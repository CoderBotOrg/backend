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
import io
import os
import logging
from threading import Condition
import numpy as np
from picamera2 import Picamera2
from picamera2.encoders import Encoder, MJPEGEncoder, H264Encoder
from picamera2.outputs import FileOutput, FfmpegOutput

class Camera(object):

    FFMPEG_CMD = 'ffmpeg'
    PHOTO_FILE_EXT = ".jpg"
    VIDEO_FILE_EXT = ".mp4"
    VIDEO_FILE_EXT_H264 = '.h264'

    class StreamingOutputMJPEG(io.BufferedIOBase):
        def __init__(self):
            self.frame = None
            self.condition = Condition()

        def write(self, buf):
            with self.condition:
                self.frame = buf
                self.condition.notify_all()

    class StreamingOutputBGR(io.BufferedIOBase):
        def __init__(self, resolution):
            self.frame = None
            self.condition = Condition()
            self.resolution = resolution

        def write(self, buf):
            with self.condition:
                frame = np.frombuffer(buf, dtype=np.uint8)
                self.frame = frame.reshape(self.resolution[1], self.resolution[0], 4)
                self.frame = np.delete(self.frame, 3, 2)
                self.condition.notify_all()

    def __init__(self, props):
        logging.info("camera init")
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_video_configuration(main={"size": (props.get('width', 640), props.get('height', 512))}))
        self.camera.resolution = (props.get('width', 640), props.get('height', 512))
        self.out_rgb_resolution = (int(props.get('width', 640) / int(props.get('cv_image_factor', 4))), int(props.get('height', 512) / int(props.get('cv_image_factor', 4))))
        self.camera.framerate = float(props.get('framerate', 20))
        self.camera.exposure_mode = props.get('exposure_mode', "auto")
        self.output_mjpeg = self.StreamingOutputMJPEG()
        self.encoder_streaming = MJPEGEncoder(10000000)
        self.encoder_streaming.output = [FileOutput(self.output_mjpeg)]
        self.encoder_h264 = H264Encoder()
        #self.output_bgr = self.StreamingOutputBGR(self.out_rgb_resolution)
        #self.h264_encoder = None
        self.recording = None
        self.video_filename = None
        self._jpeg_quality = props.get('jpeg_quality', 20)
        self._jpeg_bitrate = props.get('jpeg_bitrate', 5000000)

    def video_rec(self, filename):
        self.video_filename = filename[:filename.rfind(".")]
        output = FfmpegOutput(output_filename=filename)
        self.encoder_h264.output = [output]
        self.camera.start_encoder(self.encoder_h264, output)
        #self.camera.start_recording(self.encoder_h264, FfmpegOutput(output_filename=filename))
        #self.camera.start_recording(self.video_filename + self.VIDEO_FILE_EXT_H264, format="h264", quality=23, splitter_port=2)

    def video_stop(self):
        logging.info("video_stop")
        self.camera.stop_encoder(encoders=[self.encoder_h264])
        #self.camera.stop_recording()

    def grab_start(self):
        logging.info("grab_start")
        self.camera.start()
        self.camera.start_encoder(self.encoder_streaming)
        #self.camera.start_recording(self.output_mjpeg, format="mjpeg", splitter_port=0, bitrate=self._jpeg_bitrate)
        #self.camera.start_recording(self.output_bgr, format="bgra", splitter_port=1, resize=self.out_rgb_resolution)

    def grab_stop(self):
        logging.info("grab_stop")
        self.camera.stop_encoder(encoders=[self.encoder_streaming])

    def get_image_jpeg(self):
        with self.output_mjpeg.condition:
            self.output_mjpeg.condition.wait()
            return self.output_mjpeg.frame

    def get_image_bgr(self):
        buf = self.camera.capture_buffer()
        frame_from_buf = np.frombuffer(buf, dtype=np.uint8)
        frame = frame_from_buf.reshape(self.camera.resolution[1], self.camera.resolution[0], 4)
        frame = np.delete(frame, 3, 2)
        return frame

    def set_overlay_text(self, text):
        try:
            self.camera.annotate_text = text
        except picamera.PiCameraValueError:
            logging.info("PiCameraValueError")

    def close(self):
        self.camera.close()
