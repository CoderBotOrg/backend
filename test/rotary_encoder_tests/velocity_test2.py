from time import sleep
from motorencoder import MotorEncoder
import pigpio

pi = pigpio.pi()

m = MotorEncoder(pi, 22, 25, 24, 14, 16)

m.control(power=100.0, time_elapse=5)

