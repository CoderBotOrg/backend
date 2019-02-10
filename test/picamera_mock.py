import unittest.mock
import time
import io
import logging
import threading
from PIL import Image as PILImage
import cv2
import numpy

logger = logging.getLogger()

class PiCameraMock(object):
    """Implements PiCamera mock class
    PiCamera is the library used to access the integrated Camera, this mock class emulates the capture functions in order to test the streamer loop.
    """

    def __init__(self):
        self.resolution = None
        self.framerate = None
        self.exposure_mode = None
        self.annotate_text = None
        self.splitter_recorders = {}
        self.images = {}
        i = open('test/test_image.jpeg', 'rb')
        image_jpeg = i.read()
        i.close()
        self.images["mjpeg"] = image_jpeg 
        self.images["bgra"] = cv2.cvtColor(numpy.array(PILImage.open(io.BytesIO(image_jpeg))), cv2.COLOR_RGB2BGRA)
        

    class ImageRecorder(threading.Thread):
        def __init__(self, buffer, image):
            threading.Thread.__init__(self)
            self.buffer = buffer
            self.image = image
            self.go = True

        def run(self):
            while self.go:
                self.buffer.write(self.image)
                time.sleep(0.05)

    class VideoRecorder(object):
        def __init__(self, buffer, video):
            self.buffer = buffer
            self.video = video

    def start_recording(self, buffer, format, splitter_port, quality=None, bitrate=None, resize=None):
        """mock start_recording"""
        print(format)
        if format == "bgra" and resize:
            self.images[format] = cv2.resize(self.images[format], resize)
        if format == "h264":
            f = open("test/test.h264", "rb")
            video = f.read()
            f.close()
            self.splitter_recorders[splitter_port] = self.VideoRecorder(buffer, video)
        else:
            self.splitter_recorders[splitter_port] = self.ImageRecorder(buffer, self.images[format])
            self.splitter_recorders[splitter_port].start() 

    def stop_recording(self, splitter_port):
        if splitter_port < 2:
            self.splitter_recorders[splitter_port].go = False
            self.splitter_recorders[splitter_port].join()
        else:
            recorder = self.splitter_recorders[splitter_port]
            f = open(recorder.buffer, "wb")
            f.write(recorder.video)
            f.close()

    def close():
        """mock close"""
        pass

