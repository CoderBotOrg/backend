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
This module implements the class CNNManager, a singleton which exposes
methods used to create (retrain), list and use existing CNN models.
"""
import os
import shutil
import logging
import json
import threading

try:
    from cnn_train import CNNTrainer
except:
    logging.warning("tensorflow not available (for training)")

from cnn_classifier import CNNClassifier

MODEL_PATH = "./cnn_models"
MODEL_TMP_PATH = "/tmp/images"
MODEL_METADATA = "./cnn_models/models.json"
PHOTO_PATH = "./photos"

logger = logging.getLogger(__name__)

class CNNManager(object):
    instance = None

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = CNNManager()
        return cls.instance


    def __init__(self):
        try:
            f = open(MODEL_METADATA, "r")
            self._models = json.load(f)
            f.close()
        except IOError:
            self._models = {}
            self._save_model_meta()

        self._trainers = {}

    def get_models(self):
        return self._models

    def get_model_status(self, model_name):
        return self._models[model_name]

    @classmethod
    def get_model_info(cls, architecture):
        model_info = architecture.split("/")[1].split("_")
        return model_info

    @classmethod
    def get_model_shape(cls, architecture):
        model_info = cls.get_model_info(architecture)
        size = int(model_info[3])
        return (size, size)

    def _save_model_meta(self):
        f = open(MODEL_METADATA, "w")
        json.dump(self._models, f)
        f.close()

    def delete_model(self, model_name):
        if self._models.get(model_name):
            try:
                os.remove(MODEL_PATH + "/" + model_name + ".tflite")
                os.remove(MODEL_PATH + "/" + model_name + ".txt")
            except Exception:
                logging.warning("model files not found: %s", model_name)
            del self._models[model_name]
            self._save_model_meta()

    def train_new_model(self,
                        model_name,
                        architecture,
                        image_tags,
                        photos_meta,
                        training_steps,
                        learning_rate):

        logging.info("starting")
        trainer = self.TrainThread(self, model_name, architecture, image_tags, photos_meta, training_steps, learning_rate)
        trainer.start()
        self._trainers[model_name] = trainer

    def save_model_status(self, model_name, architecture, status):
        model_info = self.get_model_info(architecture)
        self._models[model_name] = {"status": status, "image_height": model_info[3], "image_width": model_info[3], "output_layer": "final_result"}
        self._save_model_meta()

    def wait_train_jobs(self):
        for t in self._trainers:
            t.join()

    def load_model(self, model_name):
        model_info = self._models.get(model_name)
        if model_info:
            return CNNClassifier(model_file=MODEL_PATH + "/" + model_name + ".tflite",
                                 label_file=MODEL_PATH + "/" + model_name + ".txt")
        return None

    class TrainThread(threading.Thread):

        def __init__(self, manager, model_name, architecture, image_tags, photos_metadata, training_steps, learning_rate):
            super(CNNManager.TrainThread, self).__init__()
            self.manager = manager
            self.model_name = model_name
            self.architecture = architecture
            self.image_tags = image_tags
            self.photos_metadata = photos_metadata
            self.learning_rate = learning_rate
            self.training_steps = training_steps
            self.trainer = None

        def update_train_status(self, model_name, status):
            model = self.manager._models.get(model_name)
            model["status"] = status

        def run(self):
            self.trainer = CNNTrainer(self.manager, self.architecture, CNNManager.get_model_shape(self.architecture))
            self.manager.save_model_status(self.model_name, self.architecture, 0)
            image_dir = self.prepare_images()
            logging.info("retrain")
            self.trainer.retrain(image_dir, MODEL_PATH + "/" + self.model_name, self.training_steps, self.learning_rate, flip_left_right=False, random_crop=0, random_scale=0)
            self.manager.save_model_status(self.model_name, self.architecture, 1)
            self.clear_filesystem()
            logging.info("finish")

        def prepare_images(self):
            logging.info("prepare_images")
            photo_abs_path = os.path.abspath(PHOTO_PATH)
            model_image_path = MODEL_TMP_PATH + "/" + self.model_name
            os.makedirs(model_image_path)
            for t in self.image_tags:
                tag_path = model_image_path + "/" + t
                os.makedirs(tag_path)
                for p in self.photos_metadata:
                    if p.get("tag", "---") == t:
                        os.symlink(photo_abs_path + "/" + p["name"], tag_path + "/" + p["name"])

            return model_image_path

        def clear_filesystem(self):
            shutil.rmtree(MODEL_TMP_PATH + "/" + self.model_name)
            #shutil.rmtree(MODEL_TMP_PATH + "/bottleneck")
            #shutil.rmtree(MODEL_TMP_PATH + "/retrain_logs")
