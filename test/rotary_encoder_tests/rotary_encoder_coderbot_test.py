from coderbot import CoderBot

c = CoderBot.get_instance();

c._twin_motors_enc.control_distance(100, 100, 200)

#while(True):
print(c._twin_motors_enc.distance())
