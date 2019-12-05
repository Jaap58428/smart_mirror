#!/bin/bash

sudo python3 /home/ghost/smart_mirror/main.py >> log.txt &
/home/ghost/.cargo/bin/watchexec -w /home/ghost/smart_mirror/rocket /bin/bash /home/ghost/smart_mirror/reboot.sh &
