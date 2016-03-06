#!/usr/bin/python

import socket
import subprocess
import shutil
import sys
import os
import urllib2
import fcntl
import struct
import json

class WiFi():

  CONFIG_FILE = "/etc/coderbot_wifi.conf"
  adapters = ["RT5370", "RTL8188CUS"] 
  hostapds = {"RT5370": "hostapd.RT5370", "RTL8188CUS": "hostapd.RTL8188"} 
  web_url = "http://coderbotsrv.appspot.com/register_ip"
  wifi_client_conf_file = "/etc/wpa_supplicant/wpa_supplicant.conf"
  _config = {}

  @classmethod
  def load_config(cls):
    f = open(cls.CONFIG_FILE)
    cls._config = json.load(f)
    return cls._config

  @classmethod
  def save_config(cls):
    f = open(cls.CONFIG_FILE, 'w')
    json.dump(cls._config, f)
    return cls._config

  @classmethod
  def get_config(cls):
    return cls._config

  @classmethod
  def get_adapter_type(cls):
    lsusb_out = subprocess.check_output("lsusb")
    for a in cls.adapters:
      if a in lsusb_out:
        return a
    return cls.adapters[0] 
    
  @classmethod
  def start_hostapd(cls):
    adapter = cls.get_adapter_type()
    hostapd_type = cls.hostapds.get(adapter)
    try:
      print "starting hostapd..."
      os.system("/usr/sbin/" + hostapd_type + " /etc/hostapd/" + hostapd_type + " -B")

    except subprocess.CalledProcessError as e:
      print e.output

  @classmethod
  def stop_hostapd(cls):
    try:
      out = subprocess.check_output(["pkill", "-9", "hostapd"])
      print out
    except subprocess.CalledProcessError as e:
      print e.output

  @classmethod
  def get_ipaddr(cls, ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])
    ipaddr = socket.gethostbyname(socket.gethostname())
    return ipaddr

  @classmethod
  def register_ipaddr(cls, ipaddr, botname):
    try:
      ret = urllib2.urlopen(cls.web_url + "?name=" + botname + "&ipaddr=" + ipaddr)
      print str(ret.getcode())
      if ret.getcode() != 200:
        raise Exception()
    except URLError as e:
      print e
      raise
    print botname, ": ", ipaddr

  @classmethod
  def get_wlans(cls):
    out = subprocess.check_output(["iwlist", "wlan0", "scan"])  

  @classmethod
  def set_client_params(cls, wssid, wpsk):
    f = open (cls.wifi_client_conf_file, "w+")
    f.write("""ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
network={\n""")
    f.write("  ssid=\""+wssid+"\"\n")
    f.write("  psk=\""+wpsk+"\"\n")
    f.write("}")

  @classmethod
  def set_start_as_client(cls):
    shutil.copy("/etc/network/interfaces_cli", "/etc/network/interfaces")
    cls._config["wifi_mode"] = "client"
    cls.save_config()

  @classmethod
  def start_as_client(cls):
    cls.stop_hostapd()
    try:
      out = subprocess.check_output(["ifdown", "wlan0"])
      out = subprocess.check_output(["ifup", "wlan0"])
      print "registering ip..."
      cls.register_ipaddr(cls.get_ipaddr("wlan0"), self.get_config().get('bot_name', 'CoderBot'))
    except subprocess.CalledProcessError as e:
      print e.output
      raise

  @classmethod
  def set_start_as_ap(cls):
    shutil.copy("/etc/network/interfaces_ap", "/etc/network/interfaces")
    cls._config["wifi_mode"] = "ap"
    cls.save_config()

  @classmethod
  def start_as_ap(cls):
    out = subprocess.check_output(["ifdown", "wlan0"])
    out = subprocess.check_output(["ifup", "wlan0"])
    cls.start_hostapd()

  @classmethod
  def start_service(cls):
    config = cls.load_config()
    if config["wifi_mode"] == "ap":
      print "starting as ap..."
      cls.start_as_ap()
    elif config["wifi_mode"] == "client":
      print "starting as client..."
      try:
        cls.start_as_client()
      except:
        print "Unable to register ip, revert to ap mode"
        cls.start_as_ap()

def main():
  w = WiFi()
  if len(sys.argv) > 2 and sys.argv[1] == "updatecfg":
    if len(sys.argv) > 2 and sys.argv[2] == "ap":
      w.set_start_as_ap()
      w.start_as_ap()
    elif len(sys.argv) > 2 and sys.argv[2] == "client":
      if len(sys.argv) > 3:
        w.set_client_params(sys.argv[3], sys.argv[4])
      w.set_start_as_client()
      w.stop_hostapd()
      try:
        w.start_as_client()
      except:
        print "Unable to register ip, revert to ap mode"
        w.start_as_ap()
    elif len(sys.argv) > 3 and sys.argv[2] == "bot_name":
      self.get_config()['bot_name'] = sys.argv[3]
      self.save_config()
  else:
    w.start_service()

if __name__ == "__main__":
  main()

