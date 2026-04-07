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
import time
import logging

class Music:
    _instance = None
    managerPackage = None

    noteDict = {
        'C2': -7.0, 'D2' : -5.0, 'E2' : -3.0, 'F2' : -2.0, 'F#2' : -1.0, 'G2' : 0.0,
        'A2' : 2.0, 'Bb2' : 3.0, 'B2' : 4.0, 'C3' : 5.0, 'D3' : 7.0, 'E3' : 9.0,
        'F3' : 10.0, 'G3' : 12.0
    }
    

    @classmethod
    def get_instance(cls,managerPackage):
        if cls._instance is None:
            cls._instance = Music(managerPackage)
        return cls._instance

    def __init__(self,managerPackage):
        
        #os.putenv('AUDIODRIVER', 'alsa')
        #os.putenv('AUDIODEV', 'hw:1,0')
        self.managerPackage = managerPackage
        logging.info("Music class initialized")

    def test(self):
        tfm = sox.Transformer()
        tfm.preview('cat.wav')  
        tfm.build('cat.wav', 'outMusicDemo.wav')

    #play a pause
    # @param duration: duration of the pause in seconds
    def play_pause(self, duration):
        duration = float(duration)
        time.sleep(duration)

    #play a given note for a given instrument
    # @param instrument: name of the instrument to be used
    # @param note: name of the note in the following format "A2"
    # @para alteration: if it is a diesis or a bemolle
    # @param time: duration of the note in seconds
    def play_note(self, note, instrument='piano', alteration='none', duration=1.0):
        logging.debug("play_note: %s", note)
        tfm = sox.Transformer()
        
        duration = float(duration)

        alt = 0.0
        if alteration == 'bmolle':
            alt = -1.0
        elif alteration == 'diesis':
            alt = 1.0

        if note in self.noteDict :
            shift = self.noteDict[note]+ alt
        else:
            logging.warning('note does not exist: %s', note)
            return

        tfm.pitch(shift, quick=False)
        tfm.trim(0.0, end_time=0.5*duration)
        if self.managerPackage.isPackageAvailable(instrument):
            tfm.preview('./sounds/notes/' + instrument + '/audio.wav')            
        else:
            logging.warning("no instrument: %s present in this coderbot!", instrument)
        
    def play_animal(self, instrument, note='G2', alteration='none', duration=1.0):
        tfm = sox.Transformer()
            
        duration = float(duration)

        alt = 0.0
        if alteration == 'bmolle':
            alt = -1.0
        elif alteration == 'diesis':
            alt = 1.0

        if note in self.noteDict:
            shift = self.noteDict[note] + alt
        else:
            logging.warning('note does not exist: %s', note)
            return

        if self.managerPackage.isPackageAvailable(instrument):
            tfm.preview('./sounds/notes/' + instrument + '/audio.wav')            
        else:
            logging.warning("no animal verse: %s present in this coderbot!", instrument)
            return 
        tfm.pitch(shift, quick=False)
        tfm.trim(0.0, end_time=0.5*duration)
        tfm.preview('./sounds/notes/' + instrument + '/audio.wav')
