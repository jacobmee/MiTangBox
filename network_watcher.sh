#!/bin/s

test=0
while true
do
  myssid=$(iwgetid -r)
  current_date_time="[`date "+%Y-%m-%d %H:%M:%S"`]";
  if [ "$myssid" = "MiTang" ]
  then
    #echo "$current_date_time WIFI connected to MiTang ["$test"]"
    test=0
  else
    echo "$current_date_time Trying to enable MiTang ["$test"]"
    sudo nmcli con up MiTang
    test=$((test+1))
  fi
  sleep 60
  if [ $test = 5 ]
  then
    echo "System is rebooting"
    sudo reboot
  fi

done
