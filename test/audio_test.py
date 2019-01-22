import unittest
import os
import test.pyaudio_mock

import audio

FILENAME = "test.wav"

class AudioTest(unittest.TestCase):
    def setUp(self):
        piaudio.PyAudio = test.pyaudio_mock.PyAudioMock
        self.audio = audio.Audio.get_instance()
   
    def tearDown(self):
        pass

    def test_say(self):
        self.audio.say("this is a test")
        self.assertTrue(True)

    def test_record_to_file(self):        
        self.audio.record_to_file(FILENAME, 3)
        self.assertTrue(os.path.isfile(os.path.join(audio.SOUNDDIR, FILENAME)))

    def test_play(self):
        self.audio.play(FILENAME)
        self.assertTrue(True)

    def test_hear(self):
        self.assertTrue(True)

