############################################################################
#    CoderBot, a didactical programmable robot.
#    Copyright (C) 2014, 2015 Roberto Previtera <info@coderbot.org>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
############################################################################

import numpy as np
import cv2
import colorsys
import copy
import blob
import logging

tesseract_whitelists = {
  'alpha': "ABCDEFGHIJKLMNOPQRSTUVXYZ ",
  'num': "1234567890 ",
  'alphanum': "ABCDEFGHIJKLMNOPQRSTUVXYZ1234567890 ",
  'unspec': "abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVXYZ1234567890 ",
}

try:
  ocr = cv2.text.OCRTesseract_create(".", "eng", tesseract_whitelist['unspec'], 0, cv2.text.OCR_LEVEL_TEXTLINE)
except:
  logging.info("tesseract not availabe")

MIN_MATCH_COUNT = 10

class Image():
    r_from = np.float32([[0, 0], [640, 0], [640, 480], [0, 480]])
    r_dest   = np.float32([[0, -120], [640, -120], [380, 480], [260, 480]])

    #_face_cascade = cv2.CascadeClassifier('/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml')
    _face_cascade = cv2.CascadeClassifier('/usr/local/share/OpenCV/lbpcascades/lbpcascade_frontalface.xml')

    def __init__(self, array):
      self._data = array
      img_size_y = self._data.shape[0]
      kernel_size = img_size_y / 40 
      self._kernel = np.ones((kernel_size, kernel_size),np.uint8)

    def size(self):
      return self._data.shape

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
    def transform(cls, vector, tx):
      v = np.array(vector, dtype='float32')
      v = np.array([v])
      dest = cv2.perspectiveTransform(v, tx)
      return dest[0]

    @classmethod
    def get_transform(cls, image_size_x):
      k = 640 / image_size_x
      rfrom = cls.r_from / k
      rdest = cls.r_dest / k
      tx = cv2.getPerspectiveTransform(rfrom, rdest)
      return tx

    def find_faces(self):
      faces = self._face_cascade.detectMultiScale(self._data)
      return faces

    def filter_color(self, color):
      h, s, v = colorsys.rgb_to_hsv(color[0]/255.0, color[1]/255.0, color[2]/255.0)
      image_hsv = cv2.cvtColor(self._data, cv2.COLOR_BGR2HSV)
      h = h * 180
      s = s * 255
      v = v * 255
      logging.debug("color_hsv: " + str(h) + " " + str(s) + " " + str(v))
      #lower_color = np.array([h-10 if h>=10 else 0.0, 0, 0])
      #upper_color = np.array([h+10 if h<=170 else 179.0, 255, 255])
      lower_color = np.array([h-5, 50, 50])
      upper_color = np.array([h+5, 255, 255])
      logging.debug("lower: " + str(lower_color) + " upper: " + str(upper_color))
      mask = cv2.inRange(image_hsv, lower_color, upper_color)
      return Image(mask)

    def dilate(self):
      data = cv2.dilate(self._data, self._kernel)
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
      data = cv2.cvtColor(self._data, cv2.COLOR_BGR2GRAY)
      return Image(data)

    def invert(self):
      data = cv2.bitwise_not(self._data)
      return Image(data)

    def binarize(self, threshold = -1):
      data = cv2.cvtColor(self._data, cv2.COLOR_BGR2GRAY)
      #data = cv2.adaptiveThreshold(data, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 0)
      if threshold < 0:
        data = cv2.adaptiveThreshold(data, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, max((self._kernel.shape[0]/2*2)+1, 3), 3)
      else:
        ret, data = cv2.threshold(data, threshold, 255, cv2.THRESH_BINARY_INV)
      return Image(data)

    def find_blobs(self, minsize=0, maxsize=10000000):
      blobs = []
      image = contours = hyerarchy = None
      if "2.4" in cv2.__version__:
         contours, hyerarchy = cv2.findContours(self._data, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
      else:
        image, contours, hyerarchy = cv2.findContours(self._data, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

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
        logging.info("found template: " + dst)
        templates[0] = dst

      else:
        logging.info( "Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT))
        matchesMask = None
        
      return templates

    def find_rect(self, color):
      rect_image = None
      filtered_image = self.filter_color(color)
      blobs = filtered_image.find_blobs(minsize=1000)
      logging.info("blobs: " + str(blobs))
      if len(blobs):
        blob = blobs[0]
        b_area = blob.area()
        for b in blobs:
          if b.area() > b_area:
            blob = b
            b_area = blob.area() 
        rect = blob.minAreaRect()
        center = rect[0]
        size = rect[1]
        angle = rect[2]
        if size[0] < size[1]:
          angle = angle + 90
          size = (size[1], size[0])
  
        rot_matrix = cv2.getRotationMatrix2D(center, angle, 1)
        logging.info("center: " + str(center) + " size: " + str(size) + " angle: " + str(angle))
        rect_image = Image(cv2.warpAffine(self._data, rot_matrix, (160, 120)))
        border = 5
        rect_image = rect_image.crop(int(max(0,border+center[0]-(size[0])/2)), int(max(0,border+center[1]-(size[1]+5)/2)), int(min(160,-border+center[0]+(size[0])/2)), int(min(120,-border+center[1]+(size[1]-5)/2))) 
      return rect_image 
             
    def find_text(self, accept):
      wlist = tesseract_whitelists.get(accept, None)
      t = time.time()
      ocr.setWhiteList(wlist)
      text = ocr.run(self._data, 60)
      logging.info("time: " + str(time.time() - t)  + " text: " +str(text))
      return text

    def to_jpeg(self):
      ret, jpeg_array = cv2.imencode('.jpeg', self._data)
      return np.array(jpeg_array).tostring()


