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
    def __init__(self, model_file, label_file, input_layer="input", output_layer="final_result", input_height=128, input_width=128, input_mean=127.5, input_std=127.5):
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
        #input_name = "import/" + input_layer
        #output_name = "import/" + output_layer
        #self._input_operation = self._graph.get_operation_by_name(input_name)
        #self._output_operation = self._graph.get_operation_by_name(output_name)
        #self._session = tf.compat.v1.Session(graph=self._graph)
        #self._graph_norm = tf.Graph()
        #with self._graph_norm.as_default():
        #    image_mat = tf.compat.v1.placeholder(tf.float32, None, name="image_rgb_in")
        #    float_caster = tf.cast(image_mat, tf.float32)
        #    dims_expander = tf.expand_dims(float_caster, 0)
        #    resized = tf.compat.v1.image.resize_bilinear(dims_expander, [input_height, input_width])
        #    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std], name="image_norm_out")
        #    self._input_operation_norm = self._graph_norm.get_operation_by_name("image_rgb_in")
        #    self._output_operation_norm = self._graph_norm.get_operation_by_name("image_norm_out")
        #self._sess_norm = tf.Session(graph=self._graph_norm)

    def close(self):
        pass
        #self._session.close()
        #self._sess_norm.close()

    #def load_graph(self, model_file):
    #   graph = tf.Graph()
    #    graph_def = tf.compat.v1.GraphDef()
    #
    #    with open(model_file, "rb") as f:
    #        graph_def.ParseFromString(f.read())
    #    with graph.as_default():
    #        tf.import_graph_def(graph_def)
    #
    #    return graph
    #
    #def read_tensor_from_image_file(self, file_name, input_height=299, input_width=299, input_mean=0, input_std=255):
    #    input_name = "file_reader"
    #    output_name = "normalized"
    #
    #    file_reader = tf.read_file(file_name, input_name)
    #
    #    if file_name.endswith(".png"):
    #        image_reader = tf.image.decode_png(file_reader, channels=3, name='png_reader')
    #    elif file_name.endswith(".gif"):
    #        image_reader = tf.squeeze(tf.image.decode_gif(file_reader, name='gif_reader'))
    #    elif file_name.endswith(".bmp"):
    #        image_reader = tf.image.decode_bmp(file_reader, name='bmp_reader')
    #    else:
    #        image_reader = tf.image.decode_jpeg(file_reader, channels=3, name='jpeg_reader')
    #
    #    float_caster = tf.cast(image_reader, tf.float32)
    #    dims_expander = tf.expand_dims(float_caster, 0);
    #    resized = tf.image.resize_bilinear(dims_expander, [self.input_height, self.input_width])
    #    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    #    sess = tf.Session()
    #
    #    result = sess.run(normalized)
    #    sess.close()
    #
    #    return result
    #
    #def read_tensor_from_image_mat(self, image_mat, input_height=299, input_width=299, input_mean=0, input_std=255):
    #    result = self._sess_norm.run(self._output_operation_norm.outputs[0], {self._input_operation_norm.outputs[0]: image_mat})
    #    return result
    def read_tensor_from_image_mat(self, image_mat, input_height=299, input_width=299, input_mean=0, input_std=255):
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
        #if isinstance(image_file_or_mat, str):
        #    t = self.read_tensor_from_image_file(file_name=image_file_or_mat)
        #else:
        input_image = self.read_tensor_from_image_mat(image_file_or_mat)

        logger.info("classify.0")
        self._interpreter.set_tensor(self._input_details[0]['index'], input_image)
        self._interpreter.invoke()
        logger.info("classify.1")
        scores = self._interpreter.get_tensor(self._output_details[0]['index'])[0] # Bounding box coordinates of detected objects
        #logger.info("classify.2")
        #classes = self._interpreter.get_tensor(self._output_details[1]['index'])[0] # Class index of detected objects
        #logger.info("classify.3")
        #scores = self._interpreter.get_tensor(self._output_details[2]['index'])[0] # Confidence of detected objects
        #logger.info("classify.4")

        #pairs = [(classes[i], scores[i], boxes[i]) for i in range(0, len(classes))]
        pairs = []
        for i in range(0, len(scores)):
            if scores[i] > 0.5:
                object_name = self._labels[i]
                pairs.append((object_name, scores[i]))

        logger.info(str(pairs))
        return pairs
