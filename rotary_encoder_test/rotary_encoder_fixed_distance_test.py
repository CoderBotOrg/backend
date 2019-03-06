PIN_LEFT_FORWARD = 24
PIN_LEFT_BACKWARD = 25
PIN_RIGHT_FORWARD = 17
PIN_RIGHT_BACKWARD = 4
PIN_ENCODER_LEFT = 15
PIN_ENCODER_RIGHT = 14

PIN_MOTOR_ENABLE = 22
PWM_FREQUENCY = 100 #Hz
PWM_RANGE = 100 #0-100

if __name__ == "__main__":

   import time
   import pigpio
   import signal

   import rotary_encoder

   pos = 0

   def callback_left(way):
      global pos
      pos += way

      print("You've travelled: " + str(0.196 * pos) + "mm, ticks: " + str(pos))

   pi = pigpio.pi()

   decoder_left = rotary_encoder.decoder(pi, PIN_ENCODER_LEFT, callback_left)

   # FORWARD MOVEMENT
   print("GOING FORWARD")
   pi.set_PWM_frequency(PIN_LEFT_FORWARD, PWM_FREQUENCY)
   pi.set_PWM_range(PIN_LEFT_FORWARD, PWM_RANGE)
   pi.set_PWM_frequency(PIN_RIGHT_FORWARD, PWM_FREQUENCY)
   pi.set_PWM_range(PIN_RIGHT_FORWARD, PWM_RANGE)

   pi.write(PIN_MOTOR_ENABLE, 1)

   pi.set_PWM_dutycycle(PIN_LEFT_FORWARD, 30)
   pi.set_PWM_dutycycle(PIN_RIGHT_FORWARD, 30)

   signal.pause()

   if(pos > 100):
      print("STOP")
      pi.write(PIN_LEFT_FORWARD, 0)
      pi.write(PIN_RIGHT_FORWARD, 0)
      decoder.cancel()
      pi.stop()


