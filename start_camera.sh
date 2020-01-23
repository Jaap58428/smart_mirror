#!/bin/bash

fullpath=$(realpath $0)
dir_path=$(dirname $fullpath)

sudo python3 $dir_path/purethermal_lib/camera_over_tcp.py &

