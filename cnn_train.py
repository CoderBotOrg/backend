############################################################################
#    CoderBot, a didactical programmable robot.
#    Copyright (C) 2014, 2017 Roberto Previtera <info@coderbot.org>
#    The code contained in this file is mostly derived from TensorFlow
#    "retrain.py" exmple from main tensorflow repository.
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
"""Simple transfer learning with Inception v3 or Mobilenet models.

With support for TensorBoard.

This example shows how to take a Inception v3 or Mobilenet model trained on
ImageNet images, and train a new top layer that can recognize other classes of
images.

The top layer receives as input a 2048-dimensional vector (1001-dimensional for
Mobilenet) for each image. We train a softmax layer on top of this
representation. Assuming the softmax layer contains N labels, this corresponds
to learning N + 2048*N (or 1001*N)  model parameters corresponding to the
learned biases and weights.

Here's an example, which assumes you have a folder containing class-named
subfolders, each full of images for each label. The example folder flower_photos
should have a structure like this:

~/flower_photos/daisy/photo1.jpg
~/flower_photos/daisy/photo2.jpg
...
~/flower_photos/rose/anotherphoto77.jpg
...
~/flower_photos/sunflower/somepicture.jpg
"""

import time
import tempfile
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from tensorflow_hub.tools.make_image_classifier import make_image_classifier_lib as lib

class CNNTrainer(object):
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-boolean-expressions

    def __init__(self, manager, architecture, shape):
        self.manager = manager
        self.architecture = architecture
        self.shape = shape

    def retrain(self,
                image_dir,
                output_graph,
                training_steps,
                learning_rate,
                desired_training_accuracy=100.0,
                desired_validation_accuracy=100.0,
                flip_left_right=True,
                random_crop=30,
                random_scale=30,
                random_brightness=30):

        _check_keras_dependencies()
        hparams = _get_hparams(train_epochs=training_steps,
                               learning_rate=learning_rate)

        image_size=self.shape[0]
        tfhub_module="https://tfhub.dev/google/"+self.architecture
        model, labels, train_result = lib.make_image_classifier(
            tfhub_module, image_dir, hparams, image_size)
        print("Done with training.")

        labels_output_file=output_graph+".txt"
        with tf.io.gfile.GFile(labels_output_file, "w") as f:
            f.write("\n".join(labels + ("",)))
            print("Labels written to", labels_output_file)

        saved_model_dir = tempfile.mkdtemp()
        tf.saved_model.save(model, saved_model_dir)
        print("SavedModel model exported to", saved_model_dir)

        tflite_output_file = output_graph+".tflite"
        converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
        converter.optimizations = [tf.lite.Optimize.OPTIMIZE_FOR_LATENCY]
        lite_model_content = converter.convert()
        with tf.io.gfile.GFile(tflite_output_file, "wb") as f:
            f.write(lite_model_content)
            print("TFLite model exported to", tflite_output_file)


def _get_hparams(train_epochs=1, learning_rate=0.005):
  "Creates dict of hyperparameters from flags."""
  return lib.HParams(
    train_epochs=train_epochs,
    do_fine_tuning=False,
    batch_size=1,
    learning_rate=learning_rate,
    momentum=0.9)

def _check_keras_dependencies():
  """Checks dependencies of tf.keras.preprocessing.image are present.
  This function may come to depend on flag values that determine the kind
  of preprocessing being done.
  Raises:
    ImportError: If dependencies are missing.
  """
  try:
    tf.keras.preprocessing.image.load_img(six.BytesIO())
  except ImportError:
    print("\n*** Unsatisfied dependencies of keras_preprocessing.image. ***\n"
          "To install them, use your system's equivalent of\n"
          "pip install tensorflow_hub[make_image_classifier]\n")
    raise
  except Exception as e:  # pylint: disable=broad-except
    # Loading from dummy content as above is expected to fail in other ways.
    pass


def _assert_accuracy(train_result, assert_accuracy_at_least):
  # Fun fact: With TF1 behavior, the key was called "val_acc".
  val_accuracy = train_result.history["val_accuracy"][-1]
  accuracy_message = "found {:f}, expected at least {:f}".format(
      val_accuracy, assert_accuracy_at_least)
  if val_accuracy >= assert_accuracy_at_least:
    print("ACCURACY PASSED:", accuracy_message)
  else:
    raise AssertionError("ACCURACY FAILED:", accuracy_message)

