#!/bin/sh
#
export PATH_GLUETUN=/srv/gluetun/forwarded_port
export PATH_QBITTORRENT=/srv/qBittorrent/qBittorrent.conf
export QBT_CONTAINER_ID=qbittorrent
export CREATE_LOG_FILE=yes
export LOGFILE=/home/user/logs/qbt_port_update.log
export LOGTIMEFORMAT="%d-%m-%Y %H:%M:%S"
