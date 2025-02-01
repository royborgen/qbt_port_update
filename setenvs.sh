#!/bin/sh
#
export CREATE_LOG_FILE="yes"
export GLUETUN_IP="127.0.0.1"
export GLUETUN_PORT="8000"
export GLUETUN_USER="username"
export GLUETUN_PASS="password"
export LOGFILE="qbt_port_update.log"
export LOGTIMEFORMAT="%d-%m-%Y %H:%M:%S"
#export PATH_GLUETUN="/srv/gluetun/forwarded_port"
export PATH_QBITTORRENT="/srv/qBittorrent/qBittorrent.conf"
export QBT_CONTAINER_ID="qbittorrent"
