#!/bin/sh

export PYTHONPATH=./stub:./test:./coderbot
cd /coderbot
python3 coderbot/main.py & python3 wifi/main.py 
