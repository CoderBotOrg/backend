import threading
from event_channel.threaded_event_channel import ThreadedEventChannel

class EventManager(object):
    _instance = None
    @classmethod
    def get_instance(cls, node_name=None):
        if cls._instance is None and node_name is not None:
            cls._instance = EventManager(node_name)
        return cls._instance

    def __init__(self, node_name):
        self._channel = ThreadedEventChannel(blocking=False)
        self._publisher_threads = None 
        self._subscribers = [] 
        self._node_name = node_name
        self._event_generators = []

    def publish(self, topic, msg):
        self._publisher_threads = self._channel.publish(topic, msg)

    def register_event_listener(self, topic, callback):
        self._channel.subscribe(topic, callback)
        self._subscribers.append((topic, callback))

    def register_event_generator(self, generator_func):
        generator = threading.Thread(target=generator_func)
        self._event_generators.append(generator)
        generator.start()

    def unregister_listeners(self):
        for l in self._subscribers:
            self._channel.unsubscribe(l[0], l[1]) 
        self._subscribers = []
	
    def unregister_publishers(self):
        if self._publisher_threads:
            for t in self._publisher_threads:
                t.join()

    def start_event_generators(self):
        for g in self._event_generators:
            g.start()

    def wait_event_generators(self):
        for g in self._event_generators:
            g.join()
        self._event_generators = []
