import logging
import threading
from pubsub import pub 

class EventManager:
    _instance = None
    @classmethod
    def get_instance(cls, node_name=None):
        if cls._instance is None and node_name is not None:
            cls._instance = EventManager(node_name)
        return cls._instance

    def __init__(self, node_name):
        self._node_name = node_name
        self._event_generators = []

    def publish(self, topic, msg):
        pub.sendMessage(topic, message=msg)

    def register_event_listener(self, topic, callback):
        pub.subscribe(callback, topic)

    def register_event_generator(self, generator_func):
        generator = threading.Thread(target=generator_func)
        self._event_generators.append(generator)
        generator.start()
    
    def unregister_listeners(self):
        pub.unsubAll()

    def unregister_publishers(self):
        pass

    def start_event_generators(self):
        for g in self._event_generators:
            g.start()

    def wait_event_generators(self):
        for g in self._event_generators:
            g.join()
