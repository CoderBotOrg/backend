#!/usr/bin/python3

import socket
import subprocess
import shutil
import sys
import os
import time
import urllib
import fcntl
import struct
import json
import argparse

class WiFi():

    CONFIG_FILE = "/etc/coderbot/wifi.conf"
    adapters = ["default", "RT5370", "RTL8188CUS"]
    hostapds = {"default": "hostapd", "RT5370": "hostapd-RT5370.conf", "RTL8188CUS": "hostapd-RTL8188.conf"}
    web_url = "http://my.coderbot.org/api/coderbot/1.0/bot/"
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
        lsusb_out = str(subprocess.check_output("lsusb"))
        for a in cls.adapters:
            if a in lsusb_out:
                return a
        return cls.adapters[0]

    @classmethod
    def start_hostapd(cls):
        adapter = cls.get_adapter_type()
        hostapd_type = cls.hostapds.get(adapter)
        try:
            print("starting hostapd...")
            out = os.system("/usr/sbin/" + hostapd_type + " -B /etc/hostapd/" + hostapd_type + ".conf")
            print("hostapd out: " + str(out))

        except subprocess.CalledProcessError as e:
            print(e.output)

    @classmethod
    def start_dnsmasq(cls):
        try:
            print("starting dnsmasq...")
            out = os.system("systemctl start dnsmasq")
            print("dnsmasq out: " + str(out))

        except subprocess.CalledProcessError as e:
            print(e.output)

    @classmethod
    def stop_hostapd(cls):
        try:
            print("stopping hostapd...")
            out = subprocess.check_output(["sudo", "pkill", "-9", "hostapd"])
            print("hostapd out: " + str(out))
        except subprocess.CalledProcessError as e:
            print(e.output)

    @classmethod
    def stop_dnsmasq(cls):
        try:
            print("stopping dnsmasq...")
            out = subprocess.check_output(["systemctl", "stop", "dnsmasq"])
            print("dnsmasq out: " + str(out))
        except subprocess.CalledProcessError as e:
            print(e.output)

    @classmethod
    def get_ipaddr(cls, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])

    @classmethod
    def get_macaddr(cls, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
        return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

    @classmethod
    def register_ipaddr(cls, bot_uid, bot_name, bot_ipaddr, user_email):
        try:
            data = {"bot_uid": bot_uid,
                    "bot_name": bot_name,
                    "bot_ip": bot_ipaddr,
                    "bot_version": "1.0",
                    "user_email": user_email}
            req = urllib.Request(cls.web_url + bot_uid, json.dumps(data), headers={"Authorization": "CoderBot 123456"})
            ret = urllib.urlopen(req)
            if ret.getcode() != 200:
                raise Exception()
        except Exception as e:
            print("except: " + str(e))
            raise

    @classmethod
    def get_wlans(cls):
        out = subprocess.check_output(["iwlist", "wlan0", "scan"])

    @classmethod
    def set_client_params(cls, wssid, wpsk):
        os.system("sudo sed -i s/ssid=.*$/ssid='\"" + wssid + "\"'/ " + cls.wifi_client_conf_file)
        os.system("sudo sed -i s/psk=.*$/psk='\"" + wpsk + "\"'/ " + cls.wifi_client_conf_file)

    @classmethod
    def set_ap_params(cls, wssid, wpsk):
        adapter = cls.get_adapter_type()
        os.system("sudo sed -i s/ssid=.*$/ssid=" + wssid + "/ /etc/hostapd/" + cls.hostapds.get(adapter) + ".conf")
        if wpsk:
            os.system("sudo sed -i s/wpa_passphrase=.*$/wpa_passphrase=" + wpsk + "/ /etc/hostapd/" + cls.hostapds.get(adapter) + ".conf")

    @classmethod
    def set_start_as_client(cls):
        cls._config["wifi_mode"] = "client"
        cls.save_config()

    @classmethod
    def set_bot_name(cls, name):
        cls._config["bot_name"] = name
        cls.save_config()

    @classmethod
    def start_as_client(cls):
        cls.stop_dnsmasq()
        cls.stop_hostapd()
        try:
            time.sleep(1.0)
            out = os.system("wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null 2>&1")
            out += os.system("dhclient -1 wlan0")
            print(out)
            try:
                cls.register_ipaddr(cls.get_macaddr("wlan0"), cls.get_config().get('bot_name', 'CoderBot'), cls.get_ipaddr("wlan0"), "roberto.previtera@gmail.com")
                print("registered bot, ip: " + str(cls.get_ipaddr("wlan0") + " name: " + cls.get_config().get('bot_name', 'CoderBot')))
            except:
                pass
        except subprocess.CalledProcessError as e:
            print(e.output)
            raise

    @classmethod
    def set_start_as_ap(cls):
        cls._config["wifi_mode"] = "ap"
        cls.save_config()

    @classmethod
    def start_as_ap(cls):
        time.sleep(1.0)
        out = str(subprocess.check_output(["ip", "link", "set", "dev", "wlan0", "down"]))
        out += str(subprocess.check_output(["ip", "a", "add", "10.0.0.1/24", "dev", "wlan0"]))
        out += str(subprocess.check_output(["ip", "link", "set", "dev", "wlan0", "up"]))
        out += str(subprocess.check_output(["ifconfig"]))
        print(out)
        cls.start_hostapd()
        cls.start_dnsmasq()

    @classmethod
    def start_service(cls):
        config = cls.load_config()
        if config["wifi_mode"] == "ap":
            print("starting as ap...")
            cls.start_as_ap()
        elif config["wifi_mode"] == "client":
            print("starting as client...")
            try:
                cls.start_as_client()
            except:
                print("Unable to register ip, revert to ap mode")
                cls.start_as_ap()

    @classmethod
    def get_hostapd_config_file(cls):
        adapter = cls.get_adapter_type()
        hostapd_type = cls.hostapds.get(adapter)
        return "/etc/hostapd/" + hostapd_type + ".conf"

    @classmethod
    def set_unique_ssid(cls):
        """
        See if ssid is already a unique id based on CPU serial number.
        If not, set it in hostapd.conf
        """
        try:
            inconfig = None
            with open(cls.get_hostapd_config_file()) as infile:
                inconfig = infile.read()
            inconfig = inconfig.replace("CHANGEMEATFIRSTRUN", str(abs(hash(cls.get_serial())))[0:4])
            with open(cls.get_hostapd_config_file(), "w") as outfile:
                outfile.write(inconfig)
        except:
            print("Unexpected error: ", sys.exc_info()[0])
            raise

    @classmethod
    def get_serial(cls):
        """
        Extract serial from cpuinfo file
        """
        cpuserial = "0000000000000000"
        try:
            f = open('/proc/cpuinfo','r')
            for line in f:
                if line[0:6]=='Serial':
                    cpuserial = line[10:26]
            f.close()
        except:
            cpuserial = "ERROR000000000"
        return cpuserial

def main():
    parser = argparse.ArgumentParser(description="CoderBot wifi config manager and daemon initializer", prog="wifi.py")
    subparsers = parser.add_subparsers()
    up = subparsers.add_parser('updatecfg', help="update configuration")
    up.add_argument('-m', '--mode', choices=['ap', 'client'], help='wifi mode')
    up.add_argument('-s', '--ssid', help='wifi ssid')
    up.add_argument('-p', '--pwd', help='wifi password')
    up.add_argument('-n', '--name', help='coderbot unique id')
    args = vars(parser.parse_args())
    print(args)
    w = WiFi()
    if args:
        if args['mode'] == 'ap':
            w.set_start_as_ap()
            if args.get('ssid') and args.get('pwd'):
                w.set_ap_params(args['ssid'], args['pwd'])
        elif args['mode'] == 'client':
            w.set_start_as_client()
            if args.get('ssid') and args.get('pwd'):
                w.set_client_params(args['ssid'], args['pwd'])
        if args['name']:
            w.set_bot_name(args['name'])
    else:
        w.set_unique_ssid()
        w.start_service()

if __name__ == "__main__":
    main()
