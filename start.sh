#!/bin/bash

export QT_QPA_PLATFORM=linuxfb:fb=/dev/fb1

cd /home/pi/matrix/demo/nanopi-status
sudo run.sh /dev/fb1

cd /home/pi/mitangbox
python3 mitangbox.py
