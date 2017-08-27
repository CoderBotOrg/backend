import config
import camera
import cnn_classifier
import cv2 as cv
 
config = config.Config.read()
cam = camera.Camera.get_instance()
classifier = cnn_classifier.CNNClassifier("models/applekiwi.pb", "models/applekiwi.txt", "input", "final_result")


while True:
  i = cam.get_image().resize(128, 128).mat()
  results = classifier.classify_image(i, 128, 128)
  print "results: " + str(results)


