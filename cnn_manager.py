import os
import shutil
import logging
import json
import threading

from cnn_train import CNNTrainer

MODEL_PATH = "./cnn_models"
MODEL_TMP_PATH = "/tmp/images"
MODEL_METADATA = "./cnn_models/models.json"
PHOTO_PATH = "./photos"

class CNNManager:
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
      f.close
    except IOError:
      self._models = {}
      f = open(MODEL_METADATA, "w")
      json.dump(self._models, f)
      f.close
    self._trainers = {} 

  def get_models(self):
    return self._models

  def get_model_status(self, model_name):
    return self._models[model_name]

  def delete_model(self, model_name):
    if self._models.get(model_name):
      os.remove(MODEL_PATH + "/" + model_name + ".*")
      del self._models[model_name]    

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
    #trainer.join()
    
  def save_model(self, model_name, architecture):
    model_info = architecture.split("_")
    self._models[model_name] = {"status": 1, "image_height": model_info[2], "image_width": model_info[2]}
    f = open(MODEL_METADATA, "w")
    json.dump(self._models, f)
    f.close()

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
      self.trainer = CNNTrainer(architecture)

    def update_train_status(self, model_name, status):
      model = self.manager._models.get(model_name)
      model["status"] = status

    def run(self):
      image_dir = self.prepare_images()
      logging.info("retrain")
      self.trainer.retrain(image_dir, MODEL_PATH + "/" + self.model_name, self.training_steps, self.learning_rate)
      self.manager.save_model(self.model_name, self.architecture)
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

