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
import time
from sys import byteorder
from array import array
from struct import pack
import logging

import pyaudio
import wave
import audioop
import logging

try:
    from pocketsphinx.pocketsphinx import Decoder
    from sphinxbase.sphinxbase import *
except:
    logging.info("pocketsphinx not available")

## GOOGLE Speech API ##
# [START import_libraries]
#from __future__ import division

import re
import sys

#from google.cloud import speech
#from google.cloud.speech import enums
#from google.cloud.speech import types
import pyaudio
from six.moves import queue
# [END import_libraries]

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
FORMAT = pyaudio.paInt16

MODELDIR = "/home/pi/coderbot/psmodels/"
SOUNDDIR = "./sounds/"

class Audio:

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Audio()
        return cls._instance

    def __init__(self):
        #self.pyaudio = pyaudio.PyAudio()
        try:
            #self.stream_in = self.pyaudio.open(format=FORMAT,
            #  channels=1, rate=RATE,
            #  input=True,
            #  frames_per_buffer=CHUNK)
            #self.stream_in.start_stream()
            self.stream_in = self.MicrophoneStream(FORMAT, RATE, CHUNK)
        except Exception as e:
            logging.info("Audio: input stream not available")

        #self._google_speech_client = speech.SpeechClient()

    def exit(self):
        pass
        # cleanup stuff.
        #self.stream_in.close()
        #self.pyaudio.terminate()

    def say(self, what, locale='en'):
        if what and "$" in what:
            os.system ('omxplayer sounds/' + what[1:])
        elif what and len(what):
            os.system ('espeak --stdout -v' + locale + ' -p 90 -a 200 -s 150 -g 10 "' + what + '" 2>>/dev/null | aplay')

    def normalize(self, snd_data):
        "Average the volume out"
        MAXIMUM = 16384
        times = float(MAXIMUM)/max(abs(i) for i in snd_data)

        r = array('h', snd_data)
        c = 0
        for i in snd_data:
            r[c] = int(i*times)
            c +=1
        return r

    def record(self, elapse):
        num_silent = 0
        snd_started = False
        c = 0

        r = bytearray()

        t = time.time()
        with self.stream_in as stream:
            audio_generator = stream.generator()
            for content in audio_generator:
                r.extend(content)
                if time.time() - t >= elapse:
                    return r

    def record_to_file(self, filename, elapse):
        data = self.record(elapse)
        #data = pack('<' + ('h'*len(data)), *data)

        wf = wave.open(SOUNDDIR + filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.pyaudio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(data)
        wf.close()

    def play(self, filename):
        os.system ('omxplayer sounds/' + filename)

        """
        # open the file for reading.
        wf = wave.open(SOUNDDIR + filename, 'rb')

        # open stream based on the wave object which has been input.
        stream = self.pyaudio.open(format =
                    self.pyaudio.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)

        # read data (based on the chunk size)
        data = wf.readframes(CHUNK)

        # play stream (looping from beginning of file to the end)
        while data != '':
          # writing to the stream is what *actually* plays the sound.
          stream.write(data)
          data = wf.readframes(CHUNK)
          logging.info("play")

        # cleanup stuff.
        stream.close()
        """

    def hear(self, level, elapse=1.0):
        ts_total = time.time()

        t = time.time()
        with self.stream_in as stream:
            audio_generator = stream.generator()
            for content in audio_generator:
                snd_rms = audioop.rms(content, 2)
                if snd_rms > level:
                    return True
                if time.time() - t >= elapse:
                    return False

    def speech_recog(self, model):

        # Create a decoder with certain model
        config = Decoder.default_config()
        config.set_string('-hmm', '/usr/local/share/pocketsphinx/model/en-us/en-us')
        config.set_int('-ds', 2)
        config.set_int('-topn', 3)
        config.set_int('-maxwpf', 5)
        #config.set_string('-kws', MODELDIR + model + '.txt')
        config.set_string('-lm', MODELDIR + model + '.lm')
        config.set_string('-dict', MODELDIR + model + '.dict')
        decoder = Decoder(config)

        decoder.start_utt()
        tstamp = time.time()
        recog_text = ''

        with self.stream_in as stream:
            audio_generator = stream.generator()
            for content in audio_generator:
                decoder.process_raw(content, False, False)
                if decoder.hyp() and decoder.hyp().hypstr != '':
                    recog_text += decoder.hyp().hypstr
                    tstamp = time.time()
                    if len(recog_text) > 1:
                        decoder.end_utt()
                        logging.info("recog text: " + recog_text)
                        return recog_text

 #   def speech_recog_google(self, locale):
 #       config = types.RecognitionConfig(
 #           encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
 #           sample_rate_hertz=RATE,
 #           language_code=locale)
 #       streaming_config = types.StreamingRecognitionConfig(
 #           config=config,
 #           interim_results=False,
 #           single_utterance=True)
#
 #       t1 = time.time()
  #      with self.stream_in as stream:
   #         audio_generator = stream.generator()
    #        requests = (types.StreamingRecognizeRequest(audio_content=content)
     #                   for content in audio_generator)
#
 #           responses = self._google_speech_client.streaming_recognize(streaming_config, requests)

            # Now, put the transcription responses to use.
  #          for response in responses:
   #             if time.time() - t1 > 10:
    #                return ""
     #           if response.results:
      #              result = response.results[0]
       #             if result.is_final:
        #                return result.alternatives[0].transcript

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

        def __exit__(self, type, value, traceback):
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
