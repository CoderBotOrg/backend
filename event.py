import logging
import threading
import rospy
import std_msgs

class EventManager:
  _instance = None
  @classmethod
  def get_instance(cls, node_name=None):
    if cls._instance is None and node_name is not None:
      cls._instance = EventManager(node_name)
    return cls._instance

  def __init__(self, node_name):
    rospy.init_node(node_name)
    self._publishers = {}
    self._event_generators = []

  def register_publisher(self, topic):
    publisher = rospy.Publisher("/" + node_name + "/" + topic, String, queue_size=10)
    self._publishers[topic] = publisher
    return publisher 
    
  def register_listener(self, topic, callback):
    rospy.Subscriber("/" + node_name + "/" + topic, std_msgs.msg.String, callback)

  def register_event_generator(self, generator_func):
    generator = threading.Thread(target=generator_func)
    self._event_generators.append(generator)
    generator.start()

  def start_event_generators(self):
    for g in self._event_generators:
      g.start()

  def wait_event_generators(self):
    for g in self._event_generators:
      g.join()
