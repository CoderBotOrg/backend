#!/bin/bash
[[ -d "firmware" ]] && [[ ! -f "firmware/initialised" ]] && source firmware/upload.sh
AUDIODEV=hw:1 LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1.2.0 PYTHONPATH=/coderbot python3 coderbot/main.py
