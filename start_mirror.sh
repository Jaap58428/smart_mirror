#!/bin/bash

echo $0

full_path=$(realpath $0)
dir_path=$(dirname $full_path)

sudo $dirpath/rocket/target/release/rocket &
sudo python3 $dir_path/main.py &

