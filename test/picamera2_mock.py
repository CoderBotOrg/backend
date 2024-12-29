import unittest.mock
import time
import io
import logging
import threading
from PIL import Image as PILImage
import cv2
import numpy

logger = logging.getLogger()

class Picamera2EoncoderMock(threading.Thread):
    def __init__(self, output):
        self.output = output
        self.image_jpeg = open('test/test_image.jpeg', 'rb').read()
        self.exit = False
        super().__init__()

    def close(self):
        self.output[0].close()

    def stop(self):
        self.exit = True

    def run(self):
        while(not self.exit):
            self.output[0].outputframe(self.image_jpeg)
            time.sleep(0.03)

class Picamera2MJPEGEncoderMock(Picamera2EoncoderMock):
    def __init__(self, output=None, quality=20):
        super().__init__(output)
        self.quality = quality

class Picamera2H264EncoderMock(Picamera2EoncoderMock):
    def __init__(self, output=None):
        super().__init__(output)

class Picamera2Mock(object):
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
        
    def configure(self, configuration):
        pass

    def create_video_configuration(self, main):
        return {}

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

    def start(self):
        pass

    def start_encoder(self, encoder, output=None):
        encoder.start()
        output

    def stop_encoder(self, encoders):
        for encoder in encoders:
            encoder.stop()

    def capture_buffer(self):
        return self.images["bgra"]

    def close():
        """mock close"""
        pass

