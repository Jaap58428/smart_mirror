#!/bin/bash

sudo python3 /home/jaap/smart_mirror/main.py >> log.txt &
/home/ghost/.cargo/watchexec -w /home/jaap/smart_mirror/rocket /bin/sh reboot.sh