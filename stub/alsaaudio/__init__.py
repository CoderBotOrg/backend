PCM_FORMAT_U8 = 1
PCM_FORMAT_S16_LE = 2
PCM_FORMAT_S24_3LE = 3
PCM_FORMAT_S32_LE = 4

class Mixer():

    def __init__(self, device, cardindex):
        pass
    
    def getvolume(self):
        return 0.0

    def setvolume(self, volume):
        pass


class PCM():
    def __init__(self, channels, rate, format, periodsize):
        pass

    def write(self, data):
        pass