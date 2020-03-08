import unittest
import test.pigpio_mock
import coderbot
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

sh = logging.StreamHandler()
# add a rotating handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)

logger.addHandler(sh)

class CoderBotDCMotorTestCase(unittest.TestCase):
    def setUp(self):
        coderbot.pigpio.pi = test.pigpio_mock.PIGPIOMock
        coderbot.CoderBot._instance = None
        self.bot = coderbot.CoderBot.get_instance()

    def test_motor_forward(self):
        self.bot.forward(speed=100, elapse=0.1)

    def test_motor_backward(self):
        self.bot.backward(speed=100, elapse=0.1)

    def test_motor_left(self):
        self.bot.left(speed=100, elapse=0.1)

    def test_motor_right(self):
        self.bot.left(speed=100, elapse=0.1)

    def test_motor_move(self):
        self.bot.move(speed=100, elapse=0.1)
        self.bot.move(speed=-100, elapse=0.1)

    def test_motor_turn(self):
        self.bot.turn(speed=100, elapse=0.1)
        self.bot.turn(speed=-100, elapse=0.1)

class CoderBotServoMotorTestCase(unittest.TestCase):
    def setUp(self):
        coderbot.pigpio.pi = test.pigpio_mock.PIGPIOMock
        coderbot.CoderBot._instance = None
        self.bot = coderbot.CoderBot.get_instance(servo=True)

    def test_motor_forward(self):
        self.bot.forward(speed=100, elapse=0.1)

    def test_motor_backward(self):
        self.bot.backward(speed=100, elapse=0.1)

    def test_motor_left(self):
        self.bot.left(speed=100, elapse=0.1)

    def test_motor_right(self):
        self.bot.left(speed=100, elapse=0.1)

    def test_motor_move(self):
        self.bot.move(speed=100, elapse=0.1)
        self.bot.move(speed=-100, elapse=0.1)

    def test_motor_turn(self):
        self.bot.turn(speed=100, elapse=0.1)
        self.bot.turn(speed=-100, elapse=0.1)


class CoderBotSonarTestCase(unittest.TestCase):
    def setUp(self):
        coderbot.pigpio.pi = test.pigpio_mock.PIGPIOMock
        coderbot.CoderBot._instance = None
        self.bot = coderbot.CoderBot.get_instance()

    def test_sonar(self):
        for i in range(0, 3):
            distance = self.bot.get_sonar_distance(i)
            self.assertTrue(distance > 85 and distance < 86) 
