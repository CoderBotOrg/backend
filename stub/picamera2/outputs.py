class Output():
    pass

class FileOutput(Output):
    def __init__(self, output):
        self.output = output

    def outputframe(self, frame):
        self.output.write(frame)

class FfmpegOutput(Output):
    def __init__(video_filename):
        pass