#!/bin/bash

export QWS_DISPLAY=Linuxfb:/dev/fb_st7789v:enable=1:mWidth120:mmHeight92:0
export QT_QPA_PLATFORM=linuxfb:fb=/dev/fb1:size=320x240:
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export PATH=/bin:/sbin:/usr/bin/:/usr/sbin:/usr/local/bin
#export QWS_MOUSE_PROTO="MouseMan:/dev/input/mice"
python3 MiTangBox.py
