import pigpio

pi = pigpio.pi()
pi.write(24, 0)
pi.write(17, 0)
