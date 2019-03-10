PIN_ENCODER_LEFT = 15
PIN_ENCODER_RIGHT = 14

if __name__ == "__main__":

   import time
   import pigpio

   import rotary_encoder

   pos_left = 0
   pos_right = 0

   def callback_left(way):

      global pos_left

      pos_left += way

      print("Current ticks (left wheel)= {}".format(pos_left))

   def callback_right(way):

      global pos_right

      pos_right += way

      print("Current ticks (right wheel) = {}".format(pos_right))
   pi = pigpio.pi()

   print("Rotary encoder ticks test (left wheel ONLY)")

   decoder_left = rotary_encoder.decoder(pi, PIN_ENCODER_LEFT, callback_left)
   decoder_right = rotary_encoder.decoder(pi, PIN_ENCODER_RIGHT, callback_right)

   time.sleep(300)

   decoder.cancel()

   pi.stop()

