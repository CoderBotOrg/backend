from wheelsaxel import WheelsAxel
import pigpio

# GPIO
# motors
PIN_MOTOR_ENABLE = 22
PIN_LEFT_FORWARD = 25
PIN_LEFT_BACKWARD = 24
PIN_RIGHT_FORWARD = 4
PIN_RIGHT_BACKWARD = 17
#?
PIN_PUSHBUTTON = 11
# servo
PIN_SERVO_3 = 9
PIN_SERVO_4 = 10
# sonar
PIN_SONAR_1_TRIGGER = 18
PIN_SONAR_1_ECHO = 7
PIN_SONAR_2_TRIGGER = 18
PIN_SONAR_2_ECHO = 8
PIN_SONAR_3_TRIGGER = 18
PIN_SONAR_3_ECHO = 23
# encoder
PIN_ENCODER_LEFT_A = 14
PIN_ENCODER_LEFT_B = 6
PIN_ENCODER_RIGHT_A = 15
PIN_ENCODER_RIGHT_B = 12

pi = pigpio.pi()

twin_motors_enc = WheelsAxel(
            pi,
            enable_pin=PIN_MOTOR_ENABLE,
            left_forward_pin=PIN_LEFT_FORWARD,
            left_backward_pin=PIN_LEFT_BACKWARD,
            left_encoder_feedback_pin_A=PIN_ENCODER_LEFT_A,
            left_encoder_feedback_pin_B=PIN_ENCODER_LEFT_B,
            right_forward_pin=PIN_RIGHT_FORWARD,
            right_backward_pin=PIN_RIGHT_BACKWARD,
            right_encoder_feedback_pin_A=PIN_ENCODER_RIGHT_A,
            right_encoder_feedback_pin_B=PIN_ENCODER_RIGHT_B)

twin_motors_enc.control_distance(100, 100, 200)