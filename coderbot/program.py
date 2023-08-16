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
import threading
import json
import shutil
import logging
from datetime import datetime
import math

from tinydb import TinyDB, Query
from threading import Lock

import coderbot
import camera
import motion
import config
import audio
import event
import music
import musicPackages
from hw.atmega328p import ATMega328 

PROGRAM_PATH = "./data/"
PROGRAM_PREFIX = "program_"
PROGRAM_SUFFIX = ".json"
PROGRAMS_DB = "data/programs.json"
PROGRAMS_PATH_DEFAULTS = "defaults/programs/"
PROGRAM_STATUS_ACTIVE = "active"
PROGRAM_STATUS_DELETED = "deleted"
PROGRAM_KIND_STOCK = "stock"
PROGRAM_KIND_USER = "user"

musicPackageManager = musicPackages.MusicPackageManager.get_instance()

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

def get_music():
    return music.Music.get_instance(musicPackageManager)

def get_atmega():
    return ATMega328.get_instance()

class ProgramEngine:

    # pylint: disable=exec-used

    _instance = None

    def __init__(self, settings):
        self._program = None
        self._log = ""
        self._programs = TinyDB(PROGRAMS_DB)

        # initialise DB from default programs
        query = Query()
        self.lock = Lock()
        for dirname, dirnames, filenames, in os.walk(PROGRAMS_PATH_DEFAULTS):
            for filename in filenames:
                if PROGRAM_PREFIX in filename:
                    program_name = filename[len(PROGRAM_PREFIX):-len(PROGRAM_SUFFIX)]
                    if self.load(program_name) is None:
                        logging.info("adding program %s in path %s as default %r", program_name, dirname, ("default" in dirname))
                        with open(os.path.join(dirname, filename), "r") as f:
                            program_dict = json.load(f)
                            program_dict["kind"] = PROGRAM_KIND_STOCK
                            program_dict["status"] = PROGRAM_STATUS_ACTIVE
                            program = Program.from_dict(program_dict)
                            self.save(program)

    @classmethod
    def get_instance(cls, settings=None):
        if not cls._instance:
            cls._instance = ProgramEngine(settings)
        return cls._instance

    def prog_list(self, active_only = True):
        programs = None 
        query = Query()
        if active_only:
            programs = self._programs.search(query.status == PROGRAM_STATUS_ACTIVE)
        else:
            programs = self._programs.all()
        return programs

    def save(self, program):
        with self.lock: 
            query = Query()
            program._modified = datetime.now()
            self._program = program
            program_db_entry = self._program.as_dict()
            if self._programs.search(query.name == program.name) != []:
                self._programs.update(program_db_entry, query.name == program.name)
            else:
                self._programs.insert(program_db_entry)

    def load(self, name):
        with self.lock: 
            query = Query()
            program_db_entries = self._programs.search(query.name == name)
            if len(program_db_entries) > 0:
                prog_db_entry = program_db_entries[0]
                #logging.debug(prog_db_entry)
                self._program = Program.from_dict(prog_db_entry)
                return self._program
            return None

    def delete(self, name, logical = True):
        with self.lock: 
            query = Query()
            program_db_entries = self._programs.search(query.name == name)
            if len(program_db_entries) > 0:
                program_db_entry = program_db_entries[0]
                if logical:
                    program_db_entry["status"] = PROGRAM_STATUS_DELETED
                    program_db_entry["modified"] = datetime.now().isoformat()
                    self._programs.update(program_db_entry, query.name == name)
                else:
                    self._programs.remove(query.name == name)
        return None

    def create(self, name, code):
        self._program = Program(name, code, modified=datetime.now())
        return self._program

    def is_running(self, name):
        return self._program.is_running() and self._program.name == name

    def check_end(self):
        return self._program.check_end()

    def log(self, text):
        self._log += text + "\n"

    def get_log(self):
        return self._log

    def set_log(self, log):
        self._log = ""

    def get_current_program(self):
        return self._program

class Program:
    _running = False

    @property
    def dom_code(self):
        return self._dom_code

    def __init__(self, name, description=None, code=None, dom_code=None, kind=PROGRAM_KIND_USER, id=None, modified=None, status=None):
        self._thread = None
        self._name = name
        self._description = description
        self._dom_code = dom_code
        self._code = code
        self._kind = kind
        self._id = id
        self._modified = modified
        self._status = status

    def execute(self, options={}):
        if self._running:
            raise RuntimeError('already running')

        ProgramEngine.get_instance().set_log("")
        self._running = True
        try:
            self._thread = threading.Thread(target=self.run, args=(options,))
            self._thread.start()
        except RuntimeError as re:
            logging.error("RuntimeError: %s", str(re))
        except Exception as e:
            logging.error("Exception: %s", str(e))

        return "ok"

    def stop(self):
        if self._running:
            self._running = False
            self._thread.join()

    def check_end(self):
        if self._running is False:
            raise RuntimeError('stop requested')
        return None

    def is_running(self):
        return self._running

    def is_stock(self):
        return self._kind == PROGRAM_KIND_STOCK

    def run(self, *args):
        options = args[0]
        try:
            program = self
            try:
                if options.get("autoRecVideo") == True:
                    get_cam().video_rec(program.name.replace(" ", "_"))
                    logging.debug("starting video")
            except Exception as e:
                logging.error("Camera not available: " + str(e))

            self._log = "" #clear log
            imports = "import json\n"
            code = imports + self._code
            env = globals()
            logging.debug("** start code **\n"+str(code)+ "\n** end code **")
            exec(code, env, env)
        except RuntimeError as re:
            logging.info("quit: %s", str(re))
            get_prog_eng().log(str(re))
        except Exception as e:
            logging.info("quit: %s", str(e))
            get_prog_eng().log(str(e))
        finally:
            try:
                get_event().wait_event_generators()
                get_event().unregister_listeners()
                get_event().unregister_publishers()
            except Exception as e:
                logging.error("error polishing event system: %s", str(e))
            try:
                get_bot().stop()
                get_cam().video_stop() #if video is running, stop it
                get_cam().set_text("") #clear overlay text (if any)
                get_motion().stop()
            except Exception:
                logging.error("Camera not available")
            self._running = False


    @property
    def name(self):
        return self._name

    def as_dict(self):
        return {'name': self._name,
                'dom_code': self._dom_code,
                'code': self._code,
                'kind': self._kind,
                'id': self._id,
                'modified': self._modified.isoformat(),
                'status': self._status}

    @classmethod
    def from_dict(cls, amap):
        return Program(name=amap['name'], 
                       dom_code=amap['dom_code'], 
                       code=amap['code'], 
                       kind=amap.get('kind', PROGRAM_KIND_USER), 
                       id=amap.get('id', None),
                       modified=datetime.fromisoformat(amap.get('modified', datetime.now().isoformat())),
                       status=amap.get('status', None),)
