import picamera
import picamera.array
import io
import time
import copy

class Camera():

  def __init__(self, props):
    print "camera init"
    time.sleep(2.0)
    self.camera = picamera.PiCamera()
    self.camera.resolution = (props.get('width', 640), props.get('height', 240))
    self.camera.framerate = 30
    self.out_jpeg = io.BytesIO() #bytearray(int(props.get('width', 640)) * int(props.get('height', 480)) * 3)
    self.out_yuv = picamera.array.PiYUVArray(self.camera, size=(160,120)) #io.BytesIO() #bytearray(int(props.get('width', 640)) * int(props.get('height', 480)) * 3)

  def grab(self):
    ts = time.time()
    camera_port_0, output_port_0 = self.camera._get_ports(True, 0)
    self.jpeg_encoder = self.camera._get_image_encoder(camera_port_0, output_port_0, 'jpeg', None, quality=40)
    camera_port_1, output_port_1 = self.camera._get_ports(True, 1)
    self.yuv_encoder = self.camera._get_image_encoder(camera_port_1, output_port_1, 'yuv', (160, 120))
    #print "g.1: " + str(ts - time.time())
    #ts = time.time()

    with self.camera._encoders_lock:
      self.camera._encoders[0] = self.jpeg_encoder
      self.camera._encoders[1] = self.yuv_encoder

    #print "g.2: " + str(ts - time.time())
    #ts = time.time()

    self.out_jpeg.seek(0)
    self.out_yuv.seek(0)

    self.jpeg_encoder.start(self.out_jpeg)
    self.yuv_encoder.start(self.out_yuv)

    #print "g.3: " + str(ts - time.time())
    #ts = time.time()

    if not self.jpeg_encoder.wait(10):
      raise picamera.PiCameraError('Timed out')
    if not self.yuv_encoder.wait(10):
      raise picamera.PiCameraError('Timed out')

    #print "g.4: " + str(ts - time.time())
    #ts = time.time()

    with self.camera._encoders_lock:
      del self.camera._encoders[0]
      del self.camera._encoders[1]
    self.jpeg_encoder.close()
    self.yuv_encoder.close()

    #print "g.5: " + str(ts - time.time())
    #ts = time.time()


  def get_image_jpeg(self):
    return self.out_jpeg.getvalue()

  def get_image_bgr(self):
    return self.out_yuv.rgb_array
    
  def close(self):
    pass
