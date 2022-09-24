class PyAudio(object):
    def __init__(self):
        pass

    def open(self, *args, **kwargs):
        return Stream()

    def get_sample_size(self, mode):
        return 10000

    def get_format_from_width(self, *args, **kwargs):
        return 0

class Stream(object):
    def __init__(self):
        pass

    def close(self):
        pass
    
    def write(self, *args, **kwargs):
        pass

paInt16 = 0


