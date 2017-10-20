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

    def minAreaRect(self):
        return cv2.minAreaRect(self._contour)

    @classmethod
    def sort_distance(cls, point, blobs):
        return sorted(blobs, key=lambda blob: (point[0] - blob.bottom))
