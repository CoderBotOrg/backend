import json

CONFIG_FILE = "coderbot.cfg"

class Config:

  _config = {}

  @classmethod
  def get(cls):
    return cls._config

  @classmethod
  def read(cls):
    f = open(CONFIG_FILE, 'r')
    cls._config = json.load(f)
    return cls._config
  
  @classmethod
  def write(cls, config):
    cls._config = config
    f = open(CONFIG_FILE, 'w')
    json.dump(cls._config, f)
    return cls._config

