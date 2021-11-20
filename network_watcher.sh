#!/bin/s

while true
do
  myssid=$(iwgetid -r)
  current_date_time="[`date "+%Y-%m-%d %H:%M:%S"`]";
  if [ "$myssid" = "MiTang" ]
  then
    echo "$current_date_time WIFI connected to MiTang"
  else
    echo "$current_date_time Reload NetworkManager"
    systemctl reload NetworkManager
  fi
  sleep 60
done
