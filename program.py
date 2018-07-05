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

import os
import sys
import threading
import json
import logging

import time
from pathlib import Path
import pigpio

import math
import coderbot
import camera
import motion
import config
import audio
import event
import conversation

import subprocess

PROGRAM_PATH = "./data/"
PROGRAM_PREFIX = "program_"
PROGRAM_SUFFIX = ".data"




tmp_folder_path = "tmp/"
status_fileName = "coderbotStatus_temp.json"
prog_gen_commands_fileName = "coderbotProg_gen_commands_temp.json"




class Commands:
    def get_cam():
        return camera.Camera.get_instance()

    def get_bot():
        return coderbot.CoderBot.get_instance()

    def get_motion():
        return motion.Motion.get_instance()

    def get_audio():
        return audio.Audio.get_instance()

    def get_prog_eng():
        return ProgramEngine.get_instance()

    def get_event():
        return event.EventManager.get_instance()

    def get_conv():
        return conversation.Conversation.get_instance()

class ProgramEngine:

    _instance = None

    def __init__(self):
        self._program = None
        self._repository = {}
        self._log = ""
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

    def prog_list(self):
        return list(self._repository.keys())

    def save(self, program):
        self._program = self._repository[program.name] = program
        f = open(PROGRAM_PATH + PROGRAM_PREFIX + program.name + PROGRAM_SUFFIX, 'w')
        json.dump(program.as_json(), f)
        f.close()

    def load(self, name):
        #return self._repository[name]
        f = open(PROGRAM_PATH + PROGRAM_PREFIX + name + PROGRAM_SUFFIX, 'r')
        self._program = Program.from_json(json.load(f))
        return self._program

    def delete(self, name):
        del self._repository[name]
        os.remove(PROGRAM_PATH + PROGRAM_PREFIX + name + PROGRAM_SUFFIX)
        return "ok"

    def create(self, name, code):
        self._program = Program(name, code)
        return self._program

    def is_running(self, name):
        return self._repository[name].is_running()

    def check_end(self):
        return self._program.check_end()

    def log(self, text):
        self._log += text + "\n"

    def get_log(self):
        return self._log

 
class Program:
    _running = False

    @property
    def dom_code(self):
        return self._dom_code

    def __init__(self, name, code=None, dom_code=None):
        #super(Program, self).__init__()
        self._thread = None
        self.name = name
        self._dom_code = dom_code
        self._code = code

    def execute(self):
        if self._running:
            raise RuntimeError('already running')

        self._running = True

        try:
            self._thread = threading.Thread(target=self.run)
            self._thread.start()
        except RuntimeError as re:
            logging.error("RuntimeError:" + str(re))
        except Exception as e:
            logging.error("Exception:" + str(e))

        return "ok"

    def end(self):
        if self._running:
            self._running = False
            self._thread.join()

    def check_end(self):
        if self._running == False:
            raise RuntimeError('end requested')
        return None

    def is_running(self):
        return self._running

    def run(name, code, mode):

        try:

            if mode == "fullExec":
                is_execFull = "is_execFull = True\n"
            else: # mode == stepByStep
                is_execFull = "is_execFull = False\n"

            headerFile = is_execFull + '\n\
\n\
import json\n\
from os import getpid, rename\n\
import sys\n\
import signal\n\
with open("' + tmp_folder_path + status_fileName + '", "r") as fh:\n\
 data_coderbotStatus = json.loads(fh.read())\n\
\n\
def saveStatus():\n\
 with open("' + tmp_folder_path + status_fileName + '.tmp", "w") as fh:\n\
  fh.write(json.dumps(data_coderbotStatus))\n\
  rename("' + tmp_folder_path + status_fileName + '.tmp", "' + tmp_folder_path + status_fileName + '")\n\
\n\
data_coderbotStatus["prog_gen"]["currentBlockId"] = None\n\
data_coderbotStatus["prog_gen"]["status"] = "loading"\n\
data_coderbotStatus["prog_gen"]["pid"] = getpid()\n\
saveStatus()\n\
print("####### "+str(data_coderbotStatus["prog_gen"]["pid"]))\n\
print("###### LAUNCHED")\n\
print("###### IMPORTING program.py MODULE...")\n\
\n\
from program import Commands\n\
\n\
print("###### MODULE IMPORTED")\n\
data_coderbotStatus["prog_gen"]["status"] = "running"\n\
saveStatus()\n\
\n\
def do_command(sig, stack):\n\
 global is_execFull\n\
 with open("' + tmp_folder_path + prog_gen_commands_fileName + '", "r") as fh:\n\
  data_prog_gen_commands = json.loads(fh.read())\n\
\n\
 if data_prog_gen_commands["command"] == "change_mode":\n\
  if data_prog_gen_commands["argument"] == "fullExec":\n\
   is_execFull = True\n\
   data_coderbotStatus["prog_gen"]["status"] = "running"\n\
  elif data_prog_gen_commands["argument"] == "stepByStep":\n\
   is_execFull = False\n\
   data_coderbotStatus["prog_gen"]["status"] = "running"\n\
  else:\n\
   pass # Ignore if the argument is unknown\n\
 else:\n\
  pass # Ignore if the command is unknown\n\
 saveStatus()\n\
def do_terminate(sig, stack):\n\
 data_coderbotStatus["prog_gen"] = {}\n\
 data_coderbotStatus["prog_handler"]["mode"] = "stop"\n\
 saveStatus()\n\
 print("######### PROGRAM TERMINATED")\n\
 sys.exit(0)\n\
signal.signal(signal.SIGUSR1, do_command)\n\
signal.signal(signal.SIGTERM, do_terminate)\n\
\n'

            footerFile = 'data_coderbotStatus["prog_gen"] = {}\ndata_coderbotStatus["prog_handler"]["mode"] = "stop"\nsaveStatus()\nprint("######### PROGRAM TERMINATED")'

            code = headerFile + code + footerFile

            print("######## PREPARING THE FILE...")
            with open("_coderbot_generated_program.tmp.py", "w") as fh:
                fh.write(code)
            print("######## THE FILE IS READY")
            print("######## LAUNCHING...")
            subprocess.Popen(["python3", "_coderbot_generated_program.tmp.py"])

            return {"ok":True,"description":""}
        except Exception as e:
            return {"ok":False,"error_code":500,"description":"ProblemOnLauchingTheGeneratedProgram"}



    def as_json(self):
        return {'name': self.name,
                'dom_code': self._dom_code,
                'code': self._code}

    @classmethod
    def from_json(cls, map):
        return Program(name=map['name'], dom_code=map['dom_code'], code=map['code'])
