PIN_ENCODER_LEFT_A = 14
PIN_ENCODER_LEFT_B = 6
PIN_ENCODER_RIGHT_A = 15
PIN_ENCODER_RIGHT_B = 12


if __name__ == "__main__":

   import time
   import pigpio

   from rotarydecoder import RotaryDecoder

   pos_left = 0
   pos_right = 0

   def callback_left(way):

      global pos_left

      pos_left += way

      print("pos_LEFT={}".format(pos_left))

   def callback_right(way):

      global pos_right

      pos_right += way

      print("pos_RIGHT={}".format(pos_right))


   # pi = pigpio.pi('coderbot.local')
   pi = pigpio.pi()

   decoder_left = RotaryDecoder(pi, PIN_ENCODER_LEFT_A, PIN_ENCODER_LEFT_B, callback_left)
   decoder_right = RotaryDecoder(pi, PIN_ENCODER_RIGHT_A, PIN_ENCODER_RIGHT_B, callback_right)

   time.sleep(1000)

   decoder_left.cancel()
   decoder_right.cancel()

   pi.stop()
