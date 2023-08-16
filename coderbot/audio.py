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
from array import array
import time
import logging
import wave
import audioop
import pyaudio
import alsaaudio

from six.moves import queue
# [END import_libraries]

# Audio recording parameters
RATE = 44100
CHUNK = int(RATE / 10)  # 100ms
FORMAT = pyaudio.paInt16

MODELDIR = "/home/pi/coderbot/psmodels/"
SOUNDDIR = "./sounds/"
SOUNDEXT = ".wav"

SOURCE_OUTPUT = 0
SOURCE_INPUT = 1

class Audio:

    _instance = None

    @classmethod
    def get_instance(cls, settings=None):
        if cls._instance is None:
            cls._instance = Audio(settings)
        return cls._instance

    def __init__(self, settings):
        self.pa = pyaudio.PyAudio()
        try:
            self.stream_in = self.MicrophoneStream(FORMAT, RATE, CHUNK)
        except Exception:
            logging.info("Audio: input stream not available")

    def exit(self):
       pass

    def say(self, what, locale='en'):
        if what and "$" in what:
            self.play(what[1:] + SOUNDEXT)
        elif what and what:
            os.system('espeak --stdout -v' + locale + ' -p 90 -a 200 -s 150 -g 10 "' + what + '" 2>>/dev/null | aplay -q')

    def normalize(self, snd_data):
        "Average the volume out"
        MAXIMUM = 16384
        times = float(MAXIMUM) / max(abs(i) for i in snd_data)

        r = array('h', snd_data)
        c = 0
        for i in snd_data:
            r[c] = int(i*times)
            c += 1
        return r

    def record(self, elapse):
        r = bytearray()
        t = time.time()
        with self.stream_in as stream:
            audio_generator = stream.generator()
            for content in audio_generator:
                r.extend(content)
                if time.time() - t >= elapse:
                    return r
        return r

    def record_to_file(self, filename, elapse):
        data = self.record(elapse)
        #data = pack('<' + ('h'*len(data)), *data)

        wf = wave.open(SOUNDDIR + filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.stream_in.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(data)
        wf.close()

    def play(self, filename):	

        f = wave.open(SOUNDDIR + filename, 'rb')

        format = None

        # 8bit is unsigned in wav files
        if f.getsampwidth() == 1:
            format = alsaaudio.PCM_FORMAT_U8
        # Otherwise we assume signed data, little endian
        elif f.getsampwidth() == 2:
            format = alsaaudio.PCM_FORMAT_S16_LE
        elif f.getsampwidth() == 3:
            format = alsaaudio.PCM_FORMAT_S24_3LE
        elif f.getsampwidth() == 4:
            format = alsaaudio.PCM_FORMAT_S32_LE
        else:
            raise ValueError('Unsupported format')

        periodsize = f.getframerate() // 8

        logging.info('%d channels, %d sampling rate, format %d, periodsize %d\n' % (f.getnchannels(),
                                                                            f.getframerate(),
                                                                            format,
                                                                            periodsize))

        device = alsaaudio.PCM(channels=f.getnchannels(), rate=f.getframerate(), format=format, periodsize=periodsize)
        
        data = f.readframes(periodsize)
        while data:
            # Read data from stdin
            device.write(data)
            data = f.readframes(periodsize)

    def hear(self, level, elapse=1.0):
        t = time.time()
        with self.stream_in as stream:
            audio_generator = stream.generator()
            for content in audio_generator:
                snd_rms = audioop.rms(content, 2)
                if snd_rms > level:
                    return True
                if time.time() - t >= elapse:
                    return False
        return False

    def get_volume(self):
        volume = alsaaudio.Mixer('Headphone', cardindex=0).getvolume()
        logging.info(volume) # list of per-channel values (floats)
        return volume
    
    def set_volume(self, volume_output, volume_input):
        alsaaudio.Mixer('Headphone', cardindex=0).setvolume(volume_output)
        alsaaudio.Mixer('Mic', cardindex=1).setvolume(volume_input)

    class MicrophoneStream(object):
        """Opens a recording stream as a generator yielding the audio chunks."""
        def __init__(self, fmt, rate, chunk):
            self._audio_interface = None
            self._format = fmt
            self._rate = rate
            self._chunk = chunk

            # Create a thread-safe buffer of audio data
            self._buff = None
            self.closed = True

        def __enter__(self):
            self._audio_interface = pyaudio.PyAudio()
            self._buff = queue.Queue()
            self._audio_stream = self._audio_interface.open(
                format=self._format,
                # The API currently only supports 1-channel (mono) audio
                # https://goo.gl/z757pE
                channels=1, rate=self._rate,
                input=True, frames_per_buffer=self._chunk,
                input_device_index=1,
                # Run the audio stream asynchronously to fill the buffer object.
                # This is necessary so that the input device's buffer doesn't
                # overflow while the calling thread makes network requests, etc.
                stream_callback=self._fill_buffer,
            )
            self.closed = False

            return self

        def __exit__(self, atype, value, traceback):
            self._audio_stream.stop_stream()
            self._audio_stream.close()
            self._audio_interface.terminate()
            self.closed = True
            self._buff.put(None)

        def close(self):
            pass

        def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
            """Continuously collect data from the audio stream, into the buffer."""
            self._buff.put(in_data)
            return None, pyaudio.paContinue

        def get_sample_size(self, fmt):
            return self._audio_interface.get_sample_size(fmt)

        def generator(self):
            while not self.closed:
                # Use a blocking get() to ensure there's at least one chunk of
                # data, and stop iteration if the chunk is None, indicating the
                # end of the audio stream.
                chunk = self._buff.get()
                if chunk is None:
                    return
                data = [chunk]

                # Now consume whatever other data's still buffered.
                while True:
                    try:
                        chunk = self._buff.get(block=False)
                        if chunk is None:
                            return
                        data.append(chunk)
                    except queue.Empty:
                        break

                yield b''.join(data)
# [END audio_stream]
