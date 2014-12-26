import numpy as np
import cv2
import colorsys
import copy
import blob

r_from = np.float32([[0, 0], [160, 0], [160, 120], [0, 120]])
r_dest   = np.float32([[0, -30], [160, -30], [95, 120], [65, 120]])

class Image():

    def __init__(self, array):
      self._data = array

    def resize(self, width, heigth):
      return Image(cv2.resize(self._data, (width, heigth)))

    def crop(self, x, y, x1, y1):
      self._data = self._data[x:y, x1-x:y1-y]

    def warp(self, r_from, r_dest):
      tx = cv2.getPerspectiveTransform(r_from, r_dest)
      dest = cv2.warpPerspective(self._data, tx, (640,480))
      return Image(dest)

    def transform(self, x, y):
      tx = cv2.getPerspectiveTransform(r_from, r_dest)
      v = np.array([[x, y]], dtype='float32')
      v = np.array([v])
      dest = cv2.perspectiveTransform(v, tx)
      print dest
      dest = dest[0][0]
      return dest[0], dest[1]

    def find_faces(self):
      face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
      faces = face_cascade.detectMultiScale(self._data)
      return faces

    def filter_color(self, color):
      h, s, v = colorsys.rgb_to_hsv(color[0]/255.0, color[1]/255.0, color[2]/255.0)
      image_hsv = cv2.cvtColor(self._data, cv2.COLOR_BGR2HSV)
      h = h * 180
      s = s * 255
      v = v * 255
      print h, s, v
      #print str(image_hsv.shape)
      lower_color = np.array([h-10, s-80, v-80])
      upper_color = np.array([h+10, s+80, v+80])
      mask = cv2.inRange(image_hsv, lower_color, upper_color)
      return Image(mask)


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

    def to_jpeg(self):
      ret, jpeg_array = cv2.imencode('.jpeg', self._data)
      return np.array(jpeg_array).tostring()

