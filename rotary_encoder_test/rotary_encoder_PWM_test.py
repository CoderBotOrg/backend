PIN_LEFT_FORWARD = 24
PIN_LEFT_BACKWARD = 25
PIN_RIGHT_FORWARD = 17
PIN_RIGHT_BACKWARD = 4
PIN_MOTOR_ENABLE = 22

PWM_FREQUENCY = 100 #Hz
PWM_RANGE = 100 #0-100

if __name__ == "__main__":

   import time
   import pigpio
   
   #pi = pigpio.pi('coderbot.local')
   pi = pigpio.pi()
   print("Connected, waiting for signal")

   # FORWARD MOVEMENT
   print("FORWARD")
   pi.set_PWM_frequency(PIN_LEFT_FORWARD, PWM_FREQUENCY)
   pi.set_PWM_range(PIN_LEFT_FORWARD, PWM_RANGE)
   pi.set_PWM_frequency(PIN_RIGHT_FORWARD, PWM_FREQUENCY)
   pi.set_PWM_range(PIN_RIGHT_FORWARD, PWM_RANGE)

   pi.write(PIN_MOTOR_ENABLE, 1)

   pi.set_PWM_dutycycle(PIN_LEFT_FORWARD, 100)
   pi.set_PWM_dutycycle(PIN_RIGHT_FORWARD, 100) 
   
   time.sleep(.5)

   print("STOP")
   pi.write(PIN_LEFT_FORWARD, 0)
   pi.write(PIN_RIGHT_FORWARD, 0)

   # BACKWARDS MOVEMENT
   print("BACKWARDS")
   pi.set_PWM_frequency(PIN_LEFT_BACKWARD, PWM_FREQUENCY)
   pi.set_PWM_range(PIN_LEFT_BACKWARD, PWM_RANGE)
   pi.set_PWM_frequency(PIN_RIGHT_BACKWARD, PWM_FREQUENCY)
   pi.set_PWM_range(PIN_RIGHT_BACKWARD, PWM_RANGE)

   pi.set_PWM_dutycycle(PIN_LEFT_BACKWARD, 100)
   pi.set_PWM_dutycycle(PIN_RIGHT_BACKWARD, 100) 

   time.sleep(.5)

   print("STOP")
   pi.write(PIN_LEFT_BACKWARD, 0)
   pi.write(PIN_RIGHT_BACKWARD, 0)

   pi.stop()