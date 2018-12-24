import unittest
import time
import os
import config
import camera
import cnn_manager

class CNNTest(unittest.TestCase):
    def setUp(self):
        config.Config.read()
        os.system("mv photos saved_photos")
        os.system("wget https://github.com/CoderBotOrg/test-data/raw/master/dnn-images/coderbot-dnn-test-images-01.tar.xz")
        os.system("tar xJf coderbot-dnn-test-images-01.tar.xz")
        os.system("rm coderbot-dnn-test-images-01.tar.xz")
        cnn = cnn_manager.CNNManager.get_instance()

    def tearDown(self):
        os.system("rm -rvf photos")
        os.system("mv saved_photos photos")

    def test_train_set_1(self):
        name="test_model_1"
        cam = camera.Camera.get_instance()
        cnn = cnn_manager.CNNManager.get_instance()
        cnn.train_new_model(model_name=name,
                            architecture="mobilenet_v1_0.50_128",
                            image_tags=["other","tomato","apple","kiwi"],
                            photos_meta=cam.get_photo_list(),
                            training_steps=20,
                            learning_rate=0.1)
        start = time.time()
        while True:
            model_status = cnn.get_models().get(name, {"status": 0})
            if model_status.get("status") == 1 or time.time() - start > 6000:
                break
            print("status: " + str(model_status["status"]))
            time.sleep(1)
        self.assertTrue(cnn.get_models().get(name).get("status") == 1.0)

        name="test_model_1"
        cnn = cnn_manager.CNNManager.get_instance()
        mod = cnn.load_model(name)
        result = mod.classify_image("photos/DSC86.jpg")
        print("result: " + str(result))
        self.assertTrue(result["kiwi"] == 1.0)

        name="test_model_1"
        cnn = cnn_manager.CNNManager.get_instance()
        cnn.delete_model(name)
        self.assertTrue(cnn.get_models().get(name) is None)

    def test_train_set_2(self):
        name="test_model_2"
        cam = camera.Camera.get_instance()
        cnn = cnn_manager.CNNManager.get_instance()
        cnn.train_new_model(model_name=name,
                            architecture="mobilenet_v2_0.5_128",
                            image_tags=["other","tomato","apple","kiwi"],
                            photos_meta=cam.get_photo_list(),
                            training_steps=20,
                            learning_rate=0.1)
        start = time.time()
        while True:
            model_status = cnn.get_models().get(name, {"status": 0})
            if model_status.get("status") == 1 or time.time() - start > 6000:
                break
            print("status: " + str(model_status["status"]))
            time.sleep(1)
        self.assertTrue(cnn.get_models().get(name).get("status") == 1.0)

        cnn = cnn_manager.CNNManager.get_instance()
        mod = cnn.load_model(name)
        result = mod.classify_image("photos/DSC86.jpg")
        print("result: " + str(result))
        self.assertTrue(result["kiwi"] >= 0.9)

        cnn = cnn_manager.CNNManager.get_instance()
        cnn.delete_model(name)
        self.assertTrue(cnn.get_models().get(name) is None)
