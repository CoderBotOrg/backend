import unittest
import time
import os
import picamera_mock
import picamera
import camera
import config

class CameraTest(unittest.TestCase):
    def setUp(self):
        settings = config.Config.read().get('settings')
        picamera.PiCamera = picamera_mock.PiCameraMock
        self.cam = camera.Camera.get_instance(settings)
   
    def tearDown(self):
        self.cam.exit()
        camera.Camera._instance = None

    def test_take_picture_jpeg(self):
        pic = self.cam.get_image_jpeg()
        self.assertTrue(pic is not None)

    def test_take_picture_bgr(self):
        pic = self.cam.get_image()
        self.assertTrue(pic is not None)

    def test_video_rec(self):
        video_filename = "video_test"
        self.cam.video_rec(video_filename)
        time.sleep(5)
        self.cam.video_stop()
        v = open("data/media/VID" + video_filename + ".mp4")
        t = open("data/media/VID" + video_filename + "_thumb.jpg")
        self.assertTrue(v is not None and t is not None)
        v.close()
        t.close()
        os.remove("data/media/VID" + video_filename + ".mp4")
        os.remove("data/media/VID" + video_filename + "_thumb.jpg")

    def test_find_color(self):
        color = 'ff0000'
        dist, angle = self.cam.find_color(color)
        self.assertTrue(dist > 0 and angle < 180)
