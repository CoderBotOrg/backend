#!/bin/bash
[[ -d "firmware" ]] && [[ ! -f "firmware/initialised" ]] && source firmware/upload.sh
LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1.2.0 python3 init.py
