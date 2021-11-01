############################################################################
#    CoderBot, a didactical programmable robot.
#    Copyright (C) 2014, 2017 Roberto Previtera <info@coderbot.org>
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
"""
This module implements the CNNClassifier class, which is the interface for
using an existing and trained CNN model.
"""
import logging

import numpy as np
from tensorflow.lite.python.interpreter import Interpreter
import cv2

logger = logging.getLogger(__name__)

class CNNClassifier(object):
    def __init__(self, model_file, label_file):
        logger.info(model_file)
        self._interpreter = Interpreter(model_path=model_file)
        self._interpreter.set_num_threads(4)
        self._interpreter.allocate_tensors()
        self._labels = self.load_labels(label_file)
        self._input_details = self._interpreter.get_input_details()
        self._output_details = self._interpreter.get_output_details()
        self._input_height=self._input_details[0]['shape'][1]
        self._input_width=self._input_details[0]['shape'][2]
        self._floating_model = (self._input_details[0]['dtype'] == np.float32)

    def close(self):
        pass

    def read_tensor_from_image_file(self, file_name):
        image = cv2.imread(file_name)
        return self.read_tensor_from_image_mat(image)

    def read_tensor_from_image_mat(self, image_mat):
        frame_rgb = cv2.cvtColor(image_mat, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (self._input_width, self._input_height))
        input_data = np.expand_dims(frame_resized, axis=0)

        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
        if self._floating_model:
            input_mean = 127.5
            input_std = 127.5
            input_data = (np.float32(input_data) - input_mean) / input_std

        return input_data

    def load_labels(self, label_file):
        labels = []
        with open(label_file, 'r') as f:
            labels = [line.strip() for line in f.readlines()]
        return labels

    def classify_image(self,
                       image_file_or_mat,
                       top_results=3):
        input_image = None
        if isinstance(image_file_or_mat, str):
            input_image = self.read_tensor_from_image_file(file_name=image_file_or_mat)
        else:
            input_image = self.read_tensor_from_image_mat(image_file_or_mat)

        self._interpreter.set_tensor(self._input_details[0]['index'], input_image)
        self._interpreter.invoke()
        scores = self._interpreter.get_tensor(self._output_details[0]['index'])[0]

        #print("scores: " + str(scores))
        confidence = 0.4
        base = 1
        # normalize to int8 for quantized models
        if len(scores)>0 and (scores[0] == int(scores[0])):
            confidence = 128
            base = 256
        pairs = []
        for i in range(0, len(scores)):
            if scores[i] > confidence:
                object_name = self._labels[i]
                pairs.append((object_name, int(100*scores[i]/base)))

        pairs = sorted(pairs, key=lambda x: x[1], reverse=True)[:top_results]
        return pairs

    def detect_objects(self,
                       image_file_or_mat,
                       top_results=3):
        input_image = None
        if isinstance(image_file_or_mat, str):
            input_image = self.read_tensor_from_image_file(file_name=image_file_or_mat)
        else:
            input_image = self.read_tensor_from_image_mat(image_file_or_mat)

        self._interpreter.set_tensor(self._input_details[0]['index'], input_image)
        self._interpreter.invoke()

        # Retrieve detection results
        boxes = self._interpreter.get_tensor(self._output_details[0]['index'])[0] # Bounding box coordinates of detected objects
        classes = self._interpreter.get_tensor(self._output_details[1]['index'])[0] # Class index of detected objects
        scores = self._interpreter.get_tensor(self._output_details[2]['index'])[0] # Confidence of detected objects

        # Loop over all detections and draw detection box if confidence is above minimum threshold
        min_conf_threshold=0.1
        imH=100
        imW=100
        pairs = []
        for i in range(len(scores)):
            if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):

                # Get bounding box coordinates and draw box
                # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                ymin = int(max(1,(boxes[i][0] * imH)))
                xmin = int(max(1,(boxes[i][1] * imW)))
                ymax = int(min(imH,(boxes[i][2] * imH)))
                xmax = int(min(imW,(boxes[i][3] * imW)))

                object_name = self._labels[int(classes[i])+1]
                pairs.append((object_name, int(100*scores[i]), (xmin, ymin, xmax, ymax)))

        pairs = sorted(pairs, key=lambda x: x[1], reverse=True)[:top_results]
        logger.info(str(pairs))
        return pairs
