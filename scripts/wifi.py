import socket
import subprocess
import shutil
import sys

class WiFi():

  adapters = ["RT5370", "RTL8188CUS"] 
  hostapds = {"RT5370": "hostapd.RT5370", "RTL8188CUS": "hostapd.RTL8188"} 
  web_url = "http://coderbotsrv.appspot.com/register_ip"
  wifi_client_conf_file = "/etc/wpa_supplicant/wpa_supplicant.conf"

  @classmethod
  def get_adapter_type(cls):
    lsusb_out = subprocess.check_output("lsusb")
    for a in cls.adapters:
      if a in lsusb_out:
        return a
    return None
    
  @classmethod
  def start_hostapd(cls):
    adapter = cls.get_adapter_type()
    hostapd_type = cls.hostapds.get(adapter)
    print hostapd_type
    try:
      #out = subprocess.check_output(["start-stop-daemon",  "--start", "--oknodo",  "--quiet", "--exec", "/usr/sbin/" + hostapd_type, "--", "/etc/hostapd/" + hostapd_type])
      out = subprocess.check_output(["/usr/sbin/" + hostapd_type, "/etc/hostapd/" + hostapd_type])

    except subprocess.CalledProcessError as e:
      print e.output
      raise

  @classmethod
  def stop_hostapd(cls):
    try:
      out = subprocess.check_output(["pkill", "-9", "hostapd"])
      print out
    except:
      pass

  @classmethod
  def get_ipaddr(cls):
    ipaddr = socket.gethostbyname(socket.gethostname())
    return ipaddr

  @classmethod
  def register_ipaddr(cls, ipaddr, botname):
    urllib.request.urlopen(cls.web_url + "?name=" + botname + "&ipaddr=" + ipaddr)

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
  def start_as_client(cls):
    cls.stop_hostapd()
    out = subprocess.check_output(["ifdown", "wlan0"])
    shutil.copy("/etc/network/interfaces_cli", "/etc/network/interfaces")
    out = subprocess.check_output(["ifup", "wlan0"])

  @classmethod
  def start_as_ap(cls):
    out = subprocess.check_output(["ifdown", "wlan0"])
    shutil.copy("/etc/network/interfaces_ap", "/etc/network/interfaces")
    out = subprocess.check_output(["ifup", "wlan0"])
    cls.start_hostapd()

def main():
  w = WiFi()


main()

