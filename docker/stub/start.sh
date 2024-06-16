#!/bin/sh

export PYTHONPATH=./stub:./test:./coderbot
cd /coderbot
python3 coderbot/main.py & python3 stub/wifi/main.py