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

import coderbot
import camera
import motion
import config
import audio
import event
import conversation

PROGRAM_PATH = "./data/"
PROGRAM_PREFIX = "program_"
PROGRAM_SUFFIX = ".data"

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
        self._log = ""

    def execute(self):
        if self._running:
            raise RuntimeError('already running')

        self._running = True

        try:
            self._thread = threading.Thread(target=self.run)
            self._thread.start()
        except RuntimeError as re:
            logging.error("RuntimeError:" + str(re))
            print str(e)
        except Exception as e:
            logging.error("Exception:" + str(e))
            print str(e)

        return "ok"

    def end(self):
        if self._running:
            self._running = False
            self._thread.join()

    def check_end(self):
        if self._running == False:
            raise RuntimeError('end requested')
        return None

    def log(self, text):
        self._log += text + "\n"

    def get_log(self):
        return self._log

    def is_running(self):
        return self._running

    def run(self):
        try:
            bot = coderbot.CoderBot.get_instance()
            program = self
            try:
                cam = camera.Camera.get_instance()
                if config.Config.get().get("prog_video_rec") == "true":
                    get_cam().video_rec(program.name)
                    logging.debug("starting video")
            except:
                logging.error("Camera not available")

            imports = "import json\n"
            code = imports + self._code
            exec(code)
            get_event().wait_event_generators()
        except RuntimeError as re:
            logging.info("quit: " + str(re))
            self.log(str(re))
        except Exception as e:
            logging.info("quit: " + str(e))
            self.log(str(e))
        finally:
            try:
                get_cam().video_stop() #if video is running, stop it
                get_motion().stop()
            except:
                logging.error("Camera not available")
            self._running = False


    def as_json(self):
        return {'name': self.name,
                'dom_code': self._dom_code,
                'code': self._code}

    @classmethod
    def from_json(cls, map):
        return Program(name=map['name'], dom_code=map['dom_code'], code=map['code'])
