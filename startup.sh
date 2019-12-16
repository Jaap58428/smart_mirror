#!/bin/bash

sudo /home/ghost/smart_mirror/rocket/target/release/rocket >> log_rocket.txt &
sudo python3 /home/ghost/smart_mirror/main.py >> log.txt &
