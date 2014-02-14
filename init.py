import camera_handler
import main

camera_handler = camera_handler.CameraReader.get_instance()
camera_handler.add_handler(camera_handler.SignalReader())
camera_handler.add_handler(camera_handler.LogoReader())
camera_handler.set_active_handler(None)

if __name__=="__main__":
  camera_handler.start()
  main.run_server()
  reader.join()


