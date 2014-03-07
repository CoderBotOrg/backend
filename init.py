#!/usr/bin/python

from handler import camera, signal, logo
import coderbot
import main

cam_h = camera.CameraHandler.get_instance()
cam_h.add_handler(camera.SimpleHandler())
cam_h.add_handler(signal.SignalHandler(coderbot.CoderBot.get_instance()))
cam_h.add_handler(logo.LogoHandler("coderdojo-logo.png", coderbot.CoderBot.get_instance()))
cam_h.set_active_handler(None)

if __name__=="__main__":
  cam_h.start()
  main.run_server()
