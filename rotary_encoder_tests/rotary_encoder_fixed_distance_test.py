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

   # mm and ticks
   pos = 0
   mm = 0

   # callback function on EITHER EDGE 
   def callback_left(way):
      global pos
      global mm
      pos += way
      mm = 0.196 * pos

   pi = pigpio.pi() # GPIO daemon

   # decoding number of ticks for right wheel only
   decoder_left = rotary_encoder.decoder(pi, PIN_ENCODER_RIGHT, callback_left)

   # setting up FORWARD MOVEMENT
   print("GOING FORWARD")
   pi.set_PWM_frequency(PIN_LEFT_FORWARD, PWM_FREQUENCY)
   pi.set_PWM_range(PIN_LEFT_FORWARD, PWM_RANGE)
   pi.set_PWM_frequency(PIN_RIGHT_FORWARD, PWM_FREQUENCY)
   pi.set_PWM_range(PIN_RIGHT_FORWARD, PWM_RANGE)

   # enabling motors
   pi.write(PIN_MOTOR_ENABLE, 1)

   # going forward on 30% speed
   pi.set_PWM_dutycycle(PIN_LEFT_FORWARD, 30)
   pi.set_PWM_dutycycle(PIN_RIGHT_FORWARD, 30)


   try:
       while(True):
           # print current ticks and mm
           print("You've travelled:  %.3f mm, ticks: %d" %(mm, pos))
           if(mm >= 100):
               break # stop if travelled Xmm
   except KeyboardInterrupt: pass #handling keyboard interrupt to stop motors
   finally:
       # stop motors no matter what
       print("STOP")
       pi.write(PIN_LEFT_FORWARD, 0)
       pi.write(PIN_RIGHT_FORWARD, 0)
       decoder_left.cancel()
       pi.stop()
       time.sleep(.5) # avoiding print spamming
