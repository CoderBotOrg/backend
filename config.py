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

import json

CONFIG_FILE = "coderbot.cfg"

class Config(object):

    _config = {}

    @classmethod
    def get(cls):
        return cls._config

    @classmethod
    def read(cls):
        f = open(CONFIG_FILE, 'r')
        cls._config = json.load(f)
        f.close()
        return cls._config

    @classmethod
    def write(cls, config):
        cls._config = config
        f = open(CONFIG_FILE, 'w')
        json.dump(cls._config, f)
        return cls._config
