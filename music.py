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
        tfm.build('cat.wav', 'outMusicDemo.wav')

    #play a pause
    # @param duration: duration of the pause in seconds
    def play_pause(self, duration):
        time.sleep(duration)

    #play a given note for a given instrument
    # @param instrument: name of the instrument to be used
    # @param note: name of the note in the following format "A2"
    # @para alteration: if it is a diesis or a bemolle
    # @param time: duration of the note in seconds
    def play_note(self, note, alteration='none', time=1.0, instrument='piano'):
            tfm = sox.Transformer()
            
            time = float(time)

            alt = 0.0
            
            #noteArray={}

            if note == 'C2':
            # pitch shift combined audio up n semitones, quick may reduce audio quality
                shift = -7.0 + alt
            elif note == 'D2':
                shift = -5.0 + alt
            elif note == 'E2':
                shift = -3.0 + alt
            elif note == 'F2':
                shift = -2.0 + alt
            elif note == 'F#2':
                shift = -1.0 + alt
                       
            tfm.pitch(shift, quick=False)

            tfm.trim(0.0, end_time=0.5*time)
            
            tfm.preview(instrument + '.wav')
            print("play_note:  note " + note )

if __name__ == "__main__":
    a = Music()
    
    a.play_note('C2')
    a.play_pause(1)
    a.play_note('E2')
    a.play_note('D2')
    a.test()
