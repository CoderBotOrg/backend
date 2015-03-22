import numpy as np
import cv2
import colorsys
import copy
import blob

r_from = np.float32([[0, 0], [160, 0], [160, 120], [0, 120]])
r_dest   = np.float32([[0, -30], [160, -30], [95, 120], [65, 120]])
MIN_MATCH_COUNT = 10

class Image():
    #_face_cascade = cv2.CascadeClassifier('/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml')
    _face_cascade = cv2.CascadeClassifier('/usr/local/share/OpenCV/lbpcascades/lbpcascade_frontalface.xml')
    _kernel = np.ones((3,3),np.uint8)

    def __init__(self, array):
      self._data = array

    @classmethod
    def load(cls, filename):
      return Image(cv2.imread(filename))

    def resize(self, width, heigth):
      return Image(cv2.resize(self._data, (width, heigth)))

    def crop(self, x1, y1, x2, y2):
      return Image(self._data[y1:y2,x1:x2])

    def warp(self, r_from, r_dest):
      tx = cv2.getPerspectiveTransform(r_from, r_dest)
      dest = cv2.warpPerspective(self._data, tx, (640,480))
      return Image(dest)

    @classmethod
    def transform(cls, vector):
      tx = cv2.getPerspectiveTransform(r_from, r_dest)
      v = np.array(vector, dtype='float32')
      v = np.array([v])
      dest = cv2.perspectiveTransform(v, tx)
      return dest[0]

    def find_faces(self):
      faces = self._face_cascade.detectMultiScale(self._data)
      return faces

    def filter_color(self, color):
      h, s, v = colorsys.rgb_to_hsv(color[0]/255.0, color[1]/255.0, color[2]/255.0)
      image_hsv = cv2.cvtColor(self._data, cv2.COLOR_BGR2HSV)
      h = h * 180
      s = s * 255
      v = v * 255
      #print str(image_hsv.shape)
      lower_color = np.array([h-10, s-80, v-80])
      upper_color = np.array([h+10, s+80, v+80])
      mask = cv2.inRange(image_hsv, lower_color, upper_color)
      return Image(mask)

    def dilate(self):
      data = cv2.dilate(self._datai, self._kernel)
      return Image(data)

    def erode(self):
      data = cv2.erode(self._data, self._kernel)
      return Image(data)
  
    def open(self):
      data = cv2.morphologyEx(self._data, cv2.MORPH_OPEN, self._kernel)
      return Image(data)
  
    def close(self):
      data = cv2.morphologyEx(self._data, cv2.MORPH_CLOSE, self._kernel)
      return Image(data)
  
    def grayscale(self):
      data = cv2.cvtColor(self._data, cv2.cv.CV_BGR2GRAY)
      return Image(data)

    def invert(self):
      data = cv2.bitwise_not(self._data)
      return Image(data)

    def binarize(self):
      data = cv2.cvtColor(self._data, cv2.cv.CV_BGR2GRAY)
      data = cv2.adaptiveThreshold(data, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 5, 3)
      return Image(data)

    def find_blobs(self, minsize=0, maxsize=10000000):
      blobs = []
      contours, hyerarchy = cv2.findContours(self._data, cv2.cv.CV_RETR_TREE, cv2.cv.CV_CHAIN_APPROX_SIMPLE)
      for c in contours:
        area = cv2.contourArea(c)
        if area > minsize and area < maxsize:
	  if len(blobs) and area > blobs[0].area:
            blobs.insert(0, blob.Blob(c))
          else:  
	    blobs.append(blob.Blob(c))
          
      return blobs

    def find_template(self, img_template):
      # Initiate SIFT detector
      sift = cv2.SIFT()

      # find the keypoints and descriptors with SIFT
      kp1, des1 = sift.detectAndCompute(img_template._data,None)
      kp2, des2 = sift.detectAndCompute(self._data,None)

      FLANN_INDEX_KDTREE = 0
      index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
      search_params = dict(checks = 50)

      flann = cv2.FlannBasedMatcher(index_params, search_params)

      matches = flann.knnMatch(des1,des2,k=2)

      # store all the good matches as per Lowe's ratio test.
      good = []
      templates = []
      for m,n in matches:
        if m.distance < 0.7*n.distance:
          good.append(m)      

      if len(good) > MIN_MATCH_COUNT:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
        matchesMask = mask.ravel().tolist()

        h,w = img_template.shape
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts,M)
        print "found template: ", dst
        templates[0] = dst

      else:
        print "Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT)
        matchesMask = None
        
      return templates
      

    def to_jpeg(self):
      ret, jpeg_array = cv2.imencode('.jpeg', self._data)
      return np.array(jpeg_array).tostring()


