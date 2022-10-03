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
from pulsectl import Pulse, PulseVolumeInfo

from six.moves import queue
# [END import_libraries]

# Audio recording parameters
RATE = 44100
CHUNK = int(RATE / 10)  # 100ms
FORMAT = pyaudio.paInt16

MODELDIR = "/home/pi/coderbot/psmodels/"
SOUNDDIR = "./sounds/"

SINK_OUTPUT = 0
SINK_INPUT = 1

class Audio:

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Audio()
        return cls._instance

    def __init__(self):
        self.pa = pyaudio.PyAudio()
        try:
            self.stream_in = self.MicrophoneStream(FORMAT, RATE, CHUNK)
        except Exception:
            logging.info("Audio: input stream not available")

    def exit(self):
       pass

    def say(self, what, locale='en'):
        if what and "$" in what:
            self.play(what[1:])
        elif what and what:
            os.system('espeak --stdout -v' + locale + ' -p 90 -a 200 -s 150 -g 10 "' + what + '" 2>>/dev/null | paplay')

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
        # open the file for reading.
        wf = wave.open(SOUNDDIR + filename, 'rb')

        # open stream based on the wave object which has been input.
        stream = self.pa.open(format =
                    self.pa.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)

        # read data (based on the chunk size)
        data = wf.readframes(CHUNK)

        # play stream (looping from beginning of file to the end)
        while len(data) > 0:
            # writing to the stream is what *actually* plays the sound.
            stream.write(data)
            data = wf.readframes(CHUNK)

        # cleanup stuff.
        stream.close()

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
        with Pulse('volume') as pulse:
            sink = pulse.sink_list()[0] # first random sink-input stream

            volume = sink.volume
            logging.info(volume.values) # list of per-channel values (floats)
            return volume
    
    def set_volume(self, volume_output, volume_input):
        with Pulse('volume') as pulse:
            sinks= pulse.sink_list() # first random sink-input stream

            volume = sinks[SINK_OUTPUT].volume
            logging.info(volume.values) # list of per-channel values (floats)
            logging.info(volume.value_flat) # average level across channels (float)

            volume.value_flat = volume_output # sets all volume.values to volume_new_value
            pulse.volume_set(sinks[SINK_OUTPUT], volume) # applies the change

            volume = sinks[SINK_INPUT].volume
            logging.info(volume.values) # list of per-channel values (floats)
            logging.info(volume.value_flat) # average level across channels (float)

            volume.value_flat = volume_input # sets all volume.values to volume_new_value
            pulse.volume_set(sinks[SINK_INPUT], volume) # applies the change

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