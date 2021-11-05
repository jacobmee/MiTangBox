#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage:${0} /dev/fbx"
    exit 1
fi
FB_DEV=${1}

HARDWARE=`cat /proc/cpuinfo | grep Hardware`
REVISION=`cat /proc/cpuinfo | grep Revision`
HARDWARE=${HARDWARE#*: }
REVISION=${REVISION#*: }
echo "Hardware:${HARDWARE}"
echo "Revision:${REVISION}"


export QWS_DISPLAY=Transformed:Rot0:Linuxfb:${FB_DEV}:enable=1

export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export PATH=/bin:/sbin:/usr/bin/:/usr/sbin:/usr/local/bin
export QWS_MOUSE_PROTO="MouseMan:/dev/input/mice"
export QWS_KEYBOARD=TTY:/dev/tty1

cd /home/pi/mitangbox/init
killall init_screen > /dev/null 2>&1
./init_screen -qws &
