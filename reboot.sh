#!/bin/bash

PYPID="$(pgrep python)"

echo $PYPID
if [ $PYPID ]
then
	pgrep python | sudo xargs kill;
fi
sudo python3 /home/ghost/smart_mirror/main.py >> log.txt &
