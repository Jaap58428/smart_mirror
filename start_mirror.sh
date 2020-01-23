#!/bin/bash

full_path=$(realpath $0)
dir_path=$(dirname $full_path)

sudo $dir_path/rocket/target/release/rocket &
sudo python3 $dir_path/main.py &

