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
#    CoderBot, a didactical programmable robot.
#    Copyright (C) 2014, 2015 Roberto Previtera <info@coderbot.org>
#
#    MUSICAL EXTENTION for CoderBot
#    This extention is develop by:
#    Michele Carbonera - miki_992@hotmail.it - m.carbonera@campus.unimib.it - michele.carbonera@unimib.it
#    Antonino Tramontana - a.tramontana1@campus.unimib.it
#    Copyright (C) 2020 
############################################################################

import os
import sox

class Music:

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Music()
        return cls._instance

    def __init__(self):
        os.putenv('AUDIODRIVER', 'alsa')
        os.putenv('AUDIODEV', 'hw:1,0')
        print("We have create a class: MUSICAL")

    def test(self):
        tfm = sox.Transformer()
        tfm.preview('cat.wav')  

if __name__ == "__main__":
    a = Music()
    
    a.test()
    a.test()
    a.test()
    a.test()
