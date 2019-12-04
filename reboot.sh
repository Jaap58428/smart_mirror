#!/bin/bash

python_pid = $(prep python)
kill python_pid
sudo python3 /home/jaap/smart_mirror/main.py >> log.txt