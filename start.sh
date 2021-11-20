#!/bin/bash

export QT_QPA_PLATFORM=linuxfb:fb=/dev/fb1
cd /home/pi/mitangbox
sudo rm -f /tmp/*.jpg
sudo rm -f *.log
sudo sh init/init.sh /dev/fb1
sudo sh network_watcher.sh > network_watcher.log &
python3 ./mitangbox.py
