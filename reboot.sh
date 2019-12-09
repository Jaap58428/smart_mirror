#!/bin/bash

PYPID="$(pgrep python)"

sudo echo $PYPID
if [ $PYPID ]
then
	sudo pgrep python | sudo xargs kill
	sleep 3s
fi

PYPID="$(pgrep python)"

sudo echo $PYPID
if [ $PYPID ]
then
	sudo pgrep python | sudo xargs kill
	sleep 2s
fi

sudo python3 /home/ghost/smart_mirror/main.py >> /home/ghost/smart_mirror/log.txt &
