import os
import sys
import threading
import json

import coderbot
import camera

PROGRAM_PATH = "./data/"
PROGRAM_PREFIX = "program_"
PROGRAM_SUFFIX = ".data"

class ProgramEngine:

  _instance = None

  def __init__(self):
    self._program = None
    self._repository = {}
    for dirname, dirnames, filenames,  in os.walk("./data"):
      for filename in filenames:
        if PROGRAM_PREFIX in filename:
          program_name = filename[len(PROGRAM_PREFIX):-len(PROGRAM_SUFFIX)]    
          self._repository[program_name] = filename
    
  @classmethod
  def get_instance(cls):
    if not cls._instance:
      cls._instance = ProgramEngine()
    return cls._instance

  def list(self):
    return self._repository.keys()
    
  def save(self, program):
    program = self._repository[program.name] = program
    f = open(PROGRAM_PATH + PROGRAM_PREFIX + program.name + PROGRAM_SUFFIX, 'w')
    json.dump(program.as_json(), f)
    f.close()
    
  def load(self, name):
    #return self._repository[name]
    f = open(PROGRAM_PATH + PROGRAM_PREFIX + name + PROGRAM_SUFFIX, 'r')
    return Program.from_json(json.load(f))

  def delete(self, name):
    del self._repository[name]
    os.remove(PROGRAM_PATH + PROGRAM_PREFIX + name + PROGRAM_SUFFIX)
    return "ok"

  def is_running(self, name):
    return self._repository[name].is_running()

class Program(threading.Thread):

  _running = False

  @property
  def dom_code(self):
    return self._dom_code

  def __init__(self, name, code=None, dom_code=None):
    super(Program, self).__init__()
    self.name = name
    self._dom_code = dom_code
    self._code = code 

  def execute(self):
    if self._running:
      raise RuntimeError('already running')

    print "execute.1"
    self._running = True

    try:
      self.start()
    except RuntimeError as re:
      print "RuntimeError:" + str(re)
    print "execute.2"
    return "ok"

  def end(self):
    self._running = False
    self.join()

  def check_end(self):
    if self._running == False:
      raise RuntimeError('end requested')

  def is_running(self):
    return self._running

  def run(self):
    try:
      print "run.1"
      bot = coderbot.CoderBot.get_instance()
      cam = camera.Camera.get_instance()
      program = self
      exec(self._code)
      print "run.2"
    except RuntimeError as re:
      print "quit: " + str(re)
    self._running = False

  def as_json(self):
    return {'name': self.name,
            'dom_code': self._dom_code,
            'code': self._code}

  @classmethod
  def from_json(cls, map):
    return Program(name=map['name'], dom_code=map['dom_code'], code=map['code'])
