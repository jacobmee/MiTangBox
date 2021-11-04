#!/bin/bash
export QT_QPA_PLATFORM=linuxfb:fb=/dev/fb1

sudo ~/matrix/demo/nanopi-status/run.sh /dev/fb1
python3 mitangbox.py
