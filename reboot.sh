#!/bin/bash

pgrep python | sudo xargs kill
sudo python3 /home/ghost/smart_mirror/main.py >> log.txt &
