import unittest.mock
import time
import logging
import logging.handlers
import coderbot

logger = logging.getLogger()

class PIGPIOMock(object):
    """Implements PIGPIO library mock class
    PIGPIO is the library used to access digital General Purpose IO (GPIO),
    this mock class emulates the behaviour of the inputs used by the sonar sensors: a fake signal is triggered to emulate a 85.1 distance.
    Output (DC motor and Servo) are just no-op function, they implement basic parameters check via assertions.
    """

    def __init__(self, host="localhost", port=None):
        self.callbacks = {}
        logger.info("mock called")

    def set_mode(self, pin_id, pin_mode):
        """mock set_mode"""
        pass

    def get_mode(self, pin_id):
        """mock get_mode"""
        return 0

    def callback(self, pin_id, edge, callback):
        """mock callback"""
        self.callbacks[pin_id] = callback
        return self.Callback(pin_id)

    def write(self, pin_id, value):
        """mock write"""
        assert(pin_id > 0 and pin_id < 32)
        assert(value == 0 or value == 1)

    def read(self, pin_id):
        """mock read"""
        pass

    def gpio_trigger(self, pin_id):
        """mock gpio_trigger"""
        assert(pin_id > 0 and pin_id < 32)
        # mock sonars triger and echo
        if pin_id == coderbot.GPIO_CODERBOT_V_4.PIN_SONAR_1_TRIGGER or pin_id == coderbot.GPIO_CODERBOT_V_5.PIN_SONAR_1_TRIGGER:
            if pin_id == coderbot.GPIO_CODERBOT_V_4.PIN_SONAR_1_TRIGGER:
                GPIOS=coderbot.GPIO_CODERBOT_V_4
            else:
                GPIOS=coderbot.GPIO_CODERBOT_V_5
            self.callbacks[GPIOS.PIN_SONAR_1_ECHO](GPIOS.PIN_SONAR_1_TRIGGER, 0, 0)
            self.callbacks[GPIOS.PIN_SONAR_2_ECHO](GPIOS.PIN_SONAR_1_TRIGGER, 0, 0)
            self.callbacks[GPIOS.PIN_SONAR_3_ECHO](GPIOS.PIN_SONAR_1_TRIGGER, 0, 0)
            self.callbacks[GPIOS.PIN_SONAR_1_ECHO](GPIOS.PIN_SONAR_1_ECHO, 1, 0)
            self.callbacks[GPIOS.PIN_SONAR_2_ECHO](GPIOS.PIN_SONAR_2_ECHO, 1, 0)
            self.callbacks[GPIOS.PIN_SONAR_3_ECHO](GPIOS.PIN_SONAR_3_ECHO, 1, 0)
            time.sleep(0.005)
            self.callbacks[GPIOS.PIN_SONAR_1_ECHO](GPIOS.PIN_SONAR_1_ECHO, 0, 5000)
            self.callbacks[GPIOS.PIN_SONAR_2_ECHO](GPIOS.PIN_SONAR_2_ECHO, 0, 5000)
            self.callbacks[GPIOS.PIN_SONAR_3_ECHO](GPIOS.PIN_SONAR_3_ECHO, 0, 5000)

    def set_PWM_frequency(self, pin_id, frequency):
        """mock set_PWM_frequency"""
        assert(pin_id > 0 and pin_id < 32)
        assert(frequency > 0)

    def set_PWM_range(self, pin_id, range):
        """mock set_PWM_range"""
        pass

    def set_PWM_dutycycle(self, pin_id, dutycycle):
        """mock set_PWM_dutycyle"""
        pass

    class Callback(object):
        def __init__(self, pin_id):
            pass

        def cancel(self):
            pass

    def set_pull_up_down(self, feedback_pin_A, mode):
        pass
