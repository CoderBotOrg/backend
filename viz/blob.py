import cv2

class Blob():

    def __init__(self, contour):
        self._contour = contour

    @property
    def bottom(self):
        return self._contour[self._contour[:,:,1].argmax()][0][1]

    @property
    def top(self):
        return self._contour[self._contour[:,:,1].argmin()][0][1]

    @property
    def left(self):
        return self._contour[self._contour[:,:,0].argmin()][0][0]

    @property
    def right(self):
        return self._contour[self._contour[:,:,0].argmax()][0][0]

    @property
    def center(self):
        return ((self.right + self.left) / 2, (self.top + self.bottom) / 2)

    def area(self):
        return cv2.contourArea(self._contour)

    @classmethod
    def sort_distance(cls, point, blobs):
      return sorted(blobs, key=lambda blob: (point[0] - blob.bottom))
