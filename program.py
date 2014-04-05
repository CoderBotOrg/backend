import sys
import threading

import coderbot
import camera

class ProgramEngine:

  _instance = None

  def __init__(self):
    self._program = None
    self._repository = {}
  
  @classmethod
  def get_instance(cls):
    if not cls._instance:
      cls._instance = ProgramEngine()
    return cls._instance

  def list(self):
    return self._repository.values()
    
  def save(self, program):
    program = self._repository[program.name] = program
    
  def load(self, name):
    return self._repository[name]


class Program(threading.Thread):

  _running = False

  def __init__(self, name, code):
    super(Program, self).__init__()
    self.name = name
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
