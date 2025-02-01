#!/bin/sh
#
export PATH_GLUETUN=/srv/gluetun/forwarded_port
export PATH_QBITTORRENT=/srv/qBittorrent/qBittorrent.conf
export QBT_CONTAINER_ID=qbittorrent
export CREATE_LOG_FILE=yes
export LOGFILE=qbt_port_update.log
export LOGTIMEFORMAT="%d-%m-%Y %H:%M:%S"
export GLUETUN_IP=10.0.0.9
export GLUETUN_PORT=8001
export GLUETUN_USER=roy
export GLUETUN_PASS=eYUbKfRDX9J6IhyNrbVQL6hx7fHSSe6S4IrjSb1gN4yma5qxoM
