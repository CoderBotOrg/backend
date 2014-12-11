import numpy as np
import cv2
import colorsys
import copy
import blob

class Image():

    @classmethod
    def from_bgr(cls, bgrarray):
      return Image(bgrarray)

    def __init__(self, array):
      self._data = array

    def resize(self, width, heigth):
      return Image(cv2.resize(self._data, (width, heigth)))

    def warp(self, r_from, r_dest):
      tx = cv2.getPerspectiveTransform(r_from, r_dest)
      dest = cv2.warpPerspective(self._data, tx, (640,480))
      return Image(dest)

    def find_face(self):
      face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
      faces = face_cascade.detectMultiScale(self._data)
      return faces

    def filter_color(self, color):
      color_hsv = colorsys.rgb_to_hsv(color[0], color[1], color[2])
      image_hsv = cv2.cvtColor(self._data, cv2.COLOR_BGR2HSV)
      lower_color = np.array([color_hsv[0], 50, 50])
      upper_color = np.array([color_hsv[0], 255, 255])
      image_mask = cv2.inRange(image_hsv, lower_color, upper_color)
      return Image(image_mask)


    def binarize(self):
      data = cv2.cvtColor(self._data, cv2.cv.CV_BGR2GRAY)
      data = cv2.adaptiveThreshold(data, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
      return Image(data)

    def find_blobs(self, minsize=0, maxsize=10000000):
      blobs = []
      contours, hyerarchy = cv2.findContours(self._data, cv2.cv.CV_RETR_TREE, cv2.cv.CV_CHAIN_APPROX_SIMPLE)
      for c in contours:
        area = cv2.contourArea(c)
        if area > minsize and area < maxsize:
          blobs.append(blob.Blob(c))
      return blobs

    def as_jpeg(self):
      ret, jpeg_array = cv2.imencode('.jpeg', self._data)
      return np.array(jpeg_array).tostring()

