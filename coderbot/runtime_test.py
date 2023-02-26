"""
    This file defines base tests for CoderBot
    in order to test its functionality

    The function run_test(varargin) lanuches tests
    according to required test from the front-end.
    e.g. varagrin = ["motor_test", "sonar_test"]
    __test_encoder() and __test_sonar() will be launched.

    If something goes wrong a -1 is returned for the correspondent failed test.
    If a test passes for correspondent component, a 1 is returned.
    If no test was executed on that component, 0 is preserved.
"""
import logging
from coderbot import CoderBot

# Single components tests

# encoder motors
def __test_encoder():
    try:
        c = CoderBot.get_instance()
        # moving both wheels at speed 100 clockwise
        logging.info("moving both wheels at speed 100 clockwise")
        assert(c.speed() == 0)
        c.move(speed=100, elapse=2)
        assert(c.distance() != 0)
        assert (c.speed() == 0)

        # moving both wheels at speed 40 clockwise
        logging.info("moving both wheels at speed 40 clockwise")
        assert(c.speed() == 0)
        c.move(speed=40, elapse=2)
        assert(c.distance() != 0)
        assert (c.speed() == 0)

        # moving both wheels at speed 100 counter-clockwise
        logging.info("moving both wheels at speed 100 counter-clockwise")
        assert(c.speed() == 0)
        c.move(speed=-100, elapse=2)
        assert(c.distance() != 0)
        assert (c.speed() == 0)

        # moving both wheels at speed 40 counter-clockwise
        logging.info("moving both wheels at speed 40 counter-clockwise")
        assert(c.speed() == 0)
        c.move(speed=-40, elapse=2)
        assert(c.distance() != 0)
        assert (c.speed() == 0)

        # moving forward
        logging.info("moving forward")
        assert(c.speed() == 0)
        c.forward(speed=100, elapse=2)
        assert(c.distance() != 0)
        assert (c.speed() == 0)

        # moving backwards
        logging.info("moving backwards")
        assert(c.speed() == 0)
        c.backward(speed=100, elapse=2)
        assert(c.distance() != 0)
        assert (c.speed() == 0)

        # moving forward for 1 meter
        logging.info("moving forward for 1 meter")
        assert(c.speed() == 0)
        c.forward(speed=100, distance=1000)
        assert(c.distance() != 0)
        assert (c.speed() == 0)

        # moving backwards for 1 meter
        logging.info("moving backwards for 1 meter")
        assert(c.speed() == 0)
        c.backward(speed=100, distance=1000)
        assert(c.distance() != 0)
        assert (c.speed() == 0)

        # turning left
        logging.info("turning left")
        assert(c.speed() == 0)
        c.left(speed=100, elapse=2)
        assert(c.distance() != 0)
        assert (c.speed() == 0)

        # turning right
        logging.info("turning right")
        assert(c.speed() == 0)
        c.right(speed=100, elapse=2)
        assert(c.distance() != 0)
        assert (c.speed() == 0)

        return 1
    except:
        return -1

# sonar
def __testSonar():
    return 1

# speaker
def __test_speaker():
    return 1

# OCR
def __test_OCR():
    return 1

# add more tests here

""" Main test function
    it launches tests to test single components individually.
    A dictionary is returned monitoring the state of the
    tests for each component. 
    Varargin is a list of strings that indicates which test
    to run. """
def run_test(varargin):
    # state for each executed test
    #  0 = component not tested
    #  1 = test passed
    # -1 = test failed
    tests_state = {
        "motors":   0,
        "sonar":    0,
        "speaker":  0,
        "OCR":      0
        # add more tests state here
    }

    # running chosen tests
    for test in varargin:
        if(test == 'motors'):
            tests_state[test] = __test_encoder()
        elif(test == 'sonar'):
            tests_state[test] = __testSonar()
        elif (test == 'speaker'):
            tests_state[test] = __test_speaker()
        elif(test == 'ocr'):
            tests_state[test] = __test_OCR()
        #add more test cases here

    return tests_state
