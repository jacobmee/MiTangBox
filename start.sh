#!/bin/bash

export QT_QPA_PLATFORM=linuxfb:fb=/dev/fb1
cd /home/pi/mitangbox
sudo rm /tmp/*.jpg
sudo rm *.log
sudo sh init/init.sh /dev/fb1
python3 ./mitangbox.py
