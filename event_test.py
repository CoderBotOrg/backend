def event_generator_1():
  while True:
    get_prog_eng().check_end() 
    c = get_cam().find_class()
    if c != "o":
      get_event().get_publisher("image/classified").publish(c)
      print "pub event: " + c
get_event().register_event_generator(event_generator_1)

def event_listener_1(event):
  get_cam().set_text(event)
  print event
get_event().register_event_listener("image/classified", event_listener_1)

while True:
  get_prog_eng().check_end() 
  get_cam().sleep(0.1)
