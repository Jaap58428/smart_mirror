#!/bin/bash

sudo /home/ghost/smart_mirror/rocket/target/release/rocket &
sudo python3 /home/ghost/smart_mirror/main.py &

