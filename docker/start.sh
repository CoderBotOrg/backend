#!/bin/sh
# disable ethernet, usb
[ "$CODERBOT_disable_eth_usb" = "true" ] && echo '1-1' | tee /sys/bus/usb/drivers/usb/unbind
# disable HDMI output
/usr/bin/tvservice -o
# enable i2c driver
modprobe i2c-dev
# set home
cd /coderbot
# start coderbot
python3 coderbot/main.py
