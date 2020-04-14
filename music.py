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
        print("We have create a class: MUSICAL")

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
        print(note)
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
            print('note not exist')            

        tfm.pitch(shift, quick=False)
        tfm.trim(0.0, end_time=0.5*duration)
        if self.managerPackage.isPackageAvailable(instrument):
            tfm.preview('./sounds/notes/' + instrument + '/audio.wav')            
        else:
            print("no instrument:"+str(instrument)+" present in this coderbot!")
        
    def play_animal(self, instrument, note='G2', alteration='none', duration=1.0):
        tfm = sox.Transformer()
            
        duration = float(duration)

        alt = 0.0
        if alteration == 'bmolle':
            alt = -1.0
        elif alteration == 'diesis':
            alt = 1.0

        if note == 'C2':
            shift = -7.0 + alt
        elif note == 'D2':
            shift = -5.0 + alt
        elif note == 'E2':
            shift = -3.0 + alt
        elif note == 'F2':
            shift = -2.0 + alt
        elif note == 'F#2':
            shift = -1.0 + alt
        elif note == 'G2':
            shift = 0.0 + alt
        elif note == 'A2':
            shift = 2.0 + alt
        elif note == 'Bb2':
            shift = 3.0 + alt
        elif note == 'B2':
            shift = 4.0 + alt
        elif note == 'C3':
            shift = 5.0 + alt
        elif note == 'D3':
            shift = 7.0 + alt
        elif note == 'E3':
            shift = 9.0 + alt
        elif note == 'F3':
            shift = 10.0 + alt
        elif note == 'G3':
            shift = 12.0 + alt                
        tfm.pitch(shift, quick=False)
        tfm.trim(0.0, end_time=0.5*duration)
        #tfm.stretch(time, window=20)
        tfm.preview('./sounds/notes/' + instrument + '/audio.wav')
