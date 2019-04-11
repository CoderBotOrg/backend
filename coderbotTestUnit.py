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
# Single components tests

# encoder motors
def __test_encoder():
    return 1

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
        elif(test == 'OCR'):
            tests_state[test] = __test_OCR()
        #add more test cases here

    return tests_state