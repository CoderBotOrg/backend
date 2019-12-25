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
        os.system("wget https://github.com/CoderBotOrg/test-data/raw/master/dnn-images/coderbot-dnn-test-images-02.tar.xz")
        os.system("tar xJf coderbot-dnn-test-images-02.tar.xz")
        os.system("rm coderbot-dnn-test-images-02.tar.xz")
        cnn = cnn_manager.CNNManager.get_instance()

    def tearDown(self):
        os.system("rm -rf photos")
        os.system("mv saved_photos photos")
        cnn = cnn_manager.CNNManager.get_instance()
        name="test_model_1"
        cnn.delete_model(name)
        name="test_model_2"
        cnn.delete_model(name)

    def test_1_train_set_1(self):
        name="test_model_1"
        cam = camera.Camera.get_instance()
        cnn = cnn_manager.CNNManager.get_instance()
        cnn.train_new_model(model_name=name,
                            architecture="imagenet/mobilenet_v2_100_160/feature_vector/4",
                            image_tags=["orange","apple","other"],
                            photos_meta=cam.get_photo_list(),
                            training_steps=5,
                            learning_rate=0.0001)
        start = time.time()
        while True:
            model_status = cnn.get_models().get(name, {"status": 0})
            if model_status.get("status") == 1 or time.time() - start > 6000:
                break
            time.sleep(1)
        self.assertTrue(cnn.get_models().get(name).get("status") == 1.0)
        mod = cnn.load_model(name)
        result = mod.classify_image("photos/DSC1.jpg")
        print("result: " + str(result))
        self.assertTrue(result[0][0] == "orange" and result[0][1] > 40)
        result = mod.classify_image("photos/DSC201.jpg")
        print("result: " + str(result))
        #self.assertTrue(result[0][0] == "apple" and result[0][1] > 40)
        result = mod.classify_image("photos/DSC301.jpg")
        print("result: " + str(result))
        #self.assertTrue(result[0][0] == "other" and result[0][1] > 40)
        t1 = time.time()
        iterations = 20
        for x in range(iterations):
            result = mod.classify_image("photos/DSC1.jpg")
        print("result: " + str(result) + " fps: " + str(1.0*iterations/(time.time()-t1)))
        cnn.delete_model(name)
        self.assertTrue(cnn.get_models().get(name) is None)

    def test_2_train_set_2(self):
        name="test_model_2"
        cam = camera.Camera.get_instance()
        cnn = cnn_manager.CNNManager.get_instance()
        cnn.train_new_model(model_name=name,
                            architecture="imagenet/mobilenet_v2_050_160/feature_vector/4",
                            image_tags=["orange","apple","other"],
                            photos_meta=cam.get_photo_list(),
                            training_steps=1,
                            learning_rate=0.005)
        start = time.time()
        while True:
            model_status = cnn.get_models().get(name, {"status": 0})
            if model_status.get("status") == 1 or time.time() - start > 6000:
                break
            time.sleep(1)
        self.assertTrue(cnn.get_models().get(name).get("status") == 1.0)

        mod = cnn.load_model(name)
        result = mod.classify_image("photos/DSC1.jpg")
        print("result: " + str(result))
        self.assertTrue(result[0][0] == "orange" and result[0][1] > 40)

    def test_3_classify_1(self):
        cnn = cnn_manager.CNNManager.get_instance()
        mod = cnn.load_model('base_high_slow')
        t1 = time.time()
        iterations = 20
        for x in range(iterations):
            result = mod.classify_image("photos/DSC201.jpg")
        print("result: " + str(result) + " fps: " + str(1.0*iterations/(time.time()-t1)))
        self.assertTrue(len(result) and result[0][0] == "Granny Smith" and result[0][1] > 50)

    def test_4_classify_2(self):
        cnn = cnn_manager.CNNManager.get_instance()
        mod = cnn.load_model('base_low_fast')
        t1 = time.time()
        iterations = 20
        for x in range(iterations):
            result = mod.classify_image("photos/DSC201.jpg")
        print("result: " + str(result) + " fps: " + str(1.0*iterations/(time.time()-t1)))
        self.assertTrue(len(result) and result[0][0] == "Granny Smith" and result[0][1] > 50)

    def test_5_detect_objects_1(self):
        cnn = cnn_manager.CNNManager.get_instance()
        mod = cnn.load_model('object_detect')
        t1 = time.time()
        iterations = 20
        for x in range(iterations):
            result = mod.detect_objects("photos/DSC201.jpg")
        print("result: " + str(result) + " fps: " + str(1.0*iterations/(time.time()-t1)))
        self.assertTrue(len(result) and result[0] == ('apple', 78, (18, 10, 72, 82)))
