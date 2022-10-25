class Balena():
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Balena()
        return cls._instance

    def __init__(self):
        pass
    
    def purge(self):
        return ""

    def shutdown(self):
        return ""

    def restart(self):
        return ""

    def reboot(self):
        return ""

    def device(self):
        return {}
