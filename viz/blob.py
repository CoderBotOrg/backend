import cv2

class Blob():

    def __init__(self, contour):
        self._contour = contour

    @property
    def bottom(self):
        return tuple(self._contour[self._contour[:,:,1].argmax()][0])

    def area(self):
        return cv2.contourArea(self._contour)

