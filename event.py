import logging
import threading
import rospy
import std_msgs
import json

class EventManager:
  _instance = None
  @classmethod
  def get_instance(cls, node_name=None):
    if cls._instance is None and node_name is not None:
      cls._instance = EventManager(node_name)
    return cls._instance

  def __init__(self, node_name):
    self._node_name = node_name
    rospy.init_node(node_name)
    self._publishers = {}
    self._event_generators = []
    self._event_listeners = []

  def publish(self, topic, message):
    publisher = self._publishers.get(topic)
    if publisher is None:
      publisher = rospy.Publisher("/" + self._node_name + "/" + topic, std_msgs.msg.String, queue_size=10)
      self._publishers[topic] = publisher
    publisher.publish(json.dumps(message)) 
    
  def register_event_listener(self, topic, callback):
    self._event_listeners.append(rospy.Subscriber("/" + self._node_name + "/" + topic, std_msgs.msg.String, callback))

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
