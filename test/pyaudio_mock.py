import unittest.mock
import time
import io
import logging
import numpy

logger = logging.getLogger()

class PyAudioMock(object):
    """Implements PyAudio mock class
    PyAudio is the library used to access the integrated audio output and external audio source (microphone)
    """

    def __init__(self):
        pass

    def open(self, format, channels, rate, frames_per_buffer, stream_callback):
        return self

    def stop_stream(self):
        pass

    def close(self):
        pass

    def terminate(self):
        pass

    def get_sample_size(format):
        return format * 16

